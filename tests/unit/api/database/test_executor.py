from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest

from src.main.api.database.db_request import DBRequest
from src.main.api.database.executor import (
    PostgreSQLExecutor,
    TeamCityBackupExecutor,
)


def test_backup_executor_filters_and_normalizes_rows(tmp_path: Path) -> None:
    archive_path = tmp_path / "database.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "database_dump/users",
            "ID,USERNAME,ENABLED,EMAIL\n1,alice,1,alice@example.test\n2,bob,0,\n",
        )

    executor = TeamCityBackupExecutor(archive_path)

    row = executor.fetch_one(
        DBRequest.select("users", {"username": "alice", "enabled": True})
    )

    assert row == {
        "ID": "1",
        "USERNAME": "alice",
        "ENABLED": "1",
        "EMAIL": "alice@example.test",
    }


def test_backup_executor_reports_missing_table(tmp_path: Path) -> None:
    archive_path = tmp_path / "database.zip"
    with ZipFile(archive_path, "w"):
        pass

    executor = TeamCityBackupExecutor(archive_path)

    with pytest.raises(LookupError, match="'users'.*snapshot"):
        executor.fetch_all(DBRequest.select("users"))


def test_postgresql_executor_builds_parameterized_select() -> None:
    connection = _Connection(rows=[{"id": 1, "username": "alice", "enabled": 1}])
    executor = PostgreSQLExecutor(connection)  # type: ignore[arg-type]

    rows = executor.fetch_all(
        DBRequest.select(
            "users",
            {"username": "alice", "enabled": True},
            limit=2,
        )
    )

    assert connection.cursor_instance.executed == (
        "SELECT * FROM users WHERE username = %s AND enabled = %s LIMIT 2",
        ["alice", 1],
    )
    assert rows == [{"ID": 1, "USERNAME": "alice", "ENABLED": 1}]


def test_executor_fetch_one_applies_limit() -> None:
    connection = _Connection(rows=[{"id": 1}, {"id": 2}])
    executor = PostgreSQLExecutor(connection)  # type: ignore[arg-type]

    row = executor.fetch_one(DBRequest.select("users"))

    assert connection.cursor_instance.executed == (
        "SELECT * FROM users LIMIT 1",
        [],
    )
    assert row == {"ID": 1}


class _Cursor:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
        self.executed: tuple[str, list[Any]] | None = None

    def __enter__(self) -> _Cursor:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, query: str, params: list[Any]) -> None:
        self.executed = (query, params)

    def fetchall(self) -> list[dict[str, Any]]:
        if self.executed is None:
            raise AssertionError("Query must be executed before fetching rows")
        query, _ = self.executed
        if "LIMIT 1" in query:
            return self.rows[:1]
        return self.rows


class _Connection:
    def __init__(self, rows: list[dict[str, Any]]):
        self.cursor_instance = _Cursor(rows)

    def cursor(self) -> _Cursor:
        return self.cursor_instance
