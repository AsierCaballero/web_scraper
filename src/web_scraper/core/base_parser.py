from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup
from loguru import logger

from .exceptions import ParseError
from .models import ScrapeConfig, ScrapedItem

if TYPE_CHECKING:
    import requests


class BaseParser(ABC):
    def __init__(self, config: ScrapeConfig | None = None) -> None:
        self.config = config or ScrapeConfig()

    @abstractmethod
    def parse(self, html: str, url: str) -> list[ScrapedItem]:
        pass

    @abstractmethod
    def extract_links(self, html: str, base_url: str) -> list[str]:
        pass

    def safe_extract_text(
        self,
        element: Any,
        selector: str,
        default: str | None = None,
        strip: bool = True,
    ) -> str | None:
        try:
            found = element.select_one(selector)
            if not found:
                return default
            text = found.get_text()
            return text.strip() if strip else text
        except Exception as e:
            logger.warning(f"Failed to extract text for {selector}: {e}")
            return default

    def safe_extract_attr(
        self,
        element: Any,
        selector: str,
        attribute: str,
        default: str | None = None,
    ) -> str | None:
        try:
            found = element.select_one(selector)
            if not found:
                return default
            return found.get(attribute) or default
        except Exception as e:
            logger.warning(f"Failed to extract attr {attribute} for {selector}: {e}")
            return default

    def parse_datetime(self, date_string: str | None) -> datetime | None:
        if not date_string:
            return None
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        return None

    def build_absolute_url(self, url: str, base_url: str) -> str:
        from urllib.parse import urljoin

        return urljoin(base_url, url)

    def create_item(
        self,
        url: str,
        title: str | None = None,
        description: str | None = None,
        content: str | None = None,
        author: str | None = None,
        published_date: datetime | None = None,
        image_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ScrapedItem:
        return ScrapedItem(
            url=url,
            title=title,
            description=description,
            content=content,
            author=author,
            published_date=published_date,
            image_url=image_url,
            metadata=metadata or {},
        )