# File: agents/arxiv_agent.py
"""Arxiv agent for BioMesh."""
from __future__ import annotations

import textwrap
from typing import List
from xml.etree import ElementTree as ET

import requests

from a2a.registry import registry
from a2a.protocol import Artifact, Task
from .base import BaseBiotechAgent


class ArxivExecutor(BaseBiotechAgent):
    def __init__(self) -> None:
        super().__init__(
            name="ArxivAgent",
            description="Searches arXiv and summarizes recent biotech research.",
            artifact_type="arxiv_research",
            skill_name="arXiv Research",
            skill_description="Searches arXiv for biotech research and extracts high-signal paper summaries.",
        )

    def _fetch_papers(self, topic: str, max_results: int = 5) -> List[dict]:
        query = requests.utils.quote(topic)
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
            summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
            authors = [author.findtext("atom:name", default="", namespaces=ns).strip() for author in entry.findall("atom:author", ns)]
            papers.append({"title": title, "summary": summary, "authors": authors})
        return papers

    def execute(self, task: Task) -> Artifact:
        topic = task.input_message.as_text().strip()
        papers = self._fetch_papers(topic)
        if not papers:
            content = self._section(
                "Arxiv Research",
                f"No arXiv results were returned for: {topic}",
            )
            return self.build_output("Arxiv Research", content, {"topic": topic, "papers": []})

        paper_blocks = []
        for index, paper in enumerate(papers[:5], start=1):
            authors = ", ".join(paper["authors"]) if paper["authors"] else "Unknown authors"
            paper_blocks.append(
                textwrap.dedent(
                    f"""
                    Paper {index}
                    Title: {paper['title']}
                    Authors: {authors}
                    Abstract: {paper['summary']}
                    """
                ).strip()
            )
        prompt = (
            "You are ArxivAgent for a biotech research platform. "
            "Summarize the most relevant findings from these arXiv papers in concise bullet points, "
            "highlighting themes, technical directions, and translational potential.\n\n"
            + "\n\n".join(paper_blocks)
        )
        summary = self._summarize(prompt, temperature=0.2)
        content = self._section(
            "Arxiv Research",
            "\n\n".join(
                [
                    summary,
                    "\n".join(
                        f"- {paper['title']} | {', '.join(paper['authors']) if paper['authors'] else 'Unknown authors'}"
                        for paper in papers[:5]
                    ),
                ]
            ),
        )
        return self.build_output("Arxiv Research", content, {"topic": topic, "papers": papers[:5]})


ArxivAgent = ArxivExecutor


if not registry.cards.get("arxivagent"):
    registry.register("ArxivAgent", ArxivExecutor().card, ArxivExecutor())
