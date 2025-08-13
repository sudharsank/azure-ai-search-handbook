# C# Examples - Data Sources & Indexers

## Overview

This directory contains C# examples for working with Azure AI Search data sources and indexers using the `Azure.Search.Documents` SDK.

## Prerequisites

### .NET Environment
- .NET 6.0 or higher
- Visual Studio 2022 or VS Code with C# extension

### Required Packages
```xml
<PackageReference Include="Azure.Search.Documents" Version="11.4.0" />
<PackageReference Include="Azure.Identity" Version="1.10.0" />
<PackageReference Include="Microsoft.Extensions.Configuration" Version="7.0.0" />
<PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="7.0.0" />
```

### Azure Resources
- Azure AI Search service
- Data source (SQL Database, Storage Account, or Cosmos DB)
- Appropriate permissions configured

## Setup

### 1. Create Project
```bash
dotnet new console -n AzureSearchIndexerExamples
cd AzureSearchIndexerExamples
dotnet add package Azure.Search.Documents
dotnet add package Azure.Identity
dotnet add package Microsoft.Extensions.Configuration
dotnet add package Microsoft.Extensions.Configuration.Json
```

### 2. Configure Settings
Create an `appsettings.json` file:
```json
{
  "SearchService": {
    "ServiceName": "your-search-service",
    "ApiKey": "your-admin-api-key",
    "Endpoint": "https://your-search-service.search.windows.net"
  },
  "DataSources": {
    "SqlConnectionString": "Server=tcp:your-server.database.windows.net,1433;Database=your-db;User ID=your-user;Password=your-password;",
    "StorageConnectionString": "DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net",
    "CosmosConnectionString": "AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;Database=your-database"
  }
}
```

### 3. Verify Setup
Run the setup verification:
```bash
dotnet run --project VerifySetup.cs
```

## Examples

### 01 - Azure SQL Indexer
**File:** `01_AzureSqlIndexer.cs`

Demonstrates:
- Creating SQL data source with change tracking
- Configuring indexer for relational data
- Field mapping for complex structures
- Monitoring execution status

### 02 - Blob Storage Indexer
**File:** `02_BlobStorageIndexer.cs`

Demonstrates:
- Creating blob storage data source
- Processing various document formats
- Metadata extraction and content processing
- LastModified change detection

### 03 - Cosmos DB Indexer
**File:** `03_CosmosDbIndexer.cs`

Demonstrates:
- Creating Cosmos DB data source
- JSON document processing
- Change feed integration
- Partition key optimization

### 04 - Change Detection
**File:** `04_ChangeDetection.cs`

Demonstrates:
- Different change detection policies
- High water mark implementation
- Incremental update strategies
- Custom change detection logic

### 05 - Indexer Scheduling
**File:** `05_IndexerScheduling.cs`

Demonstrates:
- Configuring indexer schedules
- Automated execution patterns
- Schedule management APIs
- Monitoring scheduled runs

### 06 - Field Mappings
**File:** `06_FieldMappings.cs`

Demonstrates:
- Basic and complex field mappings
- Built-in mapping functions
- Output field mappings
- Data transformation techniques

### 07 - Error Handling
**File:** `07_ErrorHandling.cs`

Demonstrates:
- Robust error handling patterns
- Retry logic implementation
- Error threshold configuration
- Logging and monitoring

### 08 - Performance Monitoring & Optimization
**File:** `08_MonitoringOptimization.cs`

Demonstrates:
- Performance metrics collection and analysis
- Indexer health monitoring
- Optimization strategies implementation
- Batch size and configuration tuning
- Resource usage monitoring

## Running Examples

### Individual Examples
```bash
dotnet run --project 01_AzureSqlIndexer.cs
dotnet run --project 02_BlobStorageIndexer.cs
# ... etc
```

### All Examples
```bash
dotnet run --project RunAllExamples.cs
```

## Common Patterns

### Authentication
```csharp
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Identity;

// Using API key
var credential = new AzureKeyCredential(apiKey);
var indexerClient = new SearchIndexerClient(endpoint, credential);

// Using managed identity
var credential = new DefaultAzureCredential();
var indexerClient = new SearchIndexerClient(endpoint, credential);
```

### Error Handling
```csharp
try
{
    await indexerClient.CreateIndexerAsync(indexer);
    Console.WriteLine("Indexer created successfully");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Error creating indexer: {ex.Message}");
    // Handle specific error scenarios
}
```

### Monitoring
```csharp
public async Task MonitorIndexerExecutionAsync(string indexerName)
{
    var status = await indexerClient.GetIndexerStatusAsync(indexerName);
    Console.WriteLine($"Status: {status.Value.Status}");
    Console.WriteLine($"Items processed: {status.Value.LastResult?.ItemCount ?? 0}");
    Console.WriteLine($"Errors: {status.Value.LastResult?.Errors?.Count ?? 0}");
}
```

## Configuration Management

### Using Configuration
```csharp
using Microsoft.Extensions.Configuration;

var configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .Build();

var searchConfig = new SearchConfiguration
{
    Endpoint = new Uri(configuration["SearchService:Endpoint"]),
    ApiKey = configuration["SearchService:ApiKey"],
    SqlConnectionString = configuration["DataSources:SqlConnectionString"]
};
```

### Configuration Class
```csharp
public class SearchConfiguration
{
    public Uri Endpoint { get; set; }
    public string ApiKey { get; set; }
    public string SqlConnectionString { get; set; }
    
    public void Validate()
    {
        if (Endpoint == null || string.IsNullOrEmpty(ApiKey))
        {
            throw new InvalidOperationException("Missing required configuration");
        }
    }
}
```

## Testing

### Unit Tests
```bash
dotnet test
```

### Integration Tests
```bash
dotnet test --filter Category=Integration
```

### Test Coverage
```bash
dotnet test --collect:"XPlat Code Coverage"
```

## Debugging

### Enable Logging
```csharp
using Microsoft.Extensions.Logging;

var loggerFactory = LoggerFactory.Create(builder => builder.AddConsole());
var logger = loggerFactory.CreateLogger<Program>();

// Use logger throughout your application
logger.LogInformation("Creating indexer: {IndexerName}", indexerName);
```

### Debug Mode
```csharp
#if DEBUG
    Console.WriteLine($"Creating indexer: {indexerName}");
    Console.WriteLine($"Configuration: {JsonSerializer.Serialize(indexerDefinition)}");
#endif
```

## Best Practices

### Async/Await Usage
```csharp
// Use ConfigureAwait(false) for library code
public async Task<SearchIndexer> CreateIndexerAsync(SearchIndexer indexer)
{
    try
    {
        var result = await indexerClient.CreateIndexerAsync(indexer).ConfigureAwait(false);
        return result.Value;
    }
    catch (RequestFailedException ex)
    {
        logger.LogError(ex, "Failed to create indexer");
        throw;
    }
}
```

### Resource Management
```csharp
// Use using statements for proper disposal
using var indexerClient = new SearchIndexerClient(endpoint, credential);
await indexerClient.CreateIndexerAsync(indexer);
```

### Error Recovery
```csharp
public async Task<SearchIndexer> CreateIndexerWithRetryAsync(SearchIndexer indexer, int maxRetries = 3)
{
    for (int attempt = 1; attempt <= maxRetries; attempt++)
    {
        try
        {
            var result = await indexerClient.CreateIndexerAsync(indexer);
            return result.Value;
        }
        catch (RequestFailedException ex) when (attempt < maxRetries)
        {
            var delay = TimeSpan.FromSeconds(Math.Pow(2, attempt)); // Exponential backoff
            await Task.Delay(delay);
        }
    }
    
    throw new InvalidOperationException($"Failed to create indexer after {maxRetries} attempts");
}
```

## Troubleshooting

### Common Issues
1. **Authentication failures**: Check API keys and permissions
2. **Connection errors**: Verify network connectivity and firewall rules
3. **Schema mismatches**: Ensure field mappings are correct
4. **Performance issues**: Optimize batch sizes and queries

### Debug Tools
```csharp
public async Task DebugIndexerStatusAsync(string indexerName)
{
    var status = await indexerClient.GetIndexerStatusAsync(indexerName);
    
    Console.WriteLine($"Indexer: {indexerName}");
    Console.WriteLine($"Status: {status.Value.Status}");
    Console.WriteLine($"Last run: {status.Value.LastResult?.StartTime}");
    
    if (status.Value.LastResult?.Errors?.Any() == true)
    {
        Console.WriteLine("Errors:");
        foreach (var error in status.Value.LastResult.Errors)
        {
            Console.WriteLine($"  - {error.ErrorMessage}");
        }
    }
}
```

## Additional Resources

- [Azure.Search.Documents Documentation](https://docs.microsoft.com/dotnet/api/azure.search.documents)
- [.NET SDK Samples](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/search/Azure.Search.Documents/samples)
- [Azure AI Search REST API Reference](https://docs.microsoft.com/rest/api/searchservice/)

## Next Steps

1. Run the basic examples to understand core concepts
2. Modify examples for your specific data sources
3. Implement error handling and monitoring
4. Explore advanced features in intermediate modules