# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-07-25T00:00:00+00:00 — 2026-07-31T13:00:46+00:00).

Published runs: **2** · fully passed: **2** · final test results: **154** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 100.00% | >= 98.00% | OK | average pass rate = (100.00 + 100.00) / 2 = 100.00% |
| Average Fail Rate | 0.00% | <= 2.00% | OK | average fail rate = (0.00 + 0.00) / 2 = 0.00% |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = (0.00 + 0.00) / 2 = 0.00% |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 154 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = (0.00 + 0.00) / 2 = 0.00% |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = (0.00 + 0.00) / 2 = 0.00% |
| Test Stability | 100.00% | >= 95.00% | OK | stability = 2 / 2 = 100.00% |
| Average UI Test Duration | 8.45s | <= 12.00s | OK | average UI test duration = (8.45 + 8.46) / 2 = 8.45s |
| Average API Test Duration | 1.01s | <= 1.50s | OK | average API test duration = (1.07 + 0.94) / 2 = 1.01s |
| Total UI Test Time | 228.27s | <= 300.00s | OK | total UI test time = (228.17 + 228.38) / 2 = 228.27s |
| Average API Test Run Duration | 50.29s | <= 75.00s | OK | average API run duration = (53.62 + 46.97) / 2 = 50.29s |
| Average Pipeline Duration | 436.00s | <= 360.00s | Failed | average pipeline duration = (452.00 + 420.00) / 2 = 436.00s |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| [2026-07-31 12:52](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631704406) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.45s | 1.07s | 228.17s | 53.62s | 452.00s |
| [2026-07-31 12:59](https://github.com/get-offer-in-qa-auto/snake-team-5.0/actions/runs/30631712572) | 77 | 77 / 100.00% | 0 / 0.00% | 0 / 0.00% | 0 / 0.00% | Successful | 8.46s | 0.94s | 228.38s | 46.97s | 420.00s |

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 100.00% | 0 | 0.00% | 8.88s | <= 11.00s | 17.48s | 80.02s | <= 100.00s | OK |
| Firefox | 100.00% | 0 | 0.00% | 8.95s | <= 13.00s | 16.31s | 81.24s | <= 115.00s | OK |
| WebKit | 100.00% | 0 | 0.00% | 7.53s | <= 14.00s | 13.97s | 68.34s | <= 120.00s | OK |

Browser coverage: **100.00%** (9/9 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 12:59 | tests.ui.auth.test_login#test_admin_can_login | 17.51s | <= 12.00s | Failed |
| 2026-07-31 12:59 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 17.47s | <= 12.00s | Failed |
| 2026-07-31 12:59 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 16.45s | <= 12.00s | Failed |
| 2026-07-31 12:52 | tests.ui.identity_access.test_access_tokens#test_admin_can_create_access_token_for_user | 16.31s | <= 12.00s | Failed |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| 2026-07-31 12:52 | tests.api.build_execution.test_build_cancellation#test_running_build_can_be_cancelled | 13.49s | <= 1.50s | Failed |
| 2026-07-31 12:59 | tests.api.build_execution.test_build_runtime_parameters#test_build_run_with_runtime_parameter | 12.62s | <= 1.50s | Failed |
| 2026-07-31 12:52 | tests.api.build_execution.test_manual_build_run#test_successful_build_run | 12.60s | <= 1.50s | Failed |
| 2026-07-31 12:59 | tests.api.build_execution.test_manual_build_run#test_successful_build_run | 12.53s | <= 1.50s | Failed |

## Data completeness

- Completed workflow runs: **11**
- Published Allure reports used in test metrics: **2**
- Workflow runs without a published report: **9**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
