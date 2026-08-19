"use client";

import { Activity, CheckCircle2, Cpu, Loader2, Sparkles, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentEvent } from "@/lib/api";

const ALL_AGENTS = [
  { name: "Router", desc: "Intent Classifier", color: "text-indigo-400 border-indigo-500/40 bg-indigo-500/10" },
  { name: "Memory", desc: "Episodic & Fact Recall", color: "text-purple-400 border-purple-500/40 bg-purple-500/10" },
  { name: "Retrieval", desc: "Vector Semantic Search", color: "text-cyan-400 border-cyan-500/40 bg-cyan-500/10" },
  { name: "Research", desc: "Context Synthesis", color: "text-amber-400 border-amber-500/40 bg-amber-500/10" },
  { name: "Response", desc: "Grounded LLM Generator", color: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10" },
  { name: "Validation", desc: "Citation & Fact Checker", color: "text-pink-400 border-pink-500/40 bg-pink-500/10" },
  { name: "AdminMonitoring", desc: "Telemetry & Audit Trace", color: "text-slate-400 border-slate-500/40 bg-slate-500/10" },
];

export function AgentActivity({ events, isStreaming }: { events: AgentEvent[]; isStreaming?: boolean }) {
  return (
    <Card className="flex flex-col h-full border-slate-800 bg-slate-950/60 backdrop-blur-xl">
      <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-indigo-400" />
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Neural Agent Pipeline
          </CardTitle>
        </div>
        <Badge variant={isStreaming ? "default" : "secondary"} className="font-mono text-2xs">
          {isStreaming ? "ORCHESTRATING..." : `${events.length} STEPS`}
        </Badge>
      </CardHeader>

      <CardContent className="flex-1 space-y-4 p-4 overflow-y-auto">
        {/* Agent Node Topology Visualization */}
        <div className="space-y-1.5">
          <div className="text-2xs font-semibold uppercase tracking-wider text-slate-500">
            Active Agent Mesh
          </div>
          <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-2">
            {ALL_AGENTS.map((spec) => {
              const matchedEvt = events.find((e) => e.agent.toLowerCase().includes(spec.name.toLowerCase()));
              const isDone = matchedEvt?.status === "completed" || matchedEvt?.status === "done";
              const isRunning = isStreaming && !isDone && matchedEvt;

              return (
                <div
                  key={spec.name}
                  className={`rounded-lg border p-2 text-left transition-all duration-200 ${
                    isDone
                      ? "border-emerald-500/50 bg-emerald-500/10 shadow-xs shadow-emerald-500/20"
                      : isRunning
                      ? "border-indigo-500/70 bg-indigo-500/15 animate-pulse"
                      : "border-slate-800/80 bg-slate-900/40 opacity-70"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200">{spec.name}</span>
                    {isDone ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    ) : isRunning ? (
                      <Loader2 className="h-3.5 w-3.5 text-indigo-400 animate-spin" />
                    ) : (
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-700" />
                    )}
                  </div>
                  <div className="text-2xs text-slate-400 mt-0.5 truncate">{spec.desc}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Real-Time Step Activity Log */}
        <div className="space-y-2 pt-2 border-t border-slate-800/80">
          <div className="text-2xs font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
            <span>Execution Trace Log</span>
            <span className="font-mono text-2xs text-indigo-400">{events.length} events</span>
          </div>

          {events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center text-xs text-slate-500">
              <Zap className="h-6 w-6 text-slate-700 mb-2" />
              <p>Ready for prompt dispatch.</p>
              <p className="text-2xs text-slate-600">The 11-agent pipeline will stream execution details here.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((event, index) => (
                <div
                  key={`${event.agent}-${index}`}
                  className="rounded-lg border border-slate-800 bg-slate-900/70 p-2.5 text-xs shadow-xs animate-in fade-in duration-200"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
                      {event.agent}
                    </span>
                    <Badge
                      variant={event.status === "completed" ? "success" : "secondary"}
                      className="text-2xs font-mono"
                    >
                      {event.status}
                    </Badge>
                  </div>
                  <p className="mt-1 text-2xs text-slate-400 leading-relaxed font-mono whitespace-pre-wrap">
                    {event.detail}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
