import React, { useState } from 'react';
import { 
  AlertCircle, 
  Activity, 
  Car, 
  AlertTriangle, 
  Droplets, 
  MapPin, 
  Eye
} from 'lucide-react';

export default function IncidentFeed({ 
  defects = [], 
  incidents = [], 
  onSelectDefect, 
  selectedTicketId = null,
  onGenerateWorkOrder 
}) {
  const [activeTab, setActiveTab] = useState('all'); // all, critical, pothole, vehicle

  // Format relative time helper
  const getRelativeTime = (timestamp) => {
    if (!timestamp) return 'Just now';
    const now = new Date();
    const past = new Date(timestamp);
    const diffSec = Math.max(1, Math.floor((now - past) / 1000));

    if (diffSec < 60) return `${diffSec}s ago`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    return `${diffHr}h ago`;
  };

  // Filter items based on selected tab
  const filteredDefects = defects.filter(defect => {
    if (activeTab === 'critical') return defect.severity === 'critical';
    if (activeTab === 'pothole') return defect.defect_type === 'pothole';
    if (activeTab === 'vehicle') return false; // Handled in vehicle incidents
    return true;
  });

  return (
    <div className="glass-panel rounded-xl overflow-hidden flex flex-col h-[580px] border border-slate-800/80 shadow-2xl">
      {/* Header with Live Indicator */}
      <div className="p-3.5 bg-command-900/90 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping absolute" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          </div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Live Telemetry Feed
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800/60">
            3s Auto-Sync
          </span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="px-3 pt-2.5 pb-2 bg-command-950/80 border-b border-slate-800 flex items-center gap-1.5 overflow-x-auto text-[11px]">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-2.5 py-1 rounded-md font-medium transition ${
            activeTab === 'all' 
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' 
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          All ({defects.length})
        </button>
        <button
          onClick={() => setActiveTab('critical')}
          className={`px-2.5 py-1 rounded-md font-medium transition flex items-center gap-1 ${
            activeTab === 'critical' 
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' 
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
          Critical ({defects.filter(d => d.severity === 'critical').length})
        </button>
        <button
          onClick={() => setActiveTab('pothole')}
          className={`px-2.5 py-1 rounded-md font-medium transition ${
            activeTab === 'pothole' 
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' 
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          Potholes ({defects.filter(d => d.defect_type === 'pothole').length})
        </button>
        <button
          onClick={() => setActiveTab('vehicle')}
          className={`px-2.5 py-1 rounded-md font-medium transition flex items-center gap-1 ${
            activeTab === 'vehicle' 
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' 
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          ANPR ({incidents.length})
        </button>
      </div>

      {/* Feed List Items */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {/* Show Vehicle ANPR Incidents if 'vehicle' tab is selected */}
        {activeTab === 'vehicle' && incidents.map((inc) => (
          <div
            key={inc.id}
            className="p-3 bg-command-900/60 border border-slate-800 hover:border-blue-500/50 rounded-lg transition-all"
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <Car className="w-3.5 h-3.5 text-blue-400" />
                <span className="text-xs font-mono font-bold text-white uppercase">{inc.incident_type.replace('_', ' ')}</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">{getRelativeTime(inc.timestamp)}</span>
            </div>
            <div className="flex items-center justify-between text-xs mt-1.5">
              <span className="font-mono bg-slate-950 px-2 py-0.5 rounded text-amber-400 font-bold border border-slate-800">
                {inc.license_plate}
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {inc.bus_id} ({Math.round(inc.confidence * 100)}% Conf)
              </span>
            </div>
          </div>
        ))}

        {/* Show Road Defects */}
        {activeTab !== 'vehicle' && filteredDefects.map((defect) => {
          const isSelected = selectedTicketId === defect.ticket_id;
          const isCritical = defect.severity === 'critical';
          const isResolved = defect.status === 'resolved';

          return (
            <div
              key={defect.ticket_id || defect.id}
              onClick={() => onSelectDefect && onSelectDefect(defect)}
              className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border ${
                isSelected 
                  ? 'bg-command-800/90 border-cyan-400 shadow-lg shadow-cyan-500/10' 
                  : isCritical && !isResolved
                  ? 'bg-command-900/70 border-rose-900/60 hover:border-rose-500/60'
                  : 'bg-command-900/50 border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Top Row: Type & Severity */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {defect.defect_type === 'pothole' && <AlertTriangle className="w-4 h-4 text-rose-400" />}
                  {defect.defect_type === 'waterlogging' && <Droplets className="w-4 h-4 text-sky-400" />}
                  {defect.defect_type === 'damaged_sign' && <AlertCircle className="w-4 h-4 text-amber-400" />}
                  {defect.defect_type === 'missing_zebra' && <Activity className="w-4 h-4 text-yellow-400" />}

                  <span className="text-xs font-semibold text-white capitalize">
                    {defect.defect_type.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                    isCritical 
                      ? 'bg-rose-950 text-rose-400 border border-rose-800/60' 
                      : 'bg-amber-950 text-amber-400 border border-amber-800/60'
                  }`}>
                    {defect.severity}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {getRelativeTime(defect.timestamp)}
                  </span>
                </div>
              </div>

              {/* Middle Row: Ticket ID & Deduplication count */}
              <div className="mt-2 flex items-center justify-between text-[11px] font-mono">
                <span className="text-cyan-400 font-bold">{defect.ticket_id}</span>
                <span className="text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-900/50 text-[10px]">
                  {defect.occurrence_count} Bus Pass{defect.occurrence_count > 1 ? 'es' : ''}
                </span>
              </div>

              {/* Bottom Row: Location, Status and Quick Actions */}
              <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400">
                <div className="flex items-center gap-1 font-mono">
                  <MapPin className="w-3 h-3 text-slate-500" />
                  <span>{(defect.latitude || 0).toFixed(4)}, {(defect.longitude || 0).toFixed(4)}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  <span className={`px-1.5 py-0.5 rounded capitalize font-medium ${
                    defect.status === 'resolved' ? 'text-emerald-400 bg-emerald-950/40' :
                    defect.status === 'under_repair' ? 'text-amber-400 bg-amber-950/40' :
                    'text-rose-400 bg-rose-950/40'
                  }`}>
                    {(defect.status || 'open').replace('_', ' ')}
                  </span>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onGenerateWorkOrder && onGenerateWorkOrder(defect);
                    }}
                    title="View Statutory Work Order"
                    className="p-1 hover:bg-slate-800 rounded text-slate-300 hover:text-cyan-300 transition"
                  >
                    <Eye className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {filteredDefects.length === 0 && activeTab !== 'vehicle' && (
          <div className="p-8 text-center text-slate-500 text-xs">
            No hazard incidents logged in this view.
          </div>
        )}
      </div>

      {/* Feed Bottom Status */}
      <div className="px-3.5 py-2 bg-command-950/90 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
        <span>Fleet AI Stream: ACTIVE</span>
        <span className="text-cyan-400">100% Ingestion Rate</span>
      </div>
    </div>
  );
}
