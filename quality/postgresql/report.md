# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-24T00:00:00+00:00 — 2026-08-30T08:02:53+00:00).

Published runs: **7** · fully passed: **3** · final test results: **539** · flaky results: **3**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.33% | >= 98.00% | OK | average pass rate = (97.40 + 100.00 + 96.10 + 100.00 + 98.70 + 96.10 + 100.00) / 7 = 98.33% |
| Average Fail Rate | 1.67% | <= 2.00% | OK | average fail rate = (2.60 + 0.00 + 3.90 + 0.00 + 1.30 + 3.90 + 0.00) / 7 = 1.67% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.56% | <= 2.00% | OK | flaky rate = 3 / 539 = 0.56% |
| Average UI Flaky Rate | 1.59% | <= 2.00% | OK | average UI flaky rate = (7.41 + 0.00 + 0.00 + 0.00 + 0.00 + 3.70 + 0.00) / 7 = 1.59% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 42.86% | >= 95.00% | Failed | stability = 3 / 7 = 42.86% |
| Average UI Test Duration | 10.20s | <= 12.00s | OK | average UI test duration = (10.25 + 10.40 + 11.39 + 9.55 + 10.18 + 9.95 + 9.65) / 7 = 10.20s |
| Average API Test Duration | 1.37s | <= 1.50s | OK | average API test duration = (1.44 + 1.38 + 1.16 + 1.41 + 1.41 + 1.36 + 1.41) / 7 = 1.37s |
| Total UI Test Time | 275.27s | <= 300.00s | OK | total UI test time = (276.77 + 280.76 + 307.44 + 257.78 + 274.93 + 268.70 + 260.48) / 7 = 275.27s |
| Average API Test Run Duration | 68.36s | <= 75.00s | OK | average API run duration = (71.93 + 69.17 + 58.05 + 70.49 + 70.42 + 68.11 + 70.34) / 7 = 68.36s |
| Average Pipeline Duration | 292.71s | <= 360.00s | OK | average pipeline duration = (298.00 + 260.00 + 276.00 + 269.00 + 315.00 + 334.00 + 297.00) / 7 = 292.71s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-24 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32685018845) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.25s | 1.44s | 276.77s | 71.93s | 298.00s |
| [2026-08-25 03:03](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32803361770) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.40s | 1.38s | 280.76s | 69.17s | 260.00s |
| [2026-08-26 03:09](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32925034333) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.39s | 1.16s | 307.44s | 58.05s | 276.00s |
| [2026-08-27 12:28](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33071579651) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.55s | 1.41s | 257.78s | 70.49s | 269.00s |
| [2026-08-28 13:55](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33177187113) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.18s | 1.41s | 274.93s | 70.42s | 315.00s |
| [2026-08-29 08:46](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33243684681) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.95s | 1.36s | 268.70s | 68.11s | 334.00s |
| [2026-08-30 08:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33300345944) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.65s | 1.41s | 260.48s | 70.34s | 297.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 93.65% | 4 | 3.17% | 9.23s | <= 11.00s | 23.14s | 94.59s | <= 100.00s | Failed |
| Firefox | 98.41% | 1 | 1.59% | 10.91s | <= 13.00s | 23.75s | 107.20s | <= 115.00s | OK |
| WebKit | 96.83% | 2 | 0.00% | 10.44s | <= 14.00s | 27.27s | 111.20s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-24 03:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.59s | <= 12.00s | Failed |
| 2026-08-26 03:09 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.00s | <= 12.00s | Failed |
| 2026-08-27 12:28 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.52s | <= 12.00s | Failed |
| 2026-08-25 03:03 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.60s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-24 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.39s | <= 1.50s | Failed |
| 2026-08-28 13:55 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.27s | <= 1.50s | Failed |
| 2026-08-30 08:02 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.70s | <= 1.50s | Failed |
| 2026-08-26 03:09 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.41s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
