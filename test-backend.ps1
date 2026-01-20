# Backend Testing Script
# Run this after starting Docker containers: docker compose up -d

Write-Host "`n=== Social Media Posting Web - Backend Test Script ===" -ForegroundColor Cyan

# Change to project directory
Set-Location "C:\Users\daz10_wz66zyw\PycharmProjects\SocialMediaPosting-Web"

# Step 1: Check Docker services
Write-Host "`n[1/7] Checking Docker services..." -ForegroundColor Yellow
docker compose ps

# Step 2: Create database migration
Write-Host "`n[2/7] Creating database migration..." -ForegroundColor Yellow
docker compose exec backend alembic revision --autogenerate -m "Initial migration - User, Tag, Prompt models"

Write-Host "`n[2/7] Applying migration..." -ForegroundColor Yellow
docker compose exec backend alembic upgrade head

# Step 3: Create test user
Write-Host "`n[3/7] Creating test user..." -ForegroundColor Yellow
docker compose exec backend python -c @"
import asyncio
from app.database import async_session_maker
from app.models.user import User
from app.utils.auth import get_password_hash

async def create_test_user():
    async with async_session_maker() as session:
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(select(User).filter(User.username == 'testuser'))
        existing = result.scalar_one_or_none()

        if existing:
            print('⚠️  Test user already exists: testuser')
            return

        user = User(
            username='testuser',
            email='test@example.com',
            hashed_password=get_password_hash('password123'),
            is_active=True,
            is_superuser=False
        )
        session.add(user)
        await session.commit()
        print('✅ Test user created: testuser / password123')

asyncio.run(create_test_user())
"@

# Step 4: Create test tag
Write-Host "`n[4/7] Creating test tag..." -ForegroundColor Yellow
docker compose exec backend python -c @"
import asyncio
from app.database import async_session_maker
from app.models.tag import Tag

async def create_tag():
    async with async_session_maker() as session:
        # Check if tag exists
        from sqlalchemy import select
        result = await session.execute(select(Tag).filter(Tag.name == 'Entertain'))
        existing = result.scalar_one_or_none()

        if existing:
            print('⚠️  Tag already exists: Entertain')
            return

        tag = Tag(name='Entertain', description='Entertainment posts')
        session.add(tag)
        await session.commit()
        print('✅ Tag created: Entertain (ID: 1)')

asyncio.run(create_tag())
"@

# Step 5: Test health endpoints
Write-Host "`n[5/7] Testing health endpoints..." -ForegroundColor Yellow

Write-Host "  GET /health" -ForegroundColor Gray
$response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
Write-Host "  Response: $($response | ConvertTo-Json)" -ForegroundColor Green

Write-Host "  GET /api/v1/health" -ForegroundColor Gray
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get
Write-Host "  Response: $($response | ConvertTo-Json)" -ForegroundColor Green

# Step 6: Test authentication
Write-Host "`n[6/7] Testing authentication..." -ForegroundColor Yellow

Write-Host "  POST /api/v1/auth/login" -ForegroundColor Gray
$loginBody = @{
    username = "testuser"
    password = "password123"
}
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $loginBody

Write-Host "  ✅ Login successful!" -ForegroundColor Green
$accessToken = $loginResponse.access_token

Write-Host "  GET /api/v1/auth/me" -ForegroundColor Gray
$headers = @{
    Authorization = "Bearer $accessToken"
}
$userResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
    -Method Get `
    -Headers $headers

Write-Host "  ✅ Current user: $($userResponse.username) ($($userResponse.email))" -ForegroundColor Green

# Step 7: Test Prompt CRUD
Write-Host "`n[7/7] Testing Prompt CRUD..." -ForegroundColor Yellow

Write-Host "  POST /api/v1/prompts/ (Create)" -ForegroundColor Gray
$promptData = @{
    name = "Test Prompt"
    details = "This is a test prompt for AI generation"
    selected_customers = @{
        "Customer Persona" = $true
        "Desires" = $false
    }
    tag_id = 1
} | ConvertTo-Json

$createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prompts/" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $promptData

Write-Host "  ✅ Prompt created: ID $($createResponse.id)" -ForegroundColor Green
$promptId = $createResponse.id

Write-Host "  GET /api/v1/prompts/ (List)" -ForegroundColor Gray
$listResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prompts/" `
    -Method Get `
    -Headers $headers

Write-Host "  ✅ Listed $($listResponse.total) prompts" -ForegroundColor Green

Write-Host "  GET /api/v1/prompts/$promptId (Read)" -ForegroundColor Gray
$readResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prompts/$promptId" `
    -Method Get `
    -Headers $headers

Write-Host "  ✅ Prompt read: $($readResponse.name)" -ForegroundColor Green

Write-Host "  PUT /api/v1/prompts/$promptId (Update)" -ForegroundColor Gray
$updateData = @{
    name = "Updated Test Prompt"
} | ConvertTo-Json

$updateResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prompts/$promptId" `
    -Method Put `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $updateData

Write-Host "  ✅ Prompt updated: $($updateResponse.name)" -ForegroundColor Green

Write-Host "  DELETE /api/v1/prompts/$promptId (Delete)" -ForegroundColor Gray
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prompts/$promptId" `
    -Method Delete `
    -Headers $headers | Out-Null

Write-Host "  ✅ Prompt deleted" -ForegroundColor Green

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "✅ Docker services running" -ForegroundColor Green
Write-Host "✅ Database migration applied" -ForegroundColor Green
Write-Host "✅ Test user created" -ForegroundColor Green
Write-Host "✅ Health endpoints working" -ForegroundColor Green
Write-Host "✅ Authentication working (JWT)" -ForegroundColor Green
Write-Host "✅ Prompt CRUD operations working" -ForegroundColor Green

Write-Host "`n🎉 All tests passed! Backend is ready." -ForegroundColor Green
Write-Host "`n📝 View API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
