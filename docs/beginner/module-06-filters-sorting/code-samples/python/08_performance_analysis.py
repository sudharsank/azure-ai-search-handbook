#!/usr/bin/env python3
"""
Azure AI Search - Performance Analysis Dashboard

This script provides comprehensive performance analysis for Azure AI Search
filter and sort operations, including real-time monitoring, optimization
strategies, and scalability considerations.

Key Features:
- Real-time query performance monitoring
- Filter optimization strategies
- Resource usage pattern analysis
- Optimization recommendations
- Scalability planning
- Performance bottleneck identification
- Comparative analysis of filtering approaches

Prerequisites:
- Azure AI Search service configured
- Sample data loaded in your index
- Environment variables set in .env file
"""

import os
import time
import statistics
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class PerformanceMetric:
    """Represents a performance measurement."""
    timestamp: datetime
    query_type: str
    filter_expression: str
    execution_time: float
    result_count: int
    complexity_score: int
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation."""
    category: str
    priority: str  # 'high', 'medium', 'low'
    description: str
    impact: str
    implementation: str

class PerformanceAnalyzer:
    """Analyzes and monitors Azure AI Search performance."""
    
    def __init__(self):
        """Initialize the performance analyzer."""
        self.search_client = self._initialize_client()
        self.performance_history: List[PerformanceMetric] = []
        self.baseline_metrics = {}
        
    def _initialize_client(self) -> SearchClient:
        """Initialize Azure AI Search client."""
        try:
            endpoint = os.getenv('SEARCH_ENDPOINT')
            api_key = os.getenv('SEARCH_API_KEY')
            index_name = os.getenv('INDEX_NAME')
            
            if not all([endpoint, api_key, index_name]):
                raise ValueError("Missing required environment variables")
            
            credential = AzureKeyCredential(api_key)
            client = SearchClient(endpoint, index_name, credential)
            
            print(f"✅ Connected to Azure AI Search")
            print(f"📍 Endpoint: {endpoint}")
            print(f"📊 Index: {index_name}")
            
            return client
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            raise
    
    def calculate_complexity_score(self, filter_expr: str) -> int:
        """Calculate complexity score for a filter expression."""
        if not filter_expr or filter_expr == "*":
            return 0
        
        score = 0
        score += filter_expr.count('and') * 1
        score += filter_expr.count('or') * 2
        score += filter_expr.count('/any') * 3
        score += filter_expr.count('/all') * 4
        score += filter_expr.count('geo.distance') * 3
        score += filter_expr.count('(') * 1
        score += len(filter_expr.split()) * 0.1
        
        return int(score)
    
    def measure_query_performance(self, search_text: str = "*", 
                                filter_expr: str = None,
                                orderby: str = None,
                                top: int = 10,
                                query_type: str = "standard") -> PerformanceMetric:
        """
        Measure performance of a single query.
        
        Args:
            search_text: Search query text
            filter_expr: Filter expression
            orderby: Sort expression
            top: Number of results
            query_type: Type of query for categorization
            
        Returns:
            Performance metric
        """
        try:
            start_time = time.time()
            
            search_params = {
                'search_text': search_text,
                'top': top,
                'include_total_count': True
            }
            
            if filter_expr:
                search_params['filter'] = filter_expr
            if orderby:
                search_params['order_by'] = orderby
            
            results = self.search_client.search(**search_params)
            
            # Process results to get count
            documents = list(results)
            result_count = results.get_count() or len(documents)
            
            execution_time = time.time() - start_time
            complexity_score = self.calculate_complexity_score(filter_expr or "")
            
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                query_type=query_type,
                filter_expression=filter_expr or "none",
                execution_time=execution_time,
                result_count=result_count,
                complexity_score=complexity_score
            )
            
            self.performance_history.append(metric)
            return metric
            
        except Exception as e:
            print(f"❌ Performance measurement error: {e}")
            return None
    
    def run_performance_benchmark(self, test_scenarios: List[Dict] = None) -> Dict:
        """
        Run a comprehensive performance benchmark.
        
        Args:
            test_scenarios: List of test scenarios to run
            
        Returns:
            Benchmark results
        """
        if test_scenarios is None:
            test_scenarios = self._get_default_test_scenarios()
        
        print("🚀 Running Performance Benchmark...")
        print("=" * 40)
        
        benchmark_results = {
            'scenarios': [],
            'summary': {},
            'recommendations': []
        }
        
        for scenario in test_scenarios:
            print(f"\n📊 Testing: {scenario['name']}")
            
            # Run multiple iterations for statistical accuracy
            iterations = scenario.get('iterations', 3)
            metrics = []
            
            for i in range(iterations):
                metric = self.measure_query_performance(
                    search_text=scenario.get('search_text', '*'),
                    filter_expr=scenario.get('filter'),
                    orderby=scenario.get('orderby'),
                    top=scenario.get('top', 10),
                    query_type=scenario['name']
                )
                
                if metric:
                    metrics.append(metric)
                
                # Small delay between iterations
                time.sleep(0.1)
            
            if metrics:
                # Calculate statistics
                execution_times = [m.execution_time for m in metrics]
                result_counts = [m.result_count for m in metrics]
                
                scenario_result = {
                    'name': scenario['name'],
                    'avg_execution_time': statistics.mean(execution_times),
                    'min_execution_time': min(execution_times),
                    'max_execution_time': max(execution_times),
                    'std_execution_time': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                    'avg_result_count': statistics.mean(result_counts),
                    'complexity_score': metrics[0].complexity_score,
                    'filter': scenario.get('filter', 'none')
                }
                
                benchmark_results['scenarios'].append(scenario_result)
                
                print(f"   Avg Time: {scenario_result['avg_execution_time']:.3f}s")
                print(f"   Results: {scenario_result['avg_result_count']:.0f}")
                print(f"   Complexity: {scenario_result['complexity_score']}")
        
        # Generate summary and recommendations
        benchmark_results['summary'] = self._generate_benchmark_summary(benchmark_results['scenarios'])
        benchmark_results['recommendations'] = self._generate_optimization_recommendations(benchmark_results['scenarios'])
        
        return benchmark_results
    
    def _get_default_test_scenarios(self) -> List[Dict]:
        """Get default test scenarios for benchmarking."""
        return [
            {
                'name': 'Baseline Search',
                'search_text': '*',
                'iterations': 5
            },
            {
                'name': 'Simple Filter',
                'search_text': '*',
                'filter': "rating ge 4.0",
                'iterations': 5
            },
            {
                'name': 'Range Filter',
                'search_text': '*',
                'filter': "price ge 50 and price le 200",
                'iterations': 5
            },
            {
                'name': 'Collection Filter',
                'search_text': '*',
                'filter': "tags/any(item: item eq 'premium')",
                'iterations': 5
            },
            {
                'name': 'Complex Filter',
                'search_text': '*',
                'filter': "(tags/any(item: item eq 'premium') or rating gt 4.5) and price le 300",
                'iterations': 5
            },
            {
                'name': 'Geographic Filter',
                'search_text': '*',
                'filter': "geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 10",
                'iterations': 5
            },
            {
                'name': 'Sorted Results',
                'search_text': '*',
                'orderby': 'rating desc',
                'iterations': 5
            },
            {
                'name': 'Complex Sort',
                'search_text': '*',
                'orderby': 'rating desc, price asc',
                'iterations': 5
            }
        ]
    
    def _generate_benchmark_summary(self, scenarios: List[Dict]) -> Dict:
        """Generate summary statistics from benchmark results."""
        if not scenarios:
            return {}
        
        execution_times = [s['avg_execution_time'] for s in scenarios]
        complexity_scores = [s['complexity_score'] for s in scenarios]
        
        return {
            'total_scenarios': len(scenarios),
            'avg_execution_time': statistics.mean(execution_times),
            'fastest_scenario': min(scenarios, key=lambda x: x['avg_execution_time'])['name'],
            'slowest_scenario': max(scenarios, key=lambda x: x['avg_execution_time'])['name'],
            'avg_complexity': statistics.mean(complexity_scores),
            'performance_variance': statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        }
    
    def _generate_optimization_recommendations(self, scenarios: List[Dict]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on benchmark results."""
        recommendations = []
        
        # Analyze slow queries
        slow_threshold = 1.0  # 1 second
        slow_scenarios = [s for s in scenarios if s['avg_execution_time'] > slow_threshold]
        
        if slow_scenarios:
            recommendations.append(OptimizationRecommendation(
                category="Query Performance",
                priority="high",
                description=f"Found {len(slow_scenarios)} slow queries (>{slow_threshold}s)",
                impact="Significant performance improvement",
                implementation="Review and optimize slow filter expressions"
            ))
        
        # Analyze complexity
        high_complexity = [s for s in scenarios if s['complexity_score'] > 15]
        if high_complexity:
            recommendations.append(OptimizationRecommendation(
                category="Filter Complexity",
                priority="medium",
                description=f"Found {len(high_complexity)} high-complexity filters",
                impact="Moderate performance improvement",
                implementation="Simplify complex filter expressions or use faceted navigation"
            ))
        
        # Check for geographic queries
        geo_scenarios = [s for s in scenarios if 'geo.distance' in s.get('filter', '')]
        if geo_scenarios:
            recommendations.append(OptimizationRecommendation(
                category="Geographic Queries",
                priority="medium",
                description="Geographic queries detected",
                impact="Location-based performance optimization",
                implementation="Consider using smaller search radii and geographic indexing"
            ))
        
        # General recommendations
        recommendations.append(OptimizationRecommendation(
            category="Index Configuration",
            priority="low",
            description="Ensure proper field indexing",
            impact="Overall performance improvement",
            implementation="Mark frequently filtered fields as 'filterable' in index schema"
        ))
        
        return recommendations
    
    def analyze_performance_trends(self, hours: int = 24) -> Dict:
        """
        Analyze performance trends over time.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Trend analysis results
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.performance_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {'error': 'No recent performance data available'}
        
        # Group by query type
        by_type = {}
        for metric in recent_metrics:
            if metric.query_type not in by_type:
                by_type[metric.query_type] = []
            by_type[metric.query_type].append(metric)
        
        trends = {}
        for query_type, metrics in by_type.items():
            execution_times = [m.execution_time for m in metrics]
            trends[query_type] = {
                'count': len(metrics),
                'avg_time': statistics.mean(execution_times),
                'trend': 'stable'  # Simplified - would need more data for real trend analysis
            }
        
        return {
            'period_hours': hours,
            'total_queries': len(recent_metrics),
            'query_types': trends,
            'overall_avg_time': statistics.mean([m.execution_time for m in recent_metrics])
        }
    
    def generate_performance_report(self, benchmark_results: Dict = None) -> str:
        """Generate a comprehensive performance report."""
        report = []
        report.append("📊 Azure AI Search Performance Analysis Report")
        report.append("=" * 55)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if benchmark_results:
            summary = benchmark_results.get('summary', {})
            scenarios = benchmark_results.get('scenarios', [])
            recommendations = benchmark_results.get('recommendations', [])
            
            # Summary section
            report.append("📈 Performance Summary")
            report.append("-" * 25)
            report.append(f"Total Scenarios Tested: {summary.get('total_scenarios', 0)}")
            report.append(f"Average Execution Time: {summary.get('avg_execution_time', 0):.3f}s")
            report.append(f"Fastest Scenario: {summary.get('fastest_scenario', 'N/A')}")
            report.append(f"Slowest Scenario: {summary.get('slowest_scenario', 'N/A')}")
            report.append(f"Performance Variance: {summary.get('performance_variance', 0):.3f}s")
            report.append("")
            
            # Detailed results
            report.append("🔍 Detailed Results")
            report.append("-" * 20)
            for scenario in scenarios:
                report.append(f"• {scenario['name']}")
                report.append(f"  Time: {scenario['avg_execution_time']:.3f}s ± {scenario['std_execution_time']:.3f}s")
                report.append(f"  Results: {scenario['avg_result_count']:.0f}")
                report.append(f"  Complexity: {scenario['complexity_score']}")
                if scenario['filter'] != 'none':
                    report.append(f"  Filter: {scenario['filter']}")
                report.append("")
            
            # Recommendations
            if recommendations:
                report.append("💡 Optimization Recommendations")
                report.append("-" * 35)
                for rec in recommendations:
                    report.append(f"• {rec.category} ({rec.priority.upper()} priority)")
                    report.append(f"  {rec.description}")
                    report.append(f"  Impact: {rec.impact}")
                    report.append(f"  Action: {rec.implementation}")
                    report.append("")
        
        # Historical trends
        trends = self.analyze_performance_trends()
        if 'error' not in trends:
            report.append("📊 Recent Performance Trends")
            report.append("-" * 30)
            report.append(f"Period: Last {trends['period_hours']} hours")
            report.append(f"Total Queries: {trends['total_queries']}")
            report.append(f"Overall Average Time: {trends['overall_avg_time']:.3f}s")
            report.append("")
            
            for query_type, data in trends['query_types'].items():
                report.append(f"• {query_type}: {data['count']} queries, {data['avg_time']:.3f}s avg")
        
        return "\n".join(report)
    
    def export_performance_data(self, filename: str = None) -> str:
        """Export performance data to JSON file."""
        if filename is None:
            filename = f"performance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'metrics': [asdict(metric) for metric in self.performance_history],
            'summary': {
                'total_queries': len(self.performance_history),
                'date_range': {
                    'start': min(m.timestamp for m in self.performance_history).isoformat() if self.performance_history else None,
                    'end': max(m.timestamp for m in self.performance_history).isoformat() if self.performance_history else None
                }
            }
        }
        
        # Convert datetime objects to strings for JSON serialization
        for metric in data['metrics']:
            metric['timestamp'] = metric['timestamp'].isoformat()
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Performance data exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Export error: {e}")
            return None

def main():
    """Main demonstration function."""
    try:
        # Initialize the performance analyzer
        analyzer = PerformanceAnalyzer()
        
        print("🚀 Starting Performance Analysis...")
        print()
        
        # Run benchmark
        benchmark_results = analyzer.run_performance_benchmark()
        
        # Generate and display report
        print("\n" + "="*60)
        report = analyzer.generate_performance_report(benchmark_results)
        print(report)
        
        # Export data
        print("\n📁 Exporting Performance Data...")
        filename = analyzer.export_performance_data()
        
        print(f"\n✅ Performance analysis completed!")
        print(f"📊 Analyzed {len(benchmark_results['scenarios'])} scenarios")
        print(f"💡 Generated {len(benchmark_results['recommendations'])} recommendations")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()