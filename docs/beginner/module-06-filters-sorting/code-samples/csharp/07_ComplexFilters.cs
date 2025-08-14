/*
 * Complex Filters Example
 * 
 * This example demonstrates advanced filtering operations in Azure AI Search,
 * including collection filtering, nested conditions, and complex logical combinations.
 */

using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;
using System.Text.RegularExpressions;

namespace AzureSearchFiltersExamples
{
    public class ComplexFiltersExample
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public ComplexFiltersExample()
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

        public async Task DemonstrateCollectionFiltersAsync()
        {
            Console.WriteLine("\n📚 Collection Filters (any/all)");
            Console.WriteLine("=".PadRight(40, '='));

            var collectionExamples = new[]
            {
                new
                {
                    Name = "Items with 'premium' tag",
                    Filter = "tags/any(tag: tag eq 'premium')",
                    Description = "Find items that have the 'premium' tag"
                },
                new
                {
                    Name = "Items with parking amenity",
                    Filter = "amenities/any(amenity: amenity eq 'parking')",
                    Description = "Find locations that offer parking"
                },
                new
                {
                    Name = "Items with all required features",
                    Filter = "features/all(feature: feature eq 'available')",
                    Description = "Find items where all features are available"
                },
                new
                {
                    Name = "Items with WiFi or Pool",
                    Filter = "amenities/any(amenity: amenity eq 'wifi' or amenity eq 'pool')",
                    Description = "Find locations with WiFi or Pool amenities"
                },
                new
                {
                    Name = "Items with specific categories",
                    Filter = "categories/any(category: contains(category, 'electronics'))",
                    Description = "Find items in electronics-related categories"
                }
            };

            foreach (var example in collectionExamples)
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
                    searchOptions.Select.Add("tags");
                    searchOptions.Select.Add("amenities");
                    searchOptions.Select.Add("features");
                    searchOptions.Select.Add("categories");
                    searchOptions.Select.Add("rating");

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
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";
                        var tags = doc.TryGetValue("tags", out var tagsValue) ? 
                            string.Join(", ", ((object[])tagsValue).Take(3)) : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} - {rating}⭐ - Tags: {tags}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateNestedConditionsAsync()
        {
            Console.WriteLine("\n🔗 Nested Logical Conditions");
            Console.WriteLine("=".PadRight(40, '='));

            var nestedExamples = new[]
            {
                new
                {
                    Name = "Premium electronics or high-rated books",
                    Filter = "(category eq 'Electronics' and tags/any(tag: tag eq 'premium')) or (category eq 'Books' and rating ge 4.5)",
                    Description = "Find premium electronics OR highly-rated books"
                },
                new
                {
                    Name = "Available items with amenities",
                    Filter = "inStock eq true and (amenities/any(amenity: amenity eq 'wifi') or amenities/any(amenity: amenity eq 'parking'))",
                    Description = "Find in-stock items with WiFi or parking"
                },
                new
                {
                    Name = "Budget or premium with conditions",
                    Filter = "(price le 50 and rating ge 3.0) or (price ge 500 and tags/any(tag: tag eq 'luxury'))",
                    Description = "Find budget items with good rating OR luxury premium items"
                },
                new
                {
                    Name = "Multi-category with features",
                    Filter = "(categories/any(cat: cat eq 'electronics') or categories/any(cat: cat eq 'appliances')) and features/all(feature: feature ne 'discontinued')",
                    Description = "Find electronics/appliances with no discontinued features"
                }
            };

            foreach (var example in nestedExamples)
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
                    searchOptions.Select.Add("category");
                    searchOptions.Select.Add("price");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("tags");
                    searchOptions.Select.Add("amenities");
                    searchOptions.Select.Add("inStock");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;
                    var complexity = ComplexFilterAnalyzer.CalculateComplexity(example.Filter);

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");
                    Console.WriteLine($"   Complexity Score: {complexity}");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
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

        public async Task DemonstrateAdvancedCollectionFiltersAsync()
        {
            Console.WriteLine("\n🎯 Advanced Collection Filtering");
            Console.WriteLine("=".PadRight(40, '='));

            var advancedExamples = new[]
            {
                new
                {
                    Name = "Multiple collection conditions",
                    Filter = "tags/any(tag: tag eq 'new') and categories/any(cat: contains(cat, 'tech')) and amenities/any(amenity: amenity eq 'support')",
                    Description = "Find new tech items with support amenity"
                },
                new
                {
                    Name = "Collection with text search",
                    Filter = "tags/any(tag: contains(tag, 'special')) and (contains(name, 'pro') or contains(description, 'professional'))",
                    Description = "Find special items with 'pro' in name or description"
                },
                new
                {
                    Name = "Complex collection logic",
                    Filter = "(tags/any(tag: tag eq 'featured') or tags/any(tag: tag eq 'bestseller')) and not (tags/any(tag: tag eq 'discontinued'))",
                    Description = "Find featured/bestseller items that are not discontinued"
                },
                new
                {
                    Name = "Geographic + Collection",
                    Filter = "geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 20 and amenities/any(amenity: amenity eq 'parking')",
                    Description = "Find locations near Seattle with parking"
                }
            };

            foreach (var example in advancedExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var validation = ComplexFilterAnalyzer.ValidateFilter(example.Filter);
                    Console.WriteLine($"   Validation: {(validation.IsValid ? "✅ Valid" : "❌ Invalid")}");
                    if (!validation.IsValid)
                    {
                        Console.WriteLine($"   Issues: {string.Join(", ", validation.Issues)}");
                        continue;
                    }

                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("tags");
                    searchOptions.Select.Add("categories");
                    searchOptions.Select.Add("amenities");
                    searchOptions.Select.Add("location");
                    searchOptions.Select.Add("description");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;
                    var complexity = ComplexFilterAnalyzer.CalculateComplexity(example.Filter);

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");
                    Console.WriteLine($"   Complexity Score: {complexity}");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var tags = doc.TryGetValue("tags", out var tagsValue) ? 
                            string.Join(", ", ((object[])tagsValue).Take(2)) : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} - Tags: {tags}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateFilterOptimizationAsync()
        {
            Console.WriteLine("\n⚡ Filter Optimization Techniques");
            Console.WriteLine("=".PadRight(40, '='));

            var optimizationExamples = new[]
            {
                new
                {
                    Name = "Unoptimized Filter",
                    Filter = "price gt 0 and category eq 'Electronics' and tags/any(tag: tag eq 'premium')",
                    Description = "Less selective condition first"
                },
                new
                {
                    Name = "Optimized Filter",
                    Filter = "category eq 'Electronics' and tags/any(tag: tag eq 'premium') and price gt 0",
                    Description = "Most selective conditions first"
                },
                new
                {
                    Name = "Complex Unoptimized",
                    Filter = "rating ge 1.0 and (tags/any(tag: contains(tag, 'special')) or tags/any(tag: contains(tag, 'featured'))) and category eq 'Books'",
                    Description = "Generic condition first, complex logic"
                },
                new
                {
                    Name = "Complex Optimized",
                    Filter = "category eq 'Books' and (tags/any(tag: tag eq 'special' or tag eq 'featured')) and rating ge 4.0",
                    Description = "Specific condition first, simplified logic"
                }
            };

            var performanceResults = new List<(string Name, long ElapsedMs, int ResultCount, int Complexity)>();

            foreach (var example in optimizationExamples)
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
                        Size = 10,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;
                    var complexity = ComplexFilterAnalyzer.CalculateComplexity(example.Filter);

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");
                    Console.WriteLine($"   Complexity Score: {complexity}");

                    performanceResults.Add((example.Name, stopwatch.ElapsedMilliseconds, totalCount, complexity));
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }

            // Performance comparison
            Console.WriteLine("\n📊 Performance Comparison:");
            foreach (var result in performanceResults)
            {
                var performance = result.ElapsedMs < 100 ? "Excellent" : 
                                result.ElapsedMs < 500 ? "Good" : 
                                result.ElapsedMs < 1000 ? "Fair" : "Needs optimization";
                
                Console.WriteLine($"   {result.Name}: {result.ElapsedMs}ms - {performance}");
            }
        }

        public void DemonstrateComplexFilterBestPractices()
        {
            Console.WriteLine("\n💡 Complex Filter Best Practices");
            Console.WriteLine("=".PadRight(40, '='));

            Console.WriteLine("\n1. Use 'any()' instead of 'all()' when possible");
            Console.WriteLine("   ✅ More efficient: tags/any(tag: tag eq 'premium')");
            Console.WriteLine("   ❌ Less efficient: tags/all(tag: tag ne 'basic')");

            Console.WriteLine("\n2. Place most selective conditions first");
            Console.WriteLine("   ✅ Good: category eq 'Electronics' and price gt 100");
            Console.WriteLine("   ❌ Less optimal: price gt 0 and category eq 'Electronics'");

            Console.WriteLine("\n3. Avoid deep nesting when possible");
            Console.WriteLine("   ✅ Good: (A and B) or (C and D)");
            Console.WriteLine("   ❌ Complex: ((A and B) or (C and (D or E))) and F");

            Console.WriteLine("\n4. Combine similar collection filters");
            Console.WriteLine("   ✅ Good: tags/any(tag: tag eq 'new' or tag eq 'featured')");
            Console.WriteLine("   ❌ Redundant: tags/any(tag: tag eq 'new') or tags/any(tag: tag eq 'featured')");

            Console.WriteLine("\n5. Use parentheses for clarity");
            Console.WriteLine("   ✅ Clear: (A and B) or (C and D)");
            Console.WriteLine("   ❌ Ambiguous: A and B or C and D");

            // Filter complexity analysis
            Console.WriteLine("\n📊 Filter Complexity Analysis:");
            var testFilters = new[]
            {
                "category eq 'Electronics'",
                "tags/any(tag: tag eq 'premium')",
                "category eq 'Electronics' and tags/any(tag: tag eq 'premium')",
                "(category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.0)",
                "tags/any(tag: tag eq 'new') and categories/any(cat: contains(cat, 'tech')) and amenities/any(amenity: amenity eq 'support')"
            };

            foreach (var filter in testFilters)
            {
                var complexity = ComplexFilterAnalyzer.CalculateComplexity(filter);
                var performance = complexity <= 5 ? "Excellent" : 
                                complexity <= 10 ? "Good" : 
                                complexity <= 20 ? "Fair" : "Needs optimization";
                
                Console.WriteLine($"   Complexity {complexity}: {filter.Substring(0, Math.Min(50, filter.Length))}... - {performance}");
            }
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Complex Filters Example");
            Console.WriteLine("=".PadRight(50, '='));

            try
            {
                await DemonstrateCollectionFiltersAsync();
                await DemonstrateNestedConditionsAsync();
                await DemonstrateAdvancedCollectionFiltersAsync();
                await DemonstrateFilterOptimizationAsync();
                DemonstrateComplexFilterBestPractices();

                Console.WriteLine("\n✅ Complex filters example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Use any() and all() for collection filtering");
                Console.WriteLine("- Combine filters with logical operators for complex conditions");
                Console.WriteLine("- Place most selective conditions first for better performance");
                Console.WriteLine("- Validate complex filter syntax before execution");
                Console.WriteLine("- Monitor and optimize filter complexity for production use");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }
    }

    public static class ComplexFilterAnalyzer
    {
        public static int CalculateComplexity(string filterExpression)
        {
            if (string.IsNullOrEmpty(filterExpression))
                return 0;

            var score = 0;
            score += CountOccurrences(filterExpression, " and ") * 1;
            score += CountOccurrences(filterExpression, " or ") * 2;
            score += CountOccurrences(filterExpression, "/any(") * 3;
            score += CountOccurrences(filterExpression, "/all(") * 4;
            score += CountOccurrences(filterExpression, "geo.distance") * 3;
            score += CountOccurrences(filterExpression, "(") * 1;
            score += filterExpression.Split(' ').Length * 0.1;

            return (int)score;
        }

        public static (bool IsValid, List<string> Issues, List<string> Warnings) ValidateFilter(string filterExpression)
        {
            var issues = new List<string>();
            var warnings = new List<string>();

            try
            {
                if (string.IsNullOrEmpty(filterExpression))
                    return (true, issues, warnings);

                // Check for balanced quotes
                var singleQuotes = CountOccurrences(filterExpression, "'");
                if (singleQuotes % 2 != 0)
                    issues.Add("Unbalanced single quotes");

                // Check for balanced parentheses
                var openParens = CountOccurrences(filterExpression, "(");
                var closeParens = CountOccurrences(filterExpression, ")");
                if (openParens != closeParens)
                    issues.Add("Unbalanced parentheses");

                // Check for valid operators
                var validOperators = new[] { "eq", "ne", "gt", "ge", "lt", "le", "and", "or", "not", "any", "all" };
                var words = Regex.Split(filterExpression, @"\W+");
                
                foreach (var word in words)
                {
                    if (word.Length > 2 && !validOperators.Contains(word.ToLower()) && 
                        !word.Contains("contains") && !word.Contains("startswith") && 
                        !word.Contains("endswith") && !word.Contains("geo.distance"))
                    {
                        // This might be a field name or value, which is fine
                    }
                }

                // Performance warnings
                var complexity = CalculateComplexity(filterExpression);
                if (complexity > 20)
                    warnings.Add("High complexity filter - consider optimization");

                if (CountOccurrences(filterExpression, "/all(") > 2)
                    warnings.Add("Multiple all() functions may impact performance");

                return (issues.Count == 0, issues, warnings);
            }
            catch (Exception ex)
            {
                issues.Add($"Validation error: {ex.Message}");
                return (false, issues, warnings);
            }
        }

        private static int CountOccurrences(string text, string pattern)
        {
            return (text.Length - text.Replace(pattern, "").Length) / pattern.Length;
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var example = new ComplexFiltersExample();
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