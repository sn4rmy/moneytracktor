# moneytracktor

REST API for personal finance tracking: accounts, income and expenses, transfers between
accounts, budgets and reports. All amounts are in Kazakhstani tenge (KZT).

Work in progress.

## Stack

Python 3.13, Django 5.2 LTS, Django REST Framework, Simple JWT, PostgreSQL 18, Celery with Redis,
uv, pytest, ruff, Docker Compose.

## API

| Method | URL | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | no | Create a user with default categories |
| POST | `/api/auth/token` | no | Get access and refresh tokens |
| POST | `/api/auth/token/refresh` | no | Get a new access token |
| GET | `/api/me` | yes | Current user |

Authenticated requests send the access token in the header `Authorization: Bearer <token>`.

## Running with Docker

```bash
docker compose up --build
```

This starts the web server (http://localhost:8000), PostgreSQL, Redis and a Celery worker.
Migrations are applied on startup.

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

The admin is available at http://localhost:8000/admin/.

## Local development

```bash
cp .env.example .env
uv sync
docker compose up -d db redis
uv run python manage.py migrate
uv run python manage.py runserver
```

## Tests and linting

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Tests need PostgreSQL. Run them inside Docker with `docker compose exec web pytest`,
or on the host against the `db` service as shown above.
