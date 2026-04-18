import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_html():
    return """
    <html>
    <head>
        <title>Sample Page</title>
        <meta name="description" content="Sample description">
    </head>
    <body>
        <article>
            <h1>Sample Title</h1>
            <p>This is the main content of the page.</p>
        </article>
    </body>
    </html>
    """


@pytest.fixture
def sample_url():
    return "https://example.com/page"