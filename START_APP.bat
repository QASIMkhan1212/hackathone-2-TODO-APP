@echo off
echo ================================================
echo STARTING TODO APP WITH NEON POSTGRESQL
echo ================================================
echo.

echo [1/2] Starting Backend Server...
echo (First startup may take 30 seconds - Neon database is waking up)
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak > nul

echo [2/2] Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo SERVERS STARTING...
echo ================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo IMPORTANT:
echo - Wait 30-60 seconds for backend to fully start
echo - First sign-up/sign-in will take 10-30 seconds (Neon wake-up)
echo - After first request, everything will be fast
echo.
echo Then open: http://localhost:3000 in your browser
echo.
echo Press any key to exit this window (servers will keep running)
pause > nul
