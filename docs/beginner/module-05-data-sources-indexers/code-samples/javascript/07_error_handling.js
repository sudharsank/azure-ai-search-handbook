/**
 * Error Handling Example
 * 
 * This example demonstrates robust error handling patterns for Azure AI Search
 * indexers, including retry logic, error thresholds, and monitoring strategies.
 */

const { SearchIndexClient, SearchIndexerClient, SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

// Configuration
const SEARCH_ENDPOINT = process.env.SEARCH_ENDPOINT;
const SEARCH_API_KEY = process.env.SEARCH_API_KEY;
const SQL_CONNECTION_STRING = process.env.SQL_CONNECTION_STRING;

// Resource names
const DATA_SOURCE_NAME = 'errorhandling-datasource';
const INDEX_NAME = 'errorhandling-index';
const INDEXER_NAME = 'errorhandling-indexer';

class ErrorHandlingExample {
    constructor() {
        this.validateConfiguration();
        
        const credential = new AzureKeyCredential(SEARCH_API_KEY);
        this.indexClient = new SearchIndexClient(SEARCH_ENDPOINT, credential);
        this.indexerClient = new SearchIndexerClient(SEARCH_ENDPOINT, credential);
        this.searchClient = new SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential);
        
        // Error tracking
        this.errorLog = [];
        this.retryAttempts = new Map();
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

    demonstrateErrorTypes() {
        console.log('\n❌ Common Indexer Error Types');
        console.log('='.repeat(35));

        const errorTypes = [
            {
                category: 'Data Source Errors',
                errors: [
                    {
                        type: 'Connection Timeout',
                        description: 'Unable to connect to data source',
                        causes: ['Network issues', 'Firewall blocking', 'Service unavailable'],
                        handling: 'Retry with exponential backoff'
                    },
                    {
                        type: 'Authentication Failed',
                        description: 'Invalid credentials or permissions',
                        causes: ['Expired credentials', 'Insufficient permissions', 'Wrong connection string'],
                        handling: 'Check credentials and permissions'
                    },
                    {
                        type: 'Data Source Not Found',
                        description: 'Specified table/container does not exist',
                        causes: ['Incorrect name', 'Resource deleted', 'Permission issues'],
                        handling: 'Verify resource exists and is accessible'
                    }
                ]
            },
            {
                category: 'Data Processing Errors',
                errors: [
                    {
                        type: 'Field Mapping Error',
                        description: 'Unable to map source field to target field',
                        causes: ['Field not found', 'Type mismatch', 'Invalid mapping function'],
                        handling: 'Review and fix field mappings'
                    },
                    {
                        type: 'Document Parsing Error',
                        description: 'Unable to parse document content',
                        causes: ['Corrupted file', 'Unsupported format', 'Encoding issues'],
                        handling: 'Skip problematic documents or fix at source'
                    },
                    {
                        type: 'Data Type Conversion Error',
                        description: 'Cannot convert data to target type',
                        causes: ['Invalid format', 'Null values', 'Out of range values'],
                        handling: 'Use mapping functions or handle nulls'
                    }
                ]
            },
            {
                category: 'Index Errors',
                errors: [
                    {
                        type: 'Document Too Large',
                        description: 'Document exceeds size limits',
                        causes: ['Large text content', 'Many fields', 'Large collections'],
                        handling: 'Split document or reduce content'
                    },
                    {
                        type: 'Key Field Missing',
                        description: 'Required key field is null or empty',
                        causes: ['Source data issue', 'Mapping problem', 'Field not populated'],
                        handling: 'Ensure key field is always populated'
                    },
                    {
                        type: 'Index Schema Mismatch',
                        description: 'Document structure doesn\'t match index',
                        causes: ['Schema changes', 'Wrong field types', 'Missing required fields'],
                        handling: 'Update index schema or fix mappings'
                    }
                ]
            }
        ];

        errorTypes.forEach(category => {
            console.log(`\n📋 ${category.category}:`);
            category.errors.forEach(error => {
                console.log(`\n   ❌ ${error.type}`);
                console.log(`      Description: ${error.description}`);
                console.log(`      Common Causes: ${error.causes.join(', ')}`);
                console.log(`      Handling: ${error.handling}`);
            });
        });
    }

    async createRobustDataSource() {
        console.log('\n🔗 Creating data source with error handling...');

        if (!SQL_CONNECTION_STRING) {
            console.log('⚠️ SQL connection not available, creating mock configuration');
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
            description: 'SQL data source with robust error handling configuration'
        };

        try {
            const result = await this.createWithRetry(
                () => this.indexerClient.createOrUpdateDataSourceConnection(dataSource),
                'data source creation',
                3
            );
            
            console.log(`✅ Data source '${DATA_SOURCE_NAME}' created successfully`);
            return result;
        } catch (error) {
            this.logError('DataSource Creation', error);
            throw error;
        }
    }

    async createRobustIndex() {
        console.log('\n📊 Creating index with error-resilient schema...');

        const fields = [
            { name: 'id', type: 'Edm.String', key: true, searchable: false },
            { name: 'hotelName', type: 'Edm.String', searchable: true, sortable: true },
            { name: 'description', type: 'Edm.String', searchable: true, analyzer: 'en.lucene' },
            { name: 'category', type: 'Edm.String', filterable: true, facetable: true },
            { name: 'rating', type: 'Edm.Double', filterable: true, sortable: true, facetable: true },
            { name: 'lastModified', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            // Error tracking fields
            { name: 'processingErrors', type: 'Collection(Edm.String)', searchable: false },
            { name: 'lastProcessed', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: 'processingAttempts', type: 'Edm.Int32', filterable: true }
        ];

        const index = { name: INDEX_NAME, fields };

        try {
            const result = await this.createWithRetry(
                () => this.indexClient.createOrUpdateIndex(index),
                'index creation',
                3
            );
            
            console.log(`✅ Index '${INDEX_NAME}' created successfully`);
            console.log(`   Total Fields: ${result.fields.length}`);
            return result;
        } catch (error) {
            this.logError('Index Creation', error);
            throw error;
        }
    }

    async createRobustIndexer() {
        console.log('\n⚙️ Creating indexer with comprehensive error handling...');

        const indexer = {
            name: INDEXER_NAME,
            dataSourceName: DATA_SOURCE_NAME,
            targetIndexName: INDEX_NAME,
            description: 'Indexer with robust error handling configuration',
            parameters: {
                // Error handling configuration
                batchSize: 10, // Smaller batches for better error isolation
                maxFailedItems: 50, // Allow some failures
                maxFailedItemsPerBatch: 5, // Limit failures per batch
                
                // Processing configuration
                configuration: {
                    parsingMode: 'default',
                    failOnUnsupportedContentType: false,
                    failOnUnprocessableDocument: false,
                    indexedFileNameExtensions: '.pdf,.docx,.txt,.html',
                    excludedFileNameExtensions: '.png,.jpg,.gif'
                }
            },
            fieldMappings: [
                { sourceFieldName: 'id', targetFieldName: 'id' },
                { sourceFieldName: 'hotel_name', targetFieldName: 'hotelName' },
                { sourceFieldName: 'description', targetFieldName: 'description' },
                { sourceFieldName: 'category', targetFieldName: 'category' },
                { sourceFieldName: 'rating', targetFieldName: 'rating' },
                { sourceFieldName: 'last_modified', targetFieldName: 'lastModified' }
            ]
        };

        try {
            const result = await this.createWithRetry(
                () => this.indexerClient.createOrUpdateIndexer(indexer),
                'indexer creation',
                3
            );
            
            console.log(`✅ Indexer '${INDEXER_NAME}' created successfully`);
            console.log(`   Batch Size: ${result.parameters?.batchSize}`);
            console.log(`   Max Failed Items: ${result.parameters?.maxFailedItems}`);
            console.log(`   Max Failed Items Per Batch: ${result.parameters?.maxFailedItemsPerBatch}`);
            return result;
        } catch (error) {
            this.logError('Indexer Creation', error);
            throw error;
        }
    }

    async createWithRetry(operation, operationName, maxRetries = 3) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.log(`   Attempt ${attempt}/${maxRetries} for ${operationName}...`);
                const result = await operation();
                
                if (attempt > 1) {
                    console.log(`   ✅ ${operationName} succeeded on attempt ${attempt}`);
                }
                
                return result;
            } catch (error) {
                lastError = error;
                console.log(`   ❌ Attempt ${attempt} failed: ${error.message}`);
                
                if (attempt < maxRetries) {
                    const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
                    console.log(`   ⏳ Waiting ${delay}ms before retry...`);
                    await this.sleep(delay);
                }
            }
        }
        
        throw new Error(`${operationName} failed after ${maxRetries} attempts. Last error: ${lastError.message}`);
    }

    async runIndexerWithErrorHandling() {
        console.log('\n🚀 Running indexer with error monitoring...');

        try {
            // Start the indexer
            await this.indexerClient.runIndexer(INDEXER_NAME);
            console.log('✅ Indexer started successfully');

            // Monitor execution with error tracking
            await this.monitorIndexerWithErrorHandling(INDEXER_NAME, 3);

        } catch (error) {
            this.logError('Indexer Execution', error);
            console.log(`❌ Error running indexer: ${error.message}`);
            
            // Attempt recovery
            await this.attemptIndexerRecovery(INDEXER_NAME);
        }
    }

    async monitorIndexerWithErrorHandling(indexerName, durationMinutes) {
        console.log(`\n📊 Monitoring ${indexerName} with error tracking...`);
        console.log(`   Duration: ${durationMinutes} minutes`);
        console.log('='.repeat(50));

        const startTime = Date.now();
        const endTime = startTime + (durationMinutes * 60 * 1000);
        let lastStatus = null;
        let errorCount = 0;
        let warningCount = 0;

        while (Date.now() < endTime) {
            try {
                const status = await this.indexerClient.getIndexerStatus(indexerName);
                const currentTime = new Date().toLocaleTimeString();

                // Check for status changes
                if (!lastStatus || this.hasStatusChanged(lastStatus, status)) {
                    console.log(`\n⏰ ${currentTime} - Status Update:`);
                    console.log(`   Status: ${status.status}`);
                    
                    if (status.lastResult) {
                        const result = status.lastResult;
                        console.log(`   Items Processed: ${result.itemCount || 0}`);
                        console.log(`   Items Failed: ${result.failedItemCount || 0}`);
                        
                        // Track errors
                        if (result.errors && result.errors.length > 0) {
                            errorCount += result.errors.length;
                            console.log(`   🔴 New Errors: ${result.errors.length}`);
                            
                            // Log first few errors
                            result.errors.slice(0, 3).forEach((error, index) => {
                                console.log(`     ${index + 1}. ${error.errorMessage}`);
                                this.logError('Indexer Processing', error);
                            });
                            
                            if (result.errors.length > 3) {
                                console.log(`     ... and ${result.errors.length - 3} more errors`);
                            }
                        }
                        
                        // Track warnings
                        if (result.warnings && result.warnings.length > 0) {
                            warningCount += result.warnings.length;
                            console.log(`   🟡 New Warnings: ${result.warnings.length}`);
                            
                            result.warnings.slice(0, 2).forEach((warning, index) => {
                                console.log(`     ${index + 1}. ${warning.message}`);
                            });
                        }
                        
                        // Calculate processing rate
                        if (result.itemCount && result.itemCount > 0 && result.endTime && result.startTime) {
                            const duration = (new Date(result.endTime) - new Date(result.startTime)) / 1000;
                            if (duration > 0) {
                                const rate = result.itemCount / duration;
                                console.log(`   📊 Processing Rate: ${rate.toFixed(2)} items/sec`);
                            }
                        }
                    }
                    
                    lastStatus = status;
                }

                // Check for critical error conditions
                if (status.status === 'error') {
                    console.log('\n🚨 Critical Error Detected!');
                    await this.handleCriticalError(indexerName, status);
                    break;
                }

                // Check error thresholds
                if (errorCount > 20) {
                    console.log('\n⚠️ Error threshold exceeded, investigating...');
                    await this.investigateErrors(indexerName);
                }

                if (status.status === 'success') {
                    console.log('\n🎉 Indexer completed successfully!');
                    break;
                }

                await this.sleep(10000); // Check every 10 seconds
            } catch (error) {
                console.log(`❌ Error monitoring indexer: ${error.message}`);
                this.logError('Monitoring', error);
                break;
            }
        }

        // Summary
        console.log('\n📋 Monitoring Summary:');
        console.log(`   Total Errors: ${errorCount}`);
        console.log(`   Total Warnings: ${warningCount}`);
        console.log(`   Error Log Entries: ${this.errorLog.length}`);
    }

    hasStatusChanged(lastStatus, currentStatus) {
        return lastStatus.status !== currentStatus.status ||
               lastStatus.lastResult?.startTime !== currentStatus.lastResult?.startTime ||
               (lastStatus.lastResult?.errors?.length || 0) !== (currentStatus.lastResult?.errors?.length || 0);
    }

    async handleCriticalError(indexerName, status) {
        console.log('🔧 Handling critical error...');
        
        if (status.lastResult?.errors) {
            console.log('   Analyzing error patterns...');
            
            const errorPatterns = this.analyzeErrorPatterns(status.lastResult.errors);
            console.log('   Error Analysis:');
            
            Object.entries(errorPatterns).forEach(([pattern, count]) => {
                console.log(`     - ${pattern}: ${count} occurrences`);
            });
            
            // Suggest recovery actions
            const recoveryActions = this.suggestRecoveryActions(errorPatterns);
            console.log('   Suggested Recovery Actions:');
            recoveryActions.forEach(action => {
                console.log(`     • ${action}`);
            });
        }
    }

    analyzeErrorPatterns(errors) {
        const patterns = {};
        
        errors.forEach(error => {
            // Categorize errors by type
            let category = 'Unknown';
            
            if (error.errorMessage.includes('timeout')) {
                category = 'Timeout';
            } else if (error.errorMessage.includes('authentication')) {
                category = 'Authentication';
            } else if (error.errorMessage.includes('not found')) {
                category = 'Not Found';
            } else if (error.errorMessage.includes('parsing')) {
                category = 'Parsing';
            } else if (error.errorMessage.includes('mapping')) {
                category = 'Field Mapping';
            }
            
            patterns[category] = (patterns[category] || 0) + 1;
        });
        
        return patterns;
    }

    suggestRecoveryActions(errorPatterns) {
        const actions = [];
        
        if (errorPatterns['Timeout']) {
            actions.push('Reduce batch size to handle timeouts');
            actions.push('Check network connectivity and firewall settings');
        }
        
        if (errorPatterns['Authentication']) {
            actions.push('Verify connection string and credentials');
            actions.push('Check service permissions and access policies');
        }
        
        if (errorPatterns['Not Found']) {
            actions.push('Verify data source configuration');
            actions.push('Check if referenced resources exist');
        }
        
        if (errorPatterns['Parsing']) {
            actions.push('Review document formats and encoding');
            actions.push('Consider excluding problematic file types');
        }
        
        if (errorPatterns['Field Mapping']) {
            actions.push('Review and fix field mapping configuration');
            actions.push('Check source data schema changes');
        }
        
        if (actions.length === 0) {
            actions.push('Review indexer logs for specific error details');
            actions.push('Consider contacting support for assistance');
        }
        
        return actions;
    }

    async attemptIndexerRecovery(indexerName) {
        console.log('\n🔄 Attempting indexer recovery...');
        
        try {
            // Reset the indexer
            console.log('   Resetting indexer...');
            await this.indexerClient.resetIndexer(indexerName);
            console.log('   ✅ Indexer reset successfully');
            
            // Wait a moment
            await this.sleep(5000);
            
            // Try running again with modified parameters
            console.log('   Attempting restart with reduced batch size...');
            
            const indexer = await this.indexerClient.getIndexer(indexerName);
            const modifiedIndexer = {
                ...indexer,
                parameters: {
                    ...indexer.parameters,
                    batchSize: Math.max(1, (indexer.parameters?.batchSize || 10) / 2),
                    maxFailedItems: Math.max(1, (indexer.parameters?.maxFailedItems || 10) / 2)
                }
            };
            
            await this.indexerClient.createOrUpdateIndexer(modifiedIndexer);
            console.log('   ✅ Indexer parameters adjusted for recovery');
            
            await this.indexerClient.runIndexer(indexerName);
            console.log('   ✅ Recovery attempt initiated');
            
        } catch (error) {
            console.log(`   ❌ Recovery failed: ${error.message}`);
            this.logError('Recovery Attempt', error);
        }
    }

    async investigateErrors(indexerName) {
        console.log('🔍 Investigating error patterns...');
        
        try {
            const status = await this.indexerClient.getIndexerStatus(indexerName);
            
            if (status.lastResult?.errors) {
                const recentErrors = status.lastResult.errors.slice(-10);
                
                console.log('   Recent Error Analysis:');
                const errorSummary = {};
                
                recentErrors.forEach(error => {
                    const key = error.key || 'Unknown';
                    if (!errorSummary[key]) {
                        errorSummary[key] = {
                            count: 0,
                            messages: new Set()
                        };
                    }
                    errorSummary[key].count++;
                    errorSummary[key].messages.add(error.errorMessage);
                });
                
                Object.entries(errorSummary).forEach(([key, summary]) => {
                    console.log(`     Document ${key}: ${summary.count} errors`);
                    summary.messages.forEach(message => {
                        console.log(`       - ${message}`);
                    });
                });
            }
        } catch (error) {
            console.log(`   ❌ Error investigation failed: ${error.message}`);
        }
    }

    logError(context, error) {
        const errorEntry = {
            timestamp: new Date().toISOString(),
            context: context,
            message: error.message || error.errorMessage || 'Unknown error',
            details: error
        };
        
        this.errorLog.push(errorEntry);
        
        // Keep only last 100 errors
        if (this.errorLog.length > 100) {
            this.errorLog.shift();
        }
    }

    demonstrateErrorHandlingBestPractices() {
        console.log('\n💡 Error Handling Best Practices');
        console.log('='.repeat(35));

        const bestPractices = [
            {
                category: 'Prevention',
                practices: [
                    'Validate data source connectivity before creating indexers',
                    'Test field mappings with sample data',
                    'Use appropriate batch sizes for your data volume',
                    'Implement data quality checks at the source'
                ]
            },
            {
                category: 'Configuration',
                practices: [
                    'Set reasonable error thresholds (maxFailedItems)',
                    'Use smaller batch sizes for better error isolation',
                    'Configure appropriate timeout values',
                    'Enable detailed logging and monitoring'
                ]
            },
            {
                category: 'Monitoring',
                practices: [
                    'Implement automated error alerting',
                    'Monitor indexer execution patterns',
                    'Track error trends over time',
                    'Set up health check endpoints'
                ]
            },
            {
                category: 'Recovery',
                practices: [
                    'Implement exponential backoff for retries',
                    'Have rollback procedures for failed deployments',
                    'Maintain error logs for troubleshooting',
                    'Plan for manual intervention scenarios'
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

    showErrorLogSummary() {
        console.log('\n📊 Error Log Summary');
        console.log('='.repeat(20));
        
        if (this.errorLog.length === 0) {
            console.log('   No errors logged during this session');
            return;
        }
        
        console.log(`   Total Errors: ${this.errorLog.length}`);
        
        // Group by context
        const contextSummary = {};
        this.errorLog.forEach(error => {
            contextSummary[error.context] = (contextSummary[error.context] || 0) + 1;
        });
        
        console.log('   Errors by Context:');
        Object.entries(contextSummary).forEach(([context, count]) => {
            console.log(`     ${context}: ${count}`);
        });
        
        // Show recent errors
        console.log('\n   Recent Errors:');
        this.errorLog.slice(-5).forEach((error, index) => {
            console.log(`     ${index + 1}. [${error.context}] ${error.message}`);
        });
    }

    async cleanup() {
        console.log('\n🧹 Cleaning up resources...');
        
        try {
            await this.indexerClient.deleteIndexer(INDEXER_NAME);
            console.log(`   ✅ Deleted indexer: ${INDEXER_NAME}`);
        } catch (error) {
            console.log(`   ⚠️ Warning deleting indexer: ${error.message}`);
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
        console.log('🚀 Error Handling Example');
        console.log('='.repeat(50));

        try {
            // Demonstrate error concepts
            this.demonstrateErrorTypes();

            // Create resources with error handling
            const dataSource = await this.createRobustDataSource();
            const index = await this.createRobustIndex();
            
            if (dataSource) {
                const indexer = await this.createRobustIndexer();
                await this.runIndexerWithErrorHandling();
            } else {
                console.log('\n⚠️ Skipping indexer execution due to missing data source');
            }

            // Best practices and summary
            this.demonstrateErrorHandlingBestPractices();
            this.showErrorLogSummary();

            console.log('\n✅ Error handling example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Implement retry logic with exponential backoff');
            console.log('- Set appropriate error thresholds and batch sizes');
            console.log('- Monitor indexer execution and track error patterns');
            console.log('- Have recovery procedures for critical failures');
            console.log('- Log errors systematically for troubleshooting');

            await this.cleanup();

        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            this.logError('Example Execution', error);
            this.showErrorLogSummary();
            throw error;
        }
    }
}

async function main() {
    const example = new ErrorHandlingExample();
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

module.exports = ErrorHandlingExample;