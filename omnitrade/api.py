from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any, cast
from uuid import UUID

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from omnitrade.auth import LoginRequest, User, authenticate, current_user, issue_token
from omnitrade.config import get_settings
from omnitrade.contracts import (
    Checkpoint,
    FailurePolicy,
    NodeRun,
    NodeStatus,
    Run,
    RunEvent,
    RunRequest,
    RunStatus,
    UserProfile,
    WorkflowDefinition,
)
from omnitrade.engine.executors import deterministic_executors
from omnitrade.engine.runtime import WorkflowRuntime
from omnitrade.engine.validator import WorkflowValidator
from omnitrade.infrastructure.events import RedisStreamEventBus
from omnitrade.reporting import build_detailed_report, render_pdf
from omnitrade.sample_workflow import defense_workflow
from omnitrade.storage import NotFoundError, store

app = FastAPI(title="OmniTrade AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


@app.post("/api/v1/auth/login")
def login(request: LoginRequest) -> dict[str, str]:
    user = authenticate(request)
    return {"access_token": issue_token(user), "token_type": "bearer"}


@app.get("/api/v1/profile")
def get_profile(user: User = Depends(current_user)) -> dict[str, object]:
    return store.get_profile(user.id).model_dump(mode="json")


@app.put("/api/v1/profile")
def update_profile(
    profile: UserProfile, user: User = Depends(current_user)
) -> dict[str, object]:
    return store.save_profile(user.id, profile).model_dump(mode="json")


@app.get("/api/v1/catalog")
def catalog(_: User = Depends(current_user)) -> dict[str, object]:
    from omnitrade.engine.catalog import NODE_CATALOG, NODE_DESCRIPTIONS, ports_compatible

    return {
        "count": len(NODE_CATALOG),
        "nodes": {
            name: {
                "group": spec.group,
                "description": NODE_DESCRIPTIONS[name],
                "inputs": spec.inputs,
                "outputs": spec.outputs,
                "suggested_targets": [
                    {
                        "node_type": target_name,
                        "source_port": source_port,
                        "target_port": target_port,
                        "data_type": str(source_type),
                    }
                    for target_name, target_spec in NODE_CATALOG.items()
                    for source_port, source_type in spec.outputs.items()
                    for target_port, target_type in target_spec.inputs.items()
                    if target_name != name and ports_compatible(source_type, target_type)
                ],
            }
            for name, spec in NODE_CATALOG.items()
        },
    }


@app.get("/api/v1/analysis-options")
def analysis_options(_: User = Depends(current_user)) -> dict[str, object]:
    settings = get_settings()
    return {
        "tickers": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD"],
        "quick_models": ["deterministic-fixture"],
        "deep_models": ["deterministic-fixture"],
        "languages": ["English", "Italian", "French", "German", "Spanish"],
        "currencies": ["USD", "EUR", "GBP", "JPY"],
        "data_modes": (
            ["recorded", "prefer_live", "live"]
            if not settings.fixture_mode
            else ["recorded"]
        ),
    }


@app.get("/api/v1/workflows")
def list_workflows(user: User = Depends(current_user)) -> list[dict[str, object]]:
    return [_workflow_response(item) for item in store.list_workflows(user.id)]


@app.post("/api/v1/workflows", status_code=201)
def create_workflow(
    definition: WorkflowDefinition, user: User = Depends(current_user)
) -> dict[str, object]:
    return _workflow_response(store.create_workflow(user.id, definition))


@app.post("/api/v1/workflows/sample", status_code=201)
def create_sample(user: User = Depends(current_user)) -> dict[str, object]:
    sample = defense_workflow()
    existing = next(
        (
            record
            for record in store.list_workflows(user.id)
            if record["definition"] == sample
        ),
        None,
    )
    return _workflow_response(existing or store.create_workflow(user.id, sample))


@app.get("/api/v1/workflows/{workflow_id}")
def get_workflow(workflow_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    try:
        return _workflow_response(store.get_workflow(workflow_id, user.id))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@app.put("/api/v1/workflows/{workflow_id}")
def update_workflow(
    workflow_id: UUID, definition: WorkflowDefinition, user: User = Depends(current_user)
) -> dict[str, object]:
    try:
        return _workflow_response(store.update_workflow(workflow_id, user.id, definition))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@app.delete("/api/v1/workflows/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: UUID, user: User = Depends(current_user)) -> Response:
    try:
        store.delete_workflow(workflow_id, user.id)
        return Response(status_code=204)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@app.post("/api/v1/workflows/{workflow_id}/validate")
def validate_workflow(workflow_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    try:
        result = WorkflowValidator().validate(
            store.get_workflow(workflow_id, user.id)["definition"]
        )
        return result.model_dump(mode="json")
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@app.post("/api/v1/workflows/{workflow_id}/publish")
def publish_workflow(workflow_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    try:
        record = store.get_workflow(workflow_id, user.id)
        result = WorkflowValidator().validate(record["definition"])
        if not result.valid:
            raise HTTPException(status_code=422, detail=result.model_dump(mode="json"))
        return store.publish(workflow_id, user.id).model_dump(mode="json")
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@app.post("/api/v1/runs", status_code=202)
def create_run(
    request: RunRequest, background: BackgroundTasks, user: User = Depends(current_user)
) -> dict[str, object]:
    version = store.versions.get(request.workflow_version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Workflow version not found")
    workflow = store.workflows.get(version.workflow_id)
    if not workflow or workflow["owner_id"] != user.id:
        raise HTTPException(status_code=404, detail="Workflow version not found")
    run = Run(
        workflow_version_id=version.id,
        owner_id=user.id,
        ticker=request.ticker,
        as_of=request.as_of,
        configuration=request.configuration,
        budget_override=request.budget_override,
    )
    if request.configuration.data_mode == "live" and get_settings().fixture_mode:
        raise HTTPException(
            status_code=422,
            detail="Live-only mode is unavailable until live provider credentials are configured",
        )
    if request.configuration.data_mode == "prefer_live" and get_settings().fixture_mode:
        run.degraded_reasons.append(
            "Live providers are not configured; recorded evidence was used"
        )
    configured = _configured_definition(version.definition, run)
    validation = WorkflowValidator().validate(configured)
    if not validation.valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Run settings make this workflow invalid",
                "validation": validation.model_dump(mode="json"),
            },
        )
    store.save_run(run)
    background.add_task(_execute_run, run.id)
    return run.model_dump(mode="json")


@app.get("/api/v1/runs")
def list_runs(user: User = Depends(current_user)) -> list[dict[str, object]]:
    return [run.model_dump(mode="json") for run in store.list_runs(user.id)]


@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    run = _owned_run(run_id, user)
    return run.model_dump(mode="json")


@app.post("/api/v1/runs/{run_id}/cancel")
async def cancel_run(run_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    run = _owned_run(run_id, user)
    if run.status not in {RunStatus.QUEUED, RunStatus.RUNNING, RunStatus.DEGRADED}:
        raise HTTPException(status_code=409, detail="Run cannot be cancelled in its current state")
    run.status = RunStatus.CANCELLING
    store.save_run(run)
    if get_settings().env == "compose":
        await RedisStreamEventBus(get_settings().redis_url).request_cancel(run_id)
    return run.model_dump(mode="json")


@app.post("/api/v1/runs/{run_id}/resume", status_code=202)
def resume_run(
    run_id: UUID, background: BackgroundTasks, user: User = Depends(current_user)
) -> dict[str, object]:
    run = _owned_run(run_id, user)
    if run.status not in {RunStatus.INTERRUPTED, RunStatus.FAILED}:
        raise HTTPException(status_code=409, detail="Only interrupted or failed runs can resume")
    background.add_task(_execute_run, run.id)
    return run.model_dump(mode="json")


@app.get("/api/v1/runs/{run_id}/events")
def run_events(run_id: UUID, user: User = Depends(current_user)) -> StreamingResponse:
    _owned_run(run_id, user)

    async def stream() -> AsyncIterator[str]:
        sent = 0
        seen: set[UUID] = set()
        redis_bus = (
            RedisStreamEventBus(get_settings().redis_url)
            if get_settings().env == "compose"
            else None
        )
        while True:
            if redis_bus:
                events = [
                    event async for event in redis_bus.stream(run_id) if event.event_id not in seen
                ]
            else:
                events = store.run_events[run_id][sent:]
            for event in events:
                seen.add(event.event_id)
                sent += 1
                yield f"id: {sent}\nevent: {event.event_type}\ndata: {event.model_dump_json()}\n\n"
            run = store.runs[run_id]
            if run.status in {
                RunStatus.SUCCEEDED,
                RunStatus.DEGRADED,
                RunStatus.FAILED,
                RunStatus.CANCELLED,
            } and (redis_bus is not None or sent >= len(store.run_events[run_id])):
                break
            await asyncio.sleep(0.1)

    return StreamingResponse(
        stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


@app.get("/api/v1/runs/{run_id}/lineage")
def lineage(run_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    _owned_run(run_id, user)
    result = store.run_results.get(run_id, {})
    return {
        "run_id": run_id,
        "nodes": result.get("nodes", {}),
        "events": len(store.run_events[run_id]),
        "complete": bool(result),
    }


@app.get("/api/v1/runs/{run_id}/activity")
async def run_activity(run_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    run = _owned_run(run_id, user)
    events = store.run_events[run_id]
    if get_settings().env == "compose":
        events = [
            event
            async for event in RedisStreamEventBus(get_settings().redis_url).stream(run_id)
        ]
    nodes = store.run_results.get(run_id, {}).get("nodes", {})
    return {
        "run": run.model_dump(mode="json"),
        "events": [event.model_dump(mode="json") for event in events],
        "nodes": nodes,
    }


@app.get("/api/v1/reports/{run_id}")
def report(run_id: UUID, user: User = Depends(current_user)) -> dict[str, object]:
    _owned_run(run_id, user)
    result = store.run_results.get(run_id)
    if not result:
        raise HTTPException(status_code=409, detail="Report is not ready")
    return cast(dict[str, object], result.get("report", {}))


@app.get("/api/v1/report-history")
def list_reports(user: User = Depends(current_user)) -> list[dict[str, object]]:
    reports: list[dict[str, object]] = []
    for run in store.list_runs(user.id):
        result = store.run_results.get(run.id)
        if not result or not result.get("report"):
            continue
        report_data = cast(dict[str, object], result["report"])
        decision_value = report_data.get("decision")
        decision = cast(dict[str, object], decision_value) if isinstance(decision_value, dict) else {}
        reports.append(
            {
                "run_id": run.id,
                "ticker": run.ticker,
                "as_of": run.as_of,
                "created_at": run.created_at,
                "status": run.status,
                "action": decision.get("action", "NO_DECISION"),
                "confidence": decision.get("confidence", 0),
            }
        )
    return reports


@app.get("/api/v1/reports/{run_id}/export/{format}")
def export_report(run_id: UUID, format: str, user: User = Depends(current_user)) -> Response:
    data = report(run_id, user)
    if format == "json":
        return Response(json.dumps(data, indent=2, default=str), media_type="application/json")
    if format == "html":
        body = f"<html><body><h1>OmniTrade AI report</h1><pre>{json.dumps(data, indent=2, default=str)}</pre><p>Decision support only.</p></body></html>"
        return Response(body, media_type="text/html")
    if format == "pdf":
        return Response(
            render_pdf(data),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="omnitrade-{run_id}.pdf"'},
        )
    raise HTTPException(status_code=400, detail="Supported formats: json, html, pdf")


async def _execute_run(run_id: UUID) -> None:
    run = store.runs[run_id]
    version = store.versions[run.workflow_version_id]
    checkpoint = await _latest_checkpoint(run_id)
    definition = _configured_definition(version.definition, run)
    if get_settings().env == "compose":
        try:
            async with httpx.AsyncClient(
                timeout=definition.budget.max_runtime_seconds + 10
            ) as client:
                response = await client.post(
                    "http://workflow:8001/internal/runs/execute",
                    json={
                        "workflow": definition.model_dump(mode="json"),
                        "run": run.model_dump(mode="json"),
                        "checkpoint": checkpoint.model_dump(mode="json") if checkpoint else None,
                    },
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError:
            run.status = RunStatus.INTERRUPTED
            store.save_run(run)
            return
        updated = Run.model_validate(body["run"])
        store.save_run(updated)
        for event_data in body["events"]:
            store.add_event(RunEvent.model_validate(event_data))
        detailed_report = build_detailed_report(body["report"], body["nodes"], updated)
        store.save_result(run_id, {"nodes": body["nodes"], "report": detailed_report})
        return
    runtime = WorkflowRuntime(
        deterministic_executors(),
        listener=_event_listener,
        cancellation_probe=_local_cancellation_probe,
    )
    result = await runtime.execute(definition, run, restored=checkpoint)
    report_node: Any = next(
        (
            state.output
            for node_id, state in result.node_runs.items()
            if definition.nodes and node_id == "report"
        ),
        {},
    )
    store.save_run(result.run)
    node_data = {
        key: value.model_dump(mode="json") for key, value in result.node_runs.items()
    }
    store.save_result(
        run.id,
        {
            "nodes": node_data,
            "report": build_detailed_report(report_node or {}, node_data, result.run),
        },
    )


async def _event_listener(event: RunEvent) -> None:
    store.add_event(event)


async def _local_cancellation_probe(run_id: UUID) -> bool:
    return store.runs[run_id].status == RunStatus.CANCELLING


async def _latest_checkpoint(run_id: UUID) -> Checkpoint | None:
    if get_settings().env == "compose":
        events = [
            event async for event in RedisStreamEventBus(get_settings().redis_url).stream(run_id)
        ]
    else:
        events = store.run_events[run_id]
    candidates = [event for event in events if event.event_type == "run.checkpointed"]
    if not candidates:
        return None
    event = max(candidates, key=lambda item: int(item.payload["sequence"]))
    states = {
        node_id: NodeRun.model_validate(state)
        for node_id, state in event.payload["node_states"].items()
    }
    for state in states.values():
        if state.status in {
            NodeStatus.FAILED,
            NodeStatus.SKIPPED,
            NodeStatus.CANCELLED,
            NodeStatus.RUNNING,
            NodeStatus.READY,
        }:
            state.status = NodeStatus.PENDING
            state.error = None
    return Checkpoint(
        run_id=run_id,
        sequence=int(event.payload["sequence"]),
        node_states=states,
    )


def _owned_run(run_id: UUID, user: User) -> Run:
    run = store.runs.get(run_id)
    if not run or run.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def _configured_definition(definition: WorkflowDefinition, run: Run) -> WorkflowDefinition:
    configured = definition.model_copy(deep=True)
    if run.budget_override:
        configured.budget = run.budget_override
    for node in configured.nodes:
        if node.type == "bounded_loop":
            node.config["max_iterations"] = run.configuration.research_depth
        elif node.type == "time_guard":
            node.config["max_age_hours"] = run.configuration.evidence_freshness_hours
        if not run.configuration.allow_degraded:
            node.failure_policy = FailurePolicy.REQUIRED
    analyst_nodes = {
        "market": "market_analyst",
        "fundamentals": "fundamental_analyst",
        "news": "news_analyst",
        "sentiment": "sentiment_analyst",
    }
    removed = {
        node_id
        for analyst, node_id in analyst_nodes.items()
        if analyst not in run.configuration.analysts
    }
    configured.nodes = [node for node in configured.nodes if node.id not in removed]
    configured.edges = [
        edge
        for edge in configured.edges
        if edge.source not in removed and edge.target not in removed
    ]
    return configured


def _workflow_response(record: dict[str, object]) -> dict[str, object]:
    return {
        "id": record["id"],
        "owner_id": record["owner_id"],
        "definition": record["definition"],
        "version": record["version"],
        "published_version_id": record["published_version_id"],
    }
