from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from math import ceil

from dateutil import parser


def parse_partial_date(value: str | None) -> date | None:
    if not value:
        return None
    lowered = value.strip().lower()
    if lowered in {"present", "current", "now"}:
        return date.today()
    try:
        return parser.parse(value, default=datetime(1900, 1, 1)).date()
    except (ValueError, OverflowError, TypeError):
        return None


def months_between(start: str | None, end: str | None) -> int:
    start_date = parse_partial_date(start)
    end_date = parse_partial_date(end)
    if not start_date or not end_date or end_date < start_date:
        return 0
    return max((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month), 0) + 1


def years_from_ranges(ranges: Iterable[tuple[str | None, str | None]]) -> float:
    total_months = sum(months_between(start, end) for start, end in ranges)
    return round(total_months / 12, 1) if total_months else 0.0


def rounded_years(value: float) -> float:
    return round(value, 1)


def ceil_years(value: float) -> int:
    return ceil(value)
