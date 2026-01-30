# Skill 10: revenue-forecasting
# Production-ready Docker container

FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Dependencies stage
# ============================================================================
FROM base as dependencies

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Application stage
# ============================================================================
FROM dependencies as application

WORKDIR /app

# Copy shared modules
COPY ../../shared/ /app/shared/

# Copy skill-specific code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/tmp /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    LOG_LEVEL=INFO \
    SKILL_NAME=revenue-forecasting

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run as non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Start application
CMD ["uvicorn", "handler:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
