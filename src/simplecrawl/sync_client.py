from typing import Any, Dict, List, Optional

import requests

from .models import (
    CrawlJob,
    CrawlStatus,
    MapResult,
    ScrapeResult,
)


class FirecrawlClient:
    """
    Synchronous client for the firecrawl-simple API.

    This client allows you to:
    - Scrape a single URL for content and metadata.
    - Start and manage crawl jobs to scrape multiple pages.
    - Map (discover) URLs on a given website without scraping.

    Usage:
        client = FirecrawlClient(base_url="https://api.firecrawl.dev/v1")

        # Scrape a single page
        scrape_result = client.scrape("https://example.com")
        print(scrape_result.markdown)

        # Start a crawl
        crawl_job = client.crawl("https://example.com", max_depth=2, limit=5)
        print("Crawl Job ID:", crawl_job.id)

        # Check crawl status
        status = client.get_crawl_status(crawl_job.id)
        print("Crawl Status:", status.status)

        # Cancel the crawl
        success = client.cancel_crawl(crawl_job.id)
        print("Crawl Cancelled:", success)

        # Map URLs
        map_result = client.map("https://example.com")
        print("Found links:", map_result.links)
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialize the FirecrawlClient.

        Args:
            base_url: The base URL for the API, e.g. "https://api.firecrawl.dev/v1"
        """
        if not base_url:
            raise ValueError("Base URL must be provided.")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def scrape(
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
        Scrape a single URL for content and metadata.

        Args:
            url: URL to scrape.
            formats: List of formats to retrieve. Defaults to ["markdown"].
            include_tags: Tags to include in scraping.
            exclude_tags: Tags to exclude from scraping.
            headers: Custom HTTP headers for the request.
            wait_for: Milliseconds to wait before scraping (helpful for JS-heavy sites).
            timeout: Request timeout in milliseconds.
            extract_schema: Schema for LLM extraction.
            extract_system_prompt: System prompt for extraction.
            extract_prompt: User prompt for extraction.

        Returns:
            A ScrapeResult model containing scraped content and metadata.
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

        resp = self.session.post(f"{self.base_url}/scrape", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return ScrapeResult.model_validate(data["data"])

    def crawl(
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
        Start a crawl job to scrape multiple pages starting from a given URL.

        Args:
            url: Starting URL.
            exclude_paths: URL patterns to exclude.
            include_paths: URL patterns to include.
            max_depth: Max crawl depth.
            ignore_sitemap: Whether to ignore sitemap.xml.
            limit: Maximum number of pages to crawl.
            allow_backward_links: Whether to allow navigation back to previously linked pages.
            allow_external_links: Whether to allow following external domains.
            webhook: URL to send crawl status updates.
            scrape_formats: Formats to scrape each page with.
            scrape_headers: Headers for each request during crawl.
            scrape_include_tags: Tags to include in each page scrape.
            scrape_exclude_tags: Tags to exclude in each page scrape.
            scrape_wait_for: Milliseconds to wait before scraping each page.

        Returns:
            A CrawlJob model with the job ID for checking status.
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

        resp = self.session.post(f"{self.base_url}/crawl", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return CrawlJob.model_validate(data)

    def get_crawl_status(self, job_id: str) -> CrawlStatus:
        """
        Retrieve the status of a crawl job.

        Args:
            job_id: The crawl job ID.

        Returns:
            A CrawlStatus model with current job status and data.
        """
        resp = self.session.get(f"{self.base_url}/crawl/{job_id}")
        resp.raise_for_status()
        data = resp.json()
        return CrawlStatus.model_validate(data)

    def cancel_crawl(self, job_id: str) -> bool:
        """
        Cancel a running crawl job.

        Args:
            job_id: The crawl job ID.

        Returns:
            True if successfully cancelled, False otherwise.
        """
        resp = self.session.delete(f"{self.base_url}/crawl/{job_id}")
        resp.raise_for_status()
        data = resp.json()
        return data.get("success", False)

    def map(
        self,
        url: str,
        search: Optional[str] = None,
        ignore_sitemap: bool = True,
        include_subdomains: bool = False,
        limit: int = 5000,
    ) -> MapResult:
        """
        Map (discover) URLs from a given website.

        Args:
            url: The base URL to start from.
            search: Optional search query to filter results.
            ignore_sitemap: Whether to ignore the sitemap.
            include_subdomains: Whether to include subdomains.
            limit: Maximum number of links to return.

        Returns:
            A MapResult model with discovered links.
        """
        payload: Dict[str, Any] = {
            "url": url,
            "ignoreSitemap": ignore_sitemap,
            "includeSubdomains": include_subdomains,
            "limit": limit,
        }

        if search is not None:
            payload["search"] = search

        resp = self.session.post(f"{self.base_url}/map", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return MapResult.model_validate(data)
