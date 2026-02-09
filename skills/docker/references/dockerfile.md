# Dockerfile Reference

Complete guide to writing efficient, secure, and production-ready Dockerfiles.

## Basic Structure

```dockerfile
# Base image
FROM <image>:<tag>

# Metadata
LABEL maintainer="you@example.com"
LABEL version="1.0"

# Environment variables
ENV APP_HOME=/app
ENV NODE_ENV=production

# Working directory
WORKDIR $APP_HOME

# Install dependencies
RUN <commands>

# Copy files
COPY <src> <dest>

# Expose ports
EXPOSE <port>

# Define entrypoint
ENTRYPOINT ["executable"]

# Default command
CMD ["param1", "param2"]
```

## Instructions Reference

### FROM

```dockerfile
# Official images
FROM python:3.12-slim
FROM node:20-alpine
FROM golang:1.22-alpine

# Specific digest (immutable)
FROM python:3.12-slim@sha256:abc123...

# Multi-platform
FROM --platform=linux/amd64 python:3.12-slim

# Scratch (empty base)
FROM scratch
```

### ARG and ENV

```dockerfile
# Build-time arguments
ARG PYTHON_VERSION=3.12
ARG BUILD_DATE

FROM python:${PYTHON_VERSION}-slim

# Runtime environment variables
ENV APP_HOME=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Convert ARG to ENV
ARG VERSION
ENV APP_VERSION=${VERSION}
```

### WORKDIR

```dockerfile
# Set working directory (creates if doesn't exist)
WORKDIR /app

# Use ENV variable
ENV APP_HOME=/application
WORKDIR $APP_HOME

# Multiple WORKDIR (paths are relative)
WORKDIR /app
WORKDIR src
WORKDIR api
# Current dir: /app/src/api
```

### COPY and ADD

```dockerfile
# Copy files
COPY package.json ./
COPY package*.json ./
COPY . .

# Copy with ownership
COPY --chown=appuser:appgroup src/ ./src/

# Copy from build stage
COPY --from=builder /app/dist ./dist

# ADD (avoid unless needed)
# - Extracts tar archives automatically
# - Can fetch URLs (not recommended)
ADD archive.tar.gz /app/
```

### RUN

```dockerfile
# Shell form (runs in /bin/sh -c)
RUN apt-get update && apt-get install -y curl

# Exec form (preferred for commands with spaces)
RUN ["apt-get", "install", "-y", "curl"]

# Multi-line with cleanup
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Run as different user
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
```

### USER

```dockerfile
# Create and switch to non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Alpine variant
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Switch user
USER appuser

# Switch back for specific commands
USER root
RUN apt-get update
USER appuser
```

### EXPOSE

```dockerfile
# Document exposed ports
EXPOSE 8000
EXPOSE 8000/tcp
EXPOSE 8000/udp

# Multiple ports
EXPOSE 80 443 8080
```

### ENTRYPOINT and CMD

```dockerfile
# ENTRYPOINT: defines the executable
# CMD: provides default arguments

# Exec form (preferred)
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["main:app", "--host", "0.0.0.0"]

# Result: python -m uvicorn main:app --host 0.0.0.0

# Can override CMD at runtime:
# docker run myapp main:app --host 0.0.0.0 --port 9000

# Shell form (avoid - creates shell subprocess)
ENTRYPOINT python main.py
CMD ["--port", "8000"]

# Script entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
```

### HEALTHCHECK

```dockerfile
# Basic health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

# With options
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Disable inherited health check
HEALTHCHECK NONE

# Using exec form
HEALTHCHECK --interval=30s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
```

### VOLUME

```dockerfile
# Create mount point
VOLUME /data
VOLUME /var/log /var/db

# JSON format
VOLUME ["/data"]
```

### LABEL

```dockerfile
# Metadata labels
LABEL maintainer="dev@example.com"
LABEL version="1.0.0"
LABEL description="My application"

# Multiple labels
LABEL org.opencontainers.image.title="My App" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="My Company" \
      org.opencontainers.image.source="https://github.com/user/repo"
```

## Multi-Stage Builds

### Basic Multi-Stage

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

### Multiple Build Targets

```dockerfile
# Base stage
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .

# Development stage
FROM base AS development
RUN pip install -r requirements.txt
RUN pip install pytest black ruff
COPY . .
CMD ["python", "-m", "pytest"]

# Production dependencies
FROM base AS production-deps
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM production-deps AS production
COPY . .
USER nobody
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]

# Build specific target:
# docker build --target development -t myapp:dev .
# docker build --target production -t myapp:prod .
```

### Build with External Binaries

```dockerfile
# Build Go binary
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server

# Minimal runtime
FROM scratch
COPY --from=builder /app/server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/server"]
```

## Build Cache Optimization

### Layer Caching

```dockerfile
# Good: Dependencies first, code later
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Bad: Cache invalidated on any change
COPY . .
RUN npm ci
```

### BuildKit Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1

# Cache pip downloads
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache npm
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Cache Go modules
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

# Cache apt
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

### Bind Mounts for Build

```dockerfile
# syntax=docker/dockerfile:1

# Mount source without copying
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    npm ci

# Mount secrets during build
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

## Language-Specific Patterns

### Python

```dockerfile
FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Node.js

```dockerfile
FROM node:20-alpine

# Create app directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Bundle app source
COPY . .

# Use non-root user
USER node

EXPOSE 3000
CMD ["node", "index.js"]
```

### Go

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server ./cmd/server

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates
WORKDIR /app

COPY --from=builder /app/server .

RUN adduser -D -g '' appuser
USER appuser

EXPOSE 8080
ENTRYPOINT ["./server"]
```

### Rust

```dockerfile
# Build stage
FROM rust:1.75-alpine AS builder

RUN apk add --no-cache musl-dev

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release --target x86_64-unknown-linux-musl

# Runtime stage
FROM scratch

COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/myapp /myapp

ENTRYPOINT ["/myapp"]
```

## Security Best Practices

### Non-Root User

```dockerfile
# Debian/Ubuntu
RUN groupadd -r app && useradd -r -g app app
USER app

# Alpine
RUN addgroup -S app && adduser -S app -G app
USER app

# Use numeric UID for compatibility
USER 1000:1000
```

### Read-Only Filesystem

```dockerfile
# Application code as read-only
COPY --chmod=444 src/ ./src/

# Make specific files executable
COPY --chmod=555 entrypoint.sh /

# At runtime:
# docker run --read-only --tmpfs /tmp myapp
```

### No New Privileges

```dockerfile
# In entrypoint script
#!/bin/sh
exec "$@"

# At runtime:
# docker run --security-opt=no-new-privileges myapp
```

### Minimal Base Images

```dockerfile
# Size comparison:
# python:3.12       ~1GB
# python:3.12-slim  ~150MB
# python:3.12-alpine ~50MB

# Distroless (no shell, minimal)
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
CMD ["main.py"]
```

## Debugging Dockerfiles

### Build with Progress

```bash
# Show all build output
DOCKER_BUILDKIT=1 docker build --progress=plain .

# No cache for fresh build
docker build --no-cache .

# Build specific stage
docker build --target builder .
```

### Inspect Image

```bash
# View image layers
docker history myimage:latest

# Inspect image metadata
docker inspect myimage:latest

# View filesystem
docker run -it myimage:latest sh
```

### Common Issues

```dockerfile
# Issue: Permission denied
# Fix: Ensure files are owned by runtime user
COPY --chown=appuser:appgroup . .

# Issue: Module not found
# Fix: Ensure PYTHONPATH or working directory is correct
ENV PYTHONPATH=/app
WORKDIR /app

# Issue: Binary not found
# Fix: Use exec form with full path
CMD ["/usr/local/bin/python", "main.py"]

# Issue: Signal handling (PID 1 problem)
# Fix: Use tini or dumb-init
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "main.py"]
```
