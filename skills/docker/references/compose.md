# Docker Compose Reference

Complete guide to orchestrating multi-container applications with Docker Compose.

## File Structure

```yaml
# docker-compose.yml
version: "3.9"  # Optional in Compose v2+

name: myproject  # Project name (optional)

services:
  service1:
    # Service definition
  service2:
    # Service definition

networks:
  network1:
    # Network definition

volumes:
  volume1:
    # Volume definition

configs:
  config1:
    # Config definition

secrets:
  secret1:
    # Secret definition
```

## Service Configuration

### Basic Service

```yaml
services:
  app:
    image: myapp:latest
    container_name: myapp-container
    hostname: myapp
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
```

### Build Configuration

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
      args:
        - BUILD_VERSION=1.0.0
      cache_from:
        - myapp:cache
      labels:
        - "com.example.version=1.0"

    # Or simple build
    build: .

    # Build with specific platforms
    build:
      context: .
      platforms:
        - linux/amd64
        - linux/arm64
```

### Environment Variables

```yaml
services:
  app:
    environment:
      # Key=Value format
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - DEBUG=false
      # From host environment
      - API_KEY

    # Map format
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      DEBUG: "false"

    # From file
    env_file:
      - .env
      - .env.local
```

### Ports

```yaml
services:
  app:
    ports:
      # HOST:CONTAINER
      - "8000:8000"
      # Host IP binding
      - "127.0.0.1:8000:8000"
      # Random host port
      - "8000"
      # Port range
      - "8000-8010:8000-8010"
      # UDP
      - "8000:8000/udp"

    # Expose to other services only (not host)
    expose:
      - "8000"
```

### Volumes

```yaml
services:
  app:
    volumes:
      # Named volume
      - app_data:/app/data

      # Bind mount (absolute path)
      - /host/path:/container/path

      # Bind mount (relative path)
      - ./src:/app/src

      # Read-only
      - ./config:/app/config:ro

      # Anonymous volume
      - /app/temp

      # Long syntax
      - type: volume
        source: app_data
        target: /app/data
        volume:
          nocopy: true

      - type: bind
        source: ./src
        target: /app/src
        bind:
          create_host_path: true

volumes:
  app_data:
    driver: local
```

### Networking

```yaml
services:
  app:
    networks:
      - frontend
      - backend

    # With aliases and IP
    networks:
      frontend:
        aliases:
          - api
          - api.local
      backend:
        ipv4_address: 172.28.0.10

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Dependencies

```yaml
services:
  app:
    depends_on:
      - db
      - cache

    # With condition
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
      migrations:
        condition: service_completed_successfully
```

### Health Checks

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    # Shell command
    healthcheck:
      test: curl -f http://localhost:8000/health || exit 1

    # Disable health check
    healthcheck:
      disable: true
```

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M
```

### Restart Policy

```yaml
services:
  app:
    # Simple restart policy
    restart: always
    # Options: "no", always, on-failure, unless-stopped

    # Deploy restart policy (Swarm mode)
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
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

    # Other drivers: syslog, journald, gelf, fluentd, awslogs
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: myapp
```

## Complete Examples

### Web Application Stack

```yaml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/app
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app

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
    environment:
      - USERS_SERVICE=http://users:8000
      - ORDERS_SERVICE=http://orders:8000
      - PRODUCTS_SERVICE=http://products:8000
    depends_on:
      - users
      - orders
      - products
    networks:
      - public
      - internal

  # User Service
  users:
    build: ./services/users
    environment:
      - DATABASE_URL=postgresql://postgres:pass@users-db:5432/users
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      users-db:
        condition: service_healthy
    networks:
      - internal

  users-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: users
      POSTGRES_PASSWORD: pass
    volumes:
      - users_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - internal

  # Order Service
  orders:
    build: ./services/orders
    environment:
      - DATABASE_URL=postgresql://postgres:pass@orders-db:5432/orders
      - RABBITMQ_URL=amqp://queue:5672
    depends_on:
      orders-db:
        condition: service_healthy
      queue:
        condition: service_healthy
    networks:
      - internal

  orders-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: orders
      POSTGRES_PASSWORD: pass
    volumes:
      - orders_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - internal

  # Product Service
  products:
    build: ./services/products
    environment:
      - DATABASE_URL=postgresql://postgres:pass@products-db:5432/products
    depends_on:
      products-db:
        condition: service_healthy
    networks:
      - internal

  products-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: products
      POSTGRES_PASSWORD: pass
    volumes:
      - products_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - internal

  # Message Queue
  queue:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
    ports:
      - "15672:15672"  # Management UI
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: rabbitmq-diagnostics -q ping
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true

volumes:
  users_data:
  orders_data:
  products_data:
  rabbitmq_data:
```

### AI/ML Development Stack

```yaml
version: "3.9"

services:
  # AI Agent Application
  agent:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://postgres:pass@db:5432/agents
      - VECTOR_DB_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      qdrant:
        condition: service_started
      redis:
        condition: service_started
    volumes:
      - agent_data:/app/data
      - ./prompts:/app/prompts:ro
    ports:
      - "8000:8000"

  # PostgreSQL with pgvector
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: agents
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-pgvector.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage

  # Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # Jupyter Notebook for Development
  jupyter:
    image: jupyter/scipy-notebook:latest
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - agent_data:/home/jovyan/data:ro
    environment:
      - JUPYTER_ENABLE_LAB=yes

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  agent_data:
  postgres_data:
  qdrant_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Development vs Production

```yaml
# docker-compose.yml (base)
version: "3.9"

services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/app

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app

# docker-compose.override.yml (development, auto-loaded)
version: "3.9"

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

  db:
    ports:
      - "5432:5432"

# docker-compose.prod.yml (production)
version: "3.9"

services:
  app:
    build:
      target: production
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M

  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 1G

volumes:
  postgres_data:

# Usage:
# Development: docker-compose up (uses base + override)
# Production: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Commands Reference

### Basic Operations

```bash
# Start services
docker-compose up
docker-compose up -d          # Detached mode
docker-compose up --build     # Rebuild images

# Stop services
docker-compose down
docker-compose down -v        # Remove volumes
docker-compose down --rmi all # Remove images

# Restart
docker-compose restart
docker-compose restart app    # Specific service
```

### Service Management

```bash
# View status
docker-compose ps
docker-compose top

# View logs
docker-compose logs
docker-compose logs -f        # Follow
docker-compose logs -f app db # Specific services
docker-compose logs --tail=100 app

# Execute commands
docker-compose exec app bash
docker-compose exec -T app pytest  # No TTY
docker-compose exec db psql -U postgres

# Run one-off command
docker-compose run --rm app python manage.py migrate
docker-compose run --rm -e DEBUG=true app bash
```

### Scaling and Updates

```bash
# Scale services
docker-compose up -d --scale worker=3

# Update specific service
docker-compose up -d --no-deps app
docker-compose up -d --no-deps --build app

# Pull latest images
docker-compose pull
docker-compose pull app

# Build/rebuild
docker-compose build
docker-compose build --no-cache app
```

### Configuration

```bash
# Validate compose file
docker-compose config

# View resolved config
docker-compose config --services
docker-compose config --volumes

# Use specific file
docker-compose -f docker-compose.prod.yml up

# Use multiple files
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# Use project name
docker-compose -p myproject up
```
