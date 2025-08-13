#!/usr/bin/env node

/**
 * Module 4: Simple Queries and Filters - Basic Queries
 * ====================================================
 * 
 * This script demonstrates basic text search operations in Azure AI Search using JavaScript.
 * Learn how to perform simple searches, use query operators, and work with search fields.
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
        console.log(`   Score: ${result.score?.toFixed(2) || 'N/A'}`);
        console.log(`   ID: ${document.id || 'N/A'}`);
        
        // Show content preview if available
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
 * Demonstrate basic text search operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function basicTextSearch(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('BASIC TEXT SEARCH EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Simple text search
    console.log('\n1. Simple Text Search');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure');
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'azure'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
        return;
    }

    // Example 2: Multi-word search
    console.log('\n2. Multi-word Search');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('machine learning');
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'machine learning'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Empty search (returns all documents)
    console.log('\n3. Empty Search (All Documents)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', { top: 3 });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: '*' (all documents)", 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate searching in specific fields.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function searchWithFields(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('FIELD-SPECIFIC SEARCH EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Search in title field only
    console.log('\n1. Search in Title Field Only');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python', {
            searchFields: ['title']
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'python' in title field");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Search in multiple specific fields
    console.log('\n2. Search in Multiple Fields');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            searchFields: ['title', 'content']
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'azure' in title and content fields");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Search with field boosting (title field weighted more)
    console.log('\n3. Search with Field Boosting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('tutorial', {
            searchFields: ['title^3', 'content'] // Title matches weighted 3x
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'tutorial' with title boosting (3x)");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate query operators in simple syntax.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function queryOperators(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('QUERY OPERATORS EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Required term (+)
    console.log('\n1. Required Term (+)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('+azure search');
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: '+azure search' (azure is required)");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Excluded term (-)
    console.log('\n2. Excluded Term (-)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure -cognitive');
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'azure -cognitive' (exclude cognitive)");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Exact phrase ("")
    console.log('\n3. Exact Phrase Search');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('"machine learning"');
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Search: "machine learning" (exact phrase)');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Wildcard search (*)
    console.log('\n4. Wildcard Search');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('develop*');
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'develop*' (wildcard)");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 5: Grouping with parentheses
    console.log('\n5. Grouping with Parentheses');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('(azure OR microsoft) search');
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: '(azure OR microsoft) search'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate different search modes and query types.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function searchModesAndTypes(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('SEARCH MODES AND QUERY TYPES');
    console.log('='.repeat(80));

    // Example 1: Any search mode (default)
    console.log('\n1. Search Mode: Any (Default)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure machine learning', {
            searchMode: 'any'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search mode 'any': matches any term");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: All search mode
    console.log('\n2. Search Mode: All');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure machine learning', {
            searchMode: 'all'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search mode 'all': matches all terms");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Simple query type (default)
    console.log('\n3. Query Type: Simple (Default)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure AND search', {
            queryType: 'simple'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Simple query type with AND operator");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Full Lucene query type
    console.log('\n4. Query Type: Full Lucene');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('title:azure AND content:search', {
            queryType: 'full'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Full Lucene query with field-specific search");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate advanced text search features.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function advancedTextFeatures(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('ADVANCED TEXT SEARCH FEATURES');
    console.log('='.repeat(80));

    // Example 1: Case sensitivity (searches are case-insensitive by default)
    console.log('\n1. Case Insensitive Search');
    console.log('-'.repeat(40));

    try {
        const resultsLower = await resultsToArray(await searchClient.search('azure'));
        const resultsUpper = await resultsToArray(await searchClient.search('AZURE'));

        console.log(`Search 'azure': ${resultsLower.length} results`);
        console.log(`Search 'AZURE': ${resultsUpper.length} results`);
        console.log('Note: Both searches return the same results (case-insensitive)');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Search with top parameter
    console.log('\n2. Search with Top Parameter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure machine learning', {
            top: 3 // Limit to top 3 results
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Top 3 results for 'azure machine learning'", 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Include total count
    console.log('\n3. Include Total Count');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            includeTotalCount: true,
            top: 5
        });

        const results = await resultsToArray(searchResults);
        const totalCount = searchResults.count;

        console.log(`Total matching documents: ${totalCount}`);
        console.log(`Returned documents: ${results.length}`);
        displayResults(results, "Sample results with total count", 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate working with search result metadata.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function demonstrateResultMetadata(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('SEARCH RESULT METADATA');
    console.log('='.repeat(80));

    try {
        const searchResults = await searchClient.search('azure', { top: 3 });
        const results = await resultsToArray(searchResults);

        console.log('\nDetailed Result Analysis:');
        console.log('-'.repeat(40));

        for (let i = 0; i < results.length; i++) {
            const result = results[i];
            const document = result.document;

            console.log(`\nResult ${i + 1}:`);
            console.log(`  Document ID: ${document.id || 'N/A'}`);
            console.log(`  Search Score: ${result.score?.toFixed(4) || 'N/A'}`);
            console.log(`  Title: ${document.title || 'N/A'}`);

            // Show all available fields
            console.log('  Available fields:');
            for (const [key, value] of Object.entries(document)) {
                if (!key.startsWith('@search')) {
                    const fieldValue = value?.toString() || 'null';
                    const fieldPreview = fieldValue.length > 50 
                        ? fieldValue.substring(0, 50) + '...' 
                        : fieldValue;
                    console.log(`    ${key}: ${fieldPreview}`);
                }
            }
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Main function to run all basic query examples.
 */
async function main() {
    console.log('Azure AI Search - Basic Queries Examples');
    console.log('='.repeat(80));

    try {
        // Create search client
        const searchClient = createSearchClient();
        console.log(`✅ Connected to search service: ${process.env.AZURE_SEARCH_SERVICE_ENDPOINT}`);
        console.log(`✅ Using index: ${process.env.AZURE_SEARCH_INDEX_NAME}`);

        // Run examples
        await basicTextSearch(searchClient);
        await searchWithFields(searchClient);
        await queryOperators(searchClient);
        await searchModesAndTypes(searchClient);
        await advancedTextFeatures(searchClient);
        await demonstrateResultMetadata(searchClient);

        console.log('\n' + '='.repeat(80));
        console.log('✅ All basic query examples completed successfully!');
        console.log('='.repeat(80));

        console.log('\n📚 What you learned:');
        console.log('• How to perform simple text searches');
        console.log('• How to search in specific fields');
        console.log('• How to use query operators (+, -, "", *, ())');
        console.log('• How to work with search modes and query types');
        console.log('• How to access search result metadata');

        console.log('\n🔗 Next steps:');
        console.log('• Run 02_filtering.js to learn about OData filters');
        console.log('• Experiment with your own search terms');
        console.log('• Try different field combinations');

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