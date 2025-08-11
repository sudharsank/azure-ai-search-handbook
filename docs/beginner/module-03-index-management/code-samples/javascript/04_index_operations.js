#!/usr/bin/env node
/**
 * Module 3: Index Management - Index Operations and Maintenance (JavaScript)
 * ==========================================================================
 * 
 * This example demonstrates various index management operations including updating
 * schemas, managing documents, monitoring index health, and performing maintenance
 * tasks using JavaScript.
 * 
 * Learning Objectives:
 * - Perform index lifecycle operations (create, update, delete)
 * - Update index schemas safely
 * - Monitor index health and statistics
 * - Manage document operations (update, merge, delete)
 * - Handle index versioning and maintenance
 * 
 * Prerequisites:
 * - Completed previous examples (01-03)
 * - Understanding of index schemas and data ingestion
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

const { SearchIndexClient, SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class IndexOperationsManager {
    /**
     * Initialize the index operations manager
     */
    constructor() {
        this.endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
        this.adminKey = process.env.AZURE_SEARCH_ADMIN_KEY;
        this.indexClient = null;
        
        if (!this.endpoint || !this.adminKey) {
            throw new Error('Missing required environment variables');
        }
    }
    
    /**
     * Create and validate the search clients
     */
    async createClients() {
        console.log('🔍 Creating Search Clients...');
        
        try {
            this.indexClient = new SearchIndexClient(
                this.endpoint,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Test connection
            const stats = await this.indexClient.getServiceStatistics();
            console.log('✅ Connected to Azure AI Search service');
            return true;
            
        } catch (error) {
            console.log(`❌ Failed to create clients: ${error.message}`);
            return false;
        }
    }
    
    /**
     * List all indexes in the service
     */
    async listAllIndexes() {
        console.log('📋 Listing All Indexes...');
        
        try {
            const indexes = [];
            for await (const index of this.indexClient.listIndexes()) {
                indexes.push(index);
            }
            
            if (indexes.length > 0) {
                console.log(`Found ${indexes.length} indexes:`);
                const indexNames = [];
                for (const index of indexes) {
                    console.log(`   - ${index.name} (${index.fields.length} fields)`);
                    indexNames.push(index.name);
                }
                return indexNames;
            } else {
                console.log('No indexes found');
                return [];
            }
            
        } catch (error) {
            console.log(`❌ Failed to list indexes: ${error.message}`);
            return [];
        }
    }
    
    /**
     * Get comprehensive information about a specific index
     */
    async getDetailedIndexInfo(indexName) {
        console.log(`🔍 Getting Detailed Information for '${indexName}'...`);
        
        try {
            const index = await this.indexClient.getIndex(indexName);
            
            // Create search client for document operations
            const searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Get document count
            const docCount = await searchClient.getDocumentCount();
            
            // Analyze field types and attributes
            const fieldAnalysis = this.analyzeIndexFields(index.fields);
            
            const indexInfo = {
                name: index.name,
                fieldCount: index.fields.length,
                documentCount: docCount,
                analyzers: index.analyzers ? index.analyzers.length : 0,
                scoringProfiles: index.scoringProfiles ? index.scoringProfiles.length : 0,
                corsConfigured: index.corsOptions !== null,
                fieldAnalysis: fieldAnalysis,
                fields: index.fields
            };
            
            console.log(`✅ Index Information Retrieved:`);
            console.log(`   Name: ${indexInfo.name}`);
            console.log(`   Fields: ${indexInfo.fieldCount}`);
            console.log(`   Documents: ${indexInfo.documentCount}`);
            console.log(`   Analyzers: ${indexInfo.analyzers}`);
            console.log(`   Scoring Profiles: ${indexInfo.scoringProfiles}`);
            console.log(`   CORS: ${indexInfo.corsConfigured ? 'Configured' : 'Not configured'}`);
            
            console.log(`\n   Field Analysis:`);
            for (const [fieldType, count] of Object.entries(indexInfo.fieldAnalysis.types)) {
                console.log(`     ${fieldType}: ${count}`);
            }
            
            console.log(`\n   Field Attributes:`);
            for (const [attr, count] of Object.entries(indexInfo.fieldAnalysis.attributes)) {
                console.log(`     ${attr}: ${count}`);
            }
            
            return indexInfo;
            
        } catch (error) {
            console.log(`❌ Failed to get index info: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Analyze field types and attributes
     */
    analyzeIndexFields(fields) {
        const fieldTypes = {};
        const attributes = {
            key: 0,
            searchable: 0,
            filterable: 0,
            sortable: 0,
            facetable: 0,
            retrievable: 0
        };
        
        for (const field of fields) {
            // Count field types
            const fieldType = field.type;
            fieldTypes[fieldType] = (fieldTypes[fieldType] || 0) + 1;
            
            // Count attributes
            if (field.key) attributes.key++;
            if (field.searchable) attributes.searchable++;
            if (field.filterable) attributes.filterable++;
            if (field.sortable) attributes.sortable++;
            if (field.facetable) attributes.facetable++;
            if (field.retrievable) attributes.retrievable++;
        }
        
        return {
            types: fieldTypes,
            attributes: attributes
        };
    }
    
    /**
     * Demonstrate safe schema updates by adding a new field
     */
    async updateIndexSchema(indexName, newFieldName, newFieldType) {
        console.log(`🔧 Updating Schema for '${indexName}'...`);
        
        try {
            // Get current index
            const currentIndex = await this.indexClient.getIndex(indexName);
            
            // Create new field based on type
            let newField;
            switch (newFieldType) {
                case 'string':
                    newField = {
                        name: newFieldName,
                        type: 'Edm.String',
                        filterable: true,
                        retrievable: true
                    };
                    break;
                case 'int':
                    newField = {
                        name: newFieldName,
                        type: 'Edm.Int32',
                        filterable: true,
                        sortable: true,
                        retrievable: true
                    };
                    break;
                case 'double':
                    newField = {
                        name: newFieldName,
                        type: 'Edm.Double',
                        filterable: true,
                        sortable: true,
                        retrievable: true
                    };
                    break;
                case 'boolean':
                    newField = {
                        name: newFieldName,
                        type: 'Edm.Boolean',
                        filterable: true,
                        retrievable: true
                    };
                    break;
                case 'date':
                    newField = {
                        name: newFieldName,
                        type: 'Edm.DateTimeOffset',
                        filterable: true,
                        sortable: true,
                        retrievable: true
                    };
                    break;
                default:
                    console.log(`❌ Unsupported field type: ${newFieldType}`);
                    return false;
            }
            
            // Check if field already exists
            const existingFieldNames = currentIndex.fields.map(f => f.name);
            if (existingFieldNames.includes(newFieldName)) {
                console.log(`⚠️  Field '${newFieldName}' already exists`);
                return true;
            }
            
            // Create updated field list
            const updatedFields = [...currentIndex.fields, newField];
            
            // Create updated index
            const updatedIndex = {
                name: currentIndex.name,
                fields: updatedFields,
                analyzers: currentIndex.analyzers,
                scoringProfiles: currentIndex.scoringProfiles,
                corsOptions: currentIndex.corsOptions
            };
            
            // Update the index
            const result = await this.indexClient.createOrUpdateIndex(updatedIndex);
            
            console.log(`✅ Schema updated successfully!`);
            console.log(`   Added field: ${newFieldName} (${newFieldType})`);
            console.log(`   Total fields: ${result.fields.length}`);
            
            return true;
            
        } catch (error) {
            console.log(`❌ Schema update failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Demonstrate various document operations
     */
    async demonstrateDocumentOperations(indexName) {
        console.log(`📄 Demonstrating Document Operations on '${indexName}'...`);
        
        try {
            const searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            // 1. Upload new documents
            console.log('   Step 1: Uploading new documents...');
            const newDocuments = [
                {
                    id: 'ops-demo-1',
                    title: 'Document Operations Demo 1',
                    content: 'This document demonstrates upload operations.',
                    author: 'Operations Manager',
                    category: 'Demo',
                    publishedDate: '2024-02-10T10:00:00Z',
                    tags: ['demo', 'operations'],
                    rating: 4.0,
                    viewCount: 10,
                    isPublished: true
                },
                {
                    id: 'ops-demo-2',
                    title: 'Document Operations Demo 2',
                    content: 'This document will be updated in the next step.',
                    author: 'Operations Manager',
                    category: 'Demo',
                    publishedDate: '2024-02-10T11:00:00Z',
                    tags: ['demo', 'operations'],
                    rating: 3.5,
                    viewCount: 5,
                    isPublished: true
                }
            ];
            
            const uploadResult = await searchClient.uploadDocuments(newDocuments);
            const successfulUploads = uploadResult.results.filter(r => r.succeeded).length;
            console.log(`   ✅ Uploaded ${successfulUploads} documents`);
            
            // Wait for indexing
            await this.sleep(2000);
            
            // 2. Update a document using merge
            console.log('   Step 2: Updating document using merge...');
            const updateDocument = {
                id: 'ops-demo-2',
                title: 'Document Operations Demo 2 - Updated',
                rating: 4.5,
                viewCount: 25
            };
            
            const mergeResult = await searchClient.mergeDocuments([updateDocument]);
            if (mergeResult.results[0].succeeded) {
                console.log(`   ✅ Document merged successfully`);
            }
            
            // Wait for indexing
            await this.sleep(2000);
            
            // 3. Verify the update
            console.log('   Step 3: Verifying document update...');
            const searchResults = await searchClient.search('ops-demo-2', {
                select: ['id', 'title', 'rating', 'viewCount']
            });
            
            for await (const result of searchResults.results) {
                if (result.document.id === 'ops-demo-2') {
                    console.log(`   📄 Updated document:`);
                    console.log(`      Title: ${result.document.title}`);
                    console.log(`      Rating: ${result.document.rating}`);
                    console.log(`      Views: ${result.document.viewCount}`);
                    break;
                }
            }
            
            // 4. Delete a document
            console.log('   Step 4: Deleting a document...');
            const deleteResult = await searchClient.deleteDocuments([{ id: 'ops-demo-1' }]);
            if (deleteResult.results[0].succeeded) {
                console.log(`   ✅ Document deleted successfully`);
            }
            
            // Wait for indexing
            await this.sleep(2000);
            
            // 5. Verify deletion
            const finalCount = await searchClient.getDocumentCount();
            console.log(`   📊 Final document count: ${finalCount}`);
            
            return true;
            
        } catch (error) {
            console.log(`❌ Document operations failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Monitor health and performance of multiple indexes
     */
    async monitorIndexHealth(indexNames) {
        console.log('🏥 Monitoring Index Health...');
        
        const healthReport = {
            timestamp: new Date().toISOString(),
            serviceStats: null,
            indexes: {}
        };
        
        try {
            // Get service-level statistics
            const serviceStats = await this.indexClient.getServiceStatistics();
            healthReport.serviceStats = {
                storageSize: serviceStats.storageSize,
                documentCount: serviceStats.documentCount
            };
            
            console.log(`📊 Service Statistics:`);
            console.log(`   Total Storage: ${serviceStats.storageSize.toLocaleString()} bytes`);
            console.log(`   Total Documents: ${serviceStats.documentCount.toLocaleString()}`);
            
            // Monitor each index
            for (const indexName of indexNames) {
                try {
                    const searchClient = new SearchClient(
                        this.endpoint,
                        indexName,
                        new AzureKeyCredential(this.adminKey)
                    );
                    
                    const docCount = await searchClient.getDocumentCount();
                    const index = await this.indexClient.getIndex(indexName);
                    
                    const indexHealth = {
                        documentCount: docCount,
                        fieldCount: index.fields.length,
                        status: docCount >= 0 ? 'healthy' : 'unknown'
                    };
                    
                    healthReport.indexes[indexName] = indexHealth;
                    
                    console.log(`   📋 ${indexName}:`);
                    console.log(`      Documents: ${docCount}`);
                    console.log(`      Fields: ${index.fields.length}`);
                    console.log(`      Status: ${indexHealth.status}`);
                    
                } catch (error) {
                    healthReport.indexes[indexName] = {
                        error: error.message,
                        status: 'error'
                    };
                    console.log(`   ❌ ${indexName}: ${error.message}`);
                }
            }
            
            return healthReport;
            
        } catch (error) {
            console.log(`❌ Health monitoring failed: ${error.message}`);
            return healthReport;
        }
    }
    
    /**
     * Create a test index for demonstrating operations
     */
    async createTestIndexForOperations() {
        console.log('🏗️  Creating Test Index for Operations Demo...');
        
        const indexName = 'operations-demo-index-js';
        
        const fields = [
            { name: 'id', type: 'Edm.String', key: true },
            { name: 'title', type: 'Edm.String', searchable: true },
            { name: 'content', type: 'Edm.String', searchable: true },
            { name: 'author', type: 'Edm.String', filterable: true },
            { name: 'category', type: 'Edm.String', filterable: true, facetable: true },
            { name: 'publishedDate', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: 'tags', type: 'Collection(Edm.String)', filterable: true, facetable: true },
            { name: 'rating', type: 'Edm.Double', filterable: true, sortable: true },
            { name: 'viewCount', type: 'Edm.Int32', filterable: true, sortable: true },
            { name: 'isPublished', type: 'Edm.Boolean', filterable: true }
        ];
        
        try {
            const index = { name: indexName, fields: fields };
            const result = await this.indexClient.createOrUpdateIndex(index);
            
            console.log(`✅ Test index '${result.name}' created successfully`);
            return indexName;
            
        } catch (error) {
            console.log(`❌ Failed to create test index: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Compare multiple indexes side by side
     */
    compareIndexes(indexNames) {
        console.log('📊 Comparing Indexes...');
        
        if (indexNames.length < 2) {
            console.log('❌ Need at least 2 indexes to compare');
            return;
        }
        
        console.log('\n📈 Index Comparison:');
        console.log('='.repeat(80));
        
        // This would need to be implemented with actual index data
        // For now, showing the structure
        console.log('Index comparison functionality would be implemented here');
        console.log('This would show field counts, document counts, etc. side by side');
    }
    
    /**
     * Utility function to sleep for a specified number of milliseconds
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Main function demonstrating index operations and maintenance
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Module 3: Index Operations and Maintenance Example (JavaScript)');
    console.log('='.repeat(60));
    
    // Initialize the operations manager
    let manager;
    try {
        manager = new IndexOperationsManager();
    } catch (error) {
        console.log(`❌ Configuration error: ${error.message}`);
        return;
    }
    
    // Create clients
    if (!(await manager.createClients())) {
        console.log('❌ Failed to create clients. Exiting.');
        return;
    }
    
    // List all indexes
    const indexNames = await manager.listAllIndexes();
    
    let testIndex = null;
    if (indexNames.length === 0) {
        console.log('ℹ️  No indexes found. Creating a test index...');
        testIndex = await manager.createTestIndexForOperations();
        if (testIndex) {
            indexNames.push(testIndex);
        } else {
            console.log('❌ Could not create test index. Exiting.');
            return;
        }
    }
    
    // Get detailed info for the first index
    if (indexNames.length > 0) {
        console.log(`\n${'='.repeat(20)} Detailed Index Information ${'='.repeat(20)}`);
        await manager.getDetailedIndexInfo(indexNames[0]);
    }
    
    // Demonstrate schema update
    console.log(`\n${'='.repeat(20)} Schema Update Demo ${'='.repeat(20)}`);
    const success = await manager.updateIndexSchema(indexNames[0], 'lastModified', 'date');
    
    if (success) {
        // Show updated schema
        await manager.getDetailedIndexInfo(indexNames[0]);
    }
    
    // Demonstrate document operations
    console.log(`\n${'='.repeat(20)} Document Operations Demo ${'='.repeat(20)}`);
    await manager.demonstrateDocumentOperations(indexNames[0]);
    
    // Monitor index health
    console.log(`\n${'='.repeat(20)} Index Health Monitoring ${'='.repeat(20)}`);
    const healthReport = await manager.monitorIndexHealth(indexNames.slice(0, 3)); // Monitor up to 3 indexes
    
    console.log('\n' + '='.repeat(60));
    console.log('Example completed!');
    console.log('='.repeat(60));
    
    console.log('\n📚 What you learned:');
    console.log('✅ How to perform index lifecycle operations');
    console.log('✅ How to update index schemas safely');
    console.log('✅ How to monitor index health and statistics');
    console.log('✅ How to manage document operations');
    console.log('✅ How to handle index versioning and maintenance');
    
    console.log('\n🚀 Next steps:');
    console.log('1. Try updating schemas with different field types');
    console.log('2. Implement automated health monitoring');
    console.log('3. Run the next example: 05_performance_optimization.js');
    console.log('4. Set up index maintenance schedules');
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

module.exports = { IndexOperationsManager };