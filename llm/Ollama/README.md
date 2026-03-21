# 🚀 Ollama + Open WebUI (Docker Compose)

This project runs **Ollama + Open WebUI** with GPU support (tested on
RTX 3070 8GB).

------------------------------------------------------------------------

## 📦 Requirements

-   Windows 10/11
-   WSL2 enabled
-   Docker Desktop (WSL2 backend)
-   Latest NVIDIA Driver
-   RTX 3070 (8GB) or compatible GPU

Test GPU inside Docker:

``` bash
docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
```

If RTX 3070 appears → GPU is ready ✅

------------------------------------------------------------------------

## 🛠 Setup

### 1️⃣ Files required

-   docker-compose.yml
-   README.md

### 2️⃣ Start services

``` bash
docker compose up -d
```

------------------------------------------------------------------------

## 🌐 Access Web UI

Open browser:

    http://localhost:3000

------------------------------------------------------------------------

## 📥 Download Recommended Models

For RTX 3070:

``` bash
docker exec -it ollama ollama pull qwen2.5:7b
```

Optional (more reasoning, slower):

``` bash
docker exec -it ollama ollama pull qwen2.5:14b
```

------------------------------------------------------------------------

## ▶️ Run Model via CLI

``` bash
docker exec -it ollama ollama run qwen2.5:7b
```


``` bash
docker exec -it ollama ollama pull nomic-embed-text
```
------------------------------------------------------------------------

## 🧠 Verify GPU Usage

Open another terminal:

``` bash
nvidia-smi -l 1
```

If VRAM usage increases (5--7GB), GPU is being used 🔥

------------------------------------------------------------------------

## 📂 Model Storage

Models are stored in Docker volume:

    ollama:/root/.ollama

Remove models:

``` bash
docker compose down -v
```

------------------------------------------------------------------------

## 🎯 Recommended Models

  Model         Use Case
  ------------- -----------------------------
  qwen2.5:7b    Coding / Dev / Log Analysis
  llama3:8b     Chat Assistant
  qwen2.5:14b   Deep Reasoning

------------------------------------------------------------------------

## 🧹 Stop Services

``` bash
docker compose down
```

------------------------------------------------------------------------

Happy Testing 🚀




docker exec -it postgres-pgvector psql -U postgres -d vectordb
