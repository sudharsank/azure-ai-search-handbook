# C# Code Samples - Module 2: Basic Search Operations

This directory contains focused C# examples for basic search operations in Azure AI Search using the .NET SDK. Each file demonstrates a specific aspect of search functionality with clear, production-ready code.

## 📁 Files Overview

### Core Search Operations (Files 01-05)
1. **`01_SimpleTextSearch.cs`** - Basic text search and result handling
2. **`02_PhraseSearch.cs`** - Exact phrase matching with quotes
3. **`03_BooleanSearch.cs`** - Boolean operators (AND, OR, NOT)
4. **`04_WildcardSearch.cs`** - Pattern matching with wildcards
5. **`05_FieldSearch.cs`** - Field-specific and multi-field searches

### Advanced Features (Files 06-08)
6. **`06_ResultProcessing.cs`** - Processing and formatting search results
7. **`07_ErrorHandling.cs`** - Comprehensive error handling strategies
8. **`08_SearchPatterns.cs`** - Advanced search patterns and best practices

## 🎯 Complete Coverage Matrix

| Topic | Python | C# | JavaScript | REST | Description |
|-------|--------|----|-----------|----- |-------------|
| Simple Text Search | ✅ | ✅ | ✅ | ✅ | Basic keyword searching |
| Phrase Search | ✅ | ✅ | ✅ | ✅ | Exact phrase matching |
| Boolean Search | ✅ | ✅ | ✅ | ✅ | AND, OR, NOT operators |
| Wildcard Search | ✅ | ✅ | ✅ | ✅ | Pattern matching with * |
| Field Search | ✅ | ✅ | ✅ | ✅ | Field-specific searches |
| Result Processing | ✅ | ✅ | ✅ | ✅ | Formatting and analysis |
| Error Handling | ✅ | ✅ | ✅ | ✅ | Robust error management |
| Search Patterns | ✅ | ✅ | ✅ | ✅ | Advanced strategies |

## 🚀 Getting Started

### ⚠️ CRITICAL FIRST STEP: Prerequisites Setup

**Before running ANY C# examples, you MUST run the prerequisites setup:**

```bash
# Navigate to the parent directory
cd ../

# Run the prerequisites setup script
python setup_prerequisites.py
```

**What this does:**
- 🔌 Tests your Azure AI Search connection
- 🏗️ Creates the `handbook-samples` index with comprehensive schema
- 📄 Uploads 10 sample documents with rich content
- 🧪 Tests all search operations to ensure everything works
- 📋 Provides a summary of what's ready

**Time Required**: 5-10 minutes

### Prerequisites
```bash
# Create new console application
dotnet new console -n AzureSearchBasics
cd AzureSearchBasics

# Add Azure Search package
dotnet add package Azure.Search.Documents

# Add configuration package (optional)
dotnet add package Microsoft.Extensions.Configuration
dotnet add package Microsoft.Extensions.Configuration.Json
```

### Configuration Setup

#### Option 1: Direct Configuration (Simple)
```csharp
// Replace with your actual service details
private const string ServiceEndpoint = "https://your-service.search.windows.net";
private const string ApiKey = "your-api-key";
private const string IndexName = "your-index-name";

var searchClient = new SearchClient(
    new Uri(ServiceEndpoint),
    IndexName,
    new AzureKeyCredential(ApiKey)
);
```

#### Option 2: Configuration File (Recommended)
Create `appsettings.json`:
```json
{
  "AzureSearch": {
    "ServiceEndpoint": "https://your-service.search.windows.net",
    "ApiKey": "your-api-key",
    "IndexName": "your-index-name"
  }
}
```

Then in your code:
```csharp
using Microsoft.Extensions.Configuration;

var configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .Build();

var searchClient = new SearchClient(
    new Uri(configuration["AzureSearch:ServiceEndpoint"]),
    configuration["AzureSearch:IndexName"],
    new AzureKeyCredential(configuration["AzureSearch:ApiKey"])
);
```

### Quick Start
```bash
# 1. FIRST: Run prerequisites setup (from parent directory)
cd ../
python setup_prerequisites.py

# 2. THEN: Compile and run C# examples
cd csharp/
dotnet run 01_SimpleTextSearch.cs

# Or build and run
dotnet build
dotnet run
```

## 📚 Learning Path

### Beginner Path (Recommended Order)
1. **Start Here**: `01_SimpleTextSearch.cs` - Learn basic search concepts
2. **Precision**: `02_PhraseSearch.cs` - Understand exact matching
3. **Logic**: `03_BooleanSearch.cs` - Combine terms with operators
4. **Flexibility**: `04_WildcardSearch.cs` - Pattern matching techniques
5. **Targeting**: `05_FieldSearch.cs` - Search specific fields

### Advanced Path (After Basics)
6. **Processing**: `06_ResultProcessing.cs` - Handle and format results effectively
7. **Reliability**: `07_ErrorHandling.cs` - Build robust search applications
8. **Patterns**: `08_SearchPatterns.cs` - Implement advanced search strategies

### Quick Reference
- **Need basic search?** → `01_SimpleTextSearch.cs`
- **Want exact phrases?** → `02_PhraseSearch.cs`
- **Combining terms?** → `03_BooleanSearch.cs`
- **Partial matching?** → `04_WildcardSearch.cs`
- **Specific fields?** → `05_FieldSearch.cs`
- **Processing results?** → `06_ResultProcessing.cs`
- **Handling errors?** → `07_ErrorHandling.cs`
- **Advanced patterns?** → `08_SearchPatterns.cs`

## 💡 Key C# Concepts Covered

### Advanced Search Features
- **Result Processing**: Format, filter, and analyze search results with strongly-typed classes
- **Error Handling**: Comprehensive error management using try-catch patterns and custom exceptions
- **Search Patterns**: Progressive search, fallback strategies, and multi-field searches
- **Performance Optimization**: Async/await patterns and efficient result processing

### Azure SDK Integration
- **SearchClient**: Main client for search operations
- **SearchOptions**: Configuration for search requests
- **SearchResults<T>**: Strongly-typed search results
- **AzureKeyCredential**: Authentication with API keys

### Async/Await Patterns
```csharp
// All search operations are async
var results = await searchClient.SearchAsync<SearchDocument>(query, options);

// Process results asynchronously
await foreach (var result in results.Value.GetResultsAsync())
{
    // Process each result
}
```

### Error Handling
```csharp
try
{
    var results = await searchClient.SearchAsync<SearchDocument>(query);
    // Process results
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    // Handle bad request (invalid query)
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    // Handle not found (invalid index)
}
catch (Exception ex)
{
    // Handle other errors
}
```

### Result Processing
```csharp
// Access search results
foreach (var result in results.Value.GetResults())
{
    var score = result.Score;
    var document = result.Document;
    
    // Access document fields
    var title = document.TryGetValue("title", out var titleValue) ? 
        titleValue?.ToString() : "No title";
}
```

## 🔧 Code Structure

Each C# file follows this structure:
```csharp
/*
Module description and concepts covered
*/

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module02.BasicSearch
{
    // Main class demonstrating the concept
    public class ConceptDemo
    {
        private readonly SearchClient _searchClient;

        public ConceptDemo(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        // Core functionality methods
        public async Task<SearchResults<SearchDocument>> MainMethodAsync(string query, int top = 10)
        {
            // Implementation
        }

        // Helper methods
        public static void DisplayResults(SearchResults<SearchDocument> results)
        {
            // Display logic
        }
    }

    // Program class for demonstration
    public class Program
    {
        public static async Task Main(string[] args)
        {
            // Demo execution
        }
    }
}
```

## 🎯 Usage Examples

### Basic Search
```csharp
using Azure;
using Azure.Search.Documents;

// Initialize client
var searchClient = new SearchClient(
    new Uri("https://your-service.search.windows.net"),
    "your-index-name",
    new AzureKeyCredential("your-api-key")
);

// Perform search
var results = await searchClient.SearchAsync<SearchDocument>("python programming");

// Process results
await foreach (var result in results.Value.GetResultsAsync())
{
    Console.WriteLine($"Title: {result.Document["title"]}");
    Console.WriteLine($"Score: {result.Score}");
}
```

### Using the Example Classes
```csharp
// Import from any example file
using AzureSearchHandbook.Module02.BasicSearch;

// Initialize and use basic search
var searchOps = new SimpleTextSearch(searchClient);
var results = await searchOps.BasicSearchAsync("machine learning", 5);
SimpleTextSearch.DisplayResults(results);

// Process results with advanced formatting
var processor = new ResultProcessor();
var processedResults = processor.ProcessRawResults(results);
var formattedOutput = processor.FormatForDisplay(processedResults);
Console.WriteLine(formattedOutput);

// Use safe search with error handling
var safeClient = new SafeSearchClient(searchClient);
var (safeResults, errorMessage) = await safeClient.SafeSearchAsync("python programming");

// Implement advanced search patterns
var patterns = new SearchPatterns(searchClient);
var fallbackResults = await patterns.SearchWithFallbackAsync("artificial intelligence tutorial");
```

## 🛡️ Error Handling

All examples include comprehensive error handling:
```csharp
try
{
    var results = await searchClient.SearchAsync<SearchDocument>(query);
    // Process results
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Search error: {ex.Status} - {ex.Message}");
}
catch (Exception ex)
{
    Console.WriteLine($"Unexpected error: {ex.Message}");
}
```

## 📊 Performance Tips

1. **Use Async/Await**: All operations are async for better performance
2. **Limit Results**: Use `Size` property in `SearchOptions`
3. **Select Fields**: Use `Select` property to return only needed fields
4. **Connection Pooling**: Reuse `SearchClient` instances
5. **Batch Operations**: Process multiple searches efficiently

## 🔗 Integration Examples

### With Dependency Injection
```csharp
// In Startup.cs or Program.cs
services.AddSingleton<SearchClient>(provider =>
{
    var config = provider.GetService<IConfiguration>();
    return new SearchClient(
        new Uri(config["AzureSearch:ServiceEndpoint"]),
        config["AzureSearch:IndexName"],
        new AzureKeyCredential(config["AzureSearch:ApiKey"])
    );
});
```

### With ASP.NET Core
```csharp
[ApiController]
[Route("api/[controller]")]
public class SearchController : ControllerBase
{
    private readonly SearchClient _searchClient;

    public SearchController(SearchClient searchClient)
    {
        _searchClient = searchClient;
    }

    [HttpGet]
    public async Task<IActionResult> Search(string query)
    {
        var results = await _searchClient.SearchAsync<SearchDocument>(query);
        return Ok(results.Value.GetResults());
    }
}
```

## 🚀 Next Steps

After working through these examples:
1. ✅ Try modifying the queries and parameters
2. 🔧 Implement your own search functionality
3. 📚 Explore other language examples
4. 🎯 Check out the interactive notebooks
5. 📖 Move on to Module 3: Index Management

## 🔗 Cross-Language Learning

These C# examples complement the other language implementations:
- **[Python Examples](../python/README.md)** - Python implementations for data science workflows
- **[JavaScript Examples](../javascript/README.md)** - Node.js and browser examples
- **[REST API Examples](../rest/README.md)** - Direct HTTP API calls for any language
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter examples for experimentation

**🎯 Learning Approach:**
- **Enterprise Path**: Focus on production-ready patterns with dependency injection
- **Sequential Learning**: Follow 01-08 in order for structured learning
- **Cross-Platform**: Compare C# patterns with other language implementations
- **Integration Focused**: Learn ASP.NET Core and enterprise integration patterns

## 📖 Additional Resources

- [Azure.Search.Documents Documentation](https://docs.microsoft.com/en-us/dotnet/api/azure.search.documents/)
- [Azure AI Search .NET Samples](https://github.com/Azure-Samples/azure-search-dotnet-samples)
- [.NET SDK Quickstart](https://docs.microsoft.com/en-us/azure/search/search-get-started-dotnet)
- [Enterprise Integration Patterns](https://docs.microsoft.com/en-us/dotnet/architecture/)

---

**Happy Coding!** 🔷✨