# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-06T00:00:00+00:00 — 2026-08-12T05:11:11+00:00).

Published runs: **7** · fully passed: **5** · final test results: **539** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.44% | >= 98.00% | OK | average pass rate = (98.70 + 100.00 + 100.00 + 100.00 + 97.40 + 100.00 + 100.00) / 7 = 99.44% |
| Average Fail Rate | 0.56% | <= 2.00% | OK | average fail rate = (1.30 + 0.00 + 0.00 + 0.00 + 2.60 + 0.00 + 0.00) / 7 = 0.56% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 539 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 71.43% | >= 95.00% | Failed | stability = 5 / 7 = 71.43% |
| Average UI Test Duration | 10.42s | <= 12.00s | OK | average UI test duration = (11.01 + 10.93 + 9.70 + 10.00 + 10.82 + 8.53 + 11.96) / 7 = 10.42s |
| Average API Test Duration | 1.27s | <= 1.50s | OK | average API test duration = (1.38 + 1.40 + 1.38 + 1.38 + 0.60 + 1.40 + 1.36) / 7 = 1.27s |
| Total UI Test Time | 281.36s | <= 300.00s | OK | total UI test time = (297.15 + 295.23 + 261.77 + 270.02 + 292.16 + 230.26 + 322.90) / 7 = 281.36s |
| Average API Test Run Duration | 63.47s | <= 75.00s | OK | average API run duration = (68.82 + 69.81 + 68.92 + 68.84 + 30.12 + 69.91 + 67.85) / 7 = 63.47s |
| Average Pipeline Duration | 328.57s | <= 360.00s | OK | average pipeline duration = (571.00 + 290.00 + 288.00 + 280.00 + 281.00 + 301.00 + 289.00) / 7 = 328.57s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-06 05:27](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31073646604) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.01s | 1.38s | 297.15s | 68.82s | 571.00s |
| [2026-08-07 04:31](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31147367715) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.93s | 1.40s | 295.23s | 69.81s | 290.00s |
| [2026-08-08 03:30](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31237135709) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.70s | 1.38s | 261.77s | 68.92s | 288.00s |
| [2026-08-09 03:47](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31292965512) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.00s | 1.38s | 270.02s | 68.84s | 280.00s |
| [2026-08-10 04:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31353883386) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.82s | 0.60s | 292.16s | 30.12s | 281.00s |
| [2026-08-11 03:49](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31456259472) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.53s | 1.40s | 230.26s | 69.91s | 301.00s |
| [2026-08-12 04:13](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31562257105) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.96s | 1.36s | 322.90s | 67.85s | 289.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.16s | <= 11.00s | 22.63s | 95.90s | <= 100.00s | OK |
| Firefox | 98.41% | 1 | 0.00% | 10.94s | <= 13.00s | 23.25s | 108.17s | <= 115.00s | OK |
| WebKit | 100.00% | 0 | 0.00% | 11.17s | <= 14.00s | 27.74s | 113.41s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-06 05:27 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 32.85s | <= 12.00s | Failed |
| 2026-08-12 04:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.66s | <= 12.00s | Failed |
| 2026-08-08 03:30 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.34s | <= 12.00s | Failed |
| 2026-08-07 04:31 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.76s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-06 05:27 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.41s | <= 1.50s | Failed |
| 2026-08-07 04:31 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.56s | <= 1.50s | Failed |
| 2026-08-08 03:30 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.37s | <= 1.50s | Failed |
| 2026-08-11 03:49 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 27.51s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
