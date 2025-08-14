/*
 * Range Filters Example
 * 
 * This example demonstrates range filtering operations in Azure AI Search,
 * including numeric ranges, date ranges, and performance optimization techniques.
 */

using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;

namespace AzureSearchFiltersExamples
{
    public class RangeFiltersExample
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public RangeFiltersExample()
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

        public async Task DemonstrateNumericRangesAsync()
        {
            Console.WriteLine("\n💰 Numeric Range Filters");
            Console.WriteLine("=".PadRight(40, '='));

            var numericExamples = new[]
            {
                new
                {
                    Name = "Budget items ($10 - $50)",
                    Filter = "price ge 10 and price le 50",
                    Description = "Find affordable products in budget range",
                    OrderBy = "price asc"
                },
                new
                {
                    Name = "Mid-range items ($50 - $200)",
                    Filter = "price gt 50 and price lt 200",
                    Description = "Find mid-range products",
                    OrderBy = "price asc"
                },
                new
                {
                    Name = "Premium items ($500+)",
                    Filter = "price ge 500",
                    Description = "Find premium high-end products",
                    OrderBy = "price desc"
                },
                new
                {
                    Name = "High-rated items (4+ stars)",
                    Filter = "rating ge 4.0 and rating le 5.0",
                    Description = "Find highly rated products",
                    OrderBy = "rating desc"
                },
                new
                {
                    Name = "Quantity in stock (10-100)",
                    Filter = "quantity ge 10 and quantity le 100",
                    Description = "Find items with moderate stock levels",
                    OrderBy = "quantity desc"
                }
            };

            foreach (var example in numericExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("price");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("quantity");
                    searchOptions.Select.Add("category");
                    searchOptions.OrderBy.Add(example.OrderBy);

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                        var quantity = doc.TryGetValue("quantity", out var quantityValue) ? quantityValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {rating}⭐ - Qty: {quantity}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateDateRangesAsync()
        {
            Console.WriteLine("\n📅 Date Range Filters");
            Console.WriteLine("=".PadRight(40, '='));

            var now = DateTime.UtcNow;
            var lastWeek = now.AddDays(-7);
            var lastMonth = now.AddDays(-30);
            var lastYear = now.AddYears(-1);

            var dateExamples = new[]
            {
                new
                {
                    Name = "Items added last week",
                    Filter = $"createdDate ge {lastWeek:yyyy-MM-ddTHH:mm:ssZ}",
                    Description = "Find recently added items (last 7 days)",
                    OrderBy = "createdDate desc"
                },
                new
                {
                    Name = "Items added last month",
                    Filter = $"createdDate ge {lastMonth:yyyy-MM-ddTHH:mm:ssZ} and createdDate lt {lastWeek:yyyy-MM-ddTHH:mm:ssZ}",
                    Description = "Find items added 7-30 days ago",
                    OrderBy = "createdDate desc"
                },
                new
                {
                    Name = "Items modified this year",
                    Filter = $"lastModified ge {new DateTime(now.Year, 1, 1):yyyy-MM-ddTHH:mm:ssZ}",
                    Description = "Find items modified in current year",
                    OrderBy = "lastModified desc"
                },
                new
                {
                    Name = "Older items (1+ year)",
                    Filter = $"createdDate lt {lastYear:yyyy-MM-ddTHH:mm:ssZ}",
                    Description = "Find legacy items older than 1 year",
                    OrderBy = "createdDate asc"
                }
            };

            foreach (var example in dateExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("createdDate");
                    searchOptions.Select.Add("lastModified");
                    searchOptions.Select.Add("category");
                    searchOptions.OrderBy.Add(example.OrderBy);

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var created = doc.TryGetValue("createdDate", out var createdValue) ? 
                            DateTime.Parse(createdValue.ToString()).ToString("yyyy-MM-dd") : "N/A";
                        var modified = doc.TryGetValue("lastModified", out var modifiedValue) ? 
                            DateTime.Parse(modifiedValue.ToString()).ToString("yyyy-MM-dd") : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - Created: {created} - Modified: {modified}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateAdvancedRangesAsync()
        {
            Console.WriteLine("\n🎯 Advanced Range Combinations");
            Console.WriteLine("=".PadRight(40, '='));

            var advancedExamples = new[]
            {
                new
                {
                    Name = "Sweet spot products",
                    Filter = "price ge 50 and price le 150 and rating ge 4.0",
                    Description = "Find well-priced, highly-rated products",
                    OrderBy = "rating desc"
                },
                new
                {
                    Name = "Clearance candidates",
                    Filter = "quantity ge 1 and quantity le 5 and price ge 100",
                    Description = "Find expensive items with low stock",
                    OrderBy = "quantity asc"
                },
                new
                {
                    Name = "Popular recent items",
                    Filter = $"createdDate ge {DateTime.UtcNow.AddDays(-30):yyyy-MM-ddTHH:mm:ssZ} and rating ge 4.0 and price le 200",
                    Description = "Find recent, popular, reasonably-priced items",
                    OrderBy = "rating desc"
                },
                new
                {
                    Name = "Inventory optimization",
                    Filter = "(quantity le 10 and price ge 200) or (quantity ge 100 and price le 50)",
                    Description = "Find items needing inventory attention",
                    OrderBy = "quantity asc"
                }
            };

            foreach (var example in advancedExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("price");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("quantity");
                    searchOptions.Select.Add("createdDate");
                    searchOptions.Select.Add("category");
                    searchOptions.OrderBy.Add(example.OrderBy);

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                        var quantity = doc.TryGetValue("quantity", out var quantityValue) ? quantityValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {rating}⭐ - Qty: {quantity}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateRangeBuilderAsync()
        {
            Console.WriteLine("\n🔧 Dynamic Range Filter Building");
            Console.WriteLine("=".PadRight(40, '='));

            var rangeScenarios = new[]
            {
                new
                {
                    Name = "Budget electronics",
                    Category = "Electronics",
                    MinPrice = 20m,
                    MaxPrice = 100m,
                    MinRating = (double?)null,
                    MaxRating = (double?)null
                },
                new
                {
                    Name = "High-end items",
                    Category = (string)null,
                    MinPrice = 500m,
                    MaxPrice = (decimal?)null,
                    MinRating = 4.0,
                    MaxRating = (double?)null
                },
                new
                {
                    Name = "Mid-range books",
                    Category = "Books",
                    MinPrice = 15m,
                    MaxPrice = 50m,
                    MinRating = 3.5,
                    MaxRating = 5.0
                },
                new
                {
                    Name = "Recent premium items",
                    Category = (string)null,
                    MinPrice = 200m,
                    MaxPrice = (decimal?)null,
                    MinRating = 4.5,
                    MaxRating = (double?)null,
                    MinDate = DateTime.UtcNow.AddDays(-60)
                }
            };

            foreach (var scenario in rangeScenarios)
            {
                Console.WriteLine($"\n📋 {scenario.Name}");
                
                var filterExpr = RangeFilterBuilder.BuildRangeFilter(
                    category: scenario.Category,
                    minPrice: scenario.MinPrice,
                    maxPrice: scenario.MaxPrice,
                    minRating: scenario.MinRating,
                    maxRating: scenario.MaxRating,
                    minDate: scenario.MinDate
                );
                
                Console.WriteLine($"   Generated Filter: {filterExpr ?? "null"}");

                if (!string.IsNullOrEmpty(filterExpr))
                {
                    try
                    {
                        var stopwatch = Stopwatch.StartNew();
                        
                        var searchOptions = new SearchOptions
                        {
                            Filter = filterExpr,
                            Size = 2,
                            IncludeTotalCount = true
                        };
                        searchOptions.Select.Add("id");
                        searchOptions.Select.Add("name");
                        searchOptions.Select.Add("category");
                        searchOptions.Select.Add("price");
                        searchOptions.Select.Add("rating");
                        searchOptions.Select.Add("createdDate");

                        var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                        var resultList = new List<SearchResult<SearchDocument>>();

                        await foreach (var result in results.Value.GetResultsAsync())
                        {
                            resultList.Add(result);
                        }

                        stopwatch.Stop();
                        var totalCount = results.Value.TotalCount ?? resultList.Count;

                        Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");

                        for (int i = 0; i < resultList.Count; i++)
                        {
                            var doc = resultList[i].Document;
                            var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                            var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                            var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                            var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";

                            Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {rating}⭐");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"   ❌ Error: {ex.Message}");
                    }
                }
            }
        }

        public void DemonstratePerformanceOptimization()
        {
            Console.WriteLine("\n⚡ Range Filter Performance Tips");
            Console.WriteLine("=".PadRight(40, '='));

            Console.WriteLine("\n1. Use inclusive ranges when possible");
            Console.WriteLine("   ✅ Good: price ge 100 and price le 500");
            Console.WriteLine("   ❌ Slower: price gt 99.99 and price lt 500.01");

            Console.WriteLine("\n2. Order range conditions by selectivity");
            Console.WriteLine("   ✅ Good: category eq 'Electronics' and price ge 100");
            Console.WriteLine("   ❌ Less optimal: price ge 100 and category eq 'Electronics'");

            Console.WriteLine("\n3. Use appropriate date formats");
            Console.WriteLine("   ✅ Good: createdDate ge 2024-01-01T00:00:00Z");
            Console.WriteLine("   ❌ Avoid: createdDate ge '2024-01-01'");

            Console.WriteLine("\n4. Combine related ranges");
            Console.WriteLine("   ✅ Good: price ge 100 and price le 500");
            Console.WriteLine("   ❌ Redundant: price ge 100 and price gt 50 and price le 500");

            Console.WriteLine("\n5. Consider index design for range queries");
            Console.WriteLine("   • Mark numeric fields as filterable and sortable");
            Console.WriteLine("   • Use appropriate data types (Edm.Double, Edm.DateTimeOffset)");
            Console.WriteLine("   • Consider field ordering in composite indexes");

            // Performance comparison example
            Console.WriteLine("\n📊 Performance Comparison Example:");
            var performanceTests = new[]
            {
                new { Name = "Simple range", Filter = "price ge 100", Complexity = "Low" },
                new { Name = "Double range", Filter = "price ge 100 and price le 500", Complexity = "Low" },
                new { Name = "Multi-field range", Filter = "price ge 100 and rating ge 4.0", Complexity = "Medium" },
                new { Name = "Complex range", Filter = "(price ge 100 and price le 200) or (price ge 500 and rating ge 4.5)", Complexity = "High" }
            };

            foreach (var test in performanceTests)
            {
                Console.WriteLine($"   {test.Name}: {test.Filter} - Complexity: {test.Complexity}");
            }
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Range Filters Example");
            Console.WriteLine("=".PadRight(50, '='));

            try
            {
                await DemonstrateNumericRangesAsync();
                await DemonstrateDateRangesAsync();
                await DemonstrateAdvancedRangesAsync();
                await DemonstrateRangeBuilderAsync();
                DemonstratePerformanceOptimization();

                Console.WriteLine("\n✅ Range filters example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Use ge/le for inclusive ranges, gt/lt for exclusive ranges");
                Console.WriteLine("- Combine multiple range conditions with logical operators");
                Console.WriteLine("- Format dates properly for date range filtering");
                Console.WriteLine("- Build dynamic range filters based on user input");
                Console.WriteLine("- Optimize range queries for better performance");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }
    }

    public static class RangeFilterBuilder
    {
        public static string BuildRangeFilter(string category = null,
            decimal? minPrice = null, decimal? maxPrice = null,
            double? minRating = null, double? maxRating = null,
            DateTime? minDate = null, DateTime? maxDate = null,
            int? minQuantity = null, int? maxQuantity = null)
        {
            var filters = new List<string>();

            // Category filter
            if (!string.IsNullOrEmpty(category))
                filters.Add($"category eq '{EscapeODataString(category)}'");

            // Price range
            if (minPrice.HasValue)
                filters.Add($"price ge {minPrice.Value}");
            if (maxPrice.HasValue)
                filters.Add($"price le {maxPrice.Value}");

            // Rating range
            if (minRating.HasValue)
                filters.Add($"rating ge {minRating.Value}");
            if (maxRating.HasValue)
                filters.Add($"rating le {maxRating.Value}");

            // Date range
            if (minDate.HasValue)
                filters.Add($"createdDate ge {minDate.Value:yyyy-MM-ddTHH:mm:ssZ}");
            if (maxDate.HasValue)
                filters.Add($"createdDate le {maxDate.Value:yyyy-MM-ddTHH:mm:ssZ}");

            // Quantity range
            if (minQuantity.HasValue)
                filters.Add($"quantity ge {minQuantity.Value}");
            if (maxQuantity.HasValue)
                filters.Add($"quantity le {maxQuantity.Value}");

            return filters.Count > 0 ? string.Join(" and ", filters) : null;
        }

        public static string BuildDateRangeFilter(DateTime? startDate, DateTime? endDate, string dateField = "createdDate")
        {
            var filters = new List<string>();

            if (startDate.HasValue)
                filters.Add($"{dateField} ge {startDate.Value:yyyy-MM-ddTHH:mm:ssZ}");
            
            if (endDate.HasValue)
                filters.Add($"{dateField} le {endDate.Value:yyyy-MM-ddTHH:mm:ssZ}");

            return filters.Count > 0 ? string.Join(" and ", filters) : null;
        }

        public static string BuildNumericRangeFilter(decimal? min, decimal? max, string field)
        {
            var filters = new List<string>();

            if (min.HasValue)
                filters.Add($"{field} ge {min.Value}");
            
            if (max.HasValue)
                filters.Add($"{field} le {max.Value}");

            return filters.Count > 0 ? string.Join(" and ", filters) : null;
        }

        private static string EscapeODataString(string value)
        {
            return value?.Replace("'", "''");
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var example = new RangeFiltersExample();
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