/*
 * Module 3: Index Management - Index Operations and Maintenance (C#)
 * =================================================================
 * 
 * This example demonstrates various index management operations including updating schemas,
 * managing documents, monitoring index health, and performing maintenance tasks using the
 * .NET SDK with proper async/await patterns.
 * 
 * Learning Objectives:
 * - Perform index lifecycle operations (create, update, delete)
 * - Update index schemas safely
 * - Monitor index health and statistics
 * - Manage document operations (update, merge, delete)
 * - Handle index versioning and maintenance
 * 
 * Prerequisites:
 * - Completed previous examples (01-03)
 * - Understanding of index schemas and data ingestion
 * - Azure AI Search service with admin access
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
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module03
{
    /// <summary>
    /// Demonstrates index operations and maintenance using the .NET SDK
    /// </summary>
    public class IndexOperationsManager
    {
        private readonly string _endpoint;
        private readonly string _adminKey;
        private SearchIndexClient? _indexClient;
        private SearchClient? _searchClient;

        /// <summary>
        /// Initialize the index operations manager
        /// </summary>
        public IndexOperationsManager()
        {
            _endpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_SERVICE_ENDPOINT environment variable is required");
            
            _adminKey = Environment.GetEnvironmentVariable("AZURE_SEARCH_ADMIN_KEY") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_ADMIN_KEY environment variable is required");
        }

        /// <summary>
        /// Create and validate the search clients
        /// </summary>
        public async Task<bool> CreateClientsAsync()
        {
            Console.WriteLine("🔍 Creating Search Clients...");

            try
            {
                _indexClient = new SearchIndexClient(
                    new Uri(_endpoint),
                    new AzureKeyCredential(_adminKey)
                );

                // Test connection
                var stats = await _indexClient.GetServiceStatisticsAsync();
                Console.WriteLine("✅ Connected to Azure AI Search service");
                Console.WriteLine($"   Storage used: {stats.Value.StorageSize:N0} bytes");
                Console.WriteLine($"   Document count: {stats.Value.DocumentCount:N0}");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create clients: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Create a sample index for operations testing
        /// </summary>
        public async Task<string?> CreateOperationsTestIndexAsync()
        {
            Console.WriteLine("🏗️  Creating operations test index...");

            const string indexName = "index-operations-demo-cs";

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
                var index = new SearchIndex(indexName, fields);
                var result = await _indexClient!.CreateOrUpdateIndexAsync(index);

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
                Console.WriteLine($"❌ Failed to create index: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Demonstrate index schema updates
        /// </summary>
        public async Task<bool> UpdateIndexSchemaAsync()
        {
            Console.WriteLine("🔄 Index Schema Update Example...");

            try
            {
                // Get current index
                var currentIndex = await _indexClient!.GetIndexAsync(_searchClient!.IndexName);
                
                Console.WriteLine($"   Current index has {currentIndex.Value.Fields.Count} fields");

                // Create updated field list with new field
                var updatedFields = currentIndex.Value.Fields.ToList();
                
                // Add a new field
                var newField = new SearchField("readingTime", SearchFieldDataType.Int32)
                {
                    IsFilterable = true,
                    IsSortable = true
                };
                
                updatedFields.Add(newField);

                // Create updated index
                var updatedIndex = new SearchIndex(currentIndex.Value.Name, updatedFields)
                {
                    // Preserve other index properties
                    Analyzers = currentIndex.Value.Analyzers,
                    ScoringProfiles = currentIndex.Value.ScoringProfiles,
                    CorsOptions = currentIndex.Value.CorsOptions
                };

                // Update the index
                var result = await _indexClient.CreateOrUpdateIndexAsync(updatedIndex);
                
                Console.WriteLine($"✅ Index schema updated successfully");
                Console.WriteLine($"   Updated index has {result.Value.Fields.Count} fields");
                Console.WriteLine($"   New field added: {newField.Name} ({newField.Type})");

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Schema update failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Demonstrate document lifecycle operations
        /// </summary>
        public async Task<bool> DocumentLifecycleOperationsAsync()
        {
            Console.WriteLine("📄 Document Lifecycle Operations...");

            try
            {
                // 1. Upload initial documents
                Console.WriteLine("   Step 1: Uploading initial documents...");
                var initialDocs = GenerateInitialDocuments();
                
                var uploadResult = await _searchClient!.UploadDocumentsAsync(initialDocs);
                var successfulUploads = uploadResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Uploaded {successfulUploads} initial documents");

                // Wait for indexing
                await Task.Delay(2000);

                // 2. Update existing documents
                Console.WriteLine("   Step 2: Updating existing documents...");
                var updateDocs = new[]
                {
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-1",
                        ["title"] = "Updated: Index Operations and Maintenance",
                        ["rating"] = 4.8,
                        ["viewCount"] = 250,
                        ["readingTime"] = 15 // New field
                    }
                };

                var updateResult = await _searchClient.MergeDocumentsAsync(updateDocs);
                var successfulUpdates = updateResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Updated {successfulUpdates} documents");

                // 3. Upsert operations (merge or upload)
                Console.WriteLine("   Step 3: Upsert operations...");
                var upsertDocs = new[]
                {
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-4", // New document
                        ["title"] = "New Document via Upsert",
                        ["content"] = "This document was created via merge or upload operation.",
                        ["category"] = "Operations",
                        ["author"] = "Operations Manager",
                        ["publishedDate"] = DateTimeOffset.Parse("2024-02-15T10:00:00Z"),
                        ["rating"] = 4.2,
                        ["viewCount"] = 50,
                        ["tags"] = new[] { "operations", "upsert", "new" },
                        ["isPublished"] = true,
                        ["readingTime"] = 8
                    },
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-2", // Existing document - will be merged
                        ["content"] = "Updated content for existing document via upsert.",
                        ["rating"] = 4.9,
                        ["readingTime"] = 12
                    }
                };

                var upsertResult = await _searchClient.MergeOrUploadDocumentsAsync(upsertDocs);
                var successfulUpserts = upsertResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Upserted {successfulUpserts} documents");

                // Wait for indexing
                await Task.Delay(2000);

                // 4. Verify current state
                var docCount = await _searchClient.GetDocumentCountAsync();
                Console.WriteLine($"   📊 Current document count: {docCount.Value}");

                // 5. Delete specific documents
                Console.WriteLine("   Step 4: Deleting specific documents...");
                var deleteResult = await _searchClient.DeleteDocumentsAsync("id", new[] { "ops-doc-3" });
                var successfulDeletes = deleteResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Deleted {successfulDeletes} documents");

                // Wait for indexing
                await Task.Delay(2000);

                // 6. Final verification
                var finalCount = await _searchClient.GetDocumentCountAsync();
                Console.WriteLine($"   📊 Final document count: {finalCount.Value}");

                Console.WriteLine("✅ Document lifecycle operations completed successfully");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Document lifecycle operations failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Monitor index health and performance
        /// </summary>
        public async Task<bool> MonitorIndexHealthAsync()
        {
            Console.WriteLine("🏥 Index Health Monitoring...");

            try
            {
                // Get service statistics
                var serviceStats = await _indexClient!.GetServiceStatisticsAsync();
                Console.WriteLine("📊 Service Statistics:");
                Console.WriteLine($"   Storage used: {serviceStats.Value.StorageSize:N0} bytes");
                Console.WriteLine($"   Total documents: {serviceStats.Value.DocumentCount:N0}");

                // Get index information
                var index = await _indexClient.GetIndexAsync(_searchClient!.IndexName);
                Console.WriteLine($"\n📋 Index Information:");
                Console.WriteLine($"   Name: {index.Value.Name}");
                Console.WriteLine($"   Fields: {index.Value.Fields.Count}");
                Console.WriteLine($"   Analyzers: {index.Value.Analyzers?.Count ?? 0}");
                Console.WriteLine($"   Scoring Profiles: {index.Value.ScoringProfiles?.Count ?? 0}");

                // Get document count for this specific index
                var docCount = await _searchClient.GetDocumentCountAsync();
                Console.WriteLine($"   Documents: {docCount.Value}");

                // Test search performance
                Console.WriteLine("\n⚡ Performance Testing:");
                var performanceTests = new[]
                {
                    new { Name = "Simple Search", Query = "operations" },
                    new { Name = "Filtered Search", Query = "operations", Filter = "category eq 'Operations'" },
                    new { Name = "Faceted Search", Query = "*", Facets = new[] { "category", "author" } }
                };

                foreach (var test in performanceTests)
                {
                    var startTime = DateTime.Now;
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = test.Filter,
                        IncludeTotalCount = true,
                        Size = 10
                    };

                    if (test.Facets != null)
                    {
                        foreach (var facet in test.Facets)
                        {
                            searchOptions.Facets.Add(facet);
                        }
                    }

                    var results = await _searchClient.SearchAsync<Dictionary<string, object>>(test.Query, searchOptions);
                    var responseTime = (DateTime.Now - startTime).TotalMilliseconds;

                    Console.WriteLine($"   {test.Name}: {responseTime:F0}ms ({results.Value.TotalCount} results)");
                }

                // Check for common issues
                Console.WriteLine("\n🔍 Health Check Results:");
                
                // Check if index has documents
                if (docCount.Value == 0)
                {
                    Console.WriteLine("   ⚠️  Warning: Index is empty");
                }
                else
                {
                    Console.WriteLine("   ✅ Index contains documents");
                }

                // Check if all fields are being used
                var sampleDoc = await GetSampleDocumentAsync();
                if (sampleDoc != null)
                {
                    var fieldsWithData = sampleDoc.Keys.Count;
                    var totalFields = index.Value.Fields.Count;
                    var fieldUtilization = (double)fieldsWithData / totalFields * 100;
                    
                    Console.WriteLine($"   📈 Field utilization: {fieldUtilization:F1}% ({fieldsWithData}/{totalFields} fields)");
                    
                    if (fieldUtilization < 50)
                    {
                        Console.WriteLine("   ⚠️  Warning: Low field utilization - consider schema optimization");
                    }
                }

                Console.WriteLine("✅ Index health monitoring completed");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Health monitoring failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Demonstrate index maintenance operations
        /// </summary>
        public async Task<bool> IndexMaintenanceOperationsAsync()
        {
            Console.WriteLine("🔧 Index Maintenance Operations...");

            try
            {
                // 1. Rebuild index statistics
                Console.WriteLine("   Step 1: Analyzing index usage patterns...");
                await AnalyzeIndexUsageAsync();

                // 2. Optimize document storage
                Console.WriteLine("   Step 2: Optimizing document storage...");
                await OptimizeDocumentStorageAsync();

                // 3. Clean up test data
                Console.WriteLine("   Step 3: Cleaning up test data...");
                await CleanupTestDataAsync();

                // 4. Validate index integrity
                Console.WriteLine("   Step 4: Validating index integrity...");
                await ValidateIndexIntegrityAsync();

                Console.WriteLine("✅ Index maintenance operations completed");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Index maintenance failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Generate initial documents for testing
        /// </summary>
        private List<Dictionary<string, object>> GenerateInitialDocuments()
        {
            return new List<Dictionary<string, object>>
            {
                new Dictionary<string, object>
                {
                    ["id"] = "ops-doc-1",
                    ["title"] = "Index Operations and Maintenance",
                    ["content"] = "Comprehensive guide to managing Azure AI Search indexes including operations, monitoring, and maintenance tasks.",
                    ["category"] = "Operations",
                    ["author"] = "Operations Team",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T10:00:00Z"),
                    ["rating"] = 4.5,
                    ["viewCount"] = 200,
                    ["tags"] = new[] { "operations", "maintenance", "guide" },
                    ["isPublished"] = true
                },
                new Dictionary<string, object>
                {
                    ["id"] = "ops-doc-2",
                    ["title"] = "Schema Design Best Practices",
                    ["content"] = "Learn how to design effective schemas for Azure AI Search indexes with performance and maintainability in mind.",
                    ["category"] = "Best Practices",
                    ["author"] = "Architecture Team",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-11T14:30:00Z"),
                    ["rating"] = 4.7,
                    ["viewCount"] = 180,
                    ["tags"] = new[] { "schema", "design", "best-practices" },
                    ["isPublished"] = true
                },
                new Dictionary<string, object>
                {
                    ["id"] = "ops-doc-3",
                    ["title"] = "Performance Monitoring Strategies",
                    ["content"] = "Effective strategies for monitoring and optimizing the performance of your Azure AI Search implementation.",
                    ["category"] = "Performance",
                    ["author"] = "Performance Team",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-12T09:15:00Z"),
                    ["rating"] = 4.3,
                    ["viewCount"] = 150,
                    ["tags"] = new[] { "performance", "monitoring", "optimization" },
                    ["isPublished"] = true
                }
            };
        }

        /// <summary>
        /// Get a sample document for analysis
        /// </summary>
        private async Task<Dictionary<string, object>?> GetSampleDocumentAsync()
        {
            try
            {
                var results = await _searchClient!.SearchAsync<Dictionary<string, object>>("*", new SearchOptions { Size = 1 });
                
                await foreach (var result in results.Value.GetResultsAsync())
                {
                    return result.Document;
                }
                
                return null;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Analyze index usage patterns
        /// </summary>
        private async Task AnalyzeIndexUsageAsync()
        {
            try
            {
                // Analyze field usage
                var searchResults = await _searchClient!.SearchAsync<Dictionary<string, object>>("*", new SearchOptions 
                { 
                    Size = 100,
                    IncludeTotalCount = true
                });

                var fieldUsage = new Dictionary<string, int>();
                var totalDocs = 0;

                await foreach (var result in searchResults.Value.GetResultsAsync())
                {
                    totalDocs++;
                    foreach (var field in result.Document.Keys)
                    {
                        fieldUsage[field] = fieldUsage.GetValueOrDefault(field, 0) + 1;
                    }
                }

                Console.WriteLine($"   📊 Analyzed {totalDocs} documents");
                Console.WriteLine("   Field usage statistics:");
                
                foreach (var field in fieldUsage.OrderByDescending(f => f.Value))
                {
                    var percentage = (double)field.Value / totalDocs * 100;
                    Console.WriteLine($"     {field.Key}: {percentage:F1}% ({field.Value}/{totalDocs})");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"   ⚠️  Analysis warning: {ex.Message}");
            }
        }

        /// <summary>
        /// Optimize document storage
        /// </summary>
        private async Task OptimizeDocumentStorageAsync()
        {
            try
            {
                // Check for documents with large content fields
                var results = await _searchClient!.SearchAsync<Dictionary<string, object>>("*", new SearchOptions 
                { 
                    Select = { "id", "content" },
                    Size = 50
                });

                var largeDocuments = new List<string>();
                
                await foreach (var result in results.Value.GetResultsAsync())
                {
                    if (result.Document.TryGetValue("content", out var content) && 
                        content is string contentStr && 
                        contentStr.Length > 10000)
                    {
                        largeDocuments.Add(result.Document["id"].ToString()!);
                    }
                }

                if (largeDocuments.Any())
                {
                    Console.WriteLine($"   📋 Found {largeDocuments.Count} documents with large content fields");
                    Console.WriteLine("   💡 Consider content summarization or field splitting for optimization");
                }
                else
                {
                    Console.WriteLine("   ✅ Document sizes are within optimal ranges");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"   ⚠️  Optimization warning: {ex.Message}");
            }
        }

        /// <summary>
        /// Clean up test data
        /// </summary>
        private async Task CleanupTestDataAsync()
        {
            try
            {
                // Find test documents (documents with "test" in title or content)
                var testResults = await _searchClient!.SearchAsync<Dictionary<string, object>>(
                    "test", 
                    new SearchOptions { Select = { "id" }, Size = 100 }
                );

                var testDocIds = new List<string>();
                await foreach (var result in testResults.Value.GetResultsAsync())
                {
                    testDocIds.Add(result.Document["id"].ToString()!);
                }

                if (testDocIds.Any())
                {
                    Console.WriteLine($"   🗑️  Found {testDocIds.Count} test documents");
                    Console.WriteLine("   💡 In production, consider implementing automated cleanup policies");
                    // Note: Not actually deleting in this demo to preserve data
                }
                else
                {
                    Console.WriteLine("   ✅ No test documents found requiring cleanup");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"   ⚠️  Cleanup warning: {ex.Message}");
            }
        }

        /// <summary>
        /// Validate index integrity
        /// </summary>
        private async Task ValidateIndexIntegrityAsync()
        {
            try
            {
                // Check for duplicate IDs (shouldn't happen with proper key field)
                var allDocs = await _searchClient!.SearchAsync<Dictionary<string, object>>("*", new SearchOptions 
                { 
                    Select = { "id" },
                    Size = 1000
                });

                var ids = new HashSet<string>();
                var duplicates = new List<string>();
                
                await foreach (var result in allDocs.Value.GetResultsAsync())
                {
                    var id = result.Document["id"].ToString()!;
                    if (!ids.Add(id))
                    {
                        duplicates.Add(id);
                    }
                }

                if (duplicates.Any())
                {
                    Console.WriteLine($"   ❌ Found {duplicates.Count} duplicate document IDs");
                    foreach (var duplicate in duplicates.Take(5))
                    {
                        Console.WriteLine($"     - {duplicate}");
                    }
                }
                else
                {
                    Console.WriteLine("   ✅ No duplicate document IDs found");
                }

                // Check for required field completeness
                var sampleResults = await _searchClient.SearchAsync<Dictionary<string, object>>("*", new SearchOptions { Size = 10 });
                var requiredFields = new[] { "id", "title" };
                var incompleteDocuments = 0;

                await foreach (var result in sampleResults.Value.GetResultsAsync())
                {
                    foreach (var requiredField in requiredFields)
                    {
                        if (!result.Document.ContainsKey(requiredField) || 
                            result.Document[requiredField] == null ||
                            string.IsNullOrEmpty(result.Document[requiredField].ToString()))
                        {
                            incompleteDocuments++;
                            break;
                        }
                    }
                }

                if (incompleteDocuments > 0)
                {
                    Console.WriteLine($"   ⚠️  Found {incompleteDocuments} documents missing required fields");
                }
                else
                {
                    Console.WriteLine("   ✅ All sampled documents have required fields");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"   ⚠️  Validation warning: {ex.Message}");
            }
        }

        /// <summary>
        /// Get index operations statistics
        /// </summary>
        public async Task GetIndexOperationsStatisticsAsync()
        {
            Console.WriteLine("📊 Current Index Operations Statistics:");

            try
            {
                var docCount = await _searchClient!.GetDocumentCountAsync();
                Console.WriteLine($"   Total documents: {docCount.Value}");

                // Sample some documents to show variety
                var searchOptions = new SearchOptions
                {
                    Size = 5,
                    Select = { "id", "title", "category", "author" }
                };

                var results = await _searchClient.SearchAsync<Dictionary<string, object>>("*", searchOptions);

                Console.WriteLine("   Sample documents:");
                await foreach (var result in results.Value.GetResultsAsync())
                {
                    var doc = result.Document;
                    Console.WriteLine($"     - {doc["id"]}: {doc["title"]} ({doc.GetValueOrDefault("category", "N/A")})");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to get statistics: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Main program demonstrating index operations
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("=".PadRight(60, '='));
            Console.WriteLine("Module 3: Index Operations and Maintenance Example (C#)");
            Console.WriteLine("=".PadRight(60, '='));

            // Initialize the index operations manager
            IndexOperationsManager manager;
            try
            {
                manager = new IndexOperationsManager();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                return;
            }

            // Create clients
            if (!await manager.CreateClientsAsync())
            {
                Console.WriteLine("❌ Failed to create clients. Exiting.");
                return;
            }

            // Create operations test index
            var indexName = await manager.CreateOperationsTestIndexAsync();
            if (indexName == null)
            {
                Console.WriteLine("❌ Failed to create operations test index. Exiting.");
                return;
            }

            Console.WriteLine($"\n🎯 Running index operations demonstrations on index '{indexName}'...");

            // Run demonstrations
            var demonstrations = new (string Name, Func<Task<bool>> Func)[]
            {
                ("Index Schema Updates", manager.UpdateIndexSchemaAsync),
                ("Document Lifecycle Operations", manager.DocumentLifecycleOperationsAsync),
                ("Index Health Monitoring", manager.MonitorIndexHealthAsync),
                ("Index Maintenance Operations", manager.IndexMaintenanceOperationsAsync)
            };

            foreach (var (name, func) in demonstrations)
            {
                Console.WriteLine($"\n{"=".PadRight(20, '=')} {name} {"=".PadRight(20, '=')}");
                try
                {
                    var success = await func();
                    if (success)
                    {
                        Console.WriteLine($"✅ {name} completed successfully");
                    }
                    else
                    {
                        Console.WriteLine($"⚠️  {name} completed with issues");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"❌ {name} failed: {ex.Message}");
                }

                // Brief pause between demonstrations
                await Task.Delay(1000);
            }

            // Show current statistics
            Console.WriteLine($"\n{"=".PadRight(20, '=')} Current Statistics {"=".PadRight(20, '=')}");
            await manager.GetIndexOperationsStatisticsAsync();

            Console.WriteLine("\n" + "=".PadRight(60, '='));
            Console.WriteLine("Example completed!");
            Console.WriteLine("=".PadRight(60, '='));

            Console.WriteLine("\n📚 What you learned:");
            Console.WriteLine("✅ How to perform index lifecycle operations");
            Console.WriteLine("✅ How to update index schemas safely");
            Console.WriteLine("✅ How to monitor index health and statistics");
            Console.WriteLine("✅ How to manage document operations");
            Console.WriteLine("✅ How to handle index versioning and maintenance");

            Console.WriteLine("\n🚀 Next steps:");
            Console.WriteLine("1. Implement index monitoring in your applications");
            Console.WriteLine("2. Set up automated maintenance procedures");
            Console.WriteLine("3. Run the next example: 05_PerformanceOptimization.cs");
            Console.WriteLine("4. Plan index lifecycle management for production");

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}