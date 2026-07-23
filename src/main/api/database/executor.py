from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import psycopg

from src.main.api.database.db_request import DBRequest

DatabaseRow = dict[str, Any]


class DBExecutor(ABC):
    """Executes DBRequest instances against a concrete database source."""

    def fetch_one(self, request: DBRequest) -> DatabaseRow | None:
        rows = self.fetch_all(request.with_limit(1))
        return rows[0] if rows else None

    @abstractmethod
    def fetch_all(self, request: DBRequest) -> list[DatabaseRow]: ...


class TeamCityBackupExecutor(DBExecutor):
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path

    def fetch_all(self, request: DBRequest) -> list[DatabaseRow]:
        normalized_where = {
            key.upper(): _normalize_comparison_value(value)
            for key, value in request.where.items()
        }
        member = f"database_dump/{request.table.lower()}"

        with ZipFile(self.archive_path) as archive:
            try:
                with archive.open(member) as table_file:
                    lines = (line.decode("utf-8") for line in table_file)
                    reader = csv.DictReader(lines, skipinitialspace=True)
                    rows = [
                        {
                            str(key).upper(): _normalize_snapshot_value(value)
                            for key, value in row.items()
                        }
                        for row in reader
                    ]
            except KeyError as error:
                raise LookupError(
                    f"Table {request.table!r} is absent from the "
                    "TeamCity database snapshot"
                ) from error

        matched_rows = [
            row
            for row in rows
            if all(
                _normalize_comparison_value(row.get(column)) == expected
                for column, expected in normalized_where.items()
            )
        ]
        if request.limit is not None:
            return matched_rows[: request.limit]
        return matched_rows


class PostgreSQLExecutor(DBExecutor):
    def __init__(self, connection: psycopg.Connection[DatabaseRow]):
        self.connection = connection

    def fetch_all(self, request: DBRequest) -> list[DatabaseRow]:
        query = f"SELECT * FROM {request.table}"
        params: list[Any] = []
        columns = list(request.where)

        if columns:
            query += " WHERE " + " AND ".join(f"{column} = %s" for column in columns)
            params.extend(
                int(request.where[column])
                if isinstance(request.where[column], bool)
                else request.where[column]
                for column in columns
            )
        if request.limit is not None:
            query += f" LIMIT {request.limit}"

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return [
                {str(key).upper(): value for key, value in row.items()}
                for row in cursor.fetchall()
            ]


def _normalize_snapshot_value(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


def _normalize_comparison_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)
