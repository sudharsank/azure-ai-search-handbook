"""
Phrase Search - Module 2 Python Examples
Exact phrase matching in Azure AI Search

This module demonstrates:
- Exact phrase search with quotes
- Comparing phrase vs individual terms
- Understanding when to use phrase search
- Phrase search best practices
"""

import os
import sys
import logging
from typing import List, Dict, Any, Tuple
from azure.search.documents import SearchClient

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class PhraseSearch:
    """Class demonstrating phrase search operations"""
    
    def __init__(self, search_client: SearchClient = None):
        """Initialize with a search client"""
        self.search_client = search_client or get_default_search_client()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for search operations"""
        logger = logging.getLogger("phrase_search")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def exact_phrase_search(self, phrase: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for an exact phrase using quotes
        
        Args:
            phrase: Exact phrase to search for
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            # Wrap phrase in quotes for exact matching
            quoted_phrase = f'"{phrase}"'
            self.logger.info(f"Performing exact phrase search: {quoted_phrase}")
            
            results = self.search_client.search(
                search_text=quoted_phrase,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} exact phrase matches")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in phrase search: {str(e)}")
            return []
    
    def individual_terms_search(self, phrase: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Search for individual terms (without quotes)
        
        Args:
            phrase: Terms to search for individually
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            self.logger.info(f"Performing individual terms search: '{phrase}'")
            
            results = self.search_client.search(
                search_text=phrase,
                top=top,
                include_total_count=True
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results for individual terms")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in individual terms search: {str(e)}")
            return []
    
    def compare_phrase_vs_terms(self, phrase: str, top: int = 5) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Compare exact phrase search vs individual terms search
        
        Args:
            phrase: Phrase to compare
            top: Maximum number of results for each search
            
        Returns:
            Tuple of (phrase_results, terms_results)
        """
        phrase_results = self.exact_phrase_search(phrase, top)
        terms_results = self.individual_terms_search(phrase, top)
        
        return phrase_results, terms_results
    
    def display_comparison(self, phrase: str, phrase_results: List[Dict[str, Any]], 
                          terms_results: List[Dict[str, Any]]):
        """
        Display comparison between phrase and terms search
        
        Args:
            phrase: Original phrase searched
            phrase_results: Results from exact phrase search
            terms_results: Results from individual terms search
        """
        print(f"\n🔤 Phrase vs Terms Comparison: '{phrase}'")
        print("=" * 60)
        
        # Exact phrase results
        print(f"\n1️⃣ EXACT PHRASE SEARCH: \"{phrase}\"")
        print("-" * 40)
        print(f"Results found: {len(phrase_results)}")
        
        if phrase_results:
            print("Top matches:")
            for i, result in enumerate(phrase_results[:3], 1):
                title = result.get('title', 'No title')
                score = result.get('@search.score', 0.0)
                print(f"  {i}. {title} (Score: {score:.3f})")
        else:
            print("  No exact phrase matches found")
        
        # Individual terms results
        print(f"\n2️⃣ INDIVIDUAL TERMS SEARCH: {phrase}")
        print("-" * 40)
        print(f"Results found: {len(terms_results)}")
        
        if terms_results:
            print("Top matches:")
            for i, result in enumerate(terms_results[:3], 1):
                title = result.get('title', 'No title')
                score = result.get('@search.score', 0.0)
                print(f"  {i}. {title} (Score: {score:.3f})")
        else:
            print("  No results found for individual terms")
        
        # Analysis
        print(f"\n📊 COMPARISON ANALYSIS:")
        print(f"   Exact phrase: {len(phrase_results)} results")
        print(f"   Individual terms: {len(terms_results)} results")
        
        if phrase_results and terms_results:
            phrase_avg = sum(r.get('@search.score', 0) for r in phrase_results) / len(phrase_results)
            terms_avg = sum(r.get('@search.score', 0) for r in terms_results) / len(terms_results)
            print(f"   Average phrase score: {phrase_avg:.3f}")
            print(f"   Average terms score: {terms_avg:.3f}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if len(phrase_results) > 0:
            print("   ✅ Exact phrase found - use phrase search for precision")
        elif len(terms_results) > 0:
            print("   ⚠️ No exact phrase - individual terms provide broader results")
        else:
            print("   ❌ No results found - try different keywords or broader terms")
    
    def multi_phrase_search(self, phrases: List[str], top: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for multiple phrases
        
        Args:
            phrases: List of phrases to search for
            top: Maximum results per phrase
            
        Returns:
            Dictionary mapping phrases to their results
        """
        results = {}
        
        for phrase in phrases:
            self.logger.info(f"Searching for phrase: '{phrase}'")
            phrase_results = self.exact_phrase_search(phrase, top)
            results[phrase] = phrase_results
        
        return results


def demonstrate_phrase_search():
    """Demonstrate phrase search operations"""
    print("🔤 Phrase Search Demonstration")
    print("=" * 50)
    
    try:
        # Initialize search operations
        search_ops = PhraseSearch()
        
        # Example 1: Compare phrase vs terms
        print("\n1️⃣ Phrase vs Terms Comparison")
        
        test_phrase = "machine learning"
        phrase_results, terms_results = search_ops.compare_phrase_vs_terms(test_phrase, top=5)
        search_ops.display_comparison(test_phrase, phrase_results, terms_results)
        
        # Example 2: Another comparison
        print(f"\n{'='*70}")
        print("\n2️⃣ Another Comparison Example")
        
        test_phrase2 = "web development"
        phrase_results2, terms_results2 = search_ops.compare_phrase_vs_terms(test_phrase2, top=5)
        search_ops.display_comparison(test_phrase2, phrase_results2, terms_results2)
        
        # Example 3: Multiple phrase search
        print(f"\n{'='*70}")
        print("\n3️⃣ Multiple Phrase Search")
        print("-" * 30)
        
        phrases_to_search = [
            "artificial intelligence",
            "data science",
            "software engineering"
        ]
        
        multi_results = search_ops.multi_phrase_search(phrases_to_search, top=2)
        
        for phrase, results in multi_results.items():
            print(f"\nPhrase: \"{phrase}\"")
            print(f"Results: {len(results)}")
            if results:
                top_result = results[0]
                title = top_result.get('title', 'No title')
                score = top_result.get('@search.score', 0.0)
                print(f"Top match: {title} (Score: {score:.3f})")
            else:
                print("No matches found")
        
        print("\n✅ Phrase search demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Make sure your Azure AI Search service is configured correctly.")


def phrase_search_best_practices():
    """Demonstrate best practices for phrase search"""
    print("\n📚 Phrase Search Best Practices")
    print("=" * 50)
    
    search_ops = PhraseSearch()
    
    print("\n💡 When to Use Phrase Search:")
    print("   ✅ Looking for specific technical terms")
    print("   ✅ Searching for proper names or titles")
    print("   ✅ Finding exact quotes or references")
    print("   ✅ When word order matters")
    
    print("\n⚠️ When NOT to Use Phrase Search:")
    print("   ❌ General topic searches")
    print("   ❌ When you want broader results")
    print("   ❌ Searching for concepts (not exact terms)")
    print("   ❌ When unsure of exact wording")
    
    # Demonstrate with examples
    print("\n🧪 Practice Examples:")
    
    # Good phrase search examples
    good_phrases = [
        "React hooks",
        "machine learning algorithm",
        "REST API"
    ]
    
    print("\n✅ Good Phrase Search Examples:")
    for phrase in good_phrases:
        results = search_ops.exact_phrase_search(phrase, top=1)
        status = "Found" if results else "Not found"
        print(f"   \"{phrase}\": {status}")
    
    # Show fallback strategy
    print("\n🔄 Fallback Strategy Example:")
    test_phrase = "deep learning neural networks"
    
    # Try exact phrase first
    exact_results = search_ops.exact_phrase_search(test_phrase, top=3)
    print(f"   Exact phrase \"{test_phrase}\": {len(exact_results)} results")
    
    if not exact_results:
        # Fallback to individual terms
        terms_results = search_ops.individual_terms_search(test_phrase, top=3)
        print(f"   Fallback to terms: {len(terms_results)} results")
        
        if terms_results:
            print("   💡 Recommendation: Use individual terms for broader results")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_phrase_search()
    phrase_search_best_practices()
    
    print("\n💡 Next Steps:")
    print("   - Try your own phrases with the examples above")
    print("   - Compare results between phrase and terms search")
    print("   - Check out 03_boolean_search.py for combining terms with AND/OR")
    print("   - Learn about wildcards in 04_wildcard_search.py")