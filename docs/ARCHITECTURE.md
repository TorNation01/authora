# AUTHORA Architecture

## Overview

AUTHORA is a full-stack application with a Next.js frontend and FastAPI backend, designed for standalone deployment or integration into the Anakatech ecosystem.

## Components

### Frontend (apps/web)

- **Framework**: Next.js 14 with App Router
- **UI**: Tailwind CSS, shadcn/ui (Radix primitives)
- **Editor**: TipTap (ProseMirror-based)
- **State**: React state, localStorage for tokens

### Backend (apps/api)

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Auth**: JWT (access + refresh tokens), bcrypt passwords

### Data

- **PostgreSQL**: Primary data store
- **Redis**: Session storage (optional, for future scaling)

## API Structure

```
/api/v1/
  /auth          - register, login, refresh, logout, me
  /projects      - CRUD projects
  /projects/{id}/books - CRUD books, chapters
  /projects/{id}/books/{id}/notes - CRUD notes
  /ai/complete    - AI writing assistance (streaming)
  /export/books/{id}/{format} - DOCX, PDF, EPUB, TXT
  /dictionary    - lookup, thesaurus (Free Dictionary API)
```

## Database Schema

- **users**: Accounts, auth
- **sessions**: Refresh token storage
- **projects**: User project containers
- **books**: Fiction/nonfiction with planner_data (JSONB)
- **chapters**: TipTap JSON content, word_count
- **notes**: Research/scratch per book
- **user_stats**: Streaks, XP, level
- **achievements**, **goals**, **streak_logs**: Gamification
- **audit_logs**: Security/compliance
- **settings**: Key-value config

## AI Integration

- **Providers**: OpenAI (default), Anthropic
- **Config**: OPENAI_API_KEY, ANTHROPIC_API_KEY, AI_PROVIDER, AI_MODEL
- **Flow**: Streaming completion with optional chapter context

## Export

- **Formats**: DOCX (python-docx), PDF (reportlab), EPUB (ebooklib), TXT
- **Content**: TipTap JSON → plain text extraction

## Deployment

- **Local**: `npm run dev` + `npm run dev:api`
- **Docker**: `docker compose up -d`
- **Setup**: `npm run setup` for guided env config
