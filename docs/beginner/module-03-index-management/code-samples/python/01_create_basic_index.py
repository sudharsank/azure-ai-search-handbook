#!/usr/bin/env python3
"""
Module 3: Index Management - Basic Index Creation
================================================

This example demonstrates the fundamentals of creating a search index in Azure AI Search.
You'll learn how to define field types, set attributes, and create your first index.

Learning Objectives:
- Create SearchIndexClient with proper authentication
- Define field types and attributes
- Create a basic index schema
- Handle index creation responses
- Validate index creation

Prerequisites:
- Azure AI Search service with admin access
- Environment variables configured
- azure-search-documents package installed

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SimpleField,
        SearchableField,
        SearchFieldDataType
    )
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
except ImportError as e:
    print("❌ Missing required packages. Please install:")
    print("   pip install azure-search-documents python-dotenv")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

class BasicIndexCreator:
    """Demonstrates basic index creation patterns"""
    
    def __init__(self):
        """Initialize the index creator with Azure AI Search credentials"""
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_client = None
        
        if not self.endpoint or not self.admin_key:
            raise ValueError("Missing required environment variables: AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_ADMIN_KEY")
    
    def create_index_client(self) -> bool:
        """Create and validate the SearchIndexClient"""
        print("🔍 Creating SearchIndexClient...")
        
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Test connection by getting service statistics
            stats = self.index_client.get_service_statistics()
            print(f"✅ Connected to Azure AI Search service")
            print(f"   Storage used: {stats.storage_size_in_bytes:,} bytes")
            print(f"   Document count: {stats.document_count:,}")
            
            return True
            
        except HttpResponseError as e:
            if e.status_code == 403:
                print("❌ Access denied - check your admin API key")
            else:
                print(f"❌ HTTP error {e.status_code}: {e.message}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to create index client: {str(e)}")
            return False
    
    def define_basic_schema(self) -> List:
        """Define a basic index schema for a blog application"""
        print("📋 Defining Basic Index Schema...")
        
        # Define fields with different types and attributes
        fields = [
            # Key field (required) - unique identifier for each document
            SimpleField(
                name="id", 
                type=SearchFieldDataType.String, 
                key=True
            ),
            
            # Searchable text fields - enable full-text search
            SearchableField(
                name="title", 
                type=SearchFieldDataType.String,
                analyzer_name="en.microsoft"  # English language analyzer
            ),
            
            SearchableField(
                name="content", 
                type=SearchFieldDataType.String,
                analyzer_name="en.microsoft"
            ),
            
            # Simple fields for exact matching and filtering
            SimpleField(
                name="author", 
                type=SearchFieldDataType.String,
                filterable=True,  # Enable filtering by author
                facetable=True    # Enable faceting for navigation
            ),
            
            SimpleField(
                name="category", 
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True
            ),
            
            # Date field - filterable and sortable
            SimpleField(
                name="publishedDate", 
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True
            ),
            
            # Collection field for multiple values
            SimpleField(
                name="tags", 
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                filterable=True,
                facetable=True
            ),
            
            # Numeric fields
            SimpleField(
                name="rating", 
                type=SearchFieldDataType.Double,
                filterable=True,
                sortable=True
            ),
            
            SimpleField(
                name="viewCount", 
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True
            ),
            
            # Boolean field
            SimpleField(
                name="isPublished", 
                type=SearchFieldDataType.Boolean,
                filterable=True
            )
        ]
        
        # Display schema information
        print(f"✅ Schema defined with {len(fields)} fields:")
        print(f"{'Field Name':<15} | {'Type':<25} | {'Attributes'}")
        print("-" * 70)
        
        for field in fields:
            attributes = []
            if hasattr(field, 'key') and field.key:
                attributes.append("KEY")
            if hasattr(field, 'searchable') and field.searchable:
                attributes.append("searchable")
            if hasattr(field, 'filterable') and field.filterable:
                attributes.append("filterable")
            if hasattr(field, 'sortable') and field.sortable:
                attributes.append("sortable")
            if hasattr(field, 'facetable') and field.facetable:
                attributes.append("facetable")
            
            attr_str = ", ".join(attributes) if attributes else "retrievable only"
            print(f"{field.name:<15} | {str(field.type):<25} | {attr_str}")
        
        return fields
    
    def create_index(self, index_name: str, fields: List) -> Optional[SearchIndex]:
        """Create the search index"""
        print(f"🏗️  Creating index '{index_name}'...")
        
        try:
            # Create the index object
            index = SearchIndex(name=index_name, fields=fields)
            
            # Create the index (use create_or_update_index for safety)
            result = self.index_client.create_or_update_index(index)
            
            print(f"✅ Index '{result.name}' created successfully!")
            print(f"   Fields: {len(result.fields)}")
            print(f"   Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return result
            
        except HttpResponseError as e:
            if e.status_code == 400:
                print(f"❌ Bad request - check index definition: {e.message}")
            elif e.status_code == 409:
                print(f"❌ Index already exists (this shouldn't happen with create_or_update)")
            else:
                print(f"❌ HTTP error {e.status_code}: {e.message}")
            return None
            
        except Exception as e:
            print(f"❌ Failed to create index: {str(e)}")
            return None
    
    def validate_index(self, index_name: str) -> bool:
        """Validate that the index was created correctly"""
        print(f"🔍 Validating index '{index_name}'...")
        
        try:
            # Get the index details
            index = self.index_client.get_index(index_name)
            
            print(f"✅ Index validation successful:")
            print(f"   Name: {index.name}")
            print(f"   Fields: {len(index.fields)}")
            
            # Validate key field exists
            key_fields = [f for f in index.fields if hasattr(f, 'key') and f.key]
            if len(key_fields) == 1:
                print(f"   Key field: {key_fields[0].name}")
            else:
                print(f"   ⚠️  Warning: Found {len(key_fields)} key fields (should be 1)")
            
            # Count searchable fields
            searchable_fields = [f for f in index.fields if hasattr(f, 'searchable') and f.searchable]
            print(f"   Searchable fields: {len(searchable_fields)}")
            
            # Count filterable fields
            filterable_fields = [f for f in index.fields if hasattr(f, 'filterable') and f.filterable]
            print(f"   Filterable fields: {len(filterable_fields)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Index validation failed: {str(e)}")
            return False
    
    def test_index_functionality(self, index_name: str) -> bool:
        """Test basic index functionality with a sample document"""
        print(f"🧪 Testing index functionality...")
        
        try:
            # Create search client for document operations
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Create a test document
            test_document = {
                "id": "test-doc-1",
                "title": "Test Document for Index Validation",
                "content": "This is a test document to validate that our newly created index is working correctly.",
                "author": "Test Author",
                "category": "Test",
                "publishedDate": "2024-02-10T10:00:00Z",
                "tags": ["test", "validation", "index"],
                "rating": 5.0,
                "viewCount": 1,
                "isPublished": True
            }
            
            # Upload the test document
            result = search_client.upload_documents([test_document])
            
            if result[0].succeeded:
                print("✅ Test document uploaded successfully")
                
                # Wait a moment for indexing
                import time
                time.sleep(2)
                
                # Try to retrieve the document
                doc_count = search_client.get_document_count()
                print(f"✅ Index contains {doc_count} document(s)")
                
                # Clean up - delete the test document
                delete_result = search_client.delete_documents([{"id": "test-doc-1"}])
                if delete_result[0].succeeded:
                    print("✅ Test document cleaned up successfully")
                
                return True
            else:
                print(f"❌ Test document upload failed: {result[0].error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Index functionality test failed: {str(e)}")
            return False
    
    def list_existing_indexes(self) -> None:
        """List existing indexes in the service"""
        print("📋 Listing existing indexes...")
        
        try:
            indexes = list(self.index_client.list_indexes())
            
            if indexes:
                print(f"Found {len(indexes)} existing indexes:")
                for index in indexes:
                    print(f"   - {index.name} ({len(index.fields)} fields)")
            else:
                print("No existing indexes found")
                
        except Exception as e:
            print(f"❌ Failed to list indexes: {str(e)}")
    
    def cleanup_index(self, index_name: str) -> bool:
        """Clean up the created index (optional)"""
        print(f"🧹 Cleaning up index '{index_name}'...")
        
        try:
            self.index_client.delete_index(index_name)
            print(f"✅ Index '{index_name}' deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete index: {str(e)}")
            return False

def main():
    """Main function demonstrating basic index creation"""
    print("=" * 60)
    print("Module 3: Basic Index Creation Example")
    print("=" * 60)
    
    # Initialize the index creator
    try:
        creator = BasicIndexCreator()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set the required environment variables:")
        print("   export AZURE_SEARCH_SERVICE_ENDPOINT='https://your-service.search.windows.net'")
        print("   export AZURE_SEARCH_ADMIN_KEY='your-admin-api-key'")
        return
    
    # Create index client
    if not creator.create_index_client():
        print("❌ Failed to create index client. Exiting.")
        return
    
    # List existing indexes
    creator.list_existing_indexes()
    
    # Define the index schema
    fields = creator.define_basic_schema()
    
    # Create the index
    index_name = "basic-blog-index"
    index = creator.create_index(index_name, fields)
    
    if index:
        # Validate the index
        if creator.validate_index(index_name):
            # Test index functionality
            if creator.test_index_functionality(index_name):
                print("\n🎉 Index creation and testing completed successfully!")
                
                # Ask if user wants to clean up
                cleanup = input(f"\nDo you want to delete the test index '{index_name}'? (y/N): ").lower().strip()
                if cleanup in ['y', 'yes']:
                    creator.cleanup_index(index_name)
                else:
                    print(f"ℹ️  Index '{index_name}' preserved for further experimentation")
            else:
                print("⚠️  Index created but functionality test failed")
        else:
            print("⚠️  Index created but validation failed")
    else:
        print("❌ Index creation failed")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\n📚 What you learned:")
    print("✅ How to create SearchIndexClient with proper authentication")
    print("✅ How to define field types and attributes")
    print("✅ How to create a basic index schema")
    print("✅ How to handle index creation responses")
    print("✅ How to validate index creation")
    print("✅ How to test index functionality")
    
    print("\n🚀 Next steps:")
    print("1. Try modifying the schema with different field types")
    print("2. Experiment with different field attributes")
    print("3. Run the next example: 02_schema_design.py")
    print("4. Upload real documents to your index")

if __name__ == "__main__":
    main()