@echo off
cd /d "%~dp0"
echo =========================================================================
echo    BHARAT URBAN INTELLIGENCE PLATFORM (BEL - SIH 2026)
echo    Starting Complete Stack (Backend + Frontend)
echo =========================================================================

echo Starting FastAPI Backend in a new window...
start "BEL Urban Intelligence Backend" cmd /k "call "%~dp0start_backend.bat""

echo Starting React GIS Frontend in a new window...
start "BEL Urban Intelligence Frontend" cmd /k "call "%~dp0start_frontend.bat""

echo.
echo Both services are starting!
echo Backend API Docs: http://localhost:8000/docs
echo Frontend Dashboard: http://localhost:5173
echo.
