<div align="center">

<h1>🧠 MultiMind</h1>
<h3>Enterprise Multi-Agent AI Copilot & RAG Platform</h3>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-15-black?logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Qdrant-Vector%20DB-FF4438?logo=qdrant&logoColor=white" />
  <img src="https://img.shields.io/badge/Prometheus-Metrics-E6522C?logo=prometheus&logoColor=white" />
  <img src="https://img.shields.io/badge/Tests-51%20Passing-brightgreen?logo=pytest" />
</p>

<p>
  <strong>MultiMind</strong> is a production-oriented, full-stack Enterprise AI Copilot.<br/>
  It routes user questions through an <strong>11-agent sequential pipeline</strong>, retrieves grounded answers
  from an indexed knowledge base via <strong>RAG</strong>, maintains <strong>long-term memory</strong> per user,
  executes <strong>automated workflows</strong>, and streams responses <strong>word-by-word</strong> over SSE.
</p>

</div>

---

## ✨ Key Features

| Feature | Details |
|---------|---------|
| **11-Agent Pipeline** | Router → Memory → Retrieval → Research → Meeting → Summarization → Report → Workflow → Response → Validation → Admin |
| **RAG Knowledge Base** | PDF, DOCX, PPTX, CSV ingestion · Sliding-window chunking · 384-dim dense embeddings · Qdrant vector search |
| **Long-Term Memory** | 3-layer memory (Semantic Facts, Episodic Events, User Preferences) with hybrid recall scoring |
| **SSE Token Streaming** | Real-time word-by-word streaming — time-to-first-token < 1.5 s |
| **Workflow Automation** | DAG workflow engine with 5 enterprise tools (task creation, report generation, notifications) |
| **JWT Auth + RBAC** | Dual-token (access + refresh), bcrypt password hashing, composable role guards |
| **Prometheus Observability** | `/metrics` endpoint — HTTP throughput, agent executions, RAG query volume, latency |
| **Next.js Copilot Studio** | Glassmorphism dark UI, live Neural Agent Mesh visualizer, citation drawer, persona switcher |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     FRONTEND  (Next.js 15 + TypeScript)              │
│   Chat Studio │ Knowledge Hub │ Workflows │ Analytics │ Admin         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  REST + SSE  (text/event-stream)
┌──────────────────────────────▼───────────────────────────────────────┐
│                      BACKEND  (FastAPI)                               │
│                                                                      │
│   Middleware: CORS · JWT Guard · X-Request-ID · Prometheus           │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────┐       │
│   │                11-Agent Pipeline                         │       │
│   │                                                          │       │
│   │  RouterAgent → MemoryAgent → RetrievalAgent              │       │
│   │       → ResearchAgent → MeetingAgent → SummarizAgent     │       │
│   │       → ReportAgent → WorkflowAgent                      │       │
│   │       → ResponseAgent ──────────────────▶ SSE: tokens   │       │
│   │       → ValidationAgent → AdminAgent                     │       │
│   └──────────────────────────────────────────────────────────┘       │
│                                                                      │
│   ┌────────────┐   ┌──────────────┐   ┌──────────────┐              │
│   │  VectorDB  │   │    Memory    │   │    Tools     │              │
│   │   Qdrant   │   │  Service     │   │  Registry    │              │
│   │ + fallback │   │  3 layers    │   │   5 tools    │              │
│   └────────────┘   └──────────────┘   └──────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
MULTIMIND-main/
├── apps/
│   ├── api/                          # Python FastAPI Backend
│   │   ├── app/
│   │   │   ├── main.py               # Application Factory (create_app)
│   │   │   ├── core/
│   │   │   │   ├── config.py         # Pydantic BaseSettings (env validation)
│   │   │   │   ├── security.py       # JWT + bcrypt + RBAC guards
│   │   │   │   └── logging.py        # structlog JSON output
│   │   │   ├── api/v1/endpoints/
│   │   │   │   ├── auth.py           # POST /register /login /refresh GET /me
│   │   │   │   ├── chat.py           # POST /chat  POST /chat/stream (SSE)
│   │   │   │   ├── documents.py      # POST /upload  GET /  DELETE /{id}
│   │   │   │   ├── knowledge.py      # GET /search
│   │   │   │   ├── memory.py         # POST /remember /recall  GET /  DELETE /{id}
│   │   │   │   ├── workflows.py      # POST /run  GET /tools  GET /runs/{id}
│   │   │   │   ├── admin.py          # RBAC-gated admin endpoints
│   │   │   │   └── health.py         # GET /live  GET /ready
│   │   │   ├── schemas/              # Pydantic request/response models
│   │   │   ├── services/
│   │   │   │   ├── auth.py           # AuthService: users, workspaces, tokens
│   │   │   │   ├── llm.py            # LLM Gateway: OpenAI + Ollama + fallback
│   │   │   │   ├── agents/
│   │   │   │   │   ├── base.py       # Agent ABC + AgentState (Blackboard)
│   │   │   │   │   ├── specialists.py# 11 specialist agent implementations
│   │   │   │   │   └── orchestrator.py # Pipeline + SSE stream generator
│   │   │   │   ├── rag/
│   │   │   │   │   ├── document_loader.py  # Parser + sliding-window chunker
│   │   │   │   │   ├── vector_store.py     # Embeddings + Qdrant + fallback
│   │   │   │   │   └── service.py          # RAGService search facade
│   │   │   │   ├── memory/
│   │   │   │   │   └── service.py    # Hybrid recall: 0.70×sim + 0.30×importance
│   │   │   │   ├── tools/
│   │   │   │   │   └── registry.py   # 5 enterprise tools (Strategy Pattern)
│   │   │   │   └── workflows/
│   │   │   │       └── engine.py     # DAG Workflow Engine
│   │   │   └── observability/
│   │   │       ├── metrics.py        # Prometheus MetricsCollector
│   │   │       └── middleware.py     # X-Request-ID + latency middleware
│   │   └── tests/                    # 51 pytest tests (10 phases)
│   │
│   └── web/                          # Next.js 15 Frontend
│       ├── app/(dashboard)/
│       │   ├── layout.tsx            # Floating nav dock
│       │   ├── chat/page.tsx         # Copilot Studio + Persona Switcher
│       │   ├── knowledge/page.tsx    # Document ingestion hub
│       │   ├── workflows/page.tsx    # DAG workflow visualizer
│       │   ├── analytics/page.tsx    # Prometheus metrics viewer
│       │   └── admin/page.tsx        # RBAC matrix + audit log
│       ├── components/copilot/
│       │   ├── chat-console.tsx      # SSE consumer + citation drawer
│       │   └── agent-activity.tsx    # Live 11-agent Neural Mesh visualizer
│       └── lib/api.ts                # Typed API client + TypeScript interfaces
│
├── docker-compose.yml                # Full-stack orchestration
└── .env.example                      # Required environment variables
```

---

## 🚀 Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/mani1854/MultiMind.git
cd MultiMind
cp .env.example .env
```

Edit `.env` with your values:

```env
JWT_SECRET=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-...          # optional — local fallback works without it
QDRANT_URL=http://localhost:6333
```

### 2. Backend

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend

```bash
cd apps/web
npm install
npm run dev
```

### 4. Open

| Service | URL |
|---------|-----|
| Copilot Studio | http://localhost:3000/chat |
| Knowledge Hub | http://localhost:3000/knowledge |
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| Prometheus Metrics | http://127.0.0.1:8000/metrics |
| Health Probe | http://127.0.0.1:8000/health |

**Demo credentials:** `admin@omnimind.local` / `admin123`

---

## 🐳 Docker (Full Stack)

```bash
docker compose up --build
```

Starts: FastAPI · Next.js · Qdrant

---

## 🔬 How It Works

### RAG Pipeline

```
User Query
    │
    ▼
generate_dense_embedding(query, dim=384)         ← SHA-256 token hashing + L2-norm
    │
    ▼
VectorStore.search(query_vector, workspace_id)   ← Qdrant HNSW or in-memory cosine fallback
    │
    ▼
top-5 Citations injected into LLM prompt         ← grounded context window
    │
    ▼
LLMGateway.stream_complete(prompt)               ← OpenAI streaming or deterministic fallback
    │
    ▼
SSE: event:token per word → Browser              ← <1.5s time-to-first-token
```

### Hybrid Memory Recall

$$\text{Score} = 0.70 \times \text{CosineSimilarity} + 0.30 \times \text{ImportanceScore}$$

Threshold: `similarity > 0.05 OR importance ≥ 0.8`

Critical facts with high importance always surface — even when semantic similarity to the current query is low.

### Sliding Window Chunking

```
chunk_size = 1000 chars   |  overlap = 150 chars   |  advance = 850 chars

Chunk 1:  [0 ────────────────── 1000]
Chunk 2:          [850 ──────────────────── 1850]
                   ↑
           150-char shared overlap
           (preserves boundary-crossing sentences)
```

---

## 🔐 Security

| Mechanism | Implementation |
|-----------|---------------|
| Password hashing | `bcrypt` with explicit 72-byte truncation (collision prevention) |
| Access tokens | HS256 JWT, 60-minute expiry |
| Refresh tokens | HS256 JWT, 7-day expiry, type-validated on decode |
| RBAC | `require_role("admin")` — composable FastAPI `Depends()` factory |
| Multi-tenancy | All queries filtered by `workspace_id` at the service layer |

---

## 📊 Observability

`GET /metrics` exposes Prometheus-format telemetry:

```
multimind_http_requests_total{method="POST",path="/api/v1/chat/stream",status="200"} 42
multimind_http_request_duration_seconds_avg 0.3821
multimind_agent_executions_total{agent="Retrieval",status="completed"} 87
multimind_rag_queries_total{workspace="demo-workspace"} 87
multimind_workflow_runs_total{status="completed"} 5
```

Every request carries `X-Request-ID` (UUID4) in the response header for distributed tracing.

---

## 🧪 Testing

```bash
cd apps/api
pytest tests/ -v
```

**51 tests · 10 phases · 100% passing · fully offline** (no API key or Qdrant required)

| Phase | Coverage |
|-------|---------|
| Phase 1 | Health probes, app startup |
| Phase 2 | JWT auth, bcrypt security, RBAC |
| Phase 3 | Document parsing, chunking correctness |
| Phase 4 | Embedding generation, vector similarity search |
| Phase 5 | LLM Gateway (batch + streaming, fallback) |
| Phase 6 | Memory service — hybrid recall scoring |
| Phase 7 | Agent pipeline — all 11 specialists |
| Phase 8 | Tool registry, DAG workflow execution |
| Phase 9–10 | Prometheus metrics, middleware, readiness probe |

---

## 🛠 Design Patterns Used

| Pattern | Where | Why |
|---------|-------|-----|
| **Blackboard** | `agents/base.py` | 11 agents share `AgentState` with zero direct coupling |
| **Façade** | `services/llm.py` | One interface over OpenAI / Ollama / fallback |
| **Factory** | `main.py` | `create_app()` — testable without global state |
| **Strategy** | `tools/registry.py` | Tool handlers by name — add tool = one dict entry |
| **Dependency Injection** | `core/security.py` | RBAC via `Depends(require_role("admin"))` |

---

## 🗺 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register new user + workspace |
| `POST` | `/api/v1/auth/login` | Login → access + refresh tokens |
| `POST` | `/api/v1/auth/refresh` | Rotate tokens |
| `GET` | `/api/v1/auth/me` | Current user info |
| `POST` | `/api/v1/chat` | Batch chat (full response) |
| `POST` | `/api/v1/chat/stream` | **SSE streaming chat** |
| `POST` | `/api/v1/documents/upload` | Ingest document (PDF/DOCX/CSV…) |
| `GET` | `/api/v1/documents` | List ingested documents |
| `GET` | `/api/v1/knowledge/search` | Semantic similarity search |
| `POST` | `/api/v1/memory/remember` | Store memory fact/preference |
| `POST` | `/api/v1/memory/recall` | Hybrid recall query |
| `POST` | `/api/v1/workflows/run` | Execute automated workflow |
| `GET` | `/api/v1/workflows/tools` | List available tools |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/health` | Liveness probe |
| `GET` | `/api/v1/health/ready` | Deep readiness probe |

Full interactive docs at **http://127.0.0.1:8000/docs**

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | ✅ | — | Min 32-char secret for HS256 signing |
| `OPENAI_API_KEY` | ❌ | — | GPT-4 key (deterministic fallback used if absent) |
| `QDRANT_URL` | ❌ | `http://localhost:6333` | Qdrant cluster URL |
| `LLM_MODEL` | ❌ | `gpt-4o-mini` | OpenAI model name |
| `LLM_TEMPERATURE` | ❌ | `0.1` | Low = more grounded, less hallucination |
| `VECTOR_DIMENSION` | ❌ | `384` | Embedding vector size |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `60` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ | `7` | Refresh token TTL |
| `ENVIRONMENT` | ❌ | `development` | `development` / `production` |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI 0.111 + Python 3.11 |
| Frontend framework | Next.js 15 + TypeScript 5 |
| UI library | Tailwind CSS + shadcn/ui |
| Vector database | Qdrant (+ in-memory cosine fallback) |
| LLM providers | OpenAI GPT-4 / Ollama / Deterministic fallback |
| Auth | JWT (python-jose) + bcrypt |
| Observability | Prometheus (custom collector) + structlog |
| Document parsing | pypdf · python-docx · python-pptx · pandas |
| Testing | Pytest + httpx AsyncClient |
| Containerization | Docker + Docker Compose |



<div align="center">
  Built with ❤️ for enterprise AI workflows
</div>
