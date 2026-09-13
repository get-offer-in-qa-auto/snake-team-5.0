# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-07T00:00:00+00:00 — 2026-09-13T08:26:13+00:00).

Published runs: **7** · fully passed: **0** · final test results: **539** · flaky results: **6**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 97.59% | >= 98.00% | Failed | average pass rate = (96.10 + 98.70 + 97.40 + 97.40 + 98.70 + 97.40 + 97.40) / 7 = 97.59% |
| Average Fail Rate | 2.41% | <= 2.00% | Failed | average fail rate = (3.90 + 1.30 + 2.60 + 2.60 + 1.30 + 2.60 + 2.60) / 7 = 2.41% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 1.11% | <= 2.00% | OK | flaky rate = 6 / 539 = 1.11% |
| Average UI Flaky Rate | 3.17% | <= 2.00% | Failed | average UI flaky rate = (0.00 + 0.00 + 0.00 + 7.41 + 0.00 + 7.41 + 7.41) / 7 = 3.17% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 0.00% | >= 95.00% | Failed | stability = 0 / 7 = 0.00% |
| Average UI Test Duration | 9.58s | <= 12.00s | OK | average UI test duration = (10.56 + 9.27 + 9.23 + 10.65 + 11.44 + 6.37 + 9.57) / 7 = 9.58s |
| Average API Test Duration | 1.39s | <= 1.50s | OK | average API test duration = (1.07 + 1.49 + 1.38 + 1.44 + 1.40 + 1.49 + 1.42) / 7 = 1.39s |
| Total UI Test Time | 258.76s | <= 300.00s | OK | total UI test time = (285.05 + 250.21 + 249.18 + 287.67 + 308.86 + 172.02 + 258.36) / 7 = 258.76s |
| Average API Test Run Duration | 69.31s | <= 75.00s | OK | average API run duration = (53.71 + 74.52 + 69.02 + 72.21 + 70.00 + 74.59 + 71.13) / 7 = 69.31s |
| Average Pipeline Duration | 298.29s | <= 360.00s | OK | average pipeline duration = (305.00 + 277.00 + 317.00 + 311.00 + 304.00 + 277.00 + 297.00) / 7 = 298.29s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-07 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34093516528) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.56s | 1.07s | 285.05s | 53.71s | 305.00s |
| [2026-09-08 07:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34196968762) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.27s | 1.49s | 250.21s | 74.52s | 277.00s |
| [2026-09-09 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34322183656) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.23s | 1.38s | 249.18s | 69.02s | 317.00s |
| [2026-09-10 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34448004113) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.65s | 1.44s | 287.67s | 72.21s | 311.00s |
| [2026-09-11 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34572510288) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.44s | 1.40s | 308.86s | 70.00s | 304.00s |
| [2026-09-12 07:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34679340989) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 6.37s | 1.49s | 172.02s | 74.59s | 277.00s |
| [2026-09-13 07:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34744643454) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 9.57s | 1.42s | 258.36s | 71.13s | 297.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 93.65% | 4 | 3.17% | 8.26s | <= 11.00s | 20.55s | 90.55s | <= 100.00s | Failed |
| Firefox | 93.65% | 4 | 4.76% | 9.94s | <= 13.00s | 25.13s | 105.77s | <= 115.00s | Failed |
| WebKit | 96.83% | 2 | 1.59% | 10.55s | <= 14.00s | 28.93s | 120.90s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-07 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.82s | <= 12.00s | Failed |
| 2026-09-11 07:08 | tests.ui.projects.test_project_creation#test_admin_can_create_project | 31.37s | <= 12.00s | Failed |
| 2026-09-10 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.57s | <= 12.00s | Failed |
| 2026-09-11 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.19s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-12 07:00 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.68s | <= 1.50s | Failed |
| 2026-09-13 07:18 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.37s | <= 1.50s | Failed |
| 2026-09-11 07:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.27s | <= 1.50s | Failed |
| 2026-09-10 07:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.47s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
