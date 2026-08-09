from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from omnitrade.contracts import NodeDefinition
from omnitrade.engine.catalog import NODE_CATALOG
from omnitrade.engine.runtime import ExecutionContext, NodeExecutor


async def deterministic_executor(
    node: NodeDefinition, inputs: dict[str, Any], context: ExecutionContext
) -> Any:
    """Fixture executor used in CI and the defense scenario."""
    delay_ms = int(node.config.get("delay_ms", 0))
    if delay_ms:
        await asyncio.sleep(min(delay_ms, 10_000) / 1000)
    if node.config.get("simulate") == "timeout" and "_fallback_provider" not in inputs:
        raise TimeoutError("primary provider timed out")
    if node.config.get("simulate") == "failure":
        raise RuntimeError("simulated optional source failure")

    spec = NODE_CATALOG[node.type]
    if spec.provider_cost:
        context.spend_provider_call()
        await asyncio.sleep(0.05)
    if spec.model_cost:
        context.spend_model_call(tokens=250)
        await asyncio.sleep(0.12)

    if node.type == "start":
        return {"started": True}
    if node.type == "resolve_instrument":
        return {"ticker": context.run.ticker, "exchange": "NASDAQ", "currency": "USD"}
    if node.type.startswith("fetch_"):
        return fixture_provider_payload(node.type, context.run.ticker, context.run.as_of)
    if node.type.startswith("normalize_") or node.type in {"time_guard", "join", "parallel_split"}:
        return {"normalized": True, "inputs": inputs}
    if node.type in {"technical_indicators", "fundamental_ratios"}:
        return {"kind": node.type, "score": 0.62, "source": inputs}
    if node.type.endswith("_analyst"):
        profiles: dict[str, dict[str, Any]] = {
            "market_analyst": {
                "viewpoint": "MILDLY BULLISH",
                "confidence": 0.72,
                "summary": f"The market view for {context.run.ticker} is mildly positive. Price data is stable and the calculated technical score is above neutral, but the short recorded series is not enough for a strong BUY signal.",
                "key_points": ["Technical score is 0.62, above the neutral midpoint.", "Recent recorded prices are stable rather than strongly trending.", "The short sample lowers confidence in momentum."],
                "risks": ["A short price series can hide volatility and regime changes."],
            },
            "fundamental_analyst": {
                "viewpoint": "NEUTRAL TO POSITIVE",
                "confidence": 0.70,
                "summary": f"The fundamental branch finds a stable financial picture for {context.run.ticker}. The normalized ratio score supports quality, but the recorded demonstration data does not justify an aggressive valuation conclusion.",
                "key_points": ["Fundamental ratio score is 0.62.", "The available company evidence does not show a critical weakness.", "Valuation certainty is limited by the recorded fixture scope."],
                "risks": ["Incomplete statements and sector comparisons can change the valuation view."],
            },
            "news_analyst": {
                "viewpoint": "NEUTRAL",
                "confidence": 0.64,
                "summary": f"The news and macro evidence for {context.run.ticker} is mixed. No single recorded event is strong enough to override the market and fundamental branches.",
                "key_points": ["No dominant positive or negative catalyst was detected.", "Macro context remains an uncertainty for the final decision.", "News evidence is treated as time-sensitive."],
                "risks": ["New events after the analysis time are outside this report."],
            },
            "sentiment_analyst": {
                "viewpoint": "NEUTRAL",
                "confidence": 0.61,
                "summary": f"The sentiment branch for {context.run.ticker} does not show a reliable extreme. It supports caution and should not determine the decision without price and fundamental evidence.",
                "key_points": ["Sentiment is not strongly polarized.", "Sentiment has lower decision weight than validated market evidence.", "The signal may change quickly."],
                "risks": ["Social signals can contain noise, duplication, and manipulation."],
            },
        }
        profile = profiles[node.type]
        return {
            "specialist": node.type,
            **profile,
            "evidence_refs": _content_hashes(inputs),
            "claims": [
                {
                    "text": point,
                    "confidence": profile["confidence"],
                    "evidence_refs": _content_hashes(inputs),
                }
                for point in profile["key_points"]
            ],
        }
    if node.type in {"bull_researcher", "bear_researcher"}:
        bull = node.type == "bull_researcher"
        return {
            "position": "bull" if bull else "bear",
            "confidence": 0.66 if bull else 0.63,
            "summary": (
                "The positive case argues that stable price behavior, an above-neutral technical score, and acceptable fundamentals support patient upside."
                if bull
                else "The negative case argues that limited evidence depth, mixed external signals, and uncertain valuation make a strong directional trade unsafe."
            ),
            "key_points": (
                ["Technical and fundamental scores are above neutral.", "No severe negative catalyst is present.", "A HOLD position keeps exposure to possible upside."]
                if bull
                else ["The evidence sample is short and recorded.", "News and sentiment do not confirm strong momentum.", "Uncertainty can produce downside if conditions change."]
            ),
            "risks_or_counters": (
                ["The bear case correctly identifies limited evidence depth."]
                if bull
                else ["The bull case correctly notes that current evidence is not clearly negative."]
            ),
        }
    if node.type == "research_manager":
        return {
            "round": 1,
            "cases": inputs,
            "stopped": True,
            "agreement": "Both sides support caution rather than a strong directional action.",
            "summary": "The research manager gives more weight to evidence quality than to optimism or fear. The bull case supports keeping exposure, while the bear case prevents a high-confidence BUY. HOLD is the balanced proposal.",
        }
    if node.type == "bounded_loop":
        return {"round": 1, "cases": inputs, "stopped": True}
    if node.type == "proposal_builder":
        return {
            "action": "HOLD",
            "confidence": 0.68,
            "summary": "Keep the position unchanged until stronger market, fundamental, or catalyst evidence creates a clearer risk-adjusted direction.",
            "conditions": ["Reassess when new financial statements or material news arrive.", "Change to BUY only when positive evidence is confirmed across independent branches.", "Change to SELL if risk evidence becomes strong and persistent."],
            "basis": inputs,
        }
    if node.type.endswith("_risk"):
        risk_profile = node.type.removesuffix("_risk")
        views = {
            "aggressive": {"stance": "ACCEPT", "confidence": 0.67, "summary": "An aggressive user can accept the HOLD proposal because it keeps upside exposure without increasing the position.", "impact": "Supports HOLD and would allow BUY only after a stronger bullish confirmation.", "key_points": ["Upside remains possible.", "No new capital is committed."]},
            "balanced": {"stance": "SUPPORT", "confidence": 0.75, "summary": "The balanced view supports HOLD because positive and negative evidence are close and uncertainty remains material.", "impact": "Provides the main risk-policy support for the final HOLD decision.", "key_points": ["Evidence is mixed.", "Current exposure should remain unchanged."]},
            "conservative": {"stance": "CAUTIOUS", "confidence": 0.71, "summary": "The conservative view accepts HOLD only with monitoring. It rejects increasing exposure while evidence depth is limited.", "impact": "Reduces confidence and adds a warning against a new BUY position.", "key_points": ["Capital protection has priority.", "Limited data requires a wider safety margin."]},
        }
        return {
            "profile": risk_profile,
            "max_risk": 0.4,
            "proposal": inputs,
            **views[risk_profile],
        }
    if node.type == "risk_join":
        return {"views": inputs}
    if node.type == "decision_validator":
        return {
            "action": "HOLD",
            "confidence": 0.68,
            "rationale": "The combined analyst, debate, and risk views do not support a strong directional action.",
            "key_factors": ["mixed evidence", "balanced risk review", "bounded research debate"],
            "warnings": ["Decision support only"],
            "inputs": inputs,
        }
    if node.type == "report_renderer":
        decision = inputs.get("decision", inputs)
        if isinstance(decision, dict) and isinstance(decision.get("decision"), dict):
            decision = decision["decision"]
        configuration = context.run.configuration
        return {
            "report_version": "1.0",
            "title": f"OmniTrade report for {context.run.ticker}",
            "ticker": context.run.ticker,
            "as_of": context.run.as_of.isoformat(),
            "generated_at": datetime.now(UTC).isoformat(),
            "executive_summary": (
                f"OmniTrade recommends {decision.get('action', 'NO_DECISION')} with "
                f"{float(decision.get('confidence', 0)):.0%} confidence after parallel evidence, "
                "research debate, and three risk views."
            ),
            "decision": {
                "action": decision.get("action", "NO_DECISION"),
                "confidence": decision.get("confidence", 0),
                "rationale": decision.get("rationale", "No rationale was produced."),
                "key_factors": decision.get("key_factors", []),
                "warnings": decision.get("warnings", []),
            },
            "sections": [
                {"title": "Market and technical analysis", "summary": "Price evidence and technical indicators were normalized and reviewed."},
                {"title": "Fundamental analysis", "summary": "Company data and financial ratios were checked as a separate evidence branch."},
                {"title": "News and sentiment", "summary": "Text evidence was compared with market evidence when the selected analysts were enabled."},
                {"title": "Research debate", "summary": f"Bull and bear cases used a bounded debate of up to {configuration.research_depth} rounds."},
                {"title": "Risk review", "summary": f"Aggressive, neutral, and conservative views were merged for a {configuration.risk_profile} user profile."},
            ],
            "analysis_settings": configuration.model_dump(mode="json"),
            "lineage_complete": True,
            "disclaimer": "Financial decision support only. OmniTrade does not execute trades.",
        }
    if node.type == "end":
        return inputs.get("report")
    return inputs


def fixture_provider_payload(kind: str, ticker: str, as_of: datetime) -> dict[str, Any]:
    payload = {
        "kind": kind,
        "ticker": ticker,
        "observed_at": (as_of - timedelta(hours=1)).astimezone(UTC).isoformat(),
        "retrieved_at": datetime.now(UTC).isoformat(),
        "provider": "omnitrade-fixture-v1",
        "currency": "USD",
        "unit": "provider-specific",
        "values": [100.0, 101.5, 100.8],
    }
    payload["content_hash"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()
    return payload


def deterministic_executors() -> dict[str, NodeExecutor]:
    return {node_type: deterministic_executor for node_type in NODE_CATALOG}


def _content_hashes(value: Any) -> list[str]:
    found: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            content_hash = item.get("content_hash")
            if isinstance(content_hash, str) and content_hash not in found:
                found.append(content_hash)
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return found
