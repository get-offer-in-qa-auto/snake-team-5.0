# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-01T00:00:00+00:00 — 2026-09-07T07:09:22+00:00).

Published runs: **7** · fully passed: **4** · final test results: **539** · flaky results: **4**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.70% | >= 98.00% | OK | average pass rate = (97.40 + 100.00 + 100.00 + 100.00 + 97.40 + 100.00 + 96.10) / 7 = 98.70% |
| Average Fail Rate | 1.30% | <= 2.00% | OK | average fail rate = (2.60 + 0.00 + 0.00 + 0.00 + 2.60 + 0.00 + 3.90) / 7 = 1.30% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 0.74% | <= 2.00% | OK | flaky rate = 4 / 539 = 0.74% |
| Average UI Flaky Rate | 2.12% | <= 2.00% | Failed | average UI flaky rate = (7.41 + 0.00 + 0.00 + 0.00 + 7.41 + 0.00 + 0.00) / 7 = 2.12% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 57.14% | >= 95.00% | Failed | stability = 4 / 7 = 57.14% |
| Average UI Test Duration | 9.73s | <= 12.00s | OK | average UI test duration = (10.03 + 9.43 + 10.72 + 9.70 + 8.17 + 9.50 + 10.56) / 7 = 9.73s |
| Average API Test Duration | 1.34s | <= 1.50s | OK | average API test duration = (1.42 + 1.41 + 1.39 + 1.31 + 1.37 + 1.42 + 1.07) / 7 = 1.34s |
| Total UI Test Time | 262.69s | <= 300.00s | OK | total UI test time = (270.78 + 254.54 + 289.56 + 261.89 + 220.50 + 256.48 + 285.05) / 7 = 262.69s |
| Average API Test Run Duration | 67.14s | <= 75.00s | OK | average API run duration = (70.88 + 70.52 + 69.71 + 65.46 + 68.63 + 71.09 + 53.71) / 7 = 67.14s |
| Average Pipeline Duration | 305.14s | <= 360.00s | OK | average pipeline duration = (308.00 + 304.00 + 329.00 + 282.00 + 302.00 + 306.00 + 305.00) / 7 = 305.14s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-01 07:26](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33481630668) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.03s | 1.42s | 270.78s | 70.88s | 308.00s |
| [2026-09-02 06:57](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33600685235) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.43s | 1.41s | 254.54s | 70.52s | 304.00s |
| [2026-09-03 07:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33725413539) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.72s | 1.39s | 289.56s | 69.71s | 329.00s |
| [2026-09-04 07:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33846619984) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.70s | 1.31s | 261.89s | 65.46s | 282.00s |
| [2026-09-05 06:48](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/33950562289) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 8.17s | 1.37s | 220.50s | 68.63s | 302.00s |
| [2026-09-06 06:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34017664766) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.50s | 1.42s | 256.48s | 71.09s | 306.00s |
| [2026-09-07 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34093516528) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.56s | 1.07s | 285.05s | 53.71s | 305.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 98.41% | 1 | 1.59% | 9.49s | <= 11.00s | 23.84s | 94.06s | <= 100.00s | OK |
| Firefox | 98.41% | 1 | 1.59% | 9.48s | <= 13.00s | 20.86s | 102.08s | <= 115.00s | OK |
| WebKit | 96.83% | 2 | 3.17% | 10.22s | <= 14.00s | 28.43s | 115.17s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-07 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.82s | <= 12.00s | Failed |
| 2026-09-03 07:00 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.45s | <= 12.00s | Failed |
| 2026-09-02 06:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.31s | <= 12.00s | Failed |
| 2026-09-06 06:59 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.19s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-06 06:59 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.58s | <= 1.50s | Failed |
| 2026-09-01 07:26 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.31s | <= 1.50s | Failed |
| 2026-09-03 07:00 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.44s | <= 1.50s | Failed |
| 2026-09-02 06:57 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.92s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
