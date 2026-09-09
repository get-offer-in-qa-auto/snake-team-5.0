# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-03T00:00:00+00:00 — 2026-09-09T07:13:36+00:00).

Published runs: **7** · fully passed: **3** · final test results: **539** · flaky results: **2**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.52% | >= 98.00% | OK | average pass rate = (100.00 + 100.00 + 97.40 + 100.00 + 96.10 + 98.70 + 97.40) / 7 = 98.52% |
| Average Fail Rate | 1.48% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 2.60 + 0.00 + 3.90 + 1.30 + 2.60) / 7 = 1.48% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.37% | <= 2.00% | OK | flaky rate = 2 / 539 = 0.37% |
| Average UI Flaky Rate | 1.06% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 7.41 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 1.06% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 42.86% | >= 95.00% | Failed | stability = 3 / 7 = 42.86% |
| Average UI Test Duration | 9.59s | <= 12.00s | OK | average UI test duration = (10.72 + 9.70 + 8.17 + 9.50 + 10.56 + 9.27 + 9.23) / 7 = 9.59s |
| Average API Test Duration | 1.35s | <= 1.50s | OK | average API test duration = (1.39 + 1.31 + 1.37 + 1.42 + 1.07 + 1.49 + 1.38) / 7 = 1.35s |
| Total UI Test Time | 258.98s | <= 300.00s | OK | total UI test time = (289.56 + 261.89 + 220.50 + 256.48 + 285.05 + 250.21 + 249.18) / 7 = 258.98s |
| Average API Test Run Duration | 67.45s | <= 75.00s | OK | average API run duration = (69.71 + 65.46 + 68.63 + 71.09 + 53.71 + 74.52 + 69.02) / 7 = 67.45s |
| Average Pipeline Duration | 302.57s | <= 360.00s | OK | average pipeline duration = (329.00 + 282.00 + 302.00 + 306.00 + 305.00 + 277.00 + 317.00) / 7 = 302.57s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-03 07:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33725413539) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.72s | 1.39s | 289.56s | 69.71s | 329.00s |
| [2026-09-04 07:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33846619984) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.70s | 1.31s | 261.89s | 65.46s | 282.00s |
| [2026-09-05 06:48](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33950562289) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 8.17s | 1.37s | 220.50s | 68.63s | 302.00s |
| [2026-09-06 06:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34017664766) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.50s | 1.42s | 256.48s | 71.09s | 306.00s |
| [2026-09-07 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34093516528) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.56s | 1.07s | 285.05s | 53.71s | 305.00s |
| [2026-09-08 07:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34196968762) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.27s | 1.49s | 250.21s | 74.52s | 277.00s |
| [2026-09-09 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34322183656) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.23s | 1.38s | 249.18s | 69.02s | 317.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 96.83% | 2 | 0.00% | 8.58s | <= 11.00s | 21.89s | 93.10s | <= 100.00s | Failed |
| Firefox | 96.83% | 2 | 1.59% | 10.04s | <= 13.00s | 24.26s | 104.54s | <= 115.00s | Failed |
| WebKit | 98.41% | 1 | 1.59% | 10.16s | <= 14.00s | 25.94s | 115.17s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-07 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.82s | <= 12.00s | Failed |
| 2026-09-03 07:00 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.45s | <= 12.00s | Failed |
| 2026-09-06 06:59 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.19s | <= 12.00s | Failed |
| 2026-09-04 07:04 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 26.85s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-06 06:59 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.58s | <= 1.50s | Failed |
| 2026-09-03 07:00 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.44s | <= 1.50s | Failed |
| 2026-09-08 07:02 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 27.93s | <= 1.50s | Failed |
| 2026-09-05 06:48 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 26.61s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
