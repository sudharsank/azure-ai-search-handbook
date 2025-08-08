/**
 * Simple Text Search - Module 2 JavaScript Examples
 * Basic text search operations in Azure AI Search using JavaScript SDK
 * 
 * This module demonstrates:
 * - Simple text queries
 * - Basic result handling
 * - Search client initialization
 * - Understanding search scores
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

class SimpleTextSearch {
    /**
     * Initialize with a search client
     * @param {SearchClient} searchClient - Azure Search client
     */
    constructor(searchClient) {
        if (!searchClient) {
            throw new Error('SearchClient is required');
        }
        this.searchClient = searchClient;
    }

    /**
     * Perform a basic text search
     * @param {string} query - Search query string
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async basicSearch(query, top = 10) {
        try {
            console.log(`Performing basic search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            // Convert results to array for easier handling
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in basic search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search with a specific result limit
     * @param {string} query - Search query string
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async searchWithLimit(query, top = 5) {
        return await this.basicSearch(query, top);
    }

    /**
     * Get all documents in the index (useful for browsing)
     * @param {number} top - Maximum number of documents to return
     * @returns {Promise<Object>} All documents
     */
    async getAllDocuments(top = 20) {
        try {
            console.log('Retrieving all documents');

            const searchOptions = {
                top: top
            };

            // Use "*" to match all documents
            const results = await this.searchClient.search('*', searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Retrieved ${resultArray.length} documents`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error retrieving all documents: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Display search results in a readable format
     * @param {Object} searchResults - Search results object
     * @param {boolean} showScores - Whether to display search scores
     */
    static displayResults(searchResults, showScores = true) {
        const { results } = searchResults;
        
        if (!results || results.length === 0) {
            console.log('No results found.');
            return;
        }

        console.log('\n' + '='.repeat(60));
        console.log(`SEARCH RESULTS (${results.length} found)`);
        console.log('='.repeat(60));

        results.forEach((result, index) => {
            const document = result.document;
            const title = document.title || 'Untitled';
            
            console.log(`\n${index + 1}. ${title}`);

            if (showScores && result.score !== undefined) {
                console.log(`   Score: ${result.score.toFixed(3)}`);
            }

            const author = document.author;
            if (author && author !== 'Unknown') {
                console.log(`   Author: ${author}`);
            }

            const content = document.content || '';
            if (content) {
                const preview = content.length > 150 ? content.substring(0, 150) + '...' : content;
                console.log(`   Preview: ${preview}`);
            }

            const url = document.url;
            if (url && url !== '#') {
                console.log(`   URL: ${url}`);
            }

            console.log(`   ${'-'.repeat(50)}`);
        });
    }

    /**
     * Analyze search scores to understand result quality
     * @param {Object} searchResults - Search results object
     * @returns {Object} Score statistics
     */
    static analyzeScores(searchResults) {
        const { results } = searchResults;
        
        if (!results || results.length === 0) {
            return {};
        }

        const scores = results
            .filter(result => result.score !== undefined)
            .map(result => result.score);

        if (scores.length === 0) {
            return {};
        }

        const minScore = Math.min(...scores);
        const maxScore = Math.max(...scores);
        const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;

        return {
            totalResults: scores.length,
            minScore: minScore,
            maxScore: maxScore,
            avgScore: avgScore,
            scoreRange: maxScore - minScore
        };
    }
}

/**
 * Demonstrate simple text search operations
 */
async function demonstrateSimpleSearch() {
    console.log('🔍 Simple Text Search Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new SimpleTextSearch(searchClient);

        // Example 1: Basic search
        console.log('\n1️⃣ Basic Text Search');
        console.log('-'.repeat(30));

        const query = 'python programming';
        const results = await searchOps.basicSearch(query, 5);
        SimpleTextSearch.displayResults(results);

        // Analyze the results
        if (results.results.length > 0) {
            const stats = SimpleTextSearch.analyzeScores(results);
            console.log('\n📊 Score Analysis:');
            console.log(`   Total results: ${stats.totalResults}`);
            console.log(`   Score range: ${stats.minScore.toFixed(3)} - ${stats.maxScore.toFixed(3)}`);
            console.log(`   Average score: ${stats.avgScore.toFixed(3)}`);
        }

        // Example 2: Different query
        console.log('\n' + '='.repeat(60));
        console.log('\n2️⃣ Another Search Example');
        console.log('-'.repeat(30));

        const query2 = 'machine learning';
        const results2 = await searchOps.basicSearch(query2, 3);
        SimpleTextSearch.displayResults(results2);

        // Example 3: Browse all documents
        console.log('\n' + '='.repeat(60));
        console.log('\n3️⃣ Browse All Documents');
        console.log('-'.repeat(30));

        const allDocs = await searchOps.getAllDocuments(5);
        console.log(`Total documents available: ${allDocs.results.length}`);

        if (allDocs.results.length > 0) {
            console.log('\nFirst few documents:');
            allDocs.results.slice(0, 3).forEach((doc, index) => {
                const title = doc.document.title || 'Untitled';
                const author = doc.document.author || 'Unknown';
                console.log(`  ${index + 1}. ${title} by ${author}`);
            });
        }

        console.log('\n✅ Simple text search demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
        console.log('Make sure your Azure AI Search service is configured correctly.');
    }
}

/**
 * Interactive example for users to try different queries
 */
async function interactiveSearchExample() {
    console.log('\n🎮 Interactive Search Example');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new SimpleTextSearch(searchClient);

        // Sample queries for demonstration
        const sampleQueries = [
            'web development',
            'tutorial',
            'javascript',
            'data science',
            'artificial intelligence'
        ];

        console.log('Here are some sample queries you can try:');
        sampleQueries.forEach((query, index) => {
            console.log(`  ${index + 1}. ${query}`);
        });

        // For demonstration, let's try the first query
        const demoQuery = sampleQueries[0];
        console.log(`\n🔍 Trying query: '${demoQuery}'`);
        console.log('-'.repeat(40));

        const results = await searchOps.basicSearch(demoQuery, 3);
        SimpleTextSearch.displayResults(results, true);

        if (results.results.length > 0) {
            const stats = SimpleTextSearch.analyzeScores(results);
            console.log('\n💡 Tips for interpreting results:');
            console.log(`   - Higher scores (closer to ${stats.maxScore.toFixed(1)}) indicate better matches`);
            console.log('   - Scores below 1.0 might indicate weaker relevance');
            console.log('   - Try different keywords if results aren\'t relevant');
        }

    } catch (error) {
        console.error(`❌ Interactive demo failed: ${error.message}`);
    }
}

// Main execution
async function main() {
    try {
        await demonstrateSimpleSearch();
        await interactiveSearchExample();

        console.log('\n💡 Next Steps:');
        console.log('   - Try modifying the queries above');
        console.log('   - Experiment with different search terms');
        console.log('   - Check out 02_phrase_search.js for exact phrase matching');
        console.log('   - Learn about boolean searches in 03_boolean_search.js');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    SimpleTextSearch,
    demonstrateSimpleSearch,
    interactiveSearchExample
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}