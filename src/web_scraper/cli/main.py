from __future__ import annotations

import sys
from pathlib import Path

import click
from loguru import logger

from ..core.http_client import HttpClient
from ..core.models import ScrapeConfig
from ..core.scraper import Scraper
from ..parsers.generic import GenericParser
from ..storage.database import Storage


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("url")
@click.option("--max-pages", default=10, help="Maximum pages to scrape")
@click.option("--depth", default=1, help="Crawl depth")
@click.option("--output", "-o", default="scraped_data.db", help="Output database file")
@click.option("--format", "-f", type=click.Choice(["csv", "json", "both"]), default="csv")
@click.option("--export", "-e", help="Export file path")
@click.option("--rate-limit", default=1.0, help="Requests per second")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def scrape(
    url: str,
    max_pages: int,
    depth: int,
    output: str,
    format: str,
    export: str | None,
    rate_limit: float,
    verbose: bool,
) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if verbose else "INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )

    config = ScrapeConfig(max_pages=max_pages, depth=depth)
    storage = Storage(output)
    parser = GenericParser(config)
    http_client = HttpClient(requests_per_second=rate_limit)

    scraper = Scraper(parser=parser, storage=storage, config=config, http_client=http_client)

    try:
        logger.info(f"Starting scrape of: {url}")
        result = scraper.scrape([url])

        logger.info(f"Scraped {len(result.items)} items from {result.pages_scraped} pages")
        logger.info(f"Errors: {len(result.errors)}")

        if export:
            base_path = Path(export).with_suffix("")
            if format in ("csv", "both"):
                storage.export_csv(f"{base_path}.csv")
            if format in ("json", "both"):
                storage.export_json(f"{base_path}.json")

        if result.items:
            click.echo(f"\nFirst result:")
            item = result.items[0]
            click.echo(f"  Title: {item.title}")
            click.echo(f"  URL: {item.url}")
            if item.description:
                desc = item.description[:100] + "..." if len(item.description or "") > 100 else item.description
                click.echo(f"  Description: {desc}")

    finally:
        scraper.close()


@cli.command()
@click.argument("db_file", default="scraped_data.db")
@click.option("--limit", default=10, help="Number of items to show")
def list(db_file: str, limit: int) -> None:
    storage = Storage(db_file)
    items = storage.get_all(limit=limit)

    if not items:
        click.echo("No items found")
        return

    for i, item in enumerate(items, 1):
        click.echo(f"\n{i}. {item.title or 'No title'}")
        click.echo(f"   URL: {item.url}")
        if item.description:
            desc = item.description[:80] + "..." if len(item.description or "") > 80 else item.description
            click.echo(f"   Description: {desc}")

    storage.close()


@cli.command()
@click.argument("db_file", default="scraped_data.db")
@click.argument("output_file")
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
def export(db_file: str, output_file: str, format: str) -> None:
    storage = Storage(db_file)

    if format == "csv":
        count = storage.export_csv(output_file)
    else:
        count = storage.export_json(output_file)

    click.echo(f"Exported {count} items to {output_file}")
    storage.close()


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
