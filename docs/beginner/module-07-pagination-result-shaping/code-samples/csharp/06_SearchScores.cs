/*
 * Module 7: Pagination & Result Shaping - Search Scores Analysis
 * Azure AI Search .NET SDK Example
 * 
 * This example demonstrates how to work with search scores and relevance in Azure AI Search,
 * including score analysis, custom scoring, and relevance optimization techniques.
 * 
 * Prerequisites:
 * - Azure AI Search service
 * - .NET 6.0 or later
 * - Azure.Search.Documents package
 * - Sample data index (hotels-sample recommended)
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace AzureAISearch.Module07.SearchScores
{
    public class ScoreStatistics
    {
        public int Count { get; set; }
        public double MinScore { get; set; }
        public double MaxScore { get; set; }
        public double MeanScore { get; set; }
        public double MedianScore { get; set; }
        public double StandardDeviation { get; set; }
        public double ScoreRange { get; set; }
        public ScoreDistribution Distribution { get; set; }
    }

    public class ScoreDistribution
    {
        public bool IsUniform { get; set; }
        public int[] Buckets { get; set; }
        public double BucketSize { get; set; }
        public double MinScore { get; set; }
        public double MaxScore { get; set; }
    }

    public class QueryResult
    {
        public string Query { get; set; }
        public int ResultCount { get; set; }
        public ScoreStatistics ScoreStats { get; set; }
        public double TopScore { get; set; }
        public double AvgScore { get; set; }
        public double ScoreVariance { get; set; }
    }

    public class SearchScoreAnalyzer
    {
        private readonly SearchClient _searchClient;
        private readonly List<ScoreHistoryEntry> _scoreHistory;

        public SearchScoreAnalyzer(string endpoint, string indexName, string apiKey)
        {
            var credential = new AzureKeyCredential(apiKey);
            _searchClient = new SearchClient(new Uri(endpoint), indexName, credential);
            _scoreHistory = new List<ScoreHistoryEntry>();
        }

        /// <summary>
        /// Search with detailed score analysis
        /// </summary>
        /// <param name="query">Search query</param>
        /// <param name="top">Number of results to return</param>
        /// <param name="includeExplanation">Include score explanation (if supported)</param>
        /// <returns>Search results with score analysis</returns>
        public async Task<SearchResultWithScores> SearchWithScoresAsync(string query, int top = 10, bool includeExplanation = false)
        {
            var startTime = DateTime.UtcNow;

            try
            {
                var searchOptions = new SearchOptions
                {
                    Size = top,
                    SearchMode = SearchMode.All,
                    ScoringStatistics = ScoringStatistics.Global
                };

                var searchResults = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                var documents = new List<DocumentWithScore>();
                var scores = new List<double>();

                await foreach (var result in searchResults.Value.GetResultsAsync())
                {
                    var score = result.Score ?? 0.0;
                    scores.Add(score);

                    documents.Add(new DocumentWithScore
                    {
                        Document = result.Document,
                        Score = score,
                        ScoreExplanation = null // Score explanation not directly available in .NET SDK
                    });
                }

                var duration = DateTime.UtcNow - startTime;
                var scoreStats = CalculateScoreStatistics(scores);

                var result = new SearchResultWithScores
                {
                    Query = query,
                    Documents = documents,
                    ScoreStatistics = scoreStats,
                    DurationMs = duration.TotalMilliseconds,
                    ResultCount = documents.Count
                };

                // Store for analysis
                _scoreHistory.Add(new ScoreHistoryEntry
                {
                    Query = query,
                    Scores = scores,
                    Stats = scoreStats,
                    Timestamp = DateTime.UtcNow
                });

                return result;
            }
            catch (Exception ex)
            {
                var duration = DateTime.UtcNow - startTime;
                Console.WriteLine($"Error in search with scores: {ex.Message}");

                return new SearchResultWithScores
                {
                    Query = query,
                    Documents = new List<DocumentWithScore>(),
                    ScoreStatistics = new ScoreStatistics(),
                    DurationMs = duration.TotalMilliseconds,
                    ResultCount = 0,
                    Error = ex.Message
                };
            }
        }

        /// <summary>
        /// Calculate comprehensive score statistics
        /// </summary>
        /// <param name="scores">Array of scores</param>
        /// <returns>Score statistics</returns>
        private ScoreStatistics CalculateScoreStatistics(List<double> scores)
        {
            if (scores == null || scores.Count == 0)
            {
                return new ScoreStatistics();
            }

            var sortedScores = scores.OrderBy(s => s).ToList();
            var mean = scores.Average();
            var variance = scores.Sum(s => Math.Pow(s - mean, 2)) / scores.Count;
            var standardDeviation = Math.Sqrt(variance);

            // Calculate median
            var median = sortedScores.Count % 2 == 0
                ? (sortedScores[sortedScores.Count / 2 - 1] + sortedScores[sortedScores.Count / 2]) / 2
                : sortedScores[sortedScores.Count / 2];

            return new ScoreStatistics
            {
                Count = scores.Count,
                MinScore = scores.Min(),
                MaxScore = scores.Max(),
                MeanScore = mean,
                MedianScore = median,
                StandardDeviation = standardDeviation,
                ScoreRange = scores.Max() - scores.Min(),
                Distribution = AnalyzeScoreDistribution(scores)
            };
        }

        /// <summary>
        /// Analyze score distribution patterns
        /// </summary>
        /// <param name="scores">Array of scores</param>
        /// <returns>Distribution analysis</returns>
        private ScoreDistribution AnalyzeScoreDistribution(List<double> scores)
        {
            if (scores == null || scores.Count == 0)
            {
                return new ScoreDistribution();
            }

            var minScore = scores.Min();
            var maxScore = scores.Max();

            if (Math.Abs(maxScore - minScore) < 0.001) // Essentially equal
            {
                return new ScoreDistribution
                {
                    IsUniform = true,
                    Buckets = new[] { scores.Count }
                };
            }

            const int bucketCount = 5;
            var bucketSize = (maxScore - minScore) / bucketCount;
            var buckets = new int[bucketCount];

            foreach (var score in scores)
            {
                var bucketIndex = Math.Min((int)((score - minScore) / bucketSize), bucketCount - 1);
                buckets[bucketIndex]++;
            }

            return new ScoreDistribution
            {
                IsUniform = false,
                Buckets = buckets,
                BucketSize = bucketSize,
                MinScore = minScore,
                MaxScore = maxScore
            };
        }

        /// <summary>
        /// Compare relevance across multiple queries
        /// </summary>
        /// <param name="queries">List of queries to compare</param>
        /// <param name="top">Number of results per query</param>
        /// <returns>Comparison analysis</returns>
        public async Task<QueryComparisonResult> CompareQueryRelevanceAsync(List<string> queries, int top = 10)
        {
            Console.WriteLine($"🔍 Comparing relevance across {queries.Count} queries...");

            var queryResults = new List<QueryResult>();

            foreach (var query in queries)
            {
                Console.WriteLine($"  Analyzing query: '{query}'");
                var result = await SearchWithScoresAsync(query, top);

                if (result.ResultCount > 0)
                {
                    queryResults.Add(new QueryResult
                    {
                        Query = query,
                        ResultCount = result.ResultCount,
                        ScoreStats = result.ScoreStatistics,
                        TopScore = result.ScoreStatistics.MaxScore,
                        AvgScore = result.ScoreStatistics.MeanScore,
                        ScoreVariance = result.ScoreStatistics.StandardDeviation
                    });
                }
            }

            return new QueryComparisonResult
            {
                QueriesAnalyzed = queryResults.Count,
                QueryResults = queryResults,
                Insights = GenerateRelevanceInsights(queryResults)
            };
        }

        /// <summary>
        /// Generate insights from query comparison
        /// </summary>
        /// <param name="queryResults">Query results to analyze</param>
        /// <returns>Array of insights</returns>
        private List<string> GenerateRelevanceInsights(List<QueryResult> queryResults)
        {
            var insights = new List<string>();

            if (queryResults == null || queryResults.Count == 0)
            {
                insights.Add("No valid query results to analyze");
                return insights;
            }

            // Find best and worst performing queries
            var bestQuery = queryResults.OrderByDescending(q => q.AvgScore).First();
            var worstQuery = queryResults.OrderBy(q => q.AvgScore).First();

            insights.Add($"Best performing query: '{bestQuery.Query}' (avg score: {bestQuery.AvgScore:F3})");
            insights.Add($"Worst performing query: '{worstQuery.Query}' (avg score: {worstQuery.AvgScore:F3})");

            // Analyze score variance
            var highVarianceQueries = queryResults.Where(q => q.ScoreVariance > 0.1).ToList();
            if (highVarianceQueries.Any())
            {
                insights.Add($"{highVarianceQueries.Count} queries show high score variance (>0.1)");
            }

            // Analyze result counts
            var avgResults = queryResults.Average(q => q.ResultCount);
            insights.Add($"Average results per query: {avgResults:F1}");

            return insights;
        }

        /// <summary>
        /// Analyze patterns in historical score data
        /// </summary>
        /// <param name="minQueries">Minimum number of queries needed for analysis</param>
        /// <returns>Pattern analysis results</returns>
        public PatternAnalysisResult AnalyzeScorePatterns(int minQueries = 5)
        {
            if (_scoreHistory.Count < minQueries)
            {
                return new PatternAnalysisResult
                {
                    Error = $"Need at least {minQueries} queries for pattern analysis. Current: {_scoreHistory.Count}"
                };
            }

            Console.WriteLine($"📊 Analyzing patterns from {_scoreHistory.Count} queries...");

            // Aggregate statistics
            var allScores = _scoreHistory.SelectMany(entry => entry.Scores).ToList();
            var queryStats = _scoreHistory.Select(entry => new
            {
                Query = entry.Query,
                MeanScore = entry.Stats.MeanScore,
                MaxScore = entry.Stats.MaxScore,
                ResultCount = entry.Scores.Count
            }).ToList();

            // Overall patterns
            var overallStats = CalculateScoreStatistics(allScores);
            var overallMean = overallStats.MeanScore;

            // Query performance patterns
            var performancePatterns = new PerformancePatterns
            {
                HighPerformers = queryStats.Where(q => q.MeanScore > overallMean).ToList(),
                LowPerformers = queryStats.Where(q => q.MeanScore < overallMean * 0.8).ToList(),
                ConsistentQueries = queryStats.Where(q => q.ResultCount >= 5).ToList()
            };

            return new PatternAnalysisResult
            {
                TotalQueriesAnalyzed = _scoreHistory.Count,
                TotalDocumentsScored = allScores.Count,
                OverallStatistics = overallStats,
                PerformancePatterns = performancePatterns,
                Recommendations = GenerateScoreRecommendations(overallStats, performancePatterns)
            };
        }

        /// <summary>
        /// Generate recommendations based on score analysis
        /// </summary>
        /// <param name="overallStats">Overall score statistics</param>
        /// <param name="patterns">Performance patterns</param>
        /// <returns>Array of recommendations</returns>
        private List<string> GenerateScoreRecommendations(ScoreStatistics overallStats, PerformancePatterns patterns)
        {
            var recommendations = new List<string>();

            // Score range analysis
            if (overallStats.ScoreRange < 0.5)
            {
                recommendations.Add("Consider using custom scoring profiles to increase score differentiation");
            }

            // Low performer analysis
            if (patterns.LowPerformers.Count > patterns.HighPerformers.Count)
            {
                recommendations.Add("Many queries show low relevance scores - review query construction and index fields");
            }

            // Consistency analysis
            if (patterns.ConsistentQueries.Count < _scoreHistory.Count * 0.5)
            {
                recommendations.Add("Many queries return few results - consider broader search strategies");
            }

            // Score distribution
            if (overallStats.MeanScore < 1.0)
            {
                recommendations.Add("Overall scores are low - consider boosting relevant fields or using custom scoring");
            }

            return recommendations;
        }

        /// <summary>
        /// Test different scoring strategies for a query
        /// </summary>
        /// <param name="baseQuery">Base query to test with different strategies</param>
        /// <returns>Comparison of scoring strategies</returns>
        public async Task<ScoringStrategyComparison> TestScoringStrategiesAsync(string baseQuery)
        {
            Console.WriteLine($"🧪 Testing scoring strategies for query: '{baseQuery}'");

            var strategies = new Dictionary<string, SearchOptions>
            {
                ["default"] = new SearchOptions { SearchMode = SearchMode.Any },
                ["all_terms"] = new SearchOptions { SearchMode = SearchMode.All },
                ["exact_phrase"] = new SearchOptions { SearchMode = SearchMode.Any }
            };

            var strategyResults = new Dictionary<string, StrategyResult>();

            foreach (var (strategyName, searchOptions) in strategies)
            {
                Console.WriteLine($"  Testing strategy: {strategyName}");

                try
                {
                    var searchText = strategyName == "exact_phrase" ? $"\"{baseQuery}\"" : baseQuery;
                    searchOptions.Size = 10;

                    var searchResults = await _searchClient.SearchAsync<SearchDocument>(searchText, searchOptions);
                    var scores = new List<double>();
                    var documents = new List<dynamic>();

                    await foreach (var result in searchResults.Value.GetResultsAsync())
                    {
                        var score = result.Score ?? 0.0;
                        scores.Add(score);
                        documents.Add(new
                        {
                            Id = result.Document.TryGetValue("hotelId", out var id) ? id.ToString() : "unknown",
                            Name = result.Document.TryGetValue("hotelName", out var name) ? name.ToString() : "Unknown",
                            Score = score
                        });
                    }

                    strategyResults[strategyName] = new StrategyResult
                    {
                        Documents = documents,
                        ScoreStats = CalculateScoreStatistics(scores),
                        ResultCount = documents.Count
                    };
                }
                catch (Exception ex)
                {
                    strategyResults[strategyName] = new StrategyResult
                    {
                        Error = ex.Message,
                        Documents = new List<dynamic>(),
                        ScoreStats = new ScoreStatistics(),
                        ResultCount = 0
                    };
                }
            }

            // Compare strategies
            var comparison = CompareStrategies(strategyResults);

            return new ScoringStrategyComparison
            {
                BaseQuery = baseQuery,
                StrategyResults = strategyResults,
                Comparison = comparison
            };
        }

        /// <summary>
        /// Compare different scoring strategies
        /// </summary>
        /// <param name="strategyResults">Results from different strategies</param>
        /// <returns>Strategy comparison</returns>
        private StrategyComparison CompareStrategies(Dictionary<string, StrategyResult> strategyResults)
        {
            var validStrategies = strategyResults
                .Where(kvp => string.IsNullOrEmpty(kvp.Value.Error) && kvp.Value.ResultCount > 0)
                .ToDictionary(kvp => kvp.Key, kvp => kvp.Value);

            if (!validStrategies.Any())
            {
                return new StrategyComparison { Error = "No valid strategy results to compare" };
            }

            // Find best strategy by different metrics
            var bestByMaxScore = validStrategies
                .OrderByDescending(kvp => kvp.Value.ScoreStats.MaxScore)
                .First();

            var bestByAvgScore = validStrategies
                .OrderByDescending(kvp => kvp.Value.ScoreStats.MeanScore)
                .First();

            var mostResults = validStrategies
                .OrderByDescending(kvp => kvp.Value.ResultCount)
                .First();

            return new StrategyComparison
            {
                StrategiesCompared = validStrategies.Count,
                BestMaxScore = new StrategyMetric
                {
                    Strategy = bestByMaxScore.Key,
                    Score = bestByMaxScore.Value.ScoreStats.MaxScore
                },
                BestAvgScore = new StrategyMetric
                {
                    Strategy = bestByAvgScore.Key,
                    Score = bestByAvgScore.Value.ScoreStats.MeanScore
                },
                MostResults = new StrategyMetric
                {
                    Strategy = mostResults.Key,
                    Count = mostResults.Value.ResultCount
                },
                Recommendation = RecommendStrategy(validStrategies)
            };
        }

        /// <summary>
        /// Recommend the best strategy based on analysis
        /// </summary>
        /// <param name="strategies">Valid strategies to analyze</param>
        /// <returns>Strategy recommendation</returns>
        private string RecommendStrategy(Dictionary<string, StrategyResult> strategies)
        {
            if (!strategies.Any())
            {
                return "No valid strategies to recommend";
            }

            // Score strategies based on multiple factors
            var strategyScores = strategies.ToDictionary(
                kvp => kvp.Key,
                kvp => kvp.Value.ScoreStats.MeanScore * 0.4 +  // Average relevance
                       kvp.Value.ScoreStats.MaxScore * 0.3 +   // Best match quality
                       (kvp.Value.ResultCount / 10.0) * 0.3    // Result coverage
            );

            var bestStrategy = strategyScores.OrderByDescending(kvp => kvp.Value).First();
            return $"Recommended strategy: {bestStrategy.Key} (score: {bestStrategy.Value:F3})";
        }
    }

    // Supporting classes
    public class SearchResultWithScores
    {
        public string Query { get; set; }
        public List<DocumentWithScore> Documents { get; set; }
        public ScoreStatistics ScoreStatistics { get; set; }
        public double DurationMs { get; set; }
        public int ResultCount { get; set; }
        public string Error { get; set; }
    }

    public class DocumentWithScore
    {
        public SearchDocument Document { get; set; }
        public double Score { get; set; }
        public string ScoreExplanation { get; set; }
    }

    public class ScoreHistoryEntry
    {
        public string Query { get; set; }
        public List<double> Scores { get; set; }
        public ScoreStatistics Stats { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class QueryComparisonResult
    {
        public int QueriesAnalyzed { get; set; }
        public List<QueryResult> QueryResults { get; set; }
        public List<string> Insights { get; set; }
    }

    public class PatternAnalysisResult
    {
        public int TotalQueriesAnalyzed { get; set; }
        public int TotalDocumentsScored { get; set; }
        public ScoreStatistics OverallStatistics { get; set; }
        public PerformancePatterns PerformancePatterns { get; set; }
        public List<string> Recommendations { get; set; }
        public string Error { get; set; }
    }

    public class PerformancePatterns
    {
        public List<dynamic> HighPerformers { get; set; }
        public List<dynamic> LowPerformers { get; set; }
        public List<dynamic> ConsistentQueries { get; set; }
    }

    public class ScoringStrategyComparison
    {
        public string BaseQuery { get; set; }
        public Dictionary<string, StrategyResult> StrategyResults { get; set; }
        public StrategyComparison Comparison { get; set; }
    }

    public class StrategyResult
    {
        public List<dynamic> Documents { get; set; }
        public ScoreStatistics ScoreStats { get; set; }
        public int ResultCount { get; set; }
        public string Error { get; set; }
    }

    public class StrategyComparison
    {
        public int StrategiesCompared { get; set; }
        public StrategyMetric BestMaxScore { get; set; }
        public StrategyMetric BestAvgScore { get; set; }
        public StrategyMetric MostResults { get; set; }
        public string Recommendation { get; set; }
        public string Error { get; set; }
    }

    public class StrategyMetric
    {
        public string Strategy { get; set; }
        public double Score { get; set; }
        public int Count { get; set; }
    }

    // Main program
    public class Program
    {
        public static async Task Main(string[] args)
        {
            // Configuration
            var configuration = new ConfigurationBuilder()
                .AddEnvironmentVariables()
                .Build();

            var endpoint = configuration["SEARCH_ENDPOINT"] ?? "https://your-search-service.search.windows.net";
            var apiKey = configuration["SEARCH_API_KEY"] ?? "your-api-key";
            var indexName = configuration["INDEX_NAME"] ?? "hotels-sample";

            Console.WriteLine("🔍 Azure AI Search - Search Scores Analysis");
            Console.WriteLine(new string('=', 50));

            // Initialize analyzer
            var analyzer = new SearchScoreAnalyzer(endpoint, indexName, apiKey);

            try
            {
                // Example 1: Basic score analysis
                Console.WriteLine("\n1. Basic Score Analysis");
                Console.WriteLine(new string('-', 25));

                var result = await analyzer.SearchWithScoresAsync("luxury hotel", 5);
                if (result.ResultCount > 0)
                {
                    var stats = result.ScoreStatistics;
                    Console.WriteLine($"Query: '{result.Query}'");
                    Console.WriteLine($"Results: {result.ResultCount}");
                    Console.WriteLine($"Score range: {stats.MinScore:F3} - {stats.MaxScore:F3}");
                    Console.WriteLine($"Average score: {stats.MeanScore:F3}");
                    Console.WriteLine($"Standard deviation: {stats.StandardDeviation:F3}");

                    Console.WriteLine("\nTop results:");
                    for (int i = 0; i < Math.Min(3, result.Documents.Count); i++)
                    {
                        var doc = result.Documents[i];
                        var name = doc.Document.TryGetValue("hotelName", out var hotelName) ? hotelName.ToString() : "Unknown";
                        Console.WriteLine($"  {i + 1}. {name} (score: {doc.Score:F3})");
                    }
                }

                // Example 2: Query comparison
                Console.WriteLine("\n2. Query Relevance Comparison");
                Console.WriteLine(new string('-', 30));

                var testQueries = new List<string> { "luxury", "beach hotel", "spa resort", "budget accommodation" };
                var comparison = await analyzer.CompareQueryRelevanceAsync(testQueries, 5);

                Console.WriteLine($"Analyzed {comparison.QueriesAnalyzed} queries:");
                foreach (var queryResult in comparison.QueryResults)
                {
                    Console.WriteLine($"  '{queryResult.Query}': avg score {queryResult.AvgScore:F3}, {queryResult.ResultCount} results");
                }

                Console.WriteLine("\nInsights:");
                foreach (var insight in comparison.Insights)
                {
                    Console.WriteLine($"  • {insight}");
                }

                // Example 3: Scoring strategy testing
                Console.WriteLine("\n3. Scoring Strategy Testing");
                Console.WriteLine(new string('-', 30));

                var strategyTest = await analyzer.TestScoringStrategiesAsync("ocean view");
                Console.WriteLine($"Base query: '{strategyTest.BaseQuery}'");

                foreach (var (strategy, strategyResult) in strategyTest.StrategyResults)
                {
                    if (string.IsNullOrEmpty(strategyResult.Error))
                    {
                        var stats = strategyResult.ScoreStats;
                        Console.WriteLine($"  {strategy}: {strategyResult.ResultCount} results, avg score: {stats.MeanScore:F3}");
                    }
                    else
                    {
                        Console.WriteLine($"  {strategy}: Error - {strategyResult.Error}");
                    }
                }

                Console.WriteLine($"\n{strategyTest.Comparison.Recommendation ?? "No recommendation available"}");

                // Example 4: Pattern analysis
                Console.WriteLine("\n4. Score Pattern Analysis");
                Console.WriteLine(new string('-', 26));

                // Add more queries for pattern analysis
                var additionalQueries = new[] { "wifi", "parking", "restaurant", "pool", "gym" };
                foreach (var query in additionalQueries)
                {
                    await analyzer.SearchWithScoresAsync(query, 3);
                }

                var patterns = analyzer.AnalyzeScorePatterns();
                if (string.IsNullOrEmpty(patterns.Error))
                {
                    Console.WriteLine($"Analyzed {patterns.TotalQueriesAnalyzed} queries");
                    Console.WriteLine($"Total documents scored: {patterns.TotalDocumentsScored}");

                    var overall = patterns.OverallStatistics;
                    Console.WriteLine("Overall score statistics:");
                    Console.WriteLine($"  Mean: {overall.MeanScore:F3}");
                    Console.WriteLine($"  Range: {overall.ScoreRange:F3}");
                    Console.WriteLine($"  Std Dev: {overall.StandardDeviation:F3}");

                    Console.WriteLine("\nRecommendations:");
                    foreach (var rec in patterns.Recommendations)
                    {
                        Console.WriteLine($"  • {rec}");
                    }
                }
                else
                {
                    Console.WriteLine($"Pattern analysis error: {patterns.Error}");
                }

                Console.WriteLine("\n✅ Search score analysis completed!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error during analysis: {ex.Message}");
            }
        }
    }
}