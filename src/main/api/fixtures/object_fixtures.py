import logging
from typing import Any

import allure
import pytest

from src.main.api.fixtures.created_objects_registry import CreatedObjectsRegistry
from src.main.api.utils.cleanup_helper import CleanupFailure, cleanup_objects


def _resolve_source(request: pytest.FixtureRequest, source: str) -> Any:
    parts = [part for part in source.split(".") if part]
    if not parts:
        raise ValueError("Cleanup source cannot be empty")

    root = parts[0]
    callspec = getattr(request.node, "callspec", None)
    if callspec is not None and root in getattr(callspec, "params", {}):
        value = callspec.params[root]
    else:
        value = request.getfixturevalue(root)

    for attribute in parts[1:]:
        value = getattr(value, attribute)
    return value


@pytest.fixture
def created_objects(request: pytest.FixtureRequest):
    objects = CreatedObjectsRegistry()
    yield objects

    failures = cleanup_objects(objects)
    if not failures:
        return

    details = _format_cleanup_failures(failures)
    request.node.add_report_section("teardown", "cleanup failures", details)
    allure.attach(details, "Cleanup failures", allure.attachment_type.TEXT)

    call_report = getattr(request.node, "rep_call", None)
    if call_report is not None and call_report.failed:
        logging.error(
            "Cleanup failed after an already failed test; preserving the original "
            "test failure.\n%s",
            details,
        )
        return

    pytest.fail(f"Test data cleanup failed:\n{details}", pytrace=False)


@pytest.fixture(autouse=True)
def entity_will_be_created(request: pytest.FixtureRequest):
    """Register UI-created entities before the browser performs the action."""
    mark = request.node.get_closest_marker("entity_will_be_created")
    if mark is None:
        yield
        return

    sources = list(mark.args)
    source = mark.kwargs.get("source")
    if source is not None:
        sources.append(source)
    if not sources:
        raise ValueError("entity_will_be_created requires a fixture source")

    created_objects = request.getfixturevalue("created_objects")
    for item in sources:
        entity = _resolve_source(request, item) if isinstance(item, str) else item
        created_objects.append(entity)

    yield


def _format_cleanup_failures(failures: list[CleanupFailure]) -> str:
    return "\n\n".join(
        f"{failure.object_type} {failure.object_id}: {failure.error}\n"
        f"{failure.traceback}"
        for failure in failures
    )
