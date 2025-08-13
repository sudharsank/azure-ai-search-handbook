using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents;

namespace AzureSearchSamples.DataSourcesIndexers
{
    /// <summary>
    /// Azure Cosmos DB Indexer Example
    /// 
    /// This example demonstrates how to create and manage indexers for Azure Cosmos DB data sources.
    /// It covers JSON document processing, change feed integration, and partition key handling.
    /// 
    /// Prerequisites:
    /// - Azure AI Search service
    /// - Azure Cosmos DB account with sample data
    /// - Admin API key or managed identity
    /// - Required NuGet packages installed
    /// </summary>
    public class CosmosDbIndexerExample
    {
        private readonly SearchIndexClient _indexClient;
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;
        private readonly string _cosmosConnectionString;

        // Resource names
        private const string DataSourceName = "cosmos-hotels-datasource";
        private const string IndexName = "hotels-cosmos-index";
        private const string IndexerName = "hotels-cosmos-indexer";
        private const string ContainerName = "hotels";

        public CosmosDbIndexerExample(string searchEndpoint, string apiKey, string cosmosConnectionString)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
            _cosmosConnectionString = cosmosConnectionString ?? throw new ArgumentNullException(nameof(cosmosConnectionString));

            var credential = new AzureKeyCredential(_apiKey);
            _indexClient = new SearchIndexClient(new Uri(_searchEndpoint), credential);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        /// <summary>
        /// Main execution method that demonstrates Cosmos DB indexer creation and management
        /// </summary>
        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Azure Cosmos DB Indexer Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Validate configuration
                ValidateConfiguration();

                // Create resources
                var dataSource = await CreateCosmosDataSourceAsync();
                var index = await CreateHotelsIndexAsync();
                var indexer = await CreateCosmosIndexerAsync();

                // Run and monitor indexer
                await RunAndMonitorIndexerAsync();

                // Test search functionality
                await TestHotelSearchAsync();

                // Demonstrate change feed concepts
                DemonstrateChangeFeed();

                // Show cleanup options
                ShowCleanupOptions();

                Console.WriteLine("\n✅ Cosmos DB indexer example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Cosmos DB change feed provides efficient incremental updates");
                Console.WriteLine("- Complex fields handle nested JSON structures well");
                Console.WriteLine("- Collection fields are perfect for arrays like amenities");
                Console.WriteLine("- Faceted search works great with categorical hotel data");
                Console.WriteLine("- Higher batch sizes work well with JSON documents");
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
        /// Creates a data source connection to Azure Cosmos DB with change feed detection
        /// </summary>
        private async Task<SearchIndexerDataSourceConnection> CreateCosmosDataSourceAsync()
        {
            Console.WriteLine("\n🔗 Creating Cosmos DB data source...");

            var dataSource = new SearchIndexerDataSourceConnection(
                name: DataSourceName,
                type: SearchIndexerDataSourceType.CosmosDb,
                connectionString: _cosmosConnectionString,
                container: new SearchIndexerDataContainer(ContainerName)
                {
                    Query = "SELECT * FROM c WHERE c._ts >= @HighWaterMark ORDER BY c._ts"
                })
            {
                DataChangeDetectionPolicy = new HighWaterMarkChangeDetectionPolicy("_ts"),
                Description = "Hotel data from Cosmos DB with change feed detection"
            };

            try
            {
                var result = await _indexerClient.CreateOrUpdateDataSourceConnectionAsync(dataSource);
                Console.WriteLine($"✅ Data source '{DataSourceName}' created successfully");

                // Display configuration
                Console.WriteLine($"   Type: {result.Value.Type}");
                Console.WriteLine($"   Container: {result.Value.Container.Name}");
                Console.WriteLine($"   Change Detection: {result.Value.DataChangeDetectionPolicy?.GetType().Name}");
                if (result.Value.DataChangeDetectionPolicy is HighWaterMarkChangeDetectionPolicy hwm)
                {
                    Console.WriteLine($"   High Water Mark: {hwm.HighWaterMarkColumnName}");
                }

                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating data source: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Creates a search index optimized for hotel data from Cosmos DB
        /// </summary>
        private async Task<SearchIndex> CreateHotelsIndexAsync()
        {
            Console.WriteLine("\n📊 Creating hotels index...");

            // Define index fields for hotel data
            var fields = new List<SearchField>
            {
                new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
                new SearchableField("hotelName") { IsSortable = true },
                new SearchableField("description") { AnalyzerName = LexicalAnalyzerName.EnLucene },
                new SimpleField("category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SimpleField("rating", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true, IsFacetable = true },

                // Complex field for address
                new ComplexField("address")
                {
                    Fields =
                    {
                        new SearchableField("street"),
                        new SearchableField("city") { IsFilterable = true, IsFacetable = true },
                        new SearchableField("state") { IsFilterable = true, IsFacetable = true },
                        new SimpleField("zipCode", SearchFieldDataType.String) { IsFilterable = true },
                        new SimpleField("country", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true }
                    }
                },

                // Collection field for amenities
                new SearchableField("amenities", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFacetable = true },

                // Date fields
                new SimpleField("lastRenovated", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true },
                new SimpleField("_ts", SearchFieldDataType.Int64) { IsFilterable = true, IsSortable = true },

                // Location field for geo-search (if coordinates available)
                new SimpleField("location", SearchFieldDataType.GeographyPoint) { IsFilterable = true, IsSortable = true }
            };

            var index = new SearchIndex(IndexName, fields);

            try
            {
                var result = await _indexClient.CreateOrUpdateIndexAsync(index);
                Console.WriteLine($"✅ Index '{IndexName}' created successfully");
                Console.WriteLine($"   Total Fields: {result.Value.Fields.Count}");

                // Display key fields
                Console.WriteLine("   Key fields for hotel data:");
                var keyFields = new[] { "id", "hotelName", "category", "rating", "address" };
                foreach (var field in result.Value.Fields.Where(f => keyFields.Contains(f.Name)))
                {
                    var attributes = new List<string>();
                    if (field.IsKey == true) attributes.Add("key");
                    if (field.IsSearchable == true) attributes.Add("searchable");
                    if (field.IsFilterable == true) attributes.Add("filterable");
                    if (field.IsFacetable == true) attributes.Add("facetable");

                    var fieldType = field is ComplexField ? "Complex" : field.Type.ToString();
                    Console.WriteLine($"     - {field.Name} ({fieldType}) [{string.Join(", ", attributes)}]");
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
        /// Creates an indexer to process hotel data from Cosmos DB
        /// </summary>
        private async Task<SearchIndexer> CreateCosmosIndexerAsync()
        {
            Console.WriteLine("\n⚙️ Creating Cosmos DB indexer...");

            // Field mappings for Cosmos DB data
            var fieldMappings = new List<FieldMapping>
            {
                new FieldMapping("id") { TargetFieldName = "id" },
                new FieldMapping("hotelName") { TargetFieldName = "hotelName" },
                new FieldMapping("description") { TargetFieldName = "description" },
                new FieldMapping("category") { TargetFieldName = "category" },
                new FieldMapping("rating") { TargetFieldName = "rating" },
                new FieldMapping("address") { TargetFieldName = "address" },
                new FieldMapping("amenities") { TargetFieldName = "amenities" },
                new FieldMapping("lastRenovated") { TargetFieldName = "lastRenovated" },
                new FieldMapping("_ts") { TargetFieldName = "_ts" }
            };

            var indexer = new SearchIndexer(
                name: IndexerName,
                dataSourceName: DataSourceName,
                targetIndexName: IndexName)
            {
                Description = "Indexer for hotel data from Cosmos DB",
                FieldMappings = fieldMappings,
                Parameters = new IndexingParameters
                {
                    BatchSize = 100, // Larger batch for JSON documents
                    MaxFailedItems = 10,
                    MaxFailedItemsPerBatch = 5,
                    Configuration =
                    {
                        ["parsingMode"] = "json"
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
                Console.WriteLine($"   Batch Size: {result.Value.Parameters?.BatchSize ?? 0}");

                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating indexer: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Runs the indexer and monitors hotel data processing
        /// </summary>
        private async Task RunAndMonitorIndexerAsync()
        {
            Console.WriteLine($"\n🚀 Starting Cosmos DB indexer: {IndexerName}");

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
                        Console.WriteLine($"   🏨 Hotels processed: {result.ItemCount}");
                        Console.WriteLine($"   ❌ Hotels failed: {result.FailedItemCount}");

                        // Show processing rate if available
                        if (result.ItemCount > 0 && result.EndTime.HasValue && result.StartTime.HasValue)
                        {
                            var duration = result.EndTime.Value - result.StartTime.Value;
                            if (duration.TotalSeconds > 0)
                            {
                                var rate = result.ItemCount / duration.TotalSeconds;
                                Console.WriteLine($"   📊 Processing rate: {rate:F2} hotels/sec");
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

                        // Show warnings if any
                        if (result.Warnings?.Count > 0)
                        {
                            Console.WriteLine($"   ⚠️ Warnings: {result.Warnings.Count}");
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
        /// Tests search functionality on the indexed hotel data
        /// </summary>
        private async Task TestHotelSearchAsync()
        {
            Console.WriteLine("\n🔍 Testing hotel search...");

            var searchClient = new SearchClient(new Uri(_searchEndpoint), IndexName, new AzureKeyCredential(_apiKey));

            var testQueries = new[]
            {
                new { Name = "All hotels", Query = "*", Filter = (string)null, OrderBy = (string)null, Facets = (string[])null },
                new { Name = "Luxury hotels", Query = "luxury", Filter = (string)null, OrderBy = (string)null, Facets = (string[])null },
                new { Name = "High-rated hotels", Query = "*", Filter = "rating ge 4.0", OrderBy = "rating desc", Facets = (string[])null },
                new { Name = "Hotels by city", Query = "*", Filter = (string)null, OrderBy = (string)null, Facets = new[] { "address/city" } },
                new { Name = "Hotels with amenities", Query = "*", Filter = "amenities/any(a: a eq 'WiFi')", OrderBy = (string)null, Facets = (string[])null }
            };

            foreach (var test in testQueries)
            {
                Console.WriteLine($"\n   🔍 {test.Name}:");
                try
                {
                    var searchOptions = new SearchOptions
                    {
                        Size = test.Facets != null ? 0 : 3,
                        Select = { "hotelName", "category", "rating", "address" }
                    };

                    if (!string.IsNullOrEmpty(test.Filter))
                        searchOptions.Filter = test.Filter;

                    if (!string.IsNullOrEmpty(test.OrderBy))
                        searchOptions.OrderBy.Add(test.OrderBy);

                    if (test.Facets != null)
                    {
                        foreach (var facet in test.Facets)
                            searchOptions.Facets.Add(facet);
                    }

                    var results = await searchClient.SearchAsync<SearchDocument>(test.Query, searchOptions);

                    if (test.Facets != null)
                    {
                        // Handle facet results
                        if (results.Value.Facets?.ContainsKey("address/city") == true)
                        {
                            Console.WriteLine($"      Cities found:");
                            foreach (var facet in results.Value.Facets["address/city"].Take(5))
                            {
                                Console.WriteLine($"        - {facet.Value}: {facet.Count} hotels");
                            }
                        }
                    }
                    else
                    {
                        // Handle regular search results
                        var documents = new List<SearchResult<SearchDocument>>();
                        await foreach (var result in results.Value.GetResultsAsync())
                        {
                            documents.Add(result);
                        }

                        Console.WriteLine($"      Found {documents.Count} results");

                        foreach (var (result, index) in documents.Take(2).Select((r, i) => (r, i)))
                        {
                            var hotelName = result.Document.TryGetValue("hotelName", out var name) ? name?.ToString() : "N/A";
                            var category = result.Document.TryGetValue("category", out var cat) ? cat?.ToString() : "N/A";
                            var rating = result.Document.TryGetValue("rating", out var ratingObj) && double.TryParse(ratingObj?.ToString(), out var ratingValue) ? ratingValue : 0;
                            
                            var city = "N/A";
                            if (result.Document.TryGetValue("address", out var addressObj) && addressObj is SearchDocument address)
                            {
                                city = address.TryGetValue("city", out var cityObj) ? cityObj?.ToString() : "N/A";
                            }

                            Console.WriteLine($"      {index + 1}. {hotelName} ({category}) - {rating}⭐ in {city}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"      ❌ Error: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Demonstrates how change feed detection works with Cosmos DB
        /// </summary>
        private void DemonstrateChangeFeed()
        {
            Console.WriteLine("\n🔄 Change Feed Detection:");
            Console.WriteLine("   Cosmos DB indexer uses the '_ts' field for change detection");
            Console.WriteLine("   Benefits:");
            Console.WriteLine("   - Automatic detection of new and updated documents");
            Console.WriteLine("   - Efficient incremental updates");
            Console.WriteLine("   - Built-in ordering by timestamp");
            Console.WriteLine("   - No additional configuration required");
            Console.WriteLine("\n   The indexer query includes: WHERE c._ts >= @HighWaterMark ORDER BY c._ts");
            Console.WriteLine("   This ensures only changed documents are processed on subsequent runs");
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
    /// Program entry point for running the Cosmos DB indexer example
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            // Configuration - replace with your actual values
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";
            var cosmosConnectionString = Environment.GetEnvironmentVariable("COSMOS_CONNECTION_STRING") ?? "your-cosmos-connection-string";

            var example = new CosmosDbIndexerExample(searchEndpoint, apiKey, cosmosConnectionString);

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