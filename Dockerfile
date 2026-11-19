FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY alembic.ini .
COPY alembic ./alembic/
COPY app ./app/
COPY consumer ./consumer/

COPY docker/entrypoint-api.sh docker/entrypoint-consumer.sh /entrypoint/
RUN chmod +x /entrypoint/entrypoint-api.sh /entrypoint/entrypoint-consumer.sh
