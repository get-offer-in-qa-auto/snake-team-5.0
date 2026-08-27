# TeamCity QA metrics report

Period: **7 UTC calendar days** (2026-08-21T00:00:00+00:00 — 2026-08-27T12:29:19+00:00).

Published runs: **0** · fully passed: **0** · final test results: **0** · flaky results: **0**.

## Quality gates and exact calculations

| Metric | Value | Target | Status | Calculation |
|---|---:|---:|---|---|
| Average Pass Rate | 0.00% | >= 98.00% | Failed | average pass rate = n/a |
| Average Fail Rate | 0.00% | <= 2.00% | OK | average fail rate = n/a |
| Average Broken Rate | 0.00% | <= 1.00% | OK | average broken rate = n/a |
| Flaky Rate | 0.00% | <= 2.00% | OK | flaky rate = 0 / 0 = 0.00% |
| Average UI Flaky Rate | 0.00% | <= 2.00% | OK | average UI flaky rate = n/a |
| Average API Flaky Rate | 0.00% | <= 2.00% | OK | average API flaky rate = n/a |
| Test Stability | 0.00% | >= 95.00% | Failed | stability = 0 / 0 = 0.00% |
| Average UI Test Duration | 0.00s | <= 12.00s | OK | average UI test duration = n/a |
| Average API Test Duration | 0.00s | <= 1.50s | OK | average API test duration = n/a |
| Total UI Test Time | 0.00s | <= 300.00s | OK | total UI test time = n/a |
| Average API Test Run Duration | 0.00s | <= 75.00s | OK | average API run duration = n/a |
| Average Pipeline Duration | 0.00s | <= 360.00s | OK | average pipeline duration = n/a |

## Every published run

| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|

## Cross-browser UI

| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Chromium | 0.00% | 0 | 0.00% | 0.00s | <= 11.00s | 0.00s | 0.00s | <= 100.00s | Failed |
| Firefox | 0.00% | 0 | 0.00% | 0.00s | <= 13.00s | 0.00s | 0.00s | <= 115.00s | Failed |
| WebKit | 0.00% | 0 | 0.00% | 0.00s | <= 14.00s | 0.00s | 0.00s | <= 120.00s | Failed |

Browser coverage: **0.00%** (0/0 UI scenarios executed in all three browsers).

## Slowest UI tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| — | No duration data | — | — | — |

## Slowest API tests

| Run | Test | Duration | Target | Status |
|---|---|---:|---:|---|
| — | No duration data | — | — | — |

## Data completeness

- Completed workflow runs: **0**
- Published Allure reports used in test metrics: **0**
- Workflow runs without a published report: **0**

Flaky counts use final Allure test cases explicitly marked `flaky`. Pass, fail and broken rates are calculated per run and then averaged without weighting, matching the reference report.
