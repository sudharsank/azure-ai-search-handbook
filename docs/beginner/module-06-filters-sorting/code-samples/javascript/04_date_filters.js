/**
 * Date Filters Example
 * 
 * This example demonstrates date and time filtering operations in Azure AI Search,
 * including date ranges, relative dates, and time zone handling.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class DateFiltersExample {
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

    async demonstrateBasicDateFilters() {
        console.log('\n📅 Basic Date Filters');
        console.log('='.repeat(40));
        
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
        const oneWeekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        const basicDateExamples = [
            {
                name: 'Items modified today',
                filter: `lastModified ge ${today.toISOString()}`,
                description: 'Find items modified today'
            },
            {
                name: 'Items modified yesterday',
                filter: `lastModified ge ${yesterday.toISOString()} and lastModified lt ${today.toISOString()}`,
                description: 'Find items modified yesterday'
            },
            {
                name: 'Items modified in last week',
                filter: `lastModified ge ${oneWeekAgo.toISOString()}`,
                description: 'Find items modified in the last 7 days'
            },
            {
                name: 'Items modified before this year',
                filter: `lastModified lt ${new Date(now.getFullYear(), 0, 1).toISOString()}`,
                description: 'Find items not modified this year'
            }
        ];

        for (const example of basicDateExamples) {
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
                        new Date(result.lastModified).toLocaleString() : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Modified: ${lastModified}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateDateRanges() {
        console.log('\n📊 Date Range Filters');
        console.log('='.repeat(40));
        
        const now = new Date();
        const currentYear = now.getFullYear();
        const lastYear = currentYear - 1;
        
        const dateRangeExamples = [
            {
                name: 'Items from current year',
                filter: `lastModified ge ${new Date(currentYear, 0, 1).toISOString()} and lastModified lt ${new Date(currentYear + 1, 0, 1).toISOString()}`,
                description: 'Find items modified this year'
            },
            {
                name: 'Items from last year',
                filter: `lastModified ge ${new Date(lastYear, 0, 1).toISOString()} and lastModified lt ${new Date(currentYear, 0, 1).toISOString()}`,
                description: 'Find items modified last year'
            },
            {
                name: 'Items from Q1 2024',
                filter: `lastModified ge 2024-01-01T00:00:00Z and lastModified lt 2024-04-01T00:00:00Z`,
                description: 'Find items modified in Q1 2024'
            },
            {
                name: 'Items from specific month',
                filter: `lastModified ge 2024-06-01T00:00:00Z and lastModified lt 2024-07-01T00:00:00Z`,
                description: 'Find items modified in June 2024'
            }
        ];

        for (const example of dateRangeExamples) {
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

    async demonstrateRelativeDateFilters() {
        console.log('\n⏰ Relative Date Filters');
        console.log('='.repeat(40));
        
        const now = new Date();
        const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
        const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        const relativeDateExamples = [
            {
                name: 'Items modified in last hour',
                filter: `lastModified ge ${oneHourAgo.toISOString()}`,
                description: 'Find very recently modified items'
            },
            {
                name: 'Items modified in last 24 hours',
                filter: `lastModified ge ${oneDayAgo.toISOString()}`,
                description: 'Find items modified in the last day'
            },
            {
                name: 'Items modified in last week',
                filter: `lastModified ge ${oneWeekAgo.toISOString()}`,
                description: 'Find items modified in the last 7 days'
            },
            {
                name: 'Items modified in last month',
                filter: `lastModified ge ${oneMonthAgo.toISOString()}`,
                description: 'Find items modified in the last 30 days'
            }
        ];

        for (const example of relativeDateExamples) {
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
                        new Date(result.lastModified).toLocaleString() : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Modified: ${lastModified}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateDateWithOtherFilters() {
        console.log('\n🔗 Date Filters Combined with Other Filters');
        console.log('='.repeat(40));
        
        const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        const oneMonthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        
        const combinedFilterExamples = [
            {
                name: 'Recent Electronics',
                filter: `category eq 'Electronics' and lastModified ge ${oneWeekAgo.toISOString()}`,
                description: 'Find electronics modified in the last week'
            },
            {
                name: 'Recent high-priced items',
                filter: `price gt 500 and lastModified ge ${oneMonthAgo.toISOString()}`,
                description: 'Find expensive items added/modified recently'
            },
            {
                name: 'Recent Apple products',
                filter: `brand eq 'Apple' and lastModified ge ${oneWeekAgo.toISOString()}`,
                description: 'Find Apple products modified recently'
            },
            {
                name: 'Old discontinued items',
                filter: `status eq 'Discontinued' and lastModified lt ${new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString()}`,
                description: 'Find items discontinued over a year ago'
            }
        ];

        for (const example of combinedFilterExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'brand', 'price', 'status', 'lastModified'],
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
                    const brand = result.brand || 'N/A';
                    const price = result.price || 'N/A';
                    const status = result.status || 'N/A';
                    const lastModified = result.lastModified ? 
                        new Date(result.lastModified).toLocaleDateString() : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - ${brand} - $${price} - ${status}`);
                    console.log(`        Modified: ${lastModified}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    buildDateFilter(field, startDate = null, endDate = null, includeStart = true, includeEnd = false) {
        /**
         * Build a date range filter
         * @param {string} field - Date field name
         * @param {Date|string} startDate - Start date (inclusive by default)
         * @param {Date|string} endDate - End date (exclusive by default)
         * @param {boolean} includeStart - Include start date (ge vs gt)
         * @param {boolean} includeEnd - Include end date (le vs lt)
         * @returns {string|null} Filter expression
         */
        const filters = [];
        
        if (startDate) {
            const startIso = startDate instanceof Date ? startDate.toISOString() : startDate;
            const operator = includeStart ? 'ge' : 'gt';
            filters.push(`${field} ${operator} ${startIso}`);
        }
        
        if (endDate) {
            const endIso = endDate instanceof Date ? endDate.toISOString() : endDate;
            const operator = includeEnd ? 'le' : 'lt';
            filters.push(`${field} ${operator} ${endIso}`);
        }
        
        return filters.length > 0 ? filters.join(' and ') : null;
    }

    getRelativeDate(days = 0, hours = 0, minutes = 0) {
        /**
         * Get a date relative to now
         * @param {number} days - Days to subtract (negative for past)
         * @param {number} hours - Hours to subtract
         * @param {number} minutes - Minutes to subtract
         * @returns {Date} Calculated date
         */
        const now = new Date();
        const totalMilliseconds = (days * 24 * 60 * 60 * 1000) + 
                                 (hours * 60 * 60 * 1000) + 
                                 (minutes * 60 * 1000);
        return new Date(now.getTime() - totalMilliseconds);
    }

    async demonstrateDynamicDateFiltering() {
        console.log('\n🏗️ Dynamic Date Filter Building');
        console.log('='.repeat(40));
        
        const dateScenarios = [
            {
                name: 'Last 7 days',
                startDate: this.getRelativeDate(7),
                endDate: null,
                description: 'Items modified in the last week'
            },
            {
                name: 'Specific month (June 2024)',
                startDate: new Date('2024-06-01T00:00:00Z'),
                endDate: new Date('2024-07-01T00:00:00Z'),
                description: 'Items from June 2024'
            },
            {
                name: 'Last 24 hours',
                startDate: this.getRelativeDate(1),
                endDate: null,
                description: 'Items modified in the last day'
            },
            {
                name: 'Before this year',
                startDate: null,
                endDate: new Date(new Date().getFullYear(), 0, 1),
                description: 'Items from previous years'
            }
        ];

        for (const scenario of dateScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            const filter = this.buildDateFilter('lastModified', scenario.startDate, scenario.endDate);
            
            console.log(`   Generated Filter: ${filter}`);
            console.log(`   Description: ${scenario.description}`);
            
            if (filter) {
                try {
                    const searchResults = await this.searchClient.search('*', {
                        filter: filter,
                        top: 2,
                        select: ['id', 'name', 'lastModified', 'category'],
                        orderBy: ['lastModified desc']
                    });

                    const results = [];
                    for await (const result of searchResults.results) {
                        results.push(result.document);
                    }

                    console.log(`   Results: ${results.length} items found`);
                    
                    results.forEach((result, index) => {
                        const name = result.name || 'N/A';
                        const category = result.category || 'N/A';
                        const lastModified = result.lastModified ? 
                            new Date(result.lastModified).toLocaleString() : 'N/A';
                        console.log(`     ${index + 1}. ${name} (${category}) - Modified: ${lastModified}`);
                    });
                    
                } catch (error) {
                    console.log(`   ❌ Error: ${error.message}`);
                }
            }
        }
    }

    demonstrateDateFilterBestPractices() {
        console.log('\n💡 Date Filter Best Practices');
        console.log('='.repeat(40));
        
        console.log('\n1. Date Format Requirements');
        console.log('   ✅ Use ISO 8601 format: 2024-12-25T10:30:00Z');
        console.log('   ✅ Include timezone information (Z for UTC)');
        console.log('   ✅ Use consistent date formats throughout');
        console.log('   ❌ Avoid locale-specific date formats');
        
        console.log('\n2. Time Zone Handling');
        console.log('   ✅ Store dates in UTC when possible');
        console.log('   ✅ Convert local times to UTC for filtering');
        console.log('   ✅ Be consistent with timezone handling');
        console.log('   ⚠️ Consider user timezone for relative dates');
        
        console.log('\n3. Range Filtering');
        console.log('   ✅ Use ge (>=) for start dates (inclusive)');
        console.log('   ✅ Use lt (<) for end dates (exclusive)');
        console.log('   ✅ This pattern: startDate <= value < endDate');
        console.log('   ❌ Avoid overlapping date ranges');
        
        console.log('\n4. Performance Optimization');
        console.log('   ✅ Use date ranges instead of exact matches');
        console.log('   ✅ Index date fields properly');
        console.log('   ✅ Combine date filters with other selective filters');
        console.log('   ❌ Avoid complex date calculations in filters');
        
        console.log('\n5. Common Date Patterns');
        console.log('   📅 Today: lastModified ge 2024-12-25T00:00:00Z');
        console.log('   📅 This week: lastModified ge 2024-12-18T00:00:00Z');
        console.log('   📅 This month: lastModified ge 2024-12-01T00:00:00Z');
        console.log('   📅 This year: lastModified ge 2024-01-01T00:00:00Z');
        console.log('   📅 Range: date ge start and date lt end');
        
        console.log('\n6. Error Prevention');
        console.log('   ✅ Validate date inputs before filtering');
        console.log('   ✅ Handle null date values appropriately');
        console.log('   ✅ Test with various date ranges');
        console.log('   ✅ Consider leap years and month boundaries');
    }

    async run() {
        console.log('🚀 Date Filters Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateBasicDateFilters();
            await this.demonstrateDateRanges();
            await this.demonstrateRelativeDateFilters();
            await this.demonstrateDateWithOtherFilters();
            await this.demonstrateDynamicDateFiltering();
            this.demonstrateDateFilterBestPractices();
            
            console.log('\n✅ Date filters example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use ISO 8601 format for all date values');
            console.log('- Handle timezones consistently (prefer UTC)');
            console.log('- Use inclusive start dates (ge) and exclusive end dates (lt)');
            console.log('- Combine date filters with other criteria for better performance');
            console.log('- Build dynamic date filters for relative time periods');
            console.log('- Always validate date inputs and handle edge cases');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new DateFiltersExample();
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

module.exports = DateFiltersExample;