"""Configuration settings"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./assets.db")
    
    # JWT Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # AI Search (OpenAI compatible)
    AI_API_URL: str = os.getenv("AI_API_URL", "http://localhost:11434/v1")
    AI_MODEL: str = os.getenv("AI_MODEL", "qwen2.5:3b")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "ollama")
    
    class Config:
        env_file = ".env"

settings = Settings()
