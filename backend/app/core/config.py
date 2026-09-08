"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file or system environment.
"""

from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # App Information
    APP_ENV: str = Field(default="development", description="Runtime environment")
    APP_NAME: str = Field(default="Drug Information Q&A Agent")
    API_PORT: int = Field(default=8000)
    API_HOST: str = Field(default="127.0.0.1")

    # LLM Settings (Google Gemini)
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini model name")

    # Embeddings Engine
    EMBEDDING_PROVIDER: str = Field(default="local", description="'local' or 'gemini'")
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    # Storage Paths
    SQLITE_DB_PATH: str = Field(default="./data/app.db")
    CHROMA_PERSIST_DIR: str = Field(default="./data/chroma")
    UPLOAD_DIR: str = Field(default="./data/uploads")

    # Security & Access
    ADMIN_PASSCODE: str = Field(default="admin123", description="Passcode required for PDF upload")
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")

    # Medical RAG & Guardrail Settings
    SIMILARITY_THRESHOLD: float = Field(default=0.75, description="Cosine distance threshold")
    MAX_RETRIEVAL_CHUNKS: int = Field(default=5, description="Top-k chunks to retrieve")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        """Convert comma-separated CORS origins into a list."""
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def ensure_directories(self) -> None:
        """Ensure necessary data and storage directories exist."""
        Path(self.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(self.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
