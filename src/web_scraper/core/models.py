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
    extra: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime = Field(default_factory=datetime.now)


@dataclass
class ScrapeConfig:
    max_pages: int = 10
    depth: int = 1
    timeout: int = 30
    requests_per_second: float = 1.0
    extract_metadata: bool = True

    def validate(self) -> None:
        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        if self.depth < 1:
            raise ValueError("depth must be at least 1")
        if self.requests_per_second <= 0 or self.requests_per_second > 100:
            raise ValueError("requests_per_second must be between 0 and 100")


@dataclass
class ScrapeResult:
    items: list[ScrapedItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    urls_visited: set[str] = field(default_factory=set)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration(self) -> float | None:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
