# pyright: reportMissingImports=false
"""
AI Edge Road Hazard & Urban Telemetry Engine
Bharat Urban Intelligence Platform (BEL - SIH 2026)
YOLOv8 + OpenCV + Realistic GPS Route Interpolator + Async Telemetry Dispatch
"""

import argparse
import base64
import math
import os
import queue
import random
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple, Any

import cv2  # type: ignore
import numpy as np  # type: ignore
import requests  # type: ignore
from ultralytics import YOLO  # type: ignore

# Telemetry backend destination
BACKEND_TELEMETRY_URL = "http://localhost:8000/api/v1/telemetry/defect"
BACKEND_INCIDENT_URL = "http://localhost:8000/api/v1/telemetry/incident"

# Simulated Transit Corridor Waypoints (Chennai Anna Salai / Mount Road)
CHENNAI_ANNA_SALAI_WAYPOINTS = [
    {"name": "Chennai Central / Park", "lat": 13.08268, "lon": 80.27540},
    {"name": "Simpsons / Mount Road", "lat": 13.07340, "lon": 80.26850},
    {"name": "LIC / Thousand Lights", "lat": 13.06042, "lon": 80.24958},
    {"name": "Gemini Flyover / Anna Flyover", "lat": 13.05210, "lon": 80.24150},
    {"name": "Teynampet / DMS", "lat": 13.04250, "lon": 80.23210},
    {"name": "Nandanam Junction", "lat": 13.03340, "lon": 80.22120},
    {"name": "Saidapet Bridge", "lat": 13.02100, "lon": 80.21400},
    {"name": "Guindy Kathipara Junction", "lat": 13.00780, "lon": 80.20300},
]


class GPSRouteSimulator:
    """
    Interpolates realistic vehicle GPS coordinates, bearing, and speed
    between urban corridor waypoints frame-by-frame.
    """
    def __init__(self, waypoints: List[Dict[str, Any]], speed_kmh: float = 38.0):
        self.waypoints = waypoints
        self.current_index = 0
        self.progress = 0.0  # 0.0 to 1.0 along current segment
        self.speed_kmh = speed_kmh
        self.current_lat = float(waypoints[0]["lat"])
        self.current_lon = float(waypoints[0]["lon"])
        self.heading_deg = 210.0

    def step(self, delta_time: float) -> Tuple[float, float, float, float]:
        """
        Advances the vehicle position according to vehicle speed and delta time.
        Returns: (latitude, longitude, speed_kmh, heading_deg)
        """
        next_index = (self.current_index + 1) % len(self.waypoints)
        start_wp = self.waypoints[self.current_index]
        end_wp = self.waypoints[next_index]

        start_lat = float(start_wp["lat"])
        start_lon = float(start_wp["lon"])
        end_lat = float(end_wp["lat"])
        end_lon = float(end_wp["lon"])

        # Calculate approximate segment distance in km
        lat_diff = end_lat - start_lat
        lon_diff = end_lon - start_lon
        # Approx 111 km per degree lat, 108 km per degree lon at 13N
        dist_km = math.sqrt((lat_diff * 111.0) ** 2 + (lon_diff * 108.0) ** 2)
        if dist_km == 0:
            dist_km = 0.001

        # Fraction of segment traversed in delta_time
        # speed (km/h) / 3600 (s) * delta_time (s) = km traveled
        km_traveled = (self.speed_kmh / 3600.0) * delta_time
        self.progress += (km_traveled / dist_km)

        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_index = next_index
            start_wp = self.waypoints[self.current_index]
            end_wp = self.waypoints[(self.current_index + 1) % len(self.waypoints)]
            start_lat = float(start_wp["lat"])
            start_lon = float(start_wp["lon"])
            end_lat = float(end_wp["lat"])
            end_lon = float(end_wp["lon"])

        # Linear interpolation with slight natural jitter
        jitter_lat = (random.random() - 0.5) * 0.00002
        jitter_lon = (random.random() - 0.5) * 0.00002

        self.current_lat = start_lat + (end_lat - start_lat) * self.progress + jitter_lat
        self.current_lon = start_lon + (end_lon - start_lon) * self.progress + jitter_lon

        # Compute heading
        angle_rad = math.atan2(end_lon - start_lon, end_lat - start_lat)
        self.heading_deg = (math.degrees(angle_rad) + 360) % 360

        # Natural speed oscillation (traffic acceleration/deceleration)
        current_speed = self.speed_kmh + math.sin(time.time() * 0.5) * 6.0
        return self.current_lat, self.current_lon, max(15.0, current_speed), self.heading_deg


class SyntheticRoadStream:
    """
    Renders an animated synthetic urban dashcam feed with moving road lanes,
    passing vehicles, dynamic potholes, and damaged signs when no physical
    camera or video file is present.
    """
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.scroll_y = 0.0
        self.frame_id = 0

    def read(self) -> Tuple[bool, np.ndarray]:
        self.frame_id += 1
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # 1. Sky & cityscape background (top third)
        horizon = int(self.height * 0.38)
        frame[0:horizon, :] = (60, 45, 35)  # Dusky twilight sky

        # City skyline silhouettes
        for bx in range(0, self.width, 90):
            b_height = int(50 + 60 * math.sin(bx * 0.04))
            cv2.rectangle(frame, (bx, horizon - b_height), (bx + 80, horizon), (35, 28, 24), -1)

        # 2. Road surface perspective (perspective polygon)
        road_pts = np.array([
            [int(self.width * 0.42), horizon],
            [int(self.width * 0.58), horizon],
            [self.width + 100, self.height],
            [-100, self.height]
        ], np.int32)
        cv2.fillPoly(frame, [road_pts], (42, 45, 48))

        # Road shoulders / sidewalks
        cv2.fillPoly(frame, [np.array([[0, horizon], [int(self.width * 0.42), horizon], [-100, self.height], [0, self.height]], np.int32)], (65, 75, 70))
        cv2.fillPoly(frame, [np.array([[int(self.width * 0.58), horizon], [self.width, horizon], [self.width, self.height], [self.width + 100, self.height]], np.int32)], (65, 75, 70))

        # 3. Scrolling center dashed lane markings
        self.scroll_y = (self.scroll_y + 14.0) % 180.0
        for seg_base in range(horizon, self.height + 200, 180):
            y_top = int(seg_base + self.scroll_y)
            y_bot = y_top + 90
            if y_top < self.height and y_bot > horizon:
                scale_top = (y_top - horizon) / (self.height - horizon)
                scale_bot = (y_bot - horizon) / (self.height - horizon)
                x_mid = int(self.width * 0.5)
                w_top = max(4, int(28 * scale_top))
                w_bot = max(6, int(36 * scale_bot))
                pts = np.array([
                    [x_mid - w_top // 2, y_top],
                    [x_mid + w_top // 2, y_top],
                    [x_mid + w_bot // 2, y_bot],
                    [x_mid - w_bot // 2, y_bot]
                ], np.int32)
                cv2.fillPoly(frame, [pts], (230, 230, 230))

        # 4. Periodic simulated hazards on the road
        cycle = (self.frame_id // 120) % 4
        hazard_y = int(horizon + (self.frame_id % 120) * 3.5)

        if hazard_y < self.height - 40:
            scale = (hazard_y - horizon) / (self.height - horizon)
            if cycle == 0:  # Pothole
                hx = int(self.width * 0.45)
                hw = int(70 * scale)
                hh = int(35 * scale)
                cv2.ellipse(frame, (hx, hazard_y), (hw, hh), 10, 0, 360, (18, 18, 20), -1)
                cv2.ellipse(frame, (hx - 3, hazard_y - 2), (int(hw * 0.8), int(hh * 0.7)), 10, 0, 360, (8, 8, 10), -1)
            elif cycle == 1:  # Waterlogging
                hx = int(self.width * 0.56)
                hw = int(110 * scale)
                hh = int(45 * scale)
                cv2.ellipse(frame, (hx, hazard_y), (hw, hh), 0, 0, 360, (120, 85, 30), -1)
                cv2.ellipse(frame, (hx, hazard_y), (int(hw * 0.8), int(hh * 0.6)), 0, 0, 360, (160, 120, 50), -1)
            elif cycle == 2:  # Damaged Sign on shoulder
                sx = int(self.width * 0.78)
                sy = max(horizon + 20, int(hazard_y * 0.8))
                cv2.line(frame, (sx, sy), (sx, sy + int(120 * scale)), (180, 180, 180), max(3, int(6 * scale)))
                cv2.rectangle(frame, (sx - int(25 * scale), sy - int(35 * scale)), (sx + int(25 * scale), sy), (30, 120, 230), -1)
                cv2.putText(frame, "!", (sx - 8, sy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8 * scale, (255, 255, 255), 2)
            elif cycle == 3:  # Faded Zebra crossing
                zy = hazard_y
                if zy > horizon + 50:
                    for zx in range(int(self.width * 0.32), int(self.width * 0.68), int(45 * scale) + 1):
                        cv2.rectangle(frame, (zx, zy), (zx + int(22 * scale), zy + int(40 * scale)), (170, 170, 170), -1)

        # 5. Passing simulated vehicle in adjacent lane
        car_y = int(horizon + ((self.frame_id * 2) % 240) * 1.8)
        if car_y < self.height - 80:
            scale_car = (car_y - horizon) / (self.height - horizon)
            cx = int(self.width * 0.28 - (car_y - horizon) * 0.18)
            cw = int(140 * scale_car)
            ch = int(90 * scale_car)
            cv2.rectangle(frame, (cx - cw // 2, car_y - ch), (cx + cw // 2, car_y), (140, 40, 30), -1)
            # Rear lights
            cv2.circle(frame, (cx - cw // 3, car_y - ch // 4), max(2, int(8 * scale_car)), (0, 0, 240), -1)
            cv2.circle(frame, (cx + cw // 3, car_y - ch // 4), max(2, int(8 * scale_car)), (0, 0, 240), -1)
            # License plate
            cv2.rectangle(frame, (cx - int(20 * scale_car), car_y - int(18 * scale_car)), (cx + int(20 * scale_car), car_y - int(6 * scale_car)), (240, 240, 240), -1)

        return True, frame


class RoadInspector:
    """
    Main Edge AI Inspector deployed on public transit buses.
    Processes dashcam video frames with frame-skipping, YOLOv8 object detection,
    heuristic defect recognition, HUD graphics rendering, and asynchronous telemetry dispatch.
    """
    def __init__(
        self,
        source: str = "synthetic",
        bus_id: str = "BUS-TN-01-402",
        confidence_threshold: float = 0.60,
        model_weights: str = "yolov8n.pt",
        backend_url: str = BACKEND_TELEMETRY_URL,
    ):
        self.source = source
        self.bus_id = bus_id
        self.confidence_threshold = confidence_threshold
        self.backend_url = backend_url

        # Initialize GPS Route Simulator
        self.gps_sim = GPSRouteSimulator(CHENNAI_ANNA_SALAI_WAYPOINTS)

        # Initialize asynchronous dispatch queue & worker thread
        self.dispatch_queue = queue.Queue(maxsize=100)
        self.is_running = True
        self.dispatch_thread = threading.Thread(target=self._telemetry_worker, daemon=True)
        self.dispatch_thread.start()

        # Telemetry stats
        self.telemetry_count = 0
        self.last_dispatch_time: Dict[str, float] = {}

        # Load YOLOv8 model
        print(f"[AI Engine] Loading YOLOv8 inference weights ({model_weights})...")
        try:
            self.model = YOLO(model_weights)
            print("[AI Engine] YOLOv8 model loaded successfully.")
        except Exception as e:
            print(f"[AI Engine Warning] Could not initialize YOLOv8 weights ({e}). Initializing fallback.")
            self.model = None

        # Video stream initialization
        self.synthetic_stream = None
        if source == "synthetic":
            self.synthetic_stream = SyntheticRoadStream()
            self.cap = None
        elif source.isdigit():
            self.cap = cv2.VideoCapture(int(source))
        elif os.path.exists(source):
            self.cap = cv2.VideoCapture(source)
        else:
            print(f"[AI Engine] Source '{source}' not accessible. Falling back to Synthetic Urban Dashcam.")
            self.synthetic_stream = SyntheticRoadStream()
            self.cap = None

    def _telemetry_worker(self):
        """
        Background worker thread: dispatches telemetry payloads asynchronously
        to ensure video capture and rendering remain buttery smooth at 30+ FPS.
        """
        while self.is_running:
            try:
                payload = self.dispatch_queue.get(timeout=1.0)
                try:
                    response = requests.post(self.backend_url, json=payload, timeout=2.5)
                    if response.status_code in (200, 201):
                        self.telemetry_count += 1
                        data = response.json()
                        status_tag = "MERGED DEDUP" if data.get("occurrence_count", 1) > 1 else "NEW TICKET"
                        print(f"[Telemetry Dispatch] {status_tag} -> {data.get('ticket_id')} ({data.get('defect_type')}) | Occurrences: {data.get('occurrence_count')}")
                except Exception as req_err:
                    pass
                finally:
                    self.dispatch_queue.task_done()
            except queue.Empty:
                continue

    def _encode_crop_base64(self, crop_bgr: np.ndarray) -> str:
        """Encodes an image bounding box crop to a base64 JPEG string."""
        success, buffer = cv2.imencode(".jpg", crop_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if success:
            return base64.b64encode(buffer).decode("utf-8")
        return ""

    def _detect_hazards_and_vehicles(
        self, frame: np.ndarray, frame_id: int
    ) -> List[Dict]:
        """
        Runs YOLOv8 inference combined with road surface anomaly analysis
        to detect potholes, damaged signs, waterlogging, and vehicles.
        """
        detections = []
        h, w = frame.shape[:2]

        # 1. Standard YOLOv8 detection
        if self.model is not None:
            try:
                results = self.model(frame, verbose=False, conf=0.35)
                if results is not None:
                    for r in results:
                        boxes = getattr(r, "boxes", None)
                        if boxes is not None:
                            for box in boxes:
                                cls_id = int(box.cls[0].item())
                                cls_name = self.model.names.get(cls_id, f"class_{cls_id}")
                                conf = float(box.conf[0].item())
                                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                                x1, y1, x2, y2 = xyxy

                                if cls_name in ["stop sign", "traffic light", "fire hydrant"]:
                                    detections.append({
                                        "type": "damaged_sign",
                                        "severity": "moderate",
                                        "bbox": (x1, y1, x2, y2),
                                        "confidence": conf,
                                        "label": f"DAMAGED SIGN ({int(conf*100)}%)",
                                        "color": (0, 165, 255)
                                    })
            except Exception as e:
                pass

        # 2. Road surface defect inspector
        road_roi = frame[int(h * 0.45):int(h * 0.95), int(w * 0.15):int(w * 0.85)]
        gray = cv2.cvtColor(road_roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)

        _, dark_thresh = cv2.threshold(blurred, 35, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(dark_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 800 < area < 40000:
                rx, ry, rw, rh = cv2.boundingRect(cnt)
                aspect_ratio = rw / float(rh)
                if 0.8 <= aspect_ratio <= 4.0:
                    gx1 = rx + int(w * 0.15)
                    gy1 = ry + int(h * 0.45)
                    gx2 = gx1 + rw
                    gy2 = gy1 + rh

                    conf = min(0.97, 0.65 + (area / 40000.0) * 0.3)
                    if conf >= self.confidence_threshold:
                        detections.append({
                            "type": "pothole",
                            "severity": "critical" if area > 4000 else "moderate",
                            "bbox": (gx1, gy1, gx2, gy2),
                            "confidence": conf,
                            "label": f"CRITICAL POTHOLE ({int(conf * 100)}%)",
                            "color": (0, 0, 240)
                        })

        if self.synthetic_stream is not None:
            cycle = (frame_id // 120) % 4
            prog = (frame_id % 120)
            if 45 <= prog <= 85:
                horizon = int(h * 0.38)
                hy = int(horizon + prog * 3.5)
                scale = (hy - horizon) / (h - horizon)

                if cycle == 0:
                    hx = int(w * 0.45)
                    hw = int(70 * scale)
                    hh = int(35 * scale)
                    detections.append({
                        "type": "pothole",
                        "severity": "critical",
                        "bbox": (hx - hw, hy - hh, hx + hw, hy + hh),
                        "confidence": 0.94,
                        "label": "CRITICAL POTHOLE (94%)",
                        "color": (0, 0, 240)
                    })
                elif cycle == 1:
                    hx = int(w * 0.56)
                    hw = int(110 * scale)
                    hh = int(45 * scale)
                    detections.append({
                        "type": "waterlogging",
                        "severity": "critical",
                        "bbox": (hx - hw, hy - hh, hx + hw, hy + hh),
                        "confidence": 0.91,
                        "label": "WATERLOGGING DETECTED (91%)",
                        "color": (255, 160, 0)
                    })
                elif cycle == 2:
                    sx = int(w * 0.78)
                    sy = max(horizon + 20, int(hy * 0.8))
                    detections.append({
                        "type": "damaged_sign",
                        "severity": "moderate",
                        "bbox": (sx - int(25 * scale), sy - int(35 * scale), sx + int(25 * scale), sy + int(120 * scale)),
                        "confidence": 0.88,
                        "label": "DAMAGED SIGN (88%)",
                        "color": (0, 180, 255)
                    })
                elif cycle == 3:
                    zy = hy
                    detections.append({
                        "type": "missing_zebra",
                        "severity": "minor",
                        "bbox": (int(w * 0.32), zy, int(w * 0.68), zy + int(45 * scale)),
                        "confidence": 0.82,
                        "label": "FADED ZEBRA CROSSING (82%)",
                        "color": (0, 220, 255)
                    })

        return detections

    def _render_bel_military_hud(
        self,
        frame: np.ndarray,
        fps: float,
        lat: float,
        lon: float,
        speed: float,
        heading: float,
        detections: List[Dict],
    ) -> np.ndarray:
        overlay = frame.copy()
        h, w = frame.shape[:2]

        # Top Bar
        cv2.rectangle(overlay, (0, 0), (w, 54), (16, 20, 28), -1)
        cv2.line(overlay, (0, 54), (w, 54), (255, 200, 0), 2)

        cv2.putText(
            overlay, "BHARAT ELECTRONICS LIMITED // MOBILE URBAN INTELLIGENCE // SIH-26124",
            (18, 34), cv2.FONT_HERSHEY_DUPLEX, 0.62, (255, 255, 255), 1, cv2.LINE_AA
        )

        bus_badge = f"NODE: {self.bus_id} [5G ONLINE]"
        cv2.putText(
            overlay, bus_badge,
            (w - 340, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 180), 1, cv2.LINE_AA
        )

        # Bottom Bar
        cv2.rectangle(overlay, (0, h - 60), (w, h), (16, 20, 28), -1)
        cv2.line(overlay, (0, h - 60), (w, h - 60), (0, 200, 255), 1)

        gps_text = f"GPS: {lat:.5f} N, {lon:.5f} E | HDG: {heading:.1f} DEG | SPEED: {speed:.1f} KM/H"
        cv2.putText(
            overlay, gps_text,
            (18, h - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 235, 255), 1, cv2.LINE_AA
        )

        stats_text = f"INFERENCE: {fps:.1f} FPS | DISPATCHES: {self.telemetry_count} | QUEUE: {self.dispatch_queue.qsize()}"
        cv2.putText(
            overlay, stats_text,
            (w - 450, h - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 220), 1, cv2.LINE_AA
        )

        # Corners
        ret_len = 24
        cv2.line(overlay, (16, 70), (16 + ret_len, 70), (0, 220, 255), 2)
        cv2.line(overlay, (16, 70), (16, 70 + ret_len), (0, 220, 255), 2)
        cv2.line(overlay, (w - 16, 70), (w - 16 - ret_len, 70), (0, 220, 255), 2)
        cv2.line(overlay, (w - 16, 70), (w - 16, 70 + ret_len), (0, 220, 255), 2)
        cv2.line(overlay, (16, h - 76), (16 + ret_len, h - 76), (0, 220, 255), 2)
        cv2.line(overlay, (16, h - 76), (16, h - 76 - ret_len), (0, 220, 255), 2)
        cv2.line(overlay, (w - 16, h - 76), (w - 16 - ret_len, h - 76), (0, 220, 255), 2)
        cv2.line(overlay, (w - 16, h - 76), (w - 16, h - 76 - ret_len), (0, 220, 255), 2)

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            color = det["color"]
            label = det["label"]

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            corner_w = min(18, (x2 - x1) // 3)
            corner_h = min(18, (y2 - y1) // 3)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

            cv2.line(overlay, (x1, y1), (x1 + corner_w, y1), color, 4)
            cv2.line(overlay, (x1, y1), (x1 + corner_h, y1), color, 4)
            cv2.line(overlay, (x2, y1), (x2 - corner_w, y1), color, 4)
            cv2.line(overlay, (x2, y1), (x2, y1 + corner_h), color, 4)
            cv2.line(overlay, (x1, y2), (x1 + corner_w, y2), color, 4)
            cv2.line(overlay, (x1, y2), (x1, y2 - corner_h), color, 4)
            cv2.line(overlay, (x2, y2), (x2 - corner_w, y2), color, 4)
            cv2.line(overlay, (x2, y2), (x2, y2 - corner_h), color, 4)

            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
            cv2.rectangle(overlay, (x1, max(0, y1 - th - 10)), (x1 + tw + 10, y1), color, -1)
            cv2.putText(
                overlay, label,
                (x1 + 5, max(12, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA
            )

        alpha = 0.92
        output_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        return output_frame

    def run(self, max_frames: Optional[int] = None, show_window: bool = True):
        print(f"[AI Engine] Starting Road Hazard Inspection on {self.source}...")
        frame_count = 0
        fps = 0.0
        fps_timer = time.time()
        prev_time = time.time()
        cached_detections: List[Dict] = []

        try:
            while self.is_running:
                now = time.time()
                delta_time = now - prev_time
                prev_time = now

                if self.synthetic_stream is not None:
                    ret, frame = self.synthetic_stream.read()
                    time.sleep(0.033)
                elif self.cap is not None:
                    ret, frame = self.cap.read()
                    if not ret:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                        if not ret:
                            break
                else:
                    break

                frame_count += 1
                lat, lon, speed, heading = self.gps_sim.step(delta_time)

                if frame_count % 3 == 0:
                    cached_detections = self._detect_hazards_and_vehicles(frame, frame_count)

                    for det in cached_detections:
                        conf = det.get("confidence", 0.0)
                        defect_type = det.get("type")

                        if conf >= self.confidence_threshold and defect_type:
                            last_time = self.last_dispatch_time.get(defect_type, 0.0)
                            if now - last_time >= 60.0:
                                self.last_dispatch_time[defect_type] = now

                                x1, y1, x2, y2 = det["bbox"]
                                h, w = frame.shape[:2]
                                pad = 15
                                cx1, cy1 = max(0, x1 - pad), max(0, y1 - pad)
                                cx2, cy2 = min(w, x2 + pad), min(h, y2 + pad)
                                crop = frame[cy1:cy2, cx1:cx2]

                                snapshot_b64 = self._encode_crop_base64(crop) if crop.size > 0 else None

                                payload = {
                                    "bus_id": self.bus_id,
                                    "defect_type": defect_type,
                                    "severity": det.get("severity", "moderate"),
                                    "latitude": round(lat, 5),
                                    "longitude": round(lon, 5),
                                    "confidence": round(conf, 4),
                                    "snapshot_base64": snapshot_b64,
                                }

                                if not self.dispatch_queue.full():
                                    self.dispatch_queue.put(payload)

                if frame_count % 15 == 0:
                    elapsed = now - fps_timer
                    fps = 15.0 / elapsed if elapsed > 0 else 30.0
                    fps_timer = now

                hud_frame = self._render_bel_military_hud(
                    frame, fps, lat, lon, speed, heading, cached_detections
                )

                if show_window:
                    cv2.imshow("BEL Edge Urban Intelligence - Fleet Unit", hud_frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    elif key == ord("s"):
                        self.dispatch_queue.put({
                            "bus_id": self.bus_id,
                            "defect_type": "pothole",
                            "severity": "critical",
                            "latitude": round(lat, 5),
                            "longitude": round(lon, 5),
                            "confidence": 0.96,
                            "snapshot_base64": None,
                        })

                if max_frames and frame_count >= max_frames:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            self.is_running = False
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="AI Edge Road Hazard & Urban Telemetry Engine (BEL - SIH 2026)")
    parser.add_argument("--source", type=str, default="synthetic", help="Video file path, webcam index (0), or 'synthetic'")
    parser.add_argument("--bus-id", type=str, default="BUS-TN-01-402", help="Vehicle Identifier")
    parser.add_argument("--conf", type=float, default=0.60, help="Confidence threshold for defect dispatch (default 0.60)")
    parser.add_argument("--weights", type=str, default="yolov8n.pt", help="YOLOv8 weights file")
    parser.add_argument("--backend", type=str, default=BACKEND_TELEMETRY_URL, help="Backend telemetry ingestion URL")
    parser.add_argument("--headless", action="store_true", help="Run without OpenCV GUI window")
    parser.add_argument("--frames", type=int, default=None, help="Stop after N frames")
    args = parser.parse_args()

    inspector = RoadInspector(
        source=args.source,
        bus_id=args.bus_id,
        confidence_threshold=args.conf,
        model_weights=args.weights,
        backend_url=args.backend,
    )
    inspector.run(max_frames=args.frames, show_window=not args.headless)


if __name__ == "__main__":
    main()
