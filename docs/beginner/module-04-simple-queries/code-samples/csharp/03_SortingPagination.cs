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
    /// Module 4: Simple Queries and Filters - Sorting and Pagination
    /// 
    /// This class demonstrates sorting and pagination in Azure AI Search using C#.
    /// Learn how to order results and efficiently navigate through large result sets.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service configured
    /// - Sample index with data (from previous modules)
    /// - Configuration set up in appsettings.json or environment variables
    /// 
    /// Author: Azure AI Search Tutorial
    /// </summary>
    public class SortingPagination
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        public SortingPagination()
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
                Console.WriteLine($"   Price: ${document.GetValueOrDefault("price", "N/A")}");
            }

            if (results.GetResults().Count() > maxResults)
            {
                Console.WriteLine($"\n... and {results.GetResults().Count() - maxResults} more results");
            }
        }

        /// <summary>
        /// Demonstrate basic sorting operations.
        /// </summary>
        public async Task BasicSortingAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("BASIC SORTING EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Sort by relevance score (default)
            Console.WriteLine("\n1. Default Sorting (Relevance Score)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions { Size = 5 };
                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                DisplayResults(results.Value, "Default sort by relevance score");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Sort by date (descending - newest first)
            Console.WriteLine("\n2. Sort by Date (Newest First)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 5
                };
                searchOptions.OrderBy.Add("publishedDate desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Sort by publishedDate desc");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 3: Sort by rating (highest first)
            Console.WriteLine("\n3. Sort by Rating (Highest First)");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 5
                };
                searchOptions.OrderBy.Add("rating desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Sort by rating desc");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate multi-field sorting operations.
        /// </summary>
        public async Task MultiFieldSortingAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("MULTI-FIELD SORTING EXAMPLES");
            Console.WriteLine(new string('=', 80));

            // Example 1: Sort by category, then by rating
            Console.WriteLine("\n1. Sort by Category, then Rating");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 8
                };
                searchOptions.OrderBy.Add("category asc");
                searchOptions.OrderBy.Add("rating desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Sort by category asc, rating desc", 8);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Sort by rating, then by date
            Console.WriteLine("\n2. Sort by Rating, then Date");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = 8
                };
                searchOptions.OrderBy.Add("rating desc");
                searchOptions.OrderBy.Add("publishedDate desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, "Sort by rating desc, publishedDate desc", 8);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate basic pagination operations.
        /// </summary>
        public async Task BasicPaginationAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("BASIC PAGINATION EXAMPLES");
            Console.WriteLine(new string('=', 80));

            int pageSize = 3;

            // Example 1: First page
            Console.WriteLine("\n1. First Page");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = pageSize,
                    Skip = 0
                };
                searchOptions.OrderBy.Add("publishedDate desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, $"Page 1 (size {pageSize}, skip 0)", pageSize);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }

            // Example 2: Second page
            Console.WriteLine("\n2. Second Page");
            Console.WriteLine(new string('-', 40));

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = pageSize,
                    Skip = pageSize // Skip first page
                };
                searchOptions.OrderBy.Add("publishedDate desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                DisplayResults(results.Value, $"Page 2 (size {pageSize}, skip {pageSize})", pageSize);
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate pagination with total count for building navigation.
        /// </summary>
        public async Task PaginationWithTotalCountAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("PAGINATION WITH TOTAL COUNT");
            Console.WriteLine(new string('=', 80));

            int pageSize = 5;

            try
            {
                // Get first page with total count
                var searchOptions = new SearchOptions
                {
                    Size = pageSize,
                    Skip = 0,
                    IncludeTotalCount = true
                };
                searchOptions.OrderBy.Add("rating desc");

                var results = await _searchClient.SearchAsync<SearchDocument>("azure", searchOptions);
                var resultList = results.Value.GetResults().ToList();
                var totalCount = results.Value.TotalCount;
                var totalPages = totalCount.HasValue ? (int)Math.Ceiling((double)totalCount.Value / pageSize) : 0;

                Console.WriteLine($"\nPagination Summary:");
                Console.WriteLine($"Total documents: {totalCount}");
                Console.WriteLine($"Page size: {pageSize}");
                Console.WriteLine($"Total pages: {totalPages}");
                Console.WriteLine($"Current page: 1");

                DisplayResults(results.Value, $"Page 1 of {totalPages}");

                // Show pagination navigation info
                Console.WriteLine($"\nNavigation:");
                Console.WriteLine($"• Previous: N/A (first page)");
                Console.WriteLine($"• Next: Page 2 (skip={pageSize})");
                Console.WriteLine($"• Last: Page {totalPages} (skip={pageSize * (totalPages - 1)})");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Search failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrate advanced pagination patterns and utilities.
        /// </summary>
        public async Task AdvancedPaginationPatternsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("ADVANCED PAGINATION PATTERNS");
            Console.WriteLine(new string('=', 80));

            // Helper method for paginated search
            async Task<PaginationResult> PaginatedSearchAsync(string query, int page = 1, int pageSize = 5, 
                                                            string[] orderBy = null, string filter = null)
            {
                int skip = (page - 1) * pageSize;

                var searchOptions = new SearchOptions
                {
                    Size = pageSize,
                    Skip = skip,
                    IncludeTotalCount = true
                };

                if (orderBy != null)
                {
                    foreach (var order in orderBy)
                    {
                        searchOptions.OrderBy.Add(order);
                    }
                }

                if (!string.IsNullOrEmpty(filter))
                {
                    searchOptions.Filter = filter;
                }

                try
                {
                    var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                    var resultList = results.Value.GetResults().ToList();
                    var totalCount = results.Value.TotalCount ?? 0;
                    var totalPages = (int)Math.Ceiling((double)totalCount / pageSize);

                    return new PaginationResult
                    {
                        Results = resultList,
                        CurrentPage = page,
                        PageSize = pageSize,
                        TotalCount = totalCount,
                        TotalPages = totalPages,
                        HasPrevious = page > 1,
                        HasNext = page < totalPages,
                        PreviousPage = page > 1 ? page - 1 : (int?)null,
                        NextPage = page < totalPages ? page + 1 : (int?)null
                    };
                }
                catch (RequestFailedException ex)
                {
                    return new PaginationResult
                    {
                        Results = new List<SearchResult<SearchDocument>>(),
                        Error = ex.Message
                    };
                }
            }

            // Example 1: Page 1
            Console.WriteLine("\n1. Advanced Pagination - Page 1");
            Console.WriteLine(new string('-', 40));

            var result = await PaginatedSearchAsync(
                query: "azure",
                page: 1,
                pageSize: 3,
                orderBy: new[] { "rating desc" }
            );

            if (string.IsNullOrEmpty(result.Error))
            {
                Console.WriteLine($"Page {result.CurrentPage} of {result.TotalPages} (Total: {result.TotalCount} results)");
                
                for (int i = 0; i < result.Results.Count; i++)
                {
                    var doc = result.Results[i].Document;
                    Console.WriteLine($"\n{i + 1}. {doc.GetValueOrDefault("title", "No title")}");
                    Console.WriteLine($"   Rating: {doc.GetValueOrDefault("rating", "N/A")}");
                }

                Console.WriteLine($"\nPagination Info:");
                Console.WriteLine($"• Has previous: {result.HasPrevious}");
                Console.WriteLine($"• Has next: {result.HasNext}");
                Console.WriteLine($"• Previous page: {result.PreviousPage}");
                Console.WriteLine($"• Next page: {result.NextPage}");
            }
            else
            {
                Console.WriteLine($"Error: {result.Error}");
            }
        }

        /// <summary>
        /// Main method to run all sorting and pagination examples.
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Azure AI Search - Sorting and Pagination Examples");
            Console.WriteLine(new string('=', 80));

            try
            {
                var sortingPagination = new SortingPagination();

                Console.WriteLine($"✅ Connected to search service");
                Console.WriteLine($"✅ Using configured index");

                // Run examples
                await sortingPagination.BasicSortingAsync();
                await sortingPagination.MultiFieldSortingAsync();
                await sortingPagination.BasicPaginationAsync();
                await sortingPagination.PaginationWithTotalCountAsync();
                await sortingPagination.AdvancedPaginationPatternsAsync();

                Console.WriteLine("\n" + new string('=', 80));
                Console.WriteLine("✅ All sorting and pagination examples completed successfully!");
                Console.WriteLine(new string('=', 80));

                Console.WriteLine("\n📚 What you learned:");
                Console.WriteLine("• How to sort results by single and multiple fields");
                Console.WriteLine("• How to combine sorting with search and filters");
                Console.WriteLine("• How to implement basic and advanced pagination");
                Console.WriteLine("• How to get total counts for navigation");
                Console.WriteLine("• How to optimize sorting performance");

                Console.WriteLine("\n🔗 Next steps:");
                Console.WriteLine("• Run 04_ResultCustomization.cs to learn about field selection");
                Console.WriteLine("• Experiment with different sort combinations");
                Console.WriteLine("• Build pagination UI components");
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
    /// Helper class for pagination results.
    /// </summary>
    public class PaginationResult
    {
        public List<SearchResult<SearchDocument>> Results { get; set; } = new List<SearchResult<SearchDocument>>();
        public int CurrentPage { get; set; }
        public int PageSize { get; set; }
        public long TotalCount { get; set; }
        public int TotalPages { get; set; }
        public bool HasPrevious { get; set; }
        public bool HasNext { get; set; }
        public int? PreviousPage { get; set; }
        public int? NextPage { get; set; }
        public string Error { get; set; }
    }
}