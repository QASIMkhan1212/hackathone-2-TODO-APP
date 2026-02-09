# TODO Chatbot Integration Guide

This guide documents the integration of the AI chatbot from phase-3 into the TODO app from phase-2.

## Overview

The integration adds an AI-powered chatbot that allows users to manage their tasks through natural language commands while keeping the existing manual UI fully functional.

## Architecture

### Backend Components

#### 1. Agent Module (`backend/agent/`)
- **`__init__.py`**: Module exports
- **`todo_agent.py`**: Groq LLM-based agent for processing natural language
  - Model: `llama-3.1-8b-instant`
  - Parses function calls from LLM responses
  - Generates human-friendly responses
- **`mcp_tools.py`**: MCP tool server working with SQLModel
  - Maps phase-2's `content` field to phase-3's `title` concept
  - Tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
  - Works directly with SQLModel Session

#### 2. Chat Schemas (`backend/schemas.py`)
- **`ChatRequest`**: Request model with `message` field
- **`ChatResponse`**: Response with `response` text and `tool_calls` array
- **`ToolCall`**: Model for tracking tool executions

#### 3. Chat Endpoint (`backend/main.py`)
- **POST `/api/{user_id}/chat`**
  - Requires JWT authentication (reuses existing `get_current_user`)
  - Stateless - no conversation persistence
  - Returns AI response with list of tool calls executed

### Frontend Components

#### 1. Chat API Client (`frontend/src/lib/chat-api.ts`)
- **`sendChatMessage()`**: Sends message to backend
- Returns `ChatResponse` with AI response and tool calls

#### 2. ChatBubble Component (`frontend/src/components/ChatBubble.tsx`)
- Floating chat button in bottom-right corner
- Expandable chat panel
- Features:
  - Local message history (not persisted)
  - Auto-scroll to latest message
  - Loading states
  - Calls `onTasksChanged()` after tool execution to refresh task list

#### 3. Main Page Integration (`frontend/src/app/page.tsx`)
- Fetches JWT token for authenticated requests
- Renders `ChatBubble` when user is logged in and token is available
- Passes `refetch()` callback to refresh tasks after chat actions

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

The following packages were added:
- `groq` - Groq API client
- `httpx` - HTTP client for async requests
- `cryptography` - For JWT key handling
- `pyjwt` - JWT token processing

#### Configure Environment Variables

Edit `backend/.env` and add your Groq API key:

```env
# Groq API Configuration
GROQ_API_KEY="your_actual_groq_api_key_here"
```

To get a Groq API key:
1. Visit https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into `.env`

#### Start the Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

The frontend already has all necessary dependencies installed. No additional packages are required.

#### Start the Frontend Server
```bash
cd frontend
npm run dev
```

The app will be available at http://localhost:3000

## Testing the Integration

### 1. Start Both Servers
Make sure both backend (port 8000) and frontend (port 3000) are running.

### 2. Login to the App
- Open http://localhost:3000
- Sign in with your existing account or create a new one

### 3. Open the Chat Panel
- Look for the floating chat button in the bottom-right corner
- Click it to open the chat panel

### 4. Test Natural Language Commands

Try these example commands:

#### Add Tasks
- "Add task buy groceries"
- "Create a task to call mom"
- "add task finish homework"

#### List Tasks
- "Show my tasks"
- "List all tasks"
- "What tasks do I have?"

#### Complete Tasks
- "Complete task 1"
- "Mark task 2 as done"

#### Delete Tasks
- "Delete task 3"
- "Remove task 1"

#### Update Tasks
- "Update task 1 to buy milk and bread"
- "Change task 2 to call dad"

### 5. Verify Real-Time Sync

After each chat command:
1. The chatbot should respond with confirmation
2. The main task list should update automatically
3. Changes should be visible immediately without manual refresh

### 6. Test Authentication

Try accessing the chat endpoint without authentication:
```bash
curl -X POST http://localhost:8000/api/test-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show tasks"}'
```

Expected: Should return 401 Unauthorized

## Features

### What Works
✅ Natural language task management through chat
✅ Real-time sync between chatbot and task list
✅ JWT authentication for chat endpoint
✅ Both manual UI and chatbot work with same tasks
✅ Stateless chat (no conversation persistence)
✅ Automatic task list refresh after chat actions

### What's NOT Included
❌ Conversation history persistence
❌ WebSocket real-time updates
❌ Multi-user chat features
❌ Task descriptions (phase-2 only has content field)

## File Structure

```
phase-2/
├── backend/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── todo_agent.py       # Groq LLM agent
│   │   └── mcp_tools.py        # MCP tools with SQLModel
│   ├── schemas.py              # Chat schemas
│   ├── main.py                 # Added chat endpoint
│   ├── requirements.txt        # Added groq, httpx, etc.
│   └── .env                    # Added GROQ_API_KEY
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatBubble.tsx  # Chat UI component
│   │   ├── lib/
│   │   │   ├── chat-api.ts     # Chat API client
│   │   │   └── hooks/
│   │   │       └── useTasks.ts # Added refetch function
│   │   └── app/
│   │       └── page.tsx        # Integrated ChatBubble
└── INTEGRATION_GUIDE.md        # This file
```

## API Reference

### POST /api/{user_id}/chat

**Request:**
```json
{
  "message": "add task buy milk"
}
```

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "response": "Added task: 'buy milk' (ID: 42)",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {
        "title": "buy milk"
      },
      "result": {
        "task_id": 42,
        "status": "created",
        "title": "buy milk"
      }
    }
  ]
}
```

## Troubleshooting

### Chat Button Not Appearing
- Check that you're logged in
- Verify JWT token is being fetched (check browser console)
- Ensure backend is running on port 8000

### Chat Errors
- Check that `GROQ_API_KEY` is set in `backend/.env`
- Verify Groq API key is valid
- Check backend logs for detailed error messages

### Tasks Not Syncing
- Ensure `onTasksChanged` callback is being called
- Check that the task list has `refetch` function
- Verify backend is returning tool_calls in response

### Import Errors
- Run `pip install -r requirements.txt` in backend
- Make sure you're using the backend virtual environment

## Next Steps

Potential enhancements:
1. Add conversation history persistence
2. Implement WebSocket for real-time updates
3. Add typing indicators
4. Support voice input
5. Add task descriptions field
6. Implement conversation context (remember previous messages)
7. Add more sophisticated NLP for complex commands
8. Add analytics for chatbot usage

## Credits

- Phase-2 TODO App: Next.js 16 + FastAPI + SQLModel
- Phase-3 Chatbot: Groq LLM (llama-3.1-8b-instant)
- Integration completed: February 8, 2026
