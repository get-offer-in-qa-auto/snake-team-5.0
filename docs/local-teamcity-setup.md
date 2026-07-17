# Local TeamCity Setup

Дата решения: 2026-06-29

## Цель

Поднять локальный стенд TeamCity для разработки и запуска автотестов.

Стенд состоит из двух контейнеров:

- `teamcity-server-local` — TeamCity Server;
- `teamcity-agent-local` — TeamCity Build Agent.

## Версия

Используем закрепленную версию:

```bash
jetbrains/teamcity-server:2026.1.1
jetbrains/teamcity-agent:2026.1.1
```

Причина выбора версии описана в документе `docs/teamcity-version.md`.

## Почему используем Docker Compose

Официальная инструкция JetBrains показывает запуск сервера через `docker run` с volume для data directory и logs.

Для локального тестового проекта удобнее использовать `ci/teamcity/local/compose.yaml`, потому что нам нужен не только сервер, но и build agent. Agent нужен, чтобы TeamCity мог реально запускать builds.

В `ci/teamcity/local/compose.yaml` используется полный образ `jetbrains/teamcity-agent:2026.1.1`. Он тяжелее, чем `jetbrains/teamcity-minimal-agent`, зато содержит больше готовых инструментов для сборок и лучше подходит как универсальный локальный agent.

Образ `jetbrains/teamcity-minimal-agent` содержит только TeamCity agent без дополнительных инструментов вроде VCS clients. Его можно использовать для простых smoke-проверок или как базу для своего кастомного agent image, но не как основной agent для полноценного тестирования TeamCity.

Решение: оставляем полный `teamcity-agent`, чтобы не ловить ошибки из-за отсутствующих инструментов внутри agent и проверять продукт ближе к реальному использованию.

## Локальные директории

При запуске локальные runtime-артефакты TeamCity будут созданы внутри директории `teamcity-local/`:

- `teamcity-local/teamcity-data/` — TeamCity Data Directory: настройки, проекты, build history, внутренняя база для локального стенда;
- `teamcity-local/teamcity-logs/` — логи сервера;
- `teamcity-local/teamcity-agent-conf/` — конфигурация agent и состояние авторизации;
- `teamcity-local/teamcity-agent-work/` — рабочая директория agent;
- `teamcity-local/teamcity-agent-system/` — кеши и системные файлы agent;
- `teamcity-local/teamcity-agent-temp/` — временные файлы agent;
- `teamcity-local/teamcity-agent-tools/` — инструменты agent;
- `teamcity-local/teamcity-agent-plugins/` — плагины agent.

Директория `teamcity-local/` добавлена в `.gitignore`, потому что это локальное состояние стенда, а не код проекта. Версионируемые compose-настройки лежат в `ci/teamcity/` вместе с остальной CI-инфраструктурой.

## Запуск

Проверить, что Docker установлен:

```bash
docker --version
docker compose version
```

Запустить TeamCity:

```bash
export TEAMCITY_SUPER_USER_TOKEN="$(openssl rand -hex 24)"
docker compose -f ci/teamcity/local/compose.yaml up -d
```

Первый запуск может быть долгим, потому что Docker скачивает образы сервера и agent. Последующие запуски будут быстрее, если образы уже есть локально.

Посмотреть логи сервера:

```bash
docker compose -f ci/teamcity/local/compose.yaml logs -f teamcity-server
```

## Super User token

Super User не имеет отдельного имени пользователя. Войти можно с пустым именем
пользователя и значением `TEAMCITY_SUPER_USER_TOKEN` как паролем. Compose
требует передать token при создании контейнера, но не хранит его в репозитории.

Перед созданием или пересозданием локального контейнера сгенерировать token:

```bash
export TEAMCITY_SUPER_USER_TOKEN="$(openssl rand -hex 24)"
```

Для CI используется отдельный краткоживущий `TEAMCITY_ACCESS_TOKEN`.

После старта открыть:

```text
http://localhost:8111
```

Если HTTP-проверка возвращает `503`, но в логах есть строка `Startup confirmation is required`, это ожидаемое состояние первого запуска. Нужно открыть UI в браузере и подтвердить запуск.

## Первичная настройка

При первом запуске нужно пройти setup wizard в браузере:

1. Открыть `http://localhost:8111`.
2. Подтвердить startup confirmation, если TeamCity попросит.
3. Выбрать/подтвердить внутреннюю базу данных `Internal database / HSQLDB` для локального стенда.
4. Принять лицензию.
5. Создать первого администратора.
6. Перейти в `Agents -> Unauthorized`.
7. Авторизовать agent `local-agent-1`.

После авторизации agent сможет запускать builds.

Для локального стенда выбираем именно `Internal database / HSQLDB`. Этот вариант не требует отдельного контейнера базы данных и подходит для изучения продукта, ручной проверки setup wizard и быстрых автотестов. Для production-like CI отдельно планируем PostgreSQL и compatibility smoke по другим поддерживаемым базам.

## Проверка, что стенд живой

Минимальная проверка после запуска:

```bash
docker compose -f ci/teamcity/local/compose.yaml ps
```

Ожидаем:

- `teamcity-server-local` запущен;
- `teamcity-agent-local` запущен;
- UI доступен на `http://localhost:8111`;
- после авторизации agent виден как connected/idle в TeamCity UI.

## Остановка

Остановить контейнеры, сохранив данные:

```bash
docker compose -f ci/teamcity/local/compose.yaml stop
```

Остановить и удалить контейнеры, сохранив локальные директории:

```bash
docker compose -f ci/teamcity/local/compose.yaml down
```

Для полного сброса локального стенда нужно удалить директорию `teamcity-local/`.

## Важные замечания

- Не используем тег `latest`, чтобы локальный стенд не менял версию без явного решения.
- Для agent внутри Docker Compose нельзя указывать `http://localhost:8111` как `SERVER_URL`, потому что `localhost` внутри контейнера указывает на сам контейнер agent.
- Поэтому agent подключается к серверу через имя сервиса: `http://teamcity-server:8111`.
- Для production JetBrains рекомендует внешнюю базу данных, но для локального тестового стенда достаточно внутренней базы в `teamcity-local/teamcity-data/`.

## Источники

- TeamCity Server Docker image: https://github.com/JetBrains/teamcity-docker-images/blob/master/dockerhub/teamcity-server/README.md
- TeamCity Agent Docker image: https://github.com/JetBrains/teamcity-docker-images/blob/master/dockerhub/teamcity-agent/README.md
- TeamCity Docker Compose samples: https://github.com/JetBrains/teamcity-docker-samples
