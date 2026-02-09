# Todo AI Chatbot

AI-powered chatbot for managing todos through natural language using MCP server architecture and Google Gemini API.

## Features

- Natural language task management
- Create, list, complete, update, and delete tasks
- Conversation persistence across sessions
- Multi-user support with isolated data
- Real-time AI responses with function calling

## Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Next.js        │────▶│   FastAPI        │────▶│   PostgreSQL     │
│   Frontend       │     │   Backend        │     │   Database       │
└──────────────────┘     └────────┬─────────┘     └──────────────────┘
                                  │
                         ┌────────▼─────────┐
                         │   Gemini AI      │
                         │   + MCP Tools    │
                         └──────────────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Google API Key (for Gemini)

## Setup

### 1. Database Setup

Create a PostgreSQL database:

```bash
createdb todo_chatbot
```

Or using psql:

```sql
CREATE DATABASE todo_chatbot;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL: Your PostgreSQL connection string
# - GOOGLE_API_KEY: Your Google API key

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Reference

### Chat Endpoint

```
POST /api/{user_id}/chat
```

Request body:
```json
{
  "conversation_id": 1,  // optional
  "message": "Add a task to buy groceries"
}
```

Response:
```json
{
  "conversation_id": 1,
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {"title": "buy groceries"},
      "result": {"task_id": 1, "status": "created", "title": "buy groceries"}
    }
  ]
}
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task |
| `list_tasks` | List all tasks (can filter by pending/completed) |
| `complete_task` | Mark a task as done |
| `delete_task` | Remove a task |
| `update_task` | Modify task title or description |

## Example Conversations

**Create a task:**
```
User: "Remind me to call mom tomorrow"
AI: "I've added 'call mom tomorrow' to your tasks."
```

**List tasks:**
```
User: "What do I need to do?"
AI: "Here are your tasks:
1. Buy groceries (pending)
2. Call mom tomorrow (pending)"
```

**Complete a task:**
```
User: "I finished buying groceries"
AI: "Great! I've marked 'Buy groceries' as completed."
```

**Delete a task:**
```
User: "Delete task 2"
AI: "Done! I've removed 'Call mom tomorrow' from your list."
```

## Project Structure

```
phase-3/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── agent/         # Gemini AI agent
│   │   ├── crud/          # Database operations
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database connection
│   │   └── main.py        # FastAPI app
│   ├── mcp_server/        # MCP tool server
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   └── lib/           # API client
│   └── package.json
└── README.md
```

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/todo_chatbot` |
| `GOOGLE_API_KEY` | Google Gemini API key | Required |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## License

MIT
