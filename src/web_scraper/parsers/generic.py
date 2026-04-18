from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from loguru import logger

from ..core.base_parser import BaseParser
from ..core.models import ScrapedItem


class GenericParser(BaseParser):
    def parse(self, html: str, url: str) -> list[ScrapedItem]:
        soup = BeautifulSoup(html, "lxml")
        parsed_url = urlparse(url)

        title = self._extract_title(soup, url)
        description = self._extract_description(soup)
        content = self._extract_content(soup)
        author = self._extract_author(soup)
        published_date = self._extract_date(soup)
        image_url = self._extract_main_image(soup, url)

        metadata = {}
        if self.config.extract_metadata:
            metadata = self._extract_all_metadata(soup)

        item = self.create_item(
            url=url,
            title=title,
            description=description,
            content=content,
            author=author,
            published_date=published_date,
            image_url=image_url,
            metadata=metadata,
        )

        return [item]

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str | None:
        title = None

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]

        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)

        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

        logger.debug(f"Extracted title from {url}: {title}")
        return title

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        desc = None

        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc["content"]

        if not desc:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                desc = meta_desc["content"]

        return desc

    def _extract_content(self, soup: BeautifulSoup) -> str | None:
        article = soup.find("article")
        if article:
            return article.get_text(separator="\n", strip=True)

        main = soup.find("main")
        if main:
            return main.get_text(separator="\n", strip=True)

        body = soup.find("body")
        if body:
            for tag in body.find_all(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return body.get_text(separator="\n", strip=True)

        return None

    def _extract_author(self, soup: BeautifulSoup) -> str | None:
        author = None

        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            author = meta_author["content"]

        if not author:
            author_link = soup.find("a", class_=lambda x: x and "author" in x.lower())
            if author_link:
                author = author_link.get_text(strip=True)

        return author

    def _extract_date(self, soup: BeautifulSoup) -> Any:
        date_str = None

        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            date_str = time_tag["datetime"]
        elif time_tag and time_tag.get("content"):
            date_str = time_tag["content"]

        if not date_str:
            meta_date = soup.find("meta", property="article:published_time")
            if meta_date and meta_date.get("content"):
                date_str = meta_date["content"]

        return self.parse_datetime(date_str)

    def _extract_main_image(self, soup: BeautifulSoup, base_url: str) -> str | None:
        image_url = None

        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = self.build_absolute_url(og_image["content"], base_url)

        if not image_url:
            img = soup.find("article") or soup.find("main") or soup
            first_img = img.find("img", src=True)
            if first_img:
                image_url = self.build_absolute_url(first_img["src"], base_url)

        return image_url

    def _extract_all_metadata(self, soup: BeautifulSoup) -> dict[str, Any]:
        metadata = {}

        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                metadata[name] = content

        return metadata

    def extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith(("http://", "https://")):
                links.append(href)
            elif href.startswith("/"):
                from urllib.parse import urljoin

                links.append(urljoin(base_url, href))

        return list(set(links))
