"""
Storage Client - Unified interface for OSS/MinIO storage
"""
from typing import Optional
from urllib.parse import urljoin
from loguru import logger
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
        logger.info(f"Initialized StorageClient in {self.config.mode} mode")

    def _get_client(self):
        """Lazy initialization of storage client"""
        if self._client is None:
            try:
                if self.config.mode == "minio":
                    from minio import Minio
                    self._client = Minio(
                        self.config.minio_endpoint.replace("http://", "").replace("https://", "") if self.config.minio_endpoint else "localhost:9000",
                        access_key=self.config.minio_access_key or "minioadmin",
                        secret_key=self.config.minio_secret_key or "minioadmin",
                        secure=self.config.minio_endpoint.startswith("https") if self.config.minio_endpoint else False
                    )
                    # Ensure bucket exists
                    if not self._client.bucket_exists(self.config.bucket_name):
                        logger.info(f"Creating bucket: {self.config.bucket_name}")
                        self._client.make_bucket(self.config.bucket_name)
                    else:
                        logger.debug(f"Bucket {self.config.bucket_name} already exists")
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
                    logger.info(f"Connected to OSS bucket: {self.config.bucket_name}")
                else:
                    raise ValueError(f"Unsupported storage mode: {self.config.mode}")
            except Exception as e:
                logger.error(f"Failed to initialize storage client: {e}")
                raise
        return self._client

    def upload_content(self, object_name: str, content: bytes) -> str:
        """Upload content to storage and return URL"""
        client = self._get_client()
        logger.info(f"Uploading content to {object_name} ({len(content)} bytes)")

        try:
            if self.config.mode == "minio":
                client.put_object(
                    self.config.bucket_name,
                    object_name,
                    data=content, # Minio expects a stream or bytes/buffer
                    length=len(content),
                )
            elif self.config.mode == "oss":
                client.put_object(object_name, content)
            
            url = urljoin(self.config.base_url, object_name)
            logger.success(f"Successfully uploaded to {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to upload content to {object_name}: {e}")
            raise

    def get_content(self, object_name: str) -> bytes:
        """Download content from storage and return bytes"""
        client = self._get_client()
        logger.info(f"Retrieving content for {object_name}")

        try:
            if self.config.mode == "minio":
                response = client.get_object(self.config.bucket_name, object_name)
                try:
                    data = response.read()
                    logger.debug(f"Downloaded {len(data)} bytes from {object_name}")
                    return data
                finally:
                    response.close()
                    response.release_conn()
            elif self.config.mode == "oss":
                data = client.get_object(object_name).read()
                logger.debug(f"Downloaded {len(data)} bytes from {object_name}")
                return data
        except Exception as e:
            logger.error(f"Failed to get content for {object_name}: {e}")
            raise
        return b""

    def upload_file(self, object_name: str, file_path: str) -> str:
        """Upload local file to storage"""
        logger.info(f"Uploading file {file_path} to {object_name}")
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return self.upload_content(object_name, content)
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise

    def delete_content(self, object_name: str) -> bool:
        """Delete object from storage (alias for delete_file for API consistency)"""
        return self.delete_file(object_name)

    def delete_file(self, object_name: str) -> bool:
        """Delete file from storage"""
        client = self._get_client()
        logger.warning(f"Deleting object: {object_name}")

        try:
            if self.config.mode == "minio":
                client.remove_object(self.config.bucket_name, object_name)
            elif self.config.mode == "oss":
                client.delete_object(object_name)
            logger.success(f"Successfully deleted {object_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {object_name}: {e}")
            return False

    def get_url(self, object_name: str) -> str:
        """Get public URL for object"""
        return urljoin(self.config.base_url, object_name)


# Default instance - configured from settings
from app.config import settings

_storage_client = None


def get_storage_client() -> StorageClient:
    """Get or create storage client with settings from config"""
    global _storage_client
    if _storage_client is None:
        try:
            config = StorageConfig(
                mode=settings.storage_mode,
                base_url=settings.minio_endpoint, # Note: this should be the public URL base
                bucket_name=settings.minio_bucket,
                minio_access_key=settings.minio_access_key or "minioadmin",
                minio_secret_key=settings.minio_secret_key or "minioadmin",
                minio_endpoint=settings.minio_endpoint,
                oss_access_key_id=settings.oss_access_key_id,
                oss_access_key_secret=settings.oss_access_key_secret,
                oss_endpoint=settings.oss_endpoint,
            )
            _storage_client = StorageClient(config)
        except Exception as e:
            logger.critical(f"Failed to create StorageClient globally: {e}")
            # Fallback or initialization error
            _storage_client = StorageClient() 

    return _storage_client


storage_client = get_storage_client()
