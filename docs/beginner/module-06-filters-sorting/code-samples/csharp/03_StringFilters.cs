using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using System.Text.RegularExpressions;

namespace AzureSearchFiltersExamples
{
    /// <summary>
    /// Demonstrates string filtering operations using Azure AI Search.
    /// 
    /// Key Features:
    /// - Text matching with startswith, endswith, contains
    /// - Case sensitivity handling
    /// - Pattern matching techniques
    /// - Multi-language considerations
    /// - String filter optimization
    /// - Wildcard and regex-like filtering
    /// </summary>
    public class StringFilters
    {
        private readonly SearchClient _searchClient;
        private readonly ILogger<StringFilters> _logger;
        private readonly List<StringFilterExample> _examples;

        public StringFilters(SearchClient searchClient, ILogger<StringFilters> logger)
        {
            _searchClient = searchClient;
            _logger = logger;
            _examples = LoadStringFilterExamples();
        }

        /// <summary>
        /// Represents a string filter example with metadata.
        /// </summary>
        public class StringFilterExample
        {
            public string Name { get; set; } = string.Empty;
            public string Filter { get; set; } = string.Empty;
            public string Description { get; set; } = string.Empty;
            public string UseCase { get; set; } = string.Empty;
            public bool CaseSensitive { get; set; }
            public int ComplexityScore { get; set; }
        }

        /// <summary>
        /// Represents search results with performance metrics.
        /// </summary>
        public class StringFilterResult
        {
            public IList<SearchResult<SearchDocument>> Documents { get; set; } = new List<SearchResult<SearchDocument>>();
            public long? TotalCount { get; set; }
            public TimeSpan ExecutionTime { get; set; }
            public string Filter { get; set; } = string.Empty;
            public Dictionary<string, object> Metadata { get; set; } = new();
        }

        /// <summary>
        /// Build a startswith filter for text fields.
        /// </summary>
        public string BuildStartsWithFilter(string fieldName, string prefix, bool caseSensitive = false)
        {
            if (string.IsNullOrEmpty(fieldName) || string.IsNullOrEmpty(prefix))
                throw new ArgumentException("Field name and prefix cannot be null or empty");

            // Escape single quotes in the prefix
            var escapedPrefix = prefix.Replace("'", "''");
            
            if (caseSensitive)
            {
                return $"startswith({fieldName}, '{escapedPrefix}')";
            }
            else
            {
                // Use tolower for case-insensitive matching
                return $"startswith(tolower({fieldName}), tolower('{escapedPrefix}'))";
            }
        }

        /// <summary>
        /// Build an endswith filter for text fields.
        /// </summary>
        public string BuildEndsWithFilter(string fieldName, string suffix, bool caseSensitive = false)
        {
            if (string.IsNullOrEmpty(fieldName) || string.IsNullOrEmpty(suffix))
                throw new ArgumentException("Field name and suffix cannot be null or empty");

            var escapedSuffix = suffix.Replace("'", "''");
            
            if (caseSensitive)
            {
                return $"endswith({fieldName}, '{escapedSuffix}')";
            }
            else
            {
                return $"endswith(tolower({fieldName}), tolower('{escapedSuffix}'))";
            }
        }

        /// <summary>
        /// Build a contains filter for text fields.
        /// </summary>
        public string BuildContainsFilter(string fieldName, string substring, bool caseSensitive = false)
        {
            if (string.IsNullOrEmpty(fieldName) || string.IsNullOrEmpty(substring))
                throw new ArgumentException("Field name and substring cannot be null or empty");

            var escapedSubstring = substring.Replace("'", "''");
            
            if (caseSensitive)
            {
                return $"search.ismatch('{escapedSubstring}', '{fieldName}')";
            }
            else
            {
                return $"contains(tolower({fieldName}), tolower('{escapedSubstring}'))";
            }
        }

        /// <summary>
        /// Build a multi-pattern filter (OR condition for multiple patterns).
        /// </summary>
        public string BuildMultiPatternFilter(string fieldName, List<string> patterns, 
            string operation = "contains", bool caseSensitive = false)
        {
            if (string.IsNullOrEmpty(fieldName) || patterns == null || !patterns.Any())
                throw new ArgumentException("Field name and patterns cannot be null or empty");

            var conditions = new List<string>();

            foreach (var pattern in patterns)
            {
                var escapedPattern = pattern.Replace("'", "''");
                string condition;

                switch (operation.ToLower())
                {
                    case "startswith":
                        condition = caseSensitive 
                            ? $"startswith({fieldName}, '{escapedPattern}')"
                            : $"startswith(tolower({fieldName}), tolower('{escapedPattern}'))";
                        break;
                    case "endswith":
                        condition = caseSensitive 
                            ? $"endswith({fieldName}, '{escapedPattern}')"
                            : $"endswith(tolower({fieldName}), tolower('{escapedPattern}'))";
                        break;
                    case "contains":
                    default:
                        condition = caseSensitive 
                            ? $"search.ismatch('{escapedPattern}', '{fieldName}')"
                            : $"contains(tolower({fieldName}), tolower('{escapedPattern}'))";
                        break;
                }

                conditions.Add(condition);
            }

            return string.Join(" or ", conditions);
        }

        /// <summary>
        /// Build a length-based filter for string fields.
        /// </summary>
        public string BuildLengthFilter(string fieldName, int minLength, int? maxLength = null)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            var conditions = new List<string>();

            if (minLength > 0)
            {
                conditions.Add($"length({fieldName}) ge {minLength}");
            }

            if (maxLength.HasValue)
            {
                conditions.Add($"length({fieldName}) le {maxLength.Value}");
            }

            return conditions.Any() ? string.Join(" and ", conditions) : string.Empty;
        }

        /// <summary>
        /// Execute a string filter search with performance monitoring.
        /// </summary>
        public async Task<StringFilterResult> ExecuteStringFilterAsync(string filter, 
            string searchText = "*", int top = 10)
        {
            var stopwatch = Stopwatch.StartNew();

            try
            {
                _logger.LogInformation("Executing string filter search: {Filter}", filter);

                var searchOptions = new SearchOptions
                {
                    Filter = filter,
                    Size = top,
                    IncludeTotalCount = true
                };

                var response = await _searchClient.SearchAsync<SearchDocument>(searchText, searchOptions);
                var results = new List<SearchResult<SearchDocument>>();

                await foreach (var result in response.Value.GetResultsAsync())
                {
                    results.Add(result);
                }

                stopwatch.Stop();

                return new StringFilterResult
                {
                    Documents = results,
                    TotalCount = response.Value.TotalCount,
                    ExecutionTime = stopwatch.Elapsed,
                    Filter = filter,
                    Metadata = new Dictionary<string, object>
                    {
                        ["complexity_score"] = CalculateComplexityScore(filter),
                        ["case_sensitive"] = !filter.Contains("tolower"),
                        ["operation_type"] = DetectOperationType(filter)
                    }
                };
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Error executing string filter: {Filter}", filter);
                
                return new StringFilterResult
                {
                    ExecutionTime = stopwatch.Elapsed,
                    Filter = filter,
                    Metadata = new Dictionary<string, object> { ["error"] = ex.Message }
                };
            }
        }

        /// <summary>
        /// Calculate complexity score for a string filter.
        /// </summary>
        private int CalculateComplexityScore(string filter)
        {
            if (string.IsNullOrEmpty(filter)) return 0;

            int score = 0;
            score += filter.Split(" and ").Length - 1; // AND operations
            score += (filter.Split(" or ").Length - 1) * 2; // OR operations (more expensive)
            score += filter.Count(c => c == '('); // Nested conditions
            score += filter.Contains("tolower") ? 1 : 0; // Case conversion
            score += filter.Contains("search.ismatch") ? 2 : 0; // Full-text search
            score += filter.Contains("length") ? 1 : 0; // Length functions

            return score;
        }

        /// <summary>
        /// Detect the primary operation type in a filter.
        /// </summary>
        private string DetectOperationType(string filter)
        {
            if (filter.Contains("startswith")) return "startswith";
            if (filter.Contains("endswith")) return "endswith";
            if (filter.Contains("contains")) return "contains";
            if (filter.Contains("search.ismatch")) return "full_text";
            if (filter.Contains("length")) return "length";
            return "unknown";
        }

        /// <summary>
        /// Demonstrate various string filtering scenarios.
        /// </summary>
        public async Task DemonstrateStringFiltersAsync()
        {
            Console.WriteLine("🔤 String Filters Demonstration");
            Console.WriteLine("=" + new string('=', 49));

            foreach (var example in _examples)
            {
                Console.WriteLine($"\n📝 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Use Case: {example.UseCase}");
                Console.WriteLine($"   Filter: {example.Filter}");
                Console.WriteLine($"   Case Sensitive: {example.CaseSensitive}");
                Console.WriteLine($"   Complexity: {example.ComplexityScore}");

                // Execute the filter (in demo mode, we'll just validate syntax)
                try
                {
                    var result = await ExecuteStringFilterAsync(example.Filter, "*", 5);
                    Console.WriteLine($"   ✅ Execution Time: {result.ExecutionTime.TotalMilliseconds:F2}ms");
                    
                    if (result.Metadata.ContainsKey("error"))
                    {
                        Console.WriteLine($"   ❌ Error: {result.Metadata["error"]}");
                    }
                    else
                    {
                        Console.WriteLine($"   📊 Results: {result.TotalCount ?? 0} documents");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Demo Error: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Show string filter best practices.
        /// </summary>
        public void ShowBestPractices()
        {
            Console.WriteLine("\n🚀 String Filter Best Practices:");
            Console.WriteLine("=" + new string('=', 40));

            var practices = new[]
            {
                "Use case-insensitive filters for user input (tolower function)",
                "Escape single quotes in filter values to prevent syntax errors",
                "Prefer 'contains' over 'search.ismatch' for simple substring matching",
                "Use 'startswith' for prefix matching - it's more efficient than contains",
                "Consider field-specific analyzers for complex text matching",
                "Validate input length to prevent performance issues",
                "Use multi-pattern filters instead of multiple OR conditions",
                "Cache frequently used string filter patterns",
                "Consider using search.ismatch for complex pattern matching",
                "Test string filters with various character encodings and languages"
            };

            for (int i = 0; i < practices.Length; i++)
            {
                Console.WriteLine($"{i + 1,2}. {practices[i]}");
            }
        }

        /// <summary>
        /// Analyze performance of different string filter patterns.
        /// </summary>
        public async Task AnalyzeStringFilterPerformanceAsync()
        {
            Console.WriteLine("\n⚡ String Filter Performance Analysis");
            Console.WriteLine("=" + new string('=', 42));

            var testFilters = new[]
            {
                ("Simple Contains", "contains(tolower(name), 'test')"),
                ("Starts With", "startswith(tolower(name), 'prod')"),
                ("Ends With", "endswith(tolower(name), '.com')"),
                ("Multi-Pattern", "contains(tolower(name), 'test') or contains(tolower(name), 'demo')"),
                ("Length Filter", "length(name) ge 5 and length(name) le 20"),
                ("Complex Pattern", "startswith(tolower(name), 'prod') and contains(tolower(description), 'premium')")
            };

            Console.WriteLine($"{"Filter Type",-20} {"Complexity",-12} {"Performance",-15}");
            Console.WriteLine(new string('-', 50));

            foreach (var (name, filter) in testFilters)
            {
                var complexity = CalculateComplexityScore(filter);
                
                // Performance estimation based on complexity
                string performance = complexity switch
                {
                    <= 2 => "Excellent",
                    <= 5 => "Good",
                    <= 10 => "Fair",
                    _ => "Needs optimization"
                };

                Console.WriteLine($"{name,-20} {complexity,-12} {performance,-15}");
            }
        }

        /// <summary>
        /// Load predefined string filter examples.
        /// </summary>
        private List<StringFilterExample> LoadStringFilterExamples()
        {
            return new List<StringFilterExample>
            {
                new()
                {
                    Name = "Product Name Prefix",
                    Filter = "startswith(tolower(name), 'azure')",
                    Description = "Find products starting with 'Azure'",
                    UseCase = "Product catalog filtering",
                    CaseSensitive = false,
                    ComplexityScore = 1
                },
                new()
                {
                    Name = "Email Domain Filter",
                    Filter = "endswith(tolower(email), '@microsoft.com')",
                    Description = "Find users with Microsoft email addresses",
                    UseCase = "User management and filtering",
                    CaseSensitive = false,
                    ComplexityScore = 1
                },
                new()
                {
                    Name = "Description Keywords",
                    Filter = "contains(tolower(description), 'machine learning')",
                    Description = "Find items containing 'machine learning' in description",
                    UseCase = "Content discovery and search",
                    CaseSensitive = false,
                    ComplexityScore = 1
                },
                new()
                {
                    Name = "Multi-Category Filter",
                    Filter = "contains(tolower(category), 'ai') or contains(tolower(category), 'ml') or contains(tolower(category), 'data')",
                    Description = "Find items in AI, ML, or Data categories",
                    UseCase = "Multi-category product filtering",
                    CaseSensitive = false,
                    ComplexityScore = 4
                },
                new()
                {
                    Name = "Title Length Filter",
                    Filter = "length(title) ge 10 and length(title) le 100",
                    Description = "Find items with title length between 10-100 characters",
                    UseCase = "Content quality filtering",
                    CaseSensitive = false,
                    ComplexityScore = 2
                },
                new()
                {
                    Name = "Complex Text Pattern",
                    Filter = "startswith(tolower(name), 'azure') and contains(tolower(description), 'cloud') and not contains(tolower(tags), 'deprecated')",
                    Description = "Azure products with cloud in description, not deprecated",
                    UseCase = "Advanced product filtering",
                    CaseSensitive = false,
                    ComplexityScore = 6
                }
            };
        }

        /// <summary>
        /// Validate string filter syntax and provide recommendations.
        /// </summary>
        public (bool IsValid, List<string> Issues, List<string> Recommendations) ValidateStringFilter(string filter)
        {
            var issues = new List<string>();
            var recommendations = new List<string>();

            if (string.IsNullOrEmpty(filter))
            {
                issues.Add("Filter cannot be null or empty");
                return (false, issues, recommendations);
            }

            // Check for unescaped quotes
            var singleQuoteCount = filter.Count(c => c == '\'');
            if (singleQuoteCount % 2 != 0)
            {
                issues.Add("Unmatched single quotes detected");
            }

            // Check for potential SQL injection patterns
            var suspiciousPatterns = new[] { "--", "/*", "*/", "xp_", "sp_" };
            if (suspiciousPatterns.Any(pattern => filter.Contains(pattern, StringComparison.OrdinalIgnoreCase)))
            {
                issues.Add("Potentially unsafe patterns detected");
            }

            // Performance recommendations
            if (filter.Contains("contains") && !filter.Contains("tolower"))
            {
                recommendations.Add("Consider using tolower() for case-insensitive matching");
            }

            if (filter.Split(" or ").Length > 5)
            {
                recommendations.Add("Consider using search.ismatch for complex OR conditions");
            }

            var complexity = CalculateComplexityScore(filter);
            if (complexity > 10)
            {
                recommendations.Add("Filter complexity is high - consider simplification");
            }

            return (issues.Count == 0, issues, recommendations);
        }

        /// <summary>
        /// Run the string filters demonstration.
        /// </summary>
        public static async Task RunAsync(IConfiguration configuration, ILogger<StringFilters> logger)
        {
            try
            {
                // Initialize search client
                var searchClient = SearchClientFactory.Create(configuration);
                var stringFilters = new StringFilters(searchClient, logger);

                // Run demonstrations
                await stringFilters.DemonstrateStringFiltersAsync();
                stringFilters.ShowBestPractices();
                await stringFilters.AnalyzeStringFilterPerformanceAsync();

                Console.WriteLine("\n✅ String filters demonstration completed!");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error running string filters demonstration");
                Console.WriteLine($"❌ Error: {ex.Message}");
            }
        }
    }
}