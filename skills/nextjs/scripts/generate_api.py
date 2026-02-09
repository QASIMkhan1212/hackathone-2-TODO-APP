#!/usr/bin/env python3
"""Generate Next.js API route with CRUD operations."""

import argparse
from pathlib import Path


def generate_api_route(
    resource: str,
    base_path: Path,
    with_auth: bool = False,
    with_validation: bool = False,
) -> None:
    """Generate API route files for a resource."""

    app_path = base_path / "app"
    if not app_path.exists():
        print(f"Error: 'app' directory not found at {base_path}")
        return

    # Create API directory
    api_path = app_path / "api" / resource
    api_path.mkdir(parents=True, exist_ok=True)
    print(f"Created: {api_path}")

    # Singular form for model name
    model_name = resource.rstrip("s").capitalize()

    # Imports
    imports = ["import { NextRequest, NextResponse } from 'next/server';"]
    imports.append("import { db } from '@/lib/db';")

    if with_auth:
        imports.append("import { getServerSession } from 'next-auth';")
        imports.append("import { authOptions } from '@/lib/auth';")

    if with_validation:
        imports.append("import { z } from 'zod';")

    imports_str = "\n".join(imports)

    # Validation schema
    validation_schema = ""
    if with_validation:
        validation_schema = f'''
const {model_name}Schema = z.object({{
  // Define your schema fields here
  name: z.string().min(1).max(100),
  // Add more fields as needed
}});
'''

    # Auth check helper
    auth_check = ""
    if with_auth:
        auth_check = '''
  const session = await getServerSession(authOptions);
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
'''

    # Collection route (GET all, POST create)
    collection_route = f'''{imports_str}
{validation_schema}
// GET /api/{resource} - List all
export async function GET(request: NextRequest) {{{auth_check}
  try {{
    const {{ searchParams }} = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    const skip = (page - 1) * limit;

    const [{resource}, total] = await Promise.all([
      db.{resource.rstrip("s")}.findMany({{
        skip,
        take: limit,
        orderBy: {{ createdAt: 'desc' }},
      }}),
      db.{resource.rstrip("s")}.count(),
    ]);

    return NextResponse.json({{
      data: {resource},
      pagination: {{
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      }},
    }});
  }} catch (error) {{
    console.error('GET /{resource} error:', error);
    return NextResponse.json(
      {{ error: 'Failed to fetch {resource}' }},
      {{ status: 500 }}
    );
  }}
}}

// POST /api/{resource} - Create new
export async function POST(request: NextRequest) {{{auth_check}
  try {{
    const body = await request.json();
'''

    if with_validation:
        collection_route += f'''
    const result = {model_name}Schema.safeParse(body);
    if (!result.success) {{
      return NextResponse.json(
        {{ errors: result.error.flatten() }},
        {{ status: 400 }}
      );
    }}

    const {resource.rstrip("s")} = await db.{resource.rstrip("s")}.create({{
      data: result.data,
    }});
'''
    else:
        collection_route += f'''
    const {resource.rstrip("s")} = await db.{resource.rstrip("s")}.create({{
      data: body,
    }});
'''

    collection_route += f'''
    return NextResponse.json({resource.rstrip("s")}, {{ status: 201 }});
  }} catch (error) {{
    console.error('POST /{resource} error:', error);
    return NextResponse.json(
      {{ error: 'Failed to create {resource.rstrip("s")}' }},
      {{ status: 400 }}
    );
  }}
}}
'''

    collection_file = api_path / "route.ts"
    collection_file.write_text(collection_route)
    print(f"Created: {collection_file}")

    # Single resource route (GET one, PUT update, DELETE)
    single_path = api_path / "[id]"
    single_path.mkdir(exist_ok=True)

    single_route = f'''{imports_str}
{validation_schema}
type Params = {{ params: {{ id: string }} }};

// GET /api/{resource}/:id - Get single
export async function GET(
  request: NextRequest,
  {{ params }}: Params
) {{{auth_check}
  try {{
    const {resource.rstrip("s")} = await db.{resource.rstrip("s")}.findUnique({{
      where: {{ id: params.id }},
    }});

    if (!{resource.rstrip("s")}) {{
      return NextResponse.json(
        {{ error: '{model_name} not found' }},
        {{ status: 404 }}
      );
    }}

    return NextResponse.json({resource.rstrip("s")});
  }} catch (error) {{
    console.error('GET /{resource}/[id] error:', error);
    return NextResponse.json(
      {{ error: 'Failed to fetch {resource.rstrip("s")}' }},
      {{ status: 500 }}
    );
  }}
}}

// PUT /api/{resource}/:id - Update
export async function PUT(
  request: NextRequest,
  {{ params }}: Params
) {{{auth_check}
  try {{
    const body = await request.json();
'''

    if with_validation:
        single_route += f'''
    const result = {model_name}Schema.partial().safeParse(body);
    if (!result.success) {{
      return NextResponse.json(
        {{ errors: result.error.flatten() }},
        {{ status: 400 }}
      );
    }}

    const {resource.rstrip("s")} = await db.{resource.rstrip("s")}.update({{
      where: {{ id: params.id }},
      data: result.data,
    }});
'''
    else:
        single_route += f'''
    const {resource.rstrip("s")} = await db.{resource.rstrip("s")}.update({{
      where: {{ id: params.id }},
      data: body,
    }});
'''

    single_route += f'''
    return NextResponse.json({resource.rstrip("s")});
  }} catch (error) {{
    console.error('PUT /{resource}/[id] error:', error);
    return NextResponse.json(
      {{ error: 'Failed to update {resource.rstrip("s")}' }},
      {{ status: 400 }}
    );
  }}
}}

// DELETE /api/{resource}/:id - Delete
export async function DELETE(
  request: NextRequest,
  {{ params }}: Params
) {{{auth_check}
  try {{
    await db.{resource.rstrip("s")}.delete({{
      where: {{ id: params.id }},
    }});

    return new NextResponse(null, {{ status: 204 }});
  }} catch (error) {{
    console.error('DELETE /{resource}/[id] error:', error);
    return NextResponse.json(
      {{ error: 'Failed to delete {resource.rstrip("s")}' }},
      {{ status: 400 }}
    );
  }}
}}
'''

    single_file = single_path / "route.ts"
    single_file.write_text(single_route)
    print(f"Created: {single_file}")

    print(f"\nAPI routes for '{resource}' generated successfully!")
    print(f"Endpoints:")
    print(f"  GET    /api/{resource}      - List all")
    print(f"  POST   /api/{resource}      - Create")
    print(f"  GET    /api/{resource}/:id  - Get one")
    print(f"  PUT    /api/{resource}/:id  - Update")
    print(f"  DELETE /api/{resource}/:id  - Delete")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Next.js API route with CRUD"
    )
    parser.add_argument("resource", help="Resource name (e.g., 'posts', 'users')")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project root path (default: current directory)"
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Include authentication checks"
    )
    parser.add_argument(
        "--validation",
        action="store_true",
        help="Include Zod validation"
    )

    args = parser.parse_args()

    generate_api_route(
        args.resource,
        args.path,
        with_auth=args.auth,
        with_validation=args.validation,
    )


if __name__ == "__main__":
    main()
