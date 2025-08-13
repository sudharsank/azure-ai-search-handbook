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
    /// Module 4: Simple Queries and Filters - Result Customization
    /// 
    /// This class demonstrates result customization in Azure AI Search using C#.
    /// Learn how to select specific fields, highlight matching terms, and format results.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service configured
    /// - Sample index with data (from previous modules)
    /// - Configuration set up in appsettings.json or environment variables
    /// 
    /// Author: Azure AI Search Tutorial
    /// </summary>
    public class ResultCustomization
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public ResultCustomization()
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
        /// Display search results in a formatted way with highlighting support.
        /// </summary>
        /// <param name="results">Search results</param>
        /// <param name="title">Title for the result set</param>
        /// <param name="maxResults">Maximum number of results to display</param>
        /// <param name="showHighlights">Whether to display highlight information</param>
        public static void DisplayResults(SearchResults<SearchDocument> results, string title, 
                                        int maxResults = 5, bool showHighlights = false)
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

                // Show selected fields
                foreach (var kvp in document)
                {
                    if (!kvp.Key.StartsWith("@search") && kvp.Key != "title")
                    {
                        var value = kvp.Value;
                        if (value is IEnumerable<object> list && !(value is string))
                        {
                            var items = list.Take(3).Select(x => x.ToString());
                            var display = string.Join(", ", items);
                            if (list.Count() > 3) display += "...";
                            Console.WriteLine($"   {kvp.Key}: {display}");
                        }
                        else if (value is string str && str.Length > 100)
                        {
                            Console.WriteLine($"   {kvp.Key}: {str.Substring(0, 100)}...");
                        }
                        else
                        {
                            Console.WriteLine($"   {kvp.Key}: {value}");
                        }
                    }
                }

                // Show highlights if requested and available
                if (showHighlights && document.ContainsKey("@search.highlights"))
                {
                    var highlights = document["@search.highlights"] as IDictionary<string, object>;
                    if (highlights != null)
                    {
                        Console.WriteLine("   Highlights:");
                        foreach (var highlight in highlights)
                        {
                            if (highlight.Value is IEnumerable<object> highlightList)
                            {
                                foreach (var item in highlightList.Take(2))
                                {
                                    Console.WriteLine($"     {highlight.Key}: {item}");
                                }
                            }
                        }
                    }
                }
            }

            if (results.GetResults().Count() > maxResults)
            {
                Console.WriteLine($"\n... and {results.GetResults().Count() - maxResults} more results");
            }
        }

        /// <summary>
        /// Demonstrate field selection to customize returned data.
        /// </summary>
        public async Task FieldSelectionExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("FIELD SELECTION EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: All fields (default behavior)
            Console.WriteLine("\n1. All Fields (Default)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions { Size = 2 };
                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "All fields returned", 2);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Select specific fields
            Console.WriteLine("\n2. Select Specific Fields");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 3
                };
                searchOptions.Select.Add("id");
                searchOptions.Select.Add("title");
                searchOptions.Select.Add("category");
                searchOptions.Select.Add("rating");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "Selected fields: id, title, category, rating", 3);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Minimal field selection for performance
            Console.WriteLine("\n3. Minimal Fields for Performance");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 5
                };
                searchOptions.Select.Add("id");
                searchOptions.Select.Add("title");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "Minimal fields: id, title only", 5);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate search result highlighting.
        /// </summary>
        public async Task SearchHighlightingExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("SEARCH HIGHLIGHTING EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Basic highlighting
            Console.WriteLine("\n1. Basic Highlighting");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 3
                };
                searchOptions.HighlightFields.Add("title");
                searchOptions.HighlightFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("machine learning", searchOptions);
                DisplayResults(results.Value, "Basic highlighting on title and content", 3, true);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Custom highlight tags
            Console.WriteLine("\n2. Custom Highlight Tags");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 3,
                    HighlightPreTag = "<mark>",
                    HighlightPostTag = "</mark>"
                };
                searchOptions.HighlightFields.Add("title");
                searchOptions.HighlightFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure search", searchOptions);
                DisplayResults(results.Value, "Custom highlight tags: <mark>...</mark>", 3, true);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Highlighting with field selection
            Console.WriteLine("\n3. Highlighting with Field Selection");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 3,
                    HighlightPreTag = "**",
                    HighlightPostTag = "**"
                };
                searchOptions.Select.Add("id");
                searchOptions.Select.Add("title");
                searchOptions.Select.Add("category");
                searchOptions.HighlightFields.Add("title");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure cognitive", searchOptions);
                DisplayResults(results.Value, "Selected fields + title highlighting", 3, true);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate working with search result metadata.
        /// </summary>
        public async Task ResultMetadataExamplesAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("RESULT METADATA EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Search score analysis
            Console.WriteLine("\n1. Search Score Analysis");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions { Size = 5 };
                var results = await _searchClient.SearchAsync<SearchDocument>("azure machine learning", searchOptions);
                var resultList = results.Value.GetResults().ToList();

                Console.WriteLine("Search Score Analysis:");
                Console.WriteLine(new string('-', 30));
                for (int i = 0; i < resultList.Count; i++)
                {
                    var result = resultList[i];
                    var score = result.Score;
                    var title = result.Document.GetValueOrDefault("title", "No title").ToString();
                    Console.WriteLine($"{i + 1}. Score: {score:F4} - {title.Substring(0, Math.Min(50, title.Length))}...");
                }

                if (resultList.Any())
                {
                    var scores = resultList.Select(r => r.Score).ToList();
                    Console.WriteLine($"\nScore Statistics:");
                    Console.WriteLine($"• Highest: {scores.Max():F4}");
                    Console.WriteLine($"• Lowest: {scores.Min():F4}");
                    Console.WriteLine($"• Average: {scores.Average():F4}");
                }
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate custom result formatting and processing.
        /// </summary>
        public async Task CustomResultFormattingAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("CUSTOM RESULT FORMATTING");
            Console.WriteLine(new string('=', 80));

            // Custom formatter method
            CustomSearchResult FormatSearchResult(SearchResult<SearchDocument> result)
            {
                var document = result.Document;
                var formatted = new CustomSearchResult
                {
                    Id = document.GetValueOrDefault("id")?.ToString(),
                    Title = document.GetValueOrDefault("title")?.ToString() ?? "Untitled",
                    Summary = GetContentSummary(document.GetValueOrDefault("content")?.ToString()),
                    Metadata = new SearchMetadata
                    {
                        Score = Math.Round(result.Score, 3),
                        Category = document.GetValueOrDefault("category")?.ToString() ?? "Uncategorized",
                        Rating = document.GetValueOrDefault("rating"),
                        Published = document.GetValueOrDefault("publishedDate"),
                        Tags = GetTags(document.GetValueOrDefault("tags"))
                    }
                };

                // Add highlights if available
                if (document.ContainsKey("@search.highlights"))
                {
                    formatted.Highlights = new Dictionary<string, List<string>>();
                    var highlights = document["@search.highlights"] as IDictionary<string, object>;
                    if (highlights != null)
                    {
                        foreach (var highlight in highlights)
                        {
                            if (highlight.Value is IEnumerable<object> highlightList)
                            {
                                formatted.Highlights[highlight.Key] = highlightList.Take(2).Select(x => x.ToString()).ToList();
                            }
                        }
                    }
                }

                return formatted;
            }

            // Example 1: Custom formatted results
            Console.WriteLine("\n1. Custom Formatted Results");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 3
                };
                searchOptions.Select.Add("id");
                searchOptions.Select.Add("title");
                searchOptions.Select.Add("content");
                searchOptions.Select.Add("category");
                searchOptions.Select.Add("rating");
                searchOptions.Select.Add("publishedDate");
                searchOptions.Select.Add("tags");
                searchOptions.HighlightFields.Add("title");
                searchOptions.HighlightFields.Add("content");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure tutorial", searchOptions);
                var resultList = results.Value.GetResults().ToList();
                var formattedResults = resultList.Select(FormatSearchResult).ToList();

                Console.WriteLine("Custom Formatted Results:");
                for (int i = 0; i < formattedResults.Count; i++)
                {
                    var result = formattedResults[i];
                    Console.WriteLine($"\n{i + 1}. {result.Title}");
                    Console.WriteLine($"   Summary: {result.Summary}");
                    Console.WriteLine($"   Score: {result.Metadata.Score}");
                    Console.WriteLine($"   Category: {result.Metadata.Category}");
                    Console.WriteLine($"   Rating: {result.Metadata.Rating}");
                    Console.WriteLine($"   Tags: {string.Join(", ", result.Metadata.Tags)}");

                    if (result.Highlights?.Any() == true)
                    {
                        Console.WriteLine($"   Highlights: {result.Highlights.Count} fields");
                    }
                }
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Helper method to get content summary.
        /// </summary>
        private string GetContentSummary(string content)
        {
            if (string.IsNullOrEmpty(content))
                return "";

            return content.Length > 150 ? content.Substring(0, 150) + "..." : content;
        }

        /// <summary>
        /// Helper method to get tags list.
        /// </summary>
        private List<string> GetTags(object tagsObj)
        {
            if (tagsObj is IEnumerable<object> tags)
            {
                return tags.Take(5).Select(t => t.ToString()).ToList();
            }
            return new List<string>();
        }

        /// <summary>
        /// Main method to run all result customization examples.
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Azure AI Search - Result Customization Examples");
            Console.WriteLine(new string('=', 80));

            try
            {
                var resultCustomization = new ResultCustomization();

                Console.WriteLine($"✅ Connected to search service");
                Console.WriteLine($"✅ Using configured index");

                // Run examples
                await resultCustomization.FieldSelectionExamplesAsync();
                await resultCustomization.SearchHighlightingExamplesAsync();
                await resultCustomization.ResultMetadataExamplesAsync();
                await resultCustomization.CustomResultFormattingAsync();

                Console.WriteLine("\n" + new string('=', 80));
                Console.WriteLine("✅ All result customization examples completed successfully!");
                Console.WriteLine(new string('=', 80));

                Console.WriteLine("\n📚 What you learned:");
                Console.WriteLine("• How to select specific fields to optimize performance");
                Console.WriteLine("• How to implement search result highlighting");
                Console.WriteLine("• How to work with search metadata and scores");
                Console.WriteLine("• How to format and process results for different use cases");

                Console.WriteLine("\n🔗 Next steps:");
                Console.WriteLine("• Run 05_AdvancedQueries.cs to learn advanced query techniques");
                Console.WriteLine("• Experiment with different field combinations");
                Console.WriteLine("• Build custom result formatters for your applications");
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

    /// <summary>
    /// Custom search result class for formatted output.
    /// </summary>
    public class CustomSearchResult
    {
        public string Id { get; set; }
        public string Title { get; set; }
        public string Summary { get; set; }
        public SearchMetadata Metadata { get; set; }
        public Dictionary<string, List<string>> Highlights { get; set; }
    }

    /// <summary>
    /// Search metadata class.
    /// </summary>
    public class SearchMetadata
    {
        public double Score { get; set; }
        public string Category { get; set; }
        public object Rating { get; set; }
        public object Published { get; set; }
        public List<string> Tags { get; set; } = new List<string>();
    }
}