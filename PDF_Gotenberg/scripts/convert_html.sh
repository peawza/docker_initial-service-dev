#!/usr/bin/env bash
set -euo pipefail
OUT=${1:-out.pdf}
curl -s -X POST "http://localhost:3000/forms/chromium/convert/html"   -F "files=@examples/index.html"   -F "emulatedMediaType=screen"   -F "marginTop=10" -F "marginBottom=10" -F "marginLeft=10" -F "marginRight=10"   -o "$OUT"
echo "Wrote $OUT"
