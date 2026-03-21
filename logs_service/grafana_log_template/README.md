# Grafana Log Template v1 (Separated)

This is a fully separated stack from other logging setups.

## Components
- Loki (log store)
- Promtail (collect + parse logs)
- Grafana (visualization)
- API log simulator (structured schema)
- Linux log simulator

## Structured API schema
The API simulator writes these fields:
- Id
- Timestamp
- Level
- Message
- Request
- Response
- Path
- Method
- StatusCode
- RequestSizeKb
- ResponseSizeKb
- Exception

## Run

```bash
cd logs_service/grafana_log_template
docker compose up -d
```

## Access
- Grafana: http://localhost:3001
- Loki API: http://localhost:3101/ready

Login (from .env):
- user: admin
- password: admin123

## Auto provisioning
- Datasource: Loki
- Dashboard: API + Linux Logs Template

## Stop

```bash
docker compose down
```

## Notes
- Change credentials in .env before shared usage.
- Simulator writes files to simulator/logs and Promtail reads from there.
