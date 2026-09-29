"""
Bharat Urban Intelligence Platform (BEL - SIH 2026)
Pydantic Schemas with Strict Typing & Validation
Problem Statement: SIH26124
"""

from datetime import datetime, timezone
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


def get_utc_now() -> datetime:
    """Helper to return current UTC timestamp."""
    return datetime.now(timezone.utc)


class DefectCreate(BaseModel):
    """Schema for directly creating a new RoadDefect record via REST API."""
    ticket_id: Optional[str] = Field(default=None, description="Optional unique ticket ID; generated automatically if omitted")
    defect_type: str = Field(description="pothole, damaged_sign, missing_zebra, waterlogging", examples=["pothole"])
    severity: str = Field(description="minor, moderate, critical", examples=["critical"])
    latitude: float = Field(ge=-90.0, le=90.0, examples=[13.0604])
    longitude: float = Field(ge=-180.0, le=180.0, examples=[80.2496])
    confidence: float = Field(ge=0.0, le=1.0, examples=[0.92])
    snapshot_url: Optional[str] = Field(default=None, examples=["/static/snapshots/sample_pothole.jpg"])
    status: Optional[str] = Field(default="open", description="open, under_repair, resolved", examples=["open"])
    occurrence_count: Optional[int] = Field(default=1, ge=1, examples=[1])
    timestamp: Optional[datetime] = Field(default_factory=get_utc_now)
    bus_id: str = Field(description="Identifier of the reporting bus unit", examples=["BUS-TN-01-402"])


class DefectTelemetryCreate(BaseModel):
    """Payload sent by Edge Bus AI camera upon real-time road hazard detection."""
    bus_id: str = Field(description="Identifier of the edge vehicle", examples=["BUS-TN-01-402"])
    defect_type: str = Field(description="pothole, damaged_sign, missing_zebra, waterlogging", examples=["pothole"])
    severity: str = Field(description="minor, moderate, critical", examples=["critical"])
    latitude: float = Field(ge=-90.0, le=90.0, examples=[13.0604])
    longitude: float = Field(ge=-180.0, le=180.0, examples=[80.2496])
    confidence: float = Field(ge=0.0, le=1.0, examples=[0.88])
    snapshot_base64: Optional[str] = Field(default=None, description="Base64 encoded cropped JPEG defect evidence")
    timestamp: Optional[datetime] = Field(default_factory=get_utc_now)


class DefectResponse(BaseModel):
    """Standardized response schema for a RoadDefect entity."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: str
    defect_type: str
    severity: str
    latitude: float
    longitude: float
    confidence: float
    snapshot_url: str
    status: str
    occurrence_count: int
    timestamp: datetime
    bus_id: str


class DefectStatusUpdate(BaseModel):
    """Schema for updating ticket lifecycle status."""
    status: str = Field(description="open, under_repair, resolved", examples=["under_repair"])
    notes: Optional[str] = Field(default=None, description="Optional municipal resolution notes")


class IncidentTelemetryCreate(BaseModel):
    """Payload for logging vehicle violations and traffic incidents."""
    incident_type: str = Field(description="rash_driving, hit_and_run, bottleneck", examples=["rash_driving"])
    license_plate: str = Field(examples=["TN-09-CB-1294"])
    confidence: float = Field(ge=0.0, le=1.0, examples=[0.92])
    latitude: float = Field(ge=-90.0, le=90.0, examples=[13.0604])
    longitude: float = Field(ge=-180.0, le=180.0, examples=[80.2496])
    bus_id: str = Field(examples=["BUS-TN-01-402"])
    timestamp: Optional[datetime] = Field(default_factory=get_utc_now)


class IncidentResponse(BaseModel):
    """Standardized response schema for a VehicleIncident entity."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_type: str
    license_plate: str
    confidence: float
    latitude: float
    longitude: float
    timestamp: datetime
    bus_id: str


class AnalyticsSummaryResponse(BaseModel):
    """Executive summary metrics for BEL Command Center KPI cards."""
    total_defects: int
    open_tickets: int
    critical_hazards: int
    resolved_count: int
    under_repair_count: int
    total_occurrences_absorbed: int
    deduplication_ratio_pct: float
    active_fleet_count: int
    type_breakdown: Dict[str, int]
    severity_breakdown: Dict[str, int]
    last_telemetry_time: Optional[datetime] = None
