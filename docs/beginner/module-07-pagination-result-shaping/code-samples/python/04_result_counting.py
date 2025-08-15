"""
Module 7: Result Counting and Metadata

This example demonstrates how to implement result counting, manage total counts,
and work with search metadata for better user experience and performance optimization.
"""

import os
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY', 'your-api-key')
INDEX_NAME = os.getenv('INDEX_NAME', 'hotels-sample')


@dataclass
class CountingResult:
    """Data class for result counting operations"""
    documents: List[Dict[str, Any]]
    total_count: Optional[int]
    estimated_count: Optional[int]
    has_more_results: bool
    duration_ms: float
    query: str
    page_size: int
    skip: int
    count_accuracy: str  # 'exact', 'estimate', 'unknown'


@dataclass
class CountingMetrics:
    """Data class for counting performance metrics"""
    query: str
    with_count_duration: float
    without_count_duration: float
    count_overhead_ms: float
    count_overhead_percentage: float
    total_results: Optional[int]
    timestamp: float


class ResultCounter:
    """
    Result counter for managing search result counts and metadata.
    
    This class provides functionality to efficiently handle result counting,
    estimate totals, and optimize counting performance.
    """
    
    def __init__(self, search_client: SearchClient):
        """
        Initialize the result counter.
        
        Args:
            search_client: Azure AI Search client
        """
        self.search_client = search_client
        self.count_cache: Dict[str, Dict[str, Any]] = {}
        self.metrics: List[CountingMetrics] = []
    
    def search_with_count(self, search_text: str, 
                         include_count: bool = True,
                         **kwargs) -> CountingResult:
        """
        Search with optional result counting.
        
        Args:
            search_text: Search query
            include_count: Whether to include total count
            **kwargs: Additional search parameters
            
        Returns:
            CountingResult with count information
        """
        try:
            print(f"Searching with count={include_count}: '{search_text}'")
            
            start_time = time.time()
            
            # Perform search
            results = self.search_client.search(
                search_text=search_text,
                include_total_count=include_count,
                top=kwargs.get('top', 10),
                skip=kwargs.get('skip', 0),
                **{k: v for k, v in kwargs.items() 
                   if k not in ['top', 'skip']}
            )
            
            # Convert to list and get count
            documents = list(results)
            total_count = getattr(results, 'get_count', lambda: None)()
            
            duration = (time.time() - start_time) * 1000
            
            # Determine count accuracy
            count_accuracy = 'exact' if include_count and total_count is not None else 'unknown'
            
            # Estimate if we have more results
            page_size = kwargs.get('top', 10)
            skip = kwargs.get('skip', 0)
            has_more = len(documents) == page_size
            
            if total_count is not None:
                has_more = (skip + len(documents)) < total_count
            
            print(f"Search completed in {duration:.1f}ms")
            if total_count is not None:
                print(f"Total count: {total_count}")
            else:
                print("Count not requested/available")
            
            return CountingResult(
                documents=documents,
                total_count=total_count,
                estimated_count=None,  # Could implement estimation logic
                has_more_results=has_more,
                duration_ms=duration,
                query=search_text,
                page_size=page_size,
                skip=skip,
                count_accuracy=count_accuracy
            )
            
        except Exception as e:
            print(f"Search with count error: {e}")
            raise
    
    def compare_count_performance(self, search_text: str, 
                                iterations: int = 3) -> CountingMetrics:
        """
        Compare performance with and without counting.
        
        Args:
            search_text: Search query
            iterations: Number of test iterations
            
        Returns:
            CountingMetrics with performance comparison
        """
        print(f"Comparing count performance for: '{search_text}'")
        
        with_count_times = []
        without_count_times = []
        total_results = None
        
        # Test with counting
        for i in range(iterations):
            result = self.search_with_count(search_text, include_count=True, top=10)
            with_count_times.append(result.duration_ms)
            if total_results is None:
                total_results = result.total_count
        
        # Test without counting
        for i in range(iterations):
            result = self.search_with_count(search_text, include_count=False, top=10)
            without_count_times.append(result.duration_ms)
        
        # Calculate averages
        avg_with_count = sum(with_count_times) / len(with_count_times)
        avg_without_count = sum(without_count_times) / len(without_count_times)
        
        count_overhead = avg_with_count - avg_without_count
        overhead_percentage = (count_overhead / avg_without_count) * 100 if avg_without_count > 0 else 0
        
        metrics = CountingMetrics(
            query=search_text,
            with_count_duration=avg_with_count,
            without_count_duration=avg_without_count,
            count_overhead_ms=count_overhead,
            count_overhead_percentage=overhead_percentage,
            total_results=total_results,
            timestamp=time.time()
        )
        
        self.metrics.append(metrics)
        
        print(f"With count: {avg_with_count:.1f}ms")
        print(f"Without count: {avg_without_count:.1f}ms")
        print(f"Count overhead: {count_overhead:.1f}ms ({overhead_percentage:.1f}%)")
        
        return metrics
    
    def estimate_total_results(self, search_text: str, 
                             sample_pages: int = 3,
                             page_size: int = 50) -> Dict[str, Any]:
        """
        Estimate total results without expensive counting.
        
        Args:
            search_text: Search query
            sample_pages: Number of pages to sample
            page_size: Size of each sample page
            
        Returns:
            Estimation results
        """
        print(f"Estimating total results for: '{search_text}'")
        
        try:
            estimation_data = {
                'query': search_text,
                'sample_pages': sample_pages,
                'page_size': page_size,
                'pages_sampled': 0,
                'total_documents_seen': 0,
                'estimated_total': None,
                'confidence': 'unknown',
                'method': 'sampling'
            }
            
            last_page_size = page_size
            
            for page in range(sample_pages):
                result = self.search_with_count(
                    search_text,
                    include_count=False,
                    skip=page * page_size,
                    top=page_size
                )
                
                estimation_data['pages_sampled'] += 1
                estimation_data['total_documents_seen'] += len(result.documents)
                
                # If we get less than a full page, we've reached the end
                if len(result.documents) < page_size:
                    estimation_data['estimated_total'] = estimation_data['total_documents_seen']
                    estimation_data['confidence'] = 'exact'
                    estimation_data['method'] = 'complete_sampling'
                    break
                
                last_page_size = len(result.documents)
            
            # If we didn't reach the end, estimate based on consistent page sizes
            if estimation_data['estimated_total'] is None:
                if last_page_size == page_size:
                    # Assume there are more pages, make a conservative estimate
                    avg_per_page = estimation_data['total_documents_seen'] / estimation_data['pages_sampled']
                    # Estimate there are at least 2x more pages (conservative)
                    estimated_pages = estimation_data['pages_sampled'] * 3
                    estimation_data['estimated_total'] = int(avg_per_page * estimated_pages)
                    estimation_data['confidence'] = 'low'
                    estimation_data['method'] = 'extrapolation'
                else:
                    estimation_data['estimated_total'] = estimation_data['total_documents_seen']
                    estimation_data['confidence'] = 'medium'
                    estimation_data['method'] = 'partial_sampling'
            
            print(f"Estimation: {estimation_data['estimated_total']} results "
                  f"(confidence: {estimation_data['confidence']})")
            
            return estimation_data
            
        except Exception as e:
            print(f"Estimation error: {e}")
            return {'error': str(e)}
    
    def get_count_with_caching(self, search_text: str, 
                              cache_duration: int = 300) -> Optional[int]:
        """
        Get result count with caching to improve performance.
        
        Args:
            search_text: Search query
            cache_duration: Cache duration in seconds
            
        Returns:
            Cached or fresh count
        """
        cache_key = f"count_{hash(search_text)}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.count_cache:
            cached_data = self.count_cache[cache_key]
            if current_time - cached_data['timestamp'] < cache_duration:
                print(f"Using cached count: {cached_data['count']}")
                return cached_data['count']
        
        # Get fresh count
        print(f"Fetching fresh count for: '{search_text}'")
        result = self.search_with_count(search_text, include_count=True, top=1)
        
        # Cache the result
        self.count_cache[cache_key] = {
            'count': result.total_count,
            'timestamp': current_time,
            'query': search_text
        }
        
        return result.total_count
    
    def analyze_count_patterns(self, queries: List[str]) -> Dict[str, Any]:
        """
        Analyze counting patterns across multiple queries.
        
        Args:
            queries: List of search queries to analyze
            
        Returns:
            Pattern analysis results
        """
        print(f"Analyzing count patterns for {len(queries)} queries")
        
        analysis = {
            'queries_analyzed': len(queries),
            'total_overhead_ms': 0,
            'avg_overhead_ms': 0,
            'max_overhead_ms': 0,
            'min_overhead_ms': float('inf'),
            'overhead_by_result_size': {},
            'recommendations': []
        }
        
        for query in queries:
            try:
                metrics = self.compare_count_performance(query, iterations=2)
                
                analysis['total_overhead_ms'] += metrics.count_overhead_ms
                analysis['max_overhead_ms'] = max(analysis['max_overhead_ms'], metrics.count_overhead_ms)
                analysis['min_overhead_ms'] = min(analysis['min_overhead_ms'], metrics.count_overhead_ms)
                
                # Categorize by result size
                if metrics.total_results is not None:
                    if metrics.total_results < 100:
                        category = 'small'
                    elif metrics.total_results < 1000:
                        category = 'medium'
                    else:
                        category = 'large'
                    
                    if category not in analysis['overhead_by_result_size']:
                        analysis['overhead_by_result_size'][category] = []
                    
                    analysis['overhead_by_result_size'][category].append(metrics.count_overhead_ms)
                
            except Exception as e:
                print(f"Error analyzing query '{query}': {e}")
        
        # Calculate averages
        if len(queries) > 0:
            analysis['avg_overhead_ms'] = analysis['total_overhead_ms'] / len(queries)
        
        # Calculate category averages
        for category, overheads in analysis['overhead_by_result_size'].items():
            if overheads:
                avg_overhead = sum(overheads) / len(overheads)
                analysis['overhead_by_result_size'][category] = {
                    'avg_overhead_ms': avg_overhead,
                    'samples': len(overheads)
                }
        
        # Generate recommendations
        if analysis['avg_overhead_ms'] > 50:
            analysis['recommendations'].append("Consider disabling counts for performance-critical scenarios")
        
        if analysis['avg_overhead_ms'] < 10:
            analysis['recommendations'].append("Count overhead is minimal, safe to use counts")
        
        return analysis
    
    def get_smart_count_strategy(self, search_text: str, 
                               context: str = 'general') -> Dict[str, Any]:
        """
        Get intelligent counting strategy based on context.
        
        Args:
            search_text: Search query
            context: Usage context ('pagination', 'display', 'api', 'analytics')
            
        Returns:
            Recommended counting strategy
        """
        strategies = {
            'pagination': {
                'include_count': True,
                'reason': 'Pagination requires total count for page calculation',
                'cache_duration': 60,
                'estimate_threshold': 10000
            },
            'display': {
                'include_count': True,
                'reason': 'Users expect to see result counts',
                'cache_duration': 300,
                'estimate_threshold': 5000
            },
            'api': {
                'include_count': False,
                'reason': 'API performance is critical, count on demand',
                'cache_duration': 600,
                'estimate_threshold': 1000
            },
            'analytics': {
                'include_count': True,
                'reason': 'Analytics require accurate counts',
                'cache_duration': 3600,
                'estimate_threshold': None
            },
            'search_as_you_type': {
                'include_count': False,
                'reason': 'Real-time search needs fast response',
                'cache_duration': 30,
                'estimate_threshold': 100
            }
        }
        
        strategy = strategies.get(context, strategies['general'] if 'general' in strategies else strategies['display'])
        
        # Add query-specific recommendations
        strategy['query'] = search_text
        strategy['context'] = context
        
        # Estimate complexity
        if len(search_text.split()) > 5:
            strategy['complexity'] = 'high'
            strategy['include_count'] = False
            strategy['reason'] += ' (complex query detected)'
        else:
            strategy['complexity'] = 'low'
        
        return strategy


def demonstrate_basic_counting():
    """Demonstrate basic result counting functionality."""
    print("=== Basic Result Counting Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        # Search with count
        print("1. Search with count enabled:")
        result_with_count = counter.search_with_count('hotel', include_count=True, top=5)
        
        print(f"Query: '{result_with_count.query}'")
        print(f"Results returned: {len(result_with_count.documents)}")
        print(f"Total count: {result_with_count.total_count}")
        print(f"Has more results: {result_with_count.has_more_results}")
        print(f"Count accuracy: {result_with_count.count_accuracy}")
        
        # Search without count
        print("\n2. Search without count:")
        result_without_count = counter.search_with_count('hotel', include_count=False, top=5)
        
        print(f"Results returned: {len(result_without_count.documents)}")
        print(f"Total count: {result_without_count.total_count}")
        print(f"Has more results: {result_without_count.has_more_results}")
        print(f"Count accuracy: {result_without_count.count_accuracy}")
        
    except Exception as e:
        print(f"Basic counting demo error: {e}")


def demonstrate_count_performance():
    """Demonstrate count performance comparison."""
    print("\n=== Count Performance Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        queries = ['luxury', 'beach resort', 'spa', 'business hotel']
        
        for query in queries:
            print(f"Testing query: '{query}'")
            metrics = counter.compare_count_performance(query, iterations=2)
            
            print(f"  Overhead: {metrics.count_overhead_ms:.1f}ms "
                  f"({metrics.count_overhead_percentage:.1f}%)")
            print(f"  Total results: {metrics.total_results}")
            print()
        
    except Exception as e:
        print(f"Count performance demo error: {e}")


def demonstrate_result_estimation():
    """Demonstrate result estimation techniques."""
    print("=== Result Estimation Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        queries = ['hotel', 'luxury resort']
        
        for query in queries:
            print(f"Estimating results for: '{query}'")
            
            # Get actual count for comparison
            actual_result = counter.search_with_count(query, include_count=True, top=1)
            actual_count = actual_result.total_count
            
            # Get estimation
            estimation = counter.estimate_total_results(query, sample_pages=2, page_size=20)
            
            if 'error' not in estimation:
                estimated_count = estimation['estimated_total']
                confidence = estimation['confidence']
                method = estimation['method']
                
                print(f"  Actual count: {actual_count}")
                print(f"  Estimated count: {estimated_count}")
                print(f"  Confidence: {confidence}")
                print(f"  Method: {method}")
                
                if actual_count and estimated_count:
                    accuracy = abs(actual_count - estimated_count) / actual_count * 100
                    print(f"  Accuracy: {100 - accuracy:.1f}%")
            else:
                print(f"  Estimation failed: {estimation['error']}")
            
            print()
        
    except Exception as e:
        print(f"Result estimation demo error: {e}")


def demonstrate_count_caching():
    """Demonstrate count caching functionality."""
    print("=== Count Caching Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        query = 'spa hotel'
        
        # First call - should fetch fresh
        print("1. First call (fresh fetch):")
        start_time = time.time()
        count1 = counter.get_count_with_caching(query, cache_duration=60)
        duration1 = (time.time() - start_time) * 1000
        print(f"Count: {count1}, Duration: {duration1:.1f}ms")
        
        # Second call - should use cache
        print("\n2. Second call (cached):")
        start_time = time.time()
        count2 = counter.get_count_with_caching(query, cache_duration=60)
        duration2 = (time.time() - start_time) * 1000
        print(f"Count: {count2}, Duration: {duration2:.1f}ms")
        
        print(f"\nCache speedup: {duration1 / max(duration2, 1):.1f}x faster")
        
    except Exception as e:
        print(f"Count caching demo error: {e}")


def demonstrate_smart_counting_strategy():
    """Demonstrate smart counting strategy selection."""
    print("\n=== Smart Counting Strategy Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        query = 'luxury hotel'
        contexts = ['pagination', 'display', 'api', 'analytics', 'search_as_you_type']
        
        print(f"Smart strategies for query: '{query}'\n")
        
        for context in contexts:
            strategy = counter.get_smart_count_strategy(query, context)
            
            print(f"{context.upper()}:")
            print(f"  Include count: {strategy['include_count']}")
            print(f"  Reason: {strategy['reason']}")
            print(f"  Cache duration: {strategy['cache_duration']}s")
            print(f"  Complexity: {strategy['complexity']}")
            print()
        
    except Exception as e:
        print(f"Smart counting strategy demo error: {e}")


def demonstrate_counting_with_pagination():
    """Demonstrate counting in pagination scenarios."""
    print("=== Counting with Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        query = 'hotel'
        page_size = 5
        
        # First page with count
        print("Page 1 (with count):")
        page1 = counter.search_with_count(
            query, 
            include_count=True, 
            top=page_size, 
            skip=0
        )
        
        total_count = page1.total_count
        total_pages = (total_count + page_size - 1) // page_size if total_count else 0
        
        print(f"  Results: {len(page1.documents)}")
        print(f"  Total count: {total_count}")
        print(f"  Total pages: {total_pages}")
        print(f"  Duration: {page1.duration_ms:.1f}ms")
        
        # Subsequent pages without count
        print("\nPage 2 (without count):")
        page2 = counter.search_with_count(
            query, 
            include_count=False, 
            top=page_size, 
            skip=page_size
        )
        
        print(f"  Results: {len(page2.documents)}")
        print(f"  Total count: {page2.total_count}")
        print(f"  Duration: {page2.duration_ms:.1f}ms")
        
        # Show performance difference
        if page1.duration_ms > 0 and page2.duration_ms > 0:
            speedup = page1.duration_ms / page2.duration_ms
            print(f"\nSubsequent page speedup: {speedup:.1f}x faster")
        
    except Exception as e:
        print(f"Counting with pagination demo error: {e}")


def demonstrate_count_analysis():
    """Demonstrate comprehensive count analysis."""
    print("\n=== Count Analysis Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    counter = ResultCounter(search_client)
    
    try:
        queries = ['hotel', 'luxury', 'beach', 'spa wellness']
        
        print("Analyzing count patterns...")
        analysis = counter.analyze_count_patterns(queries)
        
        print(f"\nAnalysis Results:")
        print(f"Queries analyzed: {analysis['queries_analyzed']}")
        print(f"Average overhead: {analysis['avg_overhead_ms']:.1f}ms")
        print(f"Max overhead: {analysis['max_overhead_ms']:.1f}ms")
        print(f"Min overhead: {analysis['min_overhead_ms']:.1f}ms")
        
        print("\nOverhead by result size:")
        for category, data in analysis['overhead_by_result_size'].items():
            if isinstance(data, dict):
                print(f"  {category}: {data['avg_overhead_ms']:.1f}ms "
                      f"({data['samples']} samples)")
        
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
        
    except Exception as e:
        print(f"Count analysis demo error: {e}")


class CountingHelper:
    """Utility class for common counting patterns."""
    
    @staticmethod
    def should_include_count(context: str, query_complexity: str = 'low') -> bool:
        """Determine if count should be included based on context."""
        count_contexts = {
            'pagination': True,
            'display': True,
            'analytics': True,
            'api': False,
            'search_as_you_type': False,
            'autocomplete': False
        }
        
        base_decision = count_contexts.get(context, True)
        
        # Adjust for query complexity
        if query_complexity == 'high' and context in ['api', 'search_as_you_type']:
            return False
        
        return base_decision
    
    @staticmethod
    def get_cache_duration(context: str) -> int:
        """Get appropriate cache duration for context."""
        durations = {
            'pagination': 60,      # 1 minute
            'display': 300,        # 5 minutes
            'api': 600,           # 10 minutes
            'analytics': 3600,     # 1 hour
            'search_as_you_type': 30,  # 30 seconds
            'autocomplete': 30     # 30 seconds
        }
        
        return durations.get(context, 300)
    
    @staticmethod
    def format_count(count: Optional[int], 
                    show_exact: bool = True,
                    threshold: int = 10000) -> str:
        """Format count for display."""
        if count is None:
            return "Unknown"
        
        if not show_exact and count > threshold:
            if count > 1000000:
                return f"{count // 1000000}M+"
            elif count > 1000:
                return f"{count // 1000}K+"
        
        return f"{count:,}"


if __name__ == "__main__":
    try:
        demonstrate_basic_counting()
        demonstrate_count_performance()
        demonstrate_result_estimation()
        demonstrate_count_caching()
        demonstrate_smart_counting_strategy()
        demonstrate_counting_with_pagination()
        demonstrate_count_analysis()
        
        # Show helper usage
        print("\n=== Counting Helper Demo ===\n")
        helper = CountingHelper()
        
        print("Should include count:")
        contexts = ['pagination', 'api', 'analytics']
        for context in contexts:
            should_count = helper.should_include_count(context)
            cache_duration = helper.get_cache_duration(context)
            print(f"  {context}: {should_count} (cache: {cache_duration}s)")
        
        print("\nCount formatting:")
        counts = [42, 1234, 15678, 1234567, None]
        for count in counts:
            exact = helper.format_count(count, show_exact=True)
            approx = helper.format_count(count, show_exact=False, threshold=1000)
            print(f"  {count}: exact='{exact}', approx='{approx}'")
        
    except Exception as e:
        print(f"Demo failed: {e}")