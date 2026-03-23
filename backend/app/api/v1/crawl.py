"""
Crawl API - Web content crawling endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from app.services.crawl.crawler import crawl_service
from app.services.storage.client import storage_client
from app.services.knowledge_file import KnowledgeFileService
from app.services.crawl.task_service import CrawlTaskService
from app.services.crawl.task_worker import process_batch_crawl, process_batch_crawl_with_knowledge
from app.database.models.crawl_task import CrawlTask
from app.api.dependencies import get_current_user


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
    enable_vector: bool = Field(default=True, description="Enable vector storage")
    enable_keyword: bool = Field(default=True, description="Enable keyword storage")


class CrawlBatchWithKnowledgeRequest(BaseModel):
    """Request model for batch crawling with knowledge base"""
    urls: List[str] = Field(..., description="List of URLs to crawl")
    knowledge_id: str = Field(..., description="Knowledge base ID")
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


class CrawlTaskResponse(BaseModel):
    """Response model for async crawl task submission"""
    task_id: str
    status: str
    message: str


@router.get("/crawl/tasks", response_model=List[CrawlTask])
async def list_crawl_tasks(
    current_user: dict = Depends(get_current_user)
):
    """List all crawl tasks for the current user"""
    return CrawlTaskService.list_tasks(current_user["user_id"])


@router.get("/crawl/tasks/{task_id}", response_model=CrawlTask)
async def get_crawl_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the progress and status of a batch crawl task"""
    task = CrawlTaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Ownership check
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No permission to access this task")

    return task


@router.post("/crawl/create", response_model=CrawlResponse)
async def crawl_url(
    request: CrawlRequest,
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(get_current_user)
):
    """
    Crawl URL, store to OSS, create knowledge_file record, and index to vector/keyword DB

    End-to-end flow: crawl -> OSS -> knowledge_file -> index
    """
    user_id = current_user["user_id"]
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
            user_id=user_id,
            oss_url=oss_url,
            object_name=storage_key,
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


@router.post("/crawl/batch", response_model=CrawlTaskResponse)
async def crawl_batch(
    request: CrawlBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Crawl multiple URLs asynchronously using BackgroundTasks

    Returns a task ID that can be polled for progress.
    """
    try:
        user_id = current_user["user_id"]
        task = CrawlTaskService.create_task(
            user_id=user_id,
            total_urls=len(request.urls),
        )

        background_tasks.add_task(
            process_batch_crawl,
            task_id=task.id,
            urls=request.urls,
            store_to_oss=request.store_to_oss,
        )

        return CrawlTaskResponse(
            task_id=task.id,
            status=task.status,
            message="Batch crawl task started",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl/batch-with-knowledge", response_model=CrawlTaskResponse)
async def crawl_batch_with_knowledge(
    request: CrawlBatchWithKnowledgeRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Crawl multiple URLs and create knowledge_file records for each asynchronously

    File records will be created with status PENDING_VERIFY allowing manual verification.
    """
    try:
        user_id = current_user["user_id"]
        task = CrawlTaskService.create_task(
            user_id=user_id,
            total_urls=len(request.urls),
            knowledge_id=request.knowledge_id,
        )

        background_tasks.add_task(
            process_batch_crawl_with_knowledge,
            task_id=task.id,
            urls=request.urls,
            knowledge_id=request.knowledge_id,
            user_id=user_id,
        )

        return CrawlTaskResponse(
            task_id=task.id,
            status=task.status,
            message="Batch crawl with knowledge task started",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
