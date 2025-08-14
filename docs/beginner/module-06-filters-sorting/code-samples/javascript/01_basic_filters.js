/**
 * Basic Filters Example
 * 
 * This example demonstrates fundamental filtering operations in Azure AI Search,
 * including equality filters, comparison filters, and logical combinations.
 */

const { SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

class BasicFiltersExample {
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
    
    async demonstrateEqualityFilters() {
        console.log('\n🔍 Equality Filters');
        console.log('='.repeat(40));
        
        const filterExamples = [
            {
                name: 'Category equals Electronics',
                filter: "category eq 'Electronics'",
                description: 'Find all products in Electronics category'
            },
            {
                name: 'Status not discontinued',
                filter: "status ne 'Discontinued'",
                description: 'Find products that are not discontinued'
            },
            {
                name: 'In stock items',
                filter: "inStock eq true",
                description: 'Find items that are currently in stock'
            },
            {
                name: 'Out of stock items',
                filter: "inStock eq false",
                description: 'Find items that are out of stock'
            }
        ];
        
        for (const example of filterExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const results = await this.searchClient.search("*", {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'status', 'inStock', 'price']
                });
                
                const resultList = [];
                for await (const result of results.results) {
                    resultList.push(result);
                }
                
                console.log(`   Results: ${resultList.length} items found`);
                
                resultList.slice(0, 2).forEach((result, index) => {
                    const doc = result.document;
                    const name = doc.name || 'N/A';
                    const category = doc.category || 'N/A';
                    const status = doc.status || 'N/A';
                    const inStock = doc.inStock !== undefined ? doc.inStock : 'N/A';
                    const price = doc.price || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${status} - Stock: ${inStock}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }
    
    async demonstrateComparisonFilters() {
        console.log('\n📊 Comparison Filters');
        console.log('='.repeat(40));
        
        const comparisonExamples = [
            {
                name: 'Price greater than $100',
                filter: "price gt 100",
                description: 'Find products priced above $100'
            },
            {
                name: 'Rating 4.0 or higher',
                filter: "rating ge 4.0",
                description: 'Find highly rated products (4+ stars)'
            },
            {
                name: 'Price less than $50',
                filter: "price lt 50",
                description: 'Find budget-friendly products under $50'
            },
            {
                name: 'Rating 3.0 or lower',
                filter: "rating le 3.0",
                description: 'Find lower-rated products (3 stars or less)'
            }
        ];
        
        for (const example of comparisonExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const orderBy = example.filter.includes('price') ? ['price asc'] : ['rating desc'];
                
                const results = await this.searchClient.search("*", {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'price', 'rating', 'category'],
                    orderBy: orderBy
                });
                
                const resultList = [];
                for await (const result of results.results) {
                    resultList.push(result);
                }
                
                console.log(`   Results: ${resultList.length} items found`);
                
                resultList.slice(0, 2).forEach((result, index) => {
                    const doc = result.document;
                    const name = doc.name || 'N/A';
                    const price = doc.price || 'N/A';
                    const rating = doc.rating || 'N/A';
                    const category = doc.category || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }
    
    async demonstrateLogicalCombinations() {
        console.log('\n🔗 Logical Combinations');
        console.log('='.repeat(40));
        
        const logicalExamples = [
            {
                name: 'Electronics AND high rating',
                filter: "category eq 'Electronics' and rating ge 4.0",
                description: 'Find high-rated electronics products'
            },
            {
                name: 'Budget OR Premium categories',
                filter: "category eq 'Budget' or category eq 'Premium'",
                description: 'Find products in Budget or Premium categories'
            },
            {
                name: 'NOT discontinued items',
                filter: "not (status eq 'Discontinued')",
                description: 'Find all non-discontinued products'
            },
            {
                name: 'Complex combination',
                filter: "(category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.5)",
                description: 'Find expensive electronics OR highly-rated books'
            }
        ];
        
        for (const example of logicalExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const results = await this.searchClient.search("*", {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'price', 'rating', 'status']
                });
                
                const resultList = [];
                for await (const result of results.results) {
                    resultList.push(result);
                }
                
                console.log(`   Results: ${resultList.length} items found`);
                
                resultList.slice(0, 2).forEach((result, index) => {
                    const doc = result.document;
                    const name = doc.name || 'N/A';
                    const category = doc.category || 'N/A';
                    const price = doc.price || 'N/A';
                    const rating = doc.rating || 'N/A';
                    const status = doc.status || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐ - ${status}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }
    
    async demonstrateNullHandling() {
        console.log('\n🚫 Null Value Handling');
        console.log('='.repeat(40));
        
        const nullExamples = [
            {
                name: 'Items with rating',
                filter: "rating ne null",
                description: 'Find items that have a rating value'
            },
            {
                name: 'Items without description',
                filter: "description eq null",
                description: 'Find items missing description'
            },
            {
                name: 'Items with non-zero price',
                filter: "price ne null and price gt 0",
                description: 'Find items with valid pricing'
            }
        ];
        
        for (const example of nullExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const results = await this.searchClient.search("*", {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'price', 'rating', 'description']
                });
                
                const resultList = [];
                for await (const result of results.results) {
                    resultList.push(result);
                }
                
                console.log(`   Results: ${resultList.length} items found`);
                
                resultList.slice(0, 2).forEach((result, index) => {
                    const doc = result.document;
                    const name = doc.name || 'N/A';
                    const price = doc.price || 'N/A';
                    const rating = doc.rating || 'N/A';
                    const hasDesc = doc.description ? 'Yes' : 'No';
                    console.log(`     ${index + 1}. ${name} - $${price} - ${rating}⭐ - Desc: ${hasDesc}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }
    
    async demonstrateFilterBuilding() {
        console.log('\n🔧 Dynamic Filter Building');
        console.log('='.repeat(40));
        
        function buildProductFilter(options = {}) {
            const { category, minPrice, maxPrice, minRating, inStock } = options;
            const filters = [];
            
            if (category) {
                filters.push(`category eq '${category}'`);
            }
            
            if (minPrice !== undefined) {
                filters.push(`price ge ${minPrice}`);
            }
            
            if (maxPrice !== undefined) {
                filters.push(`price le ${maxPrice}`);
            }
            
            if (minRating !== undefined) {
                filters.push(`rating ge ${minRating}`);
            }
            
            if (inStock !== undefined) {
                filters.push(`inStock eq ${inStock}`);
            }
            
            return filters.length > 0 ? filters.join(' and ') : null;
        }
        
        // Test different filter combinations
        const filterScenarios = [
            {
                name: 'Electronics under $200',
                params: { category: 'Electronics', maxPrice: 200 }
            },
            {
                name: 'High-rated items in stock',
                params: { minRating: 4.0, inStock: true }
            },
            {
                name: 'Budget items ($10-$50)',
                params: { minPrice: 10, maxPrice: 50 }
            },
            {
                name: 'Premium electronics in stock',
                params: { category: 'Electronics', minPrice: 500, inStock: true }
            }
        ];
        
        for (const scenario of filterScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            const filterExpr = buildProductFilter(scenario.params);
            console.log(`   Generated Filter: ${filterExpr}`);
            console.log(`   Parameters: ${JSON.stringify(scenario.params)}`);
            
            if (filterExpr) {
                try {
                    const results = await this.searchClient.search("*", {
                        filter: filterExpr,
                        top: 2,
                        select: ['id', 'name', 'category', 'price', 'rating', 'inStock']
                    });
                    
                    const resultList = [];
                    for await (const result of results.results) {
                        resultList.push(result);
                    }
                    
                    console.log(`   Results: ${resultList.length} items found`);
                    
                    resultList.forEach((result, index) => {
                        const doc = result.document;
                        const name = doc.name || 'N/A';
                        const category = doc.category || 'N/A';
                        const price = doc.price || 'N/A';
                        const rating = doc.rating || 'N/A';
                        const inStock = doc.inStock !== undefined ? doc.inStock : 'N/A';
                        console.log(`     ${index + 1}. ${name} (${category}) - $${price} - ${rating}⭐ - Stock: ${inStock}`);
                    });
                    
                } catch (error) {
                    console.log(`   ❌ Error: ${error.message}`);
                }
            }
        }
    }
    
    demonstrateBestPractices() {
        console.log('\n💡 Filter Best Practices');
        console.log('='.repeat(40));
        
        console.log('\n1. Use specific filters first (most selective)');
        console.log("   ✅ Good: category eq 'Electronics' and price gt 1000");
        console.log("   ❌ Avoid: price gt 0 and category eq 'Electronics'");
        
        console.log('\n2. Use appropriate data types');
        console.log('   ✅ Good: price gt 100 (numeric)');
        console.log("   ❌ Avoid: price gt '100' (string)");
        
        console.log('\n3. Handle null values explicitly');
        console.log('   ✅ Good: rating ne null and rating ge 4.0');
        console.log('   ❌ Risky: rating ge 4.0 (may include nulls)');
        
        console.log('\n4. Use parentheses for complex logic');
        console.log("   ✅ Good: (category eq 'A' and price gt 100) or (category eq 'B' and rating ge 4.0)");
        console.log("   ❌ Confusing: category eq 'A' and price gt 100 or category eq 'B' and rating ge 4.0");
        
        console.log('\n5. Validate filter expressions');
        
        function validateFilterSyntax(filterExpr) {
            if (!filterExpr) {
                return { valid: true, message: "Empty filter is valid" };
            }
            
            // Check for balanced parentheses
            const openParens = (filterExpr.match(/\(/g) || []).length;
            const closeParens = (filterExpr.match(/\)/g) || []).length;
            if (openParens !== closeParens) {
                return { valid: false, message: "Unbalanced parentheses" };
            }
            
            // Check for balanced quotes
            const singleQuotes = (filterExpr.match(/'/g) || []).length;
            if (singleQuotes % 2 !== 0) {
                return { valid: false, message: "Unbalanced single quotes" };
            }
            
            return { valid: true, message: "Filter appears valid" };
        }
        
        const testFilters = [
            "category eq 'Electronics'",  // Valid
            "category eq 'Electronics",   // Invalid - missing quote
            "(price gt 100 and rating ge 4.0",  // Invalid - unbalanced parentheses
            "price gt 100 and rating ge 4.0"    // Valid
        ];
        
        console.log('\n   Filter Validation Examples:');
        testFilters.forEach(filterExpr => {
            const result = validateFilterSyntax(filterExpr);
            const status = result.valid ? "✅" : "❌";
            console.log(`   ${status} '${filterExpr}' - ${result.message}`);
        });
    }
    
    async run() {
        console.log('🚀 Basic Filters Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateEqualityFilters();
            await this.demonstrateComparisonFilters();
            await this.demonstrateLogicalCombinations();
            await this.demonstrateNullHandling();
            await this.demonstrateFilterBuilding();
            this.demonstrateBestPractices();
            
            console.log('\n✅ Basic filters example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use equality (eq/ne) and comparison (gt/ge/lt/le) operators');
            console.log('- Combine filters with logical operators (and/or/not)');
            console.log('- Handle null values explicitly in your filters');
            console.log('- Build filters dynamically based on user input');
            console.log('- Validate filter syntax before executing queries');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new BasicFiltersExample();
    try {
        await example.run();
    } catch (error) {
        console.error(`Application failed: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = BasicFiltersExample;