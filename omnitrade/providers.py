from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import httpx


class Provider(Protocol):
    name: str

    async def fetch(self, ticker: str, as_of: datetime) -> dict[str, Any]: ...


class ProviderError(RuntimeError):
    pass


@dataclass
class RecordedProvider:
    name: str
    records: dict[str, dict[str, Any]]

    async def fetch(self, ticker: str, as_of: datetime) -> dict[str, Any]:
        if ticker not in self.records:
            raise ProviderError(f"No recorded data for {ticker}")
        return {
            **self.records[ticker],
            "ticker": ticker,
            "as_of": as_of.isoformat(),
            "provider": self.name,
        }


@dataclass
class HttpJsonProvider:
    name: str
    base_url: str
    api_key: str
    timeout_seconds: float = 10

    async def fetch(self, ticker: str, as_of: datetime) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(
                self.base_url,
                params={"symbol": ticker, "as_of": as_of.isoformat()},
                headers=headers,
            )
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict):
                raise ProviderError("Provider response must be a JSON object")
            return {**body, "provider": self.name}


async def fetch_with_policy(
    primary: Provider,
    fallback: Provider,
    ticker: str,
    as_of: datetime,
    attempts: int = 2,
    backoff_seconds: float = 0.05,
) -> tuple[dict[str, Any], bool]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await primary.fetch(ticker, as_of), False
        except (httpx.HTTPError, ProviderError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                await asyncio.sleep(backoff_seconds * (2**attempt))
    try:
        return await fallback.fetch(ticker, as_of), True
    except Exception as exc:
        raise ProviderError(f"Primary and fallback providers failed: {last_error}; {exc}") from exc
