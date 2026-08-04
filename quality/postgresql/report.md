# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-29T00:00:00+00:00 — 2026-08-04T06:08:24+00:00).

Published runs: **9** · fully passed: **5** · final test results: **693** · flaky results: **1**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.42% | >= 98.00% | OK | average pass rate = (100.00 + 100.00 + 98.70 + 100.00 + 98.70 + 98.70 + 100.00 + 98.70 + 100.00) / 9 = 99.42% |
| Average Fail Rate | 0.58% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 1.30 + 0.00 + 1.30 + 1.30 + 0.00 + 1.30 + 0.00) / 9 = 0.58% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.00% |
| Flaky Rate | 0.14% | <= 2.00% | OK | flaky rate = 1 / 693 = 0.14% |
| Average UI Flaky Rate | 0.41% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 3.70 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.41% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 9 = 0.00% |
| Test Stability | 55.56% | >= 95.00% | Failed | stability = 5 / 9 = 55.56% |
| Average UI Test Duration | 10.23s | <= 12.00s | OK | average UI test duration = (8.45 + 8.46 + 11.33 + 11.21 + 11.69 + 9.75 + 8.87 + 10.84 + 11.49) / 9 = 10.23s |
| Average API Test Duration | 1.32s | <= 1.50s | OK | average API test duration = (1.07 + 0.94 + 1.41 + 1.47 + 1.39 + 1.38 + 1.40 + 1.44 + 1.37) / 9 = 1.32s |
| Total UI Test Time | 276.26s | <= 300.00s | OK | total UI test time = (228.17 + 228.38 + 306.04 + 302.70 + 315.65 + 263.21 + 239.38 + 292.62 + 310.23) / 9 = 276.26s |
| Average API Test Run Duration | 65.96s | <= 75.00s | OK | average API run duration = (53.62 + 46.97 + 70.46 + 73.69 + 69.58 + 68.81 + 70.07 + 71.96 + 68.45) / 9 = 65.96s |
| Average Pipeline Duration | 329.33s | <= 360.00s | OK | average pipeline duration = (452.00 + 420.00 + 297.00 + 281.00 + 329.00 + 290.00 + 284.00 + 313.00 + 298.00) / 9 = 329.33s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-31 12:52](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631704406) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.45s | 1.07s | 228.17s | 53.62s | 452.00s |
| [2026-07-31 12:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631712572) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.46s | 0.94s | 228.38s | 46.97s | 420.00s |
| [2026-07-31 13:13](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633108937) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.33s | 1.41s | 306.04s | 70.46s | 297.00s |
| [2026-07-31 13:19](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633470768) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.21s | 1.47s | 302.70s | 73.69s | 281.00s |
| [2026-07-31 13:26](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30633680390) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 11.69s | 1.39s | 315.65s | 69.58s | 329.00s |
| [2026-08-01 05:33](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30685864002) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.75s | 1.38s | 263.21s | 68.81s | 290.00s |
| [2026-08-02 05:33](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30734152165) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.87s | 1.40s | 239.38s | 70.07s | 284.00s |
| [2026-08-03 05:48](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30787886208) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 10.84s | 1.44s | 292.62s | 71.96s | 313.00s |
| [2026-08-04 05:21](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30880101070) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.49s | 1.37s | 310.23s | 68.45s | 298.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 97.53% | 2 | 0.00% | 9.41s | <= 11.00s | 21.79s | 91.43s | <= 100.00s | Failed |
| Firefox | 97.53% | 2 | 1.23% | 10.49s | <= 13.00s | 24.91s | 108.32s | <= 115.00s | Failed |
| WebKit | 100.00% | 0 | 0.00% | 10.80s | <= 14.00s | 28.66s | 115.35s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 13:26 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 37.62s | <= 12.00s | Failed |
| 2026-07-31 13:13 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 33.06s | <= 12.00s | Failed |
| 2026-07-31 13:19 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.46s | <= 12.00s | Failed |
| 2026-08-02 05:33 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.32s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 13:13 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.62s | <= 1.50s | Failed |
| 2026-08-02 05:33 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.48s | <= 1.50s | Failed |
| 2026-08-03 05:48 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.27s | <= 1.50s | Failed |
| 2026-07-31 13:19 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.14s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **16**
- Published Allure reports used in test metrics: **9**
- Workflow runs without a published report: **7**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
