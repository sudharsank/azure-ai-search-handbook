#!/usr/bin/env python3
"""
Module 4: Simple Queries and Filters - Advanced Queries
=======================================================

This script demonstrates advanced query techniques in Azure AI Search using Python.
Learn about field boosting, fuzzy search, wildcards, and complex query patterns.

Prerequisites:
- Azure AI Search service configured
- Sample index with data (from previous modules)
- Environment variables set in .env file

Author: Azure AI Search Tutorial
"""

import os
import sys
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
        print(f"   Score: {result.get('@search.score', 'N/A'):.4f}")
        print(f"   Category: {result.get('category', 'N/A')}")
        print(f"   Rating: {result.get('rating', 'N/A')}")
        
        # Show content preview
        content = result.get('content', '')
        if content:
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   Preview: {preview}")
    
    if len(results) > max_results:
        print(f"\n... and {len(results) - max_results} more results")

def field_boosting_examples(search_client: SearchClient) -> None:
    """
    Demonstrate field boosting to influence relevance scoring.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("FIELD BOOSTING EXAMPLES")
    print("="*80)
    
    # Example 1: No boosting (baseline)
    print("\n1. No Field Boosting (Baseline)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python tutorial",
            search_fields=["title", "content"],
            top=5
        ))
        print_results(results, "No boosting - equal weight for all fields")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Boost title field
    print("\n2. Boost Title Field (3x weight)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python tutorial",
            search_fields=["title^3", "content"],  # Title weighted 3x
            top=5
        ))
        print_results(results, "Title boosted 3x - title matches score higher")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Multiple field boosting
    print("\n3. Multiple Field Boosting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure machine learning",
            search_fields=["title^5", "category^2", "content"],  # Title 5x, category 2x
            top=5
        ))
        print_results(results, "Title 5x, category 2x, content 1x")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Extreme boosting comparison
    print("\n4. Extreme Boosting Comparison")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="tutorial",
            search_fields=["title^10", "content"],  # Extreme title boost
            top=5
        ))
        print_results(results, "Extreme title boosting (10x)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def fuzzy_search_examples(search_client: SearchClient) -> None:
    """
    Demonstrate fuzzy search for handling typos and variations.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("FUZZY SEARCH EXAMPLES")
    print("="*80)
    
    # Example 1: Exact match (baseline)
    print("\n1. Exact Match (Baseline)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="machine",
            query_type="simple",
            top=3
        ))
        print_results(results, "Exact match: 'machine'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Fuzzy search with typo
    print("\n2. Fuzzy Search with Typo")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="machne~",  # Typo: missing 'i'
            query_type="full",  # Requires full Lucene syntax
            top=3
        ))
        print_results(results, "Fuzzy search: 'machne~' (should match 'machine')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Fuzzy search with edit distance
    print("\n3. Fuzzy Search with Edit Distance")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="learing~2",  # Allow up to 2 character differences
            query_type="full",
            top=3
        ))
        print_results(results, "Fuzzy search: 'learing~2' (should match 'learning')")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Multiple fuzzy terms
    print("\n4. Multiple Fuzzy Terms")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="machne~ learing~",  # Multiple fuzzy terms
            query_type="full",
            top=3
        ))
        print_results(results, "Multiple fuzzy: 'machne~ learing~'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def wildcard_search_examples(search_client: SearchClient) -> None:
    """
    Demonstrate wildcard search patterns.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("WILDCARD SEARCH EXAMPLES")
    print("="*80)
    
    # Example 1: Suffix wildcard
    print("\n1. Suffix Wildcard")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="develop*",  # Matches develop, developer, development, etc.
            top=5
        ))
        print_results(results, "Suffix wildcard: 'develop*'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Prefix wildcard (requires full Lucene)
    print("\n2. Prefix Wildcard")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*ing",  # Matches words ending in 'ing'
            query_type="full",
            top=5
        ))
        print_results(results, "Prefix wildcard: '*ing'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Middle wildcard
    print("\n3. Middle Wildcard")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="mach*ne",  # Matches machine, etc.
            query_type="full",
            top=5
        ))
        print_results(results, "Middle wildcard: 'mach*ne'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Single character wildcard
    print("\n4. Single Character Wildcard")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="te?t",  # Matches test, text, etc.
            query_type="full",
            top=5
        ))
        print_results(results, "Single char wildcard: 'te?t'")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def proximity_search_examples(search_client: SearchClient) -> None:
    """
    Demonstrate proximity search for terms near each other.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("PROXIMITY SEARCH EXAMPLES")
    print("="*80)
    
    # Example 1: Exact phrase
    print("\n1. Exact Phrase")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text='"machine learning"',  # Exact phrase
            top=3
        ))
        print_results(results, 'Exact phrase: "machine learning"')
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Proximity search (within N words)
    print("\n2. Proximity Search (Within 5 Words)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text='"machine learning"~5',  # Within 5 words of each other
            query_type="full",
            top=3
        ))
        print_results(results, 'Proximity: "machine learning"~5')
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Looser proximity
    print("\n3. Looser Proximity (Within 10 Words)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text='"azure cognitive"~10',
            query_type="full",
            top=3
        ))
        print_results(results, 'Proximity: "azure cognitive"~10')
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def regular_expression_examples(search_client: SearchClient) -> None:
    """
    Demonstrate regular expression search patterns.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("REGULAR EXPRESSION EXAMPLES")
    print("="*80)
    
    # Example 1: Simple regex pattern
    print("\n1. Simple Regex Pattern")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="/[Tt]utorial/",  # Matches Tutorial or tutorial
            query_type="full",
            top=3
        ))
        print_results(results, "Regex: /[Tt]utorial/")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Number pattern
    print("\n2. Number Pattern")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="/[0-9]+/",  # Matches any number
            query_type="full",
            top=3
        ))
        print_results(results, "Regex: /[0-9]+/ (any number)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Version pattern
    print("\n3. Version Pattern")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="/[0-9]+\\.[0-9]+/",  # Matches version numbers like 3.8
            query_type="full",
            top=3
        ))
        print_results(results, "Regex: /[0-9]+\\.[0-9]+/ (version numbers)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def complex_query_combinations(search_client: SearchClient) -> None:
    """
    Demonstrate complex combinations of advanced query features.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("COMPLEX QUERY COMBINATIONS")
    print("="*80)
    
    # Example 1: Boosting + Fuzzy + Filter
    print("\n1. Boosting + Fuzzy + Filter")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="machne~ learing~",  # Fuzzy search
            search_fields=["title^3", "content"],  # Field boosting
            filter="rating ge 3.0",  # Filter
            query_type="full",
            top=3
        ))
        print_results(results, "Fuzzy + boosting + filter combination")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Wildcard + Proximity + Sorting
    print("\n2. Wildcard + Proximity + Sorting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text='develop* AND "tutorial guide"~3',  # Wildcard + proximity
            order_by=["rating desc"],  # Sorting
            query_type="full",
            top=3
        ))
        print_results(results, "Wildcard + proximity + sorting")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Multiple techniques with highlighting
    print("\n3. Multiple Techniques + Highlighting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python* OR java*",  # Wildcard OR
            search_fields=["title^2", "content"],  # Boosting
            filter="category eq 'Technology'",  # Filter
            highlight_fields=["title", "content"],  # Highlighting
            order_by=["@search.score desc"],  # Sort by relevance
            query_type="full",
            top=3
        ))
        
        print_results(results, "Complex combination with highlighting")
        
        # Show highlights
        for i, result in enumerate(results[:2]):
            if '@search.highlights' in result:
                print(f"\nHighlights for result {i+1}:")
                for field, highlights in result['@search.highlights'].items():
                    for highlight in highlights[:1]:
                        print(f"  {field}: {highlight}")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def query_performance_analysis(search_client: SearchClient) -> None:
    """
    Analyze performance of different advanced query techniques.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("QUERY PERFORMANCE ANALYSIS")
    print("="*80)
    
    import time
    
    queries = [
        ("Simple text", "azure machine learning", "simple"),
        ("Wildcard", "develop*", "simple"),
        ("Fuzzy", "machne~ learing~", "full"),
        ("Regex", "/[Tt]utorial/", "full"),
        ("Complex", 'python* AND "tutorial guide"~3', "full")
    ]
    
    print("\nPerformance Comparison:")
    print("-" * 40)
    
    for name, query, query_type in queries:
        try:
            start_time = time.time()
            
            results = list(search_client.search(
                search_text=query,
                query_type=query_type,
                top=10
            ))
            
            execution_time = time.time() - start_time
            
            print(f"{name:15} | {execution_time:6.3f}s | {len(results):3d} results | {query}")
            
        except HttpResponseError as e:
            print(f"{name:15} | ERROR   | {str(e)[:50]}...")
    
    print("\nPerformance Tips:")
    print("• Simple queries are fastest")
    print("• Wildcard queries are moderately fast")
    print("• Fuzzy queries add processing overhead")
    print("• Regex queries can be slow with complex patterns")
    print("• Complex combinations multiply overhead")

def advanced_scoring_examples(search_client: SearchClient) -> None:
    """
    Demonstrate advanced scoring and relevance techniques.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("ADVANCED SCORING EXAMPLES")
    print("="*80)
    
    # Example 1: Score analysis with different query types
    print("\n1. Score Analysis by Query Type")
    print("-" * 40)
    
    query_types = [
        ("Simple", "azure tutorial", "simple"),
        ("Fuzzy", "azure~ tutorial~", "full"),
        ("Wildcard", "azure* tutorial*", "full")
    ]
    
    for name, query, query_type in query_types:
        try:
            results = list(search_client.search(
                search_text=query,
                query_type=query_type,
                top=3
            ))
            
            if results:
                scores = [r.get('@search.score', 0) for r in results]
                avg_score = sum(scores) / len(scores)
                print(f"\n{name} Query: '{query}'")
                print(f"  Average score: {avg_score:.4f}")
                print(f"  Score range: {min(scores):.4f} - {max(scores):.4f}")
            
        except HttpResponseError as e:
            print(f"{name} query failed: {e.message}")
    
    # Example 2: Boosting impact on scores
    print("\n2. Boosting Impact on Scores")
    print("-" * 40)
    
    try:
        # No boosting
        results_normal = list(search_client.search(
            search_text="python tutorial",
            search_fields=["title", "content"],
            top=3
        ))
        
        # With boosting
        results_boosted = list(search_client.search(
            search_text="python tutorial",
            search_fields=["title^5", "content"],
            top=3
        ))
        
        print("Score comparison (same query, different boosting):")
        print("\nNo boosting:")
        for i, result in enumerate(results_normal[:2]):
            print(f"  {i+1}. Score: {result.get('@search.score', 0):.4f} - {result.get('title', '')[:40]}...")
        
        print("\nWith title boosting (5x):")
        for i, result in enumerate(results_boosted[:2]):
            print(f"  {i+1}. Score: {result.get('@search.score', 0):.4f} - {result.get('title', '')[:40]}...")
        
    except HttpResponseError as e:
        print(f"Boosting comparison failed: {e.message}")

def main():
    """
    Main function to run all advanced query examples.
    """
    print("Azure AI Search - Advanced Queries Examples")
    print("=" * 80)
    
    try:
        # Create search client
        search_client = create_search_client()
        print(f"✅ Connected to search service: {os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')}")
        print(f"✅ Using index: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
        
        # Run examples
        field_boosting_examples(search_client)
        fuzzy_search_examples(search_client)
        wildcard_search_examples(search_client)
        proximity_search_examples(search_client)
        regular_expression_examples(search_client)
        complex_query_combinations(search_client)
        query_performance_analysis(search_client)
        advanced_scoring_examples(search_client)
        
        print("\n" + "="*80)
        print("✅ All advanced query examples completed successfully!")
        print("="*80)
        
        print("\n📚 What you learned:")
        print("• How to use field boosting to influence relevance")
        print("• How to implement fuzzy search for typo tolerance")
        print("• How to use wildcard patterns for flexible matching")
        print("• How to perform proximity and phrase searches")
        print("• How to use regular expressions in queries")
        print("• How to combine multiple advanced techniques")
        print("• How to analyze and optimize query performance")
        
        print("\n🔗 Next steps:")
        print("• Run 06_error_handling.py to learn robust query implementation")
        print("• Experiment with different boosting values")
        print("• Try complex query combinations with your data")
        print("• Monitor query performance in production")
        
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