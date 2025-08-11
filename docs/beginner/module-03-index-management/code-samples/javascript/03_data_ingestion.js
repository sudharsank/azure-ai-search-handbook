#!/usr/bin/env node
/**
 * Module 3: Index Management - Data Ingestion Strategies (JavaScript)
 * ===================================================================
 * 
 * This example demonstrates efficient data ingestion strategies for Azure AI Search
 * using JavaScript. You'll learn about batch operations, large dataset handling,
 * progress tracking, and optimization techniques for document uploads.
 * 
 * Learning Objectives:
 * - Implement single and batch document uploads
 * - Handle large datasets efficiently
 * - Optimize batch sizes for performance
 * - Track upload progress and handle errors
 * - Use different document actions (upload, merge, delete)
 * 
 * Prerequisites:
 * - Completed 01_create_basic_index.js and 02_schema_design.js
 * - Understanding of index schemas
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

const { SearchIndexClient, SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class DataIngestionManager {
    /**
     * Initialize the data ingestion manager
     */
    constructor() {
        this.endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
        this.adminKey = process.env.AZURE_SEARCH_ADMIN_KEY;
        this.indexClient = null;
        this.searchClient = null;
        
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
     * Create a sample index for data ingestion testing
     */
    async createSampleIndex() {
        console.log('🏗️  Creating sample index for data ingestion...');
        
        const indexName = 'data-ingestion-demo-js';
        
        const fields = [
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
        ];
        
        try {
            const index = { name: indexName, fields: fields };
            const result = await this.indexClient.createOrUpdateIndex(index);
            
            // Create search client for this index
            this.searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            console.log(`✅ Index '${result.name}' created successfully`);
            return indexName;
            
        } catch (error) {
            console.log(`❌ Failed to create index: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Demonstrate single document upload
     */
    async singleDocumentUpload() {
        console.log('📄 Single Document Upload Example...');
        
        try {
            // Create a single document
            const document = {
                id: 'single-doc-1',
                title: 'Single Document Upload Example',
                content: 'This document demonstrates how to upload a single document to Azure AI Search.',
                category: 'Tutorial',
                author: 'Data Ingestion Manager',
                publishedDate: '2024-02-10T10:00:00Z',
                rating: 4.5,
                viewCount: 100,
                tags: ['tutorial', 'single-upload', 'example'],
                isPublished: true
            };
            
            // Upload the document
            const startTime = Date.now();
            const result = await this.searchClient.uploadDocuments([document]);
            const uploadTime = (Date.now() - startTime) / 1000;
            
            if (result.results[0].succeeded) {
                console.log(`✅ Document uploaded successfully in ${uploadTime.toFixed(3)} seconds`);
                console.log(`   Document ID: ${result.results[0].key}`);
                return true;
            } else {
                console.log(`❌ Upload failed: ${result.results[0].errorMessage}`);
                return false;
            }
            
        } catch (error) {
            console.log(`❌ Single document upload failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Demonstrate batch document upload
     */
    async batchDocumentUpload(batchSize = 10) {
        console.log(`📦 Batch Document Upload Example (batch size: ${batchSize})...`);
        
        try {
            // Generate sample documents
            const documents = this.generateSampleDocuments(batchSize);
            
            // Upload documents in batch
            const startTime = Date.now();
            const result = await this.searchClient.uploadDocuments(documents);
            const uploadTime = (Date.now() - startTime) / 1000;
            
            // Analyze results
            const successful = result.results.filter(r => r.succeeded).length;
            const failed = result.results.length - successful;
            
            console.log(`✅ Batch upload completed in ${uploadTime.toFixed(3)} seconds`);
            console.log(`   Successful: ${successful}/${documents.length}`);
            console.log(`   Failed: ${failed}`);
            console.log(`   Rate: ${(successful / uploadTime).toFixed(1)} documents/second`);
            
            // Show any failures
            result.results.forEach(r => {
                if (!r.succeeded) {
                    console.log(`   ❌ Failed: ${r.key} - ${r.errorMessage}`);
                }
            });
            
            return successful > 0;
            
        } catch (error) {
            console.log(`❌ Batch upload failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Demonstrate large dataset upload with progress tracking
     */
    async largeDatasetUpload(totalDocuments = 1000, batchSize = 100) {
        console.log(`🗂️  Large Dataset Upload Example (${totalDocuments} documents, batch size: ${batchSize})...`);
        
        try {
            let totalSuccessful = 0;
            let totalFailed = 0;
            let totalTime = 0;
            
            // Process in batches
            for (let batchNum = 0; batchNum < totalDocuments; batchNum += batchSize) {
                const currentBatchSize = Math.min(batchSize, totalDocuments - batchNum);
                
                // Generate batch documents
                const documents = this.generateSampleDocuments(currentBatchSize, batchNum + 1);
                
                // Upload batch
                const startTime = Date.now();
                const result = await this.searchClient.uploadDocuments(documents);
                const batchTime = (Date.now() - startTime) / 1000;
                totalTime += batchTime;
                
                // Track results
                const successful = result.results.filter(r => r.succeeded).length;
                const failed = result.results.length - successful;
                
                totalSuccessful += successful;
                totalFailed += failed;
                
                // Progress update
                const progress = ((batchNum + currentBatchSize) / totalDocuments) * 100;
                const rate = successful / batchTime;
                
                console.log(`   Batch ${Math.floor(batchNum / batchSize) + 1}: ${successful}/${currentBatchSize} uploaded ` +
                          `(${rate.toFixed(1)} docs/sec) - Progress: ${progress.toFixed(1)}%`);
                
                // Brief pause to avoid overwhelming the service
                if (batchNum + batchSize < totalDocuments) {
                    await this.sleep(100);
                }
            }
            
            // Final summary
            const overallRate = totalSuccessful / totalTime;
            console.log(`\n✅ Large dataset upload completed:`);
            console.log(`   Total successful: ${totalSuccessful}`);
            console.log(`   Total failed: ${totalFailed}`);
            console.log(`   Total time: ${totalTime.toFixed(2)} seconds`);
            console.log(`   Overall rate: ${overallRate.toFixed(1)} documents/second`);
            
            return totalSuccessful > 0;
            
        } catch (error) {
            console.log(`❌ Large dataset upload failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Demonstrate parallel upload for improved performance
     */
    async parallelUpload(totalDocuments = 500, batchSize = 50, maxWorkers = 4) {
        console.log(`⚡ Parallel Upload Example (${totalDocuments} documents, ${maxWorkers} workers)...`);
        
        try {
            // Create batches
            const batches = [];
            for (let batchNum = 0; batchNum < totalDocuments; batchNum += batchSize) {
                const currentBatchSize = Math.min(batchSize, totalDocuments - batchNum);
                const documents = this.generateSampleDocuments(
                    currentBatchSize, 
                    batchNum + 10000  // Different ID range to avoid conflicts
                );
                batches.push({ batchNum: Math.floor(batchNum / batchSize) + 1, documents });
            }
            
            // Upload batches in parallel with controlled concurrency
            const startTime = Date.now();
            let totalSuccessful = 0;
            let totalFailed = 0;
            
            // Process batches with limited concurrency
            for (let i = 0; i < batches.length; i += maxWorkers) {
                const batchGroup = batches.slice(i, i + maxWorkers);
                
                const promises = batchGroup.map(async ({ batchNum, documents }) => {
                    try {
                        const result = await this.searchClient.uploadDocuments(documents);
                        const successful = result.results.filter(r => r.succeeded).length;
                        const failed = result.results.length - successful;
                        
                        console.log(`   Batch ${batchNum}: ${successful}/${documents.length} uploaded`);
                        return { successful, failed };
                    } catch (error) {
                        console.log(`   ❌ Batch ${batchNum} failed: ${error.message}`);
                        return { successful: 0, failed: documents.length };
                    }
                });
                
                const results = await Promise.all(promises);
                results.forEach(({ successful, failed }) => {
                    totalSuccessful += successful;
                    totalFailed += failed;
                });
            }
            
            const totalTime = (Date.now() - startTime) / 1000;
            const overallRate = totalSuccessful / totalTime;
            
            console.log(`\n✅ Parallel upload completed:`);
            console.log(`   Total successful: ${totalSuccessful}`);
            console.log(`   Total failed: ${totalFailed}`);
            console.log(`   Total time: ${totalTime.toFixed(2)} seconds`);
            console.log(`   Overall rate: ${overallRate.toFixed(1)} documents/second`);
            console.log(`   Workers used: ${maxWorkers}`);
            
            return totalSuccessful > 0;
            
        } catch (error) {
            console.log(`❌ Parallel upload failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Demonstrate different document operations (upload, merge, delete)
     */
    async documentOperationsDemo() {
        console.log('🔄 Document Operations Demo (Upload, Merge, Delete)...');
        
        try {
            // 1. Upload initial documents
            console.log('   Step 1: Uploading initial documents...');
            const initialDocs = [
                {
                    id: 'ops-doc-1',
                    title: 'Original Title 1',
                    content: 'Original content for document 1',
                    category: 'Original',
                    author: 'Original Author',
                    publishedDate: '2024-02-10T10:00:00Z',
                    rating: 3.0,
                    viewCount: 50,
                    tags: ['original'],
                    isPublished: true
                },
                {
                    id: 'ops-doc-2',
                    title: 'Original Title 2',
                    content: 'Original content for document 2',
                    category: 'Original',
                    author: 'Original Author',
                    publishedDate: '2024-02-10T11:00:00Z',
                    rating: 3.5,
                    viewCount: 75,
                    tags: ['original'],
                    isPublished: true
                }
            ];
            
            const uploadResult = await this.searchClient.uploadDocuments(initialDocs);
            const successfulUploads = uploadResult.results.filter(r => r.succeeded).length;
            console.log(`   ✅ Uploaded ${successfulUploads} initial documents`);
            
            // Wait for indexing
            await this.sleep(2000);
            
            // 2. Merge operation (partial update)
            console.log('   Step 2: Merging document updates...');
            const mergeDocs = [
                {
                    id: 'ops-doc-1',
                    title: 'Updated Title 1',  // Update title
                    rating: 4.5,  // Update rating
                    viewCount: 150  // Update view count
                    // Other fields remain unchanged
                }
            ];
            
            const mergeResult = await this.searchClient.mergeDocuments(mergeDocs);
            const successfulMerges = mergeResult.results.filter(r => r.succeeded).length;
            console.log(`   ✅ Merged ${successfulMerges} document updates`);
            
            // 3. Merge or upload operation (upsert)
            console.log('   Step 3: Merge or upload (upsert) operation...');
            const upsertDocs = [
                {
                    id: 'ops-doc-3',  // New document
                    title: 'New Document via Upsert',
                    content: 'This document was created via mergeOrUpload',
                    category: 'Upsert',
                    author: 'Upsert Author',
                    publishedDate: '2024-02-10T12:00:00Z',
                    rating: 4.0,
                    viewCount: 25,
                    tags: ['upsert', 'new'],
                    isPublished: true
                },
                {
                    id: 'ops-doc-2',  // Existing document - will be merged
                    content: 'Updated content for document 2',
                    rating: 4.8
                }
            ];
            
            const upsertResult = await this.searchClient.mergeOrUploadDocuments(upsertDocs);
            const successfulUpserts = upsertResult.results.filter(r => r.succeeded).length;
            console.log(`   ✅ Upserted ${successfulUpserts} documents`);
            
            // Wait for indexing
            await this.sleep(2000);
            
            // 4. Verify current state
            console.log('   Step 4: Verifying current document state...');
            const docCount = await this.searchClient.getDocumentCount();
            console.log(`   📊 Current document count: ${docCount}`);
            
            // 5. Delete operation
            console.log('   Step 5: Deleting a document...');
            const deleteResult = await this.searchClient.deleteDocuments([{ id: 'ops-doc-2' }]);
            const successfulDeletes = deleteResult.results.filter(r => r.succeeded).length;
            console.log(`   ✅ Deleted ${successfulDeletes} documents`);
            
            // Wait for indexing
            await this.sleep(2000);
            
            // 6. Final verification
            const finalCount = await this.searchClient.getDocumentCount();
            console.log(`   📊 Final document count: ${finalCount}`);
            
            console.log('✅ Document operations demo completed successfully');
            return true;
            
        } catch (error) {
            console.log(`❌ Document operations demo failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Generate sample documents for testing
     */
    generateSampleDocuments(count, startId = 1) {
        const documents = [];
        const categories = ['Technology', 'Science', 'Business', 'Health', 'Education'];
        const authors = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eve Brown'];
        
        for (let i = 0; i < count; i++) {
            const docId = startId + i;
            const category = categories[i % categories.length];
            const author = authors[i % authors.length];
            
            const document = {
                id: `doc-${docId}`,
                title: `Sample Document ${docId}: ${category} Article`,
                content: `This is sample content for document ${docId}. It contains information about ${category.toLowerCase()} topics and is written by ${author}. The content is generated for testing purposes and demonstrates various aspects of the subject matter.`,
                category: category,
                author: author,
                publishedDate: `2024-02-${String((i % 28) + 1).padStart(2, '0')}T${String(i % 24).padStart(2, '0')}:00:00Z`,
                rating: Math.round((3.0 + (i % 20) * 0.1) * 10) / 10,  // Rating between 3.0 and 5.0
                viewCount: (i + 1) * 10 + (i % 100),
                tags: [category.toLowerCase(), 'sample', `tag${i % 5}`],
                isPublished: i % 10 !== 0  // 90% published
            };
            documents.push(document);
        }
        
        return documents;
    }
    
    /**
     * Get ingestion statistics
     */
    async getIngestionStatistics() {
        console.log('📊 Current Index Statistics:');
        
        try {
            const docCount = await this.searchClient.getDocumentCount();
            console.log(`   Total documents: ${docCount}`);
            
            // Sample some documents to show variety
            const results = await this.searchClient.search('*', {
                top: 5,
                select: ['id', 'title', 'category', 'author']
            });
            
            console.log(`   Sample documents:`);
            for await (const result of results.results) {
                console.log(`     - ${result.document.id}: ${result.document.title} (${result.document.category})`);
            }
            
        } catch (error) {
            console.log(`❌ Failed to get statistics: ${error.message}`);
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
 * Main function demonstrating data ingestion strategies
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Module 3: Data Ingestion Strategies Example (JavaScript)');
    console.log('='.repeat(60));
    
    // Initialize the data ingestion manager
    let manager;
    try {
        manager = new DataIngestionManager();
    } catch (error) {
        console.log(`❌ Configuration error: ${error.message}`);
        return;
    }
    
    // Create clients
    if (!(await manager.createClients())) {
        console.log('❌ Failed to create clients. Exiting.');
        return;
    }
    
    // Create sample index
    const indexName = await manager.createSampleIndex();
    if (!indexName) {
        console.log('❌ Failed to create sample index. Exiting.');
        return;
    }
    
    console.log(`\n🎯 Running data ingestion demonstrations on index '${indexName}'...`);
    
    // Run demonstrations
    const demonstrations = [
        { name: 'Single Document Upload', func: () => manager.singleDocumentUpload() },
        { name: 'Batch Document Upload', func: () => manager.batchDocumentUpload(50) },
        { name: 'Large Dataset Upload', func: () => manager.largeDatasetUpload(200, 50) },
        { name: 'Parallel Upload', func: () => manager.parallelUpload(200, 25, 3) },
        { name: 'Document Operations', func: () => manager.documentOperationsDemo() }
    ];
    
    for (const demo of demonstrations) {
        console.log(`\n${'='.repeat(20)} ${demo.name} ${'='.repeat(20)}`);
        try {
            const success = await demo.func();
            if (success) {
                console.log(`✅ ${demo.name} completed successfully`);
            } else {
                console.log(`⚠️  ${demo.name} completed with issues`);
            }
        } catch (error) {
            console.log(`❌ ${demo.name} failed: ${error.message}`);
        }
        
        // Brief pause between demonstrations
        await manager.sleep(1000);
    }
    
    // Show current statistics
    console.log(`\n${'='.repeat(20)} Current Statistics ${'='.repeat(20)}`);
    await manager.getIngestionStatistics();
    
    console.log('\n' + '='.repeat(60));
    console.log('Example completed!');
    console.log('='.repeat(60));
    
    console.log('\n📚 What you learned:');
    console.log('✅ How to implement single and batch document uploads');
    console.log('✅ How to handle large datasets efficiently');
    console.log('✅ How to optimize batch sizes for performance');
    console.log('✅ How to track upload progress and handle errors');
    console.log('✅ How to use different document actions (upload, merge, delete)');
    console.log('✅ How to implement parallel upload strategies');
    
    console.log('\n🚀 Next steps:');
    console.log('1. Try ingesting your own data');
    console.log('2. Experiment with different batch sizes for your use case');
    console.log('3. Run the next example: 04_index_operations.js');
    console.log('4. Implement error handling and retry logic for production');
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

module.exports = { DataIngestionManager };