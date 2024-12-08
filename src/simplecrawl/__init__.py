"""MyFirecrawlClient

A typed Python client for the firecrawl-simple API.

Provides synchronous and asynchronous clients.
"""

from .async_client import AsyncFirecrawlClient
from .models import (
    CrawlJob,
    CrawlState,
    CrawlStatus,
    MapResult,
    Metadata,
    OutputFormat,
    ScrapeResult,
)
from .sync_client import FirecrawlClient

__all__ = [
    "OutputFormat",
    "CrawlState",
    "Metadata",
    "ScrapeResult",
    "CrawlStatus",
    "CrawlJob",
    "MapResult",
    "FirecrawlClient",
    "AsyncFirecrawlClient",
]
