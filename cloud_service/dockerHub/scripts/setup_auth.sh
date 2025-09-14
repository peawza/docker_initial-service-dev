#!/usr/bin/env bash
set -euo pipefail
mkdir -p auth registry
docker run --rm --entrypoint htpasswd httpd:2.4-alpine -Bbn demo demopass > auth/htpasswd
echo "✔ Created auth/htpasswd (user: demo / pass: demopass)"
