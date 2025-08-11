#!/usr/bin/env python3
"""
Module 3: Index Management - Index Operations and Maintenance
============================================================

This example demonstrates various index management operations including updating schemas,
managing documents, monitoring index health, and performing maintenance tasks.

Learning Objectives:
- Perform index lifecycle operations (create, update, delete)
- Update index schemas safely
- Monitor index health and statistics
- Manage document operations (update, merge, delete)
- Handle index versioning and maintenance

Prerequisites:
- Completed previous examples (01-03)
- Understanding of index schemas and data ingestion
- Azure AI Search service with admin access

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
import time
from datetime import datetime, timezone
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

class IndexOperationsManager:
    """Demonstrates index operations and maintenance patterns"""
    
    def __init__(self):
        """Initialize the index operations manager"""
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_client = None
        
        if not self.endpoint or not self.admin_key:
            raise ValueError("Missing required environment variables")
    
    def create_clients(self) -> bool:
        """Create and validate the search clients"""
        print("🔍 Creating Search Clients...")
        
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Test connection
            stats = self.index_client.get_service_statistics()
            print(f"✅ Connected to Azure AI Search service")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create clients: {str(e)}")
            return False
    
    def list_all_indexes(self) -> List[str]:
        """List all indexes in the service"""
        print("📋 Listing All Indexes...")
        
        try:
            indexes = list(self.index_client.list_indexes())
            
            if indexes:
                print(f"Found {len(indexes)} indexes:")
                index_names = []
                for index in indexes:
                    print(f"   - {index.name} ({len(index.fields)} fields)")
                    index_names.append(index.name)
                return index_names
            else:
                print("No indexes found")
                return []
                
        except Exception as e:
            print(f"❌ Failed to list indexes: {str(e)}")
            return []
    
    def get_detailed_index_info(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a specific index"""
        print(f"🔍 Getting Detailed Information for '{index_name}'...")
        
        try:
            index = self.index_client.get_index(index_name)
            
            # Create search client for document operations
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Get document count
            doc_count = search_client.get_document_count()
            
            # Analyze field types and attributes
            field_analysis = self._analyze_index_fields(index.fields)
            
            index_info = {
                'name': index.name,
                'field_count': len(index.fields),
                'document_count': doc_count,
                'analyzers': len(index.analyzers) if index.analyzers else 0,
                'scoring_profiles': len(index.scoring_profiles) if index.scoring_profiles else 0,
                'cors_configured': index.cors_options is not None,
                'field_analysis': field_analysis,
                'fields': index.fields
            }
            
            print(f"✅ Index Information Retrieved:")
            print(f"   Name: {index_info['name']}")
            print(f"   Fields: {index_info['field_count']}")
            print(f"   Documents: {index_info['document_count']}")
            print(f"   Analyzers: {index_info['analyzers']}")
            print(f"   Scoring Profiles: {index_info['scoring_profiles']}")
            print(f"   CORS: {'Configured' if index_info['cors_configured'] else 'Not configured'}")
            
            print(f"\n   Field Analysis:")
            for field_type, count in index_info['field_analysis']['types'].items():
                print(f"     {field_type}: {count}")
            
            print(f"\n   Field Attributes:")
            for attr, count in index_info['field_analysis']['attributes'].items():
                print(f"     {attr}: {count}")
            
            return index_info
            
        except Exception as e:
            print(f"❌ Failed to get index info: {str(e)}")
            return None
    
    def _analyze_index_fields(self, fields) -> Dict[str, Any]:
        """Analyze field types and attributes"""
        field_types = {}
        attributes = {
            'key': 0,
            'searchable': 0,
            'filterable': 0,
            'sortable': 0,
            'facetable': 0,
            'retrievable': 0
        }
        
        for field in fields:
            # Count field types
            field_type = str(field.type)
            field_types[field_type] = field_types.get(field_type, 0) + 1
            
            # Count attributes
            if hasattr(field, 'key') and field.key:
                attributes['key'] += 1
            if hasattr(field, 'searchable') and field.searchable:
                attributes['searchable'] += 1
            if hasattr(field, 'filterable') and field.filterable:
                attributes['filterable'] += 1
            if hasattr(field, 'sortable') and field.sortable:
                attributes['sortable'] += 1
            if hasattr(field, 'facetable') and field.facetable:
                attributes['facetable'] += 1
            if hasattr(field, 'retrievable') and field.retrievable:
                attributes['retrievable'] += 1
        
        return {
            'types': field_types,
            'attributes': attributes
        }
    
    def update_index_schema(self, index_name: str, new_field_name: str, new_field_type: str) -> bool:
        """Demonstrate safe schema updates by adding a new field"""
        print(f"🔧 Updating Schema for '{index_name}'...")
        
        try:
            # Get current index
            current_index = self.index_client.get_index(index_name)
            
            # Create new field based on type
            if new_field_type == "string":
                new_field = SimpleField(
                    name=new_field_name,
                    type=SearchFieldDataType.String,
                    filterable=True,
                    retrievable=True
                )
            elif new_field_type == "int":
                new_field = SimpleField(
                    name=new_field_name,
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True,
                    retrievable=True
                )
            elif new_field_type == "double":
                new_field = SimpleField(
                    name=new_field_name,
                    type=SearchFieldDataType.Double,
                    filterable=True,
                    sortable=True,
                    retrievable=True
                )
            elif new_field_type == "boolean":
                new_field = SimpleField(
                    name=new_field_name,
                    type=SearchFieldDataType.Boolean,
                    filterable=True,
                    retrievable=True
                )
            elif new_field_type == "date":
                new_field = SimpleField(
                    name=new_field_name,
                    type=SearchFieldDataType.DateTimeOffset,
                    filterable=True,
                    sortable=True,
                    retrievable=True
                )
            else:
                print(f"❌ Unsupported field type: {new_field_type}")
                return False
            
            # Check if field already exists
            existing_field_names = [f.name for f in current_index.fields]
            if new_field_name in existing_field_names:
                print(f"⚠️  Field '{new_field_name}' already exists")
                return True
            
            # Create updated field list
            updated_fields = list(current_index.fields) + [new_field]
            
            # Create updated index
            updated_index = SearchIndex(
                name=current_index.name,
                fields=updated_fields,
                analyzers=current_index.analyzers,
                scoring_profiles=current_index.scoring_profiles,
                cors_options=current_index.cors_options
            )
            
            # Update the index
            result = self.index_client.create_or_update_index(updated_index)
            
            print(f"✅ Schema updated successfully!")
            print(f"   Added field: {new_field_name} ({new_field_type})")
            print(f"   Total fields: {len(result.fields)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Schema update failed: {str(e)}")
            return False
    
    def demonstrate_document_operations(self, index_name: str) -> bool:
        """Demonstrate various document operations"""
        print(f"📄 Demonstrating Document Operations on '{index_name}'...")
        
        try:
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # 1. Upload new documents
            print("   Step 1: Uploading new documents...")
            new_documents = [
                {
                    "id": "ops-demo-1",
                    "title": "Document Operations Demo 1",
                    "content": "This document demonstrates upload operations.",
                    "author": "Operations Manager",
                    "category": "Demo",
                    "publishedDate": "2024-02-10T10:00:00Z",
                    "tags": ["demo", "operations"],
                    "rating": 4.0,
                    "viewCount": 10,
                    "isPublished": True
                },
                {
                    "id": "ops-demo-2",
                    "title": "Document Operations Demo 2",
                    "content": "This document will be updated in the next step.",
                    "author": "Operations Manager",
                    "category": "Demo",
                    "publishedDate": "2024-02-10T11:00:00Z",
                    "tags": ["demo", "operations"],
                    "rating": 3.5,
                    "viewCount": 5,
                    "isPublished": True
                }
            ]
            
            upload_result = search_client.upload_documents(new_documents)
            successful_uploads = sum(1 for r in upload_result if r.succeeded)
            print(f"   ✅ Uploaded {successful_uploads} documents")
            
            # Wait for indexing
            time.sleep(2)
            
            # 2. Update a document using merge
            print("   Step 2: Updating document using merge...")
            update_document = {
                "id": "ops-demo-2",
                "title": "Document Operations Demo 2 - Updated",
                "rating": 4.5,
                "viewCount": 25
            }
            
            merge_result = search_client.merge_documents([update_document])
            if merge_result[0].succeeded:
                print(f"   ✅ Document merged successfully")
            
            # Wait for indexing
            time.sleep(2)
            
            # 3. Verify the update
            print("   Step 3: Verifying document update...")
            search_results = search_client.search(
                search_text="ops-demo-2",
                select=["id", "title", "rating", "viewCount"]
            )
            
            for result in search_results:
                if result['id'] == 'ops-demo-2':
                    print(f"   📄 Updated document:")
                    print(f"      Title: {result['title']}")
                    print(f"      Rating: {result['rating']}")
                    print(f"      Views: {result['viewCount']}")
                    break
            
            # 4. Delete a document
            print("   Step 4: Deleting a document...")
            delete_result = search_client.delete_documents([{"id": "ops-demo-1"}])
            if delete_result[0].succeeded:
                print(f"   ✅ Document deleted successfully")
            
            # Wait for indexing
            time.sleep(2)
            
            # 5. Verify deletion
            final_count = search_client.get_document_count()
            print(f"   📊 Final document count: {final_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Document operations failed: {str(e)}")
            return False
    
    def monitor_index_health(self, index_names: List[str]) -> Dict[str, Any]:
        """Monitor health and performance of multiple indexes"""
        print("🏥 Monitoring Index Health...")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'service_stats': None,
            'indexes': {}
        }
        
        try:
            # Get service-level statistics
            service_stats = self.index_client.get_service_statistics()
            health_report['service_stats'] = {
                'storage_size': service_stats.storage_size_in_bytes,
                'document_count': service_stats.document_count
            }
            
            print(f"📊 Service Statistics:")
            print(f"   Total Storage: {service_stats.storage_size_in_bytes:,} bytes")
            print(f"   Total Documents: {service_stats.document_count:,}")
            
            # Monitor each index
            for index_name in index_names:
                try:
                    search_client = SearchClient(
                        endpoint=self.endpoint,
                        index_name=index_name,
                        credential=AzureKeyCredential(self.admin_key)
                    )
                    
                    doc_count = search_client.get_document_count()
                    index = self.index_client.get_index(index_name)
                    
                    index_health = {
                        'document_count': doc_count,
                        'field_count': len(index.fields),
                        'status': 'healthy' if doc_count >= 0 else 'unknown'
                    }
                    
                    health_report['indexes'][index_name] = index_health
                    
                    print(f"   📋 {index_name}:")
                    print(f"      Documents: {doc_count}")
                    print(f"      Fields: {len(index.fields)}")
                    print(f"      Status: {index_health['status']}")
                    
                except Exception as e:
                    health_report['indexes'][index_name] = {
                        'error': str(e),
                        'status': 'error'
                    }
                    print(f"   ❌ {index_name}: {str(e)}")
            
            return health_report
            
        except Exception as e:
            print(f"❌ Health monitoring failed: {str(e)}")
            return health_report
    
    def cleanup_test_indexes(self, pattern: str = "test-") -> int:
        """Clean up test indexes matching a pattern"""
        print(f"🧹 Cleaning up test indexes (pattern: '{pattern}')...")
        
        deleted_count = 0
        
        try:
            indexes = list(self.index_client.list_indexes())
            test_indexes = [idx for idx in indexes if pattern in idx.name.lower()]
            
            if not test_indexes:
                print(f"   No indexes found matching pattern '{pattern}'")
                return 0
            
            print(f"   Found {len(test_indexes)} indexes to clean up:")
            for index in test_indexes:
                print(f"     - {index.name}")
            
            # Ask for confirmation
            confirm = input(f"\n   Delete these {len(test_indexes)} indexes? (y/N): ").lower().strip()
            
            if confirm in ['y', 'yes']:
                for index in test_indexes:
                    try:
                        self.index_client.delete_index(index.name)
                        print(f"   ✅ Deleted: {index.name}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ❌ Failed to delete {index.name}: {str(e)}")
            else:
                print("   Cleanup cancelled")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")
            return deleted_count
    
    def create_test_index_for_operations(self) -> str:
        """Create a test index for demonstrating operations"""
        print("🏗️  Creating Test Index for Operations Demo...")
        
        index_name = "operations-demo-index"
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="author", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, filterable=True, sortable=True),
            SimpleField(name="viewCount", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="isPublished", type=SearchFieldDataType.Boolean, filterable=True)
        ]
        
        try:
            index = SearchIndex(name=index_name, fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            print(f"✅ Test index '{result.name}' created successfully")
            return index_name
            
        except Exception as e:
            print(f"❌ Failed to create test index: {str(e)}")
            return None
    
    def compare_indexes(self, index_names: List[str]) -> None:
        """Compare multiple indexes side by side"""
        print("📊 Comparing Indexes...")
        
        if len(index_names) < 2:
            print("❌ Need at least 2 indexes to compare")
            return
        
        comparison_data = []
        
        for index_name in index_names:
            try:
                index_info = self.get_detailed_index_info(index_name)
                if index_info:
                    comparison_data.append(index_info)
            except Exception as e:
                print(f"⚠️  Could not get info for {index_name}: {str(e)}")
        
        if len(comparison_data) < 2:
            print("❌ Could not get enough index information for comparison")
            return
        
        # Display comparison table
        print(f"\n📈 Index Comparison:")
        print("=" * 80)
        
        headers = ["Index Name", "Fields", "Documents", "Analyzers", "Profiles"]
        col_widths = [20, 8, 10, 10, 8]
        
        # Print header
        header_row = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print(header_row)
        print("-" * len(header_row))
        
        # Print data rows
        for data in comparison_data:
            row = [
                data['name'][:19],  # Truncate long names
                str(data['field_count']),
                str(data['document_count']),
                str(data['analyzers']),
                str(data['scoring_profiles'])
            ]
            data_row = " | ".join(val.ljust(w) for val, w in zip(row, col_widths))
            print(data_row)

def main():
    """Main function demonstrating index operations and maintenance"""
    print("=" * 60)
    print("Module 3: Index Operations and Maintenance Example")
    print("=" * 60)
    
    # Initialize the operations manager
    try:
        manager = IndexOperationsManager()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Create clients
    if not manager.create_clients():
        print("❌ Failed to create clients. Exiting.")
        return
    
    # List all indexes
    index_names = manager.list_all_indexes()
    
    if not index_names:
        print("ℹ️  No indexes found. Creating a test index...")
        test_index = manager.create_test_index_for_operations()
        if test_index:
            index_names = [test_index]
        else:
            print("❌ Could not create test index. Exiting.")
            return
    
    # Get detailed info for the first index
    if index_names:
        print(f"\n{'='*20} Detailed Index Information {'='*20}")
        manager.get_detailed_index_info(index_names[0])
    
    # Demonstrate schema update
    print(f"\n{'='*20} Schema Update Demo {'='*20}")
    success = manager.update_index_schema(index_names[0], "lastModified", "date")
    
    if success:
        # Show updated schema
        manager.get_detailed_index_info(index_names[0])
    
    # Demonstrate document operations
    print(f"\n{'='*20} Document Operations Demo {'='*20}")
    manager.demonstrate_document_operations(index_names[0])
    
    # Monitor index health
    print(f"\n{'='*20} Index Health Monitoring {'='*20}")
    health_report = manager.monitor_index_health(index_names[:3])  # Monitor up to 3 indexes
    
    # Compare indexes if we have multiple
    if len(index_names) >= 2:
        print(f"\n{'='*20} Index Comparison {'='*20}")
        manager.compare_indexes(index_names[:3])  # Compare up to 3 indexes
    
    # Optional cleanup
    print(f"\n{'='*20} Cleanup Options {'='*20}")
    cleanup = input("Do you want to clean up test indexes? (y/N): ").lower().strip()
    if cleanup in ['y', 'yes']:
        deleted = manager.cleanup_test_indexes("demo")
        print(f"Cleaned up {deleted} test indexes")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\n📚 What you learned:")
    print("✅ How to perform index lifecycle operations")
    print("✅ How to update index schemas safely")
    print("✅ How to monitor index health and statistics")
    print("✅ How to manage document operations")
    print("✅ How to handle index versioning and maintenance")
    print("✅ How to compare multiple indexes")
    
    print("\n🚀 Next steps:")
    print("1. Try updating schemas with different field types")
    print("2. Implement automated health monitoring")
    print("3. Run the next example: 05_performance_optimization.py")
    print("4. Set up index maintenance schedules")

if __name__ == "__main__":
    main()