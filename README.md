# Hackathon 2 - TODO App

AI-powered Task Management Application built for the hackathon.

## Project Structure

```
├── phase-1/          # Phase 1 - Initial prototype
├── phase-2/          # Phase 2 - Full-stack application with deployment
│   ├── backend/      # FastAPI backend
│   ├── frontend/     # Next.js frontend
│   ├── helm/         # Kubernetes Helm charts
│   ├── scripts/      # Deployment scripts
│   └── ...
└── README.md
```

## Phase 1

Initial prototype and planning.

## Phase 2

Full-stack Q.TODO application with:
- User authentication (Better Auth)
- AI-powered task assistant (Groq LLM)
- PostgreSQL database (Neon)
- Docker containerization
- Kubernetes deployment (Helm charts)

See [phase-2/README.md](./phase-2/README.md) for detailed setup instructions.

## Tech Stack

- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLModel, Python 3.11
- **Database:** PostgreSQL (Neon)
- **AI:** Groq LLM, LangChain
- **DevOps:** Docker, Kubernetes, Helm

## Quick Start

```bash
cd phase-2

# Setup backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
uvicorn main:app --reload

# Setup frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local  # Edit with your values
npm run dev
```

## Deployment

See [phase-2/DEPLOYMENT.md](./phase-2/DEPLOYMENT.md) for cloud deployment instructions.

## License

MIT
