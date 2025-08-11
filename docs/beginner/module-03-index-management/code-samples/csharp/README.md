# C# Code Samples - Module 3: Index Management

This directory contains focused C# examples for index management operations in Azure AI Search using the .NET SDK. Each file demonstrates a specific aspect of index management with clear, production-ready code suitable for enterprise applications.

## 📁 File Structure

```
csharp/
├── README.md                           # This file
├── 01_CreateBasicIndex.cs             # Basic index creation
├── 02_SchemaDesign.cs                 # Advanced schema design patterns
├── 03_DataIngestion.cs                # Document upload strategies
├── 04_IndexOperations.cs              # Index management operations
├── 05_PerformanceOptimization.cs      # Performance tuning techniques
└── 06_ErrorHandling.cs                # Robust error handling patterns
```

## 🚀 Quick Start

### Prerequisites

1. **Development Environment**:
   ```bash
   # .NET 6.0 or later required
   dotnet --version
   
   # Create new console project (if needed)
   dotnet new console -n IndexManagementExamples
   cd IndexManagementExamples
   ```

2. **Package Installation**:
   ```bash
   # Add Azure Search package
   dotnet add package Azure.Search.Documents
   
   # Add configuration support
   dotnet add package Microsoft.Extensions.Configuration
   dotnet add package Microsoft.Extensions.Configuration.EnvironmentVariables
   ```

3. **Environment Configuration**:
   ```bash
   # Set environment variables
   export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
   export AZURE_SEARCH_ADMIN_KEY="your-admin-api-key"
   ```

### Running Examples

```bash
# Compile and run basic index creation
dotnet run 01_CreateBasicIndex.cs

# Run advanced schema design
dotnet run 02_SchemaDesign.cs

# Run data ingestion examples
dotnet run 03_DataIngestion.cs

# Continue with other examples...
```

## 📚 Example Categories

### 1. Basic Index Creation (`01_CreateBasicIndex.cs`)
**Focus**: Fundamental index creation concepts in C#

**What you'll learn**:
- Creating SearchIndexClient with proper authentication
- Defining field types using SearchField
- Index creation and validation patterns
- Basic error handling in C#

**Key concepts**:
```csharp
// Client creation
var indexClient = new SearchIndexClient(
    new Uri(endpoint), 
    new AzureKeyCredential(adminKey)
);

// Field definition
var fields = new[]
{
    new SearchField("id", SearchFieldDataType.String) { IsKey = true },
    new SearchField("title", SearchFieldDataType.String) { IsSearchable = true }
};

// Index creation
var index = new SearchIndex("my-index", fields);
await indexClient.CreateIndexAsync(index);
```

### 2. Schema Design (`02_SchemaDesign.cs`)
**Focus**: Advanced schema design patterns and C# best practices

**What you'll learn**:
- Complex field type definitions
- Attribute optimization strategies
- Nested object handling with ComplexField
- Schema validation and testing

**Key concepts**:
```csharp
// Complex field with nested properties
var authorField = new ComplexField("author")
{
    Fields =
    {
        new SearchField("name", SearchFieldDataType.String),
        new SearchField("email", SearchFieldDataType.String)
    }
};

// Collection field
var tagsField = new SearchField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String))
{
    IsFilterable = true,
    IsFacetable = true
};
```

### 3. Data Ingestion (`03_DataIngestion.cs`)
**Focus**: Efficient document upload and management strategies

**What you'll learn**:
- Batch document operations using IndexDocumentsBatch
- Async/await patterns for performance
- Large dataset processing techniques
- Progress tracking and monitoring

**Key concepts**:
```csharp
// Batch upload
var batch = IndexDocumentsBatch.Create(
    documents.Select(doc => IndexDocumentsAction.Upload(doc)).ToArray()
);

var response = await searchClient.IndexDocumentsAsync(batch);

// Check results
foreach (var result in response.Value.Results)
{
    if (!result.Succeeded)
    {
        Console.WriteLine($"Failed: {result.Key} - {result.ErrorMessage}");
    }
}
```

### 4. Index Operations (`04_IndexOperations.cs`)
**Focus**: Index lifecycle management operations

**What you'll learn**:
- Listing and inspecting indexes
- Getting index statistics and metrics
- Schema updates and versioning
- Index deletion with safety checks

**Key concepts**:
```csharp
// List indexes
await foreach (var index in indexClient.GetIndexesAsync())
{
    Console.WriteLine($"Index: {index.Name} ({index.Fields.Count} fields)");
}

// Get index details
var indexResponse = await indexClient.GetIndexAsync("my-index");
var index = indexResponse.Value;

// Update schema
var updatedIndex = new SearchIndex(index.Name, newFields);
await indexClient.CreateOrUpdateIndexAsync(updatedIndex);
```

### 5. Performance Optimization (`05_PerformanceOptimization.cs`)
**Focus**: Performance tuning and optimization techniques

**What you'll learn**:
- Optimal batch sizing strategies
- Parallel processing with Task.Run
- Memory management best practices
- Performance monitoring and metrics

**Key concepts**:
```csharp
// Custom analyzer
var customAnalyzer = new CustomAnalyzer("my_analyzer", "standard")
{
    TokenFilters = { "lowercase", "stop" }
};

// Scoring profile
var scoringProfile = new ScoringProfile("boost_recent")
{
    TextWeights = new TextWeights(new Dictionary<string, double>
    {
        { "title", 2.0 },
        { "content", 1.0 }
    })
};

var index = new SearchIndex("my-index", fields)
{
    Analyzers = { customAnalyzer },
    ScoringProfiles = { scoringProfile }
};
```

### 6. Error Handling (`06_ErrorHandling.cs`)
**Focus**: Robust error handling and recovery patterns

**What you'll learn**:
- Exception handling with RequestFailedException
- Retry policies with Polly library
- Partial failure recovery strategies
- Logging and monitoring integration

**Key concepts**:
```csharp
// Parallel batch processing
var tasks = batches.Select(async batch =>
{
    var batchActions = batch.Select(doc => IndexDocumentsAction.Upload(doc));
    var indexBatch = IndexDocumentsBatch.Create(batchActions.ToArray());
    return await searchClient.IndexDocumentsAsync(indexBatch);
});

var results = await Task.WhenAll(tasks);

// Optimal batch sizing
private static int GetOptimalBatchSize(int documentSizeKB)
{
    return documentSizeKB switch
    {
        < 1 => 1000,
        < 10 => 500,
        < 100 => 100,
        _ => 50
    };
}
```

**Key concepts**:
```csharp
// Comprehensive error handling
try
{
    var response = await searchClient.IndexDocumentsAsync(batch);
    return ProcessResults(response.Value.Results);
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    throw new UnauthorizedAccessException("Invalid admin key", ex);
}
catch (RequestFailedException ex) when (ex.Status == 503)
{
    // Service unavailable - implement retry
    await Task.Delay(TimeSpan.FromSeconds(1));
    return await RetryUpload(batch);
}

// Retry policy with Polly
var retryPolicy = Policy
    .Handle<RequestFailedException>(ex => ex.Status == 503)
    .WaitAndRetryAsync(3, retryAttempt => 
        TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
```

## 🎯 Learning Paths

### 1. Beginner Path (Sequential)
Follow the numbered sequence for structured learning:

```bash
dotnet run 01_CreateBasicIndex.cs      # Start here
dotnet run 02_SchemaDesign.cs          # Learn schema design
dotnet run 03_DataIngestion.cs         # Master data upload
dotnet run 04_IndexOperations.cs       # Index management
# Continue through all examples...
```

### 2. Enterprise Path
Focus on production-ready patterns:

```bash
dotnet run 06_ErrorHandling.cs         # Robust error handling
dotnet run 05_PerformanceOptimization.cs # Performance tuning
dotnet run 04_IndexOperations.cs       # Index management
dotnet run 02_SchemaDesign.cs          # Advanced schema design
```

### 3. Problem-Solving Path
Start with common enterprise scenarios:

```bash
# "I need enterprise-grade index creation"
dotnet run 01_CreateBasicIndex.cs

# "I need to handle large data volumes"
dotnet run 03_DataIngestion.cs

# "I need robust error handling"
dotnet run 06_ErrorHandling.cs
```

## 🔧 Code Features

### Enterprise-Ready Patterns
- ✅ Async/await throughout for scalability
- ✅ Comprehensive exception handling
- ✅ Configuration management with IConfiguration
- ✅ Logging integration with ILogger
- ✅ Dependency injection support

### Performance Optimizations
- ✅ Efficient batch processing with IndexDocumentsBatch
- ✅ Parallel processing with Task.WhenAll
- ✅ Memory-efficient streaming for large datasets
- ✅ Connection pooling and reuse

### Best Practices
- ✅ SOLID principles and clean architecture
- ✅ Proper resource disposal with using statements
- ✅ Configuration through environment variables
- ✅ Comprehensive XML documentation

## 🚨 Common Issues and Solutions

### Issue 1: Package Version Conflicts
```bash
# Problem: Package version conflicts
# Solution: Use specific version
dotnet add package Azure.Search.Documents --version 11.4.0
```

### Issue 2: Authentication Errors
```csharp
// Problem: 403 Forbidden errors
// Solution: Ensure admin key is used for index operations
var credential = new AzureKeyCredential(adminKey); // Not query key!
var indexClient = new SearchIndexClient(endpoint, credential);
```

### Issue 3: Async/Await Issues
```csharp
// Problem: Deadlocks or performance issues
// Solution: Use ConfigureAwait(false) in libraries
var result = await searchClient.IndexDocumentsAsync(batch).ConfigureAwait(false);
```

### Issue 4: Memory Issues with Large Datasets
```csharp
// Problem: OutOfMemoryException with large uploads
// Solution: Process in smaller batches
const int maxBatchSize = 100;
for (int i = 0; i < documents.Count; i += maxBatchSize)
{
    var batch = documents.Skip(i).Take(maxBatchSize);
    await ProcessBatch(batch);
}
```

## 💡 Tips for Success

### Development Workflow
1. **Start with Dependency Injection**: Set up proper DI container
2. **Use Configuration**: Externalize all settings
3. **Implement Logging**: Use ILogger for comprehensive logging
4. **Handle Async Properly**: Always use async/await correctly
5. **Test Thoroughly**: Unit test all components

### Debugging Techniques
1. **Enable Detailed Logging**: Use Debug and Trace logging
2. **Use Debugger**: Step through code to understand flow
3. **Check HTTP Responses**: Examine response details
4. **Validate Configuration**: Ensure all settings are correct
5. **Test Incrementally**: Start with small operations

### Performance Tips
1. **Use Batch Operations**: Always batch multiple operations
2. **Optimize Batch Size**: Adjust based on document complexity
3. **Implement Parallel Processing**: Use Task.WhenAll for concurrent operations
4. **Monitor Memory Usage**: Watch for memory leaks in long-running processes
5. **Reuse Clients**: Don't create new clients for each operation

## 🔗 Related Resources

### Module 3 Resources
- **[Module 3 Documentation](../documentation.md)** - Complete theory and concepts
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter notebook examples
- **[Python Examples](../python/README.md)** - Python implementations
- **[JavaScript Examples](../javascript/README.md)** - Node.js implementations

### .NET and Azure Resources
- **[Azure.Search.Documents Documentation](https://docs.microsoft.com/en-us/dotnet/api/azure.search.documents)** - Official .NET SDK docs
- **[Azure AI Search .NET Samples](https://github.com/Azure-Samples/azure-search-dotnet-samples)** - Official samples
- **[.NET Best Practices](https://docs.microsoft.com/en-us/dotnet/standard/design-guidelines/)** - .NET design guidelines

## 🚀 Next Steps

After mastering these C# examples:

1. **✅ Complete All Examples**: Work through each file systematically
2. **🏗️ Build Enterprise Solutions**: Apply patterns to your applications
3. **📝 Practice**: Complete the module exercises
4. **🌐 Explore Other Languages**: Try Python, JavaScript, or REST examples
5. **🔧 Integrate**: Add to your existing .NET applications
6. **📚 Continue Learning**: Move to Module 4: Simple Queries and Filters

---

**Ready to master Azure AI Search index management with C#?** 🔷✨

Start with `01_CreateBasicIndex.cs` and build enterprise-ready search solutions!