# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-05T00:00:00+00:00 — 2026-09-11T07:08:56+00:00).

Published runs: **7** · fully passed: **1** · final test results: **539** · flaky results: **4**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 97.96% | >= 98.00% | Failed | average pass rate = (97.40 + 100.00 + 96.10 + 98.70 + 97.40 + 97.40 + 98.70) / 7 = 97.96% |
| Average Fail Rate | 2.04% | <= 2.00% | Failed | average fail rate = (2.60 + 0.00 + 3.90 + 1.30 + 2.60 + 2.60 + 1.30) / 7 = 2.04% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.74% | <= 2.00% | OK | flaky rate = 4 / 539 = 0.74% |
| Average UI Flaky Rate | 2.12% | <= 2.00% | Failed | average UI flaky rate = (7.41 + 0.00 + 0.00 + 0.00 + 0.00 + 7.41 + 0.00) / 7 = 2.12% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 14.29% | >= 95.00% | Failed | stability = 1 / 7 = 14.29% |
| Average UI Test Duration | 9.83s | <= 12.00s | OK | average UI test duration = (8.17 + 9.50 + 10.56 + 9.27 + 9.23 + 10.65 + 11.44) / 7 = 9.83s |
| Average API Test Duration | 1.37s | <= 1.50s | OK | average API test duration = (1.37 + 1.42 + 1.07 + 1.49 + 1.38 + 1.44 + 1.40) / 7 = 1.37s |
| Total UI Test Time | 265.42s | <= 300.00s | OK | total UI test time = (220.50 + 256.48 + 285.05 + 250.21 + 249.18 + 287.67 + 308.86) / 7 = 265.42s |
| Average API Test Run Duration | 68.45s | <= 75.00s | OK | average API run duration = (68.63 + 71.09 + 53.71 + 74.52 + 69.02 + 72.21 + 70.00) / 7 = 68.45s |
| Average Pipeline Duration | 303.14s | <= 360.00s | OK | average pipeline duration = (302.00 + 306.00 + 305.00 + 277.00 + 317.00 + 311.00 + 304.00) / 7 = 303.14s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-05 06:48](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33950562289) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 8.17s | 1.37s | 220.50s | 68.63s | 302.00s |
| [2026-09-06 06:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34017664766) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.50s | 1.42s | 256.48s | 71.09s | 306.00s |
| [2026-09-07 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34093516528) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.56s | 1.07s | 285.05s | 53.71s | 305.00s |
| [2026-09-08 07:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34196968762) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.27s | 1.49s | 250.21s | 74.52s | 277.00s |
| [2026-09-09 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34322183656) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.23s | 1.38s | 249.18s | 69.02s | 317.00s |
| [2026-09-10 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34448004113) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.65s | 1.44s | 287.67s | 72.21s | 311.00s |
| [2026-09-11 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34572510288) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.44s | 1.40s | 308.86s | 70.00s | 304.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 96.83% | 2 | 0.00% | 8.49s | <= 11.00s | 21.55s | 90.22s | <= 100.00s | Failed |
| Firefox | 95.24% | 3 | 3.17% | 10.03s | <= 13.00s | 25.13s | 105.77s | <= 115.00s | Failed |
| WebKit | 95.24% | 3 | 3.17% | 10.96s | <= 14.00s | 29.19s | 120.90s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-07 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.82s | <= 12.00s | Failed |
| 2026-09-11 07:08 | tests.ui.projects.test_project_creation#test_admin_can_create_project | 31.37s | <= 12.00s | Failed |
| 2026-09-10 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.57s | <= 12.00s | Failed |
| 2026-09-06 06:59 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.19s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-06 06:59 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.58s | <= 1.50s | Failed |
| 2026-09-11 07:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.27s | <= 1.50s | Failed |
| 2026-09-10 07:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.47s | <= 1.50s | Failed |
| 2026-09-08 07:02 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 27.93s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
