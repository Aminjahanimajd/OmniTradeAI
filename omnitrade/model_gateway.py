from __future__ import annotations

import json
from typing import Protocol, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ModelClient(Protocol):
    async def complete(self, prompt: str) -> str: ...


class InvalidModelOutput(RuntimeError):
    pass


class DeterministicFakeModel:
    def __init__(self, response: dict[str, object]):
        self.response = response

    async def complete(self, prompt: str) -> str:
        return json.dumps(self.response, sort_keys=True)


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout_seconds: float = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def complete(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            return str(response.json()["choices"][0]["message"]["content"])


async def typed_completion(client: ModelClient, prompt: str, output_type: type[T]) -> T:
    raw = await client.complete(prompt)
    try:
        return output_type.model_validate_json(raw)
    except (ValidationError, ValueError) as exc:
        raise InvalidModelOutput(f"Model output failed {output_type.__name__} validation") from exc
