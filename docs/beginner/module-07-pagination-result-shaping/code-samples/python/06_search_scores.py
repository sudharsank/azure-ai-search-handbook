#!/usr/bin/env python3
"""
Module 7: Pagination & Result Shaping - Search Scores Analysis
Azure AI Search Python SDK Example

This example demonstrates how to work with search scores and relevance in Azure AI Search,
including score analysis, custom scoring, and relevance optimization techniques.

Prerequisites:
- Azure AI Search service
- Python 3.7+
- azure-search-documents package
- Sample data index (hotels-sample recommended)
"""

import os
import time
import statistics
from typing import List, Dict, Any, Optional, Tuple
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import SearchMode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchScoreAnalyzer:
    """Comprehensive search score analysis and optimization"""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the search score analyzer"""
        self.client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        self.score_history = []
    
    def search_with_scores(self, query: str, top: int = 10, 
                          include_explanation: bool = False) -> Dict[str, Any]:
        """
        Search with detailed score analysis
        
        Args:
            query: Search query
            top: Number of results to return
            include_explanation: Include score explanation (if supported)
            
        Returns:
            Dictionary with search results and score analysis
        """
        start_time = time.time()
        
        try:
            # Perform search with scoring parameters
            results = self.client.search(
                search_text=query,
                top=top,
                search_mode=SearchMode.ALL,
                scoring_statistics='global'  # Include global scoring statistics
            )
            
            documents = []
            scores = []
            
            for doc in results:
                score = getattr(doc, '@search.score', 0.0)
                scores.append(score)
                
                doc_info = {
                    'document': dict(doc),
                    'score': score,
                    'score_explanation': getattr(doc, '@search.scoreExplanation', None)
                }
                documents.append(doc_info)
            
            duration = (time.time() - start_time) * 1000
            
            # Calculate score statistics
            score_stats = self._calculate_score_statistics(scores)
            
            result = {
                'query': query,
                'documents': documents,
                'score_statistics': score_stats,
                'duration_ms': duration,
                'result_count': len(documents)
            }
            
            # Store for analysis
            self.score_history.append({
                'query': query,
                'scores': scores,
                'stats': score_stats,
                'timestamp': time.time()
            })
            
            return result
            
        except Exception as e:
            print(f"Error in search with scores: {e}")
            return {
                'query': query,
                'documents': [],
                'score_statistics': {},
                'duration_ms': 0,
                'result_count': 0,
                'error': str(e)
            }
    
    def _calculate_score_statistics(self, scores: List[float]) -> Dict[str, Any]:
        """Calculate comprehensive score statistics"""
        if not scores:
            return {}
        
        return {
            'count': len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'mean_score': statistics.mean(scores),
            'median_score': statistics.median(scores),
            'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
            'score_range': max(scores) - min(scores),
            'score_distribution': self._analyze_score_distribution(scores)
        }
    
    def _analyze_score_distribution(self, scores: List[float]) -> Dict[str, Any]:
        """Analyze score distribution patterns"""
        if not scores:
            return {}
        
        # Create score buckets
        min_score, max_score = min(scores), max(scores)
        if max_score == min_score:
            return {'uniform': True, 'buckets': [len(scores)]}
        
        bucket_count = 5
        bucket_size = (max_score - min_score) / bucket_count
        buckets = [0] * bucket_count
        
        for score in scores:
            bucket_index = min(int((score - min_score) / bucket_size), bucket_count - 1)
            buckets[bucket_index] += 1
        
        return {
            'uniform': False,
            'buckets': buckets,
            'bucket_size': bucket_size,
            'min_score': min_score,
            'max_score': max_score
        }
    
    def compare_query_relevance(self, queries: List[str], top: int = 10) -> Dict[str, Any]:
        """
        Compare relevance across multiple queries
        
        Args:
            queries: List of queries to compare
            top: Number of results per query
            
        Returns:
            Comparison analysis
        """
        print(f"🔍 Comparing relevance across {len(queries)} queries...")
        
        query_results = []
        
        for query in queries:
            print(f"  Analyzing query: '{query}'")
            result = self.search_with_scores(query, top=top)
            
            if result['result_count'] > 0:
                query_results.append({
                    'query': query,
                    'result_count': result['result_count'],
                    'score_stats': result['score_statistics'],
                    'top_score': result['score_statistics'].get('max_score', 0),
                    'avg_score': result['score_statistics'].get('mean_score', 0),
                    'score_variance': result['score_statistics'].get('std_dev', 0)
                })
        
        # Analyze comparison
        comparison = {
            'queries_analyzed': len(query_results),
            'query_results': query_results,
            'insights': self._generate_relevance_insights(query_results)
        }
        
        return comparison
    
    def _generate_relevance_insights(self, query_results: List[Dict]) -> List[str]:
        """Generate insights from query comparison"""
        insights = []
        
        if not query_results:
            return ["No valid query results to analyze"]
        
        # Find best and worst performing queries
        best_query = max(query_results, key=lambda x: x['avg_score'])
        worst_query = min(query_results, key=lambda x: x['avg_score'])
        
        insights.append(f"Best performing query: '{best_query['query']}' (avg score: {best_query['avg_score']:.3f})")
        insights.append(f"Worst performing query: '{worst_query['query']}' (avg score: {worst_query['avg_score']:.3f})")
        
        # Analyze score variance
        high_variance_queries = [q for q in query_results if q['score_variance'] > 0.1]
        if high_variance_queries:
            insights.append(f"{len(high_variance_queries)} queries show high score variance (>0.1)")
        
        # Analyze result counts
        avg_results = statistics.mean([q['result_count'] for q in query_results])
        insights.append(f"Average results per query: {avg_results:.1f}")
        
        return insights
    
    def analyze_score_patterns(self, min_queries: int = 5) -> Dict[str, Any]:
        """
        Analyze patterns in historical score data
        
        Args:
            min_queries: Minimum number of queries needed for analysis
            
        Returns:
            Pattern analysis results
        """
        if len(self.score_history) < min_queries:
            return {
                'error': f'Need at least {min_queries} queries for pattern analysis. Current: {len(self.score_history)}'
            }
        
        print(f"📊 Analyzing patterns from {len(self.score_history)} queries...")
        
        # Aggregate statistics
        all_scores = []
        query_stats = []
        
        for entry in self.score_history:
            all_scores.extend(entry['scores'])
            query_stats.append({
                'query': entry['query'],
                'mean_score': entry['stats'].get('mean_score', 0),
                'max_score': entry['stats'].get('max_score', 0),
                'result_count': len(entry['scores'])
            })
        
        # Overall patterns
        overall_stats = self._calculate_score_statistics(all_scores)
        
        # Query performance patterns
        performance_patterns = {
            'high_performers': [q for q in query_stats if q['mean_score'] > overall_stats.get('mean_score', 0)],
            'low_performers': [q for q in query_stats if q['mean_score'] < overall_stats.get('mean_score', 0) * 0.8],
            'consistent_queries': [q for q in query_stats if q['result_count'] >= 5]
        }
        
        return {
            'total_queries_analyzed': len(self.score_history),
            'total_documents_scored': len(all_scores),
            'overall_statistics': overall_stats,
            'performance_patterns': performance_patterns,
            'recommendations': self._generate_score_recommendations(overall_stats, performance_patterns)
        }
    
    def _generate_score_recommendations(self, overall_stats: Dict, patterns: Dict) -> List[str]:
        """Generate recommendations based on score analysis"""
        recommendations = []
        
        # Score range analysis
        score_range = overall_stats.get('score_range', 0)
        if score_range < 0.5:
            recommendations.append("Consider using custom scoring profiles to increase score differentiation")
        
        # Low performer analysis
        low_performers = patterns.get('low_performers', [])
        if len(low_performers) > len(patterns.get('high_performers', [])):
            recommendations.append("Many queries show low relevance scores - review query construction and index fields")
        
        # Consistency analysis
        consistent_queries = patterns.get('consistent_queries', [])
        if len(consistent_queries) < len(self.score_history) * 0.5:
            recommendations.append("Many queries return few results - consider broader search strategies")
        
        # Score distribution
        mean_score = overall_stats.get('mean_score', 0)
        if mean_score < 1.0:
            recommendations.append("Overall scores are low - consider boosting relevant fields or using custom scoring")
        
        return recommendations
    
    def test_scoring_strategies(self, base_query: str) -> Dict[str, Any]:
        """
        Test different scoring strategies for a query
        
        Args:
            base_query: Base query to test with different strategies
            
        Returns:
            Comparison of scoring strategies
        """
        print(f"🧪 Testing scoring strategies for query: '{base_query}'")
        
        strategies = {
            'default': {'search_mode': SearchMode.ANY},
            'all_terms': {'search_mode': SearchMode.ALL},
            'exact_phrase': {'search_text': f'"{base_query}"', 'search_mode': SearchMode.ANY}
        }
        
        strategy_results = {}
        
        for strategy_name, params in strategies.items():
            print(f"  Testing strategy: {strategy_name}")
            
            try:
                search_text = params.get('search_text', base_query)
                search_mode = params.get('search_mode', SearchMode.ANY)
                
                results = self.client.search(
                    search_text=search_text,
                    search_mode=search_mode,
                    top=10
                )
                
                scores = []
                documents = []
                
                for doc in results:
                    score = getattr(doc, '@search.score', 0.0)
                    scores.append(score)
                    documents.append({
                        'id': doc.get('hotelId', 'unknown'),
                        'name': doc.get('hotelName', 'Unknown'),
                        'score': score
                    })
                
                strategy_results[strategy_name] = {
                    'documents': documents,
                    'score_stats': self._calculate_score_statistics(scores),
                    'result_count': len(documents)
                }
                
            except Exception as e:
                strategy_results[strategy_name] = {
                    'error': str(e),
                    'documents': [],
                    'score_stats': {},
                    'result_count': 0
                }
        
        # Compare strategies
        comparison = self._compare_strategies(strategy_results)
        
        return {
            'base_query': base_query,
            'strategy_results': strategy_results,
            'comparison': comparison
        }
    
    def _compare_strategies(self, strategy_results: Dict) -> Dict[str, Any]:
        """Compare different scoring strategies"""
        valid_strategies = {k: v for k, v in strategy_results.items() 
                          if 'error' not in v and v['result_count'] > 0}
        
        if not valid_strategies:
            return {'error': 'No valid strategy results to compare'}
        
        # Find best strategy by different metrics
        best_by_max_score = max(valid_strategies.items(), 
                               key=lambda x: x[1]['score_stats'].get('max_score', 0))
        best_by_avg_score = max(valid_strategies.items(), 
                               key=lambda x: x[1]['score_stats'].get('mean_score', 0))
        most_results = max(valid_strategies.items(), 
                          key=lambda x: x[1]['result_count'])
        
        return {
            'strategies_compared': len(valid_strategies),
            'best_max_score': {'strategy': best_by_max_score[0], 'score': best_by_max_score[1]['score_stats'].get('max_score', 0)},
            'best_avg_score': {'strategy': best_by_avg_score[0], 'score': best_by_avg_score[1]['score_stats'].get('mean_score', 0)},
            'most_results': {'strategy': most_results[0], 'count': most_results[1]['result_count']},
            'recommendation': self._recommend_strategy(valid_strategies)
        }
    
    def _recommend_strategy(self, strategies: Dict) -> str:
        """Recommend the best strategy based on analysis"""
        if not strategies:
            return "No valid strategies to recommend"
        
        # Score strategies based on multiple factors
        strategy_scores = {}
        
        for name, result in strategies.items():
            stats = result['score_stats']
            score = (
                stats.get('mean_score', 0) * 0.4 +  # Average relevance
                stats.get('max_score', 0) * 0.3 +   # Best match quality
                (result['result_count'] / 10) * 0.3  # Result coverage
            )
            strategy_scores[name] = score
        
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        return f"Recommended strategy: {best_strategy[0]} (score: {best_strategy[1]:.3f})"

def main():
    """Main function demonstrating search score analysis"""
    # Configuration
    endpoint = os.getenv('SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net')
    api_key = os.getenv('SEARCH_API_KEY', 'your-api-key')
    index_name = os.getenv('INDEX_NAME', 'hotels-sample')
    
    print("🔍 Azure AI Search - Search Scores Analysis")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = SearchScoreAnalyzer(endpoint, index_name, api_key)
    
    # Example 1: Basic score analysis
    print("\n1. Basic Score Analysis")
    print("-" * 25)
    
    result = analyzer.search_with_scores("luxury hotel", top=5)
    if result['result_count'] > 0:
        stats = result['score_statistics']
        print(f"Query: '{result['query']}'")
        print(f"Results: {result['result_count']}")
        print(f"Score range: {stats['min_score']:.3f} - {stats['max_score']:.3f}")
        print(f"Average score: {stats['mean_score']:.3f}")
        print(f"Standard deviation: {stats['std_dev']:.3f}")
        
        print("\nTop results:")
        for i, doc in enumerate(result['documents'][:3], 1):
            name = doc['document'].get('hotelName', 'Unknown')
            score = doc['score']
            print(f"  {i}. {name} (score: {score:.3f})")
    
    # Example 2: Query comparison
    print("\n2. Query Relevance Comparison")
    print("-" * 30)
    
    test_queries = ['luxury', 'beach hotel', 'spa resort', 'budget accommodation']
    comparison = analyzer.compare_query_relevance(test_queries, top=5)
    
    print(f"Analyzed {comparison['queries_analyzed']} queries:")
    for result in comparison['query_results']:
        print(f"  '{result['query']}': avg score {result['avg_score']:.3f}, {result['result_count']} results")
    
    print("\nInsights:")
    for insight in comparison['insights']:
        print(f"  • {insight}")
    
    # Example 3: Scoring strategy testing
    print("\n3. Scoring Strategy Testing")
    print("-" * 30)
    
    strategy_test = analyzer.test_scoring_strategies("ocean view")
    print(f"Base query: '{strategy_test['base_query']}'")
    
    for strategy, result in strategy_test['strategy_results'].items():
        if 'error' not in result:
            stats = result['score_stats']
            print(f"  {strategy}: {result['result_count']} results, avg score: {stats.get('mean_score', 0):.3f}")
        else:
            print(f"  {strategy}: Error - {result['error']}")
    
    print(f"\n{strategy_test['comparison'].get('recommendation', 'No recommendation available')}")
    
    # Example 4: Pattern analysis
    print("\n4. Score Pattern Analysis")
    print("-" * 26)
    
    # Add more queries for pattern analysis
    additional_queries = ['wifi', 'parking', 'restaurant', 'pool', 'gym']
    for query in additional_queries:
        analyzer.search_with_scores(query, top=3)
    
    patterns = analyzer.analyze_score_patterns()
    if 'error' not in patterns:
        print(f"Analyzed {patterns['total_queries_analyzed']} queries")
        print(f"Total documents scored: {patterns['total_documents_scored']}")
        
        overall = patterns['overall_statistics']
        print(f"Overall score statistics:")
        print(f"  Mean: {overall.get('mean_score', 0):.3f}")
        print(f"  Range: {overall.get('score_range', 0):.3f}")
        print(f"  Std Dev: {overall.get('std_dev', 0):.3f}")
        
        print("\nRecommendations:")
        for rec in patterns['recommendations']:
            print(f"  • {rec}")
    else:
        print(f"Pattern analysis error: {patterns['error']}")
    
    print("\n✅ Search score analysis completed!")

if __name__ == "__main__":
    main()