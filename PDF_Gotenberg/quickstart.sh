#!/usr/bin/env bash
set -e
chmod +x scripts/*.sh || true
echo "Starting Gotenberg..."
docker compose up -d
echo "Health:"
curl -s http://localhost:3000/health || true
echo
echo "Converting sample HTML to PDF..."
./scripts/convert_html.sh out.pdf
echo "Done. See out.pdf"
