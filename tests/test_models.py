from datetime import datetime

from web_scraper.core.models import ScrapedItem, ScrapeConfig, ScrapeResult


class TestScrapedItem:
    def test_minimal(self):
        item = ScrapedItem(url="https://example.com")
        assert item.url == "https://example.com"
        assert item.title is None

    def test_full(self):
        dt = datetime(2026, 4, 17)
        item = ScrapedItem(
            url="https://example.com",
            title="Hello",
            description="Desc",
            published_date=dt,
            extra={"key": "val"},
        )
        assert item.title == "Hello"
        assert item.published_date == dt
        assert item.extra["key"] == "val"


class TestScrapeConfig:
    def test_defaults(self):
        c = ScrapeConfig()
        assert c.max_pages == 10
        assert c.depth == 1

    def test_validate_ok(self):
        ScrapeConfig(max_pages=5, depth=2).validate()

    def test_validate_fail(self):
        import pytest
        with pytest.raises(ValueError):
            ScrapeConfig(max_pages=0).validate()


class TestScrapeResult:
    def test_duration(self):
        r = ScrapeResult()
        r.start_time = datetime(2026, 4, 17, 10, 0, 0)
        r.end_time = datetime(2026, 4, 17, 10, 1, 30)
        assert r.duration == 90.0

    def test_no_duration(self):
        r = ScrapeResult()
        assert r.duration is None
