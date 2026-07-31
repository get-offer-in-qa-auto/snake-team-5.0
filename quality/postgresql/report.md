# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-25T00:00:00+00:00 — 2026-07-31T13:14:01+00:00).

Published runs: **3** · fully passed: **2** · final test results: **231** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.57% | >= 98.00% | OK | average pass rate = (100.00 + 100.00 + 98.70) / 3 = 99.57% |
| Average Fail Rate | 0.43% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 1.30) / 3 = 0.43% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00) / 3 = 0.00% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 231 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00) / 3 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00) / 3 = 0.00% |
| Test Stability | 66.67% | >= 95.00% | Failed | stability = 2 / 3 = 66.67% |
| Average UI Test Duration | 9.41s | <= 12.00s | OK | average UI test duration = (8.45 + 8.46 + 11.33) / 3 = 9.41s |
| Average API Test Duration | 1.14s | <= 1.50s | OK | average API test duration = (1.07 + 0.94 + 1.41) / 3 = 1.14s |
| Total UI Test Time | 254.20s | <= 300.00s | OK | total UI test time = (228.17 + 228.38 + 306.04) / 3 = 254.20s |
| Average API Test Run Duration | 57.01s | <= 75.00s | OK | average API run duration = (53.62 + 46.97 + 70.46) / 3 = 57.01s |
| Average Pipeline Duration | 389.67s | <= 360.00s | Failed | average pipeline duration = (452.00 + 420.00 + 297.00) / 3 = 389.67s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-31 12:52](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631704406) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.45s | 1.07s | 228.17s | 53.62s | 452.00s |
| [2026-07-31 12:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631712572) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.46s | 0.94s | 228.38s | 46.97s | 420.00s |
| [2026-07-31 13:13](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633108937) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.33s | 1.41s | 306.04s | 70.46s | 297.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.27s | <= 11.00s | 17.50s | 88.39s | <= 100.00s | OK |
| Firefox | 96.30% | 1 | 0.00% | 9.80s | <= 13.00s | 16.40s | 98.91s | <= 115.00s | Failed |
| WebKit | 100.00% | 0 | 0.00% | 9.18s | <= 14.00s | 17.43s | 103.53s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 13:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 33.06s | <= 12.00s | Failed |
| 2026-07-31 13:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 24.94s | <= 12.00s | Failed |
| 2026-07-31 13:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 23.24s | <= 12.00s | Failed |
| 2026-07-31 13:13 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 17.96s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 13:13 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.62s | <= 1.50s | Failed |
| 2026-07-31 12:52 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 13.49s | <= 1.50s | Failed |
| 2026-07-31 12:59 | tests.api.build_execution.test_build_runtime_parameters#test_build_run_with_runtime_parameter | 12.62s | <= 1.50s | Failed |
| 2026-07-31 12:52 | tests.api.build_execution.test_manual_build_run#test_successful_build_run | 12.60s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **14**
- Published Allure reports used in test metrics: **3**
- Workflow runs without a published report: **11**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
