from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from bs4 import Tag

from .exceptions import ParseError
from .models import ScrapeConfig, ScrapedItem


class BaseParser(ABC):
    def __init__(self, config: ScrapeConfig | None = None) -> None:
        self.config = config or ScrapeConfig()

    @abstractmethod
    def parse(self, html: str, url: str) -> list[ScrapedItem]:
        pass

    @abstractmethod
    def extract_links(self, html: str, base_url: str) -> list[str]:
        pass

    def safe_text(self, element: "Tag", selector: str, default: str | None = None) -> str | None:
        try:
            found = element.select_one(selector)
            return found.get_text(strip=True) if found else default
        except Exception as e:
            logger.warning(f"safe_text failed for '{selector}': {e}")
            return default

    def safe_attr(
        self, element: "Tag", selector: str, attr: str, default: str | None = None
    ) -> str | None:
        try:
            found = element.select_one(selector)
            return found.get(attr, default) if found else default
        except Exception as e:
            logger.warning(f"safe_attr failed for '{selector}.{attr}': {e}")
            return default

    def parse_date(self, raw: str | None) -> datetime | None:
        if not raw:
            return None
        for fmt in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
        ):
            try:
                return datetime.strptime(raw.strip(), fmt)
            except ValueError:
                continue
        return None

    def abs_url(self, url: str, base: str) -> str:
        from urllib.parse import urljoin

        return urljoin(base, url)

    def make_item(
        self,
        url: str,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
        author: str | None = None,
        published_date: datetime | None = None,
        image_url: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ScrapedItem:
        return ScrapedItem(
            url=url,
            title=title,
            description=description,
            content=content,
            author=author,
            published_date=published_date,
            image_url=image_url,
            extra=extra or {},
        )
