#!/usr/bin/env bash

# This script tests the crawling and cleaning process end-to-end.

# Parameters
URL="https://returns.readthedocs.io/en/latest/" # Replace with an actual docs URL
NAME="returns_docs"

# Step 1: Crawl the site
echo "Crawling the site..."
uv run -m simplecrawl.cli crawl "$URL" "$NAME" --max-depth 1 --limit 3 --format markdown

# Step 2: Clean the crawled HTML, identify common elements, convert to markdown
echo "Cleaning the site docs..."
uv run -m simplecrawl.cli clean "returns_docs" --threshold-ratio 0.99

# After this script:
# Check ~/docs/$NAME/raw for original HTML and ~/docs/$NAME/cleaned for cleaned markdown files.
