/**
 * Module 7: Result Counting and Totals Management
 * 
 * This example demonstrates how to manage result counts effectively,
 * including performance considerations and different counting strategies.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Configuration
const config = {
    endpoint: process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net',
    apiKey: process.env.SEARCH_API_KEY || 'your-api-key',
    indexName: process.env.INDEX_NAME || 'hotels-sample'
};

class ResultCounter {
    constructor(searchClient) {
        this.searchClient = searchClient;
        this.countCache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Search with exact result count
     */
    async searchWithExactCount(searchText, options = {}) {
        try {
            const searchOptions = {
                includeTotalCount: true,
                top: options.top || 10,
                skip: options.skip || 0,
                ...options
            };

            console.log(`Searching with exact count: "${searchText}"`);
            
            const startTime = Date.now();
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;

            return {
                results: results.results,
                totalCount: results.count,
                currentPage: Math.floor((options.skip || 0) / (options.top || 10)),
                pageSize: options.top || 10,
                totalPages: Math.ceil((results.count || 0) / (options.top || 10)),
                duration,
                countingEnabled: true
            };

        } catch (error) {
            console.error('Search with exact count error:', error);
            throw error;
        }
    }

    /**
     * Search without count for better performance
     */
    async searchWithoutCount(searchText, options = {}) {
        try {
            const searchOptions = {
                includeTotalCount: false,
                top: options.top || 10,
                skip: options.skip || 0,
                ...options
            };

            console.log(`Searching without count: "${searchText}"`);
            
            const startTime = Date.now();
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;

            // Estimate if there are more results
            const hasMoreResults = results.results.length === (options.top || 10);
            const estimatedCount = hasMoreResults ? `${(options.skip || 0) + results.results.length}+` : (options.skip || 0) + results.results.length;

            return {
                results: results.results,
                totalCount: null,
                estimatedCount,
                hasMoreResults,
                currentPage: Math.floor((options.skip || 0) / (options.top || 10)),
                pageSize: options.top || 10,
                duration,
                countingEnabled: false
            };

        } catch (error) {
            console.error('Search without count error:', error);
            throw error;
        }
    }

    /**
     * Smart counting - use cache or skip count based on context
     */
    async searchWithSmartCounting(searchText, options = {}) {
        try {
            const cacheKey = this.generateCacheKey(searchText, options);
            const cached = this.getCachedCount(cacheKey);

            // Use cached count if available and not expired
            if (cached) {
                console.log('Using cached count');
                const searchOptions = {
                    includeTotalCount: false,
                    ...options
                };

                const results = await this.searchClient.search(searchText, searchOptions);
                
                return {
                    results: results.results,
                    totalCount: cached.count,
                    totalPages: Math.ceil(cached.count / (options.top || 10)),
                    currentPage: Math.floor((options.skip || 0) / (options.top || 10)),
                    pageSize: options.top || 10,
                    countingEnabled: true,
                    fromCache: true
                };
            }

            // Get fresh count and cache it
            const result = await this.searchWithExactCount(searchText, options);
            this.setCachedCount(cacheKey, result.totalCount);
            
            return {
                ...result,
                fromCache: false
            };

        } catch (error) {
            console.error('Smart counting error:', error);
            throw error;
        }
    }

    /**
     * Conditional counting based on result size expectations
     */
    async searchWithConditionalCounting(searchText, options = {}) {
        try {
            const shouldCount = this.shouldEnableCounting(searchText, options);
            
            if (shouldCount) {
                console.log('Enabling count for this query');
                return this.searchWithExactCount(searchText, options);
            } else {
                console.log('Skipping count for performance');
                return this.searchWithoutCount(searchText, options);
            }

        } catch (error) {
            console.error('Conditional counting error:', error);
            throw error;
        }
    }

    /**
     * Get approximate count using sampling
     */
    async getApproximateCount(searchText, options = {}) {
        try {
            // Sample a small number of results to estimate total
            const sampleSize = 100;
            const sampleResults = await this.searchClient.search(searchText, {
                top: sampleSize,
                includeTotalCount: true,
                ...options
            });

            if (sampleResults.count <= sampleSize) {
                // Small result set, return exact count
                return {
                    count: sampleResults.count,
                    isApproximate: false,
                    confidence: 'exact'
                };
            }

            // For larger sets, we have the exact count anyway from the API
            return {
                count: sampleResults.count,
                isApproximate: false,
                confidence: 'exact'
            };

        } catch (error) {
            console.error('Approximate count error:', error);
            return {
                count: 0,
                isApproximate: true,
                confidence: 'unknown',
                error: error.message
            };
        }
    }

    /**
     * Compare performance with and without counting
     */
    async compareCountingPerformance(searchText, iterations = 3) {
        const results = {
            withCount: [],
            withoutCount: []
        };

        console.log(`Comparing counting performance over ${iterations} iterations...`);

        // Test with counting
        for (let i = 0; i < iterations; i++) {
            const startTime = Date.now();
            await this.searchWithExactCount(searchText, { top: 20 });
            const duration = Date.now() - startTime;
            results.withCount.push(duration);
        }

        // Test without counting
        for (let i = 0; i < iterations; i++) {
            const startTime = Date.now();
            await this.searchWithoutCount(searchText, { top: 20 });
            const duration = Date.now() - startTime;
            results.withoutCount.push(duration);
        }

        // Calculate averages
        const avgWithCount = results.withCount.reduce((a, b) => a + b, 0) / iterations;
        const avgWithoutCount = results.withoutCount.reduce((a, b) => a + b, 0) / iterations;

        return {
            withCount: {
                times: results.withCount,
                average: avgWithCount
            },
            withoutCount: {
                times: results.withoutCount,
                average: avgWithoutCount
            },
            difference: avgWithCount - avgWithoutCount,
            percentageIncrease: ((avgWithCount - avgWithoutCount) / avgWithoutCount * 100).toFixed(1)
        };
    }

    /**
     * Generate cache key for count caching
     */
    generateCacheKey(searchText, options) {
        const keyParts = [
            searchText,
            options.filter || '',
            options.orderBy?.join(',') || '',
            options.searchFields?.join(',') || ''
        ];
        return keyParts.join('|');
    }

    /**
     * Get cached count if not expired
     */
    getCachedCount(cacheKey) {
        const cached = this.countCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached;
        }
        return null;
    }

    /**
     * Cache count with timestamp
     */
    setCachedCount(cacheKey, count) {
        this.countCache.set(cacheKey, {
            count,
            timestamp: Date.now()
        });
    }

    /**
     * Clear expired cache entries
     */
    clearExpiredCache() {
        const now = Date.now();
        for (const [key, value] of this.countCache.entries()) {
            if (now - value.timestamp >= this.cacheTimeout) {
                this.countCache.delete(key);
            }
        }
    }

    /**
     * Determine if counting should be enabled based on context
     */
    shouldEnableCounting(searchText, options) {
        // Enable counting for:
        // - First page requests (for pagination UI)
        // - Simple queries (likely to be fast)
        // - Small expected result sets
        
        const isFirstPage = (options.skip || 0) === 0;
        const isSimpleQuery = !options.filter && !options.orderBy;
        const isWildcardQuery = searchText === '*';
        
        // Skip counting for wildcard queries on non-first pages
        if (isWildcardQuery && !isFirstPage) {
            return false;
        }
        
        // Enable counting for first page or simple queries
        return isFirstPage || isSimpleQuery;
    }

    /**
     * Format count for display
     */
    formatCount(count, isApproximate = false) {
        if (count === null || count === undefined) {
            return 'Unknown';
        }

        if (typeof count === 'string') {
            return count; // Already formatted (e.g., "100+")
        }

        const prefix = isApproximate ? '~' : '';
        
        if (count < 1000) {
            return `${prefix}${count}`;
        } else if (count < 1000000) {
            return `${prefix}${(count / 1000).toFixed(1)}K`;
        } else {
            return `${prefix}${(count / 1000000).toFixed(1)}M`;
        }
    }
}

/**
 * Demonstrate exact counting
 */
async function demonstrateExactCounting() {
    console.log('=== Exact Counting Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const counter = new ResultCounter(searchClient);

    try {
        // Search with exact count
        console.log('1. Search with exact count:');
        const result = await counter.searchWithExactCount('luxury', { top: 5 });
        
        console.log(`Total results: ${result.totalCount}`);
        console.log(`Current page: ${result.currentPage + 1} of ${result.totalPages}`);
        console.log(`Page size: ${result.pageSize}`);
        console.log(`Duration: ${result.duration}ms`);
        console.log(`Results on this page: ${result.results.length}\n`);

        // Show pagination info
        console.log('Pagination info:');
        console.log(`- Has more pages: ${result.currentPage < result.totalPages - 1}`);
        console.log(`- Results range: ${result.currentPage * result.pageSize + 1}-${result.currentPage * result.pageSize + result.results.length}`);

    } catch (error) {
        console.error('Exact counting demo error:', error.message);
    }
}

/**
 * Demonstrate counting without total
 */
async function demonstrateCountingWithoutTotal() {
    console.log('\n=== Counting Without Total Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const counter = new ResultCounter(searchClient);

    try {
        // Search without count for better performance
        console.log('1. Search without total count:');
        const result = await counter.searchWithoutCount('hotel', { top: 5 });
        
        console.log(`Estimated count: ${result.estimatedCount}`);
        console.log(`Has more results: ${result.hasMoreResults}`);
        console.log(`Current page: ${result.currentPage + 1}`);
        console.log(`Duration: ${result.duration}ms`);
        console.log(`Results on this page: ${result.results.length}\n`);

        // Load next page to see estimation in action
        console.log('2. Loading next page:');
        const nextPage = await counter.searchWithoutCount('hotel', { top: 5, skip: 5 });
        console.log(`Estimated count: ${nextPage.estimatedCount}`);
        console.log(`Has more results: ${nextPage.hasMoreResults}`);

    } catch (error) {
        console.error('Counting without total demo error:', error.message);
    }
}

/**
 * Demonstrate smart counting with caching
 */
async function demonstrateSmartCounting() {
    console.log('\n=== Smart Counting Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const counter = new ResultCounter(searchClient);

    try {
        // First search - will get fresh count
        console.log('1. First search (fresh count):');
        const result1 = await counter.searchWithSmartCounting('spa', { top: 3 });
        console.log(`Total count: ${result1.totalCount}`);
        console.log(`From cache: ${result1.fromCache}`);
        console.log(`Duration: ${result1.duration}ms\n`);

        // Second search with same query - will use cached count
        console.log('2. Second search (cached count):');
        const result2 = await counter.searchWithSmartCounting('spa', { top: 3, skip: 3 });
        console.log(`Total count: ${result2.totalCount}`);
        console.log(`From cache: ${result2.fromCache}`);
        console.log(`Duration: ${result2.duration}ms\n`);

        // Different query - will get fresh count
        console.log('3. Different query (fresh count):');
        const result3 = await counter.searchWithSmartCounting('resort', { top: 3 });
        console.log(`Total count: ${result3.totalCount}`);
        console.log(`From cache: ${result3.fromCache}`);
        console.log(`Duration: ${result3.duration}ms`);

    } catch (error) {
        console.error('Smart counting demo error:', error.message);
    }
}

/**
 * Demonstrate conditional counting
 */
async function demonstrateConditionalCounting() {
    console.log('\n=== Conditional Counting Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const counter = new ResultCounter(searchClient);

    try {
        const testCases = [
            { query: 'luxury', skip: 0, description: 'First page, simple query' },
            { query: 'luxury', skip: 20, description: 'Later page, simple query' },
            { query: '*', skip: 0, description: 'First page, wildcard query' },
            { query: '*', skip: 50, description: 'Later page, wildcard query' }
        ];

        for (const testCase of testCases) {
            console.log(`${testCase.description}:`);
            const result = await counter.searchWithConditionalCounting(testCase.query, {
                skip: testCase.skip,
                top: 5
            });

            if (result.countingEnabled) {
                console.log(`  Count enabled - Total: ${result.totalCount}`);
            } else {
                console.log(`  Count disabled - Estimated: ${result.estimatedCount}`);
            }
            console.log(`  Duration: ${result.duration}ms\n`);
        }

    } catch (error) {
        console.error('Conditional counting demo error:', error.message);
    }
}

/**
 * Demonstrate performance comparison
 */
async function demonstratePerformanceComparison() {
    console.log('=== Performance Comparison Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const counter = new ResultCounter(searchClient);

    try {
        console.log('Comparing performance with and without counting...');
        const comparison = await counter.compareCountingPerformance('hotel', 3);

        console.log('\nResults:');
        console.log(`With counting: ${comparison.withCount.average.toFixed(1)}ms average`);
        console.log(`Without counting: ${comparison.withoutCount.average.toFixed(1)}ms average`);
        console.log(`Difference: +${comparison.difference.toFixed(1)}ms (${comparison.percentageIncrease}% increase)`);

        console.log('\nIndividual times:');
        console.log(`With counting: ${comparison.withCount.times.join('ms, ')}ms`);
        console.log(`Without counting: ${comparison.withoutCount.times.join('ms, ')}ms`);

    } catch (error) {
        console.error('Performance comparison demo error:', error.message);
    }
}

/**
 * Demonstrate count formatting
 */
async function demonstrateCountFormatting() {
    console.log('\n=== Count Formatting Demo ===\n');

    const counter = new ResultCounter(null);

    const testCounts = [
        { count: 5, approximate: false },
        { count: 42, approximate: false },
        { count: 156, approximate: true },
        { count: 1234, approximate: false },
        { count: 15678, approximate: true },
        { count: 1234567, approximate: false },
        { count: '100+', approximate: false },
        { count: null, approximate: false }
    ];

    console.log('Count formatting examples:');
    testCounts.forEach(test => {
        const formatted = counter.formatCount(test.count, test.approximate);
        console.log(`${test.count} (approx: ${test.approximate}) -> "${formatted}"`);
    });
}

/**
 * Pagination helper with smart counting
 */
class SmartPaginator {
    constructor(searchClient, pageSize = 20) {
        this.counter = new ResultCounter(searchClient);
        this.pageSize = pageSize;
    }

    async loadPage(searchText, pageNumber, options = {}) {
        const skip = pageNumber * this.pageSize;
        const searchOptions = {
            ...options,
            skip,
            top: this.pageSize
        };

        // Use smart counting for better performance
        const result = await this.counter.searchWithSmartCounting(searchText, searchOptions);

        return {
            ...result,
            pageNumber,
            hasNextPage: result.totalCount ? skip + this.pageSize < result.totalCount : result.hasMoreResults,
            hasPreviousPage: pageNumber > 0
        };
    }
}

// Run demonstrations if this file is executed directly
if (require.main === module) {
    (async () => {
        try {
            await demonstrateExactCounting();
            await demonstrateCountingWithoutTotal();
            await demonstrateSmartCounting();
            await demonstrateConditionalCounting();
            await demonstratePerformanceComparison();
            await demonstrateCountFormatting();
            
            // Demonstrate smart paginator
            console.log('\n=== Smart Paginator Demo ===\n');
            const searchClient = new SearchClient(
                config.endpoint,
                config.indexName,
                new AzureKeyCredential(config.apiKey)
            );
            
            const paginator = new SmartPaginator(searchClient, 5);
            const page = await paginator.loadPage('luxury', 0);
            
            console.log(`Smart paginator results:`);
            console.log(`Page: ${page.pageNumber + 1}`);
            console.log(`Total: ${page.totalCount || page.estimatedCount}`);
            console.log(`Has next: ${page.hasNextPage}`);
            console.log(`Results: ${page.results.length}`);
            
        } catch (error) {
            console.error('Demo failed:', error);
        }
    })();
}

module.exports = { ResultCounter, SmartPaginator };