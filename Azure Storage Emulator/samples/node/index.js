import { BlobServiceClient } from "@azure/storage-blob";

const defaultConnStr = [
  "DefaultEndpointsProtocol=http",
  "AccountName=devstoreaccount1",
  "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
  "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1"
].join(";") + ";";

const connStr = process.env.AZURE_STORAGE_CONNECTION_STRING || defaultConnStr;

const service = BlobServiceClient.fromConnectionString(connStr);
const containerName = "demo";
const blobName = "hello.txt";

async function main() {
  const container = service.getContainerClient(containerName);
  await container.createIfNotExists();
  console.log("✔ container ready:", containerName);

  const content = "Hello Azurite from Node!";
  const blockBlob = container.getBlockBlobClient(blobName);
  await blockBlob.upload(content, Buffer.byteLength(content), { overwrite: true });
  console.log("✔ uploaded blob:", blobName);

  const downloaded = await (await blockBlob.download()).blobBody;
  const text = await downloaded.text();
  console.log("✔ downloaded content:", text);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
