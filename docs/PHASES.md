# Development Phases

## Phase 1

- Basic authenticated chat.
- Document ingestion for PDF, DOCX, TXT, Markdown, PPTX, and CSV.
- Qdrant vector integration.
- Initial citation-aware RAG.
- Docker Compose environment.

## Phase 2

- Replace sequential pipeline with explicit LangGraph state graph.
- Durable PostgreSQL memory store.
- SSE-first token streaming in the UI.
- Conversation/session persistence.

## Phase 3

- Advanced retrieval: hybrid BM25 plus dense vectors, re-ranking, compression, and multi-query retrieval.
- Redis-backed workflow queue with retries and dead-letter handling.
- LangSmith trace correlation and richer OpenTelemetry spans.
- Admin monitoring agent dashboards.

## Phase 4

- Enterprise SSO/OAuth providers.
- Tenant isolation and data retention controls.
- Kubernetes autoscaling and production ingress.
- Graph RAG and knowledge graph enrichment.
- Human-in-the-loop approval queues.

