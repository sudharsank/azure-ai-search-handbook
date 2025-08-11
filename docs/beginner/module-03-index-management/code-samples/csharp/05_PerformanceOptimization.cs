/*
 * Module 3: Index Management - Performance Optimization (C#)
 * =========================================================
 * 
 * This example demonstrates performance optimization techniques for Azure AI Search
 * index management using the .NET SDK, including batch sizing, parallel operations,
 * and monitoring with proper async/await patterns.
 * 
 * Learning Objectives:
 * - Optimize batch sizes for different document types
 * - Implement parallel upload strategies
 * - Monitor and measure performance metrics
 * - Apply performance best practices
 * - Handle memory and resource management
 * 
 * Prerequisites:
 * - Completed previous examples (01-04)
 * - Understanding of data ingestion and index operations
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module03
{
    /// <summary>
    /// Demonstrates performance optimization techniques using the .NET SDK
    /// </summary>
    public class PerformanceOptimizer
    {
        private readonly string _endpoint;
        private readonly string _adminKey;
        private SearchIndexClient? _indexClient;
        private SearchClient? _searchClient;

        /// <summary>
        /// Initialize the performance optimizer
        /// </summary>
        public PerformanceOptimizer()
        {
            _endpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_SERVICE_ENDPOINT environment variable is required");
            
            _adminKey = Environment.GetEnvironmentVariable("AZURE_SEARCH_ADMIN_KEY") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_ADMIN_KEY environment variable is required");
        }

        /// <summary>
        /// Create and validate the search clients
        /// </summary>
        public async Task<bool> CreateClientsAsync()
        {
            Console.WriteLine("🔍 Creating Search Clients...");

            try
            {
                _indexClient = new SearchIndexClient(
                    new Uri(_endpoint),
                    new AzureKeyCredential(_adminKey)
                );

                // Test connection
                var stats = await _indexClient.GetServiceStatisticsAsync();
                Console.WriteLine("✅ Connected to Azure AI Search service");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create clients: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Create a sample index for performance testing
        /// </summary>
        public async Task<string?> CreatePerformanceTestIndexAsync()
        {
            Console.WriteLine("🏗️  Creating performance test index...");

            const string indexName = "performance-test-cs";

            var fields = new List<SearchField>
            {
                new SearchField("id", SearchFieldDataType.String) { IsKey = true },
                new SearchField("title", SearchFieldDataType.String) { IsSearchable = true },
                new SearchField("content", SearchFieldDataType.String) { IsSearchable = true },
                new SearchField("category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SearchField("author", SearchFieldDataType.String) { IsFilterable = true },
                new SearchField("publishedDate", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true },
                new SearchField("rating", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true },
                new SearchField("viewCount", SearchFieldDataType.Int32) { IsFilterable = true, IsSortable = true },
                new SearchField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFilterable = true, IsFacetable = true },
                new SearchField("isPublished", SearchFieldDataType.Boolean) { IsFilterable = true }
            };

            try
            {
                var index = new SearchIndex(indexName, fields);
                var result = await _indexClient!.CreateOrUpdateIndexAsync(index);

                // Create search client for this index
                _searchClient = new SearchClient(
                    new Uri(_endpoint),
                    indexName,
                    new AzureKeyCredential(_adminKey)
                );

                Console.WriteLine($"✅ Index '{result.Value.Name}' created successfully");
                return indexName;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create index: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Test different batch sizes for optimal performance
        /// </summary>
        public async Task<List<BatchSizeResult>> TestBatchSizesAsync()
        {
            Console.WriteLine("📊 Testing Different Batch Sizes...");

            var batchSizes = new[] { 10, 25, 50, 100, 200 };
            const int totalDocuments = 500;
            var results = new List<BatchSizeResult>();

            foreach (var batchSize in batchSizes)
            {
                Console.WriteLine($"\n🧪 Testing batch size: {batchSize}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    var totalSuccessful = 0;
                    var totalFailed = 0;

                    // Process in batches
                    for (var batchNum = 0; batchNum < totalDocuments; batchNum += batchSize)
                    {
                        var currentBatchSize = Math.Min(batchSize, totalDocuments - batchNum);
                        var documents = GenerateSampleDocuments(currentBatchSize, batchNum + 1);

                        var batchStopwatch = Stopwatch.StartNew();
                        var result = await _searchClient!.UploadDocumentsAsync(documents);
                        batchStopwatch.Stop();

                        var successful = result.Value.Results.Count(r => r.Succeeded);
                        var failed = result.Value.Results.Count - successful;

                        totalSuccessful += successful;
                        totalFailed += failed;

                        var rate = successful / batchStopwatch.Elapsed.TotalSeconds;
                        Console.WriteLine($"   Batch {batchNum / batchSize + 1}: {successful}/{currentBatchSize} uploaded ({rate:F1} docs/sec)");

                        // Brief pause to avoid overwhelming the service
                        if (batchNum + batchSize < totalDocuments)
                        {
                            await Task.Delay(100);
                        }
                    }

                    stopwatch.Stop();
                    var overallRate = totalSuccessful / stopwatch.Elapsed.TotalSeconds;

                    var testResult = new BatchSizeResult
                    {
                        BatchSize = batchSize,
                        TotalSuccessful = totalSuccessful,
                        TotalFailed = totalFailed,
                        TotalTime = stopwatch.Elapsed.TotalSeconds,
                        OverallRate = overallRate
                    };

                    results.Add(testResult);

                    Console.WriteLine($"✅ Batch size {batchSize} completed:");
                    Console.WriteLine($"   Total successful: {totalSuccessful}");
                    Console.WriteLine($"   Total time: {testResult.TotalTime:F2} seconds");
                    Console.WriteLine($"   Overall rate: {overallRate:F1} documents/second");

                    // Clear index for next test
                    await ClearIndexAsync();
                    await Task.Delay(2000);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"❌ Batch size {batchSize} test failed: {ex.Message}");
                }
            }

            // Display results summary
            Console.WriteLine("\n📈 Batch Size Performance Summary:");
            Console.WriteLine("=".PadRight(60, '='));
            Console.WriteLine("Batch Size | Success | Time (s) | Rate (docs/sec)");
            Console.WriteLine("-".PadRight(60, '-'));

            foreach (var result in results)
            {
                Console.WriteLine($"{result.BatchSize,10} | {result.TotalSuccessful,7} | {result.TotalTime,8:F2} | {result.OverallRate,13:F1}");
            }

            // Find optimal batch size
            var optimal = results.OrderByDescending(r => r.OverallRate).FirstOrDefault();
            if (optimal != null)
            {
                Console.WriteLine($"\n🏆 Optimal batch size: {optimal.BatchSize} ({optimal.OverallRate:F1} docs/sec)");
            }

            return results;
        }

        /// <summary>
        /// Demonstrate parallel upload strategies
        /// </summary>
        public async Task<ParallelUploadResult?> TestParallelUploadsAsync()
        {
            Console.WriteLine("\n🔄 Testing Parallel Upload Strategies...");

            const int totalDocuments = 1000;
            const int batchSize = 50;
            const int parallelTasks = 4;

            try
            {
                var stopwatch = Stopwatch.StartNew();
                var allDocuments = GenerateSampleDocuments(totalDocuments);

                // Split documents into parallel batches
                var tasks = new List<Task<UploadThreadResult>>();
                var documentsPerTask = totalDocuments / parallelTasks;

                for (var taskIndex = 0; taskIndex < parallelTasks; taskIndex++)
                {
                    var startIndex = taskIndex * documentsPerTask;
                    var endIndex = taskIndex == parallelTasks - 1 ? totalDocuments : startIndex + documentsPerTask;
                    var taskDocuments = allDocuments.Skip(startIndex).Take(endIndex - startIndex).ToList();

                    tasks.Add(UploadBatchesSequentiallyAsync(taskDocuments, batchSize, taskIndex + 1));
                }

                // Wait for all parallel uploads to complete
                var results = await Task.WhenAll(tasks);
                stopwatch.Stop();

                // Aggregate results
                var totalSuccessful = results.Sum(r => r.Successful);
                var totalFailed = results.Sum(r => r.Failed);
                var overallRate = totalSuccessful / stopwatch.Elapsed.TotalSeconds;

                Console.WriteLine($"\n✅ Parallel upload completed:");
                Console.WriteLine($"   Total successful: {totalSuccessful}");
                Console.WriteLine($"   Total failed: {totalFailed}");
                Console.WriteLine($"   Total time: {stopwatch.Elapsed.TotalSeconds:F2} seconds");
                Console.WriteLine($"   Overall rate: {overallRate:F1} documents/second");
                Console.WriteLine($"   Parallel tasks: {parallelTasks}");

                for (var i = 0; i < results.Length; i++)
                {
                    Console.WriteLine($"   Task {i + 1}: {results[i].Successful} successful, {results[i].Failed} failed");
                }

                return new ParallelUploadResult
                {
                    TotalSuccessful = totalSuccessful,
                    TotalFailed = totalFailed,
                    TotalTime = stopwatch.Elapsed.TotalSeconds,
                    OverallRate = overallRate,
                    ParallelTasks = parallelTasks
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Parallel upload test failed: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Upload batches sequentially for a task
        /// </summary>
        private async Task<UploadThreadResult> UploadBatchesSequentiallyAsync(List<Dictionary<string, object>> documents, int batchSize, int taskId)
        {
            var successful = 0;
            var failed = 0;

            for (var i = 0; i < documents.Count; i += batchSize)
            {
                var batch = documents.Skip(i).Take(batchSize).ToList();

                try
                {
                    var result = await _searchClient!.UploadDocumentsAsync(batch);
                    var batchSuccessful = result.Value.Results.Count(r => r.Succeeded);
                    var batchFailed = result.Value.Results.Count - batchSuccessful;

                    successful += batchSuccessful;
                    failed += batchFailed;

                    // Brief pause between batches
                    await Task.Delay(50);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   Task {taskId} batch failed: {ex.Message}");
                    failed += batch.Count;
                }
            }

            return new UploadThreadResult { Successful = successful, Failed = failed };
        }

        /// <summary>
        /// Monitor memory usage during operations
        /// </summary>
        public async Task MonitorMemoryUsageAsync()
        {
            Console.WriteLine("\n💾 Memory Usage Monitoring...");

            var initialMemory = GC.GetTotalMemory(false);
            Console.WriteLine($"Initial memory usage: {FormatBytes(initialMemory)}");

            // Perform memory-intensive operation
            Console.WriteLine("\nPerforming large document upload...");
            var largeDocuments = GenerateSampleDocuments(2000);

            var stopwatch = Stopwatch.StartNew();
            var successful = 0;

            try
            {
                const int batchSize = 100;
                for (var i = 0; i < largeDocuments.Count; i += batchSize)
                {
                    var batch = largeDocuments.Skip(i).Take(batchSize).ToList();
                    var result = await _searchClient!.UploadDocumentsAsync(batch);
                    successful += result.Value.Results.Count(r => r.Succeeded);

                    // Monitor memory every 10 batches
                    if ((i / batchSize) % 10 == 0)
                    {
                        var currentMemory = GC.GetTotalMemory(false);
                        Console.WriteLine($"   Batch {i / batchSize + 1}: Memory Used: {FormatBytes(currentMemory)}");
                    }

                    await Task.Delay(50);
                }

                stopwatch.Stop();

                var finalMemory = GC.GetTotalMemory(false);
                Console.WriteLine($"\nFinal memory usage: {FormatBytes(finalMemory)}");
                Console.WriteLine($"Memory increase: {FormatBytes(finalMemory - initialMemory)}");

                Console.WriteLine($"\n✅ Memory monitoring completed:");
                Console.WriteLine($"   Documents processed: {successful}");
                Console.WriteLine($"   Time taken: {stopwatch.Elapsed.TotalSeconds:F2} seconds");

                // Force garbage collection
                GC.Collect();
                GC.WaitForPendingFinalizers();
                GC.Collect();

                var afterGcMemory = GC.GetTotalMemory(false);
                Console.WriteLine($"   After GC: {FormatBytes(afterGcMemory)}");
                Console.WriteLine($"   Memory freed: {FormatBytes(finalMemory - afterGcMemory)}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Memory monitoring test failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Apply performance best practices
        /// </summary>
        public async Task ApplyBestPracticesAsync()
        {
            Console.WriteLine("\n🎯 Applying Performance Best Practices...");

            var bestPractices = new[]
            {
                new BestPracticeTest
                {
                    Name = "Optimal Batch Size",
                    Description = "Use batch sizes between 50-100 documents for best performance",
                    TestFunc = async () =>
                    {
                        var documents = GenerateSampleDocuments(100);
                        var stopwatch = Stopwatch.StartTime();
                        var result = await _searchClient!.UploadDocumentsAsync(documents);
                        var elapsed = stopwatch.Elapsed.TotalSeconds;
                        var successful = result.Value.Results.Count(r => r.Succeeded);
                        return new { successful, time = elapsed, rate = successful / elapsed };
                    }
                },
                new BestPracticeTest
                {
                    Name = "Document Size Optimization",
                    Description = "Keep individual documents under 16MB for optimal performance",
                    TestFunc = async () =>
                    {
                        var documents = GenerateSampleDocuments(50).Select(doc =>
                        {
                            // Increase content size
                            var newDoc = new Dictionary<string, object>(doc);
                            if (newDoc.TryGetValue("content", out var content) && content is string contentStr)
                            {
                                newDoc["content"] = string.Concat(Enumerable.Repeat(contentStr, 10));
                            }
                            return newDoc;
                        }).ToList();

                        var stopwatch = Stopwatch.StartTime();
                        var result = await _searchClient!.UploadDocumentsAsync(documents);
                        var elapsed = stopwatch.Elapsed.TotalSeconds;
                        var successful = result.Value.Results.Count(r => r.Succeeded);
                        return new { successful, time = elapsed, rate = successful / elapsed };
                    }
                },
                new BestPracticeTest
                {
                    Name = "Error Handling",
                    Description = "Implement proper error handling and retry logic",
                    TestFunc = async () =>
                    {
                        var documents = GenerateSampleDocuments(50);
                        var successful = 0;
                        var retries = 0;

                        var stopwatch = Stopwatch.StartTime();

                        try
                        {
                            var result = await _searchClient!.UploadDocumentsAsync(documents);
                            successful = result.Value.Results.Count(r => r.Succeeded);

                            // Simulate retry for failed documents
                            var failed = result.Value.Results.Where(r => !r.Succeeded).ToList();
                            if (failed.Any())
                            {
                                retries = 1;
                                // In real scenario, you would retry failed documents
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"   Handled error: {ex.Message}");
                            retries = 1;
                        }

                        var elapsed = stopwatch.Elapsed.TotalSeconds;
                        return new { successful, time = elapsed, retries };
                    }
                }
            };

            foreach (var practice in bestPractices)
            {
                Console.WriteLine($"\n📋 Testing: {practice.Name}");
                Console.WriteLine($"   {practice.Description}");

                try
                {
                    var result = await practice.TestFunc();
                    Console.WriteLine($"   ✅ Result: {result}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Test failed: {ex.Message}");
                }

                // Clear index between tests
                await ClearIndexAsync();
                await Task.Delay(1000);
            }
        }

        /// <summary>
        /// Generate sample documents for testing
        /// </summary>
        private List<Dictionary<string, object>> GenerateSampleDocuments(int count, int startId = 1)
        {
            var documents = new List<Dictionary<string, object>>();
            var categories = new[] { "Technology", "Science", "Business", "Health", "Education" };
            var authors = new[] { "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eve Brown" };

            for (var i = 0; i < count; i++)
            {
                var docId = startId + i;
                var category = categories[i % categories.Length];
                var author = authors[i % authors.Length];

                var document = new Dictionary<string, object>
                {
                    ["id"] = $"doc-{docId}",
                    ["title"] = $"Performance Test Document {docId}: {category} Article",
                    ["content"] = $"This is sample content for document {docId}. It contains information about {category.ToLower()} topics and is written by {author}. The content is generated for testing purposes and demonstrates various aspects of the subject matter. This document is part of a performance optimization test suite.",
                    ["category"] = category,
                    ["author"] = author,
                    ["publishedDate"] = DateTimeOffset.Parse($"2024-02-{(i % 28) + 1:D2}T{i % 24:D2}:00:00Z"),
                    ["rating"] = Math.Round(3.0 + (i % 20) * 0.1, 1), // Rating between 3.0 and 5.0
                    ["viewCount"] = (i + 1) * 10 + (i % 100),
                    ["tags"] = new[] { category.ToLower(), "sample", $"tag{i % 5}" },
                    ["isPublished"] = i % 10 != 0 // 90% published
                };
                documents.Add(document);
            }

            return documents;
        }

        /// <summary>
        /// Clear all documents from the index
        /// </summary>
        private async Task ClearIndexAsync()
        {
            try
            {
                // Get all document IDs
                var searchResults = await _searchClient!.SearchAsync<Dictionary<string, object>>("*", new SearchOptions
                {
                    Select = { "id" },
                    Size = 1000
                });

                var documentIds = new List<string>();
                await foreach (var result in searchResults.Value.GetResultsAsync())
                {
                    documentIds.Add(result.Document["id"].ToString()!);
                }

                if (documentIds.Any())
                {
                    await _searchClient.DeleteDocumentsAsync("id", documentIds);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"   Warning: Could not clear index: {ex.Message}");
            }
        }

        /// <summary>
        /// Format bytes for display
        /// </summary>
        private static string FormatBytes(long bytes)
        {
            var sizes = new[] { "Bytes", "KB", "MB", "GB" };
            if (bytes == 0) return "0 Bytes";
            var i = (int)Math.Floor(Math.Log(bytes) / Math.Log(1024));
            return $"{Math.Round(bytes / Math.Pow(1024, i), 2)} {sizes[i]}";
        }

        /// <summary>
        /// Get performance statistics
        /// </summary>
        public async Task GetPerformanceStatisticsAsync()
        {
            Console.WriteLine("\n📊 Current Performance Statistics:");

            try
            {
                var docCount = await _searchClient!.GetDocumentCountAsync();
                Console.WriteLine($"   Total documents: {docCount.Value}");

                // Sample some documents to show variety
                var searchOptions = new SearchOptions
                {
                    Select = { "id", "title", "category", "author" },
                    Size = 5
                };

                var results = await _searchClient.SearchAsync<Dictionary<string, object>>("*", searchOptions);

                Console.WriteLine("   Sample documents:");
                await foreach (var result in results.Value.GetResultsAsync())
                {
                    var doc = result.Document;
                    Console.WriteLine($"     - {doc["id"]}: {doc["title"]} ({doc["category"]})");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to get statistics: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Result of batch size testing
    /// </summary>
    public class BatchSizeResult
    {
        public int BatchSize { get; set; }
        public int TotalSuccessful { get; set; }
        public int TotalFailed { get; set; }
        public double TotalTime { get; set; }
        public double OverallRate { get; set; }
    }

    /// <summary>
    /// Result of parallel upload testing
    /// </summary>
    public class ParallelUploadResult
    {
        public int TotalSuccessful { get; set; }
        public int TotalFailed { get; set; }
        public double TotalTime { get; set; }
        public double OverallRate { get; set; }
        public int ParallelTasks { get; set; }
    }

    /// <summary>
    /// Result of upload thread
    /// </summary>
    public class UploadThreadResult
    {
        public int Successful { get; set; }
        public int Failed { get; set; }
    }

    /// <summary>
    /// Best practice test definition
    /// </summary>
    public class BestPracticeTest
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public Func<Task<object>> TestFunc { get; set; } = null!;
    }

    /// <summary>
    /// Main program demonstrating performance optimization
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("=".PadRight(60, '='));
            Console.WriteLine("Module 3: Performance Optimization Example (C#)");
            Console.WriteLine("=".PadRight(60, '='));

            // Initialize the performance optimizer
            PerformanceOptimizer optimizer;
            try
            {
                optimizer = new PerformanceOptimizer();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                return;
            }

            // Create clients
            if (!await optimizer.CreateClientsAsync())
            {
                Console.WriteLine("❌ Failed to create clients. Exiting.");
                return;
            }

            // Create performance test index
            var indexName = await optimizer.CreatePerformanceTestIndexAsync();
            if (indexName == null)
            {
                Console.WriteLine("❌ Failed to create performance test index. Exiting.");
                return;
            }

            Console.WriteLine($"\n🎯 Running performance optimization demonstrations on index '{indexName}'...");

            // Run demonstrations
            var demonstrations = new (string Name, Func<Task> Func)[]
            {
                ("Batch Size Testing", async () => await optimizer.TestBatchSizesAsync()),
                ("Parallel Upload Testing", async () => await optimizer.TestParallelUploadsAsync()),
                ("Memory Usage Monitoring", optimizer.MonitorMemoryUsageAsync),
                ("Best Practices Application", optimizer.ApplyBestPracticesAsync)
            };

            foreach (var (name, func) in demonstrations)
            {
                Console.WriteLine($"\n{"=".PadRight(20, '=')} {name} {"=".PadRight(20, '=')}");
                try
                {
                    await func();
                    Console.WriteLine($"✅ {name} completed successfully");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"❌ {name} failed: {ex.Message}");
                }

                // Brief pause between demonstrations
                await Task.Delay(2000);
            }

            // Show current statistics
            Console.WriteLine($"\n{"=".PadRight(20, '=')} Current Statistics {"=".PadRight(20, '=')}");
            await optimizer.GetPerformanceStatisticsAsync();

            Console.WriteLine("\n" + "=".PadRight(60, '='));
            Console.WriteLine("Example completed!");
            Console.WriteLine("=".PadRight(60, '='));

            Console.WriteLine("\n📚 What you learned:");
            Console.WriteLine("✅ How to optimize batch sizes for different scenarios");
            Console.WriteLine("✅ How to implement parallel upload strategies");
            Console.WriteLine("✅ How to monitor and measure performance metrics");
            Console.WriteLine("✅ How to apply performance best practices");
            Console.WriteLine("✅ How to handle memory and resource management");

            Console.WriteLine("\n🚀 Next steps:");
            Console.WriteLine("1. Experiment with different batch sizes for your data");
            Console.WriteLine("2. Implement parallel processing for large datasets");
            Console.WriteLine("3. Run the next example: 06_ErrorHandling.cs");
            Console.WriteLine("4. Monitor performance in your production environment");

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}