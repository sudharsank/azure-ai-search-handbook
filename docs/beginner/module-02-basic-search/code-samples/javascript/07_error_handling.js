/**
 * Error Handling - Module 2 JavaScript Examples
 * Basic error handling for Azure AI Search operations
 * 
 * This module demonstrates:
 * - Input validation
 * - Common error handling
 * - Safe search operations
 * - Error recovery strategies
 * - Best practices for error handling
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

/**
 * Simple validator for search queries
 */
class SearchValidator {
    /**
     * Validate a search query
     * @param {string} query - Search query string
     * @returns {Object} Validation result with isValid and errorMessage
     */
    static validateQuery(query) {
        if (!query) {
            return { isValid: false, errorMessage: 'Search query cannot be empty' };
        }

        if (typeof query !== 'string') {
            return { isValid: false, errorMessage: 'Search query must be a string' };
        }

        if (query.trim().length === 0) {
            return { isValid: false, errorMessage: 'Search query cannot be just whitespace' };
        }

        if (query.length > 1000) {
            return { isValid: false, errorMessage: 'Search query is too long (max 1000 characters)' };
        }

        return { isValid: true, errorMessage: null };
    }

    /**
     * Basic query sanitization
     * @param {string} query - Raw search query
     * @returns {string} Sanitized query string
     */
    static sanitizeQuery(query) {
        if (!query) {
            return '';
        }

        // Remove potentially problematic characters
        let sanitized = query.replace(/[<>]/g, '');

        // Normalize whitespace
        sanitized = sanitized.replace(/\s+/g, ' ').trim();

        return sanitized;
    }
}

/**
 * Safe wrapper around SearchClient with error handling
 */
class SafeSearchClient {
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
     * Perform a safe search with error handling
     * @param {string} query - Search query string
     * @param {Object} searchOptions - Additional search options
     * @returns {Promise<Object>} Object with results array and errorMessage
     */
    async safeSearch(query, searchOptions = {}) {
        // Validate query
        const validation = SearchValidator.validateQuery(query);
        if (!validation.isValid) {
            return { results: [], errorMessage: validation.errorMessage };
        }

        // Sanitize query
        const sanitizedQuery = SearchValidator.sanitizeQuery(query);

        try {
            // Perform search
            const results = await this.searchClient.search(sanitizedQuery, searchOptions);
            const resultArray = [];
            
            for await (const result of results.results) {
                resultArray.push(result);
            }

            console.log(`Search successful: '${sanitizedQuery}' returned ${resultArray.length} results`);
            return { results: resultArray, errorMessage: null };

        } catch (error) {
            const errorMessage = this.handleSearchError(error);
            console.error(`Error in search: ${errorMessage}`);
            return { results: [], errorMessage: errorMessage };
        }
    }

    /**
     * Handle search errors with user-friendly messages
     * @param {Error} error - The error object
     * @returns {string} User-friendly error message
     */
    handleSearchError(error) {
        // Handle Azure SDK specific errors
        if (error.statusCode) {
            switch (error.statusCode) {
                case 400:
                    return 'Invalid query syntax. Please check your search terms.';
                case 401:
                    return 'Authentication failed. Please check your API key.';
                case 403:
                    return 'Access denied. Please check your permissions.';
                case 404:
                    return 'Search index not found. Please verify your index name.';
                case 429:
                    return 'Too many requests. Please wait and try again.';
                case 503:
                    return 'Search service is temporarily unavailable. Please try again later.';
                default:
                    return `HTTP error ${error.statusCode}: ${error.message}`;
            }
        }

        // Handle network and other errors
        if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
            return 'Network connection failed. Please check your internet connection and service endpoint.';
        }

        if (error.code === 'ETIMEDOUT') {
            return 'Request timed out. Please try again.';
        }

        // Generic error handling
        return `Unexpected error: ${error.message}`;
    }

    /**
     * Search with fallback queries if primary search fails or returns no results
     * @param {string} query - Primary search query
     * @param {Array<string>} fallbackQueries - Array of fallback queries to try
     * @param {Object} searchOptions - Additional search options
     * @returns {Promise<Object>} Object with results array and errorMessage
     */
    async searchWithFallback(query, fallbackQueries = [], searchOptions = {}) {
        // Try primary query first
        const primaryResult = await this.safeSearch(query, searchOptions);

        if (primaryResult.results.length > 0 || fallbackQueries.length === 0) {
            return primaryResult;
        }

        // Try fallback queries
        for (const fallbackQuery of fallbackQueries) {
            console.log(`Trying fallback query: '${fallbackQuery}'`);
            const fallbackResult = await this.safeSearch(fallbackQuery, searchOptions);

            if (fallbackResult.results.length > 0) {
                console.log(`Fallback query successful: found ${fallbackResult.results.length} results`);
                return { results: fallbackResult.results, errorMessage: null };
            }
        }

        // No results from any query
        return { 
            results: [], 
            errorMessage: primaryResult.errorMessage || 'No results found with any search strategy' 
        };
    }

    /**
     * Search with retry logic for transient errors
     * @param {string} query - Search query string
     * @param {Object} searchOptions - Additional search options
     * @param {number} maxRetries - Maximum number of retries
     * @param {number} retryDelay - Delay between retries in milliseconds
     * @returns {Promise<Object>} Object with results array and errorMessage
     */
    async searchWithRetry(query, searchOptions = {}, maxRetries = 3, retryDelay = 1000) {
        let lastError = null;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            const result = await this.safeSearch(query, searchOptions);

            // If successful or non-retryable error, return immediately
            if (result.results.length > 0 || !this.isRetryableError(result.errorMessage)) {
                return result;
            }

            lastError = result.errorMessage;

            if (attempt < maxRetries) {
                console.log(`Attempt ${attempt} failed, retrying in ${retryDelay}ms...`);
                await this.delay(retryDelay);
                retryDelay *= 2; // Exponential backoff
            }
        }

        return { results: [], errorMessage: `Failed after ${maxRetries} attempts: ${lastError}` };
    }

    /**
     * Check if an error is retryable
     * @param {string} errorMessage - Error message to check
     * @returns {boolean} True if error is retryable
     */
    isRetryableError(errorMessage) {
        if (!errorMessage) return false;
        
        const retryableErrors = [
            'Too many requests',
            'temporarily unavailable',
            'timed out',
            'Network connection failed'
        ];

        return retryableErrors.some(error => 
            errorMessage.toLowerCase().includes(error.toLowerCase())
        );
    }

    /**
     * Utility function to add delay
     * @param {number} ms - Milliseconds to delay
     * @returns {Promise} Promise that resolves after delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Demonstrate error handling capabilities
 */
async function demonstrateErrorHandling() {
    console.log('🛡️ Error Handling Demonstration');
    console.log('='.repeat(50));

    try {
        // Initialize search client (replace with your actual service details)
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );

        const safeClient = new SafeSearchClient(searchClient);

        // Test cases with different types of potential errors
        const testCases = [
            { query: '', description: 'Empty query' },
            { query: '   ', description: 'Whitespace only query' },
            { query: 'python programming', description: 'Valid query' },
            { query: 'x'.repeat(1001), description: 'Too long query' },
            { query: 'valid search terms', description: 'Another valid query' }
        ];

        console.log('\n🧪 Testing Query Validation and Error Handling:');
        console.log('-'.repeat(55));

        for (const testCase of testCases) {
            console.log(`\n📝 Test: ${testCase.description}`);
            const displayQuery = testCase.query.length > 50 ? 
                testCase.query.substring(0, 50) + '...' : testCase.query;
            console.log(`Query: '${displayQuery}'`);

            const searchOptions = { top: 3 };
            const result = await safeClient.safeSearch(testCase.query, searchOptions);

            if (result.errorMessage) {
                console.log(`❌ Error: ${result.errorMessage}`);
            } else {
                console.log(`✅ Success: Found ${result.results.length} results`);
                if (result.results.length > 0) {
                    const firstResult = result.results[0];
                    const title = firstResult.document.title || 'No title';
                    const score = firstResult.score || 0.0;
                    console.log(`   Top result: ${title} (Score: ${score.toFixed(3)})`);
                }
            }
        }

        // Demonstrate fallback search
        console.log('\n' + '='.repeat(60));
        console.log('\n🔄 Testing Fallback Search:');
        console.log('-'.repeat(30));

        const primaryQuery = 'very_specific_nonexistent_term_12345';
        const fallbackQueries = [
            'python programming',
            'tutorial',
            'development'
        ];

        console.log(`Primary query: '${primaryQuery}'`);
        console.log(`Fallback queries: [${fallbackQueries.join(', ')}]`);

        const searchOptions = { top: 2 };
        const fallbackResult = await safeClient.searchWithFallback(
            primaryQuery, fallbackQueries, searchOptions
        );

        if (fallbackResult.results.length > 0) {
            console.log(`✅ Fallback successful: Found ${fallbackResult.results.length} results`);
            fallbackResult.results.forEach((result, index) => {
                const title = result.document.title || 'No title';
                const score = result.score || 0.0;
                console.log(`  ${index + 1}. ${title} (Score: ${score.toFixed(3)})`);
            });
        } else {
            console.log(`❌ All queries failed: ${fallbackResult.errorMessage}`);
        }

        console.log('\n✅ Error handling demonstration completed!');

    } catch (error) {
        console.error(`❌ Demo failed: ${error.message}`);
    }
}

/**
 * Display error handling best practices
 */
function errorHandlingBestPractices() {
    console.log('\n📚 Error Handling Best Practices');
    console.log('='.repeat(50));

    console.log('\n💡 Always Validate Input:');
    console.log('   ✅ Check for empty or null queries');
    console.log('   ✅ Validate query length limits');
    console.log('   ✅ Sanitize user input');
    console.log('   ✅ Handle special characters appropriately');

    console.log('\n🔧 Handle Different Error Types:');
    console.log('   ✅ HTTP errors (400, 401, 403, 404, 429, 503)');
    console.log('   ✅ Network connectivity issues');
    console.log('   ✅ Service unavailability');
    console.log('   ✅ Invalid query syntax');

    console.log('\n🎯 Provide User-Friendly Messages:');
    console.log('   ✅ Translate technical errors to user language');
    console.log('   ✅ Suggest corrective actions');
    console.log('   ✅ Offer alternative search strategies');
    console.log('   ✅ Log detailed errors for debugging');

    console.log('\n🔄 Implement Fallback Strategies:');
    console.log('   ✅ Try broader search terms if specific ones fail');
    console.log('   ✅ Use alternative query syntax');
    console.log('   ✅ Provide suggested searches');
    console.log('   ✅ Gracefully degrade functionality');

    console.log('\n⚠️ Common Mistakes to Avoid:');
    console.log('   ❌ Exposing technical error messages to users');
    console.log('   ❌ Not logging errors for debugging');
    console.log('   ❌ Failing silently without user feedback');
    console.log('   ❌ Not implementing retry logic for transient errors');

    // Show example of good error handling
    console.log('\n🏆 Example of Good Error Handling:');
    const problematicQuery = ''; // Empty query
    const validation = SearchValidator.validateQuery(problematicQuery);

    if (!validation.isValid) {
        console.log(`   User sees: '${validation.errorMessage}'`);
        console.log(`   System logs: 'Empty query validation failed'`);
        console.log(`   Action: Prompt user to enter search terms`);
    } else {
        console.log(`   Success: Query is valid`);
    }
}

// Main execution
async function main() {
    try {
        await demonstrateErrorHandling();
        errorHandlingBestPractices();

        console.log('\n💡 Next Steps:');
        console.log('   - Always implement error handling in production code');
        console.log('   - Test your error handling with various input types');
        console.log('   - Check out 08_search_patterns.js for advanced search strategies');
        console.log('   - Review all JavaScript examples to build complete search functionality');
    } catch (error) {
        console.error(`❌ Main execution failed: ${error.message}`);
    }
}

// Export for use in other modules
module.exports = {
    SearchValidator,
    SafeSearchClient,
    demonstrateErrorHandling,
    errorHandlingBestPractices
};

// Run if this file is executed directly
if (require.main === module) {
    main();
}