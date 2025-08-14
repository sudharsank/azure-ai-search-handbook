"""
Range Filters Example

This example demonstrates range filtering operations in Azure AI Search,
including numeric ranges, date ranges, and performance optimization techniques.
"""

import os
from datetime import datetime, timedelta
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class RangeFiltersExample:
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
    
    def demonstrate_numeric_ranges(self):
        """Demonstrate numeric range filtering"""
        print("\n🔢 Numeric Range Filters")
        print("=" * 40)
        
        numeric_examples = [
            {
                'name': 'Budget range ($10 - $50)',
                'filter': "price ge 10 and price le 50",
                'description': 'Find products in budget price range'
            },
            {
                'name': 'Mid-range ($50 - $200)',
                'filter': "price gt 50 and price lt 200",
                'description': 'Find mid-range priced products'
            },
            {
                'name': 'Premium ($200+)',
                'filter': "price ge 200",
                'description': 'Find premium priced products'
            },
            {
                'name': 'Rating range (3.5 - 4.5)',
                'filter': "rating ge 3.5 and rating le 4.5",
                'description': 'Find moderately well-rated products'
            },
            {
                'name': 'Quantity in stock (10-100)',
                'filter': "quantityInStock ge 10 and quantityInStock le 100",
                'description': 'Find products with moderate stock levels'
            }
        ]
        
        for example in numeric_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                start_time = time.time()
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'price', 'rating', 'quantityInStock', 'category']
                )
                
                result_list = list(results)
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
                print(f"   Results: {len(result_list)} items found ({duration:.2f}ms)")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    price = result.get('price', 'N/A')
                    rating = result.get('rating', 'N/A')
                    quantity = result.get('quantityInStock', 'N/A')
                    category = result.get('category', 'N/A')
                    print(f"     {i}. {name} ({category}) - ${price} - {rating}⭐ - Qty: {quantity}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_date_ranges(self):
        """Demonstrate date range filtering"""
        print("\n📅 Date Range Filters")
        print("=" * 40)
        
        # Calculate relative dates
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        last_year = now - timedelta(days=365)
        
        # Format dates for OData (ISO 8601)
        now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_week_str = last_week.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_month_str = last_month.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_year_str = last_year.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        date_examples = [
            {
                'name': 'Items added last week',
                'filter': f"createdDate ge {last_week_str}",
                'description': 'Find recently added items (last 7 days)'
            },
            {
                'name': 'Items modified last month',
                'filter': f"lastModified ge {last_month_str}",
                'description': 'Find recently updated items (last 30 days)'
            },
            {
                'name': 'Items from specific date range',
                'filter': f"createdDate ge {last_month_str} and createdDate le {last_week_str}",
                'description': 'Find items created between last month and last week'
            },
            {
                'name': 'Older items (before last year)',
                'filter': f"createdDate lt {last_year_str}",
                'description': 'Find items older than one year'
            }
        ]
        
        for example in date_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'createdDate', 'lastModified', 'category'],
                    order_by=['createdDate desc']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    created = result.get('createdDate', 'N/A')
                    modified = result.get('lastModified', 'N/A')
                    category = result.get('category', 'N/A')
                    
                    # Format dates for display
                    if created != 'N/A' and isinstance(created, str):
                        try:
                            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            created = created_dt.strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    print(f"     {i}. {name} ({category}) - Created: {created} - Modified: {modified}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_price_range_builder(self):
        """Demonstrate dynamic price range filter building"""
        print("\n💰 Dynamic Price Range Builder")
        print("=" * 40)
        
        def build_price_range_filter(min_price=None, max_price=None, currency='USD'):
            """Build price range filter with validation"""
            filters = []
            
            if min_price is not None:
                if min_price < 0:
                    raise ValueError("Minimum price cannot be negative")
                filters.append(f"price ge {min_price}")
            
            if max_price is not None:
                if max_price < 0:
                    raise ValueError("Maximum price cannot be negative")
                if min_price is not None and max_price < min_price:
                    raise ValueError("Maximum price cannot be less than minimum price")
                filters.append(f"price le {max_price}")
            
            # Add currency filter if specified
            if currency and currency != 'USD':
                filters.append(f"currency eq '{currency}'")
            
            return " and ".join(filters) if filters else None
        
        # Test different price ranges
        price_scenarios = [
            {'name': 'Under $25', 'max_price': 25},
            {'name': '$25 - $100', 'min_price': 25, 'max_price': 100},
            {'name': '$100 - $500', 'min_price': 100, 'max_price': 500},
            {'name': 'Over $500', 'min_price': 500},
            {'name': 'EUR products under €50', 'max_price': 50, 'currency': 'EUR'}
        ]
        
        for scenario in price_scenarios:
            print(f"\n📋 {scenario['name']}")
            
            try:
                filter_expr = build_price_range_filter(**{k: v for k, v in scenario.items() if k != 'name'})
                print(f"   Generated Filter: {filter_expr}")
                
                if filter_expr:
                    results = self.search_client.search(
                        search_text="*",
                        filter=filter_expr,
                        top=2,
                        select=['id', 'name', 'price', 'currency', 'category']
                    )
                    
                    result_list = list(results)
                    print(f"   Results: {len(result_list)} items found")
                    
                    for i, result in enumerate(result_list, 1):
                        name = result.get('name', 'N/A')
                        price = result.get('price', 'N/A')
                        currency = result.get('currency', 'USD')
                        category = result.get('category', 'N/A')
                        print(f"     {i}. {name} ({category}) - {currency} {price}")
                
            except ValueError as e:
                print(f"   ❌ Validation Error: {e}")
            except Exception as e:
                print(f"   ❌ Search Error: {e}")
    
    def demonstrate_performance_optimization(self):
        """Demonstrate range filter performance optimization"""
        print("\n⚡ Performance Optimization")
        print("=" * 40)
        
        def time_filter_query(filter_expr, description):
            """Time a filter query execution"""
            start_time = time.time()
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=filter_expr,
                    top=100,
                    select=['id', 'name', 'price']
                )
                
                # Materialize results to get accurate timing
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
        
        # Compare different filter approaches
        performance_tests = [
            {
                'filter': "price ge 50 and price le 200",
                'description': 'Optimized: Specific range filter'
            },
            {
                'filter': "price gt 0 and price ge 50 and price le 200",
                'description': 'Suboptimal: Redundant conditions'
            },
            {
                'filter': "price ge 50 and price le 200 and category ne null",
                'description': 'Good: Range + selective filter'
            },
            {
                'filter': "category ne null and price ge 50 and price le 200",
                'description': 'Better: Selective filter first'
            }
        ]
        
        print("\n   Performance Comparison:")
        results = []
        
        for test in performance_tests:
            result = time_filter_query(test['filter'], test['description'])
            results.append(result)
            
            if result['success']:
                print(f"   ✅ {result['description']}")
                print(f"      Duration: {result['duration']:.2f}ms, Results: {result['count']}")
            else:
                print(f"   ❌ {result['description']}")
                print(f"      Error: {result['error']}")
        
        # Find best performing query
        successful_results = [r for r in results if r['success']]
        if successful_results:
            best_result = min(successful_results, key=lambda x: x['duration'])
            print(f"\n   🏆 Best Performance: {best_result['description']}")
            print(f"      Duration: {best_result['duration']:.2f}ms")
    
    def demonstrate_advanced_ranges(self):
        """Demonstrate advanced range filtering techniques"""
        print("\n🎯 Advanced Range Techniques")
        print("=" * 40)
        
        # Overlapping ranges
        print("\n1. Overlapping Ranges")
        overlapping_filter = "(price ge 50 and price le 150) or (price ge 100 and price le 250)"
        print(f"   Filter: {overlapping_filter}")
        print("   Use case: Products in budget OR mid-range categories")
        
        try:
            results = self.search_client.search(
                search_text="*",
                filter=overlapping_filter,
                top=3,
                select=['id', 'name', 'price', 'category']
            )
            
            result_list = list(results)
            print(f"   Results: {len(result_list)} items found")
            
            for i, result in enumerate(result_list[:2], 1):
                name = result.get('name', 'N/A')
                price = result.get('price', 'N/A')
                category = result.get('category', 'N/A')
                print(f"     {i}. {name} ({category}) - ${price}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Exclusive ranges
        print("\n2. Exclusive Ranges")
        exclusive_filter = "price lt 50 or price gt 200"
        print(f"   Filter: {exclusive_filter}")
        print("   Use case: Avoid mid-range products")
        
        try:
            results = self.search_client.search(
                search_text="*",
                filter=exclusive_filter,
                top=3,
                select=['id', 'name', 'price', 'category']
            )
            
            result_list = list(results)
            print(f"   Results: {len(result_list)} items found")
            
            for i, result in enumerate(result_list[:2], 1):
                name = result.get('name', 'N/A')
                price = result.get('price', 'N/A')
                category = result.get('category', 'N/A')
                print(f"     {i}. {name} ({category}) - ${price}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Multi-field ranges
        print("\n3. Multi-field Ranges")
        multi_field_filter = "price ge 100 and price le 500 and rating ge 3.5 and rating le 4.5"
        print(f"   Filter: {multi_field_filter}")
        print("   Use case: Products in specific price AND rating ranges")
        
        try:
            results = self.search_client.search(
                search_text="*",
                filter=multi_field_filter,
                top=3,
                select=['id', 'name', 'price', 'rating', 'category']
            )
            
            result_list = list(results)
            print(f"   Results: {len(result_list)} items found")
            
            for i, result in enumerate(result_list[:2], 1):
                name = result.get('name', 'N/A')
                price = result.get('price', 'N/A')
                rating = result.get('rating', 'N/A')
                category = result.get('category', 'N/A')
                print(f"     {i}. {name} ({category}) - ${price} - {rating}⭐")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def demonstrate_best_practices(self):
        """Demonstrate range filter best practices"""
        print("\n💡 Range Filter Best Practices")
        print("=" * 40)
        
        print("\n1. Use appropriate operators for ranges:")
        print("   ✅ Inclusive range: price ge 100 and price le 200")
        print("   ✅ Exclusive range: price gt 100 and price lt 200")
        print("   ✅ Open-ended: price ge 100 (no upper limit)")
        
        print("\n2. Validate range parameters:")
        print("   ✅ Check min <= max")
        print("   ✅ Handle null/empty values")
        print("   ✅ Validate data types")
        
        print("\n3. Optimize for performance:")
        print("   ✅ Use most selective filters first")
        print("   ✅ Combine ranges with equality filters")
        print("   ✅ Avoid redundant conditions")
        
        print("\n4. Handle edge cases:")
        print("   ✅ Zero values: price gt 0")
        print("   ✅ Negative values: price ge 0")
        print("   ✅ Null values: price ne null and price ge 100")
        
        print("\n5. Date range considerations:")
        print("   ✅ Use ISO 8601 format: 2024-01-01T00:00:00Z")
        print("   ✅ Consider time zones")
        print("   ✅ Use UTC for consistency")
    
    def run(self):
        """Run all range filter examples"""
        print("🚀 Range Filters Example")
        print("=" * 50)
        
        try:
            self.demonstrate_numeric_ranges()
            self.demonstrate_date_ranges()
            self.demonstrate_price_range_builder()
            self.demonstrate_performance_optimization()
            self.demonstrate_advanced_ranges()
            self.demonstrate_best_practices()
            
            print("\n✅ Range filters example completed successfully!")
            print("\nKey takeaways:")
            print("- Use ge/le for inclusive ranges, gt/lt for exclusive ranges")
            print("- Format dates in ISO 8601 format for consistency")
            print("- Build dynamic filters with proper validation")
            print("- Optimize performance by using selective filters first")
            print("- Handle edge cases like null values and negative numbers")
            
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            raise

def main():
    example = RangeFiltersExample()
    try:
        example.run()
    except Exception as e:
        print(f"Application failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()