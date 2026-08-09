import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from omnitrade.contracts import NodeStatus, Run, RunStatus
from omnitrade.engine.executors import deterministic_executors
from omnitrade.engine.runtime import WorkflowRuntime
from omnitrade.sample_workflow import defense_workflow


def make_run():
    return Run(
        workflow_version_id=uuid4(),
        owner_id=uuid4(),
        ticker="AAPL",
        as_of=datetime.now(UTC) - timedelta(minutes=1),
    )


def test_runtime_completes_and_is_deterministic():
    async def scenario():
        graph = defense_workflow()
        result = await WorkflowRuntime(deterministic_executors()).execute(graph, make_run())
        assert result.run.status == RunStatus.SUCCEEDED
        assert all(n.status.value == "succeeded" for n in result.node_runs.values())
        assert any(e.event_type == "node.loop_iteration" for e in result.events)
        assert result.checkpoints

    asyncio.run(scenario())


def test_optional_failure_degrades_run():
    async def scenario():
        graph = defense_workflow()
        node = next(n for n in graph.nodes if n.id == "sentiment")
        node.config["simulate"] = "failure"
        result = await WorkflowRuntime(deterministic_executors()).execute(graph, make_run())
        assert result.run.status == RunStatus.DEGRADED
        assert result.node_runs["sentiment"].status.value == "degraded"

    asyncio.run(scenario())


def test_required_failure_stops_run():
    async def scenario():
        graph = defense_workflow()
        next(n for n in graph.nodes if n.id == "market").config["simulate"] = "failure"
        result = await WorkflowRuntime(deterministic_executors()).execute(graph, make_run())
        assert result.run.status == RunStatus.FAILED
        assert any(n.status.value == "skipped" for n in result.node_runs.values())

    asyncio.run(scenario())


def test_timeout_uses_fallback():
    async def scenario():
        graph = defense_workflow()
        next(n for n in graph.nodes if n.id == "market").config["simulate"] = "timeout"
        result = await WorkflowRuntime(deterministic_executors()).execute(graph, make_run())
        assert result.run.status == RunStatus.SUCCEEDED
        assert any(e.event_type == "provider.fallback" for e in result.events)

    asyncio.run(scenario())


def test_cancellation_probe_stops_pending_nodes():
    async def scenario():
        async def cancelled(_run_id):
            return True

        result = await WorkflowRuntime(
            deterministic_executors(), cancellation_probe=cancelled
        ).execute(defense_workflow(), make_run())
        assert result.run.status == RunStatus.CANCELLED
        assert all(state.status.value == "cancelled" for state in result.node_runs.values())

    asyncio.run(scenario())


def test_failed_run_resumes_from_checkpoint_without_repeating_successes():
    async def scenario():
        graph = defense_workflow()
        next(node for node in graph.nodes if node.id == "market").config["simulate"] = "failure"
        first = await WorkflowRuntime(deterministic_executors()).execute(graph, make_run())
        checkpoint = first.checkpoints[-1]
        completed_before = {
            node_id
            for node_id, state in checkpoint.node_states.items()
            if state.status.value == "succeeded"
        }
        for state in checkpoint.node_states.values():
            if state.status.value == "failed":
                state.status = NodeStatus.PENDING
                state.error = None
        next(node for node in graph.nodes if node.id == "market").config.pop("simulate")
        second = await WorkflowRuntime(deterministic_executors()).execute(
            graph, first.run, restored=checkpoint
        )
        assert second.run.status == RunStatus.SUCCEEDED
        restarted = {event.node_id for event in second.events if event.event_type == "node.started"}
        assert completed_before.isdisjoint(restarted)

    asyncio.run(scenario())
