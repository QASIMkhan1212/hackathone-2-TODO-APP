# Hackathon TODO App

A full-stack TODO application with AI-powered task management built with FastAPI (backend) and Next.js (frontend).

## Features

- 🔐 User authentication with Better Auth
- ✅ Task management (Create, Read, Update, Delete)
- 🤖 AI-powered task assistant using Groq
- 💾 PostgreSQL database (Neon)
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive design

## Tech Stack

### Frontend
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Better Auth

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Groq AI
- LangChain

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL database (Neon recommended)
- Groq API key

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/QASIMkhan1212/hackathone-2-TODO-APP.git
cd hackathone-2-TODO-APP
```

### 2. Environment Variables

Copy the secrets from `SECRETS.env` (not in repo) to create your environment files:

#### Backend `.env`
```env
DATABASE_URL="your_postgresql_connection_string"
BETTER_AUTH_SECRET="your_secret_key_here"
BETTER_AUTH_URL="http://localhost:3000"
GROQ_API_KEY="your_groq_api_key"
```

#### Frontend `.env.local`
```env
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:8000"
DATABASE_URL="your_postgresql_connection_string"
BETTER_AUTH_SECRET="your_secret_key_here"
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend will run on `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

## Deployment

### Deploy to Vercel

1. Push your code to GitHub
2. Import project to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy!

### Environment Variables for Vercel

Add these in your Vercel project settings:

**Frontend:**
- `NEXT_PUBLIC_APP_URL` - Your Vercel app URL
- `NEXT_PUBLIC_API_URL` - Your backend API URL
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Secret for auth

**Backend:**
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Same as frontend
- `BETTER_AUTH_URL` - Your Vercel app URL
- `GROQ_API_KEY` - Your Groq API key

## Project Structure

```
├── backend/           # FastAPI backend
│   ├── main.py       # Main application
│   ├── models.py     # Database models
│   ├── schemas.py    # Pydantic schemas
│   └── agent/        # AI agent code
├── frontend/         # Next.js frontend
│   ├── src/
│   │   ├── app/     # App router pages
│   │   ├── components/
│   │   └── lib/     # Utilities
│   └── public/
└── README.md
```

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `POST /api/chat` - Chat with AI assistant

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
