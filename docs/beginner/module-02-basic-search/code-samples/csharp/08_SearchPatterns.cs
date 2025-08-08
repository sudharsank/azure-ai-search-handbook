/*
Search Patterns - Module 2 C# Examples
Common search patterns and strategies in Azure AI Search

This module demonstrates:
- Progressive search strategies
- Search with fallback
- Multi-strategy search
- Search pattern best practices
- When to use different patterns
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
    /// <summary>
    /// Class demonstrating common search patterns
    /// </summary>
    public class SearchPatterns
    {
        private readonly SearchClient _searchClient;

        public SearchPatterns(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Progressive search from specific to broad
        /// </summary>
        /// <param name="query">Base search query</param>
        /// <param name="top">Maximum results per strategy</param>
        /// <returns>Dictionary mapping strategy names to results</returns>
        public async Task<Dictionary<string, List<SearchResult<SearchDocument>>>> ProgressiveSearchAsync(
            string query, int top = 10)
        {
            var strategies = new Dictionary<string, List<SearchResult<SearchDocument>>>();

            // 1. Exact phrase (most specific)
            try
            {
                var exactOptions = new SearchOptions { Size = top };
                var exactResults = await _searchClient.SearchAsync<SearchDocument>($"\"{query}\"", exactOptions);
                
                var exactList = new List<SearchResult<SearchDocument>>();
                await foreach (var result in exactResults.Value.GetResultsAsync())
                {
                    exactList.Add(result);
                }
                
                strategies["exact_phrase"] = exactList;
                Console.WriteLine($"Exact phrase: {exactList.Count} results");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exact phrase search failed: {ex.Message}");
                strategies["exact_phrase"] = new List<SearchResult<SearchDocument>>();
            }

            // 2. All terms (moderate specificity)
            try
            {
                var allTermsOptions = new SearchOptions 
                { 
                    Size = top,
                    SearchMode = SearchMode.All
                };
                var allTermsResults = await _searchClient.SearchAsync<SearchDocument>(query, allTermsOptions);
                
                var allTermsList = new List<SearchResult<SearchDocument>>();
                await foreach (var result in allTermsResults.Value.GetResultsAsync())
                {
                    allTermsList.Add(result);
                }
                
                strategies["all_terms"] = allTermsList;
                Console.WriteLine($"All terms: {allTermsList.Count} results");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"All terms search failed: {ex.Message}");
                strategies["all_terms"] = new List<SearchResult<SearchDocument>>();
            }

            // 3. Any terms (broad)
            try
            {
                var anyTermsOptions = new SearchOptions 
                { 
                    Size = top,
                    SearchMode = SearchMode.Any
                };
                var anyTermsResults = await _searchClient.SearchAsync<SearchDocument>(query, anyTermsOptions);
                
                var anyTermsList = new List<SearchResult<SearchDocument>>();
                await foreach (var result in anyTermsResults.Value.GetResultsAsync())
                {
                    anyTermsList.Add(result);
                }
                
                strategies["any_terms"] = anyTermsList;
                Console.WriteLine($"Any terms: {anyTermsList.Count} results");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Any terms search failed: {ex.Message}");
                strategies["any_terms"] = new List<SearchResult<SearchDocument>>();
            }

            // 4. Wildcard (broadest)
            try
            {
                var terms = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                var wildcardQuery = string.Join(" OR ", terms.Select(term => $"{term}*"));
                
                var wildcardOptions = new SearchOptions { Size = top };
                var wildcardResults = await _searchClient.SearchAsync<SearchDocument>(wildcardQuery, wildcardOptions);
                
                var wildcardList = new List<SearchResult<SearchDocument>>();
                await foreach (var result in wildcardResults.Value.GetResultsAsync())
                {
                    wildcardList.Add(result);
                }
                
                strategies["wildcard"] = wildcardList;
                Console.WriteLine($"Wildcard: {wildcardList.Count} results");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Wildcard search failed: {ex.Message}");
                strategies["wildcard"] = new List<SearchResult<SearchDocument>>();
            }

            return strategies;
        }

        /// <summary>
        /// Search with automatic fallback to broader strategies
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="top">Maximum results to return</param>
        /// <returns>List of search results from first successful strategy</returns>
        public async Task<List<SearchResult<SearchDocument>>> SearchWithFallbackAsync(string query, int top = 10)
        {
            // Try strategies in order of specificity
            var strategies = new[]
            {
                (Query: $"\"{query}\"", Name: "exact phrase", Options: new SearchOptions { Size = top }),
                (Query: query, Name: "all terms (default)", Options: new SearchOptions { Size = top }),
                (Query: query, Name: "any terms", Options: new SearchOptions { Size = top, SearchMode = SearchMode.Any }),
                (Query: string.Join(" OR ", query.Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(term => $"{term}*")), 
                 Name: "wildcard", Options: new SearchOptions { Size = top })
            };

            foreach (var (searchQuery, strategyName, options) in strategies)
            {
                try
                {
                    var results = await _searchClient.SearchAsync<SearchDocument>(searchQuery, options);
                    var resultList = new List<SearchResult<SearchDocument>>();
                    
                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    if (resultList.Any())
                    {
                        Console.WriteLine($"Found {resultList.Count} results using {strategyName}");
                        return resultList;
                    }
                    else
                    {
                        Console.WriteLine($"No results with {strategyName}, trying next strategy");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error with {strategyName}: {ex.Message}");
                    continue;
                }
            }

            Console.WriteLine("No results found with any search strategy");
            return new List<SearchResult<SearchDocument>>();
        }

        /// <summary>
        /// Search across fields in order of priority
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="fieldPriority">List of fields in priority order</param>
        /// <param name="top">Maximum results to return</param>
        /// <returns>Combined results from all fields</returns>
        public async Task<List<SearchResult<SearchDocument>>> MultiFieldSearchAsync(
            string query, List<string> fieldPriority, int top = 10)
        {
            var allResults = new List<SearchResult<SearchDocument>>();
            var seenIds = new HashSet<string>();

            foreach (var field in fieldPriority)
            {
                try
                {
                    var fieldOptions = new SearchOptions 
                    { 
                        Size = top,
                        SearchFields = { field }
                    };
                    
                    var fieldResults = await _searchClient.SearchAsync<SearchDocument>(query, fieldOptions);
                    var fieldCount = 0;

                    await foreach (var result in fieldResults.Value.GetResultsAsync())
                    {
                        var resultId = result.Document.TryGetValue("id", out var idValue) ? 
                            idValue?.ToString() : result.GetHashCode().ToString();

                        if (!seenIds.Contains(resultId))
                        {
                            seenIds.Add(resultId);
                            allResults.Add(result);
                        }
                        fieldCount++;
                    }

                    Console.WriteLine($"Field '{field}': found {fieldCount} results");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error searching field '{field}': {ex.Message}");
                    continue;
                }
            }

            // Sort by score
            allResults = allResults.OrderByDescending(r => r.Score ?? 0).Take(top).ToList();
            return allResults;
        }

        /// <summary>
        /// Display results from progressive search
        /// </summary>
        /// <param name="query">Original query</param>
        /// <param name="strategies">Results from different strategies</param>
        public void DisplayProgressiveResults(string query, Dictionary<string, List<SearchResult<SearchDocument>>> strategies)
        {
            Console.WriteLine($"\n🔄 Progressive Search Results: '{query}'");
            Console.WriteLine(new string('=', 60));

            var strategyInfo = new Dictionary<string, (string DisplayName, string Description)>
            {
                ["exact_phrase"] = ("Exact Phrase", "Most specific - exact phrase match"),
                ["all_terms"] = ("All Terms", "Moderate - all terms must be present"),
                ["any_terms"] = ("Any Terms", "Broad - any terms can be present"),
                ["wildcard"] = ("Wildcard", "Broadest - partial term matching")
            };

            foreach (var (strategyName, results) in strategies)
            {
                if (strategyInfo.TryGetValue(strategyName, out var info))
                {
                    var (displayName, description) = info;

                    Console.WriteLine($"\n{displayName}:");
                    Console.WriteLine($"   Description: {description}");
                    Console.WriteLine($"   Results: {results.Count} found");

                    if (results.Any())
                    {
                        Console.WriteLine("   Top matches:");
                        for (int i = 0; i < Math.Min(3, results.Count); i++)
                        {
                            var result = results[i];
                            var title = result.Document.TryGetValue("title", out var titleValue) ? 
                                titleValue?.ToString() ?? "No title" : "No title";
                            var score = result.Score ?? 0.0;
                            Console.WriteLine($"     {i + 1}. {title} (Score: {score:F3})");
                        }
                    }
                    else
                    {
                        Console.WriteLine("   No matches found");
                    }

                    Console.WriteLine(new string('-', 40));
                }
            }

            // Recommendation
            Console.WriteLine($"\n💡 RECOMMENDATION:");
            foreach (var (strategyName, results) in strategies)
            {
                if (results.Any() && strategyInfo.TryGetValue(strategyName, out var info))
                {
                    Console.WriteLine($"   Use '{info.DisplayName}' - found {results.Count} relevant results");
                    break;
                }
            }

            if (!strategies.Values.Any(results => results.Any()))
            {
                Console.WriteLine("   Try different search terms or check your data");
            }
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class SearchPatternsProgram
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

                await DemonstrateSearchPatternsAsync(searchClient);
                DisplaySearchPatternBestPractices();

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Try different search patterns with your data");
                Console.WriteLine("   - Experiment with combining patterns");
                Console.WriteLine("   - Consider which patterns work best for your use case");
                Console.WriteLine("   - Review all C# examples to build complete search functionality");
                Console.WriteLine("   - Check out other language examples in ../python/, ../javascript/, etc.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateSearchPatternsAsync(SearchClient searchClient)
        {
            Console.WriteLine("🎯 Search Patterns Demonstration");
            Console.WriteLine(new string('=', 50));

            try
            {
                // Initialize search patterns
                var patterns = new SearchPatterns(searchClient);

                // Example 1: Progressive search
                Console.WriteLine("\n1️⃣ Progressive Search Strategy");

                var query = "machine learning";
                var progressiveResults = await patterns.ProgressiveSearchAsync(query, 5);
                patterns.DisplayProgressiveResults(query, progressiveResults);

                // Example 2: Search with fallback
                Console.WriteLine($"\n{new string('=', 70)}");
                Console.WriteLine("\n2️⃣ Search with Automatic Fallback");
                Console.WriteLine(new string('-', 40));

                var fallbackQuery = "artificial intelligence tutorial";
                var fallbackResults = await patterns.SearchWithFallbackAsync(fallbackQuery, 5);

                Console.WriteLine($"Query: '{fallbackQuery}'");
                Console.WriteLine($"Results with fallback: {fallbackResults.Count} found");

                if (fallbackResults.Any())
                {
                    Console.WriteLine("Top results:");
                    for (int i = 0; i < Math.Min(3, fallbackResults.Count); i++)
                    {
                        var result = fallbackResults[i];
                        var title = result.Document.TryGetValue("title", out var titleValue) ? 
                            titleValue?.ToString() ?? "No title" : "No title";
                        var score = result.Score ?? 0.0;
                        Console.WriteLine($"  {i + 1}. {title} (Score: {score:F3})");
                    }
                }

                // Example 3: Multi-field search
                Console.WriteLine($"\n{new string('=', 70)}");
                Console.WriteLine("\n3️⃣ Multi-Field Priority Search");
                Console.WriteLine(new string('-', 40));

                var fieldPriority = new List<string> { "title", "description", "content", "tags" };
                var multiFieldQuery = "python";

                var multiResults = await patterns.MultiFieldSearchAsync(multiFieldQuery, fieldPriority, 5);

                Console.WriteLine($"Query: '{multiFieldQuery}'");
                Console.WriteLine($"Field priority: {string.Join(" > ", fieldPriority)}");
                Console.WriteLine($"Combined results: {multiResults.Count} found");

                if (multiResults.Any())
                {
                    Console.WriteLine("Top combined results:");
                    for (int i = 0; i < Math.Min(3, multiResults.Count); i++)
                    {
                        var result = multiResults[i];
                        var title = result.Document.TryGetValue("title", out var titleValue) ? 
                            titleValue?.ToString() ?? "No title" : "No title";
                        var score = result.Score ?? 0.0;
                        Console.WriteLine($"  {i + 1}. {title} (Score: {score:F3})");
                    }
                }

                Console.WriteLine("\n✅ Search patterns demonstration completed!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
            }
        }

        private static void DisplaySearchPatternBestPractices()
        {
            Console.WriteLine("\n📚 Search Pattern Best Practices");
            Console.WriteLine(new string('=', 50));

            Console.WriteLine("\n💡 When to Use Each Pattern:");

            Console.WriteLine("\n🎯 Progressive Search:");
            Console.WriteLine("   ✅ When you want comprehensive coverage");
            Console.WriteLine("   ✅ For user-facing search interfaces");
            Console.WriteLine("   ✅ When result quality is more important than speed");
            Console.WriteLine("   ✅ For exploratory or research searches");

            Console.WriteLine("\n🔄 Fallback Search:");
            Console.WriteLine("   ✅ When you need guaranteed results");
            Console.WriteLine("   ✅ For automated systems");
            Console.WriteLine("   ✅ When speed is important");
            Console.WriteLine("   ✅ For simple search interfaces");

            Console.WriteLine("\n🏗️ Multi-Field Search:");
            Console.WriteLine("   ✅ When different fields have different importance");
            Console.WriteLine("   ✅ For structured data with clear field hierarchy");
            Console.WriteLine("   ✅ When you want to avoid duplicates");
            Console.WriteLine("   ✅ For content with rich metadata");

            Console.WriteLine("\n⚠️ Pattern Selection Guidelines:");
            Console.WriteLine("   🔍 Start simple, add complexity as needed");
            Console.WriteLine("   📊 Monitor which patterns work best for your data");
            Console.WriteLine("   ⚡ Consider performance implications");
            Console.WriteLine("   👥 Think about user expectations");

            Console.WriteLine("\n🔧 Implementation Tips:");
            Console.WriteLine("   ✅ Cache results from expensive pattern searches");
            Console.WriteLine("   ✅ Log which patterns are most successful");
            Console.WriteLine("   ✅ Allow users to choose search modes");
            Console.WriteLine("   ✅ Provide feedback about search strategy used");
        }
    }
}