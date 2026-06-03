from __future__ import annotations

import sys

import click
from loguru import logger

from ..core.http_client import HttpClient
from ..core.models import ScrapeConfig
from ..core.scraper import Scraper
from ..parsers.generic import GenericParser
from ..storage.database import Database


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("url")
@click.option("--max-pages", default=10, help="Maximum pages to scrape")
@click.option("--depth", default=1, help="Crawl depth")
@click.option("--db", default="scraped.db", help="SQLite database path")
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--export", "-e", help="Export file path")
@click.option("--rate-limit", default=1.0, help="Requests per second")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
def scrape(
    url: str,
    max_pages: int,
    depth: int,
    db: str,
    format: str,
    export: str | None,
    rate_limit: float,
    verbose: bool,
) -> None:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if verbose else "INFO")

    config = ScrapeConfig(
        max_pages=max_pages,
        depth=depth,
        requests_per_second=rate_limit,
    )
    database = Database(db)
    parser = GenericParser(config)
    http = HttpClient(requests_per_second=rate_limit)
    scraper = Scraper(parser=parser, storage=database, config=config, http_client=http)

    try:
        result = scraper.scrape_urls([url])
        click.echo(f"\nScraped: {len(result.items)} items from {result.pages_scraped} pages")
        click.echo(f"Errors: {len(result.errors)}")

        if export:
            ext = format
            database.to_json(export) if ext == "json" else database.to_csv(export)

        if result.items:
            item = result.items[0]
            click.echo(f"\nFirst result:")
            click.echo(f"  Title: {item.title or 'N/A'}")
            click.echo(f"  URL:   {item.url}")
            if item.description:
                desc = item.description[:100]
                click.echo(f"  Desc:  {desc}{'...' if len(item.description) > 100 else ''}")

    finally:
        scraper.close()


@cli.command()
@click.argument("db", default="scraped.db")
@click.option("--limit", default=10, help="Rows to show")
def list(db: str, limit: int) -> None:
    database = Database(db)
    items = database.all(limit=limit)
    if not items:
        click.echo("No items found.")
        return
    click.echo(f"\n{'#':>3}  {'Title':<50} {'Date':<20}")
    click.echo("-" * 75)
    for i, item in enumerate(items, 1):
        title = (item.title or "N/A")[:48]
        date = item.scraped_at.strftime("%Y-%m-%d %H:%M") if item.scraped_at else "N/A"
        click.echo(f"{i:>3}  {title:<50} {date:<20}")
    database.close()


@cli.command()
@click.argument("db", default="scraped.db")
@click.argument("output")
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
def export(db: str, output: str, format: str) -> None:
    database = Database(db)
    count = database.to_json(output) if format == "json" else database.to_csv(output)
    click.echo(f"Exported {count} items to {output}")
    database.close()


if __name__ == "__main__":
    cli()
