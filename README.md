# moneytracktor

A REST API for tracking personal finances. You can add your accounts (cash, card, deposit),
write down income and expenses, move money between accounts, see the balance of each one
and get simple reports. All amounts are in tenge (KZT).

I'm building this project to learn Django REST Framework. It's not finished yet: budgets
with email alerts, CSV export and Swagger docs are next.

## Stack

- Python 3.13, Django 5.2, Django REST Framework
- PostgreSQL
- JWT auth (Simple JWT)
- django-filter
- Celery + Redis
- pytest, factory_boy, ruff
- Docker Compose, uv

## How to run

You only need Docker:

```bash
docker compose up --build
```

The API will be on http://localhost:8000. Migrations run on startup.

To use the admin panel (http://localhost:8000/admin/), create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

If you want to run Django without Docker, you need uv. PostgreSQL and Redis still run in Docker:

```bash
cp .env.example .env
uv sync
docker compose up -d db redis
uv run python manage.py migrate
uv run python manage.py runserver
```

## Tests

Tests need PostgreSQL, so start it first with `docker compose up -d db`.

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

You can also run them inside the container: `docker compose exec web pytest`.

## Endpoints

Everything except register and token needs the header `Authorization: Bearer <access token>`.

| Method | URL | What it does |
|---|---|---|
| POST | /api/auth/register | Sign up, also creates default categories |
| POST | /api/auth/token | Log in, returns access and refresh tokens |
| POST | /api/auth/token/refresh | Get a new access token |
| GET | /api/me | Current user |
| GET, POST | /api/accounts | List your accounts with balances, or create one |
| GET, PUT, PATCH, DELETE | /api/accounts/{id} | One account |
| GET, POST | /api/categories | List categories, or create one |
| GET, PUT, PATCH, DELETE | /api/categories/{id} | One category |
| GET, POST | /api/transactions | List transactions, or create one |
| GET, PUT, PATCH, DELETE | /api/transactions/{id} | One transaction |
| POST | /api/transfers | Move money between two of your accounts |
| GET | /api/reports/summary?date_from=&date_to= | Income, expenses and total for a period |
| GET | /api/reports/by-category?date_from=&date_to= | Expenses by category for a period |
| GET | /api/reports/monthly?year= | Income and expenses by month |

A few rules:

- you only see your own data, someone else's object returns 404
- an account or a category that has transactions can't be deleted (400)
- you can't transfer money to the same account (400)
- transactions created by a transfer can't be edited or deleted (400)
- reports don't count transfers, because a transfer is not income or an expense
- report parameters are required (`date_from` and `date_to` in `YYYY-MM-DD`, or `year`),
  without them the API returns 400

The transaction list shows 20 items per page. Filters: `date_from`, `date_to`, `account`,
`category`, `type` (`income` or `expense`), `search` (searches in the note) and
`ordering` (`date`, `-date`, `amount`, `-amount`).

## Examples

Log in and get a token:

```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "my-password-123"}'
```

Add an expense:

```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Authorization: Bearer <access>" -H "Content-Type: application/json" \
  -d '{"type": "expense", "amount": "2500.00", "date": "2026-10-20", "account": 1, "category": 2, "note": "Lunch"}'
```

Move 50 000 tenge from the card to the deposit:

```bash
curl -X POST http://localhost:8000/api/transfers \
  -H "Authorization: Bearer <access>" -H "Content-Type: application/json" \
  -d '{"from_account": 1, "to_account": 2, "amount": "50000.00", "date": "2026-10-15"}'
```

After that `GET /api/accounts` shows the new balances:

```json
[
  {"id": 2, "name": "Deposit", "type": "deposit", "balance": "50000.00"},
  {"id": 1, "name": "Kaspi Gold", "type": "card", "balance": "197500.00"}
]
```

Get a summary for October:

```bash
curl "http://localhost:8000/api/reports/summary?date_from=2026-10-01&date_to=2026-10-31" \
  -H "Authorization: Bearer <access>"
```

```json
{"income": "250000.00", "expense": "2500.00", "total": "247500.00"}
```

## Design decisions

- Money is stored as `Decimal`, not `float`, so there are no rounding errors
  like `0.1 + 0.2 = 0.30000000000000004`.
- The account balance is not stored in the database. It's calculated from transactions
  (income minus expenses) in one SQL query, so it can't get out of sync.
- A transfer saves a transfer record and two transactions (an expense on one account and
  an income on the other) inside `transaction.atomic`. If something fails, nothing is saved.
- Reports are calculated by the database (`aggregate` and `annotate` turn into `SUM` and
  `GROUP BY`), not by loops in Python. Transfers are excluded with `transfer__isnull=True`.
- Business logic lives in `services.py`. Views only take the request and return the response.
- Someone else's object returns 404, not 403, so you can't even tell that it exists.
