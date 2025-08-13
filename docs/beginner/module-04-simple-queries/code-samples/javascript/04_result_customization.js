#!/usr/bin/env node

/**
 * Module 4: Simple Queries and Filters - Result Customization
 * ===========================================================
 * 
 * This script demonstrates result customization in Azure AI Search using JavaScript.
 * Learn how to select specific fields, highlight matching terms, and format results.
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
 * Display search results in a formatted way with highlighting support.
 * @param {Array} results - Array of search result documents
 * @param {string} title - Title for the result set
 * @param {number} maxResults - Maximum number of results to display
 * @param {boolean} showHighlights - Whether to display highlight information
 */
function displayResults(results, title, maxResults = 5, showHighlights = false) {
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
        
        // Show selected fields
        for (const [key, value] of Object.entries(document)) {
            if (!key.startsWith('@search') && key !== 'title') {
                if (Array.isArray(value)) {
                    const display = value.slice(0, 3).join(', ');
                    const suffix = value.length > 3 ? '...' : '';
                    console.log(`   ${key}: ${display}${suffix}`);
                } else if (typeof value === 'string' && value.length > 100) {
                    console.log(`   ${key}: ${value.substring(0, 100)}...`);
                } else {
                    console.log(`   ${key}: ${value}`);
                }
            }
        }
        
        // Show highlights if requested and available
        if (showHighlights && document['@search.highlights']) {
            const highlights = document['@search.highlights'];
            console.log('   Highlights:');
            for (const [field, highlightList] of Object.entries(highlights)) {
                for (const highlight of highlightList.slice(0, 2)) {
                    console.log(`     ${field}: ${highlight}`);
                }
            }
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
 * Demonstrate field selection to customize returned data.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function fieldSelectionExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('FIELD SELECTION EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: All fields (default behavior)
    console.log('\n1. All Fields (Default)');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', { top: 2 });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'All fields returned', 2);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Select specific fields
    console.log('\n2. Select Specific Fields');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            select: ['id', 'title', 'category', 'rating'],
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Selected fields: id, title, category, rating', 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Minimal field selection for performance
    console.log('\n3. Minimal Fields for Performance');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            select: ['id', 'title'], // Only essential fields
            top: 5
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Minimal fields: id, title only', 5);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Exclude large content fields
    console.log('\n4. Exclude Large Content Fields');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('tutorial', {
            select: ['id', 'title', 'category', 'rating', 'publishedDate'], // Exclude 'content'
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Exclude large content field', 3);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate search result highlighting.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function searchHighlightingExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('SEARCH HIGHLIGHTING EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Basic highlighting
    console.log('\n1. Basic Highlighting');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('machine learning', {
            highlightFields: ['title', 'content'],
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Basic highlighting on title and content', 3, true);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Custom highlight tags
    console.log('\n2. Custom Highlight Tags');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure search', {
            highlightFields: ['title', 'content'],
            highlightPreTag: '<mark>',
            highlightPostTag: '</mark>',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Custom highlight tags: <mark>...</mark>', 3, true);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Multiple highlight tags for different terms
    console.log('\n3. Multiple Highlight Tags');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python tutorial', {
            highlightFields: ['title', 'content'],
            highlightPreTag: '<strong class="highlight">',
            highlightPostTag: '</strong>',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'HTML highlight tags with CSS class', 3, true);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 4: Highlighting with field selection
    console.log('\n4. Highlighting with Field Selection');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure cognitive', {
            select: ['id', 'title', 'category'],
            highlightFields: ['title'], // Only highlight title
            highlightPreTag: '**',
            highlightPostTag: '**',
            top: 3
        });
        const results = await resultsToArray(searchResults);
        displayResults(results, 'Selected fields + title highlighting', 3, true);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate working with search result metadata.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function resultMetadataExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('RESULT METADATA EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Search score analysis
    console.log('\n1. Search Score Analysis');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure machine learning', { top: 5 });
        const results = await resultsToArray(searchResults);

        console.log('Search Score Analysis:');
        console.log('-'.repeat(30));
        for (let i = 0; i < results.length; i++) {
            const result = results[i];
            const score = result.score;
            const title = result.document.title || 'No title';
            console.log(`${i + 1}. Score: ${score.toFixed(4)} - ${title.substring(0, 50)}...`);
        }

        if (results.length > 0) {
            const scores = results.map(r => r.score);
            console.log(`\nScore Statistics:`);
            console.log(`• Highest: ${Math.max(...scores).toFixed(4)}`);
            console.log(`• Lowest: ${Math.min(...scores).toFixed(4)}`);
            console.log(`• Average: ${(scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(4)}`);
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Highlight metadata
    console.log('\n2. Highlight Metadata Analysis');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python programming', {
            highlightFields: ['title', 'content'],
            top: 3
        });
        const results = await resultsToArray(searchResults);

        console.log('Highlight Analysis:');
        console.log('-'.repeat(30));
        for (let i = 0; i < results.length; i++) {
            const result = results[i];
            const title = result.document.title || 'No title';
            console.log(`\n${i + 1}. ${title}`);

            if (result.document['@search.highlights']) {
                const highlights = result.document['@search.highlights'];
                for (const [field, highlightList] of Object.entries(highlights)) {
                    console.log(`   ${field} highlights: ${highlightList.length}`);
                    for (let j = 0; j < Math.min(2, highlightList.length); j++) {
                        console.log(`     ${j + 1}: ${highlightList[j]}`);
                    }
                }
            } else {
                console.log('   No highlights found');
            }
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate custom result formatting and processing.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function customResultFormatting(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('CUSTOM RESULT FORMATTING');
    console.log('='.repeat(80));

    /**
     * Custom formatter for search results.
     * @param {Object} result - Raw search result
     * @returns {Object} Formatted result object
     */
    function formatSearchResult(result) {
        const document = result.document;
        const formatted = {
            id: document.id,
            title: document.title || 'Untitled',
            summary: getContentSummary(document.content),
            metadata: {
                score: Math.round(result.score * 1000) / 1000,
                category: document.category || 'Uncategorized',
                rating: document.rating,
                published: document.publishedDate,
                tags: getTags(document.tags)
            }
        };

        // Add highlights if available
        if (document['@search.highlights']) {
            formatted.highlights = {};
            for (const [field, highlights] of Object.entries(document['@search.highlights'])) {
                formatted.highlights[field] = highlights.slice(0, 2); // Limit to 2 per field
            }
        }

        return formatted;
    }

    /**
     * Get content summary.
     * @param {string} content - Full content
     * @returns {string} Summary
     */
    function getContentSummary(content) {
        if (!content) return '';
        return content.length > 150 ? content.substring(0, 150) + '...' : content;
    }

    /**
     * Get tags list.
     * @param {Array} tags - Tags array
     * @returns {Array} Limited tags list
     */
    function getTags(tags) {
        if (!Array.isArray(tags)) return [];
        return tags.slice(0, 5); // Limit to 5 tags
    }

    // Example 1: Custom formatted results
    console.log('\n1. Custom Formatted Results');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure tutorial', {
            select: ['id', 'title', 'content', 'category', 'rating', 'publishedDate', 'tags'],
            highlightFields: ['title', 'content'],
            top: 3
        });
        const results = await resultsToArray(searchResults);
        const formattedResults = results.map(formatSearchResult);

        console.log('Custom Formatted Results:');
        for (let i = 0; i < formattedResults.length; i++) {
            const result = formattedResults[i];
            console.log(`\n${i + 1}. ${result.title}`);
            console.log(`   Summary: ${result.summary}`);
            console.log(`   Score: ${result.metadata.score}`);
            console.log(`   Category: ${result.metadata.category}`);
            console.log(`   Rating: ${result.metadata.rating}`);
            console.log(`   Tags: ${result.metadata.tags.join(', ')}`);

            if (result.highlights) {
                console.log(`   Highlights: ${Object.keys(result.highlights).length} fields`);
            }
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: JSON export format
    console.log('\n2. JSON Export Format');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('python', {
            select: ['id', 'title', 'category', 'rating'],
            top: 2
        });
        const results = await resultsToArray(searchResults);

        // Convert to JSON-serializable format
        const jsonResults = results.map(result => {
            const jsonResult = {};
            for (const [key, value] of Object.entries(result.document)) {
                if (!key.startsWith('@search')) {
                    jsonResult[key] = value;
                } else if (key === '@search.score') {
                    jsonResult.searchScore = Math.round(result.score * 1000) / 1000;
                }
            }
            return jsonResult;
        });

        console.log('JSON Export Format:');
        console.log(JSON.stringify(jsonResults, null, 2));
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate result aggregation and summary statistics.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function resultAggregationExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('RESULT AGGREGATION EXAMPLES');
    console.log('='.repeat(80));

    // Example 1: Category distribution
    console.log('\n1. Category Distribution Analysis');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            select: ['category', 'rating'],
            top: 50 // Get more results for analysis
        });
        const results = await resultsToArray(searchResults);

        // Aggregate by category
        const categoryStats = {};

        for (const result of results) {
            const category = result.document.category || 'Unknown';
            const rating = result.document.rating;

            if (!categoryStats[category]) {
                categoryStats[category] = {
                    count: 0,
                    ratings: []
                };
            }

            categoryStats[category].count++;
            if (rating !== null && rating !== undefined) {
                categoryStats[category].ratings.push(rating);
            }
        }

        console.log('Category Distribution:');
        for (const [category, stats] of Object.entries(categoryStats)) {
            const avgRating = stats.ratings.length > 0 
                ? stats.ratings.reduce((a, b) => a + b, 0) / stats.ratings.length 
                : 0;
            console.log(`• ${category}: ${stats.count} documents (avg rating: ${avgRating.toFixed(1)})`);
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Rating distribution
    console.log('\n2. Rating Distribution Analysis');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('*', {
            select: ['rating'],
            top: 50
        });
        const results = await resultsToArray(searchResults);

        // Aggregate by rating ranges
        const ratingRanges = {
            '5.0': 0,
            '4.0-4.9': 0,
            '3.0-3.9': 0,
            '2.0-2.9': 0,
            '1.0-1.9': 0,
            'No rating': 0
        };

        for (const result of results) {
            const rating = result.document.rating;
            if (rating === null || rating === undefined) {
                ratingRanges['No rating']++;
            } else if (rating >= 5.0) {
                ratingRanges['5.0']++;
            } else if (rating >= 4.0) {
                ratingRanges['4.0-4.9']++;
            } else if (rating >= 3.0) {
                ratingRanges['3.0-3.9']++;
            } else if (rating >= 2.0) {
                ratingRanges['2.0-2.9']++;
            } else {
                ratingRanges['1.0-1.9']++;
            }
        }

        console.log('Rating Distribution:');
        for (const [range, count] of Object.entries(ratingRanges)) {
            const percentage = results.length > 0 ? (count / results.length) * 100 : 0;
            console.log(`• ${range}: ${count} documents (${percentage.toFixed(1)}%)`);
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Demonstrate performance optimization techniques for result customization.
 * @param {SearchClient} searchClient - Azure AI Search client
 */
async function performanceOptimizationExamples(searchClient) {
    console.log('\n' + '='.repeat(80));
    console.log('PERFORMANCE OPTIMIZATION');
    console.log('='.repeat(80));

    // Example 1: Field selection performance comparison
    console.log('\n1. Field Selection Performance');
    console.log('-'.repeat(40));

    try {
        // All fields query
        const startTime1 = Date.now();
        const resultsAll = await resultsToArray(
            await searchClient.search('azure', { top: 20 })
        );
        const timeAll = Date.now() - startTime1;

        // Selected fields query
        const startTime2 = Date.now();
        const resultsSelected = await resultsToArray(
            await searchClient.search('azure', {
                select: ['id', 'title', 'category'],
                top: 20
            })
        );
        const timeSelected = Date.now() - startTime2;

        console.log(`All fields query: ${timeAll}ms (${resultsAll.length} results)`);
        console.log(`Selected fields query: ${timeSelected}ms (${resultsSelected.length} results)`);

        if (timeAll > 0) {
            const improvement = ((timeAll - timeSelected) / timeAll) * 100;
            console.log(`Performance improvement: ${improvement.toFixed(1)}%`);
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 2: Highlighting performance impact
    console.log('\n2. Highlighting Performance Impact');
    console.log('-'.repeat(40));

    try {
        // Without highlighting
        const startTime1 = Date.now();
        const resultsNoHighlight = await resultsToArray(
            await searchClient.search('machine learning tutorial', {
                select: ['id', 'title', 'category'],
                top: 10
            })
        );
        const timeNoHighlight = Date.now() - startTime1;

        // With highlighting
        const startTime2 = Date.now();
        const resultsHighlight = await resultsToArray(
            await searchClient.search('machine learning tutorial', {
                select: ['id', 'title', 'category'],
                highlightFields: ['title', 'content'],
                top: 10
            })
        );
        const timeHighlight = Date.now() - startTime2;

        console.log(`Without highlighting: ${timeNoHighlight}ms`);
        console.log(`With highlighting: ${timeHighlight}ms`);

        if (timeNoHighlight > 0) {
            const overhead = ((timeHighlight - timeNoHighlight) / timeNoHighlight) * 100;
            console.log(`Highlighting overhead: ${overhead.toFixed(1)}%`);
        }
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }

    // Example 3: Optimal result customization
    console.log('\n3. Optimal Result Customization');
    console.log('-'.repeat(40));

    try {
        const searchResults = await searchClient.search('azure', {
            select: ['id', 'title', 'category', 'rating'], // Only needed fields
            highlightFields: ['title'], // Minimal highlighting
            top: 10, // Reasonable page size
            filter: 'rating ge 3.0' // Pre-filter for better performance
        });
        const results = await resultsToArray(searchResults);

        console.log('Optimized query configuration:');
        console.log('• Selected essential fields only');
        console.log('• Limited highlighting to title field');
        console.log('• Used reasonable page size (10)');
        console.log('• Applied pre-filter to reduce dataset');
        console.log(`• Results: ${results.length} documents`);

        displayResults(results, 'Optimized results', 3, true);
    } catch (error) {
        console.error(`Search failed: ${error.message}`);
    }
}

/**
 * Main function to run all result customization examples.
 */
async function main() {
    console.log('Azure AI Search - Result Customization Examples');
    console.log('='.repeat(80));

    try {
        // Create search client
        const searchClient = createSearchClient();
        console.log(`✅ Connected to search service: ${process.env.AZURE_SEARCH_SERVICE_ENDPOINT}`);
        console.log(`✅ Using index: ${process.env.AZURE_SEARCH_INDEX_NAME}`);

        // Run examples
        await fieldSelectionExamples(searchClient);
        await searchHighlightingExamples(searchClient);
        await resultMetadataExamples(searchClient);
        await customResultFormatting(searchClient);
        await resultAggregationExamples(searchClient);
        await performanceOptimizationExamples(searchClient);

        console.log('\n' + '='.repeat(80));
        console.log('✅ All result customization examples completed successfully!');
        console.log('='.repeat(80));

        console.log('\n📚 What you learned:');
        console.log('• How to select specific fields to optimize performance');
        console.log('• How to implement search result highlighting');
        console.log('• How to work with search metadata and scores');
        console.log('• How to format and process results for different use cases');
        console.log('• How to aggregate and analyze result data');
        console.log('• How to optimize result customization for performance');

        console.log('\n🔗 Next steps:');
        console.log('• Run 05_advanced_queries.js to learn advanced query techniques');
        console.log('• Experiment with different field combinations');
        console.log('• Build custom result formatters for your applications');

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