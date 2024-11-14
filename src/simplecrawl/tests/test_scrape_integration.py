# integration_test_scrape.py

import os

from dotenv import load_dotenv

from src.simplecrawl.sync_client import Client as FirecrawlClientSync

load_dotenv()


def test_scrape_integration():
    client = FirecrawlClientSync(base_url=os.getenv("FIRECRAWL_BASE_URL"))

    try:
        scrape_result = client.scrape(
            url="https://api.firecrawl.dev/docs",  # Replace with the actual Firecrawl docs URL
            formats=["markdown", "html"],
        )

        print("Scrape Integration Test:")
        print("Title:", scrape_result.metadata.title)
        print("Description:", scrape_result.metadata.description)
        print("Status Code:", scrape_result.metadata.statusCode)
        print("Markdown Content Length:", len(scrape_result.markdown or ""))
        print("HTML Content Length:", len(scrape_result.html or ""))
        print("Links Found:", len(scrape_result.links or []))

    except Exception as e:
        print("An error occurred during the scrape integration test:", str(e))
        raise e


if __name__ == "__main__":
    test_scrape_integration()
