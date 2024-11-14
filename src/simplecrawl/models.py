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
