using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace AzureSearchModule4
{
    /// <summary>
    /// Module 4: Simple Queries and Filters - Advanced Queries
    /// 
    /// This class demonstrates advanced query techniques in Azure AI Search using C#.
    /// Learn about field boosting, fuzzy search, wildcards, and complex query patterns.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service configured
    /// - Sample index with data (from previous modules)
    /// - Configuration set up in appsettings.json or environment variables
    /// 
    /// Author: Azure AI Search Tutorial
    /// </summary>
    public class AdvancedQueries
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public AdvancedQueries()
        {
            // Load configuration
            _configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json", optional: true)
                .AddEnvironmentVariables()
                .Build();

            // Initialize search client
            _searchClient = CreateSearchClient();
        }

        /// <summary>
        /// Create and return an Azure AI Search client.
        /// </summary>
        /// <returns>Configured SearchClient</returns>
        private SearchClient CreateSearchClient()
        {
            var serviceEndpoint = _configuration["AzureSearch:ServiceEndpoint"] ?? 
                                 Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT");
            var apiKey = _configuration["AzureSearch:ApiKey"] ?? 
                        Environment.GetEnvironmentVariable("AZURE_SEARCH_API_KEY");
            var indexName = _configuration["AzureSearch:IndexName"] ?? 
                           Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX_NAME");

            if (string.IsNullOrEmpty(serviceEndpoint) || string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(indexName))
            {
                throw new InvalidOperationException("Missing required configuration. Check your appsettings.json or environment variables.");
            }

            var serviceUri = new Uri(serviceEndpoint);
            var credential = new AzureKeyCredential(apiKey);

            return new SearchClient(serviceUri, indexName, credential);
        }

        /// <summary>
        /// Display search results in a formatted way.
        /// </summary>
        /// <param name="results">Search results</param>
        /// <param name="title">Title for the result set</param>
        /// <param name="maxResults">Maximum number of results to display</param>
        public static void DisplayResults(SearchResults<SearchDocument> results, string title, int maxResults = 5)
        {
            Console.WriteLine($"\n{new string('=', 60)}");
            Console.WriteLine(title);
            Console.WriteLine(new string('=', 60));

            var resultList = results.GetResults().Take(maxResults).ToList();

            if (!resultList.Any())
            {
                Console.WriteLine("No results found.");
                return;
            }

            for (int i = 0; i < resultList.Count; i++)
            {
                var result = resultList[i];
                var document = result.Document;

                Console.WriteLine($"\n{i + 1}. {document.GetValueOrDefault("title", "No title")}");
                Console.WriteLine($"   Score: {result.Score:F4}");
                Console.WriteLine($"   Category: {document.GetValueOrDefault("category", "N/A")}");
                Console.WriteLine($"   Rating: {document.GetValueOrDefault("rating", "N/A")}");

                // Show content preview
                var content = document.GetValueOrDefault("content", "")?.ToString();
                if (!string.IsNullOrEmpty(content))
                {
                    var preview = content.Length > 100 ? content.Substring(0, 100) + "..." : content;
                    Console.WriteLine($"   Preview: {preview}");
                }
            }

            if (results.GetResults().Count() > maxResults)
            {
                Console.WriteLine($"\n... and {results.GetResults().Count() - maxResults} more results");
            }
        }

        /// <summary>
        /// Demonstrate field boosting to influence relevance scoring.
        /// </summary>
        public async Task FieldBoostingExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("FIELD BOOSTING EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: No boosting (baseline)
            Console.WriteLine("\n1. No Field Boosting (Baseline)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 5
                };
                searchOptions.SearchFields.Add("title");
                searchOptions.SearchFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("python tutorial", searchOptions);
                DisplayResults(results.Value, "No boosting - equal weight for all fields");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Boost title field
            Console.WriteLine("\n2. Boost Title Field (3x weight)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 5
                };
                searchOptions.SearchFields.Add("title^3"); // Title weighted 3x
                searchOptions.SearchFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("python tutorial", searchOptions);
                DisplayResults(results.Value, "Title boosted 3x - title matches score higher");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Multiple field boosting
            Console.WriteLine("\n3. Multiple Field Boosting");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 5
                };
                searchOptions.SearchFields.Add("title^5"); // Title 5x
                searchOptions.SearchFields.Add("category^2"); // Category 2x
                searchOptions.SearchFields.Add("content"); // Content 1x

                var results = await _searchClient.SearchAsync<SearchDocument>("azure machine learning", searchOptions);
                DisplayResults(results.Value, "Title 5x, category 2x, content 1x");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate fuzzy search for handling typos and variations.
        /// </summary>
        public async Task FuzzySearchExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("FUZZY SEARCH EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Exact match (baseline)
            Console.WriteLine("\n1. Exact Match (Baseline)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Simple,
                    Size = 3
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("machine", searchOptions);
                DisplayResults(results.Value, "Exact match: 'machine'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Fuzzy search with typo
            Console.WriteLine("\n2. Fuzzy Search with Typo");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full, // Requires full Lucene syntax
                    Size = 3
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("machne~", searchOptions); // Typo: missing 'i'
                DisplayResults(results.Value, "Fuzzy search: 'machne~' (should match 'machine')");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Fuzzy search with edit distance
            Console.WriteLine("\n3. Fuzzy Search with Edit Distance");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full,
                    Size = 3
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("learing~2", searchOptions); // Allow up to 2 character differences
                DisplayResults(results.Value, "Fuzzy search: 'learing~2' (should match 'learning')");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate wildcard search patterns.
        /// </summary>
        public async Task WildcardSearchExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("WILDCARD SEARCH EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Suffix wildcard
            Console.WriteLine("\n1. Suffix Wildcard");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions { Size = 5 };
                var results = await _searchClient.SearchAsync<SearchDocument>("develop*", searchOptions); // Matches develop, developer, development, etc.
                DisplayResults(results.Value, "Suffix wildcard: 'develop*'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Prefix wildcard (requires full Lucene)
            Console.WriteLine("\n2. Prefix Wildcard");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full,
                    Size = 5
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*ing", searchOptions); // Matches words ending in 'ing'
                DisplayResults(results.Value, "Prefix wildcard: '*ing'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Middle wildcard
            Console.WriteLine("\n3. Middle Wildcard");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full,
                    Size = 5
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("mach*ne", searchOptions); // Matches machine, etc.
                DisplayResults(results.Value, "Middle wildcard: 'mach*ne'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate complex query combinations.
        /// </summary>
        public async Task ComplexQueryCombinationsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("COMPLEX QUERY COMBINATIONS");
            Console.WriteLine(new string('=', 80));

            // Example 1: Boosting + Fuzzy + Filter
            Console.WriteLine("\n1. Boosting + Fuzzy + Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full,
                    Filter = "rating ge 3.0",
                    Size = 3
                };
                searchOptions.SearchFields.Add("title^3");
                searchOptions.SearchFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("machne~ learing~", searchOptions); // Fuzzy search
                DisplayResults(results.Value, "Fuzzy + boosting + filter combination");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Wildcard + Filter + Sorting
            Console.WriteLine("\n2. Wildcard + Filter + Sorting");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full,
                    Filter = "category eq 'Technology'",
                    Size = 3
                };
                searchOptions.OrderBy.Add("rating desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("develop* AND tutorial", searchOptions); // Wildcard + AND
                DisplayResults(results.Value, "Wildcard + filter + sorting");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Multiple techniques with highlighting
            Console.WriteLine("\n3. Multiple Techniques + Highlighting");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full,
                    Filter = "category eq 'Technology'",
                    Size = 3
                };
                searchOptions.SearchFields.Add("title^2");
                searchOptions.SearchFields.Add("content");
                searchOptions.HighlightFields.Add("title");
                searchOptions.HighlightFields.Add("content");
                searchOptions.OrderBy.Add("@search.score desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("python* OR java*", searchOptions); // Wildcard OR
                DisplayResults(results.Value, "Complex combination with highlighting");

                // Show highlights
                var resultList = results.Value.GetResults().Take(2).ToList();
                for (int i = 0; i < resultList.Count; i++)
                {
                    var result = resultList[i];
                    if (result.Document.ContainsKey("@search.highlights"))
                    {
                        Console.WriteLine($"\nHighlights for result {i + 1}:");
                        var highlights = result.Document["@search.highlights"] as IDictionary<string, object>;
                        if (highlights != null)
                        {
                            foreach (var highlight in highlights.Take(2))
                            {
                                if (highlight.Value is IEnumerable<object> highlightList)
                                {
                                    foreach (var item in highlightList.Take(1))
                                    {
                                        Console.WriteLine($"  {highlight.Key}: {item}");
                                    }
                                }
                            }
                        }
                    }
                }
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Analyze performance of different advanced query techniques.
        /// </summary>
        public async Task QueryPerformanceAnalysisAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("QUERY PERFORMANCE ANALYSIS");
            Console.WriteLine(new string('=', 80));

            var queries = new[]
            {
                ("Simple text", "azure machine learning", SearchQueryType.Simple),
                ("Wildcard", "develop*", SearchQueryType.Simple),
                ("Fuzzy", "machne~ learing~", SearchQueryType.Full),
                ("Complex", "python* AND tutorial", SearchQueryType.Full)
            };

            Console.WriteLine("\nPerformance Comparison:");
            Console.WriteLine(new string('-', 40));

            foreach (var (name, query, queryType) in queries)
            {
                try
                {
                    var startTime = DateTime.Now;

                    var searchOptions = new SearchOptions
                    {
                        QueryType = queryType,
                        Size = 10
                    };

                    var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                    var resultList = results.Value.GetResults().ToList();

                    var executionTime = DateTime.Now - startTime;

                    Console.WriteLine($"{name,-15} | {executionTime.TotalMilliseconds,6:F0}ms | {resultList.Count,3} results | {query}");
                }
                catch (RequestFailedException ex)
                {
                    Console.WriteLine($"{name,-15} | ERROR   | {ex.Message.Substring(0, Math.Min(50, ex.Message.Length))}...");
                }
            }

            Console.WriteLine("\nPerformance Tips:");
            Console.WriteLine("• Simple queries are fastest");
            Console.WriteLine("• Wildcard queries are moderately fast");
            Console.WriteLine("• Fuzzy queries add processing overhead");
            Console.WriteLine("• Complex combinations multiply overhead");
        }

        /// <summary>
        /// Main method to run all advanced query examples.
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Azure AI Search - Advanced Queries Examples");
            Console.WriteLine(new string('=', 80));

            try
            {
                var advancedQueries = new AdvancedQueries();

                Console.WriteLine($"✅ Connected to search service");
                Console.WriteLine($"✅ Using configured index");

                // Run examples
                await advancedQueries.FieldBoostingExamplesAsync();
                await advancedQueries.FuzzySearchExamplesAsync();
                await advancedQueries.WildcardSearchExamplesAsync();
                await advancedQueries.ComplexQueryCombinationsAsync();
                await advancedQueries.QueryPerformanceAnalysisAsync();

                Console.WriteLine("\n" + new string('=', 80));
                Console.WriteLine("✅ All advanced query examples completed successfully!");
                Console.WriteLine(new string('=', 80));

                Console.WriteLine("\n📚 What you learned:");
                Console.WriteLine("• How to use field boosting to influence relevance");
                Console.WriteLine("• How to implement fuzzy search for typo tolerance");
                Console.WriteLine("• How to use wildcard patterns for flexible matching");
                Console.WriteLine("• How to combine multiple advanced techniques");
                Console.WriteLine("• How to analyze and optimize query performance");

                Console.WriteLine("\n🔗 Next steps:");
                Console.WriteLine("• Run 06_ErrorHandling.cs to learn robust query implementation");
                Console.WriteLine("• Experiment with different boosting values");
                Console.WriteLine("• Try complex query combinations with your data");
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                Console.WriteLine("\n🔧 Setup required:");
                Console.WriteLine("1. Create an appsettings.json file with your Azure AI Search credentials");
                Console.WriteLine("2. Or set environment variables for the search service configuration");
                Console.WriteLine("3. Ensure you have completed previous modules to create sample indexes");
                Environment.Exit(1);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Unexpected error: {ex.Message}");
                Environment.Exit(1);
            }
        }
    }
}