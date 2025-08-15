"""
Module 7: Range-Based Pagination for Large Datasets

This example demonstrates range-based pagination using filters and sorting,
which provides better performance for large datasets and deep pagination scenarios.
"""

import os
import time
from typing import List, Dict, Any, Optional, Union, Tuple
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
class RangePaginationResult:
    """Data class for range pagination results"""
    documents: List[Dict[str, Any]]
    last_sort_value: Any
    has_next_page: bool
    page_size: int
    duration_ms: float
    query: str
    sort_field: str
    filter_expression: Optional[str]
    page_number: int


@dataclass
class RangePaginationConfig:
    """Configuration for range pagination"""
    sort_field: str
    sort_direction: str = 'asc'  # 'asc' or 'desc'
    page_size: int = 10
    filter_base: Optional[str] = None
    include_sort_value: bool = True


class RangePaginator:
    """
    Range-based paginator for efficient pagination of large datasets.
    
    This class implements pagination using range filters and sorting,
    which provides consistent performance regardless of page depth.
    """
    
    def __init__(self, search_client: SearchClient, config: RangePaginationConfig):
        """
        Initialize the range paginator.
        
        Args:
            search_client: Azure AI Search client
            config: Range pagination configuration
        """
        self.search_client = search_client
        self.config = config
        self.current_page = 0
        self.last_sort_value = None
        self.page_history: List[Any] = []
    
    def load_first_page(self, search_text: str = "*", **kwargs) -> RangePaginationResult:
        """
        Load the first page of results.
        
        Args:
            search_text: Search query
            **kwargs: Additional search parameters
            
        Returns:
            RangePaginationResult for first page
        """
        self.current_page = 0
        self.last_sort_value = None
        self.page_history = []
        
        return self._load_page(search_text, None, **kwargs)
    
    def load_next_page(self, search_text: str = "*", **kwargs) -> Optional[RangePaginationResult]:
        """
        Load the next page of results.
        
        Args:
            search_text: Search query
            **kwargs: Additional search parameters
            
        Returns:
            RangePaginationResult for next page or None if no more pages
        """
        if self.last_sort_value is None:
            raise ValueError("Must load first page before loading next page")
        
        # Store current position in history for potential backward navigation
        self.page_history.append(self.last_sort_value)
        
        result = self._load_page(search_text, self.last_sort_value, **kwargs)
        
        if result and result.documents:
            self.current_page += 1
            return result
        else:
            # No more results, remove from history
            if self.page_history:
                self.page_history.pop()
            return None
    
    def load_page_after(self, sort_value: Any, search_text: str = "*", 
                       **kwargs) -> RangePaginationResult:
        """
        Load page starting after a specific sort value.
        
        Args:
            sort_value: Sort value to start after
            search_text: Search query
            **kwargs: Additional search parameters
            
        Returns:
            RangePaginationResult starting after sort_value
        """
        return self._load_page(search_text, sort_value, **kwargs)
    
    def _load_page(self, search_text: str, after_value: Any, 
                   **kwargs) -> RangePaginationResult:
        """
        Internal method to load a page with range filtering.
        
        Args:
            search_text: Search query
            after_value: Value to start after (None for first page)
            **kwargs: Additional search parameters
            
        Returns:
            RangePaginationResult
        """
        try:
            print(f"Loading range page: after_value={after_value}")
            
            start_time = time.time()
            
            # Build filter expression
            filter_parts = []
            
            # Add base filter if provided
            if self.config.filter_base:
                filter_parts.append(self.config.filter_base)
            
            # Add range filter
            if after_value is not None:
                operator = 'gt' if self.config.sort_direction == 'asc' else 'lt'
                
                # Handle different data types
                if isinstance(after_value, str):
                    filter_value = f"'{after_value}'"
                elif isinstance(after_value, (int, float)):
                    filter_value = str(after_value)
                else:
                    filter_value = f"'{str(after_value)}'"
                
                range_filter = f"{self.config.sort_field} {operator} {filter_value}"
                filter_parts.append(range_filter)
            
            # Combine filters
            filter_expression = ' and '.join(filter_parts) if filter_parts else None
            
            # Build sort expression
            sort_expression = f"{self.config.sort_field} {self.config.sort_direction}"
            
            print(f"Filter: {filter_expression}")
            print(f"Sort: {sort_expression}")
            
            # Perform search
            search_params = {
                'search_text': search_text,
                'top': self.config.page_size,
                'order_by': [sort_expression],
                **kwargs
            }
            
            if filter_expression:
                search_params['filter'] = filter_expression
            
            if self.config.include_sort_value:
                # Include sort field in results if not already selected
                if 'select' in search_params:
                    select_fields = search_params['select']
                    if isinstance(select_fields, str):
                        select_fields = [f.strip() for f in select_fields.split(',')]
                    if self.config.sort_field not in select_fields:
                        select_fields.append(self.config.sort_field)
                    search_params['select'] = select_fields
            
            results = self.search_client.search(**search_params)
            documents = list(results)
            
            duration = (time.time() - start_time) * 1000
            
            # Get last sort value for next page
            new_last_sort_value = None
            if documents:
                last_doc = documents[-1]
                new_last_sort_value = last_doc.get(self.config.sort_field)
            
            # Update state
            if new_last_sort_value is not None:
                self.last_sort_value = new_last_sort_value
            
            # Determine if there are more pages
            has_next_page = len(documents) == self.config.page_size
            
            print(f"Loaded {len(documents)} documents in {duration:.1f}ms")
            print(f"Last sort value: {new_last_sort_value}")
            print(f"Has next page: {has_next_page}")
            
            return RangePaginationResult(
                documents=documents,
                last_sort_value=new_last_sort_value,
                has_next_page=has_next_page,
                page_size=self.config.page_size,
                duration_ms=duration,
                query=search_text,
                sort_field=self.config.sort_field,
                filter_expression=filter_expression,
                page_number=self.current_page
            )
            
        except Exception as e:
            print(f"Range pagination error: {e}")
            raise
    
    def reset(self):
        """Reset paginator state."""
        self.current_page = 0
        self.last_sort_value = None
        self.page_history = []


class CursorPaginator:
    """
    Cursor-based paginator using search_after functionality.
    
    This provides the most efficient pagination for large datasets
    when available in the search service.
    """
    
    def __init__(self, search_client: SearchClient, sort_fields: List[str]):
        """
        Initialize cursor paginator.
        
        Args:
            search_client: Azure AI Search client
            sort_fields: Fields to sort by (should include unique field)
        """
        self.search_client = search_client
        self.sort_fields = sort_fields
        self.current_cursor = None
        self.page_size = 10
    
    def load_page(self, search_text: str = "*", 
                  cursor: Optional[List[Any]] = None,
                  page_size: int = 10,
                  **kwargs) -> Dict[str, Any]:
        """
        Load page using cursor pagination.
        
        Args:
            search_text: Search query
            cursor: Cursor values from previous page
            page_size: Number of results per page
            **kwargs: Additional search parameters
            
        Returns:
            Page result with cursor information
        """
        try:
            print(f"Loading cursor page: cursor={cursor}")
            
            start_time = time.time()
            
            # Build sort expressions
            sort_expressions = [f"{field} asc" for field in self.sort_fields]
            
            search_params = {
                'search_text': search_text,
                'top': page_size,
                'order_by': sort_expressions,
                **kwargs
            }
            
            # Add search_after if cursor provided
            # Note: search_after is not directly available in Python SDK
            # This is a conceptual implementation
            if cursor:
                # In a real implementation, you would use the REST API directly
                # or wait for SDK support for search_after
                print("Note: search_after not directly supported in Python SDK")
            
            results = self.search_client.search(**search_params)
            documents = list(results)
            
            duration = (time.time() - start_time) * 1000
            
            # Generate cursor for next page
            next_cursor = None
            if documents:
                last_doc = documents[-1]
                next_cursor = [last_doc.get(field) for field in self.sort_fields]
            
            has_next_page = len(documents) == page_size
            
            return {
                'documents': documents,
                'next_cursor': next_cursor,
                'has_next_page': has_next_page,
                'duration_ms': duration,
                'page_size': page_size
            }
            
        except Exception as e:
            print(f"Cursor pagination error: {e}")
            raise


class HybridPaginator:
    """
    Hybrid paginator that chooses the best strategy based on context.
    """
    
    def __init__(self, search_client: SearchClient):
        """
        Initialize hybrid paginator.
        
        Args:
            search_client: Azure AI Search client
        """
        self.search_client = search_client
        self.strategies = {}
    
    def get_optimal_strategy(self, total_results: Optional[int], 
                           page_number: int,
                           sort_field: Optional[str] = None) -> str:
        """
        Determine optimal pagination strategy.
        
        Args:
            total_results: Total number of results
            page_number: Current page number
            sort_field: Available sort field
            
        Returns:
            Recommended strategy name
        """
        # Use skip/top for small datasets and early pages
        if total_results and total_results < 1000 and page_number < 10:
            return 'skip_top'
        
        # Use range pagination for large datasets or deep pagination
        if sort_field and (not total_results or total_results > 1000 or page_number > 10):
            return 'range'
        
        # Default to skip/top
        return 'skip_top'
    
    def create_paginator(self, strategy: str, **config) -> Union[RangePaginator, Any]:
        """
        Create paginator instance for strategy.
        
        Args:
            strategy: Strategy name
            **config: Configuration parameters
            
        Returns:
            Paginator instance
        """
        if strategy == 'range':
            range_config = RangePaginationConfig(
                sort_field=config.get('sort_field', 'hotelId'),
                sort_direction=config.get('sort_direction', 'asc'),
                page_size=config.get('page_size', 10),
                filter_base=config.get('filter_base')
            )
            return RangePaginator(self.search_client, range_config)
        
        elif strategy == 'cursor':
            sort_fields = config.get('sort_fields', ['hotelId'])
            return CursorPaginator(self.search_client, sort_fields)
        
        else:
            # Return basic paginator (would need to import from previous module)
            raise NotImplementedError("Basic paginator not implemented in this module")


def demonstrate_range_pagination():
    """Demonstrate range-based pagination."""
    print("=== Range-Based Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    # Configure range pagination
    config = RangePaginationConfig(
        sort_field='hotelId',  # Use a unique, sortable field
        sort_direction='asc',
        page_size=5
    )
    
    paginator = RangePaginator(search_client, config)
    
    try:
        # Load first page
        print("1. Loading first page:")
        page1 = paginator.load_first_page('*')
        display_range_page(page1)
        
        # Load next few pages
        print("\n2. Loading next page:")
        page2 = paginator.load_next_page('*')
        if page2:
            display_range_page(page2)
        
        print("\n3. Loading another page:")
        page3 = paginator.load_next_page('*')
        if page3:
            display_range_page(page3)
        
        # Demonstrate jumping to specific position
        print("\n4. Jumping to specific position:")
        if page2 and page2.last_sort_value:
            jump_page = paginator.load_page_after(page2.last_sort_value, '*')
            display_range_page(jump_page)
        
    except Exception as e:
        print(f"Range pagination demo error: {e}")


def display_range_page(page: RangePaginationResult):
    """Display range pagination page results."""
    print(f"Page {page.page_number + 1}")
    print(f"Results: {len(page.documents)}")
    print(f"Duration: {page.duration_ms:.1f}ms")
    print(f"Sort field: {page.sort_field}")
    print(f"Last sort value: {page.last_sort_value}")
    print(f"Has next page: {page.has_next_page}")
    
    if page.filter_expression:
        print(f"Filter: {page.filter_expression}")
    
    # Show sample results
    for i, doc in enumerate(page.documents):
        hotel_id = doc.get('hotelId', doc.get('id', 'Unknown'))
        hotel_name = doc.get('hotelName', doc.get('title', 'Unknown'))
        sort_value = doc.get(page.sort_field, 'N/A')
        print(f"  {i + 1}. {hotel_name} (ID: {hotel_id}, Sort: {sort_value})")


def demonstrate_performance_comparison():
    """Compare range pagination vs skip/top performance."""
    print("\n=== Performance Comparison Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    try:
        # Test different page positions
        page_positions = [0, 10, 50, 100]  # Skip values
        page_size = 10
        
        print("Comparing skip/top vs range pagination performance:")
        print("Page | Skip/Top (ms) | Range (ms) | Improvement")
        print("-" * 50)
        
        for skip in page_positions:
            # Test skip/top pagination
            start_time = time.time()
            skip_results = search_client.search(
                search_text='*',
                skip=skip,
                top=page_size,
                order_by=['hotelId asc']
            )
            list(skip_results)  # Consume results
            skip_duration = (time.time() - start_time) * 1000
            
            # Test range pagination (simulate by getting the boundary value)
            if skip > 0:
                # Get the boundary value first
                boundary_results = search_client.search(
                    search_text='*',
                    skip=skip - 1,
                    top=1,
                    order_by=['hotelId asc']
                )
                boundary_docs = list(boundary_results)
                
                if boundary_docs:
                    boundary_value = boundary_docs[0].get('hotelId')
                    
                    # Now test range pagination
                    start_time = time.time()
                    range_results = search_client.search(
                        search_text='*',
                        filter=f"hotelId gt '{boundary_value}'",
                        top=page_size,
                        order_by=['hotelId asc']
                    )
                    list(range_results)  # Consume results
                    range_duration = (time.time() - start_time) * 1000
                    
                    improvement = ((skip_duration - range_duration) / skip_duration) * 100
                    print(f"{skip:4d} | {skip_duration:11.1f} | {range_duration:9.1f} | {improvement:+8.1f}%")
                else:
                    print(f"{skip:4d} | {skip_duration:11.1f} | No boundary | N/A")
            else:
                print(f"{skip:4d} | {skip_duration:11.1f} | N/A (first) | N/A")
        
    except Exception as e:
        print(f"Performance comparison error: {e}")


def demonstrate_filtered_range_pagination():
    """Demonstrate range pagination with additional filters."""
    print("\n=== Filtered Range Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    try:
        # Configure with base filter
        config = RangePaginationConfig(
            sort_field='hotelId',
            sort_direction='asc',
            page_size=3,
            filter_base="rating ge 4.0"  # Only high-rated hotels
        )
        
        paginator = RangePaginator(search_client, config)
        
        print("Range pagination with rating filter (>= 4.0):")
        
        # Load first page
        page = paginator.load_first_page('luxury')
        display_range_page(page)
        
        # Load next page
        if page.has_next_page:
            print("\nNext page:")
            page = paginator.load_next_page('luxury')
            if page:
                display_range_page(page)
        
    except Exception as e:
        print(f"Filtered range pagination demo error: {e}")


def demonstrate_cursor_pagination():
    """Demonstrate cursor-based pagination concept."""
    print("\n=== Cursor Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    try:
        # Create cursor paginator
        cursor_paginator = CursorPaginator(search_client, ['rating', 'hotelId'])
        
        print("Cursor pagination (conceptual):")
        
        # Load first page
        page1 = cursor_paginator.load_page('*', cursor=None, page_size=5)
        
        print(f"Page 1: {len(page1['documents'])} results")
        print(f"Duration: {page1['duration_ms']:.1f}ms")
        print(f"Next cursor: {page1['next_cursor']}")
        
        # Show sample results
        for i, doc in enumerate(page1['documents']):
            hotel_name = doc.get('hotelName', 'Unknown')
            rating = doc.get('rating', 'N/A')
            hotel_id = doc.get('hotelId', 'N/A')
            print(f"  {i + 1}. {hotel_name} (Rating: {rating}, ID: {hotel_id})")
        
        # Load next page with cursor
        if page1['has_next_page'] and page1['next_cursor']:
            print("\nPage 2 (with cursor):")
            page2 = cursor_paginator.load_page('*', cursor=page1['next_cursor'], page_size=5)
            
            print(f"Results: {len(page2['documents'])}")
            print(f"Duration: {page2['duration_ms']:.1f}ms")
            print(f"Next cursor: {page2['next_cursor']}")
        
    except Exception as e:
        print(f"Cursor pagination demo error: {e}")


def demonstrate_hybrid_strategy():
    """Demonstrate hybrid pagination strategy selection."""
    print("\n=== Hybrid Strategy Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    try:
        hybrid = HybridPaginator(search_client)
        
        # Test different scenarios
        scenarios = [
            {'total_results': 100, 'page_number': 1, 'sort_field': 'hotelId'},
            {'total_results': 5000, 'page_number': 1, 'sort_field': 'hotelId'},
            {'total_results': 1000, 'page_number': 20, 'sort_field': 'hotelId'},
            {'total_results': 10000, 'page_number': 5, 'sort_field': None},
        ]
        
        print("Strategy recommendations:")
        for i, scenario in enumerate(scenarios, 1):
            strategy = hybrid.get_optimal_strategy(**scenario)
            print(f"Scenario {i}: {scenario} -> {strategy}")
        
    except Exception as e:
        print(f"Hybrid strategy demo error: {e}")


def demonstrate_deep_pagination():
    """Demonstrate deep pagination scenarios."""
    print("\n=== Deep Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    try:
        # Configure for deep pagination
        config = RangePaginationConfig(
            sort_field='hotelId',
            sort_direction='asc',
            page_size=10
        )
        
        paginator = RangePaginator(search_client, config)
        
        print("Simulating deep pagination (jumping to page 10):")
        
        # Simulate jumping to a deep page by loading multiple pages
        current_page = paginator.load_first_page('*')
        
        for page_num in range(1, 6):  # Load 5 pages to simulate deep pagination
            if current_page and current_page.has_next_page:
                current_page = paginator.load_next_page('*')
                if current_page:
                    print(f"Page {page_num + 1}: Last sort value = {current_page.last_sort_value}, "
                          f"Duration = {current_page.duration_ms:.1f}ms")
            else:
                break
        
        print("\nNote: Range pagination maintains consistent performance at any depth")
        
    except Exception as e:
        print(f"Deep pagination demo error: {e}")


class RangePaginationHelper:
    """Utility class for range pagination patterns."""
    
    @staticmethod
    def get_sortable_fields() -> List[str]:
        """Get commonly sortable fields for range pagination."""
        return ['hotelId', 'rating', 'lastRenovationDate', 'hotelName']
    
    @staticmethod
    def build_range_filter(field: str, value: Any, direction: str = 'asc') -> str:
        """Build range filter expression."""
        operator = 'gt' if direction == 'asc' else 'lt'
        
        if isinstance(value, str):
            return f"{field} {operator} '{value}'"
        else:
            return f"{field} {operator} {value}"
    
    @staticmethod
    def estimate_page_position(sort_value: Any, min_value: Any, max_value: Any, 
                             total_count: int, page_size: int) -> int:
        """Estimate page position based on sort value."""
        try:
            if isinstance(sort_value, (int, float)):
                if max_value > min_value:
                    ratio = (sort_value - min_value) / (max_value - min_value)
                    estimated_position = int(ratio * total_count)
                    return estimated_position // page_size
            return 0
        except:
            return 0
    
    @staticmethod
    def validate_sort_field(field: str, field_type: str) -> bool:
        """Validate if field is suitable for range pagination."""
        suitable_types = ['Edm.String', 'Edm.Int32', 'Edm.Int64', 'Edm.Double', 
                         'Edm.DateTimeOffset', 'Edm.Boolean']
        return field_type in suitable_types


if __name__ == "__main__":
    try:
        demonstrate_range_pagination()
        demonstrate_performance_comparison()
        demonstrate_filtered_range_pagination()
        demonstrate_cursor_pagination()
        demonstrate_hybrid_strategy()
        demonstrate_deep_pagination()
        
        # Show helper usage
        print("\n=== Range Pagination Helper Demo ===\n")
        helper = RangePaginationHelper()
        
        print("Sortable fields:", helper.get_sortable_fields())
        print("Range filter example:", helper.build_range_filter('hotelId', 'hotel_100', 'asc'))
        print("Page estimation:", helper.estimate_page_position(50, 0, 100, 1000, 10))
        print("Field validation:", helper.validate_sort_field('rating', 'Edm.Double'))
        
    except Exception as e:
        print(f"Demo failed: {e}")