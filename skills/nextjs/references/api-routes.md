# Next.js API Routes Reference

## Route Handlers (App Router)

### Basic Structure

```tsx
// app/api/[resource]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  return NextResponse.json({ message: 'Hello' });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  return NextResponse.json(body, { status: 201 });
}

export async function PUT(request: NextRequest) { }
export async function PATCH(request: NextRequest) { }
export async function DELETE(request: NextRequest) { }
```

---

## CRUD API Pattern

### Complete Resource API

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

// GET /api/posts - List all
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get('page') || '1');
  const limit = parseInt(searchParams.get('limit') || '10');

  const posts = await db.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' },
  });

  return NextResponse.json({ data: posts, page, limit });
}

// POST /api/posts - Create
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const post = await db.post.create({ data: body });
    return NextResponse.json(post, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create post' },
      { status: 400 }
    );
  }
}
```

### Single Resource API

```tsx
// app/api/posts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

type Params = { params: { id: string } };

// GET /api/posts/:id
export async function GET(request: NextRequest, { params }: Params) {
  const post = await db.post.findUnique({
    where: { id: params.id },
  });

  if (!post) {
    return NextResponse.json(
      { error: 'Post not found' },
      { status: 404 }
    );
  }

  return NextResponse.json(post);
}

// PUT /api/posts/:id
export async function PUT(request: NextRequest, { params }: Params) {
  const body = await request.json();

  const post = await db.post.update({
    where: { id: params.id },
    data: body,
  });

  return NextResponse.json(post);
}

// DELETE /api/posts/:id
export async function DELETE(request: NextRequest, { params }: Params) {
  await db.post.delete({ where: { id: params.id } });
  return new NextResponse(null, { status: 204 });
}
```

---

## Request Handling

### Query Parameters

```tsx
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');
  const tags = searchParams.getAll('tag'); // Multiple values
  // ...
}
```

### Headers

```tsx
export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  const contentType = request.headers.get('content-type');
  // ...
}
```

### Cookies

```tsx
import { cookies } from 'next/headers';

export async function GET() {
  const cookieStore = cookies();
  const token = cookieStore.get('token');

  return NextResponse.json({ token: token?.value });
}

export async function POST() {
  const response = NextResponse.json({ success: true });
  response.cookies.set('token', 'abc123', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 1 week
  });
  return response;
}
```

---

## Response Patterns

### JSON Response

```tsx
return NextResponse.json(data);
return NextResponse.json(data, { status: 201 });
return NextResponse.json({ error: 'message' }, { status: 400 });
```

### Redirect

```tsx
import { redirect } from 'next/navigation';
redirect('/login');

// Or with NextResponse
return NextResponse.redirect(new URL('/login', request.url));
```

### Stream Response

```tsx
export async function GET() {
  const stream = new ReadableStream({
    async start(controller) {
      controller.enqueue(new TextEncoder().encode('Hello '));
      controller.enqueue(new TextEncoder().encode('World'));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/plain' },
  });
}
```

---

## Middleware

```tsx
// middleware.ts (root level)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check auth
  const token = request.cookies.get('token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add headers
  const response = NextResponse.next();
  response.headers.set('x-custom-header', 'value');

  return response;
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
};
```

---

## Error Handling

### Consistent Error Response

```tsx
// lib/api-error.ts
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
  }
}

// Usage in route
export async function GET() {
  try {
    // ... logic
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode }
      );
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

---

## Validation with Zod

```tsx
import { z } from 'zod';

const PostSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(1),
  published: z.boolean().default(false),
});

export async function POST(request: NextRequest) {
  const body = await request.json();

  const result = PostSchema.safeParse(body);
  if (!result.success) {
    return NextResponse.json(
      { errors: result.error.flatten() },
      { status: 400 }
    );
  }

  const post = await db.post.create({ data: result.data });
  return NextResponse.json(post, { status: 201 });
}
```

---

## Rate Limiting

```tsx
// lib/rate-limit.ts
const rateLimit = new Map<string, { count: number; timestamp: number }>();

export function checkRateLimit(ip: string, limit = 10, window = 60000) {
  const now = Date.now();
  const record = rateLimit.get(ip);

  if (!record || now - record.timestamp > window) {
    rateLimit.set(ip, { count: 1, timestamp: now });
    return true;
  }

  if (record.count >= limit) {
    return false;
  }

  record.count++;
  return true;
}

// Usage
export async function POST(request: NextRequest) {
  const ip = request.ip || 'unknown';

  if (!checkRateLimit(ip)) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429 }
    );
  }
  // ... continue
}
```
