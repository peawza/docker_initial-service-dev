using Azure.Storage.Blobs;
using System.Text;

string defaultConnStr = string.Join(";",
  "DefaultEndpointsProtocol=http",
  "AccountName=devstoreaccount1",
  "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
  "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1"
) + ";";

var connStr = Environment.GetEnvironmentVariable("AZURE_STORAGE_CONNECTION_STRING") ?? defaultConnStr;

var service = new BlobServiceClient(connStr);
var containerName = "demo";
var blobName = "hello.txt";

var container = service.GetBlobContainerClient(containerName);
await container.CreateIfNotExistsAsync();
Console.WriteLine($"✔ container ready: {containerName}");

var blob = container.GetBlobClient(blobName);
var data = new MemoryStream(Encoding.UTF8.GetBytes("Hello Azurite from .NET!"));
await blob.UploadAsync(data, overwrite: true);
Console.WriteLine($"✔ uploaded blob: {blobName}");

var download = await blob.DownloadContentAsync();
Console.WriteLine($"✔ downloaded content: {download.Value.Content.ToString()}");
