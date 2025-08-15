/**
 * Module 7: Pagination & Result Shaping - Search Scores Analysis
 * Azure AI Search JavaScript SDK Example
 * 
 * This example demonstrates how to work with search scores and relevance in Azure AI Search,
 * including score analysis, custom scoring, and relevance optimization techniques.
 * 
 * Prerequisites:
 * - Azure AI Search service
 * - Node.js 14.x or later
 * - @azure/search-documents package
 * - Sample data index (hotels-sample recommended)
 */

const { SearchClient, AzureKeyCredential, SearchMode } = require('@azure/search-documents');
require('dotenv').config();

class SearchScoreAnalyzer {
    /**
     * Comprehensive search score analysis and optimization
     */
    constructor(endpoint, indexName, apiKey) {
        this.client = new SearchClient(
            endpoint,
            indexName,
            new AzureKeyCredential(apiKey)
        );
        this.scoreHistory = [];
    }

    /**
     * Search with detailed score analysis
     * @param {string} query - Search query
     * @param {number} top - Number of results to return
     * @param {boolean} includeExplanation - Include score explanation (if supported)
     * @returns {Object} Search results with score analysis
     */
    async searchWithScores(query, top = 10, includeExplanation = false) {
        const startTime = Date.now();

        try {
            // Perform search with scoring parameters
            const searchResults = await this.client.search(query, {
                top: top,
                searchMode: SearchMode.all,
                scoringStatistics: 'global' // Include global scoring statistics
            });

            const documents = [];
            const scores = [];

            for await (const result of searchResults.results) {
                const score = result['@search.score'] || 0.0;
                scores.push(score);

                const docInfo = {
                    document: result,
                    score: score,
                    scoreExplanation: result['@search.scoreExplanation'] || null
                };
                documents.push(docInfo);
            }

            const duration = Date.now() - startTime;

            // Calculate score statistics
            const scoreStats = this._calculateScoreStatistics(scores);

            const result = {
                query: query,
                documents: documents,
                scoreStatistics: scoreStats,
                durationMs: duration,
                resultCount: documents.length
            };

            // Store for analysis
            this.scoreHistory.push({
                query: query,
                scores: scores,
                stats: scoreStats,
                timestamp: Date.now()
            });

            return result;

        } catch (error) {
            const duration = Date.now() - startTime;
            console.error(`Error in search with scores: ${error.message}`);
            
            return {
                query: query,
                documents: [],
                scoreStatistics: {},
                durationMs: duration,
                resultCount: 0,
                error: error.message
            };
        }
    }

    /**
     * Calculate comprehensive score statistics
     * @param {number[]} scores - Array of scores
     * @returns {Object} Score statistics
     */
    _calculateScoreStatistics(scores) {
        if (!scores || scores.length === 0) {
            return {};
        }

        const sortedScores = [...scores].sort((a, b) => a - b);
        const sum = scores.reduce((a, b) => a + b, 0);
        const mean = sum / scores.length;

        // Calculate standard deviation
        const variance = scores.reduce((acc, score) => acc + Math.pow(score - mean, 2), 0) / scores.length;
        const stdDev = Math.sqrt(variance);

        // Calculate median
        const median = sortedScores.length % 2 === 0
            ? (sortedScores[sortedScores.length / 2 - 1] + sortedScores[sortedScores.length / 2]) / 2
            : sortedScores[Math.floor(sortedScores.length / 2)];

        return {
            count: scores.length,
            minScore: Math.min(...scores),
            maxScore: Math.max(...scores),
            meanScore: mean,
            medianScore: median,
            stdDev: stdDev,
            scoreRange: Math.max(...scores) - Math.min(...scores),
            scoreDistribution: this._analyzeScoreDistribution(scores)
        };
    }

    /**
     * Analyze score distribution patterns
     * @param {number[]} scores - Array of scores
     * @returns {Object} Distribution analysis
     */
    _analyzeScoreDistribution(scores) {
        if (!scores || scores.length === 0) {
            return {};
        }

        const minScore = Math.min(...scores);
        const maxScore = Math.max(...scores);

        if (maxScore === minScore) {
            return { uniform: true, buckets: [scores.length] };
        }

        const bucketCount = 5;
        const bucketSize = (maxScore - minScore) / bucketCount;
        const buckets = new Array(bucketCount).fill(0);

        scores.forEach(score => {
            const bucketIndex = Math.min(Math.floor((score - minScore) / bucketSize), bucketCount - 1);
            buckets[bucketIndex]++;
        });

        return {
            uniform: false,
            buckets: buckets,
            bucketSize: bucketSize,
            minScore: minScore,
            maxScore: maxScore
        };
    }

    /**
     * Compare relevance across multiple queries
     * @param {string[]} queries - List of queries to compare
     * @param {number} top - Number of results per query
     * @returns {Object} Comparison analysis
     */
    async compareQueryRelevance(queries, top = 10) {
        console.log(`🔍 Comparing relevance across ${queries.length} queries...`);

        const queryResults = [];

        for (const query of queries) {
            console.log(`  Analyzing query: '${query}'`);
            const result = await this.searchWithScores(query, top);

            if (result.resultCount > 0) {
                queryResults.push({
                    query: query,
                    resultCount: result.resultCount,
                    scoreStats: result.scoreStatistics,
                    topScore: result.scoreStatistics.maxScore || 0,
                    avgScore: result.scoreStatistics.meanScore || 0,
                    scoreVariance: result.scoreStatistics.stdDev || 0
                });
            }
        }

        // Analyze comparison
        const comparison = {
            queriesAnalyzed: queryResults.length,
            queryResults: queryResults,
            insights: this._generateRelevanceInsights(queryResults)
        };

        return comparison;
    }

    /**
     * Generate insights from query comparison
     * @param {Object[]} queryResults - Query results to analyze
     * @returns {string[]} Array of insights
     */
    _generateRelevanceInsights(queryResults) {
        const insights = [];

        if (!queryResults || queryResults.length === 0) {
            return ["No valid query results to analyze"];
        }

        // Find best and worst performing queries
        const bestQuery = queryResults.reduce((prev, current) => 
            (prev.avgScore > current.avgScore) ? prev : current
        );
        const worstQuery = queryResults.reduce((prev, current) => 
            (prev.avgScore < current.avgScore) ? prev : current
        );

        insights.push(`Best performing query: '${bestQuery.query}' (avg score: ${bestQuery.avgScore.toFixed(3)})`);
        insights.push(`Worst performing query: '${worstQuery.query}' (avg score: ${worstQuery.avgScore.toFixed(3)})`);

        // Analyze score variance
        const highVarianceQueries = queryResults.filter(q => q.scoreVariance > 0.1);
        if (highVarianceQueries.length > 0) {
            insights.push(`${highVarianceQueries.length} queries show high score variance (>0.1)`);
        }

        // Analyze result counts
        const avgResults = queryResults.reduce((sum, q) => sum + q.resultCount, 0) / queryResults.length;
        insights.push(`Average results per query: ${avgResults.toFixed(1)}`);

        return insights;
    }

    /**
     * Analyze patterns in historical score data
     * @param {number} minQueries - Minimum number of queries needed for analysis
     * @returns {Object} Pattern analysis results
     */
    analyzeScorePatterns(minQueries = 5) {
        if (this.scoreHistory.length < minQueries) {
            return {
                error: `Need at least ${minQueries} queries for pattern analysis. Current: ${this.scoreHistory.length}`
            };
        }

        console.log(`📊 Analyzing patterns from ${this.scoreHistory.length} queries...`);

        // Aggregate statistics
        const allScores = [];
        const queryStats = [];

        this.scoreHistory.forEach(entry => {
            allScores.push(...entry.scores);
            queryStats.push({
                query: entry.query,
                meanScore: entry.stats.meanScore || 0,
                maxScore: entry.stats.maxScore || 0,
                resultCount: entry.scores.length
            });
        });

        // Overall patterns
        const overallStats = this._calculateScoreStatistics(allScores);
        const overallMean = overallStats.meanScore || 0;

        // Query performance patterns
        const performancePatterns = {
            highPerformers: queryStats.filter(q => q.meanScore > overallMean),
            lowPerformers: queryStats.filter(q => q.meanScore < overallMean * 0.8),
            consistentQueries: queryStats.filter(q => q.resultCount >= 5)
        };

        return {
            totalQueriesAnalyzed: this.scoreHistory.length,
            totalDocumentsScored: allScores.length,
            overallStatistics: overallStats,
            performancePatterns: performancePatterns,
            recommendations: this._generateScoreRecommendations(overallStats, performancePatterns)
        };
    }

    /**
     * Generate recommendations based on score analysis
     * @param {Object} overallStats - Overall score statistics
     * @param {Object} patterns - Performance patterns
     * @returns {string[]} Array of recommendations
     */
    _generateScoreRecommendations(overallStats, patterns) {
        const recommendations = [];

        // Score range analysis
        const scoreRange = overallStats.scoreRange || 0;
        if (scoreRange < 0.5) {
            recommendations.push("Consider using custom scoring profiles to increase score differentiation");
        }

        // Low performer analysis
        const lowPerformers = patterns.lowPerformers || [];
        const highPerformers = patterns.highPerformers || [];
        if (lowPerformers.length > highPerformers.length) {
            recommendations.push("Many queries show low relevance scores - review query construction and index fields");
        }

        // Consistency analysis
        const consistentQueries = patterns.consistentQueries || [];
        if (consistentQueries.length < this.scoreHistory.length * 0.5) {
            recommendations.push("Many queries return few results - consider broader search strategies");
        }

        // Score distribution
        const meanScore = overallStats.meanScore || 0;
        if (meanScore < 1.0) {
            recommendations.push("Overall scores are low - consider boosting relevant fields or using custom scoring");
        }

        return recommendations;
    }

    /**
     * Test different scoring strategies for a query
     * @param {string} baseQuery - Base query to test with different strategies
     * @returns {Object} Comparison of scoring strategies
     */
    async testScoringStrategies(baseQuery) {
        console.log(`🧪 Testing scoring strategies for query: '${baseQuery}'`);

        const strategies = {
            'default': { searchMode: SearchMode.any },
            'all_terms': { searchMode: SearchMode.all },
            'exact_phrase': { searchText: `"${baseQuery}"`, searchMode: SearchMode.any }
        };

        const strategyResults = {};

        for (const [strategyName, params] of Object.entries(strategies)) {
            console.log(`  Testing strategy: ${strategyName}`);

            try {
                const searchText = params.searchText || baseQuery;
                const searchMode = params.searchMode || SearchMode.any;

                const searchResults = await this.client.search(searchText, {
                    searchMode: searchMode,
                    top: 10
                });

                const scores = [];
                const documents = [];

                for await (const result of searchResults.results) {
                    const score = result['@search.score'] || 0.0;
                    scores.push(score);
                    documents.push({
                        id: result.hotelId || 'unknown',
                        name: result.hotelName || 'Unknown',
                        score: score
                    });
                }

                strategyResults[strategyName] = {
                    documents: documents,
                    scoreStats: this._calculateScoreStatistics(scores),
                    resultCount: documents.length
                };

            } catch (error) {
                strategyResults[strategyName] = {
                    error: error.message,
                    documents: [],
                    scoreStats: {},
                    resultCount: 0
                };
            }
        }

        // Compare strategies
        const comparison = this._compareStrategies(strategyResults);

        return {
            baseQuery: baseQuery,
            strategyResults: strategyResults,
            comparison: comparison
        };
    }

    /**
     * Compare different scoring strategies
     * @param {Object} strategyResults - Results from different strategies
     * @returns {Object} Strategy comparison
     */
    _compareStrategies(strategyResults) {
        const validStrategies = Object.fromEntries(
            Object.entries(strategyResults).filter(([_, result]) => 
                !result.error && result.resultCount > 0
            )
        );

        if (Object.keys(validStrategies).length === 0) {
            return { error: 'No valid strategy results to compare' };
        }

        // Find best strategy by different metrics
        const strategies = Object.entries(validStrategies);
        
        const bestByMaxScore = strategies.reduce((prev, current) => 
            (prev[1].scoreStats.maxScore || 0) > (current[1].scoreStats.maxScore || 0) ? prev : current
        );
        
        const bestByAvgScore = strategies.reduce((prev, current) => 
            (prev[1].scoreStats.meanScore || 0) > (current[1].scoreStats.meanScore || 0) ? prev : current
        );
        
        const mostResults = strategies.reduce((prev, current) => 
            prev[1].resultCount > current[1].resultCount ? prev : current
        );

        return {
            strategiesCompared: Object.keys(validStrategies).length,
            bestMaxScore: { 
                strategy: bestByMaxScore[0], 
                score: bestByMaxScore[1].scoreStats.maxScore || 0 
            },
            bestAvgScore: { 
                strategy: bestByAvgScore[0], 
                score: bestByAvgScore[1].scoreStats.meanScore || 0 
            },
            mostResults: { 
                strategy: mostResults[0], 
                count: mostResults[1].resultCount 
            },
            recommendation: this._recommendStrategy(validStrategies)
        };
    }

    /**
     * Recommend the best strategy based on analysis
     * @param {Object} strategies - Valid strategies to analyze
     * @returns {string} Strategy recommendation
     */
    _recommendStrategy(strategies) {
        if (!strategies || Object.keys(strategies).length === 0) {
            return "No valid strategies to recommend";
        }

        // Score strategies based on multiple factors
        const strategyScores = {};

        Object.entries(strategies).forEach(([name, result]) => {
            const stats = result.scoreStats;
            const score = (
                (stats.meanScore || 0) * 0.4 +  // Average relevance
                (stats.maxScore || 0) * 0.3 +   // Best match quality
                (result.resultCount / 10) * 0.3  // Result coverage
            );
            strategyScores[name] = score;
        });

        const bestStrategy = Object.entries(strategyScores).reduce((prev, current) => 
            prev[1] > current[1] ? prev : current
        );

        return `Recommended strategy: ${bestStrategy[0]} (score: ${bestStrategy[1].toFixed(3)})`;
    }
}

async function main() {
    // Configuration
    const endpoint = process.env.SEARCH_ENDPOINT || 'https://your-search-service.search.windows.net';
    const apiKey = process.env.SEARCH_API_KEY || 'your-api-key';
    const indexName = process.env.INDEX_NAME || 'hotels-sample';

    console.log("🔍 Azure AI Search - Search Scores Analysis");
    console.log("=".repeat(50));

    // Initialize analyzer
    const analyzer = new SearchScoreAnalyzer(endpoint, indexName, apiKey);

    try {
        // Example 1: Basic score analysis
        console.log("\n1. Basic Score Analysis");
        console.log("-".repeat(25));

        const result = await analyzer.searchWithScores("luxury hotel", 5);
        if (result.resultCount > 0) {
            const stats = result.scoreStatistics;
            console.log(`Query: '${result.query}'`);
            console.log(`Results: ${result.resultCount}`);
            console.log(`Score range: ${stats.minScore?.toFixed(3)} - ${stats.maxScore?.toFixed(3)}`);
            console.log(`Average score: ${stats.meanScore?.toFixed(3)}`);
            console.log(`Standard deviation: ${stats.stdDev?.toFixed(3)}`);

            console.log("\nTop results:");
            result.documents.slice(0, 3).forEach((doc, i) => {
                const name = doc.document.hotelName || 'Unknown';
                const score = doc.score;
                console.log(`  ${i + 1}. ${name} (score: ${score.toFixed(3)})`);
            });
        }

        // Example 2: Query comparison
        console.log("\n2. Query Relevance Comparison");
        console.log("-".repeat(30));

        const testQueries = ['luxury', 'beach hotel', 'spa resort', 'budget accommodation'];
        const comparison = await analyzer.compareQueryRelevance(testQueries, 5);

        console.log(`Analyzed ${comparison.queriesAnalyzed} queries:`);
        comparison.queryResults.forEach(result => {
            console.log(`  '${result.query}': avg score ${result.avgScore.toFixed(3)}, ${result.resultCount} results`);
        });

        console.log("\nInsights:");
        comparison.insights.forEach(insight => {
            console.log(`  • ${insight}`);
        });

        // Example 3: Scoring strategy testing
        console.log("\n3. Scoring Strategy Testing");
        console.log("-".repeat(30));

        const strategyTest = await analyzer.testScoringStrategies("ocean view");
        console.log(`Base query: '${strategyTest.baseQuery}'`);

        Object.entries(strategyTest.strategyResults).forEach(([strategy, result]) => {
            if (!result.error) {
                const stats = result.scoreStats;
                console.log(`  ${strategy}: ${result.resultCount} results, avg score: ${(stats.meanScore || 0).toFixed(3)}`);
            } else {
                console.log(`  ${strategy}: Error - ${result.error}`);
            }
        });

        console.log(`\n${strategyTest.comparison.recommendation || 'No recommendation available'}`);

        // Example 4: Pattern analysis
        console.log("\n4. Score Pattern Analysis");
        console.log("-".repeat(26));

        // Add more queries for pattern analysis
        const additionalQueries = ['wifi', 'parking', 'restaurant', 'pool', 'gym'];
        for (const query of additionalQueries) {
            await analyzer.searchWithScores(query, 3);
        }

        const patterns = analyzer.analyzeScorePatterns();
        if (!patterns.error) {
            console.log(`Analyzed ${patterns.totalQueriesAnalyzed} queries`);
            console.log(`Total documents scored: ${patterns.totalDocumentsScored}`);

            const overall = patterns.overallStatistics;
            console.log("Overall score statistics:");
            console.log(`  Mean: ${(overall.meanScore || 0).toFixed(3)}`);
            console.log(`  Range: ${(overall.scoreRange || 0).toFixed(3)}`);
            console.log(`  Std Dev: ${(overall.stdDev || 0).toFixed(3)}`);

            console.log("\nRecommendations:");
            patterns.recommendations.forEach(rec => {
                console.log(`  • ${rec}`);
            });
        } else {
            console.log(`Pattern analysis error: ${patterns.error}`);
        }

        console.log("\n✅ Search score analysis completed!");

    } catch (error) {
        console.error("❌ Error during analysis:", error.message);
    }
}

// Export for use as module
module.exports = { SearchScoreAnalyzer };

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}