# Todo AI Chatbot - Implementation Summary

## Project Overview
AI-powered chatbot for managing todos through natural language using MCP server architecture, Groq LLM API, and PostgreSQL database.

## Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Next.js        │────▶│   FastAPI        │────▶│   PostgreSQL     │
│   Frontend       │     │   Backend        │     │   (Neon Cloud)   │
│   Port: 3000     │     │   Port: 8000     │     │                  │
└──────────────────┘     └────────┬─────────┘     └──────────────────┘
                                  │
                         ┌────────▼─────────┐
                         │   Groq LLM API   │
                         │   (llama-3.1-8b) │
                         │   + MCP Tools    │
                         └──────────────────┘
```

## What Was Implemented

### 1. Backend (FastAPI + Python)

**Directory Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with CORS
│   ├── config.py            # Environment config (DATABASE_URL, GROQ_API_KEY)
│   ├── database.py          # SQLAlchemy connection
│   ├── models/
│   │   ├── task.py          # Task model (id, user_id, title, description, completed)
│   │   ├── conversation.py  # Conversation model
│   │   └── message.py       # Message model
│   ├── schemas/
│   │   ├── task.py          # Pydantic schemas
│   │   ├── chat.py          # ChatRequest, ChatResponse
│   │   └── message.py
│   ├── crud/
│   │   ├── task.py          # Task CRUD operations
│   │   ├── conversation.py
│   │   └── message.py
│   ├── api/
│   │   └── chat.py          # POST /api/{user_id}/chat endpoint
│   └── agent/
│       └── todo_agent.py    # Groq LLM agent with function calling
├── mcp_server/
│   └── server.py            # MCP tools implementation
├── alembic/                 # Database migrations
├── requirements.txt
└── .env
```

**Key Files:**

- `main.py`: FastAPI app with CORS middleware allowing all origins
- `config.py`: Loads DATABASE_URL and GROQ_API_KEY from .env
- `database.py`: SQLAlchemy engine connected to Neon PostgreSQL
- `todo_agent.py`: Groq LLM integration with manual JSON function parsing

### 2. MCP Server (5 Tools)

Implemented in `mcp_server/server.py`:

| Tool | Description | Arguments |
|------|-------------|-----------|
| `add_task` | Create a new task | user_id, title, description? |
| `list_tasks` | List all tasks | user_id, status? (pending/completed) |
| `complete_task` | Mark task as done | user_id, task_id |
| `delete_task` | Delete a task | user_id, task_id |
| `update_task` | Update task details | user_id, task_id, title?, description? |

### 3. AI Agent (Groq LLM)

**Model:** `llama-3.1-8b-instant`

**Approach:** Manual JSON function calling
- System prompt instructs LLM to output JSON like: `{"function": "add_task", "arguments": {"title": "buy milk"}}`
- Agent parses JSON from LLM response
- Executes corresponding MCP tool
- Returns human-readable response

**Why not native tool calling?**
- Groq's native tool calling had issues with various models
- Models were either decommissioned or didn't support tool_choice
- Manual JSON parsing is more reliable across models

### 4. Frontend (Next.js + Tailwind CSS)

**Directory Structure:**
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx         # Login + Chat interface
│   │   └── globals.css
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageInput.tsx
│   │   └── TaskList.tsx
│   └── lib/
│       └── api.ts           # API client
├── package.json
└── tailwind.config.js
```

**Features:**
- User login with user_id
- Chat interface with message bubbles
- Shows tool calls/actions performed
- New chat / logout buttons
- Auto-scroll to latest message

### 5. Database (PostgreSQL on Neon)

**Connection:** Cloud-hosted on Neon
```
postgresql://neondb_owner:***@ep-cold-breeze-aig9men9-pooler.c-4.us-east-1.aws.neon.tech/neondb
```

**Tables:**
- `tasks`: id, user_id, title, description, completed, created_at, updated_at
- `conversations`: id, user_id, created_at, updated_at
- `messages`: id, user_id, conversation_id, role, content, created_at

**Note:** Tasks are isolated per user_id. Different user_ids see different tasks.

## Configuration

### Backend .env
```
DATABASE_URL=postgresql://neondb_owner:npg_ZEYkB40fxDut@ep-cold-breeze-aig9men9-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
GROQ_API_KEY=your_groq_api_key_here
```

### Dependencies

**Backend (requirements.txt):**
```
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
python-dotenv==1.0.0
groq>=0.4.0
pydantic==2.5.3
```

**Frontend (package.json):**
```json
{
  "dependencies": {
    "next": "^14.2.35",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
```

## How to Run

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoint

```
POST /api/{user_id}/chat

Request:
{
  "message": "add task buy groceries",
  "conversation_id": 1  // optional
}

Response:
{
  "conversation_id": 1,
  "response": "Added task: 'buy groceries' (ID: 3)",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"title": "buy groceries"},
      "result": {"task_id": 3, "status": "created", "title": "buy groceries"}
    }
  ]
}
```

## Issues Encountered & Solutions

### 1. Gemini API Quota
- **Issue:** Gemini free tier has 20 requests/minute limit, exhausted quickly due to multi-turn conversations
- **Solution:** Switched to Groq API (higher limits, faster)

### 2. Groq Tool Calling
- **Issue:** Native tool calling not supported on many Groq models, or models were decommissioned
- **Solution:** Manual JSON function calling - LLM outputs JSON, we parse and execute

### 3. Model Availability
- **Issue:** Several Groq models were decommissioned (qwen-2.5-coder-32b, llama-3.3-70b-specdec, etc.)
- **Solution:** Using `llama-3.1-8b-instant` which is stable and available

### 4. User Isolation
- **Issue:** User thought database wasn't working
- **Explanation:** Tasks are stored per user_id. Must use same user_id to see previously created tasks

## Current Status

- Database: Working (tasks stored in Neon PostgreSQL)
- Backend API: Working
- Frontend: Working
- AI Agent: Uses manual JSON parsing approach

**To verify database is working:**
1. Login with user_id "6"
2. Say "show tasks"
3. Should see "buy groceries" task created earlier

## Debug Output

Backend terminal shows debug logs:
```
[AGENT] User: show tasks
[AGENT] LLM Response: {"function": "list_tasks", "arguments": {}}
[PARSE] Found direct JSON: {'function': 'list_tasks', 'arguments': {}}
[AGENT] Executing: list_tasks({'user_id': '6'})
[AGENT] Result: {'tasks': [...], 'count': 1}
[AGENT] Final response: Your tasks: ...
```

Check these logs to troubleshoot any issues.
