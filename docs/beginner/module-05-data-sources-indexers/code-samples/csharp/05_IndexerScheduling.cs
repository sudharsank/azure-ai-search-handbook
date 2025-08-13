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
    /// Indexer Scheduling & Automation Example
    /// 
    /// This example demonstrates how to configure indexer schedules and automation patterns
    /// for Azure AI Search indexers.
    /// </summary>
    public class IndexerSchedulingExample
    {
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;

        public IndexerSchedulingExample(string searchEndpoint, string apiKey)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));

            var credential = new AzureKeyCredential(_apiKey);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Indexer Scheduling & Automation Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Demonstrate scheduling patterns
                var patterns = DemonstrateSchedulingPatterns();

                // Create scheduling examples
                var scheduleExamples = CreateScheduledIndexerExamples();

                // Show best practices
                DemonstrateSchedulingBestPractices();

                // Monitor existing indexers (if any)
                await MonitorScheduledIndexersAsync();

                // Show optimization strategies
                DemonstrateOptimizationStrategies();

                // Troubleshooting guide
                TroubleshootSchedulingIssues();

                Console.WriteLine("\n✅ Indexer scheduling example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Balance frequency with cost - more frequent updates cost more resources");
                Console.WriteLine("- Use change detection - minimize processing overhead with incremental updates");
                Console.WriteLine("- Schedule during off-peak hours - optimize performance and resource usage");
                Console.WriteLine("- Monitor execution patterns - track performance trends and adjust accordingly");
                Console.WriteLine("- Implement proper error handling - ensure reliable automated operations");
                Console.WriteLine("- Consider business requirements - align technical scheduling with business needs");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }

        private List<dynamic> DemonstrateSchedulingPatterns()
        {
            Console.WriteLine("\n📅 Common Indexer Scheduling Patterns");
            Console.WriteLine("=" + new string('=', 39));

            var patterns = new[]
            {
                new
                {
                    Name = "High-Frequency Updates",
                    Interval = TimeSpan.FromMinutes(15),
                    UseCase = "Real-time data feeds, news, social media",
                    Cost = "High",
                    DataFreshness = "Very High",
                    ExampleStart = DateTime.UtcNow.Date.AddHours(DateTime.UtcNow.Hour)
                },
                new
                {
                    Name = "Hourly Updates",
                    Interval = TimeSpan.FromHours(1),
                    UseCase = "E-commerce catalogs, inventory systems",
                    Cost = "Medium-High",
                    DataFreshness = "High",
                    ExampleStart = DateTime.UtcNow.Date.AddHours(DateTime.UtcNow.Hour)
                },
                new
                {
                    Name = "Daily Updates",
                    Interval = TimeSpan.FromDays(1),
                    UseCase = "Document repositories, CRM data",
                    Cost = "Medium",
                    DataFreshness = "Medium",
                    ExampleStart = DateTime.UtcNow.Date.AddHours(2)
                },
                new
                {
                    Name = "Weekly Updates",
                    Interval = TimeSpan.FromDays(7),
                    UseCase = "Archive data, reference materials",
                    Cost = "Low",
                    DataFreshness = "Low",
                    ExampleStart = DateTime.UtcNow.Date.AddHours(1)
                }
            };

            foreach (var pattern in patterns)
            {
                Console.WriteLine($"\n🔄 {pattern.Name}");
                Console.WriteLine($"   Interval: {pattern.Interval}");
                Console.WriteLine($"   Use Case: {pattern.UseCase}");
                Console.WriteLine($"   Cost Impact: {pattern.Cost}");
                Console.WriteLine($"   Data Freshness: {pattern.DataFreshness}");
                Console.WriteLine($"   Example Start Time: {pattern.ExampleStart}");

                // Calculate next few runs
                var nextRuns = new List<DateTime>();
                var currentTime = pattern.ExampleStart;
                for (int i = 0; i < 3; i++)
                {
                    nextRuns.Add(currentTime.Add(TimeSpan.FromTicks(pattern.Interval.Ticks * i)));
                }

                Console.WriteLine($"   Next 3 runs: {string.Join(", ", nextRuns.Select(t => t.ToString("HH:mm")))}");
            }

            return patterns.Cast<dynamic>().ToList();
        }

        private Dictionary<string, IndexingSchedule> CreateScheduledIndexerExamples()
        {
            Console.WriteLine("\n⚙️ Creating Scheduled Indexer Examples");
            Console.WriteLine("=" + new string('=', 39));

            var examples = new Dictionary<string, IndexingSchedule>();

            // Example 1: E-commerce Product Catalog
            Console.WriteLine("\n🛒 E-commerce Product Catalog Indexer:");
            var ecommerceSchedule = new IndexingSchedule(
                interval: TimeSpan.FromHours(2),
                startTime: DateTimeOffset.UtcNow.Date.AddHours(8));

            Console.WriteLine($"   Interval: {ecommerceSchedule.Interval}");
            Console.WriteLine($"   Start Time: {ecommerceSchedule.StartTime} (8 AM)");
            Console.WriteLine("   Rationale: Frequent updates for inventory and pricing changes");
            Console.WriteLine("   Business Impact: High - affects customer experience and sales");

            examples.Add("E-commerce", ecommerceSchedule);

            // Example 2: Document Management System
            Console.WriteLine("\n📄 Document Management System Indexer:");
            var documentSchedule = new IndexingSchedule(
                interval: TimeSpan.FromDays(1),
                startTime: DateTimeOffset.UtcNow.Date.AddHours(2).AddMinutes(30));

            Console.WriteLine($"   Interval: {documentSchedule.Interval}");
            Console.WriteLine($"   Start Time: {documentSchedule.StartTime} (2:30 AM)");
            Console.WriteLine("   Rationale: Documents change less frequently, off-hours processing");
            Console.WriteLine("   Business Impact: Medium - affects search accuracy but not critical");

            examples.Add("Documents", documentSchedule);

            // Example 3: News and Media Content
            Console.WriteLine("\n📰 News and Media Content Indexer:");
            var newsSchedule = new IndexingSchedule(
                interval: TimeSpan.FromMinutes(15),
                startTime: DateTimeOffset.UtcNow.Date.AddHours(DateTime.UtcNow.Hour));

            Console.WriteLine($"   Interval: {newsSchedule.Interval}");
            Console.WriteLine($"   Start Time: {newsSchedule.StartTime}");
            Console.WriteLine("   Rationale: Breaking news requires immediate indexing");
            Console.WriteLine("   Business Impact: Critical - affects content relevance and user engagement");

            examples.Add("News", newsSchedule);

            // Example 4: Reference Data (Low Priority)
            Console.WriteLine("\n📚 Reference Data Indexer:");
            var referenceSchedule = new IndexingSchedule(
                interval: TimeSpan.FromDays(7),
                startTime: DateTimeOffset.UtcNow.Date.AddHours(1));

            Console.WriteLine($"   Interval: {referenceSchedule.Interval}");
            Console.WriteLine($"   Start Time: {referenceSchedule.StartTime} (1 AM Sunday)");
            Console.WriteLine("   Rationale: Reference data changes infrequently");
            Console.WriteLine("   Business Impact: Low - static content with minimal updates");

            examples.Add("Reference", referenceSchedule);

            return examples;
        }

        private void DemonstrateSchedulingBestPractices()
        {
            Console.WriteLine("\n💡 Indexer Scheduling Best Practices");
            Console.WriteLine("=" + new string('=', 34));

            var bestPractices = new[]
            {
                new
                {
                    Category = "Timing Optimization",
                    Practices = new[]
                    {
                        "Schedule during off-peak hours (2-4 AM)",
                        "Avoid overlapping with backup windows",
                        "Consider time zones for global applications",
                        "Stagger multiple indexers to avoid resource conflicts"
                    }
                },
                new
                {
                    Category = "Performance Considerations",
                    Practices = new[]
                    {
                        "Use change detection to minimize processing",
                        "Adjust batch sizes based on data volume",
                        "Monitor execution duration trends",
                        "Set appropriate timeout values"
                    }
                },
                new
                {
                    Category = "Cost Management",
                    Practices = new[]
                    {
                        "Balance frequency with business requirements",
                        "Use incremental indexing when possible",
                        "Monitor search unit consumption",
                        "Consider data source throttling limits"
                    }
                },
                new
                {
                    Category = "Reliability & Monitoring",
                    Practices = new[]
                    {
                        "Set up alerting for failed executions",
                        "Monitor execution history regularly",
                        "Implement retry logic for transient failures",
                        "Document schedule rationale and dependencies"
                    }
                }
            };

            foreach (var category in bestPractices)
            {
                Console.WriteLine($"\n🎯 {category.Category}");
                foreach (var practice in category.Practices)
                    Console.WriteLine($"   • {practice}");
            }

            // Create a scheduling decision matrix
            Console.WriteLine($"\n📊 Scheduling Decision Matrix:");
            Console.WriteLine("   Data Volatility | Business Criticality | Data Volume | Recommended Frequency");
            Console.WriteLine("   Low             | Low                  | Small       | Weekly");
            Console.WriteLine("   Medium          | Medium               | Medium      | Daily");
            Console.WriteLine("   High            | High                 | Large       | Hourly");
            Console.WriteLine("   Very High       | Critical             | Very Large  | 15-30 min");
        }

        private async Task MonitorScheduledIndexersAsync()
        {
            Console.WriteLine("\n📊 Monitoring Scheduled Indexers");
            Console.WriteLine("=" + new string('=', 29));

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
                    return;
                }

                var monitoringData = new List<dynamic>();

                foreach (var indexer in indexers)
                {
                    Console.WriteLine($"\n🔍 Analyzing indexer: {indexer.Name}");

                    try
                    {
                        var status = await _indexerClient.GetIndexerStatusAsync(indexer.Name);

                        // Collect basic info
                        var indexerInfo = new
                        {
                            Name = indexer.Name,
                            Status = status.Value.Status.ToString(),
                            HasSchedule = indexer.Schedule != null,
                            ScheduleInterval = indexer.Schedule?.Interval.ToString() ?? "Manual",
                            LastResultStatus = status.Value.LastResult?.Status.ToString() ?? "None",
                            ExecutionCount = status.Value.ExecutionHistory?.Count ?? 0
                        };

                        var itemsProcessed = 0;
                        var itemsFailed = 0;
                        var executionDuration = 0.0;

                        if (status.Value.LastResult != null)
                        {
                            var result = status.Value.LastResult;
                            itemsProcessed = result.ItemCount;
                            itemsFailed = result.FailedItemCount;

                            if (result.EndTime.HasValue && result.StartTime.HasValue)
                            {
                                executionDuration = (result.EndTime.Value - result.StartTime.Value).TotalSeconds;
                            }
                        }

                        // Display indexer details
                        Console.WriteLine($"   Status: {indexerInfo.Status}");
                        Console.WriteLine($"   Schedule: {indexerInfo.ScheduleInterval}");
                        Console.WriteLine($"   Last Result: {indexerInfo.LastResultStatus}");
                        Console.WriteLine($"   Items Processed: {itemsProcessed}");
                        Console.WriteLine($"   Execution Duration: {executionDuration:F1}s");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"   ❌ Error getting status: {ex.Message}");
                        continue;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error monitoring indexers: {ex.Message}");
            }
        }

        private void DemonstrateOptimizationStrategies()
        {
            Console.WriteLine("\n🚀 Advanced Scheduling Optimization Strategies");
            Console.WriteLine("=" + new string('=', 44));

            var strategies = new[]
            {
                new
                {
                    Name = "Adaptive Scheduling",
                    Description = "Adjust frequency based on data change patterns",
                    Implementation = new[]
                    {
                        "Monitor change detection results",
                        "Reduce frequency when few changes detected",
                        "Increase frequency during high-activity periods",
                        "Use Azure Logic Apps for dynamic scheduling"
                    },
                    Benefits = "Optimal balance of freshness and cost"
                },
                new
                {
                    Name = "Tiered Scheduling",
                    Description = "Different schedules for different data priorities",
                    Implementation = new[]
                    {
                        "Critical data: High frequency (15-30 min)",
                        "Important data: Medium frequency (hourly)",
                        "Archive data: Low frequency (daily/weekly)",
                        "Use separate indexers for each tier"
                    },
                    Benefits = "Resource optimization and cost control"
                },
                new
                {
                    Name = "Event-Driven Indexing",
                    Description = "Trigger indexing based on data source events",
                    Implementation = new[]
                    {
                        "Use Azure Event Grid for blob storage changes",
                        "Implement webhook triggers for database changes",
                        "Combine with scheduled baseline runs",
                        "Use Azure Functions for event processing"
                    },
                    Benefits = "Near real-time updates with minimal overhead"
                },
                new
                {
                    Name = "Load Balancing",
                    Description = "Distribute indexer execution across time",
                    Implementation = new[]
                    {
                        "Stagger start times for multiple indexers",
                        "Use different intervals to avoid conflicts",
                        "Monitor search unit utilization",
                        "Implement queue-based execution"
                    },
                    Benefits = "Improved performance and resource utilization"
                }
            };

            foreach (var strategy in strategies)
            {
                Console.WriteLine($"\n🎯 {strategy.Name}");
                Console.WriteLine($"   Description: {strategy.Description}");
                Console.WriteLine($"   Benefits: {strategy.Benefits}");
                Console.WriteLine("   Implementation:");
                foreach (var step in strategy.Implementation)
                    Console.WriteLine($"     • {step}");
            }
        }

        private void TroubleshootSchedulingIssues()
        {
            Console.WriteLine("\n🔧 Common Scheduling Issues and Solutions");
            Console.WriteLine("=" + new string('=', 39));

            var issues = new[]
            {
                new
                {
                    Issue = "Indexer Not Running on Schedule",
                    Symptoms = new[]
                    {
                        "No recent execution history",
                        "Status shows as idle",
                        "Data not updating as expected"
                    },
                    Causes = new[]
                    {
                        "Schedule not properly configured",
                        "Indexer disabled or in error state",
                        "Service quota limits reached",
                        "Data source connection issues"
                    },
                    Solutions = new[]
                    {
                        "Verify schedule configuration",
                        "Check indexer status and enable if needed",
                        "Review service limits and usage",
                        "Test data source connectivity"
                    }
                },
                new
                {
                    Issue = "Execution Timeouts",
                    Symptoms = new[]
                    {
                        "Indexer stops mid-execution",
                        "Partial data processing",
                        "Timeout errors in execution history"
                    },
                    Causes = new[]
                    {
                        "Large batch sizes",
                        "Complex data transformations",
                        "Slow data source responses",
                        "Network connectivity issues"
                    },
                    Solutions = new[]
                    {
                        "Reduce batch size",
                        "Optimize field mappings",
                        "Implement data source caching",
                        "Increase timeout settings"
                    }
                },
                new
                {
                    Issue = "Resource Conflicts",
                    Symptoms = new[]
                    {
                        "Multiple indexers failing simultaneously",
                        "Performance degradation",
                        "Search unit exhaustion"
                    },
                    Causes = new[]
                    {
                        "Overlapping execution schedules",
                        "Insufficient search units",
                        "Concurrent indexer limits exceeded"
                    },
                    Solutions = new[]
                    {
                        "Stagger indexer schedules",
                        "Upgrade service tier",
                        "Implement execution queuing"
                    }
                }
            };

            foreach (var issue in issues)
            {
                Console.WriteLine($"\n❌ {issue.Issue}");
                Console.WriteLine("   Symptoms:");
                foreach (var symptom in issue.Symptoms)
                    Console.WriteLine($"     • {symptom}");
                Console.WriteLine("   Common Causes:");
                foreach (var cause in issue.Causes)
                    Console.WriteLine($"     • {cause}");
                Console.WriteLine("   Solutions:");
                foreach (var solution in issue.Solutions)
                    Console.WriteLine($"     ✅ {solution}");
            }

            // Diagnostic checklist
            Console.WriteLine($"\n📋 Scheduling Diagnostic Checklist:");
            var checklist = new[]
            {
                "✓ Verify indexer schedule configuration",
                "✓ Check indexer status and last execution",
                "✓ Review execution history for patterns",
                "✓ Monitor search unit consumption",
                "✓ Test data source connectivity",
                "✓ Validate change detection settings",
                "✓ Check for service limit violations",
                "✓ Review error logs and messages",
                "✓ Verify field mapping configurations",
                "✓ Test manual indexer execution"
            };

            foreach (var item in checklist)
                Console.WriteLine($"   {item}");
        }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";

            var example = new IndexerSchedulingExample(searchEndpoint, apiKey);

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