@echo off
cd /d "%~dp0"
echo =========================================================================
echo    BHARAT URBAN INTELLIGENCE PLATFORM (BEL - SIH 2026)
echo    Starting FastAPI Backend Service on http://localhost:8000
echo =========================================================================
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)
"%PYTHON_EXE%" -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
pause
