---
name: nextjs
description: Next.js full-stack React framework for building modern web applications. Use when users want to (1) create new Next.js projects, (2) implement App Router pages and layouts, (3) create API routes, (4) configure Server Components vs Client Components, (5) implement SSR/SSG/ISR rendering strategies, (6) set up authentication, (7) optimize performance with caching and Turbopack, (8) deploy to Vercel or other platforms. Triggers on mentions of "next.js", "nextjs", "app router", "server components", "vercel", or React full-stack development.
---

# Next.js

Full-stack React framework for building modern, performant web applications.

## Project Setup

### Create New Project

```bash
npx create-next-app@latest my-app
# Options: TypeScript, ESLint, Tailwind CSS, src/ directory, App Router
```

### Project Structure (App Router)

```
my-app/
├── app/
│   ├── layout.tsx          # Root layout (required)
│   ├── page.tsx            # Home page (/)
│   ├── globals.css         # Global styles
│   ├── api/                # API routes
│   │   └── route.ts
│   └── [slug]/             # Dynamic routes
│       └── page.tsx
├── components/             # Shared components
├── lib/                    # Utilities & helpers
├── public/                 # Static assets
├── next.config.js          # Next.js configuration
└── package.json
```

## Routing (App Router)

### Page Routes

| File | Route |
|------|-------|
| `app/page.tsx` | `/` |
| `app/about/page.tsx` | `/about` |
| `app/blog/[slug]/page.tsx` | `/blog/:slug` |
| `app/shop/[...slug]/page.tsx` | `/shop/*` (catch-all) |
| `app/(auth)/login/page.tsx` | `/login` (route group) |

### Special Files

| File | Purpose |
|------|---------|
| `layout.tsx` | Shared UI wrapper (preserves state) |
| `page.tsx` | Unique page content |
| `loading.tsx` | Loading UI (Suspense) |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |
| `route.ts` | API endpoint |

## Components

### Server Components (Default)

```tsx
// app/posts/page.tsx - Runs on server only
async function PostsPage() {
  const posts = await db.posts.findMany(); // Direct DB access
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>;
}
export default PostsPage;
```

### Client Components

```tsx
'use client'; // Required directive
import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### When to Use Each

| Server Components | Client Components |
|-------------------|-------------------|
| Fetch data | useState, useEffect |
| Access backend resources | Event handlers (onClick) |
| Keep sensitive data on server | Browser APIs |
| Large dependencies | Interactivity |

## Data Fetching

### Server Components (Recommended)

```tsx
// Automatic caching and deduplication
async function Page() {
  const data = await fetch('https://api.example.com/data');
  return <div>{/* render data */}</div>;
}
```

### Caching Options

```tsx
// Cached (default) - static
fetch(url);

// Revalidate every 60 seconds (ISR)
fetch(url, { next: { revalidate: 60 } });

// No cache - always fresh (SSR)
fetch(url, { cache: 'no-store' });
```

### Server Actions

```tsx
// app/actions.ts
'use server';

export async function createPost(formData: FormData) {
  const title = formData.get('title');
  await db.posts.create({ data: { title } });
  revalidatePath('/posts');
}
```

## API Routes

```tsx
// app/api/posts/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const posts = await db.posts.findMany();
  return NextResponse.json(posts);
}

export async function POST(request: Request) {
  const body = await request.json();
  const post = await db.posts.create({ data: body });
  return NextResponse.json(post, { status: 201 });
}
```

**Detailed API patterns**: See [references/api-routes.md](references/api-routes.md)

## Rendering Strategies

| Strategy | When | How |
|----------|------|-----|
| **Static (SSG)** | Content rarely changes | Default behavior |
| **ISR** | Content updates periodically | `revalidate: 60` |
| **Dynamic (SSR)** | Per-request data | `cache: 'no-store'` |
| **Client** | User-specific, interactive | `'use client'` |

## Performance

### Image Optimization

```tsx
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={800}
  height={400}
  priority // Load immediately (LCP)
/>
```

### Font Optimization

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });

export default function Layout({ children }) {
  return <body className={inter.className}>{children}</body>;
}
```

### Metadata

```tsx
// app/layout.tsx or page.tsx
export const metadata = {
  title: 'My App',
  description: 'App description',
  openGraph: { images: ['/og.png'] },
};
```

## Common Patterns

- **Authentication**: See [references/auth-patterns.md](references/auth-patterns.md)
- **Database Integration**: See [references/database.md](references/database.md)
- **Deployment**: See [references/deployment.md](references/deployment.md)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/scaffold_page.py` | Generate new page with layout |
| `scripts/generate_api.py` | Create API route with CRUD |
| `scripts/add_auth.py` | Add NextAuth.js authentication |
