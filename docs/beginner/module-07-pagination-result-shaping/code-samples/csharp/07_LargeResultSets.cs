/*
 * Module 7: Pagination & Result Shaping - Large Result Sets
 * Azure AI Search .NET SDK Example
 * 
 * This example demonstrates efficient techniques for handling large result sets in Azure AI Search,
 * including streaming, batching, parallel processing, and memory management strategies.
 * 
 * Prerequisites:
 * - Azure AI Search service
 * - .NET 6.0 or later
 * - Azure.Search.Documents package
 * - Sample data index with substantial data
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;
using System.IO;
using System.Text.Json;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace AzureAISearch.Module07.LargeResultSets
{
    public class ProcessingStats
    {
        public int TotalProcessed { get; set; }
        public double TotalTimeMs { get; set; }
        public int BatchCount { get; set; }
        public int Errors { get; set; }
        public double MemoryPeakMb { get; set; }
        public double ThroughputDocsPerSec { get; set; }

        public void UpdateThroughput()
        {
            if (TotalTimeMs > 0)
            {
                ThroughputDocsPerSec = TotalProcessed / (TotalTimeMs / 1000);
            }
        }
    }

    public class LargeResultSetHandler
    {
        private readonly SearchClient _searchClient;
        private readonly ProcessingStats _stats;

        public LargeResultSetHandler(string endpoint, string indexName, string apiKey)
        {
            var credential = new AzureKeyCredential(apiKey);
            _searchClient = new SearchClient(new Uri(endpoint), indexName, credential);
            _stats = new ProcessingStats();
        }

        /// <summary>
        /// Stream search results in batches for memory-efficient processing
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="batchSize">Size of each batch</param>
        /// <param name="maxResults">Maximum number of results to process</param>
        /// <param name="selectFields">Fields to select for reduced payload</param>
        /// <param name="progressCallback">Optional callback for progress updates</param>
        /// <returns>Enumerable of individual documents</returns>
        public async IAsyncEnumerable<SearchDocument> StreamResultsAsync(
            string query, 
            int batchSize = 100, 
            int? maxResults = null,
            IList<string> selectFields = null,
            Action<int, double> progressCallback = null)
        {
            Console.WriteLine($"🌊 Starting streaming search for query: '{query}'");
            Console.WriteLine($"📊 Batch size: {batchSize}, Max results: {maxResults?.ToString() ?? "unlimited"}");

            int currentSkip = 0;
            int totalProcessed = 0;
            var startTime = DateTime.UtcNow;

            while (true)
            {
                // Calculate batch size for this iteration
                int currentBatchSize = batchSize;
                if (maxResults.HasValue)
                {
                    int remaining = maxResults.Value - totalProcessed;
                    if (remaining <= 0) break;
                    currentBatchSize = Math.Min(batchSize, remaining);
                }

                var batchStart = DateTime.UtcNow;

                try
                {
                    // Fetch batch
                    var searchOptions = new SearchOptions
                    {
                        Skip = currentSkip,
                        Size = currentBatchSize,
                        Select = { }
                    };

                    if (selectFields != null)
                    {
                        foreach (var field in selectFields)
                        {
                            searchOptions.Select.Add(field);
                        }
                    }

                    var searchResults = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                    var batchDocs = new List<SearchDocument>();

                    await foreach (var result in searchResults.Value.GetResultsAsync())
                    {
                        batchDocs.Add(result.Document);
                    }

                    var batchDuration = (DateTime.UtcNow - batchStart).TotalMilliseconds;

                    if (batchDocs.Count == 0)
                    {
                        Console.WriteLine($"   🏁 No more results at skip={currentSkip}");
                        break;
                    }

                    // Yield documents
                    foreach (var doc in batchDocs)
                    {
                        yield return doc;
                        totalProcessed++;
                    }

                    currentSkip += batchDocs.Count;
                    _stats.BatchCount++;

                    // Progress reporting
                    if (progressCallback != null)
                    {
                        progressCallback(totalProcessed, batchDuration);
                    }
                    else if (totalProcessed % (batchSize * 5) == 0) // Report every 5 batches
                    {
                        var elapsed = (DateTime.UtcNow - startTime).TotalSeconds;
                        var rate = elapsed > 0 ? totalProcessed / elapsed : 0;
                        Console.WriteLine($"   📦 Processed {totalProcessed} documents ({rate:F1} docs/sec)");
                    }

                    // Break if we got fewer results than requested (end of data)
                    if (batchDocs.Count < currentBatchSize)
                    {
                        Console.WriteLine($"   🏁 Reached end of available results");
                        break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error in batch at skip={currentSkip}: {ex.Message}");
                    _stats.Errors++;
                    break;
                }
            }

            // Update final statistics
            var totalTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            _stats.TotalProcessed = totalProcessed;
            _stats.TotalTimeMs = totalTime;
            _stats.UpdateThroughput();

            Console.WriteLine($"✅ Streaming completed: {totalProcessed} documents in {totalTime:F1}ms");
        }

        /// <summary>
        /// Process large result sets in batches with optional parallel processing
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="processorFunc">Function to process each batch</param>
        /// <param name="batchSize">Size of each batch</param>
        /// <param name="maxResults">Maximum number of results to process</param>
        /// <param name="parallel">Whether to use parallel processing</param>
        /// <param name="maxDegreeOfParallelism">Maximum degree of parallelism</param>
        /// <returns>List of processed results</returns>
        public async Task<List<T>> BatchProcessResultsAsync<T>(
            string query,
            Func<List<SearchDocument>, Task<T>> processorFunc,
            int batchSize = 100,
            int? maxResults = null,
            bool parallel = false,
            int maxDegreeOfParallelism = 4)
        {
            Console.WriteLine($"🔄 Starting batch processing for query: '{query}'");
            Console.WriteLine($"📊 Batch size: {batchSize}, Parallel: {parallel}");

            // Collect batches
            var batches = new List<List<SearchDocument>>();
            var currentBatch = new List<SearchDocument>();

            await foreach (var doc in StreamResultsAsync(query, batchSize, maxResults, 
                new[] { "hotelId", "hotelName", "description" }))
            {
                currentBatch.Add(doc);

                if (currentBatch.Count >= batchSize)
                {
                    batches.Add(new List<SearchDocument>(currentBatch));
                    currentBatch.Clear();
                }
            }

            // Add remaining documents
            if (currentBatch.Any())
            {
                batches.Add(currentBatch);
            }

            Console.WriteLine($"📦 Created {batches.Count} batches for processing");

            // Process batches
            if (parallel && batches.Count > 1)
            {
                return await ProcessBatchesParallelAsync(batches, processorFunc, maxDegreeOfParallelism);
            }
            else
            {
                return await ProcessBatchesSequentialAsync(batches, processorFunc);
            }
        }

        /// <summary>
        /// Process batches sequentially
        /// </summary>
        private async Task<List<T>> ProcessBatchesSequentialAsync<T>(
            List<List<SearchDocument>> batches, 
            Func<List<SearchDocument>, Task<T>> processorFunc)
        {
            var results = new List<T>();

            for (int i = 0; i < batches.Count; i++)
            {
                Console.WriteLine($"   Processing batch {i + 1}/{batches.Count} ({batches[i].Count} documents)");

                try
                {
                    var batchResult = await processorFunc(batches[i]);
                    results.Add(batchResult);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error processing batch {i + 1}: {ex.Message}");
                    _stats.Errors++;
                }
            }

            return results;
        }

        /// <summary>
        /// Process batches in parallel
        /// </summary>
        private async Task<List<T>> ProcessBatchesParallelAsync<T>(
            List<List<SearchDocument>> batches,
            Func<List<SearchDocument>, Task<T>> processorFunc,
            int maxDegreeOfParallelism)
        {
            var results = new List<(int Index, T Result)>();
            var semaphore = new SemaphoreSlim(maxDegreeOfParallelism);

            var tasks = batches.Select(async (batch, index) =>
            {
                await semaphore.WaitAsync();
                try
                {
                    var result = await processorFunc(batch);
                    Console.WriteLine($"   ✅ Completed batch {index + 1}");
                    return (Index: index, Result: result);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error in batch {index + 1}: {ex.Message}");
                    _stats.Errors++;
                    return (Index: index, Result: default(T));
                }
                finally
                {
                    semaphore.Release();
                }
            });

            var completedTasks = await Task.WhenAll(tasks);
            results.AddRange(completedTasks);

            // Sort results by batch index to maintain order
            results.Sort((a, b) => a.Index.CompareTo(b.Index));
            return results.Select(r => r.Result).ToList();
        }

        /// <summary>
        /// Perform parallel searches across different ranges for large datasets
        /// </summary>
        /// <param name="baseQuery">Base search query</param>
        /// <param name="ranges">List of range filters</param>
        /// <param name="batchSize">Batch size for each range</param>
        /// <returns>Dictionary of results by range</returns>
        public async Task<Dictionary<string, List<SearchDocument>>> ParallelRangeSearchAsync(
            string baseQuery, 
            List<(string Name, string Filter)> ranges, 
            int batchSize = 50)
        {
            Console.WriteLine($"🔄 Starting parallel range search for query: '{baseQuery}'");
            Console.WriteLine($"📊 Ranges: {ranges.Count}, Batch size: {batchSize}");

            var tasks = ranges.Select(async range =>
            {
                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Filter = range.Filter,
                        Size = batchSize,
                        Select = { "hotelId", "hotelName", "rating" }
                    };

                    var searchResults = await _searchClient.SearchAsync<SearchDocument>(baseQuery, searchOptions);
                    var docs = new List<SearchDocument>();

                    await foreach (var result in searchResults.Value.GetResultsAsync())
                    {
                        docs.Add(result.Document);
                    }

                    Console.WriteLine($"   ✅ Range '{range.Name}': {docs.Count} results");
                    return (range.Name, docs);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error in range {range.Name}: {ex.Message}");
                    return (range.Name, new List<SearchDocument>());
                }
            });

            var rangeResults = await Task.WhenAll(tasks);
            var results = rangeResults.ToDictionary(r => r.Name, r => r.docs);

            var totalResults = results.Values.Sum(docs => docs.Count);
            Console.WriteLine($"✅ Parallel range search completed: {totalResults} total results");

            return results;
        }

        /// <summary>
        /// Export large result sets to file with memory efficiency
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="outputFile">Output file path</param>
        /// <param name="batchSize">Batch size for processing</param>
        /// <param name="format">Output format ('jsonl' or 'json')</param>
        /// <returns>Export statistics</returns>
        public async Task<ExportStats> MemoryEfficientExportAsync(
            string query, 
            string outputFile, 
            int batchSize = 1000, 
            string format = "jsonl")
        {
            Console.WriteLine($"💾 Starting memory-efficient export for query: '{query}'");
            Console.WriteLine($"📁 Output file: {outputFile}, Format: {format}");

            var startTime = DateTime.UtcNow;
            int exportedCount = 0;

            try
            {
                using var fileStream = new FileStream(outputFile, FileMode.Create, FileAccess.Write);
                using var writer = new StreamWriter(fileStream);

                if (format == "json")
                {
                    await writer.WriteLineAsync("[");
                }

                bool firstDoc = true;

                await foreach (var doc in StreamResultsAsync(query, batchSize, null, 
                    new[] { "hotelId", "hotelName", "description", "rating" }))
                {
                    string content;

                    if (format == "jsonl")
                    {
                        content = JsonSerializer.Serialize(doc);
                    }
                    else // json
                    {
                        if (!firstDoc)
                        {
                            await writer.WriteAsync(",\n");
                        }
                        content = "  " + JsonSerializer.Serialize(doc);
                        firstDoc = false;
                    }

                    await writer.WriteLineAsync(content);
                    exportedCount++;

                    // Progress reporting
                    if (exportedCount % 1000 == 0)
                    {
                        var elapsed = (DateTime.UtcNow - startTime).TotalSeconds;
                        var rate = elapsed > 0 ? exportedCount / elapsed : 0;
                        Console.WriteLine($"   📝 Exported {exportedCount} documents ({rate:F1} docs/sec)");
                    }
                }

                if (format == "json")
                {
                    await writer.WriteLineAsync("\n]");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Export error: {ex.Message}");
                return new ExportStats { Error = ex.Message, ExportedCount = exportedCount };
            }

            var totalTime = (DateTime.UtcNow - startTime).TotalSeconds;
            var fileInfo = new FileInfo(outputFile);
            var fileSize = fileInfo.Exists ? fileInfo.Length : 0;

            var stats = new ExportStats
            {
                ExportedCount = exportedCount,
                TotalTimeSeconds = totalTime,
                ThroughputDocsPerSec = totalTime > 0 ? exportedCount / totalTime : 0,
                OutputFile = outputFile,
                FileSizeBytes = fileSize,
                FileSizeMb = fileSize / (1024.0 * 1024.0),
                Format = format
            };

            Console.WriteLine($"✅ Export completed: {exportedCount} documents in {totalTime:F1}s");
            Console.WriteLine($"📁 File size: {stats.FileSizeMb:F2} MB");

            return stats;
        }

        /// <summary>
        /// Get current processing statistics
        /// </summary>
        /// <returns>Current processing statistics</returns>
        public ProcessingStats GetProcessingStats()
        {
            return _stats;
        }

        /// <summary>
        /// Reset processing statistics
        /// </summary>
        public void ResetStats()
        {
            _stats.TotalProcessed = 0;
            _stats.TotalTimeMs = 0;
            _stats.BatchCount = 0;
            _stats.Errors = 0;
            _stats.MemoryPeakMb = 0;
            _stats.ThroughputDocsPerSec = 0;
        }
    }

    public class ExportStats
    {
        public int ExportedCount { get; set; }
        public double TotalTimeSeconds { get; set; }
        public double ThroughputDocsPerSec { get; set; }
        public string OutputFile { get; set; }
        public long FileSizeBytes { get; set; }
        public double FileSizeMb { get; set; }
        public string Format { get; set; }
        public string Error { get; set; }
    }

    // Example processor functions
    public static class BatchProcessors
    {
        /// <summary>
        /// Example batch processor: analyze sentiment of descriptions
        /// </summary>
        public static async Task<SentimentAnalysisResult> AnalyzeSentimentBatchAsync(List<SearchDocument> batch)
        {
            await Task.Delay(10); // Simulate processing time

            int positiveCount = 0;
            int negativeCount = 0;
            int neutralCount = 0;

            foreach (var doc in batch)
            {
                var description = doc.TryGetValue("description", out var desc) ? desc.ToString().ToLower() : "";

                // Simple sentiment analysis based on keywords
                var positiveWords = new[] { "excellent", "amazing", "wonderful", "great", "fantastic" };
                var negativeWords = new[] { "poor", "bad", "terrible", "awful", "disappointing" };

                var positiveScore = positiveWords.Count(word => description.Contains(word));
                var negativeScore = negativeWords.Count(word => description.Contains(word));

                if (positiveScore > negativeScore)
                    positiveCount++;
                else if (negativeScore > positiveScore)
                    negativeCount++;
                else
                    neutralCount++;
            }

            return new SentimentAnalysisResult
            {
                BatchSize = batch.Count,
                Positive = positiveCount,
                Negative = negativeCount,
                Neutral = neutralCount,
                SentimentRatio = batch.Count > 0 ? (double)positiveCount / batch.Count : 0
            };
        }

        /// <summary>
        /// Example batch processor: extract common keywords
        /// </summary>
        public static async Task<KeywordExtractionResult> ExtractKeywordsBatchAsync(List<SearchDocument> batch)
        {
            await Task.Delay(10); // Simulate processing time

            var wordCounts = new Dictionary<string, int>();

            foreach (var doc in batch)
            {
                var description = doc.TryGetValue("description", out var desc) ? desc.ToString().ToLower() : "";
                var words = description.Split(new[] { ' ', '\t', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);

                foreach (var word in words)
                {
                    // Simple word cleaning
                    var cleanWord = word.Trim('.', ',', '!', '?', ';', ':', '"', '(', ')', '[', ']', '{', '}');
                    if (cleanWord.Length > 3) // Only count words longer than 3 characters
                    {
                        wordCounts[cleanWord] = wordCounts.GetValueOrDefault(cleanWord, 0) + 1;
                    }
                }
            }

            // Get top 10 words
            var topWords = wordCounts
                .OrderByDescending(kvp => kvp.Value)
                .Take(10)
                .ToList();

            return new KeywordExtractionResult
            {
                BatchSize = batch.Count,
                UniqueWords = wordCounts.Count,
                TopWords = topWords,
                TotalWords = wordCounts.Values.Sum()
            };
        }
    }

    public class SentimentAnalysisResult
    {
        public int BatchSize { get; set; }
        public int Positive { get; set; }
        public int Negative { get; set; }
        public int Neutral { get; set; }
        public double SentimentRatio { get; set; }
    }

    public class KeywordExtractionResult
    {
        public int BatchSize { get; set; }
        public int UniqueWords { get; set; }
        public List<KeyValuePair<string, int>> TopWords { get; set; }
        public int TotalWords { get; set; }
    }

    // Main program
    public class Program
    {
        public static async Task Main(string[] args)
        {
            // Configuration
            var configuration = new ConfigurationBuilder()
                .AddEnvironmentVariables()
                .Build();

            var endpoint = configuration["SEARCH_ENDPOINT"] ?? "https://your-search-service.search.windows.net";
            var apiKey = configuration["SEARCH_API_KEY"] ?? "your-api-key";
            var indexName = configuration["INDEX_NAME"] ?? "hotels-sample";

            Console.WriteLine("🌊 Azure AI Search - Large Result Sets Handling");
            Console.WriteLine(new string('=', 50));

            // Initialize handler
            var handler = new LargeResultSetHandler(endpoint, indexName, apiKey);

            try
            {
                // Example 1: Streaming results
                Console.WriteLine("\n1. Streaming Results");
                Console.WriteLine(new string('-', 20));

                int processedCount = 0;
                await foreach (var doc in handler.StreamResultsAsync("*", 25, 100))
                {
                    processedCount++;
                    if (processedCount <= 3) // Show first 3 documents
                    {
                        var hotelName = doc.TryGetValue("hotelName", out var name) ? name.ToString() : "Unknown";
                        Console.WriteLine($"   Document {processedCount}: {hotelName}");
                    }
                }

                Console.WriteLine($"Total streamed: {processedCount} documents");

                // Example 2: Batch processing with sentiment analysis
                Console.WriteLine("\n2. Batch Processing - Sentiment Analysis");
                Console.WriteLine(new string('-', 40));

                var sentimentResults = await handler.BatchProcessResultsAsync(
                    "hotel",
                    BatchProcessors.AnalyzeSentimentBatchAsync,
                    20,
                    100,
                    true,
                    3
                );

                if (sentimentResults.Any())
                {
                    var totalPositive = sentimentResults.Sum(r => r.Positive);
                    var totalNegative = sentimentResults.Sum(r => r.Negative);
                    var totalNeutral = sentimentResults.Sum(r => r.Neutral);
                    var totalDocs = sentimentResults.Sum(r => r.BatchSize);

                    Console.WriteLine($"Sentiment analysis results ({totalDocs} documents):");
                    Console.WriteLine($"  Positive: {totalPositive} ({(double)totalPositive / totalDocs * 100:F1}%)");
                    Console.WriteLine($"  Negative: {totalNegative} ({(double)totalNegative / totalDocs * 100:F1}%)");
                    Console.WriteLine($"  Neutral: {totalNeutral} ({(double)totalNeutral / totalDocs * 100:F1}%)");
                }

                // Example 3: Parallel range search
                Console.WriteLine("\n3. Parallel Range Search");
                Console.WriteLine(new string('-', 26));

                var ranges = new List<(string Name, string Filter)>
                {
                    ("High Rating", "rating ge 4"),
                    ("Medium Rating", "rating ge 3 and rating lt 4"),
                    ("Low Rating", "rating lt 3")
                };

                var rangeResults = await handler.ParallelRangeSearchAsync("hotel", ranges, 30);

                foreach (var (rangeName, docs) in rangeResults)
                {
                    Console.WriteLine($"  {rangeName}: {docs.Count} results");
                    if (docs.Any())
                    {
                        var avgRating = docs
                            .Where(doc => doc.TryGetValue("rating", out var rating) && rating != null)
                            .Average(doc => Convert.ToDouble(doc["rating"]));
                        Console.WriteLine($"    Average rating: {avgRating:F2}");
                    }
                }

                // Example 4: Memory-efficient export
                Console.WriteLine("\n4. Memory-Efficient Export");
                Console.WriteLine(new string('-', 27));

                var outputFile = "large_results_export.jsonl";
                var exportStats = await handler.MemoryEfficientExportAsync(
                    "luxury",
                    outputFile,
                    50,
                    "jsonl"
                );

                if (string.IsNullOrEmpty(exportStats.Error))
                {
                    Console.WriteLine("Export completed:");
                    Console.WriteLine($"  Documents: {exportStats.ExportedCount}");
                    Console.WriteLine($"  File size: {exportStats.FileSizeMb:F2} MB");
                    Console.WriteLine($"  Throughput: {exportStats.ThroughputDocsPerSec:F1} docs/sec");

                    // Clean up
                    if (File.Exists(outputFile))
                    {
                        File.Delete(outputFile);
                        Console.WriteLine($"  Cleaned up: {outputFile}");
                    }
                }

                // Show final statistics
                Console.WriteLine("\n📊 Processing Statistics");
                Console.WriteLine(new string('-', 24));

                var stats = handler.GetProcessingStats();
                Console.WriteLine($"Total processed: {stats.TotalProcessed}");
                Console.WriteLine($"Total batches: {stats.BatchCount}");
                Console.WriteLine($"Errors: {stats.Errors}");
                Console.WriteLine($"Throughput: {stats.ThroughputDocsPerSec:F1} docs/sec");

                Console.WriteLine("\n✅ Large result set handling demonstration completed!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error during processing: {ex.Message}");
            }
        }
    }
}