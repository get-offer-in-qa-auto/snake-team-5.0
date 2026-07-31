# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-25T00:00:00+00:00 — 2026-07-31T12:52:59+00:00).

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
| Average UI Test Duration | 8.45s | <= 12.00s | OK | average UI test duration = (8.45) / 1 = 8.45s |
| Average API Test Duration | 1.07s | <= 1.50s | OK | average API test duration = (1.07) / 1 = 1.07s |
| Total UI Test Time | 228.17s | <= 300.00s | OK | total UI test time = (228.17) / 1 = 228.17s |
| Average API Test Run Duration | 53.62s | <= 75.00s | OK | average API run duration = (53.62) / 1 = 53.62s |
| Average Pipeline Duration | 452.00s | <= 360.00s | Failed | average pipeline duration = (452.00) / 1 = 452.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-31 12:52](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631704406) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.45s | 1.07s | 228.17s | 53.62s | 452.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 8.86s | <= 11.00s | 16.13s | 79.73s | <= 100.00s | OK |
| Firefox | 100.00% | 0 | 0.00% | 9.04s | <= 13.00s | 15.68s | 81.39s | <= 115.00s | OK |
| WebKit | 100.00% | 0 | 0.00% | 7.45s | <= 14.00s | 12.85s | 67.05s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 12:52 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 16.31s | <= 12.00s | Failed |
| 2026-07-31 12:52 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 16.28s | <= 12.00s | Failed |
| 2026-07-31 12:52 | tests.ui.auth.test_login#test_admin_can_login | 15.85s | <= 12.00s | Failed |
| 2026-07-31 12:52 | tests.ui.identity_access.test_user_creation#test_admin_can_create_user | 14.78s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 12:52 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 13.49s | <= 1.50s | Failed |
| 2026-07-31 12:52 | tests.api.build_execution.test_manual_build_run#test_successful_build_run | 12.60s | <= 1.50s | Failed |
| 2026-07-31 12:52 | tests.api.build_execution.test_build_runtime_parameters#test_build_run_with_runtime_parameter | 11.67s | <= 1.50s | Failed |
| 2026-07-31 12:52 | tests.api.build_execution.test_manual_build_run#test_failed_build_run | 11.44s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **10**
- Published Allure reports used in test metrics: **1**
- Workflow runs without a published report: **9**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
