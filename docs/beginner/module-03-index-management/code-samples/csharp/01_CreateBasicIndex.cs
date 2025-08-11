/*
 * Module 3: Index Management - Basic Index Creation (C#)
 * =====================================================
 * 
 * This example demonstrates the fundamentals of creating a search index in Azure AI Search
 * using the .NET SDK. You'll learn how to define field types, set attributes, and
 * create your first index with proper async/await patterns and error handling.
 * 
 * Learning Objectives:
 * - Create SearchIndexClient with proper authentication
 * - Define field types and attributes using SearchField
 * - Create a basic index schema with async patterns
 * - Handle index creation responses with proper error handling
 * - Validate index creation and test functionality
 * 
 * Prerequisites:
 * - .NET 6.0 or later
 * - Azure AI Search service with admin access
 * - Environment variables configured
 * - Azure.Search.Documents NuGet package installed
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace AzureSearchHandbook.Module03
{
    /// <summary>
    /// Demonstrates basic index creation patterns using the .NET SDK
    /// </summary>
    public class BasicIndexCreator
    {
        private readonly string _endpoint;
        private readonly string _adminKey;
        private SearchIndexClient? _indexClient;

        /// <summary>
        /// Initialize the index creator with Azure AI Search credentials
        /// </summary>
        public BasicIndexCreator()
        {
            _endpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_SERVICE_ENDPOINT environment variable is required");
            
            _adminKey = Environment.GetEnvironmentVariable("AZURE_SEARCH_ADMIN_KEY") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_ADMIN_KEY environment variable is required");
        }

        /// <summary>
        /// Create and validate the SearchIndexClient
        /// </summary>
        public async Task<bool> CreateIndexClientAsync()
        {
            Console.WriteLine("🔍 Creating SearchIndexClient...");

            try
            {
                _indexClient = new SearchIndexClient(
                    new Uri(_endpoint),
                    new AzureKeyCredential(_adminKey)
                );

                // Test connection by getting service statistics
                var stats = await _indexClient.GetServiceStatisticsAsync();
                Console.WriteLine("✅ Connected to Azure AI Search service");
                Console.WriteLine($"   Storage used: {stats.Value.StorageSize:N0} bytes");
                Console.WriteLine($"   Document count: {stats.Value.DocumentCount:N0}");

                return true;
            }
            catch (RequestFailedException ex) when (ex.Status == 403)
            {
                Console.WriteLine("❌ Access denied - check your admin API key");
                return false;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ HTTP error {ex.Status}: {ex.Message}");
                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create index client: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Define a basic index schema for a blog application
        /// </summary>
        public IList<SearchField> DefineBasicSchema()
        {
            Console.WriteLine("📋 Defining Basic Index Schema...");

            // Define fields with different types and attributes
            var fields = new List<SearchField>
            {
                // Key field (required) - unique identifier for each document
                new SearchField("id", SearchFieldDataType.String)
                {
                    IsKey = true,
                    IsSearchable = false,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Searchable text fields - enable full-text search
                new SearchField("title", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true,
                    AnalyzerName = LexicalAnalyzerName.EnMicrosoft // English language analyzer
                },

                new SearchField("content", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true,
                    AnalyzerName = LexicalAnalyzerName.EnMicrosoft
                },

                // Simple fields for exact matching and filtering
                new SearchField("author", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,  // Enable filtering by author
                    IsSortable = false,
                    IsFacetable = true,   // Enable faceting for navigation
                    IsRetrievable = true
                },

                new SearchField("category", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                // Date field - filterable and sortable
                new SearchField("publishedDate", SearchFieldDataType.DateTimeOffset)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Collection field for multiple values
                new SearchField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String))
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                // Numeric fields
                new SearchField("rating", SearchFieldDataType.Double)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                new SearchField("viewCount", SearchFieldDataType.Int32)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Boolean field
                new SearchField("isPublished", SearchFieldDataType.Boolean)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                }
            };

            // Display schema information
            Console.WriteLine($"✅ Schema defined with {fields.Count} fields:");
            Console.WriteLine($"{"Field Name",-15} | {"Type",-25} | {"Attributes"}");
            Console.WriteLine(new string('-', 70));

            foreach (var field in fields)
            {
                var attributes = new List<string>();
                if (field.IsKey == true) attributes.Add("KEY");
                if (field.IsSearchable == true) attributes.Add("searchable");
                if (field.IsFilterable == true) attributes.Add("filterable");
                if (field.IsSortable == true) attributes.Add("sortable");
                if (field.IsFacetable == true) attributes.Add("facetable");

                var attrStr = attributes.Any() ? string.Join(", ", attributes) : "retrievable only";
                Console.WriteLine($"{field.Name,-15} | {field.Type,-25} | {attrStr}");
            }

            return fields;
        }

        /// <summary>
        /// Create the search index
        /// </summary>
        public async Task<SearchIndex?> CreateIndexAsync(string indexName, IList<SearchField> fields)
        {
            Console.WriteLine($"🏗️  Creating index '{indexName}'...");

            try
            {
                // Create the index object
                var index = new SearchIndex(indexName, fields);

                // Create the index (use CreateOrUpdateIndexAsync for safety)
                var result = await _indexClient!.CreateOrUpdateIndexAsync(index);

                Console.WriteLine($"✅ Index '{result.Value.Name}' created successfully!");
                Console.WriteLine($"   Fields: {result.Value.Fields.Count}");
                Console.WriteLine($"   Created at: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");

                return result.Value;
            }
            catch (RequestFailedException ex) when (ex.Status == 400)
            {
                Console.WriteLine($"❌ Bad request - check index definition: {ex.Message}");
                return null;
            }
            catch (RequestFailedException ex) when (ex.Status == 409)
            {
                Console.WriteLine($"❌ Index already exists (this shouldn't happen with CreateOrUpdateIndexAsync)");
                return null;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ HTTP error {ex.Status}: {ex.Message}");
                return null;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create index: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Validate that the index was created correctly
        /// </summary>
        public async Task<bool> ValidateIndexAsync(string indexName)
        {
            Console.WriteLine($"🔍 Validating index '{indexName}'...");

            try
            {
                // Get the index details
                var response = await _indexClient!.GetIndexAsync(indexName);
                var index = response.Value;

                Console.WriteLine($"✅ Index validation successful:");
                Console.WriteLine($"   Name: {index.Name}");
                Console.WriteLine($"   Fields: {index.Fields.Count}");

                // Validate key field exists
                var keyFields = index.Fields.Where(f => f.IsKey == true).ToList();
                if (keyFields.Count == 1)
                {
                    Console.WriteLine($"   Key field: {keyFields[0].Name}");
                }
                else
                {
                    Console.WriteLine($"   ⚠️  Warning: Found {keyFields.Count} key fields (should be 1)");
                }

                // Count searchable fields
                var searchableFields = index.Fields.Where(f => f.IsSearchable == true).ToList();
                Console.WriteLine($"   Searchable fields: {searchableFields.Count}");

                // Count filterable fields
                var filterableFields = index.Fields.Where(f => f.IsFilterable == true).ToList();
                Console.WriteLine($"   Filterable fields: {filterableFields.Count}");

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Index validation failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Test basic index functionality with a sample document
        /// </summary>
        public async Task<bool> TestIndexFunctionalityAsync(string indexName)
        {
            Console.WriteLine($"🧪 Testing index functionality...");

            try
            {
                // Create search client for document operations
                var searchClient = new SearchClient(
                    new Uri(_endpoint),
                    indexName,
                    new AzureKeyCredential(_adminKey)
                );

                // Create a test document
                var testDocument = new Dictionary<string, object>
                {
                    ["id"] = "test-doc-1",
                    ["title"] = "Test Document for Index Validation",
                    ["content"] = "This is a test document to validate that our newly created index is working correctly.",
                    ["author"] = "Test Author",
                    ["category"] = "Test",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T10:00:00Z"),
                    ["tags"] = new[] { "test", "validation", "index" },
                    ["rating"] = 5.0,
                    ["viewCount"] = 1,
                    ["isPublished"] = true
                };

                // Upload the test document
                var uploadResult = await searchClient.UploadDocumentsAsync(new[] { testDocument });

                if (uploadResult.Value.Results[0].Succeeded)
                {
                    Console.WriteLine("✅ Test document uploaded successfully");

                    // Wait a moment for indexing
                    await Task.Delay(2000);

                    // Try to get document count
                    var docCount = await searchClient.GetDocumentCountAsync();
                    Console.WriteLine($"✅ Index contains {docCount.Value:N0} document(s)");

                    // Clean up - delete the test document
                    var deleteResult = await searchClient.DeleteDocumentsAsync("id", new[] { "test-doc-1" });
                    if (deleteResult.Value.Results[0].Succeeded)
                    {
                        Console.WriteLine("✅ Test document cleaned up successfully");
                    }

                    return true;
                }
                else
                {
                    Console.WriteLine($"❌ Test document upload failed: {uploadResult.Value.Results[0].ErrorMessage}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Index functionality test failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// List existing indexes in the service
        /// </summary>
        public async Task ListExistingIndexesAsync()
        {
            Console.WriteLine("📋 Listing existing indexes...");

            try
            {
                var indexes = new List<SearchIndex>();
                await foreach (var index in _indexClient!.GetIndexesAsync())
                {
                    indexes.Add(index);
                }

                if (indexes.Any())
                {
                    Console.WriteLine($"Found {indexes.Count} existing indexes:");
                    foreach (var index in indexes)
                    {
                        Console.WriteLine($"   - {index.Name} ({index.Fields.Count} fields)");
                    }
                }
                else
                {
                    Console.WriteLine("No existing indexes found");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to list indexes: {ex.Message}");
            }
        }

        /// <summary>
        /// Clean up the created index (optional)
        /// </summary>
        public async Task<bool> CleanupIndexAsync(string indexName)
        {
            Console.WriteLine($"🧹 Cleaning up index '{indexName}'...");

            try
            {
                await _indexClient!.DeleteIndexAsync(indexName);
                Console.WriteLine($"✅ Index '{indexName}' deleted successfully");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to delete index: {ex.Message}");
                return false;
            }
        }
    }

    /// <summary>
    /// Main program demonstrating basic index creation
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("Module 3: Basic Index Creation Example (C#)");
            Console.WriteLine(new string('=', 60));

            // Initialize the index creator
            BasicIndexCreator creator;
            try
            {
                creator = new BasicIndexCreator();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                Console.WriteLine("\nPlease set the required environment variables:");
                Console.WriteLine("   set AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net");
                Console.WriteLine("   set AZURE_SEARCH_ADMIN_KEY=your-admin-api-key");
                return;
            }

            // Create index client
            if (!await creator.CreateIndexClientAsync())
            {
                Console.WriteLine("❌ Failed to create index client. Exiting.");
                return;
            }

            // List existing indexes
            await creator.ListExistingIndexesAsync();

            // Define the index schema
            var fields = creator.DefineBasicSchema();

            // Create the index
            const string indexName = "basic-blog-index-cs";
            var index = await creator.CreateIndexAsync(indexName, fields);

            if (index != null)
            {
                // Validate the index
                if (await creator.ValidateIndexAsync(indexName))
                {
                    // Test index functionality
                    if (await creator.TestIndexFunctionalityAsync(indexName))
                    {
                        Console.WriteLine("\n🎉 Index creation and testing completed successfully!");

                        // Ask if user wants to clean up
                        Console.Write($"\nDo you want to delete the test index '{indexName}'? (y/N): ");
                        var response = Console.ReadLine();
                        if (string.Equals(response?.Trim(), "y", StringComparison.OrdinalIgnoreCase) ||
                            string.Equals(response?.Trim(), "yes", StringComparison.OrdinalIgnoreCase))
                        {
                            await creator.CleanupIndexAsync(indexName);
                        }
                        else
                        {
                            Console.WriteLine($"ℹ️  Index '{indexName}' preserved for further experimentation");
                        }
                    }
                    else
                    {
                        Console.WriteLine("⚠️  Index created but functionality test failed");
                    }
                }
                else
                {
                    Console.WriteLine("⚠️  Index created but validation failed");
                }
            }
            else
            {
                Console.WriteLine("❌ Index creation failed");
            }

            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("Example completed!");
            Console.WriteLine(new string('=', 60));

            Console.WriteLine("\n📚 What you learned:");
            Console.WriteLine("✅ How to create SearchIndexClient with proper authentication");
            Console.WriteLine("✅ How to define field types and attributes using SearchField");
            Console.WriteLine("✅ How to create a basic index schema with async patterns");
            Console.WriteLine("✅ How to handle index creation responses with proper error handling");
            Console.WriteLine("✅ How to validate index creation and test functionality");

            Console.WriteLine("\n🚀 Next steps:");
            Console.WriteLine("1. Try modifying the schema with different field types");
            Console.WriteLine("2. Experiment with different field attributes");
            Console.WriteLine("3. Run the next example: 02_SchemaDesign.cs");
            Console.WriteLine("4. Upload real documents to your index");

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}