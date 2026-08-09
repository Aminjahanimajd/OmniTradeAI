import asyncio
from datetime import UTC, datetime

from omnitrade.providers import ProviderError, RecordedProvider, fetch_with_policy


class BrokenProvider:
    name = "broken"

    async def fetch(self, ticker: str, as_of: datetime):
        raise ProviderError("timeout")


def test_provider_policy_uses_recorded_fallback() -> None:
    fallback = RecordedProvider("fixture", {"AAPL": {"close": 100}})
    body, degraded = asyncio.run(
        fetch_with_policy(
            BrokenProvider(), fallback, "AAPL", datetime.now(UTC), attempts=2, backoff_seconds=0
        )
    )
    assert degraded is True
    assert body["close"] == 100
