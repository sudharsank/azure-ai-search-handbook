using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using System.Globalization;

namespace AzureSearchFiltersExamples
{
    /// <summary>
    /// Demonstrates date filtering operations using Azure AI Search.
    /// 
    /// Key Features:
    /// - Date range filtering
    /// - Relative date calculations
    /// - Time zone handling
    /// - Date format considerations
    /// - Temporal analysis and filtering
    /// - Performance optimization for date queries
    /// </summary>
    public class DateFilters
    {
        private readonly SearchClient _searchClient;
        private readonly ILogger<DateFilters> _logger;
        private readonly List<DateFilterExample> _examples;

        public DateFilters(SearchClient searchClient, ILogger<DateFilters> logger)
        {
            _searchClient = searchClient;
            _logger = logger;
            _examples = LoadDateFilterExamples();
        }

        /// <summary>
        /// Represents a date filter example with metadata.
        /// </summary>
        public class DateFilterExample
        {
            public string Name { get; set; } = string.Empty;
            public string Filter { get; set; } = string.Empty;
            public string Description { get; set; } = string.Empty;
            public string UseCase { get; set; } = string.Empty;
            public DateFilterType FilterType { get; set; }
            public int ComplexityScore { get; set; }
        }

        /// <summary>
        /// Types of date filters.
        /// </summary>
        public enum DateFilterType
        {
            Absolute,
            Relative,
            Range,
            Comparison
        }

        /// <summary>
        /// Represents search results with performance metrics.
        /// </summary>
        public class DateFilterResult
        {
            public IList<SearchResult<SearchDocument>> Documents { get; set; } = new List<SearchResult<SearchDocument>>();
            public long? TotalCount { get; set; }
            public TimeSpan ExecutionTime { get; set; }
            public string Filter { get; set; } = string.Empty;
            public Dictionary<string, object> Metadata { get; set; } = new();
        }

        /// <summary>
        /// Build a date range filter.
        /// </summary>
        public string BuildDateRangeFilter(string fieldName, DateTime? startDate, DateTime? endDate, 
            TimeZoneInfo? timeZone = null)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            if (!startDate.HasValue && !endDate.HasValue)
                throw new ArgumentException("At least one date (start or end) must be provided");

            var conditions = new List<string>();

            if (startDate.HasValue)
            {
                var adjustedStart = timeZone != null 
                    ? TimeZoneInfo.ConvertTimeToUtc(startDate.Value, timeZone)
                    : startDate.Value.ToUniversalTime();
                
                var startDateStr = adjustedStart.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);
                conditions.Add($"{fieldName} ge {startDateStr}");
            }

            if (endDate.HasValue)
            {
                var adjustedEnd = timeZone != null 
                    ? TimeZoneInfo.ConvertTimeToUtc(endDate.Value, timeZone)
                    : endDate.Value.ToUniversalTime();
                
                var endDateStr = adjustedEnd.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);
                conditions.Add($"{fieldName} le {endDateStr}");
            }

            return string.Join(" and ", conditions);
        }

        /// <summary>
        /// Build a relative date filter (e.g., last 7 days, next month).
        /// </summary>
        public string BuildRelativeDateFilter(string fieldName, int amount, DateUnit unit, 
            bool isPast = true, DateTime? referenceDate = null)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            var reference = referenceDate ?? DateTime.UtcNow;
            DateTime targetDate;

            switch (unit)
            {
                case DateUnit.Days:
                    targetDate = isPast ? reference.AddDays(-amount) : reference.AddDays(amount);
                    break;
                case DateUnit.Weeks:
                    targetDate = isPast ? reference.AddDays(-amount * 7) : reference.AddDays(amount * 7);
                    break;
                case DateUnit.Months:
                    targetDate = isPast ? reference.AddMonths(-amount) : reference.AddMonths(amount);
                    break;
                case DateUnit.Years:
                    targetDate = isPast ? reference.AddYears(-amount) : reference.AddYears(amount);
                    break;
                default:
                    throw new ArgumentException($"Unsupported date unit: {unit}");
            }

            var targetDateStr = targetDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);
            var referenceStr = reference.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);

            if (isPast)
            {
                return $"{fieldName} ge {targetDateStr} and {fieldName} le {referenceStr}";
            }
            else
            {
                return $"{fieldName} ge {referenceStr} and {fieldName} le {targetDateStr}";
            }
        }

        /// <summary>
        /// Build a date comparison filter.
        /// </summary>
        public string BuildDateComparisonFilter(string fieldName, DateTime date, 
            ComparisonOperator op, TimeZoneInfo? timeZone = null)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            var adjustedDate = timeZone != null 
                ? TimeZoneInfo.ConvertTimeToUtc(date, timeZone)
                : date.ToUniversalTime();

            var dateStr = adjustedDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);

            return op switch
            {
                ComparisonOperator.Equal => $"{fieldName} eq {dateStr}",
                ComparisonOperator.NotEqual => $"{fieldName} ne {dateStr}",
                ComparisonOperator.GreaterThan => $"{fieldName} gt {dateStr}",
                ComparisonOperator.GreaterThanOrEqual => $"{fieldName} ge {dateStr}",
                ComparisonOperator.LessThan => $"{fieldName} lt {dateStr}",
                ComparisonOperator.LessThanOrEqual => $"{fieldName} le {dateStr}",
                _ => throw new ArgumentException($"Unsupported comparison operator: {op}")
            };
        }

        /// <summary>
        /// Build a business hours filter.
        /// </summary>
        public string BuildBusinessHoursFilter(string fieldName, int startHour = 9, int endHour = 17, 
            TimeZoneInfo? timeZone = null)
        {
            if (string.IsNullOrEmpty(fieldName))
                throw new ArgumentException("Field name cannot be null or empty");

            // This is a simplified example - in practice, you'd need more complex logic
            // to handle business hours across different days and time zones
            
            var conditions = new List<string>();
            
            // Filter by hour of day (this would need to be adapted based on your index structure)
            conditions.Add($"hour({fieldName}) ge {startHour}");
            conditions.Add($"hour({fieldName}) lt {endHour}");
            
            // Exclude weekends (assuming dayofweek function exists)
            conditions.Add($"dayofweek({fieldName}) ge 1 and dayofweek({fieldName}) le 5");

            return string.Join(" and ", conditions);
        }

        /// <summary>
        /// Execute a date filter search with performance monitoring.
        /// </summary>
        public async Task<DateFilterResult> ExecuteDateFilterAsync(string filter, 
            string searchText = "*", int top = 10)
        {
            var stopwatch = Stopwatch.StartNew();

            try
            {
                _logger.LogInformation("Executing date filter search: {Filter}", filter);

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

                return new DateFilterResult
                {
                    Documents = results,
                    TotalCount = response.Value.TotalCount,
                    ExecutionTime = stopwatch.Elapsed,
                    Filter = filter,
                    Metadata = new Dictionary<string, object>
                    {
                        ["complexity_score"] = CalculateComplexityScore(filter),
                        ["filter_type"] = DetectFilterType(filter),
                        ["has_timezone_handling"] = filter.Contains("Z")
                    }
                };
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Error executing date filter: {Filter}", filter);
                
                return new DateFilterResult
                {
                    ExecutionTime = stopwatch.Elapsed,
                    Filter = filter,
                    Metadata = new Dictionary<string, object> { ["error"] = ex.Message }
                };
            }
        }

        /// <summary>
        /// Calculate complexity score for a date filter.
        /// </summary>
        private int CalculateComplexityScore(string filter)
        {
            if (string.IsNullOrEmpty(filter)) return 0;

            int score = 0;
            score += filter.Split(" and ").Length - 1; // AND operations
            score += (filter.Split(" or ").Length - 1) * 2; // OR operations
            score += filter.Count(c => c == '('); // Nested conditions
            score += filter.Contains("hour(") ? 2 : 0; // Time functions
            score += filter.Contains("dayofweek(") ? 2 : 0; // Date functions
            score += filter.Contains("Z") ? 1 : 0; // UTC handling

            return score;
        }

        /// <summary>
        /// Detect the primary filter type.
        /// </summary>
        private string DetectFilterType(string filter)
        {
            if (filter.Contains(" ge ") && filter.Contains(" le ")) return "range";
            if (filter.Contains("hour(") || filter.Contains("dayofweek(")) return "temporal";
            if (filter.Contains(" gt ") || filter.Contains(" lt ")) return "comparison";
            return "simple";
        }

        /// <summary>
        /// Demonstrate various date filtering scenarios.
        /// </summary>
        public async Task DemonstrateDateFiltersAsync()
        {
            Console.WriteLine("📅 Date Filters Demonstration");
            Console.WriteLine("=" + new string('=', 49));

            foreach (var example in _examples)
            {
                Console.WriteLine($"\n📝 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Use Case: {example.UseCase}");
                Console.WriteLine($"   Filter Type: {example.FilterType}");
                Console.WriteLine($"   Filter: {example.Filter}");
                Console.WriteLine($"   Complexity: {example.ComplexityScore}");

                // Execute the filter (in demo mode, we'll just validate syntax)
                try
                {
                    var result = await ExecuteDateFilterAsync(example.Filter, "*", 5);
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
        /// Show date filter best practices.
        /// </summary>
        public void ShowBestPractices()
        {
            Console.WriteLine("\n🚀 Date Filter Best Practices:");
            Console.WriteLine("=" + new string('=', 40));

            var practices = new[]
            {
                "Always use UTC dates in filters to avoid timezone issues",
                "Use ISO 8601 format (yyyy-MM-ddTHH:mm:ss.fffZ) for consistency",
                "Consider timezone conversion for user-facing applications",
                "Use date ranges instead of exact matches for better performance",
                "Index date fields with appropriate precision for your use case",
                "Cache relative date calculations to improve performance",
                "Validate date inputs to prevent invalid filter expressions",
                "Use business logic to handle edge cases (leap years, DST)",
                "Consider using date math functions for complex temporal queries",
                "Test date filters across different time zones and locales"
            };

            for (int i = 0; i < practices.Length; i++)
            {
                Console.WriteLine($"{i + 1,2}. {practices[i]}");
            }
        }

        /// <summary>
        /// Analyze performance of different date filter patterns.
        /// </summary>
        public async Task AnalyzeDateFilterPerformanceAsync()
        {
            Console.WriteLine("\n⚡ Date Filter Performance Analysis");
            Console.WriteLine("=" + new string('=', 42));

            var now = DateTime.UtcNow;
            var testFilters = new[]
            {
                ("Simple Comparison", $"createdDate gt {now.AddDays(-1):yyyy-MM-ddTHH:mm:ss.fffZ}"),
                ("Date Range", $"createdDate ge {now.AddDays(-7):yyyy-MM-ddTHH:mm:ss.fffZ} and createdDate le {now:yyyy-MM-ddTHH:mm:ss.fffZ}"),
                ("Last Month", $"createdDate ge {now.AddMonths(-1):yyyy-MM-ddTHH:mm:ss.fffZ}"),
                ("Business Hours", "hour(createdDate) ge 9 and hour(createdDate) lt 17"),
                ("Weekdays Only", "dayofweek(createdDate) ge 1 and dayofweek(createdDate) le 5"),
                ("Complex Temporal", $"createdDate ge {now.AddDays(-30):yyyy-MM-ddTHH:mm:ss.fffZ} and hour(createdDate) ge 9 and dayofweek(createdDate) le 5")
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
        /// Load predefined date filter examples.
        /// </summary>
        private List<DateFilterExample> LoadDateFilterExamples()
        {
            var now = DateTime.UtcNow;
            
            return new List<DateFilterExample>
            {
                new()
                {
                    Name = "Last 7 Days",
                    Filter = $"createdDate ge {now.AddDays(-7):yyyy-MM-ddTHH:mm:ss.fffZ}",
                    Description = "Find documents created in the last 7 days",
                    UseCase = "Recent content filtering",
                    FilterType = DateFilterType.Relative,
                    ComplexityScore = 1
                },
                new()
                {
                    Name = "Date Range",
                    Filter = $"createdDate ge {now.AddDays(-30):yyyy-MM-ddTHH:mm:ss.fffZ} and createdDate le {now:yyyy-MM-ddTHH:mm:ss.fffZ}",
                    Description = "Find documents created in the last 30 days",
                    UseCase = "Monthly reporting and analysis",
                    FilterType = DateFilterType.Range,
                    ComplexityScore = 2
                },
                new()
                {
                    Name = "Future Events",
                    Filter = $"eventDate gt {now:yyyy-MM-ddTHH:mm:ss.fffZ}",
                    Description = "Find upcoming events",
                    UseCase = "Event management and scheduling",
                    FilterType = DateFilterType.Comparison,
                    ComplexityScore = 1
                },
                new()
                {
                    Name = "This Year",
                    Filter = $"createdDate ge {new DateTime(now.Year, 1, 1):yyyy-MM-ddTHH:mm:ss.fffZ}",
                    Description = "Find documents created this year",
                    UseCase = "Annual reporting and analysis",
                    FilterType = DateFilterType.Absolute,
                    ComplexityScore = 1
                },
                new()
                {
                    Name = "Business Hours",
                    Filter = "hour(createdDate) ge 9 and hour(createdDate) lt 17 and dayofweek(createdDate) ge 1 and dayofweek(createdDate) le 5",
                    Description = "Find documents created during business hours",
                    UseCase = "Business activity analysis",
                    FilterType = DateFilterType.Relative,
                    ComplexityScore = 4
                }
            };
        }

        /// <summary>
        /// Run the date filters demonstration.
        /// </summary>
        public static async Task RunAsync(IConfiguration configuration, ILogger<DateFilters> logger)
        {
            try
            {
                // Initialize search client
                var searchClient = SearchClientFactory.Create(configuration);
                var dateFilters = new DateFilters(searchClient, logger);

                // Run demonstrations
                await dateFilters.DemonstrateDateFiltersAsync();
                dateFilters.ShowBestPractices();
                await dateFilters.AnalyzeDateFilterPerformanceAsync();

                Console.WriteLine("\n✅ Date filters demonstration completed!");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error running date filters demonstration");
                Console.WriteLine($"❌ Error: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Date units for relative date calculations.
    /// </summary>
    public enum DateUnit
    {
        Days,
        Weeks,
        Months,
        Years
    }

    /// <summary>
    /// Comparison operators for date filtering.
    /// </summary>
    public enum ComparisonOperator
    {
        Equal,
        NotEqual,
        GreaterThan,
        GreaterThanOrEqual,
        LessThan,
        LessThanOrEqual
    }
}