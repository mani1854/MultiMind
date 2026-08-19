"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bot,
  Cpu,
  Database,
  Gauge,
  GitBranch,
  Radio,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { Route } from "next";
import type { ReactNode } from "react";

const NAV_ITEMS: Array<{ href: Route; label: string; icon: typeof Bot; badge: string }> = [
  { href: "/chat", label: "Copilot Studio", icon: Bot, badge: "Live RAG" },
  { href: "/knowledge", label: "Knowledge Base", icon: Database, badge: "384-dim" },
  { href: "/workflows", label: "Workflow DAGs", icon: GitBranch, badge: "5 Tools" },
  { href: "/analytics", label: "Telemetry & Logs", icon: Gauge, badge: "Prometheus" },
  { href: "/admin", label: "Governance & RBAC", icon: ShieldCheck, badge: "Admin" },
];


export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 selection:bg-indigo-500 selection:text-white relative overflow-x-hidden">
      {/* Ambient Lighting Backdrop */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[1000px] h-[450px] bg-gradient-to-b from-indigo-600/15 via-purple-600/5 to-transparent blur-3xl opacity-80" />
        <div className="absolute top-1/3 -left-40 w-96 h-96 bg-emerald-600/10 blur-3xl rounded-full" />
        <div className="absolute bottom-10 -right-40 w-96 h-96 bg-indigo-600/10 blur-3xl rounded-full" />
      </div>

      {/* Top Floating Glass Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/75 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo & Status Indicator */}
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-purple-700 shadow-lg shadow-indigo-600/30">
              <Cpu className="h-5 w-5 text-white" />
              <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border-2 border-slate-950"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-white text-base">MULTIMIND</span>
                <span className="rounded-full bg-indigo-500/15 border border-indigo-500/30 px-2 py-0.2 text-2xs font-semibold text-indigo-300">
                  ENTERPRISE STUDIO
                </span>
              </div>
              <p className="text-2xs text-slate-400 font-mono">11-Agent Mesh • Qdrant RAG • Memory</p>
            </div>
          </div>

          {/* Center Navigation Dock */}
          <nav className="hidden md:flex items-center gap-1.5 rounded-full border border-slate-800/90 bg-slate-900/80 p-1.5 shadow-inner">
            {NAV_ITEMS.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-medium transition-all duration-150 ${
                    active
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 border border-indigo-400/30"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{item.label}</span>
                  {active && (
                    <span className="hidden lg:inline-block rounded-full bg-white/20 px-1.5 py-0.2 text-2xs font-mono">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right Status & User Panel */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-2xs font-mono text-emerald-400">
              <Radio className="h-3 w-3 animate-pulse text-emerald-400" />
              <span>CORE ONLINE :8000</span>
            </div>

            <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-indigo-700 to-purple-600 text-xs font-bold text-white border border-indigo-400/30 shadow-xs">
                AD
              </div>
              <div className="hidden xl:block text-left">
                <div className="text-xs font-semibold text-slate-200">admin@omnimind.local</div>
                <div className="text-2xs text-indigo-400 font-mono">ROLE: SYSTEM ADMIN</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation Bar */}
      <div className="flex md:hidden border-b border-slate-800 bg-slate-950/90 px-4 py-2 overflow-x-auto gap-2">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium ${
                active ? "bg-indigo-600 text-white" : "bg-slate-900 text-slate-400"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {item.label}
            </Link>
          );
        })}
      </div>

      {/* Main Content Area */}
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
