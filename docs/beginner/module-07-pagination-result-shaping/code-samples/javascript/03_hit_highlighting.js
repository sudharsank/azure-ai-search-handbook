/**
 * Module 7: Hit Highlighting Implementation
 * 
 * This example demonstrates how to implement hit highlighting to emphasize
 * search terms in results, improving user experience and search relevance visibility.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Configuration
const config = {
    endpoint: process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net',
    apiKey: process.env.SEARCH_API_KEY || 'your-api-key',
    indexName: process.env.INDEX_NAME || 'hotels-sample'
};

class HitHighlighter {
    constructor(searchClient) {
        this.searchClient = searchClient;
        this.defaultHighlightPreTag = '<mark>';
        this.defaultHighlightPostTag = '</mark>';
    }

    /**
     * Search with basic hit highlighting
     */
    async searchWithHighlighting(searchText, highlightFields, options = {}) {
        try {
            if (!searchText || searchText === '*') {
                console.warn('Hit highlighting works best with actual search terms, not wildcard queries');
            }

            const searchOptions = {
                highlightFields: highlightFields,
                highlightPreTag: options.highlightPreTag || this.defaultHighlightPreTag,
                highlightPostTag: options.highlightPostTag || this.defaultHighlightPostTag,
                top: options.top || 10,
                skip: options.skip || 0,
                select: options.select,
                ...options
            };

            console.log(`Searching for "${searchText}" with highlighting on: ${highlightFields.join(', ')}`);
            
            const startTime = Date.now();
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;

            return {
                results: results.results,
                count: results.count,
                duration,
                searchText,
                highlightFields,
                highlightTags: {
                    pre: searchOptions.highlightPreTag,
                    post: searchOptions.highlightPostTag
                }
            };

        } catch (error) {
            console.error('Hit highlighting search error:', error);
            throw error;
        }
    }

    /**
     * Extract and process highlights from search results
     */
    processHighlights(searchResults) {
        return searchResults.map(result => {
            const processed = {
                document: result.document,
                score: result.score,
                highlights: {},
                highlightCount: 0
            };

            // Process highlights if they exist
            if (result.highlights) {
                for (const [field, highlights] of Object.entries(result.highlights)) {
                    processed.highlights[field] = highlights;
                    processed.highlightCount += highlights.length;
                }
            }

            return processed;
        });
    }

    /**
     * Get highlighted snippets for display
     */
    getHighlightedSnippets(result, maxLength = 200) {
        const snippets = {};

        if (result.highlights) {
            for (const [field, highlights] of Object.entries(result.highlights)) {
                snippets[field] = highlights.map(highlight => {
                    // Truncate long highlights while preserving highlight tags
                    if (highlight.length > maxLength) {
                        const truncated = highlight.substring(0, maxLength);
                        const lastSpace = truncated.lastIndexOf(' ');
                        return lastSpace > 0 ? truncated.substring(0, lastSpace) + '...' : truncated + '...';
                    }
                    return highlight;
                });
            }
        }

        return snippets;
    }

    /**
     * Search with multiple highlighting configurations
     */
    async searchWithMultipleHighlighting(searchText, highlightConfigs, options = {}) {
        const results = [];

        for (const config of highlightConfigs) {
            try {
                const result = await this.searchWithHighlighting(
                    searchText, 
                    config.fields, 
                    {
                        ...options,
                        highlightPreTag: config.preTag,
                        highlightPostTag: config.postTag
                    }
                );

                results.push({
                    name: config.name,
                    config: config,
                    result: result
                });

            } catch (error) {
                results.push({
                    name: config.name,
                    config: config,
                    error: error.message
                });
            }
        }

        return results;
    }

    /**
     * Advanced highlighting with custom processing
     */
    async searchWithAdvancedHighlighting(searchText, options = {}) {
        const highlightFields = options.highlightFields || ['description', 'hotelName'];
        
        const searchOptions = {
            highlightFields: highlightFields,
            highlightPreTag: options.highlightPreTag || '<span class="highlight">',
            highlightPostTag: options.highlightPostTag || '</span>',
            top: options.top || 10,
            select: options.select || ['hotelId', 'hotelName', 'description', 'rating'],
            ...options
        };

        const results = await this.searchClient.search(searchText, searchOptions);
        
        // Process results with advanced highlighting features
        const processedResults = results.results.map(result => {
            const processed = {
                document: result.document,
                score: result.score,
                highlights: result.highlights || {},
                highlightSummary: this.createHighlightSummary(result.highlights),
                snippets: this.getHighlightedSnippets(result, 150)
            };

            return processed;
        });

        return {
            results: processedResults,
            count: results.count,
            searchText,
            highlightConfig: {
                fields: highlightFields,
                preTag: searchOptions.highlightPreTag,
                postTag: searchOptions.highlightPostTag
            }
        };
    }

    /**
     * Create a summary of highlights
     */
    createHighlightSummary(highlights) {
        if (!highlights) return { totalHighlights: 0, fieldsWithHighlights: [] };

        const summary = {
            totalHighlights: 0,
            fieldsWithHighlights: [],
            highlightsByField: {}
        };

        for (const [field, fieldHighlights] of Object.entries(highlights)) {
            summary.fieldsWithHighlights.push(field);
            summary.highlightsByField[field] = fieldHighlights.length;
            summary.totalHighlights += fieldHighlights.length;
        }

        return summary;
    }

    /**
     * Convert highlights to plain text (remove HTML tags)
     */
    highlightsToPlainText(highlights) {
        const plainText = {};

        for (const [field, fieldHighlights] of Object.entries(highlights)) {
            plainText[field] = fieldHighlights.map(highlight => 
                highlight.replace(/<[^>]*>/g, '')
            );
        }

        return plainText;
    }

    /**
     * Get searchable fields for highlighting validation
     */
    async getSearchableFields() {
        // In a real application, you would get this from the index schema
        // For this example, we'll return common searchable fields
        return ['hotelName', 'description', 'category', 'tags', 'address/streetAddress', 'address/city'];
    }

    /**
     * Validate highlight fields
     */
    async validateHighlightFields(fields) {
        const searchableFields = await this.getSearchableFields();
        const invalidFields = fields.filter(field => !searchableFields.includes(field));
        
        if (invalidFields.length > 0) {
            console.warn(`Warning: These fields may not be searchable for highlighting: ${invalidFields.join(', ')}`);
        }
        
        return invalidFields.length === 0;
    }
}

/**
 * Demonstrate basic hit highlighting
 */
async function demonstrateBasicHighlighting() {
    console.log('=== Basic Hit Highlighting Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const highlighter = new HitHighlighter(searchClient);

    try {
        // Search with highlighting on description field
        console.log('1. Basic highlighting on description field:');
        const result = await highlighter.searchWithHighlighting(
            'luxury hotel', 
            ['description'], 
            { top: 3 }
        );

        console.log(`Found ${result.results.length} results in ${result.duration}ms`);
        console.log(`Highlight tags: ${result.highlightTags.pre}...${result.highlightTags.post}\n`);

        // Display results with highlights
        result.results.forEach((searchResult, index) => {
            const doc = searchResult.document;
            console.log(`${index + 1}. ${doc.hotelName} (Score: ${searchResult.score?.toFixed(2)})`);
            
            if (searchResult.highlights && searchResult.highlights.description) {
                console.log(`   Highlights: ${searchResult.highlights.description.join(' ... ')}`);
            } else {
                console.log(`   No highlights found`);
            }
            console.log();
        });

    } catch (error) {
        console.error('Basic highlighting demo error:', error.message);
    }
}

/**
 * Demonstrate multi-field highlighting
 */
async function demonstrateMultiFieldHighlighting() {
    console.log('=== Multi-Field Highlighting Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const highlighter = new HitHighlighter(searchClient);

    try {
        // Search with highlighting on multiple fields
        console.log('1. Multi-field highlighting:');
        const result = await highlighter.searchWithHighlighting(
            'spa resort', 
            ['hotelName', 'description', 'category'], 
            { top: 3 }
        );

        console.log(`Found ${result.results.length} results\n`);

        // Process and display results
        const processedResults = highlighter.processHighlights(result.results);
        
        processedResults.forEach((result, index) => {
            const doc = result.document;
            console.log(`${index + 1}. ${doc.hotelName}`);
            console.log(`   Total highlights: ${result.highlightCount}`);
            
            // Show highlights by field
            for (const [field, highlights] of Object.entries(result.highlights)) {
                console.log(`   ${field}: ${highlights.join(' | ')}`);
            }
            console.log();
        });

    } catch (error) {
        console.error('Multi-field highlighting demo error:', error.message);
    }
}

/**
 * Demonstrate custom highlighting tags
 */
async function demonstrateCustomHighlightTags() {
    console.log('=== Custom Highlight Tags Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const highlighter = new HitHighlighter(searchClient);

    try {
        const highlightConfigs = [
            {
                name: 'HTML Bold',
                fields: ['description'],
                preTag: '<b>',
                postTag: '</b>'
            },
            {
                name: 'CSS Class',
                fields: ['description'],
                preTag: '<span class="search-highlight">',
                postTag: '</span>'
            },
            {
                name: 'Brackets',
                fields: ['description'],
                preTag: '[',
                postTag: ']'
            },
            {
                name: 'Asterisks',
                fields: ['description'],
                preTag: '*',
                postTag: '*'
            }
        ];

        console.log('Comparing different highlight tag styles:');
        const results = await highlighter.searchWithMultipleHighlighting(
            'ocean view', 
            highlightConfigs, 
            { top: 1 }
        );

        results.forEach(result => {
            console.log(`\n${result.name}:`);
            if (result.error) {
                console.log(`  Error: ${result.error}`);
            } else if (result.result.results.length > 0) {
                const firstResult = result.result.results[0];
                if (firstResult.highlights && firstResult.highlights.description) {
                    console.log(`  ${firstResult.highlights.description[0]}`);
                } else {
                    console.log(`  No highlights found`);
                }
            }
        });

    } catch (error) {
        console.error('Custom highlight tags demo error:', error.message);
    }
}

/**
 * Demonstrate advanced highlighting features
 */
async function demonstrateAdvancedHighlighting() {
    console.log('\n=== Advanced Highlighting Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const highlighter = new HitHighlighter(searchClient);

    try {
        console.log('1. Advanced highlighting with processing:');
        const result = await highlighter.searchWithAdvancedHighlighting(
            'luxury spa resort', 
            {
                highlightFields: ['hotelName', 'description'],
                top: 3,
                highlightPreTag: '<mark class="highlight">',
                highlightPostTag: '</mark>'
            }
        );

        console.log(`Search: "${result.searchText}"`);
        console.log(`Highlight fields: ${result.highlightConfig.fields.join(', ')}\n`);

        result.results.forEach((result, index) => {
            const doc = result.document;
            console.log(`${index + 1}. ${doc.hotelName} (Score: ${result.score?.toFixed(2)})`);
            
            // Show highlight summary
            const summary = result.highlightSummary;
            console.log(`   Highlights: ${summary.totalHighlights} across ${summary.fieldsWithHighlights.length} fields`);
            
            // Show snippets
            for (const [field, snippets] of Object.entries(result.snippets)) {
                console.log(`   ${field}: ${snippets.join(' ... ')}`);
            }
            console.log();
        });

    } catch (error) {
        console.error('Advanced highlighting demo error:', error.message);
    }
}

/**
 * Demonstrate highlighting with pagination
 */
async function demonstrateHighlightingWithPagination() {
    console.log('=== Highlighting with Pagination Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const highlighter = new HitHighlighter(searchClient);

    try {
        const searchTerm = 'hotel';
        const pageSize = 3;

        // Load multiple pages with highlighting
        for (let page = 0; page < 2; page++) {
            console.log(`Page ${page + 1}:`);
            
            const result = await highlighter.searchWithHighlighting(
                searchTerm,
                ['hotelName', 'description'],
                {
                    skip: page * pageSize,
                    top: pageSize,
                    includeTotalCount: page === 0
                }
            );

            if (page === 0 && result.count) {
                console.log(`Total results: ${result.count}`);
            }

            result.results.forEach((searchResult, index) => {
                const doc = searchResult.document;
                console.log(`  ${index + 1}. ${doc.hotelName}`);
                
                if (searchResult.highlights) {
                    const snippets = highlighter.getHighlightedSnippets(searchResult, 100);
                    for (const [field, fieldSnippets] of Object.entries(snippets)) {
                        if (fieldSnippets.length > 0) {
                            console.log(`     ${field}: ${fieldSnippets[0]}`);
                        }
                    }
                }
            });
            console.log();
        }

    } catch (error) {
        console.error('Highlighting with pagination demo error:', error.message);
    }
}

/**
 * Demonstrate highlighting performance considerations
 */
async function demonstrateHighlightingPerformance() {
    console.log('=== Highlighting Performance Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const highlighter = new HitHighlighter(searchClient);

    try {
        const searchTerm = 'luxury';
        const testConfigs = [
            { name: 'No Highlighting', fields: [] },
            { name: 'Single Field', fields: ['description'] },
            { name: 'Two Fields', fields: ['hotelName', 'description'] },
            { name: 'Multiple Fields', fields: ['hotelName', 'description', 'category'] }
        ];

        console.log('Performance comparison:');
        
        for (const config of testConfigs) {
            const startTime = Date.now();
            
            if (config.fields.length === 0) {
                // Search without highlighting
                await searchClient.search(searchTerm, { top: 10 });
            } else {
                await highlighter.searchWithHighlighting(searchTerm, config.fields, { top: 10 });
            }
            
            const duration = Date.now() - startTime;
            console.log(`${config.name}: ${duration}ms`);
        }

    } catch (error) {
        console.error('Highlighting performance demo error:', error.message);
    }
}

/**
 * Utility functions for highlighting
 */
const HighlightUtils = {
    /**
     * Remove HTML tags from highlighted text
     */
    stripHighlightTags: (text) => {
        return text.replace(/<[^>]*>/g, '');
    },

    /**
     * Convert highlight tags to different format
     */
    convertHighlightTags: (text, fromPre, fromPost, toPre, toPost) => {
        const regex = new RegExp(`${fromPre}(.*?)${fromPost}`, 'g');
        return text.replace(regex, `${toPre}$1${toPost}`);
    },

    /**
     * Count highlights in text
     */
    countHighlights: (text, preTag, postTag) => {
        const regex = new RegExp(`${preTag}.*?${postTag}`, 'g');
        const matches = text.match(regex);
        return matches ? matches.length : 0;
    },

    /**
     * Extract highlighted terms
     */
    extractHighlightedTerms: (text, preTag, postTag) => {
        const regex = new RegExp(`${preTag}(.*?)${postTag}`, 'g');
        const terms = [];
        let match;
        
        while ((match = regex.exec(text)) !== null) {
            terms.push(match[1]);
        }
        
        return [...new Set(terms)]; // Remove duplicates
    }
};

// Run demonstrations if this file is executed directly
if (require.main === module) {
    (async () => {
        try {
            await demonstrateBasicHighlighting();
            await demonstrateMultiFieldHighlighting();
            await demonstrateCustomHighlightTags();
            await demonstrateAdvancedHighlighting();
            await demonstrateHighlightingWithPagination();
            await demonstrateHighlightingPerformance();
            
            // Demonstrate utility functions
            console.log('\n=== Highlight Utilities Demo ===\n');
            const sampleText = '<mark>luxury</mark> hotel with <mark>spa</mark> facilities';
            console.log('Original:', sampleText);
            console.log('Stripped:', HighlightUtils.stripHighlightTags(sampleText));
            console.log('Converted:', HighlightUtils.convertHighlightTags(sampleText, '<mark>', '</mark>', '[', ']'));
            console.log('Count:', HighlightUtils.countHighlights(sampleText, '<mark>', '</mark>'));
            console.log('Terms:', HighlightUtils.extractHighlightedTerms(sampleText, '<mark>', '</mark>'));
            
        } catch (error) {
            console.error('Demo failed:', error);
        }
    })();
}

module.exports = { HitHighlighter, HighlightUtils };