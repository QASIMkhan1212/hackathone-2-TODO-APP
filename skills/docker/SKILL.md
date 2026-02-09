---
name: docker
description: Docker containerization for modern application development and deployment. Use when users want to (1) create Dockerfiles for applications, (2) set up docker-compose for multi-service apps, (3) optimize container images, (4) configure networking and volumes, (5) implement CI/CD with containers, (6) deploy microservices, (7) containerize AI/ML workloads. Triggers on mentions of "docker", "container", "dockerfile", "docker-compose", "containerize", or deployment/DevOps tasks.
---

# Docker

Containerization platform for building, shipping, and running applications consistently across any environment.

## When to Use This Skill

- Creating Dockerfiles for any application
- Setting up multi-container applications with Docker Compose
- Optimizing container images for production
- Configuring container networking and storage
- Implementing CI/CD pipelines with containers
- Deploying microservices architectures
- Containerizing AI/ML and agent workloads

## Core Concepts

### Container vs VM

```
┌─────────────────────────────────────────────────────────┐
│  Containers (Lightweight)     │  VMs (Heavy)            │
├───────────────────────────────┼─────────────────────────┤
│  Share host OS kernel         │  Full OS per instance   │
│  MBs in size                  │  GBs in size            │
│  Start in seconds             │  Start in minutes       │
│  100s per host                │  10s per host           │
│  Process-level isolation      │  Hardware-level         │
└───────────────────────────────┴─────────────────────────┘
```

### Docker Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Client                        │
│              (docker build, run, push)                  │
└─────────────────────────┬───────────────────────────────┘
                          │ REST API
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     Docker Daemon                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Containers │  │   Images    │  │  Networks   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐  ┌─────────────┐                     │
│  │   Volumes   │  │   Plugins   │                     │
│  └─────────────┘  └─────────────┘                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Container Registry                     │
│        (Docker Hub, ECR, GCR, GHCR, ACR)               │
└─────────────────────────────────────────────────────────┘
```

## Dockerfile Basics

### Simple Python Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["python", "main.py"]
```

### Node.js Application

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Build if needed
RUN npm run build

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Multi-Stage Build (Production)

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Install dependencies from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

## Docker Compose

### Basic Web Application Stack

```yaml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./src:/app/src  # Development hot-reload
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Microservices Architecture

```yaml
version: "3.9"

services:
  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "80:80"
    depends_on:
      - users
      - orders
      - products

  # User Service
  users:
    build: ./services/users
    environment:
      - DATABASE_URL=postgresql://postgres:pass@users-db:5432/users
    depends_on:
      - users-db

  users-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: users
      POSTGRES_PASSWORD: pass
    volumes:
      - users_data:/var/lib/postgresql/data

  # Order Service
  orders:
    build: ./services/orders
    environment:
      - DATABASE_URL=postgresql://postgres:pass@orders-db:5432/orders
      - RABBITMQ_URL=amqp://queue:5672
    depends_on:
      - orders-db
      - queue

  orders-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: orders
      POSTGRES_PASSWORD: pass
    volumes:
      - orders_data:/var/lib/postgresql/data

  # Product Service
  products:
    build: ./services/products
    environment:
      - DATABASE_URL=postgresql://postgres:pass@products-db:5432/products
    depends_on:
      - products-db

  products-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: products
      POSTGRES_PASSWORD: pass
    volumes:
      - products_data:/var/lib/postgresql/data

  # Message Queue
  queue:
    image: rabbitmq:3-management-alpine
    ports:
      - "15672:15672"  # Management UI

volumes:
  users_data:
  orders_data:
  products_data:
```

### AI/ML Stack

```yaml
version: "3.9"

services:
  # AI Agent
  agent:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:pass@db:5432/agents
      - VECTOR_DB_URL=http://vector-db:6333
    depends_on:
      - db
      - vector-db
    volumes:
      - agent_data:/app/data

  # PostgreSQL with pgvector
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: agents
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Vector Database (Qdrant)
  vector-db:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  # MCP Server
  mcp-server:
    build: ./mcp
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/agents

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  agent_data:
  postgres_data:
  qdrant_data:
  grafana_data:
```

## Essential Commands

### Images

```bash
# Build image
docker build -t myapp:latest .
docker build -t myapp:v1.0 -f Dockerfile.prod .

# List images
docker images

# Remove image
docker rmi myapp:latest

# Tag image
docker tag myapp:latest myregistry/myapp:v1.0

# Push to registry
docker push myregistry/myapp:v1.0

# Pull from registry
docker pull postgres:16-alpine
```

### Containers

```bash
# Run container
docker run -d --name myapp -p 8000:8000 myapp:latest

# Run with environment variables
docker run -d --env-file .env myapp:latest

# Run with volume mount
docker run -d -v $(pwd)/data:/app/data myapp:latest

# List containers
docker ps        # Running
docker ps -a     # All

# Stop/Start/Restart
docker stop myapp
docker start myapp
docker restart myapp

# Remove container
docker rm myapp
docker rm -f myapp  # Force

# View logs
docker logs myapp
docker logs -f myapp  # Follow

# Execute command in container
docker exec -it myapp bash
docker exec myapp python manage.py migrate

# Copy files
docker cp myapp:/app/data ./backup
docker cp ./config myapp:/app/config
```

### Docker Compose

```bash
# Start services
docker-compose up
docker-compose up -d          # Detached
docker-compose up --build     # Rebuild images

# Stop services
docker-compose down
docker-compose down -v        # Remove volumes

# View logs
docker-compose logs
docker-compose logs -f app    # Follow specific service

# Scale services
docker-compose up -d --scale worker=3

# Execute command
docker-compose exec app bash
docker-compose exec db psql -U postgres

# Rebuild single service
docker-compose build app
docker-compose up -d --no-deps app
```

### Cleanup

```bash
# Remove unused resources
docker system prune           # Unused containers, networks, images
docker system prune -a        # All unused images
docker volume prune           # Unused volumes

# Remove all containers
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -q)
```

## Networking

### Network Types

```yaml
services:
  app:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

### Exposing Ports

```yaml
services:
  app:
    ports:
      - "8000:8000"           # host:container
      - "127.0.0.1:8000:8000" # localhost only
      - "8000"                # Random host port
```

## Volumes

### Volume Types

```yaml
services:
  app:
    volumes:
      # Named volume (persistent)
      - app_data:/app/data

      # Bind mount (development)
      - ./src:/app/src

      # Read-only bind mount
      - ./config:/app/config:ro

      # Anonymous volume
      - /app/temp

volumes:
  app_data:
    driver: local
```

## Health Checks

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

```yaml
# In docker-compose.yml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Environment Variables

### Using .env File

```bash
# .env
POSTGRES_PASSWORD=secretpassword
API_KEY=your-api-key
DEBUG=false
```

```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:${POSTGRES_PASSWORD}@db:5432/app
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            user/app:latest
            user/app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### GitLab CI

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  script:
    - pytest tests/

deploy:
  stage: deploy
  script:
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
```

## Best Practices

### 1. Use Multi-Stage Builds

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 2. Non-Root User

```dockerfile
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

USER appuser
```

### 3. Layer Caching

```dockerfile
# Good: Dependencies change less often
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Bad: Invalidates cache on any change
COPY . .
RUN npm ci
```

### 4. .dockerignore

```
# .dockerignore
.git
.gitignore
.env
.env.*
node_modules
__pycache__
*.pyc
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
.venv
venv
.idea
.vscode
*.md
!README.md
Dockerfile*
docker-compose*
```

### 5. Security Scanning

```bash
# Scan for vulnerabilities
docker scout cve myapp:latest
docker scout quickview myapp:latest
```

## References

- See `references/dockerfile.md` for Dockerfile patterns
- See `references/compose.md` for Docker Compose patterns
- See `references/networking.md` for network configuration
- See `references/volumes.md` for storage patterns
- See `references/best-practices.md` for optimization tips

## Scripts

- `scripts/create_dockerfile.py` - Generate Dockerfile
- `scripts/create_compose.py` - Generate docker-compose.yml
- `scripts/setup_docker.py` - Set up Docker project

## Assets

- `assets/python.Dockerfile` - Python application template
- `assets/node.Dockerfile` - Node.js application template
- `assets/fastapi.Dockerfile` - FastAPI optimized template
- `assets/docker-compose.yml` - Full-stack template
- `assets/.dockerignore` - Standard ignore file
