"""
Module 7: Hit Highlighting for Enhanced Search Results

This example demonstrates how to implement hit highlighting to emphasize
search terms in results, improving user experience and search relevance visibility.
"""

import os
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY', 'your-api-key')
INDEX_NAME = os.getenv('INDEX_NAME', 'hotels-sample')


@dataclass
class HighlightResult:
    """Data class for hit highlighting results"""
    documents: List[Dict[str, Any]]
    highlights: List[Dict[str, List[str]]]
    search_terms: List[str]
    highlighted_fields: List[str]
    duration_ms: float
    query: str
    highlight_count: int


class HitHighlighter:
    """
    Hit highlighter for emphasizing search terms in results.
    
    This class provides functionality to add highlighting to search results,
    customize highlight tags, and analyze highlight effectiveness.
    """
    
    def __init__(self, search_client: SearchClient):
        """
        Initialize the hit highlighter.
        
        Args:
            search_client: Azure AI Search client
        """
        self.search_client = search_client
        self.default_highlight_fields = ['hotelName', 'description', 'category']
        self.default_pre_tag = '<em>'
        self.default_post_tag = '</em>'
    
    def search_with_highlighting(self, search_text: str, 
                               highlight_fields: Optional[List[str]] = None,
                               pre_tag: str = '<em>',
                               post_tag: str = '</em>',
                               max_highlights: int = 5,
                               **kwargs) -> HighlightResult:
        """
        Search with hit highlighting enabled.
        
        Args:
            search_text: Search query
            highlight_fields: Fields to highlight (None for default)
            pre_tag: Opening highlight tag
            post_tag: Closing highlight tag
            max_highlights: Maximum highlights per field
            **kwargs: Additional search parameters
            
        Returns:
            HighlightResult with highlighted content
        """
        try:
            if highlight_fields is None:
                highlight_fields = self.default_highlight_fields
            
            print(f"Searching with highlighting: '{search_text}'")
            print(f"Highlight fields: {', '.join(highlight_fields)}")
            
            start_time = time.time()
            
            # Configure highlighting parameters
            highlight_param = ','.join([
                f"{field}-{max_highlights}" for field in highlight_fields
            ])
            
            # Perform search with highlighting
            results = self.search_client.search(
                search_text=search_text,
                highlight_fields=highlight_param,
                highlight_pre_tag=pre_tag,
                highlight_post_tag=post_tag,
                top=kwargs.get('top', 10),
                skip=kwargs.get('skip', 0),
                include_total_count=kwargs.get('include_total_count', False),
                **{k: v for k, v in kwargs.items() 
                   if k not in ['top', 'skip', 'include_total_count']}
            )
            
            # Process results
            documents = []
            highlights = []
            highlight_count = 0
            
            for result in results:
                documents.append(result)
                
                # Extract highlights
                result_highlights = getattr(result, '@search.highlights', {})
                highlights.append(result_highlights)
                
                # Count total highlights
                for field_highlights in result_highlights.values():
                    highlight_count += len(field_highlights)
            
            duration = (time.time() - start_time) * 1000
            
            # Extract search terms for analysis
            search_terms = self._extract_search_terms(search_text)
            
            print(f"Search completed in {duration:.1f}ms")
            print(f"Found {len(documents)} results with {highlight_count} highlights")
            
            return HighlightResult(
                documents=documents,
                highlights=highlights,
                search_terms=search_terms,
                highlighted_fields=highlight_fields,
                duration_ms=duration,
                query=search_text,
                highlight_count=highlight_count
            )
            
        except Exception as e:
            print(f"Hit highlighting search error: {e}")
            raise
    
    def search_with_custom_tags(self, search_text: str, 
                              tag_style: str = 'bold',
                              highlight_fields: Optional[List[str]] = None,
                              **kwargs) -> HighlightResult:
        """
        Search with predefined highlight tag styles.
        
        Args:
            search_text: Search query
            tag_style: Style name ('bold', 'italic', 'mark', 'custom')
            highlight_fields: Fields to highlight
            **kwargs: Additional search parameters
            
        Returns:
            HighlightResult with styled highlights
        """
        tag_styles = {
            'bold': ('<b>', '</b>'),
            'italic': ('<i>', '</i>'),
            'mark': ('<mark>', '</mark>'),
            'underline': ('<u>', '</u>'),
            'strong': ('<strong>', '</strong>'),
            'span': ('<span class="highlight">', '</span>'),
            'custom': ('**', '**')  # Markdown-style
        }
        
        if tag_style not in tag_styles:
            raise ValueError(f"Unknown tag style: {tag_style}")
        
        pre_tag, post_tag = tag_styles[tag_style]
        
        print(f"Using {tag_style} highlighting style: {pre_tag}...{post_tag}")
        
        return self.search_with_highlighting(
            search_text, 
            highlight_fields, 
            pre_tag, 
            post_tag, 
            **kwargs
        )
    
    def search_phrase_highlighting(self, phrase: str,
                                 highlight_fields: Optional[List[str]] = None,
                                 **kwargs) -> HighlightResult:
        """
        Search with phrase highlighting (quoted search).
        
        Args:
            phrase: Phrase to search for
            highlight_fields: Fields to highlight
            **kwargs: Additional search parameters
            
        Returns:
            HighlightResult with phrase highlights
        """
        # Ensure phrase is quoted for exact matching
        quoted_phrase = f'"{phrase}"' if not phrase.startswith('"') else phrase
        
        print(f"Searching for phrase: {quoted_phrase}")
        
        return self.search_with_highlighting(
            quoted_phrase,
            highlight_fields,
            **kwargs
        )
    
    def compare_highlighting_strategies(self, search_text: str) -> Dict[str, Any]:
        """
        Compare different highlighting strategies.
        
        Args:
            search_text: Search query
            
        Returns:
            Comparison results
        """
        strategies = [
            {
                'name': 'Default Fields',
                'fields': None,
                'max_highlights': 5
            },
            {
                'name': 'Title Only',
                'fields': ['hotelName'],
                'max_highlights': 3
            },
            {
                'name': 'Description Only',
                'fields': ['description'],
                'max_highlights': 10
            },
            {
                'name': 'All Text Fields',
                'fields': ['hotelName', 'description', 'category', 'tags'],
                'max_highlights': 5
            }
        ]
        
        comparisons = []
        
        for strategy in strategies:
            try:
                result = self.search_with_highlighting(
                    search_text,
                    highlight_fields=strategy['fields'],
                    max_highlights=strategy['max_highlights'],
                    top=5
                )
                
                comparisons.append({
                    'name': strategy['name'],
                    'fields': strategy['fields'] or self.default_highlight_fields,
                    'duration_ms': result.duration_ms,
                    'highlight_count': result.highlight_count,
                    'results_count': len(result.documents),
                    'avg_highlights_per_result': result.highlight_count / max(len(result.documents), 1)
                })
                
                print(f"{strategy['name']}: {result.highlight_count} highlights in {result.duration_ms:.1f}ms")
                
            except Exception as e:
                comparisons.append({
                    'name': strategy['name'],
                    'error': str(e)
                })
        
        return {
            'query': search_text,
            'strategies': comparisons,
            'best_strategy': max(
                [c for c in comparisons if 'error' not in c],
                key=lambda x: x['highlight_count'],
                default=None
            )
        }
    
    def analyze_highlight_coverage(self, result: HighlightResult) -> Dict[str, Any]:
        """
        Analyze highlight coverage and effectiveness.
        
        Args:
            result: HighlightResult to analyze
            
        Returns:
            Coverage analysis
        """
        analysis = {
            'total_documents': len(result.documents),
            'total_highlights': result.highlight_count,
            'highlighted_documents': 0,
            'field_coverage': {},
            'highlight_distribution': [],
            'search_terms_found': []
        }
        
        # Analyze field coverage
        for field in result.highlighted_fields:
            analysis['field_coverage'][field] = {
                'documents_with_highlights': 0,
                'total_highlights': 0,
                'avg_highlights_per_doc': 0
            }
        
        # Process each document's highlights
        for i, highlights in enumerate(result.highlights):
            doc_highlight_count = 0
            
            if highlights:
                analysis['highlighted_documents'] += 1
                
                for field, field_highlights in highlights.items():
                    if field in analysis['field_coverage']:
                        analysis['field_coverage'][field]['documents_with_highlights'] += 1
                        analysis['field_coverage'][field]['total_highlights'] += len(field_highlights)
                        doc_highlight_count += len(field_highlights)
            
            analysis['highlight_distribution'].append({
                'document_index': i,
                'highlight_count': doc_highlight_count
            })
        
        # Calculate averages
        for field_data in analysis['field_coverage'].values():
            if field_data['documents_with_highlights'] > 0:
                field_data['avg_highlights_per_doc'] = (
                    field_data['total_highlights'] / field_data['documents_with_highlights']
                )
        
        # Analyze search term coverage
        for term in result.search_terms:
            term_found = any(
                any(term.lower() in highlight.lower() 
                    for highlight_list in doc_highlights.values() 
                    for highlight in highlight_list)
                for doc_highlights in result.highlights
            )
            if term_found:
                analysis['search_terms_found'].append(term)
        
        analysis['coverage_percentage'] = (
            analysis['highlighted_documents'] / max(analysis['total_documents'], 1) * 100
        )
        
        return analysis
    
    def extract_highlighted_snippets(self, result: HighlightResult, 
                                   max_snippet_length: int = 200) -> List[Dict[str, Any]]:
        """
        Extract highlighted snippets for display.
        
        Args:
            result: HighlightResult to process
            max_snippet_length: Maximum snippet length
            
        Returns:
            List of snippet data
        """
        snippets = []
        
        for i, (doc, highlights) in enumerate(zip(result.documents, result.highlights)):
            doc_snippets = {
                'document_index': i,
                'document_id': doc.get('hotelId', doc.get('id', f'doc_{i}')),
                'title': doc.get('hotelName', doc.get('title', 'Unknown')),
                'snippets': []
            }
            
            for field, field_highlights in highlights.items():
                for highlight in field_highlights:
                    # Truncate if too long
                    if len(highlight) > max_snippet_length:
                        # Try to keep highlight tags intact
                        truncated = highlight[:max_snippet_length]
                        if '<' in truncated and '>' not in truncated[truncated.rfind('<'):]:
                            # Incomplete tag, truncate before it
                            truncated = highlight[:truncated.rfind('<')]
                        highlight = truncated + '...'
                    
                    doc_snippets['snippets'].append({
                        'field': field,
                        'text': highlight,
                        'length': len(highlight)
                    })
            
            if doc_snippets['snippets']:
                snippets.append(doc_snippets)
        
        return snippets
    
    def _extract_search_terms(self, search_text: str) -> List[str]:
        """Extract individual search terms from query."""
        # Simple term extraction (could be enhanced for complex queries)
        # Remove quotes and special characters, split on spaces
        cleaned = re.sub(r'[^\w\s]', ' ', search_text)
        terms = [term.strip() for term in cleaned.split() if term.strip()]
        return terms


def demonstrate_basic_highlighting():
    """Demonstrate basic hit highlighting functionality."""
    print("=== Basic Hit Highlighting Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    highlighter = HitHighlighter(search_client)
    
    try:
        # Basic highlighting
        print("1. Basic highlighting with default settings:")
        result = highlighter.search_with_highlighting('luxury hotel', top=3)
        
        print(f"Query: '{result.query}'")
        print(f"Highlighted fields: {', '.join(result.highlighted_fields)}")
        print(f"Total highlights: {result.highlight_count}")
        
        # Display highlighted results
        for i, (doc, highlights) in enumerate(zip(result.documents, result.highlights)):
            hotel_name = doc.get('hotelName', 'Unknown')
            print(f"\n  Result {i + 1}: {hotel_name}")
            
            for field, field_highlights in highlights.items():
                print(f"    {field}:")
                for highlight in field_highlights:
                    print(f"      • {highlight}")
        
    except Exception as e:
        print(f"Basic highlighting demo error: {e}")


def demonstrate_custom_highlighting():
    """Demonstrate custom highlighting tags and styles."""
    print("\n=== Custom Highlighting Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    highlighter = HitHighlighter(search_client)
    
    try:
        search_query = 'beach resort'
        styles = ['bold', 'mark', 'custom']
        
        for style in styles:
            print(f"{style.upper()} highlighting:")
            result = highlighter.search_with_custom_tags(
                search_query, 
                tag_style=style, 
                top=2
            )
            
            # Show first result's highlights
            if result.highlights:
                first_highlights = result.highlights[0]
                for field, highlights in first_highlights.items():
                    if highlights:
                        print(f"  {field}: {highlights[0]}")
            print()
        
    except Exception as e:
        print(f"Custom highlighting demo error: {e}")


def demonstrate_phrase_highlighting():
    """Demonstrate phrase highlighting."""
    print("=== Phrase Highlighting Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    highlighter = HitHighlighter(search_client)
    
    try:
        # Compare individual terms vs phrase
        phrase = "luxury hotel"
        
        print("1. Individual terms highlighting:")
        individual_result = highlighter.search_with_highlighting(phrase, top=2)
        
        print("2. Phrase highlighting:")
        phrase_result = highlighter.search_phrase_highlighting(phrase, top=2)
        
        print(f"\nIndividual terms: {individual_result.highlight_count} highlights")
        print(f"Phrase search: {phrase_result.highlight_count} highlights")
        
        # Show comparison
        if phrase_result.highlights:
            print("\nPhrase highlighting example:")
            first_highlights = phrase_result.highlights[0]
            for field, highlights in first_highlights.items():
                for highlight in highlights:
                    print(f"  {field}: {highlight}")
        
    except Exception as e:
        print(f"Phrase highlighting demo error: {e}")


def demonstrate_highlighting_analysis():
    """Demonstrate highlighting analysis and optimization."""
    print("\n=== Highlighting Analysis Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    highlighter = HitHighlighter(search_client)
    
    try:
        search_query = 'spa wellness'
        
        # Compare strategies
        print("1. Comparing highlighting strategies:")
        comparison = highlighter.compare_highlighting_strategies(search_query)
        
        print(f"Query: '{comparison['query']}'")
        for strategy in comparison['strategies']:
            if 'error' in strategy:
                print(f"  {strategy['name']}: ERROR - {strategy['error']}")
            else:
                print(f"  {strategy['name']}: {strategy['highlight_count']} highlights, "
                      f"{strategy['avg_highlights_per_result']:.1f} avg per result")
        
        if comparison['best_strategy']:
            print(f"\nBest strategy: {comparison['best_strategy']['name']}")
        
        # Detailed analysis
        print("\n2. Detailed highlight analysis:")
        result = highlighter.search_with_highlighting(search_query, top=5)
        analysis = highlighter.analyze_highlight_coverage(result)
        
        print(f"Coverage: {analysis['coverage_percentage']:.1f}% of documents highlighted")
        print(f"Total highlights: {analysis['total_highlights']}")
        print(f"Search terms found: {', '.join(analysis['search_terms_found'])}")
        
        print("\nField coverage:")
        for field, coverage in analysis['field_coverage'].items():
            print(f"  {field}: {coverage['documents_with_highlights']} docs, "
                  f"{coverage['total_highlights']} highlights")
        
    except Exception as e:
        print(f"Highlighting analysis demo error: {e}")


def demonstrate_snippet_extraction():
    """Demonstrate highlighted snippet extraction."""
    print("\n=== Snippet Extraction Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    highlighter = HitHighlighter(search_client)
    
    try:
        result = highlighter.search_with_highlighting(
            'ocean view restaurant', 
            highlight_fields=['description', 'hotelName'],
            top=3
        )
        
        snippets = highlighter.extract_highlighted_snippets(result, max_snippet_length=150)
        
        print("Extracted highlighted snippets:")
        for snippet_data in snippets:
            print(f"\n{snippet_data['title']} (ID: {snippet_data['document_id']}):")
            
            for snippet in snippet_data['snippets']:
                print(f"  [{snippet['field']}] {snippet['text']}")
        
    except Exception as e:
        print(f"Snippet extraction demo error: {e}")


def demonstrate_highlighting_with_pagination():
    """Demonstrate highlighting combined with pagination."""
    print("\n=== Highlighting with Pagination Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    highlighter = HitHighlighter(search_client)
    
    try:
        search_query = 'hotel'
        page_size = 3
        
        for page in range(2):
            print(f"Page {page + 1}:")
            
            result = highlighter.search_with_highlighting(
                search_query,
                skip=page * page_size,
                top=page_size,
                include_total_count=(page == 0)
            )
            
            print(f"  {len(result.documents)} results with {result.highlight_count} highlights")
            
            # Show first result's highlights
            if result.highlights:
                first_highlights = result.highlights[0]
                doc_title = result.documents[0].get('hotelName', 'Unknown')
                print(f"  Sample from '{doc_title}':")
                
                for field, highlights in first_highlights.items():
                    if highlights:
                        print(f"    {field}: {highlights[0][:100]}...")
            print()
        
    except Exception as e:
        print(f"Highlighting with pagination demo error: {e}")


class HighlightingHelper:
    """Utility class for common highlighting patterns."""
    
    @staticmethod
    def for_search_results() -> Dict[str, Any]:
        """Get highlighting config for search results."""
        return {
            'highlight_fields': ['hotelName', 'description'],
            'pre_tag': '<mark>',
            'post_tag': '</mark>',
            'max_highlights': 3
        }
    
    @staticmethod
    def for_autocomplete() -> Dict[str, Any]:
        """Get highlighting config for autocomplete."""
        return {
            'highlight_fields': ['hotelName'],
            'pre_tag': '<strong>',
            'post_tag': '</strong>',
            'max_highlights': 1
        }
    
    @staticmethod
    def for_detailed_view() -> Dict[str, Any]:
        """Get highlighting config for detailed views."""
        return {
            'highlight_fields': ['hotelName', 'description', 'category', 'tags'],
            'pre_tag': '<span class="highlight">',
            'post_tag': '</span>',
            'max_highlights': 10
        }
    
    @staticmethod
    def clean_highlights(text: str, preserve_tags: bool = False) -> str:
        """Clean highlight tags from text."""
        if preserve_tags:
            return text
        
        # Remove common highlight tags
        import re
        patterns = [
            r'<em>(.*?)</em>',
            r'<mark>(.*?)</mark>',
            r'<b>(.*?)</b>',
            r'<strong>(.*?)</strong>',
            r'<span[^>]*>(.*?)</span>'
        ]
        
        cleaned = text
        for pattern in patterns:
            cleaned = re.sub(pattern, r'\1', cleaned)
        
        return cleaned


if __name__ == "__main__":
    try:
        demonstrate_basic_highlighting()
        demonstrate_custom_highlighting()
        demonstrate_phrase_highlighting()
        demonstrate_highlighting_analysis()
        demonstrate_snippet_extraction()
        demonstrate_highlighting_with_pagination()
        
        # Show helper usage
        print("\n=== Highlighting Helper Demo ===\n")
        helper = HighlightingHelper()
        print("Helper configurations:")
        print("Search results:", helper.for_search_results())
        print("Autocomplete:", helper.for_autocomplete())
        print("Detailed view:", helper.for_detailed_view())
        
        # Test cleaning
        sample_text = "This is a <mark>highlighted</mark> <em>sample</em> text."
        print(f"\nOriginal: {sample_text}")
        print(f"Cleaned: {helper.clean_highlights(sample_text)}")
        
    except Exception as e:
        print(f"Demo failed: {e}")