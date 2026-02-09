import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/todo_chatbot"
    )
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


settings = Settings()
