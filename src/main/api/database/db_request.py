from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


@dataclass(frozen=True, slots=True)
class DBRequest:
    """Database-agnostic description of a read-only query."""

    table: str
    where: Mapping[str, Any] = field(default_factory=dict)
    limit: int | None = None

    def __post_init__(self) -> None:
        _validate_identifier(self.table)
        for column in self.where:
            _validate_identifier(column)
        if self.limit is not None and (
            isinstance(self.limit, bool)
            or not isinstance(self.limit, int)
            or self.limit < 1
        ):
            raise ValueError("DB request limit must be greater than zero")

        object.__setattr__(self, "where", MappingProxyType(dict(self.where)))

    @classmethod
    def select(
        cls,
        table: str,
        where: Mapping[str, Any] | None = None,
        *,
        limit: int | None = None,
    ) -> DBRequest:
        return cls(table=table, where=where or {}, limit=limit)

    def with_limit(self, limit: int) -> DBRequest:
        return replace(self, limit=limit)


def _validate_identifier(value: str) -> None:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe database identifier: {value!r}")
