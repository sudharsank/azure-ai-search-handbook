"""
Search Patterns - Module 2 Python Examples
Common search patterns and strategies in Azure AI Search

This module demonstrates:
- Progressive search strategies
- Search with fallback
- Multi-strategy search
- Search pattern best practices
- When to use different patterns
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class SearchPatterns:
    """Class demonstrating common search patterns"""
    
    def __init__(self, search_client: SearchClient = None):
        self.search_client = search_client or get_default_search_client()
        self.logger = logging.getLogger("search_patterns")
    
    def progressive_search(self, query: str, top: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Progressive search from specific to broad
        
        Args:
            query: Base search query
            top: Maximum results per strategy
            
        Returns:
            Dictionary mapping strategy names to results
        """
        strategies = {}
        
        # 1. Exact phrase (most specific)
        try:
            exact_results = self.search_client.search(
                search_text=f'"{query}"',
                top=top
            )
            strategies['exact_phrase'] = list(exact_results)
            self.logger.info(f"Exact phrase: {len(strategies['exact_phrase'])} results")
        except Exception as e:
            self.logger.error(f"Exact phrase search failed: {str(e)}")
            strategies['exact_phrase'] = []
        
        # 2. All terms (moderate specificity)
        try:
            all_terms_results = self.search_client.search(
                search_text=query,
                search_mode="all",
                top=top
            )
            strategies['all_terms'] = list(all_terms_results)
            self.logger.info(f"All terms: {len(strategies['all_terms'])} results")
        except Exception as e:
            self.logger.error(f"All terms search failed: {str(e)}")
            strategies['all_terms'] = []
        
        # 3. Any terms (broad)
        try:
            any_terms_results = self.search_client.search(
                search_text=query,
                search_mode="any",
                top=top
            )
            strategies['any_terms'] = list(any_terms_results)
            self.logger.info(f"Any terms: {len(strategies['any_terms'])} results")
        except Exception as e:
            self.logger.error(f"Any terms search failed: {str(e)}")
            strategies['any_terms'] = []
        
        # 4. Wildcard (broadest)
        try:
            terms = query.split()
            wildcard_query = " OR ".join([f"{term}*" for term in terms])
            wildcard_results = self.search_client.search(
                search_text=wildcard_query,
                top=top
            )
            strategies['wildcard'] = list(wildcard_results)
            self.logger.info(f"Wildcard: {len(strategies['wildcard'])} results")
        except Exception as e:
            self.logger.error(f"Wildcard search failed: {str(e)}")
            strategies['wildcard'] = []
        
        return strategies
    
    def search_with_fallback(self, query: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search with automatic fallback to broader strategies
        
        Args:
            query: Search query
            top: Maximum results to return
            
        Returns:
            List of search results from first successful strategy
        """
        # Try strategies in order of specificity
        strategies = [
            (f'"{query}"', "exact phrase"),
            (query, "all terms (default)"),
            (query, "any terms"),
            (" OR ".join([f"{term}*" for term in query.split()]), "wildcard")
        ]
        
        for search_query, strategy_name in strategies:
            try:
                if strategy_name == "any terms":
                    results = self.search_client.search(
                        search_text=search_query,
                        search_mode="any",
                        top=top
                    )
                else:
                    results = self.search_client.search(
                        search_text=search_query,
                        top=top
                    )
                
                result_list = list(results)
                
                if result_list:
                    self.logger.info(f"Found {len(result_list)} results using {strategy_name}")
                    return result_list
                else:
                    self.logger.info(f"No results with {strategy_name}, trying next strategy")
                    
            except Exception as e:
                self.logger.error(f"Error with {strategy_name}: {str(e)}")
                continue
        
        self.logger.warning("No results found with any search strategy")
        return []
    
    def multi_field_search(self, query: str, field_priority: List[str], top: int = 10) -> List[Dict[str, Any]]:
        """
        Search across fields in order of priority
        
        Args:
            query: Search query
            field_priority: List of fields in priority order
            top: Maximum results to return
            
        Returns:
            Combined results from all fields
        """
        all_results = []
        seen_ids = set()
        
        for field in field_priority:
            try:
                field_results = self.search_client.search(
                    search_text=query,
                    search_fields=[field],
                    top=top
                )
                
                for result in field_results:
                    result_dict = dict(result)
                    result_id = result_dict.get('id', str(hash(str(result_dict))))
                    
                    if result_id not in seen_ids:
                        seen_ids.add(result_id)
                        all_results.append(result_dict)
                
                self.logger.info(f"Field '{field}': found {len(list(field_results))} results")
                
            except Exception as e:
                self.logger.error(f"Error searching field '{field}': {str(e)}")
                continue
        
        # Sort by score
        all_results.sort(key=lambda x: x.get('@search.score', 0), reverse=True)
        return all_results[:top]
    
    def display_progressive_results(self, query: str, strategies: Dict[str, List[Dict[str, Any]]]):
        """Display results from progressive search"""
        print(f"\n🔄 Progressive Search Results: '{query}'")
        print("=" * 60)
        
        strategy_info = {
            'exact_phrase': ('Exact Phrase', 'Most specific - exact phrase match'),
            'all_terms': ('All Terms', 'Moderate - all terms must be present'),
            'any_terms': ('Any Terms', 'Broad - any terms can be present'),
            'wildcard': ('Wildcard', 'Broadest - partial term matching')
        }
        
        for strategy_name, results in strategies.items():
            if strategy_name in strategy_info:
                display_name, description = strategy_info[strategy_name]
                
                print(f"\n{display_name}:")
                print(f"   Description: {description}")
                print(f"   Results: {len(results)} found")
                
                if results:
                    print("   Top matches:")
                    for i, result in enumerate(results[:3], 1):
                        title = result.get('title', 'No title')
                        score = result.get('@search.score', 0.0)
                        print(f"     {i}. {title} (Score: {score:.3f})")
                else:
                    print("   No matches found")
                
                print("-" * 40)
        
        # Recommendation
        print(f"\n💡 RECOMMENDATION:")
        for strategy_name, results in strategies.items():
            if results:
                strategy_display = strategy_info.get(strategy_name, (strategy_name, ''))[0]
                print(f"   Use '{strategy_display}' - found {len(results)} relevant results")
                break
        else:
            print("   Try different search terms or check your data")


def demonstrate_search_patterns():
    """Demonstrate search patterns"""
    print("🎯 Search Patterns Demonstration")
    print("=" * 50)
    
    try:
        # Initialize search patterns
        patterns = SearchPatterns()
        
        # Example 1: Progressive search
        print("\n1️⃣ Progressive Search Strategy")
        
        query = "machine learning"
        progressive_results = patterns.progressive_search(query, top=5)
        patterns.display_progressive_results(query, progressive_results)
        
        # Example 2: Search with fallback
        print(f"\n{'='*70}")
        print("\n2️⃣ Search with Automatic Fallback")
        print("-" * 40)
        
        fallback_query = "artificial intelligence tutorial"
        fallback_results = patterns.search_with_fallback(fallback_query, top=5)
        
        print(f"Query: '{fallback_query}'")
        print(f"Results with fallback: {len(fallback_results)} found")
        
        if fallback_results:
            print("Top results:")
            for i, result in enumerate(fallback_results[:3], 1):
                title = result.get('title', 'No title')
                score = result.get('@search.score', 0.0)
                print(f"  {i}. {title} (Score: {score:.3f})")
        
        # Example 3: Multi-field search
        print(f"\n{'='*70}")
        print("\n3️⃣ Multi-Field Priority Search")
        print("-" * 40)
        
        field_priority = ['title', 'description', 'content', 'tags']
        multi_field_query = "python"
        
        multi_results = patterns.multi_field_search(multi_field_query, field_priority, top=5)
        
        print(f"Query: '{multi_field_query}'")
        print(f"Field priority: {' > '.join(field_priority)}")
        print(f"Combined results: {len(multi_results)} found")
        
        if multi_results:
            print("Top combined results:")
            for i, result in enumerate(multi_results[:3], 1):
                title = result.get('title', 'No title')
                score = result.get('@search.score', 0.0)
                print(f"  {i}. {title} (Score: {score:.3f})")
        
        print("\n✅ Search patterns demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")


def search_pattern_best_practices():
    """Best practices for search patterns"""
    print("\n📚 Search Pattern Best Practices")
    print("=" * 50)
    
    print("\n💡 When to Use Each Pattern:")
    
    print("\n🎯 Progressive Search:")
    print("   ✅ When you want comprehensive coverage")
    print("   ✅ For user-facing search interfaces")
    print("   ✅ When result quality is more important than speed")
    print("   ✅ For exploratory or research searches")
    
    print("\n🔄 Fallback Search:")
    print("   ✅ When you need guaranteed results")
    print("   ✅ For automated systems")
    print("   ✅ When speed is important")
    print("   ✅ For simple search interfaces")
    
    print("\n🏗️ Multi-Field Search:")
    print("   ✅ When different fields have different importance")
    print("   ✅ For structured data with clear field hierarchy")
    print("   ✅ When you want to avoid duplicates")
    print("   ✅ For content with rich metadata")
    
    print("\n⚠️ Pattern Selection Guidelines:")
    print("   🔍 Start simple, add complexity as needed")
    print("   📊 Monitor which patterns work best for your data")
    print("   ⚡ Consider performance implications")
    print("   👥 Think about user expectations")
    
    print("\n🔧 Implementation Tips:")
    print("   ✅ Cache results from expensive pattern searches")
    print("   ✅ Log which patterns are most successful")
    print("   ✅ Allow users to choose search modes")
    print("   ✅ Provide feedback about search strategy used")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_search_patterns()
    search_pattern_best_practices()
    
    print("\n💡 Next Steps:")
    print("   - Try different search patterns with your data")
    print("   - Experiment with combining patterns")
    print("   - Consider which patterns work best for your use case")
    print("   - Review all Python examples to build complete search functionality")
    print("   - Check out other language examples in ../csharp/, ../javascript/, etc.")