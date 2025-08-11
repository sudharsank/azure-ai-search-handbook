/*
 * Module 3: Index Management - Error Handling and Troubleshooting (C#)
 * ====================================================================
 * 
 * This example demonstrates comprehensive error handling patterns and troubleshooting
 * techniques for Azure AI Search index management operations using the .NET SDK with
 * proper async/await patterns and exception handling.
 * 
 * Learning Objectives:
 * - Handle common error scenarios gracefully
 * - Implement retry strategies with exponential backoff
 * - Validate inputs and handle edge cases
 * - Provide meaningful error messages and recovery options
 * - Debug and troubleshoot index management issues
 * 
 * Prerequisites:
 * - Completed previous examples (01-05)
 * - Understanding of index operations and performance
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module03
{
    /// <summary>
    /// Demonstrates error handling and troubleshooting techniques using the .NET SDK
    /// </summary>
    public class ErrorHandlingManager
    {
        private readonly string _endpoint;
        private readonly string _adminKey;
        private SearchIndexClient? _indexClient;
        private SearchClient? _searchClient;
        private readonly int _maxRetries = 3;
        private readonly int _baseDelayMs = 1000;

        /// <summary>
        /// Initialize the error handling manager
        /// </summary>
        public ErrorHandlingManager()
        {
            _endpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_SERVICE_ENDPOINT environment variable is required");
            
            _adminKey = Environment.GetEnvironmentVariable("AZURE_SEARCH_ADMIN_KEY") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_ADMIN_KEY environment variable is required");
        }

        /// <summary>
        /// Create and validate search clients with error handling
        /// </summary>
        public async Task<bool> CreateClientsWithErrorHandlingAsync()
        {
            Console.WriteLine("🔍 Creating Search Clients with Error Handling...");

            try
            {
                // Validate endpoint format
                if (!_endpoint.StartsWith("https://") || !_endpoint.Contains(".search.windows.net"))
                {
                    throw new ArgumentException("Invalid endpoint format. Expected: https://[service-name].search.windows.net");
                }

                // Validate API key format
                if (string.IsNullOrEmpty(_adminKey) || _adminKey.Length < 32)
                {
                    throw new ArgumentException("Invalid API key format. Admin key should be at least 32 characters long");
                }

                _indexClient = new SearchIndexClient(
                    new Uri(_endpoint),
                    new AzureKeyCredential(_adminKey)
                );

                // Test connection with retry logic
                var stats = await ExecuteWithRetryAsync(
                    () => _indexClient.GetServiceStatisticsAsync(),
                    "Getting service statistics"
                );

                Console.WriteLine("✅ Connected to Azure AI Search service");
                Console.WriteLine($"   Storage used: {stats.Value.StorageSize:N0} bytes");
                Console.WriteLine($"   Document count: {stats.Value.DocumentCount:N0}");

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create clients: {FormatError(ex)}");
                ProvideTroubleshootingTips(ex);
                return false;
            }
        }

        /// <summary>
        /// Create a sample index with comprehensive error handling
        /// </summary>
        public async Task<string?> CreateIndexWithErrorHandlingAsync()
        {
            Console.WriteLine("🏗️  Creating index with error handling...");

            const string indexName = "error-handling-demo-cs";

            var fields = new List<SearchField>
            {
                new SearchField("id", SearchFieldDataType.String) { IsKey = true },
                new SearchField("title", SearchFieldDataType.String) { IsSearchable = true },
                new SearchField("content", SearchFieldDataType.String) { IsSearchable = true },
                new SearchField("category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SearchField("author", SearchFieldDataType.String) { IsFilterable = true },
                new SearchField("publishedDate", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true },
                new SearchField("rating", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true },
                new SearchField("viewCount", SearchFieldDataType.Int32) { IsFilterable = true, IsSortable = true },
                new SearchField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFilterable = true, IsFacetable = true },
                new SearchField("isPublished", SearchFieldDataType.Boolean) { IsFilterable = true }
            };

            try
            {
                // Validate index definition
                ValidateIndexDefinition(indexName, fields);

                var index = new SearchIndex(indexName, fields);
                var result = await ExecuteWithRetryAsync(
                    () => _indexClient!.CreateOrUpdateIndexAsync(index),
                    "Creating index"
                );

                // Create search client for this index
                _searchClient = new SearchClient(
                    new Uri(_endpoint),
                    indexName,
                    new AzureKeyCredential(_adminKey)
                );

                Console.WriteLine($"✅ Index '{result.Value.Name}' created successfully");
                return indexName;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create index: {FormatError(ex)}");
                ProvideTroubleshootingTips(ex);
                return null;
            }
        }

        /// <summary>
        /// Demonstrate document upload with error handling
        /// </summary>
        public async Task<bool> UploadDocumentsWithErrorHandlingAsync()
        {
            Console.WriteLine("📤 Document Upload with Error Handling...");

            try
            {
                // Generate sample documents with some intentional issues
                var documents = GenerateSampleDocumentsWithIssues();

                Console.WriteLine($"   Attempting to upload {documents.Count} documents...");

                var result = await ExecuteWithRetryAsync(
                    () => _searchClient!.UploadDocumentsAsync(documents),
                    "Uploading documents"
                );

                // Analyze results
                var successful = result.Value.Results.Where(r => r.Succeeded).ToList();
                var failed = result.Value.Results.Where(r => !r.Succeeded).ToList();

                Console.WriteLine($"✅ Upload completed:");
                Console.WriteLine($"   Successful: {successful.Count}");
                Console.WriteLine($"   Failed: {failed.Count}");

                // Handle failed documents
                if (failed.Any())
                {
                    Console.WriteLine("\n❌ Failed documents:");
                    foreach (var failure in failed)
                    {
                        Console.WriteLine($"   - Document {failure.Key}: {failure.ErrorMessage}");
                        SuggestDocumentFix(failure);
                    }

                    // Attempt to fix and retry failed documents
                    await RetryFailedDocumentsAsync(failed, documents);
                }

                return successful.Any();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Document upload failed: {FormatError(ex)}");
                ProvideTroubleshootingTips(ex);
                return false;
            }
        }

        /// <summary>
        /// Demonstrate search operations with error handling
        /// </summary>
        public async Task SearchWithErrorHandlingAsync()
        {
            Console.WriteLine("🔍 Search Operations with Error Handling...");

            var testQueries = new[]
            {
                new { Query = "azure search", Description = "Valid simple query" },
                new { Query = "title:azure AND content:search", Description = "Valid field-specific query" },
                new { Query = "invalid_field:test", Description = "Invalid field name" },
                new { Query = "title:azure AND (", Description = "Malformed query syntax" },
                new { Query = "", Description = "Empty query" }
            };

            foreach (var testQuery in testQueries)
            {
                Console.WriteLine($"\n🧪 Testing: {testQuery.Description}");
                Console.WriteLine($"   Query: \"{testQuery.Query}\"");

                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Size = 5,
                        IncludeTotalCount = true,
                        Select = { "id", "title", "category" }
                    };

                    var results = await ExecuteWithRetryAsync(
                        () => _searchClient!.SearchAsync<Dictionary<string, object>>(testQuery.Query, searchOptions),
                        $"Searching with query: {testQuery.Query}"
                    );

                    Console.WriteLine($"   ✅ Success: Found {results.Value.TotalCount} results");

                    var resultCount = 0;
                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        if (resultCount < 2) // Show first 2 results
                        {
                            var doc = result.Document;
                            Console.WriteLine($"     - {doc["id"]}: {doc["title"]}");
                            resultCount++;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Failed: {FormatError(ex)}");
                    SuggestQueryFix(testQuery.Query, ex);
                }
            }
        }

        /// <summary>
        /// Demonstrate filter operations with error handling
        /// </summary>
        public async Task FilterWithErrorHandlingAsync()
        {
            Console.WriteLine("\n🔍 Filter Operations with Error Handling...");

            var testFilters = new[]
            {
                new { Filter = "category eq 'Technology'", Description = "Valid string filter" },
                new { Filter = "rating gt 4.0", Description = "Valid numeric filter" },
                new { Filter = "publishedDate ge 2024-01-01T00:00:00Z", Description = "Valid date filter" },
                new { Filter = "invalid_field eq 'test'", Description = "Invalid field name" },
                new { Filter = "category eq Technology", Description = "Missing quotes in string filter" },
                new { Filter = "rating gt 'invalid'", Description = "Invalid data type" }
            };

            foreach (var testFilter in testFilters)
            {
                Console.WriteLine($"\n🧪 Testing: {testFilter.Description}");
                Console.WriteLine($"   Filter: {testFilter.Filter}");

                try
                {
                    var results = await ExecuteWithRetryAsync(
                        () => _searchClient!.SearchAsync<Dictionary<string, object>>("*", new SearchOptions
                        {
                            Filter = testFilter.Filter,
                            Size = 3,
                            Select = { "id", "title", "category", "rating" }
                        }),
                        $"Filtering with: {testFilter.Filter}"
                    );

                    Console.WriteLine($"   ✅ Success: Found {results.Value.TotalCount} results");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Failed: {FormatError(ex)}");
                    SuggestFilterFix(testFilter.Filter, ex);
                }
            }
        }

        /// <summary>
        /// Execute operation with retry logic and exponential backoff
        /// </summary>
        private async Task<T> ExecuteWithRetryAsync<T>(Func<Task<T>> operation, string operationName, int maxRetries = -1)
        {
            if (maxRetries == -1) maxRetries = _maxRetries;
            
            Exception? lastException = null;

            for (var attempt = 1; attempt <= maxRetries; attempt++)
            {
                try
                {
                    return await operation();
                }
                catch (Exception ex)
                {
                    lastException = ex;

                    if (attempt == maxRetries)
                    {
                        throw;
                    }

                    // Check if error is retryable
                    if (!IsRetryableError(ex))
                    {
                        throw;
                    }

                    var delay = CalculateBackoffDelay(attempt);
                    Console.WriteLine($"   ⚠️  {operationName} failed (attempt {attempt}/{maxRetries}). Retrying in {delay}ms...");
                    Console.WriteLine($"      Error: {FormatError(ex)}");

                    await Task.Delay(delay);
                }
            }

            throw lastException!;
        }

        /// <summary>
        /// Determine if an error is retryable
        /// </summary>
        private static bool IsRetryableError(Exception ex)
        {
            if (ex is RequestFailedException requestEx)
            {
                // Retry on server errors and rate limiting
                return requestEx.Status >= 500 || requestEx.Status == 429;
            }

            // Retry on network errors
            if (ex is HttpRequestException || ex is TaskCanceledException)
            {
                return true;
            }

            return false;
        }

        /// <summary>
        /// Calculate exponential backoff delay
        /// </summary>
        private int CalculateBackoffDelay(int attempt)
        {
            var jitter = new Random().NextDouble() * 0.1; // Add 10% jitter
            return (int)Math.Floor(_baseDelayMs * Math.Pow(2, attempt - 1) * (1 + jitter));
        }

        /// <summary>
        /// Format error messages for better readability
        /// </summary>
        private static string FormatError(Exception ex)
        {
            if (ex is RequestFailedException requestEx)
            {
                return $"HTTP {requestEx.Status}: {requestEx.Message}";
            }

            if (ex is ArgumentException argEx)
            {
                return $"Argument Error: {argEx.Message}";
            }

            return ex.Message;
        }

        /// <summary>
        /// Provide troubleshooting tips based on error type
        /// </summary>
        private static void ProvideTroubleshootingTips(Exception ex)
        {
            Console.WriteLine("\n💡 Troubleshooting Tips:");

            if (ex is RequestFailedException requestEx)
            {
                switch (requestEx.Status)
                {
                    case 401:
                        Console.WriteLine("   - Check your API key is correct and has admin permissions");
                        Console.WriteLine("   - Ensure you are using the admin key, not a query key");
                        break;
                    case 403:
                        Console.WriteLine("   - Verify your API key has the required permissions");
                        Console.WriteLine("   - Check if your service is in a restricted region");
                        break;
                    case 404:
                        Console.WriteLine("   - Verify the service endpoint URL is correct");
                        Console.WriteLine("   - Check if the index name exists");
                        break;
                    case 429:
                        Console.WriteLine("   - You are being rate limited. Reduce request frequency");
                        Console.WriteLine("   - Consider upgrading your service tier for higher limits");
                        break;
                    case >= 500:
                        Console.WriteLine("   - Server error. Try again in a few moments");
                        Console.WriteLine("   - Check Azure service health status");
                        break;
                    default:
                        Console.WriteLine($"   - HTTP {requestEx.Status} error occurred");
                        Console.WriteLine("   - Check the Azure AI Search documentation for details");
                        break;
                }
            }
            else if (ex is HttpRequestException || ex is TaskCanceledException)
            {
                Console.WriteLine("   - Network connectivity issue");
                Console.WriteLine("   - Check your internet connection");
                Console.WriteLine("   - Verify firewall settings allow HTTPS traffic");
            }
            else if (ex is ArgumentException)
            {
                Console.WriteLine("   - Check your configuration parameters");
                Console.WriteLine("   - Verify environment variables are set correctly");
            }
            else
            {
                Console.WriteLine("   - Check your configuration and try again");
                Console.WriteLine("   - Enable detailed logging for more information");
            }
        }

        /// <summary>
        /// Validate index definition
        /// </summary>
        private static void ValidateIndexDefinition(string indexName, IList<SearchField> fields)
        {
            if (string.IsNullOrEmpty(indexName))
            {
                throw new ArgumentException("Index name is required");
            }

            if (!System.Text.RegularExpressions.Regex.IsMatch(indexName, @"^[a-z0-9-]+$"))
            {
                throw new ArgumentException("Index name must contain only lowercase letters, numbers, and hyphens");
            }

            if (fields == null || !fields.Any())
            {
                throw new ArgumentException("Index must have at least one field");
            }

            var keyFields = fields.Where(f => f.IsKey == true).ToList();
            if (keyFields.Count != 1)
            {
                throw new ArgumentException("Index must have exactly one key field");
            }

            Console.WriteLine("✅ Index definition validation passed");
        }

        /// <summary>
        /// Generate sample documents with some intentional issues for testing
        /// </summary>
        private List<Dictionary<string, object>> GenerateSampleDocumentsWithIssues()
        {
            return new List<Dictionary<string, object>>
            {
                // Valid document
                new Dictionary<string, object>
                {
                    ["id"] = "doc-1",
                    ["title"] = "Valid Document",
                    ["content"] = "This is a valid document with all required fields.",
                    ["category"] = "Technology",
                    ["author"] = "John Doe",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T10:00:00Z"),
                    ["rating"] = 4.5,
                    ["viewCount"] = 100,
                    ["tags"] = new[] { "technology", "valid" },
                    ["isPublished"] = true
                },
                // Document with missing optional fields
                new Dictionary<string, object>
                {
                    ["id"] = "doc-2",
                    ["title"] = "Document with Missing Fields",
                    ["content"] = "This document is missing some optional fields.",
                    ["category"] = "Technology",
                    ["author"] = "Jane Smith",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-11T10:00:00Z"),
                    ["rating"] = 4.0,
                    ["viewCount"] = 50,
                    ["isPublished"] = true
                    // Missing tags field - this is OK as it's optional
                },
                // Valid document
                new Dictionary<string, object>
                {
                    ["id"] = "doc-4",
                    ["title"] = "Another Valid Document",
                    ["content"] = "This is another valid document for testing.",
                    ["category"] = "Science",
                    ["author"] = "Alice Brown",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-12T10:00:00Z"),
                    ["rating"] = 4.8,
                    ["viewCount"] = 200,
                    ["tags"] = new[] { "science", "valid" },
                    ["isPublished"] = true
                }
            };
        }

        /// <summary>
        /// Suggest fixes for document upload failures
        /// </summary>
        private static void SuggestDocumentFix(IndexingResult failure)
        {
            Console.WriteLine($"   💡 Suggested fix for {failure.Key}:");

            if (failure.ErrorMessage?.Contains("date", StringComparison.OrdinalIgnoreCase) == true)
            {
                Console.WriteLine("      - Check date format. Use ISO 8601 format: YYYY-MM-DDTHH:mm:ssZ");
            }
            else if (failure.ErrorMessage?.Contains("required", StringComparison.OrdinalIgnoreCase) == true)
            {
                Console.WriteLine("      - Ensure all required fields are present");
            }
            else if (failure.ErrorMessage?.Contains("type", StringComparison.OrdinalIgnoreCase) == true)
            {
                Console.WriteLine("      - Check data types match the index schema");
            }
            else
            {
                Console.WriteLine("      - Review the document structure and field values");
            }
        }

        /// <summary>
        /// Suggest fixes for query failures
        /// </summary>
        private static void SuggestQueryFix(string query, Exception error)
        {
            Console.WriteLine("   💡 Suggested fixes:");

            if (error.Message.Contains("field", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("      - Check field names exist in the index schema");
                Console.WriteLine("      - Verify field names are spelled correctly");
            }
            else if (error.Message.Contains("syntax", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("      - Check query syntax for balanced parentheses");
                Console.WriteLine("      - Verify operator usage (AND, OR, NOT)");
            }
            else if (string.IsNullOrEmpty(query))
            {
                Console.WriteLine("      - Use \"*\" for empty queries to search all documents");
            }
            else
            {
                Console.WriteLine("      - Simplify the query and test incrementally");
            }
        }

        /// <summary>
        /// Suggest fixes for filter failures
        /// </summary>
        private static void SuggestFilterFix(string filter, Exception error)
        {
            Console.WriteLine("   💡 Suggested fixes:");

            if (error.Message.Contains("field", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("      - Verify the field exists and is filterable");
            }
            else if (error.Message.Contains("quote", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("      - Enclose string values in single quotes");
            }
            else if (error.Message.Contains("type", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("      - Check data type compatibility (string, number, date)");
            }
            else
            {
                Console.WriteLine("      - Review OData filter syntax documentation");
            }
        }

        /// <summary>
        /// Retry failed documents with fixes
        /// </summary>
        private async Task RetryFailedDocumentsAsync(List<IndexingResult> failures, List<Dictionary<string, object>> originalDocuments)
        {
            Console.WriteLine("\n🔄 Attempting to fix and retry failed documents...");

            var documentsToRetry = new List<Dictionary<string, object>>();

            foreach (var failure in failures)
            {
                var originalDoc = originalDocuments.FirstOrDefault(doc => doc["id"].ToString() == failure.Key);
                if (originalDoc != null)
                {
                    // Attempt to fix common issues
                    var fixedDoc = new Dictionary<string, object>(originalDoc);

                    if (failure.ErrorMessage?.Contains("date", StringComparison.OrdinalIgnoreCase) == true)
                    {
                        // Fix invalid date format
                        fixedDoc["publishedDate"] = DateTimeOffset.Parse("2024-02-10T10:00:00Z");
                        Console.WriteLine($"   🔧 Fixed date format for document {failure.Key}");
                    }

                    documentsToRetry.Add(fixedDoc);
                }
            }

            if (documentsToRetry.Any())
            {
                try
                {
                    var retryResult = await _searchClient!.UploadDocumentsAsync(documentsToRetry);
                    var retrySuccessful = retryResult.Value.Results.Count(r => r.Succeeded);
                    var retryFailed = retryResult.Value.Results.Count - retrySuccessful;

                    Console.WriteLine($"   ✅ Retry completed: {retrySuccessful} successful, {retryFailed} failed");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Retry failed: {FormatError(ex)}");
                }
            }
        }

        /// <summary>
        /// Demonstrate comprehensive error logging
        /// </summary>
        public async Task DemonstrateErrorLoggingAsync()
        {
            Console.WriteLine("\n📝 Error Logging Demonstration...");

            // Simulate various error scenarios
            var errorScenarios = new[]
            {
                new
                {
                    Name = "Invalid Index Name",
                    Operation = new Func<Task>(async () =>
                    {
                        var invalidIndex = new SearchIndex("Invalid Index Name!", new[]
                        {
                            new SearchField("id", SearchFieldDataType.String) { IsKey = true }
                        });
                        await _indexClient!.CreateOrUpdateIndexAsync(invalidIndex);
                    }),
                    Context = new { IndexName = "Invalid Index Name!" }
                },
                new
                {
                    Name = "Missing Key Field",
                    Operation = new Func<Task>(async () =>
                    {
                        var invalidIndex = new SearchIndex("test-index", new[]
                        {
                            new SearchField("title", SearchFieldDataType.String) { IsSearchable = true }
                        });
                        await _indexClient!.CreateOrUpdateIndexAsync(invalidIndex);
                    }),
                    Context = new { IndexName = "test-index" }
                }
            };

            foreach (var scenario in errorScenarios)
            {
                Console.WriteLine($"\n🧪 Testing: {scenario.Name}");
                try
                {
                    await scenario.Operation();
                    Console.WriteLine("   ✅ Unexpectedly succeeded");
                }
                catch (Exception ex)
                {
                    LogError(scenario.Name, ex, scenario.Context);
                }
            }
        }

        /// <summary>
        /// Log error with comprehensive information
        /// </summary>
        private static void LogError(string operation, Exception error, object? context = null)
        {
            var timestamp = DateTime.UtcNow;
            Console.WriteLine($"   📋 Error Log Entry:");
            Console.WriteLine($"      Timestamp: {timestamp:yyyy-MM-dd HH:mm:ss} UTC");
            Console.WriteLine($"      Operation: {operation}");
            Console.WriteLine($"      Error: {FormatError(error)}");
            if (context != null)
            {
                Console.WriteLine($"      Context: {System.Text.Json.JsonSerializer.Serialize(context, new System.Text.Json.JsonSerializerOptions { WriteIndented = true })}");
            }
        }

        /// <summary>
        /// Get error handling statistics
        /// </summary>
        public async Task GetErrorHandlingStatisticsAsync()
        {
            Console.WriteLine("\n📊 Error Handling Statistics:");

            try
            {
                var docCount = await _searchClient!.GetDocumentCountAsync();
                Console.WriteLine($"   Total documents: {docCount.Value}");

                // Test basic connectivity
                var testResult = await _searchClient.SearchAsync<Dictionary<string, object>>("*", new SearchOptions { Size = 1 });
                Console.WriteLine("   ✅ Basic search functionality working");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to get statistics: {FormatError(ex)}");
            }
        }
    }

    /// <summary>
    /// Main program demonstrating error handling
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("=".PadRight(60, '='));
            Console.WriteLine("Module 3: Error Handling and Troubleshooting Example (C#)");
            Console.WriteLine("=".PadRight(60, '='));

            // Initialize the error handling manager
            ErrorHandlingManager manager;
            try
            {
                manager = new ErrorHandlingManager();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                return;
            }

            // Create clients with error handling
            if (!await manager.CreateClientsWithErrorHandlingAsync())
            {
                Console.WriteLine("❌ Failed to create clients. Exiting.");
                return;
            }

            // Create sample index with error handling
            var indexName = await manager.CreateIndexWithErrorHandlingAsync();
            if (indexName == null)
            {
                Console.WriteLine("❌ Failed to create sample index. Exiting.");
                return;
            }

            Console.WriteLine($"\n🎯 Running error handling demonstrations on index '{indexName}'...");

            // Run demonstrations
            var demonstrations = new (string Name, Func<Task> Func)[]
            {
                ("Document Upload Error Handling", manager.UploadDocumentsWithErrorHandlingAsync),
                ("Search Error Handling", manager.SearchWithErrorHandlingAsync),
                ("Filter Error Handling", manager.FilterWithErrorHandlingAsync),
                ("Error Logging", manager.DemonstrateErrorLoggingAsync)
            };

            foreach (var (name, func) in demonstrations)
            {
                Console.WriteLine($"\n{"=".PadRight(20, '=')} {name} {"=".PadRight(20, '=')}");
                try
                {
                    await func();
                    Console.WriteLine($"✅ {name} completed successfully");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"❌ {name} failed: {ErrorHandlingManager.FormatError(ex)}");
                }

                // Brief pause between demonstrations
                await Task.Delay(1000);
            }

            // Show current statistics
            Console.WriteLine($"\n{"=".PadRight(20, '=')} Current Statistics {"=".PadRight(20, '=')}");
            await manager.GetErrorHandlingStatisticsAsync();

            Console.WriteLine("\n" + "=".PadRight(60, '='));
            Console.WriteLine("Example completed!");
            Console.WriteLine("=".PadRight(60, '='));

            Console.WriteLine("\n📚 What you learned:");
            Console.WriteLine("✅ How to handle common error scenarios gracefully");
            Console.WriteLine("✅ How to implement retry strategies with exponential backoff");
            Console.WriteLine("✅ How to validate inputs and handle edge cases");
            Console.WriteLine("✅ How to provide meaningful error messages and recovery options");
            Console.WriteLine("✅ How to debug and troubleshoot index management issues");

            Console.WriteLine("\n🚀 Next steps:");
            Console.WriteLine("1. Implement comprehensive error handling in your applications");
            Console.WriteLine("2. Set up monitoring and alerting for production systems");
            Console.WriteLine("3. Create error recovery procedures for your team");
            Console.WriteLine("4. Move on to Module 4: Advanced Search Techniques");

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}