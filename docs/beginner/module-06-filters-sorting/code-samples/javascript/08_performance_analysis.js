/**
 * Performance Analysis Example
 * 
 * This example demonstrates performance analysis and optimization techniques
 * for filtering and sorting operations in Azure AI Search.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class PerformanceAnalysisExample {
    constructor() {
        this.validateConfiguration();
        
        // Initialize search client
        const credential = new AzureKeyCredential(process.env.SEARCH_API_KEY);
        this.searchClient = new SearchClient(
            process.env.SEARCH_ENDPOINT,
            process.env.INDEX_NAME,
            credential
        );
        
        this.performanceMetrics = [];
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

    async measureQueryPerformance(queryName, searchOptions, iterations = 3) {
        /**
         * Measure query performance over multiple iterations
         * @param {string} queryName - Name for the query being tested
         * @param {Object} searchOptions - Search options to test
         * @param {number} iterations - Number of iterations to run
         * @returns {Object} Performance metrics
         */
        const times = [];
        let totalResults = 0;
        
        console.log(`\n⏱️ Testing: ${queryName}`);
        console.log(`   Iterations: ${iterations}`);
        
        for (let i = 0; i < iterations; i++) {
            const startTime = Date.now();
            
            try {
                const searchResults = await this.searchClient.search(
                    searchOptions.searchText || '*',
                    searchOptions
                );
                
                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }
                
                const endTime = Date.now();
                const duration = endTime - startTime;
                times.push(duration);
                
                if (i === 0) {
                    totalResults = results.length;
                }
                
                console.log(`   Run ${i + 1}: ${duration}ms (${results.length} results)`);
                
            } catch (error) {
                console.log(`   Run ${i + 1}: Error - ${error.message}`);
                times.push(null);
            }
        }
        
        const validTimes = times.filter(t => t !== null);
        const avgTime = validTimes.length > 0 ? 
            validTimes.reduce((a, b) => a + b, 0) / validTimes.length : 0;
        const minTime = validTimes.length > 0 ? Math.min(...validTimes) : 0;
        const maxTime = validTimes.length > 0 ? Math.max(...validTimes) : 0;
        
        const metrics = {
            queryName,
            avgTime: Math.round(avgTime),
            minTime,
            maxTime,
            totalResults,
            successfulRuns: validTimes.length,
            totalRuns: iterations
        };
        
        this.performanceMetrics.push(metrics);
        
        console.log(`   Average: ${metrics.avgTime}ms, Min: ${minTime}ms, Max: ${maxTime}ms`);
        console.log(`   Results: ${totalResults}, Success Rate: ${validTimes.length}/${iterations}`);
        
        return metrics;
    }

    async demonstrateFilterPerformanceComparison() {
        console.log('\n🏁 Filter Performance Comparison');
        console.log('='.repeat(50));
        
        const filterTests = [
            {
                name: 'Simple equality filter',
                searchOptions: {
                    filter: "category eq 'Electronics'",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Range filter',
                searchOptions: {
                    filter: "price ge 100 and price le 500",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'String function filter',
                searchOptions: {
                    filter: "startswith(name, 'iPhone')",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Complex logical filter',
                searchOptions: {
                    filter: "(category eq 'Electronics' and price gt 200) or (category eq 'Books' and rating ge 4.0)",
                    top: 50,
                    select: ['id', 'name', 'category', 'price', 'rating']
                }
            },
            {
                name: 'Collection filter',
                searchOptions: {
                    filter: "tags/any(t: t eq 'featured' or t eq 'bestseller')",
                    top: 50,
                    select: ['id', 'name', 'tags', 'category', 'price']
                }
            }
        ];

        for (const test of filterTests) {
            await this.measureQueryPerformance(test.name, test.searchOptions);
        }
    }

    async demonstrateSortingPerformanceComparison() {
        console.log('\n📊 Sorting Performance Comparison');
        console.log('='.repeat(50));
        
        const sortTests = [
            {
                name: 'No sorting (relevance)',
                searchOptions: {
                    searchText: 'electronics',
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Single field sort (price)',
                searchOptions: {
                    searchText: 'electronics',
                    orderBy: ['price asc'],
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Multi-field sort',
                searchOptions: {
                    searchText: 'electronics',
                    orderBy: ['category asc', 'price desc'],
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Geographic sort',
                searchOptions: {
                    searchText: 'store',
                    orderBy: ["geo.distance(location, geography'POINT(-122.335167 47.608013)')"],
                    filter: 'location ne null',
                    top: 50,
                    select: ['id', 'name', 'location', 'category']
                }
            }
        ];

        for (const test of sortTests) {
            await this.measureQueryPerformance(test.name, test.searchOptions);
        }
    }

    async demonstrateResultSetSizeImpact() {
        console.log('\n📈 Result Set Size Impact');
        console.log('='.repeat(50));
        
        const resultSizeTests = [
            {
                name: 'Small result set (top 10)',
                searchOptions: {
                    filter: "category eq 'Electronics'",
                    top: 10,
                    select: ['id', 'name', 'price']
                }
            },
            {
                name: 'Medium result set (top 50)',
                searchOptions: {
                    filter: "category eq 'Electronics'",
                    top: 50,
                    select: ['id', 'name', 'price']
                }
            },
            {
                name: 'Large result set (top 100)',
                searchOptions: {
                    filter: "category eq 'Electronics'",
                    top: 100,
                    select: ['id', 'name', 'price']
                }
            },
            {
                name: 'All fields vs selected fields (top 50)',
                searchOptions: {
                    filter: "category eq 'Electronics'",
                    top: 50
                    // No select - returns all fields
                }
            }
        ];

        for (const test of resultSizeTests) {
            await this.measureQueryPerformance(test.name, test.searchOptions);
        }
    }

    async demonstrateFilterOptimizationTechniques() {
        console.log('\n⚡ Filter Optimization Techniques');
        console.log('='.repeat(50));
        
        const optimizationTests = [
            {
                name: 'Unoptimized: Complex filter first',
                searchOptions: {
                    filter: "contains(description, 'wireless') and category eq 'Electronics' and price gt 100",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Optimized: Selective filter first',
                searchOptions: {
                    filter: "category eq 'Electronics' and price gt 100 and contains(description, 'wireless')",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Unoptimized: Multiple OR conditions',
                searchOptions: {
                    filter: "category eq 'Electronics' or category eq 'Computers' or category eq 'Phones' or category eq 'Tablets'",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            },
            {
                name: 'Optimized: Using search.in function',
                searchOptions: {
                    filter: "search.in(category, 'Electronics,Computers,Phones,Tablets', ',')",
                    top: 50,
                    select: ['id', 'name', 'category', 'price']
                }
            }
        ];

        for (const test of optimizationTests) {
            await this.measureQueryPerformance(test.name, test.searchOptions);
        }
    }

    async demonstrateCachingEffects() {
        console.log('\n🗄️ Caching Effects Analysis');
        console.log('='.repeat(50));
        
        const cacheTest = {
            name: 'Repeated query (cache test)',
            searchOptions: {
                filter: "category eq 'Electronics' and price gt 100",
                top: 50,
                select: ['id', 'name', 'category', 'price']
            }
        };

        // Run the same query multiple times to see caching effects
        await this.measureQueryPerformance(cacheTest.name, cacheTest.searchOptions, 5);
    }

    analyzePerformanceResults() {
        console.log('\n📊 Performance Analysis Summary');
        console.log('='.repeat(50));
        
        if (this.performanceMetrics.length === 0) {
            console.log('No performance metrics collected.');
            return;
        }

        // Sort by average time
        const sortedMetrics = [...this.performanceMetrics].sort((a, b) => a.avgTime - b.avgTime);
        
        console.log('\n🏆 Query Performance Ranking (fastest to slowest):');
        sortedMetrics.forEach((metric, index) => {
            const rank = index + 1;
            const emoji = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '📊';
            console.log(`${emoji} ${rank}. ${metric.queryName}`);
            console.log(`     Average: ${metric.avgTime}ms, Results: ${metric.totalResults}`);
        });

        // Performance insights
        console.log('\n💡 Performance Insights:');
        
        const fastest = sortedMetrics[0];
        const slowest = sortedMetrics[sortedMetrics.length - 1];
        
        console.log(`   Fastest Query: ${fastest.queryName} (${fastest.avgTime}ms)`);
        console.log(`   Slowest Query: ${slowest.queryName} (${slowest.avgTime}ms)`);
        
        if (slowest.avgTime > 0) {
            const speedDifference = ((slowest.avgTime - fastest.avgTime) / fastest.avgTime * 100).toFixed(1);
            console.log(`   Performance Gap: ${speedDifference}% slower`);
        }

        // Identify patterns
        const filterQueries = sortedMetrics.filter(m => m.queryName.toLowerCase().includes('filter'));
        const sortQueries = sortedMetrics.filter(m => m.queryName.toLowerCase().includes('sort'));
        
        if (filterQueries.length > 1) {
            const avgFilterTime = filterQueries.reduce((sum, m) => sum + m.avgTime, 0) / filterQueries.length;
            console.log(`   Average Filter Query Time: ${Math.round(avgFilterTime)}ms`);
        }
        
        if (sortQueries.length > 1) {
            const avgSortTime = sortQueries.reduce((sum, m) => sum + m.avgTime, 0) / sortQueries.length;
            console.log(`   Average Sort Query Time: ${Math.round(avgSortTime)}ms`);
        }
    }

    demonstratePerformanceBestPractices() {
        console.log('\n💡 Performance Best Practices');
        console.log('='.repeat(50));
        
        console.log('\n1. Filter Optimization');
        console.log('   ✅ Use most selective filters first');
        console.log('   ✅ Use equality filters before range filters');
        console.log('   ✅ Use simple filters before complex ones');
        console.log('   ✅ Use search.in() instead of multiple OR conditions');
        console.log('   ❌ Avoid complex string functions as primary filters');
        
        console.log('\n2. Sorting Optimization');
        console.log('   ✅ Use numeric fields for sorting when possible');
        console.log('   ✅ Limit the number of sort criteria');
        console.log('   ✅ Use relevance scoring for text searches');
        console.log('   ❌ Avoid sorting on non-sortable fields');
        
        console.log('\n3. Result Set Management');
        console.log('   ✅ Use appropriate "top" values (don\'t over-fetch)');
        console.log('   ✅ Use "select" to limit returned fields');
        console.log('   ✅ Implement pagination for large result sets');
        console.log('   ❌ Don\'t return all fields if not needed');
        
        console.log('\n4. Index Design Considerations');
        console.log('   ✅ Mark only necessary fields as filterable/sortable');
        console.log('   ✅ Consider field data types for performance');
        console.log('   ✅ Use appropriate analyzers for text fields');
        console.log('   ⚠️ Balance functionality vs. storage/performance');
        
        console.log('\n5. Query Pattern Optimization');
        console.log('   ✅ Cache frequently used queries');
        console.log('   ✅ Use consistent query patterns');
        console.log('   ✅ Monitor query performance over time');
        console.log('   ✅ Test with realistic data volumes');
        
        console.log('\n6. Geographic Query Optimization');
        console.log('   ✅ Use appropriate distance ranges');
        console.log('   ✅ Combine geo filters with other selective filters');
        console.log('   ✅ Consider bounding box filters for rectangular areas');
        console.log('   ❌ Avoid very large distance calculations');
        
        console.log('\n7. Monitoring and Alerting');
        console.log('   ✅ Monitor average query response times');
        console.log('   ✅ Set up alerts for performance degradation');
        console.log('   ✅ Track query patterns and usage');
        console.log('   ✅ Regular performance testing with production data');
    }

    generatePerformanceReport() {
        console.log('\n📋 Performance Report');
        console.log('='.repeat(50));
        
        if (this.performanceMetrics.length === 0) {
            console.log('No performance data available for report.');
            return;
        }

        const report = {
            timestamp: new Date().toISOString(),
            totalQueries: this.performanceMetrics.length,
            metrics: this.performanceMetrics.map(m => ({
                query: m.queryName,
                avgResponseTime: m.avgTime,
                minResponseTime: m.minTime,
                maxResponseTime: m.maxTime,
                resultCount: m.totalResults,
                successRate: `${m.successfulRuns}/${m.totalRuns}`
            }))
        };

        console.log(JSON.stringify(report, null, 2));
        
        // Performance recommendations
        console.log('\n🎯 Recommendations:');
        
        const slowQueries = this.performanceMetrics.filter(m => m.avgTime > 1000);
        if (slowQueries.length > 0) {
            console.log(`   ⚠️ ${slowQueries.length} queries took over 1 second`);
            slowQueries.forEach(q => {
                console.log(`      - ${q.queryName}: ${q.avgTime}ms`);
            });
        }
        
        const highVariance = this.performanceMetrics.filter(m => 
            m.maxTime > 0 && (m.maxTime - m.minTime) / m.avgTime > 0.5
        );
        if (highVariance.length > 0) {
            console.log(`   ⚠️ ${highVariance.length} queries show high variance`);
            highVariance.forEach(q => {
                console.log(`      - ${q.queryName}: ${q.minTime}-${q.maxTime}ms range`);
            });
        }
        
        const fastQueries = this.performanceMetrics.filter(m => m.avgTime < 100);
        if (fastQueries.length > 0) {
            console.log(`   ✅ ${fastQueries.length} queries perform well (<100ms)`);
        }
    }

    async run() {
        console.log('🚀 Performance Analysis Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateFilterPerformanceComparison();
            await this.demonstrateSortingPerformanceComparison();
            await this.demonstrateResultSetSizeImpact();
            await this.demonstrateFilterOptimizationTechniques();
            await this.demonstrateCachingEffects();
            
            this.analyzePerformanceResults();
            this.demonstratePerformanceBestPractices();
            this.generatePerformanceReport();
            
            console.log('\n✅ Performance analysis example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Measure query performance to identify bottlenecks');
            console.log('- Optimize filter order for better performance');
            console.log('- Use appropriate result set sizes and field selection');
            console.log('- Monitor performance trends over time');
            console.log('- Apply best practices for index design and query patterns');
            console.log('- Consider caching for frequently used queries');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new PerformanceAnalysisExample();
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

module.exports = PerformanceAnalysisExample;