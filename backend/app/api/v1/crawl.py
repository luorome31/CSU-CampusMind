"""
Crawl API - Web content crawling endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.crawl.crawler import crawl_service
from app.services.storage.client import storage_client
from app.services.knowledge_file import KnowledgeFileService


router = APIRouter(tags=["Crawl"])


class CrawlRequest(BaseModel):
    """Request model for crawling single URL"""
    url: str = Field(..., description="URL to crawl")
    store_to_oss: bool = Field(default=True, description="Whether to store content to OSS")


class CrawlBatchRequest(BaseModel):
    """Request model for batch crawling"""
    urls: List[str] = Field(..., description="List of URLs to crawl")
    store_to_oss: bool = Field(default=True, description="Whether to store content to OSS")


class CrawlAndIndexRequest(BaseModel):
    """Request model for crawling and indexing in one go"""
    url: str = Field(..., description="URL to crawl")
    knowledge_id: str = Field(..., description="Knowledge base ID to store the crawled content")
    user_id: str = Field(default="system", description="User ID")
    enable_vector: bool = Field(default=True, description="Enable vector storage")
    enable_keyword: bool = Field(default=True, description="Enable keyword storage")


class CrawlBatchWithKnowledgeRequest(BaseModel):
    """Request model for batch crawling with knowledge base"""
    urls: List[str] = Field(..., description="List of URLs to crawl")
    knowledge_id: str = Field(..., description="Knowledge base ID")
    user_id: str = Field(default="system", description="User ID")
    enable_vector: bool = Field(default=True, description="Enable vector storage")
    enable_keyword: bool = Field(default=True, description="Enable keyword storage")


class CrawlResponse(BaseModel):
    """Response model for crawl result"""
    success: bool
    url: str
    oss_url: Optional[str] = None
    title: Optional[str] = None
    file_id: Optional[str] = None
    error: Optional[str] = None


@router.post("/crawl/create", response_model=CrawlResponse)
async def crawl_url(
    request: CrawlRequest,
):
    """
    Crawl a single URL and optionally store to OSS

    Returns the crawled content URL in OSS
    """
    try:
        # Crawl the URL
        result = await crawl_service.crawl_and_prepare_for_storage(request.url)

        if not result["success"]:
            return CrawlResponse(
                success=False,
                url=request.url,
                error=result.get("error", "Unknown error"),
            )

        # Store to OSS if requested
        oss_url = None
        if request.store_to_oss:
            content = result["content"].encode("utf-8")
            storage_key = result["storage_key"]
            oss_url = storage_client.upload_content(storage_key, content)

        return CrawlResponse(
            success=True,
            url=request.url,
            oss_url=oss_url,
            title=result["metadata"].get("title", ""),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl/create-and-index", response_model=CrawlResponse)
async def crawl_and_index(
    request: CrawlAndIndexRequest,
):
    """
    Crawl URL, store to OSS, create knowledge_file record, and index to vector/keyword DB

    End-to-end flow: crawl -> OSS -> knowledge_file -> index
    """
    try:
        # Step 1: Crawl the URL
        crawl_result = await crawl_service.crawl_and_prepare_for_storage(request.url)

        if not crawl_result["success"]:
            return CrawlResponse(
                success=False,
                url=request.url,
                error=crawl_result.get("error", "Unknown error"),
            )

        # Step 2: Store to OSS
        content = crawl_result["content"].encode("utf-8")
        storage_key = crawl_result["storage_key"]
        oss_url = storage_client.upload_content(storage_key, content)

        # Step 3: Create knowledge_file record
        file_name = storage_key.split("/")[-1]
        knowledge_file = KnowledgeFileService.create_knowledge_file(
            file_name=file_name,
            knowledge_id=request.knowledge_id,
            user_id=request.user_id,
            oss_url=oss_url,
            file_size=len(content),
        )

        # Step 4: Index to vector/keyword DB
        from app.services.rag.indexer import indexer
        index_result = await indexer.index_content(
            content=crawl_result["content"],
            knowledge_id=request.knowledge_id,
            source_name=file_name,
            metadata={
                "file_id": knowledge_file.id,
                "enable_vector": request.enable_vector,
                "enable_keyword": request.enable_keyword
            }
        )

        # Update file status based on indexing result
        if index_result.get("success"):
            KnowledgeFileService.update_file_status(knowledge_file.id, "success")
        else:
            KnowledgeFileService.update_file_status(knowledge_file.id, "fail")

        return CrawlResponse(
            success=True,
            url=request.url,
            oss_url=oss_url,
            title=crawl_result["metadata"].get("title", ""),
            file_id=knowledge_file.id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl/batch", response_model=List[CrawlResponse])
async def crawl_batch(
    request: CrawlBatchRequest,
):
    """Crawl multiple URLs and optionally store to OSS"""
    try:
        results = []

        for url in request.urls:
            result = await crawl_service.crawl_and_prepare_for_storage(url)

            if not result["success"]:
                results.append(CrawlResponse(
                    success=False,
                    url=url,
                    error=result.get("error", "Unknown error"),
                ))
                continue

            oss_url = None
            if request.store_to_oss:
                content = result["content"].encode("utf-8")
                storage_key = result["storage_key"]
                oss_url = storage_client.upload_content(storage_key, content)

            results.append(CrawlResponse(
                success=True,
                url=url,
                oss_url=oss_url,
                title=result["metadata"].get("title", ""),
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl/batch-with-knowledge", response_model=List[CrawlResponse])
async def crawl_batch_with_knowledge(
    request: CrawlBatchWithKnowledgeRequest,
):
    """
    Crawl multiple URLs and create knowledge_file records for each

    End-to-end flow for multiple URLs: crawl -> OSS -> knowledge_file -> index
    """
    from app.services.rag.indexer import indexer

    results = []
    for url in request.urls:
        try:
            # Step 1: Crawl
            crawl_result = await crawl_service.crawl_and_prepare_for_storage(url)

            if not crawl_result["success"]:
                results.append(CrawlResponse(
                    success=False,
                    url=url,
                    error=crawl_result.get("error", "Unknown error"),
                ))
                continue

            # Step 2: Store to OSS
            content = crawl_result["content"].encode("utf-8")
            storage_key = crawl_result["storage_key"]
            oss_url = storage_client.upload_content(storage_key, content)

            # Step 3: Create knowledge_file
            file_name = storage_key.split("/")[-1]
            knowledge_file = KnowledgeFileService.create_knowledge_file(
                file_name=file_name,
                knowledge_id=request.knowledge_id,
                user_id=request.user_id,
                oss_url=oss_url,
                file_size=len(content),
            )

            # Step 4: Index
            index_result = await indexer.index_content(
                content=crawl_result["content"],
                knowledge_id=request.knowledge_id,
                source_name=file_name,
                metadata={"file_id": knowledge_file.id}
            )

            # Update status
            if index_result.get("success"):
                KnowledgeFileService.update_file_status(knowledge_file.id, "success")
            else:
                KnowledgeFileService.update_file_status(knowledge_file.id, "fail")

            results.append(CrawlResponse(
                success=True,
                url=url,
                oss_url=oss_url,
                title=crawl_result["metadata"].get("title", ""),
                file_id=knowledge_file.id,
            ))

        except Exception as e:
            results.append(CrawlResponse(
                success=False,
                url=url,
                error=str(e),
            ))

    return results
