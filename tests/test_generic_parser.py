import pytest

from web_scraper.parsers.generic import GenericParser
from web_scraper.core.models import ScrapeConfig


class TestGenericParser:
    def test_parse_basic_html(self):
        config = ScrapeConfig()
        parser = GenericParser(config)

        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <h1>Test Title</h1>
            <p>This is some content.</p>
        </body>
        </html>
        """

        items = parser.parse(html, "https://example.com/page")
        assert len(items) == 1
        assert items[0].title == "Test Page"
        assert items[0].description == "Test description"

    def test_parse_with_og_tags(self):
        config = ScrapeConfig()
        parser = GenericParser(config)

        html = """
        <html>
        <head>
            <title>Page Title</title>
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <meta property="og:image" content="/image.jpg">
            <meta property="article:published_time" content="2024-01-15T10:00:00Z">
        </head>
        <body>
            <h1>Page Title</h1>
        </body>
        </html>
        """

        items = parser.parse(html, "https://example.com/page")
        assert len(items) == 1
        assert items[0].title == "OG Title"
        assert items[0].description == "OG Description"
        assert items[0].image_url == "https://example.com/image.jpg"

    def test_extract_links(self):
        config = ScrapeConfig()
        parser = GenericParser(config)

        html = """
        <html>
        <body>
            <a href="https://example.com/page1">Link 1</a>
            <a href="/page2">Link 2</a>
            <a href="page3">Link 3</a>
        </body>
        </html>
        """

        links = parser.extract_links(html, "https://example.com")
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert "https://example.com/page3" in links

    def test_parse_minimal_html(self):
        config = ScrapeConfig()
        parser = GenericParser(config)

        html = "<html><body><p>Just content</p></body></html>"

        items = parser.parse(html, "https://example.com")
        assert len(items) == 1
        assert items[0].content is not None
