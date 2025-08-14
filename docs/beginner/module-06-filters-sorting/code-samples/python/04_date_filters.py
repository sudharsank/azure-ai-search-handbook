"""
Date Filters Example

This example demonstrates date-based filtering operations in Azure AI Search,
including date ranges, relative date calculations, and time zone handling.
"""

import os
from datetime import datetime, timedelta
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class DateFiltersExample:
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
    
    def demonstrate_relative_date_builder(self):
        """Demonstrate dynamic relative date filter building"""
        print("\n🔧 Relative Date Filter Builder")
        print("=" * 40)
        
        def build_relative_date_filter(field, days_ago=None, hours_ago=None, 
                                     weeks_ago=None, months_ago=None):
            """Build relative date filter"""
            now = datetime.utcnow()
            
            if days_ago is not None:
                cutoff = now - timedelta(days=days_ago)
            elif hours_ago is not None:
                cutoff = now - timedelta(hours=hours_ago)
            elif weeks_ago is not None:
                cutoff = now - timedelta(weeks=weeks_ago)
            elif months_ago is not None:
                cutoff = now - timedelta(days=months_ago * 30)  # Approximate
            else:
                raise ValueError("Must specify one time period")
            
            cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')
            return f"{field} ge {cutoff_str}"
        
        # Test different relative date scenarios
        relative_scenarios = [
            {
                'name': 'Last 24 hours',
                'params': {'field': 'lastModified', 'hours_ago': 24}
            },
            {
                'name': 'Last 7 days',
                'params': {'field': 'createdDate', 'days_ago': 7}
            },
            {
                'name': 'Last 2 weeks',
                'params': {'field': 'lastModified', 'weeks_ago': 2}
            },
            {
                'name': 'Last 3 months',
                'params': {'field': 'createdDate', 'months_ago': 3}
            }
        ]
        
        for scenario in relative_scenarios:
            print(f"\n📋 {scenario['name']}")
            filter_expr = build_relative_date_filter(**scenario['params'])
            print(f"   Generated Filter: {filter_expr}")
            print(f"   Parameters: {scenario['params']}")
            
            try:
                results = self.search_client.search(
                    search_text="*",
                    filter=filter_expr,
                    top=2,
                    select=['id', 'name', 'createdDate', 'lastModified']
                )
                
                result_list = list(results)
                print(f"   Results: {len(result_list)} items found")
                
                for i, result in enumerate(result_list, 1):
                    name = result.get('name', 'N/A')
                    created = result.get('createdDate', 'N/A')
                    modified = result.get('lastModified', 'N/A')
                    print(f"     {i}. {name} - Created: {created} - Modified: {modified}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def demonstrate_best_practices(self):
        """Demonstrate date filtering best practices"""
        print("\n💡 Date Filtering Best Practices")
        print("=" * 40)
        
        print("\n1. Use ISO 8601 format for dates:")
        print("   ✅ Good: 2024-01-01T00:00:00Z")
        print("   ✅ Good: 2024-01-01T12:30:45.123Z")
        print("   ❌ Avoid: 01/01/2024 or 2024-1-1")
        
        print("\n2. Handle time zones consistently:")
        print("   ✅ Use UTC for storage and filtering")
        print("   ✅ Convert user input to UTC")
        print("   ✅ Display dates in user's local time zone")
        
        print("\n3. Consider date precision:")
        print("   ✅ Use appropriate precision for your use case")
        print("   ✅ Include time component when needed")
        print("   ✅ Use date-only for day-level filtering")
        
        print("\n4. Optimize date queries:")
        print("   ✅ Use indexed date fields")
        print("   ✅ Prefer 'ge' over 'gt' for inclusive ranges")
        print("   ✅ Combine date filters with other selective filters")
        
        print("\n5. Handle edge cases:")
        print("   ✅ Validate date ranges (start <= end)")
        print("   ✅ Handle null date values")
        print("   ✅ Consider leap years and month lengths")
    
    def run(self):
        """Run all date filter examples"""
        print("🚀 Date Filters Example")
        print("=" * 50)
        
        try:
            self.demonstrate_date_ranges()
            self.demonstrate_relative_date_builder()
            self.demonstrate_best_practices()
            
            print("\n✅ Date filters example completed successfully!")
            print("\nKey takeaways:")
            print("- Use ISO 8601 format for consistent date filtering")
            print("- Build relative date filters for dynamic time ranges")
            print("- Handle time zones and precision appropriately")
            print("- Optimize date queries with indexed fields")
            print("- Validate date ranges and handle edge cases")
            
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            raise

def main():
    example = DateFiltersExample()
    try:
        example.run()
    except Exception as e:
        print(f"Application failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()