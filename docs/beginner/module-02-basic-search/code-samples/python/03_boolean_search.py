"""
Boolean Search - Module 2 Python Examples
Boolean operators (AND, OR, NOT) in Azure AI Search

This module demonstrates:
- AND operator for required terms
- OR operator for alternative terms
- NOT operator for exclusions
- Combining boolean operators
- Boolean search best practices
"""

import os
import sys
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class BooleanSearch:
    """Class demonstrating boolean search operations"""
    
    def __init__(self, search_client: SearchClient = None):
        """Initialize with a search client"""
        self.search_client = search_client or get_default_search_client()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for search operations"""
        logger = logging.getLogger("boolean_search")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def and_search(self, term1: str, term2: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents containing both terms (AND operator)
        
        Args:
            term1: First required term
            term2: Second required term
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            query = f"{term1} AND {term2}"
            self.logger.info(f"Performing AND search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results with both terms")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in AND search: {str(e)}")
            return []
    
    def or_search(self, term1: str, term2: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents containing either term (OR operator)
        
        Args:
            term1: First alternative term
            term2: Second alternative term
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            query = f"{term1} OR {term2}"
            self.logger.info(f"Performing OR search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results with either term")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in OR search: {str(e)}")
            return []
    
    def not_search(self, include_term: str, exclude_term: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents containing one term but not another (NOT operator)
        
        Args:
            include_term: Term that must be present
            exclude_term: Term that must not be present
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            query = f"{include_term} NOT {exclude_term}"
            self.logger.info(f"Performing NOT search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results excluding '{exclude_term}'")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in NOT search: {str(e)}")
            return []
    
    def complex_boolean_search(self, query: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Perform complex boolean search with multiple operators
        
        Args:
            query: Complex boolean query string
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            self.logger.info(f"Performing complex boolean search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results for complex query")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in complex boolean search: {str(e)}")
            return []
    
    def compare_boolean_operators(self, term1: str, term2: str, top: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare results from different boolean operators
        
        Args:
            term1: First term
            term2: Second term
            top: Maximum results per operator
            
        Returns:
            Dictionary mapping operators to their results
        """
        results = {}
        
        # AND search
        results['AND'] = self.and_search(term1, term2, top)
        
        # OR search
        results['OR'] = self.or_search(term1, term2, top)
        
        # NOT search (term1 but not term2)
        results['NOT'] = self.not_search(term1, term2, top)
        
        return results
    
    def display_boolean_comparison(self, term1: str, term2: str, results: Dict[str, List[Dict[str, Any]]]):
        """
        Display comparison of boolean operators
        
        Args:
            term1: First term
            term2: Second term
            results: Results from different boolean operators
        """
        print(f"\n🔗 Boolean Operators Comparison: '{term1}' and '{term2}'")
        print("=" * 70)
        
        for operator, operator_results in results.items():
            print(f"\n{operator} Operation:")
            
            if operator == 'AND':
                print(f"   Query: {term1} AND {term2}")
                print(f"   Meaning: Documents must contain BOTH terms")
            elif operator == 'OR':
                print(f"   Query: {term1} OR {term2}")
                print(f"   Meaning: Documents can contain EITHER term")
            elif operator == 'NOT':
                print(f"   Query: {term1} NOT {term2}")
                print(f"   Meaning: Documents must contain '{term1}' but NOT '{term2}'")
            
            print(f"   Results found: {len(operator_results)}")
            
            if operator_results:
                print("   Top matches:")
                for i, result in enumerate(operator_results[:3], 1):
                    title = result.get('title', 'No title')
                    score = result.get('@search.score', 0.0)
                    print(f"     {i}. {title} (Score: {score:.3f})")
            else:
                print("   No matches found")
            
            print("-" * 50)
        
        # Analysis
        print(f"\n📊 ANALYSIS:")
        and_count = len(results.get('AND', []))
        or_count = len(results.get('OR', []))
        not_count = len(results.get('NOT', []))
        
        print(f"   AND results: {and_count} (most specific)")
        print(f"   OR results: {or_count} (broadest)")
        print(f"   NOT results: {not_count} (filtered)")
        
        if or_count >= and_count >= not_count:
            print("   ✅ Expected pattern: OR ≥ AND ≥ NOT")
        else:
            print("   ⚠️ Unexpected pattern - check your data or terms")


def demonstrate_boolean_search():
    """Demonstrate boolean search operations"""
    print("🔗 Boolean Search Demonstration")
    print("=" * 50)
    
    try:
        # Initialize search operations
        search_ops = BooleanSearch()
        
        # Example 1: Compare boolean operators
        print("\n1️⃣ Boolean Operators Comparison")
        
        term1, term2 = "python", "tutorial"
        boolean_results = search_ops.compare_boolean_operators(term1, term2, top=5)
        search_ops.display_boolean_comparison(term1, term2, boolean_results)
        
        # Example 2: Complex boolean queries
        print(f"\n{'='*70}")
        print("\n2️⃣ Complex Boolean Queries")
        print("-" * 30)
        
        complex_queries = [
            "python AND (tutorial OR guide)",
            "(web OR mobile) AND development",
            "programming NOT (beginner OR basic)",
            "machine AND learning AND (python OR r)"
        ]
        
        for query in complex_queries:
            print(f"\nQuery: {query}")
            results = search_ops.complex_boolean_search(query, top=3)
            print(f"Results: {len(results)}")
            
            if results:
                top_result = results[0]
                title = top_result.get('title', 'No title')
                score = top_result.get('@search.score', 0.0)
                print(f"Top match: {title} (Score: {score:.3f})")
        
        # Example 3: Practical use cases
        print(f"\n{'='*70}")
        print("\n3️⃣ Practical Use Cases")
        print("-" * 30)
        
        use_cases = [
            {
                "scenario": "Find beginner Python tutorials",
                "query": "python AND tutorial AND beginner",
                "explanation": "All three terms must be present"
            },
            {
                "scenario": "Find content about web or mobile development",
                "query": "development AND (web OR mobile)",
                "explanation": "Must have 'development' plus either 'web' or 'mobile'"
            },
            {
                "scenario": "Find programming content but exclude advanced topics",
                "query": "programming NOT (advanced OR expert)",
                "explanation": "Must have 'programming' but exclude advanced content"
            }
        ]
        
        for case in use_cases:
            print(f"\n📋 Scenario: {case['scenario']}")
            print(f"   Query: {case['query']}")
            print(f"   Logic: {case['explanation']}")
            
            results = search_ops.complex_boolean_search(case['query'], top=2)
            print(f"   Results: {len(results)} found")
        
        print("\n✅ Boolean search demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Make sure your Azure AI Search service is configured correctly.")


def boolean_search_best_practices():
    """Demonstrate best practices for boolean search"""
    print("\n📚 Boolean Search Best Practices")
    print("=" * 50)
    
    print("\n💡 When to Use Each Operator:")
    print("\n✅ AND Operator:")
    print("   - When you need ALL terms to be present")
    print("   - For specific, focused searches")
    print("   - To narrow down broad topics")
    print("   - Example: 'machine AND learning AND python'")
    
    print("\n✅ OR Operator:")
    print("   - When you want ANY of the terms")
    print("   - For broader, more inclusive searches")
    print("   - When searching for synonyms or alternatives")
    print("   - Example: 'javascript OR typescript OR js'")
    
    print("\n✅ NOT Operator:")
    print("   - To exclude unwanted content")
    print("   - To filter out irrelevant results")
    print("   - When you know what you don't want")
    print("   - Example: 'programming NOT (game OR gaming)'")
    
    print("\n⚠️ Common Mistakes to Avoid:")
    print("   ❌ Using AND when you mean OR")
    print("   ❌ Overusing NOT (can exclude relevant content)")
    print("   ❌ Forgetting parentheses in complex queries")
    print("   ❌ Making queries too restrictive with multiple ANDs")
    
    print("\n🔧 Query Building Tips:")
    print("   ✅ Start simple, then add complexity")
    print("   ✅ Use parentheses to group terms: (term1 OR term2) AND term3")
    print("   ✅ Test each part of complex queries separately")
    print("   ✅ Consider search mode ('any' vs 'all') as alternative to boolean")
    
    # Demonstrate query building
    print("\n🏗️ Query Building Example:")
    search_ops = BooleanSearch()
    
    base_term = "tutorial"
    print(f"\n1. Start with base term: '{base_term}'")
    base_results = search_ops.complex_boolean_search(base_term, top=1)
    print(f"   Results: {len(base_results)}")
    
    refined_query = "tutorial AND python"
    print(f"\n2. Add specificity: '{refined_query}'")
    refined_results = search_ops.complex_boolean_search(refined_query, top=1)
    print(f"   Results: {len(refined_results)} (more specific)")
    
    final_query = "tutorial AND python AND (beginner OR introduction)"
    print(f"\n3. Add alternatives: '{final_query}'")
    final_results = search_ops.complex_boolean_search(final_query, top=1)
    print(f"   Results: {len(final_results)} (balanced specificity)")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_boolean_search()
    boolean_search_best_practices()
    
    print("\n💡 Next Steps:")
    print("   - Practice building your own boolean queries")
    print("   - Try combining different operators")
    print("   - Check out 04_wildcard_search.py for pattern matching")
    print("   - Learn about field-specific searches in 05_field_search.py")