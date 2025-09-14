# Dev Registry Sandbox (Mock ECR) — Docker Compose + UI + Basic Auth

Self-hosted Docker Registry (like Docker Hub/ECR) with a simple UI and basic auth.

## 1) Prerequisites
- Docker & Docker Compose
- (Optional) Admin rights to edit Docker daemon config for insecure registries when using HTTP.

## 2) Prepare auth
Create `auth/htpasswd` with user `demo` / pass `demopass`:
```bash
./scripts/setup_auth.sh
```

## 3) Start
```bash
docker compose up -d
# Registry: http://localhost:5000
# UI:       http://localhost:5001
```

## 4) Allow HTTP (insecure registry) if needed
If push fails due to HTTP, add to Docker daemon config:
- Linux: `/etc/docker/daemon.json`
- Docker Desktop: Settings → Docker Engine

Example:
```json
{
  "insecure-registries": ["localhost:5000"]
}
```
Then restart Docker.

## 5) Login / Push / Pull
```bash
docker login localhost:5000   # user: demo / pass: demopass
docker pull alpine:3.19
docker tag alpine:3.19 localhost:5000/demo/alpine:3.19
docker push localhost:5000/demo/alpine:3.19
docker pull localhost:5000/demo/alpine:3.19
```
Or run:
```bash
./scripts/test_push.sh
```

Open UI: http://localhost:5001

## 6) Cleanup
```bash
./scripts/cleanup.sh
```

## 7) Use in CI (mock ECR)
Replace your image name with:
```
localhost:5000/<repo>/<image>:<tag>
```
Workflow is the same as Docker Hub/ECR: `docker login` → `build` → `push`.
