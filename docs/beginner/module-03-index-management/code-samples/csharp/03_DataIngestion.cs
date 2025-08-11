/*
 * Module 3: Index Management - Data Ingestion Strategies (C#)
 * ===========================================================
 * 
 * This example demonstrates efficient data ingestion strategies for Azure AI Search
 * using the .NET SDK. You'll learn about batch operations, large dataset handling,
 * progress tracking, and optimization techniques for document uploads.
 * 
 * Learning Objectives:
 * - Implement single and batch document uploads
 * - Handle large datasets efficiently
 * - Optimize batch sizes for performance
 * - Track upload progress and handle errors
 * - Use different document actions (upload, merge, delete)
 * 
 * Prerequisites:
 * - Completed 01_CreateBasicIndex.cs and 02_SchemaDesign.cs
 * - Understanding of index schemas
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
    /// Demonstrates advanced data ingestion strategies using the .NET SDK
    /// </summary>
    public class DataIngestionManager
    {
        private readonly string _endpoint;
        private readonly string _adminKey;
        private SearchIndexClient? _indexClient;
        private SearchClient? _searchClient;

        /// <summary>
        /// Initialize the data ingestion manager
        /// </summary>
        public DataIngestionManager()
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
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create clients: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Create a sample index for data ingestion testing
        /// </summary>
        public async Task<string?> CreateSampleIndexAsync()
        {
            Console.WriteLine("🏗️  Creating sample index for data ingestion...");

            const string indexName = "data-ingestion-demo-cs";

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
        /// Demonstrate single document upload
        /// </summary>
        public async Task<bool> SingleDocumentUploadAsync()
        {
            Console.WriteLine("📄 Single Document Upload Example...");

            try
            {
                // Create a single document
                var document = new Dictionary<string, object>
                {
                    ["id"] = "single-doc-1",
                    ["title"] = "Single Document Upload Example",
                    ["content"] = "This document demonstrates how to upload a single document to Azure AI Search.",
                    ["category"] = "Tutorial",
                    ["author"] = "Data Ingestion Manager",
                    ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T10:00:00Z"),
                    ["rating"] = 4.5,
                    ["viewCount"] = 100,
                    ["tags"] = new[] { "tutorial", "single-upload", "example" },
                    ["isPublished"] = true
                };

                // Upload the document
                var startTime = DateTime.Now;
                var result = await _searchClient!.UploadDocumentsAsync(new[] { document });
                var uploadTime = (DateTime.Now - startTime).TotalSeconds;

                if (result.Value.Results[0].Succeeded)
                {
                    Console.WriteLine($"✅ Document uploaded successfully in {uploadTime:F3} seconds");
                    Console.WriteLine($"   Document ID: {result.Value.Results[0].Key}");
                    return true;
                }
                else
                {
                    Console.WriteLine($"❌ Upload failed: {result.Value.Results[0].ErrorMessage}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Single document upload failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Demonstrate batch document upload
        /// </summary>
        public async Task<bool> BatchDocumentUploadAsync(int batchSize = 10)
        {
            Console.WriteLine($"📦 Batch Document Upload Example (batch size: {batchSize})...");

            try
            {
                // Generate sample documents
                var documents = GenerateSampleDocuments(batchSize);

                // Upload documents in batch
                var startTime = DateTime.Now;
                var result = await _searchClient!.UploadDocumentsAsync(documents);
                var uploadTime = (DateTime.Now - startTime).TotalSeconds;

                // Analyze results
                var successful = result.Value.Results.Count(r => r.Succeeded);
                var failed = result.Value.Results.Count - successful;

                Console.WriteLine($"✅ Batch upload completed in {uploadTime:F3} seconds");
                Console.WriteLine($"   Successful: {successful}/{documents.Count}");
                Console.WriteLine($"   Failed: {failed}");
                Console.WriteLine($"   Rate: {successful / uploadTime:F1} documents/second");

                // Show any failures
                foreach (var r in result.Value.Results.Where(r => !r.Succeeded))
                {
                    Console.WriteLine($"   ❌ Failed: {r.Key} - {r.ErrorMessage}");
                }

                return successful > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Batch upload failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Demonstrate large dataset upload with progress tracking
        /// </summary>
        public async Task<bool> LargeDatasetUploadAsync(int totalDocuments = 1000, int batchSize = 100)
        {
            Console.WriteLine($"🗂️  Large Dataset Upload Example ({totalDocuments} documents, batch size: {batchSize})...");

            try
            {
                var totalSuccessful = 0;
                var totalFailed = 0;
                var totalTime = 0.0;

                // Process in batches
                for (var batchNum = 0; batchNum < totalDocuments; batchNum += batchSize)
                {
                    var currentBatchSize = Math.Min(batchSize, totalDocuments - batchNum);

                    // Generate batch documents
                    var documents = GenerateSampleDocuments(currentBatchSize, batchNum + 1);

                    // Upload batch
                    var startTime = DateTime.Now;
                    var result = await _searchClient!.UploadDocumentsAsync(documents);
                    var batchTime = (DateTime.Now - startTime).TotalSeconds;
                    totalTime += batchTime;

                    // Track results
                    var successful = result.Value.Results.Count(r => r.Succeeded);
                    var failed = result.Value.Results.Count - successful;

                    totalSuccessful += successful;
                    totalFailed += failed;

                    // Progress update
                    var progress = ((double)(batchNum + currentBatchSize) / totalDocuments) * 100;
                    var rate = successful / batchTime;

                    Console.WriteLine($"   Batch {batchNum / batchSize + 1}: {successful}/{currentBatchSize} uploaded " +
                                    $"({rate:F1} docs/sec) - Progress: {progress:F1}%");

                    // Brief pause to avoid overwhelming the service
                    if (batchNum + batchSize < totalDocuments)
                    {
                        await Task.Delay(100);
                    }
                }

                // Final summary
                var overallRate = totalSuccessful / totalTime;
                Console.WriteLine($"\n✅ Large dataset upload completed:");
                Console.WriteLine($"   Total successful: {totalSuccessful}");
                Console.WriteLine($"   Total failed: {totalFailed}");
                Console.WriteLine($"   Total time: {totalTime:F2} seconds");
                Console.WriteLine($"   Overall rate: {overallRate:F1} documents/second");

                return totalSuccessful > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Large dataset upload failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Demonstrate different document operations (upload, merge, delete)
        /// </summary>
        public async Task<bool> DocumentOperationsDemoAsync()
        {
            Console.WriteLine("🔄 Document Operations Demo (Upload, Merge, Delete)...");

            try
            {
                // 1. Upload initial documents
                Console.WriteLine("   Step 1: Uploading initial documents...");
                var initialDocs = new[]
                {
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-1",
                        ["title"] = "Original Title 1",
                        ["content"] = "Original content for document 1",
                        ["category"] = "Original",
                        ["author"] = "Original Author",
                        ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T10:00:00Z"),
                        ["rating"] = 3.0,
                        ["viewCount"] = 50,
                        ["tags"] = new[] { "original" },
                        ["isPublished"] = true
                    },
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-2",
                        ["title"] = "Original Title 2",
                        ["content"] = "Original content for document 2",
                        ["category"] = "Original",
                        ["author"] = "Original Author",
                        ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T11:00:00Z"),
                        ["rating"] = 3.5,
                        ["viewCount"] = 75,
                        ["tags"] = new[] { "original" },
                        ["isPublished"] = true
                    }
                };

                var uploadResult = await _searchClient!.UploadDocumentsAsync(initialDocs);
                var successfulUploads = uploadResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Uploaded {successfulUploads} initial documents");

                // Wait for indexing
                await Task.Delay(2000);

                // 2. Merge operation (partial update)
                Console.WriteLine("   Step 2: Merging document updates...");
                var mergeDocs = new[]
                {
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-1",
                        ["title"] = "Updated Title 1",  // Update title
                        ["rating"] = 4.5,  // Update rating
                        ["viewCount"] = 150  // Update view count
                        // Other fields remain unchanged
                    }
                };

                var mergeResult = await _searchClient.MergeDocumentsAsync(mergeDocs);
                var successfulMerges = mergeResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Merged {successfulMerges} document updates");

                // 3. Merge or upload operation (upsert)
                Console.WriteLine("   Step 3: Merge or upload (upsert) operation...");
                var upsertDocs = new[]
                {
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-3",  // New document
                        ["title"] = "New Document via Upsert",
                        ["content"] = "This document was created via MergeOrUpload",
                        ["category"] = "Upsert",
                        ["author"] = "Upsert Author",
                        ["publishedDate"] = DateTimeOffset.Parse("2024-02-10T12:00:00Z"),
                        ["rating"] = 4.0,
                        ["viewCount"] = 25,
                        ["tags"] = new[] { "upsert", "new" },
                        ["isPublished"] = true
                    },
                    new Dictionary<string, object>
                    {
                        ["id"] = "ops-doc-2",  // Existing document - will be merged
                        ["content"] = "Updated content for document 2",
                        ["rating"] = 4.8
                    }
                };

                var upsertResult = await _searchClient.MergeOrUploadDocumentsAsync(upsertDocs);
                var successfulUpserts = upsertResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Upserted {successfulUpserts} documents");

                // Wait for indexing
                await Task.Delay(2000);

                // 4. Verify current state
                Console.WriteLine("   Step 4: Verifying current document state...");
                var docCount = await _searchClient.GetDocumentCountAsync();
                Console.WriteLine($"   📊 Current document count: {docCount.Value}");

                // 5. Delete operation
                Console.WriteLine("   Step 5: Deleting a document...");
                var deleteResult = await _searchClient.DeleteDocumentsAsync("id", new[] { "ops-doc-2" });
                var successfulDeletes = deleteResult.Value.Results.Count(r => r.Succeeded);
                Console.WriteLine($"   ✅ Deleted {successfulDeletes} documents");

                // Wait for indexing
                await Task.Delay(2000);

                // 6. Final verification
                var finalCount = await _searchClient.GetDocumentCountAsync();
                Console.WriteLine($"   📊 Final document count: {finalCount.Value}");

                Console.WriteLine("✅ Document operations demo completed successfully");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Document operations demo failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Generate sample documents for testing
        /// </summary>
        private List<Dictionary<string, object>> GenerateSampleDocuments(int count, int startId = 1)
        {
            var documents = new List<Dictionary<string, object>>();
            var categories = new[] { "Technology", "Science", "Business", "Health", "Education" };
            var authors = new[] { "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eve Brown" };

            for (var i = 0; i < count; i++)
            {
                var docId = startId + i;
                var category = categories[i % categories.Length];
                var author = authors[i % authors.Length];

                var document = new Dictionary<string, object>
                {
                    ["id"] = $"doc-{docId}",
                    ["title"] = $"Sample Document {docId}: {category} Article",
                    ["content"] = $"This is sample content for document {docId}. It contains information about {category.ToLower()} topics and is written by {author}. The content is generated for testing purposes and demonstrates various aspects of the subject matter.",
                    ["category"] = category,
                    ["author"] = author,
                    ["publishedDate"] = DateTimeOffset.Parse($"2024-02-{(i % 28) + 1:D2}T{i % 24:D2}:00:00Z"),
                    ["rating"] = Math.Round(3.0 + (i % 20) * 0.1, 1),  // Rating between 3.0 and 5.0
                    ["viewCount"] = (i + 1) * 10 + (i % 100),
                    ["tags"] = new[] { category.ToLower(), "sample", $"tag{i % 5}" },
                    ["isPublished"] = i % 10 != 0  // 90% published
                };
                documents.Add(document);
            }

            return documents;
        }

        /// <summary>
        /// Get ingestion statistics
        /// </summary>
        public async Task GetIngestionStatisticsAsync()
        {
            Console.WriteLine("📊 Current Index Statistics:");

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

                Console.WriteLine($"   Sample documents:");
                await foreach (var result in results.Value.GetResultsAsync())
                {
                    var doc = result.Document;
                    Console.WriteLine($"     - {doc["id"]}: {doc["title"]} ({doc["category"]})");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to get statistics: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Main program demonstrating data ingestion strategies
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("=".PadRight(60, '='));
            Console.WriteLine("Module 3: Data Ingestion Strategies Example (C#)");
            Console.WriteLine("=".PadRight(60, '='));

            // Initialize the data ingestion manager
            DataIngestionManager manager;
            try
            {
                manager = new DataIngestionManager();
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

            // Create sample index
            var indexName = await manager.CreateSampleIndexAsync();
            if (indexName == null)
            {
                Console.WriteLine("❌ Failed to create sample index. Exiting.");
                return;
            }

            Console.WriteLine($"\n🎯 Running data ingestion demonstrations on index '{indexName}'...");

            // Run demonstrations
            var demonstrations = new (string Name, Func<Task<bool>> Func)[]
            {
                ("Single Document Upload", manager.SingleDocumentUploadAsync),
                ("Batch Document Upload", () => manager.BatchDocumentUploadAsync(50)),
                ("Large Dataset Upload", () => manager.LargeDatasetUploadAsync(200, 50)),
                ("Document Operations", manager.DocumentOperationsDemoAsync)
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
            await manager.GetIngestionStatisticsAsync();

            Console.WriteLine("\n" + "=".PadRight(60, '='));
            Console.WriteLine("Example completed!");
            Console.WriteLine("=".PadRight(60, '='));

            Console.WriteLine("\n📚 What you learned:");
            Console.WriteLine("✅ How to implement single and batch document uploads");
            Console.WriteLine("✅ How to handle large datasets efficiently");
            Console.WriteLine("✅ How to optimize batch sizes for performance");
            Console.WriteLine("✅ How to track upload progress and handle errors");
            Console.WriteLine("✅ How to use different document actions (upload, merge, delete)");

            Console.WriteLine("\n🚀 Next steps:");
            Console.WriteLine("1. Try ingesting your own data");
            Console.WriteLine("2. Experiment with different batch sizes for your use case");
            Console.WriteLine("3. Run the next example: 04_IndexOperations.cs");
            Console.WriteLine("4. Implement error handling and retry logic for production");

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}