import pytest

from web_scraper.core.base_parser import BaseParser
from web_scraper.core.models import ScrapeConfig


class TestBaseParser:
    def test_safe_extract_text_found(self):
        class TestParser(BaseParser):
            def parse(self, html, url):
                pass

            def extract_links(self, html, base_url):
                pass

        from bs4 import BeautifulSoup

        config = ScrapeConfig()
        parser = TestParser(config)

        html = "<div><p class='test'>Hello World</p></div>"
        soup = BeautifulSoup(html, "lxml")

        result = parser.safe_extract_text(soup, "p.test")
        assert result == "Hello World"

    def test_safe_extract_text_not_found(self):
        class TestParser(BaseParser):
            def parse(self, html, url):
                pass

            def extract_links(self, html, base_url):
                pass

        from bs4 import BeautifulSoup

        config = ScrapeConfig()
        parser = TestParser(config)

        html = "<div><p>Hello</p></div>"
        soup = BeautifulSoup(html, "lxml")

        result = parser.safe_extract_text(soup, "p.notexist", default="default")
        assert result == "default"

    def test_safe_extract_attr(self):
        class TestParser(BaseParser):
            def parse(self, html, url):
                pass

            def extract_links(self, html, base_url):
                pass

        from bs4 import BeautifulSoup

        config = ScrapeConfig()
        parser = TestParser(config)

        html = "<a href='https://example.com' class='link'>Link</a>"
        soup = BeautifulSoup(html, "lxml")

        result = parser.safe_extract_attr(soup, "a", "href")
        assert result == "https://example.com"

    def test_build_absolute_url(self):
        class TestParser(BaseParser):
            def parse(self, html, url):
                pass

            def extract_links(self, html, base_url):
                pass

        config = ScrapeConfig()
        parser = TestParser(config)

        result = parser.build_absolute_url("/page", "https://example.com")
        assert result == "https://example.com/page"

        result = parser.build_absolute_url("https://other.com", "https://example.com")
        assert result == "https://other.com"
