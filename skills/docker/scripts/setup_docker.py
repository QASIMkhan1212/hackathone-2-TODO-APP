#!/usr/bin/env python3
"""Set up Docker project structure with all necessary files."""

import argparse
from pathlib import Path


def generate_gitignore() -> str:
    """Generate .gitignore for Docker project."""
    return '''# Environment
.env
.env.local
.env.*.local

# Docker volumes
data/
volumes/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Build artifacts
dist/
build/
*.egg-info/
'''


def generate_dockerignore() -> str:
    """Generate .dockerignore."""
    return '''# Git
.git
.gitignore
.gitattributes

# Environment
.env
.env.*
!.env.example

# Docker
Dockerfile*
docker-compose*
.dockerignore

# IDE
.idea
.vscode
*.swp
*.swo

# Documentation
*.md
!README.md
docs/

# Tests
tests/
test/
__tests__/
*.test.*
*.spec.*
.pytest_cache/
coverage/
.coverage

# CI/CD
.github/
.gitlab-ci.yml
.circleci/

# Logs
logs/
*.log

# Dependencies
node_modules/
__pycache__/
*.pyc
.mypy_cache/
.ruff_cache/

# Build artifacts
dist/
build/
*.egg-info/
target/
'''


def generate_env_example() -> str:
    """Generate .env.example."""
    return '''# Application
APP_NAME=myapp
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://postgres:password@db:5432/app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=app

# Cache
REDIS_URL=redis://cache:6379

# API Keys (if needed)
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here

# External Services (if needed)
# EXTERNAL_API_URL=https://api.example.com
# EXTERNAL_API_KEY=your-key-here
'''


def generate_makefile() -> str:
    """Generate Makefile for common Docker commands."""
    return '''# Docker commands for development

.PHONY: help build up down restart logs shell test clean

help:
\t@echo "Available commands:"
\t@echo "  make build    - Build Docker images"
\t@echo "  make up       - Start services"
\t@echo "  make down     - Stop services"
\t@echo "  make restart  - Restart services"
\t@echo "  make logs     - View logs"
\t@echo "  make shell    - Open shell in app container"
\t@echo "  make test     - Run tests"
\t@echo "  make clean    - Remove containers and volumes"

build:
\tdocker-compose build

up:
\tdocker-compose up -d

down:
\tdocker-compose down

restart:
\tdocker-compose restart

logs:
\tdocker-compose logs -f

shell:
\tdocker-compose exec app sh

test:
\tdocker-compose exec app pytest

clean:
\tdocker-compose down -v
\tdocker system prune -f
'''


def generate_readme(project_name: str, language: str) -> str:
    """Generate README.md."""
    return f'''# {project_name}

Docker-based application using {language}.

## Prerequisites

- Docker 24+
- Docker Compose v2+

## Quick Start

1. Copy environment file:
```bash
cp .env.example .env
```

2. Start services:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

4. Stop services:
```bash
docker-compose down
```

## Development

### Hot Reload

Source code is mounted as a volume for hot reload:
```bash
docker-compose up
```

### Run Tests

```bash
docker-compose exec app pytest
```

### Database Migrations

```bash
docker-compose exec app python manage.py migrate
```

### Access Container Shell

```bash
docker-compose exec app sh
```

## Production

Build production image:
```bash
docker build -t {project_name}:latest .
```

Run production:
```bash
docker run -p 8000:8000 --env-file .env {project_name}:latest
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| app | 8000 | Application server |
| db | 5432 | PostgreSQL database |
| cache | 6379 | Redis cache |

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :8000
# Or change port in docker-compose.yml
```

### Permission issues
```bash
# Fix ownership
sudo chown -R $USER:$USER .
```

### Rebuild from scratch
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```
'''


def generate_health_check_script() -> str:
    """Generate health check script."""
    return '''#!/bin/sh
# Health check script

set -e

# Check if service is responding
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Service is healthy"
    exit 0
else
    echo "✗ Service is unhealthy"
    exit 1
fi
'''


def generate_entrypoint_script(language: str) -> str:
    """Generate entrypoint script."""
    if language == "python":
        return '''#!/bin/sh
# Entrypoint script for Python application

set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 1
done
echo "Database is ready!"

# Run migrations (if applicable)
# python manage.py migrate

# Execute command
exec "$@"
'''
    elif language in ["node", "javascript"]:
        return '''#!/bin/sh
# Entrypoint script for Node.js application

set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 1
done
echo "Database is ready!"

# Run migrations (if applicable)
# npm run migrate

# Execute command
exec "$@"
'''
    else:
        return '''#!/bin/sh
# Entrypoint script

set -e

# Wait for dependencies
echo "Waiting for services..."
sleep 2

# Execute command
exec "$@"
'''


def setup_docker_project(
    output_path: Path,
    project_name: str,
    language: str,
) -> None:
    """Set up Docker project structure."""
    print(f"Setting up Docker project: {project_name}")
    print("=" * 50)

    # Create directories
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "scripts").mkdir(exist_ok=True)

    # Generate files
    files = [
        (output_path / ".gitignore", generate_gitignore()),
        (output_path / ".dockerignore", generate_dockerignore()),
        (output_path / ".env.example", generate_env_example()),
        (output_path / "Makefile", generate_makefile()),
        (output_path / "README.md", generate_readme(project_name, language)),
        (output_path / "scripts" / "health_check.sh", generate_health_check_script()),
        (output_path / "scripts" / "entrypoint.sh", generate_entrypoint_script(language)),
    ]

    for file_path, content in files:
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created: {file_path}")

    # Make scripts executable
    (output_path / "scripts" / "health_check.sh").chmod(0o755)
    (output_path / "scripts" / "entrypoint.sh").chmod(0o755)

    print("\n" + "=" * 50)
    print("Docker project setup complete!")
    print("\nNext steps:")
    print(f"  1. cd {output_path}")
    print(f"  2. Generate Dockerfile: python scripts/create_dockerfile.py {language}")
    print("  3. Generate docker-compose: python scripts/create_compose.py web")
    print("  4. cp .env.example .env")
    print("  5. docker-compose up -d")
    print("\nUseful commands:")
    print("  make help  - View all available commands")


def main():
    parser = argparse.ArgumentParser(
        description="Set up Docker project structure"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "language",
        choices=["python", "node", "javascript", "go", "rust"],
        help="Primary language",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory (default: ./<name>)",
    )

    args = parser.parse_args()
    output_path = args.output or Path(args.name.lower().replace(" ", "-"))

    setup_docker_project(output_path, args.name, args.language)


if __name__ == "__main__":
    exit(main())
