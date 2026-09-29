# pyright: reportMissingImports=false
"""
Spatial Deduplication Engine for Bharat Urban Intelligence Platform.
Implements the Haversine Great-Circle formula and temporal windowing
to consolidate repetitive defect detections from edge public transit fleet.
"""

import math
import uuid
import os
import sys

# Ensure parent directory is in path when running directly
_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy.orm import Session  # type: ignore

from backend.models import RoadDefect  # type: ignore

# Configurable spatial-temporal thresholds
DEDUP_DISTANCE_METERS_THRESHOLD = 50.0  # 50 meters cluster radius
DEDUP_TIME_WINDOW_HOURS = 24.0          # 24-hour aggregation window


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two GPS points on Earth in meters
    using the Haversine formula.

    :param lat1: Latitude of point 1 in decimal degrees
    :param lon1: Longitude of point 1 in decimal degrees
    :param lat2: Latitude of point 2 in decimal degrees
    :param lon2: Longitude of point 2 in decimal degrees
    :return: Distance in meters
    """
    EARTH_RADIUS_METERS = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    
    # Numerical safeguard against precision overshoot above 1.0
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c


def generate_ticket_id(defect_type: str) -> str:
    """
    Generates a unique, standardized municipal ticket ID.
    Example: BEL-2026-POT-8A3F2B
    """
    type_prefixes = {
        "pothole": "POT",
        "damaged_sign": "SGN",
        "missing_zebra": "ZBR",
        "waterlogging": "WTR",
    }
    prefix = type_prefixes.get(defect_type.lower(), "HAZ")
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"BEL-2026-{prefix}-{short_uuid}"


def process_spatial_deduplication(
    db: Session,
    bus_id: str,
    defect_type: str,
    severity: str,
    latitude: float,
    longitude: float,
    confidence: float,
    snapshot_url: str,
    timestamp: Optional[datetime] = None,
) -> Tuple[RoadDefect, bool]:
    """
    Processes incoming defect telemetry against historical records:
    1. Queries records with identical defect_type within last 24 hours.
    2. Evaluates Haversine distance against each candidate.
    3. If distance <= 15m: merges into existing record (increments occurrence_count,
       refreshes timestamp, updates moving average confidence, retains best snapshot).
    4. If no match: inserts new RoadDefect ticket.

    :return: Tuple[RoadDefect, bool] where bool is True if a new record was created,
             False if merged/deduplicated.
    """
    detection_time = timestamp or datetime.now(timezone.utc)
    time_cutoff = detection_time - timedelta(hours=DEDUP_TIME_WINDOW_HOURS)

    # Coarse database filter: same defect_type and within temporal window
    # Exclude already resolved tickets from deduplication so new defects after repairs are tracked
    candidate_defects = (
        db.query(RoadDefect)
        .filter(
            RoadDefect.defect_type == defect_type,
            RoadDefect.timestamp >= time_cutoff,
            RoadDefect.status.in_(["open", "under_repair"])
        )
        .all()
    )

    nearest_defect: Optional[RoadDefect] = None
    min_distance = float("inf")

    for candidate in candidate_defects:
        dist = haversine_distance(latitude, longitude, candidate.latitude, candidate.longitude)
        if dist <= DEDUP_DISTANCE_METERS_THRESHOLD and dist < min_distance:
            min_distance = dist
            nearest_defect = candidate

    if nearest_defect is not None:
        # Spatial match found within 15 meters! Perform deduplication merge
        old_count = nearest_defect.occurrence_count
        new_count = old_count + 1
        old_conf = float(nearest_defect.confidence)

        # Moving average recalculation: ((old_avg * old_n) + new_val) / new_n
        updated_confidence = ((old_conf * old_count) + confidence) / new_count
        nearest_defect.confidence = round(updated_confidence, 4)

        # Update occurrence count and refresh timestamp
        nearest_defect.occurrence_count = new_count
        nearest_defect.timestamp = detection_time

        # Escalate severity if repeat occurrences keep streaming in
        if new_count >= 5 and nearest_defect.severity == "minor":
            nearest_defect.severity = "moderate"
        elif new_count >= 10 and nearest_defect.severity != "critical":
            nearest_defect.severity = "critical"

        # If the new detection had higher confidence or fresh snapshot, adopt it
        if confidence > old_conf or not nearest_defect.snapshot_url:
            nearest_defect.snapshot_url = snapshot_url

        db.add(nearest_defect)
        db.commit()
        db.refresh(nearest_defect)
        return nearest_defect, False

    # No match within 15 meters -> Create new official record
    new_ticket_id = generate_ticket_id(defect_type)
    new_defect = RoadDefect(
        ticket_id=new_ticket_id,
        defect_type=defect_type,
        severity=severity,
        latitude=latitude,
        longitude=longitude,
        confidence=round(confidence, 4),
        snapshot_url=snapshot_url,
        status="open",
        occurrence_count=1,
        timestamp=detection_time,
        bus_id=bus_id,
    )

    db.add(new_defect)
    db.commit()
    db.refresh(new_defect)
    return new_defect, True
