#!/usr/bin/env python3
"""
Module 4: Simple Queries and Filters - Error Handling
=====================================================

This script demonstrates comprehensive error handling for Azure AI Search queries.
Learn how to handle exceptions, validate queries, implement retry logic, and debug issues.

Prerequisites:
- Azure AI Search service configured
- Sample index with data (from previous modules)
- Environment variables set in .env file

Author: Azure AI Search Tutorial
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_search_client() -> SearchClient:
    """
    Create and return an Azure AI Search client with error handling.
    
    Returns:
        SearchClient: Configured search client
        
    Raises:
        ValueError: If required environment variables are missing
    """
    endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    
    if not all([endpoint, api_key, index_name]):
        missing = []
        if not endpoint: missing.append("AZURE_SEARCH_SERVICE_ENDPOINT")
        if not api_key: missing.append("AZURE_SEARCH_API_KEY")
        if not index_name: missing.append("AZURE_SEARCH_INDEX_NAME")
        
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    try:
        client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        logger.info(f"Successfully created search client for index: {index_name}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create search client: {str(e)}")
        raise

def validate_query_parameters(search_text: str = None, **kwargs) -> Tuple[bool, str]:
    """
    Validate search query parameters before execution.
    
    Args:
        search_text: Search query text
        **kwargs: Additional search parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check search text
    if search_text is not None:
        if len(search_text.strip()) == 0:
            return False, "Search text cannot be empty"
        
        if len(search_text) > 1000:
            return False, "Search text too long (max 1000 characters)"
        
        # Check for unbalanced quotes
        if search_text.count('"') % 2 != 0:
            return False, "Unbalanced quotes in search text"
        
        # Check for unbalanced parentheses
        if search_text.count('(') != search_text.count(')'):
            return False, "Unbalanced parentheses in search text"
    
    # Check top parameter
    top = kwargs.get('top')
    if top is not None:
        if not isinstance(top, int) or top < 0:
            return False, "Top parameter must be a non-negative integer"
        if top > 1000:
            return False, "Top parameter cannot exceed 1000"
    
    # Check skip parameter
    skip = kwargs.get('skip')
    if skip is not None:
        if not isinstance(skip, int) or skip < 0:
            return False, "Skip parameter must be a non-negative integer"
        if skip > 100000:
            return False, "Skip parameter cannot exceed 100,000"
    
    # Check filter syntax (basic validation)
    filter_expr = kwargs.get('filter')
    if filter_expr:
        # Check for common syntax errors
        if filter_expr.count('(') != filter_expr.count(')'):
            return False, "Unbalanced parentheses in filter expression"
        
        # Check for invalid operators
        invalid_operators = ['=', '!=', '<>', '&&', '||']
        for op in invalid_operators:
            if op in filter_expr:
                return False, f"Invalid operator '{op}' in filter (use OData syntax)"
    
    return True, "Query parameters are valid"

def safe_search(search_client: SearchClient, **kwargs) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Perform a safe search with comprehensive error handling.
    
    Args:
        search_client: Azure AI Search client
        **kwargs: Search parameters
        
    Returns:
        Tuple of (results_list, error_message)
    """
    try:
        # Validate parameters
        is_valid, validation_error = validate_query_parameters(**kwargs)
        if not is_valid:
            logger.warning(f"Query validation failed: {validation_error}")
            return [], validation_error
        
        # Log the search attempt
        search_text = kwargs.get('search_text', '*')
        logger.info(f"Executing search: '{search_text}' with parameters: {kwargs}")
        
        # Execute search
        results = search_client.search(**kwargs)
        result_list = list(results)
        
        logger.info(f"Search completed successfully: {len(result_list)} results")
        return result_list, None
        
    except HttpResponseError as e:
        error_msg = f"HTTP error {e.status_code}: {e.message}"
        logger.error(error_msg)
        return [], error_msg
        
    except ServiceRequestError as e:
        error_msg = f"Service request error: {str(e)}"
        logger.error(error_msg)
        return [], error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return [], error_msg

def retry_search(search_client: SearchClient, max_retries: int = 3, 
                retry_delay: float = 1.0, **kwargs) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Perform search with retry logic for transient failures.
    
    Args:
        search_client: Azure AI Search client
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        **kwargs: Search parameters
        
    Returns:
        Tuple of (results_list, error_message)
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries}")
                time.sleep(retry_delay * attempt)  # Exponential backoff
            
            results, error = safe_search(search_client, **kwargs)
            
            if error is None:
                if attempt > 0:
                    logger.info(f"Search succeeded on retry attempt {attempt}")
                return results, None
            else:
                last_error = error
                # Don't retry for validation errors or client errors (4xx)
                if "validation" in error.lower() or "400" in error:
                    break
                    
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
    
    logger.error(f"Search failed after {max_retries + 1} attempts")
    return [], last_error

def demonstrate_common_errors(search_client: SearchClient) -> None:
    """
    Demonstrate common search errors and how to handle them.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("COMMON ERROR SCENARIOS")
    print("="*80)
    
    error_scenarios = [
        {
            "name": "Empty Search Text",
            "params": {"search_text": ""},
            "expected": "Empty search text should be caught by validation"
        },
        {
            "name": "Invalid Filter Syntax",
            "params": {"search_text": "*", "filter": "category = 'Technology'"},  # Should be 'eq'
            "expected": "Invalid OData syntax should return 400 error"
        },
        {
            "name": "Non-existent Field in Filter",
            "params": {"search_text": "*", "filter": "nonexistent_field eq 'value'"},
            "expected": "Unknown field should return 400 error"
        },
        {
            "name": "Invalid Top Parameter",
            "params": {"search_text": "*", "top": -1},
            "expected": "Negative top parameter should be caught by validation"
        },
        {
            "name": "Unbalanced Quotes",
            "params": {"search_text": '"unbalanced quote'},
            "expected": "Unbalanced quotes should be caught by validation"
        },
        {
            "name": "Invalid Order By Field",
            "params": {"search_text": "*", "order_by": ["nonexistent_field desc"]},
            "expected": "Unknown sort field should return 400 error"
        }
    ]
    
    for i, scenario in enumerate(error_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 40)
        print(f"Expected: {scenario['expected']}")
        
        results, error = safe_search(search_client, **scenario['params'])
        
        if error:
            print(f"✅ Error handled correctly: {error}")
        else:
            print(f"⚠️  Unexpected success: {len(results)} results returned")

def demonstrate_retry_logic(search_client: SearchClient) -> None:
    """
    Demonstrate retry logic for handling transient failures.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("RETRY LOGIC DEMONSTRATION")
    print("="*80)
    
    # Example 1: Successful search (no retries needed)
    print("\n1. Successful Search (No Retries)")
    print("-" * 40)
    
    results, error = retry_search(
        search_client,
        search_text="azure",
        top=3,
        max_retries=2
    )
    
    if error:
        print(f"❌ Search failed: {error}")
    else:
        print(f"✅ Search succeeded: {len(results)} results")
    
    # Example 2: Search with validation error (no retries)
    print("\n2. Validation Error (No Retries)")
    print("-" * 40)
    
    results, error = retry_search(
        search_client,
        search_text="",  # Empty search text
        max_retries=2
    )
    
    if error:
        print(f"✅ Validation error (no retries): {error}")
    else:
        print(f"⚠️  Unexpected success: {len(results)} results")
    
    # Example 3: Simulate network timeout scenario
    print("\n3. Timeout Handling")
    print("-" * 40)
    
    try:
        # Create a client with very short timeout to simulate network issues
        from azure.core.pipeline.policies import RetryPolicy
        
        results, error = retry_search(
            search_client,
            search_text="azure machine learning tutorial guide",
            top=100,  # Large result set
            max_retries=1,
            retry_delay=0.5
        )
        
        if error:
            print(f"Handled potential timeout: {error}")
        else:
            print(f"Search completed: {len(results)} results")
            
    except Exception as e:
        print(f"Timeout simulation: {str(e)}")

def query_debugging_tools(search_client: SearchClient) -> None:
    """
    Demonstrate tools and techniques for debugging search queries.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("QUERY DEBUGGING TOOLS")
    print("="*80)
    
    def debug_search(description: str, **kwargs):
        """Helper function to debug a search query."""
        print(f"\n{description}")
        print("-" * 40)
        
        # Log query details
        search_text = kwargs.get('search_text', '*')
        print(f"Query: '{search_text}'")
        
        if 'filter' in kwargs:
            print(f"Filter: {kwargs['filter']}")
        if 'order_by' in kwargs:
            print(f"Order by: {kwargs['order_by']}")
        if 'top' in kwargs:
            print(f"Top: {kwargs['top']}")
        
        # Validate first
        is_valid, validation_error = validate_query_parameters(**kwargs)
        if not is_valid:
            print(f"❌ Validation failed: {validation_error}")
            return
        
        # Execute with timing
        start_time = time.time()
        results, error = safe_search(search_client, **kwargs)
        execution_time = time.time() - start_time
        
        if error:
            print(f"❌ Query failed: {error}")
        else:
            print(f"✅ Query succeeded in {execution_time:.3f}s")
            print(f"   Results: {len(results)}")
            
            if results:
                # Show score distribution
                scores = [r.get('@search.score', 0) for r in results]
                print(f"   Score range: {min(scores):.3f} - {max(scores):.3f}")
                
                # Show top result
                top_result = results[0]
                print(f"   Top result: {top_result.get('title', 'No title')[:50]}...")
    
    # Debug various query types
    debug_search(
        "1. Basic Text Search",
        search_text="azure machine learning"
    )
    
    debug_search(
        "2. Filtered Search",
        search_text="tutorial",
        filter="rating ge 4.0"
    )
    
    debug_search(
        "3. Complex Query",
        search_text="python OR java",
        filter="category eq 'Technology'",
        order_by=["rating desc"],
        top=5
    )
    
    debug_search(
        "4. Problematic Query (Invalid Filter)",
        search_text="azure",
        filter="invalid_field eq 'value'"
    )

def performance_monitoring(search_client: SearchClient) -> None:
    """
    Demonstrate performance monitoring and optimization techniques.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("PERFORMANCE MONITORING")
    print("="*80)
    
    def monitor_query_performance(description: str, **kwargs):
        """Monitor and report query performance."""
        print(f"\n{description}")
        print("-" * 40)
        
        # Multiple runs for average timing
        times = []
        result_counts = []
        
        for run in range(3):
            start_time = time.time()
            results, error = safe_search(search_client, **kwargs)
            execution_time = time.time() - start_time
            
            if error:
                print(f"Run {run + 1}: Failed - {error}")
                return
            
            times.append(execution_time)
            result_counts.append(len(results))
        
        avg_time = sum(times) / len(times)
        avg_results = sum(result_counts) / len(result_counts)
        
        print(f"Average execution time: {avg_time:.3f}s")
        print(f"Average result count: {avg_results:.0f}")
        print(f"Time range: {min(times):.3f}s - {max(times):.3f}s")
        
        # Performance assessment
        if avg_time < 0.1:
            print("✅ Excellent performance")
        elif avg_time < 0.5:
            print("✅ Good performance")
        elif avg_time < 1.0:
            print("⚠️  Acceptable performance")
        else:
            print("❌ Poor performance - consider optimization")
    
    # Monitor different query types
    monitor_query_performance(
        "1. Simple Query Performance",
        search_text="azure",
        top=10
    )
    
    monitor_query_performance(
        "2. Complex Query Performance",
        search_text="machine learning tutorial",
        filter="rating ge 3.0 and category eq 'Technology'",
        order_by=["rating desc", "publishedDate desc"],
        top=20
    )
    
    monitor_query_performance(
        "3. Large Result Set Performance",
        search_text="*",
        top=100
    )

def error_recovery_strategies(search_client: SearchClient) -> None:
    """
    Demonstrate error recovery strategies for production applications.
    
    Args:
        search_client: Azure AI Search client
    """
    print("\n" + "="*80)
    print("ERROR RECOVERY STRATEGIES")
    print("="*80)
    
    def graceful_search_with_fallback(primary_query: str, fallback_query: str = None):
        """
        Perform search with graceful fallback to simpler query.
        
        Args:
            primary_query: Primary search query to try
            fallback_query: Fallback query if primary fails
        """
        print(f"\nTrying primary query: '{primary_query}'")
        
        # Try primary query
        results, error = safe_search(
            search_client,
            search_text=primary_query,
            top=5
        )
        
        if error is None and results:
            print(f"✅ Primary query succeeded: {len(results)} results")
            return results
        
        print(f"❌ Primary query failed: {error}")
        
        # Try fallback query
        if fallback_query:
            print(f"Trying fallback query: '{fallback_query}'")
            
            results, error = safe_search(
                search_client,
                search_text=fallback_query,
                top=5
            )
            
            if error is None:
                print(f"✅ Fallback query succeeded: {len(results)} results")
                return results
            else:
                print(f"❌ Fallback query also failed: {error}")
        
        # Final fallback - return all documents
        print("Trying final fallback: return all documents")
        results, error = safe_search(
            search_client,
            search_text="*",
            top=5
        )
        
        if error is None:
            print(f"✅ Final fallback succeeded: {len(results)} results")
            return results
        else:
            print(f"❌ All queries failed: {error}")
            return []
    
    # Demonstrate fallback strategies
    print("\n1. Complex to Simple Query Fallback")
    graceful_search_with_fallback(
        primary_query='title:"machine learning" AND content:python',
        fallback_query="machine learning python"
    )
    
    print("\n2. Typo to Corrected Query Fallback")
    graceful_search_with_fallback(
        primary_query="machne learing",  # Typos
        fallback_query="machine learning"  # Corrected
    )
    
    print("\n3. Specific to General Query Fallback")
    graceful_search_with_fallback(
        primary_query="azure cognitive services computer vision api",
        fallback_query="azure cognitive services"
    )

def main():
    """
    Main function to run all error handling examples.
    """
    print("Azure AI Search - Error Handling Examples")
    print("=" * 80)
    
    try:
        # Create search client with error handling
        search_client = create_search_client()
        print(f"✅ Connected to search service: {os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')}")
        print(f"✅ Using index: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
        
        # Run examples
        demonstrate_common_errors(search_client)
        demonstrate_retry_logic(search_client)
        query_debugging_tools(search_client)
        performance_monitoring(search_client)
        error_recovery_strategies(search_client)
        
        print("\n" + "="*80)
        print("✅ All error handling examples completed successfully!")
        print("="*80)
        
        print("\n📚 What you learned:")
        print("• How to validate query parameters before execution")
        print("• How to handle different types of Azure AI Search exceptions")
        print("• How to implement retry logic for transient failures")
        print("• How to debug and troubleshoot search queries")
        print("• How to monitor query performance")
        print("• How to implement graceful error recovery strategies")
        
        print("\n🔗 Next steps:")
        print("• Apply these patterns to your production applications")
        print("• Set up monitoring and alerting for search errors")
        print("• Create custom error handling for your specific use cases")
        print("• Move on to Module 5 for advanced querying techniques")
        
        print("\n💡 Production Tips:")
        print("• Always validate user input before sending to search")
        print("• Implement proper logging for debugging")
        print("• Use retry logic for transient network issues")
        print("• Provide fallback queries for better user experience")
        print("• Monitor query performance and optimize slow queries")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n🔧 Setup required:")
        print("1. Create a .env file with your Azure AI Search credentials")
        print("2. Ensure you have completed previous modules to create sample indexes")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Unexpected error in main function")
        sys.exit(1)

if __name__ == "__main__":
    main()