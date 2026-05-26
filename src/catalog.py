"""
catalog.py — Backend query layer: filter, sort, paginate cars.
Used by HomeView; keeps sorting logic in one place for consistent FE/BE behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal

from src.database import DB

SortField = Literal["price", "popularity", "newest", "rating", "availability"]
SortDirection = Literal["asc", "desc"]


class SortFieldEnum(str, Enum):
    PRICE = "price"
    POPULARITY = "popularity"
    NEWEST = "newest"
    RATING = "rating"
    AVAILABILITY = "availability"


SORT_LABELS: dict[str, str] = {
    "price": "Ціна",
    "popularity": "Популярність",
    "newest": "Новинки",
    "rating": "Рейтинг",
    "availability": "Доступність",
}


@dataclass
class CatalogQuery:
    search: str = ""
    fuel: str = "All"
    available_only: bool = False
    sort_field: SortField = "price"
    sort_direction: SortDirection = "asc"
    page: int = 1
    page_size: int = 6


@dataclass
class CatalogResult:
    items: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


def _popularity_map() -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in DB.get_rentals():
        cid = r.get("car_id")
        if cid:
            counts[cid] = counts.get(cid, 0) + 1
    return counts


def _parse_created(car: dict) -> datetime:
    raw = car.get("created_at") or "2020-01-01T00:00:00"
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return datetime(2020, 1, 1)


def _sort_key(sort_field: SortField, popularity: dict[str, int]):
    if sort_field == "price":
        return lambda c: float(c.get("price", 0))
    if sort_field == "popularity":
        return lambda c: popularity.get(c["id"], 0)
    if sort_field == "newest":
        return lambda c: _parse_created(c).timestamp()
    if sort_field == "rating":
        return lambda c: float(c.get("rating", 0))
    if sort_field == "availability":
        # Free cars first when ascending (0 = available)
        return lambda c: (1 if c.get("is_rented") else 0, c.get("brand", "").lower())
    return lambda c: c.get("brand", "").lower()


def filter_cars(query: CatalogQuery) -> list[dict]:
    """Apply filters only (no sort/pagination)."""
    cars = [dict(c) for c in DB.get_cars()]

    if query.available_only:
        cars = [c for c in cars if not c.get("is_rented")]

    if query.fuel != "All":
        cars = [c for c in cars if c.get("fuel") == query.fuel]

    q = query.search.strip().lower()
    if q:
        cars = [
            c
            for c in cars
            if q in c.get("brand", "").lower()
            or q in c.get("model", "").lower()
            or q in c.get("plate", "").lower()
        ]

    return cars


def sort_cars(cars: list[dict], sort_field: SortField, sort_direction: SortDirection) -> list[dict]:
    popularity = _popularity_map()
    key_fn = _sort_key(sort_field, popularity)
    reverse = sort_direction == "desc"
    return sorted(cars, key=key_fn, reverse=reverse)


def paginate_cars(cars: list[dict], page: int, page_size: int) -> CatalogResult:
    total = len(cars)
    page_size = max(1, page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return CatalogResult(
        items=cars[start:end],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def query_catalog(query: CatalogQuery) -> CatalogResult:
    """Full pipeline: filter → sort → paginate."""
    filtered = filter_cars(query)
    sorted_cars = sort_cars(filtered, query.sort_field, query.sort_direction)
    return paginate_cars(sorted_cars, query.page, query.page_size)
