# Consilium Backend

REST API на **FastAPI** для мобильного приложения стоматологической клиники Consilium и админ-панели контента.

| Документ | Назначение |
|----------|------------|
| [AI_BACKEND.md](./AI_BACKEND.md) | Полная спецификация API для ИИ-агентов |
| [AI_CLIENT_MOBILE.md](./AI_CLIENT_MOBILE.md) | Слой данных мобильного приложения (пациент) |
| [AI_CLIENT_ADMIN.md](./AI_CLIENT_ADMIN.md) | Слой данных админ-панели |

## Возможности

- **Auth** — регистрация, вход, JWT access token, ротация refresh token
- **Doctors** — публичное чтение; CRUD и загрузка аватара — только админ
- **News** — публичное чтение (сортировка по дате, новые первые); CRUD и загрузка изображений — только админ

## Требования

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) (менеджер зависимостей)

## Структура проекта

```
consul_back/
├── src/
│   ├── main.py              # точка входа, CORS, /health, /uploads
│   ├── config.py            # настройки из .env
│   ├── database.py
│   ├── auth/                # JWT, refresh, зависимости
│   ├── models/
│   ├── routers/             # auth, doctors, news
│   ├── schemas/
│   └── utils/uploads.py
├── scripts/create_admin.py  # интерактивное создание админа
├── docker/                  # entrypoint
├── Dockerfile               # production (multi-stage)
├── Dockerfile.dev           # dev + --reload
├── docker-compose.yml
├── docker-compose.dev.yml
└── .env.example
```

## Локальная разработка

```bash
cp .env.example .env          # задай SECRET_KEY для production
uv sync
uv run uvicorn main:app --reload --app-dir src
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: `GET /health` → `{ "status": "ok" }`

По умолчанию SQLite: `consilium.db` в корне репозитория, загрузки: `uploads/`.

## Docker

**Production:**

```bash
cp .env.example .env
docker compose up --build -d
```

**Development** (hot reload, `src/` смонтирован read-only):

```bash
docker compose -f docker-compose.dev.yml up --build
```

Создать или повысить пользователя до админа в контейнере:

```bash
docker compose exec api python scripts/create_admin.py
# dev:
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

## Администратор

Админов нельзя создать через `POST /auth/register`. Используйте интерактивный скрипт:

```bash
uv run python scripts/create_admin.py
```

Если пользователь с таким телефоном уже есть — скрипт выставит `is_admin: true` и обновит пароль.

## Переменные окружения

Скопируйте `.env.example` → `.env`.

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `SECRET_KEY` | `change-me-...` | Подпись JWT; обязательно сменить в production |
| `DEBUG` | `true` | Режим отладки |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Срок жизни access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Срок жизни refresh token |
| `DATABASE_URL` | `sqlite:///.../consilium.db` | URL БД (в Docker: `sqlite:////app/data/consilium.db`) |
| `UPLOADS_DIR` | `./uploads` | Каталог файлов (в Docker: `/app/uploads`) |
| `API_PORT` | `8000` | Порт хоста в docker-compose |

## API (кратко)

Префикс: `/api/v1`. Статика: `GET /uploads/...` (вне префикса).

| Метод | Endpoint | Auth |
|-------|----------|------|
| POST | `/auth/register` | — |
| POST | `/auth/login` | — |
| POST | `/auth/refresh` | `refresh_token` в теле |
| GET | `/auth/me` | Bearer |
| GET | `/doctors`, `/doctors/{id}` | — |
| POST | `/doctors` или `/doctors/json` | Admin Bearer |
| PUT | `/doctors/{id}` или `/doctors/{id}/json` | Admin Bearer |
| DELETE | `/doctors/{id}` | Admin Bearer |
| GET | `/news`, `/news/{id}` | — |
| POST | `/news` или `/news/json` | Admin Bearer |
| PUT | `/news/{id}` или `/news/{id}/json` | Admin Bearer |
| DELETE | `/news/{id}` | Admin Bearer |

### Auth

1. `POST /api/v1/auth/login` → `{ access_token, refresh_token, token_type }`
2. Заголовок `Authorization: Bearer <access_token>` для защищённых маршрутов
3. При истечении access → `POST /api/v1/auth/refresh` с `{ "refresh_token": "..." }` (старый refresh отзывается)

### Загрузка файлов (админ)

`multipart/form-data` на `POST/PUT` без суффикса `/json`, либо JSON на `*/json`.  
Лимит: **5 MB**; типы: JPEG, PNG, WebP, GIF.

Подробности — в [AI_BACKEND.md](./AI_BACKEND.md).
