# C# Examples - Module 7: Pagination & Result Shaping

## Overview

This directory contains comprehensive C# examples demonstrating pagination and result shaping techniques in Azure AI Search using the `Azure.Search.Documents` SDK.

## Prerequisites

### .NET Environment
```bash
# .NET 6.0 or higher
dotnet --version

# Create new console project
dotnet new console -n PaginationExamples
cd PaginationExamples

# Add required packages
dotnet add package Azure.Search.Documents
dotnet add package Microsoft.Extensions.Configuration
dotnet add package Microsoft.Extensions.Configuration.Json
dotnet add package Microsoft.Extensions.Configuration.EnvironmentVariables
```

### Project Configuration
Create `appsettings.json`:
```json
{
  "AzureSearch": {
    "ServiceName": "your-search-service",
    "IndexName": "hotels-sample",
    "ApiKey": "your-api-key"
  }
}
```

Create `appsettings.Development.json` for local development:
```json
{
  "AzureSearch": {
    "ServiceName": "your-dev-search-service",
    "IndexName": "hotels-sample-dev",
    "ApiKey": "your-dev-api-key"
  }
}
```

### Environment Variables (Alternative)
```bash
# Set environment variables
export AZURE_SEARCH_SERVICE_NAME="your-search-service"
export AZURE_SEARCH_INDEX_NAME="hotels-sample"
export AZURE_SEARCH_API_KEY="your-api-key"
```

### Azure AI Search Setup
- Active Azure AI Search service
- Sample data index (hotels-sample recommended)
- Valid API keys and endpoint URLs

## Examples Overview

### Core Pagination Examples
1. **01_BasicPagination.cs** - Skip/top pagination fundamentals with async/await
2. **02_FieldSelection.cs** - Field selection optimization and LINQ integration
3. **03_HitHighlighting.cs** - Hit highlighting with custom processing
4. **04_ResultCounting.cs** - Smart counting strategies with caching
5. **05_RangePagination.cs** - Range-based pagination for large datasets

### Advanced Examples
6. **06_SearchScores.cs** - Search scores and relevance analysis
7. **07_LargeResultSets.cs** - Efficient handling of large datasets
8. **08_PerformanceOptimization.cs** - Production-ready pagination with comprehensive monitoring

## Quick Start

### 1. Basic Setup
```csharp
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

// Configuration
var configuration = new ConfigurationBuilder()
    .AddJsonFile("appsettings.json")
    .AddEnvironmentVariables()
    .Build();

var serviceName = configuration["AzureSearch:ServiceName"];
var indexName = configuration["AzureSearch:IndexName"];
var apiKey = configuration["AzureSearch:ApiKey"];

// Initialize client
var endpoint = new Uri($"https://{serviceName}.search.windows.net");
var credential = new AzureKeyCredential(apiKey);
var searchClient = new SearchClient(endpoint, indexName, credential);

// Basic pagination
var options = new SearchOptions
{
    Skip = 0,
    Size = 10,
    IncludeTotalCount = true
};

var results = await searchClient.SearchAsync<SearchDocument>("luxury", options);
```

### 2. Running Examples
```bash
# Build the project
dotnet build

# Run individual examples
dotnet run -- BasicPagination
dotnet run -- FieldSelection

# Run all examples
dotnet run -- All
```

## Example Details

### 01_BasicPagination.cs
**Features:**
- Async/await pagination implementation
- Generic type support with strongly-typed models
- LINQ integration for result processing
- Performance monitoring with Stopwatch
- Exception handling with retry policies

**Key Classes:**
- `BasicPaginator<T>`: Generic pagination functionality
- `PaginationResult<T>`: Strongly-typed result container
- `PaginationOptions`: Configuration options
- `PerformanceMetrics`: Timing and performance data

### 02_FieldSelection.cs
**Features:**
- Strongly-typed field selection with expressions
- LINQ-based field selection
- Response size optimization
- Dynamic field selection based on context
- Integration with model binding

**Key Classes:**
- `FieldSelector<T>`: Generic field selection
- `FieldSelectionBuilder`: Fluent API for field selection
- `SelectionContext`: Context-based field selection
- `ResponseAnalyzer`: Performance analysis

### 03_HitHighlighting.cs
**Features:**
- Strongly-typed highlight processing
- Custom highlight tag configuration
- LINQ-based highlight extraction
- HTML sanitization and processing
- Integration with Razor views

**Key Classes:**
- `HitHighlighter<T>`: Generic highlighting functionality
- `HighlightResult`: Processed highlight data
- `HighlightProcessor`: HTML processing utilities
- `HighlightConfiguration`: Configuration options

### 04_ResultCounting.cs
**Features:**
- Memory-efficient counting strategies
- Async caching with IMemoryCache
- Conditional counting based on context
- Performance monitoring and metrics
- Integration with dependency injection

**Key Classes:**
- `ResultCounter<T>`: Generic counting functionality
- `CountingStrategy`: Strategy pattern implementation
- `CacheManager`: Caching abstraction
- `CountingMetrics`: Performance tracking

### 05_RangePagination.cs
**Features:**
- Expression-based range filtering
- Strongly-typed sort field specification
- State management with immutable objects
- LINQ integration for complex scenarios
- Performance optimization for large datasets

**Key Classes:**
- `RangePaginator<T>`: Generic range pagination
- `RangeNavigator<T>`: Navigation logic
- `SortExpression<T>`: Type-safe sorting
- `RangeState<T>`: Immutable state management

## Common Patterns

### Strongly-Typed Models
```csharp
public class Hotel
{
    public string HotelId { get; set; }
    public string HotelName { get; set; }
    public string Description { get; set; }
    public string Category { get; set; }
    public double? Rating { get; set; }
    public GeographyPoint Location { get; set; }
    public Address Address { get; set; }
    public string[] Tags { get; set; }
    public bool? ParkingIncluded { get; set; }
    public bool? SmokingAllowed { get; set; }
    public DateTimeOffset? LastRenovationDate { get; set; }
}

public class Address
{
    public string StreetAddress { get; set; }
    public string City { get; set; }
    public string StateProvince { get; set; }
    public string PostalCode { get; set; }
    public string Country { get; set; }
}
```

### Generic Pagination with LINQ
```csharp
public class GenericPaginator<T> where T : class
{
    private readonly SearchClient _searchClient;
    
    public async Task<PaginationResult<T>> SearchAsync<TResult>(
        string searchText,
        Expression<Func<T, TResult>> selector,
        int pageNumber = 0,
        int pageSize = 20)
    {
        var options = new SearchOptions
        {
            Skip = pageNumber * pageSize,
            Size = pageSize,
            Select = { GetFieldNames(selector) }
        };
        
        var results = await _searchClient.SearchAsync<T>(searchText, options);
        var documents = await results.Value.GetResultsAsync().ToListAsync();
        
        return new PaginationResult<T>
        {
            Documents = documents.Select(r => r.Document).ToList(),
            CurrentPage = pageNumber,
            PageSize = pageSize,
            HasMore = documents.Count == pageSize
        };
    }
}
```

### Async Enumerable Support
```csharp
public class AsyncPaginationEnumerator<T> : IAsyncEnumerable<T> where T : class
{
    private readonly SearchClient _searchClient;
    private readonly string _searchText;
    private readonly int _pageSize;
    
    public async IAsyncEnumerator<T> GetAsyncEnumerator(
        CancellationToken cancellationToken = default)
    {
        int skip = 0;
        bool hasMore = true;
        
        while (hasMore && !cancellationToken.IsCancellationRequested)
        {
            var options = new SearchOptions
            {
                Skip = skip,
                Size = _pageSize
            };
            
            var results = await _searchClient.SearchAsync<T>(_searchText, options);
            var documents = await results.Value.GetResultsAsync().ToListAsync();
            
            foreach (var doc in documents)
            {
                yield return doc.Document;
            }
            
            hasMore = documents.Count == _pageSize;
            skip += _pageSize;
        }
    }
}
```

### Dependency Injection Integration
```csharp
// Startup.cs or Program.cs
services.AddSingleton<SearchClient>(provider =>
{
    var configuration = provider.GetRequiredService<IConfiguration>();
    var serviceName = configuration["AzureSearch:ServiceName"];
    var indexName = configuration["AzureSearch:IndexName"];
    var apiKey = configuration["AzureSearch:ApiKey"];
    
    var endpoint = new Uri($"https://{serviceName}.search.windows.net");
    var credential = new AzureKeyCredential(apiKey);
    return new SearchClient(endpoint, indexName, credential);
});

services.AddScoped<IPaginationService<Hotel>, PaginationService<Hotel>>();
services.AddScoped<IFieldSelector<Hotel>, FieldSelector<Hotel>>();
services.AddMemoryCache();

// Usage in controller
[ApiController]
[Route("api/[controller]")]
public class HotelsController : ControllerBase
{
    private readonly IPaginationService<Hotel> _paginationService;
    
    public HotelsController(IPaginationService<Hotel> paginationService)
    {
        _paginationService = paginationService;
    }
    
    [HttpGet]
    public async Task<ActionResult<PaginationResult<Hotel>>> SearchAsync(
        [FromQuery] string query = "*",
        [FromQuery] int page = 0,
        [FromQuery] int size = 20)
    {
        var result = await _paginationService.SearchAsync(query, page, size);
        return Ok(result);
    }
}
```

## Testing and Validation

### Unit Tests with Moq
```csharp
[TestClass]
public class PaginationTests
{
    private Mock<SearchClient> _mockSearchClient;
    private BasicPaginator<Hotel> _paginator;
    
    [TestInitialize]
    public void Setup()
    {
        _mockSearchClient = new Mock<SearchClient>();
        _paginator = new BasicPaginator<Hotel>(_mockSearchClient.Object);
    }
    
    [TestMethod]
    public async Task SearchAsync_ReturnsExpectedResults()
    {
        // Arrange
        var mockResults = new List<SearchResult<Hotel>>
        {
            SearchModelFactory.SearchResult(new Hotel { HotelId = "1", HotelName = "Test Hotel" }, 1.0, null)
        };
        
        var mockResponse = SearchModelFactory.SearchResults(mockResults, 1, null, null, null);
        
        _mockSearchClient
            .Setup(x => x.SearchAsync<Hotel>(It.IsAny<string>(), It.IsAny<SearchOptions>(), default))
            .ReturnsAsync(Response.FromValue(mockResponse, Mock.Of<Response>()));
        
        // Act
        var result = await _paginator.SearchAsync("test", 0, 10);
        
        // Assert
        Assert.AreEqual(1, result.Documents.Count);
        Assert.AreEqual("Test Hotel", result.Documents[0].HotelName);
    }
}
```

### Integration Tests
```csharp
[TestClass]
public class IntegrationTests
{
    private SearchClient _searchClient;
    
    [TestInitialize]
    public void Setup()
    {
        var configuration = new ConfigurationBuilder()
            .AddJsonFile("appsettings.test.json")
            .Build();
        
        var serviceName = configuration["AzureSearch:ServiceName"];
        var indexName = configuration["AzureSearch:IndexName"];
        var apiKey = configuration["AzureSearch:ApiKey"];
        
        var endpoint = new Uri($"https://{serviceName}.search.windows.net");
        var credential = new AzureKeyCredential(apiKey);
        _searchClient = new SearchClient(endpoint, indexName, credential);
    }
    
    [TestMethod]
    public async Task RealSearchTest()
    {
        var paginator = new BasicPaginator<Hotel>(_searchClient);
        var result = await paginator.SearchAsync("*", 0, 5);
        
        Assert.IsTrue(result.Documents.Count <= 5);
        Assert.IsTrue(result.Documents.All(h => !string.IsNullOrEmpty(h.HotelId)));
    }
}
```

## Performance Optimization

### Async Best Practices
```csharp
public class OptimizedPaginator<T> where T : class
{
    private readonly SearchClient _searchClient;
    private readonly SemaphoreSlim _semaphore;
    
    public OptimizedPaginator(SearchClient searchClient, int maxConcurrency = 10)
    {
        _searchClient = searchClient;
        _semaphore = new SemaphoreSlim(maxConcurrency);
    }
    
    public async Task<List<PaginationResult<T>>> SearchMultiplePagesAsync(
        string searchText,
        int[] pageNumbers,
        int pageSize = 20,
        CancellationToken cancellationToken = default)
    {
        var tasks = pageNumbers.Select(async pageNumber =>
        {
            await _semaphore.WaitAsync(cancellationToken);
            try
            {
                return await SearchPageAsync(searchText, pageNumber, pageSize, cancellationToken);
            }
            finally
            {
                _semaphore.Release();
            }
        });
        
        return (await Task.WhenAll(tasks)).ToList();
    }
}
```

### Memory-Efficient Streaming
```csharp
public class StreamingPaginator<T> where T : class
{
    public async IAsyncEnumerable<T> StreamAllAsync(
        string searchText,
        int batchSize = 100,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        int skip = 0;
        bool hasMore = true;
        
        while (hasMore && !cancellationToken.IsCancellationRequested)
        {
            var options = new SearchOptions
            {
                Skip = skip,
                Size = batchSize
            };
            
            var results = await _searchClient.SearchAsync<T>(searchText, options);
            var batch = new List<T>();
            
            await foreach (var result in results.Value.GetResultsAsync())
            {
                batch.Add(result.Document);
            }
            
            foreach (var item in batch)
            {
                yield return item;
            }
            
            hasMore = batch.Count == batchSize;
            skip += batchSize;
        }
    }
}
```

### Caching with IMemoryCache
```csharp
public class CachedPaginator<T> where T : class
{
    private readonly SearchClient _searchClient;
    private readonly IMemoryCache _cache;
    private readonly TimeSpan _cacheExpiry;
    
    public async Task<PaginationResult<T>> SearchAsync(
        string searchText,
        int pageNumber,
        int pageSize,
        CancellationToken cancellationToken = default)
    {
        var cacheKey = $"search:{searchText}:page:{pageNumber}:size:{pageSize}";
        
        if (_cache.TryGetValue(cacheKey, out PaginationResult<T> cachedResult))
        {
            return cachedResult;
        }
        
        var result = await SearchDirectAsync(searchText, pageNumber, pageSize, cancellationToken);
        
        _cache.Set(cacheKey, result, _cacheExpiry);
        return result;
    }
}
```

## Error Handling and Resilience

### Retry Policies
```csharp
public class ResilientPaginator<T> where T : class
{
    private readonly SearchClient _searchClient;
    private readonly RetryPolicy _retryPolicy;
    
    public async Task<PaginationResult<T>> SearchWithRetryAsync(
        string searchText,
        int pageNumber,
        int pageSize,
        CancellationToken cancellationToken = default)
    {
        return await _retryPolicy.ExecuteAsync(async () =>
        {
            try
            {
                return await SearchDirectAsync(searchText, pageNumber, pageSize, cancellationToken);
            }
            catch (RequestFailedException ex) when (ex.Status == 429)
            {
                // Rate limiting - wait and retry
                var delay = TimeSpan.FromSeconds(Math.Pow(2, retryAttempt));
                await Task.Delay(delay, cancellationToken);
                throw;
            }
        });
    }
}
```

### Circuit Breaker Pattern
```csharp
public class CircuitBreakerPaginator<T> where T : class
{
    private readonly SearchClient _searchClient;
    private readonly CircuitBreakerPolicy _circuitBreaker;
    
    public CircuitBreakerPaginator(SearchClient searchClient)
    {
        _searchClient = searchClient;
        _circuitBreaker = Policy
            .Handle<RequestFailedException>()
            .CircuitBreakerAsync(
                handledEventsAllowedBeforeBreaking: 3,
                durationOfBreak: TimeSpan.FromMinutes(1));
    }
    
    public async Task<PaginationResult<T>> SearchAsync(
        string searchText,
        int pageNumber,
        int pageSize)
    {
        return await _circuitBreaker.ExecuteAsync(async () =>
        {
            return await SearchDirectAsync(searchText, pageNumber, pageSize);
        });
    }
}
```

## Best Practices

### Code Organization
- Use generic types for reusability
- Implement proper async/await patterns
- Follow SOLID principles
- Use dependency injection
- Implement proper logging

### Performance
- Use appropriate page sizes (10-50 for UI, up to 1000 for APIs)
- Implement caching strategies
- Use async operations for I/O
- Monitor performance with metrics
- Implement connection pooling

### Error Handling
- Use structured exception handling
- Implement retry policies with exponential backoff
- Handle rate limiting gracefully
- Validate input parameters
- Log errors with correlation IDs

## Contributing

To contribute to these examples:
1. Follow C# coding conventions
2. Use XML documentation comments
3. Include comprehensive unit tests
4. Follow async/await best practices
5. Update documentation

## Next Steps

After exploring these examples:
1. Try the interactive Jupyter notebooks
2. Implement pagination in your ASP.NET Core application
3. Explore advanced patterns in other modules
4. Contribute improvements and new examples