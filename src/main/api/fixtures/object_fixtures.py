import logging
from typing import Any

import allure
import pytest

from src.main.api.utils.cleanup_helper import CleanupFailure, cleanup_objects


@pytest.fixture
def created_objects(request: pytest.FixtureRequest):
    objects: list[Any] = []
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


def _format_cleanup_failures(failures: list[CleanupFailure]) -> str:
    return "\n\n".join(
        f"{failure.object_type} {failure.object_id}: {failure.error}\n"
        f"{failure.traceback}"
        for failure in failures
    )
