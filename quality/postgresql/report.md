# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-19T00:00:00+00:00 — 2026-08-25T04:05:41+00:00).

Published runs: **6** · fully passed: **1** · final test results: **462** · flaky results: **6**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.05% | >= 98.00% | OK | average pass rate = (98.70 + 96.10 + 98.70 + 97.40 + 97.40 + 100.00) / 6 = 98.05% |
| Average Fail Rate | 1.95% | <= 2.00% | OK | average fail rate = (1.30 + 3.90 + 1.30 + 2.60 + 2.60 + 0.00) / 6 = 1.95% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 6 = 0.00% |
| Flaky Rate | 1.30% | <= 2.00% | OK | flaky rate = 6 / 462 = 1.30% |
| Average UI Flaky Rate | 3.70% | <= 2.00% | Failed | average UI flaky rate = (3.70 + 3.70 + 0.00 + 7.41 + 7.41 + 0.00) / 6 = 3.70% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 6 = 0.00% |
| Test Stability | 16.67% | >= 95.00% | Failed | stability = 1 / 6 = 16.67% |
| Average UI Test Duration | 10.09s | <= 12.00s | OK | average UI test duration = (9.47 + 9.86 + 9.74 + 10.81 + 10.25 + 10.40) / 6 = 10.09s |
| Average API Test Duration | 1.39s | <= 1.50s | OK | average API test duration = (1.39 + 1.36 + 1.41 + 1.36 + 1.44 + 1.38) / 6 = 1.39s |
| Total UI Test Time | 272.39s | <= 300.00s | OK | total UI test time = (255.69 + 266.24 + 262.88 + 291.99 + 276.77 + 280.76) / 6 = 272.39s |
| Average API Test Run Duration | 69.44s | <= 75.00s | OK | average API run duration = (69.52 + 67.77 + 70.31 + 67.91 + 71.93 + 69.17) / 6 = 69.44s |
| Average Pipeline Duration | 292.83s | <= 360.00s | OK | average pipeline duration = (302.00 + 293.00 + 303.00 + 301.00 + 298.00 + 260.00) / 6 = 292.83s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-20 03:01](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32326376910) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.47s | 1.39s | 255.69s | 69.52s | 302.00s |
| [2026-08-21 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32441916045) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.86s | 1.36s | 266.24s | 67.77s | 293.00s |
| [2026-08-22 02:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32547465653) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.74s | 1.41s | 262.88s | 70.31s | 303.00s |
| [2026-08-23 03:07](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32614295619) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.81s | 1.36s | 291.99s | 67.91s | 301.00s |
| [2026-08-24 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32685018845) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.25s | 1.44s | 276.77s | 71.93s | 298.00s |
| [2026-08-25 03:03](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32803361770) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.40s | 1.38s | 280.76s | 69.17s | 260.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 94.44% | 3 | 3.70% | 8.52s | <= 11.00s | 19.82s | 92.69s | <= 100.00s | Failed |
| Firefox | 92.59% | 4 | 5.56% | 10.92s | <= 13.00s | 24.11s | 110.18s | <= 115.00s | Failed |
| WebKit | 96.30% | 2 | 1.85% | 10.82s | <= 14.00s | 27.43s | 116.12s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-23 03:07 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 35.07s | <= 12.00s | Failed |
| 2026-08-24 03:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 31.59s | <= 12.00s | Failed |
| 2026-08-21 03:08 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 29.52s | <= 12.00s | Failed |
| 2026-08-25 03:03 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.60s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-22 02:59 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.43s | <= 1.50s | Failed |
| 2026-08-24 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.39s | <= 1.50s | Failed |
| 2026-08-21 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.25s | <= 1.50s | Failed |
| 2026-08-20 03:01 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.00s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **6**
- Workflow runs without a published report: **1**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
