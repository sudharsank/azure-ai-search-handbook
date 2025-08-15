"""
Module 7: Field Selection and Result Optimization

This example demonstrates how to use field selection to optimize response
payloads, improve performance, and control data exposure.
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Set
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
class FieldSelectionResult:
    """Data class for field selection results"""
    documents: List[Dict[str, Any]]
    fields_requested: List[str]
    fields_returned: List[str]
    duration_ms: float
    response_size_bytes: int
    document_count: int
    query: str


@dataclass
class IndexSchema:
    """Data class representing index schema information"""
    fields: List[Dict[str, Any]]
    retrievable_fields: List[str]
    searchable_fields: List[str]
    filterable_fields: List[str]
    sortable_fields: List[str]


class FieldSelector:
    """
    Field selector for optimizing search result payloads.
    
    This class provides functionality to select specific fields from search results,
    analyze response sizes, and optimize performance through strategic field selection.
    """
    
    def __init__(self, search_client: SearchClient):
        """
        Initialize the field selector.
        
        Args:
            search_client: Azure AI Search client
        """
        self.search_client = search_client
        self.index_schema: Optional[IndexSchema] = None
        self._field_presets = self._initialize_presets()
    
    def _initialize_presets(self) -> Dict[str, List[str]]:
        """Initialize common field selection presets."""
        return {
            # Minimal fields for list views
            'list_view': ['hotelId', 'hotelName', 'rating', 'category'],
            
            # Essential fields for search results
            'search_results': ['hotelId', 'hotelName', 'description', 'rating', 'location'],
            
            # Comprehensive fields for detail views
            'detail_view': [
                'hotelId', 'hotelName', 'description', 'category', 'rating',
                'location', 'address', 'tags', 'parkingIncluded', 'smokingAllowed'
            ],
            
            # Fields for map display
            'map_view': ['hotelId', 'hotelName', 'location', 'rating'],
            
            # Fields for comparison
            'comparison': ['hotelId', 'hotelName', 'rating', 'category', 'tags', 'parkingIncluded'],
            
            # Minimal fields for autocomplete
            'autocomplete': ['hotelId', 'hotelName'],
            
            # Fields for analytics/reporting
            'analytics': ['hotelId', 'category', 'rating', 'lastRenovationDate'],
            
            # Mobile-optimized minimal fields
            'mobile': ['hotelId', 'hotelName', 'rating'],
            
            # Desktop-optimized fields
            'desktop': ['hotelId', 'hotelName', 'description', 'rating', 'category']
        }
    
    def load_index_schema(self) -> IndexSchema:
        """
        Load and cache index schema for field validation.
        
        Note: In a real application, you would get this from the management client.
        For this example, we'll simulate the schema based on common hotel index fields.
        """
        if not self.index_schema:
            # Simulated schema - in practice, get this from the search service
            fields = [
                {'name': 'hotelId', 'type': 'Edm.String', 'retrievable': True, 'searchable': False},
                {'name': 'hotelName', 'type': 'Edm.String', 'retrievable': True, 'searchable': True},
                {'name': 'description', 'type': 'Edm.String', 'retrievable': True, 'searchable': True},
                {'name': 'category', 'type': 'Edm.String', 'retrievable': True, 'searchable': True},
                {'name': 'rating', 'type': 'Edm.Double', 'retrievable': True, 'searchable': False},
                {'name': 'location', 'type': 'Edm.GeographyPoint', 'retrievable': True, 'searchable': False},
                {'name': 'address', 'type': 'Edm.ComplexType', 'retrievable': True, 'searchable': True},
                {'name': 'tags', 'type': 'Collection(Edm.String)', 'retrievable': True, 'searchable': True},
                {'name': 'parkingIncluded', 'type': 'Edm.Boolean', 'retrievable': True, 'searchable': False},
                {'name': 'smokingAllowed', 'type': 'Edm.Boolean', 'retrievable': True, 'searchable': False},
                {'name': 'lastRenovationDate', 'type': 'Edm.DateTimeOffset', 'retrievable': True, 'searchable': False}
            ]
            
            self.index_schema = IndexSchema(
                fields=fields,
                retrievable_fields=[f['name'] for f in fields if f.get('retrievable', True)],
                searchable_fields=[f['name'] for f in fields if f.get('searchable', False)],
                filterable_fields=[f['name'] for f in fields if f.get('filterable', True)],
                sortable_fields=[f['name'] for f in fields if f.get('sortable', True)]
            )
        
        return self.index_schema
    
    def get_retrievable_fields(self) -> List[str]:
        """Get list of retrievable fields from index schema."""
        schema = self.load_index_schema()
        return schema.retrievable_fields
    
    def validate_fields(self, fields: List[str]) -> Dict[str, Any]:
        """
        Validate field selection against index schema.
        
        Args:
            fields: List of field names to validate
            
        Returns:
            Validation result with valid/invalid fields
        """
        schema = self.load_index_schema()
        retrievable_fields = set(schema.retrievable_fields)
        
        valid_fields = [f for f in fields if f in retrievable_fields]
        invalid_fields = [f for f in fields if f not in retrievable_fields]
        
        return {
            'valid_fields': valid_fields,
            'invalid_fields': invalid_fields,
            'is_valid': len(invalid_fields) == 0,
            'validation_message': f"Invalid fields: {invalid_fields}" if invalid_fields else "All fields valid"
        }
    
    def search_with_fields(self, search_text: str, fields: List[str], 
                          **kwargs) -> FieldSelectionResult:
        """
        Search with specific field selection.
        
        Args:
            search_text: Search query
            fields: List of fields to select
            **kwargs: Additional search parameters
            
        Returns:
            FieldSelectionResult with performance metrics
        """
        try:
            # Validate fields if schema is available
            if self.index_schema:
                validation = self.validate_fields(fields)
                if not validation['is_valid']:
                    print(f"Warning: {validation['validation_message']}")
            
            print(f"Searching with fields: {', '.join(fields) if fields else 'all fields'}")
            
            start_time = time.time()
            
            # Perform search with field selection
            search_params = {
                'search_text': search_text,
                'top': kwargs.get('top', 10),
                'skip': kwargs.get('skip', 0),
                'include_total_count': kwargs.get('include_total_count', False)
            }
            
            if fields:
                search_params['select'] = fields
            
            # Add other parameters
            for key, value in kwargs.items():
                if key not in search_params:
                    search_params[key] = value
            
            results = self.search_client.search(**search_params)
            documents = list(results)
            
            duration = (time.time() - start_time) * 1000
            
            # Calculate response size
            response_size = self._estimate_response_size(documents)
            
            # Get actual fields returned
            fields_returned = self._get_returned_fields(documents)
            
            return FieldSelectionResult(
                documents=documents,
                fields_requested=fields,
                fields_returned=fields_returned,
                duration_ms=duration,
                response_size_bytes=response_size,
                document_count=len(documents),
                query=search_text
            )
            
        except Exception as e:
            print(f"Field selection search error: {e}")
            raise
    
    def compare_field_selections(self, search_text: str, 
                               field_sets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compare response sizes and performance with different field selections.
        
        Args:
            search_text: Search query
            field_sets: List of field set configurations
            
        Returns:
            List of comparison results
        """
        comparisons = []
        
        for field_set in field_sets:
            try:
                result = self.search_with_fields(
                    search_text, 
                    field_set['fields'], 
                    top=10
                )
                
                comparisons.append({
                    'name': field_set['name'],
                    'fields': field_set['fields'],
                    'field_count': len(field_set['fields']),
                    'duration_ms': result.duration_ms,
                    'response_size_bytes': result.response_size_bytes,
                    'document_count': result.document_count,
                    'avg_size_per_doc': result.response_size_bytes / max(result.document_count, 1)
                })
                
                print(f"{field_set['name']}: {result.duration_ms:.1f}ms, ~{result.response_size_bytes} bytes")
                
            except Exception as e:
                comparisons.append({
                    'name': field_set['name'],
                    'fields': field_set['fields'],
                    'error': str(e)
                })
        
        return comparisons
    
    def get_field_presets(self) -> Dict[str, List[str]]:
        """Get predefined field selection presets."""
        return self._field_presets.copy()
    
    def search_with_context(self, search_text: str, context: str, 
                           **kwargs) -> FieldSelectionResult:
        """
        Search with context-based field selection.
        
        Args:
            search_text: Search query
            context: Context name (e.g., 'list_view', 'detail_view')
            **kwargs: Additional search parameters
            
        Returns:
            FieldSelectionResult
        """
        presets = self.get_field_presets()
        fields = presets.get(context, presets['search_results'])
        
        print(f"Using {context} context with fields: {', '.join(fields)}")
        
        return self.search_with_fields(search_text, fields, **kwargs)
    
    def _estimate_response_size(self, documents: List[Dict[str, Any]]) -> int:
        """Estimate response size in bytes."""
        try:
            return len(json.dumps(documents, default=str).encode('utf-8'))
        except Exception:
            return 0
    
    def _get_returned_fields(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Get fields that were actually returned in results."""
        if not documents:
            return []
        
        # Get fields from first document (excluding search metadata)
        first_doc = documents[0]
        return [key for key in first_doc.keys() if not key.startswith('@search')]


class FieldSelectionOptimizer:
    """Advanced field selection optimizer with caching and analytics."""
    
    def __init__(self, field_selector: FieldSelector):
        self.field_selector = field_selector
        self.performance_cache: Dict[str, Dict[str, Any]] = {}
    
    def find_optimal_fields(self, search_text: str, max_fields: int = 10) -> List[str]:
        """
        Find optimal field selection based on performance and content value.
        
        Args:
            search_text: Search query
            max_fields: Maximum number of fields to include
            
        Returns:
            List of optimal fields
        """
        # Get all available fields
        all_fields = self.field_selector.get_retrievable_fields()
        
        # Test different combinations (simplified approach)
        essential_fields = ['hotelId', 'hotelName', 'rating']
        optional_fields = [f for f in all_fields if f not in essential_fields]
        
        # Start with essential fields and add others based on value
        optimal_fields = essential_fields.copy()
        
        # Add high-value fields for search context
        high_value_fields = ['description', 'category', 'location']
        for field in high_value_fields:
            if field in optional_fields and len(optimal_fields) < max_fields:
                optimal_fields.append(field)
        
        return optimal_fields[:max_fields]
    
    def analyze_field_usage(self, search_queries: List[str]) -> Dict[str, Any]:
        """
        Analyze field usage patterns across multiple queries.
        
        Args:
            search_queries: List of search queries to analyze
            
        Returns:
            Analysis results
        """
        analysis = {
            'queries_analyzed': len(search_queries),
            'field_performance': {},
            'recommendations': []
        }
        
        presets = self.field_selector.get_field_presets()
        
        for query in search_queries:
            for preset_name, fields in presets.items():
                try:
                    result = self.field_selector.search_with_fields(query, fields, top=5)
                    
                    if preset_name not in analysis['field_performance']:
                        analysis['field_performance'][preset_name] = {
                            'total_duration': 0,
                            'total_size': 0,
                            'query_count': 0
                        }
                    
                    perf = analysis['field_performance'][preset_name]
                    perf['total_duration'] += result.duration_ms
                    perf['total_size'] += result.response_size_bytes
                    perf['query_count'] += 1
                    
                except Exception as e:
                    print(f"Error analyzing {preset_name} for query '{query}': {e}")
        
        # Calculate averages and generate recommendations
        for preset_name, perf in analysis['field_performance'].items():
            if perf['query_count'] > 0:
                perf['avg_duration'] = perf['total_duration'] / perf['query_count']
                perf['avg_size'] = perf['total_size'] / perf['query_count']
        
        # Find best performing preset
        if analysis['field_performance']:
            best_preset = min(
                analysis['field_performance'].items(),
                key=lambda x: x[1].get('avg_duration', float('inf'))
            )
            analysis['recommendations'].append(
                f"Best performing preset: {best_preset[0]} "
                f"(avg: {best_preset[1].get('avg_duration', 0):.1f}ms)"
            )
        
        return analysis


def demonstrate_basic_field_selection():
    """Demonstrate basic field selection functionality."""
    print("=== Basic Field Selection Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    field_selector = FieldSelector(search_client)
    
    try:
        # Search without field selection (all fields)
        print("1. Search without field selection (all fields):")
        all_fields_result = field_selector.search_with_fields('luxury', [], top=3)
        print(f"Duration: {all_fields_result.duration_ms:.1f}ms")
        print(f"Response size: ~{all_fields_result.response_size_bytes} bytes")
        print(f"Fields returned: {', '.join(all_fields_result.fields_returned)}\n")
        
        # Search with minimal field selection
        print("2. Search with minimal field selection:")
        minimal_fields = ['hotelId', 'hotelName', 'rating']
        minimal_result = field_selector.search_with_fields('luxury', minimal_fields, top=3)
        print(f"Duration: {minimal_result.duration_ms:.1f}ms")
        print(f"Response size: ~{minimal_result.response_size_bytes} bytes")
        print(f"Fields returned: {', '.join(minimal_result.fields_returned)}\n")
        
        # Calculate size reduction
        if all_fields_result.response_size_bytes > 0:
            size_reduction = (
                (all_fields_result.response_size_bytes - minimal_result.response_size_bytes) /
                all_fields_result.response_size_bytes * 100
            )
            print(f"Size reduction: {size_reduction:.1f}%\n")
        
        # Display sample results
        print("Sample results with minimal fields:")
        for i, doc in enumerate(minimal_result.documents):
            hotel_name = doc.get('hotelName', 'Unknown')
            rating = doc.get('rating', 'N/A')
            hotel_id = doc.get('hotelId', 'N/A')
            print(f"  {i + 1}. {hotel_name} (Rating: {rating}, ID: {hotel_id})")
        
    except Exception as e:
        print(f"Basic field selection demo error: {e}")


def demonstrate_context_based_selection():
    """Demonstrate context-based field selection."""
    print("\n=== Context-Based Field Selection Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    field_selector = FieldSelector(search_client)
    
    try:
        contexts = ['list_view', 'search_results', 'map_view', 'comparison']
        
        for context in contexts:
            print(f"{context.upper().replace('_', ' ')} Context:")
            result = field_selector.search_with_context('*', context, top=2)
            
            print(f"  Duration: {result.duration_ms:.1f}ms")
            print(f"  Response size: ~{result.response_size_bytes} bytes")
            print(f"  Fields: {', '.join(result.fields_returned)}")
            
            # Show sample result
            if result.documents:
                doc = result.documents[0]
                sample_data = {k: v for k, v in doc.items() if not k.startswith('@search')}
                sample_str = str(sample_data)[:200]
                print(f"  Sample: {sample_str}{'...' if len(sample_str) >= 200 else ''}")
            print()
        
    except Exception as e:
        print(f"Context-based selection demo error: {e}")


def demonstrate_performance_comparison():
    """Demonstrate performance comparison between different field selections."""
    print("=== Performance Comparison Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    field_selector = FieldSelector(search_client)
    
    try:
        field_sets = [
            {
                'name': 'All Fields',
                'fields': []  # Empty list means all fields
            },
            {
                'name': 'Essential Only',
                'fields': ['hotelId', 'hotelName', 'rating']
            },
            {
                'name': 'Search Results',
                'fields': ['hotelId', 'hotelName', 'description', 'rating', 'category']
            },
            {
                'name': 'Detail View',
                'fields': ['hotelId', 'hotelName', 'description', 'category', 'rating', 
                          'location', 'tags', 'parkingIncluded']
            }
        ]
        
        print("Comparing field selection performance:")
        comparisons = field_selector.compare_field_selections('luxury', field_sets)
        
        print("\nComparison Summary:")
        for comp in comparisons:
            if 'error' in comp:
                print(f"{comp['name']}: ERROR - {comp['error']}")
            else:
                print(f"{comp['name']}: {comp['duration_ms']:.1f}ms, "
                      f"~{comp['response_size_bytes']} bytes, "
                      f"{comp['document_count']} results")
        
        # Find the most efficient option
        valid_comparisons = [c for c in comparisons if 'error' not in c]
        if valid_comparisons:
            fastest = min(valid_comparisons, key=lambda x: x['duration_ms'])
            smallest = min(valid_comparisons, key=lambda x: x['response_size_bytes'])
            
            print(f"\nFastest: {fastest['name']} ({fastest['duration_ms']:.1f}ms)")
            print(f"Smallest: {smallest['name']} (~{smallest['response_size_bytes']} bytes)")
        
    except Exception as e:
        print(f"Performance comparison demo error: {e}")


def demonstrate_field_validation():
    """Demonstrate field validation functionality."""
    print("\n=== Field Validation Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    field_selector = FieldSelector(search_client)
    
    try:
        # Load schema for validation
        schema = field_selector.load_index_schema()
        
        # Test valid fields
        print("1. Testing valid fields:")
        valid_fields = ['hotelId', 'hotelName', 'rating']
        validation = field_selector.validate_fields(valid_fields)
        print(f"✅ Valid fields: {', '.join(valid_fields)}")
        print(f"Validation result: {validation['validation_message']}")
        
        # Test invalid fields
        print("\n2. Testing invalid fields:")
        invalid_fields = ['hotelId', 'nonExistentField', 'anotherBadField']
        validation = field_selector.validate_fields(invalid_fields)
        print(f"❌ Test fields: {', '.join(invalid_fields)}")
        print(f"Validation result: {validation['validation_message']}")
        
        # Show available fields
        print("\n3. Available retrievable fields:")
        retrievable_fields = field_selector.get_retrievable_fields()
        print(', '.join(retrievable_fields))
        
    except Exception as e:
        print(f"Field validation demo error: {e}")


def demonstrate_pagination_with_fields():
    """Demonstrate pagination combined with field selection."""
    print("\n=== Pagination with Field Selection Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    field_selector = FieldSelector(search_client)
    
    try:
        fields = ['hotelId', 'hotelName', 'rating', 'category']
        
        # Load multiple pages with field selection
        for page in range(3):
            print(f"Page {page + 1}:")
            
            result = field_selector.search_with_fields(
                '*', 
                fields, 
                skip=page * 5,
                top=5,
                include_total_count=(page == 0)  # Only get count on first page
            )
            
            print(f"  Duration: {result.duration_ms:.1f}ms")
            print(f"  Results: {result.document_count}")
            
            # Show results
            for i, doc in enumerate(result.documents):
                hotel_name = doc.get('hotelName', 'Unknown')
                category = doc.get('category', 'N/A')
                rating = doc.get('rating', 'N/A')
                print(f"    {i + 1}. {hotel_name} ({category}, Rating: {rating})")
            
            print()
        
    except Exception as e:
        print(f"Pagination with fields demo error: {e}")


def demonstrate_field_optimization():
    """Demonstrate advanced field optimization techniques."""
    print("\n=== Field Optimization Demo ===\n")
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    field_selector = FieldSelector(search_client)
    optimizer = FieldSelectionOptimizer(field_selector)
    
    try:
        # Find optimal fields
        print("1. Finding optimal field selection:")
        optimal_fields = optimizer.find_optimal_fields('luxury', max_fields=8)
        print(f"Optimal fields: {', '.join(optimal_fields)}")
        
        # Test optimal selection
        result = field_selector.search_with_fields('luxury', optimal_fields, top=5)
        print(f"Performance: {result.duration_ms:.1f}ms, ~{result.response_size_bytes} bytes")
        
        # Analyze field usage patterns
        print("\n2. Analyzing field usage patterns:")
        test_queries = ['luxury', 'beach', 'city', 'spa']
        analysis = optimizer.analyze_field_usage(test_queries)
        
        print(f"Analyzed {analysis['queries_analyzed']} queries")
        print("Performance by preset:")
        for preset, perf in analysis['field_performance'].items():
            if perf['query_count'] > 0:
                print(f"  {preset}: {perf['avg_duration']:.1f}ms avg, "
                      f"~{perf['avg_size']:.0f} bytes avg")
        
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
        
    except Exception as e:
        print(f"Field optimization demo error: {e}")


class FieldSelectionHelper:
    """Utility class for common field selection patterns."""
    
    @staticmethod
    def for_mobile() -> List[str]:
        """Get fields optimized for mobile interfaces."""
        return ['hotelId', 'hotelName', 'rating']
    
    @staticmethod
    def for_desktop() -> List[str]:
        """Get fields optimized for desktop interfaces."""
        return ['hotelId', 'hotelName', 'description', 'rating', 'category']
    
    @staticmethod
    def for_api() -> List[str]:
        """Get fields optimized for API responses."""
        return ['hotelId', 'hotelName', 'description', 'rating', 'category', 'location']
    
    @staticmethod
    def for_export() -> List[str]:
        """Get fields for data export."""
        return ['hotelId', 'hotelName', 'description', 'category', 'rating', 
                'address', 'tags', 'parkingIncluded', 'smokingAllowed']
    
    @staticmethod
    def custom(*fields: str) -> List[str]:
        """Create custom field selection."""
        return list(fields)


if __name__ == "__main__":
    try:
        demonstrate_basic_field_selection()
        demonstrate_context_based_selection()
        demonstrate_performance_comparison()
        demonstrate_field_validation()
        demonstrate_pagination_with_fields()
        demonstrate_field_optimization()
        
        # Show helper usage
        print("\n=== Field Selection Helper Demo ===\n")
        helper = FieldSelectionHelper()
        print("Helper examples:")
        print("Mobile:", helper.for_mobile())
        print("Desktop:", helper.for_desktop())
        print("API:", helper.for_api())
        print("Custom:", helper.custom('hotelId', 'hotelName', 'specialField'))
        
    except Exception as e:
        print(f"Demo failed: {e}")