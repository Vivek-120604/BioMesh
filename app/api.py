# File: app/api.py
"""FastAPI endpoints for BioMesh."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from a2a.registry import registry
from agents.orchestrator import ensure_agents_registered, run_orchestration


class OrchestrateRequest(BaseModel):
    topic: str


ensure_agents_registered()

app = FastAPI(title="BioMesh API", version="1.0.0")


@app.get("/status")
def status() -> dict:
    return {"ok": True, "service": "BioMesh", "agents": registry.list_agents()}


@app.get("/agents")
def agents() -> dict:
    return {"agents": [card.model_dump() for card in registry.all_cards()]}


@app.get("/.well-known/{agent_name}.json")
def agent_card(agent_name: str) -> dict:
    try:
        return registry.get_card(agent_name).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/orchestrate")
def orchestrate(request: OrchestrateRequest) -> dict:
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")
    return run_orchestration(request.topic.strip())
