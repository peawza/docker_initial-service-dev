#!/bin/sh
set -eu

echo "[kibana-bootstrap] Waiting for Kibana..."
until curl -s -o /dev/null -w "%{http_code}" "http://kibana:5601/login" | grep -q "200"; do
  sleep 5
done

echo "[kibana-bootstrap] Creating Data View fluentd-template-*"
curl -s -u "elastic:${ELASTIC_PASSWORD}" -X POST "http://kibana:5601/api/data_views/data_view" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{"data_view":{"name":"fluentd-template","title":"fluentd-template-*","timeFieldName":"@timestamp"}}' >/dev/null || true

echo "[kibana-bootstrap] Creating saved query: Linux System Logs"
curl -s -u "elastic:${ELASTIC_PASSWORD}" -X POST "http://kibana:5601/api/saved_objects/query/linux-system-logs" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{"attributes":{"title":"Linux System Logs","description":"Template query for Linux/system logs","query":{"language":"kuery","query":"tag : \"docker.linux.system\" or message : \"*kernel*\" or message : \"*systemd*\""},"filters":[]}}' >/dev/null || true

echo "[kibana-bootstrap] Creating saved query: API Calls"
curl -s -u "elastic:${ELASTIC_PASSWORD}" -X POST "http://kibana:5601/api/saved_objects/query/api-calls" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{"attributes":{"title":"API Calls","description":"Template query for API request logs","query":{"language":"kuery","query":"tag : \"docker.api.calls\" and Method:* and Path:* and StatusCode:*"},"filters":[]}}' >/dev/null || true

echo "[kibana-bootstrap] Creating saved query: API Errors (Structured)"
curl -s -u "elastic:${ELASTIC_PASSWORD}" -X POST "http://kibana:5601/api/saved_objects/query/api-errors-structured" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{"attributes":{"title":"API Errors (Structured)","description":"StatusCode >= 400 and Exception for structured API logs","query":{"language":"kuery","query":"tag : \"docker.api.calls\" and (StatusCode >= 400 or Exception : *)"},"filters":[]}}' >/dev/null || true

echo "[kibana-bootstrap] Done"
