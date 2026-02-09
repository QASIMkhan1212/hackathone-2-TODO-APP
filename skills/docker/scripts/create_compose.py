#!/usr/bin/env python3
"""Generate docker-compose.yml for various application stacks."""

import argparse
from pathlib import Path


def generate_web_stack() -> str:
    """Generate web application stack with app, db, cache."""
    return '''version: "3.9"

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

volumes:
  postgres_data:
  redis_data:
'''


def generate_full_stack() -> str:
    """Generate full-stack with frontend, backend, db."""
    return '''version: "3.9"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/app
      - REDIS_URL=redis://cache:6379
      - CORS_ORIGINS=http://localhost:3000
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./backend/uploads:/app/uploads

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
'''


def generate_microservices() -> str:
    """Generate microservices architecture."""
    return '''version: "3.9"

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
      - "15672:15672"
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
'''


def generate_ai_stack() -> str:
    """Generate AI/ML development stack."""
    return '''version: "3.9"

services:
  # AI Agent Application
  agent:
    build: .
    ports:
      - "8000:8000"
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
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  # Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # Jupyter Notebook
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
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  agent_data:
  postgres_data:
  qdrant_data:
  redis_data:
  prometheus_data:
  grafana_data:
'''


def generate_dev_stack() -> str:
    """Generate development stack with hot reload."""
    return '''version: "3.9"

services:
  app:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
      - "5678:5678"  # Debugger
    environment:
      - DEBUG=true
      - DATABASE_URL=postgresql://postgres:password@db:5432/app
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    command: uvicorn main:app --reload --host 0.0.0.0

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Database admin UI
  adminer:
    image: adminer:latest
    ports:
      - "8080:8080"
    depends_on:
      - db

  # Redis admin UI
  redis-commander:
    image: rediscommander/redis-commander:latest
    environment:
      - REDIS_HOSTS=local:cache:6379
    ports:
      - "8081:8081"
    depends_on:
      - cache

volumes:
  postgres_data:
'''


STACK_GENERATORS = {
    "web": generate_web_stack,
    "fullstack": generate_full_stack,
    "microservices": generate_microservices,
    "ai": generate_ai_stack,
    "dev": generate_dev_stack,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate docker-compose.yml for various stacks"
    )
    parser.add_argument(
        "stack",
        choices=list(STACK_GENERATORS.keys()),
        help="Stack type to generate",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("docker-compose.yml"),
        help="Output file path",
    )

    args = parser.parse_args()

    try:
        compose_content = STACK_GENERATORS[args.stack]()

        args.output.write_text(compose_content, encoding="utf-8")
        print(f"✓ Generated {args.output}")

        # Print usage instructions
        print("\nNext steps:")
        print("  1. Review and customize the configuration")
        print("  2. Create .env file with secrets")
        print("  3. docker-compose up -d")
        print("\nManagement commands:")
        print("  docker-compose ps       # View status")
        print("  docker-compose logs -f  # View logs")
        print("  docker-compose down -v  # Stop and remove")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
