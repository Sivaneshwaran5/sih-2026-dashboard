import React from 'react';
import { AlertTriangle, ShieldAlert, Wrench, CheckCircle2 } from 'lucide-react';

export default function StatCards({ analytics }) {
  const stats = analytics || {
    total_defects: 0,
    open_tickets: 0,
    critical_hazards: 0,
    resolved_count: 0,
    under_repair_count: 0,
    total_occurrences_absorbed: 0,
    deduplication_ratio_pct: 0,
    active_fleet_count: 24,
  };

  const resolutionRate = stats.total_defects > 0 
    ? Math.round((stats.resolved_count / stats.total_defects) * 100) 
    : 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Total Hazards Logged */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden transition-all duration-300 hover:border-cyan-500/40 hover:shadow-cyan-500/10 group">
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-cyan-500/10 rounded-full blur-xl group-hover:bg-cyan-500/20 transition-all" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Hazards</span>
          <div className="p-2 bg-cyan-950/60 border border-cyan-800/40 rounded-lg text-cyan-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-bold font-mono text-white tracking-tight">
            {stats.total_defects}
          </span>
          <span className="text-xs text-emerald-400 font-mono bg-emerald-950/60 border border-emerald-800/40 px-1.5 py-0.5 rounded">
            +{(stats.total_occurrences_absorbed || 0)} Deduped
          </span>
        </div>
        <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
          <span>Active Open: <strong className="text-slate-200">{stats.open_tickets}</strong></span>
          <span className="text-cyan-400 text-[11px]">Multi-Bus Verified</span>
        </div>
      </div>

      {/* Critical Hazards Requiring Attention */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden transition-all duration-300 hover:border-rose-500/40 hover:shadow-rose-500/10 group">
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-rose-500/10 rounded-full blur-xl group-hover:bg-rose-500/20 transition-all" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Critical Hazards</span>
          <div className="p-2 bg-rose-950/60 border border-rose-800/40 rounded-lg text-rose-400 animate-pulse">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-bold font-mono text-rose-400 tracking-tight">
            {stats.critical_hazards}
          </span>
          <span className="text-xs text-rose-400 font-mono bg-rose-950/60 border border-rose-800/40 px-1.5 py-0.5 rounded">
            High Severity
          </span>
        </div>
        <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
          <span>Potholes &gt;10cm / Floods</span>
          <span className="text-rose-400 text-[11px] font-semibold">Immediate Action</span>
        </div>
      </div>

      {/* Active Work Orders Under Repair */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden transition-all duration-300 hover:border-amber-500/40 hover:shadow-amber-500/10 group">
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-amber-500/10 rounded-full blur-xl group-hover:bg-amber-500/20 transition-all" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Under Repair</span>
          <div className="p-2 bg-amber-950/60 border border-amber-800/40 rounded-lg text-amber-400">
            <Wrench className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-bold font-mono text-amber-400 tracking-tight">
            {stats.under_repair_count}
          </span>
          <span className="text-xs text-amber-400 font-mono bg-amber-950/60 border border-amber-800/40 px-1.5 py-0.5 rounded">
            Dispatched
          </span>
        </div>
        <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
          <span>Municipal Crews Assigned</span>
          <span className="text-amber-400 text-[11px]">SLA &lt; 24h</span>
        </div>
      </div>

      {/* Resolution Rate & Dedup Ratio */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden transition-all duration-300 hover:border-emerald-500/40 hover:shadow-emerald-500/10 group">
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl group-hover:bg-emerald-500/20 transition-all" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Resolution Rate</span>
          <div className="p-2 bg-emerald-950/60 border border-emerald-800/40 rounded-lg text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-bold font-mono text-emerald-400 tracking-tight">
            {resolutionRate}%
          </span>
          <span className="text-xs text-emerald-300 font-mono bg-emerald-950/60 border border-emerald-800/40 px-1.5 py-0.5 rounded">
            {stats.resolved_count} Closed
          </span>
        </div>
        <div className="mt-2">
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-emerald-400 h-1.5 rounded-full transition-all duration-500 shadow-sm shadow-emerald-400"
              style={{ width: `${Math.min(100, Math.max(5, resolutionRate))}%` }}
            />
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400">
            <span>Deduplication Ratio: <strong className="text-cyan-400">{stats.deduplication_ratio_pct}%</strong></span>
            <span>{stats.active_fleet_count} Buses Online</span>
          </div>
        </div>
      </div>
    </div>
  );
}
