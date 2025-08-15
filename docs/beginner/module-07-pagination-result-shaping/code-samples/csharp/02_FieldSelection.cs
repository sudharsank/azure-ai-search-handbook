/*
 * Module 7: Field Selection and Result Optimization
 * 
 * This example demonstrates how to use field selection to optimize response
 * payloads, improve performance, and control data exposure.
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace AzureSearchFieldSelection
{
    /// <summary>
    /// Represents the result of a field selection operation
    /// </summary>
    /// <typeparam name="T">The type of documents in the result</typeparam>
    public class FieldSelectionResult<T>
    {
        public List<T> Documents { get; set; } = new List<T>();
        public List<string> FieldsRequested { get; set; } = new List<string>();
        public List<string> FieldsReturned { get; set; } = new List<string>();
        public double DurationMs { get; set; }
        public int ResponseSizeBytes { get; set; }
        public int DocumentCount { get; set; }
        public string Query { get; set; } = string.Empty;
    }

    /// <summary>
    /// Configuration for field selection presets
    /// </summary>
    public class FieldSelectionPresets
    {
        public static readonly Dictionary<string, List<string>> Presets = new Dictionary<string, List<string>>
        {
            ["list_view"] = new List<string> { "hotelId", "hotelName", "rating", "category" },
            ["search_results"] = new List<string> { "hotelId", "hotelName", "description", "rating", "location" },
            ["detail_view"] = new List<string> 
            { 
                "hotelId", "hotelName", "description", "category", "rating",
                "location", "address", "tags", "parkingIncluded", "smokingAllowed"
            },
            ["map_view"] = new List<string> { "hotelId", "hotelName", "location", "rating" },
            ["comparison"] = new List<string> { "hotelId", "hotelName", "rating", "category", "tags", "parkingIncluded" },
            ["autocomplete"] = new List<string> { "hotelId", "hotelName" },
            ["analytics"] = new List<string> { "hotelId", "category", "rating", "lastRenovationDate" },
            ["mobile"] = new List<string> { "hotelId", "hotelName", "rating" },
            ["desktop"] = new List<string> { "hotelId", "hotelName", "description", "rating", "category" }
        };
    }

    /// <summary>
    /// Field selector for optimizing search result payloads
    /// </summary>
    /// <typeparam name="T">The type of documents to work with</typeparam>
    public class FieldSelector<T> where T : class
    {
        private readonly SearchClient _searchClient;
        private readonly Dictionary<string, object> _fieldCache;

        public FieldSelector(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
            _fieldCache = new Dictionary<string, object>();
        }

        /// <summary>
        /// Search with specific field selection
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="fields">List of fields to select</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>Field selection result</returns>
        public async Task<FieldSelectionResult<T>> SearchWithFieldsAsync(
            string searchText,
            IList<string>? fields = null,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            try
            {
                var fieldsDisplay = fields?.Any() == true ? string.Join(", ", fields) : "all fields";
                Console.WriteLine($"Searching with fields: {fieldsDisplay}");

                var stopwatch = Stopwatch.StartNew();

                // Configure search options
                var searchOptions = options ?? new SearchOptions();
                searchOptions.Size = searchOptions.Size ?? 10;
                searchOptions.Skip = searchOptions.Skip ?? 0;

                if (fields?.Any() == true)
                {
                    searchOptions.Select.Clear();
                    foreach (var field in fields)
                    {
                        searchOptions.Select.Add(field);
                    }
                }

                // Perform search
                var response = await _searchClient.SearchAsync<T>(searchText, searchOptions, cancellationToken);
                var searchResults = response.Value;

                // Convert to list
                var documents = new List<T>();
                await foreach (var result in searchResults.GetResultsAsync())
                {
                    documents.Add(result.Document);
                }

                stopwatch.Stop();
                var duration = stopwatch.Elapsed.TotalMilliseconds;

                // Calculate response size (estimate)
                var responseSize = EstimateResponseSize(documents);

                // Get actual fields returned
                var fieldsReturned = GetReturnedFields(documents);

                Console.WriteLine($"Search completed in {duration:F1}ms");
                Console.WriteLine($"Response size: ~{responseSize} bytes");

                return new FieldSelectionResult<T>
                {
                    Documents = documents,
                    FieldsRequested = fields?.ToList() ?? new List<string>(),
                    FieldsReturned = fieldsReturned,
                    DurationMs = duration,
                    ResponseSizeBytes = responseSize,
                    DocumentCount = documents.Count,
                    Query = searchText
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Field selection search error: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search with context-based field selection
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="context">Context name (e.g., 'list_view', 'detail_view')</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>Field selection result</returns>
        public async Task<FieldSelectionResult<T>> SearchWithContextAsync(
            string searchText,
            string context,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            var fields = FieldSelectionPresets.Presets.GetValueOrDefault(context, 
                FieldSelectionPresets.Presets["search_results"]);

            Console.WriteLine($"Using {context} context with fields: {string.Join(", ", fields)}");

            return await SearchWithFieldsAsync(searchText, fields, cancellationToken, options);
        }

        /// <summary>
        /// Compare response sizes and performance with different field selections
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="fieldSets">List of field set configurations</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>List of comparison results</returns>
        public async Task<List<Dictionary<string, object>>> CompareFieldSelectionsAsync(
            string searchText,
            List<(string Name, List<string> Fields)> fieldSets,
            CancellationToken cancellationToken = default)
        {
            var comparisons = new List<Dictionary<string, object>>();

            foreach (var (name, fields) in fieldSets)
            {
                try
                {
                    var result = await SearchWithFieldsAsync(searchText, fields, cancellationToken);

                    comparisons.Add(new Dictionary<string, object>
                    {
                        ["name"] = name,
                        ["fields"] = fields,
                        ["fieldCount"] = fields.Count,
                        ["durationMs"] = result.DurationMs,
                        ["responseSizeBytes"] = result.ResponseSizeBytes,
                        ["documentCount"] = result.DocumentCount,
                        ["avgSizePerDoc"] = result.DocumentCount > 0 ? result.ResponseSizeBytes / result.DocumentCount : 0
                    });

                    Console.WriteLine($"{name}: {result.DurationMs:F1}ms, ~{result.ResponseSizeBytes} bytes");
                }
                catch (Exception ex)
                {
                    comparisons.Add(new Dictionary<string, object>
                    {
                        ["name"] = name,
                        ["fields"] = fields,
                        ["error"] = ex.Message
                    });
                }
            }

            return comparisons;
        }

        /// <summary>
        /// Validate field selection against available fields
        /// </summary>
        /// <param name="fields">Fields to validate</param>
        /// <returns>Validation result</returns>
        public Dictionary<string, object> ValidateFields(IList<string> fields)
        {
            // In a real implementation, you would get this from the search service
            // For this example, we'll simulate common hotel index fields
            var availableFields = new HashSet<string>
            {
                "hotelId", "hotelName", "description", "category", "rating",
                "location", "address", "tags", "parkingIncluded", "smokingAllowed",
                "lastRenovationDate"
            };

            var validFields = fields.Where(f => availableFields.Contains(f)).ToList();
            var invalidFields = fields.Where(f => !availableFields.Contains(f)).ToList();

            return new Dictionary<string, object>
            {
                ["validFields"] = validFields,
                ["invalidFields"] = invalidFields,
                ["isValid"] = !invalidFields.Any(),
                ["validationMessage"] = invalidFields.Any() 
                    ? $"Invalid fields: {string.Join(", ", invalidFields)}" 
                    : "All fields valid"
            };
        }

        private int EstimateResponseSize<TDoc>(List<TDoc> documents)
        {
            try
            {
                var json = JsonSerializer.Serialize(documents);
                return System.Text.Encoding.UTF8.GetByteCount(json);
            }
            catch
            {
                return 0;
            }
        }

        private List<string> GetReturnedFields<TDoc>(List<TDoc> documents)
        {
            if (!documents.Any())
                return new List<string>();

            // Get properties from first document (excluding search metadata)
            var firstDoc = documents.First();
            var properties = firstDoc?.GetType().GetProperties()
                .Where(p => !p.Name.StartsWith("@search"))
                .Select(p => p.Name)
                .ToList() ?? new List<string>();

            return properties;
        }
    }

    /// <summary>
    /// Advanced field selection optimizer
    /// </summary>
    /// <typeparam name="T">Document type</typeparam>
    public class FieldSelectionOptimizer<T> where T : class
    {
        private readonly FieldSelector<T> _fieldSelector;
        private readonly Dictionary<string, Dictionary<string, object>> _performanceCache;

        public FieldSelectionOptimizer(FieldSelector<T> fieldSelector)
        {
            _fieldSelector = fieldSelector;
            _performanceCache = new Dictionary<string, Dictionary<string, object>>();
        }

        /// <summary>
        /// Find optimal field selection based on performance and content value
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="maxFields">Maximum number of fields to include</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>List of optimal fields</returns>
        public async Task<List<string>> FindOptimalFieldsAsync(
            string searchText,
            int maxFields = 10,
            CancellationToken cancellationToken = default)
        {
            // Essential fields that should always be included
            var essentialFields = new List<string> { "hotelId", "hotelName", "rating" };
            
            // High-value fields for search context
            var highValueFields = new List<string> { "description", "category", "location" };
            
            var optimalFields = new List<string>(essentialFields);
            
            // Add high-value fields up to the limit
            foreach (var field in highValueFields)
            {
                if (optimalFields.Count < maxFields && !optimalFields.Contains(field))
                {
                    optimalFields.Add(field);
                }
            }

            Console.WriteLine($"Optimal fields: {string.Join(", ", optimalFields)}");
            return optimalFields.Take(maxFields).ToList();
        }

        /// <summary>
        /// Analyze field usage patterns across multiple queries
        /// </summary>
        /// <param name="searchQueries">List of search queries to analyze</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Analysis results</returns>
        public async Task<Dictionary<string, object>> AnalyzeFieldUsageAsync(
            List<string> searchQueries,
            CancellationToken cancellationToken = default)
        {
            var analysis = new Dictionary<string, object>
            {
                ["queriesAnalyzed"] = searchQueries.Count,
                ["fieldPerformance"] = new Dictionary<string, Dictionary<string, object>>(),
                ["recommendations"] = new List<string>()
            };

            var fieldPerformance = (Dictionary<string, Dictionary<string, object>>)analysis["fieldPerformance"];

            foreach (var query in searchQueries)
            {
                foreach (var (presetName, fields) in FieldSelectionPresets.Presets)
                {
                    try
                    {
                        var result = await _fieldSelector.SearchWithFieldsAsync(
                            query, fields, cancellationToken);

                        if (!fieldPerformance.ContainsKey(presetName))
                        {
                            fieldPerformance[presetName] = new Dictionary<string, object>
                            {
                                ["totalDuration"] = 0.0,
                                ["totalSize"] = 0,
                                ["queryCount"] = 0
                            };
                        }

                        var perf = fieldPerformance[presetName];
                        perf["totalDuration"] = (double)perf["totalDuration"] + result.DurationMs;
                        perf["totalSize"] = (int)perf["totalSize"] + result.ResponseSizeBytes;
                        perf["queryCount"] = (int)perf["queryCount"] + 1;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error analyzing {presetName} for query '{query}': {ex.Message}");
                    }
                }
            }

            // Calculate averages and generate recommendations
            foreach (var (presetName, perf) in fieldPerformance)
            {
                var queryCount = (int)perf["queryCount"];
                if (queryCount > 0)
                {
                    perf["avgDuration"] = (double)perf["totalDuration"] / queryCount;
                    perf["avgSize"] = (int)perf["totalSize"] / queryCount;
                }
            }

            // Find best performing preset
            var validPresets = fieldPerformance.Where(kvp => (int)kvp.Value["queryCount"] > 0).ToList();
            if (validPresets.Any())
            {
                var bestPreset = validPresets.OrderBy(kvp => (double)kvp.Value["avgDuration"]).First();
                var recommendations = (List<string>)analysis["recommendations"];
                recommendations.Add($"Best performing preset: {bestPreset.Key} " +
                    $"(avg: {(double)bestPreset.Value["avgDuration"]:F1}ms)");
            }

            return analysis;
        }
    }

    /// <summary>
    /// Hotel model for demonstration
    /// </summary>
    public class Hotel
    {
        public string HotelId { get; set; } = string.Empty;
        public string HotelName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public double? Rating { get; set; }
        public GeographyPoint? Location { get; set; }
        public bool? ParkingIncluded { get; set; }
        public bool? SmokingAllowed { get; set; }
        public string[] Tags { get; set; } = Array.Empty<string>();
        public DateTimeOffset? LastRenovationDate { get; set; }
    }

    /// <summary>
    /// Demonstration class for field selection
    /// </summary>
    public class FieldSelectionDemo
    {
        private readonly SearchClient _searchClient;

        public FieldSelectionDemo(SearchClient searchClient)
        {
            _searchClient = searchClient;
        }

        /// <summary>
        /// Demonstrates basic field selection functionality
        /// </summary>
        public async Task DemonstrateBasicFieldSelectionAsync()
        {
            Console.WriteLine("=== Basic Field Selection Demo ===\n");

            var fieldSelector = new FieldSelector<Hotel>(_searchClient);

            try
            {
                // Search without field selection (all fields)
                Console.WriteLine("1. Search without field selection (all fields):");
                var allFieldsResult = await fieldSelector.SearchWithFieldsAsync("luxury", null);
                Console.WriteLine($"Duration: {allFieldsResult.DurationMs:F1}ms");
                Console.WriteLine($"Response size: ~{allFieldsResult.ResponseSizeBytes} bytes");
                Console.WriteLine($"Fields returned: {string.Join(", ", allFieldsResult.FieldsReturned)}\n");

                // Search with minimal field selection
                Console.WriteLine("2. Search with minimal field selection:");
                var minimalFields = new List<string> { "hotelId", "hotelName", "rating" };
                var minimalResult = await fieldSelector.SearchWithFieldsAsync("luxury", minimalFields);
                Console.WriteLine($"Duration: {minimalResult.DurationMs:F1}ms");
                Console.WriteLine($"Response size: ~{minimalResult.ResponseSizeBytes} bytes");
                Console.WriteLine($"Fields returned: {string.Join(", ", minimalResult.FieldsReturned)}\n");

                // Calculate size reduction
                if (allFieldsResult.ResponseSizeBytes > 0)
                {
                    var sizeReduction = ((double)(allFieldsResult.ResponseSizeBytes - minimalResult.ResponseSizeBytes) /
                        allFieldsResult.ResponseSizeBytes) * 100;
                    Console.WriteLine($"Size reduction: {sizeReduction:F1}%\n");
                }

                // Display sample results
                Console.WriteLine("Sample results with minimal fields:");
                for (int i = 0; i < Math.Min(minimalResult.Documents.Count, 3); i++)
                {
                    var hotel = minimalResult.Documents[i];
                    Console.WriteLine($"  {i + 1}. {hotel.HotelName} (Rating: {hotel.Rating}, ID: {hotel.HotelId})");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Basic field selection demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates context-based field selection
        /// </summary>
        public async Task DemonstrateContextBasedSelectionAsync()
        {
            Console.WriteLine("\n=== Context-Based Field Selection Demo ===\n");

            var fieldSelector = new FieldSelector<Hotel>(_searchClient);

            try
            {
                var contexts = new[] { "list_view", "search_results", "map_view", "comparison" };

                foreach (var context in contexts)
                {
                    Console.WriteLine($"{context.ToUpper().Replace("_", " ")} Context:");
                    var result = await fieldSelector.SearchWithContextAsync("*", context);

                    Console.WriteLine($"  Duration: {result.DurationMs:F1}ms");
                    Console.WriteLine($"  Response size: ~{result.ResponseSizeBytes} bytes");
                    Console.WriteLine($"  Fields: {string.Join(", ", result.FieldsReturned)}");

                    // Show sample result
                    if (result.Documents.Any())
                    {
                        var hotel = result.Documents.First();
                        var sampleData = $"Sample: {hotel.HotelName}";
                        if (hotel.Rating.HasValue) sampleData += $", Rating: {hotel.Rating}";
                        if (!string.IsNullOrEmpty(hotel.Category)) sampleData += $", Category: {hotel.Category}";
                        Console.WriteLine($"  {sampleData}");
                    }
                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Context-based selection demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates performance comparison between different field selections
        /// </summary>
        public async Task DemonstratePerformanceComparisonAsync()
        {
            Console.WriteLine("=== Performance Comparison Demo ===\n");

            var fieldSelector = new FieldSelector<Hotel>(_searchClient);

            try
            {
                var fieldSets = new List<(string Name, List<string> Fields)>
                {
                    ("All Fields", new List<string>()),  // Empty list means all fields
                    ("Essential Only", new List<string> { "hotelId", "hotelName", "rating" }),
                    ("Search Results", new List<string> { "hotelId", "hotelName", "description", "rating", "category" }),
                    ("Detail View", new List<string> { "hotelId", "hotelName", "description", "category", "rating", 
                        "location", "tags", "parkingIncluded" })
                };

                Console.WriteLine("Comparing field selection performance:");
                var comparisons = await fieldSelector.CompareFieldSelectionsAsync("luxury", fieldSets);

                Console.WriteLine("\nComparison Summary:");
                foreach (var comp in comparisons)
                {
                    if (comp.ContainsKey("error"))
                    {
                        Console.WriteLine($"{comp["name"]}: ERROR - {comp["error"]}");
                    }
                    else
                    {
                        Console.WriteLine($"{comp["name"]}: {comp["durationMs"]:F1}ms, " +
                            $"~{comp["responseSizeBytes"]} bytes, " +
                            $"{comp["documentCount"]} results");
                    }
                }

                // Find the most efficient option
                var validComparisons = comparisons.Where(c => !c.ContainsKey("error")).ToList();
                if (validComparisons.Any())
                {
                    var fastest = validComparisons.OrderBy(c => (double)c["durationMs"]).First();
                    var smallest = validComparisons.OrderBy(c => (int)c["responseSizeBytes"]).First();

                    Console.WriteLine($"\nFastest: {fastest["name"]} ({fastest["durationMs"]:F1}ms)");
                    Console.WriteLine($"Smallest: {smallest["name"]} (~{smallest["responseSizeBytes"]} bytes)");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Performance comparison demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates field validation functionality
        /// </summary>
        public async Task DemonstrateFieldValidationAsync()
        {
            Console.WriteLine("\n=== Field Validation Demo ===\n");

            var fieldSelector = new FieldSelector<Hotel>(_searchClient);

            try
            {
                // Test valid fields
                Console.WriteLine("1. Testing valid fields:");
                var validFields = new List<string> { "hotelId", "hotelName", "rating" };
                var validation = fieldSelector.ValidateFields(validFields);
                Console.WriteLine($"✅ Valid fields: {string.Join(", ", validFields)}");
                Console.WriteLine($"Validation result: {validation["validationMessage"]}");

                // Test invalid fields
                Console.WriteLine("\n2. Testing invalid fields:");
                var invalidFields = new List<string> { "hotelId", "nonExistentField", "anotherBadField" };
                validation = fieldSelector.ValidateFields(invalidFields);
                Console.WriteLine($"❌ Test fields: {string.Join(", ", invalidFields)}");
                Console.WriteLine($"Validation result: {validation["validationMessage"]}");

                // Show valid fields from validation
                var validFromValidation = (List<string>)validation["validFields"];
                Console.WriteLine($"Valid fields found: {string.Join(", ", validFromValidation)}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Field validation demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates pagination combined with field selection
        /// </summary>
        public async Task DemonstratePaginationWithFieldsAsync()
        {
            Console.WriteLine("\n=== Pagination with Field Selection Demo ===\n");

            var fieldSelector = new FieldSelector<Hotel>(_searchClient);

            try
            {
                var fields = new List<string> { "hotelId", "hotelName", "rating", "category" };

                // Load multiple pages with field selection
                for (int page = 0; page < 3; page++)
                {
                    Console.WriteLine($"Page {page + 1}:");

                    var options = new SearchOptions
                    {
                        Skip = page * 5,
                        Size = 5,
                        IncludeTotalCount = page == 0  // Only get count on first page
                    };

                    var result = await fieldSelector.SearchWithFieldsAsync("*", fields, options: options);

                    Console.WriteLine($"  Duration: {result.DurationMs:F1}ms");
                    Console.WriteLine($"  Results: {result.DocumentCount}");

                    // Show results
                    for (int i = 0; i < result.Documents.Count; i++)
                    {
                        var hotel = result.Documents[i];
                        Console.WriteLine($"    {i + 1}. {hotel.HotelName} ({hotel.Category}, Rating: {hotel.Rating})");
                    }

                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Pagination with fields demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates advanced field optimization techniques
        /// </summary>
        public async Task DemonstrateFieldOptimizationAsync()
        {
            Console.WriteLine("\n=== Field Optimization Demo ===\n");

            var fieldSelector = new FieldSelector<Hotel>(_searchClient);
            var optimizer = new FieldSelectionOptimizer<Hotel>(fieldSelector);

            try
            {
                // Find optimal fields
                Console.WriteLine("1. Finding optimal field selection:");
                var optimalFields = await optimizer.FindOptimalFieldsAsync("luxury", maxFields: 8);
                Console.WriteLine($"Optimal fields: {string.Join(", ", optimalFields)}");

                // Test optimal selection
                var result = await fieldSelector.SearchWithFieldsAsync("luxury", optimalFields);
                Console.WriteLine($"Performance: {result.DurationMs:F1}ms, ~{result.ResponseSizeBytes} bytes");

                // Analyze field usage patterns
                Console.WriteLine("\n2. Analyzing field usage patterns:");
                var testQueries = new List<string> { "luxury", "beach", "city", "spa" };
                var analysis = await optimizer.AnalyzeFieldUsageAsync(testQueries);

                Console.WriteLine($"Analyzed {analysis["queriesAnalyzed"]} queries");
                Console.WriteLine("Performance by preset:");

                var fieldPerformance = (Dictionary<string, Dictionary<string, object>>)analysis["fieldPerformance"];
                foreach (var (preset, perf) in fieldPerformance)
                {
                    var queryCount = (int)perf["queryCount"];
                    if (queryCount > 0)
                    {
                        var avgDuration = (double)perf["avgDuration"];
                        var avgSize = (int)perf["avgSize"];
                        Console.WriteLine($"  {preset}: {avgDuration:F1}ms avg, ~{avgSize} bytes avg");
                    }
                }

                Console.WriteLine("\nRecommendations:");
                var recommendations = (List<string>)analysis["recommendations"];
                foreach (var rec in recommendations)
                {
                    Console.WriteLine($"  • {rec}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Field optimization demo error: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Utility class for common field selection patterns
    /// </summary>
    public static class FieldSelectionHelper
    {
        public static List<string> ForMobile() => new List<string> { "hotelId", "hotelName", "rating" };
        
        public static List<string> ForDesktop() => new List<string> { "hotelId", "hotelName", "description", "rating", "category" };
        
        public static List<string> ForApi() => new List<string> { "hotelId", "hotelName", "description", "rating", "category", "location" };
        
        public static List<string> ForExport() => new List<string> 
        { 
            "hotelId", "hotelName", "description", "category", "rating", 
            "address", "tags", "parkingIncluded", "smokingAllowed" 
        };
        
        public static List<string> Custom(params string[] fields) => fields.ToList();
    }

    /// <summary>
    /// Program entry point for demonstration
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            try
            {
                // Configuration
                var configuration = new ConfigurationBuilder()
                    .AddJsonFile("appsettings.json", optional: true)
                    .AddEnvironmentVariables()
                    .Build();

                var serviceName = configuration["AzureSearch:ServiceName"] ?? 
                                Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_NAME");
                var indexName = configuration["AzureSearch:IndexName"] ?? 
                              Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX_NAME") ?? 
                              "hotels-sample";
                var apiKey = configuration["AzureSearch:ApiKey"] ?? 
                           Environment.GetEnvironmentVariable("AZURE_SEARCH_API_KEY");

                if (string.IsNullOrEmpty(serviceName) || string.IsNullOrEmpty(apiKey))
                {
                    Console.WriteLine("Please configure Azure Search service name and API key");
                    return;
                }

                // Initialize search client
                var endpoint = new Uri($"https://{serviceName}.search.windows.net");
                var credential = new AzureKeyCredential(apiKey);
                var searchClient = new SearchClient(endpoint, indexName, credential);

                // Run demonstrations
                var demo = new FieldSelectionDemo(searchClient);
                await demo.DemonstrateBasicFieldSelectionAsync();
                await demo.DemonstrateContextBasedSelectionAsync();
                await demo.DemonstratePerformanceComparisonAsync();
                await demo.DemonstrateFieldValidationAsync();
                await demo.DemonstratePaginationWithFieldsAsync();
                await demo.DemonstrateFieldOptimizationAsync();

                // Show helper usage
                Console.WriteLine("\n=== Field Selection Helper Demo ===\n");
                Console.WriteLine("Helper examples:");
                Console.WriteLine($"Mobile: {string.Join(", ", FieldSelectionHelper.ForMobile())}");
                Console.WriteLine($"Desktop: {string.Join(", ", FieldSelectionHelper.ForDesktop())}");
                Console.WriteLine($"API: {string.Join(", ", FieldSelectionHelper.ForApi())}");
                Console.WriteLine($"Custom: {string.Join(", ", FieldSelectionHelper.Custom("hotelId", "hotelName", "specialField"))}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Demo failed: {ex.Message}");
            }
        }
    }
}