import asyncio
from datetime import UTC, datetime

import pytest

from omnitrade.providers import (
    AlphaVantageProvider,
    ProviderError,
    fetch_from_chain,
)


def test_real_provider_chain_never_inserts_recorded_data(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenNodeProvider:
        async def fetch_node(self, node_type: str, ticker: str, as_of: datetime):
            raise ProviderError("real source unavailable")

    monkeypatch.setattr("omnitrade.providers.live_provider", lambda name, settings: BrokenNodeProvider())
    with pytest.raises(ProviderError, match="All selected real providers failed"):
        asyncio.run(fetch_from_chain("fetch_market", "AAPL", datetime.now(UTC), ["yfinance", "alpha_vantage"], {}))


def test_alpha_vantage_market_normalization_blocks_look_ahead() -> None:
    provider = AlphaVantageProvider("test")
    body = {
        "Time Series (Daily)": {
            f"2026-01-{day:02d}": {
                "1. open": str(100 + day),
                "2. high": str(102 + day),
                "3. low": str(99 + day),
                "4. close": str(101 + day),
                "5. volume": str(1_000_000 + day),
            }
            for day in range(1, 32)
        }
    }
    result = provider._normalize(
        "fetch_market", "IBM", datetime(2026, 1, 25, 12, tzinfo=UTC), body
    )
    assert result["bars"][-1]["date"] == "2026-01-25"
    assert all(item["date"] <= "2026-01-25" for item in result["bars"])
