# GitHub Actions Pipeline

Дата решения: 2026-07-06

## Текущий этап

Первый CI-этап проверяет запуск TeamCity стенда и выполняет один минимальный smoke-test.

На текущем этапе pipeline запускает один минимальный pytest smoke-test с marker `smoke`: TeamCity login page должна открыть HTTP-соединение и вернуть ожидаемый ответ без авторизации.

- поднять TeamCity Server;
- поднять TeamCity Agent;
- дождаться HTTP-ответа от `http://localhost:8111/login.html`;
- показать понятное readiness-состояние: `READY_LOGIN_PAGE`, `AUTH_REQUIRED` или `FIRST_START_REQUIRED`;
- запустить smoke-test через `pytest -m smoke`;
- сохранить JUnit XML test result;
- сохранить snapshot реальной страницы `login.html`, headers и readiness summary;
- сохранить Docker Compose status и logs как GitHub Actions artifacts;
- остановить контейнеры и удалить временные volumes после проверки.

Workflow:

```text
.github/workflows/teamcity-start-smoke.yml
```

CI Docker Compose:

```text
ci/teamcity/compose.yaml
```

## Почему это отдельный этап

Для GitHub Actions нельзя считать успешным только наличие workflow-файла. Нам нужно сначала доказать, что чистый runner может скачать Docker images, поднять TeamCity Server и Agent, открыть порт `8111` и получить ответ от web-приложения.

На чистом data directory TeamCity может остановиться на first-start confirmation или setup wizard. До появления bootstrap-скрипта это ожидаемое промежуточное состояние.

## Что считается успехом сейчас

Pipeline считается успешным, если:

- Docker Compose успешно поднял containers;
- TeamCity web endpoint начал отвечать;
- pytest smoke-test подтвердил, что TeamCity login page открылась;
- GitHub Step Summary показывает итоговое состояние TeamCity readiness;
- контейнеры не упали во время smoke-проверки;
- JUnit XML и логи собраны в artifacts.
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

Workflow можно запустить вручную через `Run workflow`; дополнительных параметров для запуска нет.

## Следующий этап

Следующим шагом нужно добавить bootstrap:

- подтвердить first start без ручного UI;
- выбрать `Internal database / HSQLDB`;
- создать administrator user или access token;
- дождаться доступности REST API;
- авторизовать agent;
- проверить состояние `authorized + connected`.

После этого можно расширять pytest smoke/e2e tests.
