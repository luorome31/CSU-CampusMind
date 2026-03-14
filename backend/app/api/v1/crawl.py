"""
Crawl API - Web content crawling endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.crawl.crawler import crawl_service
from app.services.storage.client import storage_client


router = APIRouter(tags=["Crawl"])


class CrawlRequest(BaseModel):
    """Request model for crawling"""
    url: str = Field(..., description="URL to crawl")
    store_to_oss: bool = Field(default=True, description="Whether to store content to OSS")


class CrawlBatchRequest(BaseModel):
    """Request model for batch crawling"""
    urls: List[str] = Field(..., description="List of URLs to crawl")
    store_to_oss: bool = Field(default=True, description="Whether to store content to OSS")


class CrawlResponse(BaseModel):
    """Response model for crawl result"""
    success: bool
    url: str
    oss_url: Optional[str] = None
    title: Optional[str] = None
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


@router.post("/crawl/batch", response_model=List[CrawlResponse])
async def crawl_urls(
    request: CrawlBatchRequest,
):
    """
    Crawl multiple URLs and optionally store to OSS
    """
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
