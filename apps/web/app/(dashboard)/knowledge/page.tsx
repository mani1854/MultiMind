"use client";

import { useEffect, useState } from "react";
import {
  Binary,
  CheckCircle2,
  Database,
  FileCode,
  FileSpreadsheet,
  FileText,
  Layers,
  Loader2,
  Search,
  Sparkles,
  Trash2,
  UploadCloud,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  deleteDocument,
  listDocuments,
  login,
  searchKnowledge,
  uploadDocument,
  type DocumentItem,
  type SearchResult,
} from "@/lib/api";

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    login()
      .then((auth) => {
        setToken(auth.access_token);
        loadDocuments(auth.access_token);
      })
      .catch(() => {});
  }, []);

  async function loadDocuments(authToken: string) {
    try {
      setLoading(true);
      const docs = await listDocuments(authToken);
      setDocuments(docs);
    } catch {
      // API fallback
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    try {
      setUploading(true);
      await uploadDocument(file, token);
      await loadDocuments(token);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(docId: string) {
    if (!token) return;
    try {
      await deleteDocument(docId, token);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch {
      alert("Failed to delete document");
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!searchQuery.trim() || !token) return;

    try {
      setSearching(true);
      const results = await searchKnowledge(searchQuery, token);
      setSearchResults(results);
    } catch {
      alert("Semantic search query failed");
    } finally {
      setSearching(false);
    }
  }

  function getFileIcon(type?: string, filename?: string) {
    const t = (type || "").toLowerCase();
    const f = (filename || "").toLowerCase();
    if (t.includes("pdf") || f.endsWith(".pdf")) return <FileText className="h-4 w-4 text-rose-400" />;
    if (t.includes("csv") || t.includes("sheet") || f.endsWith(".csv") || f.endsWith(".xlsx")) return <FileSpreadsheet className="h-4 w-4 text-emerald-400" />;
    if (t.includes("json") || t.includes("md") || f.endsWith(".json") || f.endsWith(".md")) return <FileCode className="h-4 w-4 text-cyan-400" />;
    return <FileText className="h-4 w-4 text-indigo-400" />;
  }

  const totalChunks = documents.reduce((acc, d) => acc + (d.chunks_count ?? d.chunk_count ?? 0), 0);

  return (
    <div className="space-y-6">
      {/* Top Banner & Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <Database className="h-6 w-6 text-indigo-400" />
            Knowledge Base & Neural Vector Index
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            384-Dim Dense Embeddings • Sliding Window Chunker • Qdrant Vector Store
          </p>
        </div>

        {/* Upload Button */}
        <label className="cursor-pointer inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-indigo-600/30 hover:bg-indigo-500 transition border border-indigo-400/30">
          {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
          {uploading ? "Parsing & Indexing..." : "Ingest New Document"}
          <input
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.docx,.pptx,.csv,.txt,.md"
            disabled={uploading}
          />
        </label>
      </div>

      {/* Vector Stats Summary Cards */}
      <div className="grid gap-3 sm:grid-cols-3">
        <Card className="p-4 border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Documents</span>
            <FileText className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">{documents.length}</div>
          <div className="text-2xs text-slate-500 mt-0.5">Ingested across workspace</div>
        </Card>

        <Card className="p-4 border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Indexed Chunks</span>
            <Layers className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">{totalChunks}</div>
          <div className="text-2xs text-slate-500 mt-0.5">1000-char sliding windows</div>
        </Card>

        <Card className="p-4 border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Vector Architecture</span>
            <Binary className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">384-Dim Cosine</div>
          <div className="text-2xs text-emerald-400 font-mono mt-0.5">QDRANT_STORE_READY</div>
        </Card>
      </div>

      {/* Semantic Vector Search Sandbox */}
      <Card className="border-slate-800 bg-slate-950/60 backdrop-blur-xl shadow-xl">
        <CardHeader className="pb-3 border-b border-slate-800/80">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <Search className="h-4 w-4 text-indigo-400" />
            Semantic Vector Search Sandbox
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 p-5">
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Test cosine similarity queries against indexed enterprise chunks..."
              className="flex-1 bg-slate-900/80 border-slate-700"
            />
            <Button
              type="submit"
              disabled={searching || !searchQuery.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium"
            >
              {searching ? <Loader2 className="h-4 w-4 animate-spin mr-1.5" /> : <Sparkles className="h-4 w-4 mr-1.5" />}
              {searching ? "Searching..." : "Vector Query"}
            </Button>
          </form>

          {/* Search Results Display */}
          {searchResults.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-slate-800/80 animate-in fade-in duration-200">
              <div className="text-2xs font-semibold uppercase tracking-wider text-slate-400">
                Top Semantic Matches (Ranked by Cosine Score):
              </div>
              <div className="grid gap-2.5 sm:grid-cols-2">
                {searchResults.map((res, idx) => (
                  <div
                    key={idx}
                    className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 shadow-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-200 truncate">{res.title}</span>
                      <Badge variant="success" className="font-mono text-2xs">
                        {(res.score * 100).toFixed(0)}% MATCH
                      </Badge>
                    </div>
                    <p className="text-2xs text-slate-400 leading-relaxed font-mono bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                      {res.snippet}
                    </p>
                    <div className="text-2xs text-slate-500 font-mono">
                      Chunk Index #{res.chunk_index} • DocID: {res.document_id.slice(0, 8)}...
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Document Library Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Document Repository ({documents.length})
          </h2>
          {loading && <Loader2 className="h-4 w-4 animate-spin text-slate-500" />}
        </div>

        {documents.length === 0 && !loading ? (
          <Card className="border-dashed border-slate-800 bg-slate-950/40 py-12 text-center">
            <CardContent className="space-y-2">
              <Database className="mx-auto h-8 w-8 text-slate-600" />
              <div className="text-sm font-semibold text-slate-300">No documents indexed in this workspace</div>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Upload .pdf, .docx, .csv, or .txt documents above to automatically extract text, generate 384-dim embeddings, and enable RAG answers.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {documents.map((doc) => (
              <Card
                key={doc.id}
                className="border-slate-800 bg-slate-900/60 backdrop-blur-xl hover:border-slate-700 transition duration-150 p-4 space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5 overflow-hidden">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-800 border border-slate-700">
                      {getFileIcon(doc.content_type || doc.file_type, doc.filename)}
                    </div>
                    <div className="truncate">
                      <div className="truncate text-xs font-semibold text-slate-200" title={doc.filename}>
                        {doc.filename}
                      </div>
                      <div className="text-2xs font-mono text-slate-500 uppercase">
                        {doc.content_type || doc.file_type || "DOCUMENT"}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(doc.id)}
                    className="h-7 w-7 p-0 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10"
                    title="Delete document"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-2 text-2xs pt-2 border-t border-slate-800/80 font-mono">
                  <div className="bg-slate-950/60 p-1.5 rounded border border-slate-800/60">
                    <span className="text-slate-500">CHUNKS: </span>
                    <span className="text-indigo-300 font-semibold">{doc.chunks_count ?? doc.chunk_count ?? 0}</span>
                  </div>
                  <div className="bg-slate-950/60 p-1.5 rounded border border-slate-800/60">
                    <span className="text-slate-500">SIZE: </span>
                    <span className="text-slate-300">{(doc.size_bytes / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
