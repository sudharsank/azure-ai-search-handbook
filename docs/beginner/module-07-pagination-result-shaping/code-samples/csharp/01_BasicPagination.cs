/*
 * Module 7: Basic Pagination with Skip/Top
 * 
 * This example demonstrates fundamental pagination using skip and top parameters.
 * Best for small to medium result sets (< 10,000 results).
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

namespace AzureSearchPagination
{
    /// <summary>
    /// Represents the result of a pagination operation
    /// </summary>
    /// <typeparam name="T">The type of documents in the result</typeparam>
    public class PaginationResult<T>
    {
        public List<T> Documents { get; set; } = new List<T>();
        public int CurrentPage { get; set; }
        public int TotalPages { get; set; }
        public long? TotalResults { get; set; }
        public int PageSize { get; set; }
        public bool HasNextPage { get; set; }
        public bool HasPreviousPage { get; set; }
        public double DurationMs { get; set; }
        public string Query { get; set; } = string.Empty;
    }

    /// <summary>
    /// Performance metrics for pagination operations
    /// </summary>
    public class PaginationMetrics
    {
        public int PageNumber { get; set; }
        public int SkipValue { get; set; }
        public int PageSize { get; set; }
        public double DurationMs { get; set; }
        public int ResultsCount { get; set; }
        public string Query { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Basic paginator implementing skip/top pagination strategy
    /// </summary>
    /// <typeparam name="T">The type of documents to paginate</typeparam>
    public class BasicPaginator<T> where T : class
    {
        private readonly SearchClient _searchClient;
        private readonly List<PaginationMetrics> _metrics;
        
        public int PageSize { get; }
        public int CurrentPage { get; private set; }
        public long? TotalResults { get; private set; }
        public int TotalPages { get; private set; }

        /// <summary>
        /// Initializes a new instance of the BasicPaginator class
        /// </summary>
        /// <param name="searchClient">Azure AI Search client</param>
        /// <param name="pageSize">Number of results per page</param>
        public BasicPaginator(SearchClient searchClient, int pageSize = 10)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
            PageSize = pageSize;
            _metrics = new List<PaginationMetrics>();
        }

        /// <summary>
        /// Loads a specific page of results
        /// </summary>
        /// <param name="pageNumber">Zero-based page number</param>
        /// <param name="searchText">Search query</param>
        /// <param name="includeCount">Whether to include total count</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>Pagination result</returns>
        public async Task<PaginationResult<T>> LoadPageAsync(
            int pageNumber,
            string searchText = "*",
            bool includeCount = true,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            try
            {
                var skip = pageNumber * PageSize;
                
                // Validate pagination parameters
                ValidatePaginationParams(skip, PageSize);
                
                Console.WriteLine($"Loading page {pageNumber + 1}, skip: {skip}, top: {PageSize}");
                
                var stopwatch = Stopwatch.StartNew();
                
                // Configure search options
                var searchOptions = options ?? new SearchOptions();
                searchOptions.Skip = skip;
                searchOptions.Size = PageSize;
                searchOptions.IncludeTotalCount = includeCount;
                
                // Perform search
                var response = await _searchClient.SearchAsync<T>(searchText, searchOptions, cancellationToken);
                var searchResults = response.Value;
                
                // Convert to list and measure duration
                var documents = new List<T>();
                await foreach (var result in searchResults.GetResultsAsync())
                {
                    documents.Add(result.Document);
                }
                
                stopwatch.Stop();
                var duration = stopwatch.Elapsed.TotalMilliseconds;
                
                // Update pagination state
                CurrentPage = pageNumber;
                TotalResults = searchResults.TotalCount;
                if (TotalResults.HasValue)
                {
                    TotalPages = (int)Math.Ceiling((double)TotalResults.Value / PageSize);
                }
                
                // Record metrics
                var metric = new PaginationMetrics
                {
                    PageNumber = pageNumber,
                    SkipValue = skip,
                    PageSize = PageSize,
                    DurationMs = duration,
                    ResultsCount = documents.Count,
                    Query = searchText,
                    Timestamp = DateTime.UtcNow
                };
                _metrics.Add(metric);
                
                Console.WriteLine($"Page loaded in {duration:F1}ms - {documents.Count} results");
                if (TotalResults.HasValue)
                {
                    Console.WriteLine($"Total results: {TotalResults}, Total pages: {TotalPages}");
                }
                
                return new PaginationResult<T>
                {
                    Documents = documents,
                    CurrentPage = pageNumber,
                    TotalPages = TotalPages,
                    TotalResults = TotalResults,
                    PageSize = PageSize,
                    HasNextPage = HasNextPage(pageNumber, documents.Count),
                    HasPreviousPage = pageNumber > 0,
                    DurationMs = duration,
                    Query = searchText
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading page {pageNumber}: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Loads the first page
        /// </summary>
        public async Task<PaginationResult<T>> LoadFirstPageAsync(
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            return await LoadPageAsync(0, searchText, true, cancellationToken, options);
        }

        /// <summary>
        /// Loads the next page
        /// </summary>
        public async Task<PaginationResult<T>> LoadNextPageAsync(
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            if (!HasNextPage())
            {
                throw new InvalidOperationException("No next page available");
            }
            return await LoadPageAsync(CurrentPage + 1, searchText, false, cancellationToken, options);
        }

        /// <summary>
        /// Loads the previous page
        /// </summary>
        public async Task<PaginationResult<T>> LoadPreviousPageAsync(
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            if (!HasPreviousPage())
            {
                throw new InvalidOperationException("No previous page available");
            }
            return await LoadPageAsync(CurrentPage - 1, searchText, false, cancellationToken, options);
        }

        /// <summary>
        /// Loads the last page
        /// </summary>
        public async Task<PaginationResult<T>> LoadLastPageAsync(
            string searchText = "*",
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            if (TotalPages == 0)
            {
                return await LoadFirstPageAsync(searchText, cancellationToken, options);
            }
            return await LoadPageAsync(TotalPages - 1, searchText, false, cancellationToken, options);
        }

        /// <summary>
        /// Checks if there's a next page
        /// </summary>
        public bool HasNextPage()
        {
            if (TotalPages > 0)
            {
                return CurrentPage < TotalPages - 1;
            }
            return false; // Unknown, assume no more pages
        }

        /// <summary>
        /// Checks if there's a previous page
        /// </summary>
        public bool HasPreviousPage()
        {
            return CurrentPage > 0;
        }

        /// <summary>
        /// Gets current pagination information
        /// </summary>
        public Dictionary<string, object> GetPaginationInfo()
        {
            return new Dictionary<string, object>
            {
                ["currentPage"] = CurrentPage + 1, // 1-based for display
                ["totalPages"] = TotalPages,
                ["totalResults"] = TotalResults,
                ["pageSize"] = PageSize,
                ["hasNextPage"] = HasNextPage(),
                ["hasPreviousPage"] = HasPreviousPage()
            };
        }

        /// <summary>
        /// Generates page numbers for pagination UI
        /// </summary>
        public List<PageInfo> GetPageNumbers(int maxVisible = 5)
        {
            if (TotalPages == 0)
            {
                return new List<PageInfo>();
            }

            var startPage = Math.Max(0, CurrentPage - maxVisible / 2);
            var endPage = Math.Min(TotalPages - 1, startPage + maxVisible - 1);

            // Adjust start_page if we're near the end
            if (endPage - startPage < maxVisible - 1)
            {
                startPage = Math.Max(0, endPage - maxVisible + 1);
            }

            var pages = new List<PageInfo>();
            for (int i = startPage; i <= endPage; i++)
            {
                pages.Add(new PageInfo
                {
                    Number = i + 1, // 1-based for display
                    Index = i,      // 0-based for logic
                    IsCurrent = i == CurrentPage
                });
            }

            return pages;
        }

        /// <summary>
        /// Gets performance metrics summary
        /// </summary>
        public Dictionary<string, object> GetPerformanceMetrics()
        {
            if (!_metrics.Any())
            {
                return new Dictionary<string, object>();
            }

            var durations = _metrics.Select(m => m.DurationMs).ToList();
            return new Dictionary<string, object>
            {
                ["totalRequests"] = _metrics.Count,
                ["averageDurationMs"] = durations.Average(),
                ["minDurationMs"] = durations.Min(),
                ["maxDurationMs"] = durations.Max(),
                ["totalResultsRetrieved"] = _metrics.Sum(m => m.ResultsCount)
            };
        }

        private bool HasNextPage(int pageNumber, int resultsCount)
        {
            if (TotalPages > 0)
            {
                return pageNumber < TotalPages - 1;
            }
            // If we don't know total pages, assume there's more if we got a full page
            return resultsCount == PageSize;
        }

        private static void ValidatePaginationParams(int skip, int top)
        {
            if (skip < 0)
            {
                throw new ArgumentException("Skip must be non-negative", nameof(skip));
            }
            if (top < 1 || top > 1000)
            {
                throw new ArgumentException("Top must be between 1 and 1000", nameof(top));
            }
            if (skip + top > 100000)
            {
                throw new ArgumentException("Cannot retrieve results beyond position 100,000");
            }
        }
    }

    /// <summary>
    /// Represents page information for UI display
    /// </summary>
    public class PageInfo
    {
        public int Number { get; set; }
        public int Index { get; set; }
        public bool IsCurrent { get; set; }
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
        public bool? ParkingIncluded { get; set; }
        public bool? SmokingAllowed { get; set; }
        public string[] Tags { get; set; } = Array.Empty<string>();
    }

    /// <summary>
    /// Pagination iterator for automatic traversal
    /// </summary>
    /// <typeparam name="T">Document type</typeparam>
    public class PaginationIterator<T> where T : class
    {
        private readonly BasicPaginator<T> _paginator;
        private readonly string _searchText;
        private readonly SearchOptions? _options;

        public PaginationIterator(BasicPaginator<T> paginator, string searchText = "*", SearchOptions? options = null)
        {
            _paginator = paginator;
            _searchText = searchText;
            _options = options;
        }

        /// <summary>
        /// Enumerates all documents across all pages
        /// </summary>
        public async IAsyncEnumerable<T> GetAllDocumentsAsync(
            [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            int currentPage = 0;
            bool hasMore = true;

            while (hasMore && !cancellationToken.IsCancellationRequested)
            {
                var result = await _paginator.LoadPageAsync(
                    currentPage, 
                    _searchText, 
                    includeCount: false, 
                    cancellationToken, 
                    _options);

                foreach (var document in result.Documents)
                {
                    yield return document;
                }

                hasMore = result.HasNextPage;
                currentPage++;
            }
        }
    }

    /// <summary>
    /// Demonstration class for basic pagination
    /// </summary>
    public class BasicPaginationDemo
    {
        private readonly SearchClient _searchClient;

        public BasicPaginationDemo(SearchClient searchClient)
        {
            _searchClient = searchClient;
        }

        /// <summary>
        /// Demonstrates basic pagination functionality
        /// </summary>
        public async Task DemonstrateBasicPaginationAsync()
        {
            Console.WriteLine("=== Basic Pagination Demo ===\n");

            var paginator = new BasicPaginator<Hotel>(_searchClient, pageSize: 5);

            try
            {
                // Load first page
                Console.WriteLine("1. Loading first page...");
                var page = await paginator.LoadFirstPageAsync("*");
                DisplayPageResults(page);

                // Load next few pages
                Console.WriteLine("\n2. Loading next page...");
                page = await paginator.LoadNextPageAsync("*");
                DisplayPageResults(page);

                Console.WriteLine("\n3. Loading one more page...");
                page = await paginator.LoadNextPageAsync("*");
                DisplayPageResults(page);

                // Go back to previous page
                Console.WriteLine("\n4. Going back to previous page...");
                page = await paginator.LoadPreviousPageAsync("*");
                DisplayPageResults(page);

                // Jump to last page
                Console.WriteLine("\n5. Jumping to last page...");
                page = await paginator.LoadLastPageAsync("*");
                DisplayPageResults(page);

                // Show pagination info
                Console.WriteLine("\n6. Pagination Info:");
                var info = paginator.GetPaginationInfo();
                foreach (var kvp in info)
                {
                    Console.WriteLine($"  {kvp.Key}: {kvp.Value}");
                }

                // Show page numbers for UI
                Console.WriteLine("\n7. Page Numbers for UI:");
                var pageNumbers = paginator.GetPageNumbers();
                foreach (var pageInfo in pageNumbers)
                {
                    var marker = pageInfo.IsCurrent ? " (current)" : "";
                    Console.WriteLine($"  Page {pageInfo.Number}{marker}");
                }

                // Show performance metrics
                Console.WriteLine("\n8. Performance Metrics:");
                var metrics = paginator.GetPerformanceMetrics();
                foreach (var kvp in metrics)
                {
                    Console.WriteLine($"  {kvp.Key}: {kvp.Value}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates search with pagination
        /// </summary>
        public async Task DemonstrateSearchPaginationAsync()
        {
            Console.WriteLine("\n=== Search with Pagination Demo ===\n");

            var paginator = new BasicPaginator<Hotel>(_searchClient, pageSize: 3);

            try
            {
                const string searchQuery = "luxury";
                Console.WriteLine($"Searching for: \"{searchQuery}\"");

                var page = await paginator.LoadFirstPageAsync(searchQuery);
                DisplayPageResults(page);

                // Load next page of search results
                if (page.HasNextPage)
                {
                    Console.WriteLine("\nLoading next page of search results...");
                    page = await paginator.LoadNextPageAsync(searchQuery);
                    DisplayPageResults(page);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Search pagination error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates error handling scenarios
        /// </summary>
        public async Task DemonstrateErrorHandlingAsync()
        {
            Console.WriteLine("\n=== Error Handling Demo ===\n");

            // Test invalid page size
            try
            {
                var invalidPaginator = new BasicPaginator<Hotel>(_searchClient, pageSize: 2000); // Too large
                await invalidPaginator.LoadFirstPageAsync("*");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Expected error for large page size: {ex.Message}");
            }

            // Test going beyond available pages
            try
            {
                var paginator = new BasicPaginator<Hotel>(_searchClient, pageSize: 10);
                await paginator.LoadPageAsync(999999, "*"); // Very high page number
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Expected error for invalid page: {ex.Message}");
            }

            // Test previous page when on first page
            try
            {
                var paginator = new BasicPaginator<Hotel>(_searchClient, pageSize: 10);
                await paginator.LoadFirstPageAsync("*");
                await paginator.LoadPreviousPageAsync("*");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Expected error for previous page on first page: {ex.Message}");
            }
        }

        /// <summary>
        /// Compares performance of different page sizes
        /// </summary>
        public async Task ComparePageSizesAsync()
        {
            Console.WriteLine("\n=== Page Size Performance Comparison ===\n");

            var pageSizes = new[] { 5, 10, 20, 50 };

            foreach (var pageSize in pageSizes)
            {
                var paginator = new BasicPaginator<Hotel>(_searchClient, pageSize);

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    var page = await paginator.LoadFirstPageAsync("*");
                    stopwatch.Stop();

                    Console.WriteLine($"Page size {pageSize}: {stopwatch.ElapsedMilliseconds}ms, {page.Documents.Count} results");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Page size {pageSize}: Error - {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Demonstrates pagination iterator
        /// </summary>
        public async Task DemonstratePaginationIteratorAsync()
        {
            Console.WriteLine("\n=== Pagination Iterator Demo ===\n");

            var paginator = new BasicPaginator<Hotel>(_searchClient, pageSize: 5);
            var iterator = new PaginationIterator<Hotel>(paginator, "hotel");

            try
            {
                int count = 0;
                await foreach (var hotel in iterator.GetAllDocumentsAsync())
                {
                    Console.WriteLine($"{count + 1}. {hotel.HotelName}");
                    count++;

                    // Limit for demo
                    if (count >= 15)
                    {
                        break;
                    }
                }

                Console.WriteLine($"\nProcessed {count} documents across multiple pages");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Iterator error: {ex.Message}");
            }
        }

        private static void DisplayPageResults<T>(PaginationResult<T> result) where T : Hotel
        {
            Console.WriteLine($"Page {result.CurrentPage + 1} of {result.TotalPages}");
            Console.WriteLine($"Showing {result.Documents.Count} results");
            if (result.TotalResults.HasValue)
            {
                Console.WriteLine($"Total results: {result.TotalResults}");
            }
            Console.WriteLine($"Load time: {result.DurationMs:F1}ms");

            for (int i = 0; i < result.Documents.Count; i++)
            {
                var hotel = result.Documents[i];
                var rating = hotel.Rating?.ToString("F1") ?? "N/A";
                Console.WriteLine($"  {i + 1}. {hotel.HotelName} (Rating: {rating})");
            }

            Console.WriteLine($"Has Next: {result.HasNextPage}, Has Previous: {result.HasPreviousPage}");
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
                var demo = new BasicPaginationDemo(searchClient);
                await demo.DemonstrateBasicPaginationAsync();
                await demo.DemonstrateSearchPaginationAsync();
                await demo.DemonstrateErrorHandlingAsync();
                await demo.ComparePageSizesAsync();
                await demo.DemonstratePaginationIteratorAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Demo failed: {ex.Message}");
            }
        }
    }
}