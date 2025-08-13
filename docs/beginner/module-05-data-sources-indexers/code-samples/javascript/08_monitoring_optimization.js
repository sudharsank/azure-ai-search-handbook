/**
 * Monitoring and Optimization Example
 * 
 * This example demonstrates comprehensive monitoring, performance analysis,
 * and optimization strategies for Azure AI Search indexers.
 */

const { SearchIndexClient, SearchIndexerClient, SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

// Configuration
const SEARCH_ENDPOINT = process.env.SEARCH_ENDPOINT;
const SEARCH_API_KEY = process.env.SEARCH_API_KEY;
const SQL_CONNECTION_STRING = process.env.SQL_CONNECTION_STRING;

// Resource names
const DATA_SOURCE_NAME = 'monitoring-datasource';
const INDEX_NAME = 'monitoring-index';
const INDEXER_NAME = 'monitoring-indexer';

class MonitoringOptimizationExample {
    constructor() {
        this.validateConfiguration();
        
        const credential = new AzureKeyCredential(SEARCH_API_KEY);
        this.indexClient = new SearchIndexClient(SEARCH_ENDPOINT, credential);
        this.indexerClient = new SearchIndexerClient(SEARCH_ENDPOINT, credential);
        this.searchClient = new SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential);
        
        // Performance tracking
        this.performanceMetrics = [];
        this.executionHistory = [];
        this.optimizationRecommendations = [];
    }

    validateConfiguration() {
        if (!SEARCH_ENDPOINT || !SEARCH_API_KEY) {
            throw new Error('Missing required search service configuration.');
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${SEARCH_ENDPOINT}`);
        console.log(`🗃️ Data Source: ${DATA_SOURCE_NAME}`);
        console.log(`📊 Index: ${INDEX_NAME}`);
        console.log(`⚙️ Indexer: ${INDEXER_NAME}`);
    }

    demonstrateMonitoringMetrics() {
        console.log('\n📊 Key Monitoring Metrics');
        console.log('='.repeat(30));

        const metricCategories = [
            {
                category: 'Performance Metrics',
                metrics: [
                    {
                        name: 'Execution Duration',
                        description: 'Total time for indexer run',
                        importance: 'High',
                        target: '< 30 minutes for typical workloads',
                        calculation: 'endTime - startTime'
                    },
                    {
                        name: 'Processing Rate',
                        description: 'Documents processed per second',
                        importance: 'High',
                        target: '> 10 docs/sec for structured data',
                        calculation: 'itemCount / duration'
                    },
                    {
                        name: 'Throughput',
                        description: 'Data volume processed per hour',
                        importance: 'Medium',
                        target: 'Varies by data size and complexity',
                        calculation: 'totalDataSize / duration'
                    }
                ]
            },
            {
                category: 'Quality Metrics',
                metrics: [
                    {
                        name: 'Success Rate',
                        description: 'Percentage of successfully processed items',
                        importance: 'Critical',
                        target: '> 95%',
                        calculation: '(itemCount - failedItemCount) / itemCount * 100'
                    },
                    {
                        name: 'Error Rate',
                        description: 'Percentage of failed items',
                        importance: 'Critical',
                        target: '< 5%',
                        calculation: 'failedItemCount / itemCount * 100'
                    },
                    {
                        name: 'Warning Count',
                        description: 'Number of processing warnings',
                        importance: 'Medium',
                        target: 'Minimize warnings',
                        calculation: 'warnings.length'
                    }
                ]
            },
            {
                category: 'Resource Metrics',
                metrics: [
                    {
                        name: 'Memory Usage',
                        description: 'Peak memory consumption',
                        importance: 'Medium',
                        target: 'Within service limits',
                        calculation: 'Monitor via Azure portal'
                    },
                    {
                        name: 'Search Unit Consumption',
                        description: 'Search units used during indexing',
                        importance: 'High',
                        target: 'Optimize for cost efficiency',
                        calculation: 'Monitor via Azure portal'
                    },
                    {
                        name: 'Storage Usage',
                        description: 'Index storage consumption',
                        importance: 'Medium',
                        target: 'Within storage limits',
                        calculation: 'Monitor index size growth'
                    }
                ]
            }
        ];

        metricCategories.forEach(category => {
            console.log(`\n📋 ${category.category}:`);
            category.metrics.forEach(metric => {
                console.log(`\n   📊 ${metric.name}`);
                console.log(`      Description: ${metric.description}`);
                console.log(`      Importance: ${metric.importance}`);
                console.log(`      Target: ${metric.target}`);
                console.log(`      Calculation: ${metric.calculation}`);
            });
        });
    }

    async createOptimizedDataSource() {
        console.log('\n🔗 Creating optimized data source...');

        if (!SQL_CONNECTION_STRING) {
            console.log('⚠️ SQL connection not available, creating mock configuration');
            return null;
        }

        const dataSource = {
            name: DATA_SOURCE_NAME,
            type: 'azuresql',
            connectionString: SQL_CONNECTION_STRING,
            container: { 
                name: 'Hotels',
                // Optimized query for better performance
                query: `
                    SELECT 
                        id, hotel_name, description, category, rating, 
                        last_modified, created_date
                    FROM Hotels 
                    WHERE last_modified >= @HighWaterMark 
                    ORDER BY last_modified ASC
                `
            },
            dataChangeDetectionPolicy: {
                '@odata.type': '#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy',
                highWaterMarkColumnName: 'last_modified'
            },
            description: 'Optimized SQL data source with efficient change detection'
        };

        try {
            const result = await this.indexerClient.createOrUpdateDataSourceConnection(dataSource);
            console.log(`✅ Optimized data source '${DATA_SOURCE_NAME}' created`);
            console.log(`   Query optimization: Custom SELECT with ORDER BY`);
            console.log(`   Change detection: High water mark on indexed column`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating data source: ${error.message}`);
            throw error;
        }
    }

    async createOptimizedIndex() {
        console.log('\n📊 Creating performance-optimized index...');

        const fields = [
            // Key field - not searchable for better performance
            { name: 'id', type: 'Edm.String', key: true, searchable: false },
            
            // Searchable fields with appropriate analyzers
            { name: 'hotelName', type: 'Edm.String', searchable: true, sortable: true, analyzer: 'standard.lucene' },
            { name: 'description', type: 'Edm.String', searchable: true, analyzer: 'en.lucene' },
            
            // Filterable/facetable fields for efficient queries
            { name: 'category', type: 'Edm.String', filterable: true, facetable: true, searchable: false },
            { name: 'rating', type: 'Edm.Double', filterable: true, sortable: true, facetable: true },
            
            // Date fields for time-based filtering
            { name: 'lastModified', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: 'createdDate', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            
            // Performance monitoring fields
            { name: 'indexingDuration', type: 'Edm.Int32', filterable: true, sortable: true },
            { name: 'processingTimestamp', type: 'Edm.DateTimeOffset', filterable: true, sortable: true }
        ];

        const index = { 
            name: INDEX_NAME, 
            fields,
            // Optimize for search performance
            defaultScoringProfile: null, // Use default scoring for better performance
            corsOptions: null // Disable CORS if not needed
        };

        try {
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Optimized index '${INDEX_NAME}' created`);
            console.log(`   Total Fields: ${result.fields.length}`);
            console.log(`   Optimization: Minimal searchable fields, appropriate analyzers`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating index: ${error.message}`);
            throw error;
        }
    }

    async createOptimizedIndexer() {
        console.log('\n⚙️ Creating performance-optimized indexer...');

        const indexer = {
            name: INDEXER_NAME,
            dataSourceName: DATA_SOURCE_NAME,
            targetIndexName: INDEX_NAME,
            description: 'Performance-optimized indexer with monitoring',
            parameters: {
                // Optimized batch size based on document complexity
                batchSize: 100, // Start with moderate batch size
                maxFailedItems: 10,
                maxFailedItemsPerBatch: 5,
                
                configuration: {
                    parsingMode: 'default',
                    // Optimize for performance
                    failOnUnsupportedContentType: false,
                    failOnUnprocessableDocument: false
                }
            },
            fieldMappings: [
                { sourceFieldName: 'id', targetFieldName: 'id' },
                { sourceFieldName: 'hotel_name', targetFieldName: 'hotelName' },
                { sourceFieldName: 'description', targetFieldName: 'description' },
                { sourceFieldName: 'category', targetFieldName: 'category' },
                { sourceFieldName: 'rating', targetFieldName: 'rating' },
                { sourceFieldName: 'last_modified', targetFieldName: 'lastModified' },
                { sourceFieldName: 'created_date', targetFieldName: 'createdDate' }
            ]
        };

        try {
            const result = await this.indexerClient.createOrUpdateIndexer(indexer);
            console.log(`✅ Optimized indexer '${INDEXER_NAME}' created`);
            console.log(`   Batch Size: ${result.parameters?.batchSize}`);
            console.log(`   Field Mappings: ${result.fieldMappings?.length}`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating indexer: ${error.message}`);
            throw error;
        }
    }

    async runPerformanceAnalysis() {
        console.log('\n🔬 Running Performance Analysis');
        console.log('='.repeat(35));

        const testConfigurations = [
            { batchSize: 50, description: 'Small batch size' },
            { batchSize: 100, description: 'Medium batch size' },
            { batchSize: 200, description: 'Large batch size' }
        ];

        for (const config of testConfigurations) {
            console.log(`\n📊 Testing ${config.description} (${config.batchSize})...`);
            
            try {
                // Update indexer with test configuration
                const indexer = await this.indexerClient.getIndexer(INDEXER_NAME);
                const testIndexer = {
                    ...indexer,
                    parameters: {
                        ...indexer.parameters,
                        batchSize: config.batchSize
                    }
                };

                await this.indexerClient.createOrUpdateIndexer(testIndexer);
                
                // Run and measure performance
                const metrics = await this.measureIndexerPerformance(INDEXER_NAME, config);
                this.performanceMetrics.push(metrics);
                
                console.log(`   ✅ Completed: ${metrics.duration}s, ${metrics.rate.toFixed(2)} docs/sec`);
                
            } catch (error) {
                console.log(`   ❌ Test failed: ${error.message}`);
            }
        }

        this.analyzePerformanceResults();
    }

    async measureIndexerPerformance(indexerName, config) {
        const startTime = Date.now();
        
        try {
            // Reset indexer to ensure clean run
            await this.indexerClient.resetIndexer(indexerName);
            await this.sleep(2000);
            
            // Start indexer
            await this.indexerClient.runIndexer(indexerName);
            
            // Monitor execution
            let status;
            let itemCount = 0;
            let duration = 0;
            
            while (true) {
                status = await this.indexerClient.getIndexerStatus(indexerName);
                
                if (status.status === 'success' || status.status === 'error') {
                    if (status.lastResult) {
                        itemCount = status.lastResult.itemCount || 0;
                        const execStart = new Date(status.lastResult.startTime);
                        const execEnd = new Date(status.lastResult.endTime);
                        duration = (execEnd - execStart) / 1000;
                    }
                    break;
                }
                
                await this.sleep(5000);
                
                // Timeout after 10 minutes
                if (Date.now() - startTime > 10 * 60 * 1000) {
                    throw new Error('Performance test timeout');
                }
            }
            
            const metrics = {
                config: config,
                itemCount: itemCount,
                duration: duration,
                rate: duration > 0 ? itemCount / duration : 0,
                status: status.status,
                errors: status.lastResult?.failedItemCount || 0,
                timestamp: new Date().toISOString()
            };
            
            return metrics;
            
        } catch (error) {
            return {
                config: config,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    analyzePerformanceResults() {
        console.log('\n📈 Performance Analysis Results');
        console.log('='.repeat(35));

        if (this.performanceMetrics.length === 0) {
            console.log('No performance data collected');
            return;
        }

        // Find best performing configuration
        const validMetrics = this.performanceMetrics.filter(m => !m.error && m.rate > 0);
        
        if (validMetrics.length === 0) {
            console.log('No valid performance metrics collected');
            return;
        }

        const bestPerformance = validMetrics.reduce((best, current) => 
            current.rate > best.rate ? current : best
        );

        console.log('\n🏆 Best Performance Configuration:');
        console.log(`   Batch Size: ${bestPerformance.config.batchSize}`);
        console.log(`   Processing Rate: ${bestPerformance.rate.toFixed(2)} docs/sec`);
        console.log(`   Duration: ${bestPerformance.duration}s`);
        console.log(`   Items Processed: ${bestPerformance.itemCount}`);

        // Performance comparison
        console.log('\n📊 Performance Comparison:');
        validMetrics.forEach(metric => {
            const efficiency = (metric.rate / bestPerformance.rate * 100).toFixed(1);
            console.log(`   Batch ${metric.config.batchSize}: ${metric.rate.toFixed(2)} docs/sec (${efficiency}% of best)`);
        });

        // Generate recommendations
        this.generateOptimizationRecommendations(validMetrics);
    }

    generateOptimizationRecommendations(metrics) {
        console.log('\n💡 Optimization Recommendations');
        console.log('='.repeat(35));

        const recommendations = [];

        // Batch size recommendations
        const avgRate = metrics.reduce((sum, m) => sum + m.rate, 0) / metrics.length;
        const bestRate = Math.max(...metrics.map(m => m.rate));
        
        if (bestRate > avgRate * 1.2) {
            const bestConfig = metrics.find(m => m.rate === bestRate);
            recommendations.push({
                category: 'Batch Size',
                recommendation: `Use batch size of ${bestConfig.config.batchSize} for optimal performance`,
                impact: 'High',
                effort: 'Low'
            });
        }

        // Error rate recommendations
        const highErrorMetrics = metrics.filter(m => m.errors > 0);
        if (highErrorMetrics.length > 0) {
            recommendations.push({
                category: 'Error Handling',
                recommendation: 'Investigate and resolve indexing errors to improve throughput',
                impact: 'Medium',
                effort: 'Medium'
            });
        }

        // Duration-based recommendations
        const longRunningMetrics = metrics.filter(m => m.duration > 300); // 5 minutes
        if (longRunningMetrics.length > 0) {
            recommendations.push({
                category: 'Performance',
                recommendation: 'Consider implementing incremental indexing or data source optimization',
                impact: 'High',
                effort: 'High'
            });
        }

        // General recommendations
        recommendations.push(
            {
                category: 'Monitoring',
                recommendation: 'Implement automated performance monitoring and alerting',
                impact: 'Medium',
                effort: 'Medium'
            },
            {
                category: 'Scheduling',
                recommendation: 'Schedule indexer runs during off-peak hours for better resource utilization',
                impact: 'Low',
                effort: 'Low'
            }
        );

        this.optimizationRecommendations = recommendations;

        recommendations.forEach(rec => {
            console.log(`\n📋 ${rec.category}:`);
            console.log(`   Recommendation: ${rec.recommendation}`);
            console.log(`   Impact: ${rec.impact}`);
            console.log(`   Effort: ${rec.effort}`);
        });
    }

    async implementHealthChecks() {
        console.log('\n🏥 Implementing Health Checks');
        console.log('='.repeat(30));

        const healthChecks = [
            {
                name: 'Indexer Status Check',
                check: async () => {
                    try {
                        const status = await this.indexerClient.getIndexerStatus(INDEXER_NAME);
                        return {
                            healthy: status.status !== 'error',
                            status: status.status,
                            lastRun: status.lastResult?.startTime,
                            details: `Status: ${status.status}`
                        };
                    } catch (error) {
                        return {
                            healthy: false,
                            error: error.message,
                            details: 'Failed to get indexer status'
                        };
                    }
                }
            },
            {
                name: 'Data Source Connectivity',
                check: async () => {
                    try {
                        const dataSource = await this.indexerClient.getDataSourceConnection(DATA_SOURCE_NAME);
                        return {
                            healthy: true,
                            details: `Data source '${dataSource.name}' is accessible`
                        };
                    } catch (error) {
                        return {
                            healthy: false,
                            error: error.message,
                            details: 'Data source connectivity issue'
                        };
                    }
                }
            },
            {
                name: 'Index Health Check',
                check: async () => {
                    try {
                        const index = await this.indexClient.getIndex(INDEX_NAME);
                        const stats = await this.searchClient.getDocumentsCount();
                        return {
                            healthy: true,
                            documentCount: stats,
                            details: `Index '${index.name}' contains ${stats} documents`
                        };
                    } catch (error) {
                        return {
                            healthy: false,
                            error: error.message,
                            details: 'Index health check failed'
                        };
                    }
                }
            }
        ];

        console.log('Running health checks...');
        
        for (const healthCheck of healthChecks) {
            console.log(`\n🔍 ${healthCheck.name}:`);
            try {
                const result = await healthCheck.check();
                
                if (result.healthy) {
                    console.log(`   ✅ Healthy: ${result.details}`);
                    if (result.documentCount !== undefined) {
                        console.log(`   📊 Document Count: ${result.documentCount}`);
                    }
                } else {
                    console.log(`   ❌ Unhealthy: ${result.details}`);
                    if (result.error) {
                        console.log(`   Error: ${result.error}`);
                    }
                }
            } catch (error) {
                console.log(`   ❌ Health check failed: ${error.message}`);
            }
        }
    }

    async monitorResourceUsage() {
        console.log('\n📊 Resource Usage Monitoring');
        console.log('='.repeat(30));

        console.log('Resource monitoring includes:');
        console.log('• Search unit consumption during indexing');
        console.log('• Storage usage growth over time');
        console.log('• Memory and CPU utilization patterns');
        console.log('• Network bandwidth usage');
        console.log('• Query performance impact during indexing');

        // Simulate resource usage data
        const resourceMetrics = {
            searchUnits: {
                current: 85,
                limit: 100,
                trend: 'stable'
            },
            storage: {
                used: '2.3 GB',
                limit: '25 GB',
                growth: '+150 MB/day'
            },
            indexingImpact: {
                queryLatency: '+15ms during indexing',
                throughput: '-5% during peak indexing'
            }
        };

        console.log('\n📈 Current Resource Usage:');
        console.log(`   Search Units: ${resourceMetrics.searchUnits.current}/${resourceMetrics.searchUnits.limit} (${resourceMetrics.searchUnits.trend})`);
        console.log(`   Storage: ${resourceMetrics.storage.used}/${resourceMetrics.storage.limit} (${resourceMetrics.storage.growth})`);
        console.log(`   Query Impact: ${resourceMetrics.indexingImpact.queryLatency}, ${resourceMetrics.indexingImpact.throughput}`);

        // Resource optimization suggestions
        console.log('\n💡 Resource Optimization Suggestions:');
        if (resourceMetrics.searchUnits.current > 80) {
            console.log('   ⚠️ High search unit usage - consider optimizing indexer schedules');
        }
        if (resourceMetrics.storage.growth.includes('+')) {
            console.log('   📈 Storage growing - monitor for unexpected growth patterns');
        }
        console.log('   🕐 Schedule heavy indexing during off-peak hours');
        console.log('   🔄 Use incremental indexing to reduce resource consumption');
    }

    demonstrateOptimizationStrategies() {
        console.log('\n🚀 Optimization Strategies');
        console.log('='.repeat(25));

        const strategies = [
            {
                category: 'Data Source Optimization',
                strategies: [
                    'Use efficient queries with proper WHERE clauses',
                    'Index columns used in change detection',
                    'Optimize database query performance',
                    'Consider data source partitioning for large datasets'
                ]
            },
            {
                category: 'Indexer Configuration',
                strategies: [
                    'Tune batch size based on document complexity',
                    'Use appropriate error thresholds',
                    'Optimize field mappings and transformations',
                    'Enable only necessary features'
                ]
            },
            {
                category: 'Index Design',
                strategies: [
                    'Minimize searchable fields where possible',
                    'Use appropriate analyzers for each field',
                    'Avoid unnecessary sortable/facetable attributes',
                    'Consider field storage requirements'
                ]
            },
            {
                category: 'Scheduling and Resource Management',
                strategies: [
                    'Schedule indexing during off-peak hours',
                    'Stagger multiple indexer schedules',
                    'Monitor and adjust based on usage patterns',
                    'Use incremental indexing when possible'
                ]
            }
        ];

        strategies.forEach(category => {
            console.log(`\n📋 ${category.category}:`);
            category.strategies.forEach(strategy => {
                console.log(`   • ${strategy}`);
            });
        });
    }

    generatePerformanceReport() {
        console.log('\n📄 Performance Report Summary');
        console.log('='.repeat(30));

        const report = {
            timestamp: new Date().toISOString(),
            testResults: this.performanceMetrics.length,
            recommendations: this.optimizationRecommendations.length,
            bestConfiguration: this.performanceMetrics.length > 0 ? 
                this.performanceMetrics.reduce((best, current) => 
                    (current.rate || 0) > (best.rate || 0) ? current : best
                ) : null
        };

        console.log(`Report Generated: ${report.timestamp}`);
        console.log(`Performance Tests: ${report.testResults}`);
        console.log(`Optimization Recommendations: ${report.recommendations}`);

        if (report.bestConfiguration) {
            console.log(`Best Performance: ${report.bestConfiguration.rate?.toFixed(2) || 'N/A'} docs/sec`);
            console.log(`Optimal Batch Size: ${report.bestConfiguration.config?.batchSize || 'N/A'}`);
        }

        console.log('\n📊 Key Metrics to Monitor:');
        console.log('   • Processing rate (docs/sec)');
        console.log('   • Error rate (%)');
        console.log('   • Execution duration');
        console.log('   • Resource utilization');
        console.log('   • Query performance impact');

        return report;
    }

    async cleanup() {
        console.log('\n🧹 Cleaning up resources...');
        
        try {
            await this.indexerClient.deleteIndexer(INDEXER_NAME);
            console.log(`   ✅ Deleted indexer: ${INDEXER_NAME}`);
        } catch (error) {
            console.log(`   ⚠️ Warning deleting indexer: ${error.message}`);
        }

        try {
            await this.indexClient.deleteIndex(INDEX_NAME);
            console.log(`   ✅ Deleted index: ${INDEX_NAME}`);
        } catch (error) {
            console.log(`   ⚠️ Warning deleting index: ${error.message}`);
        }

        try {
            await this.indexerClient.deleteDataSourceConnection(DATA_SOURCE_NAME);
            console.log(`   ✅ Deleted data source: ${DATA_SOURCE_NAME}`);
        } catch (error) {
            console.log(`   ⚠️ Warning deleting data source: ${error.message}`);
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async run() {
        console.log('🚀 Monitoring and Optimization Example');
        console.log('='.repeat(50));

        try {
            // Demonstrate monitoring concepts
            this.demonstrateMonitoringMetrics();

            // Create optimized resources
            const dataSource = await this.createOptimizedDataSource();
            const index = await this.createOptimizedIndex();
            
            if (dataSource) {
                const indexer = await this.createOptimizedIndexer();
                
                // Run performance analysis
                await this.runPerformanceAnalysis();
                
                // Implement health checks
                await this.implementHealthChecks();
                
                // Monitor resource usage
                await this.monitorResourceUsage();
            } else {
                console.log('\n⚠️ Skipping performance tests due to missing data source');
            }

            // Optimization strategies and reporting
            this.demonstrateOptimizationStrategies();
            const report = this.generatePerformanceReport();

            console.log('\n✅ Monitoring and optimization example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Monitor key performance metrics regularly');
            console.log('- Test different configurations to find optimal settings');
            console.log('- Implement automated health checks and alerting');
            console.log('- Optimize based on actual usage patterns');
            console.log('- Balance performance with resource costs');

            await this.cleanup();

        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new MonitoringOptimizationExample();
    try {
        await example.run();
    } catch (error) {
        console.error('Application failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = MonitoringOptimizationExample;