#!/usr/bin/env bash
set -euo pipefail
docker compose down -v
echo "✔ Stopped and removed containers and volumes."
