/*
Error Handling - Module 2 C# Examples
Basic error handling for Azure AI Search operations

This module demonstrates:
- Input validation
- Common error handling
- Safe search operations
- Error recovery strategies
- Best practices for error handling
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module02.BasicSearch
{
    /// <summary>
    /// Simple validator for search queries
    /// </summary>
    public static class SearchValidator
    {
        /// <summary>
        /// Validate a search query
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <returns>Tuple of (isValid, errorMessage)</returns>
        public static (bool IsValid, string ErrorMessage) ValidateQuery(string query)
        {
            if (string.IsNullOrEmpty(query))
                return (false, "Search query cannot be empty");

            if (string.IsNullOrWhiteSpace(query))
                return (false, "Search query cannot be just whitespace");

            if (query.Length > 1000)
                return (false, "Search query is too long (max 1000 characters)");

            return (true, null);
        }

        /// <summary>
        /// Basic query sanitization
        /// </summary>
        /// <param name="query">Raw search query</param>
        /// <returns>Sanitized query string</returns>
        public static string SanitizeQuery(string query)
        {
            if (string.IsNullOrEmpty(query))
                return string.Empty;

            // Remove potentially problematic characters
            var sanitized = Regex.Replace(query, @"[<>]", "");

            // Normalize whitespace
            sanitized = Regex.Replace(sanitized, @"\s+", " ").Trim();

            return sanitized;
        }
    }

    /// <summary>
    /// Safe wrapper around SearchClient with error handling
    /// </summary>
    public class SafeSearchClient
    {
        private readonly SearchClient _searchClient;

        public SafeSearchClient(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Perform a safe search with error handling
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="searchOptions">Additional search options</param>
        /// <returns>Tuple of (resultsList, errorMessage)</returns>
        public async Task<(List<SearchResult<SearchDocument>> Results, string ErrorMessage)> SafeSearchAsync(
            string query, SearchOptions searchOptions = null)
        {
            // Validate query
            var (isValid, validationError) = SearchValidator.ValidateQuery(query);
            if (!isValid)
                return (new List<SearchResult<SearchDocument>>(), validationError);

            // Sanitize query
            var sanitizedQuery = SearchValidator.SanitizeQuery(query);

            try
            {
                // Perform search
                var results = await _searchClient.SearchAsync<SearchDocument>(sanitizedQuery, searchOptions);
                var resultList = new List<SearchResult<SearchDocument>>();
                
                await foreach (var result in results.Value.GetResultsAsync())
                {
                    resultList.Add(result);
                }

                Console.WriteLine($"Search successful: '{sanitizedQuery}' returned {resultList.Count} results");
                return (resultList, null);
            }
            catch (RequestFailedException ex)
            {
                var errorMessage = HandleRequestFailedException(ex);
                Console.WriteLine($"HTTP error in search: {errorMessage}");
                return (new List<SearchResult<SearchDocument>>(), errorMessage);
            }
            catch (Exception ex)
            {
                var errorMessage = $"Unexpected error: {ex.Message}";
                Console.WriteLine($"Unexpected error in search: {errorMessage}");
                return (new List<SearchResult<SearchDocument>>(), errorMessage);
            }
        }

        /// <summary>
        /// Handle RequestFailedException with user-friendly messages
        /// </summary>
        /// <param name="ex">The RequestFailedException</param>
        /// <returns>User-friendly error message</returns>
        private string HandleRequestFailedException(RequestFailedException ex)
        {
            return ex.Status switch
            {
                400 => "Invalid query syntax. Please check your search terms.",
                401 => "Authentication failed. Please check your API key.",
                403 => "Access denied. Please check your permissions.",
                404 => "Search index not found. Please verify your index name.",
                429 => "Too many requests. Please wait and try again.",
                503 => "Search service is temporarily unavailable. Please try again later.",
                _ => $"HTTP error {ex.Status}: {ex.Message}"
            };
        }

        /// <summary>
        /// Search with fallback queries if primary search fails or returns no results
        /// </summary>
        /// <param name="query">Primary search query</param>
        /// <param name="fallbackQueries">List of fallback queries to try</param>
        /// <param name="searchOptions">Additional search options</param>
        /// <returns>Tuple of (resultsList, errorMessage)</returns>
        public async Task<(List<SearchResult<SearchDocument>> Results, string ErrorMessage)> SearchWithFallbackAsync(
            string query, List<string> fallbackQueries = null, SearchOptions searchOptions = null)
        {
            // Try primary query first
            var (results, error) = await SafeSearchAsync(query, searchOptions);

            if (results.Any() || fallbackQueries == null || !fallbackQueries.Any())
                return (results, error);

            // Try fallback queries
            foreach (var fallbackQuery in fallbackQueries)
            {
                Console.WriteLine($"Trying fallback query: '{fallbackQuery}'");
                var (fallbackResults, fallbackError) = await SafeSearchAsync(fallbackQuery, searchOptions);

                if (fallbackResults.Any())
                {
                    Console.WriteLine($"Fallback query successful: found {fallbackResults.Count} results");
                    return (fallbackResults, null);
                }
            }

            // No results from any query
            return (new List<SearchResult<SearchDocument>>(), error ?? "No results found with any search strategy");
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class ErrorHandlingProgram
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

                await DemonstrateErrorHandlingAsync(searchClient);
                DisplayErrorHandlingBestPractices();

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Always implement error handling in production code");
                Console.WriteLine("   - Test your error handling with various input types");
                Console.WriteLine("   - Check out 08_SearchPatterns.cs for advanced search strategies");
                Console.WriteLine("   - Review all C# examples to build complete search functionality");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateErrorHandlingAsync(SearchClient searchClient)
        {
            Console.WriteLine("🛡️ Error Handling Demonstration");
            Console.WriteLine(new string('=', 50));

            // Initialize safe search client
            var safeClient = new SafeSearchClient(searchClient);

            // Test cases with different types of potential errors
            var testCases = new[]
            {
                ("", "Empty query"),
                ("   ", "Whitespace only query"),
                ("python programming", "Valid query"),
                (new string('x', 1001), "Too long query"),
                ("valid search terms", "Another valid query")
            };

            Console.WriteLine("\n🧪 Testing Query Validation and Error Handling:");
            Console.WriteLine(new string('-', 55));

            foreach (var (query, description) in testCases)
            {
                Console.WriteLine($"\n📝 Test: {description}");
                var displayQuery = query.Length > 50 ? query.Substring(0, 50) + "..." : query;
                Console.WriteLine($"Query: '{displayQuery}'");

                var searchOptions = new SearchOptions { Size = 3 };
                var (results, error) = await safeClient.SafeSearchAsync(query, searchOptions);

                if (!string.IsNullOrEmpty(error))
                {
                    Console.WriteLine($"❌ Error: {error}");
                }
                else
                {
                    Console.WriteLine($"✅ Success: Found {results.Count} results");
                    if (results.Any())
                    {
                        var firstResult = results[0];
                        var title = firstResult.Document.TryGetValue("title", out var titleValue) ? 
                            titleValue?.ToString() ?? "No title" : "No title";
                        var score = firstResult.Score ?? 0.0;
                        Console.WriteLine($"   Top result: {title} (Score: {score:F3})");
                    }
                }
            }

            // Demonstrate fallback search
            Console.WriteLine($"\n{new string('=', 60)}");
            Console.WriteLine("\n🔄 Testing Fallback Search:");
            Console.WriteLine(new string('-', 30));

            var primaryQuery = "very_specific_nonexistent_term_12345";
            var fallbackQueries = new List<string>
            {
                "python programming",
                "tutorial",
                "development"
            };

            Console.WriteLine($"Primary query: '{primaryQuery}'");
            Console.WriteLine($"Fallback queries: [{string.Join(", ", fallbackQueries)}]");

            var searchOptions2 = new SearchOptions { Size = 2 };
            var (fallbackResults, fallbackError) = await safeClient.SearchWithFallbackAsync(
                primaryQuery, fallbackQueries, searchOptions2);

            if (fallbackResults.Any())
            {
                Console.WriteLine($"✅ Fallback successful: Found {fallbackResults.Count} results");
                for (int i = 0; i < fallbackResults.Count; i++)
                {
                    var result = fallbackResults[i];
                    var title = result.Document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() ?? "No title" : "No title";
                    var score = result.Score ?? 0.0;
                    Console.WriteLine($"  {i + 1}. {title} (Score: {score:F3})");
                }
            }
            else
            {
                Console.WriteLine($"❌ All queries failed: {fallbackError}");
            }

            Console.WriteLine("\n✅ Error handling demonstration completed!");
        }

        private static void DisplayErrorHandlingBestPractices()
        {
            Console.WriteLine("\n📚 Error Handling Best Practices");
            Console.WriteLine(new string('=', 50));

            Console.WriteLine("\n💡 Always Validate Input:");
            Console.WriteLine("   ✅ Check for empty or null queries");
            Console.WriteLine("   ✅ Validate query length limits");
            Console.WriteLine("   ✅ Sanitize user input");
            Console.WriteLine("   ✅ Handle special characters appropriately");

            Console.WriteLine("\n🔧 Handle Different Error Types:");
            Console.WriteLine("   ✅ HTTP errors (400, 401, 403, 404, 429, 503)");
            Console.WriteLine("   ✅ Network connectivity issues");
            Console.WriteLine("   ✅ Service unavailability");
            Console.WriteLine("   ✅ Invalid query syntax");

            Console.WriteLine("\n🎯 Provide User-Friendly Messages:");
            Console.WriteLine("   ✅ Translate technical errors to user language");
            Console.WriteLine("   ✅ Suggest corrective actions");
            Console.WriteLine("   ✅ Offer alternative search strategies");
            Console.WriteLine("   ✅ Log detailed errors for debugging");

            Console.WriteLine("\n🔄 Implement Fallback Strategies:");
            Console.WriteLine("   ✅ Try broader search terms if specific ones fail");
            Console.WriteLine("   ✅ Use alternative query syntax");
            Console.WriteLine("   ✅ Provide suggested searches");
            Console.WriteLine("   ✅ Gracefully degrade functionality");

            Console.WriteLine("\n⚠️ Common Mistakes to Avoid:");
            Console.WriteLine("   ❌ Exposing technical error messages to users");
            Console.WriteLine("   ❌ Not logging errors for debugging");
            Console.WriteLine("   ❌ Failing silently without user feedback");
            Console.WriteLine("   ❌ Not implementing retry logic for transient errors");

            // Show example of good error handling
            Console.WriteLine("\n🏆 Example of Good Error Handling:");
            var searchClient = new SearchClient(new Uri("https://example.search.windows.net"), "test", new AzureKeyCredential("key"));
            var safeClient = new SafeSearchClient(searchClient);

            // Simulate a problematic query
            var problematicQuery = "";  // Empty query
            var (isValid, error) = SearchValidator.ValidateQuery(problematicQuery);

            if (!isValid)
            {
                Console.WriteLine($"   User sees: '{error}'");
                Console.WriteLine($"   System logs: 'Empty query validation failed'");
                Console.WriteLine($"   Action: Prompt user to enter search terms");
            }
            else
            {
                Console.WriteLine($"   Success: Query is valid");
            }
        }
    }
}