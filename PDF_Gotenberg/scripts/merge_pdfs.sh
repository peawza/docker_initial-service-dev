#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 one.pdf two.pdf [out.pdf]" >&2
  exit 1
fi
A="$1"
B="$2"
OUT="${3:-merged.pdf}"
curl -s -X POST "http://localhost:3000/forms/pdfengines/merge"   -F "files=@${A}"   -F "files=@${B}"   -o "$OUT"
echo "Wrote $OUT"
