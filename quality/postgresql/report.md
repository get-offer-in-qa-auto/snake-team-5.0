# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-15T00:00:00+00:00 — 2026-08-21T03:08:53+00:00).

Published runs: **5** · fully passed: **1** · final test results: **385** · flaky results: **2**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.18% | >= 98.00% | OK | average pass rate = (100.00 + 98.70 + 97.40 + 98.70 + 96.10) / 5 = 98.18% |
| Average Fail Rate | 1.82% | <= 2.00% | OK | average fail rate = (0.00 + 1.30 + 2.60 + 1.30 + 3.90) / 5 = 1.82% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 5 = 0.00% |
| Flaky Rate | 0.52% | <= 2.00% | OK | flaky rate = 2 / 385 = 0.52% |
| Average UI Flaky Rate | 1.48% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 3.70 + 3.70) / 5 = 1.48% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 5 = 0.00% |
| Test Stability | 20.00% | >= 95.00% | Failed | stability = 1 / 5 = 20.00% |
| Average UI Test Duration | 10.32s | <= 12.00s | OK | average UI test duration = (11.04 + 9.95 + 11.30 + 9.47 + 9.86) / 5 = 10.32s |
| Average API Test Duration | 1.34s | <= 1.50s | OK | average API test duration = (1.41 + 1.40 + 1.13 + 1.39 + 1.36) / 5 = 1.34s |
| Total UI Test Time | 278.75s | <= 300.00s | OK | total UI test time = (297.96 + 268.78 + 305.09 + 255.69 + 266.24) / 5 = 278.75s |
| Average API Test Run Duration | 66.88s | <= 75.00s | OK | average API run duration = (70.69 + 70.12 + 56.29 + 69.52 + 67.77) / 5 = 66.88s |
| Average Pipeline Duration | 291.80s | <= 360.00s | OK | average pipeline duration = (280.00 + 292.00 + 292.00 + 302.00 + 293.00) / 5 = 291.80s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-08-15 02:57](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31860264737) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.04s | 1.41s | 297.96s | 70.69s | 280.00s |
| [2026-08-16 03:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31923133352) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 9.95s | 1.40s | 268.78s | 70.12s | 292.00s |
| [2026-08-17 03:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/31989648091) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.30s | 1.13s | 305.09s | 56.29s | 292.00s |
| [2026-08-20 03:01](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32326376910) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.47s | 1.39s | 255.69s | 69.52s | 302.00s |
| [2026-08-21 03:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/32441916045) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.86s | 1.36s | 266.24s | 67.77s | 293.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 97.78% | 1 | 0.00% | 9.54s | <= 11.00s | 23.87s | 93.36s | <= 100.00s | Failed |
| Firefox | 93.33% | 3 | 2.22% | 10.28s | <= 13.00s | 21.55s | 110.49s | <= 115.00s | Failed |
| WebKit | 97.78% | 1 | 2.22% | 11.15s | <= 14.00s | 27.94s | 110.07s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-17 03:04 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 32.61s | <= 12.00s | Failed |
| 2026-08-16 03:04 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 30.00s | <= 12.00s | Failed |
| 2026-08-21 03:08 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 29.52s | <= 12.00s | Failed |
| 2026-08-15 02:57 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 28.63s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-08-15 02:57 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.34s | <= 1.50s | Failed |
| 2026-08-16 03:04 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.38s | <= 1.50s | Failed |
| 2026-08-21 03:08 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.25s | <= 1.50s | Failed |
| 2026-08-20 03:01 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.00s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **5**
- Workflow runs without a published report: **2**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
