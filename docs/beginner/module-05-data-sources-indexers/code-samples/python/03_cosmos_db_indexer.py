#!/usr/bin/env python3
"""
Azure Cosmos DB Indexer Example

This script demonstrates how to create and manage indexers for Azure Cosmos DB data sources.
It covers JSON document processing, change feed integration, and partition key handling.

Prerequisites:
- Azure AI Search service
- Azure Cosmos DB account with sample data
- Admin API key or managed identity
- Required Python packages installed
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, SearchIndexer,
    SearchIndexerDataContainer, SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType, HighWaterMarkChangeDetectionPolicy,
    FieldMapping, SimpleField, SearchableField, ComplexField
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
COSMOS_CONNECTION_STRING = os.getenv('COSMOS_CONNECTION_STRING')

# Resource names
DATA_SOURCE_NAME = "cosmos-hotels-datasource"
INDEX_NAME = "hotels-cosmos-index"
INDEXER_NAME = "hotels-cosmos-indexer"
CONTAINER_NAME = "hotels"

def validate_configuration():
    """Validate that all required configuration is present."""
    required_vars = [SEARCH_ENDPOINT, SEARCH_API_KEY, COSMOS_CONNECTION_STRING]
    if not all(required_vars):
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    print("✅ Configuration validated")
    print(f"📍 Search Endpoint: {SEARCH_ENDPOINT}")
    print(f"🗃️ Data Source: {DATA_SOURCE_NAME}")
    print(f"📊 Index: {INDEX_NAME}")
    print(f"⚙️ Indexer: {INDEXER_NAME}")

def create_cosmos_data_source(indexer_client):
    """Create a data source connection to Azure Cosmos DB."""
    print("\n🔗 Creating Cosmos DB data source...")
    
    data_source = SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type=SearchIndexerDataSourceType.COSMOS_DB,
        connection_string=COSMOS_CONNECTION_STRING,
        container=SearchIndexerDataContainer(
            name=CONTAINER_NAME,
            query="SELECT * FROM c WHERE c._ts >= @HighWaterMark ORDER BY c._ts"
        ),
        data_change_detection_policy=HighWaterMarkChangeDetectionPolicy(
            high_water_mark_column_name="_ts"
        ),
        description="Hotel data from Cosmos DB with change feed detection"
    )
    
    try:
        result = indexer_client.create_or_update_data_source_connection(data_source)
        print(f"✅ Data source '{DATA_SOURCE_NAME}' created successfully")
        
        # Display configuration
        print(f"   Type: {result.type}")
        print(f"   Container: {result.container.name}")
        print(f"   Change Detection: {type(result.data_change_detection_policy).__name__}")
        print(f"   High Water Mark: {result.data_change_detection_policy.high_water_mark_column_name}")
        
        return result
    except HttpResponseError as e:
        print(f"❌ Error creating data source: {e.message}")
        raise

def create_hotels_index(index_client):
    """Create a search index optimized for hotel data from Cosmos DB."""
    print("\n📊 Creating hotels index...")
    
    # Define index fields for hotel data
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="hotelName", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="rating", type=SearchFieldDataType.Double, filterable=True, sortable=True, facetable=True),
        
        # Complex field for address
        ComplexField(name="address", fields=[
            SearchableField(name="street", type=SearchFieldDataType.String),
            SearchableField(name="city", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="state", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="zipCode", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="country", type=SearchFieldDataType.String, filterable=True, facetable=True)
        ]),
        
        # Collection field for amenities
        SearchableField(name="amenities", type=SearchFieldDataType.Collection(SearchFieldDataType.String), facetable=True),
        
        # Date fields
        SimpleField(name="lastRenovated", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SimpleField(name="_ts", type=SearchFieldDataType.Int64, filterable=True, sortable=True),
        
        # Location field for geo-search (if coordinates available)
        SimpleField(name="location", type=SearchFieldDataType.GeographyPoint, filterable=True, sortable=True)
    ]
    
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields
    )
    
    try:
        result = index_client.create_or_update_index(index)
        print(f"✅ Index '{INDEX_NAME}' created successfully")
        print(f"   Total Fields: {len(result.fields)}")
        
        # Display key fields
        print("   Key fields for hotel data:")
        key_fields = ['id', 'hotelName', 'category', 'rating', 'address']
        for field in result.fields:
            if field.name in key_fields:
                attributes = []
                if hasattr(field, 'key') and field.key:
                    attributes.append('key')
                if hasattr(field, 'searchable') and field.searchable:
                    attributes.append('searchable')
                if hasattr(field, 'filterable') and field.filterable:
                    attributes.append('filterable')
                if hasattr(field, 'facetable') and field.facetable:
                    attributes.append('facetable')
                
                field_type = field.type if hasattr(field, 'type') else 'Complex'
                print(f"     - {field.name} ({field_type}) [{', '.join(attributes)}]")
        
        return result
    except HttpResponseError as e:
        print(f"❌ Error creating index: {e.message}")
        raise

def create_cosmos_indexer(indexer_client):
    """Create an indexer to process hotel data from Cosmos DB."""
    print("\n⚙️ Creating Cosmos DB indexer...")
    
    # Field mappings for Cosmos DB data
    field_mappings = [
        FieldMapping(source_field_name="id", target_field_name="id"),
        FieldMapping(source_field_name="hotelName", target_field_name="hotelName"),
        FieldMapping(source_field_name="description", target_field_name="description"),
        FieldMapping(source_field_name="category", target_field_name="category"),
        FieldMapping(source_field_name="rating", target_field_name="rating"),
        FieldMapping(source_field_name="address", target_field_name="address"),
        FieldMapping(source_field_name="amenities", target_field_name="amenities"),
        FieldMapping(source_field_name="lastRenovated", target_field_name="lastRenovated"),
        FieldMapping(source_field_name="_ts", target_field_name="_ts")
    ]
    
    indexer = SearchIndexer(
        name=INDEXER_NAME,
        data_source_name=DATA_SOURCE_NAME,
        target_index_name=INDEX_NAME,
        field_mappings=field_mappings,
        description="Indexer for hotel data from Cosmos DB",
        parameters={
            "batchSize": 100,  # Larger batch for JSON documents
            "maxFailedItems": 10,
            "maxFailedItemsPerBatch": 5,
            "configuration": {
                "parsingMode": "json"
            }
        }
    )
    
    try:
        result = indexer_client.create_or_update_indexer(indexer)
        print(f"✅ Indexer '{INDEXER_NAME}' created successfully")
        print(f"   Data Source: {result.data_source_name}")
        print(f"   Target Index: {result.target_index_name}")
        print(f"   Field Mappings: {len(result.field_mappings)}")
        print(f"   Batch Size: {result.parameters.get('batchSize', 'default')}")
        
        return result
    except HttpResponseError as e:
        print(f"❌ Error creating indexer: {e.message}")
        raise

def run_and_monitor_indexer(indexer_client):
    """Run the indexer and monitor hotel data processing."""
    print(f"\n🚀 Starting Cosmos DB indexer: {INDEXER_NAME}")
    
    try:
        # Start the indexer
        indexer_client.run_indexer(INDEXER_NAME)
        print("✅ Indexer started successfully")
        
        # Monitor execution
        start_time = time.time()
        max_wait_time = 300  # 5 minutes
        
        while time.time() - start_time < max_wait_time:
            status = indexer_client.get_indexer_status(INDEXER_NAME)
            
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n⏰ {current_time} - Status: {status.status}")
            
            if status.last_result:
                result = status.last_result
                print(f"   🏨 Hotels processed: {result.item_count or 0}")
                print(f"   ❌ Hotels failed: {result.failed_item_count or 0}")
                
                # Show processing rate if available
                if result.item_count and result.item_count > 0 and result.end_time and result.start_time:
                    duration = (result.end_time - result.start_time).total_seconds()
                    if duration > 0:
                        rate = result.item_count / duration
                        print(f"   📊 Processing rate: {rate:.2f} hotels/sec")
                
                # Show any errors
                if result.errors:
                    print(f"   ⚠️ Recent errors:")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"     - {error.error_message}")
                
                # Show warnings if any
                if result.warnings:
                    print(f"   ⚠️ Warnings: {len(result.warnings)}")
            
            if status.status in ["success", "error"]:
                print(f"\n🎉 Indexer execution completed with status: {status.status}")
                break
            
            time.sleep(10)
        else:
            print(f"\n⏰ Monitoring timeout reached ({max_wait_time}s)")
        
        return status
        
    except HttpResponseError as e:
        print(f"❌ Error running indexer: {e.message}")
        raise

def test_hotel_search():
    """Test search functionality on the indexed hotel data."""
    print("\n🔍 Testing hotel search...")
    
    from azure.search.documents import SearchClient
    
    credential = AzureKeyCredential(SEARCH_API_KEY)
    search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential)
    
    test_queries = [
        {
            'name': 'All hotels',
            'query': {'search_text': '*', 'top': 5}
        },
        {
            'name': 'Luxury hotels',
            'query': {'search_text': 'luxury', 'top': 3}
        },
        {
            'name': 'High-rated hotels',
            'query': {
                'search_text': '*', 
                'filter': "rating ge 4.0", 
                'order_by': ['rating desc'],
                'top': 3
            }
        },
        {
            'name': 'Hotels by city',
            'query': {
                'search_text': '*', 
                'facets': ['address/city'],
                'top': 0  # Just get facets
            }
        },
        {
            'name': 'Hotels with amenities',
            'query': {
                'search_text': '*',
                'filter': "amenities/any(a: a eq 'WiFi')",
                'top': 3
            }
        }
    ]
    
    for test in test_queries:
        print(f"\n   🔍 {test['name']}:")
        try:
            results = search_client.search(**test['query'])
            
            if test['name'] == 'Hotels by city':
                # Handle facet results
                facets = results.get_facets()
                if facets and 'address/city' in facets:
                    print(f"      Cities found:")
                    for facet in facets['address/city'][:5]:
                        print(f"        - {facet['value']}: {facet['count']} hotels")
            else:
                # Handle regular search results
                results_list = list(results)
                print(f"      Found {len(results_list)} results")
                
                for i, result in enumerate(results_list[:2]):  # Show first 2 results
                    hotel_name = result.get('hotelName', 'N/A')
                    category = result.get('category', 'N/A')
                    rating = result.get('rating', 0)
                    city = result.get('address', {}).get('city', 'N/A') if result.get('address') else 'N/A'
                    print(f"      {i+1}. {hotel_name} ({category}) - {rating}⭐ in {city}")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")

def demonstrate_change_feed():
    """Demonstrate how change feed detection works with Cosmos DB."""
    print("\n🔄 Change Feed Detection:")
    print("   Cosmos DB indexer uses the '_ts' field for change detection")
    print("   Benefits:")
    print("   - Automatic detection of new and updated documents")
    print("   - Efficient incremental updates")
    print("   - Built-in ordering by timestamp")
    print("   - No additional configuration required")
    print("\n   The indexer query includes: WHERE c._ts >= @HighWaterMark ORDER BY c._ts")
    print("   This ensures only changed documents are processed on subsequent runs")

def cleanup_resources(index_client, indexer_client):
    """Clean up created resources (optional)."""
    print("\n🧹 Cleanup options:")
    print("   To clean up resources, run:")
    print(f"   - Delete indexer: indexer_client.delete_indexer('{INDEXER_NAME}')")
    print(f"   - Delete index: index_client.delete_index('{INDEX_NAME}')")
    print(f"   - Delete data source: indexer_client.delete_data_source_connection('{DATA_SOURCE_NAME}')")

def main():
    """Main execution function."""
    print("🚀 Azure Cosmos DB Indexer Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize clients
        credential = AzureKeyCredential(SEARCH_API_KEY)
        index_client = SearchIndexClient(SEARCH_ENDPOINT, credential)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Create resources
        data_source = create_cosmos_data_source(indexer_client)
        index = create_hotels_index(index_client)
        indexer = create_cosmos_indexer(indexer_client)
        
        # Run and monitor indexer
        status = run_and_monitor_indexer(indexer_client)
        
        # Test search functionality
        if status.status == "success":
            test_hotel_search()
        
        # Demonstrate change feed concepts
        demonstrate_change_feed()
        
        # Show cleanup options
        cleanup_resources(index_client, indexer_client)
        
        print("\n✅ Cosmos DB indexer example completed successfully!")
        print("\nKey takeaways:")
        print("- Cosmos DB change feed provides efficient incremental updates")
        print("- Complex fields handle nested JSON structures well")
        print("- Collection fields are perfect for arrays like amenities")
        print("- Faceted search works great with categorical hotel data")
        print("- Higher batch sizes work well with JSON documents")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()