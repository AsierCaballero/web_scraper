from dataclasses import dataclass
from typing import Any


@dataclass
class ScraperError(Exception):
    message: str
    url: str | None = None
    original_exception: Exception | None = None

    def __str__(self) -> str:
        location = f" (URL: {self.url})" if self.url else ""
        return f"ScraperError{location}: {self.message}"


@dataclass
class RateLimitError(ScraperError):
    pass


@dataclass
class ProxyError(ScraperError):
    pass


@dataclass
class ParseError(ScraperError):
    field: str | None = None

    def __str__(self) -> str:
        location = f" (URL: {self.url})" if self.url else ""
        field_info = f" [field: {self.field}]" if self.field else ""
        return f"ParseError{location}{field_info}: {self.message}"


@dataclass
class NetworkError(ScraperError):
    pass


@dataclass
class StorageError(Exception):
    message: str

    def __str__(self) -> str:
        return f"StorageError: {self.message}"