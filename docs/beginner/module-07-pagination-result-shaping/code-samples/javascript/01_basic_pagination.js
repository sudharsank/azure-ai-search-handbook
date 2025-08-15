/**
 * Module 7: Basic Pagination with Skip/Top
 * 
 * This example demonstrates fundamental pagination using skip and top parameters.
 * Best for small to medium result sets (< 10,000 results).
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Configuration
const config = {
    endpoint: process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net',
    apiKey: process.env.SEARCH_API_KEY || 'your-api-key',
    indexName: process.env.INDEX_NAME || 'hotels-sample'
};

class BasicPaginator {
    constructor(searchClient, pageSize = 10) {
        this.searchClient = searchClient;
        this.pageSize = pageSize;
        this.currentPage = 0;
        this.totalResults = 0;
        this.totalPages = 0;
    }

    /**
     * Load a specific page of results
     * @param {number} pageNumber - Zero-based page number
     * @param {string} searchText - Search query
     * @param {object} options - Additional search options
     */
    async loadPage(pageNumber, searchText = '*', options = {}) {
        try {
            const skip = pageNumber * this.pageSize;
            
            // Validate pagination parameters
            this.validatePaginationParams(skip, this.pageSize);
            
            const searchOptions = {
                skip,
                top: this.pageSize,
                includeTotalCount: true,
                ...options
            };

            console.log(`Loading page ${pageNumber + 1}, skip: ${skip}, top: ${this.pageSize}`);
            
            const startTime = Date.now();
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;

            // Update pagination state
            this.currentPage = pageNumber;
            this.totalResults = results.count || 0;
            this.totalPages = Math.ceil(this.totalResults / this.pageSize);

            console.log(`Page loaded in ${duration}ms - ${results.results.length} results`);
            console.log(`Total results: ${this.totalResults}, Total pages: ${this.totalPages}`);

            return {
                results: results.results,
                currentPage: this.currentPage,
                totalPages: this.totalPages,
                totalResults: this.totalResults,
                hasNextPage: this.hasNextPage(),
                hasPreviousPage: this.hasPreviousPage(),
                duration
            };

        } catch (error) {
            console.error('Error loading page:', error);
            throw error;
        }
    }

    /**
     * Load the next page
     */
    async loadNextPage(searchText = '*', options = {}) {
        if (!this.hasNextPage()) {
            throw new Error('No next page available');
        }
        return this.loadPage(this.currentPage + 1, searchText, options);
    }

    /**
     * Load the previous page
     */
    async loadPreviousPage(searchText = '*', options = {}) {
        if (!this.hasPreviousPage()) {
            throw new Error('No previous page available');
        }
        return this.loadPage(this.currentPage - 1, searchText, options);
    }

    /**
     * Jump to first page
     */
    async loadFirstPage(searchText = '*', options = {}) {
        return this.loadPage(0, searchText, options);
    }

    /**
     * Jump to last page
     */
    async loadLastPage(searchText = '*', options = {}) {
        if (this.totalPages === 0) {
            return this.loadPage(0, searchText, options);
        }
        return this.loadPage(this.totalPages - 1, searchText, options);
    }

    /**
     * Check if there's a next page
     */
    hasNextPage() {
        return this.currentPage < this.totalPages - 1;
    }

    /**
     * Check if there's a previous page
     */
    hasPreviousPage() {
        return this.currentPage > 0;
    }

    /**
     * Get pagination info
     */
    getPaginationInfo() {
        return {
            currentPage: this.currentPage + 1, // 1-based for display
            totalPages: this.totalPages,
            totalResults: this.totalResults,
            pageSize: this.pageSize,
            hasNextPage: this.hasNextPage(),
            hasPreviousPage: this.hasPreviousPage()
        };
    }

    /**
     * Generate page numbers for pagination UI
     */
    getPageNumbers(maxVisible = 5) {
        const pages = [];
        const startPage = Math.max(0, this.currentPage - Math.floor(maxVisible / 2));
        const endPage = Math.min(this.totalPages - 1, startPage + maxVisible - 1);

        for (let i = startPage; i <= endPage; i++) {
            pages.push({
                number: i + 1, // 1-based for display
                index: i,      // 0-based for logic
                isCurrent: i === this.currentPage
            });
        }

        return pages;
    }

    /**
     * Validate pagination parameters
     */
    validatePaginationParams(skip, top) {
        if (skip < 0) {
            throw new Error('Skip must be non-negative');
        }
        if (top < 1 || top > 1000) {
            throw new Error('Top must be between 1 and 1000');
        }
        if (skip + top > 100000) {
            throw new Error('Cannot retrieve results beyond position 100,000');
        }
    }
}

/**
 * Example usage and demonstrations
 */
async function demonstrateBasicPagination() {
    console.log('=== Basic Pagination Demo ===\n');

    // Initialize search client
    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    // Create paginator with 5 items per page
    const paginator = new BasicPaginator(searchClient, 5);

    try {
        // Load first page
        console.log('1. Loading first page...');
        let page = await paginator.loadFirstPage('*');
        displayPageResults(page);

        // Load next few pages
        console.log('\n2. Loading next page...');
        page = await paginator.loadNextPage('*');
        displayPageResults(page);

        console.log('\n3. Loading one more page...');
        page = await paginator.loadNextPage('*');
        displayPageResults(page);

        // Go back to previous page
        console.log('\n4. Going back to previous page...');
        page = await paginator.loadPreviousPage('*');
        displayPageResults(page);

        // Jump to last page
        console.log('\n5. Jumping to last page...');
        page = await paginator.loadLastPage('*');
        displayPageResults(page);

        // Demonstrate pagination info
        console.log('\n6. Pagination Info:');
        console.log(paginator.getPaginationInfo());

        // Demonstrate page numbers for UI
        console.log('\n7. Page Numbers for UI:');
        console.log(paginator.getPageNumbers());

    } catch (error) {
        console.error('Demo error:', error.message);
    }
}

/**
 * Display page results in a formatted way
 */
function displayPageResults(page) {
    console.log(`Page ${page.currentPage + 1} of ${page.totalPages}`);
    console.log(`Showing ${page.results.length} of ${page.totalResults} total results`);
    console.log(`Load time: ${page.duration}ms`);
    
    page.results.forEach((result, index) => {
        const doc = result.document;
        console.log(`  ${index + 1}. ${doc.hotelName || doc.title || doc.id} (Score: ${result.score?.toFixed(2) || 'N/A'})`);
    });
    
    console.log(`Has Next: ${page.hasNextPage}, Has Previous: ${page.hasPreviousPage}`);
}

/**
 * Demonstrate search with pagination
 */
async function demonstrateSearchPagination() {
    console.log('\n=== Search with Pagination Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const paginator = new BasicPaginator(searchClient, 3);

    try {
        // Search for specific terms with pagination
        const searchQuery = 'luxury';
        console.log(`Searching for: "${searchQuery}"`);

        let page = await paginator.loadFirstPage(searchQuery);
        displayPageResults(page);

        // Load next page of search results
        if (page.hasNextPage) {
            console.log('\nLoading next page of search results...');
            page = await paginator.loadNextPage(searchQuery);
            displayPageResults(page);
        }

    } catch (error) {
        console.error('Search pagination error:', error.message);
    }
}

/**
 * Demonstrate error handling
 */
async function demonstrateErrorHandling() {
    console.log('\n=== Error Handling Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const paginator = new BasicPaginator(searchClient, 10);

    // Test invalid page size
    try {
        const invalidPaginator = new BasicPaginator(searchClient, 2000); // Too large
        await invalidPaginator.loadFirstPage('*');
    } catch (error) {
        console.log('Expected error for large page size:', error.message);
    }

    // Test going beyond available pages
    try {
        await paginator.loadPage(999999, '*'); // Very high page number
    } catch (error) {
        console.log('Expected error for invalid page:', error.message);
    }

    // Test previous page when on first page
    try {
        await paginator.loadFirstPage('*');
        await paginator.loadPreviousPage('*');
    } catch (error) {
        console.log('Expected error for previous page on first page:', error.message);
    }
}

/**
 * Performance comparison of different page sizes
 */
async function comparePageSizes() {
    console.log('\n=== Page Size Performance Comparison ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const pageSizes = [5, 10, 20, 50];
    
    for (const pageSize of pageSizes) {
        const paginator = new BasicPaginator(searchClient, pageSize);
        
        try {
            const startTime = Date.now();
            const page = await paginator.loadFirstPage('*');
            const duration = Date.now() - startTime;
            
            console.log(`Page size ${pageSize}: ${duration}ms, ${page.results.length} results`);
        } catch (error) {
            console.log(`Page size ${pageSize}: Error - ${error.message}`);
        }
    }
}

// Run demonstrations if this file is executed directly
if (require.main === module) {
    (async () => {
        try {
            await demonstrateBasicPagination();
            await demonstrateSearchPagination();
            await demonstrateErrorHandling();
            await comparePageSizes();
        } catch (error) {
            console.error('Demo failed:', error);
        }
    })();
}

module.exports = { BasicPaginator };