/**
 * Module 7: Range-Based Pagination for Large Datasets
 * 
 * This example demonstrates range-based pagination using filters and sorting,
 * which provides better performance for large datasets and deep pagination scenarios.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Configuration
const config = {
    endpoint: process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net',
    apiKey: process.env.SEARCH_API_KEY || 'your-api-key',
    indexName: process.env.INDEX_NAME || 'hotels-sample'
};

class RangePaginator {
    constructor(searchClient, options = {}) {
        this.searchClient = searchClient;
        this.sortField = options.sortField || 'hotelId';
        this.sortDirection = options.sortDirection || 'asc';
        this.pageSize = options.pageSize || 10;
        this.filterBase = options.filterBase || null;
        this.currentPage = 0;
        this.lastSortValue = null;
        this.pageHistory = [];
    }

    /**
     * Load the first page of results
     */
    async loadFirstPage(searchText = '*', options = {}) {
        this.currentPage = 0;
        this.lastSortValue = null;
        this.pageHistory = [];
        
        return this.loadPage(searchText, null, options);
    }

    /**
     * Load the next page of results
     */
    async loadNextPage(searchText = '*', options = {}) {
        if (this.lastSortValue === null) {
            throw new Error('Must load first page before loading next page');
        }

        // Store current position in history for potential backward navigation
        this.pageHistory.push(this.lastSortValue);
        
        const result = await this.loadPage(searchText, this.lastSortValue, options);
        
        if (result && result.results.length > 0) {
            this.currentPage++;
            return result;
        } else {
            // No more results, remove from history
            if (this.pageHistory.length > 0) {
                this.pageHistory.pop();
            }
            return null;
        }
    }

    /**
     * Load page starting after a specific sort value
     */
    async loadPageAfter(sortValue, searchText = '*', options = {}) {
        return this.loadPage(searchText, sortValue, options);
    }

    /**
     * Internal method to load a page with range filtering
     */
    async loadPage(searchText, afterValue, options = {}) {
        try {
            console.log(`Loading range page: after_value=${afterValue}`);
            
            const startTime = Date.now();
            
            // Build filter expression
            const filterParts = [];
            
            // Add base filter if provided
            if (this.filterBase) {
                filterParts.push(this.filterBase);
            }
            
            // Add range filter
            if (afterValue !== null) {
                const operator = this.sortDirection === 'asc' ? 'gt' : 'lt';
                let filterValue;
                
                // Handle different data types
                if (typeof afterValue === 'string') {
                    filterValue = `'${afterValue}'`;
                } else if (typeof afterValue === 'number') {
                    filterValue = afterValue.toString();
                } else {
                    filterValue = `'${afterValue.toString()}'`;
                }
                
                const rangeFilter = `${this.sortField} ${operator} ${filterValue}`;
                filterParts.push(rangeFilter);
            }
            
            // Combine filters
            const filterExpression = filterParts.length > 0 ? filterParts.join(' and ') : null;
            
            // Build sort expression
            const sortExpression = `${this.sortField} ${this.sortDirection}`;
            
            console.log(`Filter: ${filterExpression}`);
            console.log(`Sort: ${sortExpression}`);
            
            // Perform search
            const searchOptions = {
                top: this.pageSize,
                orderBy: [sortExpression],
                ...options
            };
            
            if (filterExpression) {
                searchOptions.filter = filterExpression;
            }
            
            // Include sort field in results if not already selected
            if (searchOptions.select && !searchOptions.select.includes(this.sortField)) {
                searchOptions.select.push(this.sortField);
            }
            
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;
            
            // Get last sort value for next page
            let newLastSortValue = null;
            if (results.results.length > 0) {
                const lastDoc = results.results[results.results.length - 1].document;
                newLastSortValue = lastDoc[this.sortField];
            }
            
            // Update state
            if (newLastSortValue !== null) {
                this.lastSortValue = newLastSortValue;
            }
            
            // Determine if there are more pages
            const hasNextPage = results.results.length === this.pageSize;
            
            console.log(`Loaded ${results.results.length} documents in ${duration}ms`);
            console.log(`Last sort value: ${newLastSortValue}`);
            console.log(`Has next page: ${hasNextPage}`);
            
            return {
                results: results.results,
                lastSortValue: newLastSortValue,
                hasNextPage,
                pageSize: this.pageSize,
                duration,
                query: searchText,
                sortField: this.sortField,
                filterExpression,
                pageNumber: this.currentPage
            };
            
        } catch (error) {
            console.error('Range pagination error:', error);
            throw error;
        }
    }

    /**
     * Reset paginator state
     */
    reset() {
        this.currentPage = 0;
        this.lastSortValue = null;
        this.pageHistory = [];
    }
}

class CursorPaginator {
    constructor(searchClient, sortFields) {
        this.searchClient = searchClient;
        this.sortFields = sortFields || ['hotelId'];
        this.currentCursor = null;
        this.pageSize = 10;
    }

    /**
     * Load page using cursor pagination (conceptual implementation)
     */
    async loadPage(searchText = '*', cursor = null, pageSize = 10, options = {}) {
        try {
            console.log(`Loading cursor page: cursor=${JSON.stringify(cursor)}`);
            
            const startTime = Date.now();
            
            // Build sort expressions
            const sortExpressions = this.sortFields.map(field => `${field} asc`);
            
            const searchOptions = {
                top: pageSize,
                orderBy: sortExpressions,
                ...options
            };
            
            // Note: search_after is not directly available in JavaScript SDK
            // This is a conceptual implementation
            if (cursor) {
                console.log('Note: search_after not directly supported in JavaScript SDK');
                // In a real implementation, you would use the REST API directly
                // or implement range-based pagination as a fallback
            }
            
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;
            
            // Generate cursor for next page
            let nextCursor = null;
            if (results.results.length > 0) {
                const lastDoc = results.results[results.results.length - 1].document;
                nextCursor = this.sortFields.map(field => lastDoc[field]);
            }
            
            const hasNextPage = results.results.length === pageSize;
            
            return {
                results: results.results,
                nextCursor,
                hasNextPage,
                duration,
                pageSize
            };
            
        } catch (error) {
            console.error('Cursor pagination error:', error);
            throw error;
        }
    }
}

class HybridPaginator {
    constructor(searchClient) {
        this.searchClient = searchClient;
        this.strategies = {};
    }

    /**
     * Determine optimal pagination strategy
     */
    getOptimalStrategy(totalResults, pageNumber, sortField) {
        // Use skip/top for small datasets and early pages
        if (totalResults && totalResults < 1000 && pageNumber < 10) {
            return 'skip_top';
        }
        
        // Use range pagination for large datasets or deep pagination
        if (sortField && (!totalResults || totalResults > 1000 || pageNumber > 10)) {
            return 'range';
        }
        
        // Default to skip/top
        return 'skip_top';
    }

    /**
     * Create paginator instance for strategy
     */
    createPaginator(strategy, config = {}) {
        if (strategy === 'range') {
            return new RangePaginator(this.searchClient, {
                sortField: config.sortField || 'hotelId',
                sortDirection: config.sortDirection || 'asc',
                pageSize: config.pageSize || 10,
                filterBase: config.filterBase
            });
        } else if (strategy === 'cursor') {
            return new CursorPaginator(this.searchClient, config.sortFields || ['hotelId']);
        } else {
            throw new Error('Basic paginator not implemented in this module');
        }
    }
}

/**
 * Display range pagination page results
 */
function displayRangePage(page) {
    console.log(`Page ${page.pageNumber + 1}`);
    console.log(`Results: ${page.results.length}`);
    console.log(`Duration: ${page.duration}ms`);
    console.log(`Sort field: ${page.sortField}`);
    console.log(`Last sort value: ${page.lastSortValue}`);
    console.log(`Has next page: ${page.hasNextPage}`);
    
    if (page.filterExpression) {
        console.log(`Filter: ${page.filterExpression}`);
    }
    
    // Show sample results
    page.results.forEach((result, index) => {
        const doc = result.document;
        const hotelId = doc.hotelId || doc.id || 'Unknown';
        const hotelName = doc.hotelName || doc.title || 'Unknown';
        const sortValue = doc[page.sortField] || 'N/A';
        console.log(`  ${index + 1}. ${hotelName} (ID: ${hotelId}, Sort: ${sortValue})`);
    });
}

/**
 * Demonstrate range-based pagination
 */
async function demonstrateRangePagination() {
    console.log('=== Range-Based Pagination Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    // Configure range pagination
    const paginator = new RangePaginator(searchClient, {
        sortField: 'hotelId',  // Use a unique, sortable field
        sortDirection: 'asc',
        pageSize: 5
    });

    try {
        // Load first page
        console.log('1. Loading first page:');
        let page = await paginator.loadFirstPage('*');
        displayRangePage(page);

        // Load next few pages
        console.log('\n2. Loading next page:');
        page = await paginator.loadNextPage('*');
        if (page) {
            displayRangePage(page);
        }

        console.log('\n3. Loading another page:');
        page = await paginator.loadNextPage('*');
        if (page) {
            displayRangePage(page);
        }

        // Demonstrate jumping to specific position
        console.log('\n4. Jumping to specific position:');
        if (page && page.lastSortValue) {
            const jumpPage = await paginator.loadPageAfter(page.lastSortValue, '*');
            displayRangePage(jumpPage);
        }

    } catch (error) {
        console.error('Range pagination demo error:', error.message);
    }
}

/**
 * Compare range pagination vs skip/top performance
 */
async function demonstratePerformanceComparison() {
    console.log('\n=== Performance Comparison Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    try {
        // Test different page positions
        const pagePositions = [0, 10, 50, 100]; // Skip values
        const pageSize = 10;

        console.log('Comparing skip/top vs range pagination performance:');
        console.log('Page | Skip/Top (ms) | Range (ms) | Improvement');
        console.log('-'.repeat(50));

        for (const skip of pagePositions) {
            // Test skip/top pagination
            let startTime = Date.now();
            const skipResults = await searchClient.search('*', {
                skip,
                top: pageSize,
                orderBy: ['hotelId asc']
            });
            // Consume results
            const skipDocs = [];
            for await (const result of skipResults.results) {
                skipDocs.push(result);
            }
            const skipDuration = Date.now() - startTime;

            // Test range pagination (simulate by getting the boundary value)
            let rangeDuration = 'N/A';
            let improvement = 'N/A';

            if (skip > 0) {
                // Get the boundary value first
                const boundaryResults = await searchClient.search('*', {
                    skip: skip - 1,
                    top: 1,
                    orderBy: ['hotelId asc']
                });
                
                const boundaryDocs = [];
                for await (const result of boundaryResults.results) {
                    boundaryDocs.push(result);
                }

                if (boundaryDocs.length > 0) {
                    const boundaryValue = boundaryDocs[0].document.hotelId;

                    // Now test range pagination
                    startTime = Date.now();
                    const rangeResults = await searchClient.search('*', {
                        filter: `hotelId gt '${boundaryValue}'`,
                        top: pageSize,
                        orderBy: ['hotelId asc']
                    });
                    // Consume results
                    const rangeDocs = [];
                    for await (const result of rangeResults.results) {
                        rangeDocs.push(result);
                    }
                    rangeDuration = Date.now() - startTime;

                    const improvementPercent = ((skipDuration - rangeDuration) / skipDuration) * 100;
                    improvement = `${improvementPercent > 0 ? '+' : ''}${improvementPercent.toFixed(1)}%`;
                }
            }

            console.log(`${skip.toString().padStart(4)} | ${skipDuration.toString().padStart(11)} | ${rangeDuration.toString().padStart(9)} | ${improvement.padStart(8)}`);
        }

    } catch (error) {
        console.error('Performance comparison error:', error.message);
    }
}

/**
 * Demonstrate range pagination with additional filters
 */
async function demonstrateFilteredRangePagination() {
    console.log('\n=== Filtered Range Pagination Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    try {
        // Configure with base filter
        const paginator = new RangePaginator(searchClient, {
            sortField: 'hotelId',
            sortDirection: 'asc',
            pageSize: 3,
            filterBase: 'rating ge 4.0'  // Only high-rated hotels
        });

        console.log('Range pagination with rating filter (>= 4.0):');

        // Load first page
        let page = await paginator.loadFirstPage('luxury');
        displayRangePage(page);

        // Load next page
        if (page.hasNextPage) {
            console.log('\nNext page:');
            page = await paginator.loadNextPage('luxury');
            if (page) {
                displayRangePage(page);
            }
        }

    } catch (error) {
        console.error('Filtered range pagination demo error:', error.message);
    }
}

/**
 * Demonstrate cursor-based pagination concept
 */
async function demonstrateCursorPagination() {
    console.log('\n=== Cursor Pagination Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    try {
        // Create cursor paginator
        const cursorPaginator = new CursorPaginator(searchClient, ['rating', 'hotelId']);

        console.log('Cursor pagination (conceptual):');

        // Load first page
        const page1 = await cursorPaginator.loadPage('*', null, 5);

        console.log(`Page 1: ${page1.results.length} results`);
        console.log(`Duration: ${page1.duration}ms`);
        console.log(`Next cursor: ${JSON.stringify(page1.nextCursor)}`);

        // Show sample results
        page1.results.forEach((result, index) => {
            const doc = result.document;
            console.log(`  ${index + 1}. ${doc.hotelName || 'Unknown'} (Rating: ${doc.rating || 'N/A'}, ID: ${doc.hotelId || 'N/A'})`);
        });

        // Load next page with cursor
        if (page1.hasNextPage && page1.nextCursor) {
            console.log('\nPage 2 (with cursor):');
            const page2 = await cursorPaginator.loadPage('*', page1.nextCursor, 5);

            console.log(`Results: ${page2.results.length}`);
            console.log(`Duration: ${page2.duration}ms`);
            console.log(`Next cursor: ${JSON.stringify(page2.nextCursor)}`);
        }

    } catch (error) {
        console.error('Cursor pagination demo error:', error.message);
    }
}

/**
 * Demonstrate hybrid pagination strategy selection
 */
async function demonstrateHybridStrategy() {
    console.log('\n=== Hybrid Strategy Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    try {
        const hybrid = new HybridPaginator(searchClient);

        // Test different scenarios
        const scenarios = [
            { totalResults: 100, pageNumber: 1, sortField: 'hotelId' },
            { totalResults: 5000, pageNumber: 1, sortField: 'hotelId' },
            { totalResults: 1000, pageNumber: 20, sortField: 'hotelId' },
            { totalResults: 10000, pageNumber: 5, sortField: null },
        ];

        console.log('Strategy recommendations:');
        scenarios.forEach((scenario, index) => {
            const strategy = hybrid.getOptimalStrategy(scenario.totalResults, scenario.pageNumber, scenario.sortField);
            console.log(`Scenario ${index + 1}: ${JSON.stringify(scenario)} -> ${strategy}`);
        });

    } catch (error) {
        console.error('Hybrid strategy demo error:', error.message);
    }
}

/**
 * Demonstrate deep pagination scenarios
 */
async function demonstrateDeepPagination() {
    console.log('\n=== Deep Pagination Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    try {
        // Configure for deep pagination
        const paginator = new RangePaginator(searchClient, {
            sortField: 'hotelId',
            sortDirection: 'asc',
            pageSize: 10
        });

        console.log('Simulating deep pagination (jumping to page 10):');

        // Simulate jumping to a deep page by loading multiple pages
        let currentPage = await paginator.loadFirstPage('*');

        for (let pageNum = 1; pageNum < 6; pageNum++) { // Load 5 pages to simulate deep pagination
            if (currentPage && currentPage.hasNextPage) {
                currentPage = await paginator.loadNextPage('*');
                if (currentPage) {
                    console.log(`Page ${pageNum + 1}: Last sort value = ${currentPage.lastSortValue}, Duration = ${currentPage.duration}ms`);
                }
            } else {
                break;
            }
        }

        console.log('\nNote: Range pagination maintains consistent performance at any depth');

    } catch (error) {
        console.error('Deep pagination demo error:', error.message);
    }
}

/**
 * Utility class for range pagination patterns
 */
class RangePaginationHelper {
    static getSortableFields() {
        return ['hotelId', 'rating', 'lastRenovationDate', 'hotelName'];
    }

    static buildRangeFilter(field, value, direction = 'asc') {
        const operator = direction === 'asc' ? 'gt' : 'lt';
        
        if (typeof value === 'string') {
            return `${field} ${operator} '${value}'`;
        } else {
            return `${field} ${operator} ${value}`;
        }
    }

    static estimatePagePosition(sortValue, minValue, maxValue, totalCount, pageSize) {
        try {
            if (typeof sortValue === 'number' && typeof minValue === 'number' && typeof maxValue === 'number') {
                if (maxValue > minValue) {
                    const ratio = (sortValue - minValue) / (maxValue - minValue);
                    const estimatedPosition = Math.floor(ratio * totalCount);
                    return Math.floor(estimatedPosition / pageSize);
                }
            }
            return 0;
        } catch {
            return 0;
        }
    }

    static validateSortField(field, fieldType) {
        const suitableTypes = ['Edm.String', 'Edm.Int32', 'Edm.Int64', 'Edm.Double', 
                              'Edm.DateTimeOffset', 'Edm.Boolean'];
        return suitableTypes.includes(fieldType);
    }
}

// Run demonstrations if this file is executed directly
if (require.main === module) {
    (async () => {
        try {
            await demonstrateRangePagination();
            await demonstratePerformanceComparison();
            await demonstrateFilteredRangePagination();
            await demonstrateCursorPagination();
            await demonstrateHybridStrategy();
            await demonstrateDeepPagination();

            // Show helper usage
            console.log('\n=== Range Pagination Helper Demo ===\n');
            console.log('Sortable fields:', RangePaginationHelper.getSortableFields());
            console.log('Range filter example:', RangePaginationHelper.buildRangeFilter('hotelId', 'hotel_100', 'asc'));
            console.log('Page estimation:', RangePaginationHelper.estimatePagePosition(50, 0, 100, 1000, 10));
            console.log('Field validation:', RangePaginationHelper.validateSortField('rating', 'Edm.Double'));

        } catch (error) {
            console.error('Demo failed:', error);
        }
    })();
}

module.exports = { RangePaginator, CursorPaginator, HybridPaginator, RangePaginationHelper };