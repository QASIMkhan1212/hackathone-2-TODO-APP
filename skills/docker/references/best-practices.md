# Docker Best Practices

Comprehensive guide to Docker best practices for production-ready containers.

## Image Optimization

### Use Minimal Base Images

```dockerfile
# Good: Minimal base images
FROM python:3.12-slim      # ~150MB
FROM python:3.12-alpine    # ~50MB
FROM node:20-alpine        # ~180MB
FROM golang:1.22-alpine    # ~250MB

# Better: Distroless (no shell, minimal attack surface)
FROM gcr.io/distroless/python3-debian12
FROM gcr.io/distroless/nodejs20-debian12

# Best: Scratch for static binaries
FROM scratch
COPY myapp /myapp
ENTRYPOINT ["/myapp"]
```

### Multi-Stage Builds

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage - only runtime deps
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]

# Development stage - includes dev deps
FROM builder AS development
RUN npm install --include=dev
CMD ["npm", "run", "dev"]
```

### Layer Optimization

```dockerfile
# Good: Dependencies before code (cache friendly)
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Good: Combine RUN commands
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Good: Use .dockerignore
# .dockerignore
.git
node_modules
__pycache__
*.pyc
.env*
*.md
tests/
```

### Build Cache

```dockerfile
# syntax=docker/dockerfile:1

# Use BuildKit cache mounts
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.npm \
    npm ci

RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
```

## Security

### Non-Root User

```dockerfile
# Create user (Debian/Ubuntu)
RUN groupadd -r -g 1001 appgroup \
    && useradd -r -u 1001 -g appgroup -s /bin/false appuser

# Create user (Alpine)
RUN addgroup -g 1001 -S appgroup \
    && adduser -u 1001 -S appuser -G appgroup -s /bin/false

# Set ownership and switch user
COPY --chown=appuser:appgroup . /app
USER appuser

# Or use numeric UID for portability
USER 1001:1001
```

### Read-Only Filesystem

```dockerfile
# Application code as read-only
COPY --chmod=444 src/ ./src/
COPY --chmod=555 entrypoint.sh ./

# At runtime
# docker run --read-only --tmpfs /tmp myapp
```

### No New Privileges

```dockerfile
# Runtime security option
# docker run --security-opt=no-new-privileges myapp
```

### Secrets Handling

```dockerfile
# Never do this
ENV API_KEY=secret123  # Visible in image history

# Use build secrets (BuildKit)
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    ./configure --api-key="$API_KEY"

# Build with: docker build --secret id=api_key,src=./api_key.txt .

# At runtime, use Docker secrets or environment
services:
  app:
    secrets:
      - api_key
secrets:
  api_key:
    file: ./secrets/api_key.txt
```

### Scan for Vulnerabilities

```bash
# Docker Scout (built-in)
docker scout cve myimage:latest
docker scout quickview myimage:latest

# Trivy
trivy image myimage:latest

# Grype
grype myimage:latest
```

### Minimal Attack Surface

```dockerfile
# Remove unnecessary packages
RUN apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# Don't install docs/man pages
RUN apt-get install -y --no-install-recommends package

# Use distroless images
FROM gcr.io/distroless/base-debian12
```

## Runtime Configuration

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Graceful Shutdown

```dockerfile
# Use exec form to receive signals properly
CMD ["python", "-m", "uvicorn", "main:app"]

# Or use tini for proper signal handling
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "main.py"]
```

```python
# Application code
import signal
import sys

def shutdown_handler(signum, frame):
    print("Graceful shutdown...")
    # Cleanup resources
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M

    # OOM killer settings
    oom_score_adj: 100

    # Process limits
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### Logging

```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        tag: "{{.Name}}/{{.ID}}"
```

```dockerfile
# Application: Log to stdout/stderr
CMD ["python", "-u", "main.py"]  # -u for unbuffered
```

## Development Workflow

### Development vs Production

```yaml
# docker-compose.yml (base)
services:
  app:
    build: .

# docker-compose.override.yml (auto-loaded for development)
services:
  app:
    build:
      target: development
    volumes:
      - ./src:/app/src
    environment:
      - DEBUG=true
    ports:
      - "8000:8000"
      - "5678:5678"  # Debugger

# docker-compose.prod.yml
services:
  app:
    build:
      target: production
    restart: always
```

### Hot Reload

```yaml
services:
  # Python with uvicorn
  python-app:
    volumes:
      - ./src:/app/src
    command: uvicorn main:app --reload --host 0.0.0.0

  # Node.js with nodemon
  node-app:
    volumes:
      - ./src:/app/src
      - node_modules:/app/node_modules
    command: npx nodemon --watch src src/index.js

  # Go with Air
  go-app:
    volumes:
      - ./:/app
    command: air

volumes:
  node_modules:
```

### Debugging

```yaml
services:
  app:
    ports:
      - "5678:5678"  # debugpy
    environment:
      - DEBUG=true
    command: >
      python -m debugpy --listen 0.0.0.0:5678
      --wait-for-client -m uvicorn main:app --reload
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Test
        uses: docker/build-push-action@v5
        with:
          context: .
          target: test
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and Push
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Semantic Versioning

```yaml
- name: Docker meta
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha
```

## Orchestration Best Practices

### Service Dependencies

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
      migrations:
        condition: service_completed_successfully
      cache:
        condition: service_started

  migrations:
    build: .
    command: python manage.py migrate
    depends_on:
      db:
        condition: service_healthy
```

### Network Isolation

```yaml
services:
  nginx:
    networks:
      - frontend

  app:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend

networks:
  frontend:
  backend:
    internal: true  # No external access
```

### Scaling

```yaml
services:
  worker:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 256M
      restart_policy:
        condition: on-failure
        max_attempts: 3
```

```bash
# Scale at runtime
docker-compose up -d --scale worker=5
```

## Monitoring and Observability

### Prometheus Metrics

```yaml
services:
  app:
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8000"
      - "prometheus.path=/metrics"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

### Logging Aggregation

```yaml
services:
  app:
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: app.{{.Name}}

  fluentd:
    image: fluent/fluentd
    volumes:
      - ./fluent.conf:/fluentd/etc/fluent.conf
    ports:
      - "24224:24224"
```

## Cleanup and Maintenance

### Regular Cleanup

```bash
# Remove unused resources
docker system prune -a --volumes

# Remove old images
docker image prune -a --filter "until=720h"  # 30 days

# Scheduled cleanup (cron)
0 2 * * * docker system prune -f --filter "until=168h"
```

### Image Management

```bash
# List images by size
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | sort -k2 -h

# Remove dangling images
docker image prune -f

# Remove specific old tags
docker rmi $(docker images myapp --filter "before=myapp:latest" -q)
```

## Checklist

### Before Production

- [ ] Use minimal base image (slim/alpine/distroless)
- [ ] Multi-stage build for smaller images
- [ ] Non-root user
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Logging to stdout/stderr
- [ ] Graceful shutdown handling
- [ ] Secrets not in image
- [ ] No unnecessary packages
- [ ] .dockerignore configured
- [ ] Image scanned for vulnerabilities
- [ ] Read-only filesystem where possible

### Security Audit

- [ ] Base image updated recently
- [ ] No sensitive data in layers
- [ ] No root processes
- [ ] Network isolation configured
- [ ] Secrets properly managed
- [ ] No unnecessary capabilities
- [ ] SELinux/AppArmor profiles (if applicable)
