# Docker Volumes Reference

Complete guide to Docker volumes for persistent data storage.

## Volume Types

### Named Volumes

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
    driver: local
```

### Bind Mounts

```yaml
services:
  app:
    volumes:
      # Relative path (from compose file location)
      - ./src:/app/src

      # Absolute path
      - /host/data:/container/data

      # Read-only
      - ./config:/app/config:ro
```

### Anonymous Volumes

```yaml
services:
  app:
    volumes:
      - /app/temp  # Anonymous volume
```

### tmpfs Mounts

```yaml
services:
  app:
    tmpfs:
      - /tmp
      - /run:size=100M,mode=0755
```

## Volume Configuration

### Named Volume Options

```yaml
volumes:
  # Basic
  mydata:
    driver: local

  # With options
  mydata:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/on/host
    labels:
      - "backup=daily"
      - "environment=production"

  # External (pre-existing)
  external_data:
    external: true
    name: my-existing-volume
```

### Long Syntax

```yaml
services:
  app:
    volumes:
      # Named volume
      - type: volume
        source: mydata
        target: /data
        volume:
          nocopy: true  # Don't copy container data to volume

      # Bind mount
      - type: bind
        source: ./src
        target: /app/src
        bind:
          create_host_path: true  # Create if doesn't exist
          selinux: z  # SELinux label

      # tmpfs
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 100M
          mode: 0755
```

## Common Patterns

### Database Persistence

```yaml
services:
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      POSTGRES_PASSWORD: secret

  mysql:
    image: mysql:8
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql.conf:/etc/mysql/conf.d/custom.cnf:ro

  mongodb:
    image: mongo:7
    volumes:
      - mongo_data:/data/db
      - mongo_config:/data/configdb

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  mysql_data:
  mongo_data:
  mongo_config:
  redis_data:
```

### Development Hot Reload

```yaml
services:
  # Node.js
  node-app:
    build: .
    volumes:
      - ./src:/app/src
      - ./package.json:/app/package.json
      - node_modules:/app/node_modules  # Preserve installed modules
    command: npm run dev

  # Python
  python-app:
    build: .
    volumes:
      - ./src:/app/src
      - ./requirements.txt:/app/requirements.txt
    command: python -m uvicorn main:app --reload --host 0.0.0.0

  # Go (with Air for hot reload)
  go-app:
    build: .
    volumes:
      - ./:/app
      - go_cache:/go/pkg/mod
    command: air

volumes:
  node_modules:
  go_cache:
```

### Configuration Files

```yaml
services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
      - ./html:/usr/share/nginx/html:ro

  app:
    build: .
    volumes:
      - ./config:/app/config:ro
      - ./.env:/app/.env:ro
```

### Log Persistence

```yaml
services:
  app:
    build: .
    volumes:
      - app_logs:/var/log/app

  # Log aggregator
  fluentd:
    image: fluent/fluentd:v1.16
    volumes:
      - app_logs:/var/log/app:ro
      - ./fluent.conf:/fluentd/etc/fluent.conf:ro

volumes:
  app_logs:
```

### Shared Data Between Services

```yaml
services:
  producer:
    build: ./producer
    volumes:
      - shared_data:/data

  consumer:
    build: ./consumer
    volumes:
      - shared_data:/data:ro  # Read-only access
    depends_on:
      - producer

volumes:
  shared_data:
```

### Upload/Media Storage

```yaml
services:
  app:
    build: .
    volumes:
      - uploads:/app/uploads
      - media:/app/media

  # Media processing
  imagemagick:
    image: dpokidov/imagemagick
    volumes:
      - uploads:/input:ro
      - media:/output

  # CDN/Static file server
  nginx:
    image: nginx:alpine
    volumes:
      - media:/usr/share/nginx/html/media:ro
    ports:
      - "8080:80"

volumes:
  uploads:
  media:
```

## Backup and Restore

### Manual Backup

```bash
# Backup volume to tar
docker run --rm \
  -v myvolume:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/myvolume-backup.tar.gz -C /data .

# Restore from tar
docker run --rm \
  -v myvolume:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/myvolume-backup.tar.gz"
```

### Backup Service

```yaml
services:
  backup:
    image: alpine
    volumes:
      - postgres_data:/data/postgres:ro
      - redis_data:/data/redis:ro
      - ./backups:/backups
    command: >
      sh -c "
        tar czf /backups/postgres-$$(date +%Y%m%d).tar.gz -C /data/postgres . &&
        tar czf /backups/redis-$$(date +%Y%m%d).tar.gz -C /data/redis .
      "
    profiles:
      - backup  # Only run with: docker-compose --profile backup run backup

volumes:
  postgres_data:
  redis_data:
```

## Volume Commands

### Manage Volumes

```bash
# List volumes
docker volume ls

# Create volume
docker volume create myvolume

# Inspect volume
docker volume inspect myvolume

# Remove volume
docker volume rm myvolume

# Remove unused volumes
docker volume prune

# Remove all unused volumes (including named)
docker volume prune -a
```

### Copy Data

```bash
# Copy from container to host
docker cp container:/path/to/file ./local/path

# Copy from host to container
docker cp ./local/file container:/path/to/destination

# Copy entire directory
docker cp container:/app/data ./backup/
```

### View Volume Contents

```bash
# Interactive shell
docker run -it --rm -v myvolume:/data alpine sh

# List contents
docker run --rm -v myvolume:/data alpine ls -la /data

# View file
docker run --rm -v myvolume:/data alpine cat /data/config.json
```

## Performance Optimization

### macOS Performance (Docker Desktop)

```yaml
services:
  app:
    volumes:
      # Delegated: container's view is authoritative
      - ./src:/app/src:delegated

      # Cached: host's view is authoritative (better read perf)
      - ./node_modules:/app/node_modules:cached

      # Consistent: perfect sync (default, slowest)
      - ./config:/app/config:consistent
```

### Exclude Unnecessary Files

```yaml
services:
  app:
    volumes:
      - ./:/app
      - /app/node_modules     # Anonymous volume over bind mount
      - /app/.git             # Exclude .git
      - /app/dist             # Exclude build output
```

### Volume Driver Options

```yaml
volumes:
  # NFS mount
  nfs_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.1.100,rw,nfsvers=4
      device: ":/path/to/share"

  # CIFS/SMB mount
  smb_data:
    driver: local
    driver_opts:
      type: cifs
      o: username=user,password=pass,vers=3.0
      device: "//server/share"
```

## Security Best Practices

### Read-Only Mounts

```yaml
services:
  app:
    volumes:
      - ./config:/app/config:ro
      - ./secrets:/app/secrets:ro
    read_only: true  # Entire container filesystem read-only
    tmpfs:
      - /tmp  # Writable temp directory
```

### Minimal Permissions

```yaml
services:
  app:
    volumes:
      - type: bind
        source: ./data
        target: /data
        bind:
          selinux: z  # Shared label
          # selinux: Z  # Private label
```

### Secrets Management

```yaml
services:
  app:
    secrets:
      - db_password
      - api_key
    # Secrets mounted at /run/secrets/<secret_name>

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    external: true
    name: my_api_key
```

## Troubleshooting

### Permission Issues

```bash
# Check volume permissions
docker run --rm -v myvolume:/data alpine ls -la /data

# Fix ownership
docker run --rm -v myvolume:/data alpine chown -R 1000:1000 /data

# Run as specific user
docker run --rm -u 1000:1000 -v myvolume:/data alpine touch /data/test
```

### Volume Not Updating

```bash
# Force recreate containers
docker-compose up -d --force-recreate

# Remove and recreate volumes
docker-compose down -v
docker-compose up -d
```

### Disk Space

```bash
# Check Docker disk usage
docker system df
docker system df -v

# Clean up
docker system prune -a --volumes
```
