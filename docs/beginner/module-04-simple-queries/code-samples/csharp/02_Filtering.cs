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
    /// Module 4: Simple Queries and Filters - Filtering
    /// 
    /// This class demonstrates OData filter expressions in Azure AI Search using C#.
    /// Learn how to apply filters to narrow search results based on specific criteria.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service configured
    /// - Sample index with data (from previous modules)
    /// - Configuration set up in appsettings.json or environment variables
    /// 
    /// Author: Azure AI Search Tutorial
    /// </summary>
    public class Filtering
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public Filtering()
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
                Console.WriteLine($"   Category: {document.GetValueOrDefault("category", "N/A")}");
                Console.WriteLine($"   Rating: {document.GetValueOrDefault("rating", "N/A")}");
                Console.WriteLine($"   Published: {document.GetValueOrDefault("publishedDate", "N/A")}");

                // Show tags if available
                var tags = document.GetValueOrDefault("tags", null);
                if (tags is IEnumerable<object> tagList)
                {
                    var tagStrings = tagList.Take(3).Select(t => t.ToString());
                    var tagsDisplay = string.Join(", ", tagStrings);
                    if (tagList.Count() > 3) tagsDisplay += "...";
                    Console.WriteLine($"   Tags: {tagsDisplay}");
                }
            }

            if (results.GetResults().Count() > maxResults)
            {
                Console.WriteLine($"\n... and {results.GetResults().Count() - maxResults} more results");
            }
        }

        /// <summary>
        /// Demonstrate equality filter operations.
        /// </summary>
        public async Task EqualityFiltersAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("EQUALITY FILTER EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Exact string match
            Console.WriteLine("\n1. Exact String Match");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category eq 'Technology'"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: category eq 'Technology'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Not equal filter
            Console.WriteLine("\n2. Not Equal Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category ne 'Draft'",
                    Size = 5
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: category ne 'Draft'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Combining search with filter
            Console.WriteLine("\n3. Search Text with Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category eq 'Technology'"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "Search: 'azure' + Filter: category eq 'Technology'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate comparison filter operations.
        /// </summary>
        public async Task ComparisonFiltersAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("COMPARISON FILTER EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Greater than
            Console.WriteLine("\n1. Greater Than Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "rating gt 4.0"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: rating gt 4.0");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Greater than or equal
            Console.WriteLine("\n2. Greater Than or Equal Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "rating ge 4.5"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: rating ge 4.5");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Less than
            Console.WriteLine("\n3. Less Than Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "rating lt 3.0"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: rating lt 3.0");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 4: Range filter (between values)
            Console.WriteLine("\n4. Range Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "rating ge 3.0 and rating le 4.0"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: rating between 3.0 and 4.0");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate logical operators in filters.
        /// </summary>
        public async Task LogicalOperatorsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("LOGICAL OPERATORS IN FILTERS");
            Console.WriteLine(new string('=', 80));

            // Example 1: AND operator
            Console.WriteLine("\n1. AND Operator");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category eq 'Technology' and rating ge 4.0"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: category eq 'Technology' AND rating ge 4.0");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: OR operator
            Console.WriteLine("\n2. OR Operator");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category eq 'Technology' or category eq 'Science'"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: category eq 'Technology' OR category eq 'Science'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: NOT operator
            Console.WriteLine("\n3. NOT Operator");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "not (category eq 'Draft')"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: NOT (category eq 'Draft')");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 4: Complex logical expression
            Console.WriteLine("\n4. Complex Logical Expression");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "(category eq 'Technology' or category eq 'Science') and rating gt 3.5"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: (Technology OR Science) AND rating > 3.5");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate date filtering operations.
        /// </summary>
        public async Task DateFiltersAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("DATE FILTER EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Documents published after a specific date
            Console.WriteLine("\n1. Published After Date");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "publishedDate ge 2023-01-01T00:00:00Z"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: publishedDate ge 2023-01-01T00:00:00Z");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Documents published before a specific date
            Console.WriteLine("\n2. Published Before Date");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "publishedDate lt 2024-01-01T00:00:00Z"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: publishedDate lt 2024-01-01T00:00:00Z");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Date range filter
            Console.WriteLine("\n3. Date Range Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "publishedDate ge 2023-01-01T00:00:00Z and publishedDate le 2023-12-31T23:59:59Z"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: published in 2023");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 4: Recent documents (last 30 days)
            Console.WriteLine("\n4. Recent Documents");
            Console.WriteLine(new string('-', 40));

            try
            {
                var thirtyDaysAgo = DateTime.UtcNow.AddDays(-30);
                var recentDate = thirtyDaysAgo.ToString("yyyy-MM-ddTHH:mm:ssZ");

                var searchOptions = new SearchOptions
                {
                    Filter = $"publishedDate ge {recentDate}"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: published in last 30 days");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate filtering on collection fields (arrays).
        /// </summary>
        public async Task CollectionFiltersAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("COLLECTION FILTER EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Any element matches (tags/any)
            Console.WriteLine("\n1. Any Element Matches");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "tags/any(t: t eq 'python')"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: tags/any(t: t eq 'python')");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Multiple tag matches
            Console.WriteLine("\n2. Multiple Tag Options");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "tags/any(t: t eq 'python' or t eq 'javascript')"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: tags contain 'python' OR 'javascript'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: All elements match condition
            Console.WriteLine("\n3. All Elements Match");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "tags/all(t: t ne 'deprecated')"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: all tags are not 'deprecated'");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 4: Complex collection filter
            Console.WriteLine("\n4. Complex Collection Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "tags/any(t: t eq 'tutorial') and rating ge 4.0"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Filter: has 'tutorial' tag AND rating >= 4.0");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate filter validation and error handling.
        /// </summary>
        public async Task FilterValidationExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("FILTER VALIDATION EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Valid filter
            Console.WriteLine("\n1. Valid Filter");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category eq 'Technology'"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                var resultCount = results.Value.GetResults().Count();
                Console.WriteLine($"✅ Valid filter executed successfully: {resultCount} results");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Filter failed: {ex.Message}");
            }

            // Example 2: Invalid field name
            Console.WriteLine("\n2. Invalid Field Name");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "nonexistent_field eq 'value'"
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                var resultCount = results.Value.GetResults().Count();
                Console.WriteLine($"Results: {resultCount}");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Expected error - Invalid field: {ex.Message}");
            }

            // Example 3: Invalid syntax
            Console.WriteLine("\n3. Invalid Filter Syntax");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "category = 'Technology'" // Should be 'eq' not '='
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                var resultCount = results.Value.GetResults().Count();
                Console.WriteLine($"Results: {resultCount}");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Expected error - Invalid syntax: {ex.Message}");
            }

            // Example 4: Type mismatch
            Console.WriteLine("\n4. Type Mismatch");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Filter = "rating eq 'high'" // Should be numeric, not string
                };

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                var resultCount = results.Value.GetResults().Count();
                Console.WriteLine($"Results: {resultCount}");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Expected error - Type mismatch: {ex.Message}");
            }
        }

        /// <summary>
        /// Main method to run all filtering examples.
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Azure AI Search - Filtering Examples");
            Console.WriteLine(new string('=', 80));

            try
            {
                var filtering = new Filtering();

                Console.WriteLine($"✅ Connected to search service");
                Console.WriteLine($"✅ Using configured index");

                // Run examples
                await filtering.EqualityFiltersAsync();
                await filtering.ComparisonFiltersAsync();
                await filtering.LogicalOperatorsAsync();
                await filtering.DateFiltersAsync();
                await filtering.CollectionFiltersAsync();
                await filtering.FilterValidationExamplesAsync();

                Console.WriteLine("\n" + new string('=', 80));
                Console.WriteLine("✅ All filtering examples completed successfully!");
                Console.WriteLine(new string('=', 80));

                Console.WriteLine("\n📚 What you learned:");
                Console.WriteLine("• How to use equality and comparison operators");
                Console.WriteLine("• How to combine filters with logical operators");
                Console.WriteLine("• How to filter by dates and numeric ranges");
                Console.WriteLine("• How to work with collection fields");
                Console.WriteLine("• How to handle filter validation and errors");

                Console.WriteLine("\n🔗 Next steps:");
                Console.WriteLine("• Run 03_SortingPagination.cs to learn about result ordering");
                Console.WriteLine("• Experiment with complex filter combinations");
                Console.WriteLine("• Try filters with your own data fields");
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