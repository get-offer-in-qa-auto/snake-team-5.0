# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-06T00:00:00+00:00 — 2026-08-12T04:14:33+00:00).

Published runs: **9** · fully passed: **9** · final test results: **693** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 100.00% | >= 98.00% | OK | average pass rate = (100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00) / 9 = 100.00% |
| Average Fail Rate | 0.00% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.00% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.00% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 693 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.00% |
| Test Stability | 100.00% | >= 95.00% | OK | stability = 9 / 9 = 100.00% |
| Average UI Test Duration | 9.98s | <= 12.00s | OK | average UI test duration = (11.05 + 9.41 + 10.27 + 10.58 + 9.85 + 8.68 + 8.18 + 10.93 + 10.90) / 9 = 9.98s |
| Average API Test Duration | 1.45s | <= 1.50s | OK | average API test duration = (1.42 + 1.51 + 1.45 + 1.48 + 1.47 + 1.47 + 1.43 + 1.38 + 1.44) / 9 = 1.45s |
| Total UI Test Time | 269.54s | <= 300.00s | OK | total UI test time = (298.25 + 254.05 + 277.33 + 285.70 + 265.96 + 234.44 + 220.75 + 295.13 + 294.20) / 9 = 269.54s |
| Average API Test Run Duration | 72.46s | <= 75.00s | OK | average API run duration = (70.87 + 75.32 + 72.72 + 73.77 + 73.71 + 73.27 + 71.58 + 68.91 + 71.98) / 9 = 72.46s |
| Average Pipeline Duration | 395.00s | <= 360.00s | Failed | average pipeline duration = (341.00 + 280.00 + 1168.00 + 304.00 + 286.00 + 295.00 + 272.00 + 306.00 + 303.00) / 9 = 395.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-07 09:20](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31164949778) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.05s | 1.42s | 298.25s | 70.87s | 341.00s |
| [2026-08-07 09:37](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31166256163) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.41s | 1.51s | 254.05s | 75.32s | 280.00s |
| [2026-08-07 10:55](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31170659901) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.27s | 1.45s | 277.33s | 72.72s | 1168.00s |
| [2026-08-07 11:50](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31175218040) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.58s | 1.48s | 285.70s | 73.77s | 304.00s |
| [2026-08-07 12:14](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31176944511) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.85s | 1.47s | 265.96s | 73.71s | 286.00s |
| [2026-08-07 12:25](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31177720513) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.68s | 1.47s | 234.44s | 73.27s | 295.00s |
| [2026-08-07 12:35](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31178419149) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.18s | 1.43s | 220.75s | 71.58s | 272.00s |
| [2026-08-07 13:41](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31183279080) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.93s | 1.38s | 295.13s | 68.91s | 306.00s |
| [2026-08-07 14:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31185899467) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.90s | 1.44s | 294.20s | 71.98s | 303.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.71s | <= 11.00s | 23.11s | 93.85s | <= 100.00s | OK |
| Firefox | 100.00% | 0 | 0.00% | 9.97s | <= 13.00s | 21.65s | 104.33s | <= 115.00s | OK |
| WebKit | 100.00% | 0 | 0.00% | 10.28s | <= 14.00s | 27.23s | 107.63s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-07 09:20 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.09s | <= 12.00s | Failed |
| 2026-08-07 10:55 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 33.97s | <= 12.00s | Failed |
| 2026-08-07 11:50 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.85s | <= 12.00s | Failed |
| 2026-08-07 14:12 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.79s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-07 09:37 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.09s | <= 1.50s | Failed |
| 2026-08-07 12:14 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.81s | <= 1.50s | Failed |
| 2026-08-07 11:50 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 26.01s | <= 1.50s | Failed |
| 2026-08-07 10:55 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 25.13s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **9**
- Published Allure reports used in test metrics: **9**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
