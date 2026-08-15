# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-09T00:00:00+00:00 — 2026-08-15T02:57:49+00:00).

Published runs: **7** · fully passed: **4** · final test results: **539** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.26% | >= 98.00% | OK | average pass rate = (100.00 + 97.40 + 100.00 + 100.00 + 98.70 + 98.70 + 100.00) / 7 = 99.26% |
| Average Fail Rate | 0.74% | <= 2.00% | OK | average fail rate = (0.00 + 2.60 + 0.00 + 0.00 + 1.30 + 1.30 + 0.00) / 7 = 0.74% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 539 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 57.14% | >= 95.00% | Failed | stability = 4 / 7 = 57.14% |
| Average UI Test Duration | 10.31s | <= 12.00s | OK | average UI test duration = (10.00 + 10.82 + 8.53 + 11.96 + 9.96 + 9.84 + 11.04) / 7 = 10.31s |
| Average API Test Duration | 1.27s | <= 1.50s | OK | average API test duration = (1.38 + 0.60 + 1.40 + 1.36 + 1.34 + 1.42 + 1.41) / 7 = 1.27s |
| Total UI Test Time | 278.30s | <= 300.00s | OK | total UI test time = (270.02 + 292.16 + 230.26 + 322.90 + 269.06 + 265.76 + 297.96) / 7 = 278.30s |
| Average API Test Run Duration | 63.65s | <= 75.00s | OK | average API run duration = (68.84 + 30.12 + 69.91 + 67.85 + 66.89 + 71.24 + 70.69) / 7 = 63.65s |
| Average Pipeline Duration | 287.43s | <= 360.00s | OK | average pipeline duration = (280.00 + 281.00 + 301.00 + 289.00 + 305.00 + 276.00 + 280.00) / 7 = 287.43s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-09 03:47](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31292965512) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.00s | 1.38s | 270.02s | 68.84s | 280.00s |
| [2026-08-10 04:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31353883386) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.82s | 0.60s | 292.16s | 30.12s | 281.00s |
| [2026-08-11 03:49](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31456259472) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.53s | 1.40s | 230.26s | 69.91s | 301.00s |
| [2026-08-12 04:13](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31562257105) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.96s | 1.36s | 322.90s | 67.85s | 289.00s |
| [2026-08-13 04:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31666249542) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.96s | 1.34s | 269.06s | 66.89s | 305.00s |
| [2026-08-14 04:14](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31768956671) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.84s | 1.42s | 265.76s | 71.24s | 276.00s |
| [2026-08-15 02:57](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31860264737) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.04s | 1.41s | 297.96s | 70.69s | 280.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.21s | <= 11.00s | 22.63s | 93.87s | <= 100.00s | OK |
| Firefox | 100.00% | 0 | 0.00% | 10.77s | <= 13.00s | 25.03s | 105.23s | <= 115.00s | OK |
| WebKit | 96.83% | 2 | 0.00% | 10.94s | <= 14.00s | 27.42s | 113.41s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-12 04:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.66s | <= 12.00s | Failed |
| 2026-08-15 02:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.63s | <= 12.00s | Failed |
| 2026-08-14 04:14 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.36s | <= 12.00s | Failed |
| 2026-08-15 02:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.09s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-15 02:57 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.34s | <= 1.50s | Failed |
| 2026-08-14 04:14 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.14s | <= 1.50s | Failed |
| 2026-08-11 03:49 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 27.51s | <= 1.50s | Failed |
| 2026-08-09 03:47 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 27.38s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
