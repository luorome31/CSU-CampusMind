"""
Crawl Task Worker - Background execution for batch crawling
"""
import asyncio
from typing import List

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from loguru import logger

from app.services.crawl.crawler import crawl_service, clean_error_message
from app.services.storage.client import storage_client
from app.services.knowledge_file import KnowledgeFileService
from app.services.crawl.task_service import CrawlTaskService


async def process_batch_crawl(
    task_id: str,
    urls: List[str],
    store_to_oss: bool,
):
    """Background task to crawl URLs and update CrawlTask progress"""
    try:
        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            async def _crawl_one(url: str):
                try:
                    result = await crawler.arun(url=url, config=run_config, session_id="batch")
                    if not result.success:
                        clean_error = clean_error_message(result.error_message, url)
                        CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=clean_error)
                        return

                    if store_to_oss:
                        storage_key = crawl_service.generate_storage_key(url)
                        content = result.markdown.raw_markdown.encode("utf-8")
                        storage_client.upload_content(storage_key, content)

                    CrawlTaskService.update_task_progress(task_id, success=True, url=url)
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=str(e))

            # Limit concurrency
            sem = asyncio.Semaphore(5)

            async def _sem_task(coro):
                async with sem:
                    return await coro

            tasks = [_sem_task(_crawl_one(url)) for url in urls]
            await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Batch crawl task {task_id} failed: {e}")
        CrawlTaskService.mark_task_failed(task_id)


async def process_batch_crawl_with_knowledge(
    task_id: str,
    urls: List[str],
    knowledge_id: str,
    user_id: str,
):
    """Background task to crawl URLs, create KnowledgeFile records, and update progress"""
    from app.database.models.knowledge_file import FileStatus

    try:
        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            async def _crawl_one(url: str):
                try:
                    result = await crawler.arun(url=url, config=run_config, session_id="batch_k")
                    if not result.success:
                        clean_error = clean_error_message(result.error_message, url)
                        CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=clean_error)
                        return

                    storage_key = crawl_service.generate_storage_key(url)
                    content = result.markdown.raw_markdown.encode("utf-8")
                    oss_url = storage_client.upload_content(storage_key, content)

                    file_name = storage_key.split("/")[-1]
                    knowledge_file = KnowledgeFileService.create_knowledge_file(
                        file_name=file_name,
                        knowledge_id=knowledge_id,
                        user_id=user_id,
                        oss_url=oss_url,
                        object_name=storage_key,
                        file_size=len(content),
                    )

                    # Update status to PENDING_VERIFY instead of indexing right away
                    KnowledgeFileService.update_file_status(knowledge_file.id, FileStatus.PENDING_VERIFY)
                    CrawlTaskService.update_task_progress(task_id, success=True, url=url)
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    CrawlTaskService.update_task_progress(task_id, success=False, url=url, error=str(e))

            sem = asyncio.Semaphore(5)

            async def _sem_task(coro):
                async with sem:
                    return await coro

            sem_tasks = [_sem_task(_crawl_one(url)) for url in urls]
            await asyncio.gather(*sem_tasks)

    except Exception as e:
        logger.error(f"Batch crawl knowledge task {task_id} failed: {e}")
        CrawlTaskService.mark_task_failed(task_id)
