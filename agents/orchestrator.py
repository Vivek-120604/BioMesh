# File: agents/orchestrator.py
"""Orchestrates the BioMesh A2A agent pipeline."""
from __future__ import annotations

from uuid import uuid4

from a2a.client import A2AClient
from a2a.registry import registry

from .analysis_agent import AnalysisExecutor
from .arxiv_agent import ArxivExecutor
from .openfda_agent import OpenFDAExecutor
from .summary_agent import SummaryExecutor


_registered = False


def ensure_agents_registered() -> None:
    global _registered
    if _registered:
        return

    executors = [ArxivExecutor(), OpenFDAExecutor(), AnalysisExecutor(), SummaryExecutor()]
    for executor in executors:
        registry.register(executor.name, executor.card, executor)
    _registered = True


def run_orchestration(topic: str) -> dict:
    ensure_agents_registered()
    client = A2AClient()
    context_id = str(uuid4())

    arxiv_response = client.send_message("ArxivAgent", topic, context_id)
    fda_response = client.send_message("OpenFDAAgent", topic, context_id)
    combined_analysis_input = (
        f"Topic: {topic}\n\n"
        f"Arxiv Findings:\n{arxiv_response.artifact.content if arxiv_response.artifact else arxiv_response.task.output_message.as_text()}\n\n"
        f"OpenFDA Findings:\n{fda_response.artifact.content if fda_response.artifact else fda_response.task.output_message.as_text()}"
    )
    analysis_response = client.send_message("AnalysisAgent", combined_analysis_input, context_id)
    summary_input = analysis_response.artifact.content if analysis_response.artifact else analysis_response.task.output_message.as_text()
    summary_response = client.send_message("SummaryAgent", summary_input, context_id)

    return {
        "context_id": context_id,
        "topic": topic,
        "arxiv": arxiv_response.model_dump(),
        "openfda": fda_response.model_dump(),
        "analysis": analysis_response.model_dump(),
        "summary": summary_response.model_dump(),
        "agent_cards": [card.model_dump() for card in registry.all_cards()],
    }
