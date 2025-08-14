/*
 * Run All Examples
 * 
 * This program runs all the C# examples in sequence, providing a comprehensive
 * demonstration of Azure AI Search filtering and sorting capabilities.
 */

using System.Diagnostics;
using System.Reflection;

namespace AzureSearchFiltersExamples
{
    public class RunAllExamples
    {
        private static readonly List<ExampleInfo> Examples = new()
        {
            new ExampleInfo
            {
                Name = "Basic Filters",
                Description = "Equality, comparison, and boolean logic filters",
                ClassName = "BasicFiltersExample",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "Range Filters",
                Description = "Numeric and date range filtering",
                ClassName = "RangeFiltersExample",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "String Filters",
                Description = "Text matching and pattern filtering",
                ClassName = "StringFilters",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "Date Filters",
                Description = "Date range and temporal filtering",
                ClassName = "DateFilters",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "Geographic Filters",
                Description = "Distance-based and spatial filtering",
                ClassName = "GeographicFiltersExample",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "Sorting Operations",
                Description = "Single and multi-field sorting",
                ClassName = "SortingOperations",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "Complex Filters",
                Description = "Collection filtering and nested conditions",
                ClassName = "ComplexFiltersExample",
                RequiresSearch = true,
                Available = true
            },
            new ExampleInfo
            {
                Name = "Performance Analysis",
                Description = "Query performance monitoring and optimization",
                ClassName = "PerformanceAnalysisExample",
                RequiresSearch = true,
                Available = true
            }
        };

        public static async Task Main(string[] args)
        {
            var demoMode = args.Contains("--demo-mode");
            var skipSearch = args.Contains("--skip-search");
            var help = args.Contains("--help") || args.Contains("-h");

            if (help)
            {
                ShowHelp();
                return;
            }

            Console.WriteLine("🎯 Azure AI Search - Filters & Sorting Examples (C#)");
            Console.WriteLine("=".PadRight(60, '='));

            if (demoMode)
            {
                Console.WriteLine("🎭 DEMO MODE: Running without actual API calls");
            }
            else if (!CheckConfiguration())
            {
                Console.WriteLine("\n💡 Use --demo-mode to run without API calls");
                Console.WriteLine("💡 Use --skip-search to skip search-dependent examples");
                return;
            }

            var availableExamples = Examples.Where(e => e.Available).ToList();
            if (skipSearch)
            {
                availableExamples = availableExamples.Where(e => !e.RequiresSearch).ToList();
            }

            Console.WriteLine($"\n📊 Running {availableExamples.Count} examples...");
            if (demoMode)
                Console.WriteLine("🎭 Demo mode enabled - no API calls will be made");
            if (skipSearch)
                Console.WriteLine("⏭️  Skipping search-dependent examples");

            var results = new List<ExampleResult>();

            for (int i = 0; i < availableExamples.Count; i++)
            {
                var example = availableExamples[i];
                Console.WriteLine($"\n[{i + 1}/{availableExamples.Count}] {example.Name}");
                Console.WriteLine($"📝 {example.Description}");

                var result = await RunExampleAsync(example, demoMode);
                results.Add(result);

                // Small delay between examples
                await Task.Delay(1000);
            }

            // Generate summary
            ShowSummary(results);
        }

        private static void ShowHelp()
        {
            Console.WriteLine("Azure AI Search Filters & Sorting Examples");
            Console.WriteLine();
            Console.WriteLine("Usage: dotnet run [options]");
            Console.WriteLine();
            Console.WriteLine("Options:");
            Console.WriteLine("  --demo-mode    Run in demonstration mode (no API calls)");
            Console.WriteLine("  --skip-search  Skip examples that require search operations");
            Console.WriteLine("  --help, -h     Show this help message");
            Console.WriteLine();
            Console.WriteLine("Examples:");
            Console.WriteLine("  dotnet run");
            Console.WriteLine("  dotnet run --demo-mode");
            Console.WriteLine("  dotnet run --skip-search");
        }

        private static bool CheckConfiguration()
        {
            Console.WriteLine("🔍 Checking Configuration...");

            try
            {
                var config = new Microsoft.Extensions.Configuration.ConfigurationBuilder()
                    .AddJsonFile("appsettings.json")
                    .Build();

                var endpoint = config["SearchService:Endpoint"];
                var apiKey = config["SearchService:ApiKey"];
                var indexName = config["SearchService:IndexName"];

                if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(indexName))
                {
                    Console.WriteLine("❌ Missing required configuration in appsettings.json");
                    Console.WriteLine("Please configure SearchService:Endpoint, SearchService:ApiKey, and SearchService:IndexName");
                    return false;
                }

                Console.WriteLine("✅ Configuration looks good");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                return false;
            }
        }

        private static async Task<ExampleResult> RunExampleAsync(ExampleInfo example, bool demoMode)
        {
            var stopwatch = Stopwatch.StartNew();

            try
            {
                if (demoMode)
                {
                    // In demo mode, just validate the class exists
                    var type = Type.GetType($"AzureSearchFiltersExamples.{example.ClassName}");
                    if (type == null)
                    {
                        return new ExampleResult
                        {
                            ExampleName = example.Name,
                            Success = false,
                            ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                            ErrorMessage = "Example class not found",
                            Mode = "demo"
                        };
                    }

                    Console.WriteLine("✅ Example class found and validated");
                    await Task.Delay(500); // Simulate some work

                    return new ExampleResult
                    {
                        ExampleName = example.Name,
                        Success = true,
                        ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                        Mode = "demo"
                    };
                }
                else
                {
                    // Run the actual example
                    var type = Type.GetType($"AzureSearchFiltersExamples.{example.ClassName}");
                    if (type == null)
                    {
                        return new ExampleResult
                        {
                            ExampleName = example.Name,
                            Success = false,
                            ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                            ErrorMessage = "Example class not found",
                            Mode = "live"
                        };
                    }

                    var instance = Activator.CreateInstance(type);
                    var runMethod = type.GetMethod("RunAsync");

                    if (runMethod == null)
                    {
                        return new ExampleResult
                        {
                            ExampleName = example.Name,
                            Success = false,
                            ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                            ErrorMessage = "RunAsync method not found",
                            Mode = "live"
                        };
                    }

                    var task = (Task)runMethod.Invoke(instance, null);
                    await task;

                    return new ExampleResult
                    {
                        ExampleName = example.Name,
                        Success = true,
                        ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                        Mode = "live"
                    };
                }
            }
            catch (Exception ex)
            {
                return new ExampleResult
                {
                    ExampleName = example.Name,
                    Success = false,
                    ExecutionTimeMs = stopwatch.ElapsedMilliseconds,
                    ErrorMessage = ex.Message,
                    Mode = demoMode ? "demo" : "live"
                };
            }
            finally
            {
                stopwatch.Stop();
            }
        }

        private static void ShowSummary(List<ExampleResult> results)
        {
            Console.WriteLine($"\n{"=".PadRight(60, '=')}");
            Console.WriteLine("📊 EXECUTION SUMMARY");
            Console.WriteLine($"{"=".PadRight(60, '=')}");

            var successful = results.Where(r => r.Success).ToList();
            var failed = results.Where(r => !r.Success).ToList();

            Console.WriteLine($"✅ Successful: {successful.Count}");
            Console.WriteLine($"❌ Failed: {failed.Count}");
            Console.WriteLine($"📊 Total: {results.Count}");

            if (successful.Any())
            {
                Console.WriteLine($"\n✅ Successful Examples:");
                foreach (var result in successful)
                {
                    var modeIndicator = result.Mode == "demo" ? "🎭" : "🔍";
                    Console.WriteLine($"   {modeIndicator} {result.ExampleName} ({result.ExecutionTimeMs}ms)");
                }
            }

            if (failed.Any())
            {
                Console.WriteLine($"\n❌ Failed Examples:");
                foreach (var result in failed)
                {
                    Console.WriteLine($"   • {result.ExampleName}: {result.ErrorMessage}");
                }
            }

            // Performance summary
            if (successful.Any())
            {
                var avgTime = successful.Average(r => r.ExecutionTimeMs);
                var totalTime = successful.Sum(r => r.ExecutionTimeMs);
                Console.WriteLine($"\n⚡ Performance Summary:");
                Console.WriteLine($"   Average execution time: {avgTime:F1}ms");
                Console.WriteLine($"   Total execution time: {totalTime}ms");
            }

            // Next steps
            Console.WriteLine($"\n💡 Next Steps:");
            if (failed.Any())
            {
                Console.WriteLine("   • Check your appsettings.json configuration for failed examples");
                Console.WriteLine("   • Ensure your Azure AI Search service is accessible");
                Console.WriteLine("   • Verify your index schema supports the required fields");
            }

            Console.WriteLine("   • Explore individual examples for detailed learning");
            Console.WriteLine("   • Modify examples to work with your specific data");
            Console.WriteLine("   • Check the notebooks for interactive learning experiences");

            Console.WriteLine($"\n🎉 Examples execution completed!");
        }
    }

    public class ExampleInfo
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string ClassName { get; set; }
        public bool RequiresSearch { get; set; }
        public bool Available { get; set; }
    }

    public class ExampleResult
    {
        public string ExampleName { get; set; }
        public bool Success { get; set; }
        public long ExecutionTimeMs { get; set; }
        public string ErrorMessage { get; set; }
        public string Mode { get; set; }
    }
}