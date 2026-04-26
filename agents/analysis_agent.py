# File: agents/analysis_agent.py
"""Analysis agent for BioMesh."""
from __future__ import annotations

from a2a.registry import registry
from a2a.protocol import Artifact, Task
from .base import BaseBiotechAgent


class AnalysisExecutor(BaseBiotechAgent):
    def __init__(self) -> None:
        super().__init__(
            name="AnalysisAgent",
            description="Synthesizes arXiv and OpenFDA evidence into biotech analysis.",
            artifact_type="biotech_analysis",
            skill_name="Biotech Evidence Analysis",
            skill_description="Identifies research gaps, drug-research alignment, promising directions, and risk factors.",
        )

    def execute(self, task: Task) -> Artifact:
        input_text = task.input_message.as_text().strip()
        prompt = (
            "You are AnalysisAgent. Analyze the combined arXiv and FDA evidence below. "
            "Identify research gaps, drug-research alignment, promising directions, and key risk factors.\n\n"
            + input_text
        )
        summary = self._summarize(prompt, temperature=0.2)
        content = self._section("Biotech Analysis", summary)
        return self.build_output("Biotech Analysis", content, {"source": "combined_evidence"})


AnalysisAgent = AnalysisExecutor


if not registry.cards.get("analysisagent"):
    registry.register("AnalysisAgent", AnalysisExecutor().card, AnalysisExecutor())
