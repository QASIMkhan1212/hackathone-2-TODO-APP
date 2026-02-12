# Q.TODO - AI-Powered Task Management App

A full-stack TODO application with AI-powered task management built with FastAPI (backend) and Next.js (frontend).

## Features

- User authentication with Better Auth
- Task management (Create, Read, Update, Delete)
- AI-powered task assistant using Groq LLM
- PostgreSQL database (Neon)
- Modern UI with Tailwind CSS
- Responsive design
- Kubernetes deployment ready (Helm charts included)

## Tech Stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Better Auth

### Backend
- FastAPI
- SQLModel
- PostgreSQL (Neon)
- Groq AI
- LangChain

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL database (Neon recommended)
- Groq API key

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd phase-2
```

### 2. Environment Variables

Copy the example environment files and fill in your values:

#### Backend
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
DATABASE_URL="postgresql://user:password@host/database?sslmode=require"
BETTER_AUTH_SECRET="your-secret-key"
BETTER_AUTH_URL="http://localhost:3000"
GROQ_API_KEY="your-groq-api-key"
FRONTEND_URL="http://localhost:3000"
```

#### Frontend
```bash
cp frontend/.env.example frontend/.env.local
```

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:8000"
DATABASE_URL="postgresql://user:password@host/database?sslmode=require"
BETTER_AUTH_SECRET="your-secret-key"
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
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

### Option 1: Vercel + Railway (Recommended)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

**Quick steps:**
1. Deploy backend to Railway/Render
2. Deploy frontend to Vercel
3. Configure environment variables

### Option 2: Kubernetes (Minikube)

See [KUBERNETES.md](./KUBERNETES.md) for detailed instructions.

**Quick steps:**
```bash
# Windows
.\scripts\deploy.ps1

# Linux/macOS
./scripts/deploy.sh
```

### Option 3: Docker Compose (Local)

```bash
docker-compose up --build
```

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── security.py      # Authentication
│   ├── database.py      # Database connection
│   ├── agent/           # AI agent code
│   ├── Dockerfile       # Docker configuration
│   └── .env.example     # Environment template
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/        # App router pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities & hooks
│   ├── public/         # Static assets
│   ├── Dockerfile      # Docker configuration
│   └── .env.example    # Environment template
├── helm/               # Kubernetes Helm charts
│   └── qtodo/
├── scripts/            # Deployment scripts
├── docker-compose.yml  # Local Docker setup
├── DEPLOYMENT.md       # Cloud deployment guide
├── KUBERNETES.md       # K8s deployment guide
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/tasks/{user_id}` | Get user's tasks |
| POST | `/api/tasks/{user_id}` | Create a task |
| PUT | `/api/tasks/{user_id}/{task_id}` | Update a task |
| DELETE | `/api/tasks/{user_id}/{task_id}` | Delete a task |
| POST | `/api/chat` | Chat with AI assistant |

## Environment Variables

### Backend
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Secret key for JWT |
| `BETTER_AUTH_URL` | Frontend URL |
| `GROQ_API_KEY` | Groq API key for AI |
| `FRONTEND_URL` | Frontend URL (CORS) |

### Frontend
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_APP_URL` | Frontend URL |
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `DATABASE_URL` | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Secret key for JWT |

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
