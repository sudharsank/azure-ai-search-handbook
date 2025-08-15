/*
 * Module 7: Range-Based Pagination for Large Datasets
 * 
 * This example demonstrates range-based pagination using filters and sorting,
 * which provides better performance for large datasets and deep pagination scenarios.
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace AzureSearchRangePagination
{
    /// <summary>
    /// Represents the result of a range pagination operation
    /// </summary>
    /// <typeparam name="T">The type of documents in the result</typeparam>
    public class RangePaginationResult<T>
    {
        public List<T> Documents { get; set; } = new List<T>();
        public object? LastSortValue { get; set; }
        public bool HasNextPage { get; set; }
        public int PageSize { get; set; }
        public double DurationMs { get; set; }
        public string Query { get; set; } = string.Empty;
        public string SortField { get; set; } = string.Empty;
        public string? FilterExpression { get; set; }
        public int PageNumber { get; set; }
    }

    /// <summary>
    /// Configuration for range pagination
    /// </summary>
    public class RangePaginationConfig
    {
        public string SortField { get; set; } = "hotelId";
        public string SortDirection { get; set; } = "asc"; // 'asc' or 'desc'
        public int PageSize { get; set; } = 10;
        public string? FilterBase { get; set; }
        public bool IncludeSortValue { get; set; } = true;
    }

    /// <summary>
    /// Range-based paginator for efficient pagination of large datasets
    /// </summary>
    /// <typeparam name="T">The type of documents to work with</typeparam>
    public class RangePaginator<T> where T : class
    {
        private readonly SearchClient _searchClient;
        private readonly RangePaginationConfig _config;
        private int _currentPage;
        private object? _lastSortValue;
        private readonly List<object> _pageHistory;

        public RangePaginator(SearchClient searchClient, RangePaginationConfig config)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
            _config = config ?? throw new ArgumentNullException(nameof(config));
            _currentPage = 0;
            _lastSortValue = null;
            _pageHistory = new List<object>();
        }

        /// <summary>
        /// Load the first page of results
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>RangePaginationResult for first page</returns>
        public async Task<RangePaginationResult<T>> LoadFirstPageAsync(
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            _currentPage = 0;
            _lastSortValue = null;
            _pageHistory.Clear();

            return await LoadPageAsync(searchText, null, cancellationToken, options);
        }

        /// <summary>
        /// Load the next page of results
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>RangePaginationResult for next page or null if no more pages</returns>
        public async Task<RangePaginationResult<T>?> LoadNextPageAsync(
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            if (_lastSortValue == null)
            {
                throw new InvalidOperationException("Must load first page before loading next page");
            }

            // Store current position in history for potential backward navigation
            _pageHistory.Add(_lastSortValue);

            var result = await LoadPageAsync(searchText, _lastSortValue, cancellationToken, options);

            if (result != null && result.Documents.Any())
            {
                _currentPage++;
                return result;
            }
            else
            {
                // No more results, remove from history
                if (_pageHistory.Any())
                {
                    _pageHistory.RemoveAt(_pageHistory.Count - 1);
                }
                return null;
            }
        }

        /// <summary>
        /// Load page starting after a specific sort value
        /// </summary>
        /// <param name="sortValue">Sort value to start after</param>
        /// <param name="searchText">Search query</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>RangePaginationResult starting after sort_value</returns>
        public async Task<RangePaginationResult<T>> LoadPageAfterAsync(
            object sortValue,
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            return await LoadPageAsync(searchText, sortValue, cancellationToken, options);
        }

        /// <summary>
        /// Internal method to load a page with range filtering
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="afterValue">Value to start after (null for first page)</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>RangePaginationResult</returns>
        private async Task<RangePaginationResult<T>> LoadPageAsync(
            string searchText,
            object? afterValue,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            try
            {
                Console.WriteLine($"Loading range page: after_value={afterValue}");

                var stopwatch = Stopwatch.StartNew();

                // Build filter expression
                var filterParts = new List<string>();

                // Add base filter if provided
                if (!string.IsNullOrEmpty(_config.FilterBase))
                {
                    filterParts.Add(_config.FilterBase);
                }

                // Add range filter
                if (afterValue != null)
                {
                    var operatorStr = _config.SortDirection == "asc" ? "gt" : "lt";
                    string filterValue;

                    // Handle different data types
                    if (afterValue is string stringValue)
                    {
                        filterValue = $"'{stringValue}'";
                    }
                    else if (afterValue is int || afterValue is long || afterValue is double || afterValue is float)
                    {
                        filterValue = afterValue.ToString()!;
                    }
                    else
                    {
                        filterValue = $"'{afterValue}'";
                    }

                    var rangeFilter = $"{_config.SortField} {operatorStr} {filterValue}";
                    filterParts.Add(rangeFilter);
                }

                // Combine filters
                var filterExpression = filterParts.Any() ? string.Join(" and ", filterParts) : null;

                // Build sort expression
                var sortExpression = $"{_config.SortField} {_config.SortDirection}";

                Console.WriteLine($"Filter: {filterExpression}");
                Console.WriteLine($"Sort: {sortExpression}");

                // Configure search options
                var searchOptions = options ?? new SearchOptions();
                searchOptions.Size = _config.PageSize;
                searchOptions.OrderBy.Clear();
                searchOptions.OrderBy.Add(sortExpression);

                if (!string.IsNullOrEmpty(filterExpression))
                {
                    searchOptions.Filter = filterExpression;
                }

                if (_config.IncludeSortValue)
                {
                    // Include sort field in results if not already selected
                    if (searchOptions.Select.Any() && !searchOptions.Select.Contains(_config.SortField))
                    {
                        searchOptions.Select.Add(_config.SortField);
                    }
                }

                // Perform search
                var response = await _searchClient.SearchAsync<T>(searchText, searchOptions, cancellationToken);
                var searchResults = response.Value;

                var documents = new List<T>();
                await foreach (var result in searchResults.GetResultsAsync())
                {
                    documents.Add(result.Document);
                }

                stopwatch.Stop();
                var duration = stopwatch.Elapsed.TotalMilliseconds;

                // Get last sort value for next page
                object? newLastSortValue = null;
                if (documents.Any())
                {
                    var lastDoc = documents.Last();
                    newLastSortValue = GetSortValue(lastDoc, _config.SortField);
                }

                // Update state
                if (newLastSortValue != null)
                {
                    _lastSortValue = newLastSortValue;
                }

                // Determine if there are more pages
                var hasNextPage = documents.Count == _config.PageSize;

                Console.WriteLine($"Loaded {documents.Count} documents in {duration:F1}ms");
                Console.WriteLine($"Last sort value: {newLastSortValue}");
                Console.WriteLine($"Has next page: {hasNextPage}");

                return new RangePaginationResult<T>
                {
                    Documents = documents,
                    LastSortValue = newLastSortValue,
                    HasNextPage = hasNextPage,
                    PageSize = _config.PageSize,
                    DurationMs = duration,
                    Query = searchText,
                    SortField = _config.SortField,
                    FilterExpression = filterExpression,
                    PageNumber = _currentPage
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Range pagination error: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Reset paginator state
        /// </summary>
        public void Reset()
        {
            _currentPage = 0;
            _lastSortValue = null;
            _pageHistory.Clear();
        }

        private object? GetSortValue(T document, string fieldName)
        {
            // Use reflection to get the sort field value
            var property = document.GetType().GetProperty(fieldName);
            return property?.GetValue(document);
        }
    }

    /// <summary>
    /// Cursor-based paginator using search_after functionality (conceptual)
    /// </summary>
    /// <typeparam name="T">The type of documents to work with</typeparam>
    public class CursorPaginator<T> where T : class
    {
        private readonly SearchClient _searchClient;
        private readonly List<string> _sortFields;
        private object[]? _currentCursor;
        private int _pageSize;

        public CursorPaginator(SearchClient searchClient, List<string> sortFields)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
            _sortFields = sortFields ?? throw new ArgumentNullException(nameof(sortFields));
            _pageSize = 10;
        }

        /// <summary>
        /// Load page using cursor pagination (conceptual implementation)
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="cursor">Cursor values from previous page</param>
        /// <param name="pageSize">Number of results per page</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>Page result with cursor information</returns>
        public async Task<Dictionary<string, object>> LoadPageAsync(
            string searchText = "*",
            object[]? cursor = null,
            int pageSize = 10,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            try
            {
                Console.WriteLine($"Loading cursor page: cursor={string.Join(",", cursor ?? Array.Empty<object>())}");

                var stopwatch = Stopwatch.StartNew();

                // Build sort expressions
                var sortExpressions = _sortFields.Select(field => $"{field} asc").ToList();

                var searchOptions = options ?? new SearchOptions();
                searchOptions.Size = pageSize;
                searchOptions.OrderBy.Clear();
                foreach (var sortExpr in sortExpressions)
                {
                    searchOptions.OrderBy.Add(sortExpr);
                }

                // Add search_after if cursor provided
                // Note: search_after is not directly available in .NET SDK
                // This is a conceptual implementation
                if (cursor != null)
                {
                    Console.WriteLine("Note: search_after not directly supported in .NET SDK");
                    // In a real implementation, you would use the REST API directly
                    // or wait for SDK support for search_after
                }

                var response = await _searchClient.SearchAsync<T>(searchText, searchOptions, cancellationToken);
                var searchResults = response.Value;

                var documents = new List<T>();
                await foreach (var result in searchResults.GetResultsAsync())
                {
                    documents.Add(result.Document);
                }

                stopwatch.Stop();
                var duration = stopwatch.Elapsed.TotalMilliseconds;

                // Generate cursor for next page
                object[]? nextCursor = null;
                if (documents.Any())
                {
                    var lastDoc = documents.Last();
                    nextCursor = _sortFields.Select(field => GetSortValue(lastDoc, field)).ToArray();
                }

                var hasNextPage = documents.Count == pageSize;

                return new Dictionary<string, object>
                {
                    ["documents"] = documents,
                    ["nextCursor"] = nextCursor,
                    ["hasNextPage"] = hasNextPage,
                    ["duration"] = duration,
                    ["pageSize"] = pageSize
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Cursor pagination error: {ex.Message}");
                throw;
            }
        }

        private object? GetSortValue(T document, string fieldName)
        {
            var property = document.GetType().GetProperty(fieldName);
            return property?.GetValue(document);
        }
    }

    /// <summary>
    /// Hybrid paginator that chooses the best strategy based on context
    /// </summary>
    /// <typeparam name="T">The type of documents to work with</typeparam>
    public class HybridPaginator<T> where T : class
    {
        private readonly SearchClient _searchClient;

        public HybridPaginator(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Determine optimal pagination strategy
        /// </summary>
        /// <param name="totalResults">Total number of results</param>
        /// <param name="pageNumber">Current page number</param>
        /// <param name="sortField">Available sort field</param>
        /// <returns>Recommended strategy name</returns>
        public string GetOptimalStrategy(long? totalResults, int pageNumber, string? sortField)
        {
            // Use skip/top for small datasets and early pages
            if (totalResults.HasValue && totalResults < 1000 && pageNumber < 10)
            {
                return "skip_top";
            }

            // Use range pagination for large datasets or deep pagination
            if (!string.IsNullOrEmpty(sortField) && (!totalResults.HasValue || totalResults > 1000 || pageNumber > 10))
            {
                return "range";
            }

            // Default to skip/top
            return "skip_top";
        }

        /// <summary>
        /// Create paginator instance for strategy
        /// </summary>
        /// <param name="strategy">Strategy name</param>
        /// <param name="config">Configuration parameters</param>
        /// <returns>Paginator instance</returns>
        public object CreatePaginator(string strategy, Dictionary<string, object> config)
        {
            if (strategy == "range")
            {
                var rangeConfig = new RangePaginationConfig
                {
                    SortField = config.ContainsKey("sortField") ? (string)config["sortField"] : "hotelId",
                    SortDirection = config.ContainsKey("sortDirection") ? (string)config["sortDirection"] : "asc",
                    PageSize = config.ContainsKey("pageSize") ? (int)config["pageSize"] : 10,
                    FilterBase = config.ContainsKey("filterBase") ? (string)config["filterBase"] : null
                };
                return new RangePaginator<T>(_searchClient, rangeConfig);
            }
            else if (strategy == "cursor")
            {
                var sortFields = config.ContainsKey("sortFields") ? 
                    (List<string>)config["sortFields"] : 
                    new List<string> { "hotelId" };
                return new CursorPaginator<T>(_searchClient, sortFields);
            }
            else
            {
                throw new NotImplementedException("Basic paginator not implemented in this module");
            }
        }
    }

    /// <summary>
    /// Hotel model for demonstration
    /// </summary>
    public class Hotel
    {
        public string HotelId { get; set; } = string.Empty;
        public string HotelName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public double? Rating { get; set; }
        public GeographyPoint? Location { get; set; }
        public DateTimeOffset? LastRenovationDate { get; set; }
    }

    /// <summary>
    /// Demonstration class for range pagination
    /// </summary>
    public class RangePaginationDemo
    {
        private readonly SearchClient _searchClient;

        public RangePaginationDemo(SearchClient searchClient)
        {
            _searchClient = searchClient;
        }

        /// <summary>
        /// Demonstrates range-based pagination
        /// </summary>
        public async Task DemonstrateRangePaginationAsync()
        {
            Console.WriteLine("=== Range-Based Pagination Demo ===\n");

            // Configure range pagination
            var config = new RangePaginationConfig
            {
                SortField = "hotelId", // Use a unique, sortable field
                SortDirection = "asc",
                PageSize = 5
            };

            var paginator = new RangePaginator<Hotel>(_searchClient, config);

            try
            {
                // Load first page
                Console.WriteLine("1. Loading first page:");
                var page1 = await paginator.LoadFirstPageAsync("*");
                DisplayRangePage(page1);

                // Load next few pages
                Console.WriteLine("\n2. Loading next page:");
                var page2 = await paginator.LoadNextPageAsync("*");
                if (page2 != null)
                {
                    DisplayRangePage(page2);
                }

                Console.WriteLine("\n3. Loading another page:");
                var page3 = await paginator.LoadNextPageAsync("*");
                if (page3 != null)
                {
                    DisplayRangePage(page3);
                }

                // Demonstrate jumping to specific position
                Console.WriteLine("\n4. Jumping to specific position:");
                if (page2?.LastSortValue != null)
                {
                    var jumpPage = await paginator.LoadPageAfterAsync(page2.LastSortValue, "*");
                    DisplayRangePage(jumpPage);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Range pagination demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates range pagination with additional filters
        /// </summary>
        public async Task DemonstrateFilteredRangePaginationAsync()
        {
            Console.WriteLine("\n=== Filtered Range Pagination Demo ===\n");

            try
            {
                // Configure with base filter
                var config = new RangePaginationConfig
                {
                    SortField = "hotelId",
                    SortDirection = "asc",
                    PageSize = 3,
                    FilterBase = "rating ge 4.0" // Only high-rated hotels
                };

                var paginator = new RangePaginator<Hotel>(_searchClient, config);

                Console.WriteLine("Range pagination with rating filter (>= 4.0):");

                // Load first page
                var page = await paginator.LoadFirstPageAsync("luxury");
                DisplayRangePage(page);

                // Load next page
                if (page.HasNextPage)
                {
                    Console.WriteLine("\nNext page:");
                    page = await paginator.LoadNextPageAsync("luxury");
                    if (page != null)
                    {
                        DisplayRangePage(page);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Filtered range pagination demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates cursor-based pagination concept
        /// </summary>
        public async Task DemonstrateCursorPaginationAsync()
        {
            Console.WriteLine("\n=== Cursor Pagination Demo ===\n");

            try
            {
                // Create cursor paginator
                var cursorPaginator = new CursorPaginator<Hotel>(_searchClient, new List<string> { "rating", "hotelId" });

                Console.WriteLine("Cursor pagination (conceptual):");

                // Load first page
                var page1 = await cursorPaginator.LoadPageAsync("*", cursor: null, pageSize: 5);

                Console.WriteLine($"Page 1: {((List<Hotel>)page1["documents"]).Count} results");
                Console.WriteLine($"Duration: {page1["duration"]}ms");
                Console.WriteLine($"Next cursor: {string.Join(",", (object[])page1["nextCursor"])}");

                // Show sample results
                var documents = (List<Hotel>)page1["documents"];
                for (int i = 0; i < documents.Count; i++)
                {
                    var doc = documents[i];
                    Console.WriteLine($"  {i + 1}. {doc.HotelName} (Rating: {doc.Rating}, ID: {doc.HotelId})");
                }

                // Load next page with cursor
                if ((bool)page1["hasNextPage"] && page1["nextCursor"] != null)
                {
                    Console.WriteLine("\nPage 2 (with cursor):");
                    var page2 = await cursorPaginator.LoadPageAsync("*", cursor: (object[])page1["nextCursor"], pageSize: 5);

                    Console.WriteLine($"Results: {((List<Hotel>)page2["documents"]).Count}");
                    Console.WriteLine($"Duration: {page2["duration"]}ms");
                    Console.WriteLine($"Next cursor: {string.Join(",", (object[])page2["nextCursor"])}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Cursor pagination demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates hybrid pagination strategy selection
        /// </summary>
        public async Task DemonstrateHybridStrategyAsync()
        {
            Console.WriteLine("\n=== Hybrid Strategy Demo ===\n");

            try
            {
                var hybrid = new HybridPaginator<Hotel>(_searchClient);

                // Test different scenarios
                var scenarios = new[]
                {
                    new { TotalResults = (long?)100, PageNumber = 1, SortField = "hotelId" },
                    new { TotalResults = (long?)5000, PageNumber = 1, SortField = "hotelId" },
                    new { TotalResults = (long?)1000, PageNumber = 20, SortField = "hotelId" },
                    new { TotalResults = (long?)10000, PageNumber = 5, SortField = (string?)null },
                };

                Console.WriteLine("Strategy recommendations:");
                for (int i = 0; i < scenarios.Length; i++)
                {
                    var scenario = scenarios[i];
                    var strategy = hybrid.GetOptimalStrategy(scenario.TotalResults, scenario.PageNumber, scenario.SortField);
                    Console.WriteLine($"Scenario {i + 1}: TotalResults={scenario.TotalResults}, PageNumber={scenario.PageNumber}, SortField={scenario.SortField} -> {strategy}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Hybrid strategy demo error: {ex.Message}");
            }
        }

        private void DisplayRangePage<T>(RangePaginationResult<T> page) where T : Hotel
        {
            Console.WriteLine($"Page {page.PageNumber + 1}");
            Console.WriteLine($"Results: {page.Documents.Count}");
            Console.WriteLine($"Duration: {page.DurationMs:F1}ms");
            Console.WriteLine($"Sort field: {page.SortField}");
            Console.WriteLine($"Last sort value: {page.LastSortValue}");
            Console.WriteLine($"Has next page: {page.HasNextPage}");

            if (!string.IsNullOrEmpty(page.FilterExpression))
            {
                Console.WriteLine($"Filter: {page.FilterExpression}");
            }

            // Show sample results
            for (int i = 0; i < page.Documents.Count; i++)
            {
                var doc = page.Documents[i];
                var hotelId = doc.HotelId ?? "Unknown";
                var hotelName = doc.HotelName ?? "Unknown";
                var sortValue = GetSortValue(doc, page.SortField) ?? "N/A";
                Console.WriteLine($"  {i + 1}. {hotelName} (ID: {hotelId}, Sort: {sortValue})");
            }
        }

        private object? GetSortValue(Hotel document, string fieldName)
        {
            var property = document.GetType().GetProperty(fieldName);
            return property?.GetValue(document);
        }
    }

    /// <summary>
    /// Utility class for range pagination patterns
    /// </summary>
    public static class RangePaginationHelper
    {
        public static List<string> GetSortableFields() => new List<string> { "hotelId", "rating", "lastRenovationDate", "hotelName" };

        public static string BuildRangeFilter(string field, object value, string direction = "asc")
        {
            var operatorStr = direction == "asc" ? "gt" : "lt";

            if (value is string)
            {
                return $"{field} {operatorStr} '{value}'";
            }
            else
            {
                return $"{field} {operatorStr} {value}";
            }
        }

        public static int EstimatePagePosition(object sortValue, object minValue, object maxValue, int totalCount, int pageSize)
        {
            try
            {
                if (sortValue is int intSort && minValue is int intMin && maxValue is int intMax)
                {
                    if (intMax > intMin)
                    {
                        var ratio = (double)(intSort - intMin) / (intMax - intMin);
                        var estimatedPosition = (int)(ratio * totalCount);
                        return estimatedPosition / pageSize;
                    }
                }
                return 0;
            }
            catch
            {
                return 0;
            }
        }

        public static bool ValidateSortField(string field, string fieldType)
        {
            var suitableTypes = new[] { "Edm.String", "Edm.Int32", "Edm.Int64", "Edm.Double", "Edm.DateTimeOffset", "Edm.Boolean" };
            return suitableTypes.Contains(fieldType);
        }
    }

    /// <summary>
    /// Program entry point for demonstration
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            try
            {
                // Configuration
                var configuration = new ConfigurationBuilder()
                    .AddJsonFile("appsettings.json", optional: true)
                    .AddEnvironmentVariables()
                    .Build();

                var serviceName = configuration["AzureSearch:ServiceName"] ?? 
                                Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_NAME");
                var indexName = configuration["AzureSearch:IndexName"] ?? 
                              Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX_NAME") ?? 
                              "hotels-sample";
                var apiKey = configuration["AzureSearch:ApiKey"] ?? 
                           Environment.GetEnvironmentVariable("AZURE_SEARCH_API_KEY");

                if (string.IsNullOrEmpty(serviceName) || string.IsNullOrEmpty(apiKey))
                {
                    Console.WriteLine("Please configure Azure Search service name and API key");
                    return;
                }

                // Initialize search client
                var endpoint = new Uri($"https://{serviceName}.search.windows.net");
                var credential = new AzureKeyCredential(apiKey);
                var searchClient = new SearchClient(endpoint, indexName, credential);

                // Run demonstrations
                var demo = new RangePaginationDemo(searchClient);
                await demo.DemonstrateRangePaginationAsync();
                await demo.DemonstrateFilteredRangePaginationAsync();
                await demo.DemonstrateCursorPaginationAsync();
                await demo.DemonstrateHybridStrategyAsync();

                // Show helper usage
                Console.WriteLine("\n=== Range Pagination Helper Demo ===\n");
                Console.WriteLine("Sortable fields: " + string.Join(", ", RangePaginationHelper.GetSortableFields()));
                Console.WriteLine("Range filter example: " + RangePaginationHelper.BuildRangeFilter("hotelId", "hotel_100", "asc"));
                Console.WriteLine("Page estimation: " + RangePaginationHelper.EstimatePagePosition(50, 0, 100, 1000, 10));
                Console.WriteLine("Field validation: " + RangePaginationHelper.ValidateSortField("rating", "Edm.Double"));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Demo failed: {ex.Message}");
            }
        }
    }
}