from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class OutputFormat(str, Enum):
    """Available formats for content output from the scrape endpoint."""

    MARKDOWN = "markdown"
    HTML = "html"
    RAW_HTML = "rawHtml"
    LINKS = "links"
    SCREENSHOT = "screenshot"
    SCREENSHOT_FULL = "screenshot@fullPage"


class CrawlState(str, Enum):
    """Possible states of a crawl job."""

    SCRAPING = "scraping"
    COMPLETED = "completed"
    FAILED = "failed"


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

    markdown: Optional[str] = None
    html: Optional[str] = None
    raw_html: Optional[str] = Field(None, alias="rawHtml")
    links: Optional[List[str]] = None
    metadata: Metadata
    # llm_extraction and warning are not fully typed as they are optional, dynamic fields.
    llm_extraction: Optional[Dict[str, Any]] = Field(None, alias="llm_extraction")
    warning: Optional[str] = None


class CrawlStatus(BaseModel):
    """Status and results of a crawl job."""

    status: CrawlState
    total: int
    completed: int
    expires_at: datetime = Field(..., alias="expiresAt")
    next: Optional[str] = None
    data: List[ScrapeResult]


class CrawlJob(BaseModel):
    """Reference to a created crawl job."""

    success: bool
    id: str
    url: HttpUrl


class MapResult(BaseModel):
    """Result of URL mapping operation."""

    success: bool
    links: List[str]
