from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from loguru import logger

from ..core.base_parser import BaseParser

if TYPE_CHECKING:
    from ..core.models import ScrapedItem


class GenericParser(BaseParser):
    def parse(self, html: str, url: str) -> list[ScrapedItem]:
        soup = BeautifulSoup(html, "lxml")

        title = self._title(soup, url)
        description = self._description(soup)
        content = self._content(soup)
        author = self._author(soup)
        published_date = self.parse_date(self._date(soup))
        image_url = self._image(soup, url)

        extra = {}
        if self.config.extract_metadata:
            extra = self._meta(soup)

        item = self.make_item(
            url=url,
            title=title,
            description=description,
            content=content,
            author=author,
            published_date=published_date,
            image_url=image_url,
            extra=extra,
        )
        return [item]

    def _title(self, soup: BeautifulSoup, url: str) -> str | None:
        title = None
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            title = og["content"]
        if not title and soup.title:
            title = soup.title.get_text(strip=True)
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
        logger.debug(f"title [{url}]: {title}")
        return title

    def _description(self, soup: BeautifulSoup) -> str | None:
        og = soup.find("meta", property="og:description")
        if og and og.get("content"):
            return og["content"]
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"]
        return None

    def _content(self, soup: BeautifulSoup) -> str | None:
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        article = soup.find("article") or soup.find("main") or soup.find("body")
        if article:
            return article.get_text(separator="\n", strip=True)
        return None

    def _author(self, soup: BeautifulSoup) -> str | None:
        meta = soup.find("meta", attrs={"name": "author"})
        if meta and meta.get("content"):
            return meta["content"]
        link = soup.find("a", class_=lambda x: x and "author" in x.lower())
        if link:
            return link.get_text(strip=True)
        return None

    def _date(self, soup: BeautifulSoup) -> str | None:
        time_tag = soup.find("time")
        if time_tag:
            raw = time_tag.get("datetime") or time_tag.get("content")
            if raw:
                return raw
        meta = soup.find("meta", property="article:published_time")
        if meta and meta.get("content"):
            return meta["content"]
        return None

    def _image(self, soup: BeautifulSoup, base_url: str) -> str | None:
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return self.abs_url(og["content"], base_url)
        container = soup.find("article") or soup.find("main") or soup
        img = container.find("img", src=True)
        if img:
            return self.abs_url(img["src"], base_url)
        return None

    def _meta(self, soup: BeautifulSoup) -> dict[str, str]:
        meta = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                meta[name] = content
        return meta

    def extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("http://", "https://")):
                links.add(href)
            elif href.startswith("/"):
                links.add(self.abs_url(href, base_url))
        return list(links)
