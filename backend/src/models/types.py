"""Custom SQLAlchemy types for cross-database compatibility.

These types work with both PostgreSQL (production) and SQLite (testing).
"""

import json
from typing import Any

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import String, TypeDecorator


class StringArray(TypeDecorator):
    """A type that stores string arrays.

    Uses PostgreSQL ARRAY on PostgreSQL, JSON-encoded TEXT on SQLite.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: list[str] | None, dialect: Dialect) -> str | list[str] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: str | list[str] | None, dialect: Dialect) -> list[str] | None:
        if value is None:
            return []
        if dialect.name == "postgresql":
            return value if value else []
        if isinstance(value, str):
            return json.loads(value) if value else []
        return value if value else []


class JSONDict(TypeDecorator):
    """A type that stores JSON dictionaries.

    Uses PostgreSQL JSONB on PostgreSQL, JSON-encoded TEXT on SQLite.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: dict[str, Any] | None, dialect: Dialect) -> str | dict[str, Any] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: str | dict[str, Any] | None, dialect: Dialect) -> dict[str, Any] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        if isinstance(value, str):
            return json.loads(value) if value else None
        return value
