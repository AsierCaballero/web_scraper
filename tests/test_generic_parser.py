from web_scraper.parsers.generic import GenericParser
from web_scraper.core.models import ScrapeConfig


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
