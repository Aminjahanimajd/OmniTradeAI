import asyncio

import pytest
from pydantic import BaseModel

from omnitrade.model_gateway import DeterministicFakeModel, InvalidModelOutput, typed_completion


class Output(BaseModel):
    score: float


def test_typed_model_output():
    assert (
        asyncio.run(typed_completion(DeterministicFakeModel({"score": 0.7}), "x", Output)).score
        == 0.7
    )


def test_bad_model_output_is_rejected():
    with pytest.raises(InvalidModelOutput):
        asyncio.run(typed_completion(DeterministicFakeModel({"wrong": 1}), "x", Output))
