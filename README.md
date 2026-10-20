# moneytracktor

REST API for personal finance tracking: accounts, income and expenses, transfers between
accounts, budgets and reports. All amounts are in Kazakhstani tenge (KZT).

Work in progress.

## Stack

Python 3.13, Django 5.2 LTS, PostgreSQL 18, Celery with Redis, uv, pytest, ruff, Docker Compose.

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
