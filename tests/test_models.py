import pytest
from datetime import datetime

from web_scraper.core.models import ScrapedItem, ScrapeConfig, ScrapeResult


class TestScrapedItem:
    def test_create_item(self):
        item = ScrapedItem(
            url="https://example.com",
            title="Test Title",
            description="Test description",
        )
        assert item.url == "https://example.com"
        assert item.title == "Test Title"
        assert item.description == "Test description"
        assert item.scraped_at is not None

    def test_item_with_datetime(self):
        date = datetime(2024, 1, 15, 10, 30, 0)
        item = ScrapedItem(
            url="https://example.com",
            title="Test",
            published_date=date,
        )
        assert item.published_date == date

    def test_item_with_metadata(self):
        item = ScrapedItem(
            url="https://example.com",
            title="Test",
            metadata={"source": "test", "priority": 1},
        )
        assert item.metadata["source"] == "test"
        assert item.metadata["priority"] == 1


class TestScrapeConfig:
    def test_default_config(self):
        config = ScrapeConfig()
        assert config.max_pages == 10
        assert config.follow_external_links is False
        assert config.parse_html is True
        assert config.depth == 1

    def test_custom_config(self):
        config = ScrapeConfig(max_pages=50, depth=3, follow_external_links=True)
        assert config.max_pages == 50
        assert config.depth == 3
        assert config.follow_external_links is True


class TestScrapeResult:
    def test_empty_result(self):
        result = ScrapeResult()
        assert result.items == []
        assert result.errors == []
        assert result.pages_scraped == 0

    def test_result_with_items(self):
        items = [
            ScrapedItem(url="https://example.com/1", title="Title 1"),
            ScrapedItem(url="https://example.com/2", title="Title 2"),
        ]
        result = ScrapeResult(items=items, pages_scraped=2)
        assert len(result.items) == 2
        assert result.pages_scraped == 2

    def test_duration_calculation(self):
        result = ScrapeResult()
        result.start_time = datetime(2024, 1, 1, 10, 0, 0)
        result.end_time = datetime(2024, 1, 1, 10, 1, 0)
        assert result.duration == 60.0
