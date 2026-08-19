# API Documentation

The backend exposes OpenAPI at `/docs`.

## Authentication

`POST /api/v1/auth/login`

```json
{
  "email": "admin@omnimind.local",
  "password": "admin123"
}
```

Use the returned bearer token for protected routes.

## Chat

`POST /api/v1/chat`

```json
{
  "message": "Summarize this policy and create action items",
  "workspace_id": "demo-workspace",
  "session_id": "default",
  "stream": false
}
```

Set `stream` to `true` for server-sent events containing agent events and tokens.

## Documents

`POST /api/v1/documents/ingest`

Upload one supported file: PDF, DOCX, TXT, Markdown, PPTX, or CSV.

## Knowledge

`POST /api/v1/knowledge/search`

```json
{
  "query": "remote work policy",
  "workspace_id": "demo-workspace",
  "top_k": 6,
  "filters": {}
}
```

## Workflows

`POST /api/v1/workflows/run`

```json
{
  "name": "executive-report",
  "objective": "Generate a weekly project report",
  "inputs": {
    "sections": ["Summary", "Risks", "Next steps"]
  }
}
```

