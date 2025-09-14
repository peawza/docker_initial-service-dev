#!/usr/bin/env bash
set -euo pipefail
./scripts/setup_auth.sh
docker compose up -d
echo "Registry: http://localhost:5000"
echo "UI:       http://localhost:5001"
