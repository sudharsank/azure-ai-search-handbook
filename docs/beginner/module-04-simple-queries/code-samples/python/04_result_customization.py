#!/usr/bin/env python3
"""
Module 4: Simple Queries and Filters - Result Customization
===========================================================

This script demonstrates result customization in Azure AI Search using Python.
Learn how to select specific fields, highlight matching terms, and format results.

Prerequisites:
- Azure AI Search service configured
- Sample index with data (from previous modules)
- Environment variables set in .env file

Author: Azure AI Search Tutorial
"""

import os
import sys
import json
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

def print_results(results: List[Dict[str, Any]], title: str, max_results: int = 5, 
                 show_highlights: bool = False) -> None:
    """
    Print search results in a formatted way.
    
    Args:
        results: List of search result documents
        title: Title for the result set
        max_results: Maximum number of results to display
        show_highlights: Whether to display highlight information
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
        
        # Show selected fields
        for key, value in result.items():
            if not key.startswith('@search') and key not in ['title']:
                if isinstance(value, list):
                    print(f"   {key.title()}: {', '.join(map(str, value[:3]))}{'...' if len(value) > 3 else ''}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"   {key.title()}: {value[:100]}...")
                else:
                    print(f"   {key.title()}: {value}")
        
        # Show highlights if requested
        if show_highlights and '@search.highlights' in result:
            highlights = result['@search.highlights']
            print(f"   Highlights:")
            for field, highlight_list in highlights.items():
                for highlight in highlight_list[:2]:  # Show first 2 highlights per field
                    print(f"     {field}: {highlight}")
    
    if len(results) > max_results:
        print(f"\n... and {len(results) - max_results} more results")

def field_selection_examples(search_client: SearchClient) -> None:
    """
    Demonstrate field selection to customize returned data.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("FIELD SELECTION EXAMPLES")
    print("="*80)
    
    # Example 1: All fields (default behavior)
    print("\n1. All Fields (Default)")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            top=2
        ))
        print_results(results, "All fields returned", max_results=2)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Select specific fields
    print("\n2. Select Specific Fields")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            select=["id", "title", "category", "rating"],
            top=3
        ))
        print_results(results, "Selected fields: id, title, category, rating", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Minimal field selection for performance
    print("\n3. Minimal Fields for Performance")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            select=["id", "title"],  # Only essential fields
            top=5
        ))
        print_results(results, "Minimal fields: id, title only", max_results=5)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Exclude large content fields
    print("\n4. Exclude Large Content Fields")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="tutorial",
            select=["id", "title", "category", "rating", "publishedDate"],  # Exclude 'content'
            top=3
        ))
        print_results(results, "Exclude large content field", max_results=3)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def search_highlighting_examples(search_client: SearchClient) -> None:
    """
    Demonstrate search result highlighting.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("SEARCH HIGHLIGHTING EXAMPLES")
    print("="*80)
    
    # Example 1: Basic highlighting
    print("\n1. Basic Highlighting")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="machine learning",
            highlight_fields=["title", "content"],
            top=3
        ))
        print_results(results, "Basic highlighting on title and content", 
                     max_results=3, show_highlights=True)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Custom highlight tags
    print("\n2. Custom Highlight Tags")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure search",
            highlight_fields=["title", "content"],
            highlight_pre_tag="<mark>",
            highlight_post_tag="</mark>",
            top=3
        ))
        print_results(results, "Custom highlight tags: <mark>...</mark>", 
                     max_results=3, show_highlights=True)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Multiple highlight tags for different terms
    print("\n3. Multiple Highlight Tags")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python tutorial",
            highlight_fields=["title", "content"],
            highlight_pre_tag="<strong class='highlight'>",
            highlight_post_tag="</strong>",
            top=3
        ))
        print_results(results, "HTML highlight tags with CSS class", 
                     max_results=3, show_highlights=True)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 4: Highlighting with field selection
    print("\n4. Highlighting with Field Selection")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure cognitive",
            select=["id", "title", "category"],
            highlight_fields=["title"],  # Only highlight title
            highlight_pre_tag="**",
            highlight_post_tag="**",
            top=3
        ))
        print_results(results, "Selected fields + title highlighting", 
                     max_results=3, show_highlights=True)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def result_metadata_examples(search_client: SearchClient) -> None:
    """
    Demonstrate working with search result metadata.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("RESULT METADATA EXAMPLES")
    print("="*80)
    
    # Example 1: Search score analysis
    print("\n1. Search Score Analysis")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure machine learning",
            top=5
        ))
        
        print("Search Score Analysis:")
        print("-" * 30)
        for i, result in enumerate(results):
            score = result.get('@search.score', 0)
            title = result.get('title', 'No title')
            print(f"{i+1}. Score: {score:.4f} - {title[:50]}...")
        
        if results:
            scores = [r.get('@search.score', 0) for r in results]
            print(f"\nScore Statistics:")
            print(f"• Highest: {max(scores):.4f}")
            print(f"• Lowest: {min(scores):.4f}")
            print(f"• Average: {sum(scores)/len(scores):.4f}")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Highlight metadata
    print("\n2. Highlight Metadata Analysis")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python programming",
            highlight_fields=["title", "content"],
            top=3
        ))
        
        print("Highlight Analysis:")
        print("-" * 30)
        for i, result in enumerate(results):
            title = result.get('title', 'No title')
            print(f"\n{i+1}. {title}")
            
            if '@search.highlights' in result:
                highlights = result['@search.highlights']
                for field, highlight_list in highlights.items():
                    print(f"   {field} highlights: {len(highlight_list)}")
                    for j, highlight in enumerate(highlight_list[:2]):
                        print(f"     {j+1}: {highlight}")
            else:
                print("   No highlights found")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def custom_result_formatting(search_client: SearchClient) -> None:
    """
    Demonstrate custom result formatting and processing.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("CUSTOM RESULT FORMATTING")
    print("="*80)
    
    def format_search_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Custom formatter for search results.
        
        Args:
            result: Raw search result
            
        Returns:
            Formatted result dictionary
        """
        formatted = {
            'id': result.get('id'),
            'title': result.get('title', 'Untitled'),
            'summary': result.get('content', '')[:150] + '...' if result.get('content') else '',
            'metadata': {
                'score': round(result.get('@search.score', 0), 3),
                'category': result.get('category', 'Uncategorized'),
                'rating': result.get('rating'),
                'published': result.get('publishedDate'),
                'tags': result.get('tags', [])[:5]  # Limit to 5 tags
            }
        }
        
        # Add highlights if available
        if '@search.highlights' in result:
            formatted['highlights'] = {}
            for field, highlights in result['@search.highlights'].items():
                formatted['highlights'][field] = highlights[:2]  # Limit to 2 per field
        
        return formatted
    
    # Example 1: Custom formatted results
    print("\n1. Custom Formatted Results")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure tutorial",
            select=["id", "title", "content", "category", "rating", "publishedDate", "tags"],
            highlight_fields=["title", "content"],
            top=3
        ))
        
        formatted_results = [format_search_result(result) for result in results]
        
        print("Custom Formatted Results:")
        for i, result in enumerate(formatted_results):
            print(f"\n{i+1}. {result['title']}")
            print(f"   Summary: {result['summary']}")
            print(f"   Score: {result['metadata']['score']}")
            print(f"   Category: {result['metadata']['category']}")
            print(f"   Rating: {result['metadata']['rating']}")
            print(f"   Tags: {', '.join(result['metadata']['tags'])}")
            
            if 'highlights' in result:
                print(f"   Highlights: {len(result['highlights'])} fields")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: JSON export format
    print("\n2. JSON Export Format")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="python",
            select=["id", "title", "category", "rating"],
            top=2
        ))
        
        # Convert to JSON-serializable format
        json_results = []
        for result in results:
            json_result = {}
            for key, value in result.items():
                if not key.startswith('@search'):
                    json_result[key] = value
                elif key == '@search.score':
                    json_result['searchScore'] = round(value, 3)
            json_results.append(json_result)
        
        print("JSON Export Format:")
        print(json.dumps(json_results, indent=2, default=str))
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def result_aggregation_examples(search_client: SearchClient) -> None:
    """
    Demonstrate result aggregation and summary statistics.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("RESULT AGGREGATION EXAMPLES")
    print("="*80)
    
    # Example 1: Category distribution
    print("\n1. Category Distribution Analysis")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            select=["category", "rating"],
            top=50  # Get more results for analysis
        ))
        
        # Aggregate by category
        category_counts = {}
        category_ratings = {}
        
        for result in results:
            category = result.get('category', 'Unknown')
            rating = result.get('rating')
            
            category_counts[category] = category_counts.get(category, 0) + 1
            
            if rating is not None:
                if category not in category_ratings:
                    category_ratings[category] = []
                category_ratings[category].append(rating)
        
        print("Category Distribution:")
        for category, count in sorted(category_counts.items()):
            avg_rating = sum(category_ratings.get(category, [0])) / len(category_ratings.get(category, [1]))
            print(f"• {category}: {count} documents (avg rating: {avg_rating:.1f})")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Rating distribution
    print("\n2. Rating Distribution Analysis")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="*",
            select=["rating"],
            top=50
        ))
        
        # Aggregate by rating ranges
        rating_ranges = {
            '5.0': 0,
            '4.0-4.9': 0,
            '3.0-3.9': 0,
            '2.0-2.9': 0,
            '1.0-1.9': 0,
            'No rating': 0
        }
        
        for result in results:
            rating = result.get('rating')
            if rating is None:
                rating_ranges['No rating'] += 1
            elif rating >= 5.0:
                rating_ranges['5.0'] += 1
            elif rating >= 4.0:
                rating_ranges['4.0-4.9'] += 1
            elif rating >= 3.0:
                rating_ranges['3.0-3.9'] += 1
            elif rating >= 2.0:
                rating_ranges['2.0-2.9'] += 1
            else:
                rating_ranges['1.0-1.9'] += 1
        
        print("Rating Distribution:")
        for range_name, count in rating_ranges.items():
            percentage = (count / len(results)) * 100 if results else 0
            print(f"• {range_name}: {count} documents ({percentage:.1f}%)")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def performance_optimization_examples(search_client: SearchClient) -> None:
    """
    Demonstrate performance optimization techniques for result customization.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("PERFORMANCE OPTIMIZATION")
    print("="*80)
    
    import time
    
    # Example 1: Field selection performance comparison
    print("\n1. Field Selection Performance")
    print("-" * 40)
    
    try:
        # All fields query
        start_time = time.time()
        results_all = list(search_client.search(
            search_text="azure",
            top=20
        ))
        time_all = time.time() - start_time
        
        # Selected fields query
        start_time = time.time()
        results_selected = list(search_client.search(
            search_text="azure",
            select=["id", "title", "category"],
            top=20
        ))
        time_selected = time.time() - start_time
        
        print(f"All fields query: {time_all:.3f} seconds ({len(results_all)} results)")
        print(f"Selected fields query: {time_selected:.3f} seconds ({len(results_selected)} results)")
        
        if time_all > 0:
            improvement = ((time_all - time_selected) / time_all) * 100
            print(f"Performance improvement: {improvement:.1f}%")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 2: Highlighting performance impact
    print("\n2. Highlighting Performance Impact")
    print("-" * 40)
    
    try:
        # Without highlighting
        start_time = time.time()
        results_no_highlight = list(search_client.search(
            search_text="machine learning tutorial",
            select=["id", "title", "category"],
            top=10
        ))
        time_no_highlight = time.time() - start_time
        
        # With highlighting
        start_time = time.time()
        results_highlight = list(search_client.search(
            search_text="machine learning tutorial",
            select=["id", "title", "category"],
            highlight_fields=["title", "content"],
            top=10
        ))
        time_highlight = time.time() - start_time
        
        print(f"Without highlighting: {time_no_highlight:.3f} seconds")
        print(f"With highlighting: {time_highlight:.3f} seconds")
        
        if time_no_highlight > 0:
            overhead = ((time_highlight - time_no_highlight) / time_no_highlight) * 100
            print(f"Highlighting overhead: {overhead:.1f}%")
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")
    
    # Example 3: Optimal result customization
    print("\n3. Optimal Result Customization")
    print("-" * 40)
    
    try:
        results = list(search_client.search(
            search_text="azure",
            select=["id", "title", "category", "rating"],  # Only needed fields
            highlight_fields=["title"],  # Minimal highlighting
            top=10,  # Reasonable page size
            filter="rating ge 3.0"  # Pre-filter for better performance
        ))
        
        print("Optimized query configuration:")
        print("• Selected essential fields only")
        print("• Limited highlighting to title field")
        print("• Used reasonable page size (10)")
        print("• Applied pre-filter to reduce dataset")
        print(f"• Results: {len(results)} documents")
        
        print_results(results, "Optimized results", max_results=3, show_highlights=True)
        
    except HttpResponseError as e:
        print(f"Search failed: {e.message}")

def main():
    """
    Main function to run all result customization examples.
    """
    print("Azure AI Search - Result Customization Examples")
    print("=" * 80)
    
    try:
        # Create search client
        search_client = create_search_client()
        print(f"✅ Connected to search service: {os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')}")
        print(f"✅ Using index: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
        
        # Run examples
        field_selection_examples(search_client)
        search_highlighting_examples(search_client)
        result_metadata_examples(search_client)
        custom_result_formatting(search_client)
        result_aggregation_examples(search_client)
        performance_optimization_examples(search_client)
        
        print("\n" + "="*80)
        print("✅ All result customization examples completed successfully!")
        print("="*80)
        
        print("\n📚 What you learned:")
        print("• How to select specific fields to optimize performance")
        print("• How to implement search result highlighting")
        print("• How to work with search metadata and scores")
        print("• How to format and process results for different use cases")
        print("• How to aggregate and analyze result data")
        print("• How to optimize result customization for performance")
        
        print("\n🔗 Next steps:")
        print("• Run 05_advanced_queries.py to learn advanced query techniques")
        print("• Experiment with different field combinations")
        print("• Build custom result formatters for your applications")
        
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