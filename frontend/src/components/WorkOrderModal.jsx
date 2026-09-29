import React from 'react';
import { X, Printer, Shield, Clock, FileText } from 'lucide-react';

export default function WorkOrderModal({ defect, onClose, backendUrl = 'http://localhost:8000' }) {
  if (!defect) return null;

  const fullSnapshotUrl = defect.snapshot_url
    ? (defect.snapshot_url.startsWith('http') ? defect.snapshot_url : `${backendUrl}${defect.snapshot_url}`)
    : `${backendUrl}/static/snapshots/sample_pothole.jpg`;

  const handlePrint = () => {
    window.print();
  };

  // Determine SLA and equipment by defect type
  const getSLA = (severity) => {
    if (severity === 'critical') return '24 HOURS (STATUTORY EMERGENCY IRC:SP:20)';
    if (severity === 'moderate') return '72 HOURS';
    return '5 DAYS';
  };

  const getMaterials = (type) => {
    switch (type) {
      case 'pothole':
        return [
          'Pre-mixed Cold Asphalt Bituminous Mix (IRC Grade) - 75 kg',
          'Tack Coat Bitumen Emulsion (RS-1) - 5 Litres',
          'Mechanical Plate Vibratory Compactor',
          'Traffic Barricading Cones with Reflective Sleeves'
        ];
      case 'waterlogging':
        return [
          'Mobile De-watering Pump (5 HP Submersible)',
          'High-density Polyethylene Suction Hose (50m)',
          'Stormwater Drain De-silting Rods',
          'Emergency Sump Outlet Clearance Kit'
        ];
      case 'damaged_sign':
        return [
          'Retro-reflective Signage Sheet (High Intensity Grade Class B)',
          'Galvanized Iron Support Post (50mm NB Class B)',
          'M20 Grade Concrete Base Foundation Mix',
          'Anti-theft Anchor Fasteners'
        ];
      default:
        return [
          'Thermoplastic Road Marking Paint (White/Yellow BS EN 1871)',
          'Drop-on Glass Beads (Retro-reflectivity Class A)',
          'Pre-heater Screed Applicator Unit',
          'Pavement Surface Primer'
        ];
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      {/* Modal Container */}
      <div className="bg-command-900 border border-cyan-500/40 rounded-2xl max-w-3xl w-full shadow-2xl overflow-hidden relative my-8 text-slate-100">
        {/* Screen Action Bar (hidden when printing) */}
        <div className="no-print px-6 py-3.5 bg-command-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <span className="font-bold text-sm tracking-wide text-white uppercase">
              Statutory Work Order // Municipal Road Maintenance
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded-lg flex items-center gap-1.5 shadow transition"
            >
              <Printer className="w-4 h-4" />
              Print / Save PDF
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Official Document Body */}
        <div className="p-8 space-y-6 printable-work-order bg-slate-900 text-slate-100 print:text-black print:bg-white">
          {/* Document Header */}
          <div className="border-b-2 border-cyan-500/80 pb-4 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Shield className="w-7 h-7 text-cyan-400 print:text-blue-900" />
                <h1 className="text-xl font-black uppercase tracking-tight text-white print:text-black">
                  GREATER MUNICIPAL CORPORATION // HIGHWAYS DIVISION
                </h1>
              </div>
              <p className="text-xs font-mono text-cyan-400 print:text-blue-800 mt-0.5">
                IN PARTNERSHIP WITH BHARAT ELECTRONICS LIMITED (BEL) URBAN INTELLIGENCE FLEET
              </p>
              <p className="text-[11px] text-slate-400 print:text-gray-600 mt-1">
                Authorized pursuant to National Smart Cities Road Infrastructure Safety Mandate
              </p>
            </div>

            {/* QR Code Verification Placeholder */}
            <div className="text-right">
              <div className="inline-block p-2 bg-white rounded-lg shadow border border-slate-700 print:border-black">
                <svg className="w-16 h-16 text-black" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2 2h8v8H2V2zm2 2v4h4V4H4zm10-2h8v8h-8V2zm2 2v4h4V4h-4zM2 14h8v8H2v-8zm2 2v4h4v-4H4zm14 0h4v4h-4v-4zm-4-2h4v2h-4v-2zm0 4h2v4h-2v-4zm4 2h2v2h-2v-2zm-2-8h2v2h-2V8zm-2 2h2v2h-2v-2zm-4 4h2v2h-2v-2zm0-4h2v2h-2v-2zm2-2h2v2h-2V6z" />
                </svg>
              </div>
              <div className="text-[9px] font-mono text-slate-400 print:text-gray-600 mt-1 uppercase">
                QR Verification Stamp
              </div>
            </div>
          </div>

          {/* Ticket Metadata Banner */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-command-950/80 border border-slate-800 print:bg-gray-100 print:border-gray-300">
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400 print:text-gray-500 block">
                Official Ticket ID
              </span>
              <span className="font-mono font-bold text-sm text-cyan-400 print:text-blue-900">
                {defect.ticket_id}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400 print:text-gray-500 block">
                Defect Classification
              </span>
              <span className="font-bold text-sm text-white print:text-black capitalize">
                {defect.defect_type.replace('_', ' ')}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400 print:text-gray-500 block">
                Severity Rating
              </span>
              <span className={`font-bold text-sm uppercase ${
                defect.severity === 'critical' ? 'text-rose-400 print:text-red-700' : 'text-amber-400 print:text-amber-700'
              }`}>
                {defect.severity}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400 print:text-gray-500 block">
                AI Confidence
              </span>
              <span className="font-mono font-bold text-sm text-emerald-400 print:text-green-800">
                {Math.round(defect.confidence * 100)}% Verified
              </span>
            </div>
          </div>

          {/* Evidence Image and Geographic Coordinates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Snapshot */}
            <div className="rounded-xl overflow-hidden border border-slate-700 bg-slate-950">
              <div className="p-2 bg-slate-800/80 text-[10px] font-mono text-slate-300 print:text-black flex justify-between">
                <span>EVIDENCE PHOTO // CAM-EDGE-FRONT</span>
                <span>CONFIRMED BY {defect.occurrence_count} PASSES</span>
              </div>
              <img 
                src={fullSnapshotUrl} 
                alt="Defect Evidence" 
                className="w-full h-48 object-cover"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=60';
                }}
              />
            </div>

            {/* Geographical & Telemetry Verification */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 print:text-blue-900 border-b border-slate-700 pb-1">
                Geospatial & Telemetry Verification
              </h3>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-slate-800/60 print:border-gray-300">
                  <span className="text-slate-400 print:text-gray-600">GPS Latitude:</span>
                  <span className="font-bold text-white print:text-black">{defect.latitude.toFixed(6)}° N</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60 print:border-gray-300">
                  <span className="text-slate-400 print:text-gray-600">GPS Longitude:</span>
                  <span className="font-bold text-white print:text-black">{defect.longitude.toFixed(6)}° E</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60 print:border-gray-300">
                  <span className="text-slate-400 print:text-gray-600">Detecting Edge Bus:</span>
                  <span className="font-bold text-cyan-400 print:text-blue-800">{defect.bus_id}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60 print:border-gray-300">
                  <span className="text-slate-400 print:text-gray-600">Timestamp Logged:</span>
                  <span className="font-bold text-white print:text-black">
                    {new Date(defect.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60 print:border-gray-300">
                  <span className="text-slate-400 print:text-gray-600">Designated Corridor:</span>
                  <span className="font-bold text-white print:text-black">Anna Salai (Mount Road) Sector 3</span>
                </div>
              </div>

              {/* Statutory SLA */}
              <div className="mt-3 p-3 bg-rose-950/40 border border-rose-800/60 rounded-lg print:bg-red-50 print:border-red-300">
                <div className="flex items-center gap-2 text-rose-400 print:text-red-700 text-xs font-bold">
                  <Clock className="w-4 h-4" />
                  <span>SLA RESOLUTION TIMEFRAME:</span>
                </div>
                <div className="mt-1 font-mono font-bold text-sm text-white print:text-red-900">
                  {getSLA(defect.severity)}
                </div>
              </div>
            </div>
          </div>

          {/* Bill of Quantities / Recommended Materials */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 print:text-blue-900 border-b border-slate-700 pb-1">
              Required Maintenance Materials & Equipment Allocation
            </h3>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
              {getMaterials(defect.defect_type).map((mat, i) => (
                <li key={i} className="flex items-center gap-2 p-2 bg-command-950/60 border border-slate-800 rounded print:bg-gray-50 print:border-gray-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 print:bg-blue-600" />
                  <span className="text-slate-200 print:text-black">{mat}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Signatures & Certification Block */}
          <div className="pt-6 border-t border-slate-700/80 grid grid-cols-3 gap-6 text-center text-xs font-mono">
            <div>
              <div className="h-12 border-b border-slate-600 print:border-black flex items-end justify-center pb-1">
                <span className="text-[10px] text-cyan-400 print:text-blue-900 font-bold">BEL-EDGE-AI-AUTOSIGN</span>
              </div>
              <span className="text-slate-400 print:text-gray-600 mt-1 block">Edge Telemetry Officer</span>
            </div>
            <div>
              <div className="h-12 border-b border-slate-600 print:border-black flex items-end justify-center pb-1">
                <span className="text-[10px] text-slate-300 print:text-black font-semibold">Er. K. Ramanathan, M.E.</span>
              </div>
              <span className="text-slate-400 print:text-gray-600 mt-1 block">Executive Road Engineer</span>
            </div>
            <div>
              <div className="h-12 border-b border-slate-600 print:border-black flex items-end justify-center pb-1">
                <span className="text-[10px] text-slate-300 print:text-black font-semibold">Municipal Contractor Seal</span>
              </div>
              <span className="text-slate-400 print:text-gray-600 mt-1 block">Executing Agency Representative</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
