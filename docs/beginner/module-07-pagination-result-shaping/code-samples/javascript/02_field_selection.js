/**
 * Module 7: Field Selection and Result Optimization
 * 
 * This example demonstrates how to use field selection to optimize response
 * payloads, improve performance, and control data exposure.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Configuration
const config = {
    endpoint: process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net',
    apiKey: process.env.SEARCH_API_KEY || 'your-api-key',
    indexName: process.env.INDEX_NAME || 'hotels-sample'
};

class FieldSelector {
    constructor(searchClient) {
        this.searchClient = searchClient;
        this.indexSchema = null;
    }

    /**
     * Load and cache index schema for field validation
     */
    async loadIndexSchema() {
        if (!this.indexSchema) {
            try {
                // Note: In a real application, you might get this from the management client
                // For this example, we'll simulate the schema
                this.indexSchema = {
                    fields: [
                        { name: 'hotelId', type: 'Edm.String', retrievable: true },
                        { name: 'hotelName', type: 'Edm.String', retrievable: true },
                        { name: 'description', type: 'Edm.String', retrievable: true },
                        { name: 'category', type: 'Edm.String', retrievable: true },
                        { name: 'rating', type: 'Edm.Double', retrievable: true },
                        { name: 'location', type: 'Edm.GeographyPoint', retrievable: true },
                        { name: 'address', type: 'Edm.ComplexType', retrievable: true },
                        { name: 'rooms', type: 'Collection(Edm.ComplexType)', retrievable: true },
                        { name: 'tags', type: 'Collection(Edm.String)', retrievable: true },
                        { name: 'parkingIncluded', type: 'Edm.Boolean', retrievable: true },
                        { name: 'smokingAllowed', type: 'Edm.Boolean', retrievable: true },
                        { name: 'lastRenovationDate', type: 'Edm.DateTimeOffset', retrievable: true }
                    ]
                };
            } catch (error) {
                console.warn('Could not load index schema:', error.message);
                this.indexSchema = { fields: [] };
            }
        }
        return this.indexSchema;
    }

    /**
     * Get retrievable fields from index schema
     */
    async getRetrievableFields() {
        const schema = await this.loadIndexSchema();
        return schema.fields
            .filter(field => field.retrievable !== false)
            .map(field => field.name);
    }

    /**
     * Validate field selection against index schema
     */
    async validateFields(fields) {
        const retrievableFields = await this.getRetrievableFields();
        const invalidFields = fields.filter(field => !retrievableFields.includes(field));
        
        if (invalidFields.length > 0) {
            throw new Error(`Invalid or non-retrievable fields: ${invalidFields.join(', ')}`);
        }
        
        return true;
    }

    /**
     * Search with specific field selection
     */
    async searchWithFields(searchText, fields, options = {}) {
        try {
            // Validate fields if schema is available
            if (this.indexSchema) {
                await this.validateFields(fields);
            }

            const searchOptions = {
                select: fields,
                top: options.top || 10,
                skip: options.skip || 0,
                includeTotalCount: options.includeTotalCount || false,
                ...options
            };

            console.log(`Searching with fields: ${fields.join(', ')}`);
            
            const startTime = Date.now();
            const results = await this.searchClient.search(searchText, searchOptions);
            const duration = Date.now() - startTime;

            // Calculate approximate response size
            const responseSize = this.estimateResponseSize(results);

            return {
                results: results.results,
                count: results.count,
                duration,
                responseSize,
                fieldsRequested: fields,
                fieldsReturned: this.getReturnedFields(results.results)
            };

        } catch (error) {
            console.error('Field selection search error:', error);
            throw error;
        }
    }

    /**
     * Compare response sizes with different field selections
     */
    async compareFieldSelections(searchText, fieldSets) {
        const comparisons = [];

        for (const fieldSet of fieldSets) {
            try {
                const result = await this.searchWithFields(searchText, fieldSet.fields, { top: 10 });
                
                comparisons.push({
                    name: fieldSet.name,
                    fields: fieldSet.fields,
                    duration: result.duration,
                    responseSize: result.responseSize,
                    resultCount: result.results.length
                });

                console.log(`${fieldSet.name}: ${result.duration}ms, ~${result.responseSize} bytes`);
                
            } catch (error) {
                comparisons.push({
                    name: fieldSet.name,
                    fields: fieldSet.fields,
                    error: error.message
                });
            }
        }

        return comparisons;
    }

    /**
     * Get field selection for different use cases
     */
    getFieldSelectionPresets() {
        return {
            // Minimal fields for list views
            listView: ['hotelId', 'hotelName', 'rating', 'category'],
            
            // Essential fields for search results
            searchResults: ['hotelId', 'hotelName', 'description', 'rating', 'location'],
            
            // Comprehensive fields for detail views
            detailView: ['hotelId', 'hotelName', 'description', 'category', 'rating', 
                        'location', 'address', 'tags', 'parkingIncluded', 'smokingAllowed'],
            
            // Fields for map display
            mapView: ['hotelId', 'hotelName', 'location', 'rating'],
            
            // Fields for comparison
            comparison: ['hotelId', 'hotelName', 'rating', 'category', 'tags', 'parkingIncluded'],
            
            // Minimal fields for autocomplete
            autocomplete: ['hotelId', 'hotelName'],
            
            // Fields for analytics/reporting
            analytics: ['hotelId', 'category', 'rating', 'lastRenovationDate']
        };
    }

    /**
     * Estimate response size (approximate)
     */
    estimateResponseSize(results) {
        try {
            return JSON.stringify(results).length;
        } catch (error) {
            return 0;
        }
    }

    /**
     * Get fields that were actually returned in results
     */
    getReturnedFields(results) {
        if (!results || results.length === 0) return [];
        
        const firstResult = results[0].document;
        return Object.keys(firstResult);
    }

    /**
     * Dynamic field selection based on context
     */
    async searchWithContext(searchText, context, options = {}) {
        const presets = this.getFieldSelectionPresets();
        const fields = presets[context] || presets.searchResults;
        
        console.log(`Using ${context} context with fields: ${fields.join(', ')}`);
        
        return this.searchWithFields(searchText, fields, options);
    }
}

/**
 * Demonstrate basic field selection
 */
async function demonstrateBasicFieldSelection() {
    console.log('=== Basic Field Selection Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const fieldSelector = new FieldSelector(searchClient);

    try {
        // Search without field selection (all fields)
        console.log('1. Search without field selection (all fields):');
        const allFieldsResult = await fieldSelector.searchWithFields('luxury', [], { top: 3 });
        console.log(`Duration: ${allFieldsResult.duration}ms`);
        console.log(`Response size: ~${allFieldsResult.responseSize} bytes`);
        console.log(`Fields returned: ${allFieldsResult.fieldsReturned.join(', ')}\n`);

        // Search with minimal field selection
        console.log('2. Search with minimal field selection:');
        const minimalFields = ['hotelId', 'hotelName', 'rating'];
        const minimalResult = await fieldSelector.searchWithFields('luxury', minimalFields, { top: 3 });
        console.log(`Duration: ${minimalResult.duration}ms`);
        console.log(`Response size: ~${minimalResult.responseSize} bytes`);
        console.log(`Fields returned: ${minimalResult.fieldsReturned.join(', ')}\n`);

        // Calculate size reduction
        const sizeReduction = ((allFieldsResult.responseSize - minimalResult.responseSize) / allFieldsResult.responseSize * 100).toFixed(1);
        console.log(`Size reduction: ${sizeReduction}%\n`);

        // Display sample results
        console.log('Sample results with minimal fields:');
        minimalResult.results.forEach((result, index) => {
            const doc = result.document;
            console.log(`  ${index + 1}. ${doc.hotelName} (Rating: ${doc.rating}, ID: ${doc.hotelId})`);
        });

    } catch (error) {
        console.error('Basic field selection demo error:', error.message);
    }
}

/**
 * Demonstrate context-based field selection
 */
async function demonstrateContextBasedSelection() {
    console.log('\n=== Context-Based Field Selection Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const fieldSelector = new FieldSelector(searchClient);

    try {
        const contexts = ['listView', 'searchResults', 'mapView', 'comparison'];
        
        for (const context of contexts) {
            console.log(`${context.toUpperCase()} Context:`);
            const result = await fieldSelector.searchWithContext('*', context, { top: 2 });
            
            console.log(`  Duration: ${result.duration}ms`);
            console.log(`  Response size: ~${result.responseSize} bytes`);
            console.log(`  Fields: ${result.fieldsReturned.join(', ')}`);
            
            // Show sample result
            if (result.results.length > 0) {
                const doc = result.results[0].document;
                console.log(`  Sample: ${JSON.stringify(doc, null, 2).substring(0, 200)}...`);
            }
            console.log();
        }

    } catch (error) {
        console.error('Context-based selection demo error:', error.message);
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

    const fieldSelector = new FieldSelector(searchClient);

    try {
        const fieldSets = [
            {
                name: 'All Fields',
                fields: [] // Empty array means all fields
            },
            {
                name: 'Essential Only',
                fields: ['hotelId', 'hotelName', 'rating']
            },
            {
                name: 'Search Results',
                fields: ['hotelId', 'hotelName', 'description', 'rating', 'category']
            },
            {
                name: 'Detail View',
                fields: ['hotelId', 'hotelName', 'description', 'category', 'rating', 
                        'location', 'tags', 'parkingIncluded']
            }
        ];

        console.log('Comparing field selection performance:');
        const comparisons = await fieldSelector.compareFieldSelections('luxury', fieldSets);
        
        console.log('\nComparison Summary:');
        comparisons.forEach(comp => {
            if (comp.error) {
                console.log(`${comp.name}: ERROR - ${comp.error}`);
            } else {
                console.log(`${comp.name}: ${comp.duration}ms, ~${comp.responseSize} bytes, ${comp.resultCount} results`);
            }
        });

        // Find the most efficient option
        const validComparisons = comparisons.filter(c => !c.error);
        if (validComparisons.length > 0) {
            const fastest = validComparisons.reduce((prev, current) => 
                prev.duration < current.duration ? prev : current
            );
            const smallest = validComparisons.reduce((prev, current) => 
                prev.responseSize < current.responseSize ? prev : current
            );
            
            console.log(`\nFastest: ${fastest.name} (${fastest.duration}ms)`);
            console.log(`Smallest: ${smallest.name} (~${smallest.responseSize} bytes)`);
        }

    } catch (error) {
        console.error('Performance comparison demo error:', error.message);
    }
}

/**
 * Demonstrate field validation
 */
async function demonstrateFieldValidation() {
    console.log('\n=== Field Validation Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const fieldSelector = new FieldSelector(searchClient);

    try {
        // Load schema for validation
        await fieldSelector.loadIndexSchema();
        
        // Test valid fields
        console.log('1. Testing valid fields:');
        const validFields = ['hotelId', 'hotelName', 'rating'];
        try {
            await fieldSelector.validateFields(validFields);
            console.log(`✓ Valid fields: ${validFields.join(', ')}`);
        } catch (error) {
            console.log(`✗ Validation error: ${error.message}`);
        }

        // Test invalid fields
        console.log('\n2. Testing invalid fields:');
        const invalidFields = ['hotelId', 'nonExistentField', 'anotherBadField'];
        try {
            await fieldSelector.validateFields(invalidFields);
            console.log(`✓ Valid fields: ${invalidFields.join(', ')}`);
        } catch (error) {
            console.log(`✗ Expected validation error: ${error.message}`);
        }

        // Show available fields
        console.log('\n3. Available retrievable fields:');
        const retrievableFields = await fieldSelector.getRetrievableFields();
        console.log(retrievableFields.join(', '));

    } catch (error) {
        console.error('Field validation demo error:', error.message);
    }
}

/**
 * Demonstrate pagination with field selection
 */
async function demonstratePaginationWithFields() {
    console.log('\n=== Pagination with Field Selection Demo ===\n');

    const searchClient = new SearchClient(
        config.endpoint,
        config.indexName,
        new AzureKeyCredential(config.apiKey)
    );

    const fieldSelector = new FieldSelector(searchClient);

    try {
        const fields = ['hotelId', 'hotelName', 'rating', 'category'];
        
        // Load multiple pages with field selection
        for (let page = 0; page < 3; page++) {
            console.log(`Page ${page + 1}:`);
            
            const result = await fieldSelector.searchWithFields('*', fields, {
                skip: page * 5,
                top: 5,
                includeTotalCount: page === 0 // Only get count on first page
            });

            console.log(`  Duration: ${result.duration}ms`);
            console.log(`  Results: ${result.results.length}`);
            if (result.count !== undefined) {
                console.log(`  Total: ${result.count}`);
            }

            // Show results
            result.results.forEach((searchResult, index) => {
                const doc = searchResult.document;
                console.log(`    ${index + 1}. ${doc.hotelName} (${doc.category}, Rating: ${doc.rating})`);
            });
            
            console.log();
        }

    } catch (error) {
        console.error('Pagination with fields demo error:', error.message);
    }
}

/**
 * Utility function to create field selection helper
 */
function createFieldSelectionHelper() {
    return {
        // Common field combinations
        minimal: ['hotelId', 'hotelName'],
        basic: ['hotelId', 'hotelName', 'rating'],
        standard: ['hotelId', 'hotelName', 'rating', 'category'],
        detailed: ['hotelId', 'hotelName', 'description', 'rating', 'category', 'location'],
        
        // Helper methods
        forListView: () => ['hotelId', 'hotelName', 'rating', 'category'],
        forMapView: () => ['hotelId', 'hotelName', 'location', 'rating'],
        forComparison: () => ['hotelId', 'hotelName', 'rating', 'category', 'tags'],
        
        // Dynamic selection based on screen size or context
        forMobile: () => ['hotelId', 'hotelName', 'rating'],
        forDesktop: () => ['hotelId', 'hotelName', 'description', 'rating', 'category'],
        
        // Custom field builder
        custom: (...fields) => fields
    };
}

// Run demonstrations if this file is executed directly
if (require.main === module) {
    (async () => {
        try {
            await demonstrateBasicFieldSelection();
            await demonstrateContextBasedSelection();
            await demonstratePerformanceComparison();
            await demonstrateFieldValidation();
            await demonstratePaginationWithFields();
            
            // Show helper usage
            console.log('\n=== Field Selection Helper Demo ===\n');
            const helper = createFieldSelectionHelper();
            console.log('Helper examples:');
            console.log('Minimal:', helper.minimal);
            console.log('For list view:', helper.forListView());
            console.log('For mobile:', helper.forMobile());
            console.log('Custom:', helper.custom('hotelId', 'hotelName', 'specialField'));
            
        } catch (error) {
            console.error('Demo failed:', error);
        }
    })();
}

module.exports = { FieldSelector, createFieldSelectionHelper };