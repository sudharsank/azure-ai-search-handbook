"""
Error Handling - Module 2 Python Examples
Basic error handling for Azure AI Search operations

This module demonstrates:
- Input validation
- Common error handling
- Safe search operations
- Error recovery strategies
- Best practices for error handling
"""

import os
import sys
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from azure.search.documents import SearchClient
from azure.core.exceptions import HttpResponseError

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class SearchValidator:
    """Simple validator for search queries"""
    
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a search query
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query:
            return False, "Search query cannot be empty"
        
        if not isinstance(query, str):
            return False, "Search query must be a string"
        
        if len(query.strip()) < 1:
            return False, "Search query cannot be just whitespace"
        
        if len(query) > 1000:
            return False, "Search query is too long (max 1000 characters)"
        
        return True, None
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Basic query sanitization
        
        Args:
            query: Raw search query
            
        Returns:
            Sanitized query string
        """
        if not query:
            return ""
        
        # Remove potentially problematic characters
        sanitized = re.sub(r'[<>]', '', query)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized.strip())
        
        return sanitized


class SafeSearchClient:
    """Safe wrapper around SearchClient with error handling"""
    
    def __init__(self, search_client: SearchClient = None):
        self.search_client = search_client or get_default_search_client()
        self.validator = SearchValidator()
        self.logger = logging.getLogger("safe_search_client")
    
    def safe_search(self, query: str, **kwargs) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Perform a safe search with error handling
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
            
        Returns:
            Tuple of (results_list, error_message)
        """
        # Validate query
        is_valid, validation_error = self.validator.validate_query(query)
        if not is_valid:
            return [], validation_error
        
        # Sanitize query
        sanitized_query = self.validator.sanitize_query(query)
        
        try:
            # Perform search
            results = self.search_client.search(search_text=sanitized_query, **kwargs)
            result_list = list(results)
            
            self.logger.info(f"Search successful: '{sanitized_query}' returned {len(result_list)} results")
            return result_list, None
            
        except HttpResponseError as e:
            error_msg = self._handle_http_error(e)
            self.logger.error(f"HTTP error in search: {error_msg}")
            return [], error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"Unexpected error in search: {error_msg}")
            return [], error_msg
    
    def _handle_http_error(self, error: HttpResponseError) -> str:
        """Handle HTTP errors with user-friendly messages"""
        status_code = error.status_code
        
        if status_code == 400:
            return "Invalid query syntax. Please check your search terms."
        elif status_code == 401:
            return "Authentication failed. Please check your API key."
        elif status_code == 403:
            return "Access denied. Please check your permissions."
        elif status_code == 404:
            return "Search index not found. Please verify your index name."
        elif status_code == 429:
            return "Too many requests. Please wait and try again."
        elif status_code == 503:
            return "Search service is temporarily unavailable. Please try again later."
        else:
            return f"HTTP error {status_code}: {error.message}"
    
    def search_with_fallback(self, query: str, fallback_queries: List[str] = None, **kwargs) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Search with fallback queries if primary search fails or returns no results
        
        Args:
            query: Primary search query
            fallback_queries: List of fallback queries to try
            **kwargs: Additional search parameters
            
        Returns:
            Tuple of (results_list, error_message)
        """
        # Try primary query first
        results, error = self.safe_search(query, **kwargs)
        
        if results or not fallback_queries:
            return results, error
        
        # Try fallback queries
        for fallback_query in fallback_queries:
            self.logger.info(f"Trying fallback query: '{fallback_query}'")
            fallback_results, fallback_error = self.safe_search(fallback_query, **kwargs)
            
            if fallback_results:
                self.logger.info(f"Fallback query successful: found {len(fallback_results)} results")
                return fallback_results, None
        
        # No results from any query
        return [], error or "No results found with any search strategy"


def demonstrate_error_handling():
    """Demonstrate error handling capabilities"""
    print("🛡️ Error Handling Demonstration")
    print("=" * 50)
    
    # Initialize safe search client
    safe_client = SafeSearchClient()
    
    # Test cases with different types of potential errors
    test_cases = [
        ("", "Empty query"),
        ("   ", "Whitespace only query"),
        ("python programming", "Valid query"),
        ("x" * 1001, "Too long query"),
        ("valid search terms", "Another valid query")
    ]
    
    print("\n🧪 Testing Query Validation and Error Handling:")
    print("-" * 55)
    
    for query, description in test_cases:
        print(f"\n📝 Test: {description}")
        display_query = query[:50] + "..." if len(query) > 50 else query
        print(f"Query: '{display_query}'")
        
        results, error = safe_client.safe_search(query, top=3)
        
        if error:
            print(f"❌ Error: {error}")
        else:
            print(f"✅ Success: Found {len(results)} results")
            if results:
                first_result = results[0]
                title = first_result.get('title', 'No title')
                score = first_result.get('@search.score', 0.0)
                print(f"   Top result: {title} (Score: {score:.3f})")
    
    # Demonstrate fallback search
    print(f"\n{'='*60}")
    print("\n🔄 Testing Fallback Search:")
    print("-" * 30)
    
    primary_query = "very_specific_nonexistent_term_12345"
    fallback_queries = [
        "python programming",
        "tutorial",
        "development"
    ]
    
    print(f"Primary query: '{primary_query}'")
    print(f"Fallback queries: {fallback_queries}")
    
    results, error = safe_client.search_with_fallback(
        primary_query, 
        fallback_queries, 
        top=2
    )
    
    if results:
        print(f"✅ Fallback successful: Found {len(results)} results")
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            score = result.get('@search.score', 0.0)
            print(f"  {i}. {title} (Score: {score:.3f})")
    else:
        print(f"❌ All queries failed: {error}")
    
    print("\n✅ Error handling demonstration completed!")


def error_handling_best_practices():
    """Demonstrate best practices for error handling"""
    print("\n📚 Error Handling Best Practices")
    print("=" * 50)
    
    print("\n💡 Always Validate Input:")
    print("   ✅ Check for empty or null queries")
    print("   ✅ Validate query length limits")
    print("   ✅ Sanitize user input")
    print("   ✅ Handle special characters appropriately")
    
    print("\n🔧 Handle Different Error Types:")
    print("   ✅ HTTP errors (400, 401, 403, 404, 429, 503)")
    print("   ✅ Network connectivity issues")
    print("   ✅ Service unavailability")
    print("   ✅ Invalid query syntax")
    
    print("\n🎯 Provide User-Friendly Messages:")
    print("   ✅ Translate technical errors to user language")
    print("   ✅ Suggest corrective actions")
    print("   ✅ Offer alternative search strategies")
    print("   ✅ Log detailed errors for debugging")
    
    print("\n🔄 Implement Fallback Strategies:")
    print("   ✅ Try broader search terms if specific ones fail")
    print("   ✅ Use alternative query syntax")
    print("   ✅ Provide suggested searches")
    print("   ✅ Gracefully degrade functionality")
    
    print("\n⚠️ Common Mistakes to Avoid:")
    print("   ❌ Exposing technical error messages to users")
    print("   ❌ Not logging errors for debugging")
    print("   ❌ Failing silently without user feedback")
    print("   ❌ Not implementing retry logic for transient errors")
    
    # Show example of good error handling
    print("\n🏆 Example of Good Error Handling:")
    safe_client = SafeSearchClient()
    
    # Simulate a problematic query
    problematic_query = ""  # Empty query
    
    results, error = safe_client.safe_search(problematic_query)
    
    if error:
        print(f"   User sees: '{error}'")
        print(f"   System logs: 'Empty query validation failed'")
        print(f"   Action: Prompt user to enter search terms")
    else:
        print(f"   Success: {len(results)} results found")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_error_handling()
    error_handling_best_practices()
    
    print("\n💡 Next Steps:")
    print("   - Always implement error handling in production code")
    print("   - Test your error handling with various input types")
    print("   - Check out 08_search_patterns.py for advanced search strategies")
    print("   - Review all Python examples to build complete search functionality")