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
