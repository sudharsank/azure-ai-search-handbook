/**
 * Sorting Operations Example
 * 
 * This example demonstrates various sorting operations in Azure AI Search,
 * including single-field sorting, multi-field sorting, and geographic sorting.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class SortingOperationsExample {
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

    async demonstrateBasicSorting() {
        console.log('\n📊 Basic Sorting Operations');
        console.log('='.repeat(40));
        
        const sortExamples = [
            {
                name: 'Sort by price (ascending)',
                orderBy: ['price asc'],
                description: 'Show cheapest items first'
            },
            {
                name: 'Sort by price (descending)',
                orderBy: ['price desc'],
                description: 'Show most expensive items first'
            },
            {
                name: 'Sort by rating (descending)',
                orderBy: ['rating desc'],
                description: 'Show highest rated items first'
            },
            {
                name: 'Sort by name (alphabetical)',
                orderBy: ['name asc'],
                description: 'Show items in alphabetical order'
            },
            {
                name: 'Sort by last modified (newest first)',
                orderBy: ['lastModified desc'],
                description: 'Show recently updated items first'
            }
        ];

        for (const example of sortExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   OrderBy: ${example.orderBy.join(', ')}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    orderBy: example.orderBy,
                    top: 3,
                    select: ['id', 'name', 'price', 'rating', 'lastModified', 'category']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    const category = result.category || 'N/A';
                    const lastModified = result.lastModified ? 
                        new Date(result.lastModified).toLocaleDateString() : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐ - ${lastModified}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateMultiFieldSorting() {
        console.log('\n🔗 Multi-Field Sorting');
        console.log('='.repeat(40));
        
        const multiSortExamples = [
            {
                name: 'Category then price',
                orderBy: ['category asc', 'price asc'],
                description: 'Group by category, then sort by price within each category'
            },
            {
                name: 'Rating then price (best value first)',
                orderBy: ['rating desc', 'price asc'],
                description: 'Show highest rated items first, cheapest within each rating'
            },
            {
                name: 'Price tier then rating',
                orderBy: ['price desc', 'rating desc'],
                description: 'Show expensive items first, then by rating within price range'
            },
            {
                name: 'Category, rating, then name',
                orderBy: ['category asc', 'rating desc', 'name asc'],
                description: 'Complex sorting with three criteria'
            }
        ];

        for (const example of multiSortExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   OrderBy: ${example.orderBy.join(', ')}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    orderBy: example.orderBy,
                    top: 4,
                    select: ['id', 'name', 'category', 'price', 'rating']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateGeographicSorting() {
        console.log('\n🌍 Geographic Sorting');
        console.log('='.repeat(40));
        
        // Example coordinates (Seattle, WA)
        const referencePoint = 'geography\'POINT(-122.335167 47.608013)\'';
        
        const geoSortExamples = [
            {
                name: 'Sort by distance from Seattle',
                orderBy: [`geo.distance(location, ${referencePoint})`],
                description: 'Show items closest to Seattle first'
            },
            {
                name: 'Distance then rating',
                orderBy: [`geo.distance(location, ${referencePoint})`, 'rating desc'],
                description: 'Show closest items first, then by rating'
            }
        ];

        for (const example of geoSortExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   OrderBy: ${example.orderBy.join(', ')}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    orderBy: example.orderBy,
                    top: 3,
                    select: ['id', 'name', 'location', 'rating', 'category'],
                    filter: 'location ne null' // Only include items with location data
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const rating = result.rating || 'N/A';
                    const location = result.location ? 
                        `${result.location.coordinates[1]}, ${result.location.coordinates[0]}` : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - ${rating}⭐ - Location: ${location}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateSortingWithFilters() {
        console.log('\n🔍 Sorting with Filters');
        console.log('='.repeat(40));
        
        const filterSortExamples = [
            {
                name: 'Electronics by price (low to high)',
                filter: "category eq 'Electronics'",
                orderBy: ['price asc'],
                description: 'Show electronics sorted by price'
            },
            {
                name: 'High-rated items by price',
                filter: 'rating ge 4.0',
                orderBy: ['rating desc', 'price asc'],
                description: 'Show highly-rated items, cheapest first within each rating'
            },
            {
                name: 'Recent items by rating',
                filter: `lastModified ge ${new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()}`,
                orderBy: ['rating desc', 'lastModified desc'],
                description: 'Show recent items sorted by rating, then by recency'
            }
        ];

        for (const example of filterSortExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            console.log(`   OrderBy: ${example.orderBy.join(', ')}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    orderBy: example.orderBy,
                    top: 3,
                    select: ['id', 'name', 'category', 'price', 'rating', 'lastModified']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    const lastModified = result.lastModified ? 
                        new Date(result.lastModified).toLocaleDateString() : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐ - ${lastModified}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    buildSortExpression(sortCriteria) {
        /**
         * Build a sort expression from criteria
         * @param {Array} sortCriteria - Array of {field, direction} objects
         * @returns {Array} OrderBy array for Azure Search
         */
        return sortCriteria.map(criteria => {
            const direction = criteria.direction || 'asc';
            if (criteria.isGeo) {
                return `geo.distance(${criteria.field}, ${criteria.point}) ${direction}`;
            }
            return `${criteria.field} ${direction}`;
        });
    }

    async demonstrateDynamicSorting() {
        console.log('\n🏗️ Dynamic Sort Building');
        console.log('='.repeat(40));
        
        const sortScenarios = [
            {
                name: 'Price ascending, then rating descending',
                criteria: [
                    { field: 'price', direction: 'asc' },
                    { field: 'rating', direction: 'desc' }
                ]
            },
            {
                name: 'Category, then name alphabetically',
                criteria: [
                    { field: 'category', direction: 'asc' },
                    { field: 'name', direction: 'asc' }
                ]
            },
            {
                name: 'Distance from point, then rating',
                criteria: [
                    { 
                        field: 'location', 
                        direction: 'asc', 
                        isGeo: true, 
                        point: 'geography\'POINT(-122.335167 47.608013)\'' 
                    },
                    { field: 'rating', direction: 'desc' }
                ]
            }
        ];

        for (const scenario of sortScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            const orderBy = this.buildSortExpression(scenario.criteria);
            console.log(`   Generated OrderBy: ${orderBy.join(', ')}`);
            console.log(`   Criteria: ${JSON.stringify(scenario.criteria, null, 2)}`);
            
            try {
                const searchOptions = {
                    orderBy: orderBy,
                    top: 2,
                    select: ['id', 'name', 'category', 'price', 'rating']
                };

                // Add location filter for geo queries
                if (scenario.criteria.some(c => c.isGeo)) {
                    searchOptions.filter = 'location ne null';
                    searchOptions.select.push('location');
                }

                const searchResults = await this.searchClient.search('*', searchOptions);

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    demonstrateSortingBestPractices() {
        console.log('\n💡 Sorting Best Practices');
        console.log('='.repeat(40));
        
        console.log('\n1. Field Configuration');
        console.log('   ✅ Mark fields as sortable: true in index schema');
        console.log('   ✅ Consider storage implications of sortable fields');
        console.log('   ❌ Avoid making unnecessary fields sortable');
        
        console.log('\n2. Performance Optimization');
        console.log('   ✅ Use numeric fields for better sort performance');
        console.log('   ✅ Limit the number of sort criteria');
        console.log('   ✅ Consider caching for frequently used sort orders');
        console.log('   ❌ Avoid complex multi-field sorts on large datasets');
        
        console.log('\n3. User Experience');
        console.log('   ✅ Provide clear sort options to users');
        console.log('   ✅ Show current sort order in UI');
        console.log('   ✅ Allow users to reverse sort direction');
        console.log('   ✅ Combine with pagination for large result sets');
        
        console.log('\n4. Geographic Sorting');
        console.log('   ✅ Use geo.distance() for location-based sorting');
        console.log('   ✅ Validate coordinate formats');
        console.log('   ✅ Consider distance units (default is kilometers)');
        console.log('   ❌ Avoid geo sorting without location filters');
        
        console.log('\n5. Common Sort Patterns');
        console.log('   📊 Relevance: Default search score sorting');
        console.log('   💰 Price: Low to high, high to low');
        console.log('   ⭐ Rating: Highest rated first');
        console.log('   📅 Date: Newest first, oldest first');
        console.log('   🔤 Name: Alphabetical ordering');
        console.log('   📍 Distance: Closest first');
    }

    async run() {
        console.log('🚀 Sorting Operations Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateBasicSorting();
            await this.demonstrateMultiFieldSorting();
            await this.demonstrateGeographicSorting();
            await this.demonstrateSortingWithFilters();
            await this.demonstrateDynamicSorting();
            this.demonstrateSortingBestPractices();
            
            console.log('\n✅ Sorting operations example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use single-field sorting for simple scenarios');
            console.log('- Combine multiple sort criteria for complex ordering');
            console.log('- Use geographic sorting for location-based applications');
            console.log('- Combine sorting with filtering for targeted results');
            console.log('- Build dynamic sort expressions based on user preferences');
            console.log('- Consider performance implications of complex sorting');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new SortingOperationsExample();
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

module.exports = SortingOperationsExample;