# File: agents/summary_agent.py
"""Summary agent for BioMesh."""
from __future__ import annotations

from a2a.registry import registry
from a2a.protocol import Artifact, Task
from .base import BaseBiotechAgent


class SummaryExecutor(BaseBiotechAgent):
    def __init__(self) -> None:
        super().__init__(
            name="SummaryAgent",
            description="Produces a structured clinical executive summary from analysis output.",
            artifact_type="clinical_summary",
            skill_name="Clinical Executive Summary",
            skill_description="Produces an executive summary with findings, FDA drugs, gaps, and next steps.",
        )

    def execute(self, task: Task) -> Artifact:
        input_text = task.input_message.as_text().strip()
        prompt = (
            "You are SummaryAgent. Produce a structured clinical executive summary with the exact sections: "
            "Executive Summary, Key Research Findings, Relevant FDA-Approved Drugs, Critical Gaps & Opportunities, "
            "Recommended Next Steps. Use concise clinical language.\n\n"
            + input_text
        )
        summary = self._summarize(prompt, temperature=0.3)
        content = self._clean_lines(summary)
        return self.build_output("Clinical Executive Summary", content, {"temperature": 0.3})


SummaryAgent = SummaryExecutor


if not registry.cards.get("summaryagent"):
    registry.register("SummaryAgent", SummaryExecutor().card, SummaryExecutor())
