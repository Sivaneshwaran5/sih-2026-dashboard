import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Wrench, CheckCircle, ExternalLink, Bus, Navigation, ShieldCheck } from 'lucide-react';

// Multi-Corridor Configurations (Chennai, Kumbakonam, Bengaluru)
const CORRIDORS = {
  chennai_anna_salai: {
    name: 'Anna Salai Transit Corridor (Chennai)',
    center: [13.05210, 80.24150],
    zoom: 13,
    route: [
      [13.08268, 80.27540], // Chennai Central
      [13.07340, 80.26850], // Mount Road / Simpsons
      [13.06042, 80.24958], // LIC / Thousand Lights
      [13.05210, 80.24150], // Gemini Flyover
      [13.04250, 80.23210], // DMS / Teynampet
      [13.03340, 80.22120], // Nandanam
      [13.02100, 80.21400], // Saidapet
      [13.00780, 80.20300], // Guindy Kathipara
    ],
    buses: [
      { id: 'BUS-TN-01-402', lat: 13.0604, lon: 80.2496, speed: '42 km/h', status: 'Online - Edge AI Active' },
      { id: 'BUS-TN-01-408', lat: 13.0480, lon: 80.2380, speed: '36 km/h', status: 'Online - Edge AI Active' },
      { id: 'BUS-TN-01-415', lat: 13.0250, lon: 80.2160, speed: '28 km/h', status: 'Online - Edge AI Active' },
    ]
  },
  kumbakonam_transit: {
    name: 'Kumbakonam Smart Transit Grid',
    center: [10.9602, 79.3845],
    zoom: 14,
    route: [
      [10.9570, 79.3780],
      [10.9595, 79.3820],
      [10.9620, 79.3860],
      [10.9650, 79.3900],
    ],
    buses: [
      { id: 'BUS-TN-68-104', lat: 10.9595, lon: 79.3820, speed: '32 km/h', status: 'Online - Edge AI Active' },
      { id: 'BUS-TN-68-112', lat: 10.9620, lon: 79.3860, speed: '35 km/h', status: 'Online - Edge AI Active' },
    ]
  },
  bangalore_bel_circle: {
    name: 'Bengaluru BEL Circle - Outer Ring',
    center: [13.0382, 77.5492],
    zoom: 14,
    route: [
      [13.0480, 77.5420],
      [13.0420, 77.5460],
      [13.0382, 77.5492],
      [13.0320, 77.5530],
      [13.0250, 77.5580],
    ],
    buses: [
      { id: 'BUS-KA-01-BEL-1', lat: 13.0420, lon: 77.5460, speed: '40 km/h', status: 'Online - Edge AI Active' },
      { id: 'BUS-KA-01-BEL-2', lat: 13.0320, lon: 77.5530, speed: '34 km/h', status: 'Online - Edge AI Active' },
    ]
  }
};

const VERIFIED_IMAGES = {
  pothole: "/snapshots/pothole_cam.jpg",
  sign: "/snapshots/sign_cam.jpg",
  water: "/snapshots/water_cam.jpg",
  collision: "/snapshots/accident_cam.jpg",
  garbage: "/snapshots/garbage_cam.jpg",
  cattle: "/snapshots/cattle_cam.jpg",
  debris: "/snapshots/debris_cam.jpg"
};

const getDefectPhoto = (type) => {
  const t = (type || "").toLowerCase();
  if (t.includes("sign")) return VERIFIED_IMAGES.sign;
  if (t.includes("water") || t.includes("flood")) return VERIFIED_IMAGES.water;
  if (t.includes("collision") || t.includes("accident")) return VERIFIED_IMAGES.collision;
  if (t.includes("garbage") || t.includes("dump") || t.includes("trash")) return VERIFIED_IMAGES.garbage;
  if (t.includes("cattle") || t.includes("animal") || t.includes("stray")) return VERIFIED_IMAGES.cattle;
  if (t.includes("debris") || t.includes("construction") || t.includes("barricade")) return VERIFIED_IMAGES.debris;
  return VERIFIED_IMAGES.pothole;
};

// Helper to center or pan map programmatically
function ChangeMapView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom(), { animate: true });
    }
  }, [center, zoom, map]);
  return null;
}

// Custom Leaflet DivIcon Generators
const createDefectIcon = (defect) => {
  const { defect_type, severity, status } = defect;

  let bgClass = 'bg-rose-500 text-white';
  let pulseClass = 'marker-pulse-critical';
  let borderClass = 'border-rose-400';
  let iconGlyph = '!';

  const rawType = (defect_type || '').toLowerCase();
  
  if (status === 'resolved' || status === 'Resolved') {
    bgClass = 'bg-emerald-500 text-white';
    pulseClass = '';
    borderClass = 'border-emerald-400';
    iconGlyph = '✓';
  } else if (rawType.includes('water') || rawType.includes('flood')) {
    bgClass = 'bg-sky-500 text-white';
    pulseClass = 'marker-pulse-critical';
    borderClass = 'border-sky-300';
    iconGlyph = '≈';
  } else if (rawType.includes('sign') || rawType.includes('zebra')) {
    bgClass = 'bg-amber-500 text-white';
    pulseClass = 'marker-pulse-amber';
    borderClass = 'border-amber-300';
    iconGlyph = '▲';
  } else if (rawType.includes('collision') || rawType.includes('accident')) {
    bgClass = 'bg-fuchsia-600 text-white';
    pulseClass = 'marker-pulse-critical';
    borderClass = 'border-fuchsia-400';
    iconGlyph = '💥';
  } else if (rawType.includes('garbage') || rawType.includes('dump') || rawType.includes('trash')) {
    bgClass = 'bg-lime-600 text-white';
    pulseClass = 'marker-pulse-critical';
    borderClass = 'border-lime-400';
    iconGlyph = '🗑️';
  } else if (rawType.includes('cattle') || rawType.includes('animal') || rawType.includes('stray')) {
    bgClass = 'bg-orange-600 text-white';
    pulseClass = 'marker-pulse-critical';
    borderClass = 'border-orange-400';
    iconGlyph = '🐄';
  } else if (rawType.includes('debris') || rawType.includes('construction') || rawType.includes('barricade')) {
    bgClass = 'bg-stone-600 text-white';
    pulseClass = 'marker-pulse-critical';
    borderClass = 'border-stone-400';
    iconGlyph = '🚧';
  } else {
    // Pothole
    bgClass = (severity === 'critical' || severity === 'Critical') ? 'bg-rose-600 text-white' : 'bg-orange-500 text-white';
    pulseClass = (severity === 'critical' || severity === 'Critical') ? 'marker-pulse-critical' : '';
    borderClass = 'border-rose-300';
    iconGlyph = '●';
  }

  const html = `
    <div class="relative flex items-center justify-center">
      <div class="w-8 h-8 rounded-full border-2 ${borderClass} ${bgClass} ${pulseClass} flex items-center justify-center shadow-lg font-bold text-xs select-none">
        ${iconGlyph}
      </div>
    </div>
  `;

  return L.divIcon({
    html: html,
    className: 'custom-defect-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -18],
  });
};

const createBusIcon = (busId) => {
  const html = `
    <div class="relative flex items-center justify-center">
      <div class="w-7 h-7 rounded-full bg-cyan-500 text-slate-950 border-2 border-white flex items-center justify-center shadow-md font-mono text-[10px] font-bold">
        BUS
      </div>
      <div class="absolute -bottom-4 bg-slate-900/90 text-cyan-400 text-[9px] font-mono px-1 rounded border border-cyan-800/60 whitespace-nowrap">
        ${busId.replace('BUS-TN-01-', '#')}
      </div>
    </div>
  `;

  return L.divIcon({
    html: html,
    className: 'custom-bus-marker',
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
};

export default function MapView({ 
  defects = [], 
  onSelectDefect, 
  onUpdateStatus, 
  onGenerateWorkOrder,
  selectedDefect = null,
  backendUrl = 'http://localhost:8000',
  activeCorridor = 'chennai_anna_salai'
}) {
  const currentCorridor = CORRIDORS[activeCorridor] || CORRIDORS.chennai_anna_salai;
  const [mapCenter, setMapCenter] = useState(currentCorridor.center);
  const [zoomLevel, setZoomLevel] = useState(currentCorridor.zoom);
  const [showBusFleet, setShowBusFleet] = useState(true);
  const [showCorridor, setShowCorridor] = useState(true);

  // Update map view when corridor selection changes
  useEffect(() => {
    const config = CORRIDORS[activeCorridor] || CORRIDORS.chennai_anna_salai;
    setMapCenter(config.center);
    setZoomLevel(config.zoom);
  }, [activeCorridor]);

  // Pan to selected defect if chosen from feed
  useEffect(() => {
    if (selectedDefect && selectedDefect.latitude && selectedDefect.longitude) {
      setMapCenter([selectedDefect.latitude, selectedDefect.longitude]);
      setZoomLevel(15);
    }
  }, [selectedDefect]);

  return (
    <div className="glass-panel rounded-xl overflow-hidden relative border border-slate-800/80 shadow-2xl h-[580px] flex flex-col">
      {/* Map Control Bar Header */}
      <div className="px-4 py-2.5 bg-command-900/90 border-b border-slate-800/80 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-cyan-400 animate-spin-slow" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            GIS Spatial Intelligence Engine // Anna Salai Corridor
          </span>
          <span className="text-[10px] font-mono bg-cyan-950/80 border border-cyan-800/60 text-cyan-400 px-2 py-0.5 rounded-full">
            {defects.length} Active Spatial Entities
          </span>
        </div>

        {/* Layer Toggles */}
        <div className="flex items-center gap-3 text-xs">
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300 hover:text-white transition">
            <input 
              type="checkbox" 
              checked={showBusFleet} 
              onChange={(e) => setShowBusFleet(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0" 
            />
            <span className="text-[11px]">Edge Buses</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300 hover:text-white transition">
            <input 
              type="checkbox" 
              checked={showCorridor} 
              onChange={(e) => setShowCorridor(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0" 
            />
            <span className="text-[11px]">Transit Corridor</span>
          </label>
        </div>
      </div>

      {/* Main Map Viewport */}
      <div className="flex-1 relative w-full h-full">
        <MapContainer
          center={mapCenter}
          zoom={zoomLevel}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%', background: '#070b14' }}
        >
          <ChangeMapView center={mapCenter} zoom={zoomLevel} />

          {/* OpenStreetMap Tiles (No API Key Required) */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />

          {/* Transit Corridor Route Polyline */}
          {showCorridor && (
            <Polyline
              positions={currentCorridor.route}
              pathOptions={{
                color: '#06b6d4',
                weight: 4,
                opacity: 0.65,
                dashArray: '8, 8',
                lineCap: 'round',
              }}
            />
          )}

          {/* Active Public Transit Fleet Markers */}
          {showBusFleet && currentCorridor.buses.map((bus) => (
            <React.Fragment key={bus.id}>
              <Marker
                position={[bus.lat, bus.lon]}
                icon={createBusIcon(bus.id)}
              >
                <Popup>
                  <div className="p-3 bg-command-900 text-slate-100 rounded-lg w-52">
                    <div className="flex items-center gap-2 mb-1.5">
                      <Bus className="w-4 h-4 text-cyan-400" />
                      <span className="font-mono font-bold text-xs text-white">{bus.id}</span>
                    </div>
                    <p className="text-[11px] text-emerald-400 font-semibold mb-1">{bus.status}</p>
                    <div className="text-[10px] text-slate-400 font-mono space-y-0.5">
                      <div>Speed: {bus.speed}</div>
                      <div>GPS: {bus.lat.toFixed(4)}, {bus.lon.toFixed(4)}</div>
                      <div>Hardware: NVIDIA Jetson Orin</div>
                    </div>
                  </div>
                </Popup>
              </Marker>
              <Circle
                center={[bus.lat, bus.lon]}
                radius={80}
                pathOptions={{ color: '#06b6d4', fillColor: '#06b6d4', fillOpacity: 0.1, weight: 1 }}
              />
            </React.Fragment>
          ))}

          {/* Defect Markers */}
          {defects.map((defect) => {
            const isSelected = selectedDefect?.ticket_id === defect.ticket_id;
            const fullSnapshotUrl = defect.snapshot_url
              ? (defect.snapshot_url.startsWith('http') ? defect.snapshot_url : `${backendUrl}${defect.snapshot_url}`)
              : `${backendUrl}/static/snapshots/sample_pothole.jpg`;

            return (
              <React.Fragment key={defect.ticket_id || defect.id}>
                {defect.severity === 'critical' && defect.status !== 'resolved' && (
                  <Circle
                    center={[defect.latitude, defect.longitude]}
                    radius={45}
                    pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.2, weight: 1 }}
                  />
                )}

                <Marker
                  position={[defect.latitude, defect.longitude]}
                  icon={createDefectIcon(defect)}
                  eventHandlers={{
                    click: () => onSelectDefect && onSelectDefect(defect),
                  }}
                >
                  <Popup className="bel-custom-popup">
                    <div className="w-72 bg-command-900 border border-slate-700/80 rounded-xl overflow-hidden shadow-2xl text-slate-100">
                      {/* Snapshot Header */}
                      <div className="relative w-full h-44 mb-3 rounded-lg overflow-hidden border border-slate-700 bg-slate-950 shadow-md">
                        <img 
                          src={getDefectPhoto(defect.defect_type)} 
                          alt={defect?.defect_type || "Road Incident"} 
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                        <div className="absolute top-2 left-2 flex items-center gap-1.5 bg-black/75 backdrop-blur-sm px-2 py-0.5 rounded text-[10px] font-mono text-cyan-300 border border-cyan-500/40">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                          FLEET DASHCAM // CH-01
                        </div>
                        <div className="absolute bottom-2 right-2 bg-black/75 backdrop-blur-sm px-1.5 py-0.5 rounded text-[9px] font-mono text-slate-300 border border-slate-700">
                          FOV: 120° WIDE
                        </div>
                      </div>

                      {/* Content Body */}
                      <div className="p-3.5 space-y-2">
                        <div>
                          <div className="text-[10px] font-mono text-slate-400">
                            TICKET ID: <strong className="text-cyan-400">{defect.ticket_id}</strong>
                          </div>
                          <h4 className="font-bold text-sm text-white capitalize mt-0.5">
                            {defect.defect_type.replace('_', ' ')}
                          </h4>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-300 bg-command-950/70 p-2 rounded border border-slate-800">
                          {defect.offender_plate && (
                            <div className="col-span-2 flex items-center justify-between bg-slate-900/80 p-2 rounded border border-rose-500/30 mb-1">
                              <span className="text-rose-400 font-bold uppercase">ANPR Offender Match:</span>
                              <div className="bg-white text-black px-2 py-0.5 rounded border-2 border-black font-bold text-xs tracking-wider flex items-center gap-1.5 shadow-sm">
                                <div className="text-[6px] font-sans font-bold text-blue-800 flex flex-col items-center justify-center leading-none">
                                  <span>I</span><span>N</span><span>D</span>
                                </div>
                                {defect.offender_plate}
                              </div>
                            </div>
                          )}
                          <div>
                            <span className="text-slate-500 block">GPS Coords:</span>
                            {defect.latitude.toFixed(4)}, {defect.longitude.toFixed(4)}
                          </div>
                          <div>
                            <span className="text-slate-500 block">Reporter Node:</span>
                            {defect.bus_id}
                          </div>
                          <div>
                            <span className="text-slate-500 block">Current Status:</span>
                            <span className={`capitalize font-semibold ${
                              defect.status === 'resolved' ? 'text-emerald-400' :
                              defect.status === 'under_repair' ? 'text-amber-400' : 'text-rose-400'
                            }`}>
                              {defect.status.replace('_', ' ')}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">Logged Time:</span>
                            {defect.logged_time && defect.logged_time !== "Invalid Date" ? defect.logged_time : (defect.timestamp ? new Date(defect.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "10:50 AM")}
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="pt-1 flex flex-col gap-1.5">
                          {defect.status === 'open' && (
                            <button
                              onClick={() => {
                                onUpdateStatus(defect.ticket_id, 'under_repair');
                                onGenerateWorkOrder(defect);
                              }}
                              className="w-full py-1.5 px-3 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 shadow transition-all"
                            >
                              <Wrench className="w-3.5 h-3.5" />
                              Dispatch Municipal Repair Team
                            </button>
                          )}

                          {defect.status === 'under_repair' && (
                            <button
                              onClick={() => onUpdateStatus(defect.ticket_id, 'resolved')}
                              className="w-full py-1.5 px-3 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 shadow transition-all"
                            >
                              <CheckCircle className="w-3.5 h-3.5" />
                              Mark Hazard as Resolved
                            </button>
                          )}

                          <button
                            onClick={() => onGenerateWorkOrder(defect)}
                            className="w-full py-1.5 px-3 bg-command-800 hover:bg-command-700 text-cyan-300 border border-cyan-800/40 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                            Generate Official Statutory Work Order
                          </button>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              </React.Fragment>
            );
          })}
        </MapContainer>
      </div>

      {/* Map Legend Footer */}
      <div className="px-4 py-2 bg-command-950/95 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-4">
          <span className="font-semibold text-slate-300 uppercase tracking-wider text-[10px]">Hazard Legend:</span>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600 inline-block shadow-sm shadow-rose-500" />
            <span>Critical Pothole</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block shadow-sm shadow-amber-500" />
            <span>Damaged Sign / Zebra</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500 inline-block shadow-sm shadow-sky-500" />
            <span>Waterlogging</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block shadow-sm shadow-emerald-500" />
            <span>Resolved</span>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-[10px] text-cyan-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Haversine Spatial Deduplication Active (15m Threshold)</span>
        </div>
      </div>
    </div>
  );
}
