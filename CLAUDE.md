# Claude Code Instructions for SocialMediaPosting-Web

## Project Overview
Full-stack social media posting application migrated from tkinter desktop to web.
- **Backend:** FastAPI + PostgreSQL + SQLAlchemy
- **Frontend:** React + TypeScript + Ant Design
- **Repository:** https://github.com/daz1057/socialMediaPostingWeb

## Git Workflow

### Committing Changes
When asked to commit changes:

1. Check status first:
   ```bash
   git status
   ```

2. Stage relevant files (exclude sensitive files):
   ```bash
   git add backend/ frontend/ docker-compose.yml
   ```

3. Create descriptive commit:
   ```bash
   git commit -m "Brief description of changes

   - Detail 1
   - Detail 2

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

4. Push to GitHub:
   ```bash
   git push origin main
   ```

### Files to NEVER Commit
- `.env` (contains secrets)
- `credentials.json` / `credentials_Backup.json`
- `__pycache__/`
- `node_modules/`
- `*.log`
- `.venv/` / `venv/`
- Any file containing API keys or passwords

### Files Safe to Commit
- `.env.example` (template without real values)
- All source code in `backend/app/`
- All source code in `frontend/src/`
- `docker-compose.yml`
- `requirements.txt` / `package.json`
- Alembic migrations in `backend/alembic/versions/`
- Documentation files (*.md)

## Project Structure

```
SocialMediaPosting-Web/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── providers/       # AI provider integrations
│   │   └── utils/           # Utilities (auth, encryption)
│   ├── alembic/versions/    # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── hooks/           # React Query hooks
│   │   ├── pages/           # Page components
│   │   ├── store/           # Zustand stores
│   │   └── types/           # TypeScript types
│   └── package.json
└── docker-compose.yml
```

## Development Commands

### Start with Docker (recommended)
```bash
cd C:\Users\daz10_wz66zyw\PycharmProjects\SocialMediaPosting-Web
docker-compose up -d
```

### Start Frontend Separately
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
After adding new models or changing existing ones:
```bash
# Create migration (inside Docker or with venv activated)
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Adding New Features

### Backend (new endpoint)
1. Create/update model in `backend/app/models/`
2. Create/update schema in `backend/app/schemas/`
3. Create/update service in `backend/app/services/`
4. Create/update API endpoint in `backend/app/api/v1/`
5. Register router in `backend/app/api/v1/router.py`
6. Create migration if needed
7. Update `__init__.py` exports

### Frontend (new page)
1. Add types to `frontend/src/types/index.ts`
2. Create hook in `frontend/src/hooks/`
3. Export hook from `frontend/src/hooks/index.ts`
4. Create page components in `frontend/src/pages/`
5. Add routes in `frontend/src/App.tsx`
6. Add navigation in `frontend/src/components/Sidebar.tsx`

## Commit Message Style
- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars max)
- Blank line, then bullet points for details
- Always include Co-Authored-By line
