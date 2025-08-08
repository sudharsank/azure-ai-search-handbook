"""
Field-Specific Search - Module 2 Python Examples
Searching within specific fields in Azure AI Search

This module demonstrates:
- Searching specific fields
- Field selection for results
- Multi-field searches
- Field weighting concepts
- When to use field-specific search
"""

import os
import sys
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class FieldSearch:
    """Class demonstrating field-specific search operations"""
    
    def __init__(self, search_client: SearchClient = None):
        """Initialize with a search client"""
        self.search_client = search_client or get_default_search_client()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for search operations"""
        logger = logging.getLogger("field_search")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger    

    def search_specific_field(self, query: str, field: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search within a specific field only
        
        Args:
            query: Search query string
            field: Field name to search in
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            self.logger.info(f"Searching field '{field}' for: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                search_fields=[field],
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results in field '{field}'")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error searching field '{field}': {str(e)}")
            return []
    
    def search_multiple_fields(self, query: str, fields: List[str], top: int = 10) -> List[Dict[str, Any]]:
        """
        Search within multiple specific fields
        
        Args:
            query: Search query string
            fields: List of field names to search in
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            self.logger.info(f"Searching fields {fields} for: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                search_fields=fields,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results in fields {fields}")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error searching fields {fields}: {str(e)}")
            return []
    
    def search_with_selected_fields(self, query: str, select_fields: List[str], 
                                   search_fields: List[str] = None, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search and return only selected fields
        
        Args:
            query: Search query string
            select_fields: List of field names to return in results
            search_fields: List of field names to search in (optional)
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries with only selected fields
        """
        try:
            self.logger.info(f"Searching for '{query}' with selected fields: {select_fields}")
            
            search_params = {
                'search_text': query,
                'select': select_fields,
                'top': top,
                'include_total_count': True
            }
            
            if search_fields:
                search_params['search_fields'] = search_fields
            
            results = self.search_client.search(**search_params)
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results with selected fields")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in search with selected fields: {str(e)}")
            return []
    
    def compare_field_searches(self, query: str, fields: List[str], top: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare search results across different fields
        
        Args:
            query: Search query string
            fields: List of fields to compare
            top: Maximum results per field
            
        Returns:
            Dictionary mapping field names to their results
        """
        results = {}
        
        # Search all fields (default)
        try:
            all_results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            results['all_fields'] = [dict(result) for result in all_results]
        except Exception as e:
            self.logger.error(f"Error in all fields search: {str(e)}")
            results['all_fields'] = []
        
        # Search individual fields
        for field in fields:
            results[field] = self.search_specific_field(query, field, top)
        
        return results    
  
    def display_field_comparison(self, query: str, results: Dict[str, List[Dict[str, Any]]]):
        """
        Display comparison of field-specific searches
        
        Args:
            query: Original search query
            results: Results from different field searches
        """
        print(f"\n🎯 Field-Specific Search Comparison: '{query}'")
        print("=" * 70)
        
        for field_name, field_results in results.items():
            print(f"\n{field_name.replace('_', ' ').title()}:")
            print(f"   Results found: {len(field_results)}")
            
            if field_results:
                print("   Top matches:")
                for i, result in enumerate(field_results[:3], 1):
                    title = result.get('title', 'No title')
                    score = result.get('@search.score', 0.0)
                    print(f"     {i}. {title} (Score: {score:.3f})")
                
                # Show average score
                avg_score = sum(r.get('@search.score', 0) for r in field_results) / len(field_results)
                print(f"   Average score: {avg_score:.3f}")
            else:
                print("   No matches found")
            
            print("-" * 50)
        
        # Analysis
        print(f"\n📊 FIELD ANALYSIS:")
        for field_name, field_results in results.items():
            count = len(field_results)
            if count > 0:
                max_score = max(r.get('@search.score', 0) for r in field_results)
                print(f"   {field_name}: {count} results (max score: {max_score:.3f})")
            else:
                print(f"   {field_name}: No results")


def demonstrate_field_search():
    """Demonstrate field-specific search operations"""
    print("🎯 Field-Specific Search Demonstration")
    print("=" * 50)
    
    try:
        # Initialize search operations
        search_ops = FieldSearch()
        
        # Example 1: Compare field searches
        print("\n1️⃣ Field Search Comparison")
        
        query = "python"
        common_fields = ['title', 'content', 'description', 'author']
        
        field_results = search_ops.compare_field_searches(query, common_fields, top=5)
        search_ops.display_field_comparison(query, field_results)
        
        # Example 2: Multi-field search
        print(f"\n{'='*70}")
        print("\n2️⃣ Multi-Field Search Examples")
        print("-" * 30)
        
        multi_field_examples = [
            ("Find tutorials by title or description", ["title", "description"]),
            ("Search content and tags", ["content", "tags"]),
            ("Author and title search", ["author", "title"])
        ]
        
        for description, fields in multi_field_examples:
            print(f"\n📋 {description}")
            print(f"   Fields: {', '.join(fields)}")
            
            results = search_ops.search_multiple_fields("tutorial", fields, top=3)
            print(f"   Results: {len(results)} found")
            
            if results:
                top_result = results[0]
                title = top_result.get('title', 'No title')
                score = top_result.get('@search.score', 0.0)
                print(f"   Top match: {title} (Score: {score:.3f})")
        
        # Example 3: Field selection
        print(f"\n{'='*70}")
        print("\n3️⃣ Field Selection Examples")
        print("-" * 30)
        
        selection_examples = [
            ("Basic info only", ["id", "title", "author"]),
            ("Content preview", ["title", "description", "url"]),
            ("Metadata only", ["id", "publishedDate", "category"])
        ]
        
        for description, select_fields in selection_examples:
            print(f"\n📋 {description}")
            print(f"   Selected fields: {', '.join(select_fields)}")
            
            results = search_ops.search_with_selected_fields(
                "programming", 
                select_fields, 
                top=2
            )
            
            print(f"   Results: {len(results)} found")
            
            if results:
                first_result = results[0]
                available_fields = [key for key in first_result.keys() if not key.startswith('@')]
                print(f"   Available fields in result: {', '.join(available_fields)}")
        
        print("\n✅ Field-specific search demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Make sure your Azure AI Search service is configured correctly.")


def field_search_best_practices():
    """Demonstrate best practices for field-specific search"""
    print("\n📚 Field-Specific Search Best Practices")
    print("=" * 50)
    
    print("\n💡 When to Use Field-Specific Search:")
    print("\n✅ Search Specific Fields When:")
    print("   - You know exactly which field contains relevant information")
    print("   - You want to search titles only (more precise)")
    print("   - You need to search metadata fields (author, category, etc.)")
    print("   - You want to exclude certain fields from search")
    
    print("\n✅ Select Specific Fields When:")
    print("   - You only need certain fields in results (faster)")
    print("   - You want to reduce network traffic")
    print("   - You're building a summary or preview")
    print("   - You need consistent result structure")
    
    print("\n⚠️ Field Search Considerations:")
    print("   ❌ Field names must exist in your index")
    print("   ❌ Searching fewer fields may miss relevant content")
    print("   ❌ Field-specific search can be less flexible")
    print("   ❌ Some fields might not be searchable")
    
    print("\n🔧 Performance Tips:")
    print("   ✅ Use field selection to reduce result size")
    print("   ✅ Search high-value fields first (title, description)")
    print("   ✅ Combine field search with other filters")
    print("   ✅ Test which fields give best results for your use case")
    
    # Demonstrate field strategy
    print("\n🎯 Field Search Strategy Example:")
    search_ops = FieldSearch()
    
    query = "javascript tutorial"
    
    print(f"\nQuery: '{query}'")
    print("Strategy: Search from most specific to most general")
    
    # 1. Title only (most specific)
    title_results = search_ops.search_specific_field(query, "title", top=1)
    print(f"\n1. Title only: {len(title_results)} results")
    
    # 2. Title + description (moderate)
    title_desc_results = search_ops.search_multiple_fields(query, ["title", "description"], top=1)
    print(f"2. Title + Description: {len(title_desc_results)} results")
    
    # 3. All fields (broadest)
    all_results = search_ops.search_client.search(search_text=query, top=1)
    all_count = len(list(all_results))
    print(f"3. All fields: {all_count} results")
    
    print(f"\n💡 Recommendation: Start specific, broaden if needed")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_field_search()
    field_search_best_practices()
    
    print("\n💡 Next Steps:")
    print("   - Try searching different fields in your index")
    print("   - Experiment with field combinations")
    print("   - Check out 06_search_parameters.py for more search options")
    print("   - Learn about result processing in 07_result_processing.py")