# SimpleCrawl

A typed client for the [`firecrawl-simple`](https://github.com/nustato/firecrawl-simple) self-hosted API. 

Synchronous and asynchronous clients.

Contributions welcome.

## Features

- Scrape a single URL
- Start and manage crawl jobs
- Map (discover) URLs from a site
- No Auth!

## Installation

```bash
pip install firecrawl-simple-client
```

## Quick Start

### Synchronous Usage

`export FIRECRAWL_URL_BASE="url"`

```python
from simplecrawl import Client

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

---

A typed, synchronous and asynchronous Python client for the `firecrawl-simple` API.



## Installation

```bash
pip install myfirecrawlclient
```

## Usage

### Synchronous

```python
from myfirecrawlclient import FirecrawlClient

client = FirecrawlClient(base_url="https://api.firecrawl.dev/v1")

# Scrape a single page
result = client.scrape("https://example.com")
print(result.metadata.title, result.markdown)
```

### Asynchronous

```python
import asyncio
from myfirecrawlclient import AsyncFirecrawlClient

async def main():
    async with AsyncFirecrawlClient(base_url="https://api.firecrawl.dev/v1") as client:
        result = await client.scrape("https://example.com")
        print(result.metadata.title, result.markdown)

asyncio.run(main())
```

