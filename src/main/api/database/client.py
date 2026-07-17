from __future__ import annotations

import csv
import re
import subprocess
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from zipfile import ZipFile

import psycopg
import requests
from filelock import FileLock
from psycopg.rows import dict_row

from src.main.api.configs.config import Config
from src.main.api.specs.request_specs import RequestSpecs

DatabaseRow = dict[str, Any]
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


class DatabaseSnapshot(ABC):
    @abstractmethod
    def fetch_one(self, table: str, where: Mapping[str, Any]) -> DatabaseRow | None: ...

    @abstractmethod
    def fetch_all(
        self, table: str, where: Mapping[str, Any] | None = None
    ) -> list[DatabaseRow]: ...


class DatabaseClient(ABC):
    @abstractmethod
    @contextmanager
    def snapshot(self) -> Iterator[DatabaseSnapshot]: ...


class TeamCityBackupSnapshot(DatabaseSnapshot):
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path

    def fetch_one(self, table: str, where: Mapping[str, Any]) -> DatabaseRow | None:
        rows = self.fetch_all(table, where)
        return rows[0] if rows else None

    def fetch_all(
        self, table: str, where: Mapping[str, Any] | None = None
    ) -> list[DatabaseRow]:
        _validate_identifier(table)
        normalized_where = {
            key.upper(): _normalize_comparison_value(value)
            for key, value in (where or {}).items()
        }
        for column in normalized_where:
            _validate_identifier(column)

        member = f"database_dump/{table.lower()}"
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
                    f"Table {table!r} is absent from the TeamCity database snapshot"
                ) from error

        return [
            row
            for row in rows
            if all(
                _normalize_comparison_value(row.get(column)) == expected
                for column, expected in normalized_where.items()
            )
        ]


class TeamCityBackupDatabaseClient(DatabaseClient):
    def __init__(self) -> None:
        self.server_url = RequestSpecs._server_url()
        self.timeout = int(Config.get("TEAMCITY_REQUEST_TIMEOUT", "20"))
        self.backup_timeout = int(Config.get("TEAMCITY_DB_BACKUP_TIMEOUT", "120"))
        self.backup_dir = _configured_backup_dir()
        self.container = str(Config.get("TEAMCITY_DB_CONTAINER", "")).strip()
        self.container_backup_dir = str(
            Config.get(
                "TEAMCITY_DB_CONTAINER_BACKUP_DIR",
                "/data/teamcity_server/datadir/backup",
            )
        ).rstrip("/")
        lock_dir = self.backup_dir or Path("artifacts/teamcity-backups")
        lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock = FileLock(lock_dir / ".database-snapshot.lock")

    @contextmanager
    def snapshot(self) -> Iterator[DatabaseSnapshot]:
        with self.lock.acquire(timeout=self.backup_timeout):
            with TemporaryDirectory(prefix="teamcity-db-") as temp_dir:
                archive_path = self._create_backup(Path(temp_dir))
                try:
                    yield TeamCityBackupSnapshot(archive_path)
                finally:
                    self._remove_server_backup(archive_path.name)

    def _create_backup(self, temp_dir: Path) -> Path:
        self._wait_until_idle()
        file_name = f"autotest-db-{uuid.uuid4().hex}.zip"
        response = requests.post(
            f"{self.server_url}/app/rest/server/backup",
            params={
                "includeConfigs": "false",
                "includeDatabase": "true",
                "includeBuildLogs": "false",
                "addTimestamp": "false",
                "fileName": file_name,
            },
            headers=self._backup_headers(csrf=True),
            timeout=self.timeout,
        )
        response.raise_for_status()
        actual_name = response.text.strip() or file_name
        self._wait_until_idle()

        shared_archive = self.backup_dir / actual_name if self.backup_dir else None
        if shared_archive and shared_archive.is_file():
            return shared_archive
        if not self.container:
            raise FileNotFoundError(
                "TeamCity database backup was created but is not accessible. "
                "Set TEAMCITY_DB_BACKUP_DIR to the shared backup directory or "
                "TEAMCITY_DB_CONTAINER to the TeamCity Docker container name."
            )

        local_archive = temp_dir / actual_name
        source = f"{self.container}:{self.container_backup_dir}/{actual_name}"
        result = subprocess.run(
            ["docker", "cp", source, str(local_archive)],
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Could not copy TeamCity database backup from {source}: "
                f"{result.stderr.strip()}"
            )
        return local_archive

    def _wait_until_idle(self) -> None:
        deadline = time.monotonic() + self.backup_timeout
        while time.monotonic() < deadline:
            response = requests.get(
                f"{self.server_url}/app/rest/server/backup",
                headers=self._backup_headers(csrf=False),
                timeout=self.timeout,
            )
            response.raise_for_status()
            if response.text.strip().lower() == "idle":
                return
            time.sleep(0.5)
        raise TimeoutError(
            f"TeamCity database backup did not finish in {self.backup_timeout} seconds"
        )

    @staticmethod
    def _backup_headers(csrf: bool) -> dict[str, str]:
        headers = RequestSpecs.admin_auth_spec(csrf=csrf)
        headers["Accept"] = "text/plain"
        headers.pop("Content-Type", None)
        return headers

    def _remove_server_backup(self, file_name: str) -> None:
        if self.backup_dir:
            archive = self.backup_dir / file_name
            if archive.exists():
                archive.unlink()
                return
        if not self.container:
            return
        subprocess.run(
            [
                "docker",
                "exec",
                self.container,
                "rm",
                "-f",
                f"{self.container_backup_dir}/{file_name}",
            ],
            capture_output=True,
            check=False,
            text=True,
        )


class PostgreSQLSnapshot(DatabaseSnapshot):
    def __init__(self, connection: psycopg.Connection[DatabaseRow]):
        self.connection = connection

    def fetch_one(self, table: str, where: Mapping[str, Any]) -> DatabaseRow | None:
        rows = self._select(table, where, limit=1)
        return rows[0] if rows else None

    def fetch_all(
        self, table: str, where: Mapping[str, Any] | None = None
    ) -> list[DatabaseRow]:
        return self._select(table, where or {})

    def _select(
        self, table: str, where: Mapping[str, Any], limit: int | None = None
    ) -> list[DatabaseRow]:
        _validate_identifier(table)
        columns = list(where)
        for column in columns:
            _validate_identifier(column)

        query = f"SELECT * FROM {table}"
        params: list[Any] = []
        if columns:
            query += " WHERE " + " AND ".join(f"{column} = %s" for column in columns)
            params.extend(
                int(where[column]) if isinstance(where[column], bool) else where[column]
                for column in columns
            )
        if limit is not None:
            query += f" LIMIT {limit}"

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return [
                {str(key).upper(): value for key, value in row.items()}
                for row in cursor.fetchall()
            ]


class PostgreSQLDatabaseClient(DatabaseClient):
    def __init__(self, dsn: str):
        self.dsn = dsn

    @contextmanager
    def snapshot(self) -> Iterator[DatabaseSnapshot]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            yield PostgreSQLSnapshot(connection)


def create_database_client() -> DatabaseClient:
    adapter = str(Config.get("TEAMCITY_DB_ADAPTER", "auto")).lower()
    dsn = str(Config.get("TEAMCITY_DB_DSN", "")).strip()
    if adapter == "postgresql" or (adapter == "auto" and dsn):
        if not dsn:
            raise ValueError(
                "TEAMCITY_DB_DSN is required for TEAMCITY_DB_ADAPTER=postgresql"
            )
        return PostgreSQLDatabaseClient(dsn)
    if adapter in {"auto", "backup"}:
        return TeamCityBackupDatabaseClient()
    raise ValueError(
        f"Unsupported TEAMCITY_DB_ADAPTER={adapter!r}. Use auto, backup or postgresql."
    )


def _configured_backup_dir() -> Path | None:
    configured = str(Config.get("TEAMCITY_DB_BACKUP_DIR", "")).strip()
    if configured:
        return Path(configured).expanduser().resolve()

    local_dir = (
        Path(__file__).parents[4] / "teamcity-local" / "teamcity-data" / "backup"
    )
    return local_dir if local_dir.is_dir() else None


def _validate_identifier(value: str) -> None:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe database identifier: {value!r}")


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
