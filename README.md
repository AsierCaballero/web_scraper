# Web Scraper

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/AsierCaballero/web_scraper/ci.yml?label=CI&logo=github)](https://github.com/AsierCaballero/web_scraper/actions)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)](tests/)

A web scraping framework with rate limiting, extensible parsers and multiple storage backends.

## Features

- **Smart HTTP client** — rate limiting, automatic retry, exponential backoff
- **Extensible parsers** — bring your own or use the built-in generic parser
- **Persistent storage** — SQLite by default, CSV/JSON export
- **CLI ready** — scrape from the terminal with a single command

## Install

```bash
cd web_scraper
pip install -e ".[dev]"
```

## CLI Usage

```bash
# Scrape a website
web-scraper scrape "https://example.com" --db data.db -f csv -e output.csv

# List scraped items
web-scraper list data.db --limit 10

# Export to JSON
web-scraper export data.db data.json --format json
```

## Python Usage

```python
from web_scraper.core.models import ScrapeConfig
from web_scraper.parsers.generic import GenericParser
from web_scraper.storage.database import Database
from web_scraper.core.scraper import Scraper

config = ScrapeConfig(max_pages=5)
db = Database("data.db")
parser = GenericParser(config)

with Scraper(parser=parser, storage=db, config=config) as scraper:
    result = scraper.scrape_urls(["https://example.com"])

print(f"Got {len(result.items)} items")
db.to_csv("output.csv")
```

## Tests

```bash
pytest -v --cov=web_scraper
```

## Project Structure

```
src/web_scraper/
├── core/        # Engine, HTTP client, models, exceptions
├── parsers/     # HTML parsers (generic, custom)
├── storage/     # SQLite + CSV/JSON exporters
└── cli/         # Click-based command line interface
```

## Development

```bash
pip install -e ".[dev]"
ruff check src/
mypy src/
pytest --cov=web_scraper
```
