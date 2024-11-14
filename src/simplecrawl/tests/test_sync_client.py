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
