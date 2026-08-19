"use client";

import { useEffect, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Clock,
  Code2,
  FileCheck2,
  GitBranch,
  Layers,
  ListOrdered,
  Loader2,
  Play,
  Settings,
  Sparkles,
  Wrench,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  listTools,
  listWorkflowRuns,
  login,
  runWorkflow,
  type ToolInfo,
  type WorkflowRunResponse,
  type WorkflowRunSummary,
} from "@/lib/api";

const PRESET_PIPELINES = [
  {
    name: "Meeting Action Items & Task Dispatch",
    objective: "Extract action items from transcript, create Jira tickets, and broadcast alert",
    inputs: {
      text: "TODO: John to deploy backend on staging.\nAction: Sarah to review security compliance report.\nTODO: Alex to update swagger docs.",
      priority: "high",
    },
    category: "Operations",
  },
  {
    name: "Executive Compliance Briefing",
    objective: "Generate formal compliance and security briefing report for leadership",
    inputs: { title: "Q3 SOC-2 Security & Access Control Review" },
    category: "Governance",
  },
  {
    name: "Sprint Task Orchestrator",
    objective: "Create high priority task for API rate limiting and assign to lead",
    inputs: { owner: "lead.engineer@company.com", priority: "critical" },
    category: "Engineering",
  },
];

export default function WorkflowsPage() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [runs, setRuns] = useState<WorkflowRunSummary[]>([]);
  const [activeRun, setActiveRun] = useState<WorkflowRunResponse | null>(null);
  const [workflowName, setWorkflowName] = useState("Enterprise Automation DAG");
  const [objective, setObjective] = useState("Extract action items and create Jira tickets for engineering team");
  const [running, setRunning] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [selectedTool, setSelectedTool] = useState<ToolInfo | null>(null);

  useEffect(() => {
    login()
      .then((auth) => {
        setToken(auth.access_token);
        loadData(auth.access_token);
      })
      .catch(() => {});
  }, []);

  async function loadData(authToken: string) {
    try {
      const [tList, rList] = await Promise.all([
        listTools(authToken),
        listWorkflowRuns(authToken),
      ]);
      setTools(tList);
      setRuns(rList);
      if (tList.length > 0 && !selectedTool) {
        setSelectedTool(tList[0]);
      }
    } catch {
      // API fallback
    }
  }

  async function handleExecute(name: string, obj: string, inputs: Record<string, unknown> = {}) {
    if (!token || !obj.trim() || running) return;

    try {
      setRunning(true);
      const res = await runWorkflow(name, obj, inputs, token);
      setActiveRun(res);
      await loadData(token);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Workflow failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <GitBranch className="h-6 w-6 text-indigo-400" />
            Workflow Engine & Tool DAG Orchestrator
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Autonomous Goal Decomposition • Sequential State Accumulation • Tool Execution
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-2xs text-emerald-400 border-emerald-500/30">
            {tools.length} TOOLS REGISTERED
          </Badge>
          <Badge variant="outline" className="font-mono text-2xs text-indigo-400 border-indigo-500/30">
            {runs.length} EXECUTIONS
          </Badge>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid gap-6 lg:grid-cols-[1fr_420px]">
        {/* Left: Workflow Launch Pad & Objective Designer */}
        <Card className="border-slate-800 bg-slate-950/60 backdrop-blur-xl shadow-xl flex flex-col justify-between">
          <CardHeader className="border-b border-slate-800/80">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <Zap className="h-4 w-4 text-indigo-400" />
              Automated DAG Pipeline Builder
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 p-5">
            <div className="space-y-1.5">
              <label className="text-2xs font-semibold uppercase tracking-wider text-slate-400">
                Pipeline Identifier
              </label>
              <Input
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                className="bg-slate-900/80 border-slate-700 font-medium"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-2xs font-semibold uppercase tracking-wider text-slate-400">
                High-Level Objective (Natural Language Goal)
              </label>
              <Input
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                placeholder="e.g. Extract action items, create tickets, and dispatch email notification"
                className="bg-slate-900/80 border-slate-700"
              />
            </div>

            {/* Presets */}
            <div className="space-y-2 pt-1">
              <div className="text-2xs font-semibold uppercase tracking-wider text-slate-500">
                Pre-configured Production Scenarios:
              </div>
              <div className="grid gap-2 sm:grid-cols-3">
                {PRESET_PIPELINES.map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setWorkflowName(preset.name);
                      setObjective(preset.objective);
                    }}
                    className="flex flex-col text-left rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-300 hover:border-indigo-500/50 hover:bg-slate-800/80 transition shadow-xs"
                  >
                    <span className="text-2xs font-mono text-indigo-400 uppercase">{preset.category}</span>
                    <span className="font-semibold text-slate-200 mt-0.5 line-clamp-1">{preset.name}</span>
                    <span className="text-2xs text-slate-500 line-clamp-2 mt-1">{preset.objective}</span>
                  </button>
                ))}
              </div>
            </div>

            <Button
              onClick={() => handleExecute(workflowName, objective)}
              disabled={running || !objective.trim()}
              className="w-full h-11 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/30"
            >
              {running ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Play className="h-4 w-4 mr-2" />}
              {running ? "Synthesizing DAG & Executing Tools..." : "Run Autonomous Workflow"}
            </Button>
          </CardContent>
        </Card>

        {/* Right: Live DAG Step Visualizer & History */}
        <Card className="border-slate-800 bg-slate-950/60 backdrop-blur-xl shadow-xl flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/80 pb-3">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <Layers className="h-4 w-4 text-emerald-400" />
              Live DAG Execution Trace
            </CardTitle>
            {activeRun && (
              <Badge variant="success" className="font-mono text-2xs">
                {activeRun.status}
              </Badge>
            )}
          </CardHeader>

          <CardContent className="flex-1 space-y-3 p-4 overflow-y-auto max-h-[420px]">
            {!activeRun ? (
              <div className="flex flex-col items-center justify-center py-16 text-center text-xs text-slate-500">
                <Clock className="h-8 w-8 text-slate-700 mb-2" />
                <p className="font-medium text-slate-400">No active execution</p>
                <p className="text-2xs text-slate-600 mt-1 max-w-xs">
                  Launch a workflow on the left to watch real-time tool planning and step execution.
                </p>
              </div>
            ) : (
              <div className="space-y-3 animate-in fade-in duration-200">
                <div className="rounded-lg bg-slate-900/80 p-2.5 border border-slate-800 text-xs font-semibold text-slate-200">
                  {activeRun.name}
                  <div className="text-2xs text-slate-400 font-mono mt-0.5">{activeRun.objective}</div>
                </div>

                <div className="space-y-2">
                  {activeRun.steps.map((step, idx) => (
                    <div
                      key={step.step_id}
                      className="rounded-xl border border-slate-800 bg-slate-900/90 p-3 text-xs shadow-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between font-semibold text-slate-200">
                        <span className="flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          Step {idx + 1}: {step.name}
                        </span>
                        <Badge variant="outline" className="font-mono text-2xs text-indigo-300 border-indigo-500/30">
                          {step.tool}
                        </Badge>
                      </div>
                      <p className="text-2xs text-slate-400 leading-relaxed font-mono bg-slate-950/70 p-2 rounded-lg border border-slate-800/80">
                        {step.detail}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Bottom: Enterprise Tool Directory & Schema Inspector */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Wrench className="h-4 w-4 text-indigo-400" />
          Enterprise Tool Registry & Schema Catalog ({tools.length})
        </h2>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tools.map((tool) => (
            <Card
              key={tool.name}
              className="border-slate-800 bg-slate-900/60 backdrop-blur-xl p-4 space-y-2 hover:border-slate-700 transition"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-semibold text-indigo-300">{tool.name}</span>
                <Badge variant="secondary" className="text-2xs uppercase font-mono">
                  {tool.category}
                </Badge>
              </div>
              <p className="text-2xs text-slate-400 leading-relaxed">{tool.description}</p>
              <div className="pt-2 border-t border-slate-800/80 text-2xs font-mono text-emerald-400 flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                EXECUTION_READY
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
