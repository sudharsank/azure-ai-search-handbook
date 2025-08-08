/**
 * Phrase Search - Module 2 JavaScript Examples
 * Exact phrase matching in Azure AI Search using JavaScript SDK
 * 
 * This module demonstrates:
 * - Exact phrase search with quotes
 * - Comparing phrase vs individual terms
 * - Understanding when to use phrase search
 * - Phrase search best practices
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

class PhraseSearch {
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
     * Search for an exact phrase using quotes
     * @param {string} phrase - Exact phrase to search for
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async exactPhraseSearch(phrase, top = 10) {
        try {
            // Wrap phrase in quotes for exact matching
            const quotedPhrase = `"${phrase}"`;
            console.log(`Performing exact phrase search: ${quotedPhrase}`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(quotedPhrase, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} exact phrase matches`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in phrase search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Search for individual terms (without quotes)
     * @param {string} phrase - Terms to search for individually
     * @param {number} top - Maximum number of results to return
     * @returns {Promise<Object>} Search results
     */
    async individualTermsSearch(phrase, top = 10) {
        try {
            console.log(`Performing individual terms search: '${phrase}'`);

            const searchOptions = {
                top: top,
                includeTotalCount: true
            };

            const results = await this.searchClient.search(phrase, searchOptions);
            
            const resultArray = [];
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Found ${resultArray.length} results for individual terms`);
            return {
                results: resultArray,
                totalCount: results.count
            };
        } catch (error) {
            console.error(`Error in individual terms search: ${error.message}`);
            return { results: [], totalCount: 0 };
        }
    }

    /**
     * Compare exact phrase search vs individual terms search
     * @param {string} phrase - Phrase to compare
     * @param {number} top - Maximum number of results for each search
     * @returns {Promise<Object>} Object with phrase and terms results
     */
    async comparePhraseVsTerms(phrase, top = 5) {
        const phraseResults = await this.exactPhraseSearch(phrase, top);
        const termsResults = await this.individualTermsSearch(phrase, top);

        return { phraseResults, termsResults };
    }

    /**
     * Display comparison between phrase and terms search
     * @param {string} phrase - Original phrase searched
     * @param {Object} phraseResults - Results from exact phrase search
     * @param {Object} termsResults - Results from individual terms search
     */
    static displayComparison(phrase, phraseResults, termsResults) {
        console.log(`\n🔤 Phrase vs Terms Comparison: '${phrase}'`);
        console.log('='.repeat(60));

        // Exact phrase results
        console.log(`\n1️⃣ EXACT PHRASE SEARCH: "${phrase}"`);
        console.log('-'.repeat(40));
        console.log(`Results found: ${phraseResults.results.length}`);

        if (phraseResults.results.length > 0) {
            console.log('Top matches:');
            phraseResults.results.slice(0, 3).forEach((result, index) => {
                const title = result.document.title || 'No title';
                const score = result.score || 0.0;
                console.log(`  ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
            });
        } else {
            console.log('  No exact phrase matches found');
        }

        // Individual terms results
        console.log(`\n2️⃣ INDIVIDUAL TERMS SEARCH: ${phrase}`);
        console.log('-'.repeat(40));
        console.log(`Results found: ${termsResults.results.length}`);

        if (termsResults.results.length > 0) {
            console.log('Top matches:');
            termsResults.results.slice(0, 3).forEach((result, index) => {
                const title = result.document.title || 'No title';
                const score = result.score || 0.0;
                console.log(`  ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
            });
        } else {
            console.log('  No results found for individual terms');
        }

        // Analysis
        console.log(`\n📊 COMPARISON ANALYSIS:`);
        console.log(`   Exact phrase: ${phraseResults.results.length} results`);
        console.log(`   Individual terms: ${termsResults.results.length} results`);

        if (phraseResults.results.length > 0 && termsResults.results.length > 0) {
            const phraseAvg = phraseResults.results.reduce((sum, r) => sum + (r.score || 0), 0) / phraseResults.results.length;
            const termsAvg = termsResults.results.reduce((sum, r) => sum + (r.score || 0), 0) / termsResults.results.length;
            console.log(`   Average phrase score: ${phraseAvg.toFixed(3)}`);
            console.log(`   Average terms score: ${termsAvg.toFixed(3)}`);
        }

        // Recommendations
        console.log(`\n💡 RECOMMENDATIONS:`);
        if (phraseResults.results.length > 0) {
            console.log('   ✅ Exact phrase found - use phrase search for precision');
        } else if (termsResults.results.length > 0) {
            console.log('   ⚠️ No exact phrase - individual terms provide broader results');
        } else {
            console.log('   ❌ No results found - try different keywords or broader terms');
        }
    }

    /**
     * Search for multiple phrases
     * @param {Array<string>} phrases - List of phrases to search for
     * @param {number} top - Maximum results per phrase
     * @returns {Promise<Object>} Object mapping phrases to their results
     */
    async multiPhraseSearch(phrases, top = 3) {
        const results = {};

        for (const phrase of phrases) {
            console.log(`Searching for phrase: '${phrase}'`);
            const phraseResults = await this.exactPhraseSearch(phrase, top);
            results[phrase] = phraseResults;
        }

        return results;
    }
}

/**
 * Demonstrate phrase search operations
 */
async function demonstratePhraseSearch() {
    console.log('🔤 Phrase Search Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new PhraseSearch(searchClient);

        // Example 1: Compare phrase vs terms
        console.log('\n1️⃣ Phrase vs Terms Comparison');

        const testPhrase = 'machine learning';
        const { phraseResults, termsResults } = await searchOps.comparePhraseVsTerms(testPhrase, 5);
        PhraseSearch.displayComparison(testPhrase, phraseResults, termsResults);

        // Example 2: Another comparison
        console.log('\n' + '='.repeat(70));
        console.log('\n2️⃣ Another Comparison Example');

        const testPhrase2 = 'web development';
        const { phraseResults: phraseResults2, termsResults: termsResults2 } = 
            await searchOps.comparePhraseVsTerms(testPhrase2, 5);
        PhraseSearch.displayComparison(testPhrase2, phraseResults2, termsResults2);

        // Example 3: Multiple phrase search
        console.log('\n' + '='.repeat(70));
        console.log('\n3️⃣ Multiple Phrase Search');
        console.log('-'.repeat(30));

        const phrasesToSearch = [
            'artificial intelligence',
            'data science',
            'software engineering'
        ];

        const multiResults = await searchOps.multiPhraseSearch(phrasesToSearch, 2);

        for (const [phrase, results] of Object.entries(multiResults)) {
            console.log(`\nPhrase: "${phrase}"`);
            console.log(`Results: ${results.results.length}`);
            
            if (results.results.length > 0) {
                const topResult = results.results[0];
                const title = topResult.document.title || 'No title';
                const score = topResult.score || 0.0;
                console.log(`Top match: ${title} (Score: ${score.toFixed(3)})`);
            } else {
                console.log('No matches found');
            }
        }

        console.log('\n✅ Phrase search demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
        console.log('Make sure your Azure AI Search service is configured correctly.');
    }
}

/**
 * Demonstrate best practices for phrase search
 */
async function phraseSearchBestPractices() {
    console.log('\n📚 Phrase Search Best Practices');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const searchOps = new PhraseSearch(searchClient);

        console.log('\n💡 When to Use Phrase Search:');
        console.log('   ✅ Looking for specific technical terms');
        console.log('   ✅ Searching for proper names or titles');
        console.log('   ✅ Finding exact quotes or references');
        console.log('   ✅ When word order matters');

        console.log('\n⚠️ When NOT to Use Phrase Search:');
        console.log('   ❌ General topic searches');
        console.log('   ❌ When you want broader results');
        console.log('   ❌ Searching for concepts (not exact terms)');
        console.log('   ❌ When unsure of exact wording');

        // Demonstrate with examples
        console.log('\n🧪 Practice Examples:');

        // Good phrase search examples
        const goodPhrases = [
            'React hooks',
            'machine learning algorithm',
            'REST API'
        ];

        console.log('\n✅ Good Phrase Search Examples:');
        for (const phrase of goodPhrases) {
            const results = await searchOps.exactPhraseSearch(phrase, 1);
            const status = results.results.length > 0 ? 'Found' : 'Not found';
            console.log(`   "${phrase}": ${status}`);
        }

        // Show fallback strategy
        console.log('\n🔄 Fallback Strategy Example:');
        const testPhrase = 'deep learning neural networks';

        // Try exact phrase first
        const exactResults = await searchOps.exactPhraseSearch(testPhrase, 3);
        console.log(`   Exact phrase "${testPhrase}": ${exactResults.results.length} results`);

        if (exactResults.results.length === 0) {
            // Fallback to individual terms
            const termsResults = await searchOps.individualTermsSearch(testPhrase, 3);
            console.log(`   Fallback to terms: ${termsResults.results.length} results`);

            if (termsResults.results.length > 0) {
                console.log('   💡 Recommendation: Use individual terms for broader results');
            }
        }

    } catch (error) {
        console.error(`❌ Best practices demo failed: ${error.message}`);
    }
}

// Main execution
async function main() {
    try {
        await demonstratePhraseSearch();
        await phraseSearchBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Try your own phrases with the examples above');
        console.log('   - Compare results between phrase and terms search');
        console.log('   - Check out 03_boolean_search.js for combining terms with AND/OR');
        console.log('   - Learn about wildcards in 04_wildcard_search.js');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    PhraseSearch,
    demonstratePhraseSearch,
    phraseSearchBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}