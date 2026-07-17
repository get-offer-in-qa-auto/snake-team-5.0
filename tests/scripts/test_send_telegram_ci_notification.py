import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "scripts"
    / "send_telegram_ci_notification.py"
)
SPEC = importlib.util.spec_from_file_location(
    "send_telegram_ci_notification", SCRIPT_PATH
)
assert SPEC is not None
assert SPEC.loader is not None
telegram_notification = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = telegram_notification
SPEC.loader.exec_module(telegram_notification)


@pytest.mark.regression
def test_build_message_uses_readable_telegram_sections():
    run = telegram_notification.WorkflowRun(
        run_id="29567942357",
        run_attempt="1",
        name="TeamCity Regression",
        status="success",
        branch="feature/<build-run>",
        event_name="pull_request",
        short_sha="7675d6e72269",
        url="https://github.com/example/repo/actions/runs/29567942357",
        jobs_url="",
        artifacts_url="",
        repository="example/repo",
        pr_number="41",
        pr_url="https://github.com/example/repo/pull/41",
    )
    jobs = [
        telegram_notification.WorkflowJob(name="Code Quality", status="success"),
        telegram_notification.WorkflowJob(name="TeamCity regression", status="failure"),
    ]
    allure_report = telegram_notification.AllureReport(
        suite="regression",
        url="https://example.github.io/repo/reports/regression/29567942357-attempt-1/",
        history_url="https://example.github.io/repo/reports/regression/",
        summary=telegram_notification.AllureSummary(
            total=10,
            passed=8,
            failed=1,
            broken=1,
            skipped=0,
        ),
    )

    message = telegram_notification.build_message(run, jobs, allure_report)

    assert (
        message
        == """✅ <b>TeamCity Regression</b>
Status: <b>success</b>

<b>Run details</b>
🌿 Branch: <code>feature/&lt;build-run&gt;</code>
⚡ Event: <code>pull_request</code>
🔖 Commit: <code>7675d6e72269</code>
🔀 Pull request: <a href="https://github.com/example/repo/pull/41">PR #41</a>

<b>Jobs</b>
✅ Code Quality — success
❌ TeamCity regression — failure

<b>Allure</b>
🧪 Total: 10
✅ Passed: 8 · ❌ Failed: 1
💥 Broken: 1 · ⏭️ Skipped: 0
📊 <a href="https://example.github.io/repo/reports/regression/29567942357-attempt-1/">Open report</a> · <a href="https://example.github.io/repo/reports/regression/">Report history</a>

🔗 <a href="https://github.com/example/repo/actions/runs/29567942357">Open GitHub Actions run</a>"""
    )


@pytest.mark.regression
def test_build_message_handles_missing_jobs_and_allure():
    run = telegram_notification.WorkflowRun(
        run_id="1",
        run_attempt="1",
        name="TeamCity Regression",
        status="timed_out",
        branch="main",
        event_name="workflow_dispatch",
        short_sha="abc123",
        url="",
        jobs_url="",
        artifacts_url="",
        repository="example/repo",
        pr_number="",
        pr_url="",
    )

    message = telegram_notification.build_message(run, [], None)

    assert "⏱️ <b>TeamCity Regression</b>" in message
    assert "<b>Jobs</b>\n❔ No job data" in message
    assert "<b>Allure</b>" not in message
