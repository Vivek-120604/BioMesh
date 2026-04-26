# File: agents/base.py
"""Shared helpers for BioMesh agents."""
from __future__ import annotations

import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

try:
    from langchain_groq import ChatGroq
except Exception:  # pragma: no cover - optional at runtime for offline fallback
    ChatGroq = None

from a2a.executor import AgentExecutor
from a2a.protocol import AgentCard, AgentSkill, Artifact, Task


load_dotenv()


class BaseBiotechAgent(AgentExecutor):
    model_name = "llama3-8b-8192"

    def __init__(self, name: str, description: str, artifact_type: str, skill_name: str, skill_description: str) -> None:
        super().__init__(name=name, description=description, artifact_type=artifact_type)
        self.card = AgentCard(
            name=name,
            description=description,
            url=f"http://127.0.0.1:8000/.well-known/{name.lower()}.json",
            skills=[AgentSkill(id=name.lower(), name=skill_name, description=skill_description)],
            metadata={"artifact_type": artifact_type},
        )

    def _summarize(self, prompt: str, temperature: float = 0.2) -> str:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if ChatGroq is not None and api_key:
            llm = ChatGroq(api_key=api_key, model_name=self.model_name, temperature=temperature)
            response = llm.invoke(prompt)
            return getattr(response, "content", str(response))
        return prompt.strip()

    def _section(self, title: str, body: str) -> str:
        return f"## {title}\n\n{body.strip()}"

    def _clean_lines(self, value: str) -> str:
        return "\n".join(line.rstrip() for line in value.splitlines()).strip()

    def build_output(self, title: str, body: str, metadata: Dict[str, Any] | None = None) -> Artifact:
        return self.build_artifact(title=title, content=self._clean_lines(body), metadata=metadata or {})

    def execute(self, task: Task) -> Artifact:
        raise NotImplementedError
