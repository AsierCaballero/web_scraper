from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import NetworkError, RateLimitError


class RateLimiter:
    def __init__(self, requests_per_second: float = 1.0) -> None:
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0

    def wait(self) -> None:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()


class HttpClient:
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        requests_per_second: float = 1.0,
        user_agent: str | None = None,
    ) -> None:
        self.timeout = timeout
        self.rate_limiter = RateLimiter(requests_per_second)
        self.user_agent = user_agent or "WebScraper/1.0"

        self.session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=0,
            pool_connections=10,
            pool_maxsize=10,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_headers(self, referer: str | None = None) -> dict[str, str]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    @retry(
        retry=retry_if_exception_type((NetworkError, RateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get(
        self,
        url: str,
        referer: str | None = None,
        allow_redirects: bool = True,
    ) -> requests.Response:
        self.rate_limiter.wait()

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        try:
            logger.debug(f"GET {url}")
            response = self.session.get(
                url,
                headers=self._build_headers(referer or base_url),
                timeout=self.timeout,
                allow_redirects=allow_redirects,
            )

            if response.status_code == 429:
                raise RateLimitError(
                    message="Rate limit exceeded",
                    url=url,
                )

            response.raise_for_status()
            return response

        except requests.RequestException as e:
            raise NetworkError(
                message=str(e),
                url=url,
                original_exception=e,
            ) from e

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
