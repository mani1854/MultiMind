"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  FileKey,
  KeyRound,
  Lock,
  Radio,
  Shield,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  UsersRound,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const RBAC_ROLES = [
  {
    role: "Admin",
    users: 2,
    permissions: ["Full RAG Ingestion", "DAG Execution", "RBAC Role Assignment", "Audit Log Export"],
    badge: "danger",
  },
  {
    role: "Engineer",
    users: 8,
    permissions: ["Knowledge Upload", "Run Workflows", "Vector Sandbox Query", "Read Analytics"],
    badge: "default",
  },
  {
    role: "Analyst",
    users: 14,
    permissions: ["Chat Copilot", "Semantic Search", "View Reports"],
    badge: "secondary",
  },
];

const AUDIT_LOGS = [
  { action: "DOCUMENT_INGEST", user: "admin@omnimind.local", target: "Remote_Work_Policy.pdf", time: "2 mins ago", status: "SUCCESS" },
  { action: "WORKFLOW_EXECUTE", user: "admin@omnimind.local", target: "Meeting Action Items DAG", time: "8 mins ago", status: "SUCCESS" },
  { action: "AUTH_LOGIN_HS256", user: "admin@omnimind.local", target: "JWT Token Issued", time: "14 mins ago", status: "SUCCESS" },
  { action: "RBAC_ROLE_CHECK", user: "member@omnimind.local", target: "/api/v1/admin/users", time: "32 mins ago", status: "BLOCKED_403" },
];

export default function AdminPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <ShieldCheck className="h-6 w-6 text-indigo-400" />
            Enterprise Governance, RBAC & Security Audit
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            HS256 JWT Token Governance • Workspace Tenant Isolation • Role-Based Access Control
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-2xs text-emerald-400 border-emerald-500/30">
            TENANT_ISOLATION_ENFORCED
          </Badge>
        </div>
      </div>

      {/* RBAC Roles Matrix */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <UsersRound className="h-4 w-4 text-indigo-400" />
          Workspace Role-Based Access Control (RBAC) Matrix
        </h2>

        <div className="grid gap-4 sm:grid-cols-3">
          {RBAC_ROLES.map((r) => (
            <Card key={r.role} className="border-slate-800 bg-slate-900/60 backdrop-blur-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-base font-bold text-slate-100">{r.role}</span>
                <Badge variant={r.badge as "default" | "secondary" | "danger"}>{r.users} Active Users</Badge>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                <div className="text-2xs font-semibold uppercase tracking-wider text-slate-500">Granted Privileges:</div>
                <ul className="space-y-1">
                  {r.permissions.map((p, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-2xs text-slate-300">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Security & Audit Event Stream */}
      <Card className="border-slate-800 bg-slate-950/70 backdrop-blur-xl shadow-xl">
        <CardHeader className="border-b border-slate-800/80 pb-3">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-emerald-400" />
              Security Audit & Authentication Event Stream
            </span>
            <span className="font-mono text-2xs text-slate-500">LIVE AUDIT LOGS</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="space-y-2">
            {AUDIT_LOGS.map((log, idx) => (
              <div
                key={idx}
                className="flex flex-col sm:flex-row sm:items-center justify-between rounded-xl border border-slate-800 bg-slate-900/70 p-3 text-xs gap-2"
              >
                <div className="flex items-center gap-2.5">
                  <div className={`h-2 w-2 rounded-full ${log.status === "SUCCESS" ? "bg-emerald-400" : "bg-rose-400"}`} />
                  <span className="font-mono text-xs font-semibold text-indigo-300">{log.action}</span>
                  <span className="text-slate-400 font-mono text-2xs">{log.target}</span>
                </div>
                <div className="flex items-center gap-3 text-2xs text-slate-500 font-mono">
                  <span>{log.user}</span>
                  <span>•</span>
                  <span>{log.time}</span>
                  <Badge variant={log.status === "SUCCESS" ? "success" : "danger"} className="text-2xs font-mono">
                    {log.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
