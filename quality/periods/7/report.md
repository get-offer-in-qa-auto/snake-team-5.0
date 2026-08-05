# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-30T00:00:00+00:00 — 2026-08-05T06:05:01+00:00).

Published runs: **14** · fully passed: **12** · final test results: **1072** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 99.63% | >= 98.00% | OK | average pass rate = (100.00 + 98.70 + 96.10 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00) / 14 = 99.63% |
| Average Fail Rate | 0.28% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 3.90 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 14 = 0.28% |
| Average Broken Rate | 0.09% | <= 1.00% | OK | average broken rate = (0.00 + 1.30 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 14 = 0.09% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 1072 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 14 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 14 = 0.00% |
| Test Stability | 85.71% | >= 95.00% | Failed | stability = 12 / 14 = 85.71% |
| Average UI Test Duration | 11.02s | <= 12.00s | OK | average UI test duration = (11.34 + 10.62 + 11.28 + 11.16 + 11.63 + 10.94 + 11.30 + 11.03 + 11.32 + 10.35 + 11.37 + 9.89 + 10.59 + 11.41) / 14 = 11.02s |
| Average API Test Duration | 1.45s | <= 1.50s | OK | average API test duration = (1.42 + 1.54 + 1.46 + 1.38 + 1.48 + 1.43 + 1.47 + 1.43 + 1.48 + 1.41 + 1.45 + 1.46 + 1.45 + 1.44) / 14 = 1.45s |
| Total UI Test Time | 292.61s | <= 300.00s | OK | total UI test time = (238.19 + 286.68 + 304.65 + 301.31 + 313.94 + 295.48 + 305.08 + 297.68 + 305.66 + 279.58 + 307.08 + 267.03 + 285.96 + 308.15) / 14 = 292.61s |
| Average API Test Run Duration | 72.49s | <= 75.00s | OK | average API run duration = (70.97 + 76.82 + 73.01 + 69.21 + 73.92 + 71.67 + 73.46 + 71.53 + 73.81 + 70.26 + 72.52 + 73.08 + 72.67 + 71.89) / 14 = 72.49s |
| Average Pipeline Duration | 337.00s | <= 360.00s | OK | average pipeline duration = (293.00 + 267.00 + 300.00 + 327.00 + 281.00 + 278.00 + 607.00 + 288.00 + 302.00 + 281.00 + 276.00 + 634.00 + 300.00 + 284.00) / 14 = 337.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-30 15:05](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30554436296) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.34s | 1.42s | 238.19s | 70.97s | 293.00s |
| [2026-07-30 15:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30555853101) | 77 | 76 / 98.70% | 0 / 0.00% | 1 / 1.30% | 0 / 0.00% | Unstable | 10.62s | 1.54s | 286.68s | 76.82s | 267.00s |
| [2026-07-30 15:37](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30557103597) | 77 | 74 / 96.10% | 3 / 3.90% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.28s | 1.46s | 304.65s | 73.01s | 300.00s |
| [2026-07-30 15:45](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30557720656) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.16s | 1.38s | 301.31s | 69.21s | 327.00s |
| [2026-07-30 16:02](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30559182881) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.63s | 1.48s | 313.94s | 73.92s | 281.00s |
| [2026-07-31 11:04](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30625422697) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.94s | 1.43s | 295.48s | 71.67s | 278.00s |
| [2026-07-31 11:31](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30626642860) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.30s | 1.47s | 305.08s | 73.46s | 607.00s |
| [2026-07-31 11:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30628639314) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.03s | 1.43s | 297.68s | 71.53s | 288.00s |
| [2026-07-31 12:31](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30630523216) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.32s | 1.48s | 305.66s | 73.81s | 302.00s |
| [2026-07-31 13:01](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30632429614) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.35s | 1.41s | 279.58s | 70.26s | 281.00s |
| [2026-07-31 13:29](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30634259470) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.37s | 1.45s | 307.08s | 72.52s | 276.00s |
| [2026-07-31 14:30](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30638031001) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 9.89s | 1.46s | 267.03s | 73.08s | 634.00s |
| [2026-07-31 14:45](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30639512158) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 10.59s | 1.45s | 285.96s | 72.67s | 300.00s |
| [2026-07-31 14:58](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30640447362) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 11.41s | 1.44s | 308.15s | 71.89s | 284.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 99.19% | 1 | 0.00% | 9.93s | <= 11.00s | 23.30s | 97.63s | <= 100.00s | OK |
| Firefox | 98.39% | 2 | 0.00% | 10.89s | <= 13.00s | 22.64s | 111.50s | <= 115.00s | OK |
| WebKit | 99.19% | 1 | 0.00% | 12.23s | <= 14.00s | 33.33s | 116.91s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-30 15:37 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 47.06s | <= 12.00s | Failed |
| 2026-07-30 15:37 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.74s | <= 12.00s | Failed |
| 2026-07-30 15:45 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.71s | <= 12.00s | Failed |
| 2026-07-31 14:30 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 34.46s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-30 15:22 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.20s | <= 1.50s | Failed |
| 2026-07-31 12:31 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.24s | <= 1.50s | Failed |
| 2026-07-30 16:02 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 26.45s | <= 1.50s | Failed |
| 2026-07-31 14:30 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 26.36s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **14**
- Published Allure reports used in test metrics: **14**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
