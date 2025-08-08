"""
Simple Text Search - Module 2 Python Examples
Basic text search operations in Azure AI Search

This module demonstrates:
- Simple text queries
- Basic result handling
- Search client initialization
- Understanding search scores
"""

import os
import sys
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


class SimpleTextSearch:
    """Class demonstrating simple text search operations"""
    
    def __init__(self, search_client: SearchClient = None):
        """Initialize with a search client"""
        self.search_client = search_client or get_default_search_client()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for search operations"""
        logger = logging.getLogger("simple_text_search")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def basic_search(self, query: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a basic text search
        
        Args:
            query: Search query string
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            self.logger.info(f"Performing basic search: '{query}'")
            
            # Perform the search
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            # Convert to list for easier handling
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Found {len(result_list)} results")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error in basic search: {str(e)}")
            return []
    
    def search_with_limit(self, query: str, top: int = 5) -> List[Dict[str, Any]]:
        """
        Search with a specific result limit
        
        Args:
            query: Search query string
            top: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        return self.basic_search(query, top)
    
    def get_all_documents(self, top: int = 20) -> List[Dict[str, Any]]:
        """
        Get all documents in the index (useful for browsing)
        
        Args:
            top: Maximum number of documents to return
            
        Returns:
            List of all documents
        """
        try:
            self.logger.info("Retrieving all documents")
            
            results = self.search_client.search(
                search_text="*",  # Wildcard to match all documents
                top=top
            )
            
            result_list = []
            for result in results:
                result_list.append(dict(result))
            
            self.logger.info(f"Retrieved {len(result_list)} documents")
            return result_list
            
        except Exception as e:
            self.logger.error(f"Error retrieving all documents: {str(e)}")
            return []
    
    def display_results(self, results: List[Dict[str, Any]], show_scores: bool = True):
        """
        Display search results in a readable format
        
        Args:
            results: List of search result dictionaries
            show_scores: Whether to display search scores
        """
        if not results:
            print("No results found.")
            return
        
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS ({len(results)} found)")
        print(f"{'='*60}")
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Untitled')
            print(f"\n{i}. {title}")
            
            if show_scores and '@search.score' in result:
                score = result['@search.score']
                print(f"   Score: {score:.3f}")
            
            author = result.get('author', 'Unknown')
            if author != 'Unknown':
                print(f"   Author: {author}")
            
            content = result.get('content', '')
            if content:
                preview = content[:150] + '...' if len(content) > 150 else content
                print(f"   Preview: {preview}")
            
            url = result.get('url', '')
            if url:
                print(f"   URL: {url}")
            
            print(f"   {'-'*50}")
    
    def analyze_scores(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze search scores to understand result quality
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Dictionary with score statistics
        """
        if not results:
            return {}
        
        scores = [result.get('@search.score', 0.0) for result in results]
        
        return {
            'total_results': len(results),
            'min_score': min(scores),
            'max_score': max(scores),
            'avg_score': sum(scores) / len(scores),
            'score_range': max(scores) - min(scores)
        }


def demonstrate_simple_search():
    """Demonstrate simple text search operations"""
    print("🔍 Simple Text Search Demonstration")
    print("=" * 50)
    
    try:
        # Initialize search operations
        search_ops = SimpleTextSearch()
        
        # Example 1: Basic search
        print("\n1️⃣ Basic Text Search")
        print("-" * 30)
        
        query = "python programming"
        results = search_ops.basic_search(query, top=5)
        search_ops.display_results(results)
        
        # Analyze the results
        if results:
            stats = search_ops.analyze_scores(results)
            print(f"\n📊 Score Analysis:")
            print(f"   Total results: {stats['total_results']}")
            print(f"   Score range: {stats['min_score']:.3f} - {stats['max_score']:.3f}")
            print(f"   Average score: {stats['avg_score']:.3f}")
        
        # Example 2: Different query
        print(f"\n{'='*60}")
        print("\n2️⃣ Another Search Example")
        print("-" * 30)
        
        query2 = "machine learning"
        results2 = search_ops.basic_search(query2, top=3)
        search_ops.display_results(results2)
        
        # Example 3: Browse all documents
        print(f"\n{'='*60}")
        print("\n3️⃣ Browse All Documents")
        print("-" * 30)
        
        all_docs = search_ops.get_all_documents(top=5)
        print(f"Total documents available: {len(all_docs)}")
        
        if all_docs:
            print("\nFirst few documents:")
            for i, doc in enumerate(all_docs[:3], 1):
                title = doc.get('title', 'Untitled')
                author = doc.get('author', 'Unknown')
                print(f"  {i}. {title} by {author}")
        
        print("\n✅ Simple text search demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Make sure your Azure AI Search service is configured correctly.")


def interactive_search_example():
    """Interactive example for users to try different queries"""
    print("\n🎮 Interactive Search Example")
    print("=" * 50)
    
    search_ops = SimpleTextSearch()
    
    # Sample queries for demonstration
    sample_queries = [
        "web development",
        "tutorial",
        "javascript",
        "data science",
        "artificial intelligence"
    ]
    
    print("Here are some sample queries you can try:")
    for i, query in enumerate(sample_queries, 1):
        print(f"  {i}. {query}")
    
    # For demonstration, let's try the first query
    demo_query = sample_queries[0]
    print(f"\n🔍 Trying query: '{demo_query}'")
    print("-" * 40)
    
    results = search_ops.basic_search(demo_query, top=3)
    search_ops.display_results(results, show_scores=True)
    
    if results:
        stats = search_ops.analyze_scores(results)
        print(f"\n💡 Tips for interpreting results:")
        print(f"   - Higher scores (closer to {stats['max_score']:.1f}) indicate better matches")
        print(f"   - Scores below 1.0 might indicate weaker relevance")
        print(f"   - Try different keywords if results aren't relevant")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstrations
    demonstrate_simple_search()
    interactive_search_example()
    
    print("\n💡 Next Steps:")
    print("   - Try modifying the queries above")
    print("   - Experiment with different search terms")
    print("   - Check out 02_phrase_search.py for exact phrase matching")
    print("   - Learn about boolean searches in 03_boolean_search.py")