"""
String Filters Example

This example demonstrates string-based filtering operations in Azure AI Search,
including text matching functions, case sensitivity, and pattern matching.
"""

import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class StringFiltersExample:
    def __init__(self):
        self.validate_configuration()
        
        # Initialize search client
        credential = AzureKeyCredential(os.getenv('SEARCH_API_KEY'))
        self.search_client = SearchClient(
            endpoint=os.getenv('SEARCH_ENDPOINT'),
            index_name=os.getenv('INDEX_NAME'),
            credential=credential
        )
    
    def validate_configuration(self):
        """Validate required environment variables"""
        required_vars = ['SEARCH_ENDPOINT', 'SEARCH_API_KEY', 'INDEX_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Configuration validated")
        print(f"📍 Search Endpoint: {os.getenv('SEARCH_ENDPOINT')}")
        print(f"📊 Index Name: {os.getenv('INDEX_NAME')}")
    
    def demonstrate_string_functions(self):
        """Demonstrate string matching functions"""
        print("\n🔤 String Matching Functions")
        print("=" * 40)
        
        string_examples = [
            {
                'name': 'Starts with "iPhone"',
                'filter': "startswith(name, 'iPhone')",
                'description': 'Find products whose name starts with "iPhone"'
            },
            {
                'name': 'Ends with "Pro"',
                'filter': "endswith(name, 'Pro')",
                'description': 'Find products whose name ends with "Pro"'
            },
            {
                'name': 'Contains "wireless"',
                'filter': "contains(description, 'wireless')",
                'description': 'Find products with "wireless" in description'
            },
            {
                'name': 'Contains "bluetooth" (case insensitive)',
                'filter': "contains(tolower(description), 'bluetooth')",
                'description': 'Case-insensitive search for "bluetooth"'
            }
        ]
        
        for example in string_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                start_time = time.time()
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'description', 'category', 'brand']
                )
                
                result_list = list(results)
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
                print(f"   Results: {len(result_list)} items found ({duration:.2f}ms)")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    description = result.get('description', 'N/A')
                    category = result.get('category', 'N/A')
                    brand = result.get('brand', 'N/A')
                    
                    # Truncate description for display
                    if len(description) > 50:
                        description = description[:50] + "..."
                    
                    print(f"     {i}. {name} ({brand}) - {category}")
                    print(f"        Description: {description}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_brand_filtering(self):
        """Demonstrate brand-based filtering"""
        print("\n🏷️ Brand Filtering")
        print("=" * 40)
        
        brand_examples = [
            {
                'name': 'Apple products',
                'filter': "brand eq 'Apple'",
                'description': 'Find all Apple products'
            },
            {
                'name': 'Samsung or LG',
                'filter': "brand eq 'Samsung' or brand eq 'LG'",
                'description': 'Find Samsung or LG products'
            },
            {
                'name': 'Brands starting with "S"',
                'filter': "startswith(brand, 'S')",
                'description': 'Find brands that start with "S"'
            },
            {
                'name': 'Premium brands',
                'filter': "brand eq 'Apple' or brand eq 'Samsung' or brand eq 'Sony'",
                'description': 'Find products from premium brands'
            }
        ]
        
        for example in brand_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'brand', 'category', 'price']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    brand = result.get('brand', 'N/A')
                    category = result.get('category', 'N/A')
                    price = result.get('price', 'N/A')
                    print(f"     {i}. {name} ({brand}) - {category} - ${price}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_text_search_builder(self):
        """Demonstrate dynamic text filter building"""
        print("\n🔧 Dynamic Text Filter Builder")
        print("=" * 40)
        
        def build_text_filter(field, search_term, match_type='contains', case_sensitive=True):
            """Build text filter with various matching options"""
            if not search_term:
                return None
            
            # Escape single quotes in search term
            escaped_term = search_term.replace("'", "''")
            
            # Apply case sensitivity
            if not case_sensitive:
                field = f"tolower({field})"
                escaped_term = escaped_term.lower()
            
            # Build filter based on match type
            if match_type == 'exact':
                return f"{field} eq '{escaped_term}'"
            elif match_type == 'startswith':
                return f"startswith({field}, '{escaped_term}')"
            elif match_type == 'endswith':
                return f"endswith({field}, '{escaped_term}')"
            elif match_type == 'contains':
                return f"contains({field}, '{escaped_term}')"
            else:
                raise ValueError(f"Unknown match type: {match_type}")
        
        # Test different text filter scenarios
        text_scenarios = [
            {
                'name': 'Exact brand match',
                'params': {'field': 'brand', 'search_term': 'Apple', 'match_type': 'exact'}
            },
            {
                'name': 'Product name starts with',
                'params': {'field': 'name', 'search_term': 'iPhone', 'match_type': 'startswith'}
            },
            {
                'name': 'Description contains (case insensitive)',
                'params': {'field': 'description', 'search_term': 'WIRELESS', 'match_type': 'contains', 'case_sensitive': False}
            },
            {
                'name': 'Model ends with',
                'params': {'field': 'model', 'search_term': 'Pro', 'match_type': 'endswith'}
            }
        ]
        
        for scenario in text_scenarios:
            print(f"\n📋 {scenario['name']}")
            filter_expr = build_text_filter(**scenario['params'])
            print(f"   Generated Filter: {filter_expr}")
            print(f"   Parameters: {scenario['params']}")
            
            if filter_expr:
                try:
                    results = self.search_client.search(
                        search_text="*",
                        filter=filter_expr,
                        top=2,
                        select=['id', 'name', 'brand', 'model', 'description']
                    )
                    
                    result_list = list(results)
                    print(f"   Results: {len(result_list)} items found")
                    
                    for i, result in enumerate(result_list, 1):
                        name = result.get('name', 'N/A')
                        brand = result.get('brand', 'N/A')
                        model = result.get('model', 'N/A')
                        print(f"     {i}. {name} ({brand} {model})")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
    
    def demonstrate_pattern_matching(self):
        """Demonstrate pattern matching techniques"""
        print("\n🎯 Pattern Matching Techniques")
        print("=" * 40)
        
        pattern_examples = [
            {
                'name': 'Product codes starting with "SKU"',
                'filter': "startswith(productCode, 'SKU')",
                'description': 'Find products with SKU codes'
            },
            {
                'name': 'Email domains',
                'filter': "endswith(contactEmail, '@company.com')",
                'description': 'Find items with company email addresses'
            },
            {
                'name': 'Version numbers',
                'filter': "contains(version, 'v2.')",
                'description': 'Find version 2.x products'
            },
            {
                'name': 'Model numbers with pattern',
                'filter': "startswith(model, 'MB') and endswith(model, 'Pro')",
                'description': 'Find models starting with "MB" and ending with "Pro"'
            }
        ]
        
        for example in pattern_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'productCode', 'model', 'version', 'contactEmail']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    product_code = result.get('productCode', 'N/A')
                    model = result.get('model', 'N/A')
                    version = result.get('version', 'N/A')
                    print(f"     {i}. {name} - Code: {product_code} - Model: {model} - Version: {version}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_multilingual_filtering(self):
        """Demonstrate multilingual text filtering"""
        print("\n🌍 Multilingual Text Filtering")
        print("=" * 40)
        
        multilingual_examples = [
            {
                'name': 'Case-insensitive search',
                'filter': "contains(tolower(name), 'iphone')",
                'description': 'Find "iPhone" regardless of case'
            },
            {
                'name': 'Multiple language terms',
                'filter': "contains(description, 'phone') or contains(description, 'téléphone')",
                'description': 'Find phone in English or French'
            },
            {
                'name': 'Unicode text search',
                'filter': "contains(name, 'café')",
                'description': 'Search for Unicode characters'
            }
        ]
        
        for example in multilingual_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=2,
                    select=['id', 'name', 'description', 'language']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list, 1):
                    name = result.get('name', 'N/A')
                    description = result.get('description', 'N/A')
                    language = result.get('language', 'N/A')
                    
                    # Truncate description
                    if len(description) > 40:
                        description = description[:40] + "..."
                    
                    print(f"     {i}. {name} ({language}) - {description}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_performance_comparison(self):
        """Compare performance of different string filter approaches"""
        print("\n⚡ String Filter Performance Comparison")
        print("=" * 40)
        
        def time_string_filter(filter_expr, description):
            """Time a string filter execution"""
            start_time = time.time()
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=filter_expr,
                    top=50,
                    select=['id', 'name']
                )
                
                result_list = list(results)
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
                return {
                    'success': True,
                    'duration': duration,
                    'count': len(result_list),
                    'description': description
                }
            except Exception as e:
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
                return {
                    'success': False,
                    'duration': duration,
                    'error': str(e),
                    'description': description
                }
        
        # Compare different string filter approaches
        performance_tests = [
            {
                'filter': "brand eq 'Apple'",
                'description': 'Exact match (most efficient)'
            },
            {
                'filter': "startswith(name, 'iPhone')",
                'description': 'Starts with function'
            },
            {
                'filter': "contains(name, 'Pro')",
                'description': 'Contains function'
            },
            {
                'filter': "contains(tolower(name), 'pro')",
                'description': 'Case-insensitive contains'
            },
            {
                'filter': "contains(description, 'wireless')",
                'description': 'Contains in long text field'
            }
        ]
        
        print("\n   Performance Test Results:")
        results = []
        
        for test in performance_tests:
            result = time_string_filter(test['filter'], test['description'])
            results.append(result)
            
            if result['success']:
                print(f"   ✅ {result['description']}")
                print(f"      Duration: {result['duration']:.2f}ms, Results: {result['count']}")
            else:
                print(f"   ❌ {result['description']}")
                print(f"      Error: {result['error']}")
        
        # Find best performing approach
        successful_results = [r for r in results if r['success']]
        if successful_results:
            best_result = min(successful_results, key=lambda x: x['duration'])
            print(f"\n   🏆 Best Performance: {best_result['description']}")
            print(f"      Duration: {best_result['duration']:.2f}ms")
    
    def demonstrate_advanced_text_scenarios(self):
        """Demonstrate advanced text filtering scenarios"""
        print("\n🎯 Advanced Text Filtering Scenarios")
        print("=" * 40)
        
        # Product search with multiple text criteria
        print("\n1. Multi-field Text Search")
        multi_field_filter = "contains(name, 'Pro') or contains(description, 'Professional')"
        print(f"   Filter: {multi_field_filter}")
        print("   Use case: Find 'Pro' products by name or description")
        
        try:
            results = self.search_client.search(
                search_text="*",
                filter=multi_field_filter,
                top=3,
                select=['id', 'name', 'description']
            )
            
            result_list = list(results)
            print(f"   Results: {len(result_list)} items found")
            
            for i, result in enumerate(result_list[:2], 1):
                name = result.get('name', 'N/A')
                description = result.get('description', 'N/A')
                if len(description) > 50:
                    description = description[:50] + "..."
                print(f"     {i}. {name}")
                print(f"        {description}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Category and brand combination
        print("\n2. Category and Brand Text Filtering")
        category_brand_filter = "startswith(category, 'Elect') and contains(brand, 'Sam')"
        print(f"   Filter: {category_brand_filter}")
        print("   Use case: Electronics category with Samsung brand")
        
        try:
            results = self.search_client.search(
                search_text="*",
                filter=category_brand_filter,
                top=2,
                select=['id', 'name', 'category', 'brand']
            )
            
            result_list = list(results)
            print(f"   Results: {len(result_list)} items found")
            
            for i, result in enumerate(result_list, 1):
                name = result.get('name', 'N/A')
                category = result.get('category', 'N/A')
                brand = result.get('brand', 'N/A')
                print(f"     {i}. {name} ({brand}) - {category}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def demonstrate_best_practices(self):
        """Demonstrate string filtering best practices"""
        print("\n💡 String Filtering Best Practices")
        print("=" * 40)
        
        print("\n1. Choose the right string function:")
        print("   ✅ Use 'eq' for exact matches (fastest)")
        print("   ✅ Use 'startswith' for prefix searches")
        print("   ✅ Use 'contains' for substring searches")
        print("   ✅ Use 'endswith' for suffix searches")
        
        print("\n2. Handle case sensitivity appropriately:")
        print("   ✅ Use 'tolower()' for case-insensitive searches")
        print("   ✅ Consider user expectations for case sensitivity")
        print("   ✅ Be consistent across your application")
        
        print("\n3. Escape special characters:")
        print("   ✅ Replace single quotes with double quotes: ' -> ''")
        print("   ✅ Validate user input before building filters")
        print("   ✅ Use parameterized filter building functions")
        
        print("\n4. Performance considerations:")
        print("   ✅ Exact matches (eq) are fastest")
        print("   ✅ Prefix searches (startswith) are faster than contains")
        print("   ✅ Avoid case conversion on large text fields when possible")
        print("   ✅ Combine text filters with more selective filters")
        
        print("\n5. User experience:")
        print("   ✅ Provide search suggestions and auto-complete")
        print("   ✅ Handle typos and variations gracefully")
        print("   ✅ Show clear feedback for no results")
        print("   ✅ Consider fuzzy matching for better user experience")
    
    def run(self):
        """Run all string filter examples"""
        print("🚀 String Filters Example")
        print("=" * 50)
        
        try:
            self.demonstrate_string_functions()
            self.demonstrate_brand_filtering()
            self.demonstrate_text_search_builder()
            self.demonstrate_pattern_matching()
            self.demonstrate_multilingual_filtering()
            self.demonstrate_performance_comparison()
            self.demonstrate_advanced_text_scenarios()
            self.demonstrate_best_practices()
            
            print("\n✅ String filters example completed successfully!")
            print("\nKey takeaways:")
            print("- Use appropriate string functions for different matching needs")
            print("- Handle case sensitivity based on user expectations")
            print("- Escape special characters in user input")
            print("- Consider performance implications of different string operations")
            print("- Combine text filters with other filter types for better performance")
            
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            raise

def main():
    example = StringFiltersExample()
    try:
        example.run()
    except Exception as e:
        print(f"Application failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()