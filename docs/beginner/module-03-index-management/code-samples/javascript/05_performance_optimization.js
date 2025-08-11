#!/usr/bin/env node
/**
 * Module 3: Index Management - Performance Optimization (JavaScript)
 * =================================================================
 * 
 * This example demonstrates performance optimization techniques for Azure AI Search
 * index management using JavaScript, including batch sizing, parallel operations,
 * and monitoring.
 * 
 * Learning Objectives:
 * - Optimize batch sizes for different document types
 * - Implement parallel upload strategies
 * - Monitor and measure performance metrics
 * - Apply performance best practices
 * - Handle memory and resource management
 * 
 * Prerequisites:
 * - Completed previous examples (01-04)
 * - Understanding of data ingestion and index operations
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

const { SearchIndexClient, SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class PerformanceOptimizer {
    /**
     * Initialize the performance optimizer
     */
    constructor() {
        this.endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
        this.adminKey = process.env.AZURE_SEARCH_ADMIN_KEY;
        
        if (!this.endpoint || !this.adminKey) {
            throw new Error('Missing required environment variables: AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_ADMIN_KEY');
        }
        
        this.indexClient = null;
        this.searchClient = null;
    }

    /**
     * Create and validate search clients
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
            console.error(`❌ Failed to create clients: ${error.message}`);
            return false;
        }
    }

    /**
     * Create a sample index for performance testing
     */
    async createPerformanceTestIndex() {
        console.log('🏗️  Creating performance test index...');
        
        const indexName = 'performance-test-js';
        
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
            const result = await this.indexClient.createOrUpdateIndex(indexDefinition);
            
            // Create search client for this index
            this.searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            console.log(`✅ Index '${result.name}' created successfully`);
            return indexName;
        } catch (error) {
            console.error(`❌ Failed to create index: ${error.message}`);
            return null;
        }
    }

    /**
     * Generate sample documents for performance testing
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
                title: `Performance Test Document ${docId}: ${category} Article`,
                content: `This is sample content for document ${docId}. It contains information about ${category.toLowerCase()} topics and is written by ${author}. The content is generated for testing purposes and demonstrates various aspects of the subject matter. This document is part of a performance optimization test suite.`,
                category: category,
                author: author,
                publishedDate: new Date(2024, 1, (i % 28) + 1, i % 24, 0, 0).toISOString(),
                rating: Math.round((3.0 + (i % 20) * 0.1) * 10) / 10, // Rating between 3.0 and 5.0
                viewCount: (i + 1) * 10 + (i % 100),
                tags: [category.toLowerCase(), 'sample', `tag${i % 5}`],
                isPublished: i % 10 !== 0 // 90% published
            };
            documents.push(document);
        }
        
        return documents;
    }

    /**
     * Test different batch sizes for optimal performance
     */
    async testBatchSizes() {
        console.log('📊 Testing Different Batch Sizes...');
        
        const batchSizes = [10, 25, 50, 100, 200];
        const totalDocuments = 500;
        const results = [];
        
        for (const batchSize of batchSizes) {
            console.log(`\n🧪 Testing batch size: ${batchSize}`);
            
            try {
                const startTime = Date.now();
                let totalSuccessful = 0;
                let totalFailed = 0;
                
                // Process in batches
                for (let batchNum = 0; batchNum < totalDocuments; batchNum += batchSize) {
                    const currentBatchSize = Math.min(batchSize, totalDocuments - batchNum);
                    const documents = this.generateSampleDocuments(currentBatchSize, batchNum + 1);
                    
                    const batchStartTime = Date.now();
                    const result = await this.searchClient.uploadDocuments(documents);
                    const batchTime = (Date.now() - batchStartTime) / 1000;
                    
                    const successful = result.results.filter(r => r.succeeded).length;
                    const failed = result.results.length - successful;
                    
                    totalSuccessful += successful;
                    totalFailed += failed;
                    
                    const rate = successful / batchTime;
                    console.log(`   Batch ${Math.floor(batchNum / batchSize) + 1}: ${successful}/${currentBatchSize} uploaded (${rate.toFixed(1)} docs/sec)`);
                    
                    // Brief pause to avoid overwhelming the service
                    if (batchNum + batchSize < totalDocuments) {
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                }
                
                const totalTime = (Date.now() - startTime) / 1000;
                const overallRate = totalSuccessful / totalTime;
                
                const testResult = {
                    batchSize,
                    totalSuccessful,
                    totalFailed,
                    totalTime: totalTime.toFixed(2),
                    overallRate: overallRate.toFixed(1)
                };
                
                results.push(testResult);
                
                console.log(`✅ Batch size ${batchSize} completed:`);
                console.log(`   Total successful: ${totalSuccessful}`);
                console.log(`   Total time: ${totalTime.toFixed(2)} seconds`);
                console.log(`   Overall rate: ${overallRate.toFixed(1)} documents/second`);
                
                // Clear index for next test
                await this.clearIndex();
                await new Promise(resolve => setTimeout(resolve, 2000));
                
            } catch (error) {
                console.error(`❌ Batch size ${batchSize} test failed: ${error.message}`);
            }
        }
        
        // Display results summary
        console.log('\n📈 Batch Size Performance Summary:');
        console.log('='.repeat(60));
        console.log('Batch Size | Success | Time (s) | Rate (docs/sec)');
        console.log('-'.repeat(60));
        
        for (const result of results) {
            console.log(`${result.batchSize.toString().padStart(10)} | ${result.totalSuccessful.toString().padStart(7)} | ${result.totalTime.padStart(8)} | ${result.overallRate.padStart(13)}`);
        }
        
        // Find optimal batch size
        const optimal = results.reduce((best, current) => 
            parseFloat(current.overallRate) > parseFloat(best.overallRate) ? current : best
        );
        
        console.log(`\n🏆 Optimal batch size: ${optimal.batchSize} (${optimal.overallRate} docs/sec)`);
        
        return results;
    }

    /**
     * Demonstrate parallel upload strategies
     */
    async testParallelUploads() {
        console.log('\n🔄 Testing Parallel Upload Strategies...');
        
        const totalDocuments = 1000;
        const batchSize = 50;
        const parallelBatches = 4;
        
        try {
            const startTime = Date.now();
            const allDocuments = this.generateSampleDocuments(totalDocuments);
            
            // Split documents into parallel batches
            const batchPromises = [];
            const batchesPerThread = Math.ceil(totalDocuments / batchSize / parallelBatches);
            
            for (let thread = 0; thread < parallelBatches; thread++) {
                const threadStartIndex = thread * batchesPerThread * batchSize;
                const threadEndIndex = Math.min(threadStartIndex + (batchesPerThread * batchSize), totalDocuments);
                
                if (threadStartIndex < totalDocuments) {
                    const threadDocuments = allDocuments.slice(threadStartIndex, threadEndIndex);
                    batchPromises.push(this.uploadBatchesSequentially(threadDocuments, batchSize, thread + 1));
                }
            }
            
            // Wait for all parallel uploads to complete
            const results = await Promise.all(batchPromises);
            const totalTime = (Date.now() - startTime) / 1000;
            
            // Aggregate results
            let totalSuccessful = 0;
            let totalFailed = 0;
            
            results.forEach((result, index) => {
                totalSuccessful += result.successful;
                totalFailed += result.failed;
                console.log(`   Thread ${index + 1}: ${result.successful} successful, ${result.failed} failed`);
            });
            
            const overallRate = totalSuccessful / totalTime;
            
            console.log(`\n✅ Parallel upload completed:`);
            console.log(`   Total successful: ${totalSuccessful}`);
            console.log(`   Total failed: ${totalFailed}`);
            console.log(`   Total time: ${totalTime.toFixed(2)} seconds`);
            console.log(`   Overall rate: ${overallRate.toFixed(1)} documents/second`);
            console.log(`   Parallel threads: ${parallelBatches}`);
            
            return {
                totalSuccessful,
                totalFailed,
                totalTime: totalTime.toFixed(2),
                overallRate: overallRate.toFixed(1),
                parallelThreads: parallelBatches
            };
            
        } catch (error) {
            console.error(`❌ Parallel upload test failed: ${error.message}`);
            return null;
        }
    }

    /**
     * Upload batches sequentially for a thread
     */
    async uploadBatchesSequentially(documents, batchSize, threadId) {
        let successful = 0;
        let failed = 0;
        
        for (let i = 0; i < documents.length; i += batchSize) {
            const batch = documents.slice(i, i + batchSize);
            
            try {
                const result = await this.searchClient.uploadDocuments(batch);
                const batchSuccessful = result.results.filter(r => r.succeeded).length;
                const batchFailed = result.results.length - batchSuccessful;
                
                successful += batchSuccessful;
                failed += batchFailed;
                
                // Brief pause between batches
                await new Promise(resolve => setTimeout(resolve, 50));
                
            } catch (error) {
                console.error(`   Thread ${threadId} batch failed: ${error.message}`);
                failed += batch.length;
            }
        }
        
        return { successful, failed };
    }

    /**
     * Monitor memory usage during operations
     */
    async monitorMemoryUsage() {
        console.log('\n💾 Memory Usage Monitoring...');
        
        const formatBytes = (bytes) => {
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            if (bytes === 0) return '0 Bytes';
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        };
        
        const getMemoryUsage = () => {
            const usage = process.memoryUsage();
            return {
                rss: formatBytes(usage.rss),
                heapTotal: formatBytes(usage.heapTotal),
                heapUsed: formatBytes(usage.heapUsed),
                external: formatBytes(usage.external)
            };
        };
        
        console.log('Initial memory usage:');
        const initialMemory = getMemoryUsage();
        console.log(`   RSS: ${initialMemory.rss}`);
        console.log(`   Heap Total: ${initialMemory.heapTotal}`);
        console.log(`   Heap Used: ${initialMemory.heapUsed}`);
        console.log(`   External: ${initialMemory.external}`);
        
        // Perform memory-intensive operation
        console.log('\nPerforming large document upload...');
        const largeDocuments = this.generateSampleDocuments(2000);
        
        const startTime = Date.now();
        let successful = 0;
        
        try {
            const batchSize = 100;
            for (let i = 0; i < largeDocuments.length; i += batchSize) {
                const batch = largeDocuments.slice(i, i + batchSize);
                const result = await this.searchClient.uploadDocuments(batch);
                successful += result.results.filter(r => r.succeeded).length;
                
                // Monitor memory every 10 batches
                if ((i / batchSize) % 10 === 0) {
                    const currentMemory = getMemoryUsage();
                    console.log(`   Batch ${i / batchSize + 1}: Heap Used: ${currentMemory.heapUsed}`);
                }
                
                await new Promise(resolve => setTimeout(resolve, 50));
            }
            
            const totalTime = (Date.now() - startTime) / 1000;
            
            console.log('\nFinal memory usage:');
            const finalMemory = getMemoryUsage();
            console.log(`   RSS: ${finalMemory.rss}`);
            console.log(`   Heap Total: ${finalMemory.heapTotal}`);
            console.log(`   Heap Used: ${finalMemory.heapUsed}`);
            console.log(`   External: ${finalMemory.external}`);
            
            console.log(`\n✅ Memory monitoring completed:`);
            console.log(`   Documents processed: ${successful}`);
            console.log(`   Time taken: ${totalTime.toFixed(2)} seconds`);
            
            // Force garbage collection if available
            if (global.gc) {
                global.gc();
                console.log('   Garbage collection triggered');
                
                const afterGcMemory = getMemoryUsage();
                console.log(`   After GC - Heap Used: ${afterGcMemory.heapUsed}`);
            }
            
        } catch (error) {
            console.error(`❌ Memory monitoring test failed: ${error.message}`);
        }
    }

    /**
     * Apply performance best practices
     */
    async applyBestPractices() {
        console.log('\n🎯 Applying Performance Best Practices...');
        
        const bestPractices = [
            {
                name: 'Optimal Batch Size',
                description: 'Use batch sizes between 50-100 documents for best performance',
                test: async () => {
                    const documents = this.generateSampleDocuments(100);
                    const startTime = Date.now();
                    const result = await this.searchClient.uploadDocuments(documents);
                    const time = (Date.now() - startTime) / 1000;
                    const successful = result.results.filter(r => r.succeeded).length;
                    return { successful, time: time.toFixed(2), rate: (successful / time).toFixed(1) };
                }
            },
            {
                name: 'Document Size Optimization',
                description: 'Keep individual documents under 16MB for optimal performance',
                test: async () => {
                    const documents = this.generateSampleDocuments(50).map(doc => ({
                        ...doc,
                        content: doc.content.repeat(10) // Increase content size
                    }));
                    const startTime = Date.now();
                    const result = await this.searchClient.uploadDocuments(documents);
                    const time = (Date.now() - startTime) / 1000;
                    const successful = result.results.filter(r => r.succeeded).length;
                    return { successful, time: time.toFixed(2), rate: (successful / time).toFixed(1) };
                }
            },
            {
                name: 'Error Handling',
                description: 'Implement proper error handling and retry logic',
                test: async () => {
                    const documents = this.generateSampleDocuments(50);
                    let successful = 0;
                    let retries = 0;
                    
                    const startTime = Date.now();
                    
                    try {
                        const result = await this.searchClient.uploadDocuments(documents);
                        successful = result.results.filter(r => r.succeeded).length;
                        
                        // Simulate retry for failed documents
                        const failed = result.results.filter(r => !r.succeeded);
                        if (failed.length > 0) {
                            retries = 1;
                            // In real scenario, you would retry failed documents
                        }
                        
                    } catch (error) {
                        console.log(`   Handled error: ${error.message}`);
                        retries = 1;
                    }
                    
                    const time = (Date.now() - startTime) / 1000;
                    return { successful, time: time.toFixed(2), retries };
                }
            }
        ];
        
        for (const practice of bestPractices) {
            console.log(`\n📋 Testing: ${practice.name}`);
            console.log(`   ${practice.description}`);
            
            try {
                const result = await practice.test();
                console.log(`   ✅ Result: ${JSON.stringify(result)}`);
            } catch (error) {
                console.log(`   ❌ Test failed: ${error.message}`);
            }
            
            // Clear index between tests
            await this.clearIndex();
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    /**
     * Clear all documents from the index
     */
    async clearIndex() {
        try {
            // Get all document IDs
            const searchResults = await this.searchClient.search('*', {
                select: ['id'],
                top: 1000
            });
            
            const documentIds = [];
            for await (const result of searchResults.results) {
                documentIds.push(result.document.id);
            }
            
            if (documentIds.length > 0) {
                await this.searchClient.deleteDocuments('id', documentIds);
            }
            
        } catch (error) {
            console.log(`   Warning: Could not clear index: ${error.message}`);
        }
    }

    /**
     * Get performance statistics
     */
    async getPerformanceStatistics() {
        console.log('\n📊 Current Performance Statistics:');
        
        try {
            const docCount = await this.searchClient.getDocumentCount();
            console.log(`   Total documents: ${docCount}`);
            
            // Sample some documents to show variety
            const searchResults = await this.searchClient.search('*', {
                select: ['id', 'title', 'category', 'author'],
                top: 5
            });
            
            console.log('   Sample documents:');
            for await (const result of searchResults.results) {
                const doc = result.document;
                console.log(`     - ${doc.id}: ${doc.title} (${doc.category})`);
            }
            
        } catch (error) {
            console.error(`❌ Failed to get statistics: ${error.message}`);
        }
    }
}

/**
 * Main program demonstrating performance optimization
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Module 3: Performance Optimization Example (JavaScript)');
    console.log('='.repeat(60));
    
    // Initialize the performance optimizer
    let optimizer;
    try {
        optimizer = new PerformanceOptimizer();
    } catch (error) {
        console.error(`❌ Configuration error: ${error.message}`);
        return;
    }
    
    // Create clients
    if (!(await optimizer.createClients())) {
        console.error('❌ Failed to create clients. Exiting.');
        return;
    }
    
    // Create performance test index
    const indexName = await optimizer.createPerformanceTestIndex();
    if (!indexName) {
        console.error('❌ Failed to create performance test index. Exiting.');
        return;
    }
    
    console.log(`\n🎯 Running performance optimization demonstrations on index '${indexName}'...`);
    
    // Run demonstrations
    const demonstrations = [
        { name: 'Batch Size Testing', func: () => optimizer.testBatchSizes() },
        { name: 'Parallel Upload Testing', func: () => optimizer.testParallelUploads() },
        { name: 'Memory Usage Monitoring', func: () => optimizer.monitorMemoryUsage() },
        { name: 'Best Practices Application', func: () => optimizer.applyBestPractices() }
    ];
    
    for (const demo of demonstrations) {
        console.log(`\n${'='.repeat(20)} ${demo.name} ${'='.repeat(20)}`);
        try {
            await demo.func();
            console.log(`✅ ${demo.name} completed successfully`);
        } catch (error) {
            console.error(`❌ ${demo.name} failed: ${error.message}`);
        }
        
        // Brief pause between demonstrations
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Show current statistics
    console.log(`\n${'='.repeat(20)} Current Statistics ${'='.repeat(20)}`);
    await optimizer.getPerformanceStatistics();
    
    console.log('\n' + '='.repeat(60));
    console.log('Example completed!');
    console.log('='.repeat(60));
    
    console.log('\n📚 What you learned:');
    console.log('✅ How to optimize batch sizes for different scenarios');
    console.log('✅ How to implement parallel upload strategies');
    console.log('✅ How to monitor and measure performance metrics');
    console.log('✅ How to apply performance best practices');
    console.log('✅ How to handle memory and resource management');
    
    console.log('\n🚀 Next steps:');
    console.log('1. Experiment with different batch sizes for your data');
    console.log('2. Implement parallel processing for large datasets');
    console.log('3. Run the next example: 06_error_handling.js');
    console.log('4. Monitor performance in your production environment');
}

// Run the example
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { PerformanceOptimizer };