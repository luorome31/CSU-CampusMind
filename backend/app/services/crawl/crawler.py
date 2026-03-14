"""
Crawl Service - Web content crawling and storage
"""
import asyncio
import hashlib
import uuid
from datetime import datetime
from typing import Optional, List
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from loguru import logger


class CrawlService:
    """Service for crawling web content and storing to OSS"""

    def __init__(self):
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
        )

    async def crawl_url(
        self,
        url: str,
        markdown_generator=None,
    ) -> dict:
        """
        Crawl a single URL and return content

        Args:
            url: The URL to crawl
            markdown_generator: Optional custom markdown generator

        Returns:
            dict with keys: markdown, html, success, error
        """
        try:
            if markdown_generator is None:
                markdown_generator = DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter()
                )

            crawler_config = CrawlerRunConfig(
                markdown_generator=markdown_generator,
            )

            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=url, config=crawler_config)

                if result.success:
                    return {
                        "success": True,
                        "markdown": result.markdown.raw_markdown,
                        "html": result.html,
                        "url": result.url,
                        "title": result.metadata.get("title", "") if result.metadata else "",
                    }
                else:
                    return {
                        "success": False,
                        "error": result.error_message or "Unknown error",
                        "url": url,
                    }
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    async def crawl_urls(self, urls: List[str]) -> List[dict]:
        """Crawl multiple URLs concurrently"""
        tasks = [self.crawl_url(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

    def generate_storage_key(self, url: str, file_format: str = "md") -> str:
        """Generate a unique storage key for the crawled content"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        parsed = urlparse(url)
        domain = parsed.netloc.replace(".", "_")
        return f"crawl/{domain}_{url_hash}_{timestamp}.{file_format}"

    async def crawl_and_prepare_for_storage(
        self,
        url: str,
    ) -> dict:
        """
        Crawl URL and prepare content for OSS storage

        Returns:
            dict with keys: content, storage_key, metadata
        """
        result = await self.crawl_url(url)

        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
            }

        storage_key = self.generate_storage_key(url)
        metadata = {
            "url": url,
            "title": result.get("title", ""),
            "crawled_at": datetime.now().isoformat(),
            "content_type": "text/markdown",
        }

        return {
            "success": True,
            "content": result["markdown"],
            "storage_key": storage_key,
            "metadata": metadata,
        }


# Singleton instance
crawl_service = CrawlService()
