<<<<<<< HEAD
# BioMesh
BioMesh: Biotech research intelligence platform implementing Google's full A2A (Agent-to-Agent) protocol spec. Four specialized agents (Arxiv, OpenFDA, Analysis, Summary) register via Agent Cards, chain via A2A task lifecycle, and synthesize clinical research reports. Built with FastAPI, Gradio, LangChain, Groq. Deployed on HuggingFace Spaces.
=======
# File: README.md
# BioMesh

Biotech research intelligence powered by Google's A2A protocol.

BioMesh is a multi-agent orchestration platform for biotech research workflows. It chains specialized agents to search arXiv, query OpenFDA, synthesize evidence, and generate a clinical executive summary. The orchestrator acts as an A2A client, reads agent cards, manages task lifecycle, and returns a final research report through a FastAPI backend and a Gradio interface.

## What BioMesh Does

BioMesh solves a common research bottleneck: biotech teams often need to gather literature, check drug-label evidence, and synthesize the result into something usable for scientific or clinical decision-making. Instead of forcing one monolithic model to do everything, BioMesh splits the work across specialized agents and coordinates them through A2A-style task exchange.

The result is a traceable pipeline with intermediate artifacts for literature, regulatory context, analysis, and executive summary.

## A2A Concepts

### Agent Card

```python
from a2a.protocol import AgentCard

card = AgentCard(
    name="ArxivAgent",
    description="Searches arXiv for biotech research.",
    url="http://127.0.0.1:8000/.well-known/arxivagent.json",
)
```

### Executor

```python
from a2a.executor import AgentExecutor

class MyExecutor(AgentExecutor):
    def execute(self, task):
        return self.build_artifact("Result", "Done")
```

### Client

```python
from a2a.client import A2AClient

client = A2AClient()
response = client.send_message("ArxivAgent", "CRISPR cancer therapy", "context-123")
```

### Task Lifecycle

```python
from a2a.protocol import TaskState

states = [
    TaskState.SUBMITTED,
    TaskState.WORKING,
    TaskState.COMPLETED,
]
```

### Artifacts

```python
from a2a.protocol import Artifact

artifact = Artifact(type="biotech_analysis", title="Analysis", content="Key findings...")
```

## Architecture

```text
User
  ↓
Gradio UI
  ↓
FastAPI /orchestrate
  ↓
Orchestrator (A2A Client)
  ↓
ArxivAgent → OpenFDAAgent → AnalysisAgent → SummaryAgent
  ↓
Final synthesized clinical summary + task trace + agent cards
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| Runtime | Python 3.11 |
| Package management | uv |
| API server | FastAPI |
| UI | Gradio |
| HTTP client | httpx |
| Data validation | Pydantic |
| Research retrieval | arxiv, requests |
| LLM integration | langchain-groq |
| Deployment | HuggingFace Spaces, Docker |

## Getting Started

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create the project:

```bash
uv init BioMesh
cd BioMesh
```

Create a virtual environment:

```bash
uv venv
```

Install dependencies:

```bash
uv sync
```

Run the project:

```bash
uv run main.py
```

Add a package:

```bash
uv add <package>
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

Set `GROQ_API_KEY` in `.env` if you want LLM-backed summaries. If the key is not present, the pipeline still runs with deterministic fallback text.

## API Reference

### `POST /orchestrate`

Request body:

```json
{
  "topic": "CRISPR cancer therapy"
}
```

Response includes:

- `context_id`
- `arxiv`
- `openfda`
- `analysis`
- `summary`
- `agent_cards`

### `GET /agents`

Returns all registered agent cards.

### `GET /.well-known/{agent_name}.json`

Returns the agent card for a specific agent.

### `GET /status`

Health check showing registered agents.

## Project Structure

```text
BioMesh/
├── a2a/
│   ├── __init__.py
│   ├── protocol.py
│   ├── executor.py
│   ├── client.py
│   └── registry.py
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── arxiv_agent.py
│   ├── openfda_agent.py
│   ├── analysis_agent.py
│   ├── summary_agent.py
│   └── orchestrator.py
├── app/
│   ├── __init__.py
│   └── api.py
├── ui.py
├── main.py
├── .env.example
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── README.md
```

## HuggingFace Deployment

1. Push the repository to HuggingFace Spaces.
2. Choose a Docker Space so the `Dockerfile` is used directly.
3. Add `GROQ_API_KEY` as a Space secret if you want live Groq summaries.
4. Ensure the app listens on port `7860`; BioMesh does this through Gradio.
5. Commit `uv.lock` so dependency resolution stays reproducible.

## A2A Protocol Notes

BioMesh implements an A2A-style workflow with explicit agent cards, task objects, artifacts, and a shared registry-backed client. The orchestrator uses a single context ID across chained tasks so every step is traceable. The implementation is designed to be straightforward to deploy while still exposing the core A2A concepts needed for agent interoperability.
>>>>>>> fc88d11 (Intial Biomesh files pushed)
