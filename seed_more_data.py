"""
Extended Database Seeder for Bharat Urban Intelligence Platform (BEL - SIH 2026)
Seeds comprehensive, multi-corridor defect and incident telemetry:
- Chennai Anna Salai (Mount Road Corridor)
- Kumbakonam Smart Transit Grid
- Bengaluru BEL Circle - Outer Ring Corridor
"""

import os
import sys
from datetime import datetime, timedelta

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.database import SessionLocal, engine, Base
from backend.models import RoadDefect, VehicleIncident

ADDITIONAL_DEFECTS = [
    # ----------------------------------------------------
    # CHENNAI WIDE NETWORK
    # ----------------------------------------------------
    {
        "ticket_id": "BEL-2026-POT-CH01",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 13.0782,
        "longitude": 80.2450, # Poonamallee
        "confidence": 0.95,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 18,
        "bus_id": "BUS-TN-01-402",
        "hours_ago": 1.5,
    },
    {
        "ticket_id": "BEL-2026-SGN-CH02",
        "defect_type": "damaged_sign",
        "severity": "moderate",
        "latitude": 13.0754,
        "longitude": 80.2210, # Poonamallee
        "confidence": 0.89,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "open",
        "occurrence_count": 6,
        "bus_id": "BUS-TN-01-408",
        "hours_ago": 3.0,
    },
    {
        "ticket_id": "BEL-2026-WTR-CH03",
        "defect_type": "waterlogging",
        "severity": "critical",
        "latitude": 13.0067,
        "longitude": 80.2030, # GST Road
        "confidence": 0.92,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "under_repair",
        "occurrence_count": 24,
        "bus_id": "BUS-TN-01-415",
        "hours_ago": 0.8,
    },
    {
        "ticket_id": "BEL-2026-ZEB-CH04",
        "defect_type": "missing_zebra",
        "severity": "minor",
        "latitude": 12.9915,
        "longitude": 80.1856, # GST Road
        "confidence": 0.86,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "open",
        "occurrence_count": 4,
        "bus_id": "BUS-TN-01-402",
        "hours_ago": 5.2,
    },
    {
        "ticket_id": "BEL-2026-POT-CH05",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 12.9880,
        "longitude": 80.2464, # OMR
        "confidence": 0.96,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 14,
        "bus_id": "BUS-TN-01-408",
        "hours_ago": 2.1,
    },
    {
        "ticket_id": "BEL-2026-SGN-CH06",
        "defect_type": "damaged_sign",
        "severity": "minor",
        "latitude": 12.9352,
        "longitude": 80.2312, # OMR
        "confidence": 0.84,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "resolved",
        "occurrence_count": 5,
        "bus_id": "BUS-TN-01-415",
        "hours_ago": 18.0,
    },
    {
        "ticket_id": "BEL-2026-POT-CH07",
        "defect_type": "pothole",
        "severity": "moderate",
        "latitude": 13.0712,
        "longitude": 80.1945, # Inner Ring Road
        "confidence": 0.91,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "under_repair",
        "occurrence_count": 11,
        "bus_id": "BUS-TN-01-422",
        "hours_ago": 4.5,
    },
    {
        "ticket_id": "BEL-2026-WTR-CH08",
        "defect_type": "waterlogging",
        "severity": "moderate",
        "latitude": 13.0450,
        "longitude": 80.2010, # Inner Ring Road
        "confidence": 0.88,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "open",
        "occurrence_count": 8,
        "bus_id": "BUS-TN-01-402",
        "hours_ago": 2.7,
    },
    {
        "ticket_id": "BEL-2026-ZEB-CH09",
        "defect_type": "missing_zebra",
        "severity": "minor",
        "latitude": 13.0827,
        "longitude": 80.2707, # Central Link
        "confidence": 0.83,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "open",
        "occurrence_count": 3,
        "bus_id": "BUS-TN-01-408",
        "hours_ago": 8.0,
    },
    {
        "ticket_id": "BEL-2026-POT-CH10",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 13.0732,
        "longitude": 80.2609, # Central Link
        "confidence": 0.97,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 29,
        "bus_id": "BUS-TN-01-415",
        "hours_ago": 0.5,
    },
    {
        "ticket_id": "BEL-2026-SGN-CH11",
        "defect_type": "damaged_sign",
        "severity": "moderate",
        "latitude": 13.0768,
        "longitude": 80.2330,
        "confidence": 0.87,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "under_repair",
        "occurrence_count": 7,
        "bus_id": "BUS-TN-01-422",
        "hours_ago": 6.2,
    },
    {
        "ticket_id": "BEL-2026-POT-CH12",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 12.9991,
        "longitude": 80.1943,
        "confidence": 0.94,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 16,
        "bus_id": "BUS-TN-01-402",
        "hours_ago": 1.2,
    },
    {
        "ticket_id": "BEL-2026-WTR-CH13",
        "defect_type": "waterlogging",
        "severity": "critical",
        "latitude": 12.9616,
        "longitude": 80.2388,
        "confidence": 0.93,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "under_repair",
        "occurrence_count": 21,
        "bus_id": "BUS-TN-01-408",
        "hours_ago": 1.8,
    },
    {
        "ticket_id": "BEL-2026-ZEB-CH14",
        "defect_type": "missing_zebra",
        "severity": "moderate",
        "latitude": 13.0581,
        "longitude": 80.1977,
        "confidence": 0.89,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "resolved",
        "occurrence_count": 5,
        "bus_id": "BUS-TN-01-415",
        "hours_ago": 12.0,
    },

    # ----------------------------------------------------
    # KUMBAKONAM SMART TRANSIT GRID
    # ----------------------------------------------------
    {
        "ticket_id": "BEL-2026-POT-KU01",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 10.9575,
        "longitude": 79.3788,
        "confidence": 0.93,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 15,
        "bus_id": "BUS-TN-68-104",
        "hours_ago": 0.9,
    },
    {
        "ticket_id": "BEL-2026-SGN-KU02",
        "defect_type": "damaged_sign",
        "severity": "moderate",
        "latitude": 10.9598,
        "longitude": 79.3825,
        "confidence": 0.88,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "under_repair",
        "occurrence_count": 9,
        "bus_id": "BUS-TN-68-112",
        "hours_ago": 2.4,
    },
    {
        "ticket_id": "BEL-2026-WTR-KU03",
        "defect_type": "waterlogging",
        "severity": "critical",
        "latitude": 10.9615,
        "longitude": 79.3855,
        "confidence": 0.95,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "open",
        "occurrence_count": 22,
        "bus_id": "BUS-TN-68-104",
        "hours_ago": 1.1,
    },
    {
        "ticket_id": "BEL-2026-ZEB-KU04",
        "defect_type": "missing_zebra",
        "severity": "minor",
        "latitude": 10.9642,
        "longitude": 79.3888,
        "confidence": 0.84,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "open",
        "occurrence_count": 3,
        "bus_id": "BUS-TN-68-112",
        "hours_ago": 7.5,
    },
    {
        "ticket_id": "BEL-2026-POT-KU05",
        "defect_type": "pothole",
        "severity": "moderate",
        "latitude": 10.9582,
        "longitude": 79.3802,
        "confidence": 0.90,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 11,
        "bus_id": "BUS-TN-68-104",
        "hours_ago": 3.8,
    },
    {
        "ticket_id": "BEL-2026-SGN-KU06",
        "defect_type": "damaged_sign",
        "severity": "minor",
        "latitude": 10.9630,
        "longitude": 79.3870,
        "confidence": 0.86,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "resolved",
        "occurrence_count": 4,
        "bus_id": "BUS-TN-68-120",
        "hours_ago": 15.0,
    },
    {
        "ticket_id": "BEL-2026-WTR-KU07",
        "defect_type": "waterlogging",
        "severity": "critical",
        "latitude": 10.9658,
        "longitude": 79.3912,
        "confidence": 0.94,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "under_repair",
        "occurrence_count": 17,
        "bus_id": "BUS-TN-68-112",
        "hours_ago": 2.0,
    },
    {
        "ticket_id": "BEL-2026-POT-KU08",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 10.9665,
        "longitude": 79.3925,
        "confidence": 0.96,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 31,
        "bus_id": "BUS-TN-68-120",
        "hours_ago": 0.4,
    },
    {
        "ticket_id": "BEL-2026-ZEB-KU09",
        "defect_type": "missing_zebra",
        "severity": "minor",
        "latitude": 10.9589,
        "longitude": 79.3812,
        "confidence": 0.82,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "open",
        "occurrence_count": 2,
        "bus_id": "BUS-TN-68-104",
        "hours_ago": 10.0,
    },
    {
        "ticket_id": "BEL-2026-POT-KU10",
        "defect_type": "pothole",
        "severity": "moderate",
        "latitude": 10.9608,
        "longitude": 79.3838,
        "confidence": 0.89,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "resolved",
        "occurrence_count": 8,
        "bus_id": "BUS-TN-68-112",
        "hours_ago": 16.0,
    },

    # ----------------------------------------------------
    # BENGALURU BEL CIRCLE - OUTER RING ROAD CORRIDOR
    # ----------------------------------------------------
    {
        "ticket_id": "BEL-2026-POT-BL01",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 13.0385,
        "longitude": 77.5495,
        "confidence": 0.97,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 34,
        "bus_id": "BUS-KA-01-BEL-1",
        "hours_ago": 0.6,
    },
    {
        "ticket_id": "BEL-2026-SGN-BL02",
        "defect_type": "damaged_sign",
        "severity": "moderate",
        "latitude": 13.0475,
        "longitude": 77.5425,
        "confidence": 0.91,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "under_repair",
        "occurrence_count": 12,
        "bus_id": "BUS-KA-01-BEL-2",
        "hours_ago": 3.5,
    },
    {
        "ticket_id": "BEL-2026-WTR-BL03",
        "defect_type": "waterlogging",
        "severity": "critical",
        "latitude": 13.0425,
        "longitude": 77.5465,
        "confidence": 0.95,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "open",
        "occurrence_count": 26,
        "bus_id": "BUS-KA-01-BEL-1",
        "hours_ago": 1.4,
    },
    {
        "ticket_id": "BEL-2026-ZEB-BL04",
        "defect_type": "missing_zebra",
        "severity": "minor",
        "latitude": 13.0325,
        "longitude": 77.5525,
        "confidence": 0.87,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "open",
        "occurrence_count": 5,
        "bus_id": "BUS-KA-01-BEL-3",
        "hours_ago": 6.8,
    },
    {
        "ticket_id": "BEL-2026-POT-BL05",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 13.0255,
        "longitude": 77.5575,
        "confidence": 0.96,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "under_repair",
        "occurrence_count": 21,
        "bus_id": "BUS-KA-01-BEL-2",
        "hours_ago": 2.2,
    },
    {
        "ticket_id": "BEL-2026-SGN-BL06",
        "defect_type": "damaged_sign",
        "severity": "minor",
        "latitude": 13.0440,
        "longitude": 77.5450,
        "confidence": 0.85,
        "snapshot_url": "/static/snapshots/sample_damaged_sign.jpg",
        "status": "resolved",
        "occurrence_count": 4,
        "bus_id": "BUS-KA-01-BEL-1",
        "hours_ago": 14.0,
    },
    {
        "ticket_id": "BEL-2026-POT-BL07",
        "defect_type": "pothole",
        "severity": "moderate",
        "latitude": 13.0350,
        "longitude": 77.5510,
        "confidence": 0.89,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 14,
        "bus_id": "BUS-KA-01-BEL-3",
        "hours_ago": 4.1,
    },
    {
        "ticket_id": "BEL-2026-WTR-BL08",
        "defect_type": "waterlogging",
        "severity": "moderate",
        "latitude": 13.0460,
        "longitude": 77.5435,
        "confidence": 0.88,
        "snapshot_url": "/static/snapshots/sample_waterlogging.jpg",
        "status": "open",
        "occurrence_count": 9,
        "bus_id": "BUS-KA-01-BEL-2",
        "hours_ago": 3.1,
    },
    {
        "ticket_id": "BEL-2026-ZEB-BL09",
        "defect_type": "missing_zebra",
        "severity": "moderate",
        "latitude": 13.0305,
        "longitude": 77.5545,
        "confidence": 0.90,
        "snapshot_url": "/static/snapshots/sample_missing_zebra.jpg",
        "status": "under_repair",
        "occurrence_count": 7,
        "bus_id": "BUS-KA-01-BEL-1",
        "hours_ago": 5.0,
    },
    {
        "ticket_id": "BEL-2026-POT-BL10",
        "defect_type": "pothole",
        "severity": "critical",
        "latitude": 13.0230,
        "longitude": 77.5600,
        "confidence": 0.94,
        "snapshot_url": "/static/snapshots/sample_pothole.jpg",
        "status": "open",
        "occurrence_count": 19,
        "bus_id": "BUS-KA-01-BEL-2",
        "hours_ago": 1.7,
    },
]

ADDITIONAL_INCIDENTS = [
    # Chennai Incidents
    {
        "incident_type": "rash_driving",
        "license_plate": "TN-02-AZ-9988",
        "confidence": 0.94,
        "latitude": 13.0815,
        "longitude": 80.2745,
        "bus_id": "BUS-TN-01-402",
        "hours_ago": 0.5,
    },
    {
        "incident_type": "bottleneck",
        "license_plate": "TN-01-BV-1122",
        "confidence": 0.91,
        "latitude": 13.0515,
        "longitude": 80.2420,
        "bus_id": "BUS-TN-01-408",
        "hours_ago": 1.2,
    },
    {
        "incident_type": "hit_and_run",
        "license_plate": "TN-09-CK-3344",
        "confidence": 0.96,
        "latitude": 13.0235,
        "longitude": 80.2160,
        "bus_id": "BUS-TN-01-415",
        "hours_ago": 2.3,
    },
    {
        "incident_type": "red_light_jump",
        "license_plate": "TN-07-DM-5566",
        "confidence": 0.93,
        "latitude": 13.0320,
        "longitude": 80.2205,
        "bus_id": "BUS-TN-01-422",
        "hours_ago": 3.4,
    },
    {
        "incident_type": "illegal_parking",
        "license_plate": "TN-01-EQ-7788",
        "confidence": 0.89,
        "latitude": 13.0640,
        "longitude": 80.2555,
        "bus_id": "BUS-TN-01-402",
        "hours_ago": 4.1,
    },
    {
        "incident_type": "rash_driving",
        "license_plate": "TN-10-EE-9900",
        "confidence": 0.93,
        "latitude": 13.0075,
        "longitude": 80.2025,
        "bus_id": "BUS-TN-01-415",
        "hours_ago": 0.8,
    },
    # Kumbakonam Incidents
    {
        "incident_type": "rash_driving",
        "license_plate": "TN-68-BA-1234",
        "confidence": 0.92,
        "latitude": 10.9601,
        "longitude": 79.3828,
        "bus_id": "BUS-TN-68-104",
        "hours_ago": 1.0,
    },
    {
        "incident_type": "bottleneck",
        "license_plate": "TN-68-CC-5678",
        "confidence": 0.95,
        "latitude": 10.9578,
        "longitude": 79.3792,
        "bus_id": "BUS-TN-68-112",
        "hours_ago": 1.9,
    },
    {
        "incident_type": "hit_and_run",
        "license_plate": "TN-68-DD-9012",
        "confidence": 0.97,
        "latitude": 10.9620,
        "longitude": 79.3860,
        "bus_id": "BUS-TN-68-120",
        "hours_ago": 2.7,
    },
    {
        "incident_type": "illegal_parking",
        "license_plate": "TN-68-EE-3456",
        "confidence": 0.88,
        "latitude": 10.9645,
        "longitude": 79.3892,
        "bus_id": "BUS-TN-68-104",
        "hours_ago": 4.5,
    },
    # Bengaluru Incidents
    {
        "incident_type": "rash_driving",
        "license_plate": "KA-04-MB-4545",
        "confidence": 0.96,
        "latitude": 13.0388,
        "longitude": 77.5498,
        "bus_id": "BUS-KA-01-BEL-1",
        "hours_ago": 0.4,
    },
    {
        "incident_type": "bottleneck",
        "license_plate": "KA-03-NJ-7878",
        "confidence": 0.90,
        "latitude": 13.0478,
        "longitude": 77.5428,
        "bus_id": "BUS-KA-01-BEL-2",
        "hours_ago": 1.6,
    },
    {
        "incident_type": "illegal_parking",
        "license_plate": "KA-01-PL-1212",
        "confidence": 0.88,
        "latitude": 13.0430,
        "longitude": 77.5470,
        "bus_id": "BUS-KA-01-BEL-1",
        "hours_ago": 2.5,
    },
    {
        "incident_type": "red_light_jump",
        "license_plate": "KA-51-QK-3434",
        "confidence": 0.94,
        "latitude": 13.0330,
        "longitude": 77.5530,
        "bus_id": "BUS-KA-01-BEL-3",
        "hours_ago": 3.1,
    },
    {
        "incident_type": "hit_and_run",
        "license_plate": "KA-02-RX-5656",
        "confidence": 0.98,
        "latitude": 13.0260,
        "longitude": 77.5580,
        "bus_id": "BUS-KA-01-BEL-2",
        "hours_ago": 0.7,
    },
]


def seed_database():
    now = datetime.utcnow()
    db = SessionLocal()
    added_defects = 0
    added_incidents = 0

    try:
        for item in ADDITIONAL_DEFECTS:
            exists = db.query(RoadDefect).filter(RoadDefect.ticket_id == item["ticket_id"]).first()
            if not exists:
                hours = item.pop("hours_ago", 1.0)
                item_time = now - timedelta(hours=hours)
                defect = RoadDefect(**item, timestamp=item_time)
                db.add(defect)
                added_defects += 1
            else:
                item.pop("hours_ago", None)

        for inc in ADDITIONAL_INCIDENTS:
            exists_inc = db.query(VehicleIncident).filter(
                VehicleIncident.license_plate == inc["license_plate"],
                VehicleIncident.incident_type == inc["incident_type"]
            ).first()
            if not exists_inc:
                hours = inc.pop("hours_ago", 1.0)
                inc_time = now - timedelta(hours=hours)
                incident = VehicleIncident(**inc, timestamp=inc_time)
                db.add(incident)
                added_incidents += 1
            else:
                inc.pop("hours_ago", None)

        db.commit()

        total_defects = db.query(RoadDefect).count()
        total_incidents = db.query(VehicleIncident).count()
        print(f"[SUCCESS] Added {added_defects} new road defects and {added_incidents} new vehicle incidents.")
        print(f"[SUMMARY] Total in DB now: {total_defects} Defects, {total_incidents} Incidents.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
