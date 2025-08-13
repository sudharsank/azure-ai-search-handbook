#!/usr/bin/env python3
"""
Module 4: Simple Queries and Filters - Sorting and Pagination
=============================================================

This script demonstrates sorting and pagination in Azure AI Search using Python.
Learn how to order results and efficiently navigate through large result sets.

Prerequisites:
- Azure AI Search service configured
- Sample index with data (from previous modules)
- Environment variables set in .env file

Author: Azure AI Search Tutorial
"""

import os
import sys
import math
from typing import List, Dict, Any, Tuple
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_search_client() -> SearchClient:
    """
    Create and return an Azure AI Search client.
    
    Returns:
        SearchClient: Configured search client
    """
    endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    
    if not all([endpoint, api_key, index_name]):
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    return SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )

def print_results(results: List[Dict[str, Any]], title: str, max_results: int = 5) -> None:
    """
    Print search results in a formatted way.
    
    Args:
        results: List of search result documents
        title: Title for the result set
        max_results: Maximum number of results to display
    """
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results[:max_results]):
        print(f"\n{i+1}. {result.get('title', 'No title')}")
        print(f"   Score: {result.get('@search.score', 'N/A'):.2f}")
        print(f"   Category: {result.get('category', 'N/A')}")
        print(f"   Rating: {result.get('rating', 'N/A')}")
        print(f"   Published: {result.get('publishedDate', 'N/A')}")
        print(f"   Price: ${result.get('price', 'N/A')}")
    
    if len(results) > max_results:
        print(f"\n... and {len(results) - max_results} more results")

def basic_sorting(search_client: SearchClient) -> None:
    """
    Demonstrate basic sorting operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("BASIC SORTING EXAMPLES")
    print("="*80)
    
    # Example 1: Sort by relevance score (default)
    print("\n1. Default Sorting (Relevance Score)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            top=5
        ))
        print_results(results, "Default sort by relevance score")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Sort by date (descending - newest first)
    print("\n2. Sort by Date (Newest First)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            order_by=["publishedDate desc"],
            top=5
        ))
        print_results(results, "Sort by publishedDate desc")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Sort by date (ascending - oldest first)
    print("\n3. Sort by Date (Oldest First)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            order_by=["publishedDate asc"],
            top=5
        ))
        print_results(results, "Sort by publishedDate asc")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Sort by rating (highest first)
    print("\n4. Sort by Rating (Highest First)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            order_by=["rating desc"],
            top=5
        ))
        print_results(results, "Sort by rating desc")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def multi_field_sorting(search_client: SearchClient) -> None:
    """
    Demonstrate multi-field sorting operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("MULTI-FIELD SORTING EXAMPLES")
    print("="*80)
    
    # Example 1: Sort by category, then by rating
    print("\n1. Sort by Category, then Rating")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            order_by=["category asc", "rating desc"],
            top=8
        ))
        print_results(results, "Sort by category asc, rating desc", max_results=8)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Sort by rating, then by date
    print("\n2. Sort by Rating, then Date")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            order_by=["rating desc", "publishedDate desc"],
            top=8
        ))
        print_results(results, "Sort by rating desc, publishedDate desc", max_results=8)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Sort by price, then by rating, then by date
    print("\n3. Three-Level Sorting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            order_by=["price asc", "rating desc", "publishedDate desc"],
            top=8
        ))
        print_results(results, "Sort by price asc, rating desc, publishedDate desc", max_results=8)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def sorting_with_search_and_filters(search_client: SearchClient) -> None:
    """
    Demonstrate sorting combined with search text and filters.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("SORTING WITH SEARCH AND FILTERS")
    print("="*80)
    
    # Example 1: Search + Filter + Sort
    print("\n1. Search + Filter + Sort")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            filter="rating ge 3.0",
            order_by=["rating desc"],
            top=5
        ))
        print_results(results, "Search 'azure' + rating >= 3.0 + sort by rating desc")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Category filter with date sorting
    print("\n2. Category Filter with Date Sorting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category eq 'Technology'",
            order_by=["publishedDate desc"],
            top=5
        ))
        print_results(results, "Technology category sorted by newest first")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Complex filter with multi-field sorting
    print("\n3. Complex Filter with Multi-field Sorting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="tutorial",
            filter="rating ge 4.0 and publishedDate ge 2023-01-01T00:00:00Z",
            order_by=["rating desc", "publishedDate desc"],
            top=5
        ))
        print_results(results, "Tutorial + high rating + recent + sorted")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def basic_pagination(search_client: SearchClient) -> None:
    """
    Demonstrate basic pagination operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("BASIC PAGINATION EXAMPLES")
    print("="*80)
    
    page_size = 3
    
    # Example 1: First page
    print("\n1. First Page")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            top=page_size,
            skip=0,
            order_by=["publishedDate desc"]
        ))
        print_results(results, f"Page 1 (top {page_size}, skip 0)", max_results=page_size)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Second page
    print("\n2. Second Page")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            top=page_size,
            skip=page_size,  # Skip first page
            order_by=["publishedDate desc"]
        ))
        print_results(results, f"Page 2 (top {page_size}, skip {page_size})", max_results=page_size)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Third page
    print("\n3. Third Page")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            top=page_size,
            skip=page_size * 2,  # Skip first two pages
            order_by=["publishedDate desc"]
        ))
        print_results(results, f"Page 3 (top {page_size}, skip {page_size * 2})", max_results=page_size)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def pagination_with_total_count(search_client: SearchClient) -> None:
    """
    Demonstrate pagination with total count for building navigation.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("PAGINATION WITH TOTAL COUNT")
    print("="*80)
    
    page_size = 5
    
    try:
        # Get first page with total count
        results = search_client.search(
            search_text="azure",
            top=page_size,
            skip=0,
            include_total_count=True,
            order_by=["rating desc"]
        )
        
        result_list = list(results)
        total_count = results.get_count()
        total_pages = math.ceil(total_count / page_size) if total_count else 0
        
        print(f"\nPagination Summary:")
        print(f"Total documents: {total_count}")
        print(f"Page size: {page_size}")
        print(f"Total pages: {total_pages}")
        print(f"Current page: 1")
        
        print_results(result_list, f"Page 1 of {total_pages}")
        
        # Show pagination navigation info
        print(f"\nNavigation:")
        print(f"• Previous: N/A (first page)")
        print(f"• Next: Page 2 (skip={page_size})")
        print(f"• Last: Page {total_pages} (skip={page_size * (total_pages - 1)})")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def advanced_pagination_patterns(search_client: SearchClient) -> None:
    """
    Demonstrate advanced pagination patterns and utilities.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("ADVANCED PAGINATION PATTERNS")
    print("="*80)
    
    def paginated_search(query: str, page: int = 1, page_size: int = 5, 
                        order_by: List[str] = None, filter_expr: str = None) -> Dict[str, Any]:
        """
        Perform paginated search with metadata.
        
        Args:
            query: Search query
            page: Page number (1-based)
            page_size: Number of results per page
            order_by: Sort expressions
            filter_expr: Filter expression
            
        Returns:
            Dictionary with results and pagination metadata
        """
        skip = (page - 1) * page_size
        
        search_params = {
            'search_text': query,
            'top': page_size,
            'skip': skip,
            'include_total_count': True
        }
        
        if order_by:
            search_params['order_by'] = order_by
        if filter_expr:
            search_params['filter'] = filter_expr
        
        try:
            results = search_client.search(**search_params)
            result_list = list(results)
            total_count = results.get_count()
            total_pages = math.ceil(total_count / page_size) if total_count else 0
            
            return {
                'results': result_list,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_previous': page > 1,
                    'has_next': page < total_pages,
                    'previous_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < total_pages else None
                }
            }
        except HttpResponseError as e:
            return {
                'results': [],
                'pagination': {},
                'error': str(e)
            }
    
    # Example 1: Page 1
    print("\n1. Advanced Pagination - Page 1")
    print("-" * 40)
    
    result = paginated_search(
        query="azure",
        page=1,
        page_size=3,
        order_by=["rating desc"]
    )
    
    if 'error' not in result:
        print_results(result['results'], "Page 1 Results", max_results=3)
        
        pagination = result['pagination']
        print(f"\nPagination Info:")
        print(f"• Page {pagination['current_page']} of {pagination['total_pages']}")
        print(f"• Total results: {pagination['total_count']}")
        print(f"• Has previous: {pagination['has_previous']}")
        print(f"• Has next: {pagination['has_next']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example 2: Page 2
    print("\n2. Advanced Pagination - Page 2")
    print("-" * 40)
    
    result = paginated_search(
        query="azure",
        page=2,
        page_size=3,
        order_by=["rating desc"]
    )
    
    if 'error' not in result:
        print_results(result['results'], "Page 2 Results", max_results=3)
        
        pagination = result['pagination']
        print(f"\nPagination Info:")
        print(f"• Page {pagination['current_page']} of {pagination['total_pages']}")
        print(f"• Previous page: {pagination['previous_page']}")
        print(f"• Next page: {pagination['next_page']}")
    else:
        print(f"Error: {result['error']}")

def geographic_sorting(search_client: SearchClient) -> None:
    """
    Demonstrate geographic distance sorting (if location data is available).
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("GEOGRAPHIC SORTING EXAMPLES")
    print("="*80)
    
    # Example 1: Sort by distance from a point
    print("\n1. Sort by Geographic Distance")
    print("-" * 40)
    
    try:
        # Seattle coordinates as reference point
        reference_point = "geography'POINT(-122.131577 47.678581)'"
        
        results = list(search_client.search(
            search_text="*",
            order_by=[f"geo.distance(location, {reference_point}) asc"],
            top=5
        ))
        
        print_results(results, "Sorted by distance from Seattle")
        
        # Show distance information if available
        for i, result in enumerate(results[:3]):
            location = result.get('location')
            if location:
                print(f"   Location {i+1}: {location}")
        
    except HttpResponseError as e:
        print(f"Geographic sorting failed (location field may not exist): {e.message}")
        print("Note: Geographic sorting requires a location field of type Edm.GeographyPoint")

def sorting_performance_tips(search_client: SearchClient) -> None:
    """
    Demonstrate sorting performance optimization techniques.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("SORTING PERFORMANCE OPTIMIZATION")
    print("="*80)
    
    # Example 1: Efficient sorting with filters
    print("\n1. Filter First, Then Sort")
    print("-" * 40)
    
    try:
        import time
        
        # Measure performance of filtered + sorted query
        start_time = time.time()
        
        results = list(search_client.search(
            search_text="azure",
            filter="rating ge 3.0",  # Filter reduces dataset first
            order_by=["rating desc"],
            top=10
        ))
        
        execution_time = time.time() - start_time
        
        print(f"Filtered + sorted query executed in {execution_time:.3f} seconds")
        print(f"Results: {len(results)} documents")
        print_results(results, "Optimized: filter + sort", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Limit result set size
    print("\n2. Limit Result Set Size")
    print("-" * 40)
    
    try:
        # Use reasonable page sizes
        results = list(search_client.search(
            search_text="*",
            order_by=["publishedDate desc"],
            top=20  # Reasonable page size
        ))
        
        print(f"Limited to top 20 results for better performance")
        print_results(results, "Performance-optimized pagination", max_results=5)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Use simple sort expressions
    print("\n3. Simple vs Complex Sort Expressions")
    print("-" * 40)
    
    try:
        # Simple sort (better performance)
        results_simple = list(search_client.search(
            search_text="azure",
            order_by=["rating desc"],  # Single field sort
            top=5
        ))
        
        print("Simple sort (single field): Better performance")
        print_results(results_simple, "Simple sort by rating", max_results=3)
        
        # Complex sort (may be slower)
        results_complex = list(search_client.search(
            search_text="azure",
            order_by=["rating desc", "publishedDate desc", "category asc"],  # Multi-field sort
            top=5
        ))
        
        print("\nComplex sort (multiple fields): May be slower but more precise")
        print_results(results_complex, "Complex multi-field sort", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def main():
    """
    Main function to run all sorting and pagination examples.
    """
    print("Azure AI Search - Sorting and Pagination Examples")
    print("=" * 80)
    
    try:
        # Create search client
        search_client = create_search_client()
        print(f"✅ Connected to search service: {os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')}")
        print(f"✅ Using index: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
        
        # Run examples
        basic_sorting(search_client)
        multi_field_sorting(search_client)
        sorting_with_search_and_filters(search_client)
        basic_pagination(search_client)
        pagination_with_total_count(search_client)
        advanced_pagination_patterns(search_client)
        geographic_sorting(search_client)
        sorting_performance_tips(search_client)
        
        print("\n" + "="*80)
        print("✅ All sorting and pagination examples completed successfully!")
        print("="*80)
        
        print("\n📚 What you learned:")
        print("• How to sort results by single and multiple fields")
        print("• How to combine sorting with search and filters")
        print("• How to implement basic and advanced pagination")
        print("• How to get total counts for navigation")
        print("• How to optimize sorting performance")
        print("• How to handle geographic distance sorting")
        
        print("\n🔗 Next steps:")
        print("• Run 04_result_customization.py to learn about field selection")
        print("• Experiment with different sort combinations")
        print("• Build pagination UI components")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n🔧 Setup required:")
        print("1. Create a .env file with your Azure AI Search credentials")
        print("2. Ensure you have completed previous modules to create sample indexes")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()