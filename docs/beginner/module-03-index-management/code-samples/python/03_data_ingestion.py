#!/usr/bin/env python3
"""
Module 3: Index Management - Data Ingestion Strategies
=====================================================

This example demonstrates efficient data ingestion strategies for Azure AI Search.
You'll learn about batch operations, large dataset handling, progress tracking,
and optimization techniques for document uploads.

Learning Objectives:
- Implement single and batch document uploads
- Handle large datasets efficiently
- Optimize batch sizes for performance
- Track upload progress and handle errors
- Use different document actions (upload, merge, delete)

Prerequisites:
- Completed 01_create_basic_index.py and 02_schema_design.py
- Understanding of index schemas
- Azure AI Search service with admin access

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed

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

class DataIngestionManager:
    """Demonstrates advanced data ingestion strategies"""
    
    def __init__(self):
        """Initialize the data ingestion manager"""
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_client = None
        self.search_client = None
        
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
    
    def create_sample_index(self) -> str:
        """Create a sample index for data ingestion testing"""
        print("🏗️  Creating sample index for data ingestion...")
        
        index_name = "data-ingestion-demo"
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="author", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, filterable=True, sortable=True),
            SimpleField(name="viewCount", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            SimpleField(name="isPublished", type=SearchFieldDataType.Boolean, filterable=True)
        ]
        
        try:
            index = SearchIndex(name=index_name, fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            # Create search client for this index
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            print(f"✅ Index '{result.name}' created successfully")
            return index_name
            
        except Exception as e:
            print(f"❌ Failed to create index: {str(e)}")
            return None
    
    def single_document_upload(self) -> bool:
        """Demonstrate single document upload"""
        print("📄 Single Document Upload Example...")
        
        try:
            # Create a single document
            document = {
                "id": "single-doc-1",
                "title": "Single Document Upload Example",
                "content": "This document demonstrates how to upload a single document to Azure AI Search.",
                "category": "Tutorial",
                "author": "Data Ingestion Manager",
                "publishedDate": "2024-02-10T10:00:00Z",
                "rating": 4.5,
                "viewCount": 100,
                "tags": ["tutorial", "single-upload", "example"],
                "isPublished": True
            }
            
            # Upload the document
            start_time = time.time()
            result = self.search_client.upload_documents([document])
            upload_time = time.time() - start_time
            
            if result[0].succeeded:
                print(f"✅ Document uploaded successfully in {upload_time:.3f} seconds")
                print(f"   Document ID: {result[0].key}")
                return True
            else:
                print(f"❌ Upload failed: {result[0].error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Single document upload failed: {str(e)}")
            return False
    
    def batch_document_upload(self, batch_size: int = 10) -> bool:
        """Demonstrate batch document upload"""
        print(f"📦 Batch Document Upload Example (batch size: {batch_size})...")
        
        try:
            # Generate sample documents
            documents = self._generate_sample_documents(batch_size)
            
            # Upload documents in batch
            start_time = time.time()
            result = self.search_client.upload_documents(documents)
            upload_time = time.time() - start_time
            
            # Analyze results
            successful = sum(1 for r in result if r.succeeded)
            failed = len(result) - successful
            
            print(f"✅ Batch upload completed in {upload_time:.3f} seconds")
            print(f"   Successful: {successful}/{len(documents)}")
            print(f"   Failed: {failed}")
            print(f"   Rate: {successful/upload_time:.1f} documents/second")
            
            # Show any failures
            for r in result:
                if not r.succeeded:
                    print(f"   ❌ Failed: {r.key} - {r.error_message}")
            
            return successful > 0
            
        except Exception as e:
            print(f"❌ Batch upload failed: {str(e)}")
            return False
    
    def large_dataset_upload(self, total_documents: int = 1000, batch_size: int = 100) -> bool:
        """Demonstrate large dataset upload with progress tracking"""
        print(f"🗂️  Large Dataset Upload Example ({total_documents} documents, batch size: {batch_size})...")
        
        try:
            total_successful = 0
            total_failed = 0
            total_time = 0
            
            # Process in batches
            for batch_num in range(0, total_documents, batch_size):
                current_batch_size = min(batch_size, total_documents - batch_num)
                
                # Generate batch documents
                documents = self._generate_sample_documents(
                    current_batch_size, 
                    start_id=batch_num + 1
                )
                
                # Upload batch
                start_time = time.time()
                result = self.search_client.upload_documents(documents)
                batch_time = time.time() - start_time
                total_time += batch_time
                
                # Track results
                successful = sum(1 for r in result if r.succeeded)
                failed = len(result) - successful
                
                total_successful += successful
                total_failed += failed
                
                # Progress update
                progress = ((batch_num + current_batch_size) / total_documents) * 100
                rate = successful / batch_time if batch_time > 0 else 0
                
                print(f"   Batch {batch_num//batch_size + 1}: {successful}/{current_batch_size} uploaded "
                      f"({rate:.1f} docs/sec) - Progress: {progress:.1f}%")
                
                # Brief pause to avoid overwhelming the service
                if batch_num + batch_size < total_documents:
                    time.sleep(0.1)
            
            # Final summary
            overall_rate = total_successful / total_time if total_time > 0 else 0
            print(f"\n✅ Large dataset upload completed:")
            print(f"   Total successful: {total_successful}")
            print(f"   Total failed: {total_failed}")
            print(f"   Total time: {total_time:.2f} seconds")
            print(f"   Overall rate: {overall_rate:.1f} documents/second")
            
            return total_successful > 0
            
        except Exception as e:
            print(f"❌ Large dataset upload failed: {str(e)}")
            return False
    
    def parallel_upload(self, total_documents: int = 500, batch_size: int = 50, max_workers: int = 4) -> bool:
        """Demonstrate parallel upload for improved performance"""
        print(f"⚡ Parallel Upload Example ({total_documents} documents, {max_workers} workers)...")
        
        try:
            # Create batches
            batches = []
            for batch_num in range(0, total_documents, batch_size):
                current_batch_size = min(batch_size, total_documents - batch_num)
                documents = self._generate_sample_documents(
                    current_batch_size, 
                    start_id=batch_num + 10000  # Different ID range to avoid conflicts
                )
                batches.append((batch_num // batch_size + 1, documents))
            
            # Upload batches in parallel
            start_time = time.time()
            total_successful = 0
            total_failed = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all batch upload tasks
                future_to_batch = {
                    executor.submit(self._upload_batch, batch_num, documents): (batch_num, documents)
                    for batch_num, documents in batches
                }
                
                # Process completed tasks
                for future in as_completed(future_to_batch):
                    batch_num, documents = future_to_batch[future]
                    try:
                        successful, failed = future.result()
                        total_successful += successful
                        total_failed += failed
                        
                        rate = successful / 1.0  # Approximate rate per batch
                        print(f"   Batch {batch_num}: {successful}/{len(documents)} uploaded ({rate:.1f} docs/sec)")
                        
                    except Exception as e:
                        print(f"   ❌ Batch {batch_num} failed: {str(e)}")
                        total_failed += len(documents)
            
            total_time = time.time() - start_time
            overall_rate = total_successful / total_time if total_time > 0 else 0
            
            print(f"\n✅ Parallel upload completed:")
            print(f"   Total successful: {total_successful}")
            print(f"   Total failed: {total_failed}")
            print(f"   Total time: {total_time:.2f} seconds")
            print(f"   Overall rate: {overall_rate:.1f} documents/second")
            print(f"   Workers used: {max_workers}")
            
            return total_successful > 0
            
        except Exception as e:
            print(f"❌ Parallel upload failed: {str(e)}")
            return False
    
    def _upload_batch(self, batch_num: int, documents: List[Dict[str, Any]]) -> tuple:
        """Upload a single batch (used by parallel upload)"""
        try:
            result = self.search_client.upload_documents(documents)
            successful = sum(1 for r in result if r.succeeded)
            failed = len(result) - successful
            return successful, failed
        except Exception:
            return 0, len(documents)
    
    def document_operations_demo(self) -> bool:
        """Demonstrate different document operations (upload, merge, delete)"""
        print("🔄 Document Operations Demo (Upload, Merge, Delete)...")
        
        try:
            # 1. Upload initial documents
            print("   Step 1: Uploading initial documents...")
            initial_docs = [
                {
                    "id": "ops-doc-1",
                    "title": "Original Title 1",
                    "content": "Original content for document 1",
                    "category": "Original",
                    "author": "Original Author",
                    "publishedDate": "2024-02-10T10:00:00Z",
                    "rating": 3.0,
                    "viewCount": 50,
                    "tags": ["original"],
                    "isPublished": True
                },
                {
                    "id": "ops-doc-2",
                    "title": "Original Title 2",
                    "content": "Original content for document 2",
                    "category": "Original",
                    "author": "Original Author",
                    "publishedDate": "2024-02-10T11:00:00Z",
                    "rating": 3.5,
                    "viewCount": 75,
                    "tags": ["original"],
                    "isPublished": True
                }
            ]
            
            upload_result = self.search_client.upload_documents(initial_docs)
            successful_uploads = sum(1 for r in upload_result if r.succeeded)
            print(f"   ✅ Uploaded {successful_uploads} initial documents")
            
            # Wait for indexing
            time.sleep(2)
            
            # 2. Merge operation (partial update)
            print("   Step 2: Merging document updates...")
            merge_docs = [
                {
                    "id": "ops-doc-1",
                    "title": "Updated Title 1",  # Update title
                    "rating": 4.5,  # Update rating
                    "viewCount": 150  # Update view count
                    # Other fields remain unchanged
                }
            ]
            
            merge_result = self.search_client.merge_documents(merge_docs)
            successful_merges = sum(1 for r in merge_result if r.succeeded)
            print(f"   ✅ Merged {successful_merges} document updates")
            
            # 3. Merge or upload operation (upsert)
            print("   Step 3: Merge or upload (upsert) operation...")
            upsert_docs = [
                {
                    "id": "ops-doc-3",  # New document
                    "title": "New Document via Upsert",
                    "content": "This document was created via merge_or_upload",
                    "category": "Upsert",
                    "author": "Upsert Author",
                    "publishedDate": "2024-02-10T12:00:00Z",
                    "rating": 4.0,
                    "viewCount": 25,
                    "tags": ["upsert", "new"],
                    "isPublished": True
                },
                {
                    "id": "ops-doc-2",  # Existing document - will be merged
                    "content": "Updated content for document 2",
                    "rating": 4.8
                }
            ]
            
            upsert_result = self.search_client.merge_or_upload_documents(upsert_docs)
            successful_upserts = sum(1 for r in upsert_result if r.succeeded)
            print(f"   ✅ Upserted {successful_upserts} documents")
            
            # Wait for indexing
            time.sleep(2)
            
            # 4. Verify current state
            print("   Step 4: Verifying current document state...")
            doc_count = self.search_client.get_document_count()
            print(f"   📊 Current document count: {doc_count}")
            
            # 5. Delete operation
            print("   Step 5: Deleting a document...")
            delete_docs = [{"id": "ops-doc-2"}]
            
            delete_result = self.search_client.delete_documents(delete_docs)
            successful_deletes = sum(1 for r in delete_result if r.succeeded)
            print(f"   ✅ Deleted {successful_deletes} documents")
            
            # Wait for indexing
            time.sleep(2)
            
            # 6. Final verification
            final_count = self.search_client.get_document_count()
            print(f"   📊 Final document count: {final_count}")
            
            print("✅ Document operations demo completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Document operations demo failed: {str(e)}")
            return False
    
    def batch_size_optimization_test(self) -> None:
        """Test different batch sizes to find optimal performance"""
        print("📊 Batch Size Optimization Test...")
        
        batch_sizes = [10, 50, 100, 200, 500]
        test_results = []
        
        for batch_size in batch_sizes:
            print(f"\n   Testing batch size: {batch_size}")
            
            try:
                # Generate test documents
                documents = self._generate_sample_documents(
                    batch_size, 
                    start_id=batch_size * 1000  # Unique ID range for each test
                )
                
                # Measure upload time
                start_time = time.time()
                result = self.search_client.upload_documents(documents)
                upload_time = time.time() - start_time
                
                successful = sum(1 for r in result if r.succeeded)
                rate = successful / upload_time if upload_time > 0 else 0
                
                test_results.append({
                    'batch_size': batch_size,
                    'successful': successful,
                    'time': upload_time,
                    'rate': rate
                })
                
                print(f"   ✅ {successful}/{batch_size} uploaded in {upload_time:.3f}s ({rate:.1f} docs/sec)")
                
                # Brief pause between tests
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)}")
                test_results.append({
                    'batch_size': batch_size,
                    'successful': 0,
                    'time': 0,
                    'rate': 0
                })
        
        # Display results summary
        print(f"\n📈 Batch Size Optimization Results:")
        print(f"{'Batch Size':<12} | {'Success Rate':<12} | {'Time (s)':<10} | {'Rate (docs/s)':<15}")
        print("-" * 60)
        
        best_rate = 0
        best_batch_size = 0
        
        for result in test_results:
            success_rate = (result['successful'] / result['batch_size']) * 100 if result['batch_size'] > 0 else 0
            print(f"{result['batch_size']:<12} | {success_rate:<12.1f} | {result['time']:<10.3f} | {result['rate']:<15.1f}")
            
            if result['rate'] > best_rate:
                best_rate = result['rate']
                best_batch_size = result['batch_size']
        
        if best_batch_size > 0:
            print(f"\n🏆 Optimal batch size: {best_batch_size} (rate: {best_rate:.1f} docs/sec)")
        else:
            print(f"\n⚠️  Could not determine optimal batch size")
    
    def _generate_sample_documents(self, count: int, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate sample documents for testing"""
        documents = []
        categories = ["Technology", "Science", "Business", "Health", "Education"]
        authors = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eve Brown"]
        
        for i in range(count):
            doc_id = start_id + i
            category = categories[i % len(categories)]
            author = authors[i % len(authors)]
            
            document = {
                "id": f"doc-{doc_id}",
                "title": f"Sample Document {doc_id}: {category} Article",
                "content": f"This is sample content for document {doc_id}. It contains information about {category.lower()} topics and is written by {author}. The content is generated for testing purposes and demonstrates various aspects of the subject matter.",
                "category": category,
                "author": author,
                "publishedDate": f"2024-02-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z",
                "rating": round(3.0 + (i % 20) * 0.1, 1),  # Rating between 3.0 and 5.0
                "viewCount": (i + 1) * 10 + (i % 100),
                "tags": [category.lower(), "sample", f"tag{i % 5}"],
                "isPublished": i % 10 != 0  # 90% published
            }
            documents.append(document)
        
        return documents
    
    def get_ingestion_statistics(self) -> None:
        """Display current index statistics"""
        print("📊 Current Index Statistics:")
        
        try:
            doc_count = self.search_client.get_document_count()
            print(f"   Total documents: {doc_count}")
            
            # Sample some documents to show variety
            results = self.search_client.search(
                search_text="*",
                top=5,
                select=["id", "title", "category", "author"]
            )
            
            print(f"   Sample documents:")
            for result in results:
                print(f"     - {result.get('id')}: {result.get('title')} ({result.get('category')})")
                
        except Exception as e:
            print(f"❌ Failed to get statistics: {str(e)}")
    
    def cleanup_test_data(self) -> bool:
        """Clean up test data from the index"""
        print("🧹 Cleaning up test data...")
        
        try:
            # Get all documents
            results = self.search_client.search(
                search_text="*",
                select=["id"],
                top=10000  # Adjust based on your test data size
            )
            
            # Collect document IDs
            doc_ids = [{"id": result["id"]} for result in results]
            
            if doc_ids:
                # Delete in batches
                batch_size = 100
                total_deleted = 0
                
                for i in range(0, len(doc_ids), batch_size):
                    batch = doc_ids[i:i + batch_size]
                    result = self.search_client.delete_documents(batch)
                    successful = sum(1 for r in result if r.succeeded)
                    total_deleted += successful
                
                print(f"✅ Deleted {total_deleted} test documents")
                return True
            else:
                print("ℹ️  No documents to delete")
                return True
                
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")
            return False

def main():
    """Main function demonstrating data ingestion strategies"""
    print("=" * 60)
    print("Module 3: Data Ingestion Strategies Example")
    print("=" * 60)
    
    # Initialize the data ingestion manager
    try:
        manager = DataIngestionManager()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Create clients
    if not manager.create_clients():
        print("❌ Failed to create clients. Exiting.")
        return
    
    # Create sample index
    index_name = manager.create_sample_index()
    if not index_name:
        print("❌ Failed to create sample index. Exiting.")
        return
    
    print(f"\n🎯 Running data ingestion demonstrations on index '{index_name}'...")
    
    # Run demonstrations
    demonstrations = [
        ("Single Document Upload", manager.single_document_upload),
        ("Batch Document Upload", lambda: manager.batch_document_upload(50)),
        ("Large Dataset Upload", lambda: manager.large_dataset_upload(200, 50)),
        ("Parallel Upload", lambda: manager.parallel_upload(200, 25, 3)),
        ("Document Operations", manager.document_operations_demo),
    ]
    
    for demo_name, demo_func in demonstrations:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            success = demo_func()
            if success:
                print(f"✅ {demo_name} completed successfully")
            else:
                print(f"⚠️  {demo_name} completed with issues")
        except Exception as e:
            print(f"❌ {demo_name} failed: {str(e)}")
        
        # Brief pause between demonstrations
        time.sleep(1)
    
    # Show current statistics
    print(f"\n{'='*20} Current Statistics {'='*20}")
    manager.get_ingestion_statistics()
    
    # Optional: Batch size optimization test
    run_optimization = input("\nRun batch size optimization test? (y/N): ").lower().strip()
    if run_optimization in ['y', 'yes']:
        print(f"\n{'='*20} Batch Size Optimization {'='*20}")
        manager.batch_size_optimization_test()
    
    # Optional: Cleanup
    cleanup = input(f"\nClean up test data from index '{index_name}'? (y/N): ").lower().strip()
    if cleanup in ['y', 'yes']:
        manager.cleanup_test_data()
        
        # Optional: Delete the test index
        delete_index = input(f"Delete the test index '{index_name}'? (y/N): ").lower().strip()
        if delete_index in ['y', 'yes']:
            try:
                manager.index_client.delete_index(index_name)
                print(f"✅ Index '{index_name}' deleted successfully")
            except Exception as e:
                print(f"❌ Failed to delete index: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\n📚 What you learned:")
    print("✅ How to implement single and batch document uploads")
    print("✅ How to handle large datasets efficiently")
    print("✅ How to optimize batch sizes for performance")
    print("✅ How to track upload progress and handle errors")
    print("✅ How to use different document actions (upload, merge, delete)")
    print("✅ How to implement parallel upload strategies")
    
    print("\n🚀 Next steps:")
    print("1. Try ingesting your own data")
    print("2. Experiment with different batch sizes for your use case")
    print("3. Run the next example: 04_index_operations.py")
    print("4. Implement error handling and retry logic for production")

if __name__ == "__main__":
    main()