from __future__ import annotations

from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB

JSONVariant = JSON().with_variant(JSONB, "postgresql")


class VectorType(TypeDecorator[list[float] | None]):
    impl = JSON
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: Any, dialect):  # type: ignore[override]
        if value is None:
            return None
        return [float(item) for item in value]

    def process_result_value(self, value: Any, dialect):  # type: ignore[override]
        if value is None:
            return None
        return [float(item) for item in value]

