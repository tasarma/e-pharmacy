# --- Stage 1: Base ---
FROM python:3.14-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Install system dependencies (uncomment if needed, e.g. for Postgres or Pillow)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Dependencies ---
FROM base AS deps
COPY pyproject.toml uv.lock ./
# Install dependencies (no dev)
RUN uv sync --frozen --no-install-project --no-dev

# --- Stage 3: Development ---
FROM base AS dev
COPY pyproject.toml uv.lock ./
# Install all dependencies (including dev)
RUN uv sync --frozen --no-install-project

COPY src/ src/
COPY Makefile ./

# --- Stage 4: Testing ---
FROM dev AS tested
# Run pytest tests; build fails if tests fail
RUN make test-fast

# --- Stage 5: Release (Production Prep) ---
FROM base AS release
# Copy virtualenv from deps stage
COPY --from=deps /app/.venv /app/.venv
COPY --from=deps /app/uv.lock /app/pyproject.toml ./

COPY src/ src/
# Collect static files
RUN python src/manage.py collectstatic --noinput

# --- Stage 6: Final Service ---
FROM python:3.14-slim AS service

# Copy only necessary files from release
WORKDIR /app
COPY --from=release /app /app

# Set envs again
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

# Create a non-privileged user
RUN useradd -m django-user && \
    chown -R django-user:django-user /app
USER django-user

EXPOSE 8000

ENTRYPOINT ["gunicorn"]
CMD ["config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
