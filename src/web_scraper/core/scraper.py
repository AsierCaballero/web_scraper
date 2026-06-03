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
        self.http_client = http_client or HttpClient(
            timeout=self.config.timeout,
            requests_per_second=self.config.requests_per_second,
        )
        self.visited: set[str] = set()

    def scrape_urls(self, urls: list[str]) -> ScrapeResult:
        result = ScrapeResult()
        result.start_time = datetime.now()
        logger.info(f"Starting scrape of {len(urls)} URLs")

        queue = deque(urls)
        pages = 0

        while queue and pages < self.config.max_pages:
            url = queue.popleft()
            if url in self.visited:
                continue

            try:
                item = self._scrape_one(url)
                if item:
                    result.items.append(item)
                    result.urls_visited.add(url)
                    self.visited.add(url)
                    pages += 1

                    if self.storage:
                        self.storage.save(item)

                    if self.config.depth > 1:
                        html = self._fetch(url)
                        if html:
                            for link in self.parser.extract_links(html, url):
                                if link not in self.visited:
                                    queue.append(link)

            except (NetworkError, ParseError) as e:
                logger.error(f"Failed {url}: {e}")
                result.errors.append(str(e))

        result.pages_scraped = pages
        result.end_time = datetime.now()
        logger.success(f"Done: {pages} pages, {len(result.errors)} errors")
        return result

    def scrape_one(self, url: str) -> ScrapedItem | None:
        return self._scrape_one(url)

    def _scrape_one(self, url: str) -> ScrapedItem | None:
        resp = self.http_client.get(url)
        items = self.parser.parse(resp.text, url)
        if not items:
            return None
        item = items[0]
        if not item.title and not item.content:
            return None
        return item

    def _fetch(self, url: str) -> str | None:
        try:
            return self.http_client.get(url).text
        except NetworkError:
            return None

    def close(self) -> None:
        self.http_client.close()
        if self.storage:
            self.storage.close()

    def __enter__(self) -> "Scraper":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
