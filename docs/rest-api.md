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

## Swagger

У TeamCity есть Swagger-описание REST API.

Официальная документация TeamCity указывает, что полный список поддерживаемых REST-запросов и параметров доступен в Swagger format по endpoint:

```text
/app/rest/swagger.json
```

Для локального стенда:

```text
http://localhost:8111/app/rest/swagger.json
```

## Как это использовать в автотестах

Swagger/OpenAPI-описание можно использовать для:

- изучения доступных endpoint;
- проверки, какие параметры поддерживает API;
- генерации API-клиента;
- генерации базовых contract checks;
- поиска endpoint для smoke/e2e сценариев.

Но Swagger не заменяет ручное проектирование тестов. Для TeamCity все равно нужно отдельно описывать бизнес-сценарии:

- bootstrap;
- создание первого администратора;
- авторизация agent;
- создание project;
- создание build configuration;
- запуск build;
- проверка build status.

## Важное замечание

До завершения первичного setup wizard endpoint `/app/rest/swagger.json` может быть недоступен, потому что TeamCity еще не готов принимать обычные REST API запросы.

Сначала нужно пройти initial setup или реализовать CI bootstrap.

## Источники

- TeamCity REST API: https://www.jetbrains.com/help/teamcity/teamcity-rest-api.html
- TeamCity REST API Reference: https://www.jetbrains.com/help/teamcity/rest/teamcity-rest-api-documentation.html
