/**
 * Result Processing - Module 2 JavaScript Examples
 * Processing and formatting search results from Azure AI Search
 * 
 * This module demonstrates:
 * - Basic result processing
 * - Result formatting for display
 * - Score analysis
 * - Result filtering and sorting
 * - Export capabilities
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
const fs = require('fs').promises;

/**
 * Simple structure for processed search results
 */
class ProcessedResult {
    constructor(title, score, author, contentPreview, url) {
        this.title = title || 'Untitled';
        this.score = score || 0.0;
        this.author = author || 'Unknown';
        this.contentPreview = contentPreview || 'No content available';
        this.url = url || '#';
    }

    /**
     * Convert to plain object
     * @returns {Object} Plain object representation
     */
    toObject() {
        return {
            title: this.title,
            score: this.score,
            author: this.author,
            contentPreview: this.contentPreview,
            url: this.url
        };
    }
}

/**
 * Class for processing search results
 */
class ResultProcessor {
    /**
     * Initialize the result processor
     * @param {number} maxContentLength - Maximum length for content previews
     */
    constructor(maxContentLength = 150) {
        this.maxContentLength = maxContentLength;
    }

    /**
     * Convert raw search results to ProcessedResult objects
     * @param {Array} rawResults - Array of raw search results
     * @returns {Array<ProcessedResult>} Array of ProcessedResult objects
     */
    processRawResults(rawResults) {
        const processedResults = [];

        for (const result of rawResults) {
            try {
                const document = result.document || {};

                // Extract and clean fields
                const title = document.title || 'Untitled';
                const score = result.score || 0.0;
                const author = document.author || 'Unknown';
                const url = document.url || '#';

                // Create content preview
                const content = document.content || '';
                const contentPreview = this.createPreview(content);

                const processedResult = new ProcessedResult(
                    title, score, author, contentPreview, url
                );

                processedResults.push(processedResult);

            } catch (error) {
                console.error(`Error processing result: ${error.message}`);
                continue;
            }
        }

        return processedResults;
    }

    /**
     * Create a content preview with appropriate length
     * @param {string} content - Full content text
     * @returns {string} Preview text
     */
    createPreview(content) {
        if (!content) {
            return 'No content available';
        }

        if (content.length <= this.maxContentLength) {
            return content;
        }

        // Find a good breaking point
        let preview = content.substring(0, this.maxContentLength);
        const lastSpace = preview.lastIndexOf(' ');

        if (lastSpace > this.maxContentLength * 0.8) {
            preview = preview.substring(0, lastSpace);
        }

        return preview + '...';
    }

    /**
     * Format results for console display
     * @param {Array<ProcessedResult>} results - Array of ProcessedResult objects
     * @returns {string} Formatted string for display
     */
    formatForDisplay(results) {
        if (!results || results.length === 0) {
            return 'No results found.';
        }

        const output = [];
        output.push('');
        output.push('='.repeat(60));
        output.push(`SEARCH RESULTS (${results.length} found)`);
        output.push('='.repeat(60));

        results.forEach((result, index) => {
            output.push(`\n${index + 1}. ${result.title}`);
            output.push(`   Score: ${result.score.toFixed(3)}`);

            if (result.author !== 'Unknown') {
                output.push(`   Author: ${result.author}`);
            }

            if (result.contentPreview && result.contentPreview !== 'No content available') {
                output.push(`   Preview: ${result.contentPreview}`);
            }

            if (result.url !== '#') {
                output.push(`   URL: ${result.url}`);
            }

            output.push(`   ${'-'.repeat(50)}`);
        });

        return output.join('\n');
    }

    /**
     * Sort results by score
     * @param {Array<ProcessedResult>} results - Results to sort
     * @param {boolean} descending - Sort in descending order
     * @returns {Array<ProcessedResult>} Sorted results
     */
    sortByScore(results, descending = true) {
        return [...results].sort((a, b) => {
            return descending ? b.score - a.score : a.score - b.score;
        });
    }

    /**
     * Filter results by minimum score
     * @param {Array<ProcessedResult>} results - Results to filter
     * @param {number} minScore - Minimum score threshold
     * @returns {Array<ProcessedResult>} Filtered results
     */
    filterByScore(results, minScore) {
        return results.filter(result => result.score >= minScore);
    }

    /**
     * Analyze score distribution
     * @param {Array<ProcessedResult>} results - Results to analyze
     * @returns {Object} Score statistics
     */
    analyzeScores(results) {
        if (!results || results.length === 0) {
            return {};
        }

        const scores = results.map(result => result.score);

        const minScore = Math.min(...scores);
        const maxScore = Math.max(...scores);
        const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;

        return {
            count: scores.length,
            minScore: minScore,
            maxScore: maxScore,
            avgScore: avgScore,
            scoreRange: maxScore - minScore
        };
    }

    /**
     * Export results to JSON file
     * @param {Array<ProcessedResult>} results - Results to export
     * @param {string} filename - Output filename
     */
    async exportToJson(results, filename) {
        try {
            const resultsArray = results.map(result => result.toObject());
            const json = JSON.stringify(resultsArray, null, 2);
            
            await fs.writeFile(filename, json, 'utf8');
            console.log(`✅ Results exported to ${filename}`);

        } catch (error) {
            console.error(`❌ Error exporting to JSON: ${error.message}`);
        }
    }
}

/**
 * Demonstrate result processing capabilities
 */
async function demonstrateResultProcessing() {
    console.log('🔧 Result Processing Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        // Get some sample results
        const searchOptions = { top: 5 };
        const rawResults = await searchClient.search('python programming', searchOptions);

        const rawResultArray = [];
        for await (const result of rawResults.results) {
            rawResultArray.push(result);
        }

        if (rawResultArray.length === 0) {
            console.log('❌ No results found for demo. Make sure your index has data.');
            return;
        }

        // Process results
        const processor = new ResultProcessor();
        const processedResults = processor.processRawResults(rawResultArray);

        console.log(`✅ Processed ${processedResults.length} results`);

        // Display formatted results
        const formattedOutput = processor.formatForDisplay(processedResults.slice(0, 3));
        console.log(formattedOutput);

        // Analyze scores
        const stats = processor.analyzeScores(processedResults);
        console.log('\n📊 Score Analysis:');
        console.log(`   Total results: ${stats.count}`);
        console.log(`   Score range: ${stats.minScore.toFixed(3)} - ${stats.maxScore.toFixed(3)}`);
        console.log(`   Average score: ${stats.avgScore.toFixed(3)}`);

        // Filter high-quality results
        const highQuality = processor.filterByScore(processedResults, 1.0);
        console.log(`\n🎯 High-quality results (score ≥ 1.0): ${highQuality.length}`);

        // Export to JSON
        await processor.exportToJson(processedResults, 'sample_results.json');

        console.log('\n✅ Result processing demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
    }
}

/**
 * Show result processing best practices
 */
function resultProcessingBestPractices() {
    console.log('\n📚 Result Processing Best Practices');
    console.log('='.repeat(50));

    console.log('\n💡 Processing Guidelines:');
    console.log('   ✅ Always handle missing or null fields gracefully');
    console.log('   ✅ Create meaningful content previews');
    console.log('   ✅ Normalize and clean data consistently');
    console.log('   ✅ Provide fallback values for missing data');

    console.log('\n📊 Score Analysis Tips:');
    console.log('   ✅ Understand your score distribution');
    console.log('   ✅ Set appropriate quality thresholds');
    console.log('   ✅ Monitor score patterns over time');
    console.log('   ✅ Use scores to improve search relevance');

    console.log('\n🎨 Display Formatting:');
    console.log('   ✅ Keep previews concise but informative');
    console.log('   ✅ Highlight important information');
    console.log('   ✅ Provide consistent formatting');
    console.log('   ✅ Make results scannable');

    console.log('\n💾 Export Considerations:');
    console.log('   ✅ Choose appropriate export formats');
    console.log('   ✅ Handle large result sets efficiently');
    console.log('   ✅ Include metadata in exports');
    console.log('   ✅ Validate exported data');
}

// Main execution
async function main() {
    try {
        await demonstrateResultProcessing();
        resultProcessingBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Try processing results from different searches');
        console.log('   - Experiment with different filtering criteria');
        console.log('   - Check out 07_error_handling.js for robust error handling');
        console.log('   - Learn about search patterns in 08_search_patterns.js');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    ProcessedResult,
    ResultProcessor,
    demonstrateResultProcessing,
    resultProcessingBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}