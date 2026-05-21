from typing import Any


class ScraperError(Exception):
    def __init__(self, message: str, url: str | None = None) -> None:
        self.message = message
        self.url = url
        super().__init__(message)

    def __str__(self) -> str:
        location = f" [{self.url}]" if self.url else ""
        return f"{type(self).__name__}{location}: {self.message}"


class NetworkError(ScraperError):
    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.status_code = status_code
        super().__init__(message, url)

    def __str__(self) -> str:
        base = super().__str__()
        status = f" (HTTP {self.status_code})" if self.status_code else ""
        return base + status


class RateLimitError(ScraperError):
    pass


class ParseError(ScraperError):
    def __init__(
        self,
        message: str,
        url: str | None = None,
        field: str | None = None,
    ) -> None:
        self.field = field
        super().__init__(message, url)

    def __str__(self) -> str:
        base = super().__str__()
        field_info = f" field='{self.field}'" if self.field else ""
        return base + field_info


class StorageError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"StorageError: {self.message}"
