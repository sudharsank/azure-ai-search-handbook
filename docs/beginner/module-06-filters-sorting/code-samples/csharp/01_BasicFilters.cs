/*
 * Basic Filters Example
 * 
 * This example demonstrates fundamental filtering operations in Azure AI Search,
 * including equality filters, comparison filters, and logical combinations.
 */

using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;

namespace AzureSearchFiltersExamples
{
    public class BasicFiltersExample
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public BasicFiltersExample()
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

        public async Task DemonstrateEqualityFiltersAsync()
        {
            Console.WriteLine("\n🔍 Equality Filters");
            Console.WriteLine("=".PadRight(40, '='));

            var filterExamples = new[]
            {
                new
                {
                    Name = "Category equals Electronics",
                    Filter = "category eq 'Electronics'",
                    Description = "Find all products in Electronics category"
                },
                new
                {
                    Name = "Status not discontinued",
                    Filter = "status ne 'Discontinued'",
                    Description = "Find products that are not discontinued"
                },
                new
                {
                    Name = "In stock items",
                    Filter = "inStock eq true",
                    Description = "Find items that are currently in stock"
                },
                new
                {
                    Name = "Out of stock items",
                    Filter = "inStock eq false",
                    Description = "Find items that are out of stock"
                }
            };

            foreach (var example in filterExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("category");
                    searchOptions.Select.Add("status");
                    searchOptions.Select.Add("inStock");
                    searchOptions.Select.Add("price");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    Console.WriteLine($"   Results: {resultList.Count} items found");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                        var status = doc.TryGetValue("status", out var statusValue) ? statusValue?.ToString() : "N/A";
                        var inStock = doc.TryGetValue("inStock", out var inStockValue) ? inStockValue?.ToString() : "N/A";
                        var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {status} - Stock: {inStock}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateComparisonFiltersAsync()
        {
            Console.WriteLine("\n📊 Comparison Filters");
            Console.WriteLine("=".PadRight(40, '='));

            var comparisonExamples = new[]
            {
                new
                {
                    Name = "Price greater than $100",
                    Filter = "price gt 100",
                    Description = "Find products priced above $100",
                    OrderBy = "price asc"
                },
                new
                {
                    Name = "Rating 4.0 or higher",
                    Filter = "rating ge 4.0",
                    Description = "Find highly rated products (4+ stars)",
                    OrderBy = "rating desc"
                },
                new
                {
                    Name = "Price less than $50",
                    Filter = "price lt 50",
                    Description = "Find budget-friendly products under $50",
                    OrderBy = "price asc"
                },
                new
                {
                    Name = "Rating 3.0 or lower",
                    Filter = "rating le 3.0",
                    Description = "Find lower-rated products (3 stars or less)",
                    OrderBy = "rating desc"
                }
            };

            foreach (var example in comparisonExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("price");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("category");
                    searchOptions.OrderBy.Add(example.OrderBy);

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    Console.WriteLine($"   Results: {resultList.Count} items found");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {rating}⭐");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateLogicalCombinationsAsync()
        {
            Console.WriteLine("\n🔗 Logical Combinations");
            Console.WriteLine("=".PadRight(40, '='));

            var logicalExamples = new[]
            {
                new
                {
                    Name = "Electronics AND high rating",
                    Filter = "category eq 'Electronics' and rating ge 4.0",
                    Description = "Find high-rated electronics products"
                },
                new
                {
                    Name = "Budget OR Premium categories",
                    Filter = "category eq 'Budget' or category eq 'Premium'",
                    Description = "Find products in Budget or Premium categories"
                },
                new
                {
                    Name = "NOT discontinued items",
                    Filter = "not (status eq 'Discontinued')",
                    Description = "Find all non-discontinued products"
                },
                new
                {
                    Name = "Complex combination",
                    Filter = "(category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.5)",
                    Description = "Find expensive electronics OR highly-rated books"
                }
            };

            foreach (var example in logicalExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("category");
                    searchOptions.Select.Add("price");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("status");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    Console.WriteLine($"   Results: {resultList.Count} items found");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                        var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                        var status = doc.TryGetValue("status", out var statusValue) ? statusValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {rating}⭐ - {status}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateNullHandlingAsync()
        {
            Console.WriteLine("\n🚫 Null Value Handling");
            Console.WriteLine("=".PadRight(40, '='));

            var nullExamples = new[]
            {
                new
                {
                    Name = "Items with rating",
                    Filter = "rating ne null",
                    Description = "Find items that have a rating value"
                },
                new
                {
                    Name = "Items without description",
                    Filter = "description eq null",
                    Description = "Find items missing description"
                },
                new
                {
                    Name = "Items with non-zero price",
                    Filter = "price ne null and price gt 0",
                    Description = "Find items with valid pricing"
                }
            };

            foreach (var example in nullExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("price");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("description");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    Console.WriteLine($"   Results: {resultList.Count} items found");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                        var hasDesc = doc.TryGetValue("description", out var descValue) && descValue != null ? "Yes" : "No";

                        Console.WriteLine($"     {i + 1}. {name} - ${price} - {rating}⭐ - Desc: {hasDesc}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateFilterBuildingAsync()
        {
            Console.WriteLine("\n🔧 Dynamic Filter Building");
            Console.WriteLine("=".PadRight(40, '='));

            // Test different filter combinations
            var filterScenarios = new[]
            {
                new
                {
                    Name = "Electronics under $200",
                    Category = "Electronics",
                    MaxPrice = (decimal?)200,
                    MinPrice = (decimal?)null,
                    MinRating = (double?)null,
                    InStock = (bool?)null
                },
                new
                {
                    Name = "High-rated items in stock",
                    Category = (string)null,
                    MaxPrice = (decimal?)null,
                    MinPrice = (decimal?)null,
                    MinRating = (double?)4.0,
                    InStock = (bool?)true
                },
                new
                {
                    Name = "Budget items ($10-$50)",
                    Category = (string)null,
                    MaxPrice = (decimal?)50,
                    MinPrice = (decimal?)10,
                    MinRating = (double?)null,
                    InStock = (bool?)null
                },
                new
                {
                    Name = "Premium electronics in stock",
                    Category = "Electronics",
                    MaxPrice = (decimal?)null,
                    MinPrice = (decimal?)500,
                    MinRating = (double?)null,
                    InStock = (bool?)true
                }
            };

            foreach (var scenario in filterScenarios)
            {
                Console.WriteLine($"\n📋 {scenario.Name}");
                var filterExpr = FilterBuilder.BuildProductFilter(
                    scenario.Category, scenario.MinPrice, scenario.MaxPrice, 
                    scenario.MinRating, scenario.InStock);
                
                Console.WriteLine($"   Generated Filter: {filterExpr ?? "null"}");
                Console.WriteLine($"   Parameters: Category={scenario.Category}, MinPrice={scenario.MinPrice}, MaxPrice={scenario.MaxPrice}, MinRating={scenario.MinRating}, InStock={scenario.InStock}");

                if (!string.IsNullOrEmpty(filterExpr))
                {
                    try
                    {
                        var searchOptions = new SearchOptions
                        {
                            Filter = filterExpr,
                            Size = 2
                        };
                        searchOptions.Select.Add("id");
                        searchOptions.Select.Add("name");
                        searchOptions.Select.Add("category");
                        searchOptions.Select.Add("price");
                        searchOptions.Select.Add("rating");
                        searchOptions.Select.Add("inStock");

                        var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                        var resultList = new List<SearchResult<SearchDocument>>();

                        await foreach (var result in results.Value.GetResultsAsync())
                        {
                            resultList.Add(result);
                        }

                        Console.WriteLine($"   Results: {resultList.Count} items found");

                        for (int i = 0; i < resultList.Count; i++)
                        {
                            var doc = resultList[i].Document;
                            var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                            var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                            var price = doc.TryGetValue("price", out var priceValue) ? priceValue?.ToString() : "N/A";
                            var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                            var inStock = doc.TryGetValue("inStock", out var inStockValue) ? inStockValue?.ToString() : "N/A";

                            Console.WriteLine($"     {i + 1}. {name} ({category}) - ${price} - {rating}⭐ - Stock: {inStock}");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"   ❌ Error: {ex.Message}");
                    }
                }
            }
        }

        public void DemonstrateBestPractices()
        {
            Console.WriteLine("\n💡 Filter Best Practices");
            Console.WriteLine("=".PadRight(40, '='));

            Console.WriteLine("\n1. Use specific filters first (most selective)");
            Console.WriteLine("   ✅ Good: category eq 'Electronics' and price gt 1000");
            Console.WriteLine("   ❌ Avoid: price gt 0 and category eq 'Electronics'");

            Console.WriteLine("\n2. Use appropriate data types");
            Console.WriteLine("   ✅ Good: price gt 100 (numeric)");
            Console.WriteLine("   ❌ Avoid: price gt '100' (string)");

            Console.WriteLine("\n3. Handle null values explicitly");
            Console.WriteLine("   ✅ Good: rating ne null and rating ge 4.0");
            Console.WriteLine("   ❌ Risky: rating ge 4.0 (may include nulls)");

            Console.WriteLine("\n4. Use parentheses for complex logic");
            Console.WriteLine("   ✅ Good: (category eq 'A' and price gt 100) or (category eq 'B' and rating ge 4.0)");
            Console.WriteLine("   ❌ Confusing: category eq 'A' and price gt 100 or category eq 'B' and rating ge 4.0");

            Console.WriteLine("\n5. Validate filter expressions");

            var testFilters = new[]
            {
                "category eq 'Electronics'",  // Valid
                "category eq 'Electronics",   // Invalid - missing quote
                "(price gt 100 and rating ge 4.0",  // Invalid - unbalanced parentheses
                "price gt 100 and rating ge 4.0"    // Valid
            };

            Console.WriteLine("\n   Filter Validation Examples:");
            foreach (var filterExpr in testFilters)
            {
                var (isValid, message) = FilterValidator.ValidateFilter(filterExpr);
                var status = isValid ? "✅" : "❌";
                Console.WriteLine($"   {status} '{filterExpr}' - {message}");
            }
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Basic Filters Example");
            Console.WriteLine("=".PadRight(50, '='));

            try
            {
                await DemonstrateEqualityFiltersAsync();
                await DemonstrateComparisonFiltersAsync();
                await DemonstrateLogicalCombinationsAsync();
                await DemonstrateNullHandlingAsync();
                await DemonstrateFilterBuildingAsync();
                DemonstrateBestPractices();

                Console.WriteLine("\n✅ Basic filters example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Use equality (eq/ne) and comparison (gt/ge/lt/le) operators");
                Console.WriteLine("- Combine filters with logical operators (and/or/not)");
                Console.WriteLine("- Handle null values explicitly in your filters");
                Console.WriteLine("- Build filters dynamically based on user input");
                Console.WriteLine("- Validate filter syntax before executing queries");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }
    }

    public static class FilterBuilder
    {
        public static string BuildProductFilter(string category = null, 
            decimal? minPrice = null, decimal? maxPrice = null, 
            double? minRating = null, bool? inStock = null)
        {
            var filters = new List<string>();

            if (!string.IsNullOrEmpty(category))
                filters.Add($"category eq '{EscapeODataString(category)}'");

            if (minPrice.HasValue)
                filters.Add($"price ge {minPrice.Value}");

            if (maxPrice.HasValue)
                filters.Add($"price le {maxPrice.Value}");

            if (minRating.HasValue)
                filters.Add($"rating ge {minRating.Value}");

            if (inStock.HasValue)
                filters.Add($"inStock eq {inStock.Value.ToString().ToLower()}");

            return filters.Count > 0 ? string.Join(" and ", filters) : null;
        }

        private static string EscapeODataString(string value)
        {
            return value?.Replace("'", "''");
        }
    }

    public static class FilterValidator
    {
        public static (bool IsValid, string Message) ValidateFilter(string filterExpression)
        {
            try
            {
                if (string.IsNullOrEmpty(filterExpression))
                    return (true, "Empty filter is valid");

                // Check for balanced quotes
                var singleQuotes = filterExpression.Count(c => c == '\'');
                if (singleQuotes % 2 != 0)
                    return (false, "Unbalanced single quotes");

                // Check for balanced parentheses
                var openParens = filterExpression.Count(c => c == '(');
                var closeParens = filterExpression.Count(c => c == ')');
                if (openParens != closeParens)
                    return (false, "Unbalanced parentheses");

                return (true, "Filter appears valid");
            }
            catch (Exception ex)
            {
                return (false, $"Validation error: {ex.Message}");
            }
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var example = new BasicFiltersExample();
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