from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from omnitrade.config import get_settings
from omnitrade.contracts import (
    Checkpoint,
    NodeDefinition,
    Run,
    RunEvent,
    ValidationResult,
    WorkflowDefinition,
)
from omnitrade.engine.catalog import NODE_CATALOG
from omnitrade.engine.executors import deterministic_executor
from omnitrade.engine.runtime import ExecutionContext, NodeExecutor, WorkflowRuntime
from omnitrade.engine.validator import WorkflowValidator
from omnitrade.infrastructure.events import RedisStreamEventBus


class NodeTask(BaseModel):
    node: NodeDefinition
    inputs: dict[str, Any]
    run: Run


class NodeResult(BaseModel):
    output: Any


class WorkflowTask(BaseModel):
    workflow: WorkflowDefinition
    run: Run
    checkpoint: Checkpoint | None = None


class WorkflowResult(BaseModel):
    run: Run
    nodes: dict[str, dict[str, Any]]
    events: list[RunEvent]
    report: dict[str, Any]


def base_service(name: str) -> FastAPI:
    app = FastAPI(title=f"OmniTrade {name} service")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": name}

    return app


async def execute_task(task: NodeTask) -> NodeResult:
    context = ExecutionContext(run=task.run)
    return NodeResult(output=await deterministic_executor(task.node, task.inputs, context))


evidence_app = base_service("evidence")
model_app = base_service("model-gateway")
report_app = base_service("report")
workflow_app = base_service("workflow")


@evidence_app.post("/internal/nodes/execute", response_model=NodeResult)
async def evidence_execute(task: NodeTask) -> NodeResult:
    group = NODE_CATALOG[task.node.type].group
    if group not in {"evidence", "normalization", "calculation"}:
        raise ValueError(f"Evidence service cannot execute {group} nodes")
    return await execute_task(task)


@model_app.post("/internal/nodes/execute", response_model=NodeResult)
async def model_execute(task: NodeTask) -> NodeResult:
    group = NODE_CATALOG[task.node.type].group
    if group not in {"specialist", "research", "risk"}:
        raise ValueError(f"Model service cannot execute {group} nodes")
    return await execute_task(task)


@report_app.post("/internal/nodes/execute", response_model=NodeResult)
async def report_execute(task: NodeTask) -> NodeResult:
    if NODE_CATALOG[task.node.type].group != "output":
        raise ValueError("Report service accepts output nodes only")
    return await execute_task(task)


def remote_executor(url: str) -> NodeExecutor:
    async def execute(
        node: NodeDefinition, inputs: dict[str, Any], context: ExecutionContext
    ) -> Any:
        spec = NODE_CATALOG[node.type]
        if spec.provider_cost:
            context.spend_provider_call()
        if spec.model_cost:
            context.spend_model_call(tokens=250)
        async with httpx.AsyncClient(timeout=node.timeout_seconds + 2) as client:
            response = await client.post(
                url,
                json=NodeTask(node=node, inputs=inputs, run=context.run).model_dump(mode="json"),
            )
            response.raise_for_status()
            return NodeResult.model_validate(response.json()).output

    return execute


def distributed_executors() -> dict[str, NodeExecutor]:
    routes = {
        "evidence": remote_executor("http://evidence:8002/internal/nodes/execute"),
        "normalization": remote_executor("http://evidence:8002/internal/nodes/execute"),
        "calculation": remote_executor("http://evidence:8002/internal/nodes/execute"),
        "specialist": remote_executor("http://model-gateway:8003/internal/nodes/execute"),
        "research": remote_executor("http://model-gateway:8003/internal/nodes/execute"),
        "risk": remote_executor("http://model-gateway:8003/internal/nodes/execute"),
        "output": remote_executor("http://report:8004/internal/nodes/execute"),
    }
    return {
        node_type: routes.get(spec.group, deterministic_executor)
        for node_type, spec in NODE_CATALOG.items()
    }


@workflow_app.post("/internal/workflows/validate")
def internal_validate(workflow: WorkflowDefinition) -> ValidationResult:
    return WorkflowValidator().validate(workflow)


@workflow_app.post("/internal/runs/execute", response_model=WorkflowResult)
async def workflow_execute(task: WorkflowTask) -> WorkflowResult:
    bus = RedisStreamEventBus(get_settings().redis_url)
    runtime = WorkflowRuntime(
        distributed_executors(),
        listener=bus.publish,
        cancellation_probe=bus.is_cancelled,
    )
    result = await runtime.execute(task.workflow, task.run, restored=task.checkpoint)
    report = result.node_runs.get("report")
    return WorkflowResult(
        run=result.run,
        nodes={key: value.model_dump(mode="json") for key, value in result.node_runs.items()},
        events=result.events,
        report=report.output if report and isinstance(report.output, dict) else {},
    )
