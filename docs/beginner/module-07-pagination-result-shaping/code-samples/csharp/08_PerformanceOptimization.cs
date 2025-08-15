/*
Module 7: Pagination & Result Shaping - Performance Optimization
Azure AI Search .NET SDK Example

This example demonstrates comprehensive performance optimization techniques for pagination
and result shaping, including caching, connection pooling, monitoring, and best practices.

Prerequisites:
- Azure AI Search service
- .NET 6.0 or later
- Azure.Search.Documents NuGet package
- Sample data index with substantial data
*/

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchPerformanceOptimization
{
    public class PerformanceMetrics
    {
        public int TotalRequests { get; set; }
        public double TotalTimeMs { get; set; }
        public int CacheHits { get; set; }
        public int CacheMisses { get; set; }
        public int Errors { get; set; }
        public double AvgResponseTimeMs => TotalRequests > 0 ? TotalTimeMs / TotalRequests : 0;
        public double ThroughputRequestsPerSec => TotalTimeMs > 0 ? TotalRequests / (TotalTimeMs / 1000) : 0;

        public void UpdateAverages()
        {
            // Averages are calculated properties
        }
    }

    public class CacheEntry
    {
        public object Data { get; set; }
        public DateTime Timestamp { get; set; }
        public int AccessCount { get; set; }
        public int SizeBytes { get; set; }

        public CacheEntry(object data)
        {
            Data = data;
            Timestamp = DateTime.UtcNow;
            AccessCount = 0;
            SizeBytes = EstimateSize(data);
        }

        private int EstimateSize(object data)
        {
            try
            {
                var json = JsonSerializer.Serialize(data);
                return Encoding.UTF8.GetByteCount(json);
            }
            catch
            {
                return 1024; // Default estimate
            }
        }
    }

    public class SearchResult
    {
        public List<SearchDocument> Documents { get; set; } = new();
        public string Query { get; set; }
        public int ResultCount { get; set; }
        public double DurationMs { get; set; }
        public bool FromCache { get; set; }
        public string CacheKey { get; set; }
        public Dictionary<string, object> Parameters { get; set; } = new();
        public string Error { get; set; }
    }

    public class SlowQuery
    {
        public string Query { get; set; }
        public double DurationMs { get; set; }
        public Dictionary<string, object> Parameters { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class PerformanceOptimizer
    {
        private readonly SearchClient _client;
        private readonly PerformanceMetrics _metrics;
        private readonly ConcurrentDictionary<string, CacheEntry> _cache;
        private readonly List<Dictionary<string, object>> _requestHistory;
        private readonly List<SlowQuery> _slowQueries;
        private readonly ReaderWriterLockSlim _historyLock;
        private readonly ReaderWriterLockSlim _slowQueryLock;

        private readonly int _cacheTtlSeconds;
        private readonly int _maxCacheSize;
        private readonly double _slowQueryThresholdMs;

        public PerformanceOptimizer(string endpoint, string indexName, string apiKey, 
            int cacheTtl = 300, int maxCacheSize = 1000)
        {
            _client = new SearchClient(new Uri(endpoint), indexName, new AzureKeyCredential(apiKey));
            _metrics = new PerformanceMetrics();
            _cache = new ConcurrentDictionary<string, CacheEntry>();
            _requestHistory = new List<Dictionary<string, object>>();
            _slowQueries = new List<SlowQuery>();
            _historyLock = new ReaderWriterLockSlim();
            _slowQueryLock = new ReaderWriterLockSlim();

            _cacheTtlSeconds = cacheTtl;
            _maxCacheSize = maxCacheSize;
            _slowQueryThresholdMs = 1000;
        }

        private string GenerateCacheKey(string query, Dictionary<string, object> parameters)
        {
            var cacheData = new Dictionary<string, object> { ["query"] = query };
            foreach (var param in parameters)
            {
                cacheData[param.Key] = param.Value;
            }

            var json = JsonSerializer.Serialize(cacheData, new JsonSerializerOptions { WriteIndented = false });
            using var md5 = MD5.Create();
            var hash = md5.ComputeHash(Encoding.UTF8.GetBytes(json));
            return Convert.ToHexString(hash).ToLower();
        }

        private object GetFromCache(string cacheKey)
        {
            if (_cache.TryGetValue(cacheKey, out var entry))
            {
                // Check if entry is still valid
                if (DateTime.UtcNow.Subtract(entry.Timestamp).TotalSeconds < _cacheTtlSeconds)
                {
                    Interlocked.Increment(ref entry.AccessCount);
                    Interlocked.Increment(ref _metrics.CacheHits);
                    return entry.Data;
                }
                else
                {
                    // Remove expired entry
                    _cache.TryRemove(cacheKey, out _);
                }
            }

            Interlocked.Increment(ref _metrics.CacheMisses);
            return null;
        }

        private void StoreInCache(string cacheKey, object data)
        {
            // Manage cache size
            if (_cache.Count >= _maxCacheSize)
            {
                EvictCacheEntries();
            }

            var entry = new CacheEntry(data);
            _cache.TryAdd(cacheKey, entry);
        }

        private void EvictCacheEntries()
        {
            if (_cache.IsEmpty) return;

            // Sort by access count and timestamp (LRU)
            var sortedEntries = _cache.ToList()
                .OrderBy(x => x.Value.AccessCount)
                .ThenBy(x => x.Value.Timestamp)
                .ToList();

            // Remove oldest 25% of entries
            var entriesToRemove = Math.Max(1, sortedEntries.Count / 4);
            for (int i = 0; i < entriesToRemove; i++)
            {
                _cache.TryRemove(sortedEntries[i].Key, out _);
            }
        }

        public async Task<SearchResult> OptimizedSearchAsync(string query, int skip = 0, int top = 20,
            IEnumerable<string> selectFields = null, bool useCache = true, 
            CancellationToken cancellationToken = default)
        {
            var stopwatch = Stopwatch.StartNew();

            // Generate cache key
            var cacheParams = new Dictionary<string, object>
            {
                ["skip"] = skip,
                ["top"] = top,
                ["selectFields"] = selectFields?.ToList()
            };
            var cacheKey = GenerateCacheKey(query, cacheParams);

            // Try cache first
            if (useCache)
            {
                var cachedResult = GetFromCache(cacheKey);
                if (cachedResult is SearchResult cached)
                {
                    cached.FromCache = true;
                    cached.CacheKey = cacheKey;
                    return cached;
                }
            }

            try
            {
                // Perform search with optimizations
                var searchOptions = new SearchOptions
                {
                    Skip = skip,
                    Size = top,
                    IncludeTotalCount = false // Optimize by not counting unless needed
                };

                if (selectFields != null)
                {
                    foreach (var field in selectFields)
                    {
                        searchOptions.Select.Add(field);
                    }
                }

                var searchResults = await _client.SearchAsync<SearchDocument>(query, searchOptions, cancellationToken);
                var documents = new List<SearchDocument>();

                await foreach (var result in searchResults.Value.GetResultsAsync())
                {
                    documents.Add(result.Document);
                }

                stopwatch.Stop();
                var durationMs = stopwatch.Elapsed.TotalMilliseconds;

                // Build result
                var result = new SearchResult
                {
                    Documents = documents,
                    Query = query,
                    ResultCount = documents.Count,
                    DurationMs = durationMs,
                    FromCache = false,
                    CacheKey = cacheKey,
                    Parameters = cacheParams
                };

                // Store in cache
                if (useCache)
                {
                    StoreInCache(cacheKey, result);
                }

                // Update metrics
                UpdateMetrics(durationMs, documents.Count);

                // Check for slow queries
                if (durationMs > _slowQueryThresholdMs)
                {
                    RecordSlowQuery(query, durationMs, cacheParams);
                }

                return result;
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                var durationMs = stopwatch.Elapsed.TotalMilliseconds;
                
                Interlocked.Increment(ref _metrics.Errors);
                Interlocked.Increment(ref _metrics.TotalRequests);
                _metrics.TotalTimeMs += durationMs;

                return new SearchResult
                {
                    Documents = new List<SearchDocument>(),
                    Query = query,
                    ResultCount = 0,
                    DurationMs = durationMs,
                    FromCache = false,
                    Error = ex.Message
                };
            }
        }

        private void UpdateMetrics(double durationMs, int resultCount)
        {
            Interlocked.Increment(ref _metrics.TotalRequests);
            _metrics.TotalTimeMs += durationMs;

            // Store request history (keep last 1000)
            _historyLock.EnterWriteLock();
            try
            {
                _requestHistory.Add(new Dictionary<string, object>
                {
                    ["timestamp"] = DateTime.UtcNow,
                    ["durationMs"] = durationMs,
                    ["resultCount"] = resultCount
                });

                if (_requestHistory.Count > 1000)
                {
                    _requestHistory.RemoveRange(0, _requestHistory.Count - 1000);
                }
            }
            finally
            {
                _historyLock.ExitWriteLock();
            }
        }

        private void RecordSlowQuery(string query, double durationMs, Dictionary<string, object> parameters)
        {
            var slowQuery = new SlowQuery
            {
                Query = query,
                DurationMs = durationMs,
                Parameters = parameters,
                Timestamp = DateTime.UtcNow
            };

            _slowQueryLock.EnterWriteLock();
            try
            {
                _slowQueries.Add(slowQuery);

                // Keep only last 100 slow queries
                if (_slowQueries.Count > 100)
                {
                    _slowQueries.RemoveRange(0, _slowQueries.Count - 100);
                }
            }
            finally
            {
                _slowQueryLock.ExitWriteLock();
            }

            Console.WriteLine($"⚠️ Slow query detected: '{query}' took {durationMs:F1}ms");
        }

        public async Task<List<SearchDocument>> OptimizedPaginationAsync(string query, int pageSize = 20,
            int? maxPages = null, string strategy = "adaptive", CancellationToken cancellationToken = default)
        {
            Console.WriteLine($"🔄 Starting optimized pagination: '{query}' (strategy: {strategy})");

            var allResults = new List<SearchDocument>();
            var pageNum = 0;

            while (true)
            {
                if (maxPages.HasValue && pageNum >= maxPages.Value)
                    break;

                // Choose strategy based on page depth
                var currentStrategy = strategy == "adaptive" 
                    ? (pageNum > 10 ? "range" : "skip_top")
                    : strategy;

                // Get page based on strategy
                SearchResult pageResult;
                if (currentStrategy == "skip_top" || currentStrategy == "range") // Range fallback to skip_top for simplicity
                {
                    pageResult = await PaginateSkipTopAsync(query, pageNum, pageSize, cancellationToken);
                }
                else
                {
                    pageResult = await PaginateSkipTopAsync(query, pageNum, pageSize, cancellationToken);
                }

                if (!pageResult.Documents.Any())
                {
                    Console.WriteLine($"   🏁 No more results at page {pageNum + 1}");
                    break;
                }

                allResults.AddRange(pageResult.Documents);
                pageNum++;

                // Progress reporting
                if (pageNum % 5 == 0)
                {
                    Console.WriteLine($"   📄 Processed {pageNum} pages, {allResults.Count} total results");
                }

                // Break if we got fewer results than expected
                if (pageResult.Documents.Count < pageSize)
                {
                    Console.WriteLine($"   🏁 Reached end of results at page {pageNum}");
                    break;
                }
            }

            Console.WriteLine($"✅ Pagination completed: {allResults.Count} results from {pageNum} pages");
            return allResults;
        }

        private async Task<SearchResult> PaginateSkipTopAsync(string query, int pageNum, int pageSize, 
            CancellationToken cancellationToken)
        {
            var skip = pageNum * pageSize;
            return await OptimizedSearchAsync(query, skip, pageSize, 
                new[] { "hotelId", "hotelName", "rating" }, true, cancellationToken);
        }

        public async Task<List<SearchResult>> BatchOptimizeQueriesAsync(IEnumerable<string> queries,
            bool parallel = true, int maxConcurrency = 5, CancellationToken cancellationToken = default)
        {
            var queryList = queries.ToList();
            Console.WriteLine($"🚀 Batch optimizing {queryList.Count} queries (parallel: {parallel})");

            if (parallel && queryList.Count > 1)
            {
                return await ExecuteQueriesParallelAsync(queryList, maxConcurrency, cancellationToken);
            }
            else
            {
                return await ExecuteQueriesSequentialAsync(queryList, cancellationToken);
            }
        }

        private async Task<List<SearchResult>> ExecuteQueriesSequentialAsync(List<string> queries, 
            CancellationToken cancellationToken)
        {
            var results = new List<SearchResult>();

            for (int i = 0; i < queries.Count; i++)
            {
                var query = queries[i];
                Console.WriteLine($"   Executing query {i + 1}/{queries.Count}: '{query}'");
                var result = await OptimizedSearchAsync(query, top: 10, cancellationToken: cancellationToken);
                results.Add(result);
            }

            return results;
        }

        private async Task<List<SearchResult>> ExecuteQueriesParallelAsync(List<string> queries, 
            int maxConcurrency, CancellationToken cancellationToken)
        {
            var semaphore = new SemaphoreSlim(maxConcurrency, maxConcurrency);
            var tasks = queries.Select(async (query, index) =>
            {
                await semaphore.WaitAsync(cancellationToken);
                try
                {
                    var result = await OptimizedSearchAsync(query, top: 10, cancellationToken: cancellationToken);
                    Console.WriteLine($"   ✅ Completed query: '{query}'");
                    return (Index: index, Result: result);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Failed query: '{query}' - {ex.Message}");
                    return (Index: index, Result: new SearchResult 
                    { 
                        Error = ex.Message, 
                        Query = query,
                        Documents = new List<SearchDocument>()
                    });
                }
                finally
                {
                    semaphore.Release();
                }
            });

            var results = await Task.WhenAll(tasks);
            return results.OrderBy(r => r.Index).Select(r => r.Result).ToList();
        }

        public Dictionary<string, object> AnalyzePerformance()
        {
            Console.WriteLine("📊 Analyzing performance metrics...");

            _metrics.UpdateAverages();

            // Cache analysis
            var totalCacheRequests = _metrics.CacheHits + _metrics.CacheMisses;
            var cacheHitRate = totalCacheRequests > 0 ? (_metrics.CacheHits / (double)totalCacheRequests * 100) : 0;

            // Recent performance trends
            List<Dictionary<string, object>> recentRequests;
            _historyLock.EnterReadLock();
            try
            {
                recentRequests = _requestHistory.TakeLast(100).ToList();
            }
            finally
            {
                _historyLock.ExitReadLock();
            }

            var recentAvgTime = recentRequests.Any() 
                ? recentRequests.Average(r => (double)r["durationMs"]) 
                : 0;

            // Slow query analysis
            var slowQueryRate = _metrics.TotalRequests > 0 
                ? (_slowQueries.Count / (double)_metrics.TotalRequests * 100) 
                : 0;

            var analysis = new Dictionary<string, object>
            {
                ["overall_metrics"] = new Dictionary<string, object>
                {
                    ["total_requests"] = _metrics.TotalRequests,
                    ["avg_response_time_ms"] = _metrics.AvgResponseTimeMs,
                    ["throughput_rps"] = _metrics.ThroughputRequestsPerSec,
                    ["error_rate_pct"] = _metrics.TotalRequests > 0 ? (_metrics.Errors / (double)_metrics.TotalRequests * 100) : 0
                },
                ["cache_performance"] = new Dictionary<string, object>
                {
                    ["hit_rate_pct"] = cacheHitRate,
                    ["total_entries"] = _cache.Count,
                    ["cache_size_limit"] = _maxCacheSize,
                    ["ttl_seconds"] = _cacheTtlSeconds
                },
                ["recent_performance"] = new Dictionary<string, object>
                {
                    ["recent_avg_time_ms"] = recentAvgTime,
                    ["recent_requests_analyzed"] = recentRequests.Count
                },
                ["slow_queries"] = new Dictionary<string, object>
                {
                    ["count"] = _slowQueries.Count,
                    ["rate_pct"] = slowQueryRate,
                    ["threshold_ms"] = _slowQueryThresholdMs
                },
                ["recommendations"] = GeneratePerformanceRecommendations(cacheHitRate, slowQueryRate, recentAvgTime)
            };

            return analysis;
        }

        private List<string> GeneratePerformanceRecommendations(double cacheHitRate, double slowQueryRate, double recentAvgTime)
        {
            var recommendations = new List<string>();

            // Cache recommendations
            if (cacheHitRate < 50)
            {
                recommendations.Add("Low cache hit rate - consider increasing cache TTL or reviewing query patterns");
            }
            else if (cacheHitRate > 90)
            {
                recommendations.Add("Excellent cache performance - current caching strategy is effective");
            }

            // Slow query recommendations
            if (slowQueryRate > 10)
            {
                recommendations.Add("High slow query rate - review query complexity and consider field selection optimization");
            }

            // Response time recommendations
            if (recentAvgTime > 500)
            {
                recommendations.Add("High average response time - consider implementing field selection and result caching");
            }
            else if (recentAvgTime < 100)
            {
                recommendations.Add("Excellent response times - current optimization strategy is working well");
            }

            // General recommendations
            if (_metrics.TotalRequests > 100)
            {
                recommendations.Add("Consider implementing connection pooling for high-volume scenarios");
            }

            if (_cache.Count > _maxCacheSize * 0.8)
            {
                recommendations.Add("Cache approaching size limit - consider increasing max_cache_size or reducing TTL");
            }

            return recommendations;
        }

        public Dictionary<string, object> GetCacheStatistics()
        {
            var entries = _cache.Values.ToList();
            var totalSize = entries.Sum(e => e.SizeBytes);
            var accessCounts = entries.Select(e => e.AccessCount).ToList();

            return new Dictionary<string, object>
            {
                ["total_entries"] = _cache.Count,
                ["total_size_bytes"] = totalSize,
                ["total_size_mb"] = totalSize / (1024.0 * 1024.0),
                ["avg_access_count"] = accessCounts.Any() ? accessCounts.Average() : 0,
                ["max_access_count"] = accessCounts.Any() ? accessCounts.Max() : 0,
                ["cache_utilization_pct"] = (_cache.Count / (double)_maxCacheSize * 100)
            };
        }

        public void ClearCache()
        {
            _cache.Clear();
            Console.WriteLine("🗑️ Cache cleared");
        }

        public List<SlowQuery> GetSlowQueries(int limit = 10)
        {
            _slowQueryLock.EnterReadLock();
            try
            {
                return _slowQueries.OrderByDescending(q => q.DurationMs).Take(limit).ToList();
            }
            finally
            {
                _slowQueryLock.ExitReadLock();
            }
        }

        public void Dispose()
        {
            _historyLock?.Dispose();
            _slowQueryLock?.Dispose();
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            // Configuration
            var endpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-api-key";
            var indexName = Environment.GetEnvironmentVariable("INDEX_NAME") ?? "hotels-sample";

            Console.WriteLine("⚡ Azure AI Search - Performance Optimization");
            Console.WriteLine("=" + new string('=', 49));

            // Initialize optimizer
            var optimizer = new PerformanceOptimizer(endpoint, indexName, apiKey, cacheTtl: 300, maxCacheSize: 500);

            try
            {
                // Example 1: Optimized search with caching
                Console.WriteLine("\n1. Optimized Search with Caching");
                Console.WriteLine("-" + new string('-', 34));

                // First search (cache miss)
                var result1 = await optimizer.OptimizedSearchAsync("luxury hotel", top: 10, 
                    selectFields: new[] { "hotelId", "hotelName", "rating" });
                Console.WriteLine($"First search: {result1.ResultCount} results in {result1.DurationMs:F1}ms (cached: {result1.FromCache})");

                // Second search (cache hit)
                var result2 = await optimizer.OptimizedSearchAsync("luxury hotel", top: 10, 
                    selectFields: new[] { "hotelId", "hotelName", "rating" });
                Console.WriteLine($"Second search: {result2.ResultCount} results in {result2.DurationMs:F1}ms (cached: {result2.FromCache})");

                // Example 2: Optimized pagination
                Console.WriteLine("\n2. Optimized Pagination");
                Console.WriteLine("-" + new string('-', 22));

                var paginatedResults = await optimizer.OptimizedPaginationAsync("hotel", pageSize: 15, maxPages: 3, strategy: "adaptive");
                Console.WriteLine($"Paginated results: {paginatedResults.Count} total documents");

                // Example 3: Batch query optimization
                Console.WriteLine("\n3. Batch Query Optimization");
                Console.WriteLine("-" + new string('-', 27));

                var testQueries = new[] { "spa", "wifi", "pool", "restaurant", "parking" };
                var batchResults = await optimizer.BatchOptimizeQueriesAsync(testQueries, parallel: true, maxConcurrency: 3);

                Console.WriteLine("Batch results:");
                for (int i = 0; i < batchResults.Count; i++)
                {
                    var result = batchResults[i];
                    if (string.IsNullOrEmpty(result.Error))
                    {
                        Console.WriteLine($"  '{testQueries[i]}': {result.ResultCount} results in {result.DurationMs:F1}ms");
                    }
                    else
                    {
                        Console.WriteLine($"  '{testQueries[i]}': Error - {result.Error}");
                    }
                }

                // Example 4: Performance analysis
                Console.WriteLine("\n4. Performance Analysis");
                Console.WriteLine("-" + new string('-', 21));

                var analysis = optimizer.AnalyzePerformance();

                Console.WriteLine("Overall Metrics:");
                var metrics = (Dictionary<string, object>)analysis["overall_metrics"];
                Console.WriteLine($"  Total requests: {metrics["total_requests"]}");
                Console.WriteLine($"  Avg response time: {(double)metrics["avg_response_time_ms"]:F1}ms");
                Console.WriteLine($"  Throughput: {(double)metrics["throughput_rps"]:F1} requests/sec");
                Console.WriteLine($"  Error rate: {(double)metrics["error_rate_pct"]:F1}%");

                Console.WriteLine("\nCache Performance:");
                var cache = (Dictionary<string, object>)analysis["cache_performance"];
                Console.WriteLine($"  Hit rate: {(double)cache["hit_rate_pct"]:F1}%");
                Console.WriteLine($"  Entries: {cache["total_entries"]}/{cache["cache_size_limit"]}");

                Console.WriteLine("\nRecommendations:");
                var recommendations = (List<string>)analysis["recommendations"];
                foreach (var rec in recommendations)
                {
                    Console.WriteLine($"  • {rec}");
                }

                // Example 5: Cache statistics
                Console.WriteLine("\n5. Cache Statistics");
                Console.WriteLine("-" + new string('-', 17));

                var cacheStats = optimizer.GetCacheStatistics();
                Console.WriteLine($"Cache entries: {cacheStats["total_entries"]}");
                Console.WriteLine($"Cache size: {(double)cacheStats["total_size_mb"]:F2} MB");
                Console.WriteLine($"Cache utilization: {(double)cacheStats["cache_utilization_pct"]:F1}%");
                Console.WriteLine($"Average access count: {(double)cacheStats["avg_access_count"]:F1}");

                // Example 6: Slow query analysis
                Console.WriteLine("\n6. Slow Query Analysis");
                Console.WriteLine("-" + new string('-', 21));

                var slowQueries = optimizer.GetSlowQueries(limit: 5);
                if (slowQueries.Any())
                {
                    Console.WriteLine("Recent slow queries:");
                    foreach (var query in slowQueries)
                    {
                        Console.WriteLine($"  '{query.Query}': {query.DurationMs:F1}ms");
                    }
                }
                else
                {
                    Console.WriteLine("No slow queries detected");
                }

                Console.WriteLine("\n✅ Performance optimization demonstration completed!");
                var finalCache = (Dictionary<string, object>)analysis["cache_performance"];
                Console.WriteLine($"Final cache hit rate: {(double)finalCache["hit_rate_pct"]:F1}%");
            }
            finally
            {
                optimizer.Dispose();
            }
        }
    }
}