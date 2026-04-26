# File: ui.py
"""Gradio UI for BioMesh."""
from __future__ import annotations

import json

import gradio as gr
import httpx

API_BASE = "http://127.0.0.1:8000"


def run_pipeline(topic: str):
    topic = (topic or "").strip()
    if not topic:
        return "Enter a biotech research topic.", "", "", "", "", ""
    try:
        response = httpx.post(f"{API_BASE}/orchestrate", json={"topic": topic}, timeout=300)
        response.raise_for_status()
        payload = response.json()
        summary = payload["summary"]["artifact"]["content"] if payload["summary"].get("artifact") else "No summary returned."
        arxiv = payload["arxiv"]["artifact"]["content"] if payload["arxiv"].get("artifact") else "No arXiv output returned."
        fda = payload["openfda"]["artifact"]["content"] if payload["openfda"].get("artifact") else "No FDA output returned."
        analysis = payload["analysis"]["artifact"]["content"] if payload["analysis"].get("artifact") else "No analysis returned."
        pipeline = json.dumps(
            {
                "context_id": payload["context_id"],
                "arxiv_task": payload["arxiv"]["task"]["task_id"],
                "fda_task": payload["openfda"]["task"]["task_id"],
                "analysis_task": payload["analysis"]["task"]["task_id"],
                "summary_task": payload["summary"]["task"]["task_id"],
                "states": {
                    "arxiv": payload["arxiv"]["task"]["status"]["state"],
                    "fda": payload["openfda"]["task"]["status"]["state"],
                    "analysis": payload["analysis"]["task"]["status"]["state"],
                    "summary": payload["summary"]["task"]["status"]["state"],
                },
            },
            indent=2,
        )
        return "Pipeline completed successfully.", summary, arxiv, fda, analysis, pipeline
    except Exception as exc:
        return f"Pipeline failed: {exc}", "", "", "", "", ""


def load_cards() -> str:
    response = httpx.get(f"{API_BASE}/agents", timeout=30)
    response.raise_for_status()
    payload = response.json().get("agents", [])
    blocks = []
    for card in payload:
        blocks.append(
            f"### {card['name']}\n\n"
            f"- Description: {card['description']}\n"
            f"- Version: {card['version']}\n"
            f"- URL: {card['url']}\n"
            f"- Skills: {', '.join(skill['name'] for skill in card.get('skills', [])) or 'None'}\n"
        )
    return "\n\n".join(blocks) if blocks else "No agent cards registered."


def build_demo() -> gr.Blocks:
    with gr.Blocks(theme=gr.themes.Soft(), title="BioMesh — Biotech Multi-Agent Research Platform") as demo:
        gr.Markdown("# BioMesh — Biotech Multi-Agent Research Platform")
        with gr.Tabs():
            with gr.Tab("Research"):
                topic = gr.Textbox(label="Biotech Research Topic", placeholder="e.g. CRISPR cancer therapy")
                run_button = gr.Button("Run BioMesh Pipeline")
                status = gr.Textbox(label="Status")
                summary = gr.Textbox(label="Clinical Summary (SummaryAgent)", lines=15)
                with gr.Accordion("Arxiv Research (ArxivAgent output)", open=False):
                    arxiv_output = gr.Textbox(lines=15)
                with gr.Accordion("FDA Drug Data (OpenFDAAgent output)", open=False):
                    fda_output = gr.Textbox(lines=15)
                with gr.Accordion("Analysis Report (AnalysisAgent output)", open=False):
                    analysis_output = gr.Textbox(lines=15)
                with gr.Accordion("A2A Task Pipeline (task IDs, context ID, states)", open=False):
                    pipeline_output = gr.Textbox(lines=15)
                run_button.click(
                    run_pipeline,
                    inputs=[topic],
                    outputs=[status, summary, arxiv_output, fda_output, analysis_output, pipeline_output],
                )
            with gr.Tab("Agent Cards"):
                load_button = gr.Button("Load Agent Cards")
                cards_output = gr.Markdown()
                load_button.click(load_cards, inputs=None, outputs=[cards_output])
    return demo


demo = build_demo()
