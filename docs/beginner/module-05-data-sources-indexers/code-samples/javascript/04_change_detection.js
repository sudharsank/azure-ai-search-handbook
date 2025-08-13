/**
 * Change Detection Strategies Example
 * 
 * This example demonstrates different change detection policies and strategies
 * for efficient incremental indexing in Azure AI Search.
 */

const { SearchIndexerClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

class ChangeDetectionExample {
    constructor() {
        this.validateConfiguration();
        
        const credential = new AzureKeyCredential(process.env.SEARCH_API_KEY);
        this.indexerClient = new SearchIndexerClient(process.env.SEARCH_ENDPOINT, credential);
    }

    validateConfiguration() {
        if (!process.env.SEARCH_ENDPOINT || !process.env.SEARCH_API_KEY) {
            throw new Error('Missing required search service configuration.');
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${process.env.SEARCH_ENDPOINT}`);
    }

    demonstrateHighWaterMarkPolicies() {
        console.log('\n🌊 High Water Mark Change Detection Policies');
        console.log('='.repeat(50));

        const policies = [
            {
                name: 'SQL Database - LastModified',
                dataSourceType: 'azuresql',
                policy: {
                    '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                    highWaterMarkColumnName: 'LastModified'
                },
                description: 'Uses a datetime column to track changes',
                requirements: [
                    'DateTime column (e.g., LastModified, UpdatedAt)',
                    'Column updated on every record change',
                    'Column indexed for performance'
                ],
                pros: [
                    'Simple to implement',
                    'Works with any datetime column',
                    'Good performance with proper indexing'
                ],
                cons: [
                    'Requires application to maintain timestamp',
                    'May miss concurrent updates with same timestamp',
                    'Requires column to be consistently updated'
                ]
            },
            {
                name: 'Blob Storage - LastModified',
                dataSourceType: 'azureblob',
                policy: {
                    '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                    highWaterMarkColumnName: 'metadata_storage_last_modified'
                },
                description: 'Uses blob last modified timestamp',
                requirements: [
                    'Azure Blob Storage',
                    'Automatic metadata tracking enabled'
                ],
                pros: [
                    'Automatic timestamp management',
                    'No application changes required',
                    'Built into blob storage'
                ],
                cons: [
                    'Only detects file-level changes',
                    'May not detect metadata-only changes',
                    'Dependent on storage service timestamps'
                ]
            },
            {
                name: 'Cosmos DB - Timestamp',
                dataSourceType: 'cosmosdb',
                policy: {
                    '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                    highWaterMarkColumnName: '_ts'
                },
                description: 'Uses Cosmos DB internal timestamp',
                requirements: [
                    'Azure Cosmos DB',
                    'Access to _ts system property'
                ],
                pros: [
                    'Automatic timestamp management',
                    'Guaranteed uniqueness and ordering',
                    'Built into Cosmos DB'
                ],
                cons: [
                    'Limited to Cosmos DB',
                    'Timestamp is in epoch format',
                    'May require query modifications'
                ]
            }
        ];

        policies.forEach(policy => {
            console.log(`\n📋 ${policy.name}`);
            console.log(`   Description: ${policy.description}`);
            console.log(`   Column: ${policy.policy.highWaterMarkColumnName}`);

            console.log('   Requirements:');
            policy.requirements.forEach(req => console.log(`     • ${req}`));

            console.log('   Pros:');
            policy.pros.forEach(pro => console.log(`     ✅ ${pro}`));

            console.log('   Cons:');
            policy.cons.forEach(con => console.log(`     ⚠️ ${con}`));
        });
    }

    demonstrateSqlIntegratedChangeTracking() {
        console.log('\n🔄 SQL Integrated Change Tracking');
        console.log('='.repeat(40));

        console.log('SQL Server Change Tracking provides the most efficient change detection for SQL databases.');

        const policy = {
            '@odata.type': '#Microsoft.Azure.Search.SqlIntegratedChangeTrackingPolicy'
        };

        console.log('\nPolicy Configuration:');
        console.log(`   Type: SqlIntegratedChangeTrackingPolicy`);
        console.log(`   Description: Uses SQL Server's built-in change tracking`);

        console.log('\nSQL Server Setup Requirements:');
        const requirements = [
            'Enable change tracking on database: ALTER DATABASE [YourDB] SET CHANGE_TRACKING = ON',
            'Enable change tracking on table: ALTER TABLE [YourTable] ENABLE CHANGE_TRACKING',
            'Ensure proper permissions for indexer service',
            'Consider retention period for change tracking data'
        ];

        requirements.forEach((req, i) => console.log(`   ${i + 1}. ${req}`));

        console.log('\nBenefits:');
        const benefits = [
            'Most efficient - only changed rows are processed',
            'Handles deletes automatically',
            'No application changes required',
            'Built-in conflict resolution',
            'Minimal storage overhead'
        ];

        benefits.forEach(benefit => console.log(`   ✅ ${benefit}`));

        console.log('\nConsiderations:');
        const considerations = [
            'Only available for SQL Server/Azure SQL',
            'Requires database-level configuration',
            'May impact database performance slightly',
            'Change tracking data has retention limits'
        ];

        considerations.forEach(consideration => console.log(`   ⚠️ ${consideration}`));
    }

    async createChangeDetectionExamples() {
        console.log('\n🛠️ Creating Change Detection Examples');
        console.log('='.repeat(40));

        const examples = [];

        // SQL with High Water Mark (if connection string available)
        const sqlConnectionString = process.env.SQL_CONNECTION_STRING;
        if (sqlConnectionString) {
            console.log('\n📊 Creating SQL data source with High Water Mark...');
            try {
                const sqlDataSource = {
                    name: 'sql-highwatermark-example',
                    type: 'azuresql',
                    connectionString: sqlConnectionString,
                    container: { name: 'Hotels' },
                    dataChangeDetectionPolicy: {
                        '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                        highWaterMarkColumnName: 'LastModified'
                    },
                    description: 'SQL data source with LastModified change detection'
                };

                const result = await this.indexerClient.createOrUpdateDataSourceConnection(sqlDataSource);
                examples.push(['SQL High Water Mark', result]);
                console.log(`   ✅ Created: ${result.name}`);
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }

            // SQL with Integrated Change Tracking
            console.log('\n🔄 Creating SQL data source with Integrated Change Tracking...');
            try {
                const sqlCtDataSource = {
                    name: 'sql-changetracking-example',
                    type: 'azuresql',
                    connectionString: sqlConnectionString,
                    container: { name: 'Hotels' },
                    dataChangeDetectionPolicy: {
                        '@odata.type': '#Microsoft.Azure.Search.SqlIntegratedChangeTrackingPolicy'
                    },
                    description: 'SQL data source with integrated change tracking'
                };

                const result = await this.indexerClient.createOrUpdateDataSourceConnection(sqlCtDataSource);
                examples.push(['SQL Integrated Change Tracking', result]);
                console.log(`   ✅ Created: ${result.name}`);
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }

        // Blob Storage with High Water Mark
        const storageConnectionString = process.env.STORAGE_CONNECTION_STRING;
        if (storageConnectionString) {
            console.log('\n📁 Creating Blob Storage data source with High Water Mark...');
            try {
                const blobDataSource = {
                    name: 'blob-highwatermark-example',
                    type: 'azureblob',
                    connectionString: storageConnectionString,
                    container: { name: 'documents' },
                    dataChangeDetectionPolicy: {
                        '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                        highWaterMarkColumnName: 'metadata_storage_last_modified'
                    },
                    description: 'Blob storage data source with LastModified change detection'
                };

                const result = await this.indexerClient.createOrUpdateDataSourceConnection(blobDataSource);
                examples.push(['Blob Storage High Water Mark', result]);
                console.log(`   ✅ Created: ${result.name}`);
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }

        // Cosmos DB with High Water Mark
        const cosmosConnectionString = process.env.COSMOS_CONNECTION_STRING;
        if (cosmosConnectionString) {
            console.log('\n🌐 Creating Cosmos DB data source with High Water Mark...');
            try {
                const cosmosDataSource = {
                    name: 'cosmos-highwatermark-example',
                    type: 'cosmosdb',
                    connectionString: cosmosConnectionString,
                    container: { 
                        name: 'hotels',
                        query: 'SELECT * FROM c WHERE c._ts >= @HighWaterMark ORDER BY c._ts'
                    },
                    dataChangeDetectionPolicy: {
                        '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                        highWaterMarkColumnName: '_ts'
                    },
                    description: 'Cosmos DB data source with _ts change detection'
                };

                const result = await this.indexerClient.createOrUpdateDataSourceConnection(cosmosDataSource);
                examples.push(['Cosmos DB High Water Mark', result]);
                console.log(`   ✅ Created: ${result.name}`);
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }

        // Demonstrate behavior analysis
        if (examples.length > 0) {
            this.demonstrateChangeDetectionBehavior(examples);
        }

        return examples;
    }

    demonstrateChangeDetectionBehavior(examples) {
        console.log('\n🔍 Change Detection Behavior Analysis');
        console.log('='.repeat(40));

        examples.forEach(([name, dataSource]) => {
            console.log(`\n📋 Analyzing: ${name}`);
            console.log(`   Data Source: ${dataSource.name}`);
            console.log(`   Type: ${dataSource.type}`);

            const policy = dataSource.dataChangeDetectionPolicy;
            if (policy) {
                const policyType = policy['@odata.type'].split('.').pop();
                console.log(`   Change Detection: ${policyType}`);

                if (policy.highWaterMarkColumnName) {
                    console.log(`   High Water Mark Column: ${policy.highWaterMarkColumnName}`);
                }

                // Explain behavior
                if (policyType === 'HighWaterMarkChangeDetectionPolicy') {
                    console.log('   Behavior:');
                    console.log('     • First run: Processes all records');
                    console.log('     • Subsequent runs: Only processes records with timestamp > last processed');
                    console.log('     • Efficient for append-mostly data');
                    console.log('     • May miss updates if timestamp doesn\'t change');
                } else if (policyType === 'SqlIntegratedChangeTrackingPolicy') {
                    console.log('   Behavior:');
                    console.log('     • First run: Processes all records');
                    console.log('     • Subsequent runs: Uses SQL change tracking to find changes');
                    console.log('     • Handles inserts, updates, and deletes');
                    console.log('     • Most efficient for SQL data sources');
                }
            } else {
                console.log('   Change Detection: None (full reprocessing each run)');
            }
        });
    }

    demonstratePerformanceComparison() {
        console.log('\n📊 Performance Comparison');
        console.log('='.repeat(30));

        const comparisonData = [
            {
                strategy: 'No Change Detection',
                firstRun: 'Full scan',
                subsequentRuns: 'Full scan',
                efficiency: 'Low',
                resourceUsage: 'High',
                bestFor: 'Small datasets, infrequent updates'
            },
            {
                strategy: 'High Water Mark',
                firstRun: 'Full scan',
                subsequentRuns: 'Incremental',
                efficiency: 'Medium-High',
                resourceUsage: 'Low-Medium',
                bestFor: 'Append-heavy workloads, timestamped data'
            },
            {
                strategy: 'SQL Integrated Change Tracking',
                firstRun: 'Full scan',
                subsequentRuns: 'Changed rows only',
                efficiency: 'Very High',
                resourceUsage: 'Very Low',
                bestFor: 'SQL databases with frequent updates'
            }
        ];

        comparisonData.forEach(data => {
            console.log(`\n🎯 ${data.strategy}`);
            console.log(`   First Run: ${data.firstRun}`);
            console.log(`   Subsequent Runs: ${data.subsequentRuns}`);
            console.log(`   Efficiency: ${data.efficiency}`);
            console.log(`   Resource Usage: ${data.resourceUsage}`);
            console.log(`   Best For: ${data.bestFor}`);
        });
    }

    demonstrateCustomChangeDetection() {
        console.log('\n🔧 Custom Change Detection Strategies');
        console.log('='.repeat(40));

        console.log('For scenarios where built-in policies don\'t fit:');

        const customStrategies = [
            {
                name: 'Version-based Detection',
                description: 'Use a version number or hash column',
                implementation: 'Track record versions, process when version changes',
                pros: ['Handles any type of change', 'Application controlled'],
                cons: ['Requires application logic', 'Additional storage']
            },
            {
                name: 'Event-driven Updates',
                description: 'Trigger indexer runs on data changes',
                implementation: 'Use Azure Functions or Logic Apps to trigger indexer',
                pros: ['Real-time updates', 'Efficient resource usage'],
                cons: ['Complex setup', 'Requires event infrastructure']
            },
            {
                name: 'Hybrid Approach',
                description: 'Combine multiple detection methods',
                implementation: 'Use different policies for different data types',
                pros: ['Optimized for each data source', 'Maximum efficiency'],
                cons: ['Complex configuration', 'Multiple indexers needed']
            }
        ];

        customStrategies.forEach(strategy => {
            console.log(`\n🛠️ ${strategy.name}`);
            console.log(`   Description: ${strategy.description}`);
            console.log(`   Implementation: ${strategy.implementation}`);
            
            console.log('   Pros:');
            strategy.pros.forEach(pro => console.log(`     ✅ ${pro}`));
            
            console.log('   Cons:');
            strategy.cons.forEach(con => console.log(`     ⚠️ ${con}`));
        });
    }

    showBestPractices() {
        console.log('\n💡 Change Detection Best Practices');
        console.log('='.repeat(35));

        const practices = [
            {
                category: 'Column Selection',
                tips: [
                    'Use indexed columns for high water mark',
                    'Ensure timestamp columns are consistently updated',
                    'Consider timezone implications for datetime columns',
                    'Use UTC timestamps when possible'
                ]
            },
            {
                category: 'Performance Optimization',
                tips: [
                    'Index the change detection column',
                    'Use appropriate data types (datetime2 vs datetime)',
                    'Consider partitioning for large tables',
                    'Monitor query performance on change detection queries'
                ]
            },
            {
                category: 'Data Consistency',
                tips: [
                    'Ensure atomic updates of data and timestamp',
                    'Handle concurrent updates appropriately',
                    'Consider using triggers for automatic timestamp updates',
                    'Test edge cases like clock adjustments'
                ]
            },
            {
                category: 'Monitoring',
                tips: [
                    'Monitor indexer execution frequency',
                    'Track the number of documents processed per run',
                    'Alert on change detection failures',
                    'Monitor high water mark progression'
                ]
            }
        ];

        practices.forEach(practice => {
            console.log(`\n📋 ${practice.category}:`);
            practice.tips.forEach(tip => console.log(`   • ${tip}`));
        });
    }

    async cleanup(examples) {
        console.log('\n🧹 Cleaning up example resources...');
        
        for (const [name, dataSource] of examples) {
            try {
                await this.indexerClient.deleteDataSourceConnection(dataSource.name);
                console.log(`   ✅ Deleted: ${dataSource.name}`);
            } catch (error) {
                console.log(`   ⚠️ Warning deleting ${dataSource.name}: ${error.message}`);
            }
        }
    }

    async run() {
        console.log('🚀 Change Detection Strategies Example');
        console.log('='.repeat(50));

        try {
            // Demonstrate different policies
            this.demonstrateHighWaterMarkPolicies();
            this.demonstrateSqlIntegratedChangeTracking();

            // Create practical examples
            const examples = await this.createChangeDetectionExamples();

            // Analysis and best practices
            this.demonstratePerformanceComparison();
            this.demonstrateCustomChangeDetection();
            this.showBestPractices();

            console.log('\n✅ Change detection example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Choose the right change detection policy for your data source');
            console.log('- SQL Integrated Change Tracking is most efficient for SQL databases');
            console.log('- High Water Mark works well for append-heavy scenarios');
            console.log('- Index your change detection columns for performance');
            console.log('- Monitor change detection effectiveness regularly');

            // Cleanup
            if (examples.length > 0) {
                await this.cleanup(examples);
            }

        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new ChangeDetectionExample();
    try {
        await example.run();
    } catch (error) {
        console.error('Application failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = ChangeDetectionExample;