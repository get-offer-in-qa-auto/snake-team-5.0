# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-25T00:00:00+00:00 — 2026-07-31T08:59:28+00:00).

Published runs: **16** · fully passed: **13** · final test results: **1166** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.59% | >= 98.00% | OK | average pass rate = (100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 98.70 + 100.00 + 98.70 + 96.10 + 100.00 + 100.00) / 16 = 99.59% |
| Average Fail Rate | 0.24% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 3.90 + 0.00 + 0.00) / 16 = 0.24% |
| Average Broken Rate | 0.16% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 1.30 + 0.00 + 1.30 + 0.00 + 0.00 + 0.00) / 16 = 0.16% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 1166 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 16 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 16 = 0.00% |
| Test Stability | 81.25% | >= 95.00% | Failed | stability = 13 / 16 = 81.25% |
| Average Test Duration | 4.44s | <= 3.00s | Failed | average test duration = (3.94 + 4.51 + 4.56 + 4.17 + 4.21 + 3.87 + 4.36 + 4.16 + 4.38 + 4.06 + 5.02 + 4.35 + 4.72 + 4.90 + 4.81 + 5.04) / 16 = 4.44s |
| Average API Test Duration | 1.45s | <= 0.20s | Failed | average API test duration = (1.49 + 1.48 + 1.43 + 1.41 + 1.41 + 1.43 + 1.54 + 1.41 + 1.48 + 1.38 + 1.49 + 1.42 + 1.54 + 1.46 + 1.38 + 1.48) / 16 = 1.45s |
| Average UI Test Run Duration | 252.01s | <= 240.00s | Failed | average UI run duration = (205.58 + 246.47 + 252.21 + 225.95 + 227.99 + 202.72 + 232.93 + 225.22 + 237.24 + 218.97 + 312.16 + 238.19 + 286.68 + 304.65 + 301.31 + 313.94) / 16 = 252.01s |
| Average API Test Run Duration | 72.57s | <= 20.00s | Failed | average API run duration = (74.30 + 74.02 + 71.61 + 70.38 + 70.64 + 71.72 + 76.87 + 70.37 + 73.91 + 69.11 + 74.29 + 70.97 + 76.82 + 73.01 + 69.21 + 73.92) / 16 = 72.57s |
| Average Pipeline Duration | 388.81s | <= 240.00s | Failed | average pipeline duration = (256.00 + 276.00 + 302.00 + 627.00 + 277.00 + 286.00 + 629.00 + 270.00 + 1231.00 + 319.00 + 280.00 + 293.00 + 267.00 + 300.00 + 327.00 + 281.00) / 16 = 388.81s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-28 06:10](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30333648380) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 3.94s | 1.49s | 205.58s | 74.30s | 256.00s |
| [2026-07-28 08:26](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30342026504) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.51s | 1.48s | 246.47s | 74.02s | 276.00s |
| [2026-07-28 09:05](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30344609760) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.56s | 1.43s | 252.21s | 71.61s | 302.00s |
| [2026-07-28 11:06](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30352655198) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.17s | 1.41s | 225.95s | 70.38s | 627.00s |
| [2026-07-28 11:14](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30353623965) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.21s | 1.41s | 227.99s | 70.64s | 277.00s |
| [2026-07-28 11:26](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30354410022) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 3.87s | 1.43s | 202.72s | 71.72s | 286.00s |
| [2026-07-28 12:05](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30356644067) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.36s | 1.54s | 232.93s | 76.87s | 629.00s |
| [2026-07-28 12:42](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30359694450) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.16s | 1.41s | 225.22s | 70.37s | 270.00s |
| [2026-07-28 13:27](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30361897861) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.38s | 1.48s | 237.24s | 73.91s | 1231.00s |
| [2026-07-29 14:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30458351141) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.06s | 1.38s | 218.97s | 69.11s | 319.00s |
| [2026-07-29 23:24](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30499117530) | 77 | 76 / 98.70% | 0 / 0.00% | 1 / 1.30% | 0 / 0.00% | Unstable | 5.02s | 1.49s | 312.16s | 74.29s | 280.00s |
| [2026-07-30 15:05](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30554436296) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.35s | 1.42s | 238.19s | 70.97s | 293.00s |
| [2026-07-30 15:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30555853101) | 77 | 76 / 98.70% | 0 / 0.00% | 1 / 1.30% | 0 / 0.00% | Unstable | 4.72s | 1.54s | 286.68s | 76.82s | 267.00s |
| [2026-07-30 15:37](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30557103597) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 4.90s | 1.46s | 304.65s | 73.01s | 300.00s |
| [2026-07-30 15:45](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30557720656) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 4.81s | 1.38s | 301.31s | 69.21s | 327.00s |
| [2026-07-30 16:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30559182881) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 5.04s | 1.48s | 313.94s | 73.92s | 281.00s |

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-30 15:37 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 47.06s | <= 3.00s | Failed |
| 2026-07-30 15:37 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.74s | <= 3.00s | Failed |
| 2026-07-30 15:45 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.71s | <= 3.00s | Failed |
| 2026-07-30 16:02 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.04s | <= 3.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-30 15:22 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.20s | <= 0.20s | Failed |
| 2026-07-28 12:05 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.98s | <= 0.20s | Failed |
| 2026-07-28 08:26 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.09s | <= 0.20s | Failed |
| 2026-07-28 13:27 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 27.53s | <= 0.20s | Failed |

## Data completeness

- Completed workflow runs: **16**
- Published Allure reports used in test metrics: **16**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
