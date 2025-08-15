/*
 * Module 7: Result Counting and Metadata
 * 
 * This example demonstrates how to implement result counting, manage total counts,
 * and work with search metadata for better user experience and performance optimization.
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

namespace AzureSearchResultCounting
{
    /// <summary>
    /// Represents the result of a counting operation
    /// </summary>
    /// <typeparam name="T">The type of documents in the result</typeparam>
    public class CountingResult<T>
    {
        public List<T> Documents { get; set; } = new List<T>();
        public long? TotalCount { get; set; }
        public long? EstimatedCount { get; set; }
        public bool HasMoreResults { get; set; }
        public double DurationMs { get; set; }
        public string Query { get; set; } = string.Empty;
        public int PageSize { get; set; }
        public int Skip { get; set; }
        public string CountAccuracy { get; set; } = "unknown"; // 'exact', 'estimate', 'unknown'
    }

    /// <summary>
    /// Performance metrics for counting operations
    /// </summary>
    public class CountingMetrics
    {
        public string Query { get; set; } = string.Empty;
        public double WithCountDuration { get; set; }
        public double WithoutCountDuration { get; set; }
        public double CountOverheadMs { get; set; }
        public double CountOverheadPercentage { get; set; }
        public long? TotalResults { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Result counter for managing search result counts and metadata
    /// </summary>
    /// <typeparam name="T">The type of documents to work with</typeparam>
    public class ResultCounter<T> where T : class
    {
        private readonly SearchClient _searchClient;
        private readonly Dictionary<string, Dictionary<string, object>> _countCache;
        private readonly List<CountingMetrics> _metrics;

        public ResultCounter(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
            _countCache = new Dictionary<string, Dictionary<string, object>>();
            _metrics = new List<CountingMetrics>();
        }

        /// <summary>
        /// Search with optional result counting
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="includeCount">Whether to include total count</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>CountingResult with count information</returns>
        public async Task<CountingResult<T>> SearchWithCountAsync(
            string searchText,
            bool includeCount = true,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            try
            {
                Console.WriteLine($"Searching with count={includeCount}: '{searchText}'");

                var stopwatch = Stopwatch.StartNew();

                // Configure search options
                var searchOptions = options ?? new SearchOptions();
                searchOptions.IncludeTotalCount = includeCount;
                searchOptions.Size = searchOptions.Size ?? 10;
                searchOptions.Skip = searchOptions.Skip ?? 0;

                // Perform search
                var response = await _searchClient.SearchAsync<T>(searchText, searchOptions, cancellationToken);
                var searchResults = response.Value;

                // Convert to list and get count
                var documents = new List<T>();
                await foreach (var result in searchResults.GetResultsAsync())
                {
                    documents.Add(result.Document);
                }

                var totalCount = searchResults.TotalCount;
                stopwatch.Stop();
                var duration = stopwatch.Elapsed.TotalMilliseconds;

                // Determine count accuracy
                var countAccuracy = includeCount && totalCount.HasValue ? "exact" : "unknown";

                // Estimate if we have more results
                var pageSize = searchOptions.Size ?? 10;
                var skip = searchOptions.Skip ?? 0;
                var hasMore = documents.Count == pageSize;

                if (totalCount.HasValue)
                {
                    hasMore = (skip + documents.Count) < totalCount.Value;
                }

                Console.WriteLine($"Search completed in {duration:F1}ms");
                if (totalCount.HasValue)
                {
                    Console.WriteLine($"Total count: {totalCount}");
                }
                else
                {
                    Console.WriteLine("Count not requested/available");
                }

                return new CountingResult<T>
                {
                    Documents = documents,
                    TotalCount = totalCount,
                    EstimatedCount = null, // Could implement estimation logic
                    HasMoreResults = hasMore,
                    DurationMs = duration,
                    Query = searchText,
                    PageSize = pageSize,
                    Skip = skip,
                    CountAccuracy = countAccuracy
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Search with count error: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Compare performance with and without counting
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="iterations">Number of test iterations</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>CountingMetrics with performance comparison</returns>
        public async Task<CountingMetrics> CompareCountPerformanceAsync(
            string searchText,
            int iterations = 3,
            CancellationToken cancellationToken = default)
        {
            Console.WriteLine($"Comparing count performance for: '{searchText}'");

            var withCountTimes = new List<double>();
            var withoutCountTimes = new List<double>();
            long? totalResults = null;

            // Test with counting
            for (int i = 0; i < iterations; i++)
            {
                var result = await SearchWithCountAsync(searchText, includeCount: true, cancellationToken,
                    new SearchOptions { Size = 10 });
                withCountTimes.Add(result.DurationMs);
                totalResults ??= result.TotalCount;
            }

            // Test without counting
            for (int i = 0; i < iterations; i++)
            {
                var result = await SearchWithCountAsync(searchText, includeCount: false, cancellationToken,
                    new SearchOptions { Size = 10 });
                withoutCountTimes.Add(result.DurationMs);
            }

            // Calculate averages
            var avgWithCount = withCountTimes.Average();
            var avgWithoutCount = withoutCountTimes.Average();

            var countOverhead = avgWithCount - avgWithoutCount;
            var overheadPercentage = avgWithoutCount > 0 ? (countOverhead / avgWithoutCount) * 100 : 0;

            var metrics = new CountingMetrics
            {
                Query = searchText,
                WithCountDuration = avgWithCount,
                WithoutCountDuration = avgWithoutCount,
                CountOverheadMs = countOverhead,
                CountOverheadPercentage = overheadPercentage,
                TotalResults = totalResults,
                Timestamp = DateTime.UtcNow
            };

            _metrics.Add(metrics);

            Console.WriteLine($"With count: {avgWithCount:F1}ms");
            Console.WriteLine($"Without count: {avgWithoutCount:F1}ms");
            Console.WriteLine($"Count overhead: {countOverhead:F1}ms ({overheadPercentage:F1}%)");

            return metrics;
        }

        /// <summary>
        /// Estimate total results without expensive counting
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="samplePages">Number of pages to sample</param>
        /// <param name="pageSize">Size of each sample page</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Estimation results</returns>
        public async Task<Dictionary<string, object>> EstimateTotalResultsAsync(
            string searchText,
            int samplePages = 3,
            int pageSize = 50,
            CancellationToken cancellationToken = default)
        {
            Console.WriteLine($"Estimating total results for: '{searchText}'");

            try
            {
                var estimationData = new Dictionary<string, object>
                {
                    ["query"] = searchText,
                    ["samplePages"] = samplePages,
                    ["pageSize"] = pageSize,
                    ["pagesSampled"] = 0,
                    ["totalDocumentsSeen"] = 0,
                    ["estimatedTotal"] = null,
                    ["confidence"] = "unknown",
                    ["method"] = "sampling"
                };

                var lastPageSize = pageSize;

                for (int page = 0; page < samplePages; page++)
                {
                    var result = await SearchWithCountAsync(
                        searchText,
                        includeCount: false,
                        cancellationToken,
                        new SearchOptions
                        {
                            Skip = page * pageSize,
                            Size = pageSize
                        });

                    estimationData["pagesSampled"] = (int)estimationData["pagesSampled"] + 1;
                    estimationData["totalDocumentsSeen"] = (int)estimationData["totalDocumentsSeen"] + result.Documents.Count;

                    // If we get less than a full page, we've reached the end
                    if (result.Documents.Count < pageSize)
                    {
                        estimationData["estimatedTotal"] = (int)estimationData["totalDocumentsSeen"];
                        estimationData["confidence"] = "exact";
                        estimationData["method"] = "complete_sampling";
                        break;
                    }

                    lastPageSize = result.Documents.Count;
                }

                // If we didn't reach the end, estimate based on consistent page sizes
                if (estimationData["estimatedTotal"] == null)
                {
                    if (lastPageSize == pageSize)
                    {
                        // Assume there are more pages, make a conservative estimate
                        var totalSeen = (int)estimationData["totalDocumentsSeen"];
                        var pagesSampled = (int)estimationData["pagesSampled"];
                        var avgPerPage = (double)totalSeen / pagesSampled;
                        // Estimate there are at least 2x more pages (conservative)
                        var estimatedPages = pagesSampled * 3;
                        estimationData["estimatedTotal"] = (int)(avgPerPage * estimatedPages);
                        estimationData["confidence"] = "low";
                        estimationData["method"] = "extrapolation";
                    }
                    else
                    {
                        estimationData["estimatedTotal"] = (int)estimationData["totalDocumentsSeen"];
                        estimationData["confidence"] = "medium";
                        estimationData["method"] = "partial_sampling";
                    }
                }

                Console.WriteLine($"Estimation: {estimationData["estimatedTotal"]} results " +
                                $"(confidence: {estimationData["confidence"]})");

                return estimationData;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Estimation error: {ex.Message}");
                return new Dictionary<string, object> { ["error"] = ex.Message };
            }
        }

        /// <summary>
        /// Get result count with caching to improve performance
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="cacheDuration">Cache duration in seconds</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Cached or fresh count</returns>
        public async Task<long?> GetCountWithCachingAsync(
            string searchText,
            int cacheDuration = 300,
            CancellationToken cancellationToken = default)
        {
            var cacheKey = $"count_{searchText.GetHashCode()}";
            var currentTime = DateTime.UtcNow;

            // Check cache
            if (_countCache.ContainsKey(cacheKey))
            {
                var cachedData = _countCache[cacheKey];
                var timestamp = (DateTime)cachedData["timestamp"];
                if ((currentTime - timestamp).TotalSeconds < cacheDuration)
                {
                    var cachedCount = (long?)cachedData["count"];
                    Console.WriteLine($"Using cached count: {cachedCount}");
                    return cachedCount;
                }
            }

            // Get fresh count
            Console.WriteLine($"Fetching fresh count for: '{searchText}'");
            var result = await SearchWithCountAsync(searchText, includeCount: true, cancellationToken,
                new SearchOptions { Size = 1 });

            // Cache the result
            _countCache[cacheKey] = new Dictionary<string, object>
            {
                ["count"] = result.TotalCount,
                ["timestamp"] = currentTime,
                ["query"] = searchText
            };

            return result.TotalCount;
        }

        /// <summary>
        /// Analyze counting patterns across multiple queries
        /// </summary>
        /// <param name="queries">List of search queries to analyze</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Pattern analysis results</returns>
        public async Task<Dictionary<string, object>> AnalyzeCountPatternsAsync(
            List<string> queries,
            CancellationToken cancellationToken = default)
        {
            Console.WriteLine($"Analyzing count patterns for {queries.Count} queries");

            var analysis = new Dictionary<string, object>
            {
                ["queriesAnalyzed"] = queries.Count,
                ["totalOverheadMs"] = 0.0,
                ["avgOverheadMs"] = 0.0,
                ["maxOverheadMs"] = 0.0,
                ["minOverheadMs"] = double.MaxValue,
                ["overheadByResultSize"] = new Dictionary<string, List<double>>(),
                ["recommendations"] = new List<string>()
            };

            var overheadBySize = (Dictionary<string, List<double>>)analysis["overheadByResultSize"];
            var recommendations = (List<string>)analysis["recommendations"];

            foreach (var query in queries)
            {
                try
                {
                    var metrics = await CompareCountPerformanceAsync(query, iterations: 2, cancellationToken);

                    analysis["totalOverheadMs"] = (double)analysis["totalOverheadMs"] + metrics.CountOverheadMs;
                    analysis["maxOverheadMs"] = Math.Max((double)analysis["maxOverheadMs"], metrics.CountOverheadMs);
                    analysis["minOverheadMs"] = Math.Min((double)analysis["minOverheadMs"], metrics.CountOverheadMs);

                    // Categorize by result size
                    if (metrics.TotalResults.HasValue)
                    {
                        string category;
                        if (metrics.TotalResults < 100)
                            category = "small";
                        else if (metrics.TotalResults < 1000)
                            category = "medium";
                        else
                            category = "large";

                        if (!overheadBySize.ContainsKey(category))
                        {
                            overheadBySize[category] = new List<double>();
                        }

                        overheadBySize[category].Add(metrics.CountOverheadMs);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error analyzing query '{query}': {ex.Message}");
                }
            }

            // Calculate averages
            if (queries.Count > 0)
            {
                analysis["avgOverheadMs"] = (double)analysis["totalOverheadMs"] / queries.Count;
            }

            // Calculate category averages
            foreach (var (category, overheads) in overheadBySize.ToList())
            {
                if (overheads.Any())
                {
                    overheadBySize[category] = new List<double> { overheads.Average() };
                }
            }

            // Generate recommendations
            var avgOverhead = (double)analysis["avgOverheadMs"];
            if (avgOverhead > 50)
            {
                recommendations.Add("Consider disabling counts for performance-critical scenarios");
            }

            if (avgOverhead < 10)
            {
                recommendations.Add("Count overhead is minimal, safe to use counts");
            }

            return analysis;
        }

        /// <summary>
        /// Get intelligent counting strategy based on context
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="context">Usage context ('pagination', 'display', 'api', 'analytics')</param>
        /// <returns>Recommended counting strategy</returns>
        public Dictionary<string, object> GetSmartCountStrategy(string searchText, string context = "general")
        {
            var strategies = new Dictionary<string, Dictionary<string, object>>
            {
                ["pagination"] = new Dictionary<string, object>
                {
                    ["includeCount"] = true,
                    ["reason"] = "Pagination requires total count for page calculation",
                    ["cacheDuration"] = 60,
                    ["estimateThreshold"] = 10000
                },
                ["display"] = new Dictionary<string, object>
                {
                    ["includeCount"] = true,
                    ["reason"] = "Users expect to see result counts",
                    ["cacheDuration"] = 300,
                    ["estimateThreshold"] = 5000
                },
                ["api"] = new Dictionary<string, object>
                {
                    ["includeCount"] = false,
                    ["reason"] = "API performance is critical, count on demand",
                    ["cacheDuration"] = 600,
                    ["estimateThreshold"] = 1000
                },
                ["analytics"] = new Dictionary<string, object>
                {
                    ["includeCount"] = true,
                    ["reason"] = "Analytics require accurate counts",
                    ["cacheDuration"] = 3600,
                    ["estimateThreshold"] = null
                },
                ["search_as_you_type"] = new Dictionary<string, object>
                {
                    ["includeCount"] = false,
                    ["reason"] = "Real-time search needs fast response",
                    ["cacheDuration"] = 30,
                    ["estimateThreshold"] = 100
                }
            };

            var strategy = strategies.ContainsKey(context) ? 
                strategies[context] : 
                strategies.ContainsKey("general") ? strategies["general"] : strategies["display"];

            // Add query-specific recommendations
            var result = new Dictionary<string, object>(strategy)
            {
                ["query"] = searchText,
                ["context"] = context
            };

            // Estimate complexity
            if (searchText.Split(' ').Length > 5)
            {
                result["complexity"] = "high";
                result["includeCount"] = false;
                result["reason"] = result["reason"] + " (complex query detected)";
            }
            else
            {
                result["complexity"] = "low";
            }

            return result;
        }

        /// <summary>
        /// Get performance metrics summary
        /// </summary>
        /// <returns>Performance metrics</returns>
        public Dictionary<string, object> GetPerformanceMetrics()
        {
            if (!_metrics.Any())
            {
                return new Dictionary<string, object>();
            }

            var durations = _metrics.Select(m => m.CountOverheadMs).ToList();
            return new Dictionary<string, object>
            {
                ["totalRequests"] = _metrics.Count,
                ["averageOverheadMs"] = durations.Average(),
                ["minOverheadMs"] = durations.Min(),
                ["maxOverheadMs"] = durations.Max(),
                ["totalQueriesAnalyzed"] = _metrics.Count
            };
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
    }

    /// <summary>
    /// Demonstration class for result counting
    /// </summary>
    public class ResultCountingDemo
    {
        private readonly SearchClient _searchClient;

        public ResultCountingDemo(SearchClient searchClient)
        {
            _searchClient = searchClient;
        }

        /// <summary>
        /// Demonstrates basic result counting functionality
        /// </summary>
        public async Task DemonstrateBasicCountingAsync()
        {
            Console.WriteLine("=== Basic Result Counting Demo ===\n");

            var counter = new ResultCounter<Hotel>(_searchClient);

            try
            {
                // Search with count
                Console.WriteLine("1. Search with count enabled:");
                var resultWithCount = await counter.SearchWithCountAsync("hotel", includeCount: true,
                    options: new SearchOptions { Size = 5 });

                Console.WriteLine($"Query: '{resultWithCount.Query}'");
                Console.WriteLine($"Results returned: {resultWithCount.Documents.Count}");
                Console.WriteLine($"Total count: {resultWithCount.TotalCount}");
                Console.WriteLine($"Has more results: {resultWithCount.HasMoreResults}");
                Console.WriteLine($"Count accuracy: {resultWithCount.CountAccuracy}");

                // Search without count
                Console.WriteLine("\n2. Search without count:");
                var resultWithoutCount = await counter.SearchWithCountAsync("hotel", includeCount: false,
                    options: new SearchOptions { Size = 5 });

                Console.WriteLine($"Results returned: {resultWithoutCount.Documents.Count}");
                Console.WriteLine($"Total count: {resultWithoutCount.TotalCount}");
                Console.WriteLine($"Has more results: {resultWithoutCount.HasMoreResults}");
                Console.WriteLine($"Count accuracy: {resultWithoutCount.CountAccuracy}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Basic counting demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates count performance comparison
        /// </summary>
        public async Task DemonstrateCountPerformanceAsync()
        {
            Console.WriteLine("\n=== Count Performance Demo ===\n");

            var counter = new ResultCounter<Hotel>(_searchClient);

            try
            {
                var queries = new[] { "luxury", "beach resort", "spa", "business hotel" };

                foreach (var query in queries)
                {
                    Console.WriteLine($"Testing query: '{query}'");
                    var metrics = await counter.CompareCountPerformanceAsync(query, iterations: 2);

                    Console.WriteLine($"  Overhead: {metrics.CountOverheadMs:F1}ms " +
                                    $"({metrics.CountOverheadPercentage:F1}%)");
                    Console.WriteLine($"  Total results: {metrics.TotalResults}");
                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Count performance demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates result estimation techniques
        /// </summary>
        public async Task DemonstrateResultEstimationAsync()
        {
            Console.WriteLine("=== Result Estimation Demo ===\n");

            var counter = new ResultCounter<Hotel>(_searchClient);

            try
            {
                var queries = new[] { "hotel", "luxury resort" };

                foreach (var query in queries)
                {
                    Console.WriteLine($"Estimating results for: '{query}'");

                    // Get actual count for comparison
                    var actualResult = await counter.SearchWithCountAsync(query, includeCount: true,
                        options: new SearchOptions { Size = 1 });
                    var actualCount = actualResult.TotalCount;

                    // Get estimation
                    var estimation = await counter.EstimateTotalResultsAsync(query, samplePages: 2, pageSize: 20);

                    if (!estimation.ContainsKey("error"))
                    {
                        var estimatedCount = (int?)estimation["estimatedTotal"];
                        var confidence = (string)estimation["confidence"];
                        var method = (string)estimation["method"];

                        Console.WriteLine($"  Actual count: {actualCount}");
                        Console.WriteLine($"  Estimated count: {estimatedCount}");
                        Console.WriteLine($"  Confidence: {confidence}");
                        Console.WriteLine($"  Method: {method}");

                        if (actualCount.HasValue && estimatedCount.HasValue)
                        {
                            var accuracy = Math.Abs(actualCount.Value - estimatedCount.Value) / (double)actualCount.Value * 100;
                            Console.WriteLine($"  Accuracy: {100 - accuracy:F1}%");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"  Estimation failed: {estimation["error"]}");
                    }

                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Result estimation demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates count caching functionality
        /// </summary>
        public async Task DemonstrateCountCachingAsync()
        {
            Console.WriteLine("=== Count Caching Demo ===\n");

            var counter = new ResultCounter<Hotel>(_searchClient);

            try
            {
                var query = "spa hotel";

                // First call - should fetch fresh
                Console.WriteLine("1. First call (fresh fetch):");
                var startTime = DateTime.UtcNow;
                var count1 = await counter.GetCountWithCachingAsync(query, cacheDuration: 60);
                var duration1 = (DateTime.UtcNow - startTime).TotalMilliseconds;
                Console.WriteLine($"Count: {count1}, Duration: {duration1:F1}ms");

                // Second call - should use cache
                Console.WriteLine("\n2. Second call (cached):");
                startTime = DateTime.UtcNow;
                var count2 = await counter.GetCountWithCachingAsync(query, cacheDuration: 60);
                var duration2 = (DateTime.UtcNow - startTime).TotalMilliseconds;
                Console.WriteLine($"Count: {count2}, Duration: {duration2:F1}ms");

                Console.WriteLine($"\nCache speedup: {duration1 / Math.Max(duration2, 1):F1}x faster");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Count caching demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates smart counting strategy selection
        /// </summary>
        public async Task DemonstrateSmartCountingStrategyAsync()
        {
            Console.WriteLine("\n=== Smart Counting Strategy Demo ===\n");

            var counter = new ResultCounter<Hotel>(_searchClient);

            try
            {
                var query = "luxury hotel";
                var contexts = new[] { "pagination", "display", "api", "analytics", "search_as_you_type" };

                Console.WriteLine($"Smart strategies for query: '{query}'\n");

                foreach (var context in contexts)
                {
                    var strategy = counter.GetSmartCountStrategy(query, context);

                    Console.WriteLine($"{context.ToUpper()}:");
                    Console.WriteLine($"  Include count: {strategy["includeCount"]}");
                    Console.WriteLine($"  Reason: {strategy["reason"]}");
                    Console.WriteLine($"  Cache duration: {strategy["cacheDuration"]}s");
                    Console.WriteLine($"  Complexity: {strategy["complexity"]}");
                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Smart counting strategy demo error: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Utility class for common counting patterns
    /// </summary>
    public static class CountingHelper
    {
        public static bool ShouldIncludeCount(string context, string queryComplexity = "low")
        {
            var countContexts = new Dictionary<string, bool>
            {
                ["pagination"] = true,
                ["display"] = true,
                ["analytics"] = true,
                ["api"] = false,
                ["search_as_you_type"] = false,
                ["autocomplete"] = false
            };

            var baseDecision = countContexts.ContainsKey(context) ? countContexts[context] : true;

            // Adjust for query complexity
            if (queryComplexity == "high" && (context == "api" || context == "search_as_you_type"))
            {
                return false;
            }

            return baseDecision;
        }

        public static int GetCacheDuration(string context)
        {
            var durations = new Dictionary<string, int>
            {
                ["pagination"] = 60,      // 1 minute
                ["display"] = 300,        // 5 minutes
                ["api"] = 600,           // 10 minutes
                ["analytics"] = 3600,     // 1 hour
                ["search_as_you_type"] = 30,  // 30 seconds
                ["autocomplete"] = 30     // 30 seconds
            };

            return durations.ContainsKey(context) ? durations[context] : 300;
        }

        public static string FormatCount(long? count, bool showExact = true, int threshold = 10000)
        {
            if (!count.HasValue)
                return "Unknown";

            if (!showExact && count > threshold)
            {
                if (count > 1000000)
                    return $"{count / 1000000}M+";
                else if (count > 1000)
                    return $"{count / 1000}K+";
            }

            return count.Value.ToString("N0");
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
                var demo = new ResultCountingDemo(searchClient);
                await demo.DemonstrateBasicCountingAsync();
                await demo.DemonstrateCountPerformanceAsync();
                await demo.DemonstrateResultEstimationAsync();
                await demo.DemonstrateCountCachingAsync();
                await demo.DemonstrateSmartCountingStrategyAsync();

                // Show helper usage
                Console.WriteLine("\n=== Counting Helper Demo ===\n");
                var helper = CountingHelper.ShouldIncludeCount;

                Console.WriteLine("Should include count:");
                var contexts = new[] { "pagination", "api", "analytics" };
                foreach (var context in contexts)
                {
                    var shouldCount = CountingHelper.ShouldIncludeCount(context);
                    var cacheDuration = CountingHelper.GetCacheDuration(context);
                    Console.WriteLine($"  {context}: {shouldCount} (cache: {cacheDuration}s)");
                }

                Console.WriteLine("\nCount formatting:");
                var counts = new long?[] { 42, 1234, 15678, 1234567, null };
                foreach (var count in counts)
                {
                    var exact = CountingHelper.FormatCount(count, showExact: true);
                    var approx = CountingHelper.FormatCount(count, showExact: false, threshold: 1000);
                    Console.WriteLine($"  {count}: exact='{exact}', approx='{approx}'");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Demo failed: {ex.Message}");
            }
        }
    }
}