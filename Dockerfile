FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv

# The virtualenv lives outside /app, so the mounted project folder does not hide it.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY . .
RUN uv sync --locked

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
