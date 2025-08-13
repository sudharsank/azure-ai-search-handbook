#!/usr/bin/env node

/**
 * Module 4: Simple Queries and Filters - Filtering
 * ================================================
 * 
 * This script demonstrates OData filter expressions in Azure AI Search using JavaScript.
 * Learn how to apply filters to narrow search results based on specific criteria.
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
        console.log(`   Category: ${document.category || 'N/A'}`);
        console.log(`   Rating: ${document.rating || 'N/A'}`);
        console.log(`   Published: ${document.publishedDate || 'N/A'}`);
        
        // Show tags if available
        if (document.tags && Array.isArray(document.tags)) {
            const tagsDisplay = document.tags.slice(0, 3).join(', ');
            const suffix = document.tags.length > 3 ? '...' : '';
            console.log(`   Tags: ${tagsDisplay}${suffix}`);
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
 * Demonstrate equality filter operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function equalityFilters(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('EQUALITY FILTER EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Exact string match
    console.log('\n1. Exact String Match');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category eq 'Technology'"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: category eq 'Technology'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Not equal filter
    console.log('\n2. Not Equal Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category ne 'Draft'",
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: category ne 'Draft'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Combining search with filter
    console.log('\n3. Search Text with Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            filter: "category eq 'Technology'"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search: 'azure' + Filter: category eq 'Technology'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate comparison filter operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function comparisonFilters(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('COMPARISON FILTER EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Greater than
    console.log('\n1. Greater Than Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'rating gt 4.0'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: rating gt 4.0');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Greater than or equal
    console.log('\n2. Greater Than or Equal Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'rating ge 4.5'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: rating ge 4.5');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Less than
    console.log('\n3. Less Than Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'rating lt 3.0'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: rating lt 3.0');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Range filter (between values)
    console.log('\n4. Range Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'rating ge 3.0 and rating le 4.0'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: rating between 3.0 and 4.0');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate logical operators in filters.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function logicalOperators(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('LOGICAL OPERATORS IN FILTERS');
    console.log('='.repeat(80));

    // Example 1: AND operator
    console.log('\n1. AND Operator');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category eq 'Technology' and rating ge 4.0"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: category eq 'Technology' AND rating ge 4.0");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: OR operator
    console.log('\n2. OR Operator');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category eq 'Technology' or category eq 'Science'"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: category eq 'Technology' OR category eq 'Science'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: NOT operator
    console.log('\n3. NOT Operator');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "not (category eq 'Draft')"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: NOT (category eq 'Draft')");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Complex logical expression
    console.log('\n4. Complex Logical Expression');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "(category eq 'Technology' or category eq 'Science') and rating gt 3.5"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: (Technology OR Science) AND rating > 3.5');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate date filtering operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function dateFilters(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('DATE FILTER EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Documents published after a specific date
    console.log('\n1. Published After Date');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'publishedDate ge 2023-01-01T00:00:00Z'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: publishedDate ge 2023-01-01T00:00:00Z');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Documents published before a specific date
    console.log('\n2. Published Before Date');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'publishedDate lt 2024-01-01T00:00:00Z'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: publishedDate lt 2024-01-01T00:00:00Z');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Date range filter
    console.log('\n3. Date Range Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: 'publishedDate ge 2023-01-01T00:00:00Z and publishedDate le 2023-12-31T23:59:59Z'
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: published in 2023');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Recent documents (last 30 days)
    console.log('\n4. Recent Documents');
    console.log('-'.repeat(40));

    try {
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const recentDate = thirtyDaysAgo.toISOString();

        const searchResults = await searchClient.search('*', {
            filter: `publishedDate ge ${recentDate}`
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Filter: published in last 30 days');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate filtering on collection fields (arrays).
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function collectionFilters(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('COLLECTION FILTER EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Any element matches (tags/any)
    console.log('\n1. Any Element Matches');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "tags/any(t: t eq 'python')"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: tags/any(t: t eq 'python')");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Multiple tag matches
    console.log('\n2. Multiple Tag Options');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "tags/any(t: t eq 'python' or t eq 'javascript')"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: tags contain 'python' OR 'javascript'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: All elements match condition
    console.log('\n3. All Elements Match');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "tags/all(t: t ne 'deprecated')"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: all tags are not 'deprecated'");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Complex collection filter
    console.log('\n4. Complex Collection Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "tags/any(t: t eq 'tutorial') and rating ge 4.0"
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Filter: has 'tutorial' tag AND rating >= 4.0");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate filter validation and error handling.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function filterValidationExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('FILTER VALIDATION EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Valid filter
    console.log('\n1. Valid Filter');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category eq 'Technology'"
        });
        const results = await resultsToArray(searchResults);
        console.log(`✅ Valid filter executed successfully: ${results.length} results`);
    } catch (error) {
        console.log(`❌ Filter failed: ${error.message}`);
    }

    // Example 2: Invalid field name
    console.log('\n2. Invalid Field Name');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "nonexistent_field eq 'value'"
        });
        const results = await resultsToArray(searchResults);
        console.log(`Results: ${results.length}`);
    } catch (error) {
        console.log(`❌ Expected error - Invalid field: ${error.message}`);
    }

    // Example 3: Invalid syntax
    console.log('\n3. Invalid Filter Syntax');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category = 'Technology'" // Should be 'eq' not '='
        });
        const results = await resultsToArray(searchResults);
        console.log(`Results: ${results.length}`);
    } catch (error) {
        console.log(`❌ Expected error - Invalid syntax: ${error.message}`);
    }

    // Example 4: Type mismatch
    console.log('\n4. Type Mismatch');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "rating eq 'high'" // Should be numeric, not string
        });
        const results = await resultsToArray(searchResults);
        console.log(`Results: ${results.length}`);
    } catch (error) {
        console.log(`❌ Expected error - Type mismatch: ${error.message}`);
    }
}

/**
 * Main function to run all filtering examples.
 */
async function main() {
    console.log('Azure AI Search - Filtering Examples');
    console.log('='.repeat(80));

    try {
        // Create search client
        const searchClient = createSearchClient();
        console.log(`✅ Connected to search service: ${process.env.AZURE_SEARCH_SERVICE_ENDPOINT}`);
        console.log(`✅ Using index: ${process.env.AZURE_SEARCH_INDEX_NAME}`);

        // Run examples
        await equalityFilters(searchClient);
        await comparisonFilters(searchClient);
        await logicalOperators(searchClient);
        await dateFilters(searchClient);
        await collectionFilters(searchClient);
        await filterValidationExamples(searchClient);

        console.log('\n' + '='.repeat(80));
        console.log('✅ All filtering examples completed successfully!');
        console.log('='.repeat(80));

        console.log('\n📚 What you learned:');
        console.log('• How to use equality and comparison operators');
        console.log('• How to combine filters with logical operators');
        console.log('• How to filter by dates and numeric ranges');
        console.log('• How to work with collection fields');
        console.log('• How to handle filter validation and errors');

        console.log('\n🔗 Next steps:');
        console.log('• Run 03_sorting_pagination.js to learn about result ordering');
        console.log('• Experiment with complex filter combinations');
        console.log('• Try filters with your own data fields');

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