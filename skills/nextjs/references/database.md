# Next.js Database Integration

## Prisma Setup (Recommended)

### Installation

```bash
npm install prisma @prisma/client
npx prisma init
```

### Schema Definition

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql" // or mysql, sqlite, mongodb
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([authorId])
}
```

### Database Client Singleton

```tsx
// lib/db.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const db =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query'] : [],
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = db;
}
```

### Commands

```bash
npx prisma migrate dev --name init  # Create migration
npx prisma generate                  # Generate client
npx prisma studio                    # Open GUI
npx prisma db push                   # Push without migration
```

---

## CRUD Operations

### Create

```tsx
// Single record
const user = await db.user.create({
  data: {
    email: 'user@example.com',
    name: 'John',
  },
});

// With relations
const post = await db.post.create({
  data: {
    title: 'Hello World',
    author: { connect: { id: userId } },
  },
  include: { author: true },
});

// Many records
const users = await db.user.createMany({
  data: [
    { email: 'a@example.com' },
    { email: 'b@example.com' },
  ],
});
```

### Read

```tsx
// Find unique
const user = await db.user.findUnique({
  where: { id: userId },
});

// Find first matching
const post = await db.post.findFirst({
  where: { published: true },
  orderBy: { createdAt: 'desc' },
});

// Find many with filtering
const posts = await db.post.findMany({
  where: {
    published: true,
    author: { email: { contains: '@example.com' } },
  },
  include: { author: { select: { name: true } } },
  orderBy: { createdAt: 'desc' },
  skip: 0,
  take: 10,
});

// Count
const count = await db.post.count({
  where: { published: true },
});
```

### Update

```tsx
// Single record
const user = await db.user.update({
  where: { id: userId },
  data: { name: 'Updated Name' },
});

// Many records
const updated = await db.post.updateMany({
  where: { authorId: userId },
  data: { published: false },
});

// Upsert (create or update)
const user = await db.user.upsert({
  where: { email: 'user@example.com' },
  create: { email: 'user@example.com', name: 'New User' },
  update: { name: 'Updated User' },
});
```

### Delete

```tsx
// Single record
const user = await db.user.delete({
  where: { id: userId },
});

// Many records
const deleted = await db.post.deleteMany({
  where: { published: false },
});
```

---

## Server Components with Database

```tsx
// app/posts/page.tsx
import { db } from '@/lib/db';

export default async function PostsPage() {
  const posts = await db.post.findMany({
    where: { published: true },
    include: { author: true },
    orderBy: { createdAt: 'desc' },
  });

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>
          <h2>{post.title}</h2>
          <p>By {post.author.name}</p>
        </li>
      ))}
    </ul>
  );
}
```

---

## Server Actions with Database

```tsx
// app/actions/posts.ts
'use server';

import { db } from '@/lib/db';
import { revalidatePath } from 'next/cache';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function createPost(formData: FormData) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) throw new Error('Unauthorized');

  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  await db.post.create({
    data: {
      title,
      content,
      authorId: session.user.id,
    },
  });

  revalidatePath('/posts');
}

export async function deletePost(postId: string) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) throw new Error('Unauthorized');

  await db.post.delete({
    where: {
      id: postId,
      authorId: session.user.id, // Ensure ownership
    },
  });

  revalidatePath('/posts');
}
```

---

## Transactions

```tsx
// Interactive transaction
const result = await db.$transaction(async (tx) => {
  const user = await tx.user.create({
    data: { email: 'user@example.com' },
  });

  const post = await tx.post.create({
    data: {
      title: 'Welcome',
      authorId: user.id,
    },
  });

  return { user, post };
});

// Sequential operations
const [users, posts] = await db.$transaction([
  db.user.findMany(),
  db.post.findMany(),
]);
```

---

## Drizzle ORM Alternative

### Setup

```bash
npm install drizzle-orm postgres
npm install -D drizzle-kit
```

### Schema

```tsx
// db/schema.ts
import { pgTable, text, timestamp, boolean } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: text('id').primaryKey(),
  email: text('email').unique().notNull(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
});

export const posts = pgTable('posts', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content'),
  published: boolean('published').default(false),
  authorId: text('author_id').references(() => users.id),
});
```

### Client

```tsx
// lib/db.ts
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from '@/db/schema';

const client = postgres(process.env.DATABASE_URL!);
export const db = drizzle(client, { schema });
```

### Queries

```tsx
import { db } from '@/lib/db';
import { users, posts } from '@/db/schema';
import { eq } from 'drizzle-orm';

// Select
const allUsers = await db.select().from(users);
const user = await db.select().from(users).where(eq(users.id, userId));

// Insert
await db.insert(users).values({ id: '1', email: 'user@example.com' });

// Update
await db.update(users).set({ name: 'Updated' }).where(eq(users.id, userId));

// Delete
await db.delete(users).where(eq(users.id, userId));
```
