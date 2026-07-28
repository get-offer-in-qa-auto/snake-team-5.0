from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = (
    Path(__file__).parents[3] / ".github" / "scripts" / "update_allure_pages.py"
)


def load_update_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("update_allure_pages", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_indexes_link_to_quality_dashboard_when_it_exists(tmp_path: Path) -> None:
    update_allure_pages = load_update_module()
    (tmp_path / "quality").mkdir()
    (tmp_path / "quality" / "index.html").write_text("dashboard", encoding="utf-8")

    update_allure_pages.write_indexes(tmp_path, [])

    root_index = (tmp_path / "index.html").read_text(encoding="utf-8")
    reports_index = (tmp_path / "reports" / "index.html").read_text(encoding="utf-8")
    suite_index = (tmp_path / "reports" / "regression" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'href="quality/"' in root_index
    assert 'href="../quality/"' in reports_index
    assert 'href="../../quality/"' in suite_index


def test_indexes_omit_quality_link_before_dashboard_exists(tmp_path: Path) -> None:
    update_allure_pages = load_update_module()

    update_allure_pages.write_indexes(tmp_path, [])

    root_index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Open rolling QA metrics" not in root_index
