#!/usr/bin/env python3
"""
Module 4: Simple Queries and Filters - Filtering
================================================

This script demonstrates OData filter expressions in Azure AI Search using Python.
Learn how to apply filters to narrow search results based on specific criteria.

Prerequisites:
- Azure AI Search service configured
- Sample index with data (from previous modules)
- Environment variables set in .env file

Author: Azure AI Search Tutorial
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
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
        
        # Show tags if available
        tags = result.get('tags', [])
        if tags:
            print(f"   Tags: {', '.join(tags[:3])}{'...' if len(tags) > 3 else ''}")
    
    if len(results) > max_results:
        print(f"\n... and {len(results) - max_results} more results")

def equality_filters(search_client: SearchClient) -> None:
    """
    Demonstrate equality filter operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("EQUALITY FILTER EXAMPLES")
    print("="*80)
    
    # Example 1: Exact string match
    print("\n1. Exact String Match")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category eq 'Technology'"
        ))
        print_results(results, "Filter: category eq 'Technology'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Not equal filter
    print("\n2. Not Equal Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category ne 'Draft'",
            top=5
        ))
        print_results(results, "Filter: category ne 'Draft'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Combining search with filter
    print("\n3. Search Text with Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            filter="category eq 'Technology'"
        ))
        print_results(results, "Search: 'azure' + Filter: category eq 'Technology'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def comparison_filters(search_client: SearchClient) -> None:
    """
    Demonstrate comparison filter operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("COMPARISON FILTER EXAMPLES")
    print("="*80)
    
    # Example 1: Greater than
    print("\n1. Greater Than Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating gt 4.0"
        ))
        print_results(results, "Filter: rating gt 4.0")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Greater than or equal
    print("\n2. Greater Than or Equal Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating ge 4.5"
        ))
        print_results(results, "Filter: rating ge 4.5")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Less than
    print("\n3. Less Than Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating lt 3.0"
        ))
        print_results(results, "Filter: rating lt 3.0")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Range filter (between values)
    print("\n4. Range Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating ge 3.0 and rating le 4.0"
        ))
        print_results(results, "Filter: rating between 3.0 and 4.0")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def logical_operators(search_client: SearchClient) -> None:
    """
    Demonstrate logical operators in filters.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("LOGICAL OPERATORS IN FILTERS")
    print("="*80)
    
    # Example 1: AND operator
    print("\n1. AND Operator")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category eq 'Technology' and rating ge 4.0"
        ))
        print_results(results, "Filter: category eq 'Technology' AND rating ge 4.0")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: OR operator
    print("\n2. OR Operator")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category eq 'Technology' or category eq 'Science'"
        ))
        print_results(results, "Filter: category eq 'Technology' OR category eq 'Science'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: NOT operator
    print("\n3. NOT Operator")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="not (category eq 'Draft')"
        ))
        print_results(results, "Filter: NOT (category eq 'Draft')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Complex logical expression
    print("\n4. Complex Logical Expression")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="(category eq 'Technology' or category eq 'Science') and rating gt 3.5"
        ))
        print_results(results, "Filter: (Technology OR Science) AND rating > 3.5")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def date_filters(search_client: SearchClient) -> None:
    """
    Demonstrate date filtering operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("DATE FILTER EXAMPLES")
    print("="*80)
    
    # Calculate dates for examples
    today = datetime.now()
    last_year = today - timedelta(days=365)
    last_month = today - timedelta(days=30)
    
    # Example 1: Documents published after a specific date
    print("\n1. Published After Date")
    print("-" * 40)
    
    try:
        filter_date = "2023-01-01T00:00:00Z"
        results = list(search_client.search(
            search_text="*",
            filter=f"publishedDate ge {filter_date}"
        ))
        print_results(results, f"Filter: publishedDate ge {filter_date}")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Documents published before a specific date
    print("\n2. Published Before Date")
    print("-" * 40)
    
    try:
        filter_date = "2024-01-01T00:00:00Z"
        results = list(search_client.search(
            search_text="*",
            filter=f"publishedDate lt {filter_date}"
        ))
        print_results(results, f"Filter: publishedDate lt {filter_date}")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Date range filter
    print("\n3. Date Range Filter")
    print("-" * 40)
    
    try:
        start_date = "2023-01-01T00:00:00Z"
        end_date = "2023-12-31T23:59:59Z"
        results = list(search_client.search(
            search_text="*",
            filter=f"publishedDate ge {start_date} and publishedDate le {end_date}"
        ))
        print_results(results, f"Filter: published in 2023")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Recent documents (last 30 days)
    print("\n4. Recent Documents")
    print("-" * 40)
    
    try:
        # Format date for OData
        recent_date = last_month.strftime("%Y-%m-%dT%H:%M:%SZ")
        results = list(search_client.search(
            search_text="*",
            filter=f"publishedDate ge {recent_date}"
        ))
        print_results(results, f"Filter: published in last 30 days")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def collection_filters(search_client: SearchClient) -> None:
    """
    Demonstrate filtering on collection fields (arrays).
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("COLLECTION FILTER EXAMPLES")
    print("="*80)
    
    # Example 1: Any element matches (tags/any)
    print("\n1. Any Element Matches")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="tags/any(t: t eq 'python')"
        ))
        print_results(results, "Filter: tags/any(t: t eq 'python')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Multiple tag matches
    print("\n2. Multiple Tag Options")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="tags/any(t: t eq 'python' or t eq 'javascript')"
        ))
        print_results(results, "Filter: tags contain 'python' OR 'javascript'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: All elements match condition
    print("\n3. All Elements Match")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="tags/all(t: t ne 'deprecated')"
        ))
        print_results(results, "Filter: all tags are not 'deprecated'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Complex collection filter
    print("\n4. Complex Collection Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="tags/any(t: t eq 'tutorial') and rating ge 4.0"
        ))
        print_results(results, "Filter: has 'tutorial' tag AND rating >= 4.0")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def string_functions(search_client: SearchClient) -> None:
    """
    Demonstrate string functions in filters.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("STRING FUNCTION EXAMPLES")
    print("="*80)
    
    # Example 1: startswith function
    print("\n1. Starts With Function")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="startswith(category, 'Tech')"
        ))
        print_results(results, "Filter: startswith(category, 'Tech')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: endswith function
    print("\n2. Ends With Function")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="endswith(title, 'Guide')"
        ))
        print_results(results, "Filter: endswith(title, 'Guide')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: contains function (substring search)
    print("\n3. Contains Function")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="contains(title, 'Azure')"
        ))
        print_results(results, "Filter: contains(title, 'Azure')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: length function
    print("\n4. Length Function")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="length(title) gt 20"
        ))
        print_results(results, "Filter: length(title) gt 20")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def numeric_filters(search_client: SearchClient) -> None:
    """
    Demonstrate numeric filtering with various data types.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("NUMERIC FILTER EXAMPLES")
    print("="*80)
    
    # Example 1: Price range filter
    print("\n1. Price Range Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="price ge 10.0 and price le 100.0"
        ))
        print_results(results, "Filter: price between $10 and $100")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Rating threshold
    print("\n2. High Rating Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating ge 4.5"
        ))
        print_results(results, "Filter: rating >= 4.5 (highly rated)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Multiple numeric conditions
    print("\n3. Multiple Numeric Conditions")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating ge 4.0 and price le 50.0"
        ))
        print_results(results, "Filter: rating >= 4.0 AND price <= $50")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def advanced_filter_patterns(search_client: SearchClient) -> None:
    """
    Demonstrate advanced filter patterns and best practices.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("ADVANCED FILTER PATTERNS")
    print("="*80)
    
    # Example 1: Null value handling
    print("\n1. Null Value Handling")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating ne null"
        ))
        print_results(results, "Filter: rating is not null")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Case-sensitive string comparison
    print("\n2. Case-Sensitive Comparison")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category eq 'TECHNOLOGY'"  # This might not match 'Technology'
        ))
        print_results(results, "Filter: category eq 'TECHNOLOGY' (case-sensitive)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Complex nested conditions
    print("\n3. Complex Nested Conditions")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="((category eq 'Technology' and rating gt 4.0) or (category eq 'Science' and rating gt 3.5)) and publishedDate ge 2023-01-01T00:00:00Z"
        ))
        print_results(results, "Filter: Complex nested conditions")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Performance-optimized filter
    print("\n4. Performance-Optimized Filter")
    print("-" * 40)
    
    try:
        # Put most selective filters first
        results = list(search_client.search(
            search_text="azure",  # Search text first
            filter="rating ge 4.0 and category eq 'Technology'",  # Most selective filter first
            top=10
        ))
        print_results(results, "Optimized: search + selective filters")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def filter_validation_examples(search_client: SearchClient) -> None:
    """
    Demonstrate filter validation and error handling.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("FILTER VALIDATION EXAMPLES")
    print("="*80)
    
    # Example 1: Valid filter
    print("\n1. Valid Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category eq 'Technology'"
        ))
        print(f"✅ Valid filter executed successfully: {len(results)} results")
        
    except HttpResponseError as e:
        print(f"❌ Filter failed: {e.message}")
    
    # Example 2: Invalid field name
    print("\n2. Invalid Field Name")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="nonexistent_field eq 'value'"
        ))
        print(f"Results: {len(results)}")
        
    except HttpResponseError as e:
        print(f"❌ Expected error - Invalid field: {e.message}")
    
    # Example 3: Invalid syntax
    print("\n3. Invalid Filter Syntax")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="category = 'Technology'"  # Should be 'eq' not '='
        ))
        print(f"Results: {len(results)}")
        
    except HttpResponseError as e:
        print(f"❌ Expected error - Invalid syntax: {e.message}")
    
    # Example 4: Type mismatch
    print("\n4. Type Mismatch")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            filter="rating eq 'high'"  # Should be numeric, not string
        ))
        print(f"Results: {len(results)}")
        
    except HttpResponseError as e:
        print(f"❌ Expected error - Type mismatch: {e.message}")

def main():
    """
    Main function to run all filtering examples.
    """
    print("Azure AI Search - Filtering Examples")
    print("=" * 80)
    
    try:
        # Create search client
        search_client = create_search_client()
        print(f"✅ Connected to search service: {os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')}")
        print(f"✅ Using index: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
        
        # Run examples
        equality_filters(search_client)
        comparison_filters(search_client)
        logical_operators(search_client)
        date_filters(search_client)
        collection_filters(search_client)
        string_functions(search_client)
        numeric_filters(search_client)
        advanced_filter_patterns(search_client)
        filter_validation_examples(search_client)
        
        print("\n" + "="*80)
        print("✅ All filtering examples completed successfully!")
        print("="*80)
        
        print("\n📚 What you learned:")
        print("• How to use equality and comparison operators")
        print("• How to combine filters with logical operators")
        print("• How to filter by dates and numeric ranges")
        print("• How to work with collection fields")
        print("• How to use string functions in filters")
        print("• How to handle filter validation and errors")
        
        print("\n🔗 Next steps:")
        print("• Run 03_sorting_pagination.py to learn about result ordering")
        print("• Experiment with complex filter combinations")
        print("• Try filters with your own data fields")
        
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