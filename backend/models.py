"""
Bharat Urban Intelligence Platform (BEL - SIH 2026)
SQLAlchemy ORM Models: RoadDefect & VehicleIncident
Problem Statement: SIH26124
"""

import os
import sys

# Ensure parent directory is in path when running directly
_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Integer, String, Float, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base, engine, SessionLocal, get_db  # type: ignore


class RoadDefect(Base):
    """
    Model representing detected road surface & infrastructure anomalies
    captured by Edge AI cameras aboard the public transport fleet.
    """
    __tablename__ = "road_defects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    defect_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # pothole, damaged_sign, missing_zebra, waterlogging
    severity: Mapped[str] = mapped_column(String(16), index=True, nullable=False)     # minor, moderate, critical
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)                  # 0.0 - 1.0
    snapshot_url: Mapped[str] = mapped_column(String(256), nullable=False)            # e.g., /static/snapshots/xyz.jpg
    status: Mapped[str] = mapped_column(String(16), default="open", index=True, nullable=False) # open, under_repair, resolved
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # Incremented via spatial deduplication
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    bus_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)       # e.g., BUS-TN-01-402

    __table_args__ = (
        Index("idx_defect_type_status", "defect_type", "status"),
        Index("idx_geo_timestamp", "latitude", "longitude", "timestamp"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the ORM instance into a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "defect_type": self.defect_type,
            "severity": self.severity,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "confidence": round(self.confidence, 4),
            "snapshot_url": self.snapshot_url,
            "status": self.status,
            "occurrence_count": self.occurrence_count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "bus_id": self.bus_id,
        }


class VehicleIncident(Base):
    """
    Model representing traffic violations, bottlenecks, and hit-and-run / ANPR alerts
    detected by the fleet's wide-angle forward AI cameras.
    """
    __tablename__ = "vehicle_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False) # rash_driving, hit_and_run, bottleneck
    license_plate: Mapped[str] = mapped_column(String(24), index=True, nullable=False) # e.g., TN-09-CB-1294
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    bus_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    __table_args__ = (
        Index("idx_incident_type_time", "incident_type", "timestamp"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the incident instance into a dictionary."""
        return {
            "id": self.id,
            "incident_type": self.incident_type,
            "license_plate": self.license_plate,
            "confidence": round(self.confidence, 4),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "bus_id": self.bus_id,
        }


__all__ = ["Base", "engine", "SessionLocal", "get_db", "RoadDefect", "VehicleIncident"]
