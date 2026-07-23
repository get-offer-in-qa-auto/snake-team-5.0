from collections.abc import Mapping
from typing import Any

import pytest

from src.main.api.database.db_request import DBRequest


def test_db_request_copies_conditions() -> None:
    where: dict[str, Any] = {"username": "alice"}

    request = DBRequest.select("users", where)
    where["username"] = "bob"

    assert request.where == {"username": "alice"}


def test_db_request_conditions_are_read_only() -> None:
    request = DBRequest.select("users", {"username": "alice"})

    with pytest.raises(TypeError):
        _replace_condition(request.where, "username", "bob")


@pytest.mark.parametrize(
    ("table", "where"),
    [
        ("users; DROP TABLE users", {}),
        ("users", {"username OR 1=1": "alice"}),
    ],
)
def test_db_request_rejects_unsafe_identifiers(
    table: str, where: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="Unsafe database identifier"):
        DBRequest.select(table, where)


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_db_request_rejects_invalid_limit(limit: Any) -> None:
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        DBRequest.select("users", limit=limit)


def _replace_condition(where: Mapping[str, Any], column: str, value: Any) -> None:
    where[column] = value  # type: ignore[index]
