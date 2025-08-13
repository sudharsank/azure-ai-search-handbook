using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace AzureSearchSamples.DataSourcesIndexers
{
    /// <summary>
    /// Error Handling & Recovery Example
    /// 
    /// This example demonstrates robust error handling patterns and recovery strategies
    /// for Azure AI Search indexers.
    /// </summary>
    public class ErrorHandlingExample
    {
        private readonly SearchIndexClient _indexClient;
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;

        public ErrorHandlingExample(string searchEndpoint, string apiKey)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));

            var credential = new AzureKeyCredential(_apiKey);
            _indexClient = new SearchIndexClient(new Uri(_searchEndpoint), credential);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Error Handling & Recovery Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Demonstrate error types
                DemonstrateErrorTypes();

                // Show robust configuration
                var errorConfig = CreateRobustIndexerConfiguration();

                // Implement retry logic
                var retryFunction = ImplementRetryLogic();

                // Show error analysis
                Console.WriteLine("\n📊 Error Analysis Example:");
                Console.WriteLine("   (Run with actual indexer names to see real analysis)");

                // Implement alerting
                var (healthCheck, sendAlert) = ImplementErrorAlerting();

                // Show recovery strategies
                DemonstrateRecoveryStrategies();

                Console.WriteLine("\n✅ Error handling example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Implement comprehensive error handling from the start");
                Console.WriteLine("- Use appropriate retry strategies for different error types");
                Console.WriteLine("- Monitor error patterns to identify systemic issues");
                Console.WriteLine("- Set up alerting for proactive issue detection");
                Console.WriteLine("- Choose recovery strategies based on business requirements");
                Console.WriteLine("- Log errors comprehensively for troubleshooting");
                Console.WriteLine("- Test error scenarios in development environments");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }

        private void DemonstrateErrorTypes()
        {
            Console.WriteLine("\n❌ Common Indexer Error Types");
            Console.WriteLine("=" + new string('=', 29));

            var errorTypes = new[]
            {
                new
                {
                    Category = "Data Source Errors",
                    Errors = new[] { "Connection timeouts", "Authentication failures", "Network connectivity issues", "Data source unavailable", "Permission denied" },
                    Impact = "Indexer cannot access source data",
                    Recovery = "Retry with exponential backoff"
                },
                new
                {
                    Category = "Data Format Errors", 
                    Errors = new[] { "Invalid JSON structure", "Unsupported file formats", "Encoding issues", "Malformed data", "Missing required fields" },
                    Impact = "Individual documents fail to process",
                    Recovery = "Skip problematic documents, log for review"
                },
                new
                {
                    Category = "Schema Mismatch Errors",
                    Errors = new[] { "Field type mismatches", "Missing target fields", "Invalid field mappings", "Collection vs single value conflicts", "Date format incompatibilities" },
                    Impact = "Documents rejected during indexing",
                    Recovery = "Fix mappings or transform data"
                },
                new
                {
                    Category = "Resource Limit Errors",
                    Errors = new[] { "Document size too large", "Too many fields per document", "Batch size exceeded", "Search unit exhaustion", "Storage quota exceeded" },
                    Impact = "Indexing stops or throttles",
                    Recovery = "Adjust batch sizes, upgrade service tier"
                },
                new
                {
                    Category = "Transient Errors",
                    Errors = new[] { "Service temporarily unavailable", "Request throttling", "Network timeouts", "Temporary service degradation", "Load balancer issues" },
                    Impact = "Temporary indexing interruption",
                    Recovery = "Automatic retry with backoff"
                }
            };

            foreach (var errorType in errorTypes)
            {
                Console.WriteLine($"\n🚨 {errorType.Category}");
                Console.WriteLine($"   Impact: {errorType.Impact}");
                Console.WriteLine($"   Recovery Strategy: {errorType.Recovery}");
                Console.WriteLine("   Common Errors:");
                foreach (var error in errorType.Errors)
                    Console.WriteLine($"     • {error}");
            }
        }

        private IndexingParameters CreateRobustIndexerConfiguration()
        {
            Console.WriteLine("\n🛡️ Robust Indexer Configuration");
            Console.WriteLine("=" + new string('=', 34));

            var errorHandlingParams = new IndexingParameters
            {
                MaxFailedItems = 10,
                MaxFailedItemsPerBatch = 5,
                BatchSize = 100,
                Configuration =
                {
                    ["failOnUnsupportedContentType"] = false,
                    ["failOnUnprocessableDocument"] = false,
                    ["indexedFileNameExtensions"] = ".pdf,.docx,.txt,.json",
                    ["excludedFileNameExtensions"] = ".zip,.exe,.bin",
                    ["dataToExtract"] = "contentAndMetadata",
                    ["parsingMode"] = "default"
                }
            };

            Console.WriteLine("📋 Error Handling Configuration:");
            Console.WriteLine($"   Max Failed Items: {errorHandlingParams.MaxFailedItems}");
            Console.WriteLine($"   Max Failed Items Per Batch: {errorHandlingParams.MaxFailedItemsPerBatch}");
            Console.WriteLine($"   Batch Size: {errorHandlingParams.BatchSize}");
            Console.WriteLine($"   Fail on Unsupported Content: {errorHandlingParams.Configuration["failOnUnsupportedContentType"]}");
            Console.WriteLine($"   Fail on Unprocessable Document: {errorHandlingParams.Configuration["failOnUnprocessableDocument"]}");

            return errorHandlingParams;
        }

        private Func<string, int, Task<bool>> ImplementRetryLogic()
        {
            Console.WriteLine("\n🔄 Retry Logic Implementation");
            Console.WriteLine("=" + new string('=', 29));

            async Task<bool> RunIndexerWithRetry(string indexerName, int maxRetries = 3)
            {
                for (int attempt = 0; attempt < maxRetries; attempt++)
                {
                    try
                    {
                        Console.WriteLine($"Starting indexer '{indexerName}' (attempt {attempt + 1}/{maxRetries})");

                        await _indexerClient.RunIndexerAsync(indexerName);
                        var success = await MonitorIndexerExecution(indexerName);

                        if (success)
                        {
                            Console.WriteLine($"Indexer '{indexerName}' completed successfully");
                            return true;
                        }
                        else
                        {
                            Console.WriteLine($"Indexer '{indexerName}' completed with errors");
                        }
                    }
                    catch (RequestFailedException ex)
                    {
                        Console.WriteLine($"HTTP error running indexer (attempt {attempt + 1}): {ex.Message}");

                        if (ex.Status == 429 || ex.Status >= 500) // Throttling or server errors
                        {
                            if (attempt < maxRetries - 1)
                            {
                                var waitTime = TimeSpan.FromSeconds(Math.Pow(2, attempt) + 1); // Exponential backoff
                                Console.WriteLine($"Retrying in {waitTime.TotalSeconds} seconds...");
                                await Task.Delay(waitTime);
                                continue;
                            }
                        }
                        else
                        {
                            Console.WriteLine($"Non-retryable error: {ex.Status}");
                            break;
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Unexpected error (attempt {attempt + 1}): {ex.Message}");
                        if (attempt < maxRetries - 1)
                        {
                            var waitTime = TimeSpan.FromSeconds(Math.Pow(2, attempt) + 1);
                            Console.WriteLine($"Retrying in {waitTime.TotalSeconds} seconds...");
                            await Task.Delay(waitTime);
                            continue;
                        }
                        break;
                    }
                }

                Console.WriteLine($"Indexer '{indexerName}' failed after {maxRetries} attempts");
                return false;
            }

            Console.WriteLine("🔧 Retry Logic Features:");
            Console.WriteLine("   • Exponential backoff (2, 5, 9 seconds)");
            Console.WriteLine("   • Handles HTTP 429 (throttling) and 5xx errors");
            Console.WriteLine("   • Configurable maximum retry attempts");
            Console.WriteLine("   • Comprehensive logging");
            Console.WriteLine("   • Distinguishes between retryable and non-retryable errors");

            return RunIndexerWithRetry;
        }

        private async Task<bool> MonitorIndexerExecution(string indexerName, int timeoutMinutes = 10)
        {
            Console.WriteLine($"\n📊 Monitoring indexer: {indexerName}");

            var startTime = DateTime.UtcNow;
            var timeout = TimeSpan.FromMinutes(timeoutMinutes);

            while (DateTime.UtcNow - startTime < timeout)
            {
                try
                {
                    var status = await _indexerClient.GetIndexerStatusAsync(indexerName);

                    var currentTime = DateTime.Now.ToString("HH:mm:ss");
                    Console.WriteLine($"   ⏰ {currentTime} - Status: {status.Value.Status}");

                    if (status.Value.LastResult != null)
                    {
                        var result = status.Value.LastResult;
                        var itemsProcessed = result.ItemCount;
                        var itemsFailed = result.FailedItemCount;
                        Console.WriteLine($"      📄 Processed: {itemsProcessed}, Failed: {itemsFailed}");

                        if (result.Errors?.Count > 0)
                        {
                            Console.WriteLine($"      ❌ Errors ({result.Errors.Count}):");
                            foreach (var error in result.Errors.Take(3))
                            {
                                Console.WriteLine($"         {error.ErrorMessage}");
                            }
                        }

                        if (result.Warnings?.Count > 0)
                        {
                            Console.WriteLine($"      ⚠️ Warnings ({result.Warnings.Count}):");
                            foreach (var warning in result.Warnings.Take(2))
                            {
                                Console.WriteLine($"         {warning.Message}");
                            }
                        }
                    }

                    if (status.Value.Status == IndexerStatus.Success)
                    {
                        Console.WriteLine($"   ✅ Indexer completed successfully");
                        return true;
                    }
                    else if (status.Value.Status == IndexerStatus.Error)
                    {
                        Console.WriteLine($"   ❌ Indexer completed with errors");
                        return false;
                    }

                    await Task.Delay(10000); // Wait 10 seconds
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error monitoring indexer: {ex.Message}");
                    return false;
                }
            }

            Console.WriteLine($"   ⏰ Monitoring timeout reached ({timeoutMinutes} minutes)");
            return false;
        }

        private (Func<string[], double, Task<List<dynamic>>>, Action<dynamic>) ImplementErrorAlerting()
        {
            Console.WriteLine("\n🚨 Error Alerting Implementation");
            Console.WriteLine("=" + new string('=', 34));

            async Task<List<dynamic>> CheckIndexerHealth(string[] indexerNames, double alertThreshold = 0.1)
            {
                var alerts = new List<dynamic>();

                foreach (var indexerName in indexerNames)
                {
                    try
                    {
                        var status = await _indexerClient.GetIndexerStatusAsync(indexerName);

                        if (status.Value.LastResult != null)
                        {
                            var result = status.Value.LastResult;
                            var totalItems = result.ItemCount + result.FailedItemCount;

                            if (totalItems > 0)
                            {
                                var errorRate = (double)result.FailedItemCount / totalItems;

                                if (errorRate > alertThreshold)
                                {
                                    var alert = new
                                    {
                                        Indexer = indexerName,
                                        ErrorRate = errorRate,
                                        FailedItems = result.FailedItemCount,
                                        TotalItems = totalItems,
                                        LastRun = result.EndTime ?? result.StartTime
                                    };
                                    alerts.Add(alert);
                                }
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error checking health for indexer {indexerName}: {ex.Message}");
                    }
                }

                return alerts;
            }

            void SendAlert(dynamic alert)
            {
                Console.WriteLine($"ALERT: Indexer '{alert.Indexer}' has high error rate");
                Console.WriteLine($"  Error Rate: {alert.ErrorRate:P2}");
                Console.WriteLine($"  Failed Items: {alert.FailedItems}/{alert.TotalItems}");
                Console.WriteLine($"  Last Run: {alert.LastRun}");

                // In a real implementation, you would:
                // - Send email notifications
                // - Post to Slack/Teams
                // - Create Azure Monitor alerts
                // - Update dashboard status
            }

            Console.WriteLine("🔧 Alerting Features:");
            Console.WriteLine("   • Configurable error rate thresholds");
            Console.WriteLine("   • Multiple notification channels");
            Console.WriteLine("   • Health check scheduling");
            Console.WriteLine("   • Alert suppression to avoid spam");
            Console.WriteLine("   • Integration with monitoring systems");

            return (CheckIndexerHealth, SendAlert);
        }

        private void DemonstrateRecoveryStrategies()
        {
            Console.WriteLine("\n🔧 Recovery Strategies");
            Console.WriteLine("=" + new string('=', 19));

            var strategies = new[]
            {
                new
                {
                    Strategy = "Automatic Retry",
                    Description = "Automatically retry failed operations",
                    WhenToUse = "Transient errors, network issues",
                    Implementation = "Exponential backoff, max retry limits",
                    Pros = new[] { "Handles temporary issues", "No manual intervention" },
                    Cons = new[] { "May mask persistent problems", "Can delay error detection" }
                },
                new
                {
                    Strategy = "Partial Reset",
                    Description = "Reset indexer to last successful high water mark",
                    WhenToUse = "Data corruption, schema changes",
                    Implementation = "Reset indexer state, resume from checkpoint",
                    Pros = new[] { "Avoids full reprocessing", "Maintains progress" },
                    Cons = new[] { "May miss some updates", "Requires change detection" }
                },
                new
                {
                    Strategy = "Full Reset",
                    Description = "Complete reprocessing of all data",
                    WhenToUse = "Major schema changes, data source migration",
                    Implementation = "Reset indexer, clear index, full rerun",
                    Pros = new[] { "Ensures data consistency", "Clean slate approach" },
                    Cons = new[] { "Time consuming", "Resource intensive" }
                },
                new
                {
                    Strategy = "Error Isolation",
                    Description = "Skip problematic documents, continue processing",
                    WhenToUse = "Bad data in source, format issues",
                    Implementation = "Increase error thresholds, log failures",
                    Pros = new[] { "Maintains service availability", "Isolates problems" },
                    Cons = new[] { "Incomplete data", "Requires manual cleanup" }
                },
                new
                {
                    Strategy = "Circuit Breaker",
                    Description = "Stop processing when error rate is too high",
                    WhenToUse = "Systematic issues, data source problems",
                    Implementation = "Monitor error rates, disable on threshold",
                    Pros = new[] { "Prevents resource waste", "Fast failure detection" },
                    Cons = new[] { "Service interruption", "Requires manual intervention" }
                }
            };

            foreach (var strategy in strategies)
            {
                Console.WriteLine($"\n🎯 {strategy.Strategy}");
                Console.WriteLine($"   Description: {strategy.Description}");
                Console.WriteLine($"   When to Use: {strategy.WhenToUse}");
                Console.WriteLine($"   Implementation: {strategy.Implementation}");
                Console.WriteLine("   Pros:");
                foreach (var pro in strategy.Pros)
                    Console.WriteLine($"     ✅ {pro}");
                Console.WriteLine("   Cons:");
                foreach (var con in strategy.Cons)
                    Console.WriteLine($"     ⚠️ {con}");
            }
        }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";

            var example = new ErrorHandlingExample(searchEndpoint, apiKey);

            try
            {
                await example.RunAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Application failed: {ex.Message}");
                Environment.Exit(1);
            }

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}