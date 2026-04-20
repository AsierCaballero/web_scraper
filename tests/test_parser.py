from web_scraper.core.base_parser import BaseParser
from web_scraper.core.models import ScrapeConfig
from bs4 import BeautifulSoup


class _Concrete(BaseParser):
    def parse(self, _, url):
        return []

    def extract_links(self, html, base_url):
        return []


class TestBaseParser:
    def setup_method(self):
        self.p = _Concrete(ScrapeConfig())

    def test_safe_text_found(self):
        soup = BeautifulSoup("<p class='x'>Hi</p>", "lxml")
        assert self.p.safe_text(soup, "p.x") == "Hi"

    def test_safe_text_missing(self):
        soup = BeautifulSoup("<p>Hi</p>", "lxml")
        assert self.p.safe_text(soup, "span", default="fallback") == "fallback"

    def test_safe_attr(self):
        soup = BeautifulSoup("<a href='/go'>link</a>", "lxml")
        assert self.p.safe_attr(soup, "a", "href") == "/go"

    def test_abs_url_relative(self):
        assert self.p.abs_url("/page", "https://example.com") == "https://example.com/page"

    def test_abs_url_absolute(self):
        assert self.p.abs_url("https://other.com", "https://example.com") == "https://other.com"
