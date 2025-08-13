#!/usr/bin/env python3
"""
Module 4: Simple Queries and Filters - Basic Queries
====================================================

This script demonstrates basic text search operations in Azure AI Search using Python.
Learn how to perform simple searches, use query operators, and work with search fields.

Prerequisites:
- Azure AI Search service configured
- Sample index with data (from previous modules)
- Environment variables set in .env file

Author: Azure AI Search Tutorial
"""

import os
import sys
from typing import List, Dict, Any, Optional
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
        print(f"   ID: {result.get('id', 'N/A')}")
        
        # Show content preview if available
        content = result.get('content', '')
        if content:
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   Preview: {preview}")
    
    if len(results) > max_results:
        print(f"\n... and {len(results) - max_results} more results")

def basic_text_search(search_client: SearchClient) -> None:
    """
    Demonstrate basic text search operations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("BASIC TEXT SEARCH EXAMPLES")
    print("="*80)
    
    # Example 1: Simple text search
    print("\n1. Simple Text Search")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="azure"))
        print_results(results, "Search: 'azure'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
        return
    
    # Example 2: Multi-word search
    print("\n2. Multi-word Search")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="machine learning"))
        print_results(results, "Search: 'machine learning'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Empty search (returns all documents)
    print("\n3. Empty Search (All Documents)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="*", top=3))
        print_results(results, "Search: '*' (all documents)", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def search_with_fields(search_client: SearchClient) -> None:
    """
    Demonstrate searching in specific fields.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("FIELD-SPECIFIC SEARCH EXAMPLES")
    print("="*80)
    
    # Example 1: Search in title field only
    print("\n1. Search in Title Field Only")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python",
            search_fields=["title"]
        ))
        print_results(results, "Search: 'python' in title field")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Search in multiple specific fields
    print("\n2. Search in Multiple Fields")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            search_fields=["title", "content"]
        ))
        print_results(results, "Search: 'azure' in title and content fields")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Search with field boosting (title field weighted more)
    print("\n3. Search with Field Boosting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="tutorial",
            search_fields=["title^3", "content"]  # Title matches weighted 3x
        ))
        print_results(results, "Search: 'tutorial' with title boosting (3x)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def query_operators(search_client: SearchClient) -> None:
    """
    Demonstrate query operators in simple syntax.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("QUERY OPERATORS EXAMPLES")
    print("="*80)
    
    # Example 1: Required term (+)
    print("\n1. Required Term (+)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="+azure search"))
        print_results(results, "Search: '+azure search' (azure is required)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Excluded term (-)
    print("\n2. Excluded Term (-)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="azure -cognitive"))
        print_results(results, "Search: 'azure -cognitive' (exclude cognitive)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Exact phrase ("")
    print("\n3. Exact Phrase Search")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text='"machine learning"'))
        print_results(results, 'Search: "machine learning" (exact phrase)')
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Wildcard search (*)
    print("\n4. Wildcard Search")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="develop*"))
        print_results(results, "Search: 'develop*' (wildcard)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 5: Grouping with parentheses
    print("\n5. Grouping with Parentheses")
    print("-" * 40)
    
    try:
        results = list(search_client.search(search_text="(azure OR microsoft) search"))
        print_results(results, "Search: '(azure OR microsoft) search'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def search_modes_and_types(search_client: SearchClient) -> None:
    """
    Demonstrate different search modes and query types.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("SEARCH MODES AND QUERY TYPES")
    print("="*80)
    
    # Example 1: Any search mode (default)
    print("\n1. Search Mode: Any (Default)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure machine learning",
            search_mode="any"
        ))
        print_results(results, "Search mode 'any': matches any term")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: All search mode
    print("\n2. Search Mode: All")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure machine learning",
            search_mode="all"
        ))
        print_results(results, "Search mode 'all': matches all terms")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Simple query type (default)
    print("\n3. Query Type: Simple (Default)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure AND search",
            query_type="simple"
        ))
        print_results(results, "Simple query type with AND operator")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Full Lucene query type
    print("\n4. Query Type: Full Lucene")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="title:azure AND content:search",
            query_type="full"
        ))
        print_results(results, "Full Lucene query with field-specific search")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def advanced_text_features(search_client: SearchClient) -> None:
    """
    Demonstrate advanced text search features.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("ADVANCED TEXT SEARCH FEATURES")
    print("="*80)
    
    # Example 1: Case sensitivity (searches are case-insensitive by default)
    print("\n1. Case Insensitive Search")
    print("-" * 40)
    
    try:
        results_lower = list(search_client.search(search_text="azure"))
        results_upper = list(search_client.search(search_text="AZURE"))
        
        print(f"Search 'azure': {len(results_lower)} results")
        print(f"Search 'AZURE': {len(results_upper)} results")
        print("Note: Both searches return the same results (case-insensitive)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Minimum should match
    print("\n2. Search with Top Parameter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure machine learning",
            top=3  # Limit to top 3 results
        ))
        print_results(results, "Top 3 results for 'azure machine learning'", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Include total count
    print("\n3. Include Total Count")
    print("-" * 40)
    
    try:
        results = search_client.search(
            search_text="azure",
            include_total_count=True,
            top=5
        )
        
        result_list = list(results)
        total_count = results.get_count()
        
        print(f"Total matching documents: {total_count}")
        print(f"Returned documents: {len(result_list)}")
        print_results(result_list, "Sample results with total count", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def demonstrate_result_metadata(search_client: SearchClient) -> None:
    """
    Demonstrate working with search result metadata.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("SEARCH RESULT METADATA")
    print("="*80)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            top=3
        ))
        
        print("\nDetailed Result Analysis:")
        print("-" * 40)
        
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"  Document ID: {result.get('id', 'N/A')}")
            print(f"  Search Score: {result.get('@search.score', 'N/A'):.4f}")
            print(f"  Title: {result.get('title', 'N/A')}")
            
            # Show all available fields
            print("  Available fields:")
            for key, value in result.items():
                if not key.startswith('@search'):
                    field_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"    {key}: {field_preview}")
                    
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def main():
    """
    Main function to run all basic query examples.
    """
    print("Azure AI Search - Basic Queries Examples")
    print("=" * 80)
    
    try:
        # Create search client
        search_client = create_search_client()
        print(f"✅ Connected to search service: {os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')}")
        print(f"✅ Using index: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
        
        # Run examples
        basic_text_search(search_client)
        search_with_fields(search_client)
        query_operators(search_client)
        search_modes_and_types(search_client)
        advanced_text_features(search_client)
        demonstrate_result_metadata(search_client)
        
        print("\n" + "="*80)
        print("✅ All basic query examples completed successfully!")
        print("="*80)
        
        print("\n📚 What you learned:")
        print("• How to perform simple text searches")
        print("• How to search in specific fields")
        print("• How to use query operators (+, -, \"\", *, ())")
        print("• How to work with search modes and query types")
        print("• How to access search result metadata")
        
        print("\n🔗 Next steps:")
        print("• Run 02_filtering.py to learn about OData filters")
        print("• Experiment with your own search terms")
        print("• Try different field combinations")
        
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