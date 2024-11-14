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
