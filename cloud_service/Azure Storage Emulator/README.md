# Azurite Sandbox (Azure Storage Emulator) — Docker Compose + Samples

Run Azure Storage **locally** using Azurite, and test with official Azure SDKs (Node.js & .NET).  
Use the same code in production — just switch the connection string.

---

## 1) Prerequisites
- Docker & Docker Compose
- Optional: Node.js 18+ (for the Node sample)
- Optional: .NET SDK 8.0+ (for the C# sample)
- Optional: Azure CLI (for quick tests)

## 2) Start Azurite
```bash
docker compose up -d
# Blob:  http://127.0.0.1:10000/devstoreaccount1
# Queue: http://127.0.0.1:10001/devstoreaccount1
# Table: http://127.0.0.1:10002/devstoreaccount1
```

## 3) Default Credentials (Azurite)
```text
AccountName = devstoreaccount1
AccountKey  = Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==
ConnectionString =
  DefaultEndpointsProtocol=http;
  AccountName=devstoreaccount1;
  AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;
  BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
  QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;
  TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;
```

> ⚠️ Azurite is **HTTP** by default. Do not expose it publicly.

---

## 4) Quick test with Azure CLI (optional)
```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
az storage container create -n test --connection-string "$AZURE_STORAGE_CONNECTION_STRING"
az storage blob upload --connection-string "$AZURE_STORAGE_CONNECTION_STRING" -f README.md -c test -n hello.txt
az storage blob list --connection-string "$AZURE_STORAGE_CONNECTION_STRING" -c test -o table
```

---

## 5) Node.js sample (`samples/node`)
### Run
```bash
cd samples/node
npm install
# Optionally override conn string:
# export AZURE_STORAGE_CONNECTION_STRING="..."
node index.js
```

### What it does
- Creates container `demo`
- Uploads a text blob `hello.txt`
- Reads it back and prints the content

---

## 6) .NET sample (`samples/dotnet`)
### Run
```bash
cd samples/dotnet
dotnet restore
dotnet run
```

### What it does
- Creates container `demo`
- Uploads a text blob `hello.txt`
- Reads it back and prints the content

---

## 7) Using in Production
- Replace the Azurite connection string with your Azure Storage account’s connection string from Azure Portal.
- No code changes required; official Azure SDKs use the same API.

---

## 8) Cleanup
```bash
docker compose down -v
```

Enjoy!
