/**
 * String Filters Example
 * 
 * This example demonstrates string filtering operations in Azure AI Search,
 * including exact matches, string functions, and pattern matching.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class StringFiltersExample {
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

    async demonstrateExactStringMatches() {
        console.log('\n🎯 Exact String Matches');
        console.log('='.repeat(40));

        const exactMatchExamples = [
            {
                name: 'Category equals Electronics',
                filter: "category eq 'Electronics'",
                description: 'Find items in Electronics category'
            },
            {
                name: 'Status not discontinued',
                filter: "status ne 'Discontinued'",
                description: 'Find items that are not discontinued'
            },
            {
                name: 'Brand equals Apple',
                filter: "brand eq 'Apple'",
                description: 'Find Apple products'
            },
            {
                name: 'Multiple category match',
                filter: "category eq 'Electronics' or category eq 'Books'",
                description: 'Find items in Electronics or Books categories'
            }
        ];

        for (const example of exactMatchExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);

            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'brand', 'status', 'price']
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
                    const status = result.status || 'N/A';
                    const price = result.price || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - ${brand} - ${status} - $${price}`);
                });

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateStringFunctions() {
        console.log('\n🔍 String Functions');
        console.log('='.repeat(40));

        const stringFunctionExamples = [
            {
                name: 'Names starting with iPhone',
                filter: "startswith(name, 'iPhone')",
                description: 'Find products with names starting with iPhone'
            },
            {
                name: 'Names ending with Pro',
                filter: "endswith(name, 'Pro')",
                description: 'Find products with names ending with Pro'
            },
            {
                name: 'Description contains wireless',
                filter: "contains(description, 'wireless')",
                description: 'Find products with wireless in description'
            },
            {
                name: 'Names containing Galaxy',
                filter: "contains(name, 'Galaxy')",
                description: 'Find products with Galaxy in the name'
            }
        ];

        for (const example of stringFunctionExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);

            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'description', 'category', 'price'],
                    orderBy: ['name asc']
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
                    const description = result.description ?
                        result.description.substring(0, 50) + '...' : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price}`);
                    console.log(`        Description: ${description}`);
                });

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateComplexStringPatterns() {
        console.log('\n🔗 Complex String Patterns');
        console.log('='.repeat(40));

        const complexPatternExamples = [
            {
                name: 'Samsung Galaxy products',
                filter: "startswith(name, 'Samsung') and contains(name, 'Galaxy')",
                description: 'Find Samsung products with Galaxy in the name'
            },
            {
                name: 'Apple Pro products',
                filter: "brand eq 'Apple' and endswith(name, 'Pro')",
                description: 'Find Apple products ending with Pro'
            },
            {
                name: 'Electronics with wireless features',
                filter: "category eq 'Electronics' and contains(description, 'wireless')",
                description: 'Find electronics with wireless capabilities'
            },
            {
                name: 'Premium brand products',
                filter: "(brand eq 'Apple' or brand eq 'Samsung') and category eq 'Electronics'",
                description: 'Find premium electronics from Apple or Samsung'
            }
        ];

        for (const example of complexPatternExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);

            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'brand', 'category', 'description', 'price']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);

                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const brand = result.brand || 'N/A';
                    const category = result.category || 'N/A';
                    const price = result.price || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${brand}) - ${category} - $${price}`);
                });

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateNullAndEmptyHandling() {
        console.log('\n🚫 Null and Empty String Handling');
        console.log('='.repeat(40));

        const nullHandlingExamples = [
            {
                name: 'Items with description',
                filter: "description ne null",
                description: 'Find items that have a description'
            },
            {
                name: 'Items without brand',
                filter: "brand eq null",
                description: 'Find items with no brand specified'
            },
            {
                name: 'Items with non-empty description',
                filter: "description ne null and description ne ''",
                description: 'Find items with meaningful descriptions'
            },
            {
                name: 'Items missing brand or description',
                filter: "brand eq null or description eq null",
                description: 'Find items with missing information'
            }
        ];

        for (const example of nullHandlingExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);

            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'brand', 'description', 'category']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);

                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const brand = result.brand || 'No Brand';
                    const category = result.category || 'N/A';
                    const hasDescription = result.description ? 'Yes' : 'No';
                    console.log(`     ${index + 1}. ${name} (${category}) - Brand: ${brand} - Desc: ${hasDescription}`);
                });

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateCollectionStringFilters() {
        console.log('\n📚 Collection String Filters');
        console.log('='.repeat(40));

        const collectionExamples = [
            {
                name: 'Items with featured tag',
                filter: "tags/any(t: t eq 'featured')",
                description: 'Find items tagged as featured'
            },
            {
                name: 'Items with wireless or bluetooth tags',
                filter: "tags/any(t: t eq 'wireless' or t eq 'bluetooth')",
                description: 'Find items with connectivity tags'
            },
            {
                name: 'Items with all required tags',
                filter: "tags/all(t: t ne null and t ne '')",
                description: 'Find items where all tags are meaningful'
            },
            {
                name: 'Items with premium tags',
                filter: "tags/any(t: contains(t, 'premium') or contains(t, 'luxury'))",
                description: 'Find items with premium-related tags'
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

    buildStringFilter(field, value, operation = 'eq', caseSensitive = true) {
        /**
         * Build a string filter expression
         * @param {string} field - Field name
         * @param {string} value - Value to filter by
         * @param {string} operation - Operation (eq, ne, startswith, endswith, contains)
         * @param {boolean} caseSensitive - Whether to be case sensitive
         * @returns {string} Filter expression
         */
        if (!caseSensitive) {
            // Note: Azure AI Search string comparisons are case-sensitive by default
            // For case-insensitive searches, you'd typically use full-text search instead
            console.warn('Case-insensitive string filtering requires full-text search features');
        }

        const escapedValue = value.replace(/'/g, "''"); // Escape single quotes

        switch (operation.toLowerCase()) {
            case 'eq':
                return `${field} eq '${escapedValue}'`;
            case 'ne':
                return `${field} ne '${escapedValue}'`;
            case 'startswith':
                return `startswith(${field}, '${escapedValue}')`;
            case 'endswith':
                return `endswith(${field}, '${escapedValue}')`;
            case 'contains':
                return `contains(${field}, '${escapedValue}')`;
            default:
                throw new Error(`Unsupported string operation: ${operation}`);
        }
    }

    async demonstrateDynamicStringFiltering() {
        console.log('\n🏗️ Dynamic String Filter Building');
        console.log('='.repeat(40));

        const filterScenarios = [
            {
                name: 'Exact brand match',
                field: 'brand',
                value: 'Apple',
                operation: 'eq'
            },
            {
                name: 'Name starts with pattern',
                field: 'name',
                value: 'iPhone',
                operation: 'startswith'
            },
            {
                name: 'Description contains keyword',
                field: 'description',
                value: 'wireless',
                operation: 'contains'
            },
            {
                name: 'Name ends with suffix',
                field: 'name',
                value: 'Pro',
                operation: 'endswith'
            }
        ];

        for (const scenario of filterScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            const filter = this.buildStringFilter(
                scenario.field,
                scenario.value,
                scenario.operation
            );

            console.log(`   Generated Filter: ${filter}`);
            console.log(`   Parameters: field=${scenario.field}, value="${scenario.value}", operation=${scenario.operation}`);

            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: filter,
                    top: 2,
                    select: ['id', 'name', scenario.field, 'category', 'price']
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
                    const fieldValue = result[scenario.field] || 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - $${price}`);
                    console.log(`        ${scenario.field}: ${fieldValue}`);
                });

            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    demonstrateStringFilterBestPractices() {
        console.log('\n💡 String Filter Best Practices');
        console.log('='.repeat(40));

        console.log('\n1. String Comparison Rules');
        console.log('   ✅ String comparisons are case-sensitive by default');
        console.log('   ✅ Use single quotes around string literals');
        console.log('   ✅ Escape single quotes by doubling them ("Alice\'s" → "Alice\'\'s")');

        console.log('\n2. String Functions');
        console.log('   ✅ startswith() - Efficient for prefix matching');
        console.log('   ✅ endswith() - Good for suffix matching');
        console.log('   ✅ contains() - Use for substring searches');
        console.log('   ❌ Avoid complex nested string functions');

        console.log('\n3. Null Handling');
        console.log('   ✅ Always check for null values explicitly');
        console.log('   ✅ Use "field ne null" to exclude nulls');
        console.log('   ✅ Use "field eq null" to find missing values');
        console.log('   ✅ Check for empty strings with "field ne \'\'"');

        console.log('\n4. Performance Tips');
        console.log('   ✅ Use exact matches (eq/ne) when possible');
        console.log('   ✅ Combine string filters with other filter types');
        console.log('   ✅ Use collection filters for array fields');
        console.log('   ❌ Avoid too many OR conditions with string functions');

        console.log('\n5. Common Patterns');
        console.log('   📱 Product names: startswith(name, "iPhone")');
        console.log('   🏷️ Categories: category eq "Electronics"');
        console.log('   🔍 Descriptions: contains(description, "wireless")');
        console.log('   🏢 Brands: brand eq "Apple" or brand eq "Samsung"');
        console.log('   📋 Tags: tags/any(t: t eq "featured")');

        console.log('\n6. Error Prevention');
        console.log('   ✅ Validate input strings before building filters');
        console.log('   ✅ Escape special characters properly');
        console.log('   ✅ Handle empty or null input gracefully');
        console.log('   ✅ Test filters with various string lengths');
    }

    async run() {
        console.log('🚀 String Filters Example');
        console.log('='.repeat(50));

        try {
            await this.demonstrateExactStringMatches();
            await this.demonstrateStringFunctions();
            await this.demonstrateComplexStringPatterns();
            await this.demonstrateNullAndEmptyHandling();
            await this.demonstrateCollectionStringFilters();
            await this.demonstrateDynamicStringFiltering();
            this.demonstrateStringFilterBestPractices();

            console.log('\n✅ String filters example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use exact matches (eq/ne) for precise filtering');
            console.log('- Leverage string functions (startswith, endswith, contains)');
            console.log('- Handle null and empty values explicitly');
            console.log('- Use collection filters for array fields');
            console.log('- Build dynamic filters based on user input');
            console.log('- Always escape special characters in string values');

        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new StringFiltersExample();
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

module.exports = StringFiltersExample;