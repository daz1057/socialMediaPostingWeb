@echo off
setlocal enabledelayedexpansion

:: Quick Start Script for Social Media Posting Web App
:: Run this script to start all services with Docker Compose

echo.
echo ============================================================
echo    Starting Social Media Posting Web Application
echo ============================================================
echo.

:: Change to project directory
cd /d "C:\Users\daz10_wz66zyw\PycharmProjects\SocialMediaPosting-Web"

:: Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

:: Check if .env files exist
echo [1/4] Checking environment files...

if not exist "backend\.env" (
    echo       - backend\.env not found. Copying from root .env...
    copy ".env" "backend\.env" >nul
)

if not exist "frontend\.env" (
    if exist "frontend\.env.example" (
        echo       - frontend\.env not found. Copying from .env.example...
        copy "frontend\.env.example" "frontend\.env" >nul
    )
)
echo       - Environment files OK

:: Stop any existing containers
echo.
echo [2/4] Stopping any existing containers...
docker compose down >nul 2>&1

:: Start Docker containers
echo.
echo [3/4] Starting Docker containers...
docker compose up -d --build

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start Docker containers.
    echo        Run 'docker compose logs' to see errors.
    pause
    exit /b 1
)

:: Wait for services to be ready
echo.
echo [4/4] Waiting for services to be ready...
echo       Waiting 15 seconds for database and services to initialize...

:: Countdown timer
for /l %%i in (15,-1,1) do (
    <nul set /p "=       %%i seconds remaining...  "
    timeout /t 1 /nobreak >nul
    echo.
)

:: Check service status
echo.
echo ============================================================
echo    Service Status
echo ============================================================
docker compose ps

:: Check health endpoint
echo.
echo Checking backend health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend may still be starting up. Wait a moment and refresh.
) else (
    echo [OK] Backend is responding!
)

echo.
echo ============================================================
echo    Application URLs
echo ============================================================
echo.
echo    Frontend:    http://localhost:3000
echo    Backend:     http://localhost:8000
echo    API Docs:    http://localhost:8000/docs
echo    Health:      http://localhost:8000/health
echo.
echo ============================================================
echo    Quick Commands
echo ============================================================
echo.
echo    View logs:           docker compose logs -f
echo    View backend logs:   docker compose logs -f backend
echo    Stop application:    docker compose down
echo    Restart:             docker compose restart
echo    Run migrations:      docker compose exec backend alembic upgrade head
echo.
echo ============================================================

:: Ask if user wants to open browser
echo.
set /p openBrowser="Open API docs in browser? (Y/N): "
if /i "%openBrowser%"=="Y" (
    start http://localhost:8000/docs
)

echo.
echo Application is running! Press any key to exit this window...
echo (Services will continue running in background)
pause >nul
