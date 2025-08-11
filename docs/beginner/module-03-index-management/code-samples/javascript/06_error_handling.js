#!/usr/bin/env node
/**
 * Module 3: Index Management - Error Handling and Troubleshooting (JavaScript)
 * ===========================================================================
 * 
 * This example demonstrates comprehensive error handling patterns and troubleshooting
 * techniques for Azure AI Search index management operations using JavaScript.
 * 
 * Learning Objectives:
 * - Handle common error scenarios gracefully
 * - Implement retry strategies with exponential backoff
 * - Validate inputs and handle edge cases
 * - Provide meaningful error messages and recovery options
 * - Debug and troubleshoot index management issues
 * 
 * Prerequisites:
 * - Completed previous examples (01-05)
 * - Understanding of index operations and performance
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

const { SearchIndexClient, SearchClient, AzureKeyCredential } = require('@azure/search-documents');
const { RestError } = require('@azure/core-rest-pipeline');
require('dotenv').config();

class ErrorHandlingManager {
    /**
     * Initialize the error handling manager
     */
    constructor() {
        this.endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
        this.adminKey = process.env.AZURE_SEARCH_ADMIN_KEY;
        
        if (!this.endpoint || !this.adminKey) {
            throw new Error('Missing required environment variables: AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_ADMIN_KEY');
        }
        
        this.indexClient = null;
        this.searchClient = null;
        this.maxRetries = 3;
        this.baseDelayMs = 1000;
    }

    /**
     * Create and validate search clients with error handling
     */
    async createClientsWithErrorHandling() {
        console.log('🔍 Creating Search Clients with Error Handling...');
        
        try {
            // Validate endpoint format
            if (!this.endpoint.startsWith('https://') || !this.endpoint.includes('.search.windows.net')) {
                throw new Error('Invalid endpoint format. Expected: https://[service-name].search.windows.net');
            }
            
            // Validate API key format
            if (!this.adminKey || this.adminKey.length < 32) {
                throw new Error('Invalid API key format. Admin key should be at least 32 characters long');
            }
            
            this.indexClient = new SearchIndexClient(
                this.endpoint,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Test connection with retry logic
            const stats = await this.executeWithRetry(
                () => this.indexClient.getServiceStatistics(),
                'Getting service statistics'
            );
            
            console.log('✅ Connected to Azure AI Search service');
            console.log(`   Storage used: ${stats.storageSize.toLocaleString()} bytes`);
            console.log(`   Document count: ${stats.documentCount.toLocaleString()}`);
            
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to create clients: ${this.formatError(error)}`);
            this.provideTroubleshootingTips(error);
            return false;
        }
    }

    /**
     * Create a sample index with comprehensive error handling
     */
    async createIndexWithErrorHandling() {
        console.log('🏗️  Creating index with error handling...');
        
        const indexName = 'error-handling-demo-js';
        
        const indexDefinition = {
            name: indexName,
            fields: [
                { name: 'id', type: 'Edm.String', key: true },
                { name: 'title', type: 'Edm.String', searchable: true },
                { name: 'content', type: 'Edm.String', searchable: true },
                { name: 'category', type: 'Edm.String', filterable: true, facetable: true },
                { name: 'author', type: 'Edm.String', filterable: true },
                { name: 'publishedDate', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
                { name: 'rating', type: 'Edm.Double', filterable: true, sortable: true },
                { name: 'viewCount', type: 'Edm.Int32', filterable: true, sortable: true },
                { name: 'tags', type: 'Collection(Edm.String)', filterable: true, facetable: true },
                { name: 'isPublished', type: 'Edm.Boolean', filterable: true }
            ]
        };
        
        try {
            // Validate index definition
            this.validateIndexDefinition(indexDefinition);
            
            const result = await this.executeWithRetry(
                () => this.indexClient.createOrUpdateIndex(indexDefinition),
                'Creating index'
            );
            
            // Create search client for this index
            this.searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            console.log(`✅ Index '${result.name}' created successfully`);
            return indexName;
            
        } catch (error) {
            console.error(`❌ Failed to create index: ${this.formatError(error)}`);
            this.provideTroubleshootingTips(error);
            return null;
        }
    }

    /**
     * Demonstrate document upload with error handling
     */
    async uploadDocumentsWithErrorHandling() {
        console.log('📤 Document Upload with Error Handling...');
        
        try {
            // Generate sample documents with some intentional issues
            const documents = this.generateSampleDocumentsWithIssues();
            
            console.log(`   Attempting to upload ${documents.length} documents...`);
            
            const result = await this.executeWithRetry(
                () => this.searchClient.uploadDocuments(documents),
                'Uploading documents'
            );
            
            // Analyze results
            const successful = result.results.filter(r => r.succeeded);
            const failed = result.results.filter(r => !r.succeeded);
            
            console.log(`✅ Upload completed:`);
            console.log(`   Successful: ${successful.length}`);
            console.log(`   Failed: ${failed.length}`);
            
            // Handle failed documents
            if (failed.length > 0) {
                console.log('\n❌ Failed documents:');
                for (const failure of failed) {
                    console.log(`   - Document ${failure.key}: ${failure.errorMessage}`);
                    this.suggestDocumentFix(failure);
                }
                
                // Attempt to fix and retry failed documents
                await this.retryFailedDocuments(failed, documents);
            }
            
            return successful.length > 0;
            
        } catch (error) {
            console.error(`❌ Document upload failed: ${this.formatError(error)}`);
            this.provideTroubleshootingTips(error);
            return false;
        }
    }

    /**
     * Demonstrate search operations with error handling
     */
    async searchWithErrorHandling() {
        console.log('🔍 Search Operations with Error Handling...');
        
        const testQueries = [
            { query: 'azure search', description: 'Valid simple query' },
            { query: 'title:azure AND content:search', description: 'Valid field-specific query' },
            { query: 'invalid_field:test', description: 'Invalid field name' },
            { query: 'title:azure AND (', description: 'Malformed query syntax' },
            { query: '', description: 'Empty query' }
        ];
        
        for (const testQuery of testQueries) {
            console.log(`\n🧪 Testing: ${testQuery.description}`);
            console.log(`   Query: "${testQuery.query}"`);
            
            try {
                const searchOptions = {
                    top: 5,
                    includeTotalCount: true,
                    select: ['id', 'title', 'category']
                };
                
                const results = await this.executeWithRetry(
                    () => this.searchClient.search(testQuery.query, searchOptions),
                    `Searching with query: ${testQuery.query}`
                );
                
                console.log(`   ✅ Success: Found ${results.count} results`);
                
                let resultCount = 0;
                for await (const result of results.results) {
                    if (resultCount < 2) { // Show first 2 results
                        console.log(`     - ${result.document.id}: ${result.document.title}`);
                        resultCount++;
                    }
                }
                
            } catch (error) {
                console.log(`   ❌ Failed: ${this.formatError(error)}`);
                this.suggestQueryFix(testQuery.query, error);
            }
        }
    }

    /**
     * Demonstrate filter operations with error handling
     */
    async filterWithErrorHandling() {
        console.log('\n🔍 Filter Operations with Error Handling...');
        
        const testFilters = [
            { filter: "category eq 'Technology'", description: 'Valid string filter' },
            { filter: "rating gt 4.0", description: 'Valid numeric filter' },
            { filter: "publishedDate ge 2024-01-01T00:00:00Z", description: 'Valid date filter' },
            { filter: "invalid_field eq 'test'", description: 'Invalid field name' },
            { filter: "category eq Technology", description: 'Missing quotes in string filter' },
            { filter: "rating gt 'invalid'", description: 'Invalid data type' }
        ];
        
        for (const testFilter of testFilters) {
            console.log(`\n🧪 Testing: ${testFilter.description}`);
            console.log(`   Filter: ${testFilter.filter}`);
            
            try {
                const results = await this.executeWithRetry(
                    () => this.searchClient.search('*', {
                        filter: testFilter.filter,
                        top: 3,
                        select: ['id', 'title', 'category', 'rating']
                    }),
                    `Filtering with: ${testFilter.filter}`
                );
                
                console.log(`   ✅ Success: Found ${results.count} results`);
                
            } catch (error) {
                console.log(`   ❌ Failed: ${this.formatError(error)}`);
                this.suggestFilterFix(testFilter.filter, error);
            }
        }
    }

    /**
     * Execute operation with retry logic and exponential backoff
     */
    async executeWithRetry(operation, operationName, maxRetries = this.maxRetries) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;
                
                if (attempt === maxRetries) {
                    throw error;
                }
                
                // Check if error is retryable
                if (!this.isRetryableError(error)) {
                    throw error;
                }
                
                const delay = this.calculateBackoffDelay(attempt);
                console.log(`   ⚠️  ${operationName} failed (attempt ${attempt}/${maxRetries}). Retrying in ${delay}ms...`);
                console.log(`      Error: ${this.formatError(error)}`);
                
                await this.sleep(delay);
            }
        }
        
        throw lastError;
    }

    /**
     * Determine if an error is retryable
     */
    isRetryableError(error) {
        if (error instanceof RestError) {
            // Retry on server errors and rate limiting
            return error.statusCode >= 500 || error.statusCode === 429;
        }
        
        // Retry on network errors
        if (error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT') {
            return true;
        }
        
        return false;
    }

    /**
     * Calculate exponential backoff delay
     */
    calculateBackoffDelay(attempt) {
        const jitter = Math.random() * 0.1; // Add 10% jitter
        return Math.floor(this.baseDelayMs * Math.pow(2, attempt - 1) * (1 + jitter));
    }

    /**
     * Sleep for specified milliseconds
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Format error messages for better readability
     */
    formatError(error) {
        if (error instanceof RestError) {
            return `HTTP ${error.statusCode}: ${error.message}`;
        }
        
        if (error.code) {
            return `${error.code}: ${error.message}`;
        }
        
        return error.message || 'Unknown error';
    }

    /**
     * Provide troubleshooting tips based on error type
     */
    provideTroubleshootingTips(error) {
        console.log('\n💡 Troubleshooting Tips:');
        
        if (error instanceof RestError) {
            switch (error.statusCode) {
                case 401:
                    console.log('   - Check your API key is correct and has admin permissions');
                    console.log('   - Ensure you are using the admin key, not a query key');
                    break;
                case 403:
                    console.log('   - Verify your API key has the required permissions');
                    console.log('   - Check if your service is in a restricted region');
                    break;
                case 404:
                    console.log('   - Verify the service endpoint URL is correct');
                    console.log('   - Check if the index name exists');
                    break;
                case 429:
                    console.log('   - You are being rate limited. Reduce request frequency');
                    console.log('   - Consider upgrading your service tier for higher limits');
                    break;
                case 500:
                case 502:
                case 503:
                    console.log('   - Server error. Try again in a few moments');
                    console.log('   - Check Azure service health status');
                    break;
                default:
                    console.log(`   - HTTP ${error.statusCode} error occurred`);
                    console.log('   - Check the Azure AI Search documentation for details');
            }
        } else if (error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT') {
            console.log('   - Network connectivity issue');
            console.log('   - Check your internet connection');
            console.log('   - Verify firewall settings allow HTTPS traffic');
        } else {
            console.log('   - Check your configuration and try again');
            console.log('   - Enable detailed logging for more information');
        }
    }

    /**
     * Validate index definition
     */
    validateIndexDefinition(indexDefinition) {
        if (!indexDefinition.name) {
            throw new Error('Index name is required');
        }
        
        if (!/^[a-z0-9-]+$/.test(indexDefinition.name)) {
            throw new Error('Index name must contain only lowercase letters, numbers, and hyphens');
        }
        
        if (!indexDefinition.fields || indexDefinition.fields.length === 0) {
            throw new Error('Index must have at least one field');
        }
        
        const keyFields = indexDefinition.fields.filter(f => f.key);
        if (keyFields.length !== 1) {
            throw new Error('Index must have exactly one key field');
        }
        
        console.log('✅ Index definition validation passed');
    }

    /**
     * Generate sample documents with some intentional issues for testing
     */
    generateSampleDocumentsWithIssues() {
        return [
            // Valid document
            {
                id: 'doc-1',
                title: 'Valid Document',
                content: 'This is a valid document with all required fields.',
                category: 'Technology',
                author: 'John Doe',
                publishedDate: '2024-02-10T10:00:00Z',
                rating: 4.5,
                viewCount: 100,
                tags: ['technology', 'valid'],
                isPublished: true
            },
            // Document with missing required field (will be handled by schema)
            {
                id: 'doc-2',
                title: 'Document with Missing Fields',
                content: 'This document is missing some optional fields.',
                category: 'Technology',
                author: 'Jane Smith',
                publishedDate: '2024-02-11T10:00:00Z',
                rating: 4.0,
                viewCount: 50,
                isPublished: true
                // Missing tags field - this is OK as it's optional
            },
            // Document with invalid date format
            {
                id: 'doc-3',
                title: 'Document with Invalid Date',
                content: 'This document has an invalid date format.',
                category: 'Technology',
                author: 'Bob Johnson',
                publishedDate: 'invalid-date-format', // This will cause an error
                rating: 3.5,
                viewCount: 75,
                tags: ['technology', 'error'],
                isPublished: true
            },
            // Valid document
            {
                id: 'doc-4',
                title: 'Another Valid Document',
                content: 'This is another valid document for testing.',
                category: 'Science',
                author: 'Alice Brown',
                publishedDate: '2024-02-12T10:00:00Z',
                rating: 4.8,
                viewCount: 200,
                tags: ['science', 'valid'],
                isPublished: true
            }
        ];
    }

    /**
     * Suggest fixes for document upload failures
     */
    suggestDocumentFix(failure) {
        console.log(`   💡 Suggested fix for ${failure.key}:`);
        
        if (failure.errorMessage.includes('date')) {
            console.log('      - Check date format. Use ISO 8601 format: YYYY-MM-DDTHH:mm:ssZ');
        } else if (failure.errorMessage.includes('required')) {
            console.log('      - Ensure all required fields are present');
        } else if (failure.errorMessage.includes('type')) {
            console.log('      - Check data types match the index schema');
        } else {
            console.log('      - Review the document structure and field values');
        }
    }

    /**
     * Suggest fixes for query failures
     */
    suggestQueryFix(query, error) {
        console.log('   💡 Suggested fixes:');
        
        if (error.message.includes('field')) {
            console.log('      - Check field names exist in the index schema');
            console.log('      - Verify field names are spelled correctly');
        } else if (error.message.includes('syntax')) {
            console.log('      - Check query syntax for balanced parentheses');
            console.log('      - Verify operator usage (AND, OR, NOT)');
        } else if (query === '') {
            console.log('      - Use "*" for empty queries to search all documents');
        } else {
            console.log('      - Simplify the query and test incrementally');
        }
    }

    /**
     * Suggest fixes for filter failures
     */
    suggestFilterFix(filter, error) {
        console.log('   💡 Suggested fixes:');
        
        if (error.message.includes('field')) {
            console.log('      - Verify the field exists and is filterable');
        } else if (error.message.includes('quote')) {
            console.log('      - Enclose string values in single quotes');
        } else if (error.message.includes('type')) {
            console.log('      - Check data type compatibility (string, number, date)');
        } else {
            console.log('      - Review OData filter syntax documentation');
        }
    }

    /**
     * Retry failed documents with fixes
     */
    async retryFailedDocuments(failures, originalDocuments) {
        console.log('\n🔄 Attempting to fix and retry failed documents...');
        
        const documentsToRetry = [];
        
        for (const failure of failures) {
            const originalDoc = originalDocuments.find(doc => doc.id === failure.key);
            if (originalDoc) {
                // Attempt to fix common issues
                const fixedDoc = { ...originalDoc };
                
                if (failure.errorMessage.includes('date')) {
                    // Fix invalid date format
                    fixedDoc.publishedDate = '2024-02-10T10:00:00Z';
                    console.log(`   🔧 Fixed date format for document ${failure.key}`);
                }
                
                documentsToRetry.push(fixedDoc);
            }
        }
        
        if (documentsToRetry.length > 0) {
            try {
                const retryResult = await this.searchClient.uploadDocuments(documentsToRetry);
                const retrySuccessful = retryResult.results.filter(r => r.succeeded).length;
                const retryFailed = retryResult.results.length - retrySuccessful;
                
                console.log(`   ✅ Retry completed: ${retrySuccessful} successful, ${retryFailed} failed`);
                
            } catch (error) {
                console.log(`   ❌ Retry failed: ${this.formatError(error)}`);
            }
        }
    }

    /**
     * Demonstrate comprehensive error logging
     */
    async demonstrateErrorLogging() {
        console.log('\n📝 Error Logging Demonstration...');
        
        const errorLogger = {
            logError: (operation, error, context = {}) => {
                const timestamp = new Date().toISOString();
                const errorInfo = {
                    timestamp,
                    operation,
                    error: this.formatError(error),
                    context,
                    stackTrace: error.stack
                };
                
                console.log(`   📋 Error Log Entry:`);
                console.log(`      Timestamp: ${errorInfo.timestamp}`);
                console.log(`      Operation: ${errorInfo.operation}`);
                console.log(`      Error: ${errorInfo.error}`);
                console.log(`      Context: ${JSON.stringify(errorInfo.context, null, 2)}`);
            }
        };
        
        // Simulate various error scenarios
        const errorScenarios = [
            {
                name: 'Invalid Index Name',
                operation: async () => {
                    await this.indexClient.createOrUpdateIndex({
                        name: 'Invalid Index Name!', // Invalid characters
                        fields: [{ name: 'id', type: 'Edm.String', key: true }]
                    });
                },
                context: { indexName: 'Invalid Index Name!' }
            },
            {
                name: 'Missing Key Field',
                operation: async () => {
                    await this.indexClient.createOrUpdateIndex({
                        name: 'test-index',
                        fields: [{ name: 'title', type: 'Edm.String', searchable: true }] // No key field
                    });
                },
                context: { indexName: 'test-index' }
            }
        ];
        
        for (const scenario of errorScenarios) {
            console.log(`\n🧪 Testing: ${scenario.name}`);
            try {
                await scenario.operation();
                console.log('   ✅ Unexpectedly succeeded');
            } catch (error) {
                errorLogger.logError(scenario.name, error, scenario.context);
            }
        }
    }

    /**
     * Get error handling statistics
     */
    async getErrorHandlingStatistics() {
        console.log('\n📊 Error Handling Statistics:');
        
        try {
            const docCount = await this.searchClient.getDocumentCount();
            console.log(`   Total documents: ${docCount}`);
            
            // Test basic connectivity
            const testResult = await this.searchClient.search('*', { top: 1 });
            console.log('   ✅ Basic search functionality working');
            
        } catch (error) {
            console.error(`❌ Failed to get statistics: ${this.formatError(error)}`);
        }
    }
}

/**
 * Main program demonstrating error handling
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Module 3: Error Handling and Troubleshooting Example (JavaScript)');
    console.log('='.repeat(60));
    
    // Initialize the error handling manager
    let manager;
    try {
        manager = new ErrorHandlingManager();
    } catch (error) {
        console.error(`❌ Configuration error: ${error.message}`);
        return;
    }
    
    // Create clients with error handling
    if (!(await manager.createClientsWithErrorHandling())) {
        console.error('❌ Failed to create clients. Exiting.');
        return;
    }
    
    // Create sample index with error handling
    const indexName = await manager.createIndexWithErrorHandling();
    if (!indexName) {
        console.error('❌ Failed to create sample index. Exiting.');
        return;
    }
    
    console.log(`\n🎯 Running error handling demonstrations on index '${indexName}'...`);
    
    // Run demonstrations
    const demonstrations = [
        { name: 'Document Upload Error Handling', func: () => manager.uploadDocumentsWithErrorHandling() },
        { name: 'Search Error Handling', func: () => manager.searchWithErrorHandling() },
        { name: 'Filter Error Handling', func: () => manager.filterWithErrorHandling() },
        { name: 'Error Logging', func: () => manager.demonstrateErrorLogging() }
    ];
    
    for (const demo of demonstrations) {
        console.log(`\n${'='.repeat(20)} ${demo.name} ${'='.repeat(20)}`);
        try {
            await demo.func();
            console.log(`✅ ${demo.name} completed successfully`);
        } catch (error) {
            console.error(`❌ ${demo.name} failed: ${manager.formatError(error)}`);
        }
        
        // Brief pause between demonstrations
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Show current statistics
    console.log(`\n${'='.repeat(20)} Current Statistics ${'='.repeat(20)}`);
    await manager.getErrorHandlingStatistics();
    
    console.log('\n' + '='.repeat(60));
    console.log('Example completed!');
    console.log('='.repeat(60));
    
    console.log('\n📚 What you learned:');
    console.log('✅ How to handle common error scenarios gracefully');
    console.log('✅ How to implement retry strategies with exponential backoff');
    console.log('✅ How to validate inputs and handle edge cases');
    console.log('✅ How to provide meaningful error messages and recovery options');
    console.log('✅ How to debug and troubleshoot index management issues');
    
    console.log('\n🚀 Next steps:');
    console.log('1. Implement comprehensive error handling in your applications');
    console.log('2. Set up monitoring and alerting for production systems');
    console.log('3. Create error recovery procedures for your team');
    console.log('4. Move on to Module 4: Advanced Search Techniques');
}

// Run the example
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { ErrorHandlingManager };