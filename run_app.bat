@echo off
echo ============================================
echo   CarbonSphere AI - Local Setup & Run
echo ============================================

echo [1/3] Installing/Verifying Dependencies...
echo (Using simplified requirements for Windows compatibility)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some dependencies failed to install. 
    echo Attempting to proceed as the app has fallback modes...
)

echo.
echo [2/3] Starting Backend Server (FastAPI)...
echo    - API Docs: http://localhost:2020/docs
echo    - API Root: http://localhost:2020
echo.
echo NOTE: Using 'python -m uvicorn' to ensure it runs ensuring it is in PATH.
start "CarbonSphere Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 2020 --reload"

echo.
echo [3/3] Opening Frontend Dashboard...
echo    - Dashboard: http://localhost:3000
echo.
start "" "frontend\index.html"

echo ============================================
echo   System Running! 
echo   - Backend terminal is open in a new window.
echo   - Frontend should have opened in your browser.
echo ============================================
pause
