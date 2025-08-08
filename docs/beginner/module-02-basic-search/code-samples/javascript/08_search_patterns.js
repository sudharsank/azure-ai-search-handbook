/**
 * Search Patterns - Module 2 JavaScript Examples
 * Common search patterns and strategies in Azure AI Search
 * 
 * This module demonstrates:
 * - Progressive search strategies
 * - Search with fallback
 * - Multi-strategy search
 * - Search pattern best practices
 * - When to use different patterns
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

/**
 * Class demonstrating common search patterns
 */
class SearchPatterns {
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
     * Progressive search from specific to broad
     * @param {string} query - Base search query
     * @param {number} top - Maximum results per strategy
     * @returns {Promise<Object>} Object mapping strategy names to results
     */
    async progressiveSearch(query, top = 10) {
        const strategies = {};

        // 1. Exact phrase (most specific)
        try {
            const exactOptions = { top: top };
            const exactResults = await this.searchClient.search(`"${query}"`, exactOptions);
            
            const exactArray = [];
            for await (const result of exactResults.results) {
                exactArray.push(result);
            }
            
            strategies.exact_phrase = exactArray;
            console.log(`Exact phrase: ${exactArray.length} results`);
        } catch (error) {
            console.error(`Exact phrase search failed: ${error.message}`);
            strategies.exact_phrase = [];
        }

        // 2. All terms (moderate specificity)
        try {
            const allTermsOptions = { 
                top: top,
                searchMode: 'all'
            };
            const allTermsResults = await this.searchClient.search(query, allTermsOptions);
            
            const allTermsArray = [];
            for await (const result of allTermsResults.results) {
                allTermsArray.push(result);
            }
            
            strategies.all_terms = allTermsArray;
            console.log(`All terms: ${allTermsArray.length} results`);
        } catch (error) {
            console.error(`All terms search failed: ${error.message}`);
            strategies.all_terms = [];
        }

        // 3. Any terms (broad)
        try {
            const anyTermsOptions = { 
                top: top,
                searchMode: 'any'
            };
            const anyTermsResults = await this.searchClient.search(query, anyTermsOptions);
            
            const anyTermsArray = [];
            for await (const result of anyTermsResults.results) {
                anyTermsArray.push(result);
            }
            
            strategies.any_terms = anyTermsArray;
            console.log(`Any terms: ${anyTermsArray.length} results`);
        } catch (error) {
            console.error(`Any terms search failed: ${error.message}`);
            strategies.any_terms = [];
        }

        // 4. Wildcard (broadest)
        try {
            const terms = query.split(/\s+/).filter(term => term.length > 0);
            const wildcardQuery = terms.map(term => `${term}*`).join(' OR ');
            
            const wildcardOptions = { top: top };
            const wildcardResults = await this.searchClient.search(wildcardQuery, wildcardOptions);
            
            const wildcardArray = [];
            for await (const result of wildcardResults.results) {
                wildcardArray.push(result);
            }
            
            strategies.wildcard = wildcardArray;
            console.log(`Wildcard: ${wildcardArray.length} results`);
        } catch (error) {
            console.error(`Wildcard search failed: ${error.message}`);
            strategies.wildcard = [];
        }

        return strategies;
    }

    /**
     * Search with automatic fallback to broader strategies
     * @param {string} query - Search query
     * @param {number} top - Maximum results to return
     * @returns {Promise<Array>} Array of search results from first successful strategy
     */
    async searchWithFallback(query, top = 10) {
        // Try strategies in order of specificity
        const strategies = [
            { 
                query: `"${query}"`, 
                name: 'exact phrase',
                options: { top: top }
            },
            { 
                query: query, 
                name: 'all terms (default)',
                options: { top: top }
            },
            { 
                query: query, 
                name: 'any terms',
                options: { top: top, searchMode: 'any' }
            },
            { 
                query: query.split(/\s+/).filter(term => term.length > 0).map(term => `${term}*`).join(' OR '), 
                name: 'wildcard',
                options: { top: top }
            }
        ];

        for (const strategy of strategies) {
            try {
                const results = await this.searchClient.search(strategy.query, strategy.options);
                const resultArray = [];
                
                for await (const result of results.results) {
                    resultArray.push(result);
                }

                if (resultArray.length > 0) {
                    console.log(`Found ${resultArray.length} results using ${strategy.name}`);
                    return resultArray;
                } else {
                    console.log(`No results with ${strategy.name}, trying next strategy`);
                }
            } catch (error) {
                console.error(`Error with ${strategy.name}: ${error.message}`);
                continue;
            }
        }

        console.log('No results found with any search strategy');
        return [];
    }

    /**
     * Search across fields in order of priority
     * @param {string} query - Search query
     * @param {Array<string>} fieldPriority - Array of fields in priority order
     * @param {number} top - Maximum results to return
     * @returns {Promise<Array>} Combined results from all fields
     */
    async multiFieldSearch(query, fieldPriority, top = 10) {
        const allResults = [];
        const seenIds = new Set();

        for (const field of fieldPriority) {
            try {
                const fieldOptions = { 
                    top: top,
                    searchFields: [field]
                };
                
                const fieldResults = await this.searchClient.search(query, fieldOptions);
                let fieldCount = 0;

                for await (const result of fieldResults.results) {
                    const resultId = result.document.id || JSON.stringify(result.document);

                    if (!seenIds.has(resultId)) {
                        seenIds.add(resultId);
                        allResults.push(result);
                    }
                    fieldCount++;
                }

                console.log(`Field '${field}': found ${fieldCount} results`);
            } catch (error) {
                console.error(`Error searching field '${field}': ${error.message}`);
                continue;
            }
        }

        // Sort by score and limit results
        allResults.sort((a, b) => (b.score || 0) - (a.score || 0));
        return allResults.slice(0, top);
    }

    /**
     * Display results from progressive search
     * @param {string} query - Original query
     * @param {Object} strategies - Results from different strategies
     */
    displayProgressiveResults(query, strategies) {
        console.log(`\n🔄 Progressive Search Results: '${query}'`);
        console.log('='.repeat(60));

        const strategyInfo = {
            exact_phrase: {
                displayName: 'Exact Phrase',
                description: 'Most specific - exact phrase match'
            },
            all_terms: {
                displayName: 'All Terms',
                description: 'Moderate - all terms must be present'
            },
            any_terms: {
                displayName: 'Any Terms',
                description: 'Broad - any terms can be present'
            },
            wildcard: {
                displayName: 'Wildcard',
                description: 'Broadest - partial term matching'
            }
        };

        for (const [strategyName, results] of Object.entries(strategies)) {
            const info = strategyInfo[strategyName];
            if (info) {
                console.log(`\n${info.displayName}:`);
                console.log(`   Description: ${info.description}`);
                console.log(`   Results: ${results.length} found`);

                if (results.length > 0) {
                    console.log('   Top matches:');
                    results.slice(0, 3).forEach((result, index) => {
                        const title = result.document.title || 'No title';
                        const score = result.score || 0.0;
                        console.log(`     ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
                    });
                } else {
                    console.log('   No matches found');
                }

                console.log('-'.repeat(40));
            }
        }

        // Recommendation
        console.log('\n💡 RECOMMENDATION:');
        for (const [strategyName, results] of Object.entries(strategies)) {
            if (results.length > 0) {
                const info = strategyInfo[strategyName];
                if (info) {
                    console.log(`   Use '${info.displayName}' - found ${results.length} relevant results`);
                    break;
                }
            }
        }

        const hasResults = Object.values(strategies).some(results => results.length > 0);
        if (!hasResults) {
            console.log('   Try different search terms or check your data');
        }
    }
}

/**
 * Demonstrate search patterns
 */
async function demonstrateSearchPatterns() {
    console.log('🎯 Search Patterns Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const patterns = new SearchPatterns(searchClient);

        // Example 1: Progressive search
        console.log('\n1️⃣ Progressive Search Strategy');

        const query = 'machine learning';
        const progressiveResults = await patterns.progressiveSearch(query, 5);
        patterns.displayProgressiveResults(query, progressiveResults);

        // Example 2: Search with fallback
        console.log('\n' + '='.repeat(70));
        console.log('\n2️⃣ Search with Automatic Fallback');
        console.log('-'.repeat(40));

        const fallbackQuery = 'artificial intelligence tutorial';
        const fallbackResults = await patterns.searchWithFallback(fallbackQuery, 5);

        console.log(`Query: '${fallbackQuery}'`);
        console.log(`Results with fallback: ${fallbackResults.length} found`);

        if (fallbackResults.length > 0) {
            console.log('Top results:');
            fallbackResults.slice(0, 3).forEach((result, index) => {
                const title = result.document.title || 'No title';
                const score = result.score || 0.0;
                console.log(`  ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
            });
        }

        // Example 3: Multi-field search
        console.log('\n' + '='.repeat(70));
        console.log('\n3️⃣ Multi-Field Priority Search');
        console.log('-'.repeat(40));

        const fieldPriority = ['title', 'description', 'content', 'tags'];
        const multiFieldQuery = 'python';

        const multiResults = await patterns.multiFieldSearch(multiFieldQuery, fieldPriority, 5);

        console.log(`Query: '${multiFieldQuery}'`);
        console.log(`Field priority: ${fieldPriority.join(' > ')}`);
        console.log(`Combined results: ${multiResults.length} found`);

        if (multiResults.length > 0) {
            console.log('Top combined results:');
            multiResults.slice(0, 3).forEach((result, index) => {
                const title = result.document.title || 'No title';
                const score = result.score || 0.0;
                console.log(`  ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
            });
        }

        console.log('\n✅ Search patterns demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
    }
}

/**
 * Display search pattern best practices
 */
function searchPatternBestPractices() {
    console.log('\n📚 Search Pattern Best Practices');
    console.log('='.repeat(50));

    console.log('\n💡 When to Use Each Pattern:');

    console.log('\n🎯 Progressive Search:');
    console.log('   ✅ When you want comprehensive coverage');
    console.log('   ✅ For user-facing search interfaces');
    console.log('   ✅ When result quality is more important than speed');
    console.log('   ✅ For exploratory or research searches');

    console.log('\n🔄 Fallback Search:');
    console.log('   ✅ When you need guaranteed results');
    console.log('   ✅ For automated systems');
    console.log('   ✅ When speed is important');
    console.log('   ✅ For simple search interfaces');

    console.log('\n🏗️ Multi-Field Search:');
    console.log('   ✅ When different fields have different importance');
    console.log('   ✅ For structured data with clear field hierarchy');
    console.log('   ✅ When you want to avoid duplicates');
    console.log('   ✅ For content with rich metadata');

    console.log('\n⚠️ Pattern Selection Guidelines:');
    console.log('   🔍 Start simple, add complexity as needed');
    console.log('   📊 Monitor which patterns work best for your data');
    console.log('   ⚡ Consider performance implications');
    console.log('   👥 Think about user expectations');

    console.log('\n🔧 Implementation Tips:');
    console.log('   ✅ Cache results from expensive pattern searches');
    console.log('   ✅ Log which patterns are most successful');
    console.log('   ✅ Allow users to choose search modes');
    console.log('   ✅ Provide feedback about search strategy used');

    console.log('\n🚀 Performance Considerations:');
    console.log('   ✅ Use async/await for better performance');
    console.log('   ✅ Implement proper error handling');
    console.log('   ✅ Consider result caching strategies');
    console.log('   ✅ Monitor search latency and adjust patterns');
}

// Main execution
async function main() {
    try {
        await demonstrateSearchPatterns();
        searchPatternBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Try different search patterns with your data');
        console.log('   - Experiment with combining patterns');
        console.log('   - Consider which patterns work best for your use case');
        console.log('   - Review all JavaScript examples to build complete search functionality');
        console.log('   - Check out other language examples in ../python/, ../csharp/, etc.');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    SearchPatterns,
    demonstrateSearchPatterns,
    searchPatternBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}