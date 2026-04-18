from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .exceptions import StorageError
from .models import ScrapedItem

Base = declarative_base()


class ScraperTable(Base):
    __tablename__ = "scraped_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(1024))
    description = Column(Text)
    content = Column(Text)
    author = Column(String(512))
    published_date = Column(DateTime, nullable=True)
    image_url = Column(String(2048))
    metadata = Column(Text)
    scraped_at = Column(DateTime, default=datetime.now)


class Storage:
    def __init__(self, db_path: str = "scraped_data.db") -> None:
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_item(self, item: ScrapedItem) -> int:
        with self.SessionLocal() as session:
            db_item = ScraperTable(
                url=item.url,
                title=item.title,
                description=item.description,
                content=item.content,
                author=item.author,
                published_date=item.published_date,
                image_url=item.image_url,
                metadata=json.dumps(item.metadata) if item.metadata else None,
                scraped_at=item.scraped_at,
            )
            session.add(db_item)
            session.commit()
            return db_item.id

    def save_batch(self, items: list[ScrapedItem]) -> list[int]:
        if not items:
            return []
        with self.SessionLocal() as session:
            db_items = [
                ScraperTable(
                    url=item.url,
                    title=item.title,
                    description=item.description,
                    content=item.content,
                    author=item.author,
                    published_date=item.published_date,
                    image_url=item.image_url,
                    metadata=json.dumps(item.metadata) if item.metadata else None,
                    scraped_at=item.scraped_at,
                )
                for item in items
            ]
            session.bulk_save_objects(db_items)
            session.commit()
            return [item.id for item in db_items]

    def get_all(self, limit: int | None = None) -> list[ScrapedItem]:
        with self.SessionLocal() as session:
            query = session.query(ScraperTable).order_by(ScraperTable.scraped_at.desc())
            if limit:
                query = query.limit(limit)
            rows = query.all()
            return self._rows_to_items(rows)

    def get_by_url(self, url: str) -> list[ScrapedItem]:
        with self.SessionLocal() as session:
            rows = (
                session.query(ScraperTable)
                .filter(ScraperTable.url == url)
                .order_by(ScraperTable.scraped_at.desc())
                .all()
            )
            return self._rows_to_items(rows)

    def _rows_to_items(self, rows: list[ScraperTable]) -> list[ScrapedItem]:
        items = []
        for row in rows:
            items.append(
                ScrapedItem(
                    url=row.url,
                    title=row.title,
                    description=row.description,
                    content=row.content,
                    author=row.author,
                    published_date=row.published_date,
                    image_url=row.image_url,
                    metadata=json.loads(row.metadata) if row.metadata else {},
                    scraped_at=row.scraped_at,
                )
            )
        return items

    def export_csv(self, filepath: str, items: list[ScrapedItem] | None = None) -> int:
        items = items or self.get_all()
        if not items:
            return 0
        fieldnames = [
            "url",
            "title",
            "description",
            "content",
            "author",
            "published_date",
            "image_url",
            "scraped_at",
        ]
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for item in items:
                    row = item.model_dump()
                    if row.get("published_date"):
                        row["published_date"] = row["published_date"].isoformat()
                    if row.get("scraped_at"):
                        row["scraped_at"] = row["scraped_at"].isoformat()
                    writer.writerow(row)
            logger.info(f"Exported {len(items)} items to CSV: {filepath}")
            return len(items)
        except Exception as e:
            raise StorageError(f"Failed to export CSV: {e}")

    def export_json(self, filepath: str, items: list[ScrapedItem] | None = None) -> int:
        items = items or self.get_all()
        if not items:
            return 0
        try:
            data = [item.model_dump(mode="json") for item in items]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(items)} items to JSON: {filepath}")
            return len(items)
        except Exception as e:
            raise StorageError(f"Failed to export JSON: {e}")

    def close(self) -> None:
        self.engine.dispose()
