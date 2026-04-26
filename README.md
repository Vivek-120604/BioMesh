# BioMesh

> Biotech research intelligence powered by Google's A2A protocol.

BioMesh is a multi-agent orchestration platform that implements the full [Google A2A (Agent-to-Agent) protocol specification](https://google.github.io/A2A/). It chains four specialized agents — ArxivAgent, OpenFDAAgent, AnalysisAgent, and SummaryAgent — to transform a single biotech research query into a structured clinical intelligence report in under two minutes.

The orchestrator acts as a compliant A2A Client: it reads Agent Cards, dispatches tasks with full lifecycle management (`submitted → working → completed`), passes typed artifacts between agents, and returns a traceable pipeline result through a FastAPI backend and Gradio interface.

[![HuggingFace Space](https://img.shields.io/badge/🤗%20HuggingFace-BioMesh-blue)](https://huggingface.co/spaces)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![uv](https://img.shields.io/badge/package%20manager-uv-DE5FE9)](https://astral.sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## The Problem BioMesh Solves

A biotech researcher investigating "CRISPR applications in cancer therapy" currently needs to:

1. Search arXiv or PubMed manually — 2 hours
2. Cross-reference with FDA drug label data — 2 hours
3. Identify research-to-approval gaps — 1 hour
4. Write an internal research brief — 2 hours

**Total: 7+ hours per research question.**

BioMesh compresses this to under 2 minutes by distributing the work across four specialized agents coordinated through the A2A protocol.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Query                              │
│               "CRISPR applications in cancer therapy"           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Gradio UI (7860)                         │
│                           ui.py                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │  POST /orchestrate
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Server (8000)                       │
│                         app/api.py                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │  run_orchestration(topic)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│               Orchestrator (A2A Client)                         │
│                    agents/orchestrator.py                       │
│                                                                 │
│   A2AClient → AgentRegistry → AgentExecutor → Task Lifecycle   │
└──────┬───────────────┬──────────────┬──────────────┬───────────┘
       │               │              │              │
       ▼               ▼              ▼              ▼
┌──────────┐   ┌──────────────┐  ┌──────────┐  ┌──────────┐
│  Arxiv   │   │   OpenFDA    │  │ Analysis │  │ Summary  │
│  Agent   │──▶│    Agent     │──▶│  Agent   │──▶│  Agent  │
│          │   │              │  │          │  │          │
│ arxiv.org│   │ api.fda.gov  │  │  Groq    │  │  Groq   │
└──────────┘   └──────────────┘  └──────────┘  └──────────┘
       │               │              │              │
       ▼               ▼              ▼              ▼
  Artifact:       Artifact:       Artifact:      Artifact:
arxiv_research  fda_drug_data  biotech_analysis clinical_summary
```

Each agent exposes an Agent Card at `/.well-known/<agent>.json`. The orchestrator is not an agent — it is the A2A Client, which is the correct pattern per the A2A spec.

---

## A2A Protocol Implementation

BioMesh implements the core A2A specification across five components.

### Agent Card

Each agent registers an Agent Card describing its identity, capabilities, and discovery endpoint. External A2A clients can discover BioMesh agents by fetching `/.well-known/<agent>.json`.

```python
from a2a.protocol import AgentCard, AgentSkill

card = AgentCard(
    name="ArxivAgent",
    description="Searches arXiv for biotech and life sciences research papers.",
    url="http://127.0.0.1:8000/.well-known/arxivagent.json",
    skills=[
        AgentSkill(
            id="arxiv_search",
            name="arXiv Search",
            description="Retrieve and summarize recent papers on a biotech topic.",
        )
    ],
)
```

### Agent Executor

The Executor pattern separates task lifecycle management from agent business logic. Every agent inherits `AgentExecutor` and only implements `execute()`.

```python
from a2a.executor import AgentExecutor
from a2a.protocol import Task, Artifact

class ArxivExecutor(AgentExecutor):
    def execute(self, task: Task, user_input: str) -> Artifact:
        # Business logic only — lifecycle managed by base class
        papers = fetch_arxiv(user_input)
        summary = summarize_with_groq(papers)
        return Artifact(artifactType="arxiv_research", content=summary)
```

### A2A Client

The Orchestrator uses `A2AClient` to discover and dispatch tasks to agents. It never calls agents directly — always through the client interface.

```python
from a2a.client import A2AClient
from a2a.registry import registry

client = A2AClient(registry=registry)
response = client.send_message(
    agent_name="ArxivAgent",
    user_input="CRISPR cancer therapy",
    context_id="biomesh-CRISPR-cancer-therapy",
)
artifact = response.result.artifacts[0]
```

### Task Lifecycle

Every task transitions through defined states. The executor handles transitions automatically — agents never manage state manually.

```python
from a2a.protocol import TaskState

# Automatic lifecycle managed by AgentExecutor.run()
# submitted → working → completed
# submitted → working → failed  (on exception)

task.status.state  # TaskState.COMPLETED
task.status.message  # "Task completed successfully."
task.status.timestamp  # ISO 8601 UTC
```

### Artifacts

Each agent produces a typed artifact. The next agent in the chain receives the artifact content as its input, creating a traceable evidence trail.

```python
from a2a.protocol import Artifact

artifact = Artifact(
    artifactType="arxiv_research",       # typed output
    content="Summarized findings...",    # passed to next agent
    metadata={"topic": "CRISPR", "sources": 5},
)
```

---

## Agent Pipeline

| Agent | Input | Data Source | Output Artifact |
|---|---|---|---|
| ArxivAgent | Research topic | arxiv.org API | `arxiv_research` |
| OpenFDAAgent | Research topic | api.fda.gov | `fda_drug_data` |
| AnalysisAgent | Arxiv + FDA output | Groq LLM | `biotech_analysis` |
| SummaryAgent | Analysis output | Groq LLM | `clinical_summary` |

The AnalysisAgent receives both ArxivAgent and OpenFDAAgent outputs combined — this cross-referencing between literature and approved drugs is the core intelligence of BioMesh.

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Runtime | Python 3.11 | Core language |
| Package manager | uv | Fast dependency resolution |
| API server | FastAPI 0.115 | REST endpoints + Agent Card serving |
| UI | Gradio 4.44 | Research interface |
| HTTP client | httpx | Gradio → FastAPI communication |
| Data validation | Pydantic 2.9 | A2A protocol schemas |
| LLM | Groq (llama3-8b-8192) | Agent reasoning and summarization |
| Research data | arxiv 2.1 | Literature retrieval |
| Drug data | OpenFDA REST API | FDA drug label data |
| Deployment | HuggingFace Spaces | Public hosted demo |
| Container | Docker | Reproducible build |

---

## Getting Started

### Prerequisites

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

```bash
# Clone the repository
git clone https://github.com/Vivek-120604/BioMesh
cd BioMesh

# Create virtual environment
uv venv

# Activate
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# Install dependencies
uv sync
```

### Configuration

```bash
cp .env
```

Open `.env` and set your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### Run

```bash
uv run main.py
```

- Gradio UI: [http://localhost:7860](http://localhost:7860)
- FastAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Agent Cards: [http://localhost:8000/agents](http://localhost:8000/agents)

---

## API Reference

### `POST /orchestrate`

Run the full four-agent pipeline.

**Request:**
```json
{
  "topic": "CRISPR applications in cancer therapy"
}
```

**Response:**
```json
{
  "topic": "CRISPR applications in cancer therapy",
  "context_id": "biomesh-CRISPR-applications-in-c",
  "arxiv": {
    "task_id": "uuid",
    "status": "completed",
    "output": "..."
  },
  "openfda": {
    "task_id": "uuid",
    "status": "completed",
    "output": "..."
  },
  "analysis": {
    "task_id": "uuid",
    "status": "completed",
    "output": "..."
  },
  "summary": {
    "task_id": "uuid",
    "status": "completed",
    "output": "..."
  },
  "agent_cards": [...]
}
```

### `GET /.well-known/{agent_name}.json`

Returns the A2A Agent Card for the specified agent. Compliant with the A2A spec discovery pattern.

**Available agents:** `arxivagent`, `openfdaagent`, `analysisagent`, `summaryagent`

### `GET /agents`

Returns all registered agent cards.

### `GET /status`

Health check showing all registered agents.

```json
{
  "status": "healthy",
  "registered_agents": ["ArxivAgent", "OpenFDAAgent", "AnalysisAgent", "SummaryAgent"]
}
```

---

## Project Structure

```
BioMesh/
├── a2a/
│   ├── __init__.py
│   ├── protocol.py        # Full A2A schemas: Task, Message, Artifact, AgentCard
│   ├── executor.py        # AgentExecutor base class with lifecycle management
│   ├── client.py          # A2AClient: agent discovery and task dispatch
│   └── registry.py        # AgentRegistry: global agent card + executor store
├── agents/
│   ├── __init__.py
│   ├── base.py            # BaseAgent: auto-registration with global registry
│   ├── arxiv_agent.py     # ArxivAgent: literature retrieval from arxiv.org
│   ├── openfda_agent.py   # OpenFDAAgent: FDA drug label data retrieval
│   ├── analysis_agent.py  # AnalysisAgent: cross-reference and pattern analysis
│   ├── summary_agent.py   # SummaryAgent: clinical executive summary generation
│   └── orchestrator.py    # run_orchestration(): A2A Client pipeline function
├── app/
│   ├── __init__.py
│   └── api.py             # FastAPI: /orchestrate, /.well-known/, /agents, /status
├── ui.py                  # Gradio interface
├── main.py                # Entry point: FastAPI on 8000, Gradio on 7860
├── .env.example
├── pyproject.toml         # uv project dependencies
├── uv.lock                # Pinned dependency tree — commit this
├── Dockerfile
└── README.md
```

---

## HuggingFace Deployment

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select **Docker** as the Space SDK
3. Push this repository to the Space:
   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/BioMesh
   git push hf main
   ```
4. Add `GROQ_API_KEY` as a Space Secret under **Settings → Variables and secrets**
5. The Space builds automatically using the Dockerfile and exposes port 7860

> **Important:** Never commit `.env` to the repository. Always use Space Secrets for API keys.
> Commit `uv.lock` to ensure reproducible dependency resolution across builds.

---

## Interview Reference

Three things to demonstrate live:

```bash
# 1. Show all registered Agent Cards
GET /agents

# 2. Show A2A-compliant discovery endpoint
GET /.well-known/arxivagent.json

# 3. Run the full pipeline and show task IDs + context ID + state transitions
POST /orchestrate  {"topic": "gene therapy sickle cell"}
```

The A2A Task Pipeline tab in the UI shows `context_id`, all four `task_id` values, and final `status` states — demonstrating full A2A task lifecycle traceability in a single view.

---

## License

MIT
