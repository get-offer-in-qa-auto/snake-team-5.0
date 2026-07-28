# Timeout configuration

Все runtime-таймауты читаются из переменных окружения. Если переменная не
задана, `TimeoutConfig` использует единое валидируемое значение по умолчанию.
Значения должны быть положительными конечными числами.

| Переменная окружения | Default | Назначение |
| --- | ---: | --- |
| `TEAMCITY_HTTP_CONNECT_TIMEOUT_SECONDS` | `5` | установка HTTP-соединения |
| `TEAMCITY_HTTP_READ_TIMEOUT_SECONDS` | `20` | ожидание HTTP-ответа |
| `TEAMCITY_BUILD_WAIT_TIMEOUT_SECONDS` | `90` | изменение состояния build |
| `TEAMCITY_BUILD_POLL_INTERVAL_SECONDS` | `1` | опрос build и agent status |
| `TEAMCITY_CONFIGURATION_TIMEOUT_SECONDS` | `20` | применение configuration XML |
| `TEAMCITY_CONFIGURATION_POLL_INTERVAL_SECONDS` | `0.25` | чтение configuration XML |
| `TEAMCITY_DB_BACKUP_TIMEOUT_SECONDS` | `120` | создание TeamCity backup |
| `TEAMCITY_DB_BACKUP_POLL_INTERVAL_SECONDS` | `0.5` | опрос backup status |
| `TEAMCITY_AGENT_WAIT_TIMEOUT_SECONDS` | `120` | готовность build agents |
| `TEAMCITY_AGENT_POLL_INTERVAL_SECONDS` | `1` | опрос build agents |
| `TEAMCITY_UI_EXPECT_TIMEOUT_MS` | `15000` | все Playwright assertions |

Например:

```bash
export TEAMCITY_HTTP_READ_TIMEOUT_SECONDS=30
export TEAMCITY_UI_EXPECT_TIMEOUT_MS=20000
```

HTTP использует отдельные connect/read значения. UI timeout устанавливается
один раз для всего Playwright `expect`, поэтому Page Objects не содержат
локальных значений.

Для обратной совместимости поддерживаются прежние переменные
`TEAMCITY_REQUEST_TIMEOUT`, `TEAMCITY_CONFIGURATION_TIMEOUT` и
`TEAMCITY_DB_BACKUP_TIMEOUT`. Новые имена имеют приоритет.
