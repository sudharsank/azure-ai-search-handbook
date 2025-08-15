#!/usr/bin/env python3
"""
Module 7: Pagination & Result Shaping - Performance Optimization
Azure AI Search Python SDK Example

This example demonstrates comprehensive performance optimization techniques for pagination
and result shaping, including caching, connection pooling, monitoring, and best practices.

Prerequisites:
- Azure AI Search service
- Python 3.7+
- azure-search-documents package
- Sample data index with substantial data
"""

import os
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json
from azure.search.documents import SearchClient
from azure.search.documents.aio import SearchClient as AsyncSearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    total_requests: int = 0
    total_time_ms: float = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    avg_response_time_ms: float = 0
    throughput_requests_per_sec: float = 0
    memory_usage_mb: float = 0
    
    def update_averages(self):
        """Update calculated averages"""
        if self.total_requests > 0:
            self.avg_response_time_ms = self.total_time_ms / self.total_requests
            self.throughput_requests_per_sec = self.total_requests / (self.total_time_ms / 1000) if self.total_time_ms > 0 else 0

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: float
    access_count: int = 0
    size_bytes: int = 0

class PerformanceOptimizer:
    """Comprehensive performance optimization for Azure AI Search"""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str, 
                 cache_ttl: int = 300, max_cache_size: int = 1000):
        """
        Initialize the performance optimizer
        
        Args:
            endpoint: Azure AI Search endpoint
            index_name: Search index name
            api_key: API key
            cache_ttl: Cache time-to-live in seconds
            max_cache_size: Maximum number of cache entries
        """
        self.client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.request_history = []
        
        # Caching system
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.cache_lock = threading.RLock()
        
        # Connection pooling and optimization
        self.connection_pool_size = 10
        self.request_timeout = 30
        
        # Performance monitoring
        self.slow_query_threshold_ms = 1000
        self.slow_queries = []
    
    def _generate_cache_key(self, query: str, **kwargs) -> str:
        """Generate a cache key for the request"""
        cache_data = {'query': query, **kwargs}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        with self.cache_lock:
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                # Check if entry is still valid
                if time.time() - entry.timestamp < self.cache_ttl:
                    entry.access_count += 1
                    self.metrics.cache_hits += 1
                    return entry.data
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
            
            self.metrics.cache_misses += 1
            return None
    
    def _store_in_cache(self, cache_key: str, data: Any):
        """Store data in cache with size management"""
        with self.cache_lock:
            # Estimate size
            data_size = len(json.dumps(data, default=str)) if data else 0
            
            # Manage cache size
            if len(self.cache) >= self.max_cache_size:
                self._evict_cache_entries()
            
            # Store entry
            self.cache[cache_key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                size_bytes=data_size
            )
    
    def _evict_cache_entries(self):
        """Evict least recently used cache entries"""
        if not self.cache:
            return
        
        # Sort by access count and timestamp (LRU)
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: (x[1].access_count, x[1].timestamp)
        )
        
        # Remove oldest 25% of entries
        entries_to_remove = len(sorted_entries) // 4
        for i in range(entries_to_remove):
            cache_key = sorted_entries[i][0]
            del self.cache[cache_key]
    
    def optimized_search(self, query: str, skip: int = 0, top: int = 20,
                        select_fields: Optional[List[str]] = None,
                        use_cache: bool = True,
                        **kwargs) -> Dict[str, Any]:
        """
        Optimized search with caching and performance monitoring
        
        Args:
            query: Search query
            skip: Number of results to skip
            top: Number of results to return
            select_fields: Fields to select
            use_cache: Whether to use caching
            **kwargs: Additional search parameters
            
        Returns:
            Search results with performance metadata
        """
        start_time = time.time()
        
        # Generate cache key
        cache_params = {
            'skip': skip,
            'top': top,
            'select_fields': select_fields,
            **kwargs
        }
        cache_key = self._generate_cache_key(query, **cache_params)
        
        # Try cache first
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                cached_result['from_cache'] = True
                cached_result['cache_key'] = cache_key
                return cached_result
        
        try:
            # Perform search with optimizations
            search_params = {
                'search_text': query,
                'skip': skip,
                'top': top,
                'select': select_fields,
                **kwargs
            }
            
            results = self.client.search(**search_params)
            documents = [dict(doc) for doc in results]
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Build result
            result = {
                'documents': documents,
                'query': query,
                'result_count': len(documents),
                'duration_ms': duration_ms,
                'from_cache': False,
                'cache_key': cache_key,
                'parameters': cache_params
            }
            
            # Store in cache
            if use_cache:
                self._store_in_cache(cache_key, result)
            
            # Update metrics
            self._update_metrics(duration_ms, len(documents))
            
            # Check for slow queries
            if duration_ms > self.slow_query_threshold_ms:
                self._record_slow_query(query, duration_ms, cache_params)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.errors += 1
            self.metrics.total_requests += 1
            self.metrics.total_time_ms += duration_ms
            
            return {
                'documents': [],
                'query': query,
                'result_count': 0,
                'duration_ms': duration_ms,
                'from_cache': False,
                'error': str(e)
            }
    
    def _update_metrics(self, duration_ms: float, result_count: int):
        """Update performance metrics"""
        self.metrics.total_requests += 1
        self.metrics.total_time_ms += duration_ms
        self.metrics.update_averages()
        
        # Store request history (keep last 1000)
        self.request_history.append({
            'timestamp': time.time(),
            'duration_ms': duration_ms,
            'result_count': result_count
        })
        
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def _record_slow_query(self, query: str, duration_ms: float, params: Dict):
        """Record slow query for analysis"""
        slow_query = {
            'query': query,
            'duration_ms': duration_ms,
            'parameters': params,
            'timestamp': time.time()
        }
        
        self.slow_queries.append(slow_query)
        
        # Keep only last 100 slow queries
        if len(self.slow_queries) > 100:
            self.slow_queries = self.slow_queries[-100:]
        
        print(f"⚠️ Slow query detected: '{query}' took {duration_ms:.1f}ms")
    
    def optimized_pagination(self, query: str, page_size: int = 20, 
                           max_pages: Optional[int] = None,
                           strategy: str = 'adaptive') -> List[Dict[str, Any]]:
        """
        Optimized pagination with adaptive strategies
        
        Args:
            query: Search query
            page_size: Size of each page
            max_pages: Maximum number of pages to retrieve
            strategy: Pagination strategy ('skip_top', 'range', 'adaptive')
            
        Returns:
            List of all paginated results
        """
        print(f"🔄 Starting optimized pagination: '{query}' (strategy: {strategy})")
        
        all_results = []
        page_num = 0
        
        while True:
            if max_pages and page_num >= max_pages:
                break
            
            # Choose strategy based on page depth
            if strategy == 'adaptive':
                current_strategy = 'range' if page_num > 10 else 'skip_top'
            else:
                current_strategy = strategy
            
            # Get page based on strategy
            if current_strategy == 'skip_top':
                page_result = self._paginate_skip_top(query, page_num, page_size)
            elif current_strategy == 'range':
                # For range pagination, we'd need a sortable field
                # Fallback to skip_top for this example
                page_result = self._paginate_skip_top(query, page_num, page_size)
            else:
                page_result = self._paginate_skip_top(query, page_num, page_size)
            
            if not page_result['documents']:
                print(f"   🏁 No more results at page {page_num + 1}")
                break
            
            all_results.extend(page_result['documents'])
            page_num += 1
            
            # Progress reporting
            if page_num % 5 == 0:
                print(f"   📄 Processed {page_num} pages, {len(all_results)} total results")
            
            # Break if we got fewer results than expected
            if len(page_result['documents']) < page_size:
                print(f"   🏁 Reached end of results at page {page_num}")
                break
        
        print(f"✅ Pagination completed: {len(all_results)} results from {page_num} pages")
        return all_results
    
    def _paginate_skip_top(self, query: str, page_num: int, page_size: int) -> Dict[str, Any]:
        """Skip/top pagination implementation"""
        skip = page_num * page_size
        return self.optimized_search(
            query=query,
            skip=skip,
            top=page_size,
            select_fields=['hotelId', 'hotelName', 'rating']
        )
    
    def batch_optimize_queries(self, queries: List[str], 
                             parallel: bool = True,
                             max_workers: int = 5) -> List[Dict[str, Any]]:
        """
        Optimize multiple queries with batching and parallelization
        
        Args:
            queries: List of queries to execute
            parallel: Whether to execute in parallel
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of query results
        """
        print(f"🚀 Batch optimizing {len(queries)} queries (parallel: {parallel})")
        
        if parallel and len(queries) > 1:
            return self._execute_queries_parallel(queries, max_workers)
        else:
            return self._execute_queries_sequential(queries)
    
    def _execute_queries_sequential(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute queries sequentially"""
        results = []
        
        for i, query in enumerate(queries):
            print(f"   Executing query {i+1}/{len(queries)}: '{query}'")
            result = self.optimized_search(query, top=10)
            results.append(result)
        
        return results
    
    def _execute_queries_parallel(self, queries: List[str], max_workers: int) -> List[Dict[str, Any]]:
        """Execute queries in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all queries
            future_to_query = {
                executor.submit(self.optimized_search, query, top=10): (i, query)
                for i, query in enumerate(queries)
            }
            
            # Collect results
            for future in future_to_query:
                try:
                    result = future.result()
                    query_index, query = future_to_query[future]
                    results.append((query_index, result))
                    print(f"   ✅ Completed query: '{query}'")
                except Exception as e:
                    query_index, query = future_to_query[future]
                    print(f"   ❌ Failed query: '{query}' - {e}")
                    results.append((query_index, {'error': str(e), 'query': query}))
        
        # Sort by original order
        results.sort(key=lambda x: x[0])
        return [result[1] for result in results]
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze current performance metrics and provide recommendations
        
        Returns:
            Performance analysis and recommendations
        """
        print("📊 Analyzing performance metrics...")
        
        # Update metrics
        self.metrics.update_averages()
        
        # Cache analysis
        cache_hit_rate = (self.metrics.cache_hits / 
                         (self.metrics.cache_hits + self.metrics.cache_misses) * 100
                         if (self.metrics.cache_hits + self.metrics.cache_misses) > 0 else 0)
        
        # Recent performance trends
        recent_requests = self.request_history[-100:] if len(self.request_history) >= 100 else self.request_history
        recent_avg_time = sum(r['duration_ms'] for r in recent_requests) / len(recent_requests) if recent_requests else 0
        
        # Slow query analysis
        slow_query_rate = len(self.slow_queries) / self.metrics.total_requests * 100 if self.metrics.total_requests > 0 else 0
        
        analysis = {
            'overall_metrics': {
                'total_requests': self.metrics.total_requests,
                'avg_response_time_ms': self.metrics.avg_response_time_ms,
                'throughput_rps': self.metrics.throughput_requests_per_sec,
                'error_rate_pct': self.metrics.errors / self.metrics.total_requests * 100 if self.metrics.total_requests > 0 else 0
            },
            'cache_performance': {
                'hit_rate_pct': cache_hit_rate,
                'total_entries': len(self.cache),
                'cache_size_limit': self.max_cache_size,
                'ttl_seconds': self.cache_ttl
            },
            'recent_performance': {
                'recent_avg_time_ms': recent_avg_time,
                'recent_requests_analyzed': len(recent_requests)
            },
            'slow_queries': {
                'count': len(self.slow_queries),
                'rate_pct': slow_query_rate,
                'threshold_ms': self.slow_query_threshold_ms
            },
            'recommendations': self._generate_performance_recommendations(cache_hit_rate, slow_query_rate, recent_avg_time)
        }
        
        return analysis
    
    def _generate_performance_recommendations(self, cache_hit_rate: float, 
                                           slow_query_rate: float, 
                                           recent_avg_time: float) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Cache recommendations
        if cache_hit_rate < 50:
            recommendations.append("Low cache hit rate - consider increasing cache TTL or reviewing query patterns")
        elif cache_hit_rate > 90:
            recommendations.append("Excellent cache performance - current caching strategy is effective")
        
        # Slow query recommendations
        if slow_query_rate > 10:
            recommendations.append("High slow query rate - review query complexity and consider field selection optimization")
        
        # Response time recommendations
        if recent_avg_time > 500:
            recommendations.append("High average response time - consider implementing field selection and result caching")
        elif recent_avg_time < 100:
            recommendations.append("Excellent response times - current optimization strategy is working well")
        
        # General recommendations
        if self.metrics.total_requests > 100:
            recommendations.append("Consider implementing connection pooling for high-volume scenarios")
        
        if len(self.cache) > self.max_cache_size * 0.8:
            recommendations.append("Cache approaching size limit - consider increasing max_cache_size or reducing TTL")
        
        return recommendations
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get detailed cache statistics"""
        with self.cache_lock:
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            access_counts = [entry.access_count for entry in self.cache.values()]
            
            return {
                'total_entries': len(self.cache),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'avg_access_count': sum(access_counts) / len(access_counts) if access_counts else 0,
                'max_access_count': max(access_counts) if access_counts else 0,
                'cache_utilization_pct': len(self.cache) / self.max_cache_size * 100
            }
    
    def clear_cache(self):
        """Clear all cache entries"""
        with self.cache_lock:
            self.cache.clear()
            print("🗑️ Cache cleared")
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries for analysis"""
        return sorted(self.slow_queries, key=lambda x: x['duration_ms'], reverse=True)[:limit]

def main():
    """Main function demonstrating performance optimization"""
    # Configuration
    endpoint = os.getenv('SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net')
    api_key = os.getenv('SEARCH_API_KEY', 'your-api-key')
    index_name = os.getenv('INDEX_NAME', 'hotels-sample')
    
    print("⚡ Azure AI Search - Performance Optimization")
    print("=" * 50)
    
    # Initialize optimizer
    optimizer = PerformanceOptimizer(endpoint, index_name, api_key, cache_ttl=300, max_cache_size=500)
    
    # Example 1: Optimized search with caching
    print("\n1. Optimized Search with Caching")
    print("-" * 35)
    
    # First search (cache miss)
    result1 = optimizer.optimized_search("luxury hotel", top=10, select_fields=['hotelId', 'hotelName', 'rating'])
    print(f"First search: {result1['result_count']} results in {result1['duration_ms']:.1f}ms (cached: {result1['from_cache']})")
    
    # Second search (cache hit)
    result2 = optimizer.optimized_search("luxury hotel", top=10, select_fields=['hotelId', 'hotelName', 'rating'])
    print(f"Second search: {result2['result_count']} results in {result2['duration_ms']:.1f}ms (cached: {result2['from_cache']})")
    
    # Example 2: Optimized pagination
    print("\n2. Optimized Pagination")
    print("-" * 23)
    
    paginated_results = optimizer.optimized_pagination("hotel", page_size=15, max_pages=3, strategy='adaptive')
    print(f"Paginated results: {len(paginated_results)} total documents")
    
    # Example 3: Batch query optimization
    print("\n3. Batch Query Optimization")
    print("-" * 28)
    
    test_queries = ['spa', 'wifi', 'pool', 'restaurant', 'parking']
    batch_results = optimizer.batch_optimize_queries(test_queries, parallel=True, max_workers=3)
    
    print("Batch results:")
    for i, result in enumerate(batch_results):
        if 'error' not in result:
            print(f"  '{test_queries[i]}': {result['result_count']} results in {result['duration_ms']:.1f}ms")
        else:
            print(f"  '{test_queries[i]}': Error - {result['error']}")
    
    # Example 4: Performance analysis
    print("\n4. Performance Analysis")
    print("-" * 22)
    
    analysis = optimizer.analyze_performance()
    
    print("Overall Metrics:")
    metrics = analysis['overall_metrics']
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Avg response time: {metrics['avg_response_time_ms']:.1f}ms")
    print(f"  Throughput: {metrics['throughput_rps']:.1f} requests/sec")
    print(f"  Error rate: {metrics['error_rate_pct']:.1f}%")
    
    print("\nCache Performance:")
    cache = analysis['cache_performance']
    print(f"  Hit rate: {cache['hit_rate_pct']:.1f}%")
    print(f"  Entries: {cache['total_entries']}/{cache['cache_size_limit']}")
    
    print("\nRecommendations:")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")
    
    # Example 5: Cache statistics
    print("\n5. Cache Statistics")
    print("-" * 18)
    
    cache_stats = optimizer.get_cache_statistics()
    print(f"Cache entries: {cache_stats['total_entries']}")
    print(f"Cache size: {cache_stats['total_size_mb']:.2f} MB")
    print(f"Cache utilization: {cache_stats['cache_utilization_pct']:.1f}%")
    print(f"Average access count: {cache_stats['avg_access_count']:.1f}")
    
    # Example 6: Slow query analysis
    print("\n6. Slow Query Analysis")
    print("-" * 22)
    
    slow_queries = optimizer.get_slow_queries(limit=5)
    if slow_queries:
        print("Recent slow queries:")
        for query in slow_queries:
            print(f"  '{query['query']}': {query['duration_ms']:.1f}ms")
    else:
        print("No slow queries detected")
    
    print("\n✅ Performance optimization demonstration completed!")
    print(f"Final cache hit rate: {analysis['cache_performance']['hit_rate_pct']:.1f}%")

if __name__ == "__main__":
    main()