/**
 * Field-Specific Search - Module 2 JavaScript Examples
 * Searching within specific fields in Azure AI Search using JavaScript SDK
 * 
 * This module demonstrates:
 * - Searching specific fields
 * - Field selection for results
 * - Multi-field searches
 * - Field weighting concepts
 * - When to use field-specific search
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

class FieldSearch {
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
     * Search within a specific field only
     * @param {string} query - Search query string
     * @param {string} field - Field name to search in
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async searchSpecificField(query, field, top = 10) {
        try {
            console.log(`Searching field '${field}' for: '${query}'`);

            const searchOptions = {
                searchFields: [field],
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results in field '${field}'`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error searching field '${field}': ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search within multiple specific fields
     * @param {string} query - Search query string
     * @param {Array<string>} fields - List of field names to search in
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async searchMultipleFields(query, fields, top = 10) {
        try {
            console.log(`Searching fields [${fields.join(', ')}] for: '${query}'`);

            const searchOptions = {
                searchFields: fields,
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results in specified fields`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error searching multiple fields: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search and return only selected fields
     * @param {string} query - Search query string
     * @param {Array<string>} selectFields - List of field names to return in results
     * @param {Array<string>} searchFields - List of field names to search in (optional)
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results with only selected fields
     */
    async searchWithSelectedFields(query, selectFields, searchFields = null, top = 10) {
        try {
            console.log(`Searching for '${query}' with selected fields: [${selectFields.join(', ')}]`);

            const searchOptions = {
                select: selectFields,
                top: top,
                includeTotalCount: true
            };

            if (searchFields) {
                searchOptions.searchFields = searchFields;
            }

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results with selected fields`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in search with selected fields: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Compare search results across different fields
     * @param {string} query - Search query string
     * @param {Array<string>} fields - List of fields to compare
     * @param {number} top - Maximum results per field
     * @returns {Promise<Object>} Object mapping field names to their results
     */
    async compareFieldSearches(query, fields, top = 5) {
        const results = {};

        // Search all fields (default)
        try {
            const allResults = await this.searchClient.search(query, {
                top: top,
                includeTotalCount: true
            });
            
            const resultArray = [];
            for await (const result of allResults.results) {
                resultArray.push(result);
            }

            results['all_fields'] = {
                results: resultArray,
                totalCount: allResults.count
            };
        } catch (error) {
            console.error(`Error in all fields search: ${error.message}`);
            results['all_fields'] = { results: [], totalCount: 0 };
        }

        // Search individual fields
        for (const field of fields) {
            results[field] = await this.searchSpecificField(query, field, top);
        }

        return results;
    }

    /**
     * Display comparison of field-specific searches
     * @param {string} query - Original search query
     * @param {Object} results - Results from different field searches
     */
    static displayFieldComparison(query, results) {
        console.log(`\n🎯 Field-Specific Search Comparison: '${query}'`);
        console.log('='.repeat(70));

        for (const [fieldName, fieldResults] of Object.entries(results)) {
            const displayName = fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            console.log(`\n${displayName}:`);
            console.log(`   Results found: ${fieldResults.results.length}`);

            if (fieldResults.results.length > 0) {
                console.log('   Top matches:');
                fieldResults.results.slice(0, 3).forEach((result, index) => {
                    const title = result.document.title || 'No title';
                    const score = result.score || 0.0;
                    console.log(`     ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
                });

                // Show average score
                const avgScore = fieldResults.results.reduce((sum, r) => sum + (r.score || 0), 0) / fieldResults.results.length;
                console.log(`   Average score: ${avgScore.toFixed(3)}`);
            } else {
                console.log('   No matches found');
            }

            console.log('-'.repeat(50));
        }

        // Analysis
        console.log(`\n📊 FIELD ANALYSIS:`);
        for (const [fieldName, fieldResults] of Object.entries(results)) {
            const count = fieldResults.results.length;
            if (count > 0) {
                const maxScore = Math.max(...fieldResults.results.map(r => r.score || 0));
                console.log(`   ${fieldName}: ${count} results (max score: ${maxScore.toFixed(3)})`);
            } else {
                console.log(`   ${fieldName}: No results`);
            }
        }
    }
}

/**
 * Demonstrate field-specific search operations
 */
async function demonstrateFieldSearch() {
    console.log('🎯 Field-Specific Search Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new FieldSearch(searchClient);

        // Example 1: Compare field searches
        console.log('\n1️⃣ Field Search Comparison');

        const query = 'python';
        const commonFields = ['title', 'content', 'description', 'author'];

        const fieldResults = await searchOps.compareFieldSearches(query, commonFields, 5);
        FieldSearch.displayFieldComparison(query, fieldResults);

        // Example 2: Multi-field search
        console.log('\n' + '='.repeat(70));
        console.log('\n2️⃣ Multi-Field Search Examples');
        console.log('-'.repeat(30));

        const multiFieldExamples = [
            { description: 'Find tutorials by title or description', fields: ['title', 'description'] },
            { description: 'Search content and tags', fields: ['content', 'tags'] },
            { description: 'Author and title search', fields: ['author', 'title'] }
        ];

        for (const example of multiFieldExamples) {
            console.log(`\n📋 ${example.description}`);
            console.log(`   Fields: ${example.fields.join(', ')}`);

            const results = await searchOps.searchMultipleFields('tutorial', example.fields, 3);
            console.log(`   Results: ${results.results.length} found`);

            if (results.results.length > 0) {
                const topResult = results.results[0];
                const title = topResult.document.title || 'No title';
                const score = topResult.score || 0.0;
                console.log(`   Top match: ${title} (Score: ${score.toFixed(3)})`);
            }
        }

        // Example 3: Field selection
        console.log('\n' + '='.repeat(70));
        console.log('\n3️⃣ Field Selection Examples');
        console.log('-'.repeat(30));

        const selectionExamples = [
            { description: 'Basic info only', selectFields: ['id', 'title', 'author'] },
            { description: 'Content preview', selectFields: ['title', 'description', 'url'] },
            { description: 'Metadata only', selectFields: ['id', 'publishedDate', 'category'] }
        ];

        for (const example of selectionExamples) {
            console.log(`\n📋 ${example.description}`);
            console.log(`   Selected fields: ${example.selectFields.join(', ')}`);

            const results = await searchOps.searchWithSelectedFields(
                'programming', 
                example.selectFields, 
                null, 
                2
            );

            console.log(`   Results: ${results.results.length} found`);

            if (results.results.length > 0) {
                const firstResult = results.results[0];
                const availableFields = Object.keys(firstResult.document).filter(k => !k.startsWith('@'));
                console.log(`   Available fields in result: ${availableFields.join(', ')}`);
            }
        }

        console.log('\n✅ Field-specific search demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
        console.log('Make sure your Azure AI Search service is configured correctly.');
    }
}

/**
 * Demonstrate best practices for field-specific search
 */
async function fieldSearchBestPractices() {
    console.log('\n📚 Field-Specific Search Best Practices');
    console.log('='.repeat(50));

    console.log('\n💡 When to Use Field-Specific Search:');
    console.log('\n✅ Search Specific Fields When:');
    console.log('   - You know exactly which field contains relevant information');
    console.log('   - You want to search titles only (more precise)');
    console.log('   - You need to search metadata fields (author, category, etc.)');
    console.log('   - You want to exclude certain fields from search');

    console.log('\n✅ Select Specific Fields When:');
    console.log('   - You only need certain fields in results (faster)');
    console.log('   - You want to reduce network traffic');
    console.log('   - You\'re building a summary or preview');
    console.log('   - You need consistent result structure');

    console.log('\n⚠️ Field Search Considerations:');
    console.log('   ❌ Field names must exist in your index');
    console.log('   ❌ Searching fewer fields may miss relevant content');
    console.log('   ❌ Field-specific search can be less flexible');
    console.log('   ❌ Some fields might not be searchable');

    console.log('\n🔧 Performance Tips:');
    console.log('   ✅ Use field selection to reduce result size');
    console.log('   ✅ Search high-value fields first (title, description)');
    console.log('   ✅ Combine field search with other filters');
    console.log('   ✅ Test which fields give best results for your use case');

    // Demonstrate field strategy
    console.log('\n🎯 Field Search Strategy Example:');
    
    try {
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new FieldSearch(searchClient);
        const query = 'javascript tutorial';

        console.log(`\nQuery: '${query}'`);
        console.log('Strategy: Search from most specific to most general');

        // 1. Title only (most specific)
        const titleResults = await searchOps.searchSpecificField(query, 'title', 1);
        console.log(`\n1. Title only: ${titleResults.results.length} results`);

        // 2. Title + description (moderate)
        const titleDescResults = await searchOps.searchMultipleFields(query, ['title', 'description'], 1);
        console.log(`2. Title + Description: ${titleDescResults.results.length} results`);

        // 3. All fields (broadest)
        const allResults = await searchClient.search(query, { top: 1 });
        let allCount = 0;
        for await (const result of allResults.results) {
            allCount++;
        }
        console.log(`3. All fields: ${allCount} results`);

        console.log(`\n💡 Recommendation: Start specific, broaden if needed`);

    } catch (error) {
        console.error(`❌ Field strategy demo failed: ${error.message}`);
    }
}

// Main execution
async function main() {
    try {
        await demonstrateFieldSearch();
        await fieldSearchBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Try searching different fields in your index');
        console.log('   - Experiment with field combinations');
        console.log('   - Check out other examples for more search options');
        console.log('   - Learn about result processing techniques');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    FieldSearch,
    demonstrateFieldSearch,
    fieldSearchBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}