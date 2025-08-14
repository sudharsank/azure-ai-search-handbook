#!/usr/bin/env python3
"""
Azure AI Search - Complex Filters

This script demonstrates advanced filtering operations using Azure AI Search,
including collection filtering, nested conditions, and complex logical combinations.

Key Features:
- Collection filtering with any() and all() functions
- Nested condition optimization
- Advanced logical combinations
- Filter logic tree visualization
- Performance optimization for complex filters
- Real-world complex filtering scenarios

Prerequisites:
- Azure AI Search service configured
- Sample data with collection fields loaded
- Environment variables set in .env file
"""

import os
import time
import re
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class FilterCondition:
    """Represents a single filter condition."""
    field: str
    operator: str
    value: Any
    collection_function: Optional[str] = None  # 'any' or 'all'

@dataclass
class FilterGroup:
    """Represents a group of filter conditions with logical operator."""
    conditions: List[Union[FilterCondition, 'FilterGroup']]
    logical_operator: str = 'and'  # 'and' or 'or'

class ComplexFilterBuilder:
    """Builds and manages complex filter expressions for Azure AI Search."""
    
    def __init__(self):
        """Initialize the complex filter builder."""
        self.search_client = self._initialize_client()
        self.filter_templates = self._load_filter_templates()
    
    def _initialize_client(self) -> SearchClient:
        """Initialize Azure AI Search client."""
        try:
            endpoint = os.getenv('SEARCH_ENDPOINT')
            api_key = os.getenv('SEARCH_API_KEY')
            index_name = os.getenv('INDEX_NAME')
            
            if not all([endpoint, api_key, index_name]):
                raise ValueError("Missing required environment variables")
            
            credential = AzureKeyCredential(api_key)
            client = SearchClient(endpoint, index_name, credential)
            
            print(f"✅ Connected to Azure AI Search")
            print(f"📍 Endpoint: {endpoint}")
            print(f"📊 Index: {index_name}")
            
            return client
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            raise
    
    def _load_filter_templates(self) -> Dict[str, str]:
        """Load common complex filter templates."""
        return {
            'collection_any': "{collection}/any(item: item eq '{value}')",
            'collection_all': "{collection}/all(item: item eq '{value}')",
            'collection_contains': "{collection}/any(item: contains(item, '{value}'))",
            'nested_and': "({condition1}) and ({condition2})",
            'nested_or': "({condition1}) or ({condition2})",
            'range_with_collection': "({range_condition}) and {collection}/any(item: item eq '{value}')",
            'multi_collection': "{collection1}/any(item: item eq '{value1}') and {collection2}/any(item: item eq '{value2}')"
        }
    
    def build_collection_filter(self, collection_field: str, values: List[str], 
                              function: str = 'any', operator: str = 'eq') -> str:
        """
        Build a collection filter expression.
        
        Args:
            collection_field: Name of the collection field
            values: List of values to match
            function: 'any' or 'all'
            operator: Comparison operator ('eq', 'contains', etc.)
            
        Returns:
            OData filter expression
        """
        if not values:
            raise ValueError("At least one value must be provided")
        
        if function not in ['any', 'all']:
            raise ValueError("Function must be 'any' or 'all'")
        
        conditions = []
        for value in values:
            if operator == 'eq':
                condition = f"item eq '{value}'"
            elif operator == 'contains':
                condition = f"contains(item, '{value}')"
            elif operator == 'startswith':
                condition = f"startswith(item, '{value}')"
            elif operator == 'endswith':
                condition = f"endswith(item, '{value}')"
            else:
                raise ValueError(f"Unsupported operator: {operator}")
            
            conditions.append(condition)
        
        # Combine conditions with OR for multiple values
        combined_condition = " or ".join(conditions)
        
        return f"{collection_field}/{function}(item: {combined_condition})"
    
    def build_nested_filter(self, conditions: List[FilterCondition], 
                          logical_operator: str = 'and') -> str:
        """
        Build a nested filter with multiple conditions.
        
        Args:
            conditions: List of filter conditions
            logical_operator: 'and' or 'or'
            
        Returns:
            OData filter expression
        """
        if not conditions:
            raise ValueError("At least one condition must be provided")
        
        filter_parts = []
        
        for condition in conditions:
            if condition.collection_function:
                # Collection filter
                if condition.operator == 'eq':
                    item_condition = f"item eq '{condition.value}'"
                elif condition.operator == 'contains':
                    item_condition = f"contains(item, '{condition.value}')"
                else:
                    item_condition = f"item {condition.operator} '{condition.value}'"
                
                filter_part = f"{condition.field}/{condition.collection_function}(item: {item_condition})"
            else:
                # Regular filter
                if isinstance(condition.value, str):
                    filter_part = f"{condition.field} {condition.operator} '{condition.value}'"
                else:
                    filter_part = f"{condition.field} {condition.operator} {condition.value}"
            
            filter_parts.append(filter_part)
        
        return f" {logical_operator} ".join(filter_parts)
    
    def build_complex_filter_tree(self, filter_group: FilterGroup) -> str:
        """
        Build a complex filter from a hierarchical filter tree.
        
        Args:
            filter_group: Root filter group
            
        Returns:
            OData filter expression
        """
        parts = []
        
        for item in filter_group.conditions:
            if isinstance(item, FilterCondition):
                # Single condition
                if item.collection_function:
                    if item.operator == 'eq':
                        item_condition = f"item eq '{item.value}'"
                    elif item.operator == 'contains':
                        item_condition = f"contains(item, '{item.value}')"
                    else:
                        item_condition = f"item {item.operator} '{item.value}'"
                    
                    part = f"{item.field}/{item.collection_function}(item: {item_condition})"
                else:
                    if isinstance(item.value, str):
                        part = f"{item.field} {item.operator} '{item.value}'"
                    else:
                        part = f"{item.field} {item.operator} {item.value}"
                
                parts.append(part)
                
            elif isinstance(item, FilterGroup):
                # Nested group
                nested_filter = self.build_complex_filter_tree(item)
                parts.append(f"({nested_filter})")
        
        return f" {filter_group.logical_operator} ".join(parts)
    
    def optimize_filter_expression(self, filter_expr: str) -> str:
        """
        Optimize a filter expression for better performance.
        
        Args:
            filter_expr: Original filter expression
            
        Returns:
            Optimized filter expression
        """
        # Remove unnecessary parentheses
        optimized = re.sub(r'\(\s*([^()]+)\s*\)', r'\1', filter_expr)
        
        # Simplify redundant conditions
        optimized = re.sub(r'(\w+\s+eq\s+\'[^\']+\')\s+and\s+\1', r'\1', optimized)
        
        # Move more selective conditions first (heuristic)
        # This is a simplified optimization - in practice, you'd analyze your data
        
        return optimized
    
    def validate_filter_syntax(self, filter_expr: str) -> Dict[str, Any]:
        """
        Validate filter expression syntax.
        
        Args:
            filter_expr: Filter expression to validate
            
        Returns:
            Validation results
        """
        issues = []
        warnings = []
        
        # Check for common syntax issues
        if filter_expr.count('(') != filter_expr.count(')'):
            issues.append("Mismatched parentheses")
        
        # Check for proper quoting
        if filter_expr.count("'") % 2 != 0:
            issues.append("Unmatched quotes")
        
        # Check for valid operators
        invalid_operators = re.findall(r'\s+(\w+)\s+', filter_expr)
        valid_ops = ['eq', 'ne', 'gt', 'ge', 'lt', 'le', 'and', 'or', 'not']
        for op in invalid_operators:
            if op not in valid_ops and not op.endswith('/any') and not op.endswith('/all'):
                warnings.append(f"Potentially invalid operator: {op}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'complexity_score': self._calculate_complexity(filter_expr)
        }
    
    def _calculate_complexity(self, filter_expr: str) -> int:
        """Calculate complexity score for a filter expression."""
        score = 0
        score += filter_expr.count('and') * 1
        score += filter_expr.count('or') * 2
        score += filter_expr.count('/any') * 3
        score += filter_expr.count('/all') * 4
        score += filter_expr.count('(') * 1
        return score
    
    def search_with_complex_filter(self, filter_expr: str, search_text: str = "*",
                                 top: int = 10, include_facets: bool = False) -> Dict:
        """
        Execute a search with complex filter.
        
        Args:
            filter_expr: Complex filter expression
            search_text: Search query text
            top: Number of results to return
            include_facets: Whether to include facets
            
        Returns:
            Search results dictionary
        """
        try:
            # Validate filter first
            validation = self.validate_filter_syntax(filter_expr)
            if not validation['is_valid']:
                return {'error': f"Invalid filter: {validation['issues']}"}
            
            print(f"🔍 Executing complex search...")
            print(f"   Filter: {filter_expr}")
            print(f"   Complexity Score: {validation['complexity_score']}")
            
            start_time = time.time()
            
            search_params = {
                'search_text': search_text,
                'filter': filter_expr,
                'top': top,
                'include_total_count': True
            }
            
            if include_facets:
                search_params['facets'] = ['category', 'tags', 'rating']
            
            results = self.search_client.search(**search_params)
            
            execution_time = time.time() - start_time
            
            # Process results
            documents = list(results)
            total_count = results.get_count()
            facets = results.get_facets() if include_facets else None
            
            return {
                'documents': documents,
                'total_count': total_count,
                'execution_time': execution_time,
                'filter': filter_expr,
                'validation': validation,
                'facets': facets
            }
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {'error': str(e)}
    
    def demonstrate_complex_filters(self):
        """Demonstrate various complex filtering scenarios."""
        print("🎯 Complex Filters Demonstration")
        print("=" * 50)
        
        examples = [
            {
                'name': 'Collection Any Filter',
                'filter': "tags/any(item: item eq 'premium') and rating ge 4.0",
                'description': 'Items with premium tag and rating >= 4.0'
            },
            {
                'name': 'Collection All Filter',
                'filter': "features/all(item: item eq 'available') and price le 100",
                'description': 'Items where all features are available and price <= 100'
            },
            {
                'name': 'Multi-Collection Filter',
                'filter': "tags/any(item: item eq 'new') and categories/any(item: item eq 'electronics')",
                'description': 'Items with new tag in electronics category'
            },
            {
                'name': 'Complex Nested Filter',
                'filter': "(tags/any(item: contains(item, 'special')) or rating gt 4.5) and (price ge 50 and price le 200)",
                'description': 'Special items or high-rated items in price range 50-200'
            },
            {
                'name': 'Geographic + Collection Filter',
                'filter': "geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 10 and amenities/any(item: item eq 'parking')",
                'description': 'Locations within 10km of Seattle with parking'
            }
        ]
        
        for example in examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            # Validate the filter
            validation = self.validate_filter_syntax(example['filter'])
            print(f"   Complexity Score: {validation['complexity_score']}")
            if validation['warnings']:
                print(f"   Warnings: {', '.join(validation['warnings'])}")
    
    def show_optimization_tips(self):
        """Display complex filter optimization tips."""
        print("\n🚀 Complex Filter Optimization Tips:")
        print("=" * 45)
        
        tips = [
            "Place most selective conditions first to reduce processing",
            "Use 'any()' instead of 'all()' when possible - it's more efficient",
            "Avoid deep nesting - flatten conditions when possible",
            "Combine range filters before collection filters",
            "Use field-specific indexes for frequently filtered collections",
            "Consider faceted navigation instead of complex OR conditions",
            "Cache complex filter results when appropriate",
            "Monitor query performance and adjust based on usage patterns",
            "Use search.score() to boost relevant results instead of complex filters",
            "Test filter selectivity with your actual data"
        ]
        
        for i, tip in enumerate(tips, 1):
            print(f"{i:2d}. {tip}")
    
    def analyze_filter_performance(self, filters: List[str]):
        """Analyze performance characteristics of different filters."""
        print("\n⚡ Filter Performance Analysis")
        print("=" * 35)
        
        print(f"{'Filter Type':<25} {'Complexity':<12} {'Performance':<15}")
        print("-" * 55)
        
        for filter_expr in filters:
            validation = self.validate_filter_syntax(filter_expr)
            complexity = validation['complexity_score']
            
            # Performance estimation based on complexity
            if complexity <= 5:
                performance = "Excellent"
            elif complexity <= 10:
                performance = "Good"
            elif complexity <= 20:
                performance = "Fair"
            else:
                performance = "Needs optimization"
            
            # Truncate long filters for display
            display_filter = filter_expr[:20] + "..." if len(filter_expr) > 20 else filter_expr
            
            print(f"{display_filter:<25} {complexity:<12} {performance:<15}")

def main():
    """Main demonstration function."""
    try:
        # Initialize the complex filter builder
        filter_builder = ComplexFilterBuilder()
        
        # Demonstrate complex filters
        filter_builder.demonstrate_complex_filters()
        
        # Show optimization tips
        filter_builder.show_optimization_tips()
        
        # Performance analysis with sample filters
        sample_filters = [
            "rating ge 4.0",
            "tags/any(item: item eq 'premium')",
            "tags/any(item: item eq 'new') and price le 100",
            "(tags/any(item: contains(item, 'special')) or rating gt 4.5) and (price ge 50 and price le 200)",
            "geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 10 and amenities/any(item: item eq 'parking') and features/all(item: item eq 'available')"
        ]
        
        filter_builder.analyze_filter_performance(sample_filters)
        
        # Example of building a complex filter programmatically
        print("\n🔧 Programmatic Filter Building Example:")
        print("=" * 45)
        
        # Create filter conditions
        conditions = [
            FilterCondition('tags', 'eq', 'premium', 'any'),
            FilterCondition('rating', 'ge', 4.0),
            FilterCondition('price', 'le', 200)
        ]
        
        complex_filter = filter_builder.build_nested_filter(conditions, 'and')
        print(f"Generated Filter: {complex_filter}")
        
        # Validate the generated filter
        validation = filter_builder.validate_filter_syntax(complex_filter)
        print(f"Validation: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
        print(f"Complexity Score: {validation['complexity_score']}")
        
        print("\n✅ Complex filters demonstration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()