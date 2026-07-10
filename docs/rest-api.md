# REST API Automation Notes

Дата решения: 2026-06-30

## REST API документация

TeamCity предоставляет REST API для интеграций и скриптовой работы с сервером.

Базовая точка входа:

```text
http://<teamcity-host>:<port>/app/rest/server
```

Для локального стенда:

```text
http://localhost:8111/app/rest/server
```

## Как это использовать в автотестах

REST API проверки в этом проекте описываем через бизнес-сценарии TeamCity:

- bootstrap;
- создание первого администратора;
- авторизация agent;
- создание project;
- создание build configuration;
- запуск build;
- проверка build status.

## Важное замечание

До завершения первичного setup wizard TeamCity может быть еще не готов принимать обычные REST API запросы.

Сначала нужно пройти initial setup или реализовать CI bootstrap.

## Источники

- TeamCity REST API: https://www.jetbrains.com/help/teamcity/teamcity-rest-api.html
- TeamCity REST API Reference: https://www.jetbrains.com/help/teamcity/rest/teamcity-rest-api-documentation.html
