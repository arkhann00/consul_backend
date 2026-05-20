# Consilium Backend

FastAPI backend for the Consilium dentistry mobile app.

## AI / client integration docs

| File | For |
|------|-----|
| [AI_BACKEND.md](./AI_BACKEND.md) | Full API reference for agents |
| [AI_CLIENT_MOBILE.md](./AI_CLIENT_MOBILE.md) | Patient mobile app data layer |
| [AI_CLIENT_ADMIN.md](./AI_CLIENT_ADMIN.md) | Admin panel data layer |

## Modules

- **Auth** — registration, login, Bearer access token, refresh token rotation
- **Doctors** — CRUD for admin panel (public read)
- **News** — CRUD for admin panel (public read)

## Setup

```bash
uv sync
uv run uvicorn main:app --reload --app-dir src
```

API docs: http://127.0.0.1:8000/docs

## Docker

Production:

```bash
cp .env.example .env   # задай SECRET_KEY
docker compose up --build -d
```

Development (hot reload + монтирование `src/`):

```bash
docker compose -f docker-compose.dev.yml up --build
```

Создать админа в контейнере:

```bash
docker compose exec api python scripts/create_admin.py
```

Для dev-контейнера:

```bash
docker compose -f docker-compose.dev.yml exec api python scripts/create_admin.py
```

Только образ без compose:

```bash
docker build -t consilium-api .
docker run -p 8000:8000 --env-file .env \
  -e DATABASE_URL=sqlite:////app/data/consilium.db \
  -e UPLOADS_DIR=/app/uploads \
  -v consilium_data:/app/data \
  -v consilium_uploads:/app/uploads \
  consilium-api
```

## Create admin user

```bash
uv run python scripts/create_admin.py
```

## Environment

Copy `.env.example` to `.env` and set `SECRET_KEY` for production.

## API Overview

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/v1/auth/register` | — |
| POST | `/api/v1/auth/login` | — |
| POST | `/api/v1/auth/refresh` | refresh_token in body |
| GET | `/api/v1/auth/me` | Bearer |
| GET | `/api/v1/doctors` | — |
| POST | `/api/v1/doctors` or `/json` | Admin Bearer |
| PUT | `/api/v1/doctors/{id}` or `/json` | Admin Bearer |
| DELETE | `/api/v1/doctors/{id}` | Admin Bearer |
| GET | `/api/v1/news` | — |
| POST | `/api/v1/news` or `/json` | Admin Bearer |
| PUT | `/api/v1/news/{id}` or `/json` | Admin Bearer |
| DELETE | `/api/v1/news/{id}` | Admin Bearer |

### Auth flow

1. `POST /api/v1/auth/login` → `{ access_token, refresh_token }`
2. Use `Authorization: Bearer <access_token>` for protected routes
3. When access token expires → `POST /api/v1/auth/refresh` with `{ "refresh_token": "..." }`

### Admin CRUD with file upload

Use `multipart/form-data` on `POST /api/v1/doctors` and `POST /api/v1/news`, or JSON on `*/json` endpoints.
