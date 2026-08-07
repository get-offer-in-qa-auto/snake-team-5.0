# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-01T00:00:00+00:00 — 2026-08-07T04:32:10+00:00).

Published runs: **1** · fully passed: **1** · final test results: **77** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 100.00% | >= 98.00% | OK | average pass rate = (100.00) / 1 = 100.00% |
| Average Fail Rate | 0.00% | <= 2.00% | OK | average fail rate = (0.00) / 1 = 0.00% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00) / 1 = 0.00% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 77 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00) / 1 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00) / 1 = 0.00% |
| Test Stability | 100.00% | >= 95.00% | OK | stability = 1 / 1 = 100.00% |
| Average UI Test Duration | 10.80s | <= 12.00s | OK | average UI test duration = (10.80) / 1 = 10.80s |
| Average API Test Duration | 1.40s | <= 1.50s | OK | average API test duration = (1.40) / 1 = 1.40s |
| Total UI Test Time | 291.68s | <= 300.00s | OK | total UI test time = (291.68) / 1 = 291.68s |
| Average API Test Run Duration | 70.16s | <= 75.00s | OK | average API run duration = (70.16) / 1 = 70.16s |
| Average Pipeline Duration | 262.00s | <= 360.00s | OK | average pipeline duration = (262.00) / 1 = 262.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-05 10:57](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30999113507) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.80s | 1.40s | 291.68s | 70.16s | 262.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.94s | <= 11.00s | 21.13s | 89.49s | <= 100.00s | OK |
| Firefox | 100.00% | 0 | 0.00% | 10.90s | <= 13.00s | 20.00s | 98.08s | <= 115.00s | OK |
| WebKit | 100.00% | 0 | 0.00% | 11.57s | <= 14.00s | 22.76s | 104.11s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-05 10:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.22s | <= 12.00s | Failed |
| 2026-08-05 10:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 26.83s | <= 12.00s | Failed |
| 2026-08-05 10:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 23.40s | <= 12.00s | Failed |
| 2026-08-05 10:57 | tests.ui.auth.test_login#test_admin_can_login | 14.91s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-05 10:57 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 24.20s | <= 1.50s | Failed |
| 2026-08-05 10:57 | tests.api.build_execution.test_manual_build_run#test_successful_build_run | 12.29s | <= 1.50s | Failed |
| 2026-08-05 10:57 | tests.api.build_execution.test_build_runtime_parameters#test_build_run_with_runtime_parameter | 11.31s | <= 1.50s | Failed |
| 2026-08-05 10:57 | tests.api.build_execution.test_manual_build_run#test_failed_build_run | 11.21s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **1**
- Published Allure reports used in test metrics: **1**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
