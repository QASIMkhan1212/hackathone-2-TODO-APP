# ChatKit API Reference

## Overview

ChatKit is OpenAI's official framework for embedding customizable chat interfaces powered by AI workflows. It provides a complete solution for building agentic chat experiences with minimal setup.

## Installation

### React/Next.js Installation

```bash
npm install @openai/chatkit-react
```

### Python SDK (Backend)

```bash
pip install openai-chatkit
```

## Core Concepts

### Setup Flow

1. **Create Agent Workflow**: Build workflow in OpenAI Agent Builder or use API
2. **Set up Backend**: Create endpoint to generate ChatKit sessions
3. **Embed Frontend**: Add ChatKit component to your application
4. **Customize**: Apply theming and configuration

## Frontend API (React)

### useChatKit Hook

The primary hook for integrating ChatKit into React applications.

```typescript
import { useChatKit } from '@openai/chatkit-react';

const { session, error, isLoading } = useChatKit({
  workflowId: 'your-workflow-id',
  getClientSecret: async () => {
    const response = await fetch('/api/chatkit-session');
    const { clientSecret } = await response.json();
    return clientSecret;
  }
});
```

**Parameters:**
- `workflowId` (string, required): Your OpenAI workflow ID
- `getClientSecret` (function, required): Async function returning client secret

**Returns:**
- `session`: Current ChatKit session object
- `error`: Error object if session creation fails
- `isLoading`: Boolean indicating loading state

### ChatKit Component

The embeddable chat UI component.

```tsx
import { ChatKit } from '@openai/chatkit-react';

<ChatKit
  session={session}
  theme={{
    primaryColor: '#0066cc',
    fontFamily: 'Inter, sans-serif'
  }}
  onMessage={(message) => console.log(message)}
/>
```

**Props:**
- `session` (object, required): Session from useChatKit hook
- `theme` (object, optional): Customization options
- `onMessage` (function, optional): Message event handler
- `onError` (function, optional): Error event handler

## Backend API

### Session Creation

```python
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

session = client.chatkit.sessions.create(
    workflow_id="workflow_abc123"
)

return {
    "client_secret": session.client_secret
}
```

### Session Management

**Create Session:**
```python
session = client.chatkit.sessions.create(workflow_id="...")
```

**Retrieve Session:**
```python
session = client.chatkit.sessions.retrieve(session_id="...")
```

**List Sessions:**
```python
sessions = client.chatkit.sessions.list(limit=10)
```

## Configuration Options

### Theme Customization

```typescript
theme: {
  primaryColor: string,        // Main brand color
  backgroundColor: string,      // Chat background
  fontFamily: string,          // Typography
  borderRadius: string,        // UI element roundness
  messageBackground: string,   // Message bubble color
  userMessageColor: string,    // User message text color
  botMessageColor: string      // Bot message text color
}
```

### Advanced Options

```typescript
{
  enableFileUpload: boolean,     // Allow file attachments
  enableVoiceInput: boolean,     // Voice input support
  maxMessageLength: number,      // Character limit
  placeholder: string,           // Input placeholder text
  welcomeMessage: string,        // Initial greeting
  toolVisualization: boolean     // Show tool invocations
}
```

## Workflow Integration

### Creating Workflows

**Via Agent Builder (UI):**
1. Navigate to platform.openai.com/agent-builder
2. Drag-and-drop nodes to design workflow
3. Configure tools and prompts
4. Deploy workflow

**Via API:**
```python
workflow = client.agent_builder.workflows.create(
    name="Customer Support Agent",
    description="Handles customer inquiries",
    tools=["web_search", "knowledge_base"],
    model="gpt-4o"
)
```

### Workflow Configuration

```python
{
    "name": "Support Agent",
    "model": "gpt-4o",
    "instructions": "You are a helpful support agent...",
    "tools": [
        {"type": "web_search"},
        {"type": "code_interpreter"},
        {"type": "function", "function": {...}}
    ],
    "temperature": 0.7
}
```

## Authentication & Security

### Client Secret Management

**Best Practices:**
- Generate secrets server-side only
- Never expose API keys to frontend
- Implement rate limiting on session creation
- Set appropriate CORS policies

### Example Backend Endpoint (Next.js)

```typescript
// app/api/chatkit-session/route.ts
import { NextResponse } from 'next/server';
import OpenAI from 'openai';

export async function POST() {
  const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });

  const session = await client.chatkit.sessions.create({
    workflow_id: process.env.CHATKIT_WORKFLOW_ID
  });

  return NextResponse.json({
    clientSecret: session.client_secret
  });
}
```

## Event Handling

### Message Events

```typescript
onMessage={(message) => {
  console.log('New message:', message.content);
  console.log('Role:', message.role); // 'user' | 'assistant'
  console.log('Timestamp:', message.created_at);
}}
```

### Tool Invocation Events

```typescript
onToolInvocation={(tool) => {
  console.log('Tool called:', tool.name);
  console.log('Arguments:', tool.arguments);
  console.log('Result:', tool.result);
}}
```

### Error Handling

```typescript
onError={(error) => {
  console.error('ChatKit error:', error.message);
  // Implement retry logic or fallback UI
}}
```

## Advanced Features

### Custom Widgets

Embed custom UI components within chat messages:

```typescript
customWidgets={{
  'product_card': (data) => <ProductCard {...data} />,
  'booking_form': (data) => <BookingForm {...data} />
}}
```

### Chain-of-Thought Visualization

Display agent reasoning process:

```typescript
<ChatKit
  session={session}
  showThinking={true}
  thinkingStyle="expanded" // 'collapsed' | 'expanded' | 'hidden'
/>
```

### File Attachments

Enable file uploads:

```typescript
<ChatKit
  session={session}
  enableFileUpload={true}
  acceptedFileTypes={['image/*', '.pdf', '.docx']}
  maxFileSize={10 * 1024 * 1024} // 10MB
/>
```

## Pricing

ChatKit is included with standard OpenAI API pricing. Costs based on:
- Model tokens (input/output)
- Tool usage (web search, code interpreter, etc.)

No additional charge for ChatKit UI framework.

## Resources

- Official Docs: https://platform.openai.com/docs/guides/chatkit
- ChatKit.js Docs: https://openai.github.io/chatkit-js/
- Python SDK: https://openai.github.io/chatkit-python/
- GitHub (JS): https://github.com/openai/chatkit-js
- Agent Builder: https://platform.openai.com/agent-builder
