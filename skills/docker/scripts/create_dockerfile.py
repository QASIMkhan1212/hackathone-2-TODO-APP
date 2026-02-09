#!/usr/bin/env python3
"""Generate Dockerfile for various frameworks and languages."""

import argparse
from pathlib import Path


def generate_python_dockerfile(framework: str = "fastapi", production: bool = True) -> str:
    """Generate Python Dockerfile."""
    if framework == "fastapi":
        if production:
            return '''# syntax=docker/dockerfile:1

# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends gcc libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends libpq5 \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Install wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        else:
            return '''FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
'''

    elif framework == "django":
        if production:
            return '''# syntax=docker/dockerfile:1

FROM python:3.12-slim AS production

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    DJANGO_SETTINGS_MODULE=config.settings.production

# Install dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        gcc libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home appuser \\
    && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
'''
        else:
            return '''FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
'''

    else:  # Generic Python
        return '''FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
'''


def generate_node_dockerfile(framework: str = "express", production: bool = True) -> str:
    """Generate Node.js Dockerfile."""
    if framework == "nextjs":
        if production:
            return '''# syntax=docker/dockerfile:1

# Dependencies stage
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Builder stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g 1001 -S nodejs \\
    && adduser -S nextjs -u 1001

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
'''
        else:
            return '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
'''

    elif framework == "express":
        if production:
            return '''# syntax=docker/dockerfile:1

# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g 1001 -S appgroup \\
    && adduser -S appuser -u 1001 -G appgroup

COPY --from=builder /app/package*.json ./
RUN npm ci --only=production

COPY --from=builder --chown=appuser:appgroup /app/dist ./dist

USER appuser

EXPOSE 3000

CMD ["node", "dist/index.js"]
'''
        else:
            return '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
'''

    else:  # Generic Node
        return '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

USER node

EXPOSE 3000

CMD ["node", "index.js"]
'''


def generate_go_dockerfile(production: bool = True) -> str:
    """Generate Go Dockerfile."""
    if production:
        return '''# syntax=docker/dockerfile:1

# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server ./cmd/server

# Production stage
FROM alpine:3.19 AS production

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/server .

# Create non-root user
RUN adduser -D -g '' appuser
USER appuser

EXPOSE 8080

CMD ["./server"]
'''
    else:
        return '''FROM golang:1.22-alpine

WORKDIR /app

# Install Air for hot reload
RUN go install github.com/cosmtrek/air@latest

COPY go.* ./
RUN go mod download

COPY . .

EXPOSE 8080

CMD ["air"]
'''


def generate_rust_dockerfile(production: bool = True) -> str:
    """Generate Rust Dockerfile."""
    if production:
        return '''# syntax=docker/dockerfile:1

# Build stage
FROM rust:1.75-alpine AS builder

# Install build dependencies
RUN apk add --no-cache musl-dev

WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Build dependencies (cached layer)
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Copy source code
COPY src ./src

# Build application
RUN touch src/main.rs
RUN cargo build --release --target x86_64-unknown-linux-musl

# Production stage
FROM scratch

COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/myapp /myapp

EXPOSE 8080

ENTRYPOINT ["/myapp"]
'''
    else:
        return '''FROM rust:1.75-alpine

WORKDIR /app

# Install cargo-watch for hot reload
RUN cargo install cargo-watch

COPY Cargo.toml Cargo.lock ./
COPY src ./src

EXPOSE 8080

CMD ["cargo", "watch", "-x", "run"]
'''


def generate_dockerfile(
    language: str,
    framework: str = "",
    production: bool = True,
) -> str:
    """Generate Dockerfile based on language and framework."""
    if language == "python":
        return generate_python_dockerfile(framework or "fastapi", production)
    elif language == "node" or language == "javascript":
        return generate_node_dockerfile(framework or "express", production)
    elif language == "go" or language == "golang":
        return generate_go_dockerfile(production)
    elif language == "rust":
        return generate_rust_dockerfile(production)
    else:
        raise ValueError(f"Unsupported language: {language}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Dockerfile for various languages and frameworks"
    )
    parser.add_argument(
        "language",
        choices=["python", "node", "javascript", "go", "golang", "rust"],
        help="Programming language",
    )
    parser.add_argument(
        "--framework", "-f",
        help="Framework (fastapi, django for Python; express, nextjs for Node)",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Generate development Dockerfile",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("Dockerfile"),
        help="Output file path",
    )

    args = parser.parse_args()

    try:
        dockerfile = generate_dockerfile(
            args.language,
            args.framework,
            production=not args.dev,
        )

        args.output.write_text(dockerfile, encoding="utf-8")
        print(f"✓ Generated {args.output}")

        # Print usage instructions
        print("\nNext steps:")
        print(f"  docker build -t myapp .")
        print(f"  docker run -p 8000:8000 myapp")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
