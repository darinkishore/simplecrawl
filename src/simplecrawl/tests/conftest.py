import os

import pytest
from dotenv import load_dotenv

from src.simplecrawl.async_client import AsyncClient as FirecrawlClientAsync
from src.simplecrawl.sync_client import Client as FirecrawlClientSync


@pytest.fixture(scope="session", autouse=True)
def env_setup():
    load_dotenv()
    assert os.getenv("FIRECRAWL_BASE_URL"), "FIRECRAWL_BASE_URL must be set"


@pytest.fixture(scope="session")
def sync_client():
    client = FirecrawlClientSync(base_url="")
    yield client


# TODO: prolly delete this


@pytest.fixture(scope="session")
def async_client():
    client = FirecrawlClientAsync(base_url="https://api.firecrawl.dev/v1")
    yield client
    client.close()
