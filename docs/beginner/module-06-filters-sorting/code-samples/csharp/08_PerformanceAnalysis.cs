/*
 * Performance Analysis Example
 * 
 * This example demonstrates performance monitoring and optimization techniques
 * for Azure AI Search filter and sort operations.
 */

using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;
using System.Text.Json;

namespace AzureSearchFiltersExamples
{
    public class PerformanceAnalysisExample
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;
        private readonly List<PerformanceMetric> _performanceHistory;

        public PerformanceAnalysisExample()
        {
            ValidateConfiguration();
            
            _configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();

            var endpoint = new Uri(_configuration["SearchService:Endpoint"]);
            var apiKey = _configuration["SearchService:ApiKey"];
            var indexName = _configuration["SearchService:IndexName"];

            var credential = new AzureKeyCredential(apiKey);
            _searchClient = new SearchClient(endpoint, indexName, credential);
            _performanceHistory = new List<PerformanceMetric>();
        }

        private void ValidateConfiguration()
        {
            var config = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();

            var endpoint = config["SearchService:Endpoint"];
            var apiKey = config["SearchService:ApiKey"];
            var indexName = config["SearchService:IndexName"];

            if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(indexName))
            {
                throw new InvalidOperationException("Missing required configuration. Check your appsettings.json file.");
            }

            Console.WriteLine("✅ Configuration validated");
            Console.WriteLine($"📍 Search Endpoint: {endpoint}");
            Console.WriteLine($"📊 Index Name: {indexName}");
        }

        public async Task<PerformanceMetric> MeasureQueryPerformanceAsync(string queryType, string searchText = "*", 
            string filter = null, string orderBy = null, int size = 10)
        {
            var stopwatch = Stopwatch.StartNew();
            var startMemory = GC.GetTotalMemory(false);

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = size,
                    IncludeTotalCount = true
                };

                if (!string.IsNullOrEmpty(filter))
                    searchOptions.Filter = filter;

                if (!string.IsNullOrEmpty(orderBy))
                    searchOptions.OrderBy.Add(orderBy);

                searchOptions.Select.Add("id");
                searchOptions.Select.Add("name");
                searchOptions.Select.Add("category");
                searchOptions.Select.Add("price");
                searchOptions.Select.Add("rating");

                var results = await _searchClient.SearchAsync<SearchDocument>(searchText, searchOptions);
                var resultList = new List<SearchResult<SearchDocument>>();

                await foreach (var result in results.Value.GetResultsAsync())
                {
                    resultList.Add(result);
                }

                stopwatch.Stop();
                var endMemory = GC.GetTotalMemory(false);
                var totalCount = results.Value.TotalCount ?? resultList.Count;

                var metric = new PerformanceMetric
                {
                    Timestamp = DateTime.UtcNow,
                    QueryType = queryType,
                    SearchText = searchText,
                    FilterExpression = filter ?? "none",
                    OrderBy = orderBy ?? "none",
                    ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                    ResultCount = totalCount,
                    ReturnedCount = resultList.Count,
                    MemoryUsageBytes = endMemory - startMemory,
                    ComplexityScore = CalculateComplexityScore(filter),
                    Success = true
                };

                _performanceHistory.Add(metric);
                return metric;
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                var endMemory = GC.GetTotalMemory(false);

                var metric = new PerformanceMetric
                {
                    Timestamp = DateTime.UtcNow,
                    QueryType = queryType,
                    SearchText = searchText,
                    FilterExpression = filter ?? "none",
                    OrderBy = orderBy ?? "none",
                    ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                    MemoryUsageBytes = endMemory - startMemory,
                    ComplexityScore = CalculateComplexityScore(filter),
                    Success = false,
                    ErrorMessage = ex.Message
                };

                _performanceHistory.Add(metric);
                return metric;
            }
        }

        public async Task RunPerformanceBenchmarkAsync()
        {
            Console.WriteLine("\n🚀 Performance Benchmark Suite");
            Console.WriteLine("=".PadRight(40, '='));

            var testScenarios = new[]
            {
                new TestScenario
                {
                    Name = "Baseline Search",
                    SearchText = "*",
                    Filter = null,
                    OrderBy = null,
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Simple Filter",
                    SearchText = "*",
                    Filter = "rating ge 4.0",
                    OrderBy = null,
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Range Filter",
                    SearchText = "*",
                    Filter = "price ge 50 and price le 200",
                    OrderBy = null,
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Collection Filter",
                    SearchText = "*",
                    Filter = "tags/any(tag: tag eq 'premium')",
                    OrderBy = null,
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Complex Filter",
                    SearchText = "*",
                    Filter = "(tags/any(tag: tag eq 'premium') or rating gt 4.5) and price le 300",
                    OrderBy = null,
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Geographic Filter",
                    SearchText = "*",
                    Filter = "geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 10",
                    OrderBy = null,
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Sorted Results",
                    SearchText = "*",
                    Filter = null,
                    OrderBy = "rating desc",
                    Iterations = 5
                },
                new TestScenario
                {
                    Name = "Complex Sort",
                    SearchText = "*",
                    Filter = null,
                    OrderBy = "rating desc, price asc",
                    Iterations = 5
                }
            };

            var benchmarkResults = new List<BenchmarkResult>();

            foreach (var scenario in testScenarios)
            {
                Console.WriteLine($"\n📊 Testing: {scenario.Name}");
                Console.WriteLine($"   Filter: {scenario.Filter ?? "none"}");
                Console.WriteLine($"   Order: {scenario.OrderBy ?? "none"}");
                Console.WriteLine($"   Iterations: {scenario.Iterations}");

                var metrics = new List<PerformanceMetric>();

                for (int i = 0; i < scenario.Iterations; i++)
                {
                    var metric = await MeasureQueryPerformanceAsync(
                        scenario.Name, scenario.SearchText, scenario.Filter, scenario.OrderBy);
                    
                    if (metric.Success)
                        metrics.Add(metric);

                    // Small delay between iterations
                    await Task.Delay(100);
                }

                if (metrics.Any())
                {
                    var result = new BenchmarkResult
                    {
                        ScenarioName = scenario.Name,
                        SuccessfulRuns = metrics.Count,
                        TotalRuns = scenario.Iterations,
                        AvgExecutionTimeMs = metrics.Average(m => m.ExecutionTimeMs),
                        MinExecutionTimeMs = metrics.Min(m => m.ExecutionTimeMs),
                        MaxExecutionTimeMs = metrics.Max(m => m.ExecutionTimeMs),
                        StdDevExecutionTimeMs = CalculateStandardDeviation(metrics.Select(m => (double)m.ExecutionTimeMs)),
                        AvgResultCount = metrics.Average(m => m.ResultCount),
                        AvgMemoryUsageBytes = metrics.Average(m => m.MemoryUsageBytes),
                        ComplexityScore = metrics.First().ComplexityScore,
                        Filter = scenario.Filter
                    };

                    benchmarkResults.Add(result);

                    Console.WriteLine($"   ✅ Avg Time: {result.AvgExecutionTimeMs:F1}ms");
                    Console.WriteLine($"   📊 Results: {result.AvgResultCount:F0}");
                    Console.WriteLine($"   🎯 Complexity: {result.ComplexityScore}");
                }
                else
                {
                    Console.WriteLine($"   ❌ All iterations failed");
                }
            }

            // Generate benchmark report
            GenerateBenchmarkReport(benchmarkResults);
        }

        public void GenerateBenchmarkReport(List<BenchmarkResult> results)
        {
            Console.WriteLine("\n📊 BENCHMARK REPORT");
            Console.WriteLine("=".PadRight(50, '='));

            if (!results.Any())
            {
                Console.WriteLine("No successful benchmark results to report.");
                return;
            }

            // Summary statistics
            var avgTime = results.Average(r => r.AvgExecutionTimeMs);
            var fastestScenario = results.OrderBy(r => r.AvgExecutionTimeMs).First();
            var slowestScenario = results.OrderByDescending(r => r.AvgExecutionTimeMs).First();

            Console.WriteLine($"📈 Summary Statistics:");
            Console.WriteLine($"   Total Scenarios: {results.Count}");
            Console.WriteLine($"   Average Execution Time: {avgTime:F1}ms");
            Console.WriteLine($"   Fastest Scenario: {fastestScenario.ScenarioName} ({fastestScenario.AvgExecutionTimeMs:F1}ms)");
            Console.WriteLine($"   Slowest Scenario: {slowestScenario.ScenarioName} ({slowestScenario.AvgExecutionTimeMs:F1}ms)");

            // Detailed results
            Console.WriteLine($"\n🔍 Detailed Results:");
            Console.WriteLine($"{"Scenario",-25} {"Avg Time",-10} {"Results",-8} {"Complexity",-10} {"Performance",-12}");
            Console.WriteLine(new string('-', 70));

            foreach (var result in results.OrderBy(r => r.AvgExecutionTimeMs))
            {
                var performance = result.AvgExecutionTimeMs < 100 ? "Excellent" :
                                result.AvgExecutionTimeMs < 500 ? "Good" :
                                result.AvgExecutionTimeMs < 1000 ? "Fair" : "Needs work";

                Console.WriteLine($"{result.ScenarioName,-25} {result.AvgExecutionTimeMs,-10:F1}ms {result.AvgResultCount,-8:F0} {result.ComplexityScore,-10} {performance,-12}");
            }

            // Performance recommendations
            GenerateOptimizationRecommendations(results);
        }

        public void GenerateOptimizationRecommendations(List<BenchmarkResult> results)
        {
            Console.WriteLine($"\n💡 Optimization Recommendations:");
            Console.WriteLine(new string('-', 35));

            var recommendations = new List<string>();

            // Analyze slow queries
            var slowQueries = results.Where(r => r.AvgExecutionTimeMs > 1000).ToList();
            if (slowQueries.Any())
            {
                recommendations.Add($"🔴 HIGH PRIORITY: {slowQueries.Count} slow queries (>1s) need optimization");
                foreach (var slow in slowQueries)
                {
                    recommendations.Add($"   • {slow.ScenarioName}: {slow.AvgExecutionTimeMs:F1}ms");
                }
            }

            // Analyze complexity
            var complexQueries = results.Where(r => r.ComplexityScore > 15).ToList();
            if (complexQueries.Any())
            {
                recommendations.Add($"🟡 MEDIUM PRIORITY: {complexQueries.Count} high-complexity filters detected");
                recommendations.Add("   • Consider simplifying filter expressions");
                recommendations.Add("   • Use faceted navigation for complex OR conditions");
            }

            // Analyze geographic queries
            var geoQueries = results.Where(r => r.Filter?.Contains("geo.distance") == true).ToList();
            if (geoQueries.Any())
            {
                recommendations.Add($"🔵 INFO: {geoQueries.Count} geographic queries detected");
                recommendations.Add("   • Consider using smaller search radii");
                recommendations.Add("   • Ensure geographic fields are properly indexed");
            }

            // General recommendations
            recommendations.Add("🟢 GENERAL RECOMMENDATIONS:");
            recommendations.Add("   • Mark frequently filtered fields as 'filterable' in index schema");
            recommendations.Add("   • Use appropriate data types for optimal performance");
            recommendations.Add("   • Consider caching results for frequently used queries");
            recommendations.Add("   • Monitor query performance in production");

            foreach (var recommendation in recommendations)
            {
                Console.WriteLine(recommendation);
            }
        }

        public void AnalyzePerformanceTrends()
        {
            Console.WriteLine("\n📈 Performance Trend Analysis");
            Console.WriteLine("=".PadRight(40, '='));

            if (_performanceHistory.Count < 5)
            {
                Console.WriteLine("Insufficient data for trend analysis (need at least 5 measurements)");
                return;
            }

            // Group by query type
            var groupedMetrics = _performanceHistory
                .Where(m => m.Success)
                .GroupBy(m => m.QueryType)
                .ToList();

            foreach (var group in groupedMetrics)
            {
                var metrics = group.OrderBy(m => m.Timestamp).ToList();
                if (metrics.Count < 3) continue;

                var avgTime = metrics.Average(m => m.ExecutionTimeMs);
                var trend = CalculateTrend(metrics.Select(m => (double)m.ExecutionTimeMs).ToList());

                Console.WriteLine($"\n📊 {group.Key}:");
                Console.WriteLine($"   Measurements: {metrics.Count}");
                Console.WriteLine($"   Average Time: {avgTime:F1}ms");
                Console.WriteLine($"   Trend: {(trend > 0.1 ? "⬆️ Degrading" : trend < -0.1 ? "⬇️ Improving" : "➡️ Stable")}");
                Console.WriteLine($"   Latest: {metrics.Last().ExecutionTimeMs}ms");
            }
        }

        public void ExportPerformanceData(string filename = null)
        {
            filename ??= $"performance_data_{DateTime.Now:yyyyMMdd_HHmmss}.json";

            try
            {
                var exportData = new
                {
                    ExportTimestamp = DateTime.UtcNow,
                    TotalMeasurements = _performanceHistory.Count,
                    SuccessfulMeasurements = _performanceHistory.Count(m => m.Success),
                    DateRange = new
                    {
                        Start = _performanceHistory.Any() ? _performanceHistory.Min(m => m.Timestamp) : (DateTime?)null,
                        End = _performanceHistory.Any() ? _performanceHistory.Max(m => m.Timestamp) : (DateTime?)null
                    },
                    Metrics = _performanceHistory
                };

                var json = JsonSerializer.Serialize(exportData, new JsonSerializerOptions 
                { 
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });

                File.WriteAllText(filename, json);
                Console.WriteLine($"✅ Performance data exported to {filename}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Export failed: {ex.Message}");
            }
        }

        private int CalculateComplexityScore(string filter)
        {
            if (string.IsNullOrEmpty(filter))
                return 0;

            var score = 0;
            score += CountOccurrences(filter, " and ") * 1;
            score += CountOccurrences(filter, " or ") * 2;
            score += CountOccurrences(filter, "/any(") * 3;
            score += CountOccurrences(filter, "/all(") * 4;
            score += CountOccurrences(filter, "geo.distance") * 3;
            score += CountOccurrences(filter, "(") * 1;

            return score;
        }

        private int CountOccurrences(string text, string pattern)
        {
            return (text.Length - text.Replace(pattern, "").Length) / pattern.Length;
        }

        private double CalculateStandardDeviation(IEnumerable<double> values)
        {
            var valuesList = values.ToList();
            if (valuesList.Count <= 1) return 0;

            var average = valuesList.Average();
            var sumOfSquaresOfDifferences = valuesList.Select(val => (val - average) * (val - average)).Sum();
            return Math.Sqrt(sumOfSquaresOfDifferences / (valuesList.Count - 1));
        }

        private double CalculateTrend(List<double> values)
        {
            if (values.Count < 2) return 0;

            var n = values.Count;
            var sumX = Enumerable.Range(0, n).Sum();
            var sumY = values.Sum();
            var sumXY = values.Select((y, x) => x * y).Sum();
            var sumXX = Enumerable.Range(0, n).Select(x => x * x).Sum();

            return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Performance Analysis Example");
            Console.WriteLine("=".PadRight(50, '='));

            try
            {
                await RunPerformanceBenchmarkAsync();
                AnalyzePerformanceTrends();
                ExportPerformanceData();

                Console.WriteLine("\n✅ Performance analysis completed successfully!");
                Console.WriteLine($"\n📊 Total measurements collected: {_performanceHistory.Count}");
                Console.WriteLine($"✅ Successful queries: {_performanceHistory.Count(m => m.Success)}");
                Console.WriteLine($"❌ Failed queries: {_performanceHistory.Count(m => !m.Success)}");
                
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Monitor query performance regularly");
                Console.WriteLine("- Optimize slow and complex queries");
                Console.WriteLine("- Use appropriate indexing strategies");
                Console.WriteLine("- Consider caching for frequently used queries");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }
    }

    public class PerformanceMetric
    {
        public DateTime Timestamp { get; set; }
        public string QueryType { get; set; }
        public string SearchText { get; set; }
        public string FilterExpression { get; set; }
        public string OrderBy { get; set; }
        public long ExecutionTimeMs { get; set; }
        public int ResultCount { get; set; }
        public int ReturnedCount { get; set; }
        public long MemoryUsageBytes { get; set; }
        public int ComplexityScore { get; set; }
        public bool Success { get; set; }
        public string ErrorMessage { get; set; }
    }

    public class TestScenario
    {
        public string Name { get; set; }
        public string SearchText { get; set; }
        public string Filter { get; set; }
        public string OrderBy { get; set; }
        public int Iterations { get; set; }
    }

    public class BenchmarkResult
    {
        public string ScenarioName { get; set; }
        public int SuccessfulRuns { get; set; }
        public int TotalRuns { get; set; }
        public double AvgExecutionTimeMs { get; set; }
        public long MinExecutionTimeMs { get; set; }
        public long MaxExecutionTimeMs { get; set; }
        public double StdDevExecutionTimeMs { get; set; }
        public double AvgResultCount { get; set; }
        public double AvgMemoryUsageBytes { get; set; }
        public int ComplexityScore { get; set; }
        public string Filter { get; set; }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var example = new PerformanceAnalysisExample();
            try
            {
                await example.RunAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Application failed: {ex.Message}");
                Environment.Exit(1);
            }
        }
    }
}