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
    /// Module 4: Simple Queries and Filters - Basic Queries
    /// 
    /// This class demonstrates basic text search operations in Azure AI Search using C#.
    /// Learn how to perform simple searches, use query operators, and work with search fields.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service configured
    /// - Sample index with data (from previous modules)
    /// - Configuration set up in appsettings.json or environment variables
    /// 
    /// Author: Azure AI Search Tutorial
    /// </summary>
    public class BasicQueries
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public BasicQueries()
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
                Console.WriteLine($"   Score: {result.Score:F2}");
                Console.WriteLine($"   ID: {document.GetValueOrDefault("id", "N/A")}");

                // Show content preview if available
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
        /// Demonstrate basic text search operations.
        /// </summary>
        public async Task BasicTextSearchAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("BASIC TEXT SEARCH EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Simple text search
            Console.WriteLine("\n1. Simple Text Search");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions();
                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "Search: 'azure'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
                return;
            }

            // Example 2: Multi-word search
            Console.WriteLine("\n2. Multi-word Search");
            Console.WriteLine(new string('-', 40));

            try
            {
                var results = await _searchClient.SearchAsync<SearchDocument>("machine learning");
                DisplayResults(results.Value, "Search: 'machine learning'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Empty search (returns all documents)
            Console.WriteLine("\n3. Empty Search (All Documents)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions { Size = 3 };
                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Search: '*' (all documents)", 3);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate searching in specific fields.
        /// </summary>
        public async Task SearchWithFieldsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("FIELD-SPECIFIC SEARCH EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Search in title field only
            Console.WriteLine("\n1. Search in Title Field Only");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions();
                searchOptions.SearchFields.Add("title");

                var results = await _searchClient.SearchAsync<SearchDocument>("python", searchOptions);
                DisplayResults(results.Value, "Search: 'python' in title field");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Search in multiple specific fields
            Console.WriteLine("\n2. Search in Multiple Fields");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions();
                searchOptions.SearchFields.Add("title");
                searchOptions.SearchFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "Search: 'azure' in title and content fields");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Search with field boosting (title field weighted more)
            Console.WriteLine("\n3. Search with Field Boosting");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions();
                searchOptions.SearchFields.Add("title^3"); // Title matches weighted 3x
                searchOptions.SearchFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("tutorial", searchOptions);
                DisplayResults(results.Value, "Search: 'tutorial' with title boosting (3x)");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate query operators in simple syntax.
        /// </summary>
        public async Task QueryOperatorsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("QUERY OPERATORS EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Required term (+)
            Console.WriteLine("\n1. Required Term (+)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var results = await _searchClient.SearchAsync<SearchDocument>("+azure search");
                DisplayResults(results.Value, "Search: '+azure search' (azure is required)");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Excluded term (-)
            Console.WriteLine("\n2. Excluded Term (-)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var results = await _searchClient.SearchAsync<SearchDocument>("azure -cognitive");
                DisplayResults(results.Value, "Search: 'azure -cognitive' (exclude cognitive)");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Exact phrase ("")
            Console.WriteLine("\n3. Exact Phrase Search");
            Console.WriteLine(new string('-', 40));

            try
            {
                var results = await _searchClient.SearchAsync<SearchDocument>("\"machine learning\"");
                DisplayResults(results.Value, "Search: \"machine learning\" (exact phrase)");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 4: Wildcard search (*)
            Console.WriteLine("\n4. Wildcard Search");
            Console.WriteLine(new string('-', 40));

            try
            {
                var results = await _searchClient.SearchAsync<SearchDocument>("develop*");
                DisplayResults(results.Value, "Search: 'develop*' (wildcard)");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 5: Grouping with parentheses
            Console.WriteLine("\n5. Grouping with Parentheses");
            Console.WriteLine(new string('-', 40));

            try
            {
                var results = await _searchClient.SearchAsync<SearchDocument>("(azure OR microsoft) search");
                DisplayResults(results.Value, "Search: '(azure OR microsoft) search'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate different search modes and query types.
        /// </summary>
        public async Task SearchModesAndTypesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("SEARCH MODES AND QUERY TYPES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Any search mode (default)
            Console.WriteLine("\n1. Search Mode: Any (Default)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    SearchMode = SearchMode.Any
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("azure machine learning", searchOptions);
                DisplayResults(results.Value, "Search mode 'any': matches any term");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: All search mode
            Console.WriteLine("\n2. Search Mode: All");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    SearchMode = SearchMode.All
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("azure machine learning", searchOptions);
                DisplayResults(results.Value, "Search mode 'all': matches all terms");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Simple query type (default)
            Console.WriteLine("\n3. Query Type: Simple (Default)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Simple
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("azure AND search", searchOptions);
                DisplayResults(results.Value, "Simple query type with AND operator");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 4: Full Lucene query type
            Console.WriteLine("\n4. Query Type: Full Lucene");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    QueryType = SearchQueryType.Full
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("title:azure AND content:search", searchOptions);
                DisplayResults(results.Value, "Full Lucene query with field-specific search");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate advanced text search features.
        /// </summary>
        public async Task AdvancedTextFeaturesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("ADVANCED TEXT SEARCH FEATURES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Case sensitivity (searches are case-insensitive by default)
            Console.WriteLine("\n1. Case Insensitive Search");
            Console.WriteLine(new string('-', 40));

            try
            {
                var resultsLower = await _searchClient.SearchAsync<SearchDocument>("azure");
                var resultsUpper = await _searchClient.SearchAsync<SearchDocument>("AZURE");

                var lowerCount = resultsLower.Value.GetResults().Count();
                var upperCount = resultsUpper.Value.GetResults().Count();

                Console.WriteLine($"Search 'azure': {lowerCount} results");
                Console.WriteLine($"Search 'AZURE': {upperCount} results");
                Console.WriteLine("Note: Both searches return the same results (case-insensitive)");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Search with Size parameter
            Console.WriteLine("\n2. Search with Size Parameter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 3 // Limit to top 3 results
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("azure machine learning", searchOptions);
                DisplayResults(results.Value, "Top 3 results for 'azure machine learning'", 3);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Include total count
            Console.WriteLine("\n3. Include Total Count");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    IncludeTotalCount = true,
                    Size = 5
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                var resultList = results.Value.GetResults().ToList();
                var totalCount = results.Value.TotalCount;

                Console.WriteLine($"Total matching documents: {totalCount}");
                Console.WriteLine($"Returned documents: {resultList.Count}");
                DisplayResults(results.Value, "Sample results with total count", 3);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate working with search result metadata.
        /// </summary>
        public async Task DemonstrateResultMetadataAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("SEARCH RESULT METADATA");
            Console.WriteLine(new string('=', 80));

            try
            {
                var searchOptions = new SearchOptions { Size = 3 };
                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                var resultList = results.Value.GetResults().ToList();

                Console.WriteLine("\nDetailed Result Analysis:");
                Console.WriteLine(new string('-', 40));

                for (int i = 0; i < resultList.Count; i++)
                {
                    var result = resultList[i];
                    var document = result.Document;

                    Console.WriteLine($"\nResult {i + 1}:");
                    Console.WriteLine($"  Document ID: {document.GetValueOrDefault("id", "N/A")}");
                    Console.WriteLine($"  Search Score: {result.Score:F4}");
                    Console.WriteLine($"  Title: {document.GetValueOrDefault("title", "N/A")}");

                    // Show all available fields
                    Console.WriteLine("  Available fields:");
                    foreach (var kvp in document)
                    {
                        if (!kvp.Key.StartsWith("@search"))
                        {
                            var fieldValue = kvp.Value?.ToString() ?? "null";
                            var fieldPreview = fieldValue.Length > 50 ? fieldValue.Substring(0, 50) + "..." : fieldValue;
                            Console.WriteLine($"    {kvp.Key}: {fieldPreview}");
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
        /// Main method to run all basic query examples.
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Azure AI Search - Basic Queries Examples");
            Console.WriteLine(new string('=', 80));

            try
            {
                var basicQueries = new BasicQueries();

                Console.WriteLine($"✅ Connected to search service");
                Console.WriteLine($"✅ Using configured index");

                // Run examples
                await basicQueries.BasicTextSearchAsync();
                await basicQueries.SearchWithFieldsAsync();
                await basicQueries.QueryOperatorsAsync();
                await basicQueries.SearchModesAndTypesAsync();
                await basicQueries.AdvancedTextFeaturesAsync();
                await basicQueries.DemonstrateResultMetadataAsync();

                Console.WriteLine("\n" + new string('=', 80));
                Console.WriteLine("✅ All basic query examples completed successfully!");
                Console.WriteLine(new string('=', 80));

                Console.WriteLine("\n📚 What you learned:");
                Console.WriteLine("• How to perform simple text searches");
                Console.WriteLine("• How to search in specific fields");
                Console.WriteLine("• How to use query operators (+, -, \"\", *, ())");
                Console.WriteLine("• How to work with search modes and query types");
                Console.WriteLine("• How to access search result metadata");

                Console.WriteLine("\n🔗 Next steps:");
                Console.WriteLine("• Run 02_Filtering.cs to learn about OData filters");
                Console.WriteLine("• Experiment with your own search terms");
                Console.WriteLine("• Try different field combinations");
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