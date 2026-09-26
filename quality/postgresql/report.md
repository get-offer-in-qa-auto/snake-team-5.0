# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-20T00:00:00+00:00 — 2026-09-26T07:12:18+00:00).

Published runs: **7** · fully passed: **2** · final test results: **539** · flaky results: **4**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.52% | >= 98.00% | OK | average pass rate = (100.00 + 98.70 + 97.40 + 98.70 + 100.00 + 97.40 + 97.40) / 7 = 98.52% |
| Average Fail Rate | 1.48% | <= 2.00% | OK | average fail rate = (0.00 + 1.30 + 2.60 + 1.30 + 0.00 + 2.60 + 2.60) / 7 = 1.48% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.74% | <= 2.00% | OK | flaky rate = 4 / 539 = 0.74% |
| Average UI Flaky Rate | 2.12% | <= 2.00% | Failed | average UI flaky rate = (0.00 + 3.70 + 3.70 + 3.70 + 0.00 + 3.70 + 0.00) / 7 = 2.12% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 28.57% | >= 95.00% | Failed | stability = 2 / 7 = 28.57% |
| Average UI Test Duration | 10.13s | <= 12.00s | OK | average UI test duration = (10.95 + 8.99 + 10.41 + 11.04 + 10.42 + 10.00 + 9.08) / 7 = 10.13s |
| Average API Test Duration | 1.36s | <= 1.50s | OK | average API test duration = (1.41 + 1.42 + 1.30 + 1.42 + 1.40 + 1.21 + 1.37) / 7 = 1.36s |
| Total UI Test Time | 273.39s | <= 300.00s | OK | total UI test time = (295.55 + 242.79 + 280.96 + 298.04 + 281.38 + 269.98 + 245.03) / 7 = 273.39s |
| Average API Test Run Duration | 68.02s | <= 75.00s | OK | average API run duration = (70.55 + 70.92 + 64.92 + 70.88 + 69.78 + 60.74 + 68.38) / 7 = 68.02s |
| Average Pipeline Duration | 315.00s | <= 360.00s | OK | average pipeline duration = (267.00 + 278.00 + 259.00 + 534.00 + 327.00 + 288.00 + 252.00) / 7 = 315.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-20 07:34](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35496984029) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.95s | 1.41s | 295.55s | 70.55s | 267.00s |
| [2026-09-21 07:45](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35574038759) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 8.99s | 1.42s | 242.79s | 70.92s | 278.00s |
| [2026-09-22 07:27](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35699227389) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.41s | 1.30s | 280.96s | 64.92s | 259.00s |
| [2026-09-23 07:34](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35831506203) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 11.04s | 1.42s | 298.04s | 70.88s | 534.00s |
| [2026-09-24 07:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35968652436) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.42s | 1.40s | 281.38s | 69.78s | 327.00s |
| [2026-09-25 07:16](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/36106257985) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.00s | 1.21s | 269.98s | 60.74s | 288.00s |
| [2026-09-26 07:11](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/36225751068) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.08s | 1.37s | 245.03s | 68.38s | 252.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 98.41% | 1 | 0.00% | 9.14s | <= 11.00s | 23.56s | 91.59s | <= 100.00s | OK |
| Firefox | 93.65% | 4 | 6.35% | 10.61s | <= 13.00s | 24.33s | 103.47s | <= 115.00s | Failed |
| WebKit | 96.83% | 2 | 0.00% | 10.63s | <= 14.00s | 29.31s | 104.97s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-25 07:16 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.86s | <= 12.00s | Failed |
| 2026-09-23 07:34 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.33s | <= 12.00s | Failed |
| 2026-09-20 07:34 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.98s | <= 12.00s | Failed |
| 2026-09-21 07:45 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.44s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-25 07:16 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.05s | <= 1.50s | Failed |
| 2026-09-23 07:34 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.91s | <= 1.50s | Failed |
| 2026-09-21 07:45 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.06s | <= 1.50s | Failed |
| 2026-09-20 07:34 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.05s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
