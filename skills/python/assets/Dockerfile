# =============================================================================
# Multi-stage Dockerfile for Python applications
# =============================================================================

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
COPY src/ src/

# Create wheel
RUN pip install --no-cache-dir build \
    && python -m build --wheel

# =============================================================================
# Production stage
# =============================================================================
FROM python:3.11-slim as production

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash appuser

# Copy wheel and install
COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl \
    && rm *.whl

# Switch to non-root user
USER appuser

# Default command
CMD ["python", "-m", "my_project"]

# =============================================================================
# Development stage
# =============================================================================
FROM python:3.11-slim as development

WORKDIR /app

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/

# Install with dev dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Default command for development
CMD ["pytest", "-v"]
