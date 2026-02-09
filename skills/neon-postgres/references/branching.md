# Database Branching Reference

## Overview

Neon branches are instant, copy-on-write copies of your database. They share the same storage until data diverges, making them extremely fast and cost-effective.

## Branch Concepts

```
┌─────────────────────────────────────────────────────┐
│                    main branch                       │
│  ═══════════════════════════════════════════════    │
│                        │                             │
│                   branch point                       │
│                        │                             │
│              ┌─────────┴─────────┐                  │
│              │                   │                   │
│         dev branch          staging branch          │
│     ════════════════      ════════════════          │
│              │                                       │
│         branch point                                 │
│              │                                       │
│     feature/auth branch                             │
│     ════════════════════                            │
└─────────────────────────────────────────────────────┘
```

## Creating Branches

### Via Neon Console

1. Navigate to your project
2. Click "Branches" tab
3. Click "Create Branch"
4. Select parent branch and name

### Via Neon API

```python
import httpx
import os

NEON_API_KEY = os.getenv("NEON_API_KEY")
PROJECT_ID = os.getenv("NEON_PROJECT_ID")
API_BASE = "https://console.neon.tech/api/v2"


async def create_branch(
    name: str,
    parent_id: str | None = None,
    parent_timestamp: str | None = None,
) -> dict:
    """
    Create a new database branch.

    Args:
        name: Branch name
        parent_id: Parent branch ID (default: main)
        parent_timestamp: Point-in-time to branch from (ISO 8601)

    Returns:
        Branch details including connection string
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "branch": {"name": name},
            "endpoints": [{"type": "read_write"}],
        }

        if parent_id:
            payload["branch"]["parent_id"] = parent_id

        if parent_timestamp:
            payload["branch"]["parent_timestamp"] = parent_timestamp

        response = await client.post(
            f"{API_BASE}/projects/{PROJECT_ID}/branches",
            headers={
                "Authorization": f"Bearer {NEON_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def list_branches() -> list[dict]:
    """List all branches in the project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/projects/{PROJECT_ID}/branches",
            headers={"Authorization": f"Bearer {NEON_API_KEY}"},
        )
        response.raise_for_status()
        return response.json()["branches"]


async def get_branch(branch_id: str) -> dict:
    """Get branch details."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/projects/{PROJECT_ID}/branches/{branch_id}",
            headers={"Authorization": f"Bearer {NEON_API_KEY}"},
        )
        response.raise_for_status()
        return response.json()


async def delete_branch(branch_id: str) -> bool:
    """Delete a branch."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_BASE}/projects/{PROJECT_ID}/branches/{branch_id}",
            headers={"Authorization": f"Bearer {NEON_API_KEY}"},
        )
        return response.status_code == 204


async def get_connection_string(branch_id: str) -> str:
    """Get connection string for a branch."""
    branch = await get_branch(branch_id)
    endpoints = branch.get("endpoints", [])
    if endpoints:
        return endpoints[0].get("connection_uri", "")
    return ""
```

### Via Neon CLI

```bash
# Install Neon CLI
npm install -g neonctl

# Authenticate
neonctl auth

# Create branch
neonctl branches create --name feature/user-auth

# Create branch from specific point in time
neonctl branches create --name restore-point --parent main --timestamp "2025-01-15T10:00:00Z"

# List branches
neonctl branches list

# Delete branch
neonctl branches delete feature/user-auth
```

## Development Workflow Patterns

### Feature Branch Pattern

```python
async def feature_branch_workflow(feature_name: str):
    """
    Standard feature branch workflow:
    1. Create branch from main
    2. Develop and test
    3. Apply migrations to main
    4. Delete feature branch
    """
    # Create feature branch
    branch_name = f"feature/{feature_name}"
    result = await create_branch(branch_name)
    branch_id = result["branch"]["id"]
    conn_string = result["connection_uris"][0]["connection_uri"]

    print(f"Created branch: {branch_name}")
    print(f"Connection: {conn_string}")

    # Developer works on this branch...
    # Run migrations, test changes, etc.

    return {
        "branch_id": branch_id,
        "branch_name": branch_name,
        "connection_string": conn_string,
    }


async def cleanup_feature_branch(branch_id: str):
    """Clean up after feature is merged."""
    await delete_branch(branch_id)
    print(f"Deleted branch: {branch_id}")
```

### Preview Environment Pattern

```python
async def create_preview_environment(pr_number: int) -> dict:
    """
    Create isolated database for PR preview.
    Useful for Vercel/Netlify preview deployments.
    """
    branch_name = f"preview/pr-{pr_number}"

    # Create branch from main
    result = await create_branch(branch_name)

    return {
        "branch_id": result["branch"]["id"],
        "database_url": result["connection_uris"][0]["connection_uri"],
        "pooled_url": result["connection_uris"][0]["connection_uri"].replace(
            ".neon.tech", "-pooler.neon.tech"
        ),
    }


async def cleanup_preview_environment(pr_number: int):
    """Delete preview branch when PR is closed."""
    branches = await list_branches()
    for branch in branches:
        if branch["name"] == f"preview/pr-{pr_number}":
            await delete_branch(branch["id"])
            break
```

### Testing Pattern

```python
import pytest
import asyncio

@pytest.fixture
async def test_branch():
    """Create isolated branch for testing."""
    import uuid
    branch_name = f"test/{uuid.uuid4().hex[:8]}"

    result = await create_branch(branch_name)
    branch_id = result["branch"]["id"]
    conn_string = result["connection_uris"][0]["connection_uri"]

    yield conn_string

    # Cleanup after tests
    await delete_branch(branch_id)


@pytest.mark.asyncio
async def test_user_creation(test_branch):
    """Test runs against isolated branch."""
    engine = create_async_engine(test_branch)
    # Run tests...
```

### Point-in-Time Recovery

```python
async def restore_to_point_in_time(
    timestamp: str,
    branch_name: str = "restore-branch"
) -> dict:
    """
    Create branch from specific point in time.

    Args:
        timestamp: ISO 8601 timestamp (e.g., "2025-01-15T10:30:00Z")
        branch_name: Name for the restore branch

    Returns:
        Branch details with connection string
    """
    # Get main branch ID
    branches = await list_branches()
    main_branch = next(b for b in branches if b["name"] == "main")

    # Create branch at specific timestamp
    result = await create_branch(
        name=branch_name,
        parent_id=main_branch["id"],
        parent_timestamp=timestamp,
    )

    return result
```

## Branch Naming Conventions

```
main                    # Production database
├── staging            # Pre-production testing
├── dev                # Development integration
├── feature/*          # Feature branches
│   ├── feature/user-auth
│   ├── feature/payments
│   └── feature/notifications
├── preview/*          # PR preview environments
│   ├── preview/pr-123
│   └── preview/pr-456
├── test/*             # Automated test branches
│   └── test/abc123
└── restore/*          # Point-in-time restore branches
    └── restore/2025-01-15
```

## Best Practices

1. **Short-lived branches**: Delete branches when done to save resources
2. **Naming conventions**: Use prefixes for branch types
3. **Automate cleanup**: Set up CI/CD to clean up preview branches
4. **Branch from latest**: Create branches from recent parent state
5. **Limit active branches**: Too many branches increase storage costs
6. **Use for testing**: Create fresh branches for test isolation

## Branch Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Create  │ ──► │  Develop │ ──► │  Merge   │ ──► │  Delete  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     ▼                ▼                ▼                ▼
  Instant         Isolated         Migrations       Resources
  copy-on-       changes only      applied to       freed
  write          in branch         parent
```
