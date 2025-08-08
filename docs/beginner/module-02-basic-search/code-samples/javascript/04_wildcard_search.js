/**
 * Wildcard Search - Module 2 JavaScript Examples
 * Pattern matching with wildcards in Azure AI Search using JavaScript SDK
 * 
 * This module demonstrates:
 * - Prefix matching with *
 * - Suffix matching with *
 * - Pattern matching strategies
 * - When to use wildcards
 * - Wildcard search limitations
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

class WildcardSearch {
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
     * Search for terms starting with a prefix (prefix*)
     * @param {string} prefix - The prefix to search for
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async prefixSearch(prefix, top = 10) {
        try {
            const query = `${prefix}*`;
            console.log(`Performing prefix search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results with prefix '${prefix}'`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in prefix search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search for terms ending with a suffix (*suffix)
     * @param {string} suffix - The suffix to search for
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async suffixSearch(suffix, top = 10) {
        try {
            const query = `*${suffix}`;
            console.log(`Performing suffix search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results with suffix '${suffix}'`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in suffix search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search for terms containing a substring (*substring*)
     * @param {string} substring - The substring to search for
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async containsSearch(substring, top = 10) {
        try {
            const query = `*${substring}*`;
            console.log(`Performing contains search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results containing '${substring}'`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in contains search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search for multiple wildcard patterns
     * @param {Array<string>} patterns - List of wildcard patterns to search for
     * @param {number} top - Maximum results per pattern
     * @returns {Promise<Object>} Object mapping patterns to their results
     */
    async multipleWildcardSearch(patterns, top = 5) {
        const results = {};

        for (const pattern of patterns) {
            try {
                console.log(`Searching for pattern: '${pattern}'`);

                const searchOptions = {
                    top: top,
                    includeTotalCount: true
                };

                const searchResults = await this.searchClient.search(pattern, searchOptions);
                
                const resultArray = [];
                for await (const result of searchResults.results) {
                    resultArray.push(result);
                }

                results[pattern] = {
                    results: resultArray,
                    totalCount: searchResults.count
                };
            } catch (error) {
                console.error(`Error searching pattern '${pattern}': ${error.message}`);
                results[pattern] = { results: [], totalCount: 0 };
            }
        }

        return results;
    }

    /**
     * Compare different wildcard patterns for the same base term
     * @param {string} baseTerm - Base term to create patterns from
     * @param {number} top - Maximum results per pattern
     * @returns {Promise<Object>} Object mapping pattern types to their results
     */
    async compareWildcardPatterns(baseTerm, top = 5) {
        const patterns = {
            'exact': baseTerm,
            'prefix': `${baseTerm}*`,
            'suffix': `*${baseTerm}`,
            'contains': `*${baseTerm}*`
        };

        const results = {};

        for (const [patternType, pattern] of Object.entries(patterns)) {
            try {
                const searchOptions = {
                    top: top,
                    includeTotalCount: true
                };

                const searchResults = await this.searchClient.search(pattern, searchOptions);
                
                const resultArray = [];
                for await (const result of searchResults.results) {
                    resultArray.push(result);
                }

                results[patternType] = {
                    results: resultArray,
                    totalCount: searchResults.count
                };
            } catch (error) {
                console.error(`Error in ${patternType} search: ${error.message}`);
                results[patternType] = { results: [], totalCount: 0 };
            }
        }

        return results;
    }

    /**
     * Display comparison of wildcard patterns
     * @param {string} baseTerm - Base term used for patterns
     * @param {Object} results - Results from different wildcard patterns
     */
    static displayWildcardComparison(baseTerm, results) {
        console.log(`\n🃏 Wildcard Patterns Comparison: '${baseTerm}'`);
        console.log('='.repeat(60));

        const patternInfo = {
            'exact': ['Exact Match', baseTerm, 'Exact term only'],
            'prefix': ['Prefix Match', `${baseTerm}*`, `Terms starting with "${baseTerm}"`],
            'suffix': ['Suffix Match', `*${baseTerm}`, `Terms ending with "${baseTerm}"`],
            'contains': ['Contains Match', `*${baseTerm}*`, `Terms containing "${baseTerm}"`]
        };

        for (const [patternType, patternResults] of Object.entries(results)) {
            if (patternInfo[patternType]) {
                const [name, pattern, description] = patternInfo[patternType];

                console.log(`\n${name}:`);
                console.log(`   Pattern: ${pattern}`);
                console.log(`   Description: ${description}`);
                console.log(`   Results found: ${patternResults.results.length}`);

                if (patternResults.results.length > 0) {
                    console.log('   Top matches:');
                    patternResults.results.slice(0, 3).forEach((result, index) => {
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

        // Analysis
        console.log(`\n📊 PATTERN ANALYSIS:`);
        const exactCount = results.exact?.results.length || 0;
        const prefixCount = results.prefix?.results.length || 0;
        const suffixCount = results.suffix?.results.length || 0;
        const containsCount = results.contains?.results.length || 0;

        console.log(`   Exact: ${exactCount} (most specific)`);
        console.log(`   Prefix: ${prefixCount}`);
        console.log(`   Suffix: ${suffixCount}`);
        console.log(`   Contains: ${containsCount} (broadest)`);

        if (containsCount >= Math.max(prefixCount, suffixCount) && 
            Math.max(prefixCount, suffixCount) >= exactCount) {
            console.log('   ✅ Expected pattern: Contains ≥ Prefix/Suffix ≥ Exact');
        } else {
            console.log('   ⚠️ Unexpected pattern - depends on your data');
        }
    }
}

/**
 * Demonstrate wildcard search operations
 */
async function demonstrateWildcardSearch() {
    console.log('🃏 Wildcard Search Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new WildcardSearch(searchClient);

        // Example 1: Compare wildcard patterns
        console.log('\n1️⃣ Wildcard Patterns Comparison');

        const baseTerm = 'program';
        const wildcardResults = await searchOps.compareWildcardPatterns(baseTerm, 5);
        WildcardSearch.displayWildcardComparison(baseTerm, wildcardResults);

        // Example 2: Practical wildcard searches
        console.log('\n' + '='.repeat(70));
        console.log('\n2️⃣ Practical Wildcard Examples');
        console.log('-'.repeat(30));

        const practicalExamples = [
            { description: 'Find programming languages', pattern: 'program*', type: 'prefix' },
            { description: 'Find development terms', pattern: '*develop*', type: 'contains' },
            { description: 'Find tutorial content', pattern: '*tutorial', type: 'suffix' },
            { description: 'Find JavaScript variations', pattern: 'java*', type: 'prefix' }
        ];

        for (const example of practicalExamples) {
            console.log(`\n📋 ${example.description}`);
            console.log(`   Pattern: ${example.pattern} (${example.type})`);

            let results;
            switch (example.type) {
                case 'prefix':
                    results = await searchOps.prefixSearch(example.pattern.slice(0, -1), 3);
                    break;
                case 'suffix':
                    results = await searchOps.suffixSearch(example.pattern.slice(1), 3);
                    break;
                case 'contains':
                    results = await searchOps.containsSearch(example.pattern.slice(1, -1), 3);
                    break;
            }

            console.log(`   Results: ${results.results.length} found`);

            if (results.results.length > 0) {
                const topResult = results.results[0];
                const title = topResult.document.title || 'No title';
                const score = topResult.score || 0.0;
                console.log(`   Top match: ${title} (Score: ${score.toFixed(3)})`);
            }
        }

        // Example 3: Multiple wildcard search
        console.log('\n' + '='.repeat(70));
        console.log('\n3️⃣ Multiple Wildcard Search');
        console.log('-'.repeat(30));

        const wildcardPatterns = [
            'web*',      // web, website, webdev, etc.
            '*script',   // javascript, typescript, etc.
            '*data*',    // database, metadata, etc.
            'api*'       // api, apis, etc.
        ];

        const multiResults = await searchOps.multipleWildcardSearch(wildcardPatterns, 2);

        for (const [pattern, results] of Object.entries(multiResults)) {
            console.log(`\nPattern: ${pattern}`);
            console.log(`Results: ${results.results.length}`);
            
            if (results.results.length > 0) {
                results.results.forEach((result, index) => {
                    const title = result.document.title || 'No title';
                    const score = result.score || 0.0;
                    console.log(`  ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
                });
            }
        }

        console.log('\n✅ Wildcard search demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
        console.log('Make sure your Azure AI Search service is configured correctly.');
    }
}

/**
 * Demonstrate best practices for wildcard search
 */
async function wildcardSearchBestPractices() {
    console.log('\n📚 Wildcard Search Best Practices');
    console.log('='.repeat(50));

    console.log('\n💡 When to Use Wildcards:');
    console.log('\n✅ Prefix Search (term*):');
    console.log('   - Finding word variations (program, programming, programmer)');
    console.log('   - Technology families (java, javascript, javadoc)');
    console.log('   - Brand or product lines (micro, microsoft, microservice)');
    console.log('   - Language variations (develop, developer, development)');

    console.log('\n✅ Suffix Search (*term):');
    console.log('   - Finding words with common endings (*ing, *tion, *ment)');
    console.log('   - File types or extensions (*script, *doc)');
    console.log('   - Categories or types (*tutorial, *guide)');

    console.log('\n✅ Contains Search (*term*):');
    console.log('   - Finding partial matches when unsure of exact form');
    console.log('   - Searching within compound words');
    console.log('   - When you know a key part but not the whole term');

    console.log('\n⚠️ Wildcard Limitations:');
    console.log('   ❌ Can be slower than exact searches');
    console.log('   ❌ May return too many irrelevant results');
    console.log('   ❌ Leading wildcards (*term) are generally slower');
    console.log('   ❌ Multiple wildcards in one term can be very slow');

    console.log('\n🔧 Performance Tips:');
    console.log('   ✅ Use specific prefixes (at least 2-3 characters)');
    console.log('   ✅ Combine with other terms to narrow results');
    console.log('   ✅ Prefer prefix wildcards over suffix wildcards');
    console.log('   ✅ Test wildcard queries with small result sets first');

    // Demonstrate good vs bad practices
    console.log('\n🧪 Good vs Bad Wildcard Examples:');

    console.log('\n✅ Good Wildcard Practices:');
    const goodExamples = [
        ['program*', 'Specific prefix, likely to find relevant terms'],
        ['java* AND tutorial', 'Wildcard combined with specific term'],
        ['*development', 'Common suffix, reasonable scope']
    ];

    goodExamples.forEach(([pattern, explanation]) => {
        console.log(`   ${pattern}: ${explanation}`);
    });

    console.log('\n❌ Problematic Wildcard Practices:');
    const badExamples = [
        ['*a*', 'Too broad, will match almost everything'],
        ['*', 'Matches all documents, not useful for search'],
        ['*e*t*', 'Multiple wildcards, very slow']
    ];

    badExamples.forEach(([pattern, explanation]) => {
        console.log(`   ${pattern}: ${explanation}`);
    });

    // Show optimization example
    console.log('\n🚀 Optimization Example:');
    console.log('   Instead of: \'*script\'');
    console.log('   Try: \'javascript OR typescript OR script\'');
    console.log('   Benefit: More specific, faster, better relevance');
}

// Main execution
async function main() {
    try {
        await demonstrateWildcardSearch();
        await wildcardSearchBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Experiment with different wildcard patterns');
        console.log('   - Try combining wildcards with boolean operators');
        console.log('   - Check out 05_field_search.js for field-specific searches');
        console.log('   - Learn about search parameters in other examples');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    WildcardSearch,
    demonstrateWildcardSearch,
    wildcardSearchBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}