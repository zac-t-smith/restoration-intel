# syntax=docker/dockerfile:1.4
ARG PYTHON_VERSION=3.11

# ===== BUILDER STAGE =====
FROM python:${PYTHON_VERSION}-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/usr/local/bin:$PATH"

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with pip caching
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# ===== DEVELOPMENT STAGE =====
FROM python:${PYTHON_VERSION}-slim AS development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH" \
    UVICORN_RELOAD=true

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    # Add non-root user
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --ingroup appuser appuser

WORKDIR /app

# Copy Python packages and binaries from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY api/py /app/py
COPY api/__init__.py /app/__init__.py

# Set permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

# Development mode with hot reload
CMD ["python", "-m", "uvicorn", "py.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===== PRODUCTION STAGE =====
FROM python:${PYTHON_VERSION}-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH" \
    UVICORN_RELOAD=false

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    # Add non-root user
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --ingroup appuser appuser

WORKDIR /app

# Copy Python packages and binaries from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY api/py /app/py
COPY api/__init__.py /app/__init__.py

# Set permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

# Production mode without hot reload
CMD ["python", "-m", "uvicorn", "py.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]