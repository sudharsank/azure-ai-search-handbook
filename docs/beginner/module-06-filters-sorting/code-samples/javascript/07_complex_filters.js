/**
 * Complex Filters Example
 * 
 * This example demonstrates advanced filtering operations in Azure AI Search,
 * including collection filters, nested conditions, and complex logical expressions.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class ComplexFiltersExample {
    constructor() {
        this.validateConfiguration();
        
        // Initialize search client
        const credential = new AzureKeyCredential(process.env.SEARCH_API_KEY);
        this.searchClient = new SearchClient(
            process.env.SEARCH_ENDPOINT,
            process.env.INDEX_NAME,
            credential
        );
    }

    validateConfiguration() {
        const requiredVars = ['SEARCH_ENDPOINT', 'SEARCH_API_KEY', 'INDEX_NAME'];
        const missingVars = requiredVars.filter(varName => !process.env[varName]);
        
        if (missingVars.length > 0) {
            throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${process.env.SEARCH_ENDPOINT}`);
        console.log(`📊 Index Name: ${process.env.INDEX_NAME}`);
    }

    async demonstrateCollectionFilters() {
        console.log('\n📚 Collection Filters (any/all)');
        console.log('='.repeat(40));
        
        const collectionExamples = [
            {
                name: 'Items with any featured tag',
                filter: "tags/any(t: t eq 'featured')",
                description: 'Find items that have at least one "featured" tag'
            },
            {
                name: 'Items with wireless OR bluetooth tags',
                filter: "tags/any(t: t eq 'wireless' or t eq 'bluetooth')",
                description: 'Find items with connectivity-related tags'
            },
            {
                name: 'Items where all tags are non-empty',
                filter: "tags/all(t: t ne null and t ne '')",
                description: 'Find items where every tag has a meaningful value'
            },
            {
                name: 'Items with premium-related tags',
                filter: "tags/any(t: contains(t, 'premium') or contains(t, 'luxury') or contains(t, 'pro'))",
                description: 'Find items with any premium-related tags'
            }
        ];

        for (const example of collectionExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'tags', 'category', 'price']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const price = result.price || 'N/A';
                    const tags = result.tags ? result.tags.join(', ') : 'No tags';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price}`);
                    console.log(`        Tags: ${tags}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateNestedComplexFilters() {
        console.log('\n🔗 Nested Complex Filters');
        console.log('='.repeat(40));
        
        const nestedExamples = [
            {
                name: 'Complex product filtering',
                filter: "(category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.5)",
                description: 'Find expensive electronics OR highly-rated books'
            },
            {
                name: 'Multi-criteria premium items',
                filter: "(brand eq 'Apple' or brand eq 'Samsung') and (price gt 500 and rating gt 4.0) and tags/any(t: t eq 'premium')",
                description: 'Find premium items from top brands with high price and rating'
            },
            {
                name: 'Availability and quality filter',
                filter: "inStock eq true and ((rating ge 4.0 and price le 200) or (rating ge 4.5 and price le 500))",
                description: 'Find in-stock items that are either good value or high quality'
            },
            {
                name: 'Geographic and category filter',
                filter: "(category eq 'Restaurant' or category eq 'Hotel') and geo.distance(location, geography'POINT(-122.335167 47.608013)') le 25",
                description: 'Find restaurants or hotels within 25km of Seattle'
            }
        ];

        for (const example of nestedExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'brand', 'price', 'rating', 'inStock', 'tags', 'location']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const brand = result.brand || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    const inStock = result.inStock !== undefined ? result.inStock : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - ${brand} - $${price} - ${rating}⭐ - Stock: ${inStock}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateSearchWithComplexFilters() {
        console.log('\n🔍 Search Queries with Complex Filters');
        console.log('='.repeat(40));
        
        const searchFilterExamples = [
            {
                name: 'Search "laptop" with complex filters',
                searchText: 'laptop computer',
                filter: "(category eq 'Electronics' and price ge 500 and price le 2000) and (rating ge 4.0 or tags/any(t: t eq 'bestseller'))",
                description: 'Search for laptops with price range and quality filters'
            },
            {
                name: 'Search "wireless" with availability',
                searchText: 'wireless bluetooth',
                filter: "inStock eq true and (tags/any(t: t eq 'wireless' or t eq 'bluetooth')) and price le 300",
                description: 'Search wireless products that are in stock and affordable'
            },
            {
                name: 'Search "premium" with brand filter',
                searchText: 'premium quality',
                filter: "(brand eq 'Apple' or brand eq 'Samsung' or brand eq 'Sony') and rating ge 4.5",
                description: 'Search premium products from trusted brands'
            }
        ];

        for (const example of searchFilterExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Search Text: "${example.searchText}"`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search(example.searchText, {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'brand', 'price', 'rating', 'tags', 'inStock'],
                    orderBy: ['search.score() desc', 'rating desc']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const brand = result.brand || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - ${brand} - $${price} - ${rating}⭐`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateAdvancedCollectionScenarios() {
        console.log('\n🎯 Advanced Collection Scenarios');
        console.log('='.repeat(40));
        
        const advancedCollectionExamples = [
            {
                name: 'Items with multiple specific tags',
                filter: "tags/any(t: t eq 'wireless') and tags/any(t: t eq 'premium')",
                description: 'Find items that have both wireless AND premium tags'
            },
            {
                name: 'Items missing essential tags',
                filter: "not tags/any(t: t eq 'featured' or t eq 'bestseller' or t eq 'premium')",
                description: 'Find items without any promotional tags'
            },
            {
                name: 'Items with tag count implications',
                filter: "tags/any() and not tags/any(t: t eq null or t eq '')",
                description: 'Find items that have tags and all tags are meaningful'
            },
            {
                name: 'Complex tag pattern matching',
                filter: "tags/any(t: startswith(t, 'color-') or startswith(t, 'size-') or startswith(t, 'material-'))",
                description: 'Find items with attribute-based tags'
            }
        ];

        for (const example of advancedCollectionExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'tags', 'category', 'price']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const price = result.price || 'N/A';
                    const tags = result.tags ? result.tags.join(', ') : 'No tags';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price}`);
                    console.log(`        Tags: ${tags}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    buildComplexFilter(criteria) {
        /**
         * Build a complex filter from structured criteria
         * @param {Object} criteria - Filter criteria object
         * @returns {string} Complex filter expression
         */
        const filters = [];
        
        // Category filters
        if (criteria.categories && criteria.categories.length > 0) {
            const categoryFilters = criteria.categories.map(cat => `category eq '${cat}'`);
            filters.push(`(${categoryFilters.join(' or ')})`);
        }
        
        // Price range
        if (criteria.minPrice !== undefined || criteria.maxPrice !== undefined) {
            const priceFilters = [];
            if (criteria.minPrice !== undefined) {
                priceFilters.push(`price ge ${criteria.minPrice}`);
            }
            if (criteria.maxPrice !== undefined) {
                priceFilters.push(`price le ${criteria.maxPrice}`);
            }
            filters.push(`(${priceFilters.join(' and ')})`);
        }
        
        // Rating filter
        if (criteria.minRating !== undefined) {
            filters.push(`rating ge ${criteria.minRating}`);
        }
        
        // Brand filters
        if (criteria.brands && criteria.brands.length > 0) {
            const brandFilters = criteria.brands.map(brand => `brand eq '${brand}'`);
            filters.push(`(${brandFilters.join(' or ')})`);
        }
        
        // Tag filters
        if (criteria.requiredTags && criteria.requiredTags.length > 0) {
            const tagFilters = criteria.requiredTags.map(tag => `tags/any(t: t eq '${tag}')`);
            filters.push(`(${tagFilters.join(' and ')})`);
        }
        
        if (criteria.anyTags && criteria.anyTags.length > 0) {
            const anyTagFilters = criteria.anyTags.map(tag => `t eq '${tag}'`);
            filters.push(`tags/any(t: ${anyTagFilters.join(' or ')})`);
        }
        
        // Availability
        if (criteria.inStock !== undefined) {
            filters.push(`inStock eq ${criteria.inStock}`);
        }
        
        // Geographic filter
        if (criteria.location) {
            const { lat, lon, radiusKm } = criteria.location;
            const point = `geography'POINT(${lon} ${lat})'`;
            filters.push(`geo.distance(location, ${point}) le ${radiusKm}`);
        }
        
        // Date filter
        if (criteria.modifiedAfter) {
            const date = criteria.modifiedAfter instanceof Date ? 
                criteria.modifiedAfter.toISOString() : criteria.modifiedAfter;
            filters.push(`lastModified ge ${date}`);
        }
        
        return filters.length > 0 ? filters.join(' and ') : null;
    }

    async demonstrateDynamicComplexFiltering() {
        console.log('\n🏗️ Dynamic Complex Filter Building');
        console.log('='.repeat(40));
        
        const complexScenarios = [
            {
                name: 'Premium electronics search',
                criteria: {
                    categories: ['Electronics', 'Computers'],
                    minPrice: 500,
                    maxPrice: 2000,
                    minRating: 4.0,
                    brands: ['Apple', 'Samsung', 'Sony'],
                    anyTags: ['premium', 'bestseller', 'featured'],
                    inStock: true
                }
            },
            {
                name: 'Local restaurant search',
                criteria: {
                    categories: ['Restaurant', 'Food'],
                    minRating: 4.0,
                    location: { lat: 47.608013, lon: -122.335167, radiusKm: 10 },
                    anyTags: ['delivery', 'takeout', 'dine-in']
                }
            },
            {
                name: 'Recent budget items',
                criteria: {
                    maxPrice: 100,
                    minRating: 3.5,
                    modifiedAfter: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
                    inStock: true,
                    anyTags: ['sale', 'discount', 'budget']
                }
            }
        ];

        for (const scenario of complexScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            const filter = this.buildComplexFilter(scenario.criteria);
            
            console.log(`   Generated Filter: ${filter}`);
            console.log(`   Criteria: ${JSON.stringify(scenario.criteria, null, 2)}`);
            
            if (filter) {
                try {
                    const searchResults = await this.searchClient.search('*', {
                        filter: filter,
                        top: 2,
                        select: ['id', 'name', 'category', 'brand', 'price', 'rating', 'tags', 'inStock', 'location']
                    });

                    const results = [];
                    for await (const result of searchResults.results) {
                        results.push(result.document);
                    }

                    console.log(`   Results: ${results.length} items found`);
                    
                    results.forEach((result, index) => {
                        const name = result.name || 'N/A';
                        const category = result.category || 'N/A';
                        const brand = result.brand || 'N/A';
                        const price = result.price || 'N/A';
                        const rating = result.rating || 'N/A';
                        console.log(`     ${index + 1}. ${name} (${category}) - ${brand} - $${price} - ${rating}⭐`);
                    });
                    
                } catch (error) {
                    console.log(`   ❌ Error: ${error.message}`);
                }
            }
        }
    }

    demonstrateComplexFilterBestPractices() {
        console.log('\n💡 Complex Filter Best Practices');
        console.log('='.repeat(40));
        
        console.log('\n1. Logical Operator Precedence');
        console.log('   ✅ Use parentheses to group conditions clearly');
        console.log('   ✅ Remember: NOT > Comparison > AND > OR');
        console.log('   ✅ Example: (A and B) or (C and D)');
        console.log('   ❌ Avoid: A and B or C and D (ambiguous)');
        
        console.log('\n2. Collection Filter Rules');
        console.log('   ✅ Use any() for "at least one" conditions');
        console.log('   ✅ Use all() for "every item" conditions');
        console.log('   ✅ Combine multiple any() for AND logic between collections');
        console.log('   ❌ Don\'t nest collection operators');
        
        console.log('\n3. Performance Optimization');
        console.log('   ✅ Put most selective filters first');
        console.log('   ✅ Use simple filters before complex ones');
        console.log('   ✅ Limit the number of OR conditions');
        console.log('   ❌ Avoid deeply nested expressions');
        
        console.log('\n4. Filter Complexity Management');
        console.log('   ✅ Break complex filters into smaller parts');
        console.log('   ✅ Use helper functions to build filters');
        console.log('   ✅ Test individual filter components');
        console.log('   ✅ Document complex filter logic');
        
        console.log('\n5. Common Complex Patterns');
        console.log('   🔍 Multi-category: (cat eq \'A\' or cat eq \'B\') and price gt 100');
        console.log('   🏷️ Tag combinations: tags/any(t: t eq \'X\') and tags/any(t: t eq \'Y\')');
        console.log('   📍 Geo + filters: geo.distance(...) le 10 and category eq \'Restaurant\'');
        console.log('   🔗 Search + filter: Full-text search with complex filter criteria');
        
        console.log('\n6. Error Prevention');
        console.log('   ✅ Validate all input values before building filters');
        console.log('   ✅ Escape special characters in string values');
        console.log('   ✅ Handle null and empty values appropriately');
        console.log('   ✅ Test with edge cases and boundary conditions');
        
        console.log('\n7. Debugging Complex Filters');
        console.log('   ✅ Test individual filter components separately');
        console.log('   ✅ Use simple test data to verify logic');
        console.log('   ✅ Check operator precedence with parentheses');
        console.log('   ✅ Validate OData syntax with simple tools');
    }

    async run() {
        console.log('🚀 Complex Filters Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateCollectionFilters();
            await this.demonstrateNestedComplexFilters();
            await this.demonstrateSearchWithComplexFilters();
            await this.demonstrateAdvancedCollectionScenarios();
            await this.demonstrateDynamicComplexFiltering();
            this.demonstrateComplexFilterBestPractices();
            
            console.log('\n✅ Complex filters example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use collection filters (any/all) for array fields');
            console.log('- Group complex conditions with parentheses for clarity');
            console.log('- Combine search queries with complex filters for precision');
            console.log('- Build dynamic filters from structured criteria objects');
            console.log('- Optimize performance by ordering filters by selectivity');
            console.log('- Test complex filters thoroughly with various data scenarios');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new ComplexFiltersExample();
    try {
        await example.run();
    } catch (error) {
        console.error(`Application failed: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = ComplexFiltersExample;