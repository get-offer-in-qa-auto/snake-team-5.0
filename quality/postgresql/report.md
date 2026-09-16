# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-09-10T00:00:00+00:00 — 2026-09-16T07:23:56+00:00).

Published runs: **7** · fully passed: **0** · final test results: **539** · flaky results: **8**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 98.14% | >= 98.00% | OK | average pass rate = (97.40 + 98.70 + 97.40 + 97.40 + 98.70 + 98.70 + 98.70) / 7 = 98.14% |
| Average Fail Rate | 1.67% | <= 2.00% | OK | average fail rate = (2.60 + 1.30 + 2.60 + 2.60 + 0.00 + 1.30 + 1.30) / 7 = 1.67% |
| Average Broken Rate | 0.19% | <= 1.00% | OK | average broken rate = (0.00 + 0.00 + 0.00 + 0.00 + 1.30 + 0.00 + 0.00) / 7 = 0.19% |
| Flaky Rate | 1.48% | <= 2.00% | OK | flaky rate = 8 / 539 = 1.48% |
| Average UI Flaky Rate | 4.23% | <= 2.00% | Failed | average UI flaky rate = (7.41 + 0.00 + 7.41 + 7.41 + 0.00 + 3.70 + 3.70) / 7 = 4.23% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00 + 0.00) / 7 = 0.00% |
| Test Stability | 0.00% | >= 95.00% | Failed | stability = 0 / 7 = 0.00% |
| Average UI Test Duration | 9.42s | <= 12.00s | OK | average UI test duration = (10.65 + 11.44 + 6.37 + 9.57 + 10.59 + 9.56 + 7.74) / 7 = 9.42s |
| Average API Test Duration | 1.45s | <= 1.50s | OK | average API test duration = (1.44 + 1.40 + 1.49 + 1.42 + 1.55 + 1.42 + 1.39) / 7 = 1.45s |
| Total UI Test Time | 254.27s | <= 300.00s | OK | total UI test time = (287.67 + 308.86 + 172.02 + 258.36 + 285.85 + 258.07 + 209.07) / 7 = 254.27s |
| Average API Test Run Duration | 72.28s | <= 75.00s | OK | average API run duration = (72.21 + 70.00 + 74.59 + 71.13 + 77.39 + 71.16 + 69.45) / 7 = 72.28s |
| Average Pipeline Duration | 305.29s | <= 360.00s | OK | average pipeline duration = (311.00 + 304.00 + 277.00 + 297.00 + 298.00 + 383.00 + 267.00) / 7 = 305.29s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-09-10 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34448004113) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 10.65s | 1.44s | 287.67s | 72.21s | 311.00s |
| [2026-09-11 07:08](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34572510288) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 0 / 0.00% | Unstable | 11.44s | 1.40s | 308.86s | 70.00s | 304.00s |
| [2026-09-12 07:00](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34679340989) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 6.37s | 1.49s | 172.02s | 74.59s | 277.00s |
| [2026-09-13 07:18](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34744643454) | 77 | 75 / 97.40% | 2 / 2.60% | 0 / 0.00% | 2 / 2.60% | Unstable | 9.57s | 1.42s | 258.36s | 71.13s | 297.00s |
| [2026-09-14 07:42](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34818612231) | 77 | 76 / 98.70% | 0 / 0.00% | 1 / 1.30% | 0 / 0.00% | Unstable | 10.59s | 1.55s | 285.85s | 77.39s | 298.00s |
| [2026-09-15 07:22](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/34940697002) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 9.56s | 1.42s | 258.07s | 71.16s | 383.00s |
| [2026-09-16 07:23](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/35067764436) | 77 | 76 / 98.70% | 1 / 1.30% | 0 / 0.00% | 1 / 1.30% | Unstable | 7.74s | 1.39s | 209.07s | 69.45s | 267.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 96.83% | 2 | 3.17% | 8.92s | <= 11.00s | 21.86s | 93.90s | <= 100.00s | Failed |
| Firefox | 92.06% | 5 | 7.94% | 9.40s | <= 13.00s | 22.84s | 100.41s | <= 115.00s | Failed |
| WebKit | 95.24% | 3 | 1.59% | 9.94s | <= 14.00s | 29.01s | 111.36s | <= 120.00s | Failed |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-14 07:42 | tests.ui.identity_access.test_user_creation#test_admin_can_create_user | 42.13s | <= 12.00s | Failed |
| 2026-09-11 07:08 | tests.ui.projects.test_project_creation#test_admin_can_create_project | 31.37s | <= 12.00s | Failed |
| 2026-09-10 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.57s | <= 12.00s | Failed |
| 2026-09-11 07:08 | tests.ui.build_steps.test_build_step_creation#test_admin_can_create_command_line_build_step | 29.19s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-09-16 07:23 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.81s | <= 1.50s | Failed |
| 2026-09-12 07:00 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.68s | <= 1.50s | Failed |
| 2026-09-14 07:42 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 30.45s | <= 1.50s | Failed |
| 2026-09-13 07:18 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 29.37s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **7**
- Published Allure reports used in test metrics: **7**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
