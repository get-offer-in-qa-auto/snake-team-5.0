# Test Environments Strategy

Дата решения: 2026-06-29

## Цель

Зафиксировать, какие окружения TeamCity используем для автотестов и почему.

## Основное окружение для автотестов

Для большинства автотестов используем:

```text
TeamCity Server + TeamCity Agent + internal HSQLDB
```

Это окружение подходит для быстрых проверок:

- старт TeamCity из Docker;
- первичная настройка;
- REST API;
- создание project;
- создание build configuration;
- запуск build;
- проверка build status;
- авторизация и подключение agent;
- базовые UI/API regression checks.

В этих тестах тип базы данных не является основной частью проверяемого поведения. Нам важнее быстро и стабильно поднять TeamCity и проверить основные пользовательские и API-сценарии.

## Почему не только internal HSQLDB

Internal HSQLDB подходит для локального изучения продукта, быстрых автотестов и evaluation-сценариев.

Но JetBrains не рекомендует internal HSQLDB для production. Для production-like стенда нужна внешняя база данных.

Поэтому нельзя ограничиться только internal DB, если мы хотим понимать, что TeamCity работает в конфигурации, близкой к реальной эксплуатации.

## Production-like окружение

Для отдельного CI job используем:

```text
TeamCity Server + TeamCity Agent + PostgreSQL
```

Это окружение запускается отдельным GitHub Actions workflow для более дорогой
проверки:

- nightly;
- вручную из Actions UI перед release или важными изменениями инфраструктуры.

Минимальные проверки для PostgreSQL-окружения:

- TeamCity стартует с внешней БД;
- TeamCity создает/использует схему в PostgreSQL;
- bootstrap проходит без ручного UI;
- REST API становится доступен;
- agent подключается и авторизуется;
- создается project;
- создается build configuration;
- запускается простой build;
- build завершается ожидаемым статусом.

## Почему PostgreSQL

PostgreSQL выбран как внешний database backend для production-like проверок, потому что:

- его удобно поднимать отдельным Docker-контейнером;
- он поддерживается TeamCity;
- он достаточно типовой для backend/CI-инфраструктуры;
- его проще автоматизировать в CI, чем Oracle или MS SQL Server.

## Важный вывод для CI

Если TeamCity каждый раз поднимается с пустым TeamCity Data Directory, он считает запуск первым и требует startup confirmation.

Это актуально и для internal HSQLDB, и для внешней PostgreSQL.

Поэтому в CI нужен bootstrap-процесс, который без ручного UI:

- подтверждает первый запуск;
- проходит первичную настройку;
- настраивает database backend;
- создает администратора или токен;
- дожидается готовности REST API;
- авторизует agent;
- запускает автотесты только после готовности стенда.

## Итоговое решение

Используем два уровня окружений:

```text
Fast CI:
  TeamCity Server + 2 full TeamCity Agents + internal HSQLDB

Production-like CI:
  TeamCity Server + 2 full TeamCity Agents + PostgreSQL
```

Fast CI нужен для быстрых проверок основной функциональности.

Production-like CI нужен, чтобы убедиться, что TeamCity работает с внешней БД и окружением, более близким к реальной эксплуатации.

## Database compatibility checks

TeamCity поддерживает несколько database backends, поэтому по-хорошему нужно проверять не только PostgreSQL.

Но полный набор автотестов на каждой базе запускать нерационально: такие прогоны будут долгими, более дорогими и менее стабильными из-за инфраструктуры.

Поэтому разделяем проверки:

```text
Full regression:
  internal HSQLDB
  PostgreSQL

Database compatibility smoke:
  MySQL
  MariaDB
  Microsoft SQL Server
  Oracle
```

Полный regression нужен на internal HSQLDB как быстрый основной контур и на PostgreSQL как основной production-like контур.

Для остальных внешних баз достаточно отдельного smoke-набора:

- TeamCity стартует с выбранной внешней БД;
- bootstrap проходит без ручного UI;
- TeamCity создает/использует database schema;
- REST API становится доступен;
- agent авторизуется;
- создается project;
- создается build configuration;
- запускается простой build;
- build завершается ожидаемым статусом.

Такой smoke не проверяет всю функциональность TeamCity заново. Его цель — поймать проблемы интеграции TeamCity с конкретным database backend.

## CI schedule

Рекомендуемая схема запусков:

```text
Pull Request:
  Fast CI на internal HSQLDB

Main / merge:
  Fast CI на internal HSQLDB
  Production-like CI на PostgreSQL

Nightly / scheduled:
  Full regression на PostgreSQL
  Database compatibility smoke на MySQL
  Database compatibility smoke на MariaDB
  Database compatibility smoke на Microsoft SQL Server
  Database compatibility smoke на Oracle
```

Oracle и Microsoft SQL Server могут быть тяжелее для локального и CI-запуска, поэтому их можно вынести в scheduled/manual job, если инфраструктура или лицензирование усложнят регулярный запуск.

Реализованный PostgreSQL workflow запускается ежедневно в `02:00 UTC`
(`05:00 МСК`) и вручную. Regression stage всегда использует 2 xdist worker и
2 отдельных TeamCity agent, а database adapter читает ту же PostgreSQL напрямую
в read-only транзакциях.

## Источники

- TeamCity External Database: https://www.jetbrains.com/help/teamcity/set-up-external-database.html
- Supported Platforms and Environments: https://www.jetbrains.com/help/teamcity/supported-platforms-and-environments.html
- TeamCity Data Directory: https://www.jetbrains.com/help/teamcity/teamcity-data-directory.html
