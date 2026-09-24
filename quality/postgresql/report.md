# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-18T00:00:00+00:00 — 2026-09-24T07:22:55+00:00).

Published runs: **7** · fully passed: **2** · final test results: **539** · flaky results: **4**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.89% | >= 98.00% | OK | average pass rate = (98.70 + 98.70 + 100.00 + 98.70 + 97.40 + 98.70 + 100.00) / 7 = 98.89% |
| Average Fail Rate | 1.11% | <= 2.00% | OK | average fail rate = (1.30 + 1.30 + 0.00 + 1.30 + 2.60 + 1.30 + 0.00) / 7 = 1.11% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.74% | <= 2.00% | OK | flaky rate = 4 / 539 = 0.74% |
| Average UI Flaky Rate | 2.12% | <= 2.00% | Failed | average UI flaky rate = (3.70 + 0.00 + 0.00 + 3.70 + 3.70 + 3.70 + 0.00) / 7 = 2.12% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 28.57% | >= 95.00% | Failed | stability = 2 / 7 = 28.57% |
| Average UI Test Duration | 10.22s | <= 12.00s | OK | average UI test duration = (10.58 + 9.14 + 10.95 + 8.99 + 10.41 + 11.04 + 10.42) / 7 = 10.22s |
| Average API Test Duration | 1.39s | <= 1.50s | OK | average API test duration = (1.43 + 1.36 + 1.41 + 1.42 + 1.30 + 1.42 + 1.40) / 7 = 1.39s |
| Total UI Test Time | 275.86s | <= 300.00s | OK | total UI test time = (285.67 + 246.65 + 295.55 + 242.79 + 280.96 + 298.04 + 281.38) / 7 = 275.86s |
| Average API Test Run Duration | 69.48s | <= 75.00s | OK | average API run duration = (71.29 + 68.04 + 70.55 + 70.92 + 64.92 + 70.88 + 69.78) / 7 = 69.48s |
| Average Pipeline Duration | 323.86s | <= 360.00s | OK | average pipeline duration = (321.00 + 281.00 + 267.00 + 278.00 + 259.00 + 534.00 + 327.00) / 7 = 323.86s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-18 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35317840566) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.58s | 1.43s | 285.67s | 71.29s | 321.00s |
| [2026-09-19 07:09](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35428293841) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.14s | 1.36s | 246.65s | 68.04s | 281.00s |
| [2026-09-20 07:34](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35496984029) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.95s | 1.41s | 295.55s | 70.55s | 267.00s |
| [2026-09-21 07:45](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35574038759) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 8.99s | 1.42s | 242.79s | 70.92s | 278.00s |
| [2026-09-22 07:27](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35699227389) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.41s | 1.30s | 280.96s | 64.92s | 259.00s |
| [2026-09-23 07:34](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35831506203) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 11.04s | 1.42s | 298.04s | 70.88s | 534.00s |
| [2026-09-24 07:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35968652436) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.42s | 1.40s | 281.38s | 69.78s | 327.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 96.83% | 2 | 0.00% | 8.96s | <= 11.00s | 24.69s | 91.59s | <= 100.00s | Failed |
| Firefox | 93.65% | 4 | 6.35% | 10.49s | <= 13.00s | 24.31s | 103.32s | <= 115.00s | Failed |
| WebKit | 100.00% | 0 | 0.00% | 11.20s | <= 14.00s | 29.31s | 104.97s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-23 07:34 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.33s | <= 12.00s | Failed |
| 2026-09-18 07:12 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.08s | <= 12.00s | Failed |
| 2026-09-20 07:34 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.98s | <= 12.00s | Failed |
| 2026-09-21 07:45 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.44s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-23 07:34 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.91s | <= 1.50s | Failed |
| 2026-09-18 07:12 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.78s | <= 1.50s | Failed |
| 2026-09-21 07:45 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.06s | <= 1.50s | Failed |
| 2026-09-19 07:09 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.36s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
