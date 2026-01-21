# SocialMediaPosting-Web - Complete Feature Documentation

## Project Overview

A full-stack web application for managing and generating social media content using AI. This project is a migration from a Python tkinter desktop application to a modern web-based architecture.

**Repository:** https://github.com/daz1057/socialMediaPostingWeb

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (async)
- **Migrations:** Alembic
- **Authentication:** JWT (access + refresh tokens)
- **Encryption:** Fernet (for API credentials)
- **File Storage:** AWS S3

### Frontend
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** Ant Design
- **State Management:** Zustand (auth), React Query (server state)
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Database:** PostgreSQL 15 (Docker container)

---

## Implemented Features

### 1. Authentication & User Management
- [x] User registration with email/username/password
- [x] JWT-based login (access token + refresh token)
- [x] Token refresh mechanism
- [x] Password hashing (bcrypt)
- [x] Multi-user support with data isolation
- [x] Protected routes (frontend)

### 2. Prompts Management
Prompts are AI generation templates with customer persona injection.

**Fields:**
- `name` - Prompt name/title
- `details` - Main prompt template text
- `selected_customers` - JSON object mapping customer IDs to boolean (for persona injection)
- `url` - Reference URL (OneDrive, brand assets)
- `media_file_path` - Local media file path
- `aws_folder_url` - S3 folder URL
- `artwork_description` - Description for image generation
- `example_image` - Reference image URL for style guidance
- `tag_id` - Category tag (foreign key)

**API Endpoints:**
- `GET /api/v1/prompts` - List prompts (paginated, searchable)
- `POST /api/v1/prompts` - Create prompt
- `GET /api/v1/prompts/{id}` - Get prompt details
- `PUT /api/v1/prompts/{id}` - Update prompt
- `DELETE /api/v1/prompts/{id}` - Delete prompt

### 3. Posts Management
Posts are social media content items (drafts, scheduled, published) with archive support.

**Fields:**
- `content` - Main post text
- `caption` - Platform-specific caption
- `alt_text` - Accessibility text for images
- `status` - draft | scheduled | published
- `graphic_type` - Infographic, Short Video, Illustration, Photo, Carousel, Quote, Meme, Story, Reel, Other
- `source_url` - Reference URL
- `original_prompt_name` - Name of source prompt (if AI-generated)
- `keep` - Boolean flag for "ready to publish"
- `for_deletion` - Boolean flag for "mark for deletion"
- `is_archived` - Boolean flag for archived posts
- `archived_at` - Archive datetime
- `scheduled_at` - Scheduled publication datetime
- `published_at` - Actual publication datetime
- `media_urls` - JSON array of S3 URLs
- `prompt_id` - Source prompt (foreign key)

**API Endpoints:**
- `GET /api/v1/posts` - List posts (paginated, filterable by status/date/search/archived)
- `POST /api/v1/posts` - Create post
- `GET /api/v1/posts/{id}` - Get post details
- `PUT /api/v1/posts/{id}` - Update post
- `DELETE /api/v1/posts/{id}` - Delete post
- `POST /api/v1/posts/{id}/publish` - Mark as published
- `POST /api/v1/posts/{id}/archive` - Archive a published post
- `POST /api/v1/posts/{id}/restore` - Restore an archived post
- `POST /api/v1/posts/bulk/archive` - Bulk archive posts
- `POST /api/v1/posts/bulk/restore` - Bulk restore posts
- `POST /api/v1/posts/{id}/media` - Upload media to S3
- `DELETE /api/v1/posts/{id}/media` - Remove media
- `GET /api/v1/posts/export/csv` - Export posts to CSV

### 4. Templates Management
Reusable text snippets organized by category.

**Fields:**
- `name` - Template name
- `category` - ocr | manual | custom
- `tags` - JSON array of tag strings
- `content` - Template text content

**API Endpoints:**
- `GET /api/v1/templates` - List templates (paginated, filterable)
- `POST /api/v1/templates` - Create template
- `GET /api/v1/templates/{id}` - Get template details
- `PUT /api/v1/templates/{id}` - Update template
- `DELETE /api/v1/templates/{id}` - Delete template
- `GET /api/v1/templates/tags` - Get all unique tags

### 5. AI Text Generation
Generate social media content using LLM providers.

**Supported Providers:**
- OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku)
- Google (Gemini 3 Pro, Gemini 3 Flash)

**API Endpoint:**
- `POST /api/v1/generate/text` - Generate text from prompt

**Request:**
```json
{
  "prompt_id": 1,
  "model_config_id": 1,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "content": "Generated text...",
  "model_used": "gpt-4o",
  "provider": "openai",
  "prompt_id": 1,
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  },
  "success": true,
  "request_id": "uuid"
}
```

### 6. AI Image Generation
Generate images using AI providers.

**Supported Providers:**
- OpenAI DALL-E (dall-e-3, dall-e-2)
- Black Forest Labs Flux (flux-pro-1.1, flux-pro, flux-dev)

**API Endpoint:**
- `POST /api/v1/generate/image` - Generate image from prompt

**Request:**
```json
{
  "prompt": "A sunset over mountains",
  "model_config_id": 1,
  "size": "1024x1024",
  "quality": "hd",
  "n": 1
}
```

**Response:**
```json
{
  "images": [
    {
      "base64_data": "...",
      "format": "png",
      "revised_prompt": "..."
    }
  ],
  "model_used": "dall-e-3",
  "provider": "openai",
  "request_id": "uuid"
}
```

### 7. Credentials Management
Secure storage for API keys (encrypted with Fernet).

**Supported Credential Keys:**
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `BFL_API_KEY` (Black Forest Labs)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_BUCKET`
- `AWS_REGION`

**API Endpoints:**
- `GET /api/v1/credentials` - List credentials (values hidden)
- `POST /api/v1/credentials` - Create credential
- `PUT /api/v1/credentials/{key}` - Update credential
- `DELETE /api/v1/credentials/{key}` - Delete credential
- `POST /api/v1/credentials/validate` - Validate credential exists

### 8. Model Configuration
Configure which AI models are available per user.

**Fields:**
- `provider` - openai | anthropic | google | bfl | lm_studio_vision | openai_vision | anthropic_vision
- `model_id` - Provider-specific model ID
- `model_type` - text | image | vision
- `display_name` - User-friendly name
- `is_enabled` - Whether model is active
- `is_default` - Default model for type

**API Endpoints:**
- `GET /api/v1/models` - List user's model configs
- `POST /api/v1/models` - Create model config
- `PUT /api/v1/models/{id}` - Update model config
- `DELETE /api/v1/models/{id}` - Delete model config
- `GET /api/v1/models/providers/list` - List available providers and models (text, image, vision)
- `POST /api/v1/models/initialize` - Initialize default models for user

### 9. Customer Info / Personas
Store customer persona information for prompt injection.

**Fields:**
- `name` - Customer/persona name
- `industry` - Industry sector
- `target_audience` - Target demographic
- `brand_voice` - Tone and style
- `key_products` - Main products/services
- `unique_selling_points` - USPs
- `additional_context` - Extra context

**API Endpoints:**
- `GET /api/v1/customer-info` - List customer personas
- `POST /api/v1/customer-info` - Create persona
- `GET /api/v1/customer-info/{id}` - Get persona
- `PUT /api/v1/customer-info/{id}` - Update persona
- `DELETE /api/v1/customer-info/{id}` - Delete persona

### 10. Tags
Categories for organizing prompts.

**API Endpoints:**
- `GET /api/v1/tags` - List tags
- `POST /api/v1/tags` - Create tag
- `PUT /api/v1/tags/{id}` - Update tag
- `DELETE /api/v1/tags/{id}` - Delete tag

### 11. S3 Media Storage
- Upload images/media to AWS S3
- Automatic file naming with user ID prefix
- Content type detection
- Pre-signed URLs for secure access

### 12. CSV Export
- Export posts to CSV format
- Filterable by status, date range
- Downloadable file response

### 13. Published Posts Archive
Archive functionality for published posts with separate view.

**Features:**
- Archive published posts (moves to separate view)
- Restore archived posts back to active
- Tab-based UI (Active Posts / Archived Posts)
- Bulk archive/restore operations
- Filter by archived status in API

**Frontend:**
- Tabs on Posts List page for Active/Archived views
- Archive button on published posts
- Restore button on archived posts
- Bulk selection for archive/restore operations

### 14. OCR Processing
Extract text from images using AI vision models and save as templates.

**Supported Providers:**
- LM Studio (local, no API key required) - LLaVA models
- OpenAI Vision (GPT-4o, GPT-4o-mini, GPT-4-turbo)
- Anthropic Vision (Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku)

**API Endpoints:**
- `POST /api/v1/ocr/process` - Process image and extract text
- `GET /api/v1/ocr/providers` - List available vision providers

**Request (multipart/form-data):**
```
file: <image file>
model_config_id: 1
custom_prompt: "Extract all text..." (optional)
template_name: "My OCR Template" (optional)
template_tags: "ocr, extracted" (optional, comma-separated)
```

**Response:**
```json
{
  "extracted_text": "Text from image...",
  "model_used": "gpt-4o",
  "provider": "openai_vision",
  "usage": {
    "prompt_tokens": 500,
    "completion_tokens": 200,
    "total_tokens": 700
  },
  "success": true,
  "request_id": "uuid",
  "template_id": 5,
  "template_name": "OCR: document.png"
}
```

**Features:**
- Drag & drop image upload
- Support for PNG, JPG, GIF, WEBP (max 20MB)
- Custom extraction prompts
- Automatic OCR template creation
- Copy extracted text to clipboard
- Link to view created template

---

## Frontend Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | LoginPage | User login form |
| `/register` | RegisterPage | User registration form |
| `/` | DashboardPage | Overview/home page |
| `/prompts` | PromptsListPage | List all prompts |
| `/prompts/new` | PromptCreatePage | Create new prompt |
| `/prompts/:id` | PromptDetailPage | View prompt details |
| `/prompts/:id/edit` | PromptEditPage | Edit prompt |
| `/templates` | TemplatesListPage | List all templates |
| `/templates/new` | TemplateCreatePage | Create new template |
| `/templates/:id` | TemplateDetailPage | View template details |
| `/templates/:id/edit` | TemplateEditPage | Edit template |
| `/posts` | PostsListPage | List all posts |
| `/posts/new` | PostCreatePage | Create new post |
| `/posts/:id` | PostDetailPage | View post details |
| `/posts/:id/edit` | PostEditPage | Edit post |
| `/generate/text` | TextGenerationPage | AI text generation UI |
| `/generate/image` | ImageGenerationPage | AI image generation UI |
| `/ocr` | OCRPage | OCR text extraction from images |
| `/settings/credentials` | CredentialsPage | Manage API keys |
| `/settings/models` | ModelsPage | Configure AI models |

---

## Database Schema

### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Prompts
```sql
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    details TEXT NOT NULL,
    selected_customers JSON DEFAULT '{}',
    url VARCHAR(500),
    media_file_path VARCHAR(500),
    aws_folder_url VARCHAR(500),
    artwork_description TEXT,
    example_image VARCHAR(500),
    tag_id INTEGER REFERENCES tags(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Posts
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    caption TEXT,
    alt_text TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    graphic_type VARCHAR(100),
    source_url VARCHAR(500),
    original_prompt_name VARCHAR(255),
    keep BOOLEAN DEFAULT FALSE,
    for_deletion BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP,
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    media_urls JSON DEFAULT '[]',
    prompt_id INTEGER REFERENCES prompts(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_posts_is_archived ON posts(is_archived);
```

### Templates
```sql
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(20) NOT NULL,  -- 'ocr', 'manual', 'custom'
    tags JSON DEFAULT '[]',
    content TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Credentials
```sql
CREATE TABLE credentials (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL,
    encrypted_value TEXT NOT NULL,
    description VARCHAR(255),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(key, user_id)
);
```

### Model Configs
```sql
CREATE TABLE model_configs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    model_type VARCHAR(20) NOT NULL,  -- 'text', 'image', 'vision'
    display_name VARCHAR(100),
    is_enabled BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Features NOT YET Implemented (Gap List)

These features existed in the original tkinter app but are not yet in the web version:

### Medium Priority
1. **Additional AI Models** - GPT-5.x, Claude 4.x, Gemini 2.5 versions
2. **Enhanced Customer Personas** - Rich demographic model (age, location, occupation, interests)
3. **Reference Image Support** - Use reference images for style-guided image generation

### Low Priority
4. **Debug Viewer** - View LLM API request/response logs
5. **Audit Log Viewer** - View user action logs
6. **Batch Import** - CSV bulk import of posts
7. **Batch OCR Processing** - Process entire image folders

---

## Getting Started

### Prerequisites
- Docker Desktop
- Node.js 18+ (for frontend development)
- Git

### Quick Start
```bash
# Clone repository
git clone https://github.com/daz1057/socialMediaPostingWeb.git
cd socialMediaPostingWeb

# Start backend with Docker
docker-compose up -d

# Start frontend
cd frontend
npm install
npm run dev
```

### Environment Variables
Copy `.env.example` files and configure:

**Backend (.env):**
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/socialdb
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-fernet-key
```

**Frontend (.env):**
```
VITE_API_URL=http://localhost:8000/api/v1
```

### Default URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## API Authentication

All API endpoints (except `/auth/login`, `/auth/register`, `/auth/refresh`) require JWT authentication.

**Header:** `Authorization: Bearer <access_token>`

**Token Refresh:** `POST /api/v1/auth/refresh` with refresh token in body

---

## Contributing

1. Create feature branch from `main`
2. Follow existing code patterns
3. Add appropriate tests
4. Update this documentation if adding features
5. Create pull request with descriptive title

---

*Last Updated: January 21, 2025*
