from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = (
    Path(__file__).parents[3] / ".github" / "scripts" / "update_coverage_pages.py"
)


def load_update_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("update_coverage_pages", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_copy_coverage_report_requires_standard_reports(tmp_path: Path) -> None:
    update_coverage_pages = load_update_module()
    source = tmp_path / "source"
    source.mkdir()

    try:
        update_coverage_pages.copy_coverage_report(source, tmp_path / "destination")
    except FileNotFoundError as error:
        assert "coverage.json" in str(error)
        assert "coverage.xml" in str(error)
        assert "index.html" in str(error)
    else:
        raise AssertionError("incomplete coverage artifact must be rejected")


def test_main_publishes_report_and_metadata(tmp_path: Path, monkeypatch) -> None:
    update_coverage_pages = load_update_module()
    source = tmp_path / "source"
    (source / "html").mkdir(parents=True)
    (source / "coverage.json").write_text("{}", encoding="utf-8")
    (source / "coverage.xml").write_text("<coverage/>", encoding="utf-8")
    (source / "html" / "index.html").write_text("coverage", encoding="utf-8")
    site = tmp_path / "site"
    site.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        [
            "update_coverage_pages.py",
            "--site-dir",
            str(site),
            "--coverage-dir",
            str(source),
            "--report-id",
            "100-attempt-2",
            "--workflow",
            "TeamCity Regression",
            "--event",
            "pull_request",
            "--branch",
            "feature/coverage",
            "--sha",
            "abc123",
            "--run-url",
            "https://github.test/actions/runs/100",
        ],
    )

    update_coverage_pages.main()

    destination = site / "coverage" / "100-attempt-2"
    metadata = json.loads((destination / "metadata.json").read_text(encoding="utf-8"))
    assert (destination / "html" / "index.html").is_file()
    assert metadata["report_id"] == "100-attempt-2"
    assert metadata["source"] == "src/main/api"
