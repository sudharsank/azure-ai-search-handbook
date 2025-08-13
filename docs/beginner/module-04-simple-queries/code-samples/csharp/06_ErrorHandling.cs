using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace AzureSearchModule4
{
    /// <summary>
    /// Module 4: Simple Queries and Filters - Error Handling
    /// 
    /// This class demonstrates comprehensive error handling for Azure AI Search queries using C#.
    /// Learn how to handle exceptions, validate queries, implement retry logic, and debug issues.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service configured
    /// - Sample index with data (from previous modules)
    /// - Configuration set up in appsettings.json or environment variables
    /// 
    /// Author: Azure AI Search Tutorial
    /// </summary>
    public class ErrorHandling
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<ErrorHandling> _logger;

        public ErrorHandling()
        {
            // Load configuration
            _configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json", optional: true)
                .AddEnvironmentVariables()
                .Build();

            // Setup logging
            using var loggerFactory = LoggerFactory.Create(builder => builder.AddConsole());
            _logger = loggerFactory.CreateLogger<ErrorHandling>();

            // Initialize search client
            _searchClient = CreateSearchClient();
        }

        /// <summary>
        /// Create and return an Azure AI Search client with error handling.
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
                var missing = new List<string>();
                if (string.IsNullOrEmpty(serviceEndpoint)) missing.Add("AZURE_SEARCH_SERVICE_ENDPOINT");
                if (string.IsNullOrEmpty(apiKey)) missing.Add("AZURE_SEARCH_API_KEY");
                if (string.IsNullOrEmpty(indexName)) missing.Add("AZURE_SEARCH_INDEX_NAME");

                throw new InvalidOperationException($"Missing required environment variables: {string.Join(", ", missing)}");
            }

            try
            {
                var serviceUri = new Uri(serviceEndpoint);
                var credential = new AzureKeyCredential(apiKey);
                var client = new SearchClient(serviceUri, indexName, credential);

                _logger.LogInformation($"Successfully created search client for index: {indexName}");
                return client;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Failed to create search client: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Validate search query parameters before execution.
        /// </summary>
        /// <param name="searchText">Search query text</param>
        /// <param name="searchOptions">Search options</param>
        /// <returns>Tuple of (isValid, errorMessage)</returns>
        public (bool IsValid, string ErrorMessage) ValidateQueryParameters(string searchText, SearchOptions searchOptions = null)
        {
            // Check search text
            if (searchText != null)
            {
                if (string.IsNullOrWhiteSpace(searchText))
                {
                    return (false, "Search text cannot be empty");
                }

                if (searchText.Length > 1000)
                {
                    return (false, "Search text too long (max 1000 characters)");
                }

                // Check for unbalanced quotes
                if (searchText.Count(c => c == '"') % 2 != 0)
                {
                    return (false, "Unbalanced quotes in search text");
                }

                // Check for unbalanced parentheses
                if (searchText.Count(c => c == '(') != searchText.Count(c => c == ')'))
                {
                    return (false, "Unbalanced parentheses in search text");
                }
            }

            // Check search options
            if (searchOptions != null)
            {
                // Check Size parameter
                if (searchOptions.Size.HasValue)
                {
                    if (searchOptions.Size < 0)
                    {
                        return (false, "Size parameter must be non-negative");
                    }
                    if (searchOptions.Size > 1000)
                    {
                        return (false, "Size parameter cannot exceed 1000");
                    }
                }

                // Check Skip parameter
                if (searchOptions.Skip.HasValue)
                {
                    if (searchOptions.Skip < 0)
                    {
                        return (false, "Skip parameter must be non-negative");
                    }
                    if (searchOptions.Skip > 100000)
                    {
                        return (false, "Skip parameter cannot exceed 100,000");
                    }
                }

                // Check filter syntax (basic validation)
                if (!string.IsNullOrEmpty(searchOptions.Filter))
                {
                    if (searchOptions.Filter.Count(c => c == '(') != searchOptions.Filter.Count(c => c == ')'))
                    {
                        return (false, "Unbalanced parentheses in filter expression");
                    }

                    // Check for invalid operators
                    var invalidOperators = new[] { "=", "!=", "<>", "&&", "||" };
                    foreach (var op in invalidOperators)
                    {
                        if (searchOptions.Filter.Contains(op))
                        {
                            return (false, $"Invalid operator '{op}' in filter (use OData syntax)");
                        }
                    }
                }
            }

            return (true, "Query parameters are valid");
        }

        /// <summary>
        /// Perform a safe search with comprehensive error handling.
        /// </summary>
        /// <param name="searchText">Search text</param>
        /// <param name="searchOptions">Search options</param>
        /// <returns>Tuple of (results, errorMessage)</returns>
        public async Task<(List<SearchResult<SearchDocument>> Results, string ErrorMessage)> SafeSearchAsync(
            string searchText, SearchOptions searchOptions = null)
        {
            try
            {
                // Validate parameters
                var (isValid, validationError) = ValidateQueryParameters(searchText, searchOptions);
                if (!isValid)
                {
                    _logger.LogWarning($"Query validation failed: {validationError}");
                    return (new List<SearchResult<SearchDocument>>(), validationError);
                }

                // Log the search attempt
                _logger.LogInformation($"Executing search: '{searchText}' with options: {searchOptions?.ToString() ?? "none"}");

                // Execute search
                var results = await _searchClient.SearchAsync<SearchDocument>(searchText, searchOptions);
                var resultList = results.Value.GetResults().ToList();

                _logger.LogInformation($"Search completed successfully: {resultList.Count} results");
                return (resultList, null);
            }
            catch (RequestFailedException ex)
            {
                var errorMsg = $"HTTP error {ex.Status}: {ex.Message}";
                _logger.LogError(ex, errorMsg);
                return (new List<SearchResult<SearchDocument>>(), errorMsg);
            }
            catch (Exception ex)
            {
                var errorMsg = $"Unexpected error: {ex.Message}";
                _logger.LogError(ex, errorMsg);
                return (new List<SearchResult<SearchDocument>>(), errorMsg);
            }
        }

        /// <summary>
        /// Perform search with retry logic for transient failures.
        /// </summary>
        /// <param name="searchText">Search text</param>
        /// <param name="searchOptions">Search options</param>
        /// <param name="maxRetries">Maximum number of retry attempts</param>
        /// <param name="retryDelayMs">Delay between retries in milliseconds</param>
        /// <returns>Tuple of (results, errorMessage)</returns>
        public async Task<(List<SearchResult<SearchDocument>> Results, string ErrorMessage)> RetrySearchAsync(
            string searchText, SearchOptions searchOptions = null, int maxRetries = 3, int retryDelayMs = 1000)
        {
            string lastError = null;

            for (int attempt = 0; attempt <= maxRetries; attempt++)
            {
                try
                {
                    if (attempt > 0)
                    {
                        _logger.LogInformation($"Retry attempt {attempt}/{maxRetries}");
                        await Task.Delay(retryDelayMs * attempt); // Exponential backoff
                    }

                    var (results, error) = await SafeSearchAsync(searchText, searchOptions);

                    if (error == null)
                    {
                        if (attempt > 0)
                        {
                            _logger.LogInformation($"Search succeeded on retry attempt {attempt}");
                        }
                        return (results, null);
                    }
                    else
                    {
                        lastError = error;
                        // Don't retry for validation errors or client errors (4xx)
                        if (error.Contains("validation") || error.Contains("400"))
                        {
                            break;
                        }
                    }
                }
                catch (Exception ex)
                {
                    lastError = ex.Message;
                    _logger.LogWarning($"Attempt {attempt + 1} failed: {lastError}");
                }
            }

            _logger.LogError($"Search failed after {maxRetries + 1} attempts");
            return (new List<SearchResult<SearchDocument>>(), lastError);
        }

        /// <summary>
        /// Demonstrate common search errors and how to handle them.
        /// </summary>
        public async Task DemonstrateCommonErrorsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("COMMON ERROR SCENARIOS");
            Console.WriteLine(new string('=', 80));

            var errorScenarios = new[]
            {
                ("Empty Search Text", "", null),
                ("Invalid Filter Syntax", "*", new SearchOptions { Filter = "category = 'Technology'" }), // Should be 'eq'
                ("Non-existent Field in Filter", "*", new SearchOptions { Filter = "nonexistent_field eq 'value'" }),
                ("Invalid Size Parameter", "*", new SearchOptions { Size = -1 }),
                ("Unbalanced Quotes", "\"unbalanced quote", null),
                ("Invalid Order By Field", "*", new SearchOptions { OrderBy = { "nonexistent_field desc" } })
            };

            for (int i = 0; i < errorScenarios.Length; i++)
            {
                var (name, searchText, options) = errorScenarios[i];
                Console.WriteLine($"\n{i + 1}. {name}");
                Console.WriteLine(new string('-', 40));
                Console.WriteLine($"Expected: Error should be caught and handled gracefully");

                var (results, error) = await SafeSearchAsync(searchText, options);

                if (!string.IsNullOrEmpty(error))
                {
                    Console.WriteLine($"✅ Error handled correctly: {error}");
                }
                else
                {
                    Console.WriteLine($"⚠️  Unexpected success: {results.Count} results returned");
                }
            }
        }

        /// <summary>
        /// Demonstrate retry logic for handling transient failures.
        /// </summary>
        public async Task DemonstrateRetryLogicAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("RETRY LOGIC DEMONSTRATION");
            Console.WriteLine(new string('=', 80));

            // Example 1: Successful search (no retries needed)
            Console.WriteLine("\n1. Successful Search (No Retries)");
            Console.WriteLine(new string('-', 40));

            var (results, error) = await RetrySearchAsync("azure", new SearchOptions { Size = 3 }, maxRetries: 2);

            if (string.IsNullOrEmpty(error))
            {
                Console.WriteLine($"✅ Search succeeded: {results.Count} results");
            }
            else
            {
                Console.WriteLine($"❌ Search failed: {error}");
            }

            // Example 2: Search with validation error (no retries)
            Console.WriteLine("\n2. Validation Error (No Retries)");
            Console.WriteLine(new string('-', 40));

            var (results2, error2) = await RetrySearchAsync("", maxRetries: 2); // Empty search text

            if (!string.IsNullOrEmpty(error2))
            {
                Console.WriteLine($"✅ Validation error (no retries): {error2}");
            }
            else
            {
                Console.WriteLine($"⚠️  Unexpected success: {results2.Count} results");
            }
        }

        /// <summary>
        /// Demonstrate tools and techniques for debugging search queries.
        /// </summary>
        public async Task QueryDebuggingToolsAsync()
        {
            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("QUERY DEBUGGING TOOLS");
            Console.WriteLine(new string('=', 80));

            async Task DebugSearchAsync(string description, string searchText, SearchOptions options = null)
            {
                Console.WriteLine($"\n{description}");
                Console.WriteLine(new string('-', 40));

                // Log query details
                Console.WriteLine($"Query: '{searchText}'");

                if (options?.Filter != null)
                {
                    Console.WriteLine($"Filter: {options.Filter}");
                }
                if (options?.OrderBy?.Any() == true)
                {
                    Console.WriteLine($"Order by: {string.Join(", ", options.OrderBy)}");
                }
                if (options?.Size.HasValue == true)
                {
                    Console.WriteLine($"Size: {options.Size}");
                }

                // Validate first
                var (isValid, validationError) = ValidateQueryParameters(searchText, options);
                if (!isValid)
                {
                    Console.WriteLine($"❌ Validation failed: {validationError}");
                    return;
                }

                // Execute with timing
                var startTime = DateTime.Now;
                var (results, error) = await SafeSearchAsync(searchText, options);
                var executionTime = DateTime.Now - startTime;

                if (string.IsNullOrEmpty(error))
                {
                    Console.WriteLine($"✅ Query succeeded in {executionTime.TotalMilliseconds:F0}ms");
                    Console.WriteLine($"   Results: {results.Count}");

                    if (results.Any())
                    {
                        // Show score distribution
                        var scores = results.Select(r => r.Score).ToList();
                        Console.WriteLine($"   Score range: {scores.Min():F3} - {scores.Max():F3}");

                        // Show top result
                        var topResult = results.First();
                        var title = topResult.Document.GetValueOrDefault("title", "No title").ToString();
                        Console.WriteLine($"   Top result: {title.Substring(0, Math.Min(50, title.Length))}...");
                    }
                }
                else
                {
                    Console.WriteLine($"❌ Query failed: {error}");
                }
            }

            // Debug various query types
            await DebugSearchAsync("1. Basic Text Search", "azure machine learning");

            await DebugSearchAsync("2. Filtered Search", "tutorial", new SearchOptions { Filter = "rating ge 4.0" });

            await DebugSearchAsync("3. Complex Query", "python OR java", new SearchOptions
            {
                Filter = "category eq 'Technology'",
                OrderBy = { "rating desc" },
                Size = 5
            });

            await DebugSearchAsync("4. Problematic Query (Invalid Filter)", "azure", new SearchOptions
            {
                Filter = "invalid_field eq 'value'"
            });
        }

        /// <summary>
        /// Main method to run all error handling examples.
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Azure AI Search - Error Handling Examples");
            Console.WriteLine(new string('=', 80));

            try
            {
                var errorHandling = new ErrorHandling();

                Console.WriteLine($"✅ Connected to search service");
                Console.WriteLine($"✅ Using configured index");

                // Run examples
                await errorHandling.DemonstrateCommonErrorsAsync();
                await errorHandling.DemonstrateRetryLogicAsync();
                await errorHandling.QueryDebuggingToolsAsync();

                Console.WriteLine("\n" + new string('=', 80));
                Console.WriteLine("✅ All error handling examples completed successfully!");
                Console.WriteLine(new string('=', 80));

                Console.WriteLine("\n📚 What you learned:");
                Console.WriteLine("• How to validate query parameters before execution");
                Console.WriteLine("• How to handle different types of Azure AI Search exceptions");
                Console.WriteLine("• How to implement retry logic for transient failures");
                Console.WriteLine("• How to debug and troubleshoot search queries");
                Console.WriteLine("• How to implement graceful error recovery strategies");

                Console.WriteLine("\n🔗 Next steps:");
                Console.WriteLine("• Apply these patterns to your production applications");
                Console.WriteLine("• Set up monitoring and alerting for search errors");
                Console.WriteLine("• Create custom error handling for your specific use cases");

                Console.WriteLine("\n💡 Production Tips:");
                Console.WriteLine("• Always validate user input before sending to search");
                Console.WriteLine("• Implement proper logging for debugging");
                Console.WriteLine("• Use retry logic for transient network issues");
                Console.WriteLine("• Provide fallback queries for better user experience");
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