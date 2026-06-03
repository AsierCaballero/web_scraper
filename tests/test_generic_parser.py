from web_scraper.parsers.generic import GenericParser
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


class TestGenericParser:
    def setup_method(self):
        self.parser = GenericParser(ScrapeConfig())

    def test_basic_html(self, html, url):
        items = self.parser.parse(html, url)
        assert len(items) == 1
        assert items[0].title == "Test Article"

    def test_og_tags(self):
        h = """<html><head>
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Desc">
            <meta property="og:image" content="/img.jpg">
        </head><body><h1>Fallback</h1></body></html>"""
        items = self.parser.parse(h, "https://example.com")
        assert items[0].title == "OG Title"
        assert items[0].description == "OG Desc"
        assert items[0].image_url == "https://example.com/img.jpg"

    def test_extract_links(self):
        h = """<html><body>
            <a href="https://other.com/p1">A</a>
            <a href="/p2">B</a>
            <a href="#hash">C</a>
        </body></html>"""
        links = self.parser.extract_links(h, "https://example.com")
        assert "https://other.com/p1" in links
        assert "https://example.com/p2" in links
