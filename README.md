# Web Scraper

A professional, production-ready web scraping framework built with Python.

## Features

- **HTTP Client**: Built-in rate limiting and automatic retry with exponential backoff
- **Modular Parsers**: Easy to extend with custom parsers for different websites
- **Data Storage**: SQLite database with CSV/JSON export capabilities
- **CLI Interface**: Clean command-line interface for quick scraping tasks
- **Error Handling**: Comprehensive exception hierarchy for better debugging
- **Type Safety**: Full type hints with Pydantic models
- **Logging**: Structured logging with Loguru

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Scrape a single URL
web-scraper scrape "https://example.com" -o data.db -f csv -e output

# List scraped data
web-scraper list data.db --limit 10

# Export to different formats
web-scraper export data.db data.json --format json
```

## Python API

```python
from web_scraper import Scraper, GenericParser, Storage, ScrapeConfig

# Configure
config = ScrapeConfig(max_pages=10, depth=1)

# Initialize
storage = Storage("scraped.db")
parser = GenericParser(config)

# Scrape
with Scraper(parser=parser, storage=config) as scraper:
    result = scraper.scrape(["https://example.com"])
    print(f"Scraped {len(result.items)} items")

# Export
storage.export_csv("output.csv")
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=web_scraper
```

## License

MIT License
