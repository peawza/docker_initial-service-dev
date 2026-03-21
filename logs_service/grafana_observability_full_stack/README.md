# Full Observability Stack (Root Cause Ready)

This stack is for programmers to investigate production-like issues by correlating:
- Logs (Loki + Promtail)
- Metrics (Prometheus)
- Traces (Tempo + OpenTelemetry Collector)
- Dashboards (Grafana)
- Alerts (Alertmanager)
- Infra metrics (node-exporter + cadvisor)

## Services
- `debug-api`: sample service with logs, metrics, and traces
- `loadgen`: traffic generator that creates normal/slow/error requests
- `grafana`, `prometheus`, `alertmanager`, `loki`, `promtail`, `tempo`, `otel-collector`
- `node-exporter`, `cadvisor`

## Run

```bash
cd logs_service/observability_full_stack
docker compose up -d --build
```

## Access
- Grafana: http://localhost:3003
- Prometheus: http://localhost:9091
- Alertmanager: http://localhost:9094
- Loki ready: http://localhost:3102/ready
- Tempo ready: http://localhost:3201/ready
- Sample API: http://localhost:8082/ok

Grafana login (from `.env`):
- user: `admin`
- password: `admin123`

## What You Can Investigate
1. Find spikes in 5xx errors in Grafana dashboard.
2. Check `Application Logs` panel for error messages and `trace_id`.
3. Jump from logs to traces via Tempo derived field.
4. Validate if latency and resource usage increased at same time.
5. Check active alerts in Alertmanager.

## Sample Alert Rules
- High 5xx ratio (>25% for 2m)
- High p95 latency (>1.2s for 3m)

## Stop

```bash
docker compose down
```

## Notes
- Change default passwords before sharing.
- This is a local-dev full stack for troubleshooting workflows.
