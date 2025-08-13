using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents;

namespace AzureSearchSamples.DataSourcesIndexers
{
    /// <summary>
    /// Azure Blob Storage Indexer Example
    /// 
    /// This example demonstrates how to create and manage indexers for Azure Blob Storage data sources.
    /// It covers document processing, metadata extraction, and change detection.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service
    /// - Azure Storage Account with sample documents
    /// - Admin API key or managed identity
    /// - Required NuGet packages installed
    /// </summary>
    public class BlobStorageIndexerExample
    {
        private readonly SearchIndexClient _indexClient;
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;
        private readonly string _storageConnectionString;

        // Resource names
        private const string DataSourceName = "blob-documents-datasource";
        private const string IndexName = "documents-blob-index";
        private const string IndexerName = "documents-blob-indexer";
        private const string ContainerName = "sample-documents";

        public BlobStorageIndexerExample(string searchEndpoint, string apiKey, string storageConnectionString)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
            _storageConnectionString = storageConnectionString ?? throw new ArgumentNullException(nameof(storageConnectionString));

            var credential = new AzureKeyCredential(_apiKey);
            _indexClient = new SearchIndexClient(new Uri(_searchEndpoint), credential);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        /// <summary>
        /// Main execution method that demonstrates blob storage indexer creation and management
        /// </summary>
        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Azure Blob Storage Indexer Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Validate configuration
                ValidateConfiguration();

                // Create resources
                var dataSource = await CreateBlobDataSourceAsync();
                var index = await CreateDocumentIndexAsync();
                var indexer = await CreateBlobIndexerAsync();

                // Run and monitor indexer
                await RunAndMonitorIndexerAsync();

                // Test search functionality
                await TestDocumentSearchAsync();

                // Show cleanup options
                ShowCleanupOptions();

                Console.WriteLine("\n✅ Blob storage indexer example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- LastModified change detection is ideal for file-based data sources");
                Console.WriteLine("- Metadata extraction provides valuable searchable information");
                Console.WriteLine("- Content type filtering helps organize different document types");
                Console.WriteLine("- Batch size optimization is important for document processing performance");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }

        private void ValidateConfiguration()
        {
            Console.WriteLine("✅ Configuration validated");
            Console.WriteLine($"📍 Search Endpoint: {_searchEndpoint}");
            Console.WriteLine($"🗃️ Data Source: {DataSourceName}");
            Console.WriteLine($"📊 Index: {IndexName}");
            Console.WriteLine($"⚙️ Indexer: {IndexerName}");
        }

        /// <summary>
        /// Creates a data source connection to Azure Blob Storage with LastModified change detection
        /// </summary>
        private async Task<SearchIndexerDataSourceConnection> CreateBlobDataSourceAsync()
        {
            Console.WriteLine("\n🔗 Creating blob storage data source...");

            var dataSource = new SearchIndexerDataSourceConnection(
                name: DataSourceName,
                type: SearchIndexerDataSourceType.AzureBlob,
                connectionString: _storageConnectionString,
                container: new SearchIndexerDataContainer(ContainerName))
            {
                DataChangeDetectionPolicy = new HighWaterMarkChangeDetectionPolicy("metadata_storage_last_modified"),
                Description = "Document data from Azure Blob Storage with LastModified detection"
            };

            try
            {
                var result = await _indexerClient.CreateOrUpdateDataSourceConnectionAsync(dataSource);
                Console.WriteLine($"✅ Data source '{DataSourceName}' created successfully");

                // Display configuration
                Console.WriteLine($"   Type: {result.Value.Type}");
                Console.WriteLine($"   Container: {result.Value.Container.Name}");
                Console.WriteLine($"   Change Detection: {result.Value.DataChangeDetectionPolicy?.GetType().Name}");

                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating data source: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Creates a search index optimized for document content and metadata
        /// </summary>
        private async Task<SearchIndex> CreateDocumentIndexAsync()
        {
            Console.WriteLine("\n📊 Creating document index...");

            // Define index fields for document content and metadata
            var fields = new List<SearchField>
            {
                new SimpleField("metadata_storage_path", SearchFieldDataType.String) { IsKey = true },
                new SearchableField("content") { AnalyzerName = LexicalAnalyzerName.EnLucene },
                new SimpleField("metadata_storage_name", SearchFieldDataType.String) { IsFilterable = true, IsSortable = true },
                new SimpleField("metadata_storage_size", SearchFieldDataType.Int64) { IsFilterable = true, IsSortable = true },
                new SimpleField("metadata_storage_last_modified", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true },
                new SimpleField("metadata_storage_content_type", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SimpleField("metadata_language", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SearchableField("metadata_title"),
                new SearchableField("metadata_author") { IsFilterable = true, IsFacetable = true },
                new SearchableField("keyphrases", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFacetable = true }
            };

            var index = new SearchIndex(IndexName, fields);

            try
            {
                var result = await _indexClient.CreateOrUpdateIndexAsync(index);
                Console.WriteLine($"✅ Index '{IndexName}' created successfully");
                Console.WriteLine($"   Total Fields: {result.Value.Fields.Count}");

                // Display key fields
                Console.WriteLine("   Key fields for document processing:");
                foreach (var field in result.Value.Fields.Take(5))
                {
                    var attributes = new List<string>();
                    if (field.IsKey == true) attributes.Add("key");
                    if (field.IsSearchable == true) attributes.Add("searchable");
                    if (field.IsFilterable == true) attributes.Add("filterable");

                    Console.WriteLine($"     - {field.Name} ({field.Type}) [{string.Join(", ", attributes)}]");
                }

                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating index: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Creates an indexer to process documents from blob storage
        /// </summary>
        private async Task<SearchIndexer> CreateBlobIndexerAsync()
        {
            Console.WriteLine("\n⚙️ Creating blob storage indexer...");

            // Field mappings for blob storage metadata
            var fieldMappings = new List<FieldMapping>
            {
                new FieldMapping("metadata_storage_path") { TargetFieldName = "metadata_storage_path" },
                new FieldMapping("content") { TargetFieldName = "content" },
                new FieldMapping("metadata_storage_name") { TargetFieldName = "metadata_storage_name" },
                new FieldMapping("metadata_storage_size") { TargetFieldName = "metadata_storage_size" },
                new FieldMapping("metadata_storage_last_modified") { TargetFieldName = "metadata_storage_last_modified" },
                new FieldMapping("metadata_storage_content_type") { TargetFieldName = "metadata_storage_content_type" }
            };

            var indexer = new SearchIndexer(
                name: IndexerName,
                dataSourceName: DataSourceName,
                targetIndexName: IndexName)
            {
                Description = "Indexer for documents from blob storage",
                FieldMappings = fieldMappings,
                Parameters = new IndexingParameters
                {
                    BatchSize = 50, // Smaller batch for document processing
                    MaxFailedItems = 5,
                    MaxFailedItemsPerBatch = 2,
                    Configuration =
                    {
                        ["dataToExtract"] = "contentAndMetadata",
                        ["parsingMode"] = "default",
                        ["excludedFileNameExtensions"] = ".png,.jpg,.jpeg,.gif,.bmp"
                    }
                }
            };

            try
            {
                var result = await _indexerClient.CreateOrUpdateIndexerAsync(indexer);
                Console.WriteLine($"✅ Indexer '{IndexerName}' created successfully");
                Console.WriteLine($"   Data Source: {result.Value.DataSourceName}");
                Console.WriteLine($"   Target Index: {result.Value.TargetIndexName}");
                Console.WriteLine($"   Field Mappings: {result.Value.FieldMappings?.Count ?? 0}");

                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating indexer: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Runs the indexer and monitors document processing
        /// </summary>
        private async Task RunAndMonitorIndexerAsync()
        {
            Console.WriteLine($"\n🚀 Starting blob indexer: {IndexerName}");

            try
            {
                // Start the indexer
                await _indexerClient.RunIndexerAsync(IndexerName);
                Console.WriteLine("✅ Indexer started successfully");

                // Monitor execution
                var startTime = DateTime.UtcNow;
                var maxWaitTime = TimeSpan.FromMinutes(5);

                while (DateTime.UtcNow - startTime < maxWaitTime)
                {
                    var status = await _indexerClient.GetIndexerStatusAsync(IndexerName);

                    var currentTime = DateTime.Now.ToString("HH:mm:ss");
                    Console.WriteLine($"\n⏰ {currentTime} - Status: {status.Value.Status}");

                    if (status.Value.LastResult != null)
                    {
                        var result = status.Value.LastResult;
                        Console.WriteLine($"   📄 Documents processed: {result.ItemCount}");
                        Console.WriteLine($"   ❌ Documents failed: {result.FailedItemCount}");

                        // Show processing rate if available
                        if (result.ItemCount > 0 && result.EndTime.HasValue && result.StartTime.HasValue)
                        {
                            var duration = result.EndTime.Value - result.StartTime.Value;
                            if (duration.TotalSeconds > 0)
                            {
                                var rate = result.ItemCount / duration.TotalSeconds;
                                Console.WriteLine($"   📊 Processing rate: {rate:F2} docs/sec");
                            }
                        }

                        // Show any errors
                        if (result.Errors?.Count > 0)
                        {
                            Console.WriteLine($"   ⚠️ Recent errors:");
                            foreach (var error in result.Errors.Take(3))
                            {
                                Console.WriteLine($"     - {error.ErrorMessage}");
                            }
                        }
                    }

                    if (status.Value.Status == IndexerStatus.Success || status.Value.Status == IndexerStatus.Error)
                    {
                        Console.WriteLine($"\n🎉 Indexer execution completed with status: {status.Value.Status}");
                        break;
                    }

                    await Task.Delay(10000); // Wait 10 seconds
                }
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error running indexer: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Tests search functionality on the indexed documents
        /// </summary>
        private async Task TestDocumentSearchAsync()
        {
            Console.WriteLine("\n🔍 Testing document search...");

            var searchClient = new SearchClient(new Uri(_searchEndpoint), IndexName, new AzureKeyCredential(_apiKey));

            var testQueries = new[]
            {
                new { Name = "All documents", Query = "*", Filter = (string)null, OrderBy = (string)null },
                new { Name = "Content search", Query = "document", Filter = (string)null, OrderBy = (string)null },
                new { Name = "Filter by content type", Query = "*", Filter = "metadata_storage_content_type eq 'application/pdf'", OrderBy = (string)null },
                new { Name = "Sort by size", Query = "*", Filter = (string)null, OrderBy = "metadata_storage_size desc" }
            };

            foreach (var test in testQueries)
            {
                Console.WriteLine($"\n   🔍 {test.Name}:");
                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Size = 3,
                        Select = { "metadata_storage_name", "metadata_storage_content_type", "metadata_storage_size" }
                    };

                    if (!string.IsNullOrEmpty(test.Filter))
                        searchOptions.Filter = test.Filter;

                    if (!string.IsNullOrEmpty(test.OrderBy))
                        searchOptions.OrderBy.Add(test.OrderBy);

                    var results = await searchClient.SearchAsync<SearchDocument>(test.Query, searchOptions);

                    var documents = new List<SearchResult<SearchDocument>>();
                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        documents.Add(result);
                    }

                    Console.WriteLine($"      Found {documents.Count} results");

                    foreach (var (result, index) in documents.Take(2).Select((r, i) => (r, i)))
                    {
                        var filename = result.Document.TryGetValue("metadata_storage_name", out var name) ? name?.ToString() : "N/A";
                        var contentType = result.Document.TryGetValue("metadata_storage_content_type", out var type) ? type?.ToString() : "N/A";
                        var size = result.Document.TryGetValue("metadata_storage_size", out var sizeObj) && long.TryParse(sizeObj?.ToString(), out var sizeValue) ? sizeValue : 0;
                        Console.WriteLine($"      {index + 1}. {filename} ({contentType}) - {size:N0} bytes");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"      ❌ Error: {ex.Message}");
                }
            }
        }

        private void ShowCleanupOptions()
        {
            Console.WriteLine("\n🧹 Cleanup options:");
            Console.WriteLine("   To clean up resources, call:");
            Console.WriteLine($"   - await _indexerClient.DeleteIndexerAsync(\"{IndexerName}\");");
            Console.WriteLine($"   - await _indexClient.DeleteIndexAsync(\"{IndexName}\");");
            Console.WriteLine($"   - await _indexerClient.DeleteDataSourceConnectionAsync(\"{DataSourceName}\");");
        }

        /// <summary>
        /// Cleanup method to delete created resources
        /// </summary>
        public async Task CleanupAsync()
        {
            try
            {
                await _indexerClient.DeleteIndexerAsync(IndexerName);
                await _indexClient.DeleteIndexAsync(IndexName);
                await _indexerClient.DeleteDataSourceConnectionAsync(DataSourceName);
                Console.WriteLine("✅ Resources cleaned up successfully");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"⚠️ Cleanup warning: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Program entry point for running the blob storage indexer example
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            // Configuration - replace with your actual values
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";
            var storageConnectionString = Environment.GetEnvironmentVariable("STORAGE_CONNECTION_STRING") ?? "your-storage-connection-string";

            var example = new BlobStorageIndexerExample(searchEndpoint, apiKey, storageConnectionString);

            try
            {
                await example.RunAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Application failed: {ex.Message}");
                Environment.Exit(1);
            }

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}