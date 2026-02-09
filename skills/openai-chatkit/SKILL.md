---
name: openai-chatkit
description: "OpenAI ChatKit integration assistant for building embeddable AI chat experiences. Use when working with ChatKit for: (1) Setting up ChatKit in React/Next.js applications, (2) Creating agent workflows and chat interfaces, (3) Customizing chat UI themes and layouts, (4) Integrating ChatKit with authentication systems, (5) Implementing custom widgets and event handlers, (6) Deploying production chat experiences, or any other ChatKit-related development tasks"
---

# OpenAI ChatKit Integration Assistant

## Overview

ChatKit is OpenAI's official framework for embedding customizable, agentic chat experiences into applications. This skill provides automated setup, configuration guidance, and best practices for integrating ChatKit into web applications.

## Quick Start

### Initialize ChatKit in Existing Project

Use the initialization script to automatically set up ChatKit:

```bash
python scripts/init_chatkit_project.py /path/to/your/project
```

Options:
- `--skip-install`: Skip npm dependency installation
- `--pages-router`: Use Next.js Pages Router instead of App Router

This creates:
- ChatKit dependencies installation
- Environment configuration files
- API route for session management
- Example React component
- Setup documentation

### Manual Setup

For manual setup or framework-specific guidance, see [integration-patterns.md](references/integration-patterns.md).

## Workflows

### 1. Setting Up ChatKit in a New Project

**Steps:**

1. **Install dependencies**:
   ```bash
   npm install @openai/chatkit-react openai
   ```

2. **Create environment configuration**:
   ```env
   OPENAI_API_KEY=your_api_key
   CHATKIT_WORKFLOW_ID=your_workflow_id
   NEXT_PUBLIC_WORKFLOW_ID=your_workflow_id
   ```

3. **Create backend endpoint** for session management:
   - Next.js App Router: `app/api/chatkit-session/route.ts`
   - Next.js Pages Router: `pages/api/chatkit-session.ts`
   - Express/other: Custom endpoint

   See [integration-patterns.md](references/integration-patterns.md) for code examples.

4. **Create ChatKit component** using the `useChatKit` hook

5. **Import and render** in your application

### 2. Creating Agent Workflows

**Via Agent Builder (Recommended):**

1. Navigate to https://platform.openai.com/agent-builder
2. Design workflow with drag-and-drop interface
3. Configure tools (web search, code interpreter, custom functions)
4. Deploy and copy workflow ID

**Via API (Programmatic):**

Use the workflow creation script:

```bash
python scripts/create_workflow.py create --template customer_support
```

Templates available:
- `customer_support`: Customer service agent
- `sales_assistant`: Sales and product guidance
- `technical_support`: Technical troubleshooting
- `general_assistant`: General-purpose AI assistant

Custom workflow:
```bash
python scripts/create_workflow.py create \
  --name "My Agent" \
  --instructions "You are a helpful..." \
  --tools web_search code_interpreter
```

List existing workflows:
```bash
python scripts/create_workflow.py list
```

### 3. Customizing Chat Interface

**Basic Theme:**

```tsx
<ChatKit
  session={session}
  theme={{
    primaryColor: '#0066cc',
    backgroundColor: '#ffffff',
    fontFamily: 'Inter, sans-serif',
    borderRadius: '0.5rem'
  }}
/>
```

**Pre-built Themes:**

See [customization.md](references/customization.md) for:
- Corporate theme
- Dark mode theme
- Customer support theme
- Minimalist theme
- Dynamic theme switching

**Custom Components:**

Override default components:

```tsx
<ChatKit
  session={session}
  components={{
    header: CustomHeader,
    input: CustomInput,
    userMessage: CustomUserBubble,
    botMessage: CustomBotBubble
  }}
/>
```

### 4. Integration Patterns

**Basic React:**
```tsx
import { useChatKit, ChatKit } from '@openai/chatkit-react';

const { session } = useChatKit({
  workflowId: 'workflow_abc123',
  getClientSecret: async () => {
    const res = await fetch('/api/chatkit-session', { method: 'POST' });
    return (await res.json()).clientSecret;
  }
});

return <ChatKit session={session} />;
```

**Authenticated Users:**

Tie sessions to user accounts:

```tsx
const { session } = useChatKit({
  workflowId: 'workflow_abc123',
  getClientSecret: async () => {
    const res = await fetch('/api/chatkit-session', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userToken}`
      }
    });
    return (await res.json()).clientSecret;
  }
});
```

**Session Resumption:**

Preserve conversations across page reloads:

```tsx
const [sessionId, setSessionId] = useState(
  localStorage.getItem('chatkit_session_id')
);

const { session } = useChatKit({
  workflowId: 'workflow_abc123',
  getClientSecret: async () => {
    const res = await fetch('/api/chatkit-session', {
      method: 'POST',
      body: JSON.stringify({ sessionId })
    });
    return (await res.json()).clientSecret;
  }
});

useEffect(() => {
  if (session?.id) {
    localStorage.setItem('chatkit_session_id', session.id);
  }
}, [session?.id]);
```

For additional patterns (custom widgets, multi-agent, embedded widget, etc.), see [integration-patterns.md](references/integration-patterns.md).

### 5. Advanced Features

**Custom Widgets:**

Render structured data in chat:

```tsx
const customWidgets = {
  product_card: (data) => <ProductCard {...data} />,
  booking_form: (data) => <BookingForm {...data} />
};

<ChatKit session={session} customWidgets={customWidgets} />
```

**Chain-of-Thought Visualization:**

Show agent reasoning:

```tsx
<ChatKit
  session={session}
  showThinking={true}
  thinkingStyle="expanded"
/>
```

**File Attachments:**

Enable file uploads:

```tsx
<ChatKit
  session={session}
  enableFileUpload={true}
  acceptedFileTypes={['image/*', '.pdf', '.docx']}
  maxFileSize={10 * 1024 * 1024}
/>
```

**Event Handling:**

```tsx
<ChatKit
  session={session}
  onMessage={(msg) => console.log('New message:', msg)}
  onToolInvocation={(tool) => console.log('Tool used:', tool)}
  onError={(err) => console.error('Error:', err)}
/>
```

### 6. Deployment Patterns

**Embedded Widget:**

Add chat bubble to existing site:

```tsx
function EmbeddedChat() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(!isOpen)}>💬</button>
      {isOpen && (
        <div className="chat-widget">
          <ChatKit session={session} />
        </div>
      )}
    </>
  );
}
```

**Full-Page Chat:**

Dedicated chat interface:

```tsx
<div className="h-screen">
  <header>Customer Support</header>
  <ChatKit session={session} />
</div>
```

### 7. Security & Best Practices

**Session Management:**

- Always create sessions server-side
- Never expose API keys to frontend
- Implement rate limiting on session creation
- Set appropriate CORS policies

**Backend Endpoint Example:**

```typescript
// app/api/chatkit-session/route.ts
import { NextResponse } from 'next/server';
import OpenAI from 'openai';

export async function POST() {
  // Validate request (auth, rate limit, etc.)

  const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });

  try {
    const session = await client.chatkit.sessions.create({
      workflow_id: process.env.CHATKIT_WORKFLOW_ID!
    });

    return NextResponse.json({
      clientSecret: session.client_secret
    });
  } catch (error) {
    console.error('Session creation failed:', error);
    return NextResponse.json(
      { error: 'Failed to create session' },
      { status: 500 }
    );
  }
}
```

**Error Handling:**

```tsx
const { session, error, isLoading } = useChatKit({...});

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorFallback error={error} />;

return <ChatKit session={session} />;
```

## Reference Documentation

### Complete API Reference

See [chatkit-api.md](references/chatkit-api.md) for:
- Frontend API (React hooks and components)
- Backend API (session management)
- Configuration options
- Theme customization
- Event handling
- Advanced features
- Pricing information

### Integration Patterns

See [integration-patterns.md](references/integration-patterns.md) for:
- Framework-specific setups (React, Next.js, Vue, Angular)
- Authentication patterns
- Session resumption
- Custom widgets
- Multi-agent switching
- Deployment patterns
- Error handling

### Customization Guide

See [customization.md](references/customization.md) for:
- Theme configuration
- Pre-built themes
- Dynamic theme switching
- Component customization
- Branding elements
- Internationalization
- Accessibility
- Mobile optimization

## Common Patterns

### Handling Loading States

```tsx
const { session, isLoading } = useChatKit({...});

if (isLoading) {
  return <div>Initializing chat...</div>;
}
```

### Error Recovery

```tsx
const { session, error } = useChatKit({...});

if (error) {
  return (
    <div>
      <p>Chat unavailable: {error.message}</p>
      <button onClick={() => window.location.reload()}>
        Retry
      </button>
    </div>
  );
}
```

### Dark Mode Support

```tsx
const [isDark, setIsDark] = useState(false);

const theme = isDark
  ? { primaryColor: '#60a5fa', backgroundColor: '#111827' }
  : { primaryColor: '#2563eb', backgroundColor: '#ffffff' };

<ChatKit session={session} theme={theme} />
```

## Troubleshooting

### Common Issues

**1. Session creation fails:**
- Verify OPENAI_API_KEY is set correctly
- Check CHATKIT_WORKFLOW_ID is valid
- Ensure workflow exists and is deployed
- Check API endpoint is accessible

**2. ChatKit component doesn't render:**
- Verify session is defined before rendering
- Check browser console for errors
- Ensure dependencies are installed correctly
- Verify 'use client' directive (Next.js App Router)

**3. Theme not applying:**
- Check theme object structure
- Verify CSS isn't overriding styles
- Use browser DevTools to inspect styles
- Ensure theme prop is passed correctly

**4. CORS errors:**
- Configure CORS in backend API route
- Check allowed origins
- Verify credentials handling

## Development Tips

1. **Start with templates** - Use initialization script for quick setup
2. **Use Agent Builder** - Visual workflow design is faster than API
3. **Test locally first** - Verify setup before deploying
4. **Monitor usage** - Track sessions and token consumption
5. **Implement rate limiting** - Prevent abuse of session creation
6. **Handle errors gracefully** - Provide fallback UI
7. **Customize progressively** - Start basic, add features as needed
8. **Review documentation** - Check official docs for updates

## Resources

### Scripts
- `scripts/init_chatkit_project.py` - Automated project setup
- `scripts/create_workflow.py` - Workflow management

### Reference Documentation
- `references/chatkit-api.md` - Complete API reference
- `references/integration-patterns.md` - Framework integrations
- `references/customization.md` - Theming and branding

### Official Resources
- ChatKit Docs: https://platform.openai.com/docs/guides/chatkit
- ChatKit.js: https://openai.github.io/chatkit-js/
- Python SDK: https://openai.github.io/chatkit-python/
- Agent Builder: https://platform.openai.com/agent-builder
- GitHub: https://github.com/openai/chatkit-js
