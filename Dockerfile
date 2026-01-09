# Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Builder stage for Python dependencies
FROM python:3.12-slim AS builder

# Set build arguments
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip wheel && \
    /opt/venv/bin/pip install -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies (including Typst and standard utils)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY ./app /app/app

# Copy built frontend if needed (assuming FastAPI serves it from app/static/frontend)
# Adjust the destination path as per your FastAPI setup
COPY --from=frontend-builder /frontend/dist /app/app/static/frontend

# Create a non-root user
RUN groupadd --system app && \
    useradd --system --gid app --home-dir /app --shell /bin/bash app && \
    chown -R app:app /app

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
