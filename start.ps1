# Quick Start Script for Social Media Posting Web App

Write-Host "`n=== Starting Social Media Posting Web Application ===" -ForegroundColor Cyan

# Change to project directory
Set-Location "C:\Users\daz10_wz66zyw\PycharmProjects\SocialMediaPosting-Web"

# Check if .env files exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  backend\.env not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env" "backend\.env"
}

if (-not (Test-Path "frontend\.env")) {
    Write-Host "⚠️  frontend\.env not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "frontend\.env.example" "frontend\.env"
}

# Start Docker containers
Write-Host "`n[1/3] Starting Docker containers..." -ForegroundColor Yellow
docker compose up -d

# Wait for services to be ready
Write-Host "`n[2/3] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "`n[3/3] Checking service status..." -ForegroundColor Yellow
docker compose ps

Write-Host "`n=== Services Started ===" -ForegroundColor Cyan
Write-Host "Frontend:  http://localhost:3000" -ForegroundColor Green
Write-Host "Backend:   http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health:    http://localhost:8000/health" -ForegroundColor Green

Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run .\test-backend.ps1 to test the backend" -ForegroundColor Gray
Write-Host "  2. Open http://localhost:8000/docs to explore the API" -ForegroundColor Gray
Write-Host "  3. Run 'docker compose logs -f' to view logs" -ForegroundColor Gray

Write-Host "`n💡 To stop: docker compose down" -ForegroundColor Cyan
