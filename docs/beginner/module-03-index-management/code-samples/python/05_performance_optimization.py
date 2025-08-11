#!/usr/bin/env python3
"""
Module 3: Index Management - Performance Optimization
====================================================

This example demonstrates performance optimization techniques for Azure AI Search
index management, including batch sizing, parallel operations, and monitoring.

Learning Objectives:
- Optimize batch sizes for different document types
- Implement parallel upload strategies
- Monitor and measure performance metrics
- Apply performance best practices
- Handle memory and resource management

Prerequisites:
- Completed previous examples (01-04)
- Understanding of data ingestion and index operations
- Azure AI Search service with admin access

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex, SimpleField, SearchableField, SearchFieldDataType
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

class PerformanceOptimizer:
    """Demonstrates performance optimization techniques"""
    
    def __init__(self):
        """Initialize the performance optimizer"""
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
    
    def create_performance_test_index(self) -> str:
        """Create an index optimized for performance testing"""
        print("🏗️  Creating Performance Test Index...")
        
        index_name = "performance-test-index"
        
        # Optimized field configuration
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String, retrievable=False),  # Don't retrieve large content
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, filterable=True, sortable=True),
            SimpleField(name="viewCount", type=SearchFieldDataType.Int32, filterable=True, sortable=True)
        ]
        
        try:
            index = SearchIndex(name=index_name, fields=fields)
            result = self.index_client.create_or_update_index(index)
            print(f"✅ Performance test index '{result.name}' created")
            return index_name
        except Exception as e:
            print(f"❌ Failed to create performance test index: {str(e)}")
            return None
    
    def test_batch_sizes(self, index_name: str) -> Dict[int, Dict[str, float]]:
        """Test different batch sizes to find optimal performance"""
        print("📊 Testing Batch Size Performance...")
        
        batch_sizes = [10, 50, 100, 200, 500]
        results = {}
        
        search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(self.admin_key)
        )
        
        for batch_size in batch_sizes:
            print(f"\n   Testing batch size: {batch_size}")
            
            # Generate test documents
            documents = self._generate_test_documents(batch_size, f"batch-{batch_size}")
            
            try:
                # Measure upload time
                start_time = time.time()
                result = search_client.upload_documents(documents)
                upload_time = time.time() - start_time
                
                successful = sum(1 for r in result if r.succeeded)
                rate = successful / upload_time if upload_time > 0 else 0
                
                results[batch_size] = {
                    'upload_time': upload_time,
                    'successful': successful,
                    'rate': rate,
                    'success_rate': (successful / len(documents)) * 100
                }
                
                print(f"   ✅ {successful}/{len(documents)} uploaded in {upload_time:.3f}s ({rate:.1f} docs/sec)")
                
                # Brief pause between tests
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)}")
                results[batch_size] = {'error': str(e)}
        
        # Display results summary
        self._display_batch_size_results(results)
        return results
    
    def _display_batch_size_results(self, results: Dict[int, Dict[str, float]]) -> None:
        """Display batch size test results in a formatted table"""
        print(f"\n📈 Batch Size Performance Results:")
        print(f"{'Batch Size':<12} | {'Time (s)':<10} | {'Rate (docs/s)':<15} | {'Success %':<10}")
        print("-" * 60)
        
        best_rate = 0
        best_batch_size = 0
        
        for batch_size, data in results.items():
            if 'error' not in data:
                print(f"{batch_size:<12} | {data['upload_time']:<10.3f} | {data['rate']:<15.1f} | {data['success_rate']:<10.1f}")
                
                if data['rate'] > best_rate:
                    best_rate = data['rate']
                    best_batch_size = batch_size
            else:
                print(f"{batch_size:<12} | {'ERROR':<10} | {'N/A':<15} | {'N/A':<10}")
        
        if best_batch_size > 0:
            print(f"\n🏆 Optimal batch size: {best_batch_size} (rate: {best_rate:.1f} docs/sec)")
    
    def test_parallel_uploads(self, index_name: str, total_docs: int = 1000) -> Dict[str, Any]:
        """Test parallel upload performance with different worker counts"""
        print(f"⚡ Testing Parallel Upload Performance ({total_docs} documents)...")
        
        worker_counts = [1, 2, 4, 8]
        batch_size = 100  # Use optimal batch size from previous test
        results = {}
        
        for workers in worker_counts:
            print(f"\n   Testing with {workers} workers...")
            
            try:
                start_time = time.time()
                successful, failed = self._parallel_upload_test(index_name, total_docs, batch_size, workers)
                total_time = time.time() - start_time
                
                rate = successful / total_time if total_time > 0 else 0
                
                results[workers] = {
                    'total_time': total_time,
                    'successful': successful,
                    'failed': failed,
                    'rate': rate,
                    'efficiency': rate / workers  # Rate per worker
                }
                
                print(f"   ✅ {successful}/{total_docs} uploaded in {total_time:.2f}s ({rate:.1f} docs/sec)")
                print(f"      Efficiency: {results[workers]['efficiency']:.1f} docs/sec per worker")
                
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)}")
                results[workers] = {'error': str(e)}
        
        self._display_parallel_results(results)
        return results
    
    def _parallel_upload_test(self, index_name: str, total_docs: int, batch_size: int, workers: int) -> tuple:
        """Perform parallel upload test"""
        search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(self.admin_key)
        )
        
        # Create batches
        batches = []
        for i in range(0, total_docs, batch_size):
            current_batch_size = min(batch_size, total_docs - i)
            documents = self._generate_test_documents(current_batch_size, f"parallel-{workers}-{i}")
            batches.append(documents)
        
        total_successful = 0
        total_failed = 0
        
        # Upload batches in parallel
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_batch = {
                executor.submit(search_client.upload_documents, batch): batch
                for batch in batches
            }
            
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    result = future.result()
                    successful = sum(1 for r in result if r.succeeded)
                    failed = len(batch) - successful
                    
                    total_successful += successful
                    total_failed += failed
                    
                except Exception as e:
                    total_failed += len(batch)
        
        return total_successful, total_failed
    
    def _display_parallel_results(self, results: Dict[str, Any]) -> None:
        """Display parallel upload test results"""
        print(f"\n📈 Parallel Upload Performance Results:")
        print(f"{'Workers':<8} | {'Time (s)':<10} | {'Rate (docs/s)':<15} | {'Efficiency':<12}")
        print("-" * 55)
        
        best_rate = 0
        best_workers = 0
        
        for workers, data in results.items():
            if 'error' not in data:
                print(f"{workers:<8} | {data['total_time']:<10.2f} | {data['rate']:<15.1f} | {data['efficiency']:<12.1f}")
                
                if data['rate'] > best_rate:
                    best_rate = data['rate']
                    best_workers = workers
            else:
                print(f"{workers:<8} | {'ERROR':<10} | {'N/A':<15} | {'N/A':<12}")
        
        if best_workers > 0:
            print(f"\n🏆 Optimal worker count: {best_workers} (rate: {best_rate:.1f} docs/sec)")
    
    def monitor_memory_usage(self, index_name: str, document_count: int) -> Dict[str, Any]:
        """Monitor memory usage during large uploads"""
        print(f"🧠 Monitoring Memory Usage ({document_count} documents)...")
        
        import psutil
        import gc
        
        process = psutil.Process()
        memory_stats = {
            'initial_memory': process.memory_info().rss / 1024 / 1024,  # MB
            'peak_memory': 0,
            'final_memory': 0,
            'memory_growth': 0
        }
        
        search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(self.admin_key)
        )
        
        try:
            batch_size = 100
            batches_processed = 0
            
            for i in range(0, document_count, batch_size):
                current_batch_size = min(batch_size, document_count - i)
                documents = self._generate_test_documents(current_batch_size, f"memory-{i}")
                
                # Upload batch
                result = search_client.upload_documents(documents)
                batches_processed += 1
                
                # Monitor memory
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_stats['peak_memory'] = max(memory_stats['peak_memory'], current_memory)
                
                # Force garbage collection every 10 batches
                if batches_processed % 10 == 0:
                    gc.collect()
                    print(f"   Processed {batches_processed} batches, Memory: {current_memory:.1f} MB")
            
            memory_stats['final_memory'] = process.memory_info().rss / 1024 / 1024
            memory_stats['memory_growth'] = memory_stats['final_memory'] - memory_stats['initial_memory']
            
            print(f"\n📊 Memory Usage Summary:")
            print(f"   Initial Memory: {memory_stats['initial_memory']:.1f} MB")
            print(f"   Peak Memory: {memory_stats['peak_memory']:.1f} MB")
            print(f"   Final Memory: {memory_stats['final_memory']:.1f} MB")
            print(f"   Memory Growth: {memory_stats['memory_growth']:.1f} MB")
            
            return memory_stats
            
        except Exception as e:
            print(f"❌ Memory monitoring failed: {str(e)}")
            return memory_stats
    
    def _generate_test_documents(self, count: int, prefix: str) -> List[Dict[str, Any]]:
        """Generate test documents for performance testing"""
        documents = []
        categories = ["Tech", "Science", "Business", "Health", "Education"]
        
        for i in range(count):
            doc = {
                "id": f"{prefix}-{i}",
                "title": f"Performance Test Document {i}",
                "content": f"This is test content for document {i}. " * 10,  # Moderate content size
                "category": categories[i % len(categories)],
                "publishedDate": f"2024-02-{(i % 28) + 1:02d}T10:00:00Z",
                "rating": 3.0 + (i % 20) * 0.1,
                "viewCount": (i + 1) * 5
            }
            documents.append(doc)
        
        return documents
    
    def performance_recommendations(self, batch_results: Dict, parallel_results: Dict) -> None:
        """Provide performance recommendations based on test results"""
        print("\n💡 Performance Recommendations:")
        print("=" * 50)
        
        # Batch size recommendations
        if batch_results:
            best_batch = max(batch_results.keys(), key=lambda k: batch_results[k].get('rate', 0))
            print(f"✅ Optimal Batch Size: {best_batch}")
            print(f"   Achieves {batch_results[best_batch]['rate']:.1f} documents/second")
        
        # Parallel processing recommendations
        if parallel_results:
            best_workers = max(parallel_results.keys(), key=lambda k: parallel_results[k].get('rate', 0))
            print(f"✅ Optimal Worker Count: {best_workers}")
            print(f"   Achieves {parallel_results[best_workers]['rate']:.1f} documents/second")
        
        print(f"\n📋 General Best Practices:")
        print(f"   • Use batch sizes between 100-500 documents")
        print(f"   • Implement parallel processing for large datasets")
        print(f"   • Monitor memory usage and implement garbage collection")
        print(f"   • Use retrievable=False for large content fields")
        print(f"   • Minimize the number of sortable and facetable fields")
        print(f"   • Consider using merge operations instead of full uploads")

def main():
    """Main function demonstrating performance optimization"""
    print("=" * 60)
    print("Module 3: Performance Optimization Example")
    print("=" * 60)
    
    # Initialize the performance optimizer
    try:
        optimizer = PerformanceOptimizer()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Create clients
    if not optimizer.create_clients():
        print("❌ Failed to create clients. Exiting.")
        return
    
    # Create performance test index
    index_name = optimizer.create_performance_test_index()
    if not index_name:
        print("❌ Failed to create test index. Exiting.")
        return
    
    # Test batch sizes
    print(f"\n{'='*20} Batch Size Optimization {'='*20}")
    batch_results = optimizer.test_batch_sizes(index_name)
    
    # Test parallel uploads
    print(f"\n{'='*20} Parallel Upload Testing {'='*20}")
    parallel_results = optimizer.test_parallel_uploads(index_name, 500)
    
    # Monitor memory usage
    print(f"\n{'='*20} Memory Usage Monitoring {'='*20}")
    try:
        import psutil
        memory_stats = optimizer.monitor_memory_usage(index_name, 200)
    except ImportError:
        print("⚠️  psutil not installed. Skipping memory monitoring.")
        print("   Install with: pip install psutil")
    
    # Provide recommendations
    optimizer.performance_recommendations(batch_results, parallel_results)
    
    # Cleanup
    cleanup = input(f"\nDelete the performance test index '{index_name}'? (y/N): ").lower().strip()
    if cleanup in ['y', 'yes']:
        try:
            optimizer.index_client.delete_index(index_name)
            print(f"✅ Index '{index_name}' deleted successfully")
        except Exception as e:
            print(f"❌ Failed to delete index: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\n📚 What you learned:")
    print("✅ How to optimize batch sizes for different document types")
    print("✅ How to implement parallel upload strategies")
    print("✅ How to monitor and measure performance metrics")
    print("✅ How to apply performance best practices")
    print("✅ How to handle memory and resource management")
    
    print("\n🚀 Next steps:")
    print("1. Apply optimal settings to your production indexes")
    print("2. Implement performance monitoring in your applications")
    print("3. Run the next example: 06_error_handling.py")
    print("4. Set up automated performance testing")

if __name__ == "__main__":
    main()