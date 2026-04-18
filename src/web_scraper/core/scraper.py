from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Any

from loguru import logger

from .base_parser import BaseParser
from .exceptions import NetworkError, ParseError
from .http_client import HttpClient
from .models import ScrapeConfig, ScrapeResult, ScrapedItem

if TYPE_CHECKING:
    from ..storage.database import Storage


class Scraper:
    def __init__(
        self,
        parser: BaseParser,
        storage: Storage | None = None,
        config: ScrapeConfig | None = None,
        http_client: HttpClient | None = None,
    ) -> None:
        self.parser = parser
        self.storage = storage
        self.config = config or ScrapeConfig()
        self.http_client = http_client or HttpClient()
        self.visited_urls: set[str] = set()

    def scrape(self, urls: list[str]) -> ScrapeResult:
        result = ScrapeResult()
        result.start_time = datetime.now()

        logger.info(f"Starting scrape of {len(urls)} initial URLs")
        queue = deque(urls)
        pages_scraped = 0

        while queue and pages_scraped < self.config.max_pages:
            url = queue.popleft()

            if url in self.visited_urls:
                continue

            try:
                item = self._scrape_single(url)
                if item:
                    result.items.append(item)
                    if self.storage:
                        self.storage.save_item(item)
                    self.visited_urls.add(url)
                    pages_scraped += 1

                    if self.config.depth > 1:
                        html = self._get_html_cached(url)
                        if html:
                            new_links = self.parser.extract_links(html, url)
                            for link in new_links[: self.config.max_pages - pages_scraped]:
                                if link not in self.visited_urls:
                                    queue.append(link)

            except (NetworkError, ParseError) as e:
                logger.error(f"Error scraping {url}: {e}")
                result.errors.append(str(e))

        result.pages_scraped = pages_scraped
        result.end_time = datetime.now()

        logger.info(
            f"Scraping complete: {pages_scraped} pages, {len(result.errors)} errors"
        )
        return result

    def _scrape_single(self, url: str) -> ScrapedItem | None:
        logger.debug(f"Scraping: {url}")

        response = self.http_client.get(url)
        html = response.text

        items = self.parser.parse(html, url)
        if not items:
            logger.warning(f"No items parsed from {url}")
            return None

        item = items[0]

        if not item.title and not item.description and not item.content:
            logger.warning(f"No useful content extracted from {url}")
            return None

        return item

    def _get_html_cached(self, url: str) -> str | None:
        try:
            response = self.http_client.get(url)
            return response.text
        except NetworkError:
            return None

    def scrape_single(self, url: str) -> ScrapedItem | None:
        return self._scrape_single(url)

    def close(self) -> None:
        self.http_client.close()
        if self.storage:
            self.storage.close()

    def __enter__(self) -> "Scraper":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()