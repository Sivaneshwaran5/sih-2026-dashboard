"""
Bharat Urban Intelligence Platform (BEL - SIH 2026)
Backend Application Entry Point: FastAPI + SQLite + SQLAlchemy
Problem Statement: SIH26124
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2

import sys
BASE_DIR_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR_ROOT not in sys.path:
    sys.path.insert(0, BASE_DIR_ROOT)

from backend.database import engine, Base, SessionLocal
from backend.models import RoadDefect, VehicleIncident
from backend.routes import router as api_router, seed_demo_data

# Ensure static directories exist for storing snapshot evidence
ROOT_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR: str = os.path.join(ROOT_DIR, "static")
SNAPSHOTS_DIR: str = os.path.join(STATIC_DIR, "snapshots")
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)


def generate_sample_evidence_assets() -> None:
    """
    Synthesizes realistic evidence snapshots for seed defect tickets
    (pothole, damaged sign, waterlogging, missing zebra) if not already present.
    """
    asset_configs = {
        "sample_pothole.jpg": {
            "title": "CRITICAL POTHOLE - 45cm",
            "base_color": (50, 52, 54),
            "defect_color": (25, 26, 28),
            "border_color": (0, 0, 220),
            "type": "pothole",
        },
        "sample_damaged_sign.jpg": {
            "title": "DAMAGED TRAFFIC REGULATION SIGN",
            "base_color": (120, 110, 90),
            "defect_color": (30, 90, 220),
            "border_color": (0, 165, 255),
            "type": "sign",
        },
        "sample_waterlogging.jpg": {
            "title": "SURFACE WATERLOGGING - DEPTH > 15CM",
            "base_color": (60, 65, 70),
            "defect_color": (140, 100, 40),
            "border_color": (255, 140, 0),
            "type": "water",
        },
        "sample_missing_zebra.jpg": {
            "title": "FADED PEDESTRIAN ZEBRA CROSSING",
            "base_color": (45, 47, 50),
            "defect_color": (160, 160, 160),
            "border_color": (0, 215, 255),
            "type": "zebra",
        },
    }

    for filename, config in asset_configs.items():
        file_path = os.path.join(SNAPSHOTS_DIR, filename)
        if not os.path.exists(file_path):
            img = np.zeros((360, 640, 3), dtype=np.uint8)
            img[:] = config["base_color"]
            noise = np.random.randint(-15, 15, (360, 640, 3), dtype=np.int16)
            img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

            if config["type"] == "pothole":
                cv2.ellipse(img, (320, 200), (140, 75), 15, 0, 360, config["defect_color"], -1)
                cv2.ellipse(img, (315, 195), (120, 60), 15, 0, 360, (15, 15, 18), -1)
                cv2.rectangle(img, (160, 110), (480, 280), config["border_color"], 3)
            elif config["type"] == "sign":
                cv2.rectangle(img, (290, 70), (350, 130), config["defect_color"], -1)
                cv2.line(img, (320, 130), (320, 300), (200, 200, 200), 8)
                cv2.rectangle(img, (270, 50), (370, 310), config["border_color"], 3)
            elif config["type"] == "water":
                cv2.ellipse(img, (320, 210), (220, 90), 0, 0, 360, config["defect_color"], -1)
                cv2.rectangle(img, (90, 110), (550, 300), config["border_color"], 3)
            elif config["type"] == "zebra":
                for x in range(120, 520, 70):
                    cv2.rectangle(img, (x, 150), (x + 35, 270), config["defect_color"], -1)
                cv2.rectangle(img, (100, 130), (540, 290), config["border_color"], 3)

            # Overlay tactical HUD banner
            cv2.rectangle(img, (0, 0), (640, 42), (20, 24, 30), -1)
            cv2.putText(
                img, f"BEL EDGE AI // EVIDENCE CAPTURE: {config['title']}",
                (14, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 230, 255), 1, cv2.LINE_AA
            )
            cv2.putText(
                img, "CAM-FRONT-HD // GPS: 13.0604 N, 80.2496 E // CONF: 92.4%",
                (14, 345), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 220, 255), 1, cv2.LINE_AA
            )

            cv2.imwrite(file_path, img)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifecycle manager for application startup and clean teardown.
    Automatically initializes SQLite schemas on startup via Base.metadata.create_all(bind=engine)
    and bootstraps realistic demo records without requiring manual database migration scripts.
    """
    # 1. Automatically create all SQLite tables on startup
    Base.metadata.create_all(bind=engine)
    print("[Startup] SQLite database schemas verified and synchronized.")

    # 2. Synthesize baseline evidence snapshots if missing
    generate_sample_evidence_assets()

    # 3. Seed demo dataset if database is newly initialized
    db = SessionLocal()
    try:
        defect_count = db.query(RoadDefect).count()
        if defect_count == 0:
            print("[Startup] Seeding database with initial SIH 2026 Chennai Transit Corridor data...")
            seed_demo_data(db)
    finally:
        db.close()

    yield
    print("[Shutdown] Bharat Urban Intelligence Platform backend terminated gracefully.")


# Initialize FastAPI instance with rich metadata
app: FastAPI = FastAPI(
    title="BHARAT URBAN INTELLIGENCE PLATFORM (BEL - SIH 2026)",
    description=(
        "Production-grade Mobile Urban Intelligence Platform using Public Transport Fleet "
        "for automated road hazard detection, spatial deduplication, and municipal maintenance dispatch."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-Origin Resource Sharing (CORS) for React GIS Command Center Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount snapshots directory for image serving
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include Urban Intelligence API Router
app.include_router(api_router)


@app.get("/api/health", tags=["Health"])
def health_check() -> dict:
    """Health check endpoint for connection monitors, dashboards, and load balancers."""
    return {
        "status": "online",
        "service": "Bharat Urban Intelligence Platform API",
        "organization": "Bharat Electronics Limited (BEL)",
        "competition": "Smart India Hackathon 2026",
        "problem_statement": "SIH26124"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
