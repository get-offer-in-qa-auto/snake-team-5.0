# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-20T00:00:00+00:00 — 2026-08-26T03:10:15+00:00).

Published runs: **7** · fully passed: **1** · final test results: **539** · flaky results: **6**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 97.77% | >= 98.00% | Failed | average pass rate = (98.70 + 96.10 + 98.70 + 97.40 + 97.40 + 100.00 + 96.10) / 7 = 97.77% |
| Average Fail Rate | 2.23% | <= 2.00% | Failed | average fail rate = (1.30 + 3.90 + 1.30 + 2.60 + 2.60 + 0.00 + 3.90) / 7 = 2.23% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Flaky Rate | 1.11% | <= 2.00% | OK | flaky rate = 6 / 539 = 1.11% |
| Average UI Flaky Rate | 3.17% | <= 2.00% | Failed | average UI flaky rate = (3.70 + 3.70 + 0.00 + 7.41 + 7.41 + 0.00 + 0.00) / 7 = 3.17% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 14.29% | >= 95.00% | Failed | stability = 1 / 7 = 14.29% |
| Average UI Test Duration | 10.27s | <= 12.00s | OK | average UI test duration = (9.47 + 9.86 + 9.74 + 10.81 + 10.25 + 10.40 + 11.39) / 7 = 10.27s |
| Average API Test Duration | 1.36s | <= 1.50s | OK | average API test duration = (1.39 + 1.36 + 1.41 + 1.36 + 1.44 + 1.38 + 1.16) / 7 = 1.36s |
| Total UI Test Time | 277.40s | <= 300.00s | OK | total UI test time = (255.69 + 266.24 + 262.88 + 291.99 + 276.77 + 280.76 + 307.44) / 7 = 277.40s |
| Average API Test Run Duration | 67.81s | <= 75.00s | OK | average API run duration = (69.52 + 67.77 + 70.31 + 67.91 + 71.93 + 69.17 + 58.05) / 7 = 67.81s |
| Average Pipeline Duration | 290.43s | <= 360.00s | OK | average pipeline duration = (302.00 + 293.00 + 303.00 + 301.00 + 298.00 + 260.00 + 276.00) / 7 = 290.43s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-20 03:01](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32326376910) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.47s | 1.39s | 255.69s | 69.52s | 302.00s |
| [2026-08-21 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32441916045) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.86s | 1.36s | 266.24s | 67.77s | 293.00s |
| [2026-08-22 02:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32547465653) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.74s | 1.41s | 262.88s | 70.31s | 303.00s |
| [2026-08-23 03:07](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32614295619) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.81s | 1.36s | 291.99s | 67.91s | 301.00s |
| [2026-08-24 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32685018845) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.25s | 1.44s | 276.77s | 71.93s | 298.00s |
| [2026-08-25 03:03](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32803361770) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.40s | 1.38s | 280.76s | 69.17s | 260.00s |
| [2026-08-26 03:09](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32925034333) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.39s | 1.16s | 307.44s | 58.05s | 276.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 95.24% | 3 | 3.17% | 8.77s | <= 11.00s | 22.76s | 92.66s | <= 100.00s | Failed |
| Firefox | 93.65% | 4 | 4.76% | 11.06s | <= 13.00s | 23.71s | 110.32s | <= 115.00s | Failed |
| WebKit | 95.24% | 3 | 1.59% | 10.99s | <= 14.00s | 27.57s | 116.11s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-23 03:07 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 35.07s | <= 12.00s | Failed |
| 2026-08-24 03:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.59s | <= 12.00s | Failed |
| 2026-08-26 03:09 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.00s | <= 12.00s | Failed |
| 2026-08-21 03:08 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 29.52s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-22 02:59 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.43s | <= 1.50s | Failed |
| 2026-08-24 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.39s | <= 1.50s | Failed |
| 2026-08-26 03:09 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.41s | <= 1.50s | Failed |
| 2026-08-21 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.25s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
