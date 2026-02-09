"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router

app = FastAPI(
    title="Todo AI Chatbot",
    description="AI-powered chatbot for managing todos through natural language",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Todo AI Chatbot"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
