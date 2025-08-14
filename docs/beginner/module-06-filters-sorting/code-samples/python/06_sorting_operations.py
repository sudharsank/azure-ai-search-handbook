"""
Sorting Operations Example

This example demonstrates various sorting strategies in Azure AI Search,
including single-field sorting, multi-field sorting, and performance optimization.
"""

import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class SortingOperationsExample:
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
    
    def demonstrate_basic_sorting(self):
        """Demonstrate basic single-field sorting"""
        print("\n📊 Basic Single-Field Sorting")
        print("=" * 40)
        
        sorting_examples = [
            {
                'name': 'Price: Low to High',
                'order_by': ['price asc'],
                'description': 'Sort products by price in ascending order'
            },
            {
                'name': 'Price: High to Low',
                'order_by': ['price desc'],
                'description': 'Sort products by price in descending order'
            },
            {
                'name': 'Rating: Highest First',
                'order_by': ['rating desc'],
                'description': 'Sort products by rating in descending order'
            },
            {
                'name': 'Name: Alphabetical',
                'order_by': ['name asc'],
                'description': 'Sort products alphabetically by name'
            },
            {
                'name': 'Date: Newest First',
                'order_by': ['createdDate desc'],
                'description': 'Sort products by creation date, newest first'
            }
        ]
        
        for example in sorting_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Order By: {example['order_by']}")
            
            try:
                start_time = time.time()
                results = self.search_client.search(
                    search_text="*",
                    order_by=example['order_by'],
                    top=5,
                    select=['id', 'name', 'price', 'rating', 'createdDate', 'category']
                )
                
                result_list = list(results)
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
                print(f"   Results: {len(result_list)} items ({duration:.2f}ms)")
                
                for i, result in enumerate(result_list[:3], 1):
                    name = result.get('name', 'N/A')
                    price = result.get('price', 'N/A')
                    rating = result.get('rating', 'N/A')
                    created = result.get('createdDate', 'N/A')
                    category = result.get('category', 'N/A')
                    
                    # Format date for display
                    if created != 'N/A' and isinstance(created, str):
                        try:
                            from datetime import datetime
                            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            created = created_dt.strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    print(f"     {i}. {name} ({category})")
                    print(f"        Price: ${price}, Rating: {rating}⭐, Created: {created}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_multi_field_sorting(self):
        """Demonstrate multi-field sorting strategies"""
        print("\n🔗 Multi-Field Sorting")
        print("=" * 40)
        
        multi_sort_examples = [
            {
                'name': 'Category, then Rating',
                'order_by': ['category asc', 'rating desc'],
                'description': 'Group by category, then sort by rating within each category'
            },
            {
                'name': 'Rating, then Price',
                'order_by': ['rating desc', 'price asc'],
                'description': 'Sort by rating first, then by price for same ratings'
            },
            {
                'name': 'Brand, Category, Price',
                'order_by': ['brand asc', 'category asc', 'price asc'],
                'description': 'Three-level sorting: brand, category, then price'
            },
            {
                'name': 'In Stock, then Rating',
                'order_by': ['inStock desc', 'rating desc'],
                'description': 'Show in-stock items first, then sort by rating'
            },
            {
                'name': 'Price Range, then Name',
                'order_by': ['price desc', 'name asc'],
                'description': 'Sort by price descending, then alphabetically'
            }
        ]
        
        for example in multi_sort_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Order By: {example['order_by']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    order_by=example['order_by'],
                    top=5,
                    select=['id', 'name', 'brand', 'category', 'price', 'rating', 'inStock']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items")
                
                for i, result in enumerate(result_list[:3], 1):
                    name = result.get('name', 'N/A')
                    brand = result.get('brand', 'N/A')
                    category = result.get('category', 'N/A')
                    price = result.get('price', 'N/A')
                    rating = result.get('rating', 'N/A')
                    in_stock = result.get('inStock', 'N/A')
                    
                    stock_indicator = '✅' if in_stock else '❌'
                    print(f"     {i}. {name} ({brand})")
                    print(f"        {category} - ${price} - {rating}⭐ - {stock_indicator}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_sort_builder(self):
        """Demonstrate dynamic sort order building"""
        print("\n🔧 Dynamic Sort Builder")
        print("=" * 40)
        
        class SortBuilder:
            def __init__(self):
                self.sort_fields = []
            
            def add_field(self, field, direction='asc'):
                """Add a field to the sort order"""
                if direction.lower() not in ['asc', 'desc']:
                    raise ValueError("Direction must be 'asc' or 'desc'")
                
                self.sort_fields.append(f"{field} {direction}")
                return self
            
            def add_price_sort(self, direction='asc'):
                """Add price sorting"""
                return self.add_field('price', direction)
            
            def add_rating_sort(self, direction='desc'):
                """Add rating sorting"""
                return self.add_field('rating', direction)
            
            def add_date_sort(self, field='createdDate', direction='desc'):
                """Add date sorting"""
                return self.add_field(field, direction)
            
            def add_name_sort(self, direction='asc'):
                """Add name sorting"""
                return self.add_field('name', direction)
            
            def add_category_sort(self, direction='asc'):
                """Add category sorting"""
                return self.add_field('category', direction)
            
            def build(self):
                """Build the sort order list"""
                return self.sort_fields if self.sort_fields else None
            
            def clear(self):
                """Clear all sort fields"""
                self.sort_fields = []
                return self
        
        # Test different sort combinations
        sort_scenarios = [
            {
                'name': 'E-commerce: Best Value',
                'builder_calls': lambda sb: sb.add_rating_sort('desc').add_price_sort('asc')
            },
            {
                'name': 'Catalog: Organized Browse',
                'builder_calls': lambda sb: sb.add_category_sort('asc').add_name_sort('asc')
            },
            {
                'name': 'Premium First',
                'builder_calls': lambda sb: sb.add_price_sort('desc').add_rating_sort('desc')
            },
            {
                'name': 'Latest and Greatest',
                'builder_calls': lambda sb: sb.add_date_sort('createdDate', 'desc').add_rating_sort('desc')
            }
        ]
        
        for scenario in sort_scenarios:
            print(f"\n📋 {scenario['name']}")
            
            # Build sort order
            sort_builder = SortBuilder()
            scenario['builder_calls'](sort_builder)
            sort_order = sort_builder.build()
            
            print(f"   Generated Sort Order: {sort_order}")
            
            if sort_order:
                try:
                    results = self.search_client.search(
                        search_text="*",
                        order_by=sort_order,
                        top=3,
                        select=['id', 'name', 'category', 'price', 'rating', 'createdDate']
                    )
                    
                    result_list = list(results)
                    print(f"   Results: {len(result_list)} items")
                    
                    for i, result in enumerate(result_list, 1):
                        name = result.get('name', 'N/A')
                        category = result.get('category', 'N/A')
                        price = result.get('price', 'N/A')
                        rating = result.get('rating', 'N/A')
                        print(f"     {i}. {name} ({category}) - ${price} - {rating}⭐")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
    
    def demonstrate_geographic_sorting(self):
        """Demonstrate geographic distance sorting"""
        print("\n🌍 Geographic Distance Sorting")
        print("=" * 40)
        
        # Example coordinates (Seattle, WA)
        user_location = "geography'POINT(-122.3321 47.6062)'"
        
        geographic_examples = [
            {
                'name': 'Nearest Locations',
                'order_by': [f'geo.distance(location, {user_location})'],
                'description': 'Sort by distance from user location (closest first)'
            },
            {
                'name': 'Distance + Rating',
                'order_by': [f'geo.distance(location, {user_location})', 'rating desc'],
                'description': 'Sort by distance, then by rating for same distance'
            },
            {
                'name': 'Rating + Distance',
                'order_by': ['rating desc', f'geo.distance(location, {user_location})'],
                'description': 'Sort by rating first, then by distance'
            }
        ]
        
        for example in geographic_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Order By: {example['order_by']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    order_by=example['order_by'],
                    top=3,
                    select=['id', 'name', 'location', 'rating', 'address']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items")
                
                for i, result in enumerate(result_list, 1):
                    name = result.get('name', 'N/A')
                    rating = result.get('rating', 'N/A')
                    address = result.get('address', 'N/A')
                    location = result.get('location', 'N/A')
                    
                    # Format location for display
                    location_str = 'N/A'
                    if location and isinstance(location, dict):
                        coordinates = location.get('coordinates', [])
                        if len(coordinates) >= 2:
                            location_str = f"({coordinates[1]:.4f}, {coordinates[0]:.4f})"
                    
                    print(f"     {i}. {name} - {rating}⭐")
                    print(f"        Location: {location_str} - {address}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_sort_performance(self):
        """Analyze sorting performance"""
        print("\n⚡ Sort Performance Analysis")
        print("=" * 40)
        
        def time_sort_operation(order_by, description):
            """Time a sort operation"""
            start_time = time.time()
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    order_by=order_by,
                    top=100,
                    select=['id', 'name', 'price', 'rating']
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
        
        # Compare different sorting approaches
        performance_tests = [
            {
                'order_by': None,
                'description': 'No sorting (relevance)'
            },
            {
                'order_by': ['price asc'],
                'description': 'Single field: Price'
            },
            {
                'order_by': ['rating desc'],
                'description': 'Single field: Rating'
            },
            {
                'order_by': ['name asc'],
                'description': 'Single field: Name (string)'
            },
            {
                'order_by': ['price asc', 'rating desc'],
                'description': 'Two fields: Price + Rating'
            },
            {
                'order_by': ['category asc', 'price asc', 'rating desc'],
                'description': 'Three fields: Category + Price + Rating'
            }
        ]
        
        print("\n   Performance Test Results:")
        results = []
        
        for test in performance_tests:
            result = time_sort_operation(test['order_by'], test['description'])
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
            fastest = min(successful_results, key=lambda x: x['duration'])
            slowest = max(successful_results, key=lambda x: x['duration'])
            
            print(f"\n   🏆 Fastest: {fastest['description']} ({fastest['duration']:.2f}ms)")
            print(f"   🐌 Slowest: {slowest['description']} ({slowest['duration']:.2f}ms)")
            
            if fastest['duration'] > 0 and slowest['duration'] > 0:
                performance_ratio = slowest['duration'] / fastest['duration']
                print(f"   📊 Performance Ratio: {performance_ratio:.1f}x difference")
    
    def demonstrate_sort_with_filters(self):
        """Demonstrate sorting combined with filtering"""
        print("\n🔗 Sorting with Filters")
        print("=" * 40)
        
        filter_sort_examples = [
            {
                'name': 'Electronics by Price',
                'filter': "category eq 'Electronics'",
                'order_by': ['price asc'],
                'description': 'Electronics products sorted by price'
            },
            {
                'name': 'High-rated items by Price',
                'filter': "rating ge 4.0",
                'order_by': ['price asc'],
                'description': 'High-rated products sorted by price'
            },
            {
                'name': 'In-stock Premium items',
                'filter': "inStock eq true and price ge 500",
                'order_by': ['rating desc', 'price desc'],
                'description': 'Premium in-stock items by rating and price'
            },
            {
                'name': 'Recent items by Rating',
                'filter': "createdDate ge 2024-01-01T00:00:00Z",
                'order_by': ['rating desc', 'createdDate desc'],
                'description': 'Recent items sorted by rating and date'
            }
        ]
        
        for example in filter_sort_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            print(f"   Order By: {example['order_by']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    order_by=example['order_by'],
                    top=3,
                    select=['id', 'name', 'category', 'price', 'rating', 'inStock', 'createdDate']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items")
                
                for i, result in enumerate(result_list, 1):
                    name = result.get('name', 'N/A')
                    category = result.get('category', 'N/A')
                    price = result.get('price', 'N/A')
                    rating = result.get('rating', 'N/A')
                    in_stock = result.get('inStock', 'N/A')
                    
                    stock_indicator = '✅' if in_stock else '❌'
                    print(f"     {i}. {name} ({category})")
                    print(f"        ${price} - {rating}⭐ - {stock_indicator}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_best_practices(self):
        """Demonstrate sorting best practices"""
        print("\n💡 Sorting Best Practices")
        print("=" * 40)
        
        print("\n1. Choose appropriate sort fields:")
        print("   ✅ Use numeric fields (price, rating) for fastest sorting")
        print("   ✅ Use date fields for chronological sorting")
        print("   ✅ Limit string field sorting when possible")
        print("   ✅ Ensure fields are marked as 'sortable' in index schema")
        
        print("\n2. Optimize sort order:")
        print("   ✅ Put most important sort criteria first")
        print("   ✅ Limit to 2-3 sort fields for best performance")
        print("   ✅ Use consistent sort directions when logical")
        print("   ✅ Consider user expectations and use cases")
        
        print("\n3. Combine with filters effectively:")
        print("   ✅ Apply filters before sorting for better performance")
        print("   ✅ Use selective filters to reduce result set size")
        print("   ✅ Consider filter + sort combinations for user experience")
        
        print("\n4. Performance considerations:")
        print("   ✅ Numeric sorts are faster than string sorts")
        print("   ✅ Single-field sorts are faster than multi-field sorts")
        print("   ✅ Consider caching for frequently used sort orders")
        print("   ✅ Monitor sort performance in production")
        
        print("\n5. User experience:")
        print("   ✅ Provide clear sort option labels")
        print("   ✅ Show current sort order to users")
        print("   ✅ Remember user sort preferences")
        print("   ✅ Provide sensible default sort orders")
    
    def run(self):
        """Run all sorting operation examples"""
        print("🚀 Sorting Operations Example")
        print("=" * 50)
        
        try:
            self.demonstrate_basic_sorting()
            self.demonstrate_multi_field_sorting()
            self.demonstrate_sort_builder()
            self.demonstrate_geographic_sorting()
            self.demonstrate_sort_performance()
            self.demonstrate_sort_with_filters()
            self.demonstrate_best_practices()
            
            print("\n✅ Sorting operations example completed successfully!")
            print("\nKey takeaways:")
            print("- Use appropriate sort fields based on data types and performance")
            print("- Combine multiple sort criteria for better user experience")
            print("- Build dynamic sort orders with reusable utilities")
            print("- Consider geographic sorting for location-based applications")
            print("- Monitor and optimize sort performance for production use")
            
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            raise

def main():
    example = SortingOperationsExample()
    try:
        example.run()
    except Exception as e:
        print(f"Application failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()