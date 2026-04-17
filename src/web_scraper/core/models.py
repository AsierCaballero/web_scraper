from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ScrapedItem(BaseModel):
    url: str
    title: str | None = None
    description: str | None = None
    content: str | None = None
    author: str | None = None
    published_date: datetime | None = None
    image_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime = Field(default_factory=datetime.now)


@dataclass
class ScrapeConfig:
    max_pages: int = 10
    follow_external_links: bool = False
    parse_html: bool = True
    extract_metadata: bool = True
    depth: int = 1


@dataclass
class ScrapeResult:
    items: list[ScrapedItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pages_scraped: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration(self) -> float | None:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
