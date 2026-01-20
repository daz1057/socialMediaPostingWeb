# Social Media Posting Web Application

AI-powered social media content creation platform built with FastAPI and React.

## Tech Stack

### Backend
- **FastAPI 0.110+** - Modern async Python web framework
- **PostgreSQL 16** - Relational database
- **Redis 7+** - Caching and task queue
- **SQLAlchemy 2.0** - Async ORM
- **Celery 5.3+** - Background tasks
- **Pydantic 2.x** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript 5+** - Type safety
- **Vite 5+** - Build tool
- **Ant Design 5+** - UI component library
- **Tailwind CSS 3+** - Utility-first CSS
- **Zustand** - State management
- **TanStack Query** - Server state management
- **React Router 6+** - Routing

## Project Structure

```
SocialMediaPosting-Web/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/       # API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── providers/    # AI provider integrations
│   │   └── main.py       # FastAPI app entry
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── store/        # Zustand stores
│   │   └── types/        # TypeScript types
│   └── package.json      # Node dependencies
│
└── docker-compose.yml    # Docker orchestration
```

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- (Optional) Node.js 20+ and Python 3.11+ for local development

### Quick Start (Automated)

**Windows PowerShell:**
```powershell
# Start all services
.\start.ps1

# Run backend tests
.\test-backend.ps1
```

### Manual Setup

1. **Clone the repository** (or navigate to project directory)
   ```bash
   cd SocialMediaPosting-Web
   ```

2. **Verify environment files exist**
   - `backend\.env` (or copy from `.env`)
   - `frontend\.env` (or copy from `frontend\.env.example`)

3. **Start all services**
   ```bash
   docker compose up -d
   ```

4. **Initialize database** (first time only)
   ```bash
   # Create migration
   docker compose exec backend alembic revision --autogenerate -m "Initial migration"

   # Apply migration
   docker compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000 (React dev server)
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

## Phase 1 Implementation Status

✅ **Backend (Completed)**
- FastAPI project structure with async SQLAlchemy
- JWT authentication (login, refresh, logout)
- User model with password hashing
- Tag model for categorization
- Prompt model with customer persona injection
- Pydantic schemas for validation
- Prompt CRUD endpoints with filtering
- Alembic migration setup

⏳ **Frontend (Pending)**
- React + TypeScript + Vite setup
- Authentication flow (login, protected routes)
- AppLayout with sidebar navigation
- PromptsPage with CRUD operations

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing instructions and [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for database migration steps.

Quick test:
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Development

### Backend Development

**Run backend locally (without Docker):**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Create a database migration:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

**Run tests:**
```bash
cd backend
pytest
```

### Frontend Development

**Run frontend locally (without Docker):**
```bash
cd frontend
npm install
npm run dev
```

**Build for production:**
```bash
cd frontend
npm run build
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Available Services

### PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **Database**: social_media_app
- **User**: appuser
- **Password**: password (change in production!)

### Redis
- **Host**: localhost
- **Port**: 6379

### Backend API
- **Host**: localhost
- **Port**: 8000
- **Base URL**: http://localhost:8000/api/v1

### Frontend
- **Host**: localhost
- **Port**: 3000

## Environment Variables

### Backend (.env)
See `backend/.env.example` for all available options:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `AWS_ACCESS_KEY_ID` - AWS credentials for S3
- `ENCRYPTION_KEY` - Fernet key for credential encryption

### Frontend (.env)
- `VITE_API_URL` - Backend API base URL

## Next Steps

After the foundation is running, follow the migration plan:

1. **Phase 1 Week 1**: Add User model and authentication
2. **Phase 1 Week 2**: Add Prompts model and CRUD endpoints
3. **Phase 2**: Copy AI provider abstraction layer
4. **Phase 3**: Implement post curation
5. **Continue with remaining phases...**

See the migration plan at:
`SocialMediaPosting-4o-4o-Mini-WithAutomation/.claude/plans/composed-imagining-wreath.md`

## Troubleshooting

### Backend won't start
- Check database is running: `docker-compose ps postgres`
- View logs: `docker-compose logs backend`
- Verify environment variables in `.env`

### Frontend won't start
- Check node_modules: `docker-compose exec frontend npm install`
- View logs: `docker-compose logs frontend`
- Clear cache: `docker-compose down -v`

### Database connection issues
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Check connection string in `.env`
- Recreate database: `docker-compose down -v && docker-compose up`

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database data)
docker-compose down -v
```

## License

Private project - All rights reserved

## Support

For issues or questions, refer to the migration plan documentation.
