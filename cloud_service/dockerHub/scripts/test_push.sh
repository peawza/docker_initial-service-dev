#!/usr/bin/env bash
set -euo pipefail

REGISTRY="localhost:5000"
USER="demo"
PASS="demopass"
IMAGE="alpine:3.19"
TARGET="${REGISTRY}/demo/alpine:3.19"

echo "Logging in to ${REGISTRY} ..."
echo "${PASS}" | docker login "${REGISTRY}" -u "${USER}" --password-stdin

echo "Pulling base image ${IMAGE} ..."
docker pull "${IMAGE}"

echo "Tagging -> ${TARGET} ..."
docker tag "${IMAGE}" "${TARGET}"

echo "Pushing -> ${TARGET} ..."
docker push "${TARGET}"

echo "Pulling back -> ${TARGET} ..."
docker pull "${TARGET}"

echo "✔ Push/Pull complete. Check UI at http://localhost:5001"
