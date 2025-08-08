/*
Wildcard Search - Module 2 C# Examples
Pattern matching with wildcards in Azure AI Search using .NET SDK

This module demonstrates:
- Prefix matching with *
- Suffix matching with *
- Pattern matching strategies
- When to use wildcards
- Wildcard search limitations
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
    public class WildcardSearch
    {
        private readonly SearchClient _searchClient;

        public WildcardSearch(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Search for terms starting with a prefix (prefix*)
        /// </summary>
        /// <param name="prefix">The prefix to search for</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> PrefixSearchAsync(string prefix, int top = 10)
        {
            try
            {
                var query = $"{prefix}*";
                Console.WriteLine($"Performing prefix search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results with prefix '{prefix}'");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in prefix search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for terms ending with a suffix (*suffix)
        /// </summary>
        /// <param name="suffix">The suffix to search for</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> SuffixSearchAsync(string suffix, int top = 10)
        {
            try
            {
                var query = $"*{suffix}";
                Console.WriteLine($"Performing suffix search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results with suffix '{suffix}'");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in suffix search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for terms containing a substring (*substring*)
        /// </summary>
        /// <param name="substring">The substring to search for</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> ContainsSearchAsync(string substring, int top = 10)
        {
            try
            {
                var query = $"*{substring}*";
                Console.WriteLine($"Performing contains search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results containing '{substring}'");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in contains search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for multiple wildcard patterns
        /// </summary>
        /// <param name="patterns">List of wildcard patterns to search for</param>
        /// <param name="top">Maximum results per pattern</param>
        /// <returns>Dictionary mapping patterns to their results</returns>
        public async Task<Dictionary<string, SearchResults<SearchDocument>>> MultipleWildcardSearchAsync(
            IEnumerable<string> patterns, int top = 5)
        {
            var results = new Dictionary<string, SearchResults<SearchDocument>>();

            foreach (var pattern in patterns)
            {
                try
                {
                    Console.WriteLine($"Searching for pattern: '{pattern}'");

                    var searchOptions = new SearchOptions
                    {
                        Size = top,
                        IncludeTotalCount = true
                    };

                    var searchResults = await _searchClient.SearchAsync<SearchDocument>(pattern, searchOptions);
                    results[pattern] = searchResults.Value;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error searching pattern '{pattern}': {ex.Message}");
                    // Create empty result for failed patterns
                    results[pattern] = null;
                }
            }

            return results;
        }

        /// <summary>
        /// Compare different wildcard patterns for the same base term
        /// </summary>
        /// <param name="baseTerm">Base term to create patterns from</param>
        /// <param name="top">Maximum results per pattern</param>
        /// <returns>Dictionary mapping pattern types to their results</returns>
        public async Task<Dictionary<string, SearchResults<SearchDocument>>> CompareWildcardPatternsAsync(
            string baseTerm, int top = 5)
        {
            var patterns = new Dictionary<string, string>
            {
                ["exact"] = baseTerm,
                ["prefix"] = $"{baseTerm}*",
                ["suffix"] = $"*{baseTerm}",
                ["contains"] = $"*{baseTerm}*"
            };

            var results = new Dictionary<string, SearchResults<SearchDocument>>();

            foreach (var kvp in patterns)
            {
                var patternType = kvp.Key;
                var pattern = kvp.Value;

                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Size = top,
                        IncludeTotalCount = true
                    };

                    var searchResults = await _searchClient.SearchAsync<SearchDocument>(pattern, searchOptions);
                    results[patternType] = searchResults.Value;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in {patternType} search: {ex.Message}");
                    results[patternType] = null;
                }
            }

            return results;
        }

        /// <summary>
        /// Display comparison of wildcard patterns
        /// </summary>
        /// <param name="baseTerm">Base term used for patterns</param>
        /// <param name="results">Results from different wildcard patterns</param>
        public static void DisplayWildcardComparison(string baseTerm, 
            Dictionary<string, SearchResults<SearchDocument>> results)
        {
            Console.WriteLine($"\n🃏 Wildcard Patterns Comparison: '{baseTerm}'");
            Console.WriteLine(new string('=', 60));

            var patternInfo = new Dictionary<string, (string Name, string Pattern, string Description)>
            {
                ["exact"] = ("Exact Match", baseTerm, "Exact term only"),
                ["prefix"] = ("Prefix Match", $"{baseTerm}*", $"Terms starting with \"{baseTerm}\""),
                ["suffix"] = ("Suffix Match", $"*{baseTerm}", $"Terms ending with \"{baseTerm}\""),
                ["contains"] = ("Contains Match", $"*{baseTerm}*", $"Terms containing \"{baseTerm}\"")
            };

            foreach (var kvp in results)
            {
                var patternType = kvp.Key;
                var patternResults = kvp.Value;

                if (patternInfo.ContainsKey(patternType))
                {
                    var (name, pattern, description) = patternInfo[patternType];
                    var resultList = patternResults?.GetResults()?.ToList() ?? new List<SearchResult<SearchDocument>>();

                    Console.WriteLine($"\n{name}:");
                    Console.WriteLine($"   Pattern: {pattern}");
                    Console.WriteLine($"   Description: {description}");
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
                    }
                    else
                    {
                        Console.WriteLine("   No matches found");
                    }

                    Console.WriteLine(new string('-', 40));
                }
            }

            // Analysis
            Console.WriteLine($"\n📊 PATTERN ANALYSIS:");
            var exactCount = results.ContainsKey("exact") && results["exact"] != null ? 
                results["exact"].GetResults().Count() : 0;
            var prefixCount = results.ContainsKey("prefix") && results["prefix"] != null ? 
                results["prefix"].GetResults().Count() : 0;
            var suffixCount = results.ContainsKey("suffix") && results["suffix"] != null ? 
                results["suffix"].GetResults().Count() : 0;
            var containsCount = results.ContainsKey("contains") && results["contains"] != null ? 
                results["contains"].GetResults().Count() : 0;

            Console.WriteLine($"   Exact: {exactCount} (most specific)");
            Console.WriteLine($"   Prefix: {prefixCount}");
            Console.WriteLine($"   Suffix: {suffixCount}");
            Console.WriteLine($"   Contains: {containsCount} (broadest)");

            if (containsCount >= Math.Max(prefixCount, suffixCount) && 
                Math.Max(prefixCount, suffixCount) >= exactCount)
            {
                Console.WriteLine("   ✅ Expected pattern: Contains ≥ Prefix/Suffix ≥ Exact");
            }
            else
            {
                Console.WriteLine("   ⚠️ Unexpected pattern - depends on your data");
            }
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class WildcardSearchProgram
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

                await DemonstrateWildcardSearchAsync(searchClient);
                await WildcardSearchBestPracticesAsync(searchClient);

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Experiment with different wildcard patterns");
                Console.WriteLine("   - Try combining wildcards with boolean operators");
                Console.WriteLine("   - Check out 05_FieldSearch.cs for field-specific searches");
                Console.WriteLine("   - Learn about search parameters in other examples");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateWildcardSearchAsync(SearchClient searchClient)
        {
            Console.WriteLine("🃏 Wildcard Search Demonstration");
            Console.WriteLine(new string('=', 50));

            var searchOps = new WildcardSearch(searchClient);

            // Example 1: Compare wildcard patterns
            Console.WriteLine("\n1️⃣ Wildcard Patterns Comparison");

            var baseTerm = "program";
            var wildcardResults = await searchOps.CompareWildcardPatternsAsync(baseTerm, 5);
            WildcardSearch.DisplayWildcardComparison(baseTerm, wildcardResults);

            // Example 2: Practical wildcard searches
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n2️⃣ Practical Wildcard Examples");
            Console.WriteLine(new string('-', 30));

            var practicalExamples = new[]
            {
                new { Description = "Find programming languages", Pattern = "program*", Type = "prefix" },
                new { Description = "Find development terms", Pattern = "*develop*", Type = "contains" },
                new { Description = "Find tutorial content", Pattern = "*tutorial", Type = "suffix" },
                new { Description = "Find JavaScript variations", Pattern = "java*", Type = "prefix" }
            };

            foreach (var example in practicalExamples)
            {
                Console.WriteLine($"\n📋 {example.Description}");
                Console.WriteLine($"   Pattern: {example.Pattern} ({example.Type})");

                SearchResults<SearchDocument> results = null;
                switch (example.Type)
                {
                    case "prefix":
                        results = await searchOps.PrefixSearchAsync(example.Pattern.TrimEnd('*'), 3);
                        break;
                    case "suffix":
                        results = await searchOps.SuffixSearchAsync(example.Pattern.TrimStart('*'), 3);
                        break;
                    case "contains":
                        results = await searchOps.ContainsSearchAsync(example.Pattern.Trim('*'), 3);
                        break;
                }

                if (results != null)
                {
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
            }

            // Example 3: Multiple wildcard search
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n3️⃣ Multiple Wildcard Search");
            Console.WriteLine(new string('-', 30));

            var wildcardPatterns = new[]
            {
                "web*",      // web, website, webdev, etc.
                "*script",   // javascript, typescript, etc.
                "*data*",    // database, metadata, etc.
                "api*"       // api, apis, etc.
            };

            var multiResults = await searchOps.MultipleWildcardSearchAsync(wildcardPatterns, 2);

            foreach (var kvp in multiResults)
            {
                var pattern = kvp.Key;
                var results = kvp.Value;
                var resultList = results?.GetResults()?.ToList() ?? new List<SearchResult<SearchDocument>>();

                Console.WriteLine($"\nPattern: {pattern}");
                Console.WriteLine($"Results: {resultList.Count}");
                
                if (resultList.Any())
                {
                    for (int i = 0; i < resultList.Count; i++)
                    {
                        var result = resultList[i];
                        var title = result.Document.TryGetValue("title", out var titleValue) ? 
                            titleValue?.ToString() : "No title";
                        var score = result.Score ?? 0.0;
                        Console.WriteLine($"  {i + 1}. {title} (Score: {score:F3})");
                    }
                }
            }

            Console.WriteLine("\n✅ Wildcard search demonstration completed!");
        }

        private static async Task WildcardSearchBestPracticesAsync(SearchClient searchClient)
        {
            Console.WriteLine("\n📚 Wildcard Search Best Practices");
            Console.WriteLine(new string('=', 50));

            Console.WriteLine("\n💡 When to Use Wildcards:");
            Console.WriteLine("\n✅ Prefix Search (term*):");
            Console.WriteLine("   - Finding word variations (program, programming, programmer)");
            Console.WriteLine("   - Technology families (java, javascript, javadoc)");
            Console.WriteLine("   - Brand or product lines (micro, microsoft, microservice)");
            Console.WriteLine("   - Language variations (develop, developer, development)");

            Console.WriteLine("\n✅ Suffix Search (*term):");
            Console.WriteLine("   - Finding words with common endings (*ing, *tion, *ment)");
            Console.WriteLine("   - File types or extensions (*script, *doc)");
            Console.WriteLine("   - Categories or types (*tutorial, *guide)");

            Console.WriteLine("\n✅ Contains Search (*term*):");
            Console.WriteLine("   - Finding partial matches when unsure of exact form");
            Console.WriteLine("   - Searching within compound words");
            Console.WriteLine("   - When you know a key part but not the whole term");

            Console.WriteLine("\n⚠️ Wildcard Limitations:");
            Console.WriteLine("   ❌ Can be slower than exact searches");
            Console.WriteLine("   ❌ May return too many irrelevant results");
            Console.WriteLine("   ❌ Leading wildcards (*term) are generally slower");
            Console.WriteLine("   ❌ Multiple wildcards in one term can be very slow");

            Console.WriteLine("\n🔧 Performance Tips:");
            Console.WriteLine("   ✅ Use specific prefixes (at least 2-3 characters)");
            Console.WriteLine("   ✅ Combine with other terms to narrow results");
            Console.WriteLine("   ✅ Prefer prefix wildcards over suffix wildcards");
            Console.WriteLine("   ✅ Test wildcard queries with small result sets first");

            // Demonstrate good vs bad practices
            Console.WriteLine("\n🧪 Good vs Bad Wildcard Examples:");
            var searchOps = new WildcardSearch(searchClient);

            Console.WriteLine("\n✅ Good Wildcard Practices:");
            var goodExamples = new[]
            {
                ("program*", "Specific prefix, likely to find relevant terms"),
                ("java* AND tutorial", "Wildcard combined with specific term"),
                ("*development", "Common suffix, reasonable scope")
            };

            foreach (var (pattern, explanation) in goodExamples)
            {
                Console.WriteLine($"   {pattern}: {explanation}");
            }

            Console.WriteLine("\n❌ Problematic Wildcard Practices:");
            var badExamples = new[]
            {
                ("*a*", "Too broad, will match almost everything"),
                ("*", "Matches all documents, not useful for search"),
                ("*e*t*", "Multiple wildcards, very slow")
            };

            foreach (var (pattern, explanation) in badExamples)
            {
                Console.WriteLine($"   {pattern}: {explanation}");
            }

            // Show optimization example
            Console.WriteLine("\n🚀 Optimization Example:");
            Console.WriteLine("   Instead of: '*script'");
            Console.WriteLine("   Try: 'javascript OR typescript OR script'");
            Console.WriteLine("   Benefit: More specific, faster, better relevance");
        }
    }
}