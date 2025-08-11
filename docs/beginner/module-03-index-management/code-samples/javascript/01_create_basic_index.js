#!/usr/bin/env node
/**
 * Module 3: Index Management - Basic Index Creation (JavaScript)
 * =============================================================
 * 
 * This example demonstrates the fundamentals of creating a search index in Azure AI Search
 * using the JavaScript SDK. You'll learn how to define field types, set attributes, and
 * create your first index with proper error handling.
 * 
 * Learning Objectives:
 * - Create SearchIndexClient with proper authentication
 * - Define field types and attributes in JavaScript
 * - Create a basic index schema
 * - Handle index creation responses
 * - Validate index creation
 * 
 * Prerequisites:
 * - Node.js 14.x or later
 * - Azure AI Search service with admin access
 * - Environment variables configured
 * - @azure/search-documents package installed
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

const { SearchIndexClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class BasicIndexCreator {
    /**
     * Initialize the index creator with Azure AI Search credentials
     */
    constructor() {
        this.endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
        this.adminKey = process.env.AZURE_SEARCH_ADMIN_KEY;
        this.indexClient = null;
        
        if (!this.endpoint || !this.adminKey) {
            throw new Error('Missing required environment variables: AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_ADMIN_KEY');
        }
    }
    
    /**
     * Create and validate the SearchIndexClient
     */
    async createIndexClient() {
        console.log('🔍 Creating SearchIndexClient...');
        
        try {
            this.indexClient = new SearchIndexClient(
                this.endpoint,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Test connection by getting service statistics
            const stats = await this.indexClient.getServiceStatistics();
            console.log('✅ Connected to Azure AI Search service');
            console.log(`   Storage used: ${stats.storageSize.toLocaleString()} bytes`);
            console.log(`   Document count: ${stats.documentCount.toLocaleString()}`);
            
            return true;
            
        } catch (error) {
            if (error.statusCode === 403) {
                console.log('❌ Access denied - check your admin API key');
            } else {
                console.log(`❌ HTTP error ${error.statusCode}: ${error.message}`);
            }
            return false;
        }
    }
    
    /**
     * Define a basic index schema for a blog application
     */
    defineBasicSchema() {
        console.log('📋 Defining Basic Index Schema...');
        
        // Define fields with different types and attributes
        const fields = [
            // Key field (required) - unique identifier for each document
            {
                name: 'id',
                type: 'Edm.String',
                key: true,
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Searchable text fields - enable full-text search
            {
                name: 'title',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'  // English language analyzer
            },
            
            {
                name: 'content',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'
            },
            
            // Simple fields for exact matching and filtering
            {
                name: 'author',
                type: 'Edm.String',
                searchable: false,
                filterable: true,  // Enable filtering by author
                sortable: false,
                facetable: true,   // Enable faceting for navigation
                retrievable: true
            },
            
            {
                name: 'category',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Date field - filterable and sortable
            {
                name: 'publishedDate',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Collection field for multiple values
            {
                name: 'tags',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Numeric fields
            {
                name: 'rating',
                type: 'Edm.Double',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'viewCount',
                type: 'Edm.Int32',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Boolean field
            {
                name: 'isPublished',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            }
        ];
        
        // Display schema information
        console.log(`✅ Schema defined with ${fields.length} fields:`);
        console.log(`${'Field Name'.padEnd(15)} | ${'Type'.padEnd(25)} | ${'Attributes'}`);
        console.log('-'.repeat(70));
        
        for (const field of fields) {
            const attributes = [];
            if (field.key) attributes.push('KEY');
            if (field.searchable) attributes.push('searchable');
            if (field.filterable) attributes.push('filterable');
            if (field.sortable) attributes.push('sortable');
            if (field.facetable) attributes.push('facetable');
            
            const attrStr = attributes.length > 0 ? attributes.join(', ') : 'retrievable only';
            console.log(`${field.name.padEnd(15)} | ${field.type.padEnd(25)} | ${attrStr}`);
        }
        
        return fields;
    }
    
    /**
     * Create the search index
     */
    async createIndex(indexName, fields) {
        console.log(`🏗️  Creating index '${indexName}'...`);
        
        try {
            // Create the index object
            const index = {
                name: indexName,
                fields: fields
            };
            
            // Create the index (use createOrUpdateIndex for safety)
            const result = await this.indexClient.createOrUpdateIndex(index);
            
            console.log(`✅ Index '${result.name}' created successfully!`);
            console.log(`   Fields: ${result.fields.length}`);
            console.log(`   Created at: ${new Date().toLocaleString()}`);
            
            return result;
            
        } catch (error) {
            if (error.statusCode === 400) {
                console.log(`❌ Bad request - check index definition: ${error.message}`);
            } else if (error.statusCode === 409) {
                console.log(`❌ Index already exists (this shouldn't happen with createOrUpdateIndex)`);
            } else {
                console.log(`❌ HTTP error ${error.statusCode}: ${error.message}`);
            }
            return null;
        }
    }
    
    /**
     * Validate that the index was created correctly
     */
    async validateIndex(indexName) {
        console.log(`🔍 Validating index '${indexName}'...`);
        
        try {
            // Get the index details
            const index = await this.indexClient.getIndex(indexName);
            
            console.log(`✅ Index validation successful:`);
            console.log(`   Name: ${index.name}`);
            console.log(`   Fields: ${index.fields.length}`);
            
            // Validate key field exists
            const keyFields = index.fields.filter(f => f.key);
            if (keyFields.length === 1) {
                console.log(`   Key field: ${keyFields[0].name}`);
            } else {
                console.log(`   ⚠️  Warning: Found ${keyFields.length} key fields (should be 1)`);
            }
            
            // Count searchable fields
            const searchableFields = index.fields.filter(f => f.searchable);
            console.log(`   Searchable fields: ${searchableFields.length}`);
            
            // Count filterable fields
            const filterableFields = index.fields.filter(f => f.filterable);
            console.log(`   Filterable fields: ${filterableFields.length}`);
            
            return true;
            
        } catch (error) {
            console.log(`❌ Index validation failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Test basic index functionality with a sample document
     */
    async testIndexFunctionality(indexName) {
        console.log(`🧪 Testing index functionality...`);
        
        try {
            const { SearchClient } = require('@azure/search-documents');
            
            // Create search client for document operations
            const searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Create a test document
            const testDocument = {
                id: 'test-doc-1',
                title: 'Test Document for Index Validation',
                content: 'This is a test document to validate that our newly created index is working correctly.',
                author: 'Test Author',
                category: 'Test',
                publishedDate: '2024-02-10T10:00:00Z',
                tags: ['test', 'validation', 'index'],
                rating: 5.0,
                viewCount: 1,
                isPublished: true
            };
            
            // Upload the test document
            const uploadResult = await searchClient.uploadDocuments([testDocument]);
            
            if (uploadResult.results[0].succeeded) {
                console.log('✅ Test document uploaded successfully');
                
                // Wait a moment for indexing
                await this.sleep(2000);
                
                // Try to get document count
                const docCount = await searchClient.getDocumentCount();
                console.log(`✅ Index contains ${docCount} document(s)`);
                
                // Clean up - delete the test document
                const deleteResult = await searchClient.deleteDocuments([{ id: 'test-doc-1' }]);
                if (deleteResult.results[0].succeeded) {
                    console.log('✅ Test document cleaned up successfully');
                }
                
                return true;
            } else {
                console.log(`❌ Test document upload failed: ${uploadResult.results[0].errorMessage}`);
                return false;
            }
            
        } catch (error) {
            console.log(`❌ Index functionality test failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * List existing indexes in the service
     */
    async listExistingIndexes() {
        console.log('📋 Listing existing indexes...');
        
        try {
            const indexes = [];
            for await (const index of this.indexClient.listIndexes()) {
                indexes.push(index);
            }
            
            if (indexes.length > 0) {
                console.log(`Found ${indexes.length} existing indexes:`);
                for (const index of indexes) {
                    console.log(`   - ${index.name} (${index.fields.length} fields)`);
                }
            } else {
                console.log('No existing indexes found');
            }
            
        } catch (error) {
            console.log(`❌ Failed to list indexes: ${error.message}`);
        }
    }
    
    /**
     * Clean up the created index (optional)
     */
    async cleanupIndex(indexName) {
        console.log(`🧹 Cleaning up index '${indexName}'...`);
        
        try {
            await this.indexClient.deleteIndex(indexName);
            console.log(`✅ Index '${indexName}' deleted successfully`);
            return true;
            
        } catch (error) {
            console.log(`❌ Failed to delete index: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Utility function to sleep for a specified number of milliseconds
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Main function demonstrating basic index creation
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Module 3: Basic Index Creation Example (JavaScript)');
    console.log('='.repeat(60));
    
    // Initialize the index creator
    let creator;
    try {
        creator = new BasicIndexCreator();
    } catch (error) {
        console.log(`❌ Configuration error: ${error.message}`);
        console.log('\nPlease set the required environment variables:');
        console.log('   export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"');
        console.log('   export AZURE_SEARCH_ADMIN_KEY="your-admin-api-key"');
        return;
    }
    
    // Create index client
    if (!(await creator.createIndexClient())) {
        console.log('❌ Failed to create index client. Exiting.');
        return;
    }
    
    // List existing indexes
    await creator.listExistingIndexes();
    
    // Define the index schema
    const fields = creator.defineBasicSchema();
    
    // Create the index
    const indexName = 'basic-blog-index-js';
    const index = await creator.createIndex(indexName, fields);
    
    if (index) {
        // Validate the index
        if (await creator.validateIndex(indexName)) {
            // Test index functionality
            if (await creator.testIndexFunctionality(indexName)) {
                console.log('\n🎉 Index creation and testing completed successfully!');
                
                // Ask if user wants to clean up
                const readline = require('readline');
                const rl = readline.createInterface({
                    input: process.stdin,
                    output: process.stdout
                });
                
                rl.question(`\nDo you want to delete the test index '${indexName}'? (y/N): `, async (answer) => {
                    if (answer.toLowerCase().trim() === 'y' || answer.toLowerCase().trim() === 'yes') {
                        await creator.cleanupIndex(indexName);
                    } else {
                        console.log(`ℹ️  Index '${indexName}' preserved for further experimentation`);
                    }
                    rl.close();
                });
            } else {
                console.log('⚠️  Index created but functionality test failed');
            }
        } else {
            console.log('⚠️  Index created but validation failed');
        }
    } else {
        console.log('❌ Index creation failed');
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('Example completed!');
    console.log('='.repeat(60));
    
    console.log('\n📚 What you learned:');
    console.log('✅ How to create SearchIndexClient with proper authentication');
    console.log('✅ How to define field types and attributes in JavaScript');
    console.log('✅ How to create a basic index schema');
    console.log('✅ How to handle index creation responses');
    console.log('✅ How to validate index creation');
    console.log('✅ How to test index functionality');
    
    console.log('\n🚀 Next steps:');
    console.log('1. Try modifying the schema with different field types');
    console.log('2. Experiment with different field attributes');
    console.log('3. Run the next example: 02_schema_design.js');
    console.log('4. Upload real documents to your index');
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Run the main function
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Application error:', error.message);
        process.exit(1);
    });
}

module.exports = { BasicIndexCreator };