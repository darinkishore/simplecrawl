# SimpleCrawl

A typed client for the [`firecrawl-simple`](https://github.com/nustato/firecrawl-simple) self-hosted API.

## Installation

```bash
pip install simplecrawl
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
