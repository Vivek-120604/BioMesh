# File: agents/openfda_agent.py
"""OpenFDA agent for BioMesh."""
from __future__ import annotations

from typing import List

import requests

from a2a.registry import registry
from a2a.protocol import Artifact, Task
from .base import BaseBiotechAgent


class OpenFDAExecutor(BaseBiotechAgent):
    def __init__(self) -> None:
        super().__init__(
            name="OpenFDAAgent",
            description="Queries OpenFDA drug labels and extracts clinically relevant context.",
            artifact_type="fda_drug_data",
            skill_name="OpenFDA Drug Intelligence",
            skill_description="Searches OpenFDA for labels, indications, and warnings related to a biotech topic.",
        )

    def _fetch_labels(self, topic: str, limit: int = 5) -> List[dict]:
        url = "https://api.fda.gov/drug/label.json"
        params = {"search": topic, "limit": limit}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])[:limit]

    def execute(self, task: Task) -> Artifact:
        topic = task.input_message.as_text().strip()
        try:
            labels = self._fetch_labels(topic)
        except Exception:
            labels = []

        if not labels:
            content = self._section(
                "FDA Drug Data",
                f"No OpenFDA labels were returned for: {topic}",
            )
            return self.build_output("FDA Drug Data", content, {"topic": topic, "labels": []})

        label_blocks = []
        for label in labels[:5]:
            drug_name = (label.get("openfda", {}).get("brand_name") or label.get("openfda", {}).get("generic_name") or ["Unknown drug"])[0]
            indications = " ".join(label.get("indications_and_usage", [])[:2])
            warnings = " ".join(label.get("warnings", [])[:2])
            label_blocks.append(
                f"Drug: {drug_name}\nIndications: {indications or 'Not available'}\nWarnings: {warnings or 'Not available'}"
            )

        prompt = (
            "You are OpenFDAAgent for a biotech research platform. "
            "Summarize the drug-label evidence below with emphasis on approved indications, warnings, and translational relevance.\n\n"
            + "\n\n".join(label_blocks)
        )
        summary = self._summarize(prompt, temperature=0.2)
        content = self._section("FDA Drug Data", summary + "\n\n" + "\n\n".join(label_blocks))
        return self.build_output("FDA Drug Data", content, {"topic": topic, "labels": labels[:5]})


OpenFDAAgent = OpenFDAExecutor


if not registry.cards.get("openfdaagent"):
    registry.register("OpenFDAAgent", OpenFDAExecutor().card, OpenFDAExecutor())
