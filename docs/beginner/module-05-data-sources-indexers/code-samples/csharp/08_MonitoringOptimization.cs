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
    /// Performance Monitoring & Optimization Example
    /// 
    /// This example demonstrates how to monitor indexer performance and implement
    /// optimization strategies for Azure AI Search indexers.
    /// </summary>
    public class MonitoringOptimizationExample
    {
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;

        public MonitoringOptimizationExample(string searchEndpoint, string apiKey)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));

            var credential = new AzureKeyCredential(_apiKey);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Performance Monitoring & Optimization Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Collect metrics for all indexers
                var allMetrics = await CollectPerformanceMetricsAsync();

                if (allMetrics.Any())
                {
                    // Analyze trends
                    AnalyzePerformanceTrends(allMetrics);

                    // Create dashboard
                    CreatePerformanceDashboard(allMetrics);

                    // Generate recommendations
                    GenerateOptimizationRecommendations(allMetrics);
                }

                // Show optimization strategies
                DemonstrateOptimizationStrategies();

                Console.WriteLine("\n✅ Performance monitoring example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Monitor indexer performance regularly to identify trends");
                Console.WriteLine("- Use metrics to make data-driven optimization decisions");
                Console.WriteLine("- Optimize batch sizes based on document characteristics");
                Console.WriteLine("- Implement proper change detection for incremental updates");
                Console.WriteLine("- Schedule indexers to avoid resource conflicts");
                Console.WriteLine("- Set appropriate error handling thresholds");
                Console.WriteLine("- Create dashboards for ongoing performance visibility");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }

        private async Task<List<dynamic>> CollectPerformanceMetricsAsync()
        {
            Console.WriteLine("\n📊 Collecting Performance Metrics");
            Console.WriteLine("=" + new string('=', 34));

            var allMetrics = new List<dynamic>();

            try
            {
                // Get all indexers
                var indexers = new List<SearchIndexer>();
                await foreach (var indexer in _indexerClient.GetIndexersAsync())
                {
                    indexers.Add(indexer);
                }

                if (!indexers.Any())
                {
                    Console.WriteLine("⚠️ No indexers found in the search service");
                    return allMetrics;
                }

                foreach (var indexer in indexers.Take(3)) // Limit to first 3 for demo
                {
                    var metrics = await CollectIndexerMetrics(indexer.Name);
                    if (metrics != null)
                    {
                        allMetrics.Add(metrics);
                    }
                }

                return allMetrics;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error collecting metrics: {ex.Message}");
                return allMetrics;
            }
        }

        private async Task<dynamic> CollectIndexerMetrics(string indexerName)
        {
            Console.WriteLine($"\n📊 Collecting Performance Metrics: {indexerName}");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                var status = await _indexerClient.GetIndexerStatusAsync(indexerName);

                if (status.Value.ExecutionHistory?.Count == 0)
                {
                    Console.WriteLine("   ⚠️ No execution history available");
                    return null;
                }

                var metrics = new
                {
                    IndexerName = indexerName,
                    CurrentStatus = status.Value.Status.ToString(),
                    Executions = new List<dynamic>(),
                    Summary = new Dictionary<string, object>()
                };

                var executions = new List<dynamic>();

                // Analyze execution history
                foreach (var execution in status.Value.ExecutionHistory ?? new List<IndexerExecutionResult>())
                {
                    var executionMetrics = new
                    {
                        StartTime = execution.StartTime,
                        EndTime = execution.EndTime,
                        Status = execution.Status.ToString(),
                        ItemsProcessed = execution.ItemCount,
                        ItemsFailed = execution.FailedItemCount,
                        ErrorCount = execution.Errors?.Count ?? 0,
                        WarningCount = execution.Warnings?.Count ?? 0,
                        DurationSeconds = execution.EndTime.HasValue && execution.StartTime.HasValue
                            ? (execution.EndTime.Value - execution.StartTime.Value).TotalSeconds
                            : 0,
                        ThroughputItemsPerSecond = 0.0
                    };

                    // Calculate throughput
                    if (executionMetrics.DurationSeconds > 0 && executionMetrics.ItemsProcessed > 0)
                    {
                        executionMetrics = new
                        {
                            executionMetrics.StartTime,
                            executionMetrics.EndTime,
                            executionMetrics.Status,
                            executionMetrics.ItemsProcessed,
                            executionMetrics.ItemsFailed,
                            executionMetrics.ErrorCount,
                            executionMetrics.WarningCount,
                            executionMetrics.DurationSeconds,
                            ThroughputItemsPerSecond = executionMetrics.ItemsProcessed / executionMetrics.DurationSeconds
                        };
                    }

                    executions.Add(executionMetrics);
                }

                // Calculate summary statistics
                if (executions.Any())
                {
                    var successfulExecutions = executions.Where(e => e.Status == "Success").ToList();

                    var summary = new Dictionary<string, object>
                    {
                        ["TotalExecutions"] = executions.Count,
                        ["SuccessfulExecutions"] = successfulExecutions.Count,
                        ["SuccessRate"] = successfulExecutions.Count / (double)executions.Count,
                        ["TotalItemsProcessed"] = executions.Sum(e => (int)e.ItemsProcessed),
                        ["TotalItemsFailed"] = executions.Sum(e => (int)e.ItemsFailed),
                        ["TotalErrors"] = executions.Sum(e => (int)e.ErrorCount),
                        ["TotalWarnings"] = executions.Sum(e => (int)e.WarningCount)
                    };

                    // Calculate average metrics for successful executions
                    if (successfulExecutions.Any())
                    {
                        var durations = successfulExecutions.Where(e => (double)e.DurationSeconds > 0).Select(e => (double)e.DurationSeconds).ToList();
                        var throughputs = successfulExecutions.Where(e => (double)e.ThroughputItemsPerSecond > 0).Select(e => (double)e.ThroughputItemsPerSecond).ToList();

                        if (durations.Any())
                        {
                            summary["AvgDurationSeconds"] = durations.Average();
                            summary["MinDurationSeconds"] = durations.Min();
                            summary["MaxDurationSeconds"] = durations.Max();
                        }

                        if (throughputs.Any())
                        {
                            summary["AvgThroughputItemsPerSecond"] = throughputs.Average();
                            summary["MinThroughputItemsPerSecond"] = throughputs.Min();
                            summary["MaxThroughputItemsPerSecond"] = throughputs.Max();
                        }
                    }

                    var finalMetrics = new
                    {
                        IndexerName = indexerName,
                        CurrentStatus = status.Value.Status.ToString(),
                        Executions = executions,
                        Summary = summary
                    };

                    // Display metrics
                    DisplayPerformanceMetrics(finalMetrics);

                    return finalMetrics;
                }

                return null;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"   ❌ Error collecting metrics: {ex.Message}");
                return null;
            }
        }

        private void DisplayPerformanceMetrics(dynamic metrics)
        {
            Console.WriteLine($"\n📈 Performance Summary for {metrics.IndexerName}:");

            var summary = (Dictionary<string, object>)metrics.Summary;

            // Basic statistics
            Console.WriteLine($"   Current Status: {metrics.CurrentStatus}");
            Console.WriteLine($"   Total Executions: {summary.GetValueOrDefault("TotalExecutions", 0)}");
            Console.WriteLine($"   Success Rate: {(double)summary.GetValueOrDefault("SuccessRate", 0.0):P1}");
            Console.WriteLine($"   Items Processed: {summary.GetValueOrDefault("TotalItemsProcessed", 0):N0}");
            Console.WriteLine($"   Items Failed: {summary.GetValueOrDefault("TotalItemsFailed", 0):N0}");
            Console.WriteLine($"   Total Errors: {summary.GetValueOrDefault("TotalErrors", 0)}");
            Console.WriteLine($"   Total Warnings: {summary.GetValueOrDefault("TotalWarnings", 0)}");

            // Performance metrics
            if (summary.ContainsKey("AvgDurationSeconds"))
            {
                Console.WriteLine($"\n⏱️ Execution Time Metrics:");
                Console.WriteLine($"   Average Duration: {(double)summary["AvgDurationSeconds"]:F1} seconds");
                Console.WriteLine($"   Min Duration: {(double)summary["MinDurationSeconds"]:F1} seconds");
                Console.WriteLine($"   Max Duration: {(double)summary["MaxDurationSeconds"]:F1} seconds");
            }

            if (summary.ContainsKey("AvgThroughputItemsPerSecond"))
            {
                Console.WriteLine($"\n🚀 Throughput Metrics:");
                Console.WriteLine($"   Average Throughput: {(double)summary["AvgThroughputItemsPerSecond"]:F2} items/sec");
                Console.WriteLine($"   Min Throughput: {(double)summary["MinThroughputItemsPerSecond"]:F2} items/sec");
                Console.WriteLine($"   Max Throughput: {(double)summary["MaxThroughputItemsPerSecond"]:F2} items/sec");
            }

            // Recent execution trend
            var executions = (List<dynamic>)metrics.Executions;
            if (executions.Count >= 3)
            {
                var recentExecutions = executions.Take(3).ToList();
                Console.WriteLine($"\n📊 Recent Execution Trend:");
                for (int i = 0; i < recentExecutions.Count; i++)
                {
                    var execution = recentExecutions[i];
                    var statusIcon = execution.Status == "Success" ? "✅" : "❌";
                    var duration = (double)execution.DurationSeconds;
                    var throughput = (double)execution.ThroughputItemsPerSecond;
                    Console.WriteLine($"   {i + 1}. {statusIcon} {execution.ItemsProcessed} items in {duration:F1}s ({throughput:F2} items/sec)");
                }
            }
        }

        private void AnalyzePerformanceTrends(List<dynamic> allMetrics)
        {
            Console.WriteLine($"\n📈 Performance Trend Analysis");
            Console.WriteLine("=" + new string('=', 29));

            // Compare indexers
            Console.WriteLine($"\n🔍 Indexer Comparison:");
            Console.WriteLine($"{"Indexer",-25} {"Success Rate",-12} {"Avg Duration",-12} {"Avg Throughput",-15}");
            Console.WriteLine(new string('-', 70));

            foreach (var metrics in allMetrics)
            {
                var name = ((string)metrics.IndexerName).Length > 24 ? ((string)metrics.IndexerName).Substring(0, 24) : (string)metrics.IndexerName;
                var summary = (Dictionary<string, object>)metrics.Summary;
                var successRate = (double)summary.GetValueOrDefault("SuccessRate", 0.0);
                var avgDuration = (double)summary.GetValueOrDefault("AvgDurationSeconds", 0.0);
                var avgThroughput = (double)summary.GetValueOrDefault("AvgThroughputItemsPerSecond", 0.0);

                Console.WriteLine($"{name,-25} {successRate,-11:P1} {avgDuration,-11:F1}s {avgThroughput,-14:F2}");
            }

            // Identify performance issues
            IdentifyPerformanceIssues(allMetrics);
        }

        private void IdentifyPerformanceIssues(List<dynamic> allMetrics)
        {
            Console.WriteLine($"\n🚨 Performance Issue Detection:");

            var issuesFound = false;

            foreach (var metrics in allMetrics)
            {
                var indexerName = (string)metrics.IndexerName;
                var summary = (Dictionary<string, object>)metrics.Summary;

                var issues = new List<string>();

                // Check success rate
                var successRate = (double)summary.GetValueOrDefault("SuccessRate", 1.0);
                if (successRate < 0.95) // Less than 95% success rate
                {
                    issues.Add($"Low success rate: {successRate:P1}");
                }

                // Check error rate
                var totalItems = (int)summary.GetValueOrDefault("TotalItemsProcessed", 0) + (int)summary.GetValueOrDefault("TotalItemsFailed", 0);
                if (totalItems > 0)
                {
                    var errorRate = (double)(int)summary.GetValueOrDefault("TotalItemsFailed", 0) / totalItems;
                    if (errorRate > 0.05) // More than 5% error rate
                    {
                        issues.Add($"High error rate: {errorRate:P1}");
                    }
                }

                // Check throughput consistency
                if (summary.ContainsKey("MinThroughputItemsPerSecond") && summary.ContainsKey("MaxThroughputItemsPerSecond"))
                {
                    var minThroughput = (double)summary["MinThroughputItemsPerSecond"];
                    var maxThroughput = (double)summary["MaxThroughputItemsPerSecond"];
                    if (maxThroughput > 0 && (maxThroughput - minThroughput) / maxThroughput > 0.5)
                    {
                        issues.Add("Inconsistent throughput (>50% variation)");
                    }
                }

                if (issues.Any())
                {
                    issuesFound = true;
                    Console.WriteLine($"\n   ⚠️ {indexerName}:");
                    foreach (var issue in issues)
                        Console.WriteLine($"      • {issue}");
                }
            }

            if (!issuesFound)
            {
                Console.WriteLine("   ✅ No significant performance issues detected");
            }
        }

        private void CreatePerformanceDashboard(List<dynamic> allMetrics)
        {
            Console.WriteLine($"\n📊 Performance Dashboard");
            Console.WriteLine("=" + new string('=', 24));

            if (!allMetrics.Any())
            {
                Console.WriteLine("   ⚠️ No metrics available for dashboard");
                return;
            }

            // Overall statistics
            var totalExecutions = allMetrics.Sum(m => (int)((Dictionary<string, object>)m.Summary).GetValueOrDefault("TotalExecutions", 0));
            var totalItemsProcessed = allMetrics.Sum(m => (int)((Dictionary<string, object>)m.Summary).GetValueOrDefault("TotalItemsProcessed", 0));
            var totalErrors = allMetrics.Sum(m => (int)((Dictionary<string, object>)m.Summary).GetValueOrDefault("TotalErrors", 0));

            Console.WriteLine($"📈 Overall Statistics:");
            Console.WriteLine($"   Total Indexers: {allMetrics.Count}");
            Console.WriteLine($"   Total Executions: {totalExecutions}");
            Console.WriteLine($"   Total Items Processed: {totalItemsProcessed:N0}");
            Console.WriteLine($"   Total Errors: {totalErrors}");

            if (totalItemsProcessed > 0)
            {
                var overallErrorRate = (double)totalErrors / totalItemsProcessed;
                Console.WriteLine($"   Overall Error Rate: {overallErrorRate:P2}");
            }

            // Top performers
            Console.WriteLine($"\n🏆 Top Performers:");

            // Sort by throughput
            var throughputSorted = allMetrics
                .Where(m => ((Dictionary<string, object>)m.Summary).ContainsKey("AvgThroughputItemsPerSecond"))
                .OrderByDescending(m => (double)((Dictionary<string, object>)m.Summary)["AvgThroughputItemsPerSecond"])
                .ToList();

            if (throughputSorted.Any())
            {
                Console.WriteLine("   Highest Throughput:");
                for (int i = 0; i < Math.Min(3, throughputSorted.Count); i++)
                {
                    var metrics = throughputSorted[i];
                    var throughput = (double)((Dictionary<string, object>)metrics.Summary)["AvgThroughputItemsPerSecond"];
                    Console.WriteLine($"     {i + 1}. {metrics.IndexerName}: {throughput:F2} items/sec");
                }
            }

            // Sort by success rate
            var successSorted = allMetrics
                .OrderByDescending(m => (double)((Dictionary<string, object>)m.Summary).GetValueOrDefault("SuccessRate", 0.0))
                .ToList();

            Console.WriteLine("   Highest Success Rate:");
            for (int i = 0; i < Math.Min(3, successSorted.Count); i++)
            {
                var metrics = successSorted[i];
                var successRate = (double)((Dictionary<string, object>)metrics.Summary).GetValueOrDefault("SuccessRate", 0.0);
                Console.WriteLine($"     {i + 1}. {metrics.IndexerName}: {successRate:P1}");
            }
        }

        private void GenerateOptimizationRecommendations(List<dynamic> allMetrics)
        {
            Console.WriteLine($"\n💡 Optimization Recommendations");
            Console.WriteLine("=" + new string('=', 34));

            var recommendations = new List<dynamic>();

            foreach (var metrics in allMetrics)
            {
                var indexerName = (string)metrics.IndexerName;
                var summary = (Dictionary<string, object>)metrics.Summary;

                // Low throughput recommendations
                var avgThroughput = (double)summary.GetValueOrDefault("AvgThroughputItemsPerSecond", 0.0);
                if (avgThroughput > 0 && avgThroughput < 1.0) // Less than 1 item per second
                {
                    recommendations.Add(new
                    {
                        Indexer = indexerName,
                        Issue = "Low throughput",
                        Recommendation = "Consider increasing batch size or optimizing field mappings"
                    });
                }

                // High error rate recommendations
                var totalItems = (int)summary.GetValueOrDefault("TotalItemsProcessed", 0) + (int)summary.GetValueOrDefault("TotalItemsFailed", 0);
                if (totalItems > 0)
                {
                    var errorRate = (double)(int)summary.GetValueOrDefault("TotalItemsFailed", 0) / totalItems;
                    if (errorRate > 0.05)
                    {
                        recommendations.Add(new
                        {
                            Indexer = indexerName,
                            Issue = "High error rate",
                            Recommendation = "Review data quality and adjust error handling parameters"
                        });
                    }
                }

                // Long execution time recommendations
                var avgDuration = (double)summary.GetValueOrDefault("AvgDurationSeconds", 0.0);
                if (avgDuration > 3600) // More than 1 hour
                {
                    recommendations.Add(new
                    {
                        Indexer = indexerName,
                        Issue = "Long execution time",
                        Recommendation = "Consider using change detection or reducing batch size"
                    });
                }
            }

            if (recommendations.Any())
            {
                foreach (var rec in recommendations)
                {
                    Console.WriteLine($"\n🎯 {rec.Indexer}:");
                    Console.WriteLine($"   Issue: {rec.Issue}");
                    Console.WriteLine($"   Recommendation: {rec.Recommendation}");
                }
            }
            else
            {
                Console.WriteLine("   ✅ No specific optimization recommendations at this time");
                Console.WriteLine("   Continue monitoring performance trends for future optimization opportunities");
            }
        }

        private void DemonstrateOptimizationStrategies()
        {
            Console.WriteLine("\n🚀 Optimization Strategies");
            Console.WriteLine("=" + new string('=', 24));

            var strategies = new[]
            {
                new
                {
                    Category = "Batch Size Optimization",
                    Description = "Adjust batch size based on data characteristics",
                    Techniques = new[]
                    {
                        "Start with default batch size (1000 for SQL, 100 for blobs)",
                        "Increase batch size for small documents",
                        "Decrease batch size for large documents or complex processing",
                        "Monitor memory usage and adjust accordingly",
                        "Test different batch sizes and measure throughput"
                    }
                },
                new
                {
                    Category = "Field Mapping Optimization",
                    Description = "Optimize field mappings for better performance",
                    Techniques = new[]
                    {
                        "Use only necessary field mappings",
                        "Avoid complex mapping functions when possible",
                        "Pre-process data at source when feasible",
                        "Use built-in functions instead of custom logic",
                        "Minimize the number of target fields"
                    }
                },
                new
                {
                    Category = "Change Detection Optimization",
                    Description = "Optimize change detection for incremental updates",
                    Techniques = new[]
                    {
                        "Use SQL Integrated Change Tracking when possible",
                        "Ensure change detection columns are indexed",
                        "Use appropriate high water mark columns",
                        "Monitor change detection effectiveness",
                        "Consider partition-based processing for large datasets"
                    }
                },
                new
                {
                    Category = "Resource Management",
                    Description = "Optimize resource usage and allocation",
                    Techniques = new[]
                    {
                        "Schedule indexers during off-peak hours",
                        "Stagger multiple indexer executions",
                        "Monitor search unit consumption",
                        "Use appropriate service tier for workload",
                        "Implement connection pooling for data sources"
                    }
                }
            };

            foreach (var strategy in strategies)
            {
                Console.WriteLine($"\n🎯 {strategy.Category}");
                Console.WriteLine($"   Description: {strategy.Description}");
                Console.WriteLine("   Techniques:");
                foreach (var technique in strategy.Techniques)
                    Console.WriteLine($"     • {technique}");
            }
        }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";

            var example = new MonitoringOptimizationExample(searchEndpoint, apiKey);

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