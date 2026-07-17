# Database checks

## Зачем нужен отдельный слой

DB-проверка используется только там, где нужно независимо доказать persisted state, rollback или состояние записи после удаления. Тесты не обращаются к таблицам и не содержат SQL: они вызывают доменный метод `api_manager.database_steps`.

Текущие проверки покрывают создание, удаление и неуспешное создание основных сущностей:

- project — `PROJECT_MAPPING` и `PROJECT`; удаление подтверждается заполненным `DELETE_TIME`;
- build configuration — `BUILD_TYPE_MAPPING` и `BUILD_TYPE`; удаление подтверждается заполненным `DELETE_TIME`;
- user — `USERS`; создание подтверждается строкой с ожидаемым ID, удаление — отсутствием строки.

В каждом таком сценарии сначала проверяется публичное поведение через REST API, затем независимо проверяется состояние базы данных.

## Configuration persistence checks

Build Step не имеет отдельной записи в реляционной TeamCity database: он входит в
конфигурацию build configuration. Поэтому для него используется отдельный слой
`api_manager.configuration_steps`, а не `database_steps` и не marker `database`.

`TeamCityConfigurationClient` безопасно читает только XML build configuration из
Data Directory запущенного Docker-контейнера. Он проверяет runner по `id`, `name`,
`type` и параметрам, включая `script.content`. Перед чтением все части пути
валидируются; изменения не вносятся. Configuration checks ждут короткое время,
пока TeamCity применит XML после REST create/update/delete.

| Переменная | Значение |
| --- | --- |
| `TEAMCITY_CONFIG_CONTAINER` | имя TeamCity Server Docker-контейнера |
| `TEAMCITY_CONFIG_DATA_DIR` | Data Directory внутри контейнера, default `/data/teamcity_server/datadir` |
| `TEAMCITY_CONFIGURATION_TIMEOUT` | ожидание применения XML в секундах, default `20` |

Проверки помечаются `@pytest.mark.configuration` и `@pytest.mark.regression`.
Они одинаково работают на HSQLDB и PostgreSQL, поскольку оба стенда используют
TeamCity Data Directory для конфигурации.

## Единый интерфейс и два способа доступа

`DatabaseClient` скрывает способ получения данных. `DatabaseSteps` работает с его snapshot-интерфейсом, поэтому сценарий не меняется при смене backend.

### TeamCity backup adapter

Это режим по умолчанию для локальной и CI-среды со встроенной HSQLDB. Подключаться вторым процессом к работающей HSQLDB в file mode небезопасно: файл уже открыт TeamCity. Вместо этого клиент:

1. запускает database-only backup через TeamCity REST API;
2. ждёт завершения;
3. читает нормализованные таблицы из `database_dump/`;
4. удаляет временный архив.

TeamCity создаёт одинаковую структуру backup независимо от ОС и database backend, поэтому этот режим подходит и для внешней БД, если прямой сетевой доступ к ней закрыт. Для параллельного pytest запуск snapshot-ов защищён межпроцессной блокировкой: TeamCity выполняет один backup за раз.

Режиму нужны права администратора TeamCity и один из способов получить архив:

- общая директория в `TEAMCITY_DB_BACKUP_DIR`;
- Docker-контейнер в `TEAMCITY_DB_CONTAINER`, из которого архив копируется через `docker cp`.

В GitHub Actions bootstrap создает временного администратора со случайным
runtime-паролем, выпускает для него access token и передает тестам только Bearer
token через `TEAMCITY_ACCESS_TOKEN`. Пароль и token маскируются и не сохраняются
в artifacts. Перед regression выполняется `scripts.teamcity_database_preflight`:
он запускает реальный backup, копирует и читает snapshot, а затем удаляет архив.
Если доступ к Backup API сломан, pipeline останавливается до запуска всей suite.

### PostgreSQL adapter

Для production-like стенда можно читать PostgreSQL напрямую. Соединение открывается по `TEAMCITY_DB_DSN`, а транзакция переводится в read-only режим. Имена таблиц и колонок проходят проверку, значения передаются параметрами.

Отдельный GitHub Actions workflow поднимает TeamCity с PostgreSQL 17.5 как
основной database backend. Перед тестами preflight открывает read-only snapshot и
читает таблицу `USERS` напрямую, без TeamCity Backup API. JDBC driver 42.7.13
скачивается с официального pgJDBC сайта, проверяется по SHA-256 и помещается в
`<TeamCity Data Directory>/lib/jdbc`. Runtime password и DSN маскируются.

TeamCity хранит логические флаги в PostgreSQL как `smallint`, поэтому adapter
нормализует Python `bool` в `1/0` при параметризованных запросах.

## Конфигурация

| Переменная | Значение |
| --- | --- |
| `TEAMCITY_DB_ADAPTER` | `auto` (default), `backup` или `postgresql` |
| `TEAMCITY_DB_DSN` | DSN внешней PostgreSQL; в режиме `auto` включает прямой адаптер |
| `TEAMCITY_DB_BACKUP_DIR` | доступная тестам директория TeamCity backup |
| `TEAMCITY_DB_CONTAINER` | имя TeamCity Docker-контейнера; локально `teamcity-server-local`, в CI `teamcity-server-ci` |
| `TEAMCITY_DB_CONTAINER_BACKUP_DIR` | путь backup внутри контейнера |
| `TEAMCITY_DB_BACKUP_TIMEOUT` | ожидание snapshot-а в секундах, default `120` |
| `TEAMCITY_ACCESS_TOKEN` | временный Bearer token CI-администратора для REST API |
| `TEAMCITY_POSTGRES_PASSWORD` | временный пароль PostgreSQL-контейнера в CI |

Реальные логины, пароли и DSN должны передаваться через environment/CI secrets и не должны попадать в `resources/config.properties`.

## Добавление новой проверки

1. Добавить DAO с нужными полями в `src/main/api/database/dao.py`.
2. Добавить доменный метод в `DatabaseSteps`.
3. Читать только те таблицы, которые доказывают дополнительную гарантию по сравнению с REST response.
4. Оставить тест тонким: действие через API step, persisted-state assertion через database step.
5. Проверить запуск с `-n 0` и с обычным количеством xdist workers.

## Источники

- TeamCity external database: https://www.jetbrains.com/help/teamcity/set-up-external-database.html
- TeamCity backup REST API: https://www.jetbrains.com/help/teamcity/rest/manage-data-backup.html
- TeamCity backup format: https://www.jetbrains.com/help/teamcity/creating-backup-from-teamcity-web-ui.html
