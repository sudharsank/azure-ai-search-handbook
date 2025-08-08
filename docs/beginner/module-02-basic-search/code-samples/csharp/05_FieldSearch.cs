/*
Field-Specific Search - Module 2 C# Examples
Searching within specific fields in Azure AI Search using .NET SDK

This module demonstrates:
- Searching specific fields
- Field selection for results
- Multi-field searches
- Field weighting concepts
- When to use field-specific search
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module02.BasicSearch
{
    public class FieldSearch
    {
        private readonly SearchClient _searchClient;

        public FieldSearch(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Search within a specific field only
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="field">Field name to search in</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> SearchSpecificFieldAsync(string query, string field, int top = 10)
        {
            try
            {
                Console.WriteLine($"Searching field '{field}' for: '{query}'");

                var searchOptions = new SearchOptions
                {
                    SearchFields = { field },
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results in field '{field}'");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error searching field '{field}': {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search within multiple specific fields
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="fields">List of field names to search in</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> SearchMultipleFieldsAsync(string query, IEnumerable<string> fields, int top = 10)
        {
            try
            {
                var fieldList = fields.ToList();
                Console.WriteLine($"Searching fields [{string.Join(", ", fieldList)}] for: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                foreach (var field in fieldList)
                {
                    searchOptions.SearchFields.Add(field);
                }

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results in specified fields");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error searching multiple fields: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search and return only selected fields
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="selectFields">List of field names to return in results</param>
        /// <param name="searchFields">List of field names to search in (optional)</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results with only selected fields</returns>
        public async Task<SearchResults<SearchDocument>> SearchWithSelectedFieldsAsync(
            string query, IEnumerable<string> selectFields, IEnumerable<string> searchFields = null, int top = 10)
        {
            try
            {
                var selectList = selectFields.ToList();
                Console.WriteLine($"Searching for '{query}' with selected fields: [{string.Join(", ", selectList)}]");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                foreach (var field in selectList)
                {
                    searchOptions.Select.Add(field);
                }

                if (searchFields != null)
                {
                    foreach (var field in searchFields)
                    {
                        searchOptions.SearchFields.Add(field);
                    }
                }

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results with selected fields");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in search with selected fields: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Compare search results across different fields
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="fields">List of fields to compare</param>
        /// <param name="top">Maximum results per field</param>
        /// <returns>Dictionary mapping field names to their results</returns>
        public async Task<Dictionary<string, SearchResults<SearchDocument>>> CompareFieldSearchesAsync(
            string query, IEnumerable<string> fields, int top = 5)
        {
            var results = new Dictionary<string, SearchResults<SearchDocument>>();

            // Search all fields (default)
            try
            {
                var allResults = await _searchClient.SearchAsync<SearchDocument>(query, new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                });
                results["all_fields"] = allResults.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in all fields search: {ex.Message}");
                results["all_fields"] = null;
            }

            // Search individual fields
            foreach (var field in fields)
            {
                results[field] = await SearchSpecificFieldAsync(query, field, top);
            }

            return results;
        }

        /// <summary>
        /// Display comparison of field-specific searches
        /// </summary>
        /// <param name="query">Original search query</param>
        /// <param name="results">Results from different field searches</param>
        public static void DisplayFieldComparison(string query, 
            Dictionary<string, SearchResults<SearchDocument>> results)
        {
            Console.WriteLine($"\n🎯 Field-Specific Search Comparison: '{query}'");
            Console.WriteLine(new string('=', 70));

            foreach (var kvp in results)
            {
                var fieldName = kvp.Key;
                var fieldResults = kvp.Value;
                var resultList = fieldResults?.GetResults()?.ToList() ?? new List<SearchResult<SearchDocument>>();

                Console.WriteLine($"\n{fieldName.Replace("_", " ").ToTitleCase()}:");
                Console.WriteLine($"   Results found: {resultList.Count}");

                if (resultList.Any())
                {
                    Console.WriteLine("   Top matches:");
                    for (int i = 0; i < Math.Min(3, resultList.Count); i++)
                    {
                        var result = resultList[i];
                        var title = result.Document.TryGetValue("title", out var titleValue) ? 
                            titleValue?.ToString() : "No title";
                        var score = result.Score ?? 0.0;
                        Console.WriteLine($"     {i + 1}. {title} (Score: {score:F3})");
                    }

                    // Show average score
                    var avgScore = resultList.Where(r => r.Score.HasValue).Average(r => r.Score.Value);
                    Console.WriteLine($"   Average score: {avgScore:F3}");
                }
                else
                {
                    Console.WriteLine("   No matches found");
                }

                Console.WriteLine(new string('-', 50));
            }

            // Analysis
            Console.WriteLine($"\n📊 FIELD ANALYSIS:");
            foreach (var kvp in results)
            {
                var fieldName = kvp.Key;
                var fieldResults = kvp.Value;
                var count = fieldResults?.GetResults()?.Count() ?? 0;
                
                if (count > 0)
                {
                    var resultList = fieldResults.GetResults().ToList();
                    var maxScore = resultList.Where(r => r.Score.HasValue).Max(r => r.Score.Value);
                    Console.WriteLine($"   {fieldName}: {count} results (max score: {maxScore:F3})");
                }
                else
                {
                    Console.WriteLine($"   {fieldName}: No results");
                }
            }
        }
    }

    /// <summary>
    /// Extension method for title case conversion
    /// </summary>
    public static class StringExtensions
    {
        public static string ToTitleCase(this string input)
        {
            if (string.IsNullOrEmpty(input))
                return input;

            var words = input.Split(' ');
            for (int i = 0; i < words.Length; i++)
            {
                if (words[i].Length > 0)
                {
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
                }
            }
            return string.Join(" ", words);
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class FieldSearchProgram
    {
        // Replace with your actual service details
        private const string ServiceEndpoint = "https://your-service.search.windows.net";
        private const string ApiKey = "your-api-key";
        private const string IndexName = "your-index-name";

        public static async Task Main(string[] args)
        {
            try
            {
                // Initialize search client
                var searchClient = new SearchClient(
                    new Uri(ServiceEndpoint),
                    IndexName,
                    new AzureKeyCredential(ApiKey)
                );

                await DemonstrateFieldSearchAsync(searchClient);
                await FieldSearchBestPracticesAsync(searchClient);

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Try searching different fields in your index");
                Console.WriteLine("   - Experiment with field combinations");
                Console.WriteLine("   - Check out other examples for more search options");
                Console.WriteLine("   - Learn about result processing techniques");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateFieldSearchAsync(SearchClient searchClient)
        {
            Console.WriteLine("🎯 Field-Specific Search Demonstration");
            Console.WriteLine(new string('=', 50));

            var searchOps = new FieldSearch(searchClient);

            // Example 1: Compare field searches
            Console.WriteLine("\n1️⃣ Field Search Comparison");

            var query = "python";
            var commonFields = new[] { "title", "content", "description", "author" };

            var fieldResults = await searchOps.CompareFieldSearchesAsync(query, commonFields, 5);
            FieldSearch.DisplayFieldComparison(query, fieldResults);

            // Example 2: Multi-field search
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n2️⃣ Multi-Field Search Examples");
            Console.WriteLine(new string('-', 30));

            var multiFieldExamples = new[]
            {
                new { Description = "Find tutorials by title or description", Fields = new[] { "title", "description" } },
                new { Description = "Search content and tags", Fields = new[] { "content", "tags" } },
                new { Description = "Author and title search", Fields = new[] { "author", "title" } }
            };

            foreach (var example in multiFieldExamples)
            {
                Console.WriteLine($"\n📋 {example.Description}");
                Console.WriteLine($"   Fields: {string.Join(", ", example.Fields)}");

                var results = await searchOps.SearchMultipleFieldsAsync("tutorial", example.Fields, 3);
                var resultList = results.GetResults().ToList();
                Console.WriteLine($"   Results: {resultList.Count} found");

                if (resultList.Any())
                {
                    var topResult = resultList.First();
                    var title = topResult.Document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() : "No title";
                    var score = topResult.Score ?? 0.0;
                    Console.WriteLine($"   Top match: {title} (Score: {score:F3})");
                }
            }

            // Example 3: Field selection
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n3️⃣ Field Selection Examples");
            Console.WriteLine(new string('-', 30));

            var selectionExamples = new[]
            {
                new { Description = "Basic info only", SelectFields = new[] { "id", "title", "author" } },
                new { Description = "Content preview", SelectFields = new[] { "title", "description", "url" } },
                new { Description = "Metadata only", SelectFields = new[] { "id", "publishedDate", "category" } }
            };

            foreach (var example in selectionExamples)
            {
                Console.WriteLine($"\n📋 {example.Description}");
                Console.WriteLine($"   Selected fields: {string.Join(", ", example.SelectFields)}");

                var results = await searchOps.SearchWithSelectedFieldsAsync(
                    "programming", 
                    example.SelectFields, 
                    top: 2
                );

                var resultList = results.GetResults().ToList();
                Console.WriteLine($"   Results: {resultList.Count} found");

                if (resultList.Any())
                {
                    var firstResult = resultList.First();
                    var availableFields = firstResult.Document.Keys.Where(k => !k.StartsWith("@")).ToList();
                    Console.WriteLine($"   Available fields in result: {string.Join(", ", availableFields)}");
                }
            }

            Console.WriteLine("\n✅ Field-specific search demonstration completed!");
        }

        private static async Task FieldSearchBestPracticesAsync(SearchClient searchClient)
        {
            Console.WriteLine("\n📚 Field-Specific Search Best Practices");
            Console.WriteLine(new string('=', 50));

            Console.WriteLine("\n💡 When to Use Field-Specific Search:");
            Console.WriteLine("\n✅ Search Specific Fields When:");
            Console.WriteLine("   - You know exactly which field contains relevant information");
            Console.WriteLine("   - You want to search titles only (more precise)");
            Console.WriteLine("   - You need to search metadata fields (author, category, etc.)");
            Console.WriteLine("   - You want to exclude certain fields from search");

            Console.WriteLine("\n✅ Select Specific Fields When:");
            Console.WriteLine("   - You only need certain fields in results (faster)");
            Console.WriteLine("   - You want to reduce network traffic");
            Console.WriteLine("   - You're building a summary or preview");
            Console.WriteLine("   - You need consistent result structure");

            Console.WriteLine("\n⚠️ Field Search Considerations:");
            Console.WriteLine("   ❌ Field names must exist in your index");
            Console.WriteLine("   ❌ Searching fewer fields may miss relevant content");
            Console.WriteLine("   ❌ Field-specific search can be less flexible");
            Console.WriteLine("   ❌ Some fields might not be searchable");

            Console.WriteLine("\n🔧 Performance Tips:");
            Console.WriteLine("   ✅ Use field selection to reduce result size");
            Console.WriteLine("   ✅ Search high-value fields first (title, description)");
            Console.WriteLine("   ✅ Combine field search with other filters");
            Console.WriteLine("   ✅ Test which fields give best results for your use case");

            // Demonstrate field strategy
            Console.WriteLine("\n🎯 Field Search Strategy Example:");
            var searchOps = new FieldSearch(searchClient);

            var query = "javascript tutorial";

            Console.WriteLine($"\nQuery: '{query}'");
            Console.WriteLine("Strategy: Search from most specific to most general");

            // 1. Title only (most specific)
            var titleResults = await searchOps.SearchSpecificFieldAsync(query, "title", 1);
            var titleCount = titleResults.GetResults().Count();
            Console.WriteLine($"\n1. Title only: {titleCount} results");

            // 2. Title + description (moderate)
            var titleDescResults = await searchOps.SearchMultipleFieldsAsync(query, new[] { "title", "description" }, 1);
            var titleDescCount = titleDescResults.GetResults().Count();
            Console.WriteLine($"2. Title + Description: {titleDescCount} results");

            // 3. All fields (broadest)
            var allResults = await searchClient.SearchAsync<SearchDocument>(query, new SearchOptions { Size = 1 });
            var allCount = allResults.Value.GetResults().Count();
            Console.WriteLine($"3. All fields: {allCount} results");

            Console.WriteLine($"\n💡 Recommendation: Start specific, broaden if needed");
        }
    }
}