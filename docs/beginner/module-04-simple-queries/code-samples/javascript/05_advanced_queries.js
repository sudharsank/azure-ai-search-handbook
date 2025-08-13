#!/usr/bin/env node

/**
 * Module 4: Simple Queries and Filters - Advanced Queries
 * =======================================================
 * 
 * This script demonstrates advanced query techniques in Azure AI Search using JavaScript.
 * Learn about field boosting, fuzzy search, wildcards, and complex query patterns.
 * 
 * Prerequisites:
 * - Azure AI Search service configured
 * - Sample index with data (from previous modules)
 * - Environment variables set in .env file
 * 
 * Author: Azure AI Search Tutorial
 */

import { SearchClient, AzureKeyCredential } from '@azure/search-documents';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Create and return an Azure AI Search client.
 * @returns {SearchClient} Configured search client
 */
function createSearchClient() {
    const endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
    const apiKey = process.env.AZURE_SEARCH_API_KEY;
    const indexName = process.env.AZURE_SEARCH_INDEX_NAME;

    if (!endpoint || !apiKey || !indexName) {
        throw new Error('Missing required environment variables. Check your .env file.');
    }

    return new SearchClient(endpoint, indexName, new AzureKeyCredential(apiKey));
}

/**
 * Display search results in a formatted way.
 * @param {Array} results - Array of search result documents
 * @param {string} title - Title for the result set
 * @param {number} maxResults - Maximum number of results to display
 */
function displayResults(results, title, maxResults = 5) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(title);
    console.log('='.repeat(60));

    if (!results || results.length === 0) {
        console.log('No results found.');
        return;
    }

    const displayCount = Math.min(results.length, maxResults);
    
    for (let i = 0; i < displayCount; i++) {
        const result = results[i];
        const document = result.document;
        
        console.log(`\n${i + 1}. ${document.title || 'No title'}`);
        console.log(`   Score: ${result.score?.toFixed(4) || 'N/A'}`);
        console.log(`   Category: ${document.category || 'N/A'}`);
        console.log(`   Rating: ${document.rating || 'N/A'}`);
        
        // Show content preview
        if (document.content) {
            const preview = document.content.length > 100 
                ? document.content.substring(0, 100) + '...' 
                : document.content;
            console.log(`   Preview: ${preview}`);
        }
    }

    if (results.length > maxResults) {
        console.log(`\n... and ${results.length - maxResults} more results`);
    }
}

/**
 * Convert search results async iterator to array.
 * @param {SearchResults} searchResults - Search results from Azure AI Search
 * @returns {Promise<Array>} Array of search results
 */
async function resultsToArray(searchResults) {
    const results = [];
    for await (const result of searchResults.results) {
        results.push(result);
    }
    return results;
}

/**
 * Demonstrate field boosting to influence relevance scoring.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function fieldBoostingExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('FIELD BOOSTING EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: No boosting (baseline)
    console.log('\n1. No Field Boosting (Baseline)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python tutorial', {
            searchFields: ['title', 'content'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'No boosting - equal weight for all fields');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Boost title field
    console.log('\n2. Boost Title Field (3x weight)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python tutorial', {
            searchFields: ['title^3', 'content'], // Title weighted 3x
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Title boosted 3x - title matches score higher');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Multiple field boosting
    console.log('\n3. Multiple Field Boosting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure machine learning', {
            searchFields: ['title^5', 'category^2', 'content'], // Title 5x, category 2x
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Title 5x, category 2x, content 1x');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Extreme boosting comparison
    console.log('\n4. Extreme Boosting Comparison');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('tutorial', {
            searchFields: ['title^10', 'content'], // Extreme title boost
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Extreme title boosting (10x)');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate fuzzy search for handling typos and variations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function fuzzySearchExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('FUZZY SEARCH EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Exact match (baseline)
    console.log('\n1. Exact Match (Baseline)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('machine', {
            queryType: 'simple',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Exact match: 'machine'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Fuzzy search with typo
    console.log('\n2. Fuzzy Search with Typo');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('machne~', { // Typo: missing 'i'
            queryType: 'full', // Requires full Lucene syntax
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Fuzzy search: 'machne~' (should match 'machine')");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Fuzzy search with edit distance
    console.log('\n3. Fuzzy Search with Edit Distance');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('learing~2', { // Allow up to 2 character differences
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Fuzzy search: 'learing~2' (should match 'learning')");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Multiple fuzzy terms
    console.log('\n4. Multiple Fuzzy Terms');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('machne~ learing~', { // Multiple fuzzy terms
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Multiple fuzzy: 'machne~ learing~'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate wildcard search patterns.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function wildcardSearchExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('WILDCARD SEARCH EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Suffix wildcard
    console.log('\n1. Suffix Wildcard');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('develop*', { // Matches develop, developer, development, etc.
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Suffix wildcard: 'develop*'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Prefix wildcard (requires full Lucene)
    console.log('\n2. Prefix Wildcard');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*ing', { // Matches words ending in 'ing'
            queryType: 'full',
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Prefix wildcard: '*ing'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Middle wildcard
    console.log('\n3. Middle Wildcard');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('mach*ne', { // Matches machine, etc.
            queryType: 'full',
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Middle wildcard: 'mach*ne'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Single character wildcard
    console.log('\n4. Single Character Wildcard');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('te?t', { // Matches test, text, etc.
            queryType: 'full',
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Single char wildcard: 'te?t'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate proximity search for terms near each other.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function proximitySearchExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('PROXIMITY SEARCH EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Exact phrase
    console.log('\n1. Exact Phrase');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('"machine learning"', { // Exact phrase
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Exact phrase: "machine learning"');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Proximity search (within N words)
    console.log('\n2. Proximity Search (Within 5 Words)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('"machine learning"~5', { // Within 5 words of each other
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Proximity: "machine learning"~5');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Looser proximity
    console.log('\n3. Looser Proximity (Within 10 Words)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('"azure cognitive"~10', {
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Proximity: "azure cognitive"~10');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate regular expression search patterns.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function regularExpressionExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('REGULAR EXPRESSION EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Simple regex pattern
    console.log('\n1. Simple Regex Pattern');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('/[Tt]utorial/', { // Matches Tutorial or tutorial
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Regex: /[Tt]utorial/');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Number pattern
    console.log('\n2. Number Pattern');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('/[0-9]+/', { // Matches any number
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Regex: /[0-9]+/ (any number)');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Version pattern
    console.log('\n3. Version Pattern');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('/[0-9]+\\.[0-9]+/', { // Matches version numbers like 3.8
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Regex: /[0-9]+\\.[0-9]+/ (version numbers)');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate complex combinations of advanced query features.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function complexQueryCombinations(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('COMPLEX QUERY COMBINATIONS');
    console.log('='.repeat(80));

    // Example 1: Boosting + Fuzzy + Filter
    console.log('\n1. Boosting + Fuzzy + Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('machne~ learing~', { // Fuzzy search
            searchFields: ['title^3', 'content'], // Field boosting
            filter: 'rating ge 3.0', // Filter
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Fuzzy + boosting + filter combination');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Wildcard + Proximity + Sorting
    console.log('\n2. Wildcard + Proximity + Sorting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('develop* AND "tutorial guide"~3', { // Wildcard + proximity
            orderBy: ['rating desc'], // Sorting
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Wildcard + proximity + sorting');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Multiple techniques with highlighting
    console.log('\n3. Multiple Techniques + Highlighting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python* OR java*', { // Wildcard OR
            searchFields: ['title^2', 'content'], // Boosting
            filter: "category eq 'Technology'", // Filter
            highlightFields: ['title', 'content'], // Highlighting
            orderBy: ['@search.score desc'], // Sort by relevance
            queryType: 'full',
            top: 3
        });
        const results = await resultsToArray(searchResults);

        displayResults(results, 'Complex combination with highlighting');

        // Show highlights
        for (let i = 0; i < Math.min(2, results.length); i++) {
            const result = results[i];
            if (result.document['@search.highlights']) {
                console.log(`\nHighlights for result ${i + 1}:`);
                const highlights = result.document['@search.highlights'];
                for (const [field, highlightList] of Object.entries(highlights)) {
                    for (const highlight of highlightList.slice(0, 1)) {
                        console.log(`  ${field}: ${highlight}`);
                    }
                }
            }
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Analyze performance of different advanced query techniques.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function queryPerformanceAnalysis(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('QUERY PERFORMANCE ANALYSIS');
    console.log('='.repeat(80));

    const queries = [
        ['Simple text', 'azure machine learning', 'simple'],
        ['Wildcard', 'develop*', 'simple'],
        ['Fuzzy', 'machne~ learing~', 'full'],
        ['Regex', '/[Tt]utorial/', 'full'],
        ['Complex', 'python* AND "tutorial guide"~3', 'full']
    ];

    console.log('\nPerformance Comparison:');
    console.log('-'.repeat(40));

    for (const [name, query, queryType] of queries) {
        try {
            const startTime = Date.now();

            const searchResults = await searchClient.search(query, {
                queryType: queryType,
                top: 10
            });
            const results = await resultsToArray(searchResults);

            const executionTime = Date.now() - startTime;

            console.log(`${name.padEnd(15)} | ${executionTime.toString().padStart(6)}ms | ${results.length.toString().padStart(3)} results | ${query}`);
        } catch (error) {
            console.log(`${name.padEnd(15)} | ERROR   | ${error.message.substring(0, 50)}...`);
        }
    }

    console.log('\nPerformance Tips:');
    console.log('• Simple queries are fastest');
    console.log('• Wildcard queries are moderately fast');
    console.log('• Fuzzy queries add processing overhead');
    console.log('• Regex queries can be slow with complex patterns');
    console.log('• Complex combinations multiply overhead');
}

/**
 * Demonstrate advanced scoring and relevance techniques.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function advancedScoringExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('ADVANCED SCORING EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Score analysis with different query types
    console.log('\n1. Score Analysis by Query Type');
    console.log('-'.repeat(40));

    const queryTypes = [
        ['Simple', 'azure tutorial', 'simple'],
        ['Fuzzy', 'azure~ tutorial~', 'full'],
        ['Wildcard', 'azure* tutorial*', 'full']
    ];

    for (const [name, query, queryType] of queryTypes) {
        try {
            const searchResults = await searchClient.search(query, {
                queryType: queryType,
                top: 3
            });
            const results = await resultsToArray(searchResults);

            if (results.length > 0) {
                const scores = results.map(r => r.score);
                const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
                console.log(`\n${name} Query: '${query}'`);
                console.log(`  Average score: ${avgScore.toFixed(4)}`);
                console.log(`  Score range: ${Math.min(...scores).toFixed(4)} - ${Math.max(...scores).toFixed(4)}`);
            }
        } catch (error) {
            console.log(`${name} query failed: ${error.message}`);
        }
    }

    // Example 2: Boosting impact on scores
    console.log('\n2. Boosting Impact on Scores');
    console.log('-'.repeat(40));

    try {
        // No boosting
        const resultsNormal = await resultsToArray(
            await searchClient.search('python tutorial', {
                searchFields: ['title', 'content'],
                top: 3
            })
        );

        // With boosting
        const resultsBoosted = await resultsToArray(
            await searchClient.search('python tutorial', {
                searchFields: ['title^5', 'content'],
                top: 3
            })
        );

        console.log('Score comparison (same query, different boosting):');
        console.log('\nNo boosting:');
        for (let i = 0; i < Math.min(2, resultsNormal.length); i++) {
            const result = resultsNormal[i];
            const title = result.document.title || '';
            console.log(`  ${i + 1}. Score: ${result.score.toFixed(4)} - ${title.substring(0, 40)}...`);
        }

        console.log('\nWith title boosting (5x):');
        for (let i = 0; i < Math.min(2, resultsBoosted.length); i++) {
            const result = resultsBoosted[i];
            const title = result.document.title || '';
            console.log(`  ${i + 1}. Score: ${result.score.toFixed(4)} - ${title.substring(0, 40)}...`);
        }
    } catch (error) {
        console.log(`Boosting comparison failed: ${error.message}`);
    }
}

/**
 * Main function to run all advanced query examples.
 */
async function main() {
    console.log('Azure AI Search - Advanced Queries Examples');
    console.log('='.repeat(80));

    try {
        // Create search client
        const searchClient = createSearchClient();
        console.log(`✅ Connected to search service: ${process.env.AZURE_SEARCH_SERVICE_ENDPOINT}`);
        console.log(`✅ Using index: ${process.env.AZURE_SEARCH_INDEX_NAME}`);

        // Run examples
        await fieldBoostingExamples(searchClient);
        await fuzzySearchExamples(searchClient);
        await wildcardSearchExamples(searchClient);
        await proximitySearchExamples(searchClient);
        await regularExpressionExamples(searchClient);
        await complexQueryCombinations(searchClient);
        await queryPerformanceAnalysis(searchClient);
        await advancedScoringExamples(searchClient);

        console.log('\n' + '='.repeat(80));
        console.log('✅ All advanced query examples completed successfully!');
        console.log('='.repeat(80));

        console.log('\n📚 What you learned:');
        console.log('• How to use field boosting to influence relevance');
        console.log('• How to implement fuzzy search for typo tolerance');
        console.log('• How to use wildcard patterns for flexible matching');
        console.log('• How to perform proximity and phrase searches');
        console.log('• How to use regular expressions in queries');
        console.log('• How to combine multiple advanced techniques');
        console.log('• How to analyze and optimize query performance');

        console.log('\n🔗 Next steps:');
        console.log('• Run 06_error_handling.js to learn robust query implementation');
        console.log('• Experiment with different boosting values');
        console.log('• Try complex query combinations with your data');
        console.log('• Monitor query performance in production');

    } catch (error) {
        if (error.message.includes('Missing required environment variables')) {
            console.error(`❌ Configuration error: ${error.message}`);
            console.log('\n🔧 Setup required:');
            console.log('1. Create a .env file with your Azure AI Search credentials');
            console.log('2. Ensure you have completed previous modules to create sample indexes');
            process.exit(1);
        } else {
            console.error(`❌ Unexpected error: ${error.message}`);
            process.exit(1);
        }
    }
}

// Run the main function
main().catch(console.error);