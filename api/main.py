from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.providers import DummyProvider
from core.storm_runner import StormPackLoader, StormRunner

app = FastAPI(title="AIstormfy API", version="0.1")


class RunStormRequest(BaseModel):
    pack_id: str
    user_input: str
    context: Optional[Dict[str, Any]] = None


class RunStormResponse(BaseModel):
    transcript: Any
    deliverables: Dict[str, Any]


def build_runner() -> StormRunner:
    provider_registry = {"default": DummyProvider()}
    default_model = "dummy"
    return StormRunner(provider_registry=provider_registry, default_model=default_model)


@app.post("/run_storm", response_model=RunStormResponse)
async def run_storm(body: RunStormRequest) -> RunStormResponse:
    loader = StormPackLoader()
    try:
        pack = loader.load(body.pack_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    runner = build_runner()
    result = runner.run(pack, user_input=body.user_input, context=body.context)
    return RunStormResponse(
        transcript=[turn.__dict__ for turn in result.transcript],
        deliverables=result.deliverables,
    )
