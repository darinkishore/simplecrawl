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
