from __future__ import annotations

import re
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from xml.etree import ElementTree

from src.main.api.configs.config import Config

_PATH_COMPONENT = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class BuildStepConfiguration:
    id: str
    name: str
    type: str
    parameters: Mapping[str, str]


class TeamCityConfigurationClient:
    def __init__(self) -> None:
        self.container = str(Config.get("TEAMCITY_CONFIG_CONTAINER", "")).strip()
        self.data_dir = str(
            Config.get("TEAMCITY_CONFIG_DATA_DIR", "/data/teamcity_server/datadir")
        ).rstrip("/")
        if not self.container:
            raise ValueError(
                "TEAMCITY_CONFIG_CONTAINER is required to read TeamCity "
                "configuration persistence."
            )

    def get_build_step(
        self, project_id: str, build_configuration_id: str, step_id: str
    ) -> BuildStepConfiguration | None:
        for component in (project_id, build_configuration_id, step_id):
            _validate_path_component(component)

        root = self._read_build_configuration(project_id, build_configuration_id)
        for runner in root.findall(".//{*}build-runners/{*}runner"):
            if runner.get("id") != step_id:
                continue
            return BuildStepConfiguration(
                id=step_id,
                name=runner.get("name", ""),
                type=runner.get("type", ""),
                parameters={
                    parameter.get("name", ""): parameter.get(
                        "value", parameter.text or ""
                    )
                    for parameter in runner.findall("./{*}parameters/{*}param")
                    if parameter.get("name")
                },
            )
        return None

    def _read_build_configuration(
        self, project_id: str, build_configuration_id: str
    ) -> ElementTree.Element:
        for component in (project_id, build_configuration_id):
            _validate_path_component(component)

        path = (
            f"{self.data_dir}/config/projects/{project_id}/buildTypes/"
            f"{build_configuration_id}.xml"
        )
        result = subprocess.run(
            ["docker", "exec", self.container, "cat", path],
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode != 0:
            raise FileNotFoundError(
                f"TeamCity build configuration XML is unavailable at {path}: "
                f"{result.stderr.strip()}"
            )
        try:
            return ElementTree.fromstring(result.stdout)
        except ElementTree.ParseError as error:
            raise RuntimeError(
                f"TeamCity build configuration XML is malformed at {path}"
            ) from error


def _validate_path_component(value: str) -> None:
    if not _PATH_COMPONENT.fullmatch(value):
        raise ValueError(f"Unsafe TeamCity configuration path component: {value!r}")
