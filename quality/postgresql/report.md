# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-16T00:00:00+00:00 — 2026-09-22T08:40:42+00:00).

Published runs: **7** · fully passed: **2** · final test results: **539** · flaky results: **4**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.89% | >= 98.00% | OK | average pass rate = (98.70 + 100.00 + 98.70 + 98.70 + 100.00 + 98.70 + 97.40) / 7 = 98.89% |
| Average Fail Rate | 1.11% | <= 2.00% | OK | average fail rate = (1.30 + 0.00 + 1.30 + 1.30 + 0.00 + 1.30 + 2.60) / 7 = 1.11% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.74% | <= 2.00% | OK | flaky rate = 4 / 539 = 0.74% |
| Average UI Flaky Rate | 2.12% | <= 2.00% | Failed | average UI flaky rate = (3.70 + 0.00 + 3.70 + 0.00 + 0.00 + 3.70 + 3.70) / 7 = 2.12% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 28.57% | >= 95.00% | Failed | stability = 2 / 7 = 28.57% |
| Average UI Test Duration | 9.79s | <= 12.00s | OK | average UI test duration = (7.74 + 10.71 + 10.58 + 9.14 + 10.95 + 8.99 + 10.41) / 7 = 9.79s |
| Average API Test Duration | 1.39s | <= 1.50s | OK | average API test duration = (1.39 + 1.41 + 1.43 + 1.36 + 1.41 + 1.42 + 1.30) / 7 = 1.39s |
| Total UI Test Time | 264.25s | <= 300.00s | OK | total UI test time = (209.07 + 289.07 + 285.67 + 246.65 + 295.55 + 242.79 + 280.96) / 7 = 264.25s |
| Average API Test Run Duration | 69.35s | <= 75.00s | OK | average API run duration = (69.45 + 70.32 + 71.29 + 68.04 + 70.55 + 70.92 + 64.92) / 7 = 69.35s |
| Average Pipeline Duration | 275.71s | <= 360.00s | OK | average pipeline duration = (267.00 + 257.00 + 321.00 + 281.00 + 267.00 + 278.00 + 259.00) / 7 = 275.71s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-16 07:23](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35067764436) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 7.74s | 1.39s | 209.07s | 69.45s | 267.00s |
| [2026-09-17 07:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35193434398) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.71s | 1.41s | 289.07s | 70.32s | 257.00s |
| [2026-09-18 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35317840566) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.58s | 1.43s | 285.67s | 71.29s | 321.00s |
| [2026-09-19 07:09](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35428293841) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.14s | 1.36s | 246.65s | 68.04s | 281.00s |
| [2026-09-20 07:34](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35496984029) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.95s | 1.41s | 295.55s | 70.55s | 267.00s |
| [2026-09-21 07:45](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35574038759) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 8.99s | 1.42s | 242.79s | 70.92s | 278.00s |
| [2026-09-22 07:27](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35699227389) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.41s | 1.30s | 280.96s | 64.92s | 259.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 96.83% | 2 | 0.00% | 8.68s | <= 11.00s | 24.35s | 90.00s | <= 100.00s | Failed |
| Firefox | 93.65% | 4 | 6.35% | 10.12s | <= 13.00s | 23.74s | 106.68s | <= 115.00s | Failed |
| WebKit | 100.00% | 0 | 0.00% | 10.57s | <= 14.00s | 26.81s | 104.22s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-18 07:12 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.08s | <= 12.00s | Failed |
| 2026-09-20 07:34 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.98s | <= 12.00s | Failed |
| 2026-09-21 07:45 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.44s | <= 12.00s | Failed |
| 2026-09-22 07:27 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 26.89s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-16 07:23 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.81s | <= 1.50s | Failed |
| 2026-09-18 07:12 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.78s | <= 1.50s | Failed |
| 2026-09-17 07:18 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.29s | <= 1.50s | Failed |
| 2026-09-21 07:45 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.06s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
