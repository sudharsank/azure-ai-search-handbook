/**
 * Range Filters Example
 * 
 * This example demonstrates range filtering operations in Azure AI Search,
 * including numeric ranges, date ranges, and combined range conditions.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class RangeFiltersExample {
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

    async demonstrateNumericRanges() {
        console.log('\n💰 Numeric Range Filters');
        console.log('='.repeat(40));
        
        const rangeExamples = [
            {
                name: 'Budget items ($10-$50)',
                filter: 'price ge 10 and price le 50',
                description: 'Find products in budget price range'
            },
            {
                name: 'Premium items (over $500)',
                filter: 'price gt 500',
                description: 'Find premium/luxury products'
            },
            {
                name: 'Mid-range ratings (3.0-4.0)',
                filter: 'rating ge 3.0 and rating le 4.0',
                description: 'Find moderately rated products'
            },
            {
                name: 'High-value items (price > $100, rating > 4.0)',
                filter: 'price gt 100 and rating gt 4.0',
                description: 'Find expensive, highly-rated products'
            }
        ];

        for (const example of rangeExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'price', 'rating', 'category'],
                    orderBy: ['price asc']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const price = result.price || 'N/A';
                    const rating = result.rating || 'N/A';
                    const category = result.category || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateDateRanges() {
        console.log('\n📅 Date Range Filters');
        console.log('='.repeat(40));
        
        const now = new Date();
        const oneMonthAgo = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
        const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
        
        const dateExamples = [
            {
                name: 'Recent items (last 30 days)',
                filter: `lastModified ge ${oneMonthAgo.toISOString()}`,
                description: 'Find recently updated items'
            },
            {
                name: 'Items from this year',
                filter: `lastModified ge ${new Date(now.getFullYear(), 0, 1).toISOString()}`,
                description: 'Find items updated this year'
            },
            {
                name: 'Older items (over 1 year)',
                filter: `lastModified lt ${oneYearAgo.toISOString()}`,
                description: 'Find items not updated in over a year'
            },
            {
                name: 'Items from specific date range',
                filter: `lastModified ge 2024-01-01T00:00:00Z and lastModified lt 2024-12-31T23:59:59Z`,
                description: 'Find items from 2024'
            }
        ];

        for (const example of dateExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'lastModified', 'category'],
                    orderBy: ['lastModified desc']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const lastModified = result.lastModified ? 
                        new Date(result.lastModified).toLocaleDateString() : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Modified: ${lastModified}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateAdvancedRanges() {
        console.log('\n🔧 Advanced Range Combinations');
        console.log('='.repeat(40));
        
        const advancedExamples = [
            {
                name: 'Sweet spot products',
                filter: '(price ge 50 and price le 200) and (rating ge 4.0 and rating le 5.0)',
                description: 'Find well-priced, highly-rated products'
            },
            {
                name: 'Clearance candidates',
                filter: 'price gt 100 and rating lt 3.0',
                description: 'Find expensive but poorly-rated items'
            },
            {
                name: 'Popular budget items',
                filter: 'price lt 30 and rating gt 4.0',
                description: 'Find cheap but highly-rated products'
            },
            {
                name: 'Recent premium additions',
                filter: `price gt 300 and lastModified ge ${oneMonthAgo.toISOString()}`,
                description: 'Find recently added premium items'
            }
        ];

        for (const example of advancedExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'price', 'rating', 'lastModified', 'category']
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
                    const rating = result.rating || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    buildRangeFilter(field, min = null, max = null, includeMin = true, includeMax = true) {
        /**
         * Build a range filter for a field
         * @param {string} field - Field name
         * @param {number|string} min - Minimum value
         * @param {number|string} max - Maximum value
         * @param {boolean} includeMin - Include minimum value (ge vs gt)
         * @param {boolean} includeMax - Include maximum value (le vs lt)
         * @returns {string|null} Filter expression
         */
        const filters = [];
        
        if (min !== null) {
            const operator = includeMin ? 'ge' : 'gt';
            const value = typeof min === 'string' ? `'${min}'` : min;
            filters.push(`${field} ${operator} ${value}`);
        }
        
        if (max !== null) {
            const operator = includeMax ? 'le' : 'lt';
            const value = typeof max === 'string' ? `'${max}'` : max;
            filters.push(`${field} ${operator} ${value}`);
        }
        
        return filters.length > 0 ? filters.join(' and ') : null;
    }

    async demonstrateRangeBuilder() {
        console.log('\n🏗️ Dynamic Range Filter Building');
        console.log('='.repeat(40));
        
        const rangeScenarios = [
            {
                name: 'Price range $50-$150',
                field: 'price',
                min: 50,
                max: 150,
                includeMin: true,
                includeMax: true
            },
            {
                name: 'Rating above 4.0 (exclusive)',
                field: 'rating',
                min: 4.0,
                max: null,
                includeMin: false,
                includeMax: true
            },
            {
                name: 'Items under $100 (exclusive)',
                field: 'price',
                min: null,
                max: 100,
                includeMin: true,
                includeMax: false
            }
        ];

        for (const scenario of rangeScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            const filter = this.buildRangeFilter(
                scenario.field,
                scenario.min,
                scenario.max,
                scenario.includeMin,
                scenario.includeMax
            );
            
            console.log(`   Generated Filter: ${filter}`);
            console.log(`   Parameters: field=${scenario.field}, min=${scenario.min}, max=${scenario.max}`);
            
            if (filter) {
                try {
                    const searchResults = await this.searchClient.search('*', {
                        filter: filter,
                        top: 2,
                        select: ['id', 'name', scenario.field, 'category']
                    });

                    const results = [];
                    for await (const result of searchResults.results) {
                        results.push(result.document);
                    }

                    console.log(`   Results: ${results.length} items found`);
                    
                    results.forEach((result, index) => {
                        const name = result.name || 'N/A';
                        const category = result.category || 'N/A';
                        const fieldValue = result[scenario.field] || 'N/A';
                        console.log(`     ${index + 1}. ${name} (${category}) - ${scenario.field}: ${fieldValue}`);
                    });
                    
                } catch (error) {
                    console.log(`   ❌ Error: ${error.message}`);
                }
            }
        }
    }

    async run() {
        console.log('🚀 Range Filters Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateNumericRanges();
            await this.demonstrateDateRanges();
            await this.demonstrateAdvancedRanges();
            await this.demonstrateRangeBuilder();
            
            console.log('\n✅ Range filters example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use ge/le for inclusive ranges, gt/lt for exclusive ranges');
            console.log('- Combine multiple range conditions with logical operators');
            console.log('- Handle date ranges with proper ISO format');
            console.log('- Build dynamic range filters based on user input');
            console.log('- Consider performance implications of complex range queries');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new RangeFiltersExample();
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

module.exports = RangeFiltersExample;