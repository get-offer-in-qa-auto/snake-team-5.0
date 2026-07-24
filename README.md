# TeamCity Autotests

Локальный стенд TeamCity для подготовки и запуска автотестов.

## Оглавление

1. [Установка TeamCity локально](#1-установка-teamcity-локально)
2. [Версия TeamCity](#2-версия-teamcity)
3. [Важное для CI](#3-важное-для-ci)
4. [Локальные данные](#4-локальные-данные)
5. [Качество Python-кода](#5-качество-python-кода)
6. [Автотесты и Allure report](#6-автотесты-и-allure-report)
7. [Проверки базы данных](#7-проверки-базы-данных)
8. [Защита main](#8-защита-main)
9. [Документация проекта](#9-документация-проекта)

## 1. Установка TeamCity локально

Локальный стенд поднимается через Docker Compose и состоит из двух контейнеров:

- `teamcity-server-local` — TeamCity Server;
- `teamcity-agent-local` — TeamCity Build Agent.

### Что нужно установить

- Docker
- Docker Compose

Проверить, что Docker доступен:

```bash
docker --version
docker compose version
```

### Запуск стенда

Из корня проекта выполнить:

```bash
export TEAMCITY_SUPER_USER_TOKEN="$(openssl rand -hex 24)"
docker compose -f ci/teamcity/local/compose.yaml up -d
```

Первый запуск может занять заметное время, потому что Docker скачивает образы TeamCity Server и TeamCity Agent.

Docker Compose-настройки TeamCity лежат рядом с остальной CI-инфраструктурой:

```text
ci/teamcity/local/compose.yaml       # локальный стенд с bind-mount в teamcity-local/
ci/teamcity/hsqldb/compose.yaml      # основной CI-стенд с internal HSQLDB
ci/teamcity/postgresql/compose.yaml  # production-like CI-стенд с PostgreSQL
```

После запуска TeamCity будет доступен по адресу:

```text
http://localhost:8111
```

Если HTTP-проверка возвращает `503`, это не обязательно ошибка. При первом запуске TeamCity может ждать startup confirmation в браузере.

### Первичная настройка

При первом открытии TeamCity нужно:

1. Открыть `http://localhost:8111`.
2. Подтвердить startup confirmation, если TeamCity попросит.
3. Пройти setup wizard.
4. Выбрать внутреннюю базу данных: `Internal database / HSQLDB`.
5. Принять лицензию.
6. Создать администратора.
7. Перейти в `Agents -> Unauthorized`.
8. Авторизовать agent `local-agent-1`.

Локально используем `Internal database / HSQLDB`, потому что это самый простой вариант для изучения продукта и быстрых автотестов. Production-like проверки с внешними базами описаны в `docs/test-environments.md`.

### Проверка состояния

Проверить контейнеры:

```bash
docker compose -f ci/teamcity/local/compose.yaml ps
```

Посмотреть логи сервера:

```bash
docker compose -f ci/teamcity/local/compose.yaml logs -f teamcity-server
```

### Super User для локальной диагностики

Super User — не отдельный логин. Локальный compose требует случайный token,
переданный через `TEAMCITY_SUPER_USER_TOKEN`, и использует его как пароль с
пустым именем пользователя. Фиксированного token в compose-файлах нет.

Перед созданием или пересозданием контейнера сгенерировать token:

```bash
export TEAMCITY_SUPER_USER_TOKEN="$(openssl rand -hex 24)"
docker compose -f ci/teamcity/local/compose.yaml up -d
```

Для обычных CI-тестов используется отдельный временный `TEAMCITY_ACCESS_TOKEN`,
а не Super User token.

Ожидаемое состояние после первичной настройки:

- `teamcity-server-local` запущен;
- `teamcity-agent-local` запущен;
- UI доступен на `http://localhost:8111`;
- agent `local-agent-1` авторизован и виден как connected/idle.

### Остановка стенда

Остановить контейнеры, сохранив данные:

```bash
docker compose -f ci/teamcity/local/compose.yaml stop
```

Остановить и удалить контейнеры, сохранив локальные директории:

```bash
docker compose -f ci/teamcity/local/compose.yaml down
```

Для полного сброса локального стенда нужно удалить локальные директории TeamCity, перечисленные в разделе [Локальные данные](#4-локальные-данные).

## 2. Версия TeamCity

Для тестирования используем закрепленную версию:

```bash
jetbrains/teamcity-server:2026.1.1
jetbrains/teamcity-agent:2026.1.1
```

Не используем тег `latest`, чтобы локальный стенд не менял версию без явного решения в проекте.

Для agent используем полный образ `jetbrains/teamcity-agent`, а не `jetbrains/teamcity-minimal-agent`. Минимальный agent можно использовать для простых smoke-проверок или кастомного образа, но как основной локальный agent он слишком ограничен.

Подробное обоснование версии: `docs/teamcity-version.md`.

## 3. Важное для CI

В CI стенд должен подниматься с нуля. При пустом TeamCity Data Directory TeamCity считает запуск первым и требует startup confirmation:

```text
Asking user to confirm first start with the predefined TeamCity Data Directory path
Startup confirmation is required
```

Поэтому для pipeline недостаточно просто выполнить:

```bash
docker compose -f ci/teamcity/local/compose.yaml up -d
```

Для CI нужен отдельный bootstrap-процесс, который без ручного UI:

- подтверждает первый запуск;
- проходит первичную настройку;
- создает администратора или токен;
- дожидается готовности REST API;
- авторизует agent;
- только после этого запускает автотесты.

## 4. Локальные данные

TeamCity хранит локальное состояние внутри директории `teamcity-local/`:

- `teamcity-local/teamcity-data/`
- `teamcity-local/teamcity-logs/`
- `teamcity-local/teamcity-agent-conf/`
- `teamcity-local/teamcity-agent-work/`
- `teamcity-local/teamcity-agent-system/`
- `teamcity-local/teamcity-agent-temp/`
- `teamcity-local/teamcity-agent-tools/`
- `teamcity-local/teamcity-agent-plugins/`

Директория `teamcity-local/` не коммитится в git, потому что это локальное состояние стенда, а не код проекта. Версионируемые Docker Compose-настройки лежат рядом с остальной CI-инфраструктурой в `ci/teamcity/`.

## 5. Качество Python-кода

Перед запуском автотестов можно установить полный набор зависимостей для локальной разработки:

```bash
python3 -m pip install -r requirements-dev.txt
```

Проект использует три взаимодополняющих инструмента:

- **Ruff** проверяет стиль, неиспользуемые импорты, распространенные ошибки, порядок импортов и устаревшие конструкции Python. Он же форматирует код единообразно.
- **mypy** анализирует типы в `src/main`. Это помогает найти несовместимые аргументы и возвращаемые значения до запуска тестов; строгий режим будет включаться постепенно вместе с покрытием кода аннотациями.
- **pre-commit** запускает Ruff перед каждым локальным коммитом. Это убирает простые замечания ещё до code review, но не заменяет проверки в CI.

Один раз после установки зависимостей подключите hooks:

```bash
python3 -m pre_commit install
```

Полезные команды:

```bash
# Проверить и автоматически исправить lint-замечания, которые Ruff умеет исправлять безопасно
python3 -m ruff check . --fix

# Отформатировать код
python3 -m ruff format .

# Проверить форматирование без изменения файлов
python3 -m ruff format --check .

# Проверить статические типы production-кода
python3 -m mypy src/main

# Запустить все hooks вручную
python3 -m pre_commit run --all-files
```

В каждом pull request job **Code Quality** выполняет Ruff и mypy. Только после их успеха запускается трудоёмкий TeamCity Smoke в Docker, поэтому нарушение качества кода блокирует дальнейший PR-пайплайн. Pre-commit остаётся локальным механизмом перед коммитом и не дублирует CI-проверки.

## 6. Автотесты и Allure report

Установить Python-зависимости:

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium firefox webkit
```

В `requirements.txt` входят `allure-pytest` и `pytest-playwright`. Первый сохраняет
Allure results, второй предоставляет изолированные Playwright browser context и
`page` для UI-тестов. В CI каждый UI-тест запускается в Chromium, Firefox и WebKit.

Запустить только UI-тесты в тех же трёх вариантах, что и в CI:

```bash
python3 -m pytest -m ui \
  --browser chromium \
  --browser firefox \
  --browser webkit
```

Обычные UI-тесты получают `TCSESSIONID` через TeamCity REST API и добавляют cookie
в чистый browser context до первой навигации. Basic Authorization не передается
браузерным ресурсам. Отдельный login smoke проходит настоящую форму входа.

Credentials выбираются в порядке:

1. `TEAMCITY_UI_USERNAME` / `TEAMCITY_UI_PASSWORD`;
2. `TEAMCITY_USERNAME` / `TEAMCITY_PASSWORD`;
3. локальные `ADMIN_USERNAME` / `ADMIN_PASSWORD` из `resources/config.properties`.

Маркер `admin_session` авторизует администратора. Маркер
`user_session("fixture_name", ..., auth=0)` позволяет создать пользователей API-
фикстурами, сохранить их в `SessionStorage` и выбрать активного пользователя.
API-тесты без этих маркеров не запускают браузер.

`pytest-xdist` запускает тесты параллельно. В GitHub Actions один параметр
`parallelism` одновременно задаёт количество pytest workers и отдельных
TeamCity agents. Поддерживаются значения `1`, `2` и `3`; по умолчанию
используется `2`.

В ручном запуске значение выбирается в форме `Run workflow`. Pull request и
scheduled workflow читают repository variable `TEAMCITY_PARALLELISM`, а если
она не задана, используют `2`. Smoke и оставшийся regression выполняются с
одинаковой параллельностью. Локально количество workers задаётся так:

```bash
python3 -m pytest -m regression -n 2
```

Для локальной генерации HTML-отчета нужно отдельно установить Allure Report CLI, чтобы в терминале была доступна команда `allure`.

macOS:

```bash
brew install allure
allure --version
```

Windows, PowerShell:

```powershell
scoop install allure
allure --version
```

Для Windows-варианта через Scoop должны быть установлены Scoop, Java 8 или выше и переменная окружения `JAVA_HOME`.

Если Scoop не используется, Allure можно установить вручную из архива: скачать `allure-*.zip` из последнего GitHub release, распаковать архив и добавить папку `bin` в `Path`, затем открыть новый PowerShell и проверить:

```powershell
allure --version
```

Кроссплатформенная альтернатива через Node.js:

```bash
npm install -g allure-commandline
allure --version
```

Для npm-варианта нужны установленные Node.js, Java 8 или выше и переменная окружения `JAVA_HOME`.

Официальные инструкции Allure:

- https://allurereport.org/docs/v2/install-for-macos/
- https://allurereport.org/docs/v2/install-for-windows/
- https://allurereport.org/docs/v2/install-for-nodejs/

Запустить smoke-тесты и сразу собрать Allure HTML-report:

```bash
python3 scripts/run_tests_with_allure.py --marker smoke
```

В GitHub Actions Allure commandline устанавливается автоматически.

По умолчанию pytest сохраняет Allure results в:

```text
artifacts/allure-results
```

Готовый HTML-report сохраняется в:

```text
artifacts/allure-report
```

Для ручной генерации отчета после любого pytest-запуска можно выполнить:

```bash
allure generate artifacts/allure-results --clean -o artifacts/allure-report
```

В GitHub Actions local composite action собирает Allure report автоматически после pytest-прогона и загружает artifacts:

- `teamcity-<suite>-allure-results`
- `teamcity-<suite>-allure-report`
- `teamcity-<suite>-playwright`

При UI-падении screenshot прикладывается к Allure. Screenshot, trace и video,
сохраненные Playwright, находятся в `artifacts/playwright`; CI загружает этот
каталог отдельным artifact.

GitHub Actions artifacts хранятся 7 дней.

Перед генерацией HTML-отчета workflow восстанавливает Allure `history` из последнего опубликованного отчета той же suite/job. История `smoke` и `regression` хранится отдельно и не смешивается.

После любого GitHub Actions запуска workflow также публикует Allure report в GitHub Pages:

```text
https://get-offer-in-qa-auto.github.io/snake-team-5.0/
```

Корневая страница содержит индекс всех опубликованных отчетов. Каждый запуск получает постоянную ссылку:

```text
https://get-offer-in-qa-auto.github.io/snake-team-5.0/reports/<suite>/<run_id>-attempt-<attempt>/
```

Для каждой suite/job также есть своя группа отчетов:

```text
https://get-offer-in-qa-auto.github.io/snake-team-5.0/reports/smoke/
https://get-offer-in-qa-auto.github.io/snake-team-5.0/reports/regression/
```

Чтобы старые ссылки не перезатирались, workflow хранит опубликованный Pages site в ветке `gh-pages` и добавляет каждый новый отчет в отдельный каталог. GitHub Actions artifacts хранятся 7 дней, а опубликованные Pages-отчеты остаются в `gh-pages`, пока их не удалить отдельной чисткой. Чтобы публикация работала, в настройках репозитория нужно включить GitHub Pages с source `GitHub Actions`. Ссылка на конкретный отчет появляется в workflow summary и в deployment environment `github-pages`.

## 7. Проверки базы данных

DB-проверки доступны через `api_manager.database_steps` и не содержат SQL в тестах. По умолчанию адаптер сам выбирает режим:

- встроенная HSQLDB проверяется по консистентному database snapshot, который TeamCity создаёт штатным backup API;
- для внешней PostgreSQL задаётся `TEAMCITY_DB_DSN`, после чего клиент выполняет только read-only запросы напрямую;
- backup-режим также можно использовать с внешней БД, потому что формат TeamCity backup не зависит от database backend.

Пример запуска с внешней PostgreSQL:

```bash
export TEAMCITY_DB_ADAPTER=postgresql
export TEAMCITY_DB_DSN='postgresql://teamcity:<password>@db.example.test:5432/teamcity'
python3 -m pytest tests/api/projects/test_project_lifecycle.py::test_created_project_is_persisted_in_database
```

Пароли и реальные DSN не коммитятся. Подробная архитектура, параметры и ограничения описаны в `docs/database-checks.md`.

Production-like PostgreSQL regression запускается nightly в `05:00 МСК` и
вручную через workflow `TeamCity PostgreSQL Regression`. TeamCity и тестовый
adapter используют одну временную PostgreSQL database; после job containers и
volumes удаляются.

## 8. Защита main

В GitHub для ветки `main` включена branch protection:

- прямой push в `main` запрещен;
- изменения должны попадать через pull request;
- правило применяется и к администраторам;
- перед merge должны пройти required status checks: `Start TeamCity` и `Publish Allure report page`;
- force push и удаление `main` запрещены;
- перед merge должны быть решены все conversation threads.

## 9. Документация проекта

- Подробная инструкция по локальному стенду: `docs/local-teamcity-setup.md`
- Стратегия окружений для автотестов: `docs/test-environments.md`
- Группы автотестов: `docs/test-suites.md`
- Заметки по REST API: `docs/rest-api.md`
- Проверки persisted state в БД: `docs/database-checks.md`
- Решение по версии TeamCity: `docs/teamcity-version.md`
- Первый этап GitHub Actions pipeline: `docs/github-actions-pipeline.md`
- Тест-план автоматизации: `docs/Тест План по Автоматизации Тестирования - TeamCity.docx`
