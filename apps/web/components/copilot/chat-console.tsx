"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Bot,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  FileText,
  HelpCircle,
  Lightbulb,
  RotateCcw,
  Send,
  ShieldAlert,
  Sparkles,
  UserRound,
  Zap,
} from "lucide-react";
import { AgentActivity } from "@/components/copilot/agent-activity";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  login,
  streamChat,
  type AgentEvent,
  type Citation,
} from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  citations?: Citation[];
};

const PERSONAS = [
  { id: "general", label: "Autonomous Agent", icon: Sparkles, color: "text-indigo-400" },
  { id: "executive", label: "Executive Briefing", icon: FileText, color: "text-emerald-400" },
  { id: "compliance", label: "Security & SOC-2", icon: ShieldAlert, color: "text-amber-400" },
  { id: "engineering", label: "System Architect", icon: Code2, color: "text-cyan-400" },
];

const PROMPT_SUGGESTIONS = [
  {
    title: "Company Hybrid Policy",
    prompt: "What are the key rules in our hybrid and remote work policy?",
    category: "Knowledge RAG",
  },
  {
    title: "Action Items Extraction",
    prompt: "Extract all deliverable action items and assignees from our recent sync notes.",
    category: "Intelligence",
  },
  {
    title: "SOC-2 Compliance Report",
    prompt: "Draft an executive summary of our access control and security audit status.",
    category: "Report",
  },
  {
    title: "Automate Jira & Slack Task",
    prompt: "Run an automated workflow to create a high priority task for API rate limiting.",
    category: "Workflow",
  },
];

export function ChatConsole() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "**MultiMind Neural Copilot** initialized.\n\nConnected to dense 384-dimensional vector store, multi-layered episodic memory, and the 11-agent orchestration pipeline.\n\nHow can I assist your workflow today?",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [streamingText, setStreamingText] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState("general");
  const [token, setToken] = useState<string | null>(null);
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);

  useEffect(() => {
    login()
      .then((auth) => setToken(auth.access_token))
      .catch(() => {});
  }, []);

  const lastIntent = useMemo(() => {
    const routerEvt = events.find((e) => e.agent === "Router");
    if (routerEvt) {
      return routerEvt.detail.replace("Intent classified as '", "").replace("'", "");
    }
    return "ready";
  }, [events]);

  async function handleSend(promptText: string) {
    if (!promptText.trim() || loading) return;
    const prompt = promptText.trim();
    setLoading(true);
    setInput("");
    setStreamingText("");
    setEvents([]);
    setCitations([]);
    setMessages((current) => [
      ...current,
      { role: "user", content: prompt, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
    ]);

    try {
      let authToken = token;
      if (!authToken) {
        const auth = await login();
        authToken = auth.access_token;
        setToken(authToken);
      }

      let accumulatedAnswer = "";

      await streamChat(
        prompt,
        authToken,
        (event) => {
          setEvents((prev) => {
            const exists = prev.some(
              (e) => e.agent === event.agent && e.status === event.status && e.detail === event.detail,
            );
            return exists ? prev : [...prev, event];
          });
        },
        (citation) => {
          setCitations((prev) => {
            const exists = prev.some((c) => c.source_id === citation.source_id);
            return exists ? prev : [...prev, citation];
          });
        },
        (tokenDelta) => {
          accumulatedAnswer += tokenDelta;
          setStreamingText(accumulatedAnswer);
        },
        (doneResponse) => {
          setMessages((current) => [
            ...current,
            {
              role: "assistant",
              content: doneResponse.answer || accumulatedAnswer,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              citations: doneResponse.citations,
            },
          ]);
          setStreamingText("");
          setCitations(doneResponse.citations);
          setEvents(doneResponse.agent_events);
        },
      );
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: error instanceof Error ? `❌ Error: ${error.message}` : "Request failed.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
      setStreamingText("");
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    handleSend(input);
  }

  function handleReset() {
    setMessages([
      {
        role: "assistant",
        content: "Conversation cleared. Ready for your next query.",
        timestamp: "Just now",
      },
    ]);
    setEvents([]);
    setCitations([]);
  }

  return (
    <div className="grid min-h-[calc(100vh-120px)] grid-cols-1 gap-5 lg:grid-cols-[minmax(0,1fr)_390px]">
      {/* Left Main Interactive Chat Area */}
      <Card className="flex flex-col h-full border-slate-800/90 bg-slate-950/60 backdrop-blur-2xl shadow-2xl relative">
        {/* Studio Top Toolbar */}
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800/80 px-5 py-3.5 bg-slate-900/40">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Zap className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                Copilot Studio
                <Badge variant="outline" className="font-mono text-2xs uppercase text-indigo-300 border-indigo-500/30">
                  {lastIntent}
                </Badge>
              </CardTitle>
              <div className="text-2xs text-slate-400">Grounded RAG • Memory • Multi-Agent Synthesis</div>
            </div>
          </div>

          {/* Persona Selector Chips */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {PERSONAS.map((p) => {
              const active = selectedPersona === p.id;
              const Icon = p.icon;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setSelectedPersona(p.id)}
                  className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-2xs font-medium transition-all ${
                    active
                      ? "bg-indigo-600/90 text-white shadow-xs border border-indigo-400/40"
                      : "bg-slate-900/60 text-slate-400 hover:bg-slate-800/80 hover:text-slate-200 border border-slate-800"
                  }`}
                >
                  <Icon className={`h-3 w-3 ${active ? "text-white" : p.color}`} />
                  <span>{p.label}</span>
                </button>
              );
            })}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="h-7 px-2 text-slate-500 hover:text-slate-300"
              title="Reset Conversation"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </Button>
          </div>
        </CardHeader>

        {/* Message Stream Scroll Area */}
        <CardContent className="flex flex-1 flex-col justify-between gap-4 p-5 overflow-hidden">
          <div className="flex-1 space-y-4 overflow-y-auto pr-2 max-h-[calc(100vh-340px)]">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3.5 animate-in fade-in duration-150 ${
                  message.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                {/* Avatar Icon */}
                <div
                  className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border text-xs font-semibold shadow-md ${
                    message.role === "assistant"
                      ? "border-indigo-500/40 bg-gradient-to-br from-indigo-900/60 to-slate-900 text-indigo-300"
                      : "border-slate-700 bg-slate-800 text-slate-200"
                  }`}
                >
                  {message.role === "assistant" ? <Bot className="h-4 w-4" /> : <UserRound className="h-4 w-4" />}
                </div>

                {/* Message Bubble */}
                <div className={`max-w-2xl space-y-2`}>
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                      message.role === "user"
                        ? "bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-600/20 border border-indigo-400/30"
                        : "bg-slate-900/85 text-slate-100 rounded-tl-none border border-slate-800/80 shadow-lg"
                    }`}
                  >
                    {message.content}
                  </div>

                  {/* Message Citations (if any attached) */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      <div className="text-2xs font-semibold text-slate-400 flex items-center gap-1.5">
                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                        Grounded Sources ({message.citations.length})
                      </div>
                      <div className="grid gap-1.5 sm:grid-cols-2">
                        {message.citations.map((c, cIdx) => (
                          <div
                            key={cIdx}
                            className="rounded-lg border border-slate-800/80 bg-slate-950/70 p-2 text-2xs text-slate-300"
                          >
                            <div className="flex items-center justify-between font-medium text-slate-200 truncate">
                              <span className="truncate">{c.title}</span>
                              <span className="text-emerald-400 font-mono">
                                {(c.score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <p className="mt-0.5 line-clamp-2 text-slate-400">{c.snippet}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {message.timestamp && (
                    <div
                      className={`text-2xs text-slate-500 ${
                        message.role === "user" ? "text-right" : "text-left"
                      }`}
                    >
                      {message.timestamp}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Live Streaming Delta Bubble */}
            {loading && streamingText && (
              <div className="flex gap-3.5 animate-in fade-in duration-100">
                <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-indigo-500/50 bg-indigo-950/70 text-indigo-300 shadow-md">
                  <Bot className="h-4 w-4 animate-pulse" />
                </div>
                <div className="max-w-2xl rounded-2xl rounded-tl-none border border-indigo-500/40 bg-slate-900/90 px-4 py-3 text-sm leading-relaxed text-slate-100 shadow-lg whitespace-pre-wrap">
                  {streamingText}
                  <span className="inline-block h-4 w-1.5 ml-1 bg-indigo-400 animate-pulse align-middle" />
                </div>
              </div>
            )}
          </div>

          {/* Quick Prompt Cards (if conversation is fresh) */}
          {messages.length <= 2 && (
            <div className="space-y-2 pt-2 border-t border-slate-800/60">
              <div className="flex items-center gap-1.5 text-2xs font-semibold uppercase tracking-wider text-slate-400">
                <Lightbulb className="h-3 w-3 text-amber-400" />
                Suggested Inquiries
              </div>
              <div className="grid gap-2 sm:grid-cols-2">
                {PROMPT_SUGGESTIONS.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSend(item.prompt)}
                    className="flex flex-col text-left rounded-xl border border-slate-800 bg-slate-900/60 p-2.5 text-xs text-slate-300 hover:border-indigo-500/50 hover:bg-slate-800/80 hover:text-white transition-all shadow-xs group"
                  >
                    <div className="flex items-center justify-between text-2xs font-semibold text-indigo-400 group-hover:text-indigo-300">
                      <span>{item.category}</span>
                      <ChevronRight className="h-3 w-3 opacity-60 group-hover:translate-x-0.5 transition" />
                    </div>
                    <div className="font-medium text-slate-200 mt-0.5">{item.title}</div>
                    <div className="text-2xs text-slate-400 line-clamp-1 mt-0.5">{item.prompt}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Grounded Citation Preview Bar */}
          {citations.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 shadow-inner">
              <div className="flex items-center justify-between text-2xs font-semibold text-slate-300 mb-2">
                <span className="flex items-center gap-1.5">
                  <BrainCircuit className="h-3.5 w-3.5 text-indigo-400" />
                  Real-Time Retrieved Sources ({citations.length})
                </span>
                <span className="text-2xs font-mono text-emerald-400">Grounding Active</span>
              </div>
              <div className="grid gap-2 sm:grid-cols-2">
                {citations.map((cit, idx) => (
                  <div
                    key={idx}
                    onClick={() => setExpandedCitation(expandedCitation === cit.source_id ? null : cit.source_id)}
                    className="cursor-pointer rounded-lg border border-slate-800/90 bg-slate-900/80 p-2 hover:border-slate-700 transition"
                  >
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                      <span className="truncate">{cit.title}</span>
                      <span className="text-2xs font-mono text-emerald-400 bg-emerald-950/50 px-1.5 py-0.2 rounded border border-emerald-800/40">
                        {(cit.score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className={`mt-1 text-2xs text-slate-400 ${expandedCitation === cit.source_id ? "" : "line-clamp-2"}`}>
                      {cit.snippet}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Bottom Interactive Prompt Input Box */}
          <form onSubmit={onSubmit} className="relative flex items-center gap-2 pt-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything, query knowledge, or execute a multi-agent task..."
              className="h-12 rounded-xl bg-slate-900/90 border-slate-700/80 text-sm pl-4 pr-12 focus:border-indigo-500 shadow-inner"
              disabled={loading}
            />
            <Button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-1.5 h-9 w-9 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white p-0 shadow-md shadow-indigo-600/30"
              title="Send Prompt"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Right Side: Neural Agent Mesh & Execution Trace */}
      <AgentActivity events={events} isStreaming={loading} />
    </div>
  );
}
