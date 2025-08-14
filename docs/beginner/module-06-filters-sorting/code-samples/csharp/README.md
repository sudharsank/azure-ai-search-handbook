# C# Examples - Filters & Sorting

## Overview

This directory contains C# examples for implementing filters and sorting in Azure AI Search using the `Azure.Search.Documents` SDK. The examples demonstrate various filtering techniques, sorting strategies, and performance optimization approaches.

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
<PackageReference Include="Microsoft.Extensions.Logging" Version="7.0.0" />
```

### Azure Resources
- Azure AI Search service
- Search index with filterable and sortable fields
- Sample data for testing

## Setup

### 1. Create Project
```bash
dotnet new console -n AzureSearchFiltersExamples
cd AzureSearchFiltersExamples
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
    "Endpoint": "https://your-search-service.search.windows.net",
    "IndexName": "your-index-name"
  }
}
```

### 3. Verify Setup
Run the setup verification:
```bash
dotnet run --project VerifySetup.cs
```

## Examples

### 01 - Basic Filters
**File:** `01_BasicFilters.cs`

Demonstrates:
- Equality filters (`eq`, `ne`)
- Comparison filters (`gt`, `ge`, `lt`, `le`)
- Boolean logic combinations (`and`, `or`, `not`)
- Null value handling

### 02 - Range Filters
**File:** `02_RangeFilters.cs`

Demonstrates:
- Numeric range filtering with `ge`, `le`, `gt`, `lt`
- Date range filtering with proper formatting
- Advanced range combinations and optimization
- Dynamic range filter building
- Performance optimization techniques

### 03 - String Filters
**File:** `03_StringFilters.cs` *(Coming Soon)*

Demonstrates:
- Text matching with `startswith`, `endswith`, `contains`
- Case sensitivity handling
- Pattern matching techniques
- Multi-language considerations

### 04 - Date Filters
**File:** `04_DateFilters.cs` *(Coming Soon)*

Demonstrates:
- Date range filtering
- Relative date calculations
- Time zone handling
- Date format considerations

### 05 - Geographic Filters
**File:** `05_GeographicFilters.cs`

Demonstrates:
- Distance-based filtering with `geo.distance()`
- Geographic bounds and coordinate validation
- Multi-point geographic filtering
- Distance range filters (ring shapes)
- Advanced geographic combinations
- Location preset management

### 06 - Sorting Operations
**File:** `06_SortingOperations.cs` *(Coming Soon)*

Demonstrates:
- Single field sorting
- Multi-field sorting
- Custom sort orders
- Performance optimization

### 07 - Complex Filters
**File:** `07_ComplexFilters.cs`

Demonstrates:
- Collection filtering with `any()` and `all()` functions
- Nested logical conditions and combinations
- Advanced collection filtering scenarios
- Filter optimization techniques
- Complex filter validation and analysis
- Performance monitoring for complex queries

### 08 - Performance Analysis
**File:** `08_PerformanceAnalysis.cs`

Demonstrates:
- Real-time query performance monitoring
- Comprehensive benchmark suite execution
- Performance trend analysis over time
- Optimization recommendations generation
- Performance data export and reporting
- Memory usage tracking and analysis

## Running Examples

### Individual Examples
```bash
dotnet run --project 01_BasicFilters.cs
dotnet run --project 02_RangeFilters.cs
# ... etc
```

### All Examples
```bash
# Run all available examples in sequence
dotnet run --project RunAllExamples.cs

# Run in demo mode (no API calls)
dotnet run --project RunAllExamples.cs -- --demo-mode

# Skip search-dependent examples
dotnet run --project RunAllExamples.cs -- --skip-search

# Show help
dotnet run --project RunAllExamples.cs -- --help
```

### Build and Run
```bash
# Restore packages and build
dotnet restore
dotnet build

# Run a specific example
dotnet run --project 01_BasicFilters.cs
dotnet run --project 02_RangeFilters.cs
dotnet run --project 05_GeographicFilters.cs
dotnet run --project 07_ComplexFilters.cs
dotnet run --project 08_PerformanceAnalysis.cs
```

## Common Patterns

### Authentication
```csharp
using Azure;
using Azure.Search.Documents;
using Azure.Identity;

// Using API key
var credential = new AzureKeyCredential(apiKey);
var searchClient = new SearchClient(endpoint, indexName, credential);

// Using managed identity
var credential = new DefaultAzureCredential();
var searchClient = new SearchClient(endpoint, indexName, credential);
```

### Basic Filtering
```csharp
// Simple equality filter
var searchOptions = new SearchOptions
{
    Filter = "category eq 'Electronics'"
};
var results = await searchClient.SearchAsync<SearchDocument>("*", searchOptions);

// Range filter
searchOptions.Filter = "price ge 100 and price le 500";
results = await searchClient.SearchAsync<SearchDocument>("*", searchOptions);

// Combined filters
searchOptions.Filter = "category eq 'Electronics' and rating ge 4.0";
results = await searchClient.SearchAsync<SearchDocument>("*", searchOptions);
```

### Sorting
```csharp
// Single field sorting
var searchOptions = new SearchOptions();
searchOptions.OrderBy.Add("rating desc");
var results = await searchClient.SearchAsync<SearchDocument>("*", searchOptions);

// Multi-field sorting
searchOptions.OrderBy.Add("category asc");
searchOptions.OrderBy.Add("rating desc");
searchOptions.OrderBy.Add("price asc");
results = await searchClient.SearchAsync<SearchDocument>("*", searchOptions);
```

### Error Handling
```csharp
try
{
    var searchOptions = new SearchOptions
    {
        Filter = "category eq 'Electronics'"
    };
    
    var results = await searchClient.SearchAsync<SearchDocument>("*", searchOptions);
    
    await foreach (var result in results.Value.GetResultsAsync())
    {
        Console.WriteLine($"Found: {result.Document["name"]}");
    }
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Search failed: {ex.Message}");
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
    IndexName = configuration["SearchService:IndexName"]
};
```

### Configuration Class
```csharp
public class SearchConfiguration
{
    public Uri Endpoint { get; set; }
    public string ApiKey { get; set; }
    public string IndexName { get; set; }
    
    public void Validate()
    {
        if (Endpoint == null || string.IsNullOrEmpty(ApiKey) || string.IsNullOrEmpty(IndexName))
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

### Performance Tests
```bash
dotnet test --filter Category=Performance
```

## Debugging

### Enable Logging
```csharp
using Microsoft.Extensions.Logging;

var loggerFactory = LoggerFactory.Create(builder => builder.AddConsole());
var logger = loggerFactory.CreateLogger<Program>();

// Use logger throughout your application
logger.LogInformation("Executing search with filter: {Filter}", filter);
```

### Debug Mode
```csharp
#if DEBUG
    Console.WriteLine($"Filter: {searchOptions.Filter}");
    Console.WriteLine($"Order by: {string.Join(", ", searchOptions.OrderBy)}");
#endif
```

## Best Practices

### Filter Construction
```csharp
public static class FilterBuilder
{
    public static string BuildProductFilter(string category = null, 
        decimal? minPrice = null, decimal? maxPrice = null, 
        double? minRating = null, bool? inStock = null)
    {
        var filters = new List<string>();
        
        if (!string.IsNullOrEmpty(category))
            filters.Add($"category eq '{EscapeODataString(category)}'");
        
        if (minPrice.HasValue)
            filters.Add($"price ge {minPrice.Value}");
        
        if (maxPrice.HasValue)
            filters.Add($"price le {maxPrice.Value}");
        
        if (minRating.HasValue)
            filters.Add($"rating ge {minRating.Value}");
        
        if (inStock.HasValue)
            filters.Add($"inStock eq {inStock.Value.ToString().ToLower()}");
        
        return filters.Count > 0 ? string.Join(" and ", filters) : null;
    }
    
    private static string EscapeODataString(string value)
    {
        return value?.Replace("'", "''");
    }
}
```

### Result Processing
```csharp
public static async Task<List<T>> ProcessResultsAsync<T>(SearchResults<T> results, int maxResults = 10)
{
    var processed = new List<T>();
    var count = 0;
    
    await foreach (var result in results.GetResultsAsync())
    {
        if (count >= maxResults) break;
        
        processed.Add(result.Document);
        count++;
    }
    
    return processed;
}
```

### Performance Monitoring
```csharp
public static async Task<SearchPerformanceResult<T>> TimedSearchAsync<T>(
    SearchClient searchClient, string searchText, SearchOptions options)
{
    var stopwatch = Stopwatch.StartNew();
    
    try
    {
        var results = await searchClient.SearchAsync<T>(searchText, options);
        var resultList = await ProcessResultsAsync(results.Value);
        
        stopwatch.Stop();
        
        return new SearchPerformanceResult<T>
        {
            Results = resultList,
            Duration = stopwatch.Elapsed,
            Success = true
        };
    }
    catch (Exception ex)
    {
        stopwatch.Stop();
        
        return new SearchPerformanceResult<T>
        {
            Duration = stopwatch.Elapsed,
            Success = false,
            Error = ex.Message
        };
    }
}

public class SearchPerformanceResult<T>
{
    public List<T> Results { get; set; }
    public TimeSpan Duration { get; set; }
    public bool Success { get; set; }
    public string Error { get; set; }
}
```

## Troubleshooting

### Common Issues
1. **Field not filterable**: Ensure field has `IsFilterable = true` in index schema
2. **Invalid filter syntax**: Check OData expression syntax
3. **Data type mismatches**: Ensure filter values match field types
4. **Performance issues**: Optimize filter expressions and index design

### Debug Tools
```csharp
public static class FilterValidator
{
    public static (bool IsValid, string Message) ValidateFilter(string filterExpression)
    {
        try
        {
            if (string.IsNullOrEmpty(filterExpression))
                return (true, "Empty filter is valid");
            
            // Check for balanced quotes
            var singleQuotes = filterExpression.Count(c => c == '\'');
            if (singleQuotes % 2 != 0)
                return (false, "Unbalanced single quotes");
            
            // Check for balanced parentheses
            var openParens = filterExpression.Count(c => c == '(');
            var closeParens = filterExpression.Count(c => c == ')');
            if (openParens != closeParens)
                return (false, "Unbalanced parentheses");
            
            return (true, "Filter appears valid");
        }
        catch (Exception ex)
        {
            return (false, $"Validation error: {ex.Message}");
        }
    }
}
```

## Project Structure

The examples are organized as a single .NET 6 console application with multiple example classes:

```
csharp/
├── AzureSearchFiltersExamples.csproj  # Project file with dependencies
├── appsettings.json                   # Configuration template
├── RunAllExamples.cs                  # Runs all examples in sequence
├── 01_BasicFilters.cs                 # Basic filtering operations
├── 02_RangeFilters.cs                 # Range filtering examples
├── 05_GeographicFilters.cs            # Geographic filtering examples
├── 07_ComplexFilters.cs               # Complex filtering scenarios
└── 08_PerformanceAnalysis.cs          # Performance monitoring and analysis
```

## Validation and Testing

### Example Validation
The `RunAllExamples.cs` program provides:
- Sequential execution of all available examples
- Demo mode for testing without API calls
- Comprehensive error reporting and performance metrics
- Configuration validation and setup verification

### Example Output
```bash
$ dotnet run --project RunAllExamples.cs -- --demo-mode
🎯 Azure AI Search - Filters & Sorting Examples (C#)
============================================================
🎭 DEMO MODE: Running without actual API calls

📊 Running 5 examples...
🎭 Demo mode enabled - no API calls will be made

[1/5] Basic Filters
📝 Equality, comparison, and boolean logic filters
✅ Example class found and validated

✅ All 5 examples completed successfully!
```

## Additional Resources

- [Azure.Search.Documents Documentation](https://docs.microsoft.com/dotnet/api/azure.search.documents)
- [.NET SDK Samples](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/search/Azure.Search.Documents/samples)
- [OData Filter Syntax Reference](https://docs.microsoft.com/azure/search/search-query-odata-filter)
- [Interactive Notebooks](../notebooks/) - Jupyter notebooks for hands-on learning

## Next Steps

1. **Setup**: Configure your `appsettings.json` with Azure AI Search credentials
2. **Demo Mode**: Try `dotnet run --project RunAllExamples.cs -- --demo-mode` for a quick overview
3. **Individual Examples**: Run specific examples that match your use case
4. **Interactive Learning**: Explore the Jupyter notebooks for hands-on experience
5. **Customize**: Modify examples for your specific data and requirements
6. **Production**: Implement filtering in your applications with proper error handling
7. **Advanced Features**: Explore intermediate and advanced modules