"""
Configuration Loader - Load settings from environment
"""
import os
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseModel):
    """Application settings loaded from environment"""

    # Storage
    storage_mode: str = "minio"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "campusmind"

    # OSS (Aliyun)
    oss_endpoint: Optional[str] = None
    oss_access_key_id: Optional[str] = None
    oss_access_key_secret: Optional[str] = None
    oss_bucket: str = "campusmind"

    # Embedding
    embedding_model: str = "text-embedding-3-small"
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_api_key: Optional[str] = None

    # LLM (OpenAI)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_base_url: str = "https://api.openai.com/v1"

    # Elasticsearch
    elasticsearch_hosts: str = "http://localhost:9200"

    # ChromaDB
    chroma_persist_path: str = "./data/chroma"

    # Database
    database_url: str = "sqlite:///./campusmind.db"

    # JWC Session Storage
    session_storage_path: str = "./data/csu_sessions.json"
    password_storage_path: str = "./data/csu_passwords.json"
    password_encryption_key: str = "change-this-key-in-production"
    session_ttl_seconds: int = 30 * 60  # 30 minutes

    @classmethod
    def from_env(cls):
        """Load settings from environment variables"""
        return cls(
            storage_mode=os.getenv("STORAGE_MODE", "minio"),
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            minio_bucket=os.getenv("MINIO_BUCKET", "campusmind"),
            oss_endpoint=os.getenv("OSS_ENDPOINT"),
            oss_access_key_id=os.getenv("OSS_ACCESS_KEY_ID"),
            oss_access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET"),
            oss_bucket=os.getenv("OSS_BUCKET", "campusmind"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_base_url=os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1"),
            embedding_api_key=os.getenv("EMBEDDING_API_KEY"),
            elasticsearch_hosts=os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200"),
            chroma_persist_path=os.getenv("CHROMA_PERSIST_PATH", "./data/chroma"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./campusmind.db"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            session_storage_path=os.getenv("SESSION_STORAGE_PATH", "./data/csu_sessions.json"),
            password_storage_path=os.getenv("PASSWORD_STORAGE_PATH", "./data/csu_passwords.json"),
            password_encryption_key=os.getenv("PASSWORD_ENCRYPTION_KEY", "change-this-key-in-production"),
            session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", "1800")),
        )


# Global settings instance
settings = Settings.from_env()
