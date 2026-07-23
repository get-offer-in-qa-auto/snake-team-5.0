from __future__ import annotations

import subprocess
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg
import requests
from filelock import FileLock
from psycopg.rows import dict_row

from src.main.api.configs.config import Config
from src.main.api.database.executor import (
    DBExecutor,
    PostgreSQLExecutor,
    TeamCityBackupExecutor,
)
from src.main.api.specs.request_specs import RequestSpecs


class DatabaseClient(ABC):
    @abstractmethod
    @contextmanager
    def snapshot(self) -> Iterator[DBExecutor]: ...


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
    def snapshot(self) -> Iterator[DBExecutor]:
        with self.lock.acquire(timeout=self.backup_timeout):
            with TemporaryDirectory(prefix="teamcity-db-") as temp_dir:
                archive_path = self._create_backup(Path(temp_dir))
                try:
                    yield TeamCityBackupExecutor(archive_path)
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


class PostgreSQLDatabaseClient(DatabaseClient):
    def __init__(self, dsn: str):
        self.dsn = dsn

    @contextmanager
    def snapshot(self) -> Iterator[DBExecutor]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            yield PostgreSQLExecutor(connection)


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
