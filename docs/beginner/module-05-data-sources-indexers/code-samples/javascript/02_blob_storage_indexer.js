/**
 * Azure Blob Storage Indexer Example
 * 
 * This example demonstrates how to create and manage indexers for Azure Blob Storage data sources.
 * It covers document processing, metadata extraction, and change detection.
 * 
 * Prerequisites:
 * - Azure AI Search service
 * - Azure Storage Account with sample documents
 * - Admin API key or managed identity
 * - Required npm packages installed
 */

const { SearchIndexClient, SearchIndexerClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

// Configuration
const SEARCH_ENDPOINT = process.env.SEARCH_ENDPOINT;
const SEARCH_API_KEY = process.env.SEARCH_API_KEY;
const STORAGE_CONNECTION_STRING = process.env.STORAGE_CONNECTION_STRING;

// Resource names
const DATA_SOURCE_NAME = 'blob-documents-datasource';
const INDEX_NAME = 'documents-blob-index';
const INDEXER_NAME = 'documents-blob-indexer';
const CONTAINER_NAME = 'sample-documents';

class BlobStorageIndexerExample {
    constructor() {
        this.validateConfiguration();
        
        const credential = new AzureKeyCredential(SEARCH_API_KEY);
        this.indexClient = new SearchIndexClient(SEARCH_ENDPOINT, credential);
        this.indexerClient = new SearchIndexerClient(SEARCH_ENDPOINT, credential);
    }

    validateConfiguration() {
        if (!SEARCH_ENDPOINT || !SEARCH_API_KEY || !STORAGE_CONNECTION_STRING) {
            throw new Error('Missing required environment variables. Check your .env file.');
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${SEARCH_ENDPOINT}`);
        console.log(`🗃️ Data Source: ${DATA_SOURCE_NAME}`);
        console.log(`📊 Index: ${INDEX_NAME}`);
        console.log(`⚙️ Indexer: ${INDEXER_NAME}`);
    }

    /**
     * Creates a data source connection to Azure Blob Storage with LastModified change detection
     */
    async createBlobDataSource() {
        console.log('\n🔗 Creating blob storage data source...');

        const dataSource = {
            name: DATA_SOURCE_NAME,
            type: 'azureblob',
            connectionString: STORAGE_CONNECTION_STRING,
            container: {
                name: CONTAINER_NAME
            },
            dataChangeDetectionPolicy: {
                '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                highWaterMarkColumnName: 'metadata_storage_last_modified'
            },
            description: 'Document data from Azure Blob Storage with LastModified detection'
        };

        try {
            const result = await this.indexerClient.createOrUpdateDataSourceConnection(dataSource);
            console.log(`✅ Data source '${DATA_SOURCE_NAME}' created successfully`);
            
            // Display configuration
            console.log(`   Type: ${result.type}`);
            console.log(`   Container: ${result.container.name}`);
            console.log(`   Change Detection: ${result.dataChangeDetectionPolicy['@odata.type']}`);
            
            return result;
        } catch (error) {
            console.log(`❌ Error creating data source: ${error.message}`);
            throw error;
        }
    }

    /**
     * Creates a search index optimized for document content and metadata
     */
    async createDocumentIndex() {
        console.log('\n📊 Creating document index...');

        // Define index fields for document content and metadata
        const fields = [
            { name: 'metadata_storage_path', type: 'Edm.String', key: true, searchable: false },
            { name: 'content', type: 'Edm.String', searchable: true, analyzer: 'en.lucene' },
            { name: 'metadata_storage_name', type: 'Edm.String', filterable: true, sortable: true },
            { name: 'metadata_storage_size', type: 'Edm.Int64', filterable: true, sortable: true },
            { name: 'metadata_storage_last_modified', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: 'metadata_storage_content_type', type: 'Edm.String', filterable: true, facetable: true },
            { name: 'metadata_language', type: 'Edm.String', filterable: true, facetable: true },
            { name: 'metadata_title', type: 'Edm.String', searchable: true },
            { name: 'metadata_author', type: 'Edm.String', searchable: true, filterable: true, facetable: true },
            { name: 'keyphrases', type: 'Collection(Edm.String)', searchable: true, facetable: true }
        ];

        const index = {
            name: INDEX_NAME,
            fields: fields
        };

        try {
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Index '${INDEX_NAME}' created successfully`);
            console.log(`   Total Fields: ${result.fields.length}`);
            
            // Display key fields
            console.log('   Key fields for document processing:');
            result.fields.slice(0, 5).forEach(field => {
                const attributes = [];
                if (field.key) attributes.push('key');
                if (field.searchable) attributes.push('searchable');
                if (field.filterable) attributes.push('filterable');
                
                console.log(`     - ${field.name} (${field.type}) [${attributes.join(', ')}]`);
            });
            
            return result;
        } catch (error) {
            console.log(`❌ Error creating index: ${error.message}`);
            throw error;
        }
    }

    /**
     * Creates an indexer to process documents from blob storage
     */
    async createBlobIndexer() {
        console.log('\n⚙️ Creating blob storage indexer...');

        // Field mappings for blob storage metadata
        const fieldMappings = [
            { sourceFieldName: 'metadata_storage_path', targetFieldName: 'metadata_storage_path' },
            { sourceFieldName: 'content', targetFieldName: 'content' },
            { sourceFieldName: 'metadata_storage_name', targetFieldName: 'metadata_storage_name' },
            { sourceFieldName: 'metadata_storage_size', targetFieldName: 'metadata_storage_size' },
            { sourceFieldName: 'metadata_storage_last_modified', targetFieldName: 'metadata_storage_last_modified' },
            { sourceFieldName: 'metadata_storage_content_type', targetFieldName: 'metadata_storage_content_type' }
        ];

        const indexer = {
            name: INDEXER_NAME,
            dataSourceName: DATA_SOURCE_NAME,
            targetIndexName: INDEX_NAME,
            fieldMappings: fieldMappings,
            description: 'Indexer for documents from blob storage',
            parameters: {
                batchSize: 50, // Smaller batch for document processing
                maxFailedItems: 5,
                maxFailedItemsPerBatch: 2,
                configuration: {
                    dataToExtract: 'contentAndMetadata',
                    parsingMode: 'default',
                    excludedFileNameExtensions: '.png,.jpg,.jpeg,.gif,.bmp'
                }
            }
        };

        try {
            const result = await this.indexerClient.createOrUpdateIndexer(indexer);
            console.log(`✅ Indexer '${INDEXER_NAME}' created successfully`);
            console.log(`   Data Source: ${result.dataSourceName}`);
            console.log(`   Target Index: ${result.targetIndexName}`);
            console.log(`   Field Mappings: ${result.fieldMappings?.length || 0}`);
            
            return result;
        } catch (error) {
            console.log(`❌ Error creating indexer: ${error.message}`);
            throw error;
        }
    }

    /**
     * Runs the indexer and monitors document processing
     */
    async runAndMonitorIndexer() {
        console.log(`\n🚀 Starting blob indexer: ${INDEXER_NAME}`);

        try {
            // Start the indexer
            await this.indexerClient.runIndexer(INDEXER_NAME);
            console.log('✅ Indexer started successfully');

            // Monitor execution
            const startTime = Date.now();
            const maxWaitTime = 5 * 60 * 1000; // 5 minutes

            while (Date.now() - startTime < maxWaitTime) {
                const status = await this.indexerClient.getIndexerStatus(INDEXER_NAME);

                const currentTime = new Date().toLocaleTimeString();
                console.log(`\n⏰ ${currentTime} - Status: ${status.status}`);

                if (status.lastResult) {
                    const result = status.lastResult;
                    console.log(`   📄 Documents processed: ${result.itemCount || 0}`);
                    console.log(`   ❌ Documents failed: ${result.failedItemCount || 0}`);

                    // Show processing rate if available
                    if (result.itemCount && result.itemCount > 0 && result.endTime && result.startTime) {
                        const duration = (new Date(result.endTime) - new Date(result.startTime)) / 1000;
                        if (duration > 0) {
                            const rate = result.itemCount / duration;
                            console.log(`   📊 Processing rate: ${rate.toFixed(2)} docs/sec`);
                        }
                    }

                    // Show any errors
                    if (result.errors && result.errors.length > 0) {
                        console.log(`   ⚠️ Recent errors:`);
                        result.errors.slice(0, 3).forEach(error => {
                            console.log(`     - ${error.errorMessage}`);
                        });
                    }
                }

                if (status.status === 'success' || status.status === 'error') {
                    console.log(`\n🎉 Indexer execution completed with status: ${status.status}`);
                    break;
                }

                await this.sleep(10000); // Wait 10 seconds
            }
        } catch (error) {
            console.log(`❌ Error running indexer: ${error.message}`);
            throw error;
        }
    }

    /**
     * Tests search functionality on the indexed documents
     */
    async testDocumentSearch() {
        console.log('\n🔍 Testing document search...');

        const { SearchClient } = require('@azure/search-documents');
        const searchClient = new SearchClient(SEARCH_ENDPOINT, INDEX_NAME, new AzureKeyCredential(SEARCH_API_KEY));

        const testQueries = [
            { name: 'All documents', searchText: '*', filter: null, orderBy: null },
            { name: 'Content search', searchText: 'document', filter: null, orderBy: null },
            { name: 'Filter by content type', searchText: '*', filter: "metadata_storage_content_type eq 'application/pdf'", orderBy: null },
            { name: 'Sort by size', searchText: '*', filter: null, orderBy: ['metadata_storage_size desc'] }
        ];

        for (const test of testQueries) {
            console.log(`\n   🔍 ${test.name}:`);
            try {
                const searchOptions = {
                    top: 3,
                    select: ['metadata_storage_name', 'metadata_storage_content_type', 'metadata_storage_size']
                };

                if (test.filter) searchOptions.filter = test.filter;
                if (test.orderBy) searchOptions.orderBy = test.orderBy;

                const results = await searchClient.search(test.searchText, searchOptions);
                const documents = [];
                
                for await (const result of results.results) {
                    documents.push(result);
                }

                console.log(`      Found ${documents.length} results`);

                documents.slice(0, 2).forEach((result, index) => {
                    const filename = result.document.metadata_storage_name || 'N/A';
                    const contentType = result.document.metadata_storage_content_type || 'N/A';
                    const size = result.document.metadata_storage_size || 0;
                    console.log(`      ${index + 1}. ${filename} (${contentType}) - ${size.toLocaleString()} bytes`);
                });
            } catch (error) {
                console.log(`      ❌ Error: ${error.message}`);
            }
        }
    }

    showCleanupOptions() {
        console.log('\n🧹 Cleanup options:');
        console.log('   To clean up resources, call:');
        console.log(`   - await indexerClient.deleteIndexer('${INDEXER_NAME}');`);
        console.log(`   - await indexClient.deleteIndex('${INDEX_NAME}');`);
        console.log(`   - await indexerClient.deleteDataSourceConnection('${DATA_SOURCE_NAME}');`);
    }

    /**
     * Cleanup method to delete created resources
     */
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

    /**
     * Main execution method
     */
    async run() {
        console.log('🚀 Azure Blob Storage Indexer Example');
        console.log('='.repeat(50));

        try {
            // Create resources
            const dataSource = await this.createBlobDataSource();
            const index = await this.createDocumentIndex();
            const indexer = await this.createBlobIndexer();

            // Run and monitor indexer
            await this.runAndMonitorIndexer();

            // Test search functionality
            await this.testDocumentSearch();

            // Show cleanup options
            this.showCleanupOptions();

            console.log('\n✅ Blob storage indexer example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- LastModified change detection is ideal for file-based data sources');
            console.log('- Metadata extraction provides valuable searchable information');
            console.log('- Content type filtering helps organize different document types');
            console.log('- Batch size optimization is important for document processing performance');
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

// Main execution
async function main() {
    const example = new BlobStorageIndexerExample();
    
    try {
        await example.run();
    } catch (error) {
        console.error('Application failed:', error.message);
        process.exit(1);
    }
}

// Run if this file is executed directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = BlobStorageIndexerExample;