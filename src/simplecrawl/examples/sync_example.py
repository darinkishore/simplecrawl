# sync_example.py
import os

from src.simplecrawl import Client

from dotenv import load_dotenv
load_dotenv()

def main():
    client = Client(base_url=os.getenv("FIRECRAWL_BASE_URL"))
    # Scrape a URL
    scrape_result = client.scrape(
        url="https://docs.firecrawl.dev/introduction",
        formats=["markdown", "html"],
    )
    print("Scraped Markdown:", scrape_result.markdown)
    print("Scraped HTML:", scrape_result.html)

    # Start a crawl job
    crawl_job = client.crawl(url="https://example.com", max_depth=3, limit=20)
    print(f"Crawl job started with ID: {crawl_job.id}")

    # Check crawl status
    crawl_status = client.get_crawl_status(crawl_job.id)
    print(f"Crawl status: {crawl_status.status}")

    # Cancel crawl job
    success = client.cancel_crawl(crawl_job.id)
    print(f"Crawl cancellation successful: {success}")

    # Map URLs
    map_result = client.map(url="https://example.com", search="contact", limit=100)
    print(f"Found {len(map_result.links)} links:")
    for link in map_result.links:
        print(link)


if __name__ == "__main__":
    main()
