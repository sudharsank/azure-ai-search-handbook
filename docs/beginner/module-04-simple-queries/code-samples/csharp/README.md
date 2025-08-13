# C# Code Samples - Simple Queries and Filters

This directory contains C# implementations for learning simple queries and filters in Azure AI Search using the Azure SDK for .NET.

## 📋 Prerequisites

### Required Packages

Install the required NuGet packages:

```xml
<PackageReference Include="Azure.Search.Documents" Version="11.5.1" />
<PackageReference Include="Microsoft.Extensions.Configuration" Version="7.0.0" />
<PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="7.0.0" />
<PackageReference Include="Microsoft.Extensions.Configuration.EnvironmentVariables" Version="7.0.0" />
```

Or via Package Manager Console:
```powershell
Install-Package Azure.Search.Documents
Install-Package Microsoft.Extensions.Configuration
Install-Package Microsoft.Extensions.Configuration.Json
Install-Package Microsoft.Extensions.Configuration.EnvironmentVariables
```

### Configuration Setup

Create an `appsettings.json` file in your project root:

```json
{
  "AzureSearch": {
    "ServiceEndpoint": "https://your-service.search.windows.net",
    "ApiKey": "your-api-key",
    "IndexName": "your-index-name"
  }
}
```

Or use environment variables:
```bash
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=your-index-name
```

### Sample Data

These examples assume you have sample indexes created from previous modules with documents containing:

- `id` (string) - Unique identifier
- `title` (string) - Document title
- `content` (string) - Document content
- `category` (string) - Document category
- `tags` (string[]) - Document tags
- `rating` (double) - Document rating (0.0-5.0)
- `publishedDate` (DateTimeOffset) - Publication date
- `price` (double) - Document price

## 🚀 Getting Started

### Basic Usage

```csharp
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Microsoft.Extensions.Configuration;

// Load configuration
var configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .AddEnvironmentVariables()
    .Build();

// Initialize the search client
var serviceEndpoint = new Uri(configuration["AzureSearch:ServiceEndpoint"]);
var credential = new AzureKeyCredential(configuration["AzureSearch:ApiKey"]);
var indexName = configuration["AzureSearch:IndexName"];

var searchClient = new SearchClient(serviceEndpoint, indexName, credential);

// Perform a simple search
var results = await searchClient.SearchAsync<SearchDocument>("azure");
await foreach (var result in results.Value.GetResults())
{
    Console.WriteLine($"Title: {result.Document["title"]}");
}
```

## 📚 Code Samples

### 1. Basic Queries (`01_BasicQueries.cs`)
Learn fundamental text search operations:
- Simple text search
- Field-specific search
- Query operators (+, -, "", *, ())
- Search modes and query types

**Key Concepts:**
- SearchOptions configuration
- SearchResults processing
- Query syntax variations
- Async/await patterns

### 2. Filtering (`02_Filtering.cs`)
Master OData filter expressions:
- Equality and comparison filters
- Logical operators (and, or, not)
- Collection filters (any, all)
- Date and numeric range filters

**Key Concepts:**
- OData filter syntax in C#
- Type-safe filtering
- Complex filter expressions
- Performance optimization

### 3. Sorting and Pagination (`03_SortingPagination.cs`)
Implement result ordering and pagination:
- Single and multi-field sorting
- Ascending and descending order
- Page-based navigation
- Total count retrieval

**Key Concepts:**
- OrderBy expressions
- Skip and Size parameters
- Pagination patterns
- Performance considerations

### 4. Result Customization (`04_ResultCustomization.cs`)
Customize search results:
- Field selection
- Search highlighting
- Result formatting
- Custom result processing

**Key Concepts:**
- Select parameter
- Highlight configuration
- Result metadata
- Custom formatting

### 5. Advanced Queries (`05_AdvancedQueries.cs`)
Explore advanced query features:
- Field boosting
- Fuzzy search
- Wildcard patterns
- Regular expressions

**Key Concepts:**
- Query complexity
- Performance optimization
- Advanced syntax
- Use case scenarios

### 6. Error Handling (`06_ErrorHandling.cs`)
Implement robust error handling:
- Exception types and handling
- Query validation
- Retry logic
- Debugging techniques

**Key Concepts:**
- Azure SDK exceptions
- Error recovery
- Logging and debugging
- Production best practices

## 🔧 Running the Examples

### Individual Examples

Compile and run each example:

```bash
# Basic queries
dotnet run --project 01_BasicQueries.cs

# Filtering
dotnet run --project 02_Filtering.cs

# Sorting and pagination
dotnet run --project 03_SortingPagination.cs

# Result customization
dotnet run --project 04_ResultCustomization.cs

# Advanced queries
dotnet run --project 05_AdvancedQueries.cs

# Error handling
dotnet run --project 06_ErrorHandling.cs
```

### Project Setup

Create a console application:

```bash
dotnet new console -n AzureSearchModule4
cd AzureSearchModule4
dotnet add package Azure.Search.Documents
dotnet add package Microsoft.Extensions.Configuration
dotnet add package Microsoft.Extensions.Configuration.Json
dotnet add package Microsoft.Extensions.Configuration.EnvironmentVariables
```

## 🎯 Learning Outcomes

After completing these C# examples, you will be able to:

- ✅ **Initialize Search Client**: Set up Azure AI Search client with proper authentication
- ✅ **Execute Basic Queries**: Perform text searches with various operators
- ✅ **Apply Filters**: Use OData expressions to filter results effectively
- ✅ **Implement Pagination**: Handle large result sets with proper pagination
- ✅ **Customize Results**: Select fields and highlight matching terms
- ✅ **Handle Errors**: Implement robust error handling and validation
- ✅ **Optimize Performance**: Write efficient queries for production use

## 🔍 Common Patterns

### Search Client Initialization

```csharp
public class SearchService
{
    private readonly SearchClient _searchClient;
    
    public SearchService(IConfiguration configuration)
    {
        var serviceEndpoint = new Uri(configuration["AzureSearch:ServiceEndpoint"]);
        var credential = new AzureKeyCredential(configuration["AzureSearch:ApiKey"]);
        var indexName = configuration["AzureSearch:IndexName"];
        
        _searchClient = new SearchClient(serviceEndpoint, indexName, credential);
    }
}
```

### Error Handling Pattern

```csharp
public async Task<List<SearchResult<SearchDocument>>> SafeSearchAsync(string searchText, SearchOptions options = null)
{
    try
    {
        var response = await _searchClient.SearchAsync<SearchDocument>(searchText, options);
        return response.Value.GetResults().ToList();
    }
    catch (RequestFailedException ex)
    {
        Console.WriteLine($"Search error: {ex.Message}");
        return new List<SearchResult<SearchDocument>>();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Unexpected error: {ex.Message}");
        return new List<SearchResult<SearchDocument>>();
    }
}
```

### Result Processing Pattern

```csharp
public static void DisplayResults(SearchResults<SearchDocument> results, string title, int maxResults = 5)
{
    Console.WriteLine($"\n{new string('=', 60)}");
    Console.WriteLine(title);
    Console.WriteLine(new string('=', 60));
    
    var resultList = results.GetResults().Take(maxResults).ToList();
    
    if (!resultList.Any())
    {
        Console.WriteLine("No results found.");
        return;
    }
    
    for (int i = 0; i < resultList.Count; i++)
    {
        var result = resultList[i];
        Console.WriteLine($"\n{i + 1}. {result.Document.GetValueOrDefault("title", "No title")}");
        Console.WriteLine($"   Score: {result.Score:F3}");
        Console.WriteLine($"   Category: {result.Document.GetValueOrDefault("category", "N/A")}");
        Console.WriteLine($"   Rating: {result.Document.GetValueOrDefault("rating", "N/A")}");
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Package Errors**
   ```bash
   dotnet restore
   dotnet clean
   dotnet build
   ```

2. **Configuration Errors**
   - Verify your `appsettings.json` contains correct credentials
   - Check API key permissions
   - Ensure service endpoint is correct

3. **Index Not Found**
   - Verify index name in configuration
   - Check if index exists in your search service
   - Run index creation from previous modules

4. **No Results**
   - Check if your index contains data
   - Try broader search terms
   - Verify field names in filters

### Debug Mode

Enable detailed logging:

```csharp
using Microsoft.Extensions.Logging;

// Add logging to your service
public class SearchService
{
    private readonly SearchClient _searchClient;
    private readonly ILogger<SearchService> _logger;
    
    public SearchService(SearchClient searchClient, ILogger<SearchService> logger)
    {
        _searchClient = searchClient;
        _logger = logger;
    }
    
    public async Task<SearchResults<SearchDocument>> SearchWithLoggingAsync(string query)
    {
        _logger.LogInformation("Executing search: {Query}", query);
        
        try
        {
            var results = await _searchClient.SearchAsync<SearchDocument>(query);
            _logger.LogInformation("Search completed: {Count} results", results.Value.GetResults().Count());
            return results.Value;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Search failed for query: {Query}", query);
            throw;
        }
    }
}
```

## 📖 Additional Resources

- [Azure SDK for .NET Documentation](https://docs.microsoft.com/en-us/dotnet/api/azure.search.documents)
- [Azure AI Search .NET Samples](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/search/Azure.Search.Documents/samples)
- [.NET Best Practices](https://docs.microsoft.com/en-us/dotnet/standard/design-guidelines/)

## 🔗 Next Steps

1. **Practice with Real Data**: Apply these patterns to your own datasets
2. **Explore Advanced Features**: Move to Module 5 for advanced querying
3. **Build Applications**: Integrate search into your .NET applications
4. **Performance Tuning**: Learn about search optimization and analytics

Happy coding! 🔷