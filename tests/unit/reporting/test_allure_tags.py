from collections.abc import Callable

from src.main.reporting.allure import tags as tags_module
from src.main.reporting.allure.tags import AllureTag


def capture_allure_tags(
    monkeypatch,
) -> tuple[list[tuple[str, ...]], Callable[..., object]]:
    captured: list[tuple[str, ...]] = []

    def fake_tag(*values: str):
        captured.append(values)

        def decorate(test):
            return test

        return decorate

    monkeypatch.setattr(tags_module.allure, "tag", fake_tag)
    return captured, lambda: None


def test_api_regression_tags_adds_common_and_smoke_tags(monkeypatch):
    captured, test = capture_allure_tags(monkeypatch)

    decorated = tags_module.api_regression_tags(
        AllureTag.PROJECT,
        smoke=True,
    )(test)

    assert decorated is test
    assert captured == [("api", "smoke", "regression", "project")]


def test_allure_tags_removes_duplicates_preserving_order(monkeypatch):
    captured, test = capture_allure_tags(monkeypatch)

    tags_module.allure_tags(
        AllureTag.PROJECT,
        AllureTag.DATABASE,
        AllureTag.PROJECT,
    )(test)

    assert captured == [("project", "database")]
