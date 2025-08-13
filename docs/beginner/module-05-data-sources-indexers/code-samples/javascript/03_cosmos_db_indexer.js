/**
 * Azure Cosmos DB Indexer Example
 * 
 * This example demonstrates how to create and manage indexers for Azure Cosmos DB data sources.
 * It covers JSON document processing, change feed integration, and partition key handling.
 */

const { SearchIndexClient, SearchIndexerClient, SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

// Configuration
const SEARCH_ENDPOINT = process.env.SEARCH_ENDPOINT;
const SEARCH_API_KEY = process.env.SEARCH_API_KEY;
const COSMOS_CONNECTION_STRING = process.env.COSMOS_CONNECTION_STRING;

// Resource names
const DATA_SOURCE_NAME = 'cosmos-hotels-datasource';
const INDEX_NAME = 'hotels-cosmos-index';
const INDEXER_NAME = 'hotels-cosmos-indexer';
const CONTAINER_NAME = 'hotels';

class CosmosDbIndexerExample {
    constructor() {
        this.validateConfiguration();
        
        const credential = new AzureKeyCredential(SEARCH_API_KEY);
        this.indexClient = new SearchIndexClient(SEARCH_ENDPOINT, credential);
        this.indexerClient = new SearchIndexerClient(SEARCH_ENDPOINT, credential);
    }

    validateConfiguration() {
        if (!SEARCH_ENDPOINT || !SEARCH_API_KEY || !COSMOS_CONNECTION_STRING) {
            throw new Error('Missing required environment variables. Check your .env file.');
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${SEARCH_ENDPOINT}`);
        console.log(`🗃️ Data Source: ${DATA_SOURCE_NAME}`);
        console.log(`📊 Index: ${INDEX_NAME}`);
        console.log(`⚙️ Indexer: ${INDEXER_NAME}`);
    }

    async createCosmosDataSource() {
        console.log('\n🔗 Creating Cosmos DB data source...');

        const dataSource = {
            name: DATA_SOURCE_NAME,
            type: 'cosmosdb',
            connectionString: COSMOS_CONNECTION_STRING,
            container: {
                name: CONTAINER_NAME,
                query: 'SELECT * FROM c WHERE c._ts >= @HighWaterMark ORDER BY c._ts'
            },
            dataChangeDetectionPolicy: {
                '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                highWaterMarkColumnName: '_ts'
            },
            description: 'Hotel data from Cosmos DB with change feed detection'
        };

        try {
            const result = await this.indexerClient.createOrUpdateDataSourceConnection(dataSource);
            console.log(`✅ Data source '${DATA_SOURCE_NAME}' created successfully`);
            console.log(`   Type: ${result.type}`);
            console.log(`   Container: ${result.container.name}`);
            console.log(`   Change Detection: ${result.dataChangeDetectionPolicy['@odata.type']}`);
            console.log(`   High Water Mark: ${result.dataChangeDetectionPolicy.highWaterMarkColumnName}`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating data source: ${error.message}`);
            throw error;
        }
    }

    async createHotelsIndex() {
        console.log('\n📊 Creating hotels index...');

        const fields = [
            { name: 'id', type: 'Edm.String', key: true, searchable: false },
            { name: 'hotelName', type: 'Edm.String', searchable: true, sortable: true },
            { name: 'description', type: 'Edm.String', searchable: true, analyzer: 'en.lucene' },
            { name: 'category', type: 'Edm.String', filterable: true, facetable: true },
            { name: 'rating', type: 'Edm.Double', filterable: true, sortable: true, facetable: true },
            {
                name: 'address',
                type: 'Edm.ComplexType',
                fields: [
                    { name: 'street', type: 'Edm.String', searchable: true },
                    { name: 'city', type: 'Edm.String', searchable: true, filterable: true, facetable: true },
                    { name: 'state', type: 'Edm.String', searchable: true, filterable: true, facetable: true },
                    { name: 'zipCode', type: 'Edm.String', filterable: true },
                    { name: 'country', type: 'Edm.String', filterable: true, facetable: true }
                ]
            },
            { name: 'amenities', type: 'Collection(Edm.String)', searchable: true, facetable: true },
            { name: 'lastRenovated', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: '_ts', type: 'Edm.Int64', filterable: true, sortable: true },
            { name: 'location', type: 'Edm.GeographyPoint', filterable: true, sortable: true }
        ];

        const index = { name: INDEX_NAME, fields };

        try {
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Index '${INDEX_NAME}' created successfully`);
            console.log(`   Total Fields: ${result.fields.length}`);
            
            console.log('   Key fields for hotel data:');
            const keyFields = ['id', 'hotelName', 'category', 'rating', 'address'];
            result.fields.filter(f => keyFields.includes(f.name)).forEach(field => {
                const attributes = [];
                if (field.key) attributes.push('key');
                if (field.searchable) attributes.push('searchable');
                if (field.filterable) attributes.push('filterable');
                if (field.facetable) attributes.push('facetable');
                
                const fieldType = field.type === 'Edm.ComplexType' ? 'Complex' : field.type;
                console.log(`     - ${field.name} (${fieldType}) [${attributes.join(', ')}]`);
            });
            
            return result;
        } catch (error) {
            console.log(`❌ Error creating index: ${error.message}`);
            throw error;
        }
    }

    async createCosmosIndexer() {
        console.log('\n⚙️ Creating Cosmos DB indexer...');

        const fieldMappings = [
            { sourceFieldName: 'id', targetFieldName: 'id' },
            { sourceFieldName: 'hotelName', targetFieldName: 'hotelName' },
            { sourceFieldName: 'description', targetFieldName: 'description' },
            { sourceFieldName: 'category', targetFieldName: 'category' },
            { sourceFieldName: 'rating', targetFieldName: 'rating' },
            { sourceFieldName: 'address', targetFieldName: 'address' },
            { sourceFieldName: 'amenities', targetFieldName: 'amenities' },
            { sourceFieldName: 'lastRenovated', targetFieldName: 'lastRenovated' },
            { sourceFieldName: '_ts', targetFieldName: '_ts' }
        ];

        const indexer = {
            name: INDEXER_NAME,
            dataSourceName: DATA_SOURCE_NAME,
            targetIndexName: INDEX_NAME,
            fieldMappings,
            description: 'Indexer for hotel data from Cosmos DB',
            parameters: {
                batchSize: 100,
                maxFailedItems: 10,
                maxFailedItemsPerBatch: 5,
                configuration: { parsingMode: 'json' }
            }
        };

        try {
            const result = await this.indexerClient.createOrUpdateIndexer(indexer);
            console.log(`✅ Indexer '${INDEXER_NAME}' created successfully`);
            console.log(`   Data Source: ${result.dataSourceName}`);
            console.log(`   Target Index: ${result.targetIndexName}`);
            console.log(`   Field Mappings: ${result.fieldMappings?.length || 0}`);
            console.log(`   Batch Size: ${result.parameters?.batchSize || 0}`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating indexer: ${error.message}`);
            throw error;
        }
    }

    async runAndMonitorIndexer() {
        console.log(`\n🚀 Starting Cosmos DB indexer: ${INDEXER_NAME}`);

        try {
            await this.indexerClient.runIndexer(INDEXER_NAME);
            console.log('✅ Indexer started successfully');

            const startTime = Date.now();
            const maxWaitTime = 5 * 60 * 1000;

            while (Date.now() - startTime < maxWaitTime) {
                const status = await this.indexerClient.getIndexerStatus(INDEXER_NAME);
                const currentTime = new Date().toLocaleTimeString();
                console.log(`\n⏰ ${currentTime} - Status: ${status.status}`);

                if (status.lastResult) {
                    const result = status.lastResult;
                    console.log(`   🏨 Hotels processed: ${result.itemCount || 0}`);
                    console.log(`   ❌ Hotels failed: ${result.failedItemCount || 0}`);

                    if (result.itemCount && result.itemCount > 0 && result.endTime && result.startTime) {
                        const duration = (new Date(result.endTime) - new Date(result.startTime)) / 1000;
                        if (duration > 0) {
                            const rate = result.itemCount / duration;
                            console.log(`   📊 Processing rate: ${rate.toFixed(2)} hotels/sec`);
                        }
                    }

                    if (result.errors && result.errors.length > 0) {
                        console.log(`   ⚠️ Recent errors:`);
                        result.errors.slice(0, 3).forEach(error => {
                            console.log(`     - ${error.errorMessage}`);
                        });
                    }

                    if (result.warnings && result.warnings.length > 0) {
                        console.log(`   ⚠️ Warnings: ${result.warnings.length}`);
                    }
                }

                if (status.status === 'success' || status.status === 'error') {
                    console.log(`\n🎉 Indexer execution completed with status: ${status.status}`);
                    break;
                }

                await this.sleep(10000);
            }
        } catch (error) {
            console.log(`❌ Error running indexer: ${error.message}`);
            throw error;
        }
    }

    async testHotelSearch() {
        console.log('\n🔍 Testing hotel search...');

        const searchClient = new SearchClient(SEARCH_ENDPOINT, INDEX_NAME, new AzureKeyCredential(SEARCH_API_KEY));

        const testQueries = [
            { name: 'All hotels', searchText: '*', filter: null, orderBy: null, facets: null },
            { name: 'Luxury hotels', searchText: 'luxury', filter: null, orderBy: null, facets: null },
            { name: 'High-rated hotels', searchText: '*', filter: 'rating ge 4.0', orderBy: ['rating desc'], facets: null },
            { name: 'Hotels by city', searchText: '*', filter: null, orderBy: null, facets: ['address/city'] },
            { name: 'Hotels with amenities', searchText: '*', filter: "amenities/any(a: a eq 'WiFi')", orderBy: null, facets: null }
        ];

        for (const test of testQueries) {
            console.log(`\n   🔍 ${test.name}:`);
            try {
                const searchOptions = {
                    top: test.facets ? 0 : 3,
                    select: ['hotelName', 'category', 'rating', 'address']
                };

                if (test.filter) searchOptions.filter = test.filter;
                if (test.orderBy) searchOptions.orderBy = test.orderBy;
                if (test.facets) searchOptions.facets = test.facets;

                const results = await searchClient.search(test.searchText, searchOptions);

                if (test.facets) {
                    if (results.facets && results.facets['address/city']) {
                        console.log(`      Cities found:`);
                        results.facets['address/city'].slice(0, 5).forEach(facet => {
                            console.log(`        - ${facet.value}: ${facet.count} hotels`);
                        });
                    }
                } else {
                    const documents = [];
                    for await (const result of results.results) {
                        documents.push(result);
                    }

                    console.log(`      Found ${documents.length} results`);

                    documents.slice(0, 2).forEach((result, index) => {
                        const hotelName = result.document.hotelName || 'N/A';
                        const category = result.document.category || 'N/A';
                        const rating = result.document.rating || 0;
                        const city = result.document.address?.city || 'N/A';
                        console.log(`      ${index + 1}. ${hotelName} (${category}) - ${rating}⭐ in ${city}`);
                    });
                }
            } catch (error) {
                console.log(`      ❌ Error: ${error.message}`);
            }
        }
    }

    demonstrateChangeFeed() {
        console.log('\n🔄 Change Feed Detection:');
        console.log('   Cosmos DB indexer uses the \'_ts\' field for change detection');
        console.log('   Benefits:');
        console.log('   - Automatic detection of new and updated documents');
        console.log('   - Efficient incremental updates');
        console.log('   - Built-in ordering by timestamp');
        console.log('   - No additional configuration required');
        console.log('\n   The indexer query includes: WHERE c._ts >= @HighWaterMark ORDER BY c._ts');
        console.log('   This ensures only changed documents are processed on subsequent runs');
    }

    showCleanupOptions() {
        console.log('\n🧹 Cleanup options:');
        console.log('   To clean up resources, call:');
        console.log(`   - await indexerClient.deleteIndexer('${INDEXER_NAME}');`);
        console.log(`   - await indexClient.deleteIndex('${INDEX_NAME}');`);
        console.log(`   - await indexerClient.deleteDataSourceConnection('${DATA_SOURCE_NAME}');`);
    }

    async cleanup() {
        try {
            await this.indexerClient.deleteIndexer(INDEXER_NAME);
            await this.indexClient.deleteIndex(INDEX_NAME);
            await this.indexerClient.deleteDataSourceConnection(DATA_SOURCE_NAME);
            console.log('✅ Resources cleaned up successfully');
        } catch (error) {
            console.log(`⚠️ Cleanup warning: ${error.message}`);
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async run() {
        console.log('🚀 Azure Cosmos DB Indexer Example');
        console.log('='.repeat(50));

        try {
            const dataSource = await this.createCosmosDataSource();
            const index = await this.createHotelsIndex();
            const indexer = await this.createCosmosIndexer();

            await this.runAndMonitorIndexer();
            await this.testHotelSearch();
            this.demonstrateChangeFeed();
            this.showCleanupOptions();

            console.log('\n✅ Cosmos DB indexer example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Cosmos DB change feed provides efficient incremental updates');
            console.log('- Complex fields handle nested JSON structures well');
            console.log('- Collection fields are perfect for arrays like amenities');
            console.log('- Faceted search works great with categorical hotel data');
            console.log('- Higher batch sizes work well with JSON documents');
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new CosmosDbIndexerExample();
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

module.exports = CosmosDbIndexerExample;