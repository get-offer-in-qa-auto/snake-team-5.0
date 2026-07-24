# Test Suites

Дата решения: 2026-06-29

## Цель

Зафиксировать основные группы автотестов для TeamCity.

## Initial Setup / First Admin

Создание первого администратора выделяем в отдельную группу тестов.

Это не обычный login flow, а состояние продукта при чистом первом запуске. Эта группа важна для Docker, CI, bootstrap-сценариев и проверки воспроизводимого поднятия стенда с нуля.

Что проверяем:

- TeamCity стартует с пустым TeamCity Data Directory;
- появляется startup confirmation;
- можно подтвердить первый запуск;
- можно выбрать database backend;
- для локального стенда можно выбрать `Internal database / HSQLDB`;
- обязательные поля setup wizard нельзя пропустить;
- нельзя создать первого администратора с невалидными данными;
- можно создать первого администратора с валидными данными;
- после создания первого администратора можно войти в TeamCity;
- после завершения setup REST API становится доступен;
- после завершения setup wizard не появляется повторно при рестарте с сохраненным TeamCity Data Directory;
- agent появляется в `Agents -> Unauthorized`;
- первый администратор может авторизовать agent.

## Environment Bootstrap

Эта группа связана с `Initial Setup / First Admin`, но ориентирована на CI.

Цель — поднять TeamCity с нуля без ручного UI и подготовить стенд к запуску остальных автотестов.

Что проверяем:

- bootstrap проходит на пустом TeamCity Data Directory;
- bootstrap может настроить internal HSQLDB;
- bootstrap может настроить внешний database backend для production-like окружения;
- создается administrator user или access token;
- REST API становится доступен;
- agent авторизуется автоматически или подготовленным API-шагом;
- после bootstrap можно запускать остальные suites.

## Core REST API

Базовые проверки REST API:

- health/readiness endpoints;
- получение информации о сервере;
- создание project;
- создание build configuration;
- чтение build configuration;
- запуск build;
- получение build status;
- обработка ошибок авторизации;
- работа с access token.

## Smoke Suite

Smoke suite — короткий набор проверок, который быстро отвечает на вопрос: стенд
поднялся, базовые API-сценарии работают и пользователь может выполнить ключевые
действия через UI.

В текущем наборе к `smoke` относятся:

- `tests/api/projects/test_project_lifecycle.py::test_create_project`;
- `tests/api/build_configurations/test_build_configuration_lifecycle.py::test_create_build_configuration`;
- `tests/api/build_steps/test_build_step_lifecycle.py::test_create_build_step`;
- `tests/api/build_steps/test_build_step_lifecycle.py::test_delete_build_step`;
- `tests/api/identity_access/test_user_lifecycle.py::test_create_user`;
- `tests/api/identity_access/test_access_tokens.py::test_create_user_token`;
- `tests/ui/auth/test_login.py::test_admin_can_login`;
- `tests/ui/projects/test_project_creation.py::test_admin_can_create_project`.

Эти тесты также помечены `regression`, потому что smoke является частью полного regression-прогона.

В CI 6 API-сценариев выполняются по одному разу, а каждый из 2 UI-сценариев —
отдельно в Chromium, Firefox и WebKit. Поэтому 8 логических smoke-сценариев
отображаются как 12 test items. В Allure браузерные варианты различаются
суффиксом в имени и параметром `browser_name`, но остаются в одном отчёте.

UI login smoke проверяет настоящую форму входа и шапку TeamCity. Project smoke
получает browser session через REST API, создает Project через UI, проверяет его
в Favorites и удаляет через API-fixture. Остальные UI-тесты используют маркеры
`admin_session` или `user_session(..., auth=0)`, чтобы не повторять login flow.

## Regression Suite

Regression suite — полный набор текущих API, UI и smoke проверок.

К `regression` относятся все текущие тесты проекта:

- happy-path REST API сценарии;
- негативные проверки валидации;
- проверки авторизации;
- роли и права;
- удаление project, build configuration, user и token.

## Roles / Permissions

Проверки критичного функционала с учетом ролей и прав доступа.

На старте фиксируем минимальный RBAC-scope: есть administrator user с полными правами и есть пользователь/роль с ограниченными правами. Конкретную матрицу ролей TeamCity нужно уточнить на этапе тест-дизайна TODO.

Что проверяем:

- administrator может выполнять критичные действия: управлять проектами, build configurations, build run, agent authorization;
- ограниченный пользователь может выполнить только разрешенные действия;
- ограниченный пользователь не может выполнять admin-действия;
- ограниченный пользователь не может авторизовать agent;
- ограниченный пользователь не может менять project/build configuration без нужных прав;
- REST API возвращает корректный отказ для действий без прав;
- UI не показывает или блокирует действия, недоступные текущей роли.

## Agent Management

Проверки agent lifecycle:

- agent стартует и пытается зарегистрироваться;
- unauthorized agent виден в TeamCity;
- admin может авторизовать agent;
- authorized agent становится connected/idle;
- agent может взять build;
- agent корректно отображается после рестарта.

## Build Execution

Проверки запуска сборок:

- создание простой build configuration;
- запуск build вручную;
- успешное завершение build;
- failed build при ошибочной команде;
- build logs доступны;
- build status корректно возвращается через UI/API.

MVP реализуется marker-ом `build_execution`: success, failure, runtime parameter
и отмена running build. HSQLDB и PostgreSQL CI используют единый параметр
`parallelism`: при значении `1`, `2` или `3` запускается столько же xdist
workers и отдельных TeamCity agents.

## Database Compatibility

Проверки совместимости с базами данных описаны отдельно в `docs/test-environments.md`.

Цель этой группы — не прогонять весь regression на каждой БД, а проверить, что TeamCity стартует и выполняет базовый сценарий с каждым поддерживаемым database backend.
