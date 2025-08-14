using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using System.Text;

namespace AzureSearchFiltersExamples
{
    /// <summary>
    /// Demonstrates sorting operations using Azure AI Search.
    /// 
    /// Key Features:
    /// - Single field sorting
    /// - Multi-field sorting
    /// - Custom sort orders
    /// - Performance optimization
    /// - Geographic distance sorting
    /// - Score-based sorting combinations
    /// </summary>
    public class SortingOperations
    {
        private readonly SearchClient _searchClient;
        private readonly ILogger<SortingOperations> _logger;
        private readonly List<SortExample> _examples;

        public SortingOperations(SearchClient searchClient, ILogger<SortingOperations> logger)
        {
            _searchClient = searchClient;
            _logger = logger;
            _examples = LoadSortExamples();
        }

        /// <summary>
        /// Represents a sorting example with metadata.
        /// </summary>
        public class SortExample
        {
            public string Name { get; set; } = string.Empty;
            public List<string> OrderBy { get; set; } = new();
            public string Description { get; set; } = string.Empty;
            public string UseCase { get; set; } = string.Empty;
            public SortComplexity Complexity { get; set; }
            public int PerformanceScore { get; set; }
        }

        /// <summary>
        /// Sort complexity levels.
        /// </summary>
        public enum SortComplexity
        {
            Simple,
            Moderate,
            Complex,
            Advanced
        }

        /// <summary>
        /// Represents search results with sorting metadata.
        /// </summary>
        public class SortingResult
        {
            public IList<SearchResult<SearchDocument>> Documents { get; set; } = new List<SearchResult<SearchDocument>>();
            public long? TotalCount { get; set; }
            public TimeSpan ExecutionTime { get; set; }
            public List<string> OrderBy { get; set; } = new();
            public Dictionary<string, object> Metadata { get; set; } = new();
        }

        /// <summary>
        /// Sort configuration for building complex sort expressions.
        /// </summary>
        public class SortConfiguration
        {
            public string FieldName { get; set; } = string.Empty;
            public SortDirection Direction { get; set; } = SortDirection.Ascending;
            public SortMissingValue MissingValue { get; set; } = SortMissingValue.Last;
            public string? GeographyPoint { get; set; }
        }

        /// <summary>
        /// Sort direction enumeration.
        /// </summary>
        public enum SortDirection
        {
            Ascending,
            Descending
        }

        /// <summary>
        /// How to handle missing values in sorting.
        /// </summary>
        public enum SortMissingValue
        {
            First,
            Last
        }

        /// <summary>
        /// Build a single field sort expression.
        /// </summary>
        public List<string> BuildSingleFieldSort(string fieldName, SortDirection direction = SortDirection.Ascending)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            var directionStr = direction == SortDirection.Ascending ? "asc" : "desc";
            return new List<string> { $"{fieldName} {directionStr}" };
        }

        /// <summary>
        /// Build a multi-field sort expression.
        /// </summary>
        public List<string> BuildMultiFieldSort(List<SortConfiguration> configurations)
        {
            if (configurations == null || !configurations.Any())
                throw new ArgumentException("At least one sort configuration must be provided");

            var sortExpressions = new List<string>();

            foreach (var config in configurations)
            {
                if (string.IsNullOrEmpty(config.FieldName))
                    continue;

                var directionStr = config.Direction == SortDirection.Ascending ? "asc" : "desc";
                sortExpressions.Add($"{config.FieldName} {directionStr}");
            }

            return sortExpressions;
        }

        /// <summary>
        /// Build a geographic distance sort expression.
        /// </summary>
        public List<string> BuildGeographicSort(string fieldName, double latitude, double longitude, 
            SortDirection direction = SortDirection.Ascending)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            var directionStr = direction == SortDirection.Ascending ? "asc" : "desc";
            var point = $"geography'POINT({longitude} {latitude})'";
            
            return new List<string> { $"geo.distance({fieldName}, {point}) {directionStr}" };
        }

        /// <summary>
        /// Build a score-based sort with secondary sorting.
        /// </summary>
        public List<string> BuildScoreBasedSort(List<SortConfiguration> secondarySort)
        {
            var sortExpressions = new List<string> { "search.score() desc" };

            if (secondarySort != null && secondarySort.Any())
            {
                var secondarySorts = BuildMultiFieldSort(secondarySort);
                sortExpressions.AddRange(secondarySorts);
            }

            return sortExpressions;
        }

        /// <summary>
        /// Build a custom sort expression with advanced options.
        /// </summary>
        public List<string> BuildCustomSort(string expression, SortDirection direction = SortDirection.Ascending)
        {
            if (string.IsNullOrEmpty(expression))
                throw new ArgumentException("Sort expression cannot be null or empty");

            var directionStr = direction == SortDirection.Ascending ? "asc" : "desc";
            return new List<string> { $"{expression} {directionStr}" };
        }

        /// <summary>
        /// Execute a search with sorting and performance monitoring.
        /// </summary>
        public async Task<SortingResult> ExecuteSortedSearchAsync(List<string> orderBy, 
            string searchText = "*", string? filter = null, int top = 10)
        {
            var stopwatch = Stopwatch.StartNew();

            try
            {
                _logger.LogInformation("Executing sorted search with order: {OrderBy}", string.Join(", ", orderBy));

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                // Add sorting
                foreach (var sort in orderBy)
                {
                    searchOptions.OrderBy.Add(sort);
                }

                // Add filter if provided
                if (!string.IsNullOrEmpty(filter))
                {
                    searchOptions.Filter = filter;
                }

                var response = await _searchClient.SearchAsync<SearchDocument>(searchText, searchOptions);
                var results = new List<SearchResult<SearchDocument>>();

                await foreach (var result in response.Value.GetResultsAsync())
                {
                    results.Add(result);
                }

                stopwatch.Stop();

                return new SortingResult
                {
                    Documents = results,
                    TotalCount = response.Value.TotalCount,
                    ExecutionTime = stopwatch.Elapsed,
                    OrderBy = orderBy,
                    Metadata = new Dictionary<string, object>
                    {
                        ["sort_fields"] = orderBy.Count,
                        ["has_geographic_sort"] = orderBy.Any(o => o.Contains("geo.distance")),
                        ["has_score_sort"] = orderBy.Any(o => o.Contains("search.score")),
                        ["complexity_score"] = CalculateSortComplexity(orderBy)
                    }
                };
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Error executing sorted search: {OrderBy}", string.Join(", ", orderBy));
                
                return new SortingResult
                {
                    ExecutionTime = stopwatch.Elapsed,
                    OrderBy = orderBy,
                    Metadata = new Dictionary<string, object> { ["error"] = ex.Message }
                };
            }
        }

        /// <summary>
        /// Calculate complexity score for sorting configuration.
        /// </summary>
        private int CalculateSortComplexity(List<string> orderBy)
        {
            if (orderBy == null || !orderBy.Any()) return 0;

            int score = 0;
            score += orderBy.Count; // Number of sort fields
            score += orderBy.Count(o => o.Contains("geo.distance")) * 3; // Geographic sorting is expensive
            score += orderBy.Count(o => o.Contains("search.score")) * 1; // Score sorting
            score += orderBy.Count(o => o.Contains("desc")) * 1; // Descending sorts

            return score;
        }

        /// <summary>
        /// Analyze sort field performance characteristics.
        /// </summary>
        public Dictionary<string, object> AnalyzeSortPerformance(List<string> orderBy)
        {
            var analysis = new Dictionary<string, object>();

            if (orderBy == null || !orderBy.Any())
            {
                analysis["error"] = "No sort fields provided";
                return analysis;
            }

            analysis["field_count"] = orderBy.Count;
            analysis["has_geographic"] = orderBy.Any(o => o.Contains("geo.distance"));
            analysis["has_score"] = orderBy.Any(o => o.Contains("search.score"));
            analysis["complexity_score"] = CalculateSortComplexity(orderBy);

            // Performance recommendations
            var recommendations = new List<string>();

            if (orderBy.Count > 3)
            {
                recommendations.Add("Consider reducing the number of sort fields for better performance");
            }

            if (orderBy.Any(o => o.Contains("geo.distance")))
            {
                recommendations.Add("Geographic sorting can be expensive - consider caching for frequently used locations");
            }

            if (orderBy.Any(o => o.Contains("desc")) && orderBy.Count > 1)
            {
                recommendations.Add("Mixed sort directions may impact performance");
            }

            analysis["recommendations"] = recommendations;

            return analysis;
        }

        /// <summary>
        /// Demonstrate various sorting scenarios.
        /// </summary>
        public async Task DemonstrateSortingOperationsAsync()
        {
            Console.WriteLine("🔄 Sorting Operations Demonstration");
            Console.WriteLine("=" + new string('=', 49));

            foreach (var example in _examples)
            {
                Console.WriteLine($"\n📝 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Use Case: {example.UseCase}");
                Console.WriteLine($"   Complexity: {example.Complexity}");
                Console.WriteLine($"   Order By: {string.Join(", ", example.OrderBy)}");
                Console.WriteLine($"   Performance Score: {example.PerformanceScore}");

                // Execute the sort (in demo mode, we'll just validate syntax)
                try
                {
                    var result = await ExecuteSortedSearchAsync(example.OrderBy, "*", null, 5);
                    Console.WriteLine($"   ✅ Execution Time: {result.ExecutionTime.TotalMilliseconds:F2}ms");
                    
                    if (result.Metadata.ContainsKey("error"))
                    {
                        Console.WriteLine($"   ❌ Error: {result.Metadata["error"]}");
                    }
                    else
                    {
                        Console.WriteLine($"   📊 Results: {result.TotalCount ?? 0} documents");
                        Console.WriteLine($"   🔧 Sort Fields: {result.Metadata["sort_fields"]}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Demo Error: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Show sorting best practices.
        /// </summary>
        public void ShowBestPractices()
        {
            Console.WriteLine("\n🚀 Sorting Best Practices:");
            Console.WriteLine("=" + new string('=', 40));

            var practices = new[]
            {
                "Mark frequently sorted fields as 'sortable' in the index schema",
                "Use single-field sorting when possible for best performance",
                "Place most selective sort criteria first in multi-field sorts",
                "Consider using search.score() for relevance-based sorting",
                "Cache geographic distance calculations for frequently used locations",
                "Use consistent sort directions to optimize query plans",
                "Avoid sorting on high-cardinality text fields",
                "Consider pagination strategies for large result sets",
                "Test sort performance with realistic data volumes",
                "Use faceted navigation instead of complex sorting when appropriate"
            };

            for (int i = 0; i < practices.Length; i++)
            {
                Console.WriteLine($"{i + 1,2}. {practices[i]}");
            }
        }

        /// <summary>
        /// Analyze performance of different sorting patterns.
        /// </summary>
        public async Task AnalyzeSortingPerformanceAsync()
        {
            Console.WriteLine("\n⚡ Sorting Performance Analysis");
            Console.WriteLine("=" + new string('=', 42));

            var testSorts = new[]
            {
                ("Single Field", new List<string> { "rating desc" }),
                ("Multi-Field", new List<string> { "category asc", "rating desc" }),
                ("Score + Field", new List<string> { "search.score() desc", "rating desc" }),
                ("Geographic", new List<string> { "geo.distance(location, geography'POINT(-122.3321 47.6062)') asc" }),
                ("Complex Multi", new List<string> { "category asc", "rating desc", "price asc", "createdDate desc" }),
                ("Mixed Directions", new List<string> { "rating desc", "price asc", "name desc" })
            };

            Console.WriteLine($"{"Sort Type",-20} {"Fields",-8} {"Complexity",-12} {"Performance",-15}");
            Console.WriteLine(new string('-', 60));

            foreach (var (name, orderBy) in testSorts)
            {
                var complexity = CalculateSortComplexity(orderBy);
                var fieldCount = orderBy.Count;
                
                // Performance estimation based on complexity
                string performance = complexity switch
                {
                    <= 2 => "Excellent",
                    <= 5 => "Good",
                    <= 10 => "Fair",
                    _ => "Needs optimization"
                };

                Console.WriteLine($"{name,-20} {fieldCount,-8} {complexity,-12} {performance,-15}");
            }
        }

        /// <summary>
        /// Generate sort configuration from user preferences.
        /// </summary>
        public List<string> GenerateSortFromPreferences(Dictionary<string, object> preferences)
        {
            var sortConfigs = new List<SortConfiguration>();

            // Parse preferences and build sort configurations
            if (preferences.ContainsKey("primary_sort"))
            {
                var primarySort = preferences["primary_sort"].ToString();
                var primaryDirection = preferences.ContainsKey("primary_direction") 
                    ? Enum.Parse<SortDirection>(preferences["primary_direction"].ToString()!, true)
                    : SortDirection.Descending;

                sortConfigs.Add(new SortConfiguration
                {
                    FieldName = primarySort!,
                    Direction = primaryDirection
                });
            }

            if (preferences.ContainsKey("secondary_sort"))
            {
                var secondarySort = preferences["secondary_sort"].ToString();
                var secondaryDirection = preferences.ContainsKey("secondary_direction") 
                    ? Enum.Parse<SortDirection>(preferences["secondary_direction"].ToString()!, true)
                    : SortDirection.Ascending;

                sortConfigs.Add(new SortConfiguration
                {
                    FieldName = secondarySort!,
                    Direction = secondaryDirection
                });
            }

            // Add default relevance sort if no specific sorting is requested
            if (!sortConfigs.Any())
            {
                return new List<string> { "search.score() desc" };
            }

            return BuildMultiFieldSort(sortConfigs);
        }

        /// <summary>
        /// Load predefined sorting examples.
        /// </summary>
        private List<SortExample> LoadSortExamples()
        {
            return new List<SortExample>
            {
                new()
                {
                    Name = "Relevance Sort",
                    OrderBy = new List<string> { "search.score() desc" },
                    Description = "Sort by search relevance score",
                    UseCase = "Default search result ordering",
                    Complexity = SortComplexity.Simple,
                    PerformanceScore = 10
                },
                new()
                {
                    Name = "Rating Descending",
                    OrderBy = new List<string> { "rating desc" },
                    Description = "Sort by rating from highest to lowest",
                    UseCase = "Product listings, reviews",
                    Complexity = SortComplexity.Simple,
                    PerformanceScore = 9
                },
                new()
                {
                    Name = "Price Ascending",
                    OrderBy = new List<string> { "price asc" },
                    Description = "Sort by price from lowest to highest",
                    UseCase = "E-commerce price comparison",
                    Complexity = SortComplexity.Simple,
                    PerformanceScore = 9
                },
                new()
                {
                    Name = "Multi-Field Sort",
                    OrderBy = new List<string> { "category asc", "rating desc", "price asc" },
                    Description = "Sort by category, then rating, then price",
                    UseCase = "Structured product browsing",
                    Complexity = SortComplexity.Moderate,
                    PerformanceScore = 7
                },
                new()
                {
                    Name = "Geographic Distance",
                    OrderBy = new List<string> { "geo.distance(location, geography'POINT(-122.3321 47.6062)') asc" },
                    Description = "Sort by distance from Seattle",
                    UseCase = "Location-based services",
                    Complexity = SortComplexity.Complex,
                    PerformanceScore = 6
                },
                new()
                {
                    Name = "Relevance + Rating",
                    OrderBy = new List<string> { "search.score() desc", "rating desc" },
                    Description = "Sort by relevance, then by rating",
                    UseCase = "Balanced search results",
                    Complexity = SortComplexity.Moderate,
                    PerformanceScore = 8
                },
                new()
                {
                    Name = "Date + Popularity",
                    OrderBy = new List<string> { "createdDate desc", "viewCount desc" },
                    Description = "Sort by newest first, then by popularity",
                    UseCase = "Content discovery",
                    Complexity = SortComplexity.Moderate,
                    PerformanceScore = 7
                },
                new()
                {
                    Name = "Complex Business Logic",
                    OrderBy = new List<string> { "featured desc", "rating desc", "price asc", "createdDate desc" },
                    Description = "Featured items first, then by rating, price, and date",
                    UseCase = "Advanced e-commerce sorting",
                    Complexity = SortComplexity.Advanced,
                    PerformanceScore = 5
                }
            };
        }

        /// <summary>
        /// Run the sorting operations demonstration.
        /// </summary>
        public static async Task RunAsync(IConfiguration configuration, ILogger<SortingOperations> logger)
        {
            try
            {
                // Initialize search client
                var searchClient = SearchClientFactory.Create(configuration);
                var sortingOps = new SortingOperations(searchClient, logger);

                // Run demonstrations
                await sortingOps.DemonstrateSortingOperationsAsync();
                sortingOps.ShowBestPractices();
                await sortingOps.AnalyzeSortingPerformanceAsync();

                // Demonstrate programmatic sort building
                Console.WriteLine("\n🔧 Programmatic Sort Building Example:");
                Console.WriteLine("=" + new string('=', 45));

                var preferences = new Dictionary<string, object>
                {
                    ["primary_sort"] = "rating",
                    ["primary_direction"] = "Descending",
                    ["secondary_sort"] = "price",
                    ["secondary_direction"] = "Ascending"
                };

                var generatedSort = sortingOps.GenerateSortFromPreferences(preferences);
                Console.WriteLine($"Generated Sort: {string.Join(", ", generatedSort)}");

                var analysis = sortingOps.AnalyzeSortPerformance(generatedSort);
                Console.WriteLine($"Complexity Score: {analysis["complexity_score"]}");
                
                if (analysis.ContainsKey("recommendations"))
                {
                    var recommendations = (List<string>)analysis["recommendations"];
                    if (recommendations.Any())
                    {
                        Console.WriteLine("Recommendations:");
                        foreach (var rec in recommendations)
                        {
                            Console.WriteLine($"  • {rec}");
                        }
                    }
                }

                Console.WriteLine("\n✅ Sorting operations demonstration completed!");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error running sorting operations demonstration");
                Console.WriteLine($"❌ Error: {ex.Message}");
            }
        }
    }
}