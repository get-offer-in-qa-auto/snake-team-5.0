# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-16T00:00:00+00:00 — 2026-08-22T04:01:55+00:00).

Published runs: **5** · fully passed: **0** · final test results: **385** · flaky results: **2**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 97.92% | >= 98.00% | Failed | average pass rate = (98.70 + 97.40 + 98.70 + 96.10 + 98.70) / 5 = 97.92% |
| Average Fail Rate | 2.08% | <= 2.00% | Failed | average fail rate = (1.30 + 2.60 + 1.30 + 3.90 + 1.30) / 5 = 2.08% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 5 = 0.00% |
| Flaky Rate | 0.52% | <= 2.00% | OK | flaky rate = 2 / 385 = 0.52% |
| Average UI Flaky Rate | 1.48% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 3.70 + 3.70 + 0.00) / 5 = 1.48% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 5 = 0.00% |
| Test Stability | 0.00% | >= 95.00% | Failed | stability = 0 / 5 = 0.00% |
| Average UI Test Duration | 10.06s | <= 12.00s | OK | average UI test duration = (9.95 + 11.30 + 9.47 + 9.86 + 9.74) / 5 = 10.06s |
| Average API Test Duration | 1.34s | <= 1.50s | OK | average API test duration = (1.40 + 1.13 + 1.39 + 1.36 + 1.41) / 5 = 1.34s |
| Total UI Test Time | 271.74s | <= 300.00s | OK | total UI test time = (268.78 + 305.09 + 255.69 + 266.24 + 262.88) / 5 = 271.74s |
| Average API Test Run Duration | 66.80s | <= 75.00s | OK | average API run duration = (70.12 + 56.29 + 69.52 + 67.77 + 70.31) / 5 = 66.80s |
| Average Pipeline Duration | 296.40s | <= 360.00s | OK | average pipeline duration = (292.00 + 292.00 + 302.00 + 293.00 + 303.00) / 5 = 296.40s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-16 03:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31923133352) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.95s | 1.40s | 268.78s | 70.12s | 292.00s |
| [2026-08-17 03:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31989648091) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.30s | 1.13s | 305.09s | 56.29s | 292.00s |
| [2026-08-20 03:01](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32326376910) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.47s | 1.39s | 255.69s | 69.52s | 302.00s |
| [2026-08-21 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32441916045) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.86s | 1.36s | 266.24s | 67.77s | 293.00s |
| [2026-08-22 02:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32547465653) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.74s | 1.41s | 262.88s | 70.31s | 303.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 97.78% | 1 | 0.00% | 9.57s | <= 11.00s | 23.87s | 93.64s | <= 100.00s | Failed |
| Firefox | 93.33% | 3 | 2.22% | 10.14s | <= 13.00s | 21.55s | 109.93s | <= 115.00s | Failed |
| WebKit | 95.56% | 2 | 2.22% | 10.48s | <= 14.00s | 26.97s | 110.07s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-17 03:04 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 32.61s | <= 12.00s | Failed |
| 2026-08-16 03:04 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.00s | <= 12.00s | Failed |
| 2026-08-21 03:08 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 29.52s | <= 12.00s | Failed |
| 2026-08-20 03:01 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 27.33s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-22 02:59 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.43s | <= 1.50s | Failed |
| 2026-08-16 03:04 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.38s | <= 1.50s | Failed |
| 2026-08-21 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.25s | <= 1.50s | Failed |
| 2026-08-20 03:01 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.00s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **5**
- Workflow runs without a published report: **2**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
