# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-23T00:00:00+00:00 — 2026-08-29T08:47:26+00:00).

Published runs: **7** · fully passed: **2** · final test results: **539** · flaky results: **5**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 97.96% | >= 98.00% | Failed | average pass rate = (97.40 + 97.40 + 100.00 + 96.10 + 100.00 + 98.70 + 96.10) / 7 = 97.96% |
| Average Fail Rate | 2.04% | <= 2.00% | Failed | average fail rate = (2.60 + 2.60 + 0.00 + 3.90 + 0.00 + 1.30 + 3.90) / 7 = 2.04% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.93% | <= 2.00% | OK | flaky rate = 5 / 539 = 0.93% |
| Average UI Flaky Rate | 2.65% | <= 2.00% | Failed | average UI flaky rate = (7.41 + 7.41 + 0.00 + 0.00 + 0.00 + 0.00 + 3.70) / 7 = 2.65% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 28.57% | >= 95.00% | Failed | stability = 2 / 7 = 28.57% |
| Average UI Test Duration | 10.36s | <= 12.00s | OK | average UI test duration = (10.81 + 10.25 + 10.40 + 11.39 + 9.55 + 10.18 + 9.95) / 7 = 10.36s |
| Average API Test Duration | 1.36s | <= 1.50s | OK | average API test duration = (1.36 + 1.44 + 1.38 + 1.16 + 1.41 + 1.41 + 1.36) / 7 = 1.36s |
| Total UI Test Time | 279.77s | <= 300.00s | OK | total UI test time = (291.99 + 276.77 + 280.76 + 307.44 + 257.78 + 274.93 + 268.70) / 7 = 279.77s |
| Average API Test Run Duration | 68.01s | <= 75.00s | OK | average API run duration = (67.91 + 71.93 + 69.17 + 58.05 + 70.49 + 70.42 + 68.11) / 7 = 68.01s |
| Average Pipeline Duration | 293.29s | <= 360.00s | OK | average pipeline duration = (301.00 + 298.00 + 260.00 + 276.00 + 269.00 + 315.00 + 334.00) / 7 = 293.29s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-23 03:07](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32614295619) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.81s | 1.36s | 291.99s | 67.91s | 301.00s |
| [2026-08-24 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32685018845) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.25s | 1.44s | 276.77s | 71.93s | 298.00s |
| [2026-08-25 03:03](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32803361770) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.40s | 1.38s | 280.76s | 69.17s | 260.00s |
| [2026-08-26 03:09](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32925034333) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.39s | 1.16s | 307.44s | 58.05s | 276.00s |
| [2026-08-27 12:28](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33071579651) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.55s | 1.41s | 257.78s | 70.49s | 269.00s |
| [2026-08-28 13:55](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33177187113) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.18s | 1.41s | 274.93s | 70.42s | 315.00s |
| [2026-08-29 08:46](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33243684681) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.95s | 1.36s | 268.70s | 68.11s | 334.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 92.06% | 5 | 4.76% | 9.00s | <= 11.00s | 23.14s | 94.59s | <= 100.00s | Failed |
| Firefox | 96.83% | 2 | 3.17% | 10.91s | <= 13.00s | 23.75s | 107.20s | <= 115.00s | Failed |
| WebKit | 96.83% | 2 | 0.00% | 11.17s | <= 14.00s | 28.43s | 116.11s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-23 03:07 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 35.07s | <= 12.00s | Failed |
| 2026-08-24 03:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.59s | <= 12.00s | Failed |
| 2026-08-26 03:09 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.00s | <= 12.00s | Failed |
| 2026-08-27 12:28 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.52s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-24 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.39s | <= 1.50s | Failed |
| 2026-08-28 13:55 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.27s | <= 1.50s | Failed |
| 2026-08-26 03:09 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.41s | <= 1.50s | Failed |
| 2026-08-27 12:28 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.39s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
