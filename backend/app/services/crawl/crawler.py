"""
Crawl Service - Web content crawling and storage
"""
import asyncio
import hashlib
import re
from datetime import datetime
from typing import List
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from loguru import logger


def clean_error_message(error_msg: str, url: str = "") -> str:
    """
    Clean up error message to remove technical details like Python tracebacks.
    Returns a user-friendly error message.
    """
    if not error_msg:
        return "未知错误"

    # Extract the URL from error message if not provided
    if not url:
        url_match = re.search(r'https?://[^\s]+', error_msg)
        if url_match:
            url = url_match.group(0).rstrip('.,;:')

    # Map common errors to user-friendly messages
    error_mappings = [
        # DNS/Network errors
        (r'ERR_NAME_NOT_RESOLVED|DNS.*not resolved', 'DNS解析失败'),
        (r'ERR_CONNECTION_REFUSED|Connection refused', '连接被拒绝'),
        (r'ERR_CONNECTION_TIMED_OUT|Connection timed out', '连接超时'),
        (r'ERR_CONNECTION_RESET|Connection reset', '连接被重置'),
        (r'net::ERR_|Error:\s*', ''),  # Clean up remaining net::ERR_ prefixes

        # HTTP errors
        (r'HTTP\s*error\s*(\d+)', r'HTTP错误 \1'),
        (r'404|Not Found', '页面不存在 (404)'),
        (r'403|Forbidden', '访问被拒绝 (403)'),
        (r'500|Internal Server Error', '服务器内部错误'),

        # Browser/crawl errors
        (r'Timeout|timeout', '加载超时'),
        (r'SSL|ssl', 'SSL证书错误'),
        (r'Invalid URL|url.*invalid', '无效的URL'),
    ]

    # Check for known error patterns
    for pattern, replacement in error_mappings:
        if re.search(pattern, error_msg, re.IGNORECASE):
            # Extract the key error info
            for match in re.finditer(pattern, error_msg, re.IGNORECASE):
                return f"{replacement}" if replacement else match.group(0)

    # If no pattern matched, truncate long tracebacks
    # Find the first line that looks like an actual error
    lines = error_msg.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('File ', '  ', 'at ', 'Call log:', 'Code context:')):
            # Clean up the line
            clean_line = re.sub(r'\s+', ' ', line)
            # Truncate if too long
            if len(clean_line) > 100:
                clean_line = clean_line[:100] + '...'
            return clean_line

    # Fallback: just return the first meaningful line
    return lines[0][:100] if lines else "未知错误"


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
