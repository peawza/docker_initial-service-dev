
# Portainer + Prometheus + Grafana + cAdvisor + Node Exporter (preprovisioned dashboards)

## Quick start
```bash
docker compose up -d
```

Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
cAdvisor: http://localhost:8081
Portainer: http://localhost:9000

If you don't see panels: ensure targets are UP at http://localhost:9090/targets and set Grafana time range to "Last 1 hour".
