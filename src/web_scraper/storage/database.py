from __future__ import annotations

import csv
import json
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..core.exceptions import StorageError
from ..core.models import ScrapedItem

Base = declarative_base()


class ItemTable(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(1024))
    description = Column(Text)
    content = Column(Text)
    author = Column(String(512))
    published_date = Column(DateTime, nullable=True)
    image_url = Column(String(2048))
    extra = Column(Text)
    scraped_at = Column(DateTime, default=datetime.now)


class Database:
    def __init__(self, path: str = "scraped.db") -> None:
        self.path = path
        self.engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

    def save(self, item: ScrapedItem) -> int:
        with self.session_factory() as session:
            row = self._to_row(item)
            session.add(row)
            session.commit()
            return row.id

    def save_many(self, items: list[ScrapedItem]) -> list[int]:
        if not items:
            return []
        with self.session_factory() as session:
            rows = [self._to_row(item) for item in items]
            session.bulk_save_objects(rows)
            session.commit()
            return [r.id for r in rows]

    def all(self, limit: int | None = None) -> list[ScrapedItem]:
        with self.session_factory() as session:
            q = session.query(ItemTable).order_by(ItemTable.scraped_at.desc())
            if limit:
                q = q.limit(limit)
            return [self._from_row(r) for r in q.all()]

    def by_url(self, url: str) -> list[ScrapedItem]:
        with self.session_factory() as session:
            rows = (
                session.query(ItemTable)
                .filter(ItemTable.url == url)
                .order_by(ItemTable.scraped_at.desc())
                .all()
            )
            return [self._from_row(r) for r in rows]

    def to_csv(self, path: str, items: list[ScrapedItem] | None = None) -> int:
        items = items or self.all()
        if not items:
            return 0
        fields = ["url", "title", "description", "author", "published_date", "image_url", "scraped_at"]
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                w.writeheader()
                for item in items:
                    d = item.model_dump()
                    for k in ("published_date", "scraped_at"):
                        if d.get(k):
                            d[k] = d[k].isoformat()
                    w.writerow(d)
            logger.info(f"CSV exported ({len(items)} items): {path}")
            return len(items)
        except Exception as e:
            raise StorageError(str(e))

    def to_json(self, path: str, items: list[ScrapedItem] | None = None) -> int:
        items = items or self.all()
        if not items:
            return 0
        try:
            data = [item.model_dump(mode="json") for item in items]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON exported ({len(items)} items): {path}")
            return len(items)
        except Exception as e:
            raise StorageError(str(e))

    def _to_row(self, item: ScrapedItem) -> ItemTable:
        return ItemTable(
            url=item.url,
            title=item.title,
            description=item.description,
            content=item.content,
            author=item.author,
            published_date=item.published_date,
            image_url=item.image_url,
            extra=json.dumps(item.extra) if item.extra else None,
            scraped_at=item.scraped_at,
        )

    def _from_row(self, row: ItemTable) -> ScrapedItem:
        return ScrapedItem(
            url=row.url,
            title=row.title,
            description=row.description,
            content=row.content,
            author=row.author,
            published_date=row.published_date,
            image_url=row.image_url,
            extra=json.loads(row.extra) if row.extra else {},
            scraped_at=row.scraped_at,
        )

    def close(self) -> None:
        self.engine.dispose()
