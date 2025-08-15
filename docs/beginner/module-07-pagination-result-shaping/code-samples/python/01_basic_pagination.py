"""
Module 7: Basic Pagination with Skip/Top

This example demonstrates fundamental pagination using skip and top parameters.
Best for small to medium result sets (< 10,000 results).
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
class PaginationResult:
    """Data class for pagination results"""
    documents: List[Dict[str, Any]]
    current_page: int
    total_pages: int
    total_results: Optional[int]
    page_size: int
    has_next_page: bool
    has_previous_page: bool
    duration_ms: float
    query: str


@dataclass
class PaginationMetrics:
    """Data class for pagination performance metrics"""
    page_number: int
    skip_value: int
    page_size: int
    duration_ms: float
    results_count: int
    query: str
    timestamp: float


class BasicPaginator:
    """
    Basic paginator implementing skip/top pagination strategy.
    
    This class provides fundamental pagination functionality with performance
    monitoring and error handling.
    """
    
    def __init__(self, search_client: SearchClient, page_size: int = 10):
        """
        Initialize the paginator.
        
        Args:
            search_client: Azure AI Search client
            page_size: Number of results per page
        """
        self.search_client = search_client
        self.page_size = page_size
        self.current_page = 0
        self.total_results: Optional[int] = None
        self.total_pages = 0
        self.metrics: List[PaginationMetrics] = []
    
    def load_page(self, page_number: int, search_text: str = "*", 
                  include_count: bool = True, **kwargs) -> Optional[PaginationResult]:
        """
        Load a specific page of results.
        
        Args:
            page_number: Zero-based page number
            search_text: Search query
            include_count: Whether to include total count
            **kwargs: Additional search parameters
            
        Returns:
            PaginationResult or None if error
        """
        try:
            skip = page_number * self.page_size
            
            # Validate pagination parameters
            self._validate_pagination_params(skip, self.page_size)
            
            print(f"Loading page {page_number + 1}, skip: {skip}, top: {self.page_size}")
            
            start_time = time.time()
            
            # Perform search
            results = self.search_client.search(
                search_text=search_text,
                skip=skip,
                top=self.page_size,
                include_total_count=include_count,
                **kwargs
            )
            
            # Convert to list and measure duration
            documents = list(results)
            duration = (time.time() - start_time) * 1000
            
            # Extract total count if available
            total_count = getattr(results, 'get_count', lambda: None)()
            
            # Update pagination state
            self.current_page = page_number
            if total_count is not None:
                self.total_results = total_count
                self.total_pages = (total_count + self.page_size - 1) // self.page_size
            
            # Record metrics
            metric = PaginationMetrics(
                page_number=page_number,
                skip_value=skip,
                page_size=self.page_size,
                duration_ms=duration,
                results_count=len(documents),
                query=search_text,
                timestamp=time.time()
            )
            self.metrics.append(metric)
            
            print(f"Page loaded in {duration:.1f}ms - {len(documents)} results")
            if total_count is not None:
                print(f"Total results: {total_count}, Total pages: {self.total_pages}")
            
            return PaginationResult(
                documents=documents,
                current_page=page_number,
                total_pages=self.total_pages,
                total_results=total_count,
                page_size=self.page_size,
                has_next_page=self._has_next_page(page_number, len(documents)),
                has_previous_page=page_number > 0,
                duration_ms=duration,
                query=search_text
            )
            
        except Exception as e:
            print(f"Error loading page {page_number}: {e}")
            return None
    
    def load_first_page(self, search_text: str = "*", **kwargs) -> Optional[PaginationResult]:
        """Load the first page."""
        return self.load_page(0, search_text, include_count=True, **kwargs)
    
    def load_next_page(self, search_text: str = "*", **kwargs) -> Optional[PaginationResult]:
        """Load the next page."""
        if not self.has_next_page():
            raise ValueError("No next page available")
        return self.load_page(self.current_page + 1, search_text, include_count=False, **kwargs)
    
    def load_previous_page(self, search_text: str = "*", **kwargs) -> Optional[PaginationResult]:
        """Load the previous page."""
        if not self.has_previous_page():
            raise ValueError("No previous page available")
        return self.load_page(self.current_page - 1, search_text, include_count=False, **kwargs)
    
    def load_last_page(self, search_text: str = "*", **kwargs) -> Optional[PaginationResult]:
        """Load the last page."""
        if self.total_pages == 0:
            return self.load_first_page(search_text, **kwargs)
        return self.load_page(self.total_pages - 1, search_text, include_count=False, **kwargs)
    
    def has_next_page(self) -> bool:
        """Check if there's a next page."""
        if self.total_pages > 0:
            return self.current_page < self.total_pages - 1
        return False  # Unknown, assume no more pages
    
    def has_previous_page(self) -> bool:
        """Check if there's a previous page."""
        return self.current_page > 0
    
    def get_pagination_info(self) -> Dict[str, Any]:
        """Get current pagination information."""
        return {
            'current_page': self.current_page + 1,  # 1-based for display
            'total_pages': self.total_pages,
            'total_results': self.total_results,
            'page_size': self.page_size,
            'has_next_page': self.has_next_page(),
            'has_previous_page': self.has_previous_page()
        }
    
    def get_page_numbers(self, max_visible: int = 5) -> List[Dict[str, Any]]:
        """Generate page numbers for pagination UI."""
        if self.total_pages == 0:
            return []
        
        start_page = max(0, self.current_page - max_visible // 2)
        end_page = min(self.total_pages - 1, start_page + max_visible - 1)
        
        # Adjust start_page if we're near the end
        if end_page - start_page < max_visible - 1:
            start_page = max(0, end_page - max_visible + 1)
        
        pages = []
        for i in range(start_page, end_page + 1):
            pages.append({
                'number': i + 1,  # 1-based for display
                'index': i,       # 0-based for logic
                'is_current': i == self.current_page
            })
        
        return pages
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        if not self.metrics:
            return {}
        
        durations = [m.duration_ms for m in self.metrics]
        return {
            'total_requests': len(self.metrics),
            'average_duration_ms': sum(durations) / len(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'total_results_retrieved': sum(m.results_count for m in self.metrics)
        }
    
    def _has_next_page(self, page_number: int, results_count: int) -> bool:
        """Determine if there's a next page based on results."""
        if self.total_pages > 0:
            return page_number < self.total_pages - 1
        # If we don't know total pages, assume there's more if we got a full page
        return results_count == self.page_size
    
    def _validate_pagination_params(self, skip: int, top: int) -> None:
        """Validate pagination parameters."""
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        if top < 1 or top > 1000:
            raise ValueError("Top must be between 1 and 1000")
        if skip + top > 100000:
            raise ValueError("Cannot retrieve results beyond position 100,000")


def display_page_results(result: PaginationResult) -> None:
    """Display page results in a formatted way."""
    print(f"Page {result.current_page + 1} of {result.total_pages or '?'}")
    print(f"Showing {len(result.documents)} results")
    if result.total_results:
        print(f"Total results: {result.total_results}")
    print(f"Load time: {result.duration_ms:.1f}ms")
    
    for i, doc in enumerate(result.documents):
        hotel_name = doc.get('hotelName', doc.get('title', doc.get('id', 'Unknown')))
        rating = doc.get('rating', 'N/A')
        score = doc.get('@search.score', 'N/A')
        print(f"  {i + 1}. {hotel_name} (Rating: {rating}, Score: {score})")
    
    print(f"Has Next: {result.has_next_page}, Has Previous: {result.has_previous_page}")


def demonstrate_basic_pagination():
    """Demonstrate basic pagination functionality."""
    print("=== Basic Pagination Demo ===\n")
    
    # Initialize search client
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    # Create paginator with 5 items per page
    paginator = BasicPaginator(search_client, page_size=5)
    
    try:
        # Load first page
        print("1. Loading first page...")
        page = paginator.load_first_page("*")
        if page:
            display_page_results(page)
        
        # Load next few pages
        print("\n2. Loading next page...")
        page = paginator.load_next_page("*")
        if page:
            display_page_results(page)
        
        print("\n3. Loading one more page...")
        page = paginator.load_next_page("*")
        if page:
            display_page_results(page)
        
        # Go back to previous page
        print("\n4. Going back to previous page...")
        page = paginator.load_previous_page("*")
        if page:
            display_page_results(page)
        
        # Jump to last page
        print("\n5. Jumping to last page...")
        page = paginator.load_last_page("*")
        if page:
            display_page_results(page)
        
        # Show pagination info
        print("\n6. Pagination Info:")
        print(paginator.get_pagination_info())
        
        # Show page numbers for UI
        print("\n7. Page Numbers for UI:")
        print(paginator.get_page_numbers())
        
        # Show performance metrics
        print("\n8. Performance Metrics:")
        print(paginator.get_performance_metrics())
        
    except Exception as e:
        print(f"Demo error: {e}")


def demonstrate_search_pagination():
    """Demonstrate search with pagination."""
    print("\n=== Search with Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    paginator = BasicPaginator(search_client, page_size=3)
    
    try:
        # Search for specific terms with pagination
        search_query = "luxury"
        print(f'Searching for: "{search_query}"')
        
        page = paginator.load_first_page(search_query)
        if page:
            display_page_results(page)
        
        # Load next page of search results
        if page and page.has_next_page:
            print("\nLoading next page of search results...")
            page = paginator.load_next_page(search_query)
            if page:
                display_page_results(page)
        
    except Exception as e:
        print(f"Search pagination error: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling scenarios."""
    print("\n=== Error Handling Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    # Test invalid page size
    try:
        invalid_paginator = BasicPaginator(search_client, page_size=2000)  # Too large
        invalid_paginator.load_first_page("*")
    except Exception as e:
        print(f"Expected error for large page size: {e}")
    
    # Test going beyond available pages
    try:
        paginator = BasicPaginator(search_client, page_size=10)
        paginator.load_page(999999, "*")  # Very high page number
    except Exception as e:
        print(f"Expected error for invalid page: {e}")
    
    # Test previous page when on first page
    try:
        paginator = BasicPaginator(search_client, page_size=10)
        paginator.load_first_page("*")
        paginator.load_previous_page("*")
    except Exception as e:
        print(f"Expected error for previous page on first page: {e}")


def compare_page_sizes():
    """Compare performance of different page sizes."""
    print("\n=== Page Size Performance Comparison ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    page_sizes = [5, 10, 20, 50]
    
    for page_size in page_sizes:
        paginator = BasicPaginator(search_client, page_size)
        
        try:
            start_time = time.time()
            page = paginator.load_first_page("*")
            duration = (time.time() - start_time) * 1000
            
            if page:
                print(f"Page size {page_size}: {duration:.1f}ms, {len(page.documents)} results")
            else:
                print(f"Page size {page_size}: Failed")
        except Exception as e:
            print(f"Page size {page_size}: Error - {e}")


class PaginationIterator:
    """Iterator for automatic pagination through all results."""
    
    def __init__(self, paginator: BasicPaginator, search_text: str = "*", **kwargs):
        self.paginator = paginator
        self.search_text = search_text
        self.kwargs = kwargs
        self.current_page = 0
        self.current_documents = []
        self.current_index = 0
        self.has_more = True
    
    def __iter__(self):
        return self
    
    def __next__(self):
        # If we've exhausted current page, load next
        if self.current_index >= len(self.current_documents):
            if not self.has_more:
                raise StopIteration
            
            # Load next page
            result = self.paginator.load_page(
                self.current_page, 
                self.search_text, 
                include_count=False,
                **self.kwargs
            )
            
            if not result or not result.documents:
                raise StopIteration
            
            self.current_documents = result.documents
            self.current_index = 0
            self.current_page += 1
            self.has_more = result.has_next_page
        
        # Return current document
        doc = self.current_documents[self.current_index]
        self.current_index += 1
        return doc


def demonstrate_pagination_iterator():
    """Demonstrate automatic pagination with iterator."""
    print("\n=== Pagination Iterator Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    paginator = BasicPaginator(search_client, page_size=5)
    iterator = PaginationIterator(paginator, "hotel")
    
    try:
        count = 0
        for doc in iterator:
            hotel_name = doc.get('hotelName', doc.get('title', 'Unknown'))
            print(f"{count + 1}. {hotel_name}")
            count += 1
            
            # Limit for demo
            if count >= 15:
                break
        
        print(f"\nProcessed {count} documents across multiple pages")
        
    except Exception as e:
        print(f"Iterator error: {e}")


if __name__ == "__main__":
    try:
        demonstrate_basic_pagination()
        demonstrate_search_pagination()
        demonstrate_error_handling()
        compare_page_sizes()
        demonstrate_pagination_iterator()
    except Exception as e:
        print(f"Demo failed: {e}")