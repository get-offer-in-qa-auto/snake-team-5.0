# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-09T00:00:00+00:00 — 2026-08-15T02:57:48+00:00).

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
| Average UI Test Duration | 10.43s | <= 12.00s | OK | average UI test duration = (10.43) / 1 = 10.43s |
| Average API Test Duration | 1.40s | <= 1.50s | OK | average API test duration = (1.40) / 1 = 1.40s |
| Total UI Test Time | 281.71s | <= 300.00s | OK | total UI test time = (281.71) / 1 = 281.71s |
| Average API Test Run Duration | 69.95s | <= 75.00s | OK | average API run duration = (69.95) / 1 = 69.95s |
| Average Pipeline Duration | 298.00s | <= 360.00s | OK | average pipeline duration = (298.00) / 1 = 298.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-12 12:33](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31596474598) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.43s | 1.40s | 281.71s | 69.95s | 298.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.54s | <= 11.00s | 19.18s | 85.87s | <= 100.00s | OK |
| Firefox | 100.00% | 0 | 0.00% | 10.63s | <= 13.00s | 20.06s | 95.69s | <= 115.00s | OK |
| WebKit | 100.00% | 0 | 0.00% | 11.13s | <= 14.00s | 21.57s | 100.16s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-12 12:33 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 25.36s | <= 12.00s | Failed |
| 2026-08-12 12:33 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 24.07s | <= 12.00s | Failed |
| 2026-08-12 12:33 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 23.91s | <= 12.00s | Failed |
| 2026-08-12 12:33 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 15.88s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-12 12:33 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 21.65s | <= 1.50s | Failed |
| 2026-08-12 12:33 | tests.api.build_execution.test_build_runtime_parameters#test_build_run_with_runtime_parameter | 12.31s | <= 1.50s | Failed |
| 2026-08-12 12:33 | tests.api.build_execution.test_manual_build_run#test_successful_build_run | 12.27s | <= 1.50s | Failed |
| 2026-08-12 12:33 | tests.api.build_execution.test_manual_build_run#test_failed_build_run | 11.21s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **1**
- Published Allure reports used in test metrics: **1**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
