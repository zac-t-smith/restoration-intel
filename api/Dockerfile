ARG REQUIREMENTS_PATH=requirements.txt

FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies and create non-root user
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    build-essential \
    libpq-dev && \ # <--- ADD THIS LINE FOR PSYCOPG2
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --ingroup appuser appuser

# Copy requirements file
COPY ${REQUIREMENTS_PATH} . # Using the ARG for consistency

# Install Python dependencies
RUN pip install --no-cache-dir numpy==1.23.5 && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libopenblas-dev \
    liblapack-dev && \ # Note: libpq5 (runtime for postgresql client) might be good here if not implicitly included by python slim
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --ingroup appuser appuser

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Set working directory
WORKDIR /app

# Copy application code
COPY api/py /app/py
COPY api/*.py /app/

# Create logs directory
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["uvicorn", "py.app:app", "--host", "0.0.0.0", "--port", "8000"]