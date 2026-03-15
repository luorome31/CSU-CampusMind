"""
Storage Client - Unified interface for OSS/MinIO storage
"""
import os
from typing import Optional
from urllib.parse import urljoin

from pydantic import BaseModel


class StorageConfig(BaseModel):
    """Storage configuration"""
    mode: str = "minio"  # "minio" or "oss"
    base_url: str = "http://localhost:9000"
    bucket_name: str = "campusmind"

    # MinIO settings
    minio_access_key: Optional[str] = None
    minio_secret_key: Optional[str] = None
    minio_endpoint: Optional[str] = "localhost:9000"

    # OSS settings
    oss_access_key_id: Optional[str] = None
    oss_access_key_secret: Optional[str] = None
    oss_endpoint: Optional[str] = None


class StorageClient:
    """Unified storage client for OSS/MinIO"""

    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self._client = None

    def _get_client(self):
        """Lazy initialization of storage client"""
        if self._client is None:
            if self.config.mode == "minio":
                from minio import Minio
                self._client = Minio(
                    self.config.minio_endpoint or "localhost:9000",
                    access_key=self.config.minio_access_key or "minioadmin",
                    secret_key=self.config.minio_secret_key or "minioadmin",
                )
                # Ensure bucket exists
                if not self._client.bucket_exists(self.config.bucket_name):
                    self._client.make_bucket(self.config.bucket_name)
            elif self.config.mode == "oss":
                import oss2
                auth = oss2.Auth(
                    self.config.oss_access_key_id,
                    self.config.oss_access_key_secret
                )
                self._client = oss2.Bucket(
                    auth=auth,
                    endpoint=self.config.oss_endpoint,
                    bucket_name=self.config.bucket_name
                )
            else:
                raise ValueError(f"Unsupported storage mode: {self.config.mode}")
        return self._client

    def upload_content(self, object_name: str, content: bytes) -> str:
        """Upload content to storage and return URL"""
        client = self._get_client()

        if self.config.mode == "minio":
            client.put_object(
                object_name,
                content,
                length=len(content),
            )
        elif self.config.mode == "oss":
            client.put_object(object_name, content)

        return urljoin(self.config.base_url, object_name)

    def upload_file(self, object_name: str, file_path: str) -> str:
        """Upload local file to storage"""
        client = self._get_client()

        with open(file_path, 'rb') as f:
            content = f.read()

        return self.upload_content(object_name, content)

    def download_file(self, object_name: str, local_path: str) -> None:
        """Download file from storage to local path"""
        client = self._get_client()

        if self.config.mode == "minio":
            client.fget_object(self.config.bucket_name, object_name, local_path)
        elif self.config.mode == "oss":
            client.get_object_to_file(object_name, local_path)

    def get_url(self, object_name: str) -> str:
        """Get public URL for object"""
        return urljoin(self.config.base_url, object_name)

    def delete_file(self, object_name: str) -> None:
        """Delete file from storage"""
        client = self._get_client()

        if self.config.mode == "minio":
            client.remove_object(self.config.bucket_name, object_name)
        elif self.config.mode == "oss":
            client.delete_object(object_name)


# Default instance - configured from settings
from app.config import settings

_storage_client = None


def get_storage_client() -> StorageClient:
    """Get or create storage client with settings from config"""
    global _storage_client
    if _storage_client is None:
        config = StorageConfig(
            mode=settings.storage_mode,
            base_url=settings.minio_endpoint,
            bucket_name=settings.minio_bucket,
            minio_access_key=settings.minio_access_key or "minioadmin",
            minio_secret_key=settings.minio_secret_key or "minioadmin",
            minio_endpoint=settings.minio_endpoint,
            oss_access_key_id=settings.oss_access_key_id,
            oss_access_key_secret=settings.oss_access_key_secret,
            oss_endpoint=settings.oss_endpoint,
        )
        _storage_client = StorageClient(config)
    return _storage_client


storage_client = get_storage_client()
