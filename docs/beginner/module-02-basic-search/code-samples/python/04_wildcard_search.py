"""
Wildcard Search - Module 2 Python Examples
Pattern matching with wildcards in Azure AI Search

This module demonstrates:
- Prefix matching with *
- Suffix matching with *
- Pattern matching strategies
- When to use wildcards
- Wildcard search limitations
"""

import os
import sys
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class WildcardSearch:
    """Class demonstrating wildcard search operations"""
    
    def __init__(self, search_client: SearchClient = None):
        """Initialize with a search client"""
        self.search_client = search_client or get_default_search_client()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for search operations"""
        logger = logging.getLogger("wildcard_search")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def prefix_search(self, prefix: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for terms starting with a prefix (prefix*)
        
        Args:
            prefix: The prefix to search for
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            query = f"{prefix}*"
            self.logger.info(f"Performing prefix search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results with prefix '{prefix}'")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in prefix search: {str(e)}")
            return []
    
    def suffix_search(self, suffix: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for terms ending with a suffix (*suffix)
        
        Args:
            suffix: The suffix to search for
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            query = f"*{suffix}"
            self.logger.info(f"Performing suffix search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results with suffix '{suffix}'")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in suffix search: {str(e)}")
            return []
    
    def contains_search(self, substring: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for terms containing a substring (*substring*)
        
        Args:
            substring: The substring to search for
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            query = f"*{substring}*"
            self.logger.info(f"Performing contains search: '{query}'")
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results containing '{substring}'")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in contains search: {str(e)}")
            return []
    
    def multiple_wildcard_search(self, patterns: List[str], top: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for multiple wildcard patterns
        
        Args:
            patterns: List of wildcard patterns to search for
            top: Maximum results per pattern
            
        Returns:
            Dictionary mapping patterns to their results
        """
        results = {}
        
        for pattern in patterns:
            try:
                self.logger.info(f"Searching for pattern: '{pattern}'")
                
                search_results = self.search_client.search(
                    search_text=pattern,
                    top=top,
                    include_total_count=True
                )
                
                result_list = []
                for result in search_results:
                    result_list.append(dict(result))
                
                results[pattern] = result_list
                
            except Exception as e:
                self.logger.error(f"Error searching pattern '{pattern}': {str(e)}")
                results[pattern] = []
        
        return results
    
    def compare_wildcard_patterns(self, base_term: str, top: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare different wildcard patterns for the same base term
        
        Args:
            base_term: Base term to create patterns from
            top: Maximum results per pattern
            
        Returns:
            Dictionary mapping pattern types to their results
        """
        patterns = {
            'exact': base_term,
            'prefix': f"{base_term}*",
            'suffix': f"*{base_term}",
            'contains': f"*{base_term}*"
        }
        
        results = {}
        
        for pattern_type, pattern in patterns.items():
            try:
                search_results = self.search_client.search(
                    search_text=pattern,
                    top=top,
                    include_total_count=True
                )
                
                result_list = []
                for result in search_results:
                    result_list.append(dict(result))
                
                results[pattern_type] = result_list
                
            except Exception as e:
                self.logger.error(f"Error in {pattern_type} search: {str(e)}")
                results[pattern_type] = []
        
        return results
    
    def display_wildcard_comparison(self, base_term: str, results: Dict[str, List[Dict[str, Any]]]):
        """
        Display comparison of wildcard patterns
        
        Args:
            base_term: Base term used for patterns
            results: Results from different wildcard patterns
        """
        print(f"\n🃏 Wildcard Patterns Comparison: '{base_term}'")
        print("=" * 60)
        
        pattern_info = {
            'exact': ('Exact Match', base_term, 'Exact term only'),
            'prefix': ('Prefix Match', f"{base_term}*", f'Terms starting with "{base_term}"'),
            'suffix': ('Suffix Match', f"*{base_term}", f'Terms ending with "{base_term}"'),
            'contains': ('Contains Match', f"*{base_term}*", f'Terms containing "{base_term}"')
        }
        
        for pattern_type, pattern_results in results.items():
            if pattern_type in pattern_info:
                name, pattern, description = pattern_info[pattern_type]
                
                print(f"\n{name}:")
                print(f"   Pattern: {pattern}")
                print(f"   Description: {description}")
                print(f"   Results found: {len(pattern_results)}")
                
                if pattern_results:
                    print("   Top matches:")
                    for i, result in enumerate(pattern_results[:3], 1):
                        title = result.get('title', 'No title')
                        score = result.get('@search.score', 0.0)
                        print(f"     {i}. {title} (Score: {score:.3f})")
                else:
                    print("   No matches found")
                
                print("-" * 40)
        
        # Analysis
        print(f"\n📊 PATTERN ANALYSIS:")
        exact_count = len(results.get('exact', []))
        prefix_count = len(results.get('prefix', []))
        suffix_count = len(results.get('suffix', []))
        contains_count = len(results.get('contains', []))
        
        print(f"   Exact: {exact_count} (most specific)")
        print(f"   Prefix: {prefix_count}")
        print(f"   Suffix: {suffix_count}")
        print(f"   Contains: {contains_count} (broadest)")
        
        if contains_count >= max(prefix_count, suffix_count) >= exact_count:
            print("   ✅ Expected pattern: Contains ≥ Prefix/Suffix ≥ Exact")
        else:
            print("   ⚠️ Unexpected pattern - depends on your data")


def demonstrate_wildcard_search():
    """Demonstrate wildcard search operations"""
    print("🃏 Wildcard Search Demonstration")
    print("=" * 50)
    
    try:
        # Initialize search operations
        search_ops = WildcardSearch()
        
        # Example 1: Compare wildcard patterns
        print("\n1️⃣ Wildcard Patterns Comparison")
        
        base_term = "program"
        wildcard_results = search_ops.compare_wildcard_patterns(base_term, top=5)
        search_ops.display_wildcard_comparison(base_term, wildcard_results)
        
        # Example 2: Practical wildcard searches
        print(f"\n{'='*70}")
        print("\n2️⃣ Practical Wildcard Examples")
        print("-" * 30)
        
        practical_examples = [
            ("Find programming languages", "program*", "prefix"),
            ("Find development terms", "*develop*", "contains"),
            ("Find tutorial content", "*tutorial", "suffix"),
            ("Find JavaScript variations", "java*", "prefix")
        ]
        
        for description, pattern, pattern_type in practical_examples:
            print(f"\n📋 {description}")
            print(f"   Pattern: {pattern} ({pattern_type})")
            
            if pattern_type == "prefix":
                results = search_ops.prefix_search(pattern[:-1], top=3)
            elif pattern_type == "suffix":
                results = search_ops.suffix_search(pattern[1:], top=3)
            elif pattern_type == "contains":
                results = search_ops.contains_search(pattern[1:-1], top=3)
            else:
                results = []
            
            print(f"   Results: {len(results)} found")
            
            if results:
                top_result = results[0]
                title = top_result.get('title', 'No title')
                score = top_result.get('@search.score', 0.0)
                print(f"   Top match: {title} (Score: {score:.3f})")
        
        # Example 3: Multiple wildcard search
        print(f"\n{'='*70}")
        print("\n3️⃣ Multiple Wildcard Search")
        print("-" * 30)
        
        wildcard_patterns = [
            "web*",      # web, website, webdev, etc.
            "*script",   # javascript, typescript, etc.
            "*data*",    # database, metadata, etc.
            "api*"       # api, apis, etc.
        ]
        
        multi_results = search_ops.multiple_wildcard_search(wildcard_patterns, top=2)
        
        for pattern, results in multi_results.items():
            print(f"\nPattern: {pattern}")
            print(f"Results: {len(results)}")
            if results:
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'No title')
                    score = result.get('@search.score', 0.0)
                    print(f"  {i}. {title} (Score: {score:.3f})")
        
        print("\n✅ Wildcard search demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Make sure your Azure AI Search service is configured correctly.")


def wildcard_search_best_practices():
    """Demonstrate best practices for wildcard search"""
    print("\n📚 Wildcard Search Best Practices")
    print("=" * 50)
    
    print("\n💡 When to Use Wildcards:")
    print("\n✅ Prefix Search (term*):")
    print("   - Finding word variations (program, programming, programmer)")
    print("   - Technology families (java, javascript, javadoc)")
    print("   - Brand or product lines (micro, microsoft, microservice)")
    print("   - Language variations (develop, developer, development)")
    
    print("\n✅ Suffix Search (*term):")
    print("   - Finding words with common endings (*ing, *tion, *ment)")
    print("   - File types or extensions (*script, *doc)")
    print("   - Categories or types (*tutorial, *guide)")
    
    print("\n✅ Contains Search (*term*):")
    print("   - Finding partial matches when unsure of exact form")
    print("   - Searching within compound words")
    print("   - When you know a key part but not the whole term")
    
    print("\n⚠️ Wildcard Limitations:")
    print("   ❌ Can be slower than exact searches")
    print("   ❌ May return too many irrelevant results")
    print("   ❌ Leading wildcards (*term) are generally slower")
    print("   ❌ Multiple wildcards in one term can be very slow")
    
    print("\n🔧 Performance Tips:")
    print("   ✅ Use specific prefixes (at least 2-3 characters)")
    print("   ✅ Combine with other terms to narrow results")
    print("   ✅ Prefer prefix wildcards over suffix wildcards")
    print("   ✅ Test wildcard queries with small result sets first")
    
    # Demonstrate good vs bad practices
    print("\n🧪 Good vs Bad Wildcard Examples:")
    search_ops = WildcardSearch()
    
    print("\n✅ Good Wildcard Practices:")
    good_examples = [
        ("program*", "Specific prefix, likely to find relevant terms"),
        ("java* AND tutorial", "Wildcard combined with specific term"),
        ("*development", "Common suffix, reasonable scope")
    ]
    
    for pattern, explanation in good_examples:
        print(f"   {pattern}: {explanation}")
    
    print("\n❌ Problematic Wildcard Practices:")
    bad_examples = [
        ("*a*", "Too broad, will match almost everything"),
        ("*", "Matches all documents, not useful for search"),
        ("*e*t*", "Multiple wildcards, very slow")
    ]
    
    for pattern, explanation in bad_examples:
        print(f"   {pattern}: {explanation}")
    
    # Show optimization example
    print("\n🚀 Optimization Example:")
    print("   Instead of: '*script'")
    print("   Try: 'javascript OR typescript OR script'")
    print("   Benefit: More specific, faster, better relevance")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_wildcard_search()
    wildcard_search_best_practices()
    
    print("\n💡 Next Steps:")
    print("   - Experiment with different wildcard patterns")
    print("   - Try combining wildcards with boolean operators")
    print("   - Check out 05_field_search.py for field-specific searches")
    print("   - Learn about search parameters in 06_search_parameters.py")