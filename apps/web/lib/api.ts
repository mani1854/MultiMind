/**
 * api.ts — MultiMind Enterprise Web API Client
 * ============================================
 * Provides strongly-typed frontend client bindings for:
 * - JWT Authentication (login, register, me)
 * - Real-Time Server-Sent Events (SSE) Streaming Chat
 * - Knowledge Base (document upload, listing, semantic search, deletion)
 * - Multi-Layer Memory Management (remember, list, recall, delete)
 * - Workflow Engine (tool listing, automated DAG execution, run inspection)
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type AgentEvent = {
  agent: string;
  status: string;
  detail: string;
};

export type Citation = {
  title: string;
  source_id: string;
  snippet: string;
  score: number;
  chunk_index?: number;
};

export type ChatResponse = {
  answer: string;
  intent: string;
  citations: Citation[];
  agent_events: AgentEvent[];
};

export type DocumentItem = {
  id: string;
  filename: string;
  content_type?: string;
  file_type?: string;
  size_bytes: number;
  chunks_count?: number;
  chunk_count?: number;
  workspace_id: string;
  created_at: string;
};

export type SearchResult = {
  chunk_id: string;
  document_id: string;
  title: string;
  snippet: string;
  score: number;
  chunk_index: number;
};

export type ToolInfo = {
  name: string;
  description: string;
  category: string;
  parameters: Record<string, unknown>;
};

export type WorkflowStep = {
  step_id: string;
  name: string;
  tool: string;
  status: string;
  detail: string;
  output: Record<string, unknown>;
  started_at: string;
  completed_at: string;
};

export type WorkflowRunResponse = {
  run_id: string;
  name: string;
  objective: string;
  status: string;
  workspace_id: string;
  steps: WorkflowStep[];
  result: Record<string, unknown>;
  created_at: string;
  completed_at: string;
};

export type WorkflowRunSummary = {
  run_id: string;
  name: string;
  objective: string;
  status: string;
  step_count: number;
  created_at: string;
};

export type MemoryItem = {
  id: string;
  user_id: string;
  workspace_id: string;
  content: string;
  memory_type: string;
  importance_score: number;
  tags: string[];
  created_at: string;
};

// ================= AUTHENTICATION =================

export async function login(email = "admin@omnimind.local", password = "admin123"): Promise<{ access_token: string }> {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("Authentication failed. Ensure backend API is active.");
  return response.json();
}

// ================= REAL-TIME STREAMING CHAT =================

export async function streamChat(
  message: string,
  token: string,
  onEvent: (event: AgentEvent) => void,
  onCitation: (citation: Citation) => void,
  onToken: (token: string) => void,
  onDone: (response: ChatResponse) => void,
): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message, workspace_id: "demo-workspace", stream: true }),
  });

  if (!response.ok) throw new Error(`Streaming failed: HTTP ${response.status}`);
  if (!response.body) throw new Error("No readable stream received.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      const parts = line.split("\n");
      let eventType = "message";
      let dataStr = "";

      for (const p of parts) {
        if (p.startsWith("event: ")) eventType = p.substring(7).trim();
        if (p.startsWith("data: ")) dataStr = p.substring(6).trim();
      }

      if (!dataStr) continue;

      try {
        const parsed = JSON.parse(dataStr);
        if (eventType === "agent") onEvent(parsed as AgentEvent);
        else if (eventType === "citation") onCitation(parsed as Citation);
        else if (eventType === "token") onToken(parsed as string);
        else if (eventType === "done") onDone(parsed as ChatResponse);
      } catch {
        // Fallback raw token
        if (eventType === "token") onToken(dataStr);
      }
    }
  }
}

// ================= KNOWLEDGE BASE =================

export async function listDocuments(token: string): Promise<DocumentItem[]> {
  const resp = await fetch(`${API_URL}/api/v1/documents`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Failed to fetch documents.");
  return resp.json();
}

export async function uploadDocument(file: File, token: string): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);

  const resp = await fetch(`${API_URL}/api/v1/documents/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!resp.ok) throw new Error("Document upload failed.");
  return resp.json();
}

export async function deleteDocument(docId: string, token: string): Promise<void> {
  const resp = await fetch(`${API_URL}/api/v1/documents/${docId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Delete failed.");
}

export async function searchKnowledge(query: string, token: string): Promise<SearchResult[]> {
  const resp = await fetch(`${API_URL}/api/v1/knowledge/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, top_k: 5 }),
  });
  if (!resp.ok) throw new Error("Search failed.");
  return resp.json();
}

// ================= WORKFLOWS =================

export async function listTools(token: string): Promise<ToolInfo[]> {
  const resp = await fetch(`${API_URL}/api/v1/workflows/tools`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Failed to list tools.");
  return resp.json();
}

export async function runWorkflow(name: string, objective: string, inputs: Record<string, unknown>, token: string): Promise<WorkflowRunResponse> {
  const resp = await fetch(`${API_URL}/api/v1/workflows/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ name, objective, inputs }),
  });
  if (!resp.ok) throw new Error("Workflow run failed.");
  return resp.json();
}

export async function listWorkflowRuns(token: string): Promise<WorkflowRunSummary[]> {
  const resp = await fetch(`${API_URL}/api/v1/workflows/runs`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Failed to list workflow runs.");
  return resp.json();
}

// ================= MEMORY =================

export async function listMemories(token: string): Promise<MemoryItem[]> {
  const resp = await fetch(`${API_URL}/api/v1/memory`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Failed to list memories.");
  return resp.json();
}

export async function createMemory(content: string, memory_type = "user_preference", importance_score = 0.8, token: string): Promise<MemoryItem> {
  const resp = await fetch(`${API_URL}/api/v1/memory`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content, memory_type, importance_score, tags: ["web_ui"] }),
  });
  if (!resp.ok) throw new Error("Failed to create memory.");
  return resp.json();
}

export async function deleteMemory(memoryId: string, token: string): Promise<void> {
  const resp = await fetch(`${API_URL}/api/v1/memory/${memoryId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Failed to delete memory.");
}
