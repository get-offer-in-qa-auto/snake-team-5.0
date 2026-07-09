# TeamCity Autotests

Локальный стенд TeamCity для подготовки и запуска автотестов.

## Оглавление

1. [Установка TeamCity локально](#1-установка-teamcity-локально)
2. [Версия TeamCity](#2-версия-teamcity)
3. [Важное для CI](#3-важное-для-ci)
4. [Локальные данные](#4-локальные-данные)
5. [Автотесты и Allure report](#5-автотесты-и-allure-report)
6. [Защита main](#6-защита-main)
7. [Документация проекта](#7-документация-проекта)

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
docker compose -f teamcity-local/compose.yaml up -d
```

Первый запуск может занять заметное время, потому что Docker скачивает образы TeamCity Server и TeamCity Agent.

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
docker compose -f teamcity-local/compose.yaml ps
```

Посмотреть логи сервера:

```bash
docker compose -f teamcity-local/compose.yaml logs -f teamcity-server
```

Ожидаемое состояние после первичной настройки:

- `teamcity-server-local` запущен;
- `teamcity-agent-local` запущен;
- UI доступен на `http://localhost:8111`;
- agent `local-agent-1` авторизован и виден как connected/idle.

### Остановка стенда

Остановить контейнеры, сохранив данные:

```bash
docker compose -f teamcity-local/compose.yaml stop
```

Остановить и удалить контейнеры, сохранив локальные директории:

```bash
docker compose -f teamcity-local/compose.yaml down
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

В CI стенд должен подниматься с нуля. При пустом `teamcity-local/teamcity-data/` TeamCity считает запуск первым и требует startup confirmation:

```text
Asking user to confirm first start with the predefined TeamCity Data Directory path
Startup confirmation is required
```

Поэтому для pipeline недостаточно просто выполнить:

```bash
docker compose -f teamcity-local/compose.yaml up -d
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

Директория `teamcity-local/` не коммитится в git, потому что это локальное состояние стенда, а не код проекта.

## 5. Автотесты и Allure report

Установить Python-зависимости:

```bash
python3 -m pip install -r requirements.txt
```

В `requirements.txt` уже входит `allure-pytest`, который позволяет pytest сохранять Allure results.

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

Чтобы старые ссылки не перезатирались, workflow хранит опубликованный Pages site в ветке `gh-pages` и добавляет каждый новый отчет в отдельный каталог. GitHub Actions artifacts хранятся 7 дней, а опубликованные Pages-отчеты остаются в `gh-pages`, пока их не удалить отдельной чисткой. Чтобы публикация работала, в настройках репозитория нужно включить GitHub Pages с source `GitHub Actions`. Ссылка на конкретный отчет появляется в workflow summary и в deployment environment `github-pages`.

## 6. Защита main

В GitHub для ветки `main` включена branch protection:

- прямой push в `main` запрещен;
- изменения должны попадать через pull request;
- правило применяется и к администраторам;
- force push и удаление `main` запрещены;
- перед merge должны быть решены все conversation threads.

## 7. Документация проекта

- Подробная инструкция по локальному стенду: `docs/local-teamcity-setup.md`
- Стратегия окружений для автотестов: `docs/test-environments.md`
- Группы автотестов: `docs/test-suites.md`
- Заметки по REST API и Swagger: `docs/rest-api.md`
- Решение по версии TeamCity: `docs/teamcity-version.md`
- Первый этап GitHub Actions pipeline: `docs/github-actions-pipeline.md`
- Тест-план автоматизации: `docs/Тест План по Автоматизации Тестирования - TeamCity.docx`
