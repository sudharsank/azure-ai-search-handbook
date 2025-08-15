/**
 * Module 7: Pagination & Result Shaping - Large Result Sets
 * Azure AI Search JavaScript SDK Example
 * 
 * This example demonstrates efficient techniques for handling large result sets in Azure AI Search,
 * including streaming, batching, parallel processing, and memory management strategies.
 * 
 * Prerequisites:
 * - Azure AI Search service
 * - Node.js 14.x or later
 * - @azure/search-documents package
 * - Sample data index with substantial data
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class ProcessingStats {
    constructor() {
        this.totalProcessed = 0;
        this.totalTimeMs = 0;
        this.batchCount = 0;
        this.errors = 0;
        this.memoryPeakMb = 0;
        this.throughputDocsPerSec = 0;
    }

    updateThroughput() {
        if (this.totalTimeMs > 0) {
            this.throughputDocsPerSec = this.totalProcessed / (this.totalTimeMs / 1000);
        }
    }
}

class LargeResultSetHandler {
    /**
     * Comprehensive handler for large result sets
     */
    constructor(endpoint, indexName, apiKey) {
        this.client = new SearchClient(
            endpoint,
            indexName,
            new AzureKeyCredential(apiKey)
        );
        this.stats = new ProcessingStats();
    }

    /**
     * Stream search results in batches for memory-efficient processing
     * @param {string} query - Search query
     * @param {number} batchSize - Size of each batch
     * @param {number} maxResults - Maximum number of results to process
     * @param {string[]} selectFields - Fields to select for reduced payload
     * @param {Function} progressCallback - Optional callback for progress updates
     * @returns {AsyncGenerator} Individual documents from the search results
     */
    async* streamResults(query, batchSize = 100, maxResults = null, selectFields = null, progressCallback = null) {
        console.log(`🌊 Starting streaming search for query: '${query}'`);
        console.log(`📊 Batch size: ${batchSize}, Max results: ${maxResults || 'unlimited'}`);

        let currentSkip = 0;
        let totalProcessed = 0;
        const startTime = Date.now();

        while (true) {
            // Calculate batch size for this iteration
            let currentBatchSize = batchSize;
            if (maxResults) {
                const remaining = maxResults - totalProcessed;
                if (remaining <= 0) break;
                currentBatchSize = Math.min(batchSize, remaining);
            }

            const batchStart = Date.now();

            try {
                // Fetch batch
                const searchResults = await this.client.search(query, {
                    skip: currentSkip,
                    top: currentBatchSize,
                    select: selectFields
                });

                const batchDocs = [];
                for await (const result of searchResults.results) {
                    batchDocs.push(result);
                }

                const batchDuration = Date.now() - batchStart;

                if (batchDocs.length === 0) {
                    console.log(`   🏁 No more results at skip=${currentSkip}`);
                    break;
                }

                // Yield documents
                for (const doc of batchDocs) {
                    yield doc;
                    totalProcessed++;
                }

                currentSkip += batchDocs.length;
                this.stats.batchCount++;

                // Progress reporting
                if (progressCallback) {
                    progressCallback(totalProcessed, batchDuration);
                } else if (totalProcessed % (batchSize * 5) === 0) { // Report every 5 batches
                    const elapsed = Date.now() - startTime;
                    const rate = totalProcessed / (elapsed / 1000);
                    console.log(`   📦 Processed ${totalProcessed} documents (${rate.toFixed(1)} docs/sec)`);
                }

                // Break if we got fewer results than requested (end of data)
                if (batchDocs.length < currentBatchSize) {
                    console.log(`   🏁 Reached end of available results`);
                    break;
                }

            } catch (error) {
                console.log(`   ❌ Error in batch at skip=${currentSkip}: ${error.message}`);
                this.stats.errors++;
                break;
            }
        }

        // Update final statistics
        const totalTime = Date.now() - startTime;
        this.stats.totalProcessed = totalProcessed;
        this.stats.totalTimeMs = totalTime;
        this.stats.updateThroughput();

        console.log(`✅ Streaming completed: ${totalProcessed} documents in ${totalTime}ms`);
    }

    /**
     * Process large result sets in batches with optional parallel processing
     * @param {string} query - Search query
     * @param {Function} processorFunc - Function to process each batch
     * @param {number} batchSize - Size of each batch
     * @param {number} maxResults - Maximum number of results to process
     * @param {boolean} parallel - Whether to use parallel processing
     * @param {number} maxWorkers - Number of parallel workers
     * @returns {Array} List of processed results
     */
    async batchProcessResults(query, processorFunc, batchSize = 100, maxResults = null, parallel = false, maxWorkers = 4) {
        console.log(`🔄 Starting batch processing for query: '${query}'`);
        console.log(`📊 Batch size: ${batchSize}, Parallel: ${parallel}`);

        // Collect batches
        const batches = [];
        let currentBatch = [];

        for await (const doc of this.streamResults(query, batchSize, maxResults, ['hotelId', 'hotelName', 'description'])) {
            currentBatch.push(doc);

            if (currentBatch.length >= batchSize) {
                batches.push([...currentBatch]);
                currentBatch = [];
            }
        }

        // Add remaining documents
        if (currentBatch.length > 0) {
            batches.push(currentBatch);
        }

        console.log(`📦 Created ${batches.length} batches for processing`);

        // Process batches
        if (parallel && batches.length > 1) {
            return await this._processBatchesParallel(batches, processorFunc, maxWorkers);
        } else {
            return await this._processBatchesSequential(batches, processorFunc);
        }
    }

    /**
     * Process batches sequentially
     * @param {Array[]} batches - Array of document batches
     * @param {Function} processorFunc - Function to process each batch
     * @returns {Array} Processed results
     */
    async _processBatchesSequential(batches, processorFunc) {
        const results = [];

        for (let i = 0; i < batches.length; i++) {
            console.log(`   Processing batch ${i + 1}/${batches.length} (${batches[i].length} documents)`);

            try {
                const batchResult = await processorFunc(batches[i]);
                results.push(batchResult);
            } catch (error) {
                console.log(`   ❌ Error processing batch ${i + 1}: ${error.message}`);
                this.stats.errors++;
            }
        }

        return results;
    }

    /**
     * Process batches in parallel
     * @param {Array[]} batches - Array of document batches
     * @param {Function} processorFunc - Function to process each batch
     * @param {number} maxWorkers - Maximum number of parallel workers
     * @returns {Array} Processed results
     */
    async _processBatchesParallel(batches, processorFunc, maxWorkers) {
        const results = [];
        const semaphore = new Array(maxWorkers).fill(null);
        let batchIndex = 0;

        const processBatch = async (batch, index) => {
            try {
                const result = await processorFunc(batch);
                console.log(`   ✅ Completed batch ${index + 1}`);
                return { index, result };
            } catch (error) {
                console.log(`   ❌ Error in batch ${index + 1}: ${error.message}`);
                this.stats.errors++;
                return { index, error: error.message };
            }
        };

        // Process batches with concurrency limit
        const promises = [];
        for (let i = 0; i < Math.min(batches.length, maxWorkers); i++) {
            if (batchIndex < batches.length) {
                promises.push(processBatch(batches[batchIndex], batchIndex));
                batchIndex++;
            }
        }

        while (promises.length > 0) {
            const completed = await Promise.race(promises);
            const completedIndex = promises.findIndex(p => p === Promise.resolve(completed));
            promises.splice(completedIndex, 1);

            results.push(completed);

            // Start next batch if available
            if (batchIndex < batches.length) {
                promises.push(processBatch(batches[batchIndex], batchIndex));
                batchIndex++;
            }
        }

        // Sort results by batch index to maintain order
        results.sort((a, b) => a.index - b.index);
        return results.map(r => r.result || { error: r.error });
    }

    /**
     * Perform parallel searches across different ranges for large datasets
     * @param {string} baseQuery - Base search query
     * @param {Object[]} ranges - List of range filters
     * @param {number} batchSize - Batch size for each range
     * @returns {Object} Dictionary of results by range
     */
    async parallelRangeSearch(baseQuery, ranges, batchSize = 50) {
        console.log(`🔄 Starting parallel range search for query: '${baseQuery}'`);
        console.log(`📊 Ranges: ${ranges.length}, Batch size: ${batchSize}`);

        const searchRange = async (rangeConfig) => {
            const rangeName = rangeConfig.name;
            const rangeFilter = rangeConfig.filter;

            try {
                const searchResults = await this.client.search(baseQuery, {
                    filter: rangeFilter,
                    top: batchSize,
                    select: ['hotelId', 'hotelName', 'rating']
                });

                const docs = [];
                for await (const result of searchResults.results) {
                    docs.push(result);
                }

                return { name: rangeName, docs };

            } catch (error) {
                console.log(`❌ Error in range ${rangeName}: ${error.message}`);
                return { name: rangeName, docs: [], error: error.message };
            }
        };

        // Execute searches in parallel
        const rangePromises = ranges.map(rangeConfig => searchRange(rangeConfig));
        const rangeResults = await Promise.all(rangePromises);

        const results = {};
        let totalResults = 0;

        rangeResults.forEach(result => {
            results[result.name] = result.docs;
            totalResults += result.docs.length;
            console.log(`   ✅ Range '${result.name}': ${result.docs.length} results`);
        });

        console.log(`✅ Parallel range search completed: ${totalResults} total results`);
        return results;
    }

    /**
     * Export large result sets to file with memory efficiency
     * @param {string} query - Search query
     * @param {string} outputFile - Output file path
     * @param {number} batchSize - Batch size for processing
     * @param {string} format - Output format ('jsonl' or 'json')
     * @returns {Object} Export statistics
     */
    async memoryEfficientExport(query, outputFile, batchSize = 1000, format = 'jsonl') {
        console.log(`💾 Starting memory-efficient export for query: '${query}'`);
        console.log(`📁 Output file: ${outputFile}, Format: ${format}`);

        const fs = require('fs').promises;
        const startTime = Date.now();
        let exportedCount = 0;

        try {
            let fileHandle;
            
            if (format === 'json') {
                await fs.writeFile(outputFile, '[\n', 'utf8');
            } else {
                await fs.writeFile(outputFile, '', 'utf8');
            }

            let firstDoc = true;

            for await (const doc of this.streamResults(query, batchSize, null, ['hotelId', 'hotelName', 'description', 'rating'])) {
                let content;
                
                if (format === 'jsonl') {
                    content = JSON.stringify(doc) + '\n';
                } else { // json
                    if (!firstDoc) {
                        content = ',\n';
                    } else {
                        content = '';
                        firstDoc = false;
                    }
                    content += '  ' + JSON.stringify(doc);
                }

                await fs.appendFile(outputFile, content, 'utf8');
                exportedCount++;

                // Progress reporting
                if (exportedCount % 1000 === 0) {
                    const elapsed = (Date.now() - startTime) / 1000;
                    const rate = exportedCount / elapsed;
                    console.log(`   📝 Exported ${exportedCount} documents (${rate.toFixed(1)} docs/sec)`);
                }
            }

            if (format === 'json') {
                await fs.appendFile(outputFile, '\n]', 'utf8');
            }

        } catch (error) {
            console.log(`❌ Export error: ${error.message}`);
            return { error: error.message, exportedCount };
        }

        const totalTime = (Date.now() - startTime) / 1000;
        const fs = require('fs');
        const fileSize = fs.existsSync(outputFile) ? fs.statSync(outputFile).size : 0;

        const stats = {
            exportedCount,
            totalTimeSeconds: totalTime,
            throughputDocsPerSec: exportedCount / totalTime,
            outputFile,
            fileSizeBytes: fileSize,
            fileSizeMb: fileSize / (1024 * 1024),
            format
        };

        console.log(`✅ Export completed: ${exportedCount} documents in ${totalTime.toFixed(1)}s`);
        console.log(`📁 File size: ${stats.fileSizeMb.toFixed(2)} MB`);

        return stats;
    }

    /**
     * Get current processing statistics
     * @returns {ProcessingStats} Current statistics
     */
    getProcessingStats() {
        return this.stats;
    }

    /**
     * Reset processing statistics
     */
    resetStats() {
        this.stats = new ProcessingStats();
    }
}

// Example processor functions
async function analyzeSentimentBatch(batch) {
    /**
     * Example batch processor: analyze sentiment of descriptions
     */
    let positiveCount = 0;
    let negativeCount = 0;
    let neutralCount = 0;

    batch.forEach(doc => {
        const description = (doc.description || '').toLowerCase();

        // Simple sentiment analysis based on keywords
        const positiveWords = ['excellent', 'amazing', 'wonderful', 'great', 'fantastic'];
        const negativeWords = ['poor', 'bad', 'terrible', 'awful', 'disappointing'];

        const positiveScore = positiveWords.reduce((count, word) => 
            count + (description.includes(word) ? 1 : 0), 0);
        const negativeScore = negativeWords.reduce((count, word) => 
            count + (description.includes(word) ? 1 : 0), 0);

        if (positiveScore > negativeScore) {
            positiveCount++;
        } else if (negativeScore > positiveScore) {
            negativeCount++;
        } else {
            neutralCount++;
        }
    });

    return {
        batchSize: batch.length,
        positive: positiveCount,
        negative: negativeCount,
        neutral: neutralCount,
        sentimentRatio: batch.length > 0 ? positiveCount / batch.length : 0
    };
}

async function extractKeywordsBatch(batch) {
    /**
     * Example batch processor: extract common keywords
     */
    const wordCounts = {};

    batch.forEach(doc => {
        const description = (doc.description || '').toLowerCase();
        const words = description.split(/\s+/);

        words.forEach(word => {
            // Simple word cleaning
            const cleanWord = word.replace(/[.,!?;:"()[\]{}]/g, '');
            if (cleanWord.length > 3) { // Only count words longer than 3 characters
                wordCounts[cleanWord] = (wordCounts[cleanWord] || 0) + 1;
            }
        });
    });

    // Get top 10 words
    const topWords = Object.entries(wordCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);

    return {
        batchSize: batch.length,
        uniqueWords: Object.keys(wordCounts).length,
        topWords: topWords,
        totalWords: Object.values(wordCounts).reduce((sum, count) => sum + count, 0)
    };
}

async function main() {
    // Configuration
    const endpoint = process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net';
    const apiKey = process.env.SEARCH_API_KEY || 'your-api-key';
    const indexName = process.env.INDEX_NAME || 'hotels-sample';

    console.log("🌊 Azure AI Search - Large Result Sets Handling");
    console.log("=".repeat(50));

    // Initialize handler
    const handler = new LargeResultSetHandler(endpoint, indexName, apiKey);

    try {
        // Example 1: Streaming results
        console.log("\n1. Streaming Results");
        console.log("-".repeat(20));

        let processedCount = 0;
        for await (const doc of handler.streamResults("*", 25, 100)) {
            processedCount++;
            if (processedCount <= 3) { // Show first 3 documents
                console.log(`   Document ${processedCount}: ${doc.hotelName || 'Unknown'}`);
            }
        }

        console.log(`Total streamed: ${processedCount} documents`);

        // Example 2: Batch processing with sentiment analysis
        console.log("\n2. Batch Processing - Sentiment Analysis");
        console.log("-".repeat(40));

        const sentimentResults = await handler.batchProcessResults(
            "hotel",
            analyzeSentimentBatch,
            20,
            100,
            true,
            3
        );

        if (sentimentResults.length > 0) {
            const totalPositive = sentimentResults.reduce((sum, r) => sum + (r.positive || 0), 0);
            const totalNegative = sentimentResults.reduce((sum, r) => sum + (r.negative || 0), 0);
            const totalNeutral = sentimentResults.reduce((sum, r) => sum + (r.neutral || 0), 0);
            const totalDocs = sentimentResults.reduce((sum, r) => sum + (r.batchSize || 0), 0);

            console.log(`Sentiment analysis results (${totalDocs} documents):`);
            console.log(`  Positive: ${totalPositive} (${(totalPositive/totalDocs*100).toFixed(1)}%)`);
            console.log(`  Negative: ${totalNegative} (${(totalNegative/totalDocs*100).toFixed(1)}%)`);
            console.log(`  Neutral: ${totalNeutral} (${(totalNeutral/totalDocs*100).toFixed(1)}%)`);
        }

        // Example 3: Parallel range search
        console.log("\n3. Parallel Range Search");
        console.log("-".repeat(26));

        const ranges = [
            { name: 'High Rating', filter: 'rating ge 4' },
            { name: 'Medium Rating', filter: 'rating ge 3 and rating lt 4' },
            { name: 'Low Rating', filter: 'rating lt 3' }
        ];

        const rangeResults = await handler.parallelRangeSearch("hotel", ranges, 30);

        Object.entries(rangeResults).forEach(([rangeName, docs]) => {
            console.log(`  ${rangeName}: ${docs.length} results`);
            if (docs.length > 0) {
                const avgRating = docs.reduce((sum, doc) => sum + (doc.rating || 0), 0) / docs.length;
                console.log(`    Average rating: ${avgRating.toFixed(2)}`);
            }
        });

        // Example 4: Memory-efficient export
        console.log("\n4. Memory-Efficient Export");
        console.log("-".repeat(27));

        const outputFile = "large_results_export.jsonl";
        const exportStats = await handler.memoryEfficientExport(
            "luxury",
            outputFile,
            50,
            'jsonl'
        );

        if (!exportStats.error) {
            console.log("Export completed:");
            console.log(`  Documents: ${exportStats.exportedCount}`);
            console.log(`  File size: ${exportStats.fileSizeMb.toFixed(2)} MB`);
            console.log(`  Throughput: ${exportStats.throughputDocsPerSec.toFixed(1)} docs/sec`);

            // Clean up
            const fs = require('fs');
            if (fs.existsSync(outputFile)) {
                fs.unlinkSync(outputFile);
                console.log(`  Cleaned up: ${outputFile}`);
            }
        }

        // Show final statistics
        console.log("\n📊 Processing Statistics");
        console.log("-".repeat(24));

        const stats = handler.getProcessingStats();
        console.log(`Total processed: ${stats.totalProcessed}`);
        console.log(`Total batches: ${stats.batchCount}`);
        console.log(`Errors: ${stats.errors}`);
        console.log(`Throughput: ${stats.throughputDocsPerSec.toFixed(1)} docs/sec`);

        console.log("\n✅ Large result set handling demonstration completed!");

    } catch (error) {
        console.error("❌ Error during processing:", error.message);
    }
}

// Export for use as module
module.exports = { LargeResultSetHandler, ProcessingStats };

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}