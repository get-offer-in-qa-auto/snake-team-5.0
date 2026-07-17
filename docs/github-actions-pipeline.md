# GitHub Actions Pipeline

Дата решения: 2026-07-06

## Текущий этап

PR pipeline поднимает один чистый TeamCity стенд и выполняет gated regression.
Проверки идут строго последовательно: database preflight, 6 smoke-тестов и затем
44 остальных regression-тестов. Если preflight или smoke падает, следующий этап
не запускается.

- поднять TeamCity Server;
- поднять TeamCity Agent;
- дождаться HTTP-ответа от `http://localhost:8111/login.html`;
- показать понятное readiness-состояние: `READY_LOGIN_PAGE`, `AUTH_REQUIRED` или `FIRST_START_REQUIRED`;
- проверить полный backup/copy/read/remove lifecycle через database preflight;
- запустить smoke gate через `pytest -m smoke -n 0`;
- после успешного smoke запустить `pytest -m "regression and not smoke" -n 0`;
- сохранить отдельные JUnit XML для smoke gate и оставшегося regression;
- сохранить Allure results;
- сразу собрать Allure HTML-report;
- опубликовать Allure HTML-report как GitHub Pages page с постоянной ссылкой для любого запуска;
- сохранить snapshot реальной страницы `login.html`, headers и readiness summary;
- сохранить Docker Compose status и logs как GitHub Actions artifacts;
- остановить контейнеры и удалить временные volumes после проверки.

Workflow:

```text
.github/workflows/teamcity-regression.yml
```

CI Docker Compose:

```text
ci/teamcity/compose.yaml
```

## PostgreSQL production-like regression

Отдельный workflow `.github/workflows/teamcity-postgresql-regression.yml`
поднимает один production-like стенд:

```text
TeamCity Server + TeamCity Agent + PostgreSQL 17.5
```

Он запускается:

- nightly в `02:00 UTC` (`05:00 МСК`);
- вручную через `Actions → TeamCity PostgreSQL Regression → Run workflow`.

Для ручного и scheduled запуска regression stage использует 4 xdist worker по
умолчанию. Smoke gate остаётся последовательным. Порядок выполнения:

```text
PostgreSQL health → TeamCity external DB bootstrap → read-only DB preflight
→ 6 smoke tests → 44 regression tests in 4 workers
```

Workflow не запускается на каждый PR и не публикует GitHub Pages. JUnit, Allure
и Docker/TeamCity logs сохраняются как artifacts на 7 дней. Database password и
DSN создаются внутри runner, маскируются и удаляются вместе с Docker volumes.

PostgreSQL compose-файл: `ci/teamcity-postgresql/compose.yaml`.

## Почему это отдельный этап

Для GitHub Actions нельзя считать успешным только наличие workflow-файла. Нам нужно сначала доказать, что чистый runner может скачать Docker images, поднять TeamCity Server и Agent, открыть порт `8111` и получить ответ от web-приложения.

На чистом data directory TeamCity останавливается на first-start confirmation и
setup wizard. Pipeline автоматически подтверждает новый стенд, выбирает internal
HSQLDB, принимает лицензию и создает временного CI-администратора.

Пароль администратора генерируется внутри runner и маскируется. После setup
bootstrap выпускает временный access token, и административные REST-запросы
выполняются через Bearer authentication. До pytest запускается реальный TeamCity
database backup preflight. TeamCity стартует один раз для всех трёх этапов.

## Что считается успехом сейчас

Pipeline считается успешным, если:

- Docker Compose успешно поднял containers;
- TeamCity web endpoint начал отвечать;
- database preflight подтвердил доступность Backup API и snapshot;
- все smoke-тесты прошли последовательно;
- остальные regression-тесты прошли последовательно;
- GitHub Step Summary показывает итоговое состояние TeamCity readiness;
- контейнеры не упали во время smoke-проверки;
- JUnit XML и логи собраны в artifacts.
- Allure results и готовый Allure HTML-report собраны в artifacts.
- для pull_request и workflow_dispatch запуска опубликована постоянная ссылка на конкретный Allure report.
- страница `login.html` сохранена в artifact `teamcity-login-page`.

## Debug artifacts

Runner GitHub Actions недоступен снаружи, поэтому открыть `localhost:8111` руками во время CI нельзя.

Чтобы посмотреть, что реально вернул TeamCity, pipeline сохраняет artifact:

```text
teamcity-login-page
```

Внутри:

- `login.html` — HTML страницы, которую вернул TeamCity;
- `headers.txt` — HTTP headers;
- `readiness.txt` — человекочитаемая классификация состояния.

Основной HSQLDB workflow можно запустить вручную через `Run workflow`. PR и
ручной HSQLDB regression используют фиксированный последовательный режим
`pytest_workers: 0`. PostgreSQL workflow по умолчанию использует 4 worker.

## Allure report

Pytest автоматически пишет Allure results в:

```text
artifacts/allure-results
```

Local composite action после pytest-прогона устанавливает Allure commandline, генерирует статический HTML-report и загружает два artifacts:

```text
teamcity-<suite>-allure-results
teamcity-<suite>-allure-report
```

Для отдельной smoke suite это будут:

```text
teamcity-smoke-allure-results
teamcity-smoke-allure-report
```

Gated PR pipeline публикует объединённый regression report, содержащий результаты
smoke gate и остальных regression-тестов:

```text
teamcity-regression-allure-results
teamcity-regression-allure-report
```

Перед генерацией HTML-report workflow восстанавливает Allure `history` из последнего опубликованного отчета той же suite/job. Для этого используется ветка `gh-pages`: `smoke` берет историю только из прошлых `reports/smoke/...`, а gated regression — только из прошлых `reports/regression/...`.

GitHub Actions artifacts хранятся 7 дней:

- TeamCity и Docker Compose logs;
- JUnit XML test results;
- Allure results;
- Allure HTML-report;
- TeamCity page snapshot;
- GitHub Pages artifact.

Кроме artifacts, workflow публикует готовый HTML-report в GitHub Pages для pull request и workflow_dispatch запусков.

URL индекса отчетов:

```text
https://get-offer-in-qa-auto.github.io/snake-team-5.0/
```

Каждый запуск получает постоянный URL:

```text
https://get-offer-in-qa-auto.github.io/snake-team-5.0/reports/<suite>/<run_id>-attempt-<attempt>/
```

У каждой suite/job есть отдельная группа отчетов:

```text
https://get-offer-in-qa-auto.github.io/snake-team-5.0/reports/smoke/
https://get-offer-in-qa-auto.github.io/snake-team-5.0/reports/regression/
```

Чтобы старые ссылки не перезатирались, workflow хранит опубликованный Pages site в ветке `gh-pages` и добавляет новый отчет в отдельный каталог. GitHub Actions artifacts хранятся 7 дней, а опубликованные Pages-отчеты остаются в `gh-pages`, пока их не удалить отдельной чисткой.

После деплоя ссылка на конкретный отчет также появляется в GitHub Actions workflow summary и в environment `github-pages`.

Для первого запуска нужно один раз включить Pages в настройках репозитория:

```text
Settings -> Pages -> Build and deployment -> Source: GitHub Actions
```

## Следующий этап

Bootstrap сервера, создание CI-администратора и Bearer token уже реализованы.
Следующим этапом остаются автоматическая авторизация agent, проверка состояния
`authorized + connected` и запуск минимального реального build.
