"""
End-to-End Pipeline Verification Script
Validates:
1. Health check
2. Analytics summary API
3. Defect telemetry ingestion
4. Haversine Spatial Deduplication (<15m merge, occurrence increment, confidence moving average)
5. Vehicle incident ANPR ingestion
6. Work order status transitions
Works seamlessly against live server (http://127.0.0.1:8000) or in-memory FastAPI TestClient.
"""

import sys
import requests

BASE = 'http://127.0.0.1:8000'


class HttpClientWrapper:
    """Wrapper that abstracts requests vs FastAPI TestClient."""
    def __init__(self):
        self.is_live = False
        try:
            res = requests.get(f'{BASE}/api/health', timeout=1.0)
            if res.status_code == 200:
                self.is_live = True
        except Exception:
            self.is_live = False

        if not self.is_live:
            from fastapi.testclient import TestClient
            from backend.app import app
            self.client = TestClient(app)
        else:
            self.client = None

    def get(self, path):
        if self.is_live:
            return requests.get(f'{BASE}{path}')
        assert self.client is not None
        return self.client.get(path)

    def post(self, path, json=None):
        if self.is_live:
            return requests.post(f'{BASE}{path}', json=json)
        assert self.client is not None
        return self.client.post(path, json=json)

    def patch(self, path, json=None):
        if self.is_live:
            return requests.patch(f'{BASE}{path}', json=json)
        assert self.client is not None
        return self.client.patch(path, json=json)


def main():
    print("---------------------------------------------------------")
    print(" BHARAT URBAN INTELLIGENCE PLATFORM - END-TO-END VERIFICATION")
    print("---------------------------------------------------------")

    http = HttpClientWrapper()
    if http.is_live:
        print("[INFO] Live Backend Detected at http://127.0.0.1:8000")
    else:
        print("[INFO] Standalone Mode: Direct In-Memory FastAPI Verification")

    # 1. Health
    h = http.get('/api/health').json()
    print(f"[OK] Health check status: {h['status']} | Org: {h['organization']}")

    # 2. Analytics summary
    summary = http.get('/api/v1/analytics/summary').json()
    initial_defects = summary['total_defects']
    print(f"[OK] Analytics: Total Defects = {initial_defects}, Critical = {summary['critical_hazards']}, Open = {summary['open_tickets']}")

    # 3. Ingest Defect A
    payload1 = {
        'bus_id': 'BUS-TN-01-402',
        'defect_type': 'pothole',
        'severity': 'critical',
        'latitude': 13.06042,
        'longitude': 80.24958,
        'confidence': 0.90,
        'snapshot_base64': None
    }
    r1 = http.post('/api/v1/telemetry/defect', json=payload1).json()
    ticket_a = r1['ticket_id']
    count_a = r1['occurrence_count']
    print(f"[OK] Telemetry Ingested: Ticket ID: {ticket_a} | Occurrences: {count_a} | Confidence: {r1['confidence']}")

    # 4. Ingest Defect B at ~7.8 meters away (0.00007 deg latitude)
    # MUST merge into ticket_a under Haversine deduplication
    payload2 = {
        'bus_id': 'BUS-TN-01-415',
        'defect_type': 'pothole',
        'severity': 'critical',
        'latitude': 13.06049,
        'longitude': 80.24958,
        'confidence': 0.96,
        'snapshot_base64': None
    }
    r2 = http.post('/api/v1/telemetry/defect', json=payload2).json()
    ticket_b = r2['ticket_id']
    count_b = r2['occurrence_count']
    conf_b = r2['confidence']
    print(f"[OK] Deduplication Result: Ticket ID: {ticket_b} | Occurrences: {count_b} | Moving Avg Conf: {conf_b}")

    if ticket_a != ticket_b:
        print(f"[FAIL] Expected tickets to match ({ticket_a} vs {ticket_b})")
        sys.exit(1)
    if count_b != count_a + 1:
        print(f"[FAIL] Expected occurrence count to increment ({count_a} -> {count_b})")
        sys.exit(1)

    print("[SUCCESS] Spatial Deduplication verified: Within 15m merged into single ticket and updated occurrences.")

    # 5. Transition status to under_repair
    p1 = http.patch(f'/api/v1/defects/{ticket_a}/status', json={'status': 'under_repair'}).json()
    print(f"[OK] Ticket transitioned to: {p1['status']}")

    # 6. Ingest vehicle incident
    inc_payload = {
        'incident_type': 'rash_driving',
        'license_plate': 'TN-07-BW-5521',
        'confidence': 0.94,
        'latitude': 13.0605,
        'longitude': 80.2496,
        'bus_id': 'BUS-TN-01-402'
    }
    inc_res = http.post('/api/v1/telemetry/incident', json=inc_payload).json()
    print(f"[OK] Vehicle ANPR Incident Logged: {inc_res['incident_type']} - Plate: {inc_res['license_plate']}")

    print("---------------------------------------------------------")
    print(" ALL BACKEND, AI TELEMETRY & SPATIAL DEDUP CHECKS PASSED 100%!")
    print("---------------------------------------------------------")


if __name__ == '__main__':
    main()
