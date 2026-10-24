# moneytracktor

REST API for personal finance tracking: accounts, income and expenses, transfers between
accounts, budgets and reports. All amounts are in Kazakhstani tenge (KZT).

Work in progress.

## Stack

Python 3.13, Django 5.2 LTS, Django REST Framework, Simple JWT, django-filter, PostgreSQL 18,
Celery with Redis, uv, pytest, ruff, Docker Compose.

## API

| Method | URL | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | no | Create a user with default categories |
| POST | `/api/auth/token` | no | Get access and refresh tokens |
| POST | `/api/auth/token/refresh` | no | Get a new access token |
| GET | `/api/me` | yes | Current user |
| GET, POST | `/api/accounts` | yes | List or create accounts |
| GET, PUT, PATCH, DELETE | `/api/accounts/{id}` | yes | Read, update or delete an account |
| GET, POST | `/api/categories` | yes | List or create categories |
| GET, PUT, PATCH, DELETE | `/api/categories/{id}` | yes | Read, rename or delete a category |
| GET, POST | `/api/transactions` | yes | List (paginated, filtered) or create transactions |
| GET, PUT, PATCH, DELETE | `/api/transactions/{id}` | yes | Read, update or delete a transaction |

Authenticated requests send the access token in the header `Authorization: Bearer <token>`.
Each user sees only their own data: another user's object returns 404.

An account or a category that has transactions cannot be deleted (400).

The transaction list returns 20 items per page and accepts these query parameters:

| Parameter | Example | Meaning |
|---|---|---|
| `date_from`, `date_to` | `2026-10-01` | Date range, both ends included |
| `account`, `category` | `3` | Account or category id |
| `type` | `expense` | `income` or `expense` |
| `search` | `lunch` | Text in the note, case-insensitive |
| `ordering` | `-amount` | `date`, `-date`, `amount`, `-amount` (default: newest first) |
| `page` | `2` | Page number |

Example: create an expense and list October expenses, largest first.

```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Authorization: Bearer <access>" -H "Content-Type: application/json" \
  -d '{"type": "expense", "amount": "2500.00", "date": "2026-10-20", "account": 1, "category": 2, "note": "Lunch"}'

curl "http://localhost:8000/api/transactions?type=expense&date_from=2026-10-01&date_to=2026-10-31&ordering=-amount" \
  -H "Authorization: Bearer <access>"
```

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
