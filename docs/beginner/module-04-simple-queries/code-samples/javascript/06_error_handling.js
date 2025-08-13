#!/usr/bin/env node

/**
 * Module 4: Simple Queries and Filters - Error Handling
 * =====================================================
 * 
 * This script demonstrates comprehensive error handling for Azure AI Search queries using JavaScript.
 * Learn how to handle exceptions, validate queries, implement retry logic, and debug issues.
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
 * Create and return an Azure AI Search client with error handling.
 * @returns {SearchClient} Configured search client
 */
function createSearchClient() {
    const endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
    const apiKey = process.env.AZURE_SEARCH_API_KEY;
    const indexName = process.env.AZURE_SEARCH_INDEX_NAME;

    if (!endpoint || !apiKey || !indexName) {
        const missing = [];
        if (!endpoint) missing.push('AZURE_SEARCH_SERVICE_ENDPOINT');
        if (!apiKey) missing.push('AZURE_SEARCH_API_KEY');
        if (!indexName) missing.push('AZURE_SEARCH_INDEX_NAME');
        
        throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }

    try {
        const client = new SearchClient(endpoint, indexName, new AzureKeyCredential(apiKey));
        console.log(`✅ Successfully created search client for index: ${indexName}`);
        return client;
    } catch (error) {
        console.error(`❌ Failed to create search client: ${error.message}`);
        throw error;
    }
}

/**
 * Validate search query parameters before execution.
 * @param {string} searchText - Search query text
 * @param {Object} options - Search options
 * @returns {Object} Validation result with isValid and errorMessage
 */
function validateQueryParameters(searchText = null, options = {}) {
    // Check search text
    if (searchText !== null) {
        if (typeof searchText === 'string' && searchText.trim().length === 0) {
            return { isValid: false, errorMessage: 'Search text cannot be empty' };
        }

        if (typeof searchText === 'string' && searchText.length > 1000) {
            return { isValid: false, errorMessage: 'Search text too long (max 1000 characters)' };
        }

        // Check for unbalanced quotes
        if (typeof searchText === 'string' && (searchText.match(/"/g) || []).length % 2 !== 0) {
            return { isValid: false, errorMessage: 'Unbalanced quotes in search text' };
        }

        // Check for unbalanced parentheses
        if (typeof searchText === 'string') {
            const openParens = (searchText.match(/\(/g) || []).length;
            const closeParens = (searchText.match(/\)/g) || []).length;
            if (openParens !== closeParens) {
                return { isValid: false, errorMessage: 'Unbalanced parentheses in search text' };
            }
        }
    }

    // Check top parameter
    if (options.top !== undefined) {
        if (!Number.isInteger(options.top) || options.top < 0) {
            return { isValid: false, errorMessage: 'Top parameter must be a non-negative integer' };
        }
        if (options.top > 1000) {
            return { isValid: false, errorMessage: 'Top parameter cannot exceed 1000' };
        }
    }

    // Check skip parameter
    if (options.skip !== undefined) {
        if (!Number.isInteger(options.skip) || options.skip < 0) {
            return { isValid: false, errorMessage: 'Skip parameter must be a non-negative integer' };
        }
        if (options.skip > 100000) {
            return { isValid: false, errorMessage: 'Skip parameter cannot exceed 100,000' };
        }
    }

    // Check filter syntax (basic validation)
    if (options.filter) {
        // Check for unbalanced parentheses
        const openParens = (options.filter.match(/\(/g) || []).length;
        const closeParens = (options.filter.match(/\)/g) || []).length;
        if (openParens !== closeParens) {
            return { isValid: false, errorMessage: 'Unbalanced parentheses in filter expression' };
        }

        // Check for invalid operators
        const invalidOperators = ['=', '!=', '<>', '&&', '||'];
        for (const op of invalidOperators) {
            if (options.filter.includes(op)) {
                return { isValid: false, errorMessage: `Invalid operator '${op}' in filter (use OData syntax)` };
            }
        }
    }

    return { isValid: true, errorMessage: 'Query parameters are valid' };
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
 * Perform a safe search with comprehensive error handling.
 * @param {SearchClient} searchClient - Azure AI Search client
 * @param {string} searchText - Search text
 * @param {Object} options - Search options
 * @returns {Promise<Object>} Object with results and error
 */
async function safeSearch(searchClient, searchText, options = {}) {
    try {
        // Validate parameters
        const validation = validateQueryParameters(searchText, options);
        if (!validation.isValid) {
            console.warn(`⚠️  Query validation failed: ${validation.errorMessage}`);
            return { results: [], error: validation.errorMessage };
        }

        // Log the search attempt
        console.log(`🔍 Executing search: '${searchText}' with options:`, JSON.stringify(options, null, 2));

        // Execute search
        const searchResults = await searchClient.search(searchText, options);
        const results = await resultsToArray(searchResults);

        console.log(`✅ Search completed successfully: ${results.length} results`);
        return { results, error: null };

    } catch (error) {
        let errorMsg;
        if (error.statusCode) {
            errorMsg = `HTTP error ${error.statusCode}: ${error.message}`;
        } else {
            errorMsg = `Unexpected error: ${error.message}`;
        }
        
        console.error(`❌ ${errorMsg}`);
        return { results: [], error: errorMsg };
    }
}

/**
 * Perform search with retry logic for transient failures.
 * @param {SearchClient} searchClient - Azure AI Search client
 * @param {string} searchText - Search text
 * @param {Object} options - Search options
 * @param {number} maxRetries - Maximum number of retry attempts
 * @param {number} retryDelayMs - Delay between retries in milliseconds
 * @returns {Promise<Object>} Object with results and error
 */
async function retrySearch(searchClient, searchText, options = {}, maxRetries = 3, retryDelayMs = 1000) {
    let lastError = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            if (attempt > 0) {
                console.log(`🔄 Retry attempt ${attempt}/${maxRetries}`);
                await new Promise(resolve => setTimeout(resolve, retryDelayMs * attempt)); // Exponential backoff
            }

            const result = await safeSearch(searchClient, searchText, options);

            if (result.error === null) {
                if (attempt > 0) {
                    console.log(`✅ Search succeeded on retry attempt ${attempt}`);
                }
                return result;
            } else {
                lastError = result.error;
                // Don't retry for validation errors or client errors (4xx)
                if (result.error.includes('validation') || result.error.includes('400')) {
                    break;
                }
            }
        } catch (error) {
            lastError = error.message;
            console.warn(`⚠️  Attempt ${attempt + 1} failed: ${lastError}`);
        }
    }

    console.error(`❌ Search failed after ${maxRetries + 1} attempts`);
    return { results: [], error: lastError };
}

/**
 * Demonstrate common search errors and how to handle them.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function demonstrateCommonErrors(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('COMMON ERROR SCENARIOS');
    console.log('='.repeat(80));

    const errorScenarios = [
        {
            name: 'Empty Search Text',
            searchText: '',
            options: {},
            expected: 'Empty search text should be caught by validation'
        },
        {
            name: 'Invalid Filter Syntax',
            searchText: '*',
            options: { filter: "category = 'Technology'" }, // Should be 'eq'
            expected: 'Invalid OData syntax should return 400 error'
        },
        {
            name: 'Non-existent Field in Filter',
            searchText: '*',
            options: { filter: "nonexistent_field eq 'value'" },
            expected: 'Unknown field should return 400 error'
        },
        {
            name: 'Invalid Top Parameter',
            searchText: '*',
            options: { top: -1 },
            expected: 'Negative top parameter should be caught by validation'
        },
        {
            name: 'Unbalanced Quotes',
            searchText: '"unbalanced quote',
            options: {},
            expected: 'Unbalanced quotes should be caught by validation'
        },
        {
            name: 'Invalid Order By Field',
            searchText: '*',
            options: { orderBy: ['nonexistent_field desc'] },
            expected: 'Unknown sort field should return 400 error'
        }
    ];

    for (let i = 0; i < errorScenarios.length; i++) {
        const scenario = errorScenarios[i];
        console.log(`\n${i + 1}. ${scenario.name}`);
        console.log('-'.repeat(40));
        console.log(`Expected: ${scenario.expected}`);

        const result = await safeSearch(searchClient, scenario.searchText, scenario.options);

        if (result.error) {
            console.log(`✅ Error handled correctly: ${result.error}`);
        } else {
            console.log(`⚠️  Unexpected success: ${result.results.length} results returned`);
        }
    }
}

/**
 * Demonstrate retry logic for handling transient failures.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function demonstrateRetryLogic(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('RETRY LOGIC DEMONSTRATION');
    console.log('='.repeat(80));

    // Example 1: Successful search (no retries needed)
    console.log('\n1. Successful Search (No Retries)');
    console.log('-'.repeat(40));

    const result1 = await retrySearch(searchClient, 'azure', { top: 3 }, 2);

    if (result1.error) {
        console.log(`❌ Search failed: ${result1.error}`);
    } else {
        console.log(`✅ Search succeeded: ${result1.results.length} results`);
    }

    // Example 2: Search with validation error (no retries)
    console.log('\n2. Validation Error (No Retries)');
    console.log('-'.repeat(40));

    const result2 = await retrySearch(searchClient, '', {}, 2); // Empty search text

    if (result2.error) {
        console.log(`✅ Validation error (no retries): ${result2.error}`);
    } else {
        console.log(`⚠️  Unexpected success: ${result2.results.length} results`);
    }

    // Example 3: Simulate timeout scenario
    console.log('\n3. Timeout Handling');
    console.log('-'.repeat(40));

    try {
        const result3 = await retrySearch(
            searchClient,
            'azure machine learning tutorial guide',
            { top: 100 }, // Large result set
            1,
            500
        );

        if (result3.error) {
            console.log(`Handled potential timeout: ${result3.error}`);
        } else {
            console.log(`Search completed: ${result3.results.length} results`);
        }
    } catch (error) {
        console.log(`Timeout simulation: ${error.message}`);
    }
}

/**
 * Demonstrate tools and techniques for debugging search queries.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function queryDebuggingTools(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('QUERY DEBUGGING TOOLS');
    console.log('='.repeat(80));

    /**
     * Helper function to debug a search query.
     * @param {string} description - Description of the query
     * @param {string} searchText - Search text
     * @param {Object} options - Search options
     */
    async function debugSearch(description, searchText, options = {}) {
        console.log(`\n${description}`);
        console.log('-'.repeat(40));

        // Log query details
        console.log(`Query: '${searchText}'`);

        if (options.filter) {
            console.log(`Filter: ${options.filter}`);
        }
        if (options.orderBy) {
            console.log(`Order by: ${options.orderBy.join(', ')}`);
        }
        if (options.top) {
            console.log(`Top: ${options.top}`);
        }

        // Validate first
        const validation = validateQueryParameters(searchText, options);
        if (!validation.isValid) {
            console.log(`❌ Validation failed: ${validation.errorMessage}`);
            return;
        }

        // Execute with timing
        const startTime = Date.now();
        const result = await safeSearch(searchClient, searchText, options);
        const executionTime = Date.now() - startTime;

        if (result.error === null) {
            console.log(`✅ Query succeeded in ${executionTime}ms`);
            console.log(`   Results: ${result.results.length}`);

            if (result.results.length > 0) {
                // Show score distribution
                const scores = result.results.map(r => r.score);
                console.log(`   Score range: ${Math.min(...scores).toFixed(3)} - ${Math.max(...scores).toFixed(3)}`);

                // Show top result
                const topResult = result.results[0];
                const title = topResult.document.title || 'No title';
                console.log(`   Top result: ${title.substring(0, 50)}...`);
            }
        } else {
            console.log(`❌ Query failed: ${result.error}`);
        }
    }

    // Debug various query types
    await debugSearch('1. Basic Text Search', 'azure machine learning');

    await debugSearch('2. Filtered Search', 'tutorial', { filter: 'rating ge 4.0' });

    await debugSearch('3. Complex Query', 'python OR java', {
        filter: "category eq 'Technology'",
        orderBy: ['rating desc'],
        top: 5
    });

    await debugSearch('4. Problematic Query (Invalid Filter)', 'azure', {
        filter: 'invalid_field eq \'value\''
    });
}

/**
 * Demonstrate performance monitoring and optimization techniques.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function performanceMonitoring(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('PERFORMANCE MONITORING');
    console.log('='.repeat(80));

    /**
     * Monitor and report query performance.
     * @param {string} description - Description of the query
     * @param {string} searchText - Search text
     * @param {Object} options - Search options
     */
    async function monitorQueryPerformance(description, searchText, options = {}) {
        console.log(`\n${description}`);
        console.log('-'.repeat(40));

        // Multiple runs for average timing
        const times = [];
        const resultCounts = [];

        for (let run = 0; run < 3; run++) {
            const startTime = Date.now();
            const result = await safeSearch(searchClient, searchText, options);
            const executionTime = Date.now() - startTime;

            if (result.error) {
                console.log(`Run ${run + 1}: Failed - ${result.error}`);
                return;
            }

            times.push(executionTime);
            resultCounts.push(result.results.length);
        }

        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const avgResults = resultCounts.reduce((a, b) => a + b, 0) / resultCounts.length;

        console.log(`Average execution time: ${avgTime.toFixed(0)}ms`);
        console.log(`Average result count: ${avgResults.toFixed(0)}`);
        console.log(`Time range: ${Math.min(...times)}ms - ${Math.max(...times)}ms`);

        // Performance assessment
        if (avgTime < 100) {
            console.log('✅ Excellent performance');
        } else if (avgTime < 500) {
            console.log('✅ Good performance');
        } else if (avgTime < 1000) {
            console.log('⚠️  Acceptable performance');
        } else {
            console.log('❌ Poor performance - consider optimization');
        }
    }

    // Monitor different query types
    await monitorQueryPerformance('1. Simple Query Performance', 'azure', { top: 10 });

    await monitorQueryPerformance('2. Complex Query Performance', 'machine learning tutorial', {
        filter: "rating ge 3.0 and category eq 'Technology'",
        orderBy: ['rating desc', 'publishedDate desc'],
        top: 20
    });

    await monitorQueryPerformance('3. Large Result Set Performance', '*', { top: 100 });
}

/**
 * Demonstrate error recovery strategies for production applications.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function errorRecoveryStrategies(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('ERROR RECOVERY STRATEGIES');
    console.log('='.repeat(80));

    /**
     * Perform search with graceful fallback to simpler query.
     * @param {string} primaryQuery - Primary search query to try
     * @param {string} fallbackQuery - Fallback query if primary fails
     * @returns {Promise<Array>} Search results
     */
    async function gracefulSearchWithFallback(primaryQuery, fallbackQuery = null) {
        console.log(`\nTrying primary query: '${primaryQuery}'`);

        // Try primary query
        const result1 = await safeSearch(searchClient, primaryQuery, { top: 5 });

        if (result1.error === null && result1.results.length > 0) {
            console.log(`✅ Primary query succeeded: ${result1.results.length} results`);
            return result1.results;
        }

        console.log(`❌ Primary query failed: ${result1.error}`);

        // Try fallback query
        if (fallbackQuery) {
            console.log(`Trying fallback query: '${fallbackQuery}'`);

            const result2 = await safeSearch(searchClient, fallbackQuery, { top: 5 });

            if (result2.error === null) {
                console.log(`✅ Fallback query succeeded: ${result2.results.length} results`);
                return result2.results;
            } else {
                console.log(`❌ Fallback query also failed: ${result2.error}`);
            }
        }

        // Final fallback - return all documents
        console.log('Trying final fallback: return all documents');
        const result3 = await safeSearch(searchClient, '*', { top: 5 });

        if (result3.error === null) {
            console.log(`✅ Final fallback succeeded: ${result3.results.length} results`);
            return result3.results;
        } else {
            console.log(`❌ All queries failed: ${result3.error}`);
            return [];
        }
    }

    // Demonstrate fallback strategies
    console.log('\n1. Complex to Simple Query Fallback');
    await gracefulSearchWithFallback(
        'title:"machine learning" AND content:python',
        'machine learning python'
    );

    console.log('\n2. Typo to Corrected Query Fallback');
    await gracefulSearchWithFallback(
        'machne learing', // Typos
        'machine learning' // Corrected
    );

    console.log('\n3. Specific to General Query Fallback');
    await gracefulSearchWithFallback(
        'azure cognitive services computer vision api',
        'azure cognitive services'
    );
}

/**
 * Main function to run all error handling examples.
 */
async function main() {
    console.log('Azure AI Search - Error Handling Examples');
    console.log('='.repeat(80));

    try {
        // Create search client with error handling
        const searchClient = createSearchClient();
        console.log(`✅ Connected to search service: ${process.env.AZURE_SEARCH_SERVICE_ENDPOINT}`);
        console.log(`✅ Using index: ${process.env.AZURE_SEARCH_INDEX_NAME}`);

        // Run examples
        await demonstrateCommonErrors(searchClient);
        await demonstrateRetryLogic(searchClient);
        await queryDebuggingTools(searchClient);
        await performanceMonitoring(searchClient);
        await errorRecoveryStrategies(searchClient);

        console.log('\n' + '='.repeat(80));
        console.log('✅ All error handling examples completed successfully!');
        console.log('='.repeat(80));

        console.log('\n📚 What you learned:');
        console.log('• How to validate query parameters before execution');
        console.log('• How to handle different types of Azure AI Search exceptions');
        console.log('• How to implement retry logic for transient failures');
        console.log('• How to debug and troubleshoot search queries');
        console.log('• How to monitor query performance');
        console.log('• How to implement graceful error recovery strategies');

        console.log('\n🔗 Next steps:');
        console.log('• Apply these patterns to your production applications');
        console.log('• Set up monitoring and alerting for search errors');
        console.log('• Create custom error handling for your specific use cases');
        console.log('• Move on to Module 5 for advanced querying techniques');

        console.log('\n💡 Production Tips:');
        console.log('• Always validate user input before sending to search');
        console.log('• Implement proper logging for debugging');
        console.log('• Use retry logic for transient network issues');
        console.log('• Provide fallback queries for better user experience');
        console.log('• Monitor query performance and optimize slow queries');

    } catch (error) {
        if (error.message.includes('Missing required environment variables')) {
            console.error(`❌ Configuration error: ${error.message}`);
            console.log('\n🔧 Setup required:');
            console.log('1. Create a .env file with your Azure AI Search credentials');
            console.log('2. Ensure you have completed previous modules to create sample indexes');
            process.exit(1);
        } else {
            console.error(`❌ Unexpected error: ${error.message}`);
            console.error(error.stack);
            process.exit(1);
        }
    }
}

// Run the main function
main().catch(console.error);