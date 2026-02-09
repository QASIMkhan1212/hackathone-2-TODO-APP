# Connection Pooling Reference

## Overview

Neon provides built-in connection pooling via PgBouncer, essential for serverless applications that create many short-lived connections.

## Connection Types

### Direct Connection

```
postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Use for:**
- Long-running applications (traditional servers)
- Applications managing their own connection pool
- Operations requiring session-level features (prepared statements, advisory locks)

### Pooled Connection

```
postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
```

**Use for:**
- Serverless functions (AWS Lambda, Vercel, Cloudflare Workers)
- Edge functions
- Applications with many short-lived connections
- High concurrency scenarios

## Connection String Patterns

```python
import os

# Get base URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Convert to pooled URL
def get_pooled_url(url: str) -> str:
    """Convert direct URL to pooled URL."""
    return url.replace(".neon.tech", "-pooler.neon.tech")

# Convert to direct URL
def get_direct_url(url: str) -> str:
    """Convert pooled URL to direct URL."""
    return url.replace("-pooler.neon.tech", ".neon.tech")

# Usage
DIRECT_URL = DATABASE_URL
POOLED_URL = get_pooled_url(DATABASE_URL)
```

## SQLAlchemy Configuration

### For Serverless (Recommended)

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Use NullPool - let Neon handle pooling
engine = create_async_engine(
    POOLED_URL,
    poolclass=NullPool,
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
```

### For Traditional Applications

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Use SQLAlchemy pooling with direct connection
engine = create_async_engine(
    DIRECT_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
```

## Pooling Modes

Neon's PgBouncer supports different pooling modes:

### Transaction Mode (Default)

```
# Connection string with explicit mode
postgresql://user:password@ep-xxx-pooler.neon.tech/dbname?pgbouncer=true
```

- Connection assigned per transaction
- Best for most serverless use cases
- Cannot use prepared statements
- Cannot use session-level features

### Session Mode

```python
# For session-level features, use direct connection
engine = create_async_engine(
    DIRECT_URL,  # Not pooled
    poolclass=NullPool,
)
```

## Framework Integration

### FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

@app.get("/users")
async def get_users(session: AsyncSession = Depends(get_session)):
    # Use session...
    pass
```

### Next.js (Edge Runtime)

```typescript
// lib/db.ts
import { neon } from '@neondatabase/serverless';

// For edge runtime - use HTTP driver
export const sql = neon(process.env.DATABASE_URL!);

// Usage in API route
export async function GET() {
  const users = await sql`SELECT * FROM users LIMIT 10`;
  return Response.json(users);
}
```

```typescript
// For Node.js runtime - use pooled connection
import { Pool } from '@neondatabase/serverless';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export async function getUsers() {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT * FROM users');
    return result.rows;
  } finally {
    client.release();
  }
}
```

### AWS Lambda

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Create engine outside handler for connection reuse
engine = create_async_engine(
    os.environ["DATABASE_URL"],  # Use pooled URL
    poolclass=NullPool,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def handler(event, context):
    async with async_session() as session:
        # Handle request
        result = await session.execute(...)
        return {"statusCode": 200, "body": json.dumps(result)}
```

### Vercel Serverless

```python
# api/users.py
from http.server import BaseHTTPRequestHandler
import asyncio
from db import async_session

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = asyncio.run(self.get_users())
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    async def get_users(self):
        async with async_session() as session:
            users = await session.execute(select(User))
            return [u.dict() for u in users.scalars()]
```

## Connection Limits

### Neon Free Tier
- Direct connections: 1 (max 5 with autoscaling)
- Pooled connections: 10,000+

### Neon Pro Tier
- Direct connections: Up to 1000 (configurable)
- Pooled connections: Virtually unlimited

## Handling Connection Errors

```python
from sqlalchemy.exc import OperationalError, InterfaceError
import asyncio

async def execute_with_retry(
    session: AsyncSession,
    statement,
    max_retries: int = 3,
    retry_delay: float = 0.5,
):
    """Execute statement with connection retry."""
    for attempt in range(max_retries):
        try:
            result = await session.execute(statement)
            return result
        except (OperationalError, InterfaceError) as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay * (attempt + 1))
            # Rollback and get fresh connection
            await session.rollback()
```

## Cold Start Optimization

```python
# Warm up connection on module load
async def warmup_connection():
    """Pre-warm database connection."""
    async with async_session() as session:
        await session.execute(text("SELECT 1"))

# Call during application startup
# asyncio.create_task(warmup_connection())
```

## Best Practices

1. **Always use pooled URL for serverless**: Prevents connection exhaustion
2. **Use NullPool with pooled connections**: Let Neon manage pooling
3. **Set reasonable timeouts**: Prevent hanging connections
4. **Handle reconnection**: Implement retry logic
5. **Close sessions properly**: Use context managers
6. **Monitor connections**: Track active connection count
7. **Use connection string from environment**: Never hardcode credentials

## Environment Variables

```bash
# Direct connection (for migrations, long-running processes)
DATABASE_URL_DIRECT=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

# Pooled connection (for application)
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.neon.tech/db?sslmode=require

# Alternative: Single URL with runtime conversion
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
# Application converts to pooler URL as needed
```

## Troubleshooting

### "Too many connections"

```python
# Solution: Use pooled connection with NullPool
engine = create_async_engine(POOLED_URL, poolclass=NullPool)
```

### "Connection reset by peer"

```python
# Solution: Enable pre_ping
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Validates connections before use
)
```

### Slow cold starts

```python
# Solution: Keep connection warm or use HTTP driver
from neon import neon
sql = neon(DATABASE_URL)  # HTTP-based, no connection overhead
```
