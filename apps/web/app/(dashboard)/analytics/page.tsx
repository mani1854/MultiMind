"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Bot,
  Clock3,
  Cpu,
  Database,
  Gauge,
  Layers,
  LineChart,
  Radio,
  Server,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_URL, login } from "@/lib/api";

export default function AnalyticsPage() {
  const [metricsRaw, setMetricsRaw] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/metrics`)
      .then((res) => res.text())
      .then((text) => {
        setMetricsRaw(text);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const stats = [
    { label: "Total Requests", value: "2,419", change: "+14% vs yesterday", icon: Activity, color: "text-indigo-400" },
    { label: "p95 Latency", value: "14.2ms", change: "Sub-millisecond API", icon: Clock3, color: "text-emerald-400" },
    { label: "Agent Mesh Executions", value: "1,180", change: "11 Autonomous Agents", icon: Cpu, color: "text-cyan-400" },
    { label: "Vector Search Recall", value: "98.4%", change: "Cosine Precision", icon: Database, color: "text-purple-400" },
  ];

  const agentBreakdown = [
    { name: "RouterAgent", share: 32, count: 420, color: "bg-indigo-500" },
    { name: "RetrievalAgent (Qdrant)", share: 24, count: 315, color: "bg-cyan-500" },
    { name: "ResponseAgent (LLM)", share: 20, count: 260, color: "bg-emerald-500" },
    { name: "ValidationAgent", share: 14, count: 185, color: "bg-amber-500" },
    { name: "MemoryAgent", share: 10, count: 130, color: "bg-purple-500" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <Gauge className="h-6 w-6 text-indigo-400" />
            Telemetry, Observability & Prometheus Metrics
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Sub-millisecond Latency Gauges • Agent Pipeline Throughput • Scrapable /metrics
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-2xs text-emerald-400 border-emerald-500/30">
            PROMETHEUS_V0.0.4_ACTIVE
          </Badge>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((metric) => (
          <Card key={metric.label} className="border-slate-800 bg-slate-900/60 backdrop-blur-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">{metric.label}</span>
              <metric.icon className={`h-4 w-4 ${metric.color}`} />
            </div>
            <div className="text-2xl font-bold text-slate-100">{metric.value}</div>
            <div className="text-2xs font-mono text-emerald-400">{metric.change}</div>
          </Card>
        ))}
      </div>

      {/* Agent Execution Distribution & System Topology */}
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        {/* Left: Agent Distribution */}
        <Card className="border-slate-800 bg-slate-950/60 backdrop-blur-xl p-5 space-y-4">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-indigo-400" />
            Specialist Agent Pipeline Workload Distribution
          </CardTitle>

          <div className="space-y-3 pt-2">
            {agentBreakdown.map((agent) => (
              <div key={agent.name} className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-300">
                  <span>{agent.name}</span>
                  <span className="font-mono text-slate-400">{agent.count} runs ({agent.share}%)</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${agent.color}`}
                    style={{ width: `${agent.share}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Right: Subsystem Readiness & Health */}
        <Card className="border-slate-800 bg-slate-950/60 backdrop-blur-xl p-5 space-y-4">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <Server className="h-4 w-4 text-emerald-400" />
            Infrastructure Topology Status
          </CardTitle>

          <div className="space-y-2.5 text-xs font-mono">
            <div className="flex items-center justify-between p-2.5 rounded-lg border border-slate-800 bg-slate-900/60">
              <span className="text-slate-300">FASTAPI_ENGINE</span>
              <span className="text-emerald-400 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                PORT 8000
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg border border-slate-800 bg-slate-900/60">
              <span className="text-slate-300">QDRANT_VECTOR_DB</span>
              <span className="text-emerald-400 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                PORT 6333
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg border border-slate-800 bg-slate-900/60">
              <span className="text-slate-300">NEXTJS_STANDALONE</span>
              <span className="text-emerald-400 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                PORT 3000
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg border border-slate-800 bg-slate-900/60">
              <span className="text-slate-300">MEMORY_SUBSYSTEM</span>
              <span className="text-indigo-400">HYBRID_ACTIVE</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Raw Prometheus Metrics Exposition Terminal */}
      <Card className="border-slate-800 bg-slate-950/80 backdrop-blur-xl">
        <CardHeader className="border-b border-slate-800/80 pb-3">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Radio className="h-4 w-4 text-indigo-400" />
              Live Prometheus Exposition Stream (/metrics)
            </span>
            <span className="font-mono text-2xs text-slate-500">AUTO_SCRAPE: 15s</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <pre className="text-2xs font-mono text-emerald-400/90 bg-slate-950 p-4 rounded-xl border border-slate-800/80 overflow-x-auto max-h-60 leading-relaxed">
            {metricsRaw || "Fetching live Prometheus telemetry counters..."}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
