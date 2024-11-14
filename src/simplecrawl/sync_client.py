import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

from .models import CrawlJob, CrawlStatus, FormatType, MapResult, ScrapeResult

# TODO: handle screenshot formats


class Client:
    """
    Synchronous client for the Firecrawl web scraping API.

    Provides methods to scrape single pages, crawl multiple pages,
    and discover URLs on websites.

    Args:
        token: API authentication token (optional)
        base_url: API endpoint (default: https://api.firecrawl.dev/v1)

    Basic Usage:

    ```python
        # Initialize client
        client = Client(token="your-api-token")

        # Scrape a single page
        result = client.scrape("https://example.com")
        print(result.markdown)  # Print markdown content
        print(result.metadata.title)  # Print page title

        # Scrape with multiple formats
        result = client.scrape(
            "https://example.com",
            formats=["markdown", "html", "links"]
        )
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
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def scrape(
        self,
        url: str,
        formats: Optional[List[FormatType]] = None,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: int = 0,
        timeout: int = 30000,
    ) -> ScrapeResult:
        """
        Scrape content from a single URL.

        Args:
            url: The webpage to scrape
            formats: Content formats to retrieve (default: ["markdown"])
            include_tags: HTML elements to include (e.g., ["article", "main"])
            exclude_tags: HTML elements to exclude (e.g., ["nav", "footer"])
            headers: Custom HTTP headers for the request
            wait_for: Milliseconds to wait before scraping (for JS content)
            timeout: Request timeout in milliseconds

        Returns:
            ScrapeResult containing the requested content formats and metadata

        Examples:
            ```python
            # Basic markdown scraping
            result = client.scrape("https://example.com")
            print(result.markdown)

            # Get HTML and list of links
            result = client.scrape(
                "https://example.com",
                formats=["html", "links"],
                exclude_tags=["nav", "footer", "aside"]
            )

            print(f"Found {len(result.links)} links")
            print(result.html)
            ```
        """
        # include parts of payload only if they are not None
        payload = {}
        if url:
            payload["url"] = url
        if formats:
            payload["formats"] = formats
        if include_tags:
            payload["includeTags"] = include_tags
        if exclude_tags:
            payload["excludeTags"] = exclude_tags
        if headers:
            payload["headers"] = headers
        if wait_for:
            payload["waitFor"] = wait_for
        if timeout:
            payload["timeout"] = timeout

        response = self.session.post(f"{self.base_url}/v1/scrape", json=payload)
        response.raise_for_status()
        data = response.json()
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
        scrape_formats: Optional[List[FormatType]] = None,
        scrape_headers: Optional[Dict[str, str]] = None,
        scrape_include_tags: Optional[List[str]] = None,
        scrape_exclude_tags: Optional[List[str]] = None,
        scrape_wait_for: int = 123,
    ) -> CrawlJob:
        """
        Start a crawl job to scrape multiple pages.

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
            # Crawl product pages
            job = client.crawl(
                "https://example.com",
                include_paths=["/products/*"],
                max_depth=3,
                limit=100
            )

            # Check crawl progress
            status = client.get_crawl_status(job.id)
            print(f"Crawled {status.completed} of {status.total} pages")

            # Access results
            for page in status.data:
                print(f"Page: {page.metadata.title}")
                print(page.markdown)
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

        response = self.session.post(f"{self.base_url}/v1/crawl", json=payload)
        response.raise_for_status()
        data = response.json()
        return CrawlJob.model_validate(data)

    def get_crawl_status(self, job_id: str) -> CrawlStatus:
        """
        Check the status and get results from a crawl job.

        Args:
            job_id: ID of the crawl job to check

        Returns:
            CrawlStatus with job progress and available results
        """
        response = self.session.get(f"{self.base_url}/v1/crawl/{job_id}")
        response.raise_for_status()
        data = response.json()
        return CrawlStatus.model_validate(data)

    def cancel_crawl(self, job_id: str) -> bool:
        """
        Cancel an in-progress crawl job.

        Args:
            job_id: ID of the crawl job to cancel

        Returns:
            True if cancellation was successful
        """
        response = self.session.delete(f"{self.base_url}/v1/crawl/{job_id}")
        response.raise_for_status()
        data = response.json()
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
        Discover URLs on a website without scraping content.

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
            # Find all blog posts
            result = client.map(
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

        response = self.session.post(f"{self.base_url}/v1/map", json=payload)
        response.raise_for_status()
        data = response.json()
        return MapResult.model_validate(data)
