using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Microsoft.Extensions.Configuration;

namespace AzureSearchIndexerExamples
{
    /// <summary>
    /// Azure AI Search - SQL Database Indexer Example (C#)
    /// 
    /// This example demonstrates how to:
    /// 1. Create a data source connection to Azure SQL Database
    /// 2. Create an index for SQL data
    /// 3. Create and configure an indexer
    /// 4. Monitor indexer execution
    /// 5. Implement change tracking for incremental updates
    /// 
    /// Prerequisites:
    /// - Azure AI Search service
    /// - Azure SQL Database with sample data
    /// - Required NuGet packages: Azure.Search.Documents, Azure.Identity
    /// </summary>
    public class AzureSqlIndexerExample
    {
        private readonly SearchIndexClient _indexClient;
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _sqlConnectionString;
        
        // Resource names
        private const string DataSourceName = "sql-hotels-datasource";
        private const string IndexName = "hotels-sql-index";
        private const string IndexerName = "hotels-sql-indexer";
        private const string TableName = "Hotels";
        
        public AzureSqlIndexerExample(IConfiguration configuration)
        {
            var endpoint = new Uri(configuration["SearchService:Endpoint"]);
            var apiKey = configuration["SearchService:ApiKey"];
            _sqlConnectionString = configuration["DataSources:SqlConnectionString"];
            
            if (endpoint == null || string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(_sqlConnectionString))
            {
                throw new ArgumentException("Missing required configuration values");
            }
            
            var credential = new AzureKeyCredential(apiKey);
            _indexClient = new SearchIndexClient(endpoint, credential);
            _indexerClient = new SearchIndexerClient(endpoint, credential);
        }
        
        /// <summary>
        /// Create a data source connection to Azure SQL Database
        /// </summary>
        public async Task<SearchIndexerDataSourceConnection> CreateDataSourceAsync()
        {
            Console.WriteLine($"Creating data source: {DataSourceName}");
            
            var dataSource = new SearchIndexerDataSourceConnection(
                name: DataSourceName,
                type: SearchIndexerDataSourceType.AzureSql,
                connectionString: _sqlConnectionString,
                container: new SearchIndexerDataContainer(TableName))
            {
                DataChangeDetectionPolicy = new SqlIntegratedChangeTrackingPolicy(),
                Description = "Hotels data from Azure SQL Database"
            };
            
            try
            {
                var result = await _indexerClient.CreateOrUpdateDataSourceConnectionAsync(dataSource);
                Console.WriteLine($"✅ Data source '{DataSourceName}' created successfully");
                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating data source: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Create a search index for hotel data
        /// </summary>
        public async Task<SearchIndex> CreateIndexAsync()
        {
            Console.WriteLine($"Creating index: {IndexName}");
            
            var fields = new List<SearchField>
            {
                new SimpleField("HotelId", SearchFieldDataType.String) { IsKey = true },
                new SearchableField("HotelName") { AnalyzerName = LexicalAnalyzerName.EnLucene },
                new SearchableField("Description") { AnalyzerName = LexicalAnalyzerName.EnLucene },
                new SimpleField("Category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SimpleField("Rating", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true, IsFacetable = true },
                
                // Address as a complex field
                new ComplexField("Address")
                {
                    Fields =
                    {
                        new SimpleField("StreetAddress", SearchFieldDataType.String),
                        new SimpleField("City", SearchFieldDataType.String) { IsFilterable = true, IsSortable = true, IsFacetable = true },
                        new SimpleField("StateProvince", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                        new SimpleField("PostalCode", SearchFieldDataType.String) { IsFilterable = true },
                        new SimpleField("Country", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true }
                    }
                },
                
                new SimpleField("LastRenovationDate", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true },
                new SimpleField("CreatedDate", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true },
                new SimpleField("ModifiedDate", SearchFieldDataType.DateTimeOffset) { IsFilterable = true, IsSortable = true }
            };
            
            var index = new SearchIndex(IndexName, fields);
            
            try
            {
                var result = await _indexClient.CreateOrUpdateIndexAsync(index);
                Console.WriteLine($"✅ Index '{IndexName}' created successfully");
                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating index: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Create an indexer to populate the index from SQL data
        /// </summary>
        public async Task<SearchIndexer> CreateIndexerAsync()
        {
            Console.WriteLine($"Creating indexer: {IndexerName}");
            
            var fieldMappings = new List<FieldMapping>
            {
                new FieldMapping("HotelId") { TargetFieldName = "HotelId" },
                new FieldMapping("HotelName") { TargetFieldName = "HotelName" },
                new FieldMapping("Description") { TargetFieldName = "Description" },
                new FieldMapping("Category") { TargetFieldName = "Category" },
                new FieldMapping("Rating") { TargetFieldName = "Rating" },
                
                // Map flat SQL fields to complex Address field
                new FieldMapping("Address") { TargetFieldName = "Address/StreetAddress" },
                new FieldMapping("City") { TargetFieldName = "Address/City" },
                new FieldMapping("StateProvince") { TargetFieldName = "Address/StateProvince" },
                new FieldMapping("PostalCode") { TargetFieldName = "Address/PostalCode" },
                new FieldMapping("Country") { TargetFieldName = "Address/Country" },
                
                new FieldMapping("LastRenovationDate") { TargetFieldName = "LastRenovationDate" },
                new FieldMapping("CreatedDate") { TargetFieldName = "CreatedDate" },
                new FieldMapping("ModifiedDate") { TargetFieldName = "ModifiedDate" }
            };
            
            var indexer = new SearchIndexer(
                name: IndexerName,
                dataSourceName: DataSourceName,
                targetIndexName: IndexName)
            {
                Description = "Indexer for hotels data from SQL Database",
                FieldMappings = { },
                Parameters = new IndexingParameters
                {
                    BatchSize = 100,
                    MaxFailedItems = 10,
                    MaxFailedItemsPerBatch = 5
                }
            };
            
            // Add field mappings
            foreach (var mapping in fieldMappings)
            {
                indexer.FieldMappings.Add(mapping);
            }
            
            try
            {
                var result = await _indexerClient.CreateOrUpdateIndexerAsync(indexer);
                Console.WriteLine($"✅ Indexer '{IndexerName}' created successfully");
                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating indexer: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Run the indexer and monitor its execution
        /// </summary>
        public async Task RunIndexerAsync()
        {
            Console.WriteLine($"Running indexer: {IndexerName}");
            
            try
            {
                // Start the indexer
                await _indexerClient.RunIndexerAsync(IndexerName);
                Console.WriteLine("✅ Indexer started successfully");
                
                // Monitor execution
                await MonitorIndexerExecutionAsync();
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error running indexer: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Monitor indexer execution until completion or timeout
        /// </summary>
        public async Task MonitorIndexerExecutionAsync(int timeoutSeconds = 300)
        {
            Console.WriteLine("Monitoring indexer execution...");
            var startTime = DateTime.UtcNow;
            
            while (DateTime.UtcNow.Subtract(startTime).TotalSeconds < timeoutSeconds)
            {
                try
                {
                    var status = await _indexerClient.GetIndexerStatusAsync(IndexerName);
                    
                    Console.WriteLine($"Status: {status.Value.Status}");
                    
                    if (status.Value.LastResult != null)
                    {
                        var result = status.Value.LastResult;
                        Console.WriteLine($"Items processed: {result.ItemCount}");
                        Console.WriteLine($"Items failed: {result.FailedItemCount}");
                        Console.WriteLine($"Start time: {result.StartTime}");
                        Console.WriteLine($"End time: {result.EndTime}");
                        
                        // Check for errors
                        if (result.Errors?.Count > 0)
                        {
                            Console.WriteLine("Errors encountered:");
                            foreach (var error in result.Errors)
                            {
                                Console.WriteLine($"  - {error.ErrorMessage}");
                            }
                        }
                        
                        // Check for warnings
                        if (result.Warnings?.Count > 0)
                        {
                            Console.WriteLine("Warnings:");
                            foreach (var warning in result.Warnings)
                            {
                                Console.WriteLine($"  - {warning.Message}");
                            }
                        }
                    }
                    
                    // Check if execution is complete
                    if (status.Value.Status == IndexerStatus.Success || status.Value.Status == IndexerStatus.Error)
                    {
                        Console.WriteLine($"✅ Indexer execution completed with status: {status.Value.Status}");
                        break;
                    }
                    
                    // Wait before checking again
                    await Task.Delay(10000);
                }
                catch (RequestFailedException ex)
                {
                    Console.WriteLine($"Error checking indexer status: {ex.Message}");
                    break;
                }
            }
        }
        
        /// <summary>
        /// Get and display current indexer status
        /// </summary>
        public async Task GetIndexerStatusAsync()
        {
            try
            {
                var status = await _indexerClient.GetIndexerStatusAsync(IndexerName);
                
                Console.WriteLine($"\n=== Indexer Status: {IndexerName} ===");
                Console.WriteLine($"Status: {status.Value.Status}");
                Console.WriteLine($"Last run status: {status.Value.LastResult?.Status ?? "Never run"}");
                
                if (status.Value.LastResult != null)
                {
                    Console.WriteLine($"Items processed: {status.Value.LastResult.ItemCount}");
                    Console.WriteLine($"Items failed: {status.Value.LastResult.FailedItemCount}");
                    Console.WriteLine($"Execution time: {status.Value.LastResult.StartTime} - {status.Value.LastResult.EndTime}");
                    
                    if (status.Value.ExecutionHistory?.Count > 0)
                    {
                        Console.WriteLine($"Total executions: {status.Value.ExecutionHistory.Count}");
                    }
                }
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"Error getting indexer status: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Reset the indexer to clear its execution state
        /// </summary>
        public async Task ResetIndexerAsync()
        {
            try
            {
                await _indexerClient.ResetIndexerAsync(IndexerName);
                Console.WriteLine($"✅ Indexer '{IndexerName}' reset successfully");
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error resetting indexer: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Clean up created resources
        /// </summary>
        public async Task DeleteResourcesAsync()
        {
            Console.WriteLine("Cleaning up resources...");
            
            try
            {
                await _indexerClient.DeleteIndexerAsync(IndexerName);
                Console.WriteLine($"✅ Deleted indexer: {IndexerName}");
            }
            catch (RequestFailedException)
            {
                // Ignore errors during cleanup
            }
            
            try
            {
                await _indexClient.DeleteIndexAsync(IndexName);
                Console.WriteLine($"✅ Deleted index: {IndexName}");
            }
            catch (RequestFailedException)
            {
                // Ignore errors during cleanup
            }
            
            try
            {
                await _indexerClient.DeleteDataSourceConnectionAsync(DataSourceName);
                Console.WriteLine($"✅ Deleted data source: {DataSourceName}");
            }
            catch (RequestFailedException)
            {
                // Ignore errors during cleanup
            }
        }
        
        /// <summary>
        /// Run the complete SQL indexer example
        /// </summary>
        public async Task RunCompleteExampleAsync()
        {
            Console.WriteLine("=== Azure AI Search SQL Indexer Example ===\n");
            
            try
            {
                // Step 1: Create data source
                await CreateDataSourceAsync();
                
                // Step 2: Create index
                await CreateIndexAsync();
                
                // Step 3: Create indexer
                await CreateIndexerAsync();
                
                // Step 4: Run indexer
                await RunIndexerAsync();
                
                // Step 5: Check final status
                await GetIndexerStatusAsync();
                
                Console.WriteLine("\n✅ SQL indexer example completed successfully!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Dispose of resources
        /// </summary>
        public void Dispose()
        {
            _indexClient?.Dispose();
            _indexerClient?.Dispose();
        }
    }
    
    /// <summary>
    /// Program entry point
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            try
            {
                var configuration = new ConfigurationBuilder()
                    .AddJsonFile("appsettings.json")
                    .Build();
                
                using var example = new AzureSqlIndexerExample(configuration);
                await example.RunCompleteExampleAsync();
                
                // Optionally clean up resources
                Console.Write("\nDo you want to clean up the created resources? (y/n): ");
                var answer = Console.ReadLine();
                if (answer?.ToLower() == "y")
                {
                    await example.DeleteResourcesAsync();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }
    }
}