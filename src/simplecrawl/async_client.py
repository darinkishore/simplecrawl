from typing import Any, Dict, List, Optional

import httpx

from .models import (
    CrawlJob,
    CrawlStatus,
    MapResult,
    ScrapeResult,
)


class AsyncFirecrawlClient:
    """
    Asynchronous client for the firecrawl-simple API.

    Provides the same functionalities as the synchronous client, but with async/await syntax.

    Usage:
        async with AsyncFirecrawlClient(base_url="https://api.firecrawl.dev/v1") as client:
            scrape_result = await client.scrape("https://example.com")
            print(scrape_result.markdown)
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialize the AsyncFirecrawlClient.

        Args:
            base_url: The base URL for the API, e.g. "https://api.firecrawl.dev/v1"
        """
        if not base_url:
            raise ValueError("Base URL must be provided.")
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()

    async def scrape(
        self,
        url: str,
        formats: Optional[List[str]] = None,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, Any]] = None,
        wait_for: int = 0,
        timeout: int = 30000,
        extract_schema: Optional[Dict[str, Any]] = None,
        extract_system_prompt: Optional[str] = None,
        extract_prompt: Optional[str] = None,
    ) -> ScrapeResult:
        """
        Asynchronously scrape a single URL for content and metadata.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "formats": formats or ["markdown"],
            "waitFor": wait_for,
            "timeout": timeout,
        }
        if include_tags is not None:
            payload["includeTags"] = include_tags
        if exclude_tags is not None:
            payload["excludeTags"] = exclude_tags
        if headers is not None:
            payload["headers"] = headers
        if extract_schema or extract_system_prompt or extract_prompt:
            payload["extract"] = {
                "schema": extract_schema,
                "systemPrompt": extract_system_prompt,
                "prompt": extract_prompt,
            }

        resp = await self.client.post(f"{self.base_url}/scrape", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return ScrapeResult.model_validate(data["data"])

    async def crawl(
        self,
        url: str,
        exclude_paths: Optional[List[str]] = None,
        include_paths: Optional[List[str]] = None,
        max_depth: int = 2,
        ignore_sitemap: bool = True,
        limit: int = 10,
        allow_backward_links: bool = False,
        allow_external_links: bool = False,
        webhook: Optional[str] = None,
        scrape_formats: Optional[List[str]] = None,
        scrape_headers: Optional[Dict[str, Any]] = None,
        scrape_include_tags: Optional[List[str]] = None,
        scrape_exclude_tags: Optional[List[str]] = None,
        scrape_wait_for: int = 123,
    ) -> CrawlJob:
        """
        Start an asynchronous crawl job.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "maxDepth": max_depth,
            "ignoreSitemap": ignore_sitemap,
            "limit": limit,
            "allowBackwardLinks": allow_backward_links,
            "allowExternalLinks": allow_external_links,
            "scrapeOptions": {
                "formats": scrape_formats or ["markdown"],
                "waitFor": scrape_wait_for,
            },
        }

        if exclude_paths is not None:
            payload["excludePaths"] = exclude_paths
        if include_paths is not None:
            payload["includePaths"] = include_paths
        if webhook is not None:
            payload["webhook"] = webhook
        if scrape_headers is not None:
            payload["scrapeOptions"]["headers"] = scrape_headers
        if scrape_include_tags is not None:
            payload["scrapeOptions"]["includeTags"] = scrape_include_tags
        if scrape_exclude_tags is not None:
            payload["scrapeOptions"]["excludeTags"] = scrape_exclude_tags

        resp = await self.client.post(f"{self.base_url}/crawl", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return CrawlJob.model_validate(data)

    async def get_crawl_status(self, job_id: str) -> CrawlStatus:
        """
        Retrieve the status of a crawl job.
        """
        resp = await self.client.get(f"{self.base_url}/crawl/{job_id}")
        resp.raise_for_status()
        data = resp.json()
        return CrawlStatus.model_validate(data)

    async def cancel_crawl(self, job_id: str) -> bool:
        """
        Cancel a running crawl job.
        """
        resp = await self.client.delete(f"{self.base_url}/crawl/{job_id}")
        resp.raise_for_status()
        data = resp.json()
        return data.get("success", False)

    async def map(
        self,
        url: str,
        search: Optional[str] = None,
        ignore_sitemap: bool = True,
        include_subdomains: bool = False,
        limit: int = 5000,
    ) -> MapResult:
        """
        Asynchronously map URLs from a given website.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "ignoreSitemap": ignore_sitemap,
            "includeSubdomains": include_subdomains,
            "limit": limit,
        }

        if search is not None:
            payload["search"] = search

        resp = await self.client.post(f"{self.base_url}/map", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return MapResult.model_validate(data)

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.close()
