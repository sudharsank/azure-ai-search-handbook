"""
Basic Filters Example

This example demonstrates fundamental filtering operations in Azure AI Search,
including equality filters, comparison filters, and logical combinations.
"""

import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BasicFiltersExample:
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
    
    def demonstrate_equality_filters(self):
        """Demonstrate equality and inequality filters"""
        print("\n🔍 Equality Filters")
        print("=" * 40)
        
        # Equality filter examples
        filter_examples = [
            {
                'name': 'Category equals Electronics',
                'filter': "category eq 'Electronics'",
                'description': 'Find all products in Electronics category'
            },
            {
                'name': 'Status not discontinued',
                'filter': "status ne 'Discontinued'",
                'description': 'Find products that are not discontinued'
            },
            {
                'name': 'In stock items',
                'filter': "inStock eq true",
                'description': 'Find items that are currently in stock'
            },
            {
                'name': 'Out of stock items',
                'filter': "inStock eq false",
                'description': 'Find items that are out of stock'
            }
        ]
        
        for example in filter_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'category', 'status', 'inStock', 'price']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    category = result.get('category', 'N/A')
                    status = result.get('status', 'N/A')
                    in_stock = result.get('inStock', 'N/A')
                    price = result.get('price', 'N/A')
                    print(f"     {i}. {name} ({category}) - ${price} - {status} - Stock: {in_stock}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_comparison_filters(self):
        """Demonstrate comparison filters (gt, ge, lt, le)"""
        print("\n📊 Comparison Filters")
        print("=" * 40)
        
        comparison_examples = [
            {
                'name': 'Price greater than $100',
                'filter': "price gt 100",
                'description': 'Find products priced above $100'
            },
            {
                'name': 'Rating 4.0 or higher',
                'filter': "rating ge 4.0",
                'description': 'Find highly rated products (4+ stars)'
            },
            {
                'name': 'Price less than $50',
                'filter': "price lt 50",
                'description': 'Find budget-friendly products under $50'
            },
            {
                'name': 'Rating 3.0 or lower',
                'filter': "rating le 3.0",
                'description': 'Find lower-rated products (3 stars or less)'
            }
        ]
        
        for example in comparison_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'price', 'rating', 'category'],
                    order_by=['price asc'] if 'price' in example['filter'] else ['rating desc']
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
    
    def demonstrate_logical_combinations(self):
        """Demonstrate logical operators (and, or, not)"""
        print("\n🔗 Logical Combinations")
        print("=" * 40)
        
        logical_examples = [
            {
                'name': 'Electronics AND high rating',
                'filter': "category eq 'Electronics' and rating ge 4.0",
                'description': 'Find high-rated electronics products'
            },
            {
                'name': 'Budget OR Premium categories',
                'filter': "category eq 'Budget' or category eq 'Premium'",
                'description': 'Find products in Budget or Premium categories'
            },
            {
                'name': 'NOT discontinued items',
                'filter': "not (status eq 'Discontinued')",
                'description': 'Find all non-discontinued products'
            },
            {
                'name': 'Complex combination',
                'filter': "(category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.5)",
                'description': 'Find expensive electronics OR highly-rated books'
            }
        ]
        
        for example in logical_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'category', 'price', 'rating', 'status']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    category = result.get('category', 'N/A')
                    price = result.get('price', 'N/A')
                    rating = result.get('rating', 'N/A')
                    status = result.get('status', 'N/A')
                    print(f"     {i}. {name} ({category}) - ${price} - {rating}⭐ - {status}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_null_handling(self):
        """Demonstrate handling of null values in filters"""
        print("\n🚫 Null Value Handling")
        print("=" * 40)
        
        null_examples = [
            {
                'name': 'Items with rating',
                'filter': "rating ne null",
                'description': 'Find items that have a rating value'
            },
            {
                'name': 'Items without description',
                'filter': "description eq null",
                'description': 'Find items missing description'
            },
            {
                'name': 'Items with non-zero price',
                'filter': "price ne null and price gt 0",
                'description': 'Find items with valid pricing'
            }
        ]
        
        for example in null_examples:
            print(f"\n📋 {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Filter: {example['filter']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=example['filter'],
                    top=3,
                    select=['id', 'name', 'price', 'rating', 'description']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list[:2], 1):
                    name = result.get('name', 'N/A')
                    price = result.get('price', 'N/A')
                    rating = result.get('rating', 'N/A')
                    has_desc = 'Yes' if result.get('description') else 'No'
                    print(f"     {i}. {name} - ${price} - {rating}⭐ - Desc: {has_desc}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_filter_building(self):
        """Demonstrate dynamic filter building"""
        print("\n🔧 Dynamic Filter Building")
        print("=" * 40)
        
        def build_product_filter(category=None, min_price=None, max_price=None, 
                               min_rating=None, in_stock=None):
            """Build a product filter from parameters"""
            filters = []
            
            if category:
                filters.append(f"category eq '{category}'")
            
            if min_price is not None:
                filters.append(f"price ge {min_price}")
            
            if max_price is not None:
                filters.append(f"price le {max_price}")
            
            if min_rating is not None:
                filters.append(f"rating ge {min_rating}")
            
            if in_stock is not None:
                filters.append(f"inStock eq {str(in_stock).lower()}")
            
            return " and ".join(filters) if filters else None
        
        # Test different filter combinations
        filter_scenarios = [
            {
                'name': 'Electronics under $200',
                'params': {'category': 'Electronics', 'max_price': 200}
            },
            {
                'name': 'High-rated items in stock',
                'params': {'min_rating': 4.0, 'in_stock': True}
            },
            {
                'name': 'Budget items ($10-$50)',
                'params': {'min_price': 10, 'max_price': 50}
            },
            {
                'name': 'Premium electronics in stock',
                'params': {'category': 'Electronics', 'min_price': 500, 'in_stock': True}
            }
        ]
        
        for scenario in filter_scenarios:
            print(f"\n📋 {scenario['name']}")
            filter_expr = build_product_filter(**scenario['params'])
            print(f"   Generated Filter: {filter_expr}")
            print(f"   Parameters: {scenario['params']}")
            
            if filter_expr:
                try:
                    results = self.search_client.search(
                        search_text="*",
                        filter=filter_expr,
                        top=2,
                        select=['id', 'name', 'category', 'price', 'rating', 'inStock']
                    )
                    
                    result_list = list(results)
                    print(f"   Results: {len(result_list)} items found")
                    
                    for i, result in enumerate(result_list, 1):
                        name = result.get('name', 'N/A')
                        category = result.get('category', 'N/A')
                        price = result.get('price', 'N/A')
                        rating = result.get('rating', 'N/A')
                        in_stock = result.get('inStock', 'N/A')
                        print(f"     {i}. {name} ({category}) - ${price} - {rating}⭐ - Stock: {in_stock}")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
    
    def demonstrate_best_practices(self):
        """Demonstrate filter best practices"""
        print("\n💡 Filter Best Practices")
        print("=" * 40)
        
        print("\n1. Use specific filters first (most selective)")
        print("   ✅ Good: category eq 'Electronics' and price gt 1000")
        print("   ❌ Avoid: price gt 0 and category eq 'Electronics'")
        
        print("\n2. Use appropriate data types")
        print("   ✅ Good: price gt 100 (numeric)")
        print("   ❌ Avoid: price gt '100' (string)")
        
        print("\n3. Handle null values explicitly")
        print("   ✅ Good: rating ne null and rating ge 4.0")
        print("   ❌ Risky: rating ge 4.0 (may include nulls)")
        
        print("\n4. Use parentheses for complex logic")
        print("   ✅ Good: (category eq 'A' and price gt 100) or (category eq 'B' and rating ge 4.0)")
        print("   ❌ Confusing: category eq 'A' and price gt 100 or category eq 'B' and rating ge 4.0")
        
        print("\n5. Validate filter expressions")
        
        def validate_filter_syntax(filter_expr):
            """Simple filter validation"""
            if not filter_expr:
                return True, "Empty filter is valid"
            
            # Check for balanced parentheses
            if filter_expr.count('(') != filter_expr.count(')'):
                return False, "Unbalanced parentheses"
            
            # Check for balanced quotes
            single_quotes = filter_expr.count("'")
            if single_quotes % 2 != 0:
                return False, "Unbalanced single quotes"
            
            return True, "Filter appears valid"
        
        test_filters = [
            "category eq 'Electronics'",  # Valid
            "category eq 'Electronics",   # Invalid - missing quote
            "(price gt 100 and rating ge 4.0",  # Invalid - unbalanced parentheses
            "price gt 100 and rating ge 4.0"    # Valid
        ]
        
        print("\n   Filter Validation Examples:")
        for filter_expr in test_filters:
            is_valid, message = validate_filter_syntax(filter_expr)
            status = "✅" if is_valid else "❌"
            print(f"   {status} '{filter_expr}' - {message}")
    
    def run(self):
        """Run all basic filter examples"""
        print("🚀 Basic Filters Example")
        print("=" * 50)
        
        try:
            self.demonstrate_equality_filters()
            self.demonstrate_comparison_filters()
            self.demonstrate_logical_combinations()
            self.demonstrate_null_handling()
            self.demonstrate_filter_building()
            self.demonstrate_best_practices()
            
            print("\n✅ Basic filters example completed successfully!")
            print("\nKey takeaways:")
            print("- Use equality (eq/ne) and comparison (gt/ge/lt/le) operators")
            print("- Combine filters with logical operators (and/or/not)")
            print("- Handle null values explicitly in your filters")
            print("- Build filters dynamically based on user input")
            print("- Validate filter syntax before executing queries")
            
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            raise

def main():
    example = BasicFiltersExample()
    try:
        example.run()
    except Exception as e:
        print(f"Application failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()