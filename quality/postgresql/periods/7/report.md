# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-14T00:00:00+00:00 — 2026-09-20T08:43:01+00:00).

Published runs: **7** · fully passed: **2** · final test results: **539** · flaky results: **3**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.07% | >= 98.00% | OK | average pass rate = (98.70 + 98.70 + 98.70 + 100.00 + 98.70 + 98.70 + 100.00) / 7 = 99.07% |
| Average Fail Rate | 0.74% | <= 2.00% | OK | average fail rate = (0.00 + 1.30 + 1.30 + 0.00 + 1.30 + 1.30 + 0.00) / 7 = 0.74% |
| Average Broken Rate | 0.19% | <= 1.00% | OK | average broken rate = (1.30 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.19% |
| Flaky Rate | 0.56% | <= 2.00% | OK | flaky rate = 3 / 539 = 0.56% |
| Average UI Flaky Rate | 1.59% | <= 2.00% | OK | average UI flaky rate = (0.00 + 3.70 + 3.70 + 0.00 + 3.70 + 0.00 + 0.00) / 7 = 1.59% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 28.57% | >= 95.00% | Failed | stability = 2 / 7 = 28.57% |
| Average UI Test Duration | 9.89s | <= 12.00s | OK | average UI test duration = (10.59 + 9.56 + 7.74 + 10.71 + 10.58 + 9.14 + 10.95) / 7 = 9.89s |
| Average API Test Duration | 1.42s | <= 1.50s | OK | average API test duration = (1.55 + 1.42 + 1.39 + 1.41 + 1.43 + 1.36 + 1.41) / 7 = 1.42s |
| Total UI Test Time | 267.13s | <= 300.00s | OK | total UI test time = (285.85 + 258.07 + 209.07 + 289.07 + 285.67 + 246.65 + 295.55) / 7 = 267.13s |
| Average API Test Run Duration | 71.17s | <= 75.00s | OK | average API run duration = (77.39 + 71.16 + 69.45 + 70.32 + 71.29 + 68.04 + 70.55) / 7 = 71.17s |
| Average Pipeline Duration | 296.29s | <= 360.00s | OK | average pipeline duration = (298.00 + 383.00 + 267.00 + 257.00 + 321.00 + 281.00 + 267.00) / 7 = 296.29s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-14 07:42](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34818612231) | 77 | 76 / 98.70% | 0 / 0.00% | 1 / 1.30% | 0 / 0.00% | Unstable | 10.59s | 1.55s | 285.85s | 77.39s | 298.00s |
| [2026-09-15 07:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34940697002) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.56s | 1.42s | 258.07s | 71.16s | 383.00s |
| [2026-09-16 07:23](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35067764436) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 7.74s | 1.39s | 209.07s | 69.45s | 267.00s |
| [2026-09-17 07:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35193434398) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.71s | 1.41s | 289.07s | 70.32s | 257.00s |
| [2026-09-18 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35317840566) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.58s | 1.43s | 285.67s | 71.29s | 321.00s |
| [2026-09-19 07:09](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35428293841) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.14s | 1.36s | 246.65s | 68.04s | 281.00s |
| [2026-09-20 07:34](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35496984029) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.95s | 1.41s | 295.55s | 70.55s | 267.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 98.41% | 1 | 0.00% | 8.96s | <= 11.00s | 24.38s | 93.90s | <= 100.00s | OK |
| Firefox | 95.24% | 3 | 4.76% | 10.24s | <= 13.00s | 23.28s | 106.68s | <= 115.00s | Failed |
| WebKit | 98.41% | 1 | 0.00% | 10.47s | <= 14.00s | 27.21s | 103.49s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-14 07:42 | tests.ui.identity_access.test_user_creation#test_admin_can_create_user | 42.13s | <= 12.00s | Failed |
| 2026-09-18 07:12 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.08s | <= 12.00s | Failed |
| 2026-09-20 07:34 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.98s | <= 12.00s | Failed |
| 2026-09-15 07:22 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.34s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-16 07:23 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.81s | <= 1.50s | Failed |
| 2026-09-14 07:42 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.45s | <= 1.50s | Failed |
| 2026-09-18 07:12 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.78s | <= 1.50s | Failed |
| 2026-09-17 07:18 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.29s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
