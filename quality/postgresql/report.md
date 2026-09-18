# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-12T00:00:00+00:00 — 2026-09-18T07:13:33+00:00).

Published runs: **7** · fully passed: **1** · final test results: **539** · flaky results: **7**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.52% | >= 98.00% | OK | average pass rate = (97.40 + 97.40 + 98.70 + 98.70 + 98.70 + 100.00 + 98.70) / 7 = 98.52% |
| Average Fail Rate | 1.30% | <= 2.00% | OK | average fail rate = (2.60 + 2.60 + 0.00 + 1.30 + 1.30 + 0.00 + 1.30) / 7 = 1.30% |
| Average Broken Rate | 0.19% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 1.30 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.19% |
| Flaky Rate | 1.30% | <= 2.00% | OK | flaky rate = 7 / 539 = 1.30% |
| Average UI Flaky Rate | 3.70% | <= 2.00% | Failed | average UI flaky rate = (7.41 + 7.41 + 0.00 + 3.70 + 3.70 + 0.00 + 3.70) / 7 = 3.70% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 14.29% | >= 95.00% | Failed | stability = 1 / 7 = 14.29% |
| Average UI Test Duration | 9.30s | <= 12.00s | OK | average UI test duration = (6.37 + 9.57 + 10.59 + 9.56 + 7.74 + 10.71 + 10.58) / 7 = 9.30s |
| Average API Test Duration | 1.44s | <= 1.50s | OK | average API test duration = (1.49 + 1.42 + 1.55 + 1.42 + 1.39 + 1.41 + 1.43) / 7 = 1.44s |
| Total UI Test Time | 251.16s | <= 300.00s | OK | total UI test time = (172.02 + 258.36 + 285.85 + 258.07 + 209.07 + 289.07 + 285.67) / 7 = 251.16s |
| Average API Test Run Duration | 72.19s | <= 75.00s | OK | average API run duration = (74.59 + 71.13 + 77.39 + 71.16 + 69.45 + 70.32 + 71.29) / 7 = 72.19s |
| Average Pipeline Duration | 300.00s | <= 360.00s | OK | average pipeline duration = (277.00 + 297.00 + 298.00 + 383.00 + 267.00 + 257.00 + 321.00) / 7 = 300.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-12 07:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34679340989) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 6.37s | 1.49s | 172.02s | 74.59s | 277.00s |
| [2026-09-13 07:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34744643454) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 9.57s | 1.42s | 258.36s | 71.13s | 297.00s |
| [2026-09-14 07:42](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34818612231) | 77 | 76 / 98.70% | 0 / 0.00% | 1 / 1.30% | 0 / 0.00% | Unstable | 10.59s | 1.55s | 285.85s | 77.39s | 298.00s |
| [2026-09-15 07:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34940697002) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.56s | 1.42s | 258.07s | 71.16s | 383.00s |
| [2026-09-16 07:23](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35067764436) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 7.74s | 1.39s | 209.07s | 69.45s | 267.00s |
| [2026-09-17 07:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35193434398) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.71s | 1.41s | 289.07s | 70.32s | 257.00s |
| [2026-09-18 07:12](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35317840566) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 10.58s | 1.43s | 285.67s | 71.29s | 321.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 96.83% | 2 | 3.17% | 8.91s | <= 11.00s | 23.67s | 93.90s | <= 100.00s | Failed |
| Firefox | 92.06% | 5 | 7.94% | 9.51s | <= 13.00s | 21.75s | 101.62s | <= 115.00s | Failed |
| WebKit | 98.41% | 1 | 0.00% | 9.49s | <= 14.00s | 24.80s | 97.87s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-14 07:42 | tests.ui.identity_access.test_user_creation#test_admin_can_create_user | 42.13s | <= 12.00s | Failed |
| 2026-09-18 07:12 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.08s | <= 12.00s | Failed |
| 2026-09-15 07:22 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.34s | <= 12.00s | Failed |
| 2026-09-15 07:22 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 26.52s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-16 07:23 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.81s | <= 1.50s | Failed |
| 2026-09-12 07:00 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.68s | <= 1.50s | Failed |
| 2026-09-14 07:42 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.45s | <= 1.50s | Failed |
| 2026-09-18 07:12 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.78s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
