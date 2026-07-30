# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-24T00:00:00+00:00 — 2026-07-30T15:11:45+00:00).

Published runs: **31** · fully passed: **26** · final test results: **1826** · flaky results: **1**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 97.94% | >= 98.00% | Failed | average pass rate = (100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 72.73 + 72.73 + 100.00 + 94.74 + 100.00 + 100.00 + 100.00 + 100.00 + 97.18 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 100.00 + 98.70 + 100.00) / 31 = 97.94% |
| Average Fail Rate | 0.26% | <= 2.00% | OK | average fail rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 5.26 + 0.00 + 0.00 + 0.00 + 0.00 + 2.82 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 31 = 0.26% |
| Average Broken Rate | 1.80% | <= 1.00% | Failed | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 27.27 + 27.27 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 1.30 + 0.00) / 31 = 1.80% |
| Flaky Rate | 0.05% | <= 2.00% | OK | flaky rate = 1 / 1826 = 0.05% |
| Average UI Flaky Rate | 0.15% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 4.76 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 31 = 0.15% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 31 = 0.00% |
| Test Stability | 83.87% | >= 95.00% | Failed | stability = 26 / 31 = 83.87% |
| Average Test Duration | 3.48s | <= 3.00s | Failed | average test duration = (1.69 + 1.34 + 1.76 + 1.64 + 1.31 + 1.53 + 1.30 + 1.96 + 2.04 + 1.63 + 10.76 + 11.28 + 1.74 + 1.81 + 1.73 + 2.69 + 2.51 + 3.64 + 3.97 + 3.94 + 4.51 + 4.56 + 4.17 + 4.21 + 3.87 + 4.36 + 4.16 + 4.38 + 4.06 + 5.02 + 4.35) / 31 = 3.48s |
| Average API Test Duration | 1.28s | <= 0.20s | Failed | average API test duration = (1.45 + 1.13 + 1.54 + 1.46 + 1.19 + 1.27 + 1.11 + 1.20 + 1.20 + 1.46 + 0.18 + 0.24 + 1.50 + 0.79 + 1.53 + 1.55 + 1.44 + 1.00 + 1.00 + 1.49 + 1.48 + 1.43 + 1.41 + 1.41 + 1.43 + 1.54 + 1.41 + 1.48 + 1.38 + 1.49 + 1.42) / 31 = 1.28s |
| Average UI Test Run Duration | 127.61s | <= 240.00s | OK | average UI run duration = (15.23 + 13.53 + 14.64 + 12.35 + 8.86 + 15.61 + 12.11 + 51.69 + 56.37 + 11.87 + 117.34 + 122.63 + 15.27 + 63.74 + 13.55 + 76.16 + 68.86 + 208.32 + 232.06 + 205.58 + 246.47 + 252.21 + 225.95 + 227.99 + 202.72 + 232.93 + 225.22 + 237.24 + 218.97 + 312.16 + 238.19) / 31 = 127.61s |
| Average API Test Run Duration | 63.29s | <= 20.00s | Failed | average API run duration = (72.60 + 56.30 + 77.14 + 72.78 + 59.29 + 63.75 + 55.38 + 59.85 + 60.16 + 73.10 + 1.06 + 1.43 + 75.12 + 39.70 + 76.52 + 77.25 + 71.88 + 50.25 + 50.12 + 74.30 + 74.02 + 71.61 + 70.38 + 70.64 + 71.72 + 76.87 + 70.37 + 73.91 + 69.11 + 74.29 + 70.97) / 31 = 63.29s |
| Average Pipeline Duration | 404.26s | <= 240.00s | Failed | average pipeline duration = (440.00 + 339.00 + 379.00 + 350.00 + 352.00 + 350.00 + 346.00 + 357.00 + 349.00 + 338.00 + 404.00 + 408.00 + 383.00 + 385.00 + 401.00 + 395.00 + 397.00 + 868.00 + 245.00 + 256.00 + 276.00 + 302.00 + 627.00 + 277.00 + 286.00 + 629.00 + 270.00 + 1231.00 + 319.00 + 280.00 + 293.00) / 31 = 404.26s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-24 09:33](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30082585395) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.69s | 1.45s | 15.23s | 72.60s | 440.00s |
| [2026-07-24 10:07](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30084772932) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.34s | 1.13s | 13.53s | 56.30s | 339.00s |
| [2026-07-24 10:14](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30085117270) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.76s | 1.54s | 14.64s | 77.14s | 379.00s |
| [2026-07-24 10:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30085414284) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.64s | 1.46s | 12.35s | 72.78s | 350.00s |
| [2026-07-24 10:42](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30086803816) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.31s | 1.19s | 8.86s | 59.29s | 352.00s |
| [2026-07-24 10:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30087781163) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.53s | 1.27s | 15.61s | 63.75s | 350.00s |
| [2026-07-24 11:27](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30089328640) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.30s | 1.11s | 12.11s | 55.38s | 346.00s |
| [2026-07-24 11:29](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30089396438) | 57 | 57 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.96s | 1.20s | 51.69s | 59.85s | 357.00s |
| [2026-07-24 11:37](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30089879921) | 57 | 57 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 2.04s | 1.20s | 56.37s | 60.16s | 349.00s |
| [2026-07-24 11:51](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30090697736) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.63s | 1.46s | 11.87s | 73.10s | 338.00s |
| [2026-07-24 12:57](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30094605662) | 11 | 8 / 72.73% | 0 / 0.00% | 3 / 27.27% | 0 / 0.00% | Unstable | 10.76s | 0.18s | 117.34s | 1.06s | 404.00s |
| [2026-07-24 13:06](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30095195912) | 11 | 8 / 72.73% | 0 / 0.00% | 3 / 27.27% | 0 / 0.00% | Unstable | 11.28s | 0.24s | 122.63s | 1.43s | 408.00s |
| [2026-07-24 13:21](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30096179296) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.74s | 1.50s | 15.27s | 75.12s | 383.00s |
| [2026-07-24 13:24](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30096365221) | 57 | 54 / 94.74% | 3 / 5.26% | 0 / 0.00% | 0 / 0.00% | Unstable | 1.81s | 0.79s | 63.74s | 39.70s | 385.00s |
| [2026-07-24 13:30](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30096801098) | 52 | 52 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 1.73s | 1.53s | 13.55s | 76.52s | 401.00s |
| [2026-07-24 13:37](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30097186199) | 57 | 57 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 2.69s | 1.55s | 76.16s | 77.25s | 395.00s |
| [2026-07-24 13:39](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30097313275) | 56 | 56 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 2.51s | 1.44s | 68.86s | 71.88s | 397.00s |
| [2026-07-24 14:30](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30099789286) | 71 | 71 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 3.64s | 1.00s | 208.32s | 50.25s | 868.00s |
| [2026-07-24 14:37](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30101435888) | 71 | 69 / 97.18% | 2 / 2.82% | 0 / 0.00% | 1 / 1.41% | Unstable | 3.97s | 1.00s | 232.06s | 50.12s | 245.00s |
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

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-24 13:06 | tests.ui.identity_access.test_user_creation#test_admin_can_create_user | 41.28s | <= 3.00s | Failed |
| 2026-07-24 12:57 | tests.ui.identity_access.test_user_creation#test_admin_can_create_user | 38.23s | <= 3.00s | Failed |
| 2026-07-24 13:06 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 32.66s | <= 3.00s | Failed |
| 2026-07-24 12:57 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 32.61s | <= 3.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-24 13:37 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.45s | <= 0.20s | Failed |
| 2026-07-24 10:14 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.99s | <= 0.20s | Failed |
| 2026-07-28 12:05 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.98s | <= 0.20s | Failed |
| 2026-07-24 13:30 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 28.83s | <= 0.20s | Failed |

## Data completeness

- Completed workflow runs: **32**
- Published Allure reports used in test metrics: **31**
- Workflow runs without a published report: **1**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
