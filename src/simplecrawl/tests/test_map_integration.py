# integration_test_map.py

import os

from dotenv import load_dotenv

from src.simplecrawl.sync_client import Client as FirecrawlClientSync

load_dotenv()


def test_map_integration():
    client = FirecrawlClientSync(base_url=os.getenv("FIRECRAWL_BASE_URL"))

    try:
        map_result = client.map(
            url="https://docs.firecrawl.dev/introduction",  # Replace with the actual Firecrawl docs URL
            search="api",  # Search for pages containing 'api'
            limit=100,
        )

        print("Map Integration Test:")
        print(f"Number of Links Found: {len(map_result.links)}")
        for link in map_result.links:
            print(link)

    except Exception as e:
        print("An error occurred during the map integration test:", str(e))
        raise e


if __name__ == "__main__":
    test_map_integration()
