@echo off

:: Stop Script for Social Media Posting Web App

echo.
echo ============================================================
echo    Stopping Social Media Posting Web Application
echo ============================================================
echo.

cd /d "C:\Users\daz10_wz66zyw\PycharmProjects\SocialMediaPosting-Web"

echo Stopping all containers...
docker compose down

echo.
echo ============================================================
echo    All services stopped!
echo ============================================================
echo.
echo    To start again, run: start.bat
echo.

pause
