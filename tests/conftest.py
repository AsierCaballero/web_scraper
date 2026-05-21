import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def html():
    return """<html><head>
    <title>Test Article</title>
    <meta name="description" content="A test page">
</head><body>
    <article>
        <h1>Test Article</h1>
        <p>Content body here.</p>
    </article>
</body></html>"""


@pytest.fixture
def url():
    return "https://example.com/article"


@pytest.fixture
def config():
    from web_scraper.core.models import ScrapeConfig
    return ScrapeConfig()
