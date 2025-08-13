/**
 * Indexer Scheduling Example
 * 
 * This example demonstrates how to configure and manage indexer schedules
 * for automated execution patterns in Azure AI Search.
 */

const { SearchIndexClient, SearchIndexerClient, SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

// Configuration
const SEARCH_ENDPOINT = process.env.SEARCH_ENDPOINT;
const SEARCH_API_KEY = process.env.SEARCH_API_KEY;
const SQL_CONNECTION_STRING = process.env.SQL_CONNECTION_STRING;

// Resource names
const DATA_SOURCE_NAME = 'scheduled-hotels-datasource';
const INDEX_NAME = 'hotels-scheduled-index';
const INDEXER_NAME = 'hotels-scheduled-indexer';

class IndexerSchedulingExample {
    constructor() {
        this.validateConfiguration();
        
        const credential = new AzureKeyCredential(SEARCH_API_KEY);
        this.indexClient = new SearchIndexClient(SEARCH_ENDPOINT, credential);
        this.indexerClient = new SearchIndexerClient(SEARCH_ENDPOINT, credential);
        this.searchClient = new SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential);
    }

    validateConfiguration() {
        if (!SEARCH_ENDPOINT || !SEARCH_API_KEY) {
            throw new Error('Missing required search service configuration.');
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${SEARCH_ENDPOINT}`);
        console.log(`🗃️ Data Source: ${DATA_SOURCE_NAME}`);
        console.log(`📊 Index: ${INDEX_NAME}`);
        console.log(`⚙️ Indexer: ${INDEXER_NAME}`);
    }

    demonstrateSchedulePatterns() {
        console.log('\n⏰ Common Indexer Schedule Patterns');
        console.log('='.repeat(40));

        const schedulePatterns = [
            {
                name: 'Hourly Updates',
                interval: 'PT1H',
                description: 'Run every hour for near real-time updates',
                useCase: 'High-frequency data changes, critical search applications',
                pros: ['Near real-time updates', 'Good for dynamic content'],
                cons: ['Higher resource usage', 'May hit rate limits']
            },
            {
                name: 'Daily Batch Processing',
                interval: 'P1D',
                startTime: '2024-01-01T02:00:00Z',
                description: 'Run once daily during off-peak hours',
                useCase: 'Daily data exports, batch processing scenarios',
                pros: ['Predictable resource usage', 'Good for large datasets'],
                cons: ['Less frequent updates', 'Potential data staleness']
            },
            {
                name: 'Business Hours Only',
                interval: 'PT4H',
                startTime: '2024-01-01T08:00:00Z',
                description: 'Run every 4 hours during business hours (8 AM - 6 PM)',
                useCase: 'Business applications with defined operating hours',
                pros: ['Aligned with business needs', 'Reduced off-hours processing'],
                cons: ['Complex scheduling logic needed', 'May miss off-hours changes']
            },
            {
                name: 'Weekly Maintenance',
                interval: 'P7D',
                startTime: '2024-01-07T01:00:00Z',
                description: 'Run weekly for full reprocessing',
                useCase: 'Data quality checks, full index rebuilds',
                pros: ['Comprehensive processing', 'Good for maintenance tasks'],
                cons: ['Infrequent updates', 'Long periods between runs']
            },
            {
                name: 'Custom Interval',
                interval: 'PT15M',
                description: 'Run every 15 minutes for high-frequency updates',
                useCase: 'Real-time applications, frequently changing data',
                pros: ['Very current data', 'Quick response to changes'],
                cons: ['High resource consumption', 'Potential for conflicts']
            }
        ];

        schedulePatterns.forEach(pattern => {
            console.log(`\n📅 ${pattern.name}`);
            console.log(`   Interval: ${pattern.interval}`);
            if (pattern.startTime) {
                console.log(`   Start Time: ${pattern.startTime}`);
            }
            console.log(`   Description: ${pattern.description}`);
            console.log(`   Use Case: ${pattern.useCase}`);
            
            console.log('   Pros:');
            pattern.pros.forEach(pro => console.log(`     ✅ ${pro}`));
            
            console.log('   Cons:');
            pattern.cons.forEach(con => console.log(`     ⚠️ ${con}`));
        });
    }

    async createScheduledDataSource() {
        console.log('\n🔗 Creating data source for scheduled indexer...');

        if (!SQL_CONNECTION_STRING) {
            console.log('⚠️ SQL connection string not provided, using mock configuration');
            return null;
        }

        const dataSource = {
            name: DATA_SOURCE_NAME,
            type: 'azuresql',
            connectionString: SQL_CONNECTION_STRING,
            container: { name: 'Hotels' },
            dataChangeDetectionPolicy: {
                '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                highWaterMarkColumnName: 'LastModified'
            },
            description: 'SQL data source for scheduled indexer example'
        };

        try {
            const result = await this.indexerClient.createOrUpdateDataSourceConnection(dataSource);
            console.log(`✅ Data source '${DATA_SOURCE_NAME}' created successfully`);
            console.log(`   Type: ${result.type}`);
            console.log(`   Change Detection: High Water Mark`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating data source: ${error.message}`);
            throw error;
        }
    }

    async createScheduledIndex() {
        console.log('\n📊 Creating index for scheduled processing...');

        const fields = [
            { name: 'id', type: 'Edm.String', key: true, searchable: false },
            { name: 'hotelName', type: 'Edm.String', searchable: true, sortable: true },
            { name: 'description', type: 'Edm.String', searchable: true, analyzer: 'en.lucene' },
            { name: 'category', type: 'Edm.String', filterable: true, facetable: true },
            { name: 'rating', type: 'Edm.Double', filterable: true, sortable: true, facetable: true },
            { name: 'lastModified', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: 'indexedAt', type: 'Edm.DateTimeOffset', filterable: true, sortable: true }
        ];

        const index = { name: INDEX_NAME, fields };

        try {
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Index '${INDEX_NAME}' created successfully`);
            console.log(`   Total Fields: ${result.fields.length}`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating index: ${error.message}`);
            throw error;
        }
    }

    async createScheduledIndexers() {
        console.log('\n⚙️ Creating indexers with different schedules...');

        const scheduleConfigurations = [
            {
                name: `${INDEXER_NAME}-hourly`,
                description: 'Hourly scheduled indexer',
                schedule: {
                    interval: 'PT1H',
                    startTime: new Date(Date.now() + 5 * 60 * 1000).toISOString() // Start in 5 minutes
                }
            },
            {
                name: `${INDEXER_NAME}-daily`,
                description: 'Daily scheduled indexer at 2 AM',
                schedule: {
                    interval: 'P1D',
                    startTime: '2024-01-01T02:00:00Z'
                }
            },
            {
                name: `${INDEXER_NAME}-business-hours`,
                description: 'Business hours indexer (every 4 hours, 8 AM - 6 PM)',
                schedule: {
                    interval: 'PT4H',
                    startTime: '2024-01-01T08:00:00Z'
                }
            }
        ];

        const createdIndexers = [];

        for (const config of scheduleConfigurations) {
            console.log(`\n   Creating ${config.name}...`);
            
            const indexer = {
                name: config.name,
                dataSourceName: DATA_SOURCE_NAME,
                targetIndexName: INDEX_NAME,
                description: config.description,
                schedule: config.schedule,
                parameters: {
                    batchSize: 100,
                    maxFailedItems: 10,
                    maxFailedItemsPerBatch: 5
                }
            };

            try {
                const result = await this.indexerClient.createOrUpdateIndexer(indexer);
                createdIndexers.push(result);
                
                console.log(`   ✅ Created: ${result.name}`);
                console.log(`      Interval: ${result.schedule?.interval || 'None'}`);
                console.log(`      Start Time: ${result.schedule?.startTime || 'Immediate'}`);
                console.log(`      Description: ${result.description}`);
            } catch (error) {
                console.log(`   ❌ Error creating ${config.name}: ${error.message}`);
            }
        }

        return createdIndexers;
    }

    async demonstrateScheduleManagement(indexers) {
        console.log('\n📋 Schedule Management Operations');
        console.log('='.repeat(35));

        for (const indexer of indexers) {
            console.log(`\n🔍 Managing schedule for: ${indexer.name}`);
            
            try {
                // Get current status
                const status = await this.indexerClient.getIndexerStatus(indexer.name);
                console.log(`   Current Status: ${status.status}`);
                console.log(`   Last Run: ${status.lastResult?.startTime || 'Never'}`);
                console.log(`   Next Run: ${status.lastResult?.endTime ? 'Calculated based on schedule' : 'Pending'}`);

                // Demonstrate schedule modification
                if (indexer.name.includes('hourly')) {
                    console.log('\n   🔧 Modifying hourly schedule to every 2 hours...');
                    
                    const updatedIndexer = {
                        ...indexer,
                        schedule: {
                            interval: 'PT2H',
                            startTime: indexer.schedule.startTime
                        }
                    };

                    const result = await this.indexerClient.createOrUpdateIndexer(updatedIndexer);
                    console.log(`   ✅ Schedule updated: ${result.schedule.interval}`);
                }

                // Demonstrate manual run
                console.log('\n   🚀 Triggering manual run...');
                await this.indexerClient.runIndexer(indexer.name);
                console.log('   ✅ Manual run triggered');

                // Wait a moment and check status
                await this.sleep(2000);
                const newStatus = await this.indexerClient.getIndexerStatus(indexer.name);
                console.log(`   📊 Updated Status: ${newStatus.status}`);

            } catch (error) {
                console.log(`   ❌ Error managing ${indexer.name}: ${error.message}`);
            }
        }
    }

    async monitorScheduledExecution(indexerName, durationMinutes = 2) {
        console.log(`\n📊 Monitoring scheduled execution for ${indexerName}`);
        console.log(`   Duration: ${durationMinutes} minutes`);
        console.log('='.repeat(50));

        const startTime = Date.now();
        const endTime = startTime + (durationMinutes * 60 * 1000);
        let lastStatus = null;

        while (Date.now() < endTime) {
            try {
                const status = await this.indexerClient.getIndexerStatus(indexerName);
                const currentTime = new Date().toLocaleTimeString();

                // Only log if status changed
                if (!lastStatus || lastStatus.status !== status.status || 
                    lastStatus.lastResult?.startTime !== status.lastResult?.startTime) {
                    
                    console.log(`\n⏰ ${currentTime} - Status Update:`);
                    console.log(`   Status: ${status.status}`);
                    
                    if (status.lastResult) {
                        const result = status.lastResult;
                        console.log(`   Last Run: ${result.startTime}`);
                        console.log(`   Items Processed: ${result.itemCount || 0}`);
                        console.log(`   Errors: ${result.failedItemCount || 0}`);
                        
                        if (result.endTime && result.startTime) {
                            const duration = (new Date(result.endTime) - new Date(result.startTime)) / 1000;
                            console.log(`   Duration: ${duration}s`);
                        }
                    }

                    if (status.schedule) {
                        console.log(`   Schedule: ${status.schedule.interval}`);
                        console.log(`   Next Run: Calculated from last completion + interval`);
                    }

                    lastStatus = status;
                }

                await this.sleep(10000); // Check every 10 seconds
            } catch (error) {
                console.log(`   ❌ Error monitoring: ${error.message}`);
                break;
            }
        }

        console.log('\n✅ Monitoring period completed');
    }

    demonstrateScheduleBestPractices() {
        console.log('\n💡 Indexer Scheduling Best Practices');
        console.log('='.repeat(40));

        const bestPractices = [
            {
                category: 'Schedule Design',
                practices: [
                    'Align schedule with data update patterns',
                    'Consider time zones for global applications',
                    'Use off-peak hours for resource-intensive operations',
                    'Plan for maintenance windows and downtime'
                ]
            },
            {
                category: 'Performance Optimization',
                practices: [
                    'Balance frequency with resource consumption',
                    'Use change detection to minimize processing',
                    'Configure appropriate batch sizes',
                    'Monitor execution duration trends'
                ]
            },
            {
                category: 'Error Handling',
                practices: [
                    'Set reasonable error thresholds',
                    'Implement alerting for failed executions',
                    'Plan for retry strategies',
                    'Monitor indexer health regularly'
                ]
            },
            {
                category: 'Resource Management',
                practices: [
                    'Stagger multiple indexer schedules',
                    'Consider search service capacity limits',
                    'Plan for peak usage periods',
                    'Monitor search unit consumption'
                ]
            }
        ];

        bestPractices.forEach(category => {
            console.log(`\n📋 ${category.category}:`);
            category.practices.forEach(practice => {
                console.log(`   • ${practice}`);
            });
        });
    }

    demonstrateScheduleFormats() {
        console.log('\n📅 Schedule Format Examples');
        console.log('='.repeat(30));

        const scheduleExamples = [
            { format: 'PT15M', description: 'Every 15 minutes' },
            { format: 'PT1H', description: 'Every hour' },
            { format: 'PT4H', description: 'Every 4 hours' },
            { format: 'P1D', description: 'Every day' },
            { format: 'P7D', description: 'Every week' },
            { format: 'P1M', description: 'Every month (approximately)' }
        ];

        console.log('\nISO 8601 Duration Format:');
        scheduleExamples.forEach(example => {
            console.log(`   ${example.format.padEnd(8)} - ${example.description}`);
        });

        console.log('\nStart Time Examples:');
        const startTimeExamples = [
            { time: '2024-01-01T02:00:00Z', description: 'Daily at 2 AM UTC' },
            { time: '2024-01-01T08:00:00-08:00', description: 'Daily at 8 AM PST' },
            { time: '2024-01-07T01:00:00Z', description: 'Weekly on Sunday at 1 AM UTC' }
        ];

        startTimeExamples.forEach(example => {
            console.log(`   ${example.time} - ${example.description}`);
        });
    }

    async demonstrateScheduleDisabling(indexers) {
        console.log('\n⏸️ Demonstrating Schedule Disabling');
        console.log('='.repeat(35));

        for (const indexer of indexers.slice(0, 1)) { // Just demonstrate with first indexer
            console.log(`\n🔧 Working with: ${indexer.name}`);
            
            try {
                // Disable schedule by removing it
                console.log('   Disabling schedule...');
                const disabledIndexer = {
                    ...indexer,
                    schedule: null
                };

                await this.indexerClient.createOrUpdateIndexer(disabledIndexer);
                console.log('   ✅ Schedule disabled - indexer now runs only on manual trigger');

                // Re-enable schedule
                console.log('   Re-enabling schedule...');
                await this.indexerClient.createOrUpdateIndexer(indexer);
                console.log('   ✅ Schedule re-enabled');

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    showCleanupOptions() {
        console.log('\n🧹 Cleanup options:');
        console.log('   To clean up resources, call:');
        console.log(`   - Delete indexers with schedule patterns`);
        console.log(`   - Delete index: ${INDEX_NAME}`);
        console.log(`   - Delete data source: ${DATA_SOURCE_NAME}`);
    }

    async cleanup(indexers) {
        console.log('\n🧹 Cleaning up scheduled indexers...');
        
        for (const indexer of indexers) {
            try {
                await this.indexerClient.deleteIndexer(indexer.name);
                console.log(`   ✅ Deleted indexer: ${indexer.name}`);
            } catch (error) {
                console.log(`   ⚠️ Warning deleting ${indexer.name}: ${error.message}`);
            }
        }

        try {
            await this.indexClient.deleteIndex(INDEX_NAME);
            console.log(`   ✅ Deleted index: ${INDEX_NAME}`);
        } catch (error) {
            console.log(`   ⚠️ Warning deleting index: ${error.message}`);
        }

        try {
            await this.indexerClient.deleteDataSourceConnection(DATA_SOURCE_NAME);
            console.log(`   ✅ Deleted data source: ${DATA_SOURCE_NAME}`);
        } catch (error) {
            console.log(`   ⚠️ Warning deleting data source: ${error.message}`);
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async run() {
        console.log('🚀 Indexer Scheduling Example');
        console.log('='.repeat(50));

        try {
            // Demonstrate schedule concepts
            this.demonstrateSchedulePatterns();
            this.demonstrateScheduleFormats();

            // Create resources (if SQL connection available)
            const dataSource = await this.createScheduledDataSource();
            const index = await this.createScheduledIndex();
            
            if (dataSource) {
                const indexers = await this.createScheduledIndexers();
                
                if (indexers.length > 0) {
                    await this.demonstrateScheduleManagement(indexers);
                    await this.demonstrateScheduleDisabling(indexers);
                    
                    // Monitor one indexer briefly
                    if (indexers[0]) {
                        await this.monitorScheduledExecution(indexers[0].name, 1);
                    }
                    
                    await this.cleanup(indexers);
                }
            } else {
                console.log('\n⚠️ Skipping indexer creation due to missing SQL connection');
            }

            this.demonstrateScheduleBestPractices();
            this.showCleanupOptions();

            console.log('\n✅ Indexer scheduling example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use ISO 8601 duration format for intervals');
            console.log('- Align schedules with data update patterns');
            console.log('- Consider resource consumption and limits');
            console.log('- Implement proper monitoring and alerting');
            console.log('- Plan for maintenance and error scenarios');

        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new IndexerSchedulingExample();
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

module.exports = IndexerSchedulingExample;