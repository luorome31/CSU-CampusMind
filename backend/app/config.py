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

    # Elasticsearch
    elasticsearch_hosts: str = "http://localhost:9200"

    # ChromaDB
    chroma_persist_path: str = "./data/chroma"

    # Database
    database_url: str = "sqlite:///./campusmind.db"

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
        )


# Global settings instance
settings = Settings.from_env()
