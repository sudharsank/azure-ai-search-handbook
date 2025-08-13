using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace AzureSearchSamples.DataSourcesIndexers
{
    /// <summary>
    /// Change Detection Strategies Example
    /// 
    /// This example demonstrates different change detection policies and strategies
    /// for efficient incremental indexing in Azure AI Search.
    /// </summary>
    public class ChangeDetectionExample
    {
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;

        public ChangeDetectionExample(string searchEndpoint, string apiKey)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));

            var credential = new AzureKeyCredential(_apiKey);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Change Detection Strategies Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Demonstrate different change detection policies
                DemonstrateHighWaterMarkPolicies();
                DemonstrateSqlIntegratedChangeTracking();

                // Create example data sources (if connection strings are available)
                await CreateChangeDetectionExamplesAsync();

                // Performance comparison
                DemonstratePerformanceComparison();

                // Best practices
                DemonstrateBestPractices();

                Console.WriteLine("\n✅ Change detection strategies example completed!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Choose change detection strategy based on data source capabilities");
                Console.WriteLine("- SQL Integrated Change Tracking is most efficient for SQL databases");
                Console.WriteLine("- High Water Mark works well for timestamped data");
                Console.WriteLine("- Proper indexing is crucial for performance");
                Console.WriteLine("- Monitor change detection effectiveness regularly");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }

        private void DemonstrateHighWaterMarkPolicies()
        {
            Console.WriteLine("\n🌊 High Water Mark Change Detection Policies");
            Console.WriteLine("=" + new string('=', 49));

            var policies = new[]
            {
                new
                {
                    Name = "SQL Database - LastModified",
                    DataSourceType = SearchIndexerDataSourceType.AzureSql,
                    Policy = new HighWaterMarkChangeDetectionPolicy("LastModified"),
                    Description = "Uses a datetime column to track changes",
                    Requirements = new[] {
                        "DateTime column (e.g., LastModified, UpdatedAt)",
                        "Column updated on every record change",
                        "Column indexed for performance"
                    },
                    Pros = new[] {
                        "Simple to implement",
                        "Works with any datetime column",
                        "Good performance with proper indexing"
                    },
                    Cons = new[] {
                        "Requires application to maintain timestamp",
                        "May miss concurrent updates with same timestamp",
                        "Requires column to be consistently updated"
                    }
                },
                new
                {
                    Name = "Blob Storage - LastModified",
                    DataSourceType = SearchIndexerDataSourceType.AzureBlob,
                    Policy = new HighWaterMarkChangeDetectionPolicy("metadata_storage_last_modified"),
                    Description = "Uses blob last modified timestamp",
                    Requirements = new[] {
                        "Azure Blob Storage",
                        "Automatic metadata tracking enabled"
                    },
                    Pros = new[] {
                        "Automatic timestamp management",
                        "No application changes required",
                        "Built into blob storage"
                    },
                    Cons = new[] {
                        "Only detects file-level changes",
                        "May not detect metadata-only changes",
                        "Dependent on storage service timestamps"
                    }
                },
                new
                {
                    Name = "Cosmos DB - Timestamp",
                    DataSourceType = SearchIndexerDataSourceType.CosmosDb,
                    Policy = new HighWaterMarkChangeDetectionPolicy("_ts"),
                    Description = "Uses Cosmos DB internal timestamp",
                    Requirements = new[] {
                        "Azure Cosmos DB",
                        "Access to _ts system property"
                    },
                    Pros = new[] {
                        "Automatic timestamp management",
                        "Guaranteed uniqueness and ordering",
                        "Built into Cosmos DB"
                    },
                    Cons = new[] {
                        "Limited to Cosmos DB",
                        "Timestamp is in epoch format",
                        "May require query modifications"
                    }
                }
            };

            foreach (var policy in policies)
            {
                Console.WriteLine($"\n📋 {policy.Name}");
                Console.WriteLine($"   Description: {policy.Description}");
                Console.WriteLine($"   Column: {policy.Policy.HighWaterMarkColumnName}");

                Console.WriteLine("   Requirements:");
                foreach (var req in policy.Requirements)
                    Console.WriteLine($"     • {req}");

                Console.WriteLine("   Pros:");
                foreach (var pro in policy.Pros)
                    Console.WriteLine($"     ✅ {pro}");

                Console.WriteLine("   Cons:");
                foreach (var con in policy.Cons)
                    Console.WriteLine($"     ⚠️ {con}");
            }
        }

        private void DemonstrateSqlIntegratedChangeTracking()
        {
            Console.WriteLine("\n🔄 SQL Integrated Change Tracking");
            Console.WriteLine("=" + new string('=', 39));

            Console.WriteLine("SQL Server Change Tracking provides the most efficient change detection for SQL databases.");

            var policy = new SqlIntegratedChangeTrackingPolicy();

            Console.WriteLine($"\nPolicy Configuration:");
            Console.WriteLine($"   Type: {policy.GetType().Name}");
            Console.WriteLine($"   Description: Uses SQL Server's built-in change tracking");

            Console.WriteLine($"\nSQL Server Setup Requirements:");
            var requirements = new[]
            {
                "Enable change tracking on database: ALTER DATABASE [YourDB] SET CHANGE_TRACKING = ON",
                "Enable change tracking on table: ALTER TABLE [YourTable] ENABLE CHANGE_TRACKING",
                "Ensure proper permissions for indexer service",
                "Consider retention period for change tracking data"
            };

            for (int i = 0; i < requirements.Length; i++)
                Console.WriteLine($"   {i + 1}. {requirements[i]}");

            Console.WriteLine($"\nBenefits:");
            var benefits = new[]
            {
                "Most efficient - only changed rows are processed",
                "Handles deletes automatically",
                "No application changes required",
                "Built-in conflict resolution",
                "Minimal storage overhead"
            };

            foreach (var benefit in benefits)
                Console.WriteLine($"   ✅ {benefit}");

            Console.WriteLine($"\nConsiderations:");
            var considerations = new[]
            {
                "Only available for SQL Server/Azure SQL",
                "Requires database-level configuration",
                "May impact database performance slightly",
                "Change tracking data has retention limits"
            };

            foreach (var consideration in considerations)
                Console.WriteLine($"   ⚠️ {consideration}");
        }

        private async Task CreateChangeDetectionExamplesAsync()
        {
            Console.WriteLine("\n🛠️ Creating Change Detection Examples");
            Console.WriteLine("=" + new string('=', 39));

            var examples = new List<(string Name, SearchIndexerDataSourceConnection DataSource)>();

            // SQL with High Water Mark (if connection string available)
            var sqlConnectionString = Environment.GetEnvironmentVariable("SQL_CONNECTION_STRING");
            if (!string.IsNullOrEmpty(sqlConnectionString))
            {
                Console.WriteLine("\n📊 Creating SQL data source with High Water Mark...");
                try
                {
                    var sqlDataSource = new SearchIndexerDataSourceConnection(
                        name: "sql-highwatermark-example",
                        type: SearchIndexerDataSourceType.AzureSql,
                        connectionString: sqlConnectionString,
                        container: new SearchIndexerDataContainer("Hotels"))
                    {
                        DataChangeDetectionPolicy = new HighWaterMarkChangeDetectionPolicy("LastModified"),
                        Description = "SQL data source with LastModified change detection"
                    };

                    var result = await _indexerClient.CreateOrUpdateDataSourceConnectionAsync(sqlDataSource);
                    examples.Add(("SQL High Water Mark", result.Value));
                    Console.WriteLine($"   ✅ Created: {result.Value.Name}");
                }
                catch (RequestFailedException ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }

                // SQL with Integrated Change Tracking
                Console.WriteLine("\n🔄 Creating SQL data source with Integrated Change Tracking...");
                try
                {
                    var sqlCtDataSource = new SearchIndexerDataSourceConnection(
                        name: "sql-changetracking-example",
                        type: SearchIndexerDataSourceType.AzureSql,
                        connectionString: sqlConnectionString,
                        container: new SearchIndexerDataContainer("Hotels"))
                    {
                        DataChangeDetectionPolicy = new SqlIntegratedChangeTrackingPolicy(),
                        Description = "SQL data source with integrated change tracking"
                    };

                    var result = await _indexerClient.CreateOrUpdateDataSourceConnectionAsync(sqlCtDataSource);
                    examples.Add(("SQL Integrated Change Tracking", result.Value));
                    Console.WriteLine($"   ✅ Created: {result.Value.Name}");
                }
                catch (RequestFailedException ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }

            // Demonstrate behavior analysis
            if (examples.Any())
            {
                DemonstrateChangeDetectionBehavior(examples);
            }
        }

        private void DemonstrateChangeDetectionBehavior(List<(string Name, SearchIndexerDataSourceConnection DataSource)> examples)
        {
            Console.WriteLine("\n🔍 Change Detection Behavior Analysis");
            Console.WriteLine("=" + new string('=', 39));

            foreach (var (name, dataSource) in examples)
            {
                Console.WriteLine($"\n📋 Analyzing: {name}");
                Console.WriteLine($"   Data Source: {dataSource.Name}");
                Console.WriteLine($"   Type: {dataSource.Type}");

                var policy = dataSource.DataChangeDetectionPolicy;
                if (policy != null)
                {
                    var policyType = policy.GetType().Name;
                    Console.WriteLine($"   Change Detection: {policyType}");

                    if (policy is HighWaterMarkChangeDetectionPolicy hwm)
                    {
                        Console.WriteLine($"   High Water Mark Column: {hwm.HighWaterMarkColumnName}");
                    }

                    // Explain behavior
                    if (policyType == "HighWaterMarkChangeDetectionPolicy")
                    {
                        Console.WriteLine("   Behavior:");
                        Console.WriteLine("     • First run: Processes all records");
                        Console.WriteLine("     • Subsequent runs: Only processes records with timestamp > last processed");
                        Console.WriteLine("     • Efficient for append-mostly data");
                        Console.WriteLine("     • May miss updates if timestamp doesn't change");
                    }
                    else if (policyType == "SqlIntegratedChangeTrackingPolicy")
                    {
                        Console.WriteLine("   Behavior:");
                        Console.WriteLine("     • First run: Processes all records");
                        Console.WriteLine("     • Subsequent runs: Uses SQL change tracking to find changes");
                        Console.WriteLine("     • Handles inserts, updates, and deletes");
                        Console.WriteLine("     • Most efficient for SQL data sources");
                    }
                }
                else
                {
                    Console.WriteLine("   Change Detection: None (full reprocessing each run)");
                }
            }
        }

        private void DemonstratePerformanceComparison()
        {
            Console.WriteLine("\n📊 Performance Comparison");
            Console.WriteLine("=" + new string('=', 29));

            var comparisonData = new[]
            {
                new
                {
                    Strategy = "No Change Detection",
                    FirstRun = "Full scan",
                    SubsequentRuns = "Full scan",
                    Efficiency = "Low",
                    ResourceUsage = "High",
                    BestFor = "Small datasets, infrequent updates"
                },
                new
                {
                    Strategy = "High Water Mark",
                    FirstRun = "Full scan",
                    SubsequentRuns = "Incremental",
                    Efficiency = "Medium-High",
                    ResourceUsage = "Low-Medium",
                    BestFor = "Append-heavy workloads, timestamped data"
                },
                new
                {
                    Strategy = "SQL Integrated Change Tracking",
                    FirstRun = "Full scan",
                    SubsequentRuns = "Changed rows only",
                    Efficiency = "Very High",
                    ResourceUsage = "Very Low",
                    BestFor = "SQL databases with frequent updates"
                }
            };

            foreach (var data in comparisonData)
            {
                Console.WriteLine($"\n🎯 {data.Strategy}");
                Console.WriteLine($"   First Run: {data.FirstRun}");
                Console.WriteLine($"   Subsequent Runs: {data.SubsequentRuns}");
                Console.WriteLine($"   Efficiency: {data.Efficiency}");
                Console.WriteLine($"   Resource Usage: {data.ResourceUsage}");
                Console.WriteLine($"   Best For: {data.BestFor}");
            }
        }

        private void DemonstrateBestPractices()
        {
            Console.WriteLine("\n💡 Change Detection Best Practices");
            Console.WriteLine("=" + new string('=', 34));

            var practices = new[]
            {
                new
                {
                    Category = "Column Selection",
                    Practices = new[]
                    {
                        "Use indexed columns for high water mark",
                        "Ensure timestamp columns are consistently updated",
                        "Consider timezone implications for datetime columns",
                        "Use monotonically increasing values when possible"
                    }
                },
                new
                {
                    Category = "Performance Optimization",
                    Practices = new[]
                    {
                        "Index the change detection column",
                        "Use appropriate data types (datetime2 vs datetime)",
                        "Consider partitioning for large tables",
                        "Monitor change tracking overhead"
                    }
                },
                new
                {
                    Category = "Data Consistency",
                    Practices = new[]
                    {
                        "Ensure atomic updates to data and timestamp",
                        "Handle clock skew in distributed systems",
                        "Consider using triggers for automatic timestamp updates",
                        "Test with concurrent updates"
                    }
                },
                new
                {
                    Category = "Monitoring",
                    Practices = new[]
                    {
                        "Monitor indexer execution frequency",
                        "Track change detection effectiveness",
                        "Alert on change detection failures",
                        "Monitor high water mark progression"
                    }
                }
            };

            foreach (var category in practices)
            {
                Console.WriteLine($"\n🎯 {category.Category}");
                foreach (var practice in category.Practices)
                    Console.WriteLine($"   • {practice}");
            }
        }

        public async Task CleanupAsync()
        {
            var dataSourceNames = new[]
            {
                "sql-highwatermark-example",
                "sql-changetracking-example",
                "blob-lastmodified-example",
                "cosmos-timestamp-example"
            };

            foreach (var name in dataSourceNames)
            {
                try
                {
                    await _indexerClient.DeleteDataSourceConnectionAsync(name);
                }
                catch (RequestFailedException)
                {
                    // Ignore if doesn't exist
                }
            }
        }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";

            var example = new ChangeDetectionExample(searchEndpoint, apiKey);

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