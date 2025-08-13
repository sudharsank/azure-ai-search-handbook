#!/usr/bin/env node

/**
 * Module 4: Simple Queries and Filters - Sorting and Pagination
 * =============================================================
 * 
 * This script demonstrates sorting and pagination in Azure AI Search using JavaScript.
 * Learn how to order results and efficiently navigate through large result sets.
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
        console.log(`   Price: $${document.price || 'N/A'}`);
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
 * Demonstrate basic sorting operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function basicSorting(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('BASIC SORTING EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Sort by relevance score (default)
    console.log('\n1. Default Sorting (Relevance Score)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', { top: 5 });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Default sort by relevance score');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Sort by date (descending - newest first)
    console.log('\n2. Sort by Date (Newest First)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['publishedDate desc'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Sort by publishedDate desc');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Sort by date (ascending - oldest first)
    console.log('\n3. Sort by Date (Oldest First)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['publishedDate asc'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Sort by publishedDate asc');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Sort by rating (highest first)
    console.log('\n4. Sort by Rating (Highest First)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['rating desc'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Sort by rating desc');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate multi-field sorting operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function multiFieldSorting(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('MULTI-FIELD SORTING EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Sort by category, then by rating
    console.log('\n1. Sort by Category, then Rating');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['category asc', 'rating desc'],
            top: 8
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Sort by category asc, rating desc', 8);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Sort by rating, then by date
    console.log('\n2. Sort by Rating, then Date');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['rating desc', 'publishedDate desc'],
            top: 8
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Sort by rating desc, publishedDate desc', 8);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Three-level sorting
    console.log('\n3. Three-Level Sorting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['price asc', 'rating desc', 'publishedDate desc'],
            top: 8
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Sort by price asc, rating desc, publishedDate desc', 8);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate sorting combined with search text and filters.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function sortingWithSearchAndFilters(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('SORTING WITH SEARCH AND FILTERS');
    console.log('='.repeat(80));

    // Example 1: Search + Filter + Sort
    console.log('\n1. Search + Filter + Sort');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            filter: 'rating ge 3.0',
            orderBy: ['rating desc'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, "Search 'azure' + rating >= 3.0 + sort by rating desc");
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Category filter with date sorting
    console.log('\n2. Category Filter with Date Sorting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            filter: "category eq 'Technology'",
            orderBy: ['publishedDate desc'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Technology category sorted by newest first');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Complex filter with multi-field sorting
    console.log('\n3. Complex Filter with Multi-field Sorting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('tutorial', {
            filter: 'rating ge 4.0 and publishedDate ge 2023-01-01T00:00:00Z',
            orderBy: ['rating desc', 'publishedDate desc'],
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Tutorial + high rating + recent + sorted');
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate basic pagination operations.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function basicPagination(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('BASIC PAGINATION EXAMPLES');
    console.log('='.repeat(80));

    const pageSize = 3;

    // Example 1: First page
    console.log('\n1. First Page');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            top: pageSize,
            skip: 0,
            orderBy: ['publishedDate desc']
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, `Page 1 (top ${pageSize}, skip 0)`, pageSize);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Second page
    console.log('\n2. Second Page');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            top: pageSize,
            skip: pageSize, // Skip first page
            orderBy: ['publishedDate desc']
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, `Page 2 (top ${pageSize}, skip ${pageSize})`, pageSize);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Third page
    console.log('\n3. Third Page');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            top: pageSize,
            skip: pageSize * 2, // Skip first two pages
            orderBy: ['publishedDate desc']
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, `Page 3 (top ${pageSize}, skip ${pageSize * 2})`, pageSize);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate pagination with total count for building navigation.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function paginationWithTotalCount(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('PAGINATION WITH TOTAL COUNT');
    console.log('='.repeat(80));

    const pageSize = 5;

    try {
        // Get first page with total count
        const searchResults = await searchClient.search('azure', {
            top: pageSize,
            skip: 0,
            includeTotalCount: true,
            orderBy: ['rating desc']
        });

        const results = await resultsToArray(searchResults);
        const totalCount = searchResults.count;
        const totalPages = Math.ceil(totalCount / pageSize);

        console.log(`\nPagination Summary:`);
        console.log(`Total documents: ${totalCount}`);
        console.log(`Page size: ${pageSize}`);
        console.log(`Total pages: ${totalPages}`);
        console.log(`Current page: 1`);

        displayResults(results, `Page 1 of ${totalPages}`);

        // Show pagination navigation info
        console.log(`\nNavigation:`);
        console.log(`• Previous: N/A (first page)`);
        console.log(`• Next: Page 2 (skip=${pageSize})`);
        console.log(`• Last: Page ${totalPages} (skip=${pageSize * (totalPages - 1)})`);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate advanced pagination patterns and utilities.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function advancedPaginationPatterns(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('ADVANCED PAGINATION PATTERNS');
    console.log('='.repeat(80));

    /**
     * Helper function for paginated search
     * @param {string} query - Search query
     * @param {number} page - Page number (1-based)
     * @param {number} pageSize - Number of results per page
     * @param {Array} orderBy - Sort expressions
     * @param {string} filterExpr - Filter expression
     * @returns {Promise<Object>} Pagination result
     */
    async function paginatedSearch(query, page = 1, pageSize = 5, orderBy = null, filterExpr = null) {
        const skip = (page - 1) * pageSize;

        const searchParams = {
            top: pageSize,
            skip: skip,
            includeTotalCount: true
        };

        if (orderBy) {
            searchParams.orderBy = orderBy;
        }
        if (filterExpr) {
            searchParams.filter = filterExpr;
        }

        try {
            const searchResults = await searchClient.search(query, searchParams);
            const results = await resultsToArray(searchResults);
            const totalCount = searchResults.count;
            const totalPages = Math.ceil(totalCount / pageSize);

            return {
                results: results,
                pagination: {
                    currentPage: page,
                    pageSize: pageSize,
                    totalCount: totalCount,
                    totalPages: totalPages,
                    hasPrevious: page > 1,
                    hasNext: page < totalPages,
                    previousPage: page > 1 ? page - 1 : null,
                    nextPage: page < totalPages ? page + 1 : null
                }
            };
        } catch (error) {
            return {
                results: [],
                pagination: {},
                error: error.message
            };
        }
    }

    // Example 1: Page 1
    console.log('\n1. Advanced Pagination - Page 1');
    console.log('-'.repeat(40));

    const result = await paginatedSearch(
        'azure',
        1,
        3,
        ['rating desc']
    );

    if (!result.error) {
        displayResults(result.results, 'Page 1 Results', 3);

        const pagination = result.pagination;
        console.log(`\nPagination Info:`);
        console.log(`• Page ${pagination.currentPage} of ${pagination.totalPages}`);
        console.log(`• Total results: ${pagination.totalCount}`);
        console.log(`• Has previous: ${pagination.hasPrevious}`);
        console.log(`• Has next: ${pagination.hasNext}`);
    } else {
        console.log(`Error: ${result.error}`);
    }

    // Example 2: Page 2
    console.log('\n2. Advanced Pagination - Page 2');
    console.log('-'.repeat(40));

    const result2 = await paginatedSearch(
        'azure',
        2,
        3,
        ['rating desc']
    );

    if (!result2.error) {
        displayResults(result2.results, 'Page 2 Results', 3);

        const pagination = result2.pagination;
        console.log(`\nPagination Info:`);
        console.log(`• Page ${pagination.currentPage} of ${pagination.totalPages}`);
        console.log(`• Previous page: ${pagination.previousPage}`);
        console.log(`• Next page: ${pagination.nextPage}`);
    } else {
        console.log(`Error: ${result2.error}`);
    }
}

/**
 * Demonstrate sorting performance optimization techniques.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function sortingPerformanceTips(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('SORTING PERFORMANCE OPTIMIZATION');
    console.log('='.repeat(80));

    // Example 1: Efficient sorting with filters
    console.log('\n1. Filter First, Then Sort');
    console.log('-'.repeat(40));

    try {
        const startTime = Date.now();

        const searchResults = await searchClient.search('azure', {
            filter: 'rating ge 3.0', // Filter reduces dataset first
            orderBy: ['rating desc'],
            top: 10
        });

        const results = await resultsToArray(searchResults);
        const executionTime = Date.now() - startTime;

        console.log(`Filtered + sorted query executed in ${executionTime}ms`);
        console.log(`Results: ${results.length} documents`);
        displayResults(results, 'Optimized: filter + sort', 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Limit result set size
    console.log('\n2. Limit Result Set Size');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            orderBy: ['publishedDate desc'],
            top: 20 // Reasonable page size
        });

        const results = await resultsToArray(searchResults);
        console.log(`Limited to top 20 results for better performance`);
        displayResults(results, 'Performance-optimized pagination', 5);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Simple vs Complex sort expressions
    console.log('\n3. Simple vs Complex Sort Expressions');
    console.log('-'.repeat(40));

    try {
        // Simple sort (better performance)
        const startTime1 = Date.now();
        const resultsSimple = await resultsToArray(
            await searchClient.search('azure', {
                orderBy: ['rating desc'], // Single field sort
                top: 5
            })
        );
        const time1 = Date.now() - startTime1;

        console.log(`Simple sort (single field): ${time1}ms - Better performance`);
        displayResults(resultsSimple, 'Simple sort by rating', 3);

        // Complex sort (may be slower)
        const startTime2 = Date.now();
        const resultsComplex = await resultsToArray(
            await searchClient.search('azure', {
                orderBy: ['rating desc', 'publishedDate desc', 'category asc'], // Multi-field sort
                top: 5
            })
        );
        const time2 = Date.now() - startTime2;

        console.log(`\nComplex sort (multiple fields): ${time2}ms - May be slower but more precise`);
        displayResults(resultsComplex, 'Complex multi-field sort', 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Main function to run all sorting and pagination examples.
 */
async function main() {
    console.log('Azure AI Search - Sorting and Pagination Examples');
    console.log('='.repeat(80));

    try {
        // Create search client
        const searchClient = createSearchClient();
        console.log(`✅ Connected to search service: ${process.env.AZURE_SEARCH_SERVICE_ENDPOINT}`);
        console.log(`✅ Using index: ${process.env.AZURE_SEARCH_INDEX_NAME}`);

        // Run examples
        await basicSorting(searchClient);
        await multiFieldSorting(searchClient);
        await sortingWithSearchAndFilters(searchClient);
        await basicPagination(searchClient);
        await paginationWithTotalCount(searchClient);
        await advancedPaginationPatterns(searchClient);
        await sortingPerformanceTips(searchClient);

        console.log('\n' + '='.repeat(80));
        console.log('✅ All sorting and pagination examples completed successfully!');
        console.log('='.repeat(80));

        console.log('\n📚 What you learned:');
        console.log('• How to sort results by single and multiple fields');
        console.log('• How to combine sorting with search and filters');
        console.log('• How to implement basic and advanced pagination');
        console.log('• How to get total counts for navigation');
        console.log('• How to optimize sorting performance');

        console.log('\n🔗 Next steps:');
        console.log('• Run 04_result_customization.js to learn about field selection');
        console.log('• Experiment with different sort combinations');
        console.log('• Build pagination UI components');

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