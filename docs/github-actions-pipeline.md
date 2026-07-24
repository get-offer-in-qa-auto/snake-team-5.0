# GitHub Actions Pipeline

Дата решения: 2026-07-24

## Текущий этап

После Code Quality PR pipeline параллельно запускает четыре независимых jobs:

```text
TeamCity API regression
TeamCity UI · Chromium
TeamCity UI · Firefox
TeamCity UI · WebKit
```

Каждая job получает отдельный GitHub-hosted runner и собственный чистый TeamCity
стенд. Один параметр `parallelism` задаёт одинаковое количество TeamCity agents
и pytest workers внутри каждого стенда. Поддерживаются режимы `1`, `2` и `3`,
по умолчанию — `2`.

API job выполняет database preflight, 6 smoke API-тестов и после успешного gate
ещё 44 API regression-теста. Каждая UI job запускает 2 UI-сценария только в
своём браузере. Matrix использует `fail-fast: false`, поэтому падение одного
браузера не отменяет остальные и итоговый отчёт содержит полную диагностику.

- поднять отдельный TeamCity Server для API и каждого браузера;
- поднять в каждом стенде `parallelism` экземпляров TeamCity Agent;
- дождаться HTTP-ответа от `http://localhost:8111/login.html`;
- показать понятное readiness-состояние: `READY_LOGIN_PAGE`, `AUTH_REQUIRED` или `FIRST_START_REQUIRED`;
- проверить полный backup/copy/read/remove lifecycle в API job;
- запустить API smoke gate и оставшийся API regression без браузеров;
- запустить UI regression в отдельных Chromium, Firefox и WebKit jobs;
- сохранить отдельные JUnit, Playwright diagnostics, TeamCity logs и raw Allure
  results для каждой job;
- объединить четыре Allure result artifacts без перезаписи файлов;
- восстановить общую Allure history и один раз собрать HTML-report;
- опубликовать Allure HTML-report как GitHub Pages page с постоянной ссылкой для любого запуска;
- сохранить snapshot реальной страницы `login.html`, headers и readiness summary;
- остановить контейнеры и удалить временные volumes на каждом runner.

Workflow:

```text
.github/workflows/teamcity-regression.yml
```

CI Docker Compose:

```text
ci/teamcity/hsqldb/compose.yaml
```

Все TeamCity compose-настройки сгруппированы в одной директории:

```text
ci/teamcity/local/compose.yaml
ci/teamcity/hsqldb/compose.yaml
ci/teamcity/postgresql/compose.yaml
```

## PostgreSQL production-like regression

Отдельный workflow `.github/workflows/teamcity-postgresql-regression.yml`
поднимает один production-like стенд:

```text
TeamCity Server + 1–3 TeamCity Agents + PostgreSQL 17.5
```

Он запускается:

- nightly в `02:00 UTC` (`05:00 МСК`);
- вручную через `Actions → TeamCity PostgreSQL Regression → Run workflow`.

Для ручного и scheduled запуска один `parallelism` управляет и количеством
xdist workers, и количеством отдельных TeamCity agents. В ручном запуске
доступен выбор `1`, `2` или `3`; scheduled workflow читает repository variable
`TEAMCITY_PARALLELISM` и использует `2`, если она не задана. Порядок выполнения:

```text
PostgreSQL health → TeamCity external DB bootstrap → read-only DB preflight
→ 12 smoke test items → 44 regression tests with selected parallelism
```

Workflow не запускается на каждый PR и не публикует GitHub Pages. JUnit, Allure
и Docker/TeamCity logs сохраняются как artifacts на 7 дней. Database password и
DSN создаются внутри runner, маскируются и удаляются вместе с Docker volumes.

PostgreSQL compose-файл: `ci/teamcity/postgresql/compose.yaml`.

## Почему это отдельный этап

Для GitHub Actions нельзя считать успешным только наличие workflow-файла. Нам нужно сначала доказать, что чистый runner может скачать Docker images, поднять TeamCity Server и Agent, открыть порт `8111` и получить ответ от web-приложения.

На чистом data directory TeamCity останавливается на first-start confirmation и
setup wizard. Pipeline автоматически подтверждает новый стенд, выбирает internal
HSQLDB, принимает лицензию и создает временного CI-администратора.

Пароль администратора генерируется внутри каждого runner и маскируется. После
setup bootstrap выпускает временный access token, и административные
REST-запросы выполняются через Bearer authentication. Реальный TeamCity database
backup preflight выполняется только в API job. Docker-контейнеры и `localhost`
нельзя разделить между GitHub-hosted jobs, поэтому API и каждый браузер
используют собственный стенд.

## Что считается успехом сейчас

Pipeline считается успешным, если:

- Docker Compose успешно поднял containers во всех четырёх test jobs;
- каждый TeamCity web endpoint начал отвечать;
- database preflight подтвердил доступность Backup API и snapshot;
- API smoke gate и остальные API regression-тесты прошли;
- каждый UI-тест прошёл в Chromium, Firefox и WebKit;
- GitHub Step Summary показывает итоговое состояние TeamCity readiness;
- JUnit XML, Playwright diagnostics и логи каждой job собраны в artifacts;
- четыре raw Allure artifacts объединены в один отчёт;
- Allure results и готовый Allure HTML-report собраны в artifacts;
- для pull request и workflow_dispatch опубликована постоянная ссылка на отчёт;
- snapshot `login.html` сохранён отдельно для API и каждого браузера.

## Debug artifacts

Runner GitHub Actions недоступен снаружи, поэтому открыть `localhost:8111` руками во время CI нельзя.

Чтобы посмотреть, что реально вернул каждый TeamCity стенд, pipeline сохраняет:

```text
teamcity-regression-api-login-page
teamcity-regression-chromium-login-page
teamcity-regression-firefox-login-page
teamcity-regression-webkit-login-page
```

Внутри:

- `login.html` — HTML страницы, которую вернул TeamCity;
- `headers.txt` — HTTP headers;
- `readiness.txt` — человекочитаемая классификация состояния.

Основной HSQLDB и PostgreSQL workflow можно запустить вручную через
`Run workflow`, выбрав `parallelism` равным `1`, `2` или `3`. Это значение
одновременно масштабирует TeamCity Agent service и передаётся в `pytest -n`
внутри каждой test job. Для pull request и scheduled запуска используется
repository variable `TEAMCITY_PARALLELISM` с fallback `2`.

## Allure report

Pytest автоматически пишет raw Allure results внутри каждой test job в:

```text
artifacts/allure-results
```

Test jobs загружают отдельные raw artifacts:

```text
teamcity-regression-api-allure-results
teamcity-regression-chromium-allure-results
teamcity-regression-firefox-allure-results
teamcity-regression-webkit-allure-results
```

Финальная job `TeamCity regression` скачивает их в отдельные каталоги, один раз
проверяет наличие всех четырёх shards и копирует файлы в плоский
`allure-results` с защитой от совпадающих имён. Поэтому combined raw artifact
можно напрямую передать в `allure generate`. Затем workflow один раз
восстанавливает history и публикует результат под прежними стабильными именами:

```text
teamcity-regression-allure-results
teamcity-regression-allure-report
```

В Suites browser-варианты сгруппированы как `UI · Chromium`, `UI · Firefox` и
`UI · WebKit`, при этом Authentication/Projects и Login/Creation сохраняются
следующими уровнями. Pytest добавляет к имени теста browser-суффикс, Allure
показывает `browser_name` в Parameters и ведёт отдельную историю для каждого
варианта. API-тесты выполняются и отображаются один раз. В Environment и
Executor блоках отчёта видны topology запуска и ссылка на GitHub Actions run.

Перед генерацией HTML-report workflow восстанавливает Allure `history` из
последнего опубликованного `reports/regression/...` в ветке `gh-pages`.
Если хотя бы один shard отсутствует, частичный HTML сохраняется как
диагностический artifact, но не публикуется в canonical Pages history.

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
