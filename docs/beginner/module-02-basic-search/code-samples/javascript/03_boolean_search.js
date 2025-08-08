/**
 * Boolean Search - Module 2 JavaScript Examples
 * Boolean operators (AND, OR, NOT) in Azure AI Search using JavaScript SDK
 * 
 * This module demonstrates:
 * - AND operator for required terms
 * - OR operator for alternative terms
 * - NOT operator for exclusions
 * - Combining boolean operators
 * - Boolean search best practices
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

class BooleanSearch {
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
     * Search for documents containing both terms (AND operator)
     * @param {string} term1 - First required term
     * @param {string} term2 - Second required term
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async andSearch(term1, term2, top = 10) {
        try {
            const query = `${term1} AND ${term2}`;
            console.log(`Performing AND search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results with both terms`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in AND search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search for documents containing either term (OR operator)
     * @param {string} term1 - First alternative term
     * @param {string} term2 - Second alternative term
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async orSearch(term1, term2, top = 10) {
        try {
            const query = `${term1} OR ${term2}`;
            console.log(`Performing OR search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results with either term`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in OR search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search for documents containing one term but not another (NOT operator)
     * @param {string} includeTerm - Term that must be present
     * @param {string} excludeTerm - Term that must not be present
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async notSearch(includeTerm, excludeTerm, top = 10) {
        try {
            const query = `${includeTerm} NOT ${excludeTerm}`;
            console.log(`Performing NOT search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results excluding '${excludeTerm}'`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in NOT search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Perform complex boolean search with multiple operators
     * @param {string} query - Complex boolean query string
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async complexBooleanSearch(query, top = 10) {
        try {
            console.log(`Performing complex boolean search: '${query}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(query, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results for complex query`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in complex boolean search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Compare results from different boolean operators
     * @param {string} term1 - First term
     * @param {string} term2 - Second term
     * @param {number} top - Maximum results per operator
     * @returns {Promise<Object>} Object mapping operators to their results
     */
    async compareBooleanOperators(term1, term2, top = 5) {
        const results = {};

        // AND search
        results['AND'] = await this.andSearch(term1, term2, top);

        // OR search
        results['OR'] = await this.orSearch(term1, term2, top);

        // NOT search (term1 but not term2)
        results['NOT'] = await this.notSearch(term1, term2, top);

        return results;
    }

    /**
     * Display comparison of boolean operators
     * @param {string} term1 - First term
     * @param {string} term2 - Second term
     * @param {Object} results - Results from different boolean operators
     */
    static displayBooleanComparison(term1, term2, results) {
        console.log(`\n🔗 Boolean Operators Comparison: '${term1}' and '${term2}'`);
        console.log('='.repeat(70));

        for (const [operatorName, operatorResults] of Object.entries(results)) {
            console.log(`\n${operatorName} Operation:`);

            switch (operatorName) {
                case 'AND':
                    console.log(`   Query: ${term1} AND ${term2}`);
                    console.log(`   Meaning: Documents must contain BOTH terms`);
                    break;
                case 'OR':
                    console.log(`   Query: ${term1} OR ${term2}`);
                    console.log(`   Meaning: Documents can contain EITHER term`);
                    break;
                case 'NOT':
                    console.log(`   Query: ${term1} NOT ${term2}`);
                    console.log(`   Meaning: Documents must contain '${term1}' but NOT '${term2}'`);
                    break;
            }

            console.log(`   Results found: ${operatorResults.results.length}`);

            if (operatorResults.results.length > 0) {
                console.log('   Top matches:');
                operatorResults.results.slice(0, 3).forEach((result, index) => {
                    const title = result.document.title || 'No title';
                    const score = result.score || 0.0;
                    console.log(`     ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
                });
            } else {
                console.log('   No matches found');
            }

            console.log('-'.repeat(50));
        }

        // Analysis
        console.log(`\n📊 ANALYSIS:`);
        const andCount = results['AND']?.results.length || 0;
        const orCount = results['OR']?.results.length || 0;
        const notCount = results['NOT']?.results.length || 0;

        console.log(`   AND results: ${andCount} (most specific)`);
        console.log(`   OR results: ${orCount} (broadest)`);
        console.log(`   NOT results: ${notCount} (filtered)`);

        if (orCount >= andCount && andCount >= notCount) {
            console.log('   ✅ Expected pattern: OR ≥ AND ≥ NOT');
        } else {
            console.log('   ⚠️ Unexpected pattern - check your data or terms');
        }
    }
}

/**
 * Demonstrate boolean search operations
 */
async function demonstrateBooleanSearch() {
    console.log('🔗 Boolean Search Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new BooleanSearch(searchClient);

        // Example 1: Compare boolean operators
        console.log('\n1️⃣ Boolean Operators Comparison');

        const term1 = 'python';
        const term2 = 'tutorial';
        const booleanResults = await searchOps.compareBooleanOperators(term1, term2, 5);
        BooleanSearch.displayBooleanComparison(term1, term2, booleanResults);

        // Example 2: Complex boolean queries
        console.log('\n' + '='.repeat(70));
        console.log('\n2️⃣ Complex Boolean Queries');
        console.log('-'.repeat(30));

        const complexQueries = [
            'python AND (tutorial OR guide)',
            '(web OR mobile) AND development',
            'programming NOT (beginner OR basic)',
            'machine AND learning AND (python OR r)'
        ];

        for (const query of complexQueries) {
            console.log(`\nQuery: ${query}`);
            const results = await searchOps.complexBooleanSearch(query, 3);
            console.log(`Results: ${results.results.length}`);

            if (results.results.length > 0) {
                const topResult = results.results[0];
                const title = topResult.document.title || 'No title';
                const score = topResult.score || 0.0;
                console.log(`Top match: ${title} (Score: ${score.toFixed(3)})`);
            }
        }

        // Example 3: Practical use cases
        console.log('\n' + '='.repeat(70));
        console.log('\n3️⃣ Practical Use Cases');
        console.log('-'.repeat(30));

        const useCases = [
            {
                scenario: 'Find beginner Python tutorials',
                query: 'python AND tutorial AND beginner',
                explanation: 'All three terms must be present'
            },
            {
                scenario: 'Find content about web or mobile development',
                query: 'development AND (web OR mobile)',
                explanation: 'Must have \'development\' plus either \'web\' or \'mobile\''
            },
            {
                scenario: 'Find programming content but exclude advanced topics',
                query: 'programming NOT (advanced OR expert)',
                explanation: 'Must have \'programming\' but exclude advanced content'
            }
        ];

        for (const useCase of useCases) {
            console.log(`\n📋 Scenario: ${useCase.scenario}`);
            console.log(`   Query: ${useCase.query}`);
            console.log(`   Logic: ${useCase.explanation}`);

            const results = await searchOps.complexBooleanSearch(useCase.query, 2);
            console.log(`   Results: ${results.results.length} found`);
        }

        console.log('\n✅ Boolean search demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
        console.log('Make sure your Azure AI Search service is configured correctly.');
    }
}

/**
 * Demonstrate best practices for boolean search
 */
async function booleanSearchBestPractices() {
    console.log('\n📚 Boolean Search Best Practices');
    console.log('='.repeat(50));

    console.log('\n💡 When to Use Each Operator:');
    console.log('\n✅ AND Operator:');
    console.log('   - When you need ALL terms to be present');
    console.log('   - For specific, focused searches');
    console.log('   - To narrow down broad topics');
    console.log('   - Example: \'machine AND learning AND python\'');

    console.log('\n✅ OR Operator:');
    console.log('   - When you want ANY of the terms');
    console.log('   - For broader, more inclusive searches');
    console.log('   - When searching for synonyms or alternatives');
    console.log('   - Example: \'javascript OR typescript OR js\'');

    console.log('\n✅ NOT Operator:');
    console.log('   - To exclude unwanted content');
    console.log('   - To filter out irrelevant results');
    console.log('   - When you know what you don\'t want');
    console.log('   - Example: \'programming NOT (game OR gaming)\'');

    console.log('\n⚠️ Common Mistakes to Avoid:');
    console.log('   ❌ Using AND when you mean OR');
    console.log('   ❌ Overusing NOT (can exclude relevant content)');
    console.log('   ❌ Forgetting parentheses in complex queries');
    console.log('   ❌ Making queries too restrictive with multiple ANDs');

    console.log('\n🔧 Query Building Tips:');
    console.log('   ✅ Start simple, then add complexity');
    console.log('   ✅ Use parentheses to group terms: (term1 OR term2) AND term3');
    console.log('   ✅ Test each part of complex queries separately');
    console.log('   ✅ Consider search mode (\'any\' vs \'all\') as alternative to boolean');

    // Demonstrate query building
    console.log('\n🏗️ Query Building Example:');
    
    try {
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new BooleanSearch(searchClient);

        const baseTerm = 'tutorial';
        console.log(`\n1. Start with base term: '${baseTerm}'`);
        const baseResults = await searchOps.complexBooleanSearch(baseTerm, 1);
        console.log(`   Results: ${baseResults.results.length}`);

        const refinedQuery = 'tutorial AND python';
        console.log(`\n2. Add specificity: '${refinedQuery}'`);
        const refinedResults = await searchOps.complexBooleanSearch(refinedQuery, 1);
        console.log(`   Results: ${refinedResults.results.length} (more specific)`);

        const finalQuery = 'tutorial AND python AND (beginner OR introduction)';
        console.log(`\n3. Add alternatives: '${finalQuery}'`);
        const finalResults = await searchOps.complexBooleanSearch(finalQuery, 1);
        console.log(`   Results: ${finalResults.results.length} (balanced specificity)`);

    } catch (error) {
        console.error(`❌ Query building demo failed: ${error.message}`);
    }
}

// Main execution
async function main() {
    try {
        await demonstrateBooleanSearch();
        await booleanSearchBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Practice building your own boolean queries');
        console.log('   - Try combining different operators');
        console.log('   - Check out 04_wildcard_search.js for pattern matching');
        console.log('   - Learn about field-specific searches in 05_field_search.js');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    BooleanSearch,
    demonstrateBooleanSearch,
    booleanSearchBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}