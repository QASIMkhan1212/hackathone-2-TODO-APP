# ChatKit Integration Patterns

## Quick Start Patterns

### Pattern 1: Basic React Integration

**Use when**: Simple single-page React app

```tsx
// App.tsx
import { useChatKit, ChatKit } from '@openai/chatkit-react';

function App() {
  const { session, error, isLoading } = useChatKit({
    workflowId: 'workflow_abc123',
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session');
      const { clientSecret } = await res.json();
      return clientSecret;
    }
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <ChatKit session={session} />;
}
```

```typescript
// Backend endpoint (Express)
app.post('/api/chatkit-session', async (req, res) => {
  const session = await client.chatkit.sessions.create({
    workflow_id: process.env.CHATKIT_WORKFLOW_ID
  });
  res.json({ clientSecret: session.client_secret });
});
```

### Pattern 2: Next.js App Router Integration

**Use when**: Next.js 13+ with App Router

```tsx
// app/chat/page.tsx
'use client';

import { useChatKit, ChatKit } from '@openai/chatkit-react';

export default function ChatPage() {
  const { session } = useChatKit({
    workflowId: process.env.NEXT_PUBLIC_WORKFLOW_ID!,
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session', {
        method: 'POST'
      });
      const data = await res.json();
      return data.clientSecret;
    }
  });

  return (
    <div className="h-screen">
      <ChatKit session={session} />
    </div>
  );
}
```

```typescript
// app/api/chatkit-session/route.ts
import { NextResponse } from 'next/server';
import OpenAI from 'openai';

export async function POST() {
  const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });

  const session = await client.chatkit.sessions.create({
    workflow_id: process.env.CHATKIT_WORKFLOW_ID!
  });

  return NextResponse.json({
    clientSecret: session.client_secret
  });
}
```

### Pattern 3: Next.js Pages Router Integration

**Use when**: Next.js 12 or Pages Router

```tsx
// pages/chat.tsx
import { useChatKit, ChatKit } from '@openai/chatkit-react';

export default function ChatPage() {
  const { session } = useChatKit({
    workflowId: process.env.NEXT_PUBLIC_WORKFLOW_ID!,
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session', {
        method: 'POST'
      });
      return (await res.json()).clientSecret;
    }
  });

  return <ChatKit session={session} />;
}
```

```typescript
// pages/api/chatkit-session.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });

  const session = await client.chatkit.sessions.create({
    workflow_id: process.env.CHATKIT_WORKFLOW_ID!
  });

  res.json({ clientSecret: session.client_secret });
}
```

## Advanced Patterns

### Pattern 4: Authenticated Users

**Use when**: ChatKit sessions tied to user accounts

```typescript
// Backend: User-specific sessions
app.post('/api/chatkit-session', authenticateUser, async (req, res) => {
  const userId = req.user.id;

  const session = await client.chatkit.sessions.create({
    workflow_id: process.env.CHATKIT_WORKFLOW_ID,
    metadata: {
      user_id: userId,
      user_email: req.user.email
    }
  });

  // Store session for user
  await db.chatSessions.create({
    userId,
    sessionId: session.id,
    expiresAt: new Date(Date.now() + 3600000)
  });

  res.json({ clientSecret: session.client_secret });
});
```

### Pattern 5: Session Resumption

**Use when**: Preserving conversation history across page reloads

```tsx
import { useChatKit, ChatKit } from '@openai/chatkit-react';
import { useEffect, useState } from 'react';

function ChatWithResumption() {
  const [sessionId, setSessionId] = useState<string | null>(
    localStorage.getItem('chatkit_session_id')
  );

  const { session } = useChatKit({
    workflowId: 'workflow_abc123',
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId })
      });
      const data = await res.json();
      return data.clientSecret;
    }
  });

  useEffect(() => {
    if (session?.id) {
      localStorage.setItem('chatkit_session_id', session.id);
      setSessionId(session.id);
    }
  }, [session?.id]);

  return <ChatKit session={session} />;
}
```

### Pattern 6: Custom Widget Integration

**Use when**: Displaying structured data within chat

```tsx
import { ChatKit } from '@openai/chatkit-react';

// Custom widgets for structured responses
const customWidgets = {
  product_card: (data: ProductData) => (
    <div className="product-card">
      <img src={data.image} alt={data.name} />
      <h3>{data.name}</h3>
      <p>${data.price}</p>
      <button>Add to Cart</button>
    </div>
  ),
  booking_form: (data: BookingData) => (
    <form onSubmit={handleBooking}>
      <input type="date" value={data.date} />
      <input type="time" value={data.time} />
      <button>Confirm Booking</button>
    </form>
  )
};

function ChatWithWidgets() {
  const { session } = useChatKit({...});

  return (
    <ChatKit
      session={session}
      customWidgets={customWidgets}
    />
  );
}
```

### Pattern 7: Multi-Agent Switching

**Use when**: Different workflows for different purposes

```tsx
function MultiAgentChat() {
  const [activeWorkflow, setActiveWorkflow] = useState('support');

  const workflows = {
    support: 'workflow_support_123',
    sales: 'workflow_sales_456',
    technical: 'workflow_tech_789'
  };

  const { session } = useChatKit({
    workflowId: workflows[activeWorkflow],
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session', {
        method: 'POST',
        body: JSON.stringify({ workflow: activeWorkflow })
      });
      return (await res.json()).clientSecret;
    }
  });

  return (
    <>
      <div className="workflow-selector">
        <button onClick={() => setActiveWorkflow('support')}>
          Support
        </button>
        <button onClick={() => setActiveWorkflow('sales')}>
          Sales
        </button>
        <button onClick={() => setActiveWorkflow('technical')}>
          Technical
        </button>
      </div>
      <ChatKit session={session} />
    </>
  );
}
```

## Framework-Specific Patterns

### Vanilla JavaScript Integration

**Use when**: No framework or legacy application

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/@openai/chatkit-web"></script>
</head>
<body>
  <div id="chatkit-container"></div>

  <script>
    async function initChatKit() {
      const response = await fetch('/api/chatkit-session', {
        method: 'POST'
      });
      const { clientSecret } = await response.json();

      window.ChatKit.render({
        container: document.getElementById('chatkit-container'),
        workflowId: 'workflow_abc123',
        clientSecret: clientSecret
      });
    }

    initChatKit();
  </script>
</body>
</html>
```

### Vue.js Integration

**Use when**: Vue 3 application

```vue
<!-- ChatKitComponent.vue -->
<template>
  <div ref="chatkitContainer"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useChatKit } from '@openai/chatkit-react';

const chatkitContainer = ref(null);

onMounted(async () => {
  const { session } = await useChatKit({
    workflowId: 'workflow_abc123',
    getClientSecret: async () => {
      const res = await fetch('/api/chatkit-session', {
        method: 'POST'
      });
      return (await res.json()).clientSecret;
    }
  });

  // Render ChatKit in container
});
</script>
```

### Angular Integration

**Use when**: Angular 15+ application

```typescript
// chat.component.ts
import { Component, OnInit, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-chat',
  template: '<div #chatkitContainer></div>'
})
export class ChatComponent implements OnInit {
  @ViewChild('chatkitContainer') container!: ElementRef;

  constructor(private http: HttpClient) {}

  async ngOnInit() {
    const { clientSecret } = await this.http
      .post<{ clientSecret: string }>('/api/chatkit-session', {})
      .toPromise();

    // Initialize ChatKit with client secret
  }
}
```

## Deployment Patterns

### Pattern 8: Embedded Widget

**Use when**: Adding chat to existing application

```tsx
// EmbeddedChat.tsx
function EmbeddedChat({ position = 'bottom-right' }) {
  const [isOpen, setIsOpen] = useState(false);
  const { session } = useChatKit({...});

  return (
    <>
      <button
        className={`chat-toggle ${position}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        💬
      </button>
      {isOpen && (
        <div className={`chat-widget ${position}`}>
          <ChatKit session={session} />
        </div>
      )}
    </>
  );
}
```

```css
.chat-widget {
  position: fixed;
  width: 400px;
  height: 600px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 12px;
  overflow: hidden;
}

.chat-widget.bottom-right {
  bottom: 80px;
  right: 20px;
}
```

### Pattern 9: Full-Page Chat

**Use when**: Dedicated chat interface

```tsx
function FullPageChat() {
  const { session } = useChatKit({...});

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-blue-600 text-white p-4">
        <h1>Customer Support</h1>
      </header>
      <main className="flex-1">
        <ChatKit
          session={session}
          theme={{
            primaryColor: '#2563eb',
            fontFamily: 'system-ui'
          }}
        />
      </main>
    </div>
  );
}
```

## Error Handling Patterns

### Pattern 10: Graceful Degradation

```tsx
function ResilientChat() {
  const { session, error, isLoading } = useChatKit({
    workflowId: 'workflow_abc123',
    getClientSecret: async () => {
      try {
        const res = await fetch('/api/chatkit-session', {
          method: 'POST'
        });

        if (!res.ok) throw new Error('Session creation failed');

        return (await res.json()).clientSecret;
      } catch (err) {
        console.error('ChatKit error:', err);
        throw err;
      }
    }
  });

  if (isLoading) {
    return <Skeleton className="h-screen" />;
  }

  if (error) {
    return (
      <ErrorFallback
        error={error}
        retry={() => window.location.reload()}
      />
    );
  }

  return <ChatKit session={session} />;
}
```

## Best Practices

1. **Always create sessions server-side** - Never expose API keys to frontend
2. **Implement rate limiting** - Prevent abuse of session creation
3. **Handle errors gracefully** - Provide fallback UI for failures
4. **Cache sessions appropriately** - Balance UX and security
5. **Monitor usage** - Track session creation and token consumption
6. **Set CORS policies** - Restrict access to trusted domains
7. **Use environment variables** - Never hardcode API keys or workflow IDs
8. **Implement analytics** - Track user interactions and satisfaction
