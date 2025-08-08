"""
Result Processing - Module 2 Python Examples
Processing and formatting search results from Azure AI Search

This module demonstrates:
- Basic result processing
- Result formatting for display
- Score analysis
- Result filtering and sorting
- Export capabilities
"""

import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add setup directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'setup'))
from connection_utils import get_default_search_client


@dataclass
class ProcessedResult:
    """Simple structure for processed search results"""
    title: str
    score: float
    author: str
    content_preview: str
    url: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'score': self.score,
            'author': self.author,
            'content_preview': self.content_preview,
            'url': self.url
        }


class ResultProcessor:
    """Class for processing search results"""
    
    def __init__(self, max_content_length: int = 150):
        self.max_content_length = max_content_length
        self.logger = logging.getLogger("result_processor")
    
    def process_raw_results(self, raw_results: List[Dict[str, Any]]) -> List[ProcessedResult]:
        """
        Convert raw search results to ProcessedResult objects
        
        Args:
            raw_results: List of raw result dictionaries
            
        Returns:
            List of ProcessedResult objects
        """
        processed_results = []
        
        for result in raw_results:
            try:
                # Extract and clean fields
                title = result.get('title', 'Untitled')
                score = result.get('@search.score', 0.0)
                author = result.get('author', 'Unknown')
                url = result.get('url', '#')
                
                # Create content preview
                content = result.get('content', '')
                content_preview = self._create_preview(content)
                
                processed_result = ProcessedResult(
                    title=title,
                    score=score,
                    author=author,
                    content_preview=content_preview,
                    url=url
                )
                
                processed_results.append(processed_result)
                
            except Exception as e:
                self.logger.error(f"Error processing result: {str(e)}")
                continue
        
        return processed_results
    
    def _create_preview(self, content: str) -> str:
        """Create a content preview with appropriate length"""
        if not content:
            return "No content available"
        
        if len(content) <= self.max_content_length:
            return content
        
        # Find a good breaking point
        preview = content[:self.max_content_length]
        last_space = preview.rfind(' ')
        
        if last_space > self.max_content_length * 0.8:
            preview = preview[:last_space]
        
        return preview + "..."
    
    def format_for_display(self, results: List[ProcessedResult]) -> str:
        """
        Format results for console display
        
        Args:
            results: List of ProcessedResult objects
            
        Returns:
            Formatted string for display
        """
        if not results:
            return "No results found."
        
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"SEARCH RESULTS ({len(results)} found)")
        output.append(f"{'='*60}")
        
        for i, result in enumerate(results, 1):
            output.append(f"\n{i}. {result.title}")
            output.append(f"   Score: {result.score:.3f}")
            
            if result.author != "Unknown":
                output.append(f"   Author: {result.author}")
            
            if result.content_preview:
                output.append(f"   Preview: {result.content_preview}")
            
            if result.url != "#":
                output.append(f"   URL: {result.url}")
            
            output.append(f"   {'-'*50}")
        
        return "\n".join(output)
    
    def sort_by_score(self, results: List[ProcessedResult], reverse: bool = True) -> List[ProcessedResult]:
        """Sort results by score"""
        return sorted(results, key=lambda x: x.score, reverse=reverse)
    
    def filter_by_score(self, results: List[ProcessedResult], min_score: float) -> List[ProcessedResult]:
        """Filter results by minimum score"""
        return [result for result in results if result.score >= min_score]
    
    def analyze_scores(self, results: List[ProcessedResult]) -> Dict[str, float]:
        """Analyze score distribution"""
        if not results:
            return {}
        
        scores = [result.score for result in results]
        
        return {
            'count': len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'avg_score': sum(scores) / len(scores),
            'score_range': max(scores) - min(scores)
        }
    
    def export_to_json(self, results: List[ProcessedResult], filename: str):
        """Export results to JSON file"""
        try:
            results_dict = [result.to_dict() for result in results]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {str(e)}")


def demonstrate_result_processing():
    """Demonstrate result processing capabilities"""
    print("🔧 Result Processing Demonstration")
    print("=" * 50)
    
    try:
        # Get some sample results
        search_client = get_default_search_client()
        raw_results = search_client.search(search_text="python programming", top=5)
        raw_result_list = list(raw_results)
        
        if not raw_result_list:
            print("❌ No results found for demo. Make sure your index has data.")
            return
        
        # Process results
        processor = ResultProcessor()
        processed_results = processor.process_raw_results(raw_result_list)
        
        print(f"✅ Processed {len(processed_results)} results")
        
        # Display formatted results
        formatted_output = processor.format_for_display(processed_results[:3])
        print(formatted_output)
        
        # Analyze scores
        stats = processor.analyze_scores(processed_results)
        print(f"\n📊 Score Analysis:")
        print(f"   Total results: {stats['count']}")
        print(f"   Score range: {stats['min_score']:.3f} - {stats['max_score']:.3f}")
        print(f"   Average score: {stats['avg_score']:.3f}")
        
        # Filter high-quality results
        high_quality = processor.filter_by_score(processed_results, 1.0)
        print(f"\n🎯 High-quality results (score ≥ 1.0): {len(high_quality)}")
        
        # Export to JSON
        processor.export_to_json(processed_results, "sample_results.json")
        
        print("\n✅ Result processing demonstration completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Run demonstration
    demonstrate_result_processing()
    
    print("\n💡 Next Steps:")
    print("   - Try processing results from different searches")
    print("   - Experiment with different filtering criteria")
    print("   - Check out 07_error_handling.py for robust error handling")
    print("   - Learn about search patterns in 08_search_patterns.py")