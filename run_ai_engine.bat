@echo off
cd /d "%~dp0"
echo =========================================================================
echo    BHARAT URBAN INTELLIGENCE PLATFORM (BEL - SIH 2026)
echo    Starting AI Edge Detection Engine (YOLOv8 + GPS Telemetry Stream)
echo =========================================================================
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)
"%PYTHON_EXE%" ai_engine/video_detector.py --source synthetic
pause
