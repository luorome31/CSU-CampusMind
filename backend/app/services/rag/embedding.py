"""
Embedding Service - Text to vector conversion
"""
import asyncio
from typing import Union, List, Optional
from pydantic import BaseModel
from loguru import logger


class EmbeddingConfig(BaseModel):
    """Embedding configuration"""
    model_name: str = "text-embedding-3-small"
    base_url: str = "https://api.openai.com/v1"
    api_key: Optional[str] = None


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key or "dummy-key"  # Will be overridden
            )
        return self._client

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        client = self._get_client()
        response = await client.embeddings.create(
            model=self.config.model_name,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        if not texts:
            return []

        # Handle large batches
        if len(texts) <= 10:
            client = self._get_client()
            response = await client.embeddings.create(
                model=self.config.model_name,
                input=texts,
                encoding_format="float"
            )
            return [item.embedding for item in response.data]

        # Process in batches for larger inputs
        semaphore = asyncio.Semaphore(5)
        all_embeddings = []

        async def process_batch(batch: List[str]):
            async with semaphore:
                client = self._get_client()
                response = await client.embeddings.create(
                    model=self.config.model_name,
                    input=batch,
                    encoding_format="float"
                )
                return [item.embedding for item in response.data]

        batches = [texts[i:i + 10] for i in range(0, len(texts), 10)]
        tasks = [process_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks)

        for batch_result in results:
            all_embeddings.extend(batch_result)

        return all_embeddings


# Default embedding service instance - configured from settings
from app.config import settings

_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service with settings from config"""
    global _embedding_service
    if _embedding_service is None:
        config = EmbeddingConfig(
            model_name=settings.embedding_model,
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
        )
        _embedding_service = EmbeddingService(config)
    return _embedding_service


embedding_service = get_embedding_service()
