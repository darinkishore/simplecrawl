import os
from typing import Any, Dict, List, Optional

import httpx

from .models import CrawlJob, CrawlStatus, MapResult, ScrapeResult
from dotenv import load_dotenv
# TODO: handle screenshot formats


class AsyncClient:
    """
    Asynchronous client for the Firecrawl web scraping API.

    Provides asynchronous methods to scrape single pages, crawl multiple pages,
    and discover URLs on websites. Should be used with async context manager
    or explicitly closed.

    Args:
        token: API authentication token
        base_url: API endpoint (default: https://api.firecrawl.dev/v1)

    Basic Usage:

    ```python
    async with AsyncClient(token="your-api-token") as client:
        # Scrape a single page
        result = await client.scrape("https://example.com")
        print(result.markdown)  # Print markdown content
        print(result.metadata.title)  # Print page title

        # Scrape with multiple formats
        result = await client.scrape(
            "https://example.com",
            formats=["markdown", "html", "links"]
        )
    ```

    Alternative usage:
    ```python
    client = AsyncClient(token="your-api-token")
    try:
        result = await client.scrape("https://example.com")
    finally:
        await client.close()
    ```
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = os.getenv("FIRECRAWL_BASE_URL", None),
    ):
        load_dotenv()
        if not base_url:
            raise ValueError("Base URL is required")
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()
        if token:
            self.client.headers.update({"Authorization": f"Bearer {token}"})

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
        Asynchronously scrape content from a single URL.

        Args:
            url: The webpage to scrape
            formats: Content formats to retrieve (default: ["markdown"])
            include_tags: HTML elements to include (e.g., ["article", "main"])
            exclude_tags: HTML elements to exclude (e.g., ["nav", "footer"])
            headers: Custom HTTP headers for the request
            wait_for: Milliseconds to wait before scraping (for JS content)
            timeout: Request timeout in milliseconds
            extract_schema: JSON schema for structured data extraction
            extract_system_prompt: System prompt for AI extraction
            extract_prompt: User prompt for AI extraction

        Returns:
            ScrapeResult containing the requested content formats and metadata

        Examples:
            ```python
            async with AsyncClient() as client:
                # Basic markdown scraping
                result = await client.scrape("https://example.com")
                print(result.markdown)

                # Get HTML and list of links
                result = await client.scrape(
                    "https://example.com",
                    formats=["html", "links"],
                    exclude_tags=["nav", "footer", "aside"]
                )
            ```
        """
        payload = {
            "url": url,
            "formats": formats or ["markdown"],
            "includeTags": include_tags,
            "excludeTags": exclude_tags,
            "headers": headers,
            "waitFor": wait_for,
            "timeout": timeout,
            "extract": {
                "schema": extract_schema,
                "systemPrompt": extract_system_prompt,
                "prompt": extract_prompt,
            }
            if any([extract_schema, extract_system_prompt, extract_prompt])
            else None,
        }

        response = await self.client.post(f"{self.base_url}/v1/scrape", json=payload)
        response.raise_for_status()
        data = response.json()
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
        Start an asynchronous crawl job to scrape multiple pages.

        Args:
            url: Starting URL for the crawl
            exclude_paths: URL patterns to skip (e.g., ["/admin/*", "/private/*"])
            include_paths: URL patterns to crawl (e.g., ["/blog/*", "/products/*"])
            max_depth: Maximum number of links to follow from start URL
            ignore_sitemap: Whether to ignore sitemap.xml
            limit: Maximum number of pages to crawl
            allow_backward_links: Allow revisiting previously seen URLs
            allow_external_links: Allow following links to other domains
            webhook: URL to receive crawl status updates
            scrape_formats: Content formats to get from each page
            scrape_headers: Custom HTTP headers for requests
            scrape_include_tags: HTML elements to include
            scrape_exclude_tags: HTML elements to exclude
            scrape_wait_for: Milliseconds to wait before scraping each page

        Returns:
            CrawlJob containing the job ID for status checks

        Examples:
            ```python
            async with AsyncClient() as client:
                # Crawl product pages
                job = await client.crawl(
                    "https://example.com",
                    include_paths=["/products/*"],
                    max_depth=3,
                    limit=100
                )

                # Check crawl progress
                status = await client.get_crawl_status(job.id)
                print(f"Crawled {status.completed} of {status.total} pages")
            ```
        """
        payload = {
            "url": url,
            "excludePaths": exclude_paths,
            "includePaths": include_paths,
            "maxDepth": max_depth,
            "ignoreSitemap": ignore_sitemap,
            "limit": limit,
            "allowBackwardLinks": allow_backward_links,
            "allowExternalLinks": allow_external_links,
            "webhook": webhook,
            "scrapeOptions": {
                "formats": scrape_formats or ["markdown"],
                "headers": scrape_headers,
                "includeTags": scrape_include_tags,
                "excludeTags": scrape_exclude_tags,
                "waitFor": scrape_wait_for,
            },
        }

        response = await self.client.post(f"{self.base_url}/v1/crawl", json=payload)
        response.raise_for_status()
        data = response.json()
        return CrawlJob.model_validate(data)

    async def get_crawl_status(self, job_id: str) -> CrawlStatus:
        """
        Check the status and get results from a crawl job.

        Args:
            job_id: ID of the crawl job to check

        Returns:
            CrawlStatus with job progress and available results
        """
        response = await self.client.get(f"{self.base_url}/v1/crawl/{job_id}")
        response.raise_for_status()
        data = response.json()
        return CrawlStatus.model_validate(data)

    async def cancel_crawl(self, job_id: str) -> bool:
        """
        Cancel an in-progress crawl job.

        Args:
            job_id: ID of the crawl job to cancel

        Returns:
            True if cancellation was successful
        """
        response = await self.client.delete(f"{self.base_url}/v1/crawl/{job_id}")
        response.raise_for_status()
        data = response.json()
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
        Asynchronously discover URLs on a website without scraping content.

        Args:
            url: Website to map
            search: Optional search term to filter URLs
            ignore_sitemap: Whether to ignore sitemap.xml
            include_subdomains: Include URLs from subdomains
            limit: Maximum URLs to return (max 5000)

        Returns:
            MapResult containing the discovered URLs

        Example:
            ```python
            async with AsyncClient() as client:
                # Find all blog posts
                result = await client.map(
                    "https://example.com",
                    search="blog",
                    limit=1000
                )

                for url in result.links:
                    print(url)
            ```
        """
        payload = {
            "url": url,
            "search": search,
            "ignoreSitemap": ignore_sitemap,
            "includeSubdomains": include_subdomains,
            "limit": limit,
        }

        response = await self.client.post(f"{self.base_url}/v1/map", json=payload)
        response.raise_for_status()
        data = response.json()
        return MapResult.model_validate(data)

    async def close(self):
        """Close the underlying HTTP client session."""
        await self.client.aclose()

    async def __aenter__(self):
        """Support using client as an async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Ensure the client is closed when exiting the context manager."""
        await self.close()
