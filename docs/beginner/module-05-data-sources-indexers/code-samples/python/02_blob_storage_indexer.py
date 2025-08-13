#!/usr/bin/env python3
"""
Azure Blob Storage Indexer Example

This script demonstrates how to create and manage indexers for Azure Blob Storage data sources.
It covers document processing, metadata extraction, and change detection.

Prerequisites:
- Azure AI Search service
- Azure Storage Account with sample documents
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
    FieldMapping, SimpleField, SearchableField
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
STORAGE_CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')

# Resource names
DATA_SOURCE_NAME = "blob-documents-datasource"
INDEX_NAME = "documents-blob-index"
INDEXER_NAME = "documents-blob-indexer"
CONTAINER_NAME = "sample-documents"

def validate_configuration():
    """Validate that all required configuration is present."""
    required_vars = [SEARCH_ENDPOINT, SEARCH_API_KEY, STORAGE_CONNECTION_STRING]
    if not all(required_vars):
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    print("✅ Configuration validated")
    print(f"📍 Search Endpoint: {SEARCH_ENDPOINT}")
    print(f"🗃️ Data Source: {DATA_SOURCE_NAME}")
    print(f"📊 Index: {INDEX_NAME}")
    print(f"⚙️ Indexer: {INDEXER_NAME}")

def create_blob_data_source(indexer_client):
    """Create a data source connection to Azure Blob Storage."""
    print("\n🔗 Creating blob storage data source...")
    
    data_source = SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type=SearchIndexerDataSourceType.AZURE_BLOB,
        connection_string=STORAGE_CONNECTION_STRING,
        container=SearchIndexerDataContainer(name=CONTAINER_NAME),
        data_change_detection_policy=HighWaterMarkChangeDetectionPolicy(
            high_water_mark_column_name="metadata_storage_last_modified"
        ),
        description="Document data from Azure Blob Storage with LastModified detection"
    )
    
    try:
        result = indexer_client.create_or_update_data_source_connection(data_source)
        print(f"✅ Data source '{DATA_SOURCE_NAME}' created successfully")
        
        # Display configuration
        print(f"   Type: {result.type}")
        print(f"   Container: {result.container.name}")
        print(f"   Change Detection: {type(result.data_change_detection_policy).__name__}")
        
        return result
    except HttpResponseError as e:
        print(f"❌ Error creating data source: {e.message}")
        raise

def create_document_index(index_client):
    """Create a search index optimized for document content and metadata."""
    print("\n📊 Creating document index...")
    
    # Define index fields for document content and metadata
    fields = [
        SimpleField(name="metadata_storage_path", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SimpleField(name="metadata_storage_name", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="metadata_storage_size", type=SearchFieldDataType.Int64, filterable=True, sortable=True),
        SimpleField(name="metadata_storage_last_modified", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SimpleField(name="metadata_storage_content_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="metadata_language", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="metadata_title", type=SearchFieldDataType.String),
        SearchableField(name="metadata_author", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="keyphrases", type=SearchFieldDataType.Collection(SearchFieldDataType.String), facetable=True)
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
        print("   Key fields for document processing:")
        for field in result.fields[:5]:  # Show first 5 fields
            attributes = []
            if hasattr(field, 'key') and field.key:
                attributes.append('key')
            if hasattr(field, 'searchable') and field.searchable:
                attributes.append('searchable')
            if hasattr(field, 'filterable') and field.filterable:
                attributes.append('filterable')
            
            print(f"     - {field.name} ({field.type}) [{', '.join(attributes)}]")
        
        return result
    except HttpResponseError as e:
        print(f"❌ Error creating index: {e.message}")
        raise

def create_blob_indexer(indexer_client):
    """Create an indexer to process documents from blob storage."""
    print("\n⚙️ Creating blob storage indexer...")
    
    # Field mappings for blob storage metadata
    field_mappings = [
        FieldMapping(source_field_name="metadata_storage_path", target_field_name="metadata_storage_path"),
        FieldMapping(source_field_name="content", target_field_name="content"),
        FieldMapping(source_field_name="metadata_storage_name", target_field_name="metadata_storage_name"),
        FieldMapping(source_field_name="metadata_storage_size", target_field_name="metadata_storage_size"),
        FieldMapping(source_field_name="metadata_storage_last_modified", target_field_name="metadata_storage_last_modified"),
        FieldMapping(source_field_name="metadata_storage_content_type", target_field_name="metadata_storage_content_type")
    ]
    
    indexer = SearchIndexer(
        name=INDEXER_NAME,
        data_source_name=DATA_SOURCE_NAME,
        target_index_name=INDEX_NAME,
        field_mappings=field_mappings,
        description="Indexer for documents from blob storage",
        parameters={
            "batchSize": 50,  # Smaller batch for document processing
            "maxFailedItems": 5,
            "maxFailedItemsPerBatch": 2,
            "configuration": {
                "dataToExtract": "contentAndMetadata",
                "parsingMode": "default",
                "excludedFileNameExtensions": ".png,.jpg,.jpeg,.gif,.bmp"
            }
        }
    )
    
    try:
        result = indexer_client.create_or_update_indexer(indexer)
        print(f"✅ Indexer '{INDEXER_NAME}' created successfully")
        print(f"   Data Source: {result.data_source_name}")
        print(f"   Target Index: {result.target_index_name}")
        print(f"   Field Mappings: {len(result.field_mappings)}")
        
        return result
    except HttpResponseError as e:
        print(f"❌ Error creating indexer: {e.message}")
        raise

def run_and_monitor_indexer(indexer_client):
    """Run the indexer and monitor document processing."""
    print(f"\n🚀 Starting blob indexer: {INDEXER_NAME}")
    
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
                print(f"   📄 Documents processed: {result.item_count or 0}")
                print(f"   ❌ Documents failed: {result.failed_item_count or 0}")
                
                # Show processing rate if available
                if result.item_count and result.item_count > 0 and result.end_time and result.start_time:
                    duration = (result.end_time - result.start_time).total_seconds()
                    if duration > 0:
                        rate = result.item_count / duration
                        print(f"   📊 Processing rate: {rate:.2f} docs/sec")
                
                # Show any errors
                if result.errors:
                    print(f"   ⚠️ Recent errors:")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"     - {error.error_message}")
            
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

def test_document_search():
    """Test search functionality on the indexed documents."""
    print("\n🔍 Testing document search...")
    
    from azure.search.documents import SearchClient
    
    credential = AzureKeyCredential(SEARCH_API_KEY)
    search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential)
    
    test_queries = [
        {
            'name': 'All documents',
            'query': {'search_text': '*', 'top': 5}
        },
        {
            'name': 'Content search',
            'query': {'search_text': 'document', 'top': 3}
        },
        {
            'name': 'Filter by content type',
            'query': {
                'search_text': '*', 
                'filter': "metadata_storage_content_type eq 'application/pdf'", 
                'top': 3
            }
        },
        {
            'name': 'Sort by size',
            'query': {
                'search_text': '*', 
                'order_by': ['metadata_storage_size desc'], 
                'top': 3
            }
        }
    ]
    
    for test in test_queries:
        print(f"\n   🔍 {test['name']}:")
        try:
            results = list(search_client.search(**test['query']))
            print(f"      Found {len(results)} results")
            
            for i, result in enumerate(results[:2]):  # Show first 2 results
                filename = result.get('metadata_storage_name', 'N/A')
                content_type = result.get('metadata_storage_content_type', 'N/A')
                size = result.get('metadata_storage_size', 0)
                print(f"      {i+1}. {filename} ({content_type}) - {size:,} bytes")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")

def cleanup_resources(index_client, indexer_client):
    """Clean up created resources (optional)."""
    print("\n🧹 Cleanup options:")
    print("   To clean up resources, run:")
    print(f"   - Delete indexer: indexer_client.delete_indexer('{INDEXER_NAME}')")
    print(f"   - Delete index: index_client.delete_index('{INDEX_NAME}')")
    print(f"   - Delete data source: indexer_client.delete_data_source_connection('{DATA_SOURCE_NAME}')")

def main():
    """Main execution function."""
    print("🚀 Azure Blob Storage Indexer Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize clients
        credential = AzureKeyCredential(SEARCH_API_KEY)
        index_client = SearchIndexClient(SEARCH_ENDPOINT, credential)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Create resources
        data_source = create_blob_data_source(indexer_client)
        index = create_document_index(index_client)
        indexer = create_blob_indexer(indexer_client)
        
        # Run and monitor indexer
        status = run_and_monitor_indexer(indexer_client)
        
        # Test search functionality
        if status.status == "success":
            test_document_search()
        
        # Show cleanup options
        cleanup_resources(index_client, indexer_client)
        
        print("\n✅ Blob storage indexer example completed successfully!")
        print("\nKey takeaways:")
        print("- LastModified change detection is ideal for file-based data sources")
        print("- Metadata extraction provides valuable searchable information")
        print("- Content type filtering helps organize different document types")
        print("- Batch size optimization is important for document processing performance")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()