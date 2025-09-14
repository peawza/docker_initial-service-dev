#!/usr/bin/env bash
set -euo pipefail
URL=${1:-https://example.com}
OUT=${2:-example.pdf}
curl -s -X POST "http://localhost:3000/forms/chromium/convert/url"   -F "url=$URL"   -o "$OUT"
echo "Wrote $OUT"
