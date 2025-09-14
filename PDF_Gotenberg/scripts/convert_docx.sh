#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/file.docx [out.pdf]" >&2
  exit 1
fi
SRC="$1"
OUT="${2:-doc.pdf}"
curl -s -X POST "http://localhost:3000/forms/libreoffice/convert"   -F "files=@${SRC}"   -o "$OUT"
echo "Wrote $OUT"
