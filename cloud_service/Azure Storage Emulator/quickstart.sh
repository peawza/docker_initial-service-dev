#!/usr/bin/env bash
set -e

echo "Starting Azurite..."
docker compose up -d

export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

echo "Creating container via Azure CLI (if installed)..."
if command -v az >/dev/null 2>&1; then
  az storage container create -n quickstart --connection-string "$AZURE_STORAGE_CONNECTION_STRING" >/dev/null
  echo "✔ container 'quickstart' created"
else
  echo "Azure CLI not found; skipping CLI quick test."
fi
