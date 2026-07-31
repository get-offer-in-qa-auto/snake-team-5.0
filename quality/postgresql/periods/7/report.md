# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-25T00:00:00+00:00 — 2026-07-31T15:00:47+00:00).

Published runs: **5** · fully passed: **3** · final test results: **385** · flaky results: **1**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.48% | >= 98.00% | OK | average pass rate = (100.00 + 100.00 + 98.70 + 100.00 + 98.70) / 5 = 99.48% |
| Average Fail Rate | 0.52% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 1.30 + 0.00 + 1.30) / 5 = 0.52% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 5 = 0.00% |
| Flaky Rate | 0.26% | <= 2.00% | OK | flaky rate = 1 / 385 = 0.26% |
| Average UI Flaky Rate | 0.74% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 3.70) / 5 = 0.74% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 5 = 0.00% |
| Test Stability | 60.00% | >= 95.00% | Failed | stability = 3 / 5 = 60.00% |
| Average UI Test Duration | 10.23s | <= 12.00s | OK | average UI test duration = (8.45 + 8.46 + 11.33 + 11.21 + 11.69) / 5 = 10.23s |
| Average API Test Duration | 1.26s | <= 1.50s | OK | average API test duration = (1.07 + 0.94 + 1.41 + 1.47 + 1.39) / 5 = 1.26s |
| Total UI Test Time | 276.19s | <= 300.00s | OK | total UI test time = (228.17 + 228.38 + 306.04 + 302.70 + 315.65) / 5 = 276.19s |
| Average API Test Run Duration | 62.86s | <= 75.00s | OK | average API run duration = (53.62 + 46.97 + 70.46 + 73.69 + 69.58) / 5 = 62.86s |
| Average Pipeline Duration | 355.80s | <= 360.00s | OK | average pipeline duration = (452.00 + 420.00 + 297.00 + 281.00 + 329.00) / 5 = 355.80s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-31 12:52](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631704406) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.45s | 1.07s | 228.17s | 53.62s | 452.00s |
| [2026-07-31 12:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631712572) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.46s | 0.94s | 228.38s | 46.97s | 420.00s |
| [2026-07-31 13:13](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633108937) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.33s | 1.41s | 306.04s | 70.46s | 297.00s |
| [2026-07-31 13:19](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633470768) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.21s | 1.47s | 302.70s | 73.69s | 281.00s |
| [2026-07-31 13:26](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633680390) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 11.69s | 1.39s | 315.65s | 69.58s | 329.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 9.40s | <= 11.00s | 20.51s | 89.29s | <= 100.00s | OK |
| Firefox | 95.56% | 2 | 2.22% | 10.53s | <= 13.00s | 22.97s | 106.51s | <= 115.00s | Failed |
| WebKit | 100.00% | 0 | 0.00% | 10.76s | <= 14.00s | 28.02s | 121.48s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 13:26 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 37.62s | <= 12.00s | Failed |
| 2026-07-31 13:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 33.06s | <= 12.00s | Failed |
| 2026-07-31 13:19 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.46s | <= 12.00s | Failed |
| 2026-07-31 13:26 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 25.51s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 13:13 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.62s | <= 1.50s | Failed |
| 2026-07-31 13:19 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.14s | <= 1.50s | Failed |
| 2026-07-31 13:26 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.41s | <= 1.50s | Failed |
| 2026-07-31 13:19 | tests.api.build_execution.test_build_runtime_parameters#test_build_run_with_runtime_parameter | 16.99s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **16**
- Published Allure reports used in test metrics: **5**
- Workflow runs without a published report: **11**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
