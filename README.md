# SimpleCrawl

A typed client for the `firecrawl-simple` self-hosted API.

## Installation

```bash
pip install simplecrawl
```

## Quick Start

### Synchronous Usage

`export FIRECRAWL_URL_BASE="url"`

```python
from src.simplecrawl import Client

# Initialize client
client = Client(base_url="some-url", ) # defaults to https://api.firecrawl.dev/v1 as base URL if not found in environment

# Scrape a single page
result = client.scrape("https://example.com")
print(result.markdown)
print(result.metadata.title)

# Crawl multiple pages
job = client.crawl(
    "https://example.com",
    include_paths=["/blog/*"],
    max_depth=2,
    limit=10
)
```

### Async Usage

```python
import asyncio
from simplecrawl import AsyncClient

async def main():
    async with AsyncClient(token="your-api-token") as client:
        result = await client.scrape("https://example.com")
        print(result.markdown)

asyncio.run(main())
```

## Features

- Synchronous and asynchronous clients
- Single page scraping
- Multi-page crawling
- URL discovery/mapping
- Content format options (Markdown, HTML, Links, etc.)
- Customizable scraping options

## Documentation

For detailed examples, check out the examples folder.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


Project Path: simplecrawl

Source Tree:

```
simplecrawl
├── LICENSE
├── uv.lock
├── pyproject.toml
├── README.md
└── src
    └── simplecrawl
        ├── models.py
        ├── tests
        │   ├── conftest.py
        │   ├── test_scrape_integration.py
        │   ├── __init__.py
        │   ├── test_async_client.py
        │   ├── test_sync_client.py
        │   └── test_map_integration.py
        ├── __init__.py
        ├── async_client.py
        ├── examples
        │   ├── sync_example.py
        │   └── async_example.py
        ├── py.typed
        └── sync_client.py

```

`/Users/darin/Projects/simplecrawl/README.md`:

```md
# SimpleCrawl

A typed client for the `firecrawl-simple` self-hosted API.

## Installation

```bash
pip install simplecrawl
```

## Quick Start

### Synchronous Usage

`export FIRECRAWL_URL_BASE="url"`

```python
from src.simplecrawl import Client

# Initialize client
client = Client(base_url="some-url", ) # defaults to https://api.firecrawl.dev/v1 as base URL if not found in environment

# Scrape a single page
result = client.scrape("https://example.com")
print(result.markdown)
print(result.metadata.title)

# Crawl multiple pages
job = client.crawl(
    "https://example.com",
    include_paths=["/blog/*"],
    max_depth=2,
    limit=10
)
```

### Async Usage

```python
import asyncio
from simplecrawl import AsyncClient

async def main():
    async with AsyncClient(token="your-api-token") as client:
        result = await client.scrape("https://example.com")
        print(result.markdown)

asyncio.run(main())
```

## Features

- Synchronous and asynchronous clients
- Single page scraping
- Multi-page crawling
- URL discovery/mapping
- Content format options (Markdown, HTML, Links, etc.)
- Customizable scraping options

## Documentation

For detailed examples, check out the examples folder.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/models.py`:

```py
from datetime import datetime
from enum import Enum
from typing import Literal, Optional, List

from pydantic import BaseModel, HttpUrl, ConfigDict, Field


class OutputFormat(str, Enum):
    """Available formats for content output."""

    MARKDOWN = "markdown"  # Cleaned, readable markdown version of the page
    HTML = "html"  # Cleaned HTML version of the page
    RAW_HTML = "rawHtml"  # Original HTML as received from the server
    LINKS = "links"  # List of all links found on the page
    SCREENSHOT = "screenshot"  # Screenshot of the visible area
    SCREENSHOT_FULL = "screenshot@fullPage"  # Full page screenshot


FormatType = Literal[
    "markdown", "html", "rawHtml", "links", "screenshot", "screenshot@fullPage"
]


class CrawlState(str, Enum):
    """Possible states of a crawl job."""

    SCRAPING = "scraping"  # Currently crawling pages
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"  # Encountered an error and stopped


class Metadata(BaseModel):
    """Metadata about a scraped page."""

    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    sourceURL: HttpUrl
    statusCode: int
    error: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ScrapeResult(BaseModel):
    """Content and metadata from a scraped page."""

    markdown: Optional[str] = None  # Markdown version of the content
    html: Optional[str] = None  # Clean HTML version
    raw_html: Optional[str] = Field(None, alias="rawHtml")  # Original HTML
    links: Optional[List[str]] = None  # All links found on the page
    metadata: Metadata  # Page metadata (title, description, etc)


class CrawlStatus(BaseModel):
    """Current status and results of a crawl job."""

    status: CrawlState
    total: int  # Total pages attempted
    completed: int  # Successfully crawled pages
    expires_at: datetime = Field(..., alias="expiresAt")
    next: Optional[str] = None  # URL for next batch of results
    data: List[ScrapeResult]  # Results from crawled pages


class CrawlJob(BaseModel):
    """Reference to a created crawl job."""

    success: bool
    id: str  # Job identifier for status checks
    url: HttpUrl  # Starting URL of the crawl


class MapResult(BaseModel):
    """Result of URL mapping operation."""

    success: bool
    links: List[str]  # Discovered URLs

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/tests/conftest.py`:

```py
import os

import pytest

from src.simplecrawl.sync_client import Client as FirecrawlClientSync
from src.simplecrawl.async_client import AsyncClient as FirecrawlClientAsync

from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def env_setup():
    load_dotenv()
    assert os.getenv("FIRECRAWL_BASE_URL"), "FIRECRAWL_BASE_URL must be set"

@pytest.fixture(scope="session")
def sync_client():
    client = FirecrawlClientSync(base_url="")
    yield client


@pytest.fixture(scope="session")
def async_client():
    client = FirecrawlClientAsync(base_url="https://api.firecrawl.dev/v1")
    yield client
    client.close()
```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/tests/test_scrape_integration.py`:

```py
# integration_test_scrape.py

import os

from dotenv import load_dotenv

from src.simplecrawl.sync_client import Client as FirecrawlClientSync

load_dotenv()


def test_scrape_integration():
    client = FirecrawlClientSync(base_url=os.getenv("FIRECRAWL_BASE_URL"))

    try:
        scrape_result = client.scrape(
            url="https://api.firecrawl.dev/docs",  # Replace with the actual Firecrawl docs URL
            formats=["markdown", "html"],
        )

        print("Scrape Integration Test:")
        print("Title:", scrape_result.metadata.title)
        print("Description:", scrape_result.metadata.description)
        print("Status Code:", scrape_result.metadata.statusCode)
        print("Markdown Content Length:", len(scrape_result.markdown or ""))
        print("HTML Content Length:", len(scrape_result.html or ""))
        print("Links Found:", len(scrape_result.links or []))

    except Exception as e:
        print("An error occurred during the scrape integration test:", str(e))
        raise e


if __name__ == "__main__":
    test_scrape_integration()

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/tests/test_async_client.py`:

```py
# tests/test_async_client.py

import pytest
import pytest_asyncio
import respx
from httpx import Response

from src.simplecrawl import (
    CrawlJob,
    AsyncClient as FirecrawlClientAsync,
    MapResult,
    ScrapeResult,
)


@pytest_asyncio.fixture
async def async_client():
    client = FirecrawlClientAsync(token="test_token", base_url="https://api.firecrawl.dev")
    yield client
    await client.close()


@respx.mock
@pytest.mark.asyncio
async def test_scrape(async_client):
    route = respx.post("https://api.firecrawl.dev/v1/scrape").mock(
        return_value=Response(
            status_code=200,
            json={
                "success": True,
                "data": {
                    "markdown": "# Example",
                    "html": "<h1>Example</h1>",
                    "links": [
                        "https://example.com/about",
                        "https://example.com/contact",
                    ],
                    "metadata": {
                        "title": "Example Domain",
                        "description": "This domain is for use in illustrative examples in documents.",
                        "sourceURL": "https://example.com",
                        "statusCode": 200,
                        "error": None,
                    },
                    "llm_extraction": None,
                    "warning": None,
                },
            },
        )
    )

    result = await async_client.scrape(
        url="https://example.com", formats=["markdown", "html"]
    )

    assert route.called
    assert isinstance(result, ScrapeResult)
    assert result.markdown == "# Example"
    assert result.html == "<h1>Example</h1>"
    assert result.links == ["https://example.com/about", "https://example.com/contact"]
    assert result.metadata.title == "Example Domain"
    assert result.metadata.statusCode == 200


@respx.mock
@pytest.mark.asyncio
async def test_crawl(async_client):
    route = respx.post("https://api.firecrawl.dev/v1/crawl").mock(
        return_value=Response(
            status_code=200,
            json={
                "success": True,
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "url": "https://example.com",
            },
        )
    )

    result = await async_client.crawl(url="https://example.com", max_depth=3, limit=20)

    assert route.called
    assert isinstance(result, CrawlJob)
    assert result.id == "123e4567-e89b-12d3-a456-426614174000"
    assert str(result.url) == "https://example.com/"
    assert result.success is True


@respx.mock
@pytest.mark.asyncio
async def test_get_crawl_status(async_client):
    route = respx.get(
        "https://api.firecrawl.dev/v1/crawl/123e4567-e89b-12d3-a456-426614174000"
    ).mock(
        return_value=Response(
            status_code=200,
            json={
                "status": "completed",
                "total": 20,
                "completed": 20,
                "expiresAt": "2024-12-31T23:59:59Z",
                "next": None,
                "data": [],
            },
        )
    )

    result = await async_client.get_crawl_status("123e4567-e89b-12d3-a456-426614174000")

    assert route.called
    assert result.status == "completed"
    assert result.total == 20
    assert result.completed == 20
    assert result.expires_at.isoformat() == "2024-12-31T23:59:59+00:00"
    assert result.next is None
    assert isinstance(result.data, list)


@respx.mock
@pytest.mark.asyncio
async def test_cancel_crawl(async_client):
    route = respx.delete(
        "https://api.firecrawl.dev/v1/crawl/123e4567-e89b-12d3-a456-426614174000"
    ).mock(
        return_value=Response(
            status_code=200,
            json={"success": True, "message": "Crawl job successfully cancelled."},
        )
    )

    result = await async_client.cancel_crawl("123e4567-e89b-12d3-a456-426614174000")

    assert route.called
    assert result is True


@respx.mock
@pytest.mark.asyncio
async def test_map(async_client):
    route = respx.post("https://api.firecrawl.dev/v1/map").mock(
        return_value=Response(
            status_code=200,
            json={
                "success": True,
                "links": ["https://example.com/contact", "https://example.com/about"],
            },
        )
    )

    result = await async_client.map(
        url="https://example.com", search="contact", limit=100
    )

    assert route.called
    assert isinstance(result, MapResult)
    assert result.success is True
    assert len(result.links) == 2
    assert "https://example.com/contact" in result.links

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/tests/test_sync_client.py`:

```py
# tests/test_sync_client.py

from unittest.mock import patch

import pytest

from src.simplecrawl import (
    CrawlJob,
    MapResult,
    Client as FirecrawlClientSync,
)


@pytest.fixture
def client():
    return FirecrawlClientSync(token="test_token", base_url="https://api.firecrawl.dev/v1")


def test_crawl(client):
    mock_response = {
        "success": True,
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "url": "https://example.com/",
    }

    with patch.object(client.session, "post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        result = client.crawl(url="https://example.com", max_depth=3, limit=20)

        assert isinstance(result, CrawlJob)
        assert result.id == "123e4567-e89b-12d3-a456-426614174000"
        assert str(result.url) == "https://example.com/"
        assert result.success is True


def test_crawl(client):
    mock_response = {
        "success": True,
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "url": "https://example.com",
    }

    with patch.object(client.session, "post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        result = client.crawl(url="https://example.com", max_depth=3, limit=20)

        assert isinstance(result, CrawlJob)
        assert result.id == "123e4567-e89b-12d3-a456-426614174000"
        assert str(result.url) == "https://example.com/"
        assert result.success is True


def test_get_crawl_status(client):
    mock_response = {
        "status": "completed",
        "total": 20,
        "completed": 20,
        "expiresAt": "2024-12-31T23:59:59Z",
        "next": None,
        "data": [],
    }

    with patch.object(client.session, "get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = client.get_crawl_status("123e4567-e89b-12d3-a456-426614174000")

        assert result.status == "completed"
        assert result.total == 20
        assert result.completed == 20
        assert result.expires_at.isoformat() == "2024-12-31T23:59:59+00:00"
        assert result.next is None
        assert isinstance(result.data, list)


def test_cancel_crawl(client):
    mock_response = {"success": True, "message": "Crawl job successfully cancelled."}

    with patch.object(client.session, "delete") as mock_delete:
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = mock_response

        result = client.cancel_crawl("123e4567-e89b-12d3-a456-426614174000")

        assert result is True


def test_map(client):
    mock_response = {
        "success": True,
        "links": ["https://example.com/contact", "https://example.com/about"],
    }

    with patch.object(client.session, "post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        result = client.map(url="https://example.com", search="contact", limit=100)

        assert isinstance(result, MapResult)
        assert result.success is True
        assert len(result.links) == 2
        assert "https://example.com/contact" in result.links

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/tests/test_map_integration.py`:

```py
# integration_test_map.py

import os

from dotenv import load_dotenv

from src.simplecrawl.sync_client import Client as FirecrawlClientSync

load_dotenv()


def test_map_integration():
    client = FirecrawlClientSync(base_url=os.getenv("FIRECRAWL_BASE_URL"))

    try:
        map_result = client.map(
            url="https://docs.firecrawl.dev/introduction",  # Replace with the actual Firecrawl docs URL
            search="api",  # Search for pages containing 'api'
            limit=100,
        )

        print("Map Integration Test:")
        print(f"Number of Links Found: {len(map_result.links)}")
        for link in map_result.links:
            print(link)

    except Exception as e:
        print("An error occurred during the map integration test:", str(e))
        raise e


if __name__ == "__main__":
    test_map_integration()

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/__init__.py`:

```py
"""SimpleCrawl - A simple, modern Python client for the `firecrawl-simple` API."""

from simplecrawl.async_client import AsyncClient
from simplecrawl.models import (
    CrawlJob,
    CrawlStatus,
    MapResult,
    ScrapeResult,
)
from simplecrawl.sync_client import Client

__all__ = [
    "Client",
    "AsyncClient",
    "CrawlJob",
    "CrawlStatus",
    "MapResult",
    "ScrapeResult",
]

__version__ = "0.1.0"

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/async_client.py`:

```py
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

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/examples/sync_example.py`:

```py
# sync_example.py
import os

from src.simplecrawl import Client

from dotenv import load_dotenv
load_dotenv()

def main():
    client = Client(base_url=os.getenv("FIRECRAWL_BASE_URL"))
    # Scrape a URL
    scrape_result = client.scrape(
        url="https://docs.firecrawl.dev/introduction",
        formats=["markdown", "html"],
    )
    print("Scraped Markdown:", scrape_result.markdown)
    print("Scraped HTML:", scrape_result.html)

    # Start a crawl job
    crawl_job = client.crawl(url="https://example.com", max_depth=3, limit=20)
    print(f"Crawl job started with ID: {crawl_job.id}")

    # Check crawl status
    crawl_status = client.get_crawl_status(crawl_job.id)
    print(f"Crawl status: {crawl_status.status}")

    # Cancel crawl job
    success = client.cancel_crawl(crawl_job.id)
    print(f"Crawl cancellation successful: {success}")

    # Map URLs
    map_result = client.map(url="https://example.com", search="contact", limit=100)
    print(f"Found {len(map_result.links)} links:")
    for link in map_result.links:
        print(link)


if __name__ == "__main__":
    main()

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/examples/async_example.py`:

```py
# async_example.py

import asyncio

from simplecrawl.firecrawl_client import FirecrawlClientAsync


async def main():
    async with FirecrawlClientAsync(token="your_token_here") as client:
        # Scrape a URL
        scrape_result = await client.scrape(
            url="https://example.com", formats=["markdown", "html"]
        )
        print("Scraped Markdown:", scrape_result.markdown)
        print("Scraped HTML:", scrape_result.html)

        # Start a crawl job
        crawl_job = await client.crawl(url="https://example.com", max_depth=3, limit=20)
        print(f"Crawl job started with ID: {crawl_job.id}")

        # Check crawl status
        crawl_status = await client.get_crawl_status(crawl_job.id)
        print(f"Crawl status: {crawl_status.status}")

        # Cancel crawl job
        success = await client.cancel_crawl(crawl_job.id)
        print(f"Crawl cancellation successful: {success}")

        # Map URLs
        map_result = await client.map(
            url="https://example.com", search="contact", limit=100
        )
        print(f"Found {len(map_result.links)} links:")
        for link in map_result.links:
            print(link)


if __name__ == "__main__":
    asyncio.run(main())

```

`/Users/darin/Projects/simplecrawl/src/simplecrawl/sync_client.py`:

```py
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

```