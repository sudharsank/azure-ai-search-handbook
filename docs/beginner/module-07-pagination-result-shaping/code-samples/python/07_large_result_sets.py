#!/usr/bin/env python3
"""
Module 7: Pagination & Result Shaping - Large Result Sets
Azure AI Search Python SDK Example

This example demonstrates efficient techniques for handling large result sets in Azure AI Search,
including streaming, batching, parallel processing, and memory management strategies.

Prerequisites:
- Azure AI Search service
- Python 3.7+
- azure-search-documents package
- Sample data index with substantial data
"""

import os
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Iterator, Optional, Callable
from dataclasses import dataclass
from azure.search.documents import SearchClient
from azure.search.documents.aio import SearchClient as AsyncSearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

@dataclass
class ProcessingStats:
    """Statistics for large result set processing"""
    total_processed: int = 0
    total_time_ms: float = 0
    batch_count: int = 0
    errors: int = 0
    memory_peak_mb: float = 0
    throughput_docs_per_sec: float = 0

class LargeResultSetHandler:
    """Comprehensive handler for large result sets"""
    
    def __init__(self, endpoint: str, index_name: str, api_key: str):
        """Initialize the large result set handler"""
        self.client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        self.async_client = AsyncSearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        self.stats = ProcessingStats()
    
    def stream_results(self, query: str, batch_size: int = 100, 
                      max_results: Optional[int] = None,
                      select_fields: Optional[List[str]] = None,
                      progress_callback: Optional[Callable] = None) -> Iterator[Dict[str, Any]]:
        """
        Stream search results in batches for memory-efficient processing
        
        Args:
            query: Search query
            batch_size: Size of each batch
            max_results: Maximum number of results to process
            select_fields: Fields to select for reduced payload
            progress_callback: Optional callback for progress updates
            
        Yields:
            Individual documents from the search results
        """
        print(f"🌊 Starting streaming search for query: '{query}'")
        print(f"📊 Batch size: {batch_size}, Max results: {max_results or 'unlimited'}")
        
        current_skip = 0
        total_processed = 0
        start_time = time.time()
        
        while True:
            # Calculate batch size for this iteration
            if max_results:
                remaining = max_results - total_processed
                if remaining <= 0:
                    break
                current_batch_size = min(batch_size, remaining)
            else:
                current_batch_size = batch_size
            
            batch_start = time.time()
            
            try:
                # Fetch batch
                results = self.client.search(
                    search_text=query,
                    skip=current_skip,
                    top=current_batch_size,
                    select=select_fields
                )
                
                batch_docs = list(results)
                batch_duration = (time.time() - batch_start) * 1000
                
                if not batch_docs:
                    print(f"   🏁 No more results at skip={current_skip}")
                    break
                
                # Yield documents
                for doc in batch_docs:
                    yield dict(doc)
                    total_processed += 1
                
                current_skip += len(batch_docs)
                self.stats.batch_count += 1
                
                # Progress reporting
                if progress_callback:
                    progress_callback(total_processed, batch_duration)
                elif total_processed % (batch_size * 5) == 0:  # Report every 5 batches
                    elapsed = time.time() - start_time
                    rate = total_processed / elapsed if elapsed > 0 else 0
                    print(f"   📦 Processed {total_processed} documents ({rate:.1f} docs/sec)")
                
                # Break if we got fewer results than requested (end of data)
                if len(batch_docs) < current_batch_size:
                    print(f"   🏁 Reached end of available results")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error in batch at skip={current_skip}: {e}")
                self.stats.errors += 1
                break
        
        # Update final statistics
        total_time = (time.time() - start_time) * 1000
        self.stats.total_processed = total_processed
        self.stats.total_time_ms = total_time
        self.stats.throughput_docs_per_sec = total_processed / (total_time / 1000) if total_time > 0 else 0
        
        print(f"✅ Streaming completed: {total_processed} documents in {total_time:.1f}ms")
    
    def batch_process_results(self, query: str, processor_func: Callable,
                            batch_size: int = 100, max_results: Optional[int] = None,
                            parallel: bool = False, max_workers: int = 4) -> List[Any]:
        """
        Process large result sets in batches with optional parallel processing
        
        Args:
            query: Search query
            processor_func: Function to process each batch
            batch_size: Size of each batch
            max_results: Maximum number of results to process
            parallel: Whether to use parallel processing
            max_workers: Number of parallel workers
            
        Returns:
            List of processed results
        """
        print(f"🔄 Starting batch processing for query: '{query}'")
        print(f"📊 Batch size: {batch_size}, Parallel: {parallel}")
        
        # Collect batches
        batches = []
        current_batch = []
        
        for doc in self.stream_results(query, batch_size, max_results, 
                                     select_fields=['hotelId', 'hotelName', 'description']):
            current_batch.append(doc)
            
            if len(current_batch) >= batch_size:
                batches.append(current_batch)
                current_batch = []
        
        # Add remaining documents
        if current_batch:
            batches.append(current_batch)
        
        print(f"📦 Created {len(batches)} batches for processing")
        
        # Process batches
        if parallel and len(batches) > 1:
            return self._process_batches_parallel(batches, processor_func, max_workers)
        else:
            return self._process_batches_sequential(batches, processor_func)
    
    def _process_batches_sequential(self, batches: List[List[Dict]], 
                                  processor_func: Callable) -> List[Any]:
        """Process batches sequentially"""
        results = []
        
        for i, batch in enumerate(batches):
            print(f"   Processing batch {i+1}/{len(batches)} ({len(batch)} documents)")
            
            try:
                batch_result = processor_func(batch)
                results.append(batch_result)
            except Exception as e:
                print(f"   ❌ Error processing batch {i+1}: {e}")
                self.stats.errors += 1
        
        return results
    
    def _process_batches_parallel(self, batches: List[List[Dict]], 
                                processor_func: Callable, max_workers: int) -> List[Any]:
        """Process batches in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(processor_func, batch): i 
                for i, batch in enumerate(batches)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_index = future_to_batch[future]
                
                try:
                    batch_result = future.result()
                    results.append((batch_index, batch_result))
                    print(f"   ✅ Completed batch {batch_index + 1}")
                except Exception as e:
                    print(f"   ❌ Error in batch {batch_index + 1}: {e}")
                    self.stats.errors += 1
        
        # Sort results by batch index to maintain order
        results.sort(key=lambda x: x[0])
        return [result[1] for result in results]
    
    async def async_stream_results(self, query: str, batch_size: int = 100,
                                 max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Asynchronously stream results for better performance
        
        Args:
            query: Search query
            batch_size: Size of each batch
            max_results: Maximum number of results
            
        Returns:
            List of all documents
        """
        print(f"⚡ Starting async streaming for query: '{query}'")
        
        all_documents = []
        current_skip = 0
        total_processed = 0
        
        while True:
            if max_results and total_processed >= max_results:
                break
            
            current_batch_size = batch_size
            if max_results:
                remaining = max_results - total_processed
                current_batch_size = min(batch_size, remaining)
            
            try:
                results = await self.async_client.search(
                    search_text=query,
                    skip=current_skip,
                    top=current_batch_size,
                    select=['hotelId', 'hotelName', 'rating']
                )
                
                batch_docs = []
                async for doc in results:
                    batch_docs.append(dict(doc))
                
                if not batch_docs:
                    break
                
                all_documents.extend(batch_docs)
                total_processed += len(batch_docs)
                current_skip += len(batch_docs)
                
                if len(batch_docs) < current_batch_size:
                    break
                    
            except Exception as e:
                print(f"❌ Async error at skip={current_skip}: {e}")
                break
        
        print(f"✅ Async streaming completed: {len(all_documents)} documents")
        return all_documents
    
    def parallel_range_search(self, base_query: str, ranges: List[Dict[str, str]],
                            batch_size: int = 50) -> Dict[str, List[Dict]]:
        """
        Perform parallel searches across different ranges for large datasets
        
        Args:
            base_query: Base search query
            ranges: List of range filters
            batch_size: Batch size for each range
            
        Returns:
            Dictionary of results by range
        """
        print(f"🔄 Starting parallel range search for query: '{base_query}'")
        print(f"📊 Ranges: {len(ranges)}, Batch size: {batch_size}")
        
        def search_range(range_config):
            """Search a specific range"""
            range_name = range_config['name']
            range_filter = range_config['filter']
            
            try:
                results = self.client.search(
                    search_text=base_query,
                    filter=range_filter,
                    top=batch_size,
                    select=['hotelId', 'hotelName', 'rating']
                )
                
                docs = [dict(doc) for doc in results]
                return range_name, docs
                
            except Exception as e:
                print(f"❌ Error in range {range_name}: {e}")
                return range_name, []
        
        # Execute searches in parallel
        range_results = {}
        
        with ThreadPoolExecutor(max_workers=min(len(ranges), 8)) as executor:
            future_to_range = {
                executor.submit(search_range, range_config): range_config['name']
                for range_config in ranges
            }
            
            for future in as_completed(future_to_range):
                range_name = future_to_range[future]
                
                try:
                    name, docs = future.result()
                    range_results[name] = docs
                    print(f"   ✅ Range '{name}': {len(docs)} results")
                except Exception as e:
                    print(f"   ❌ Range '{range_name}' failed: {e}")
                    range_results[range_name] = []
        
        total_results = sum(len(docs) for docs in range_results.values())
        print(f"✅ Parallel range search completed: {total_results} total results")
        
        return range_results
    
    def memory_efficient_export(self, query: str, output_file: str,
                              batch_size: int = 1000, format: str = 'jsonl') -> Dict[str, Any]:
        """
        Export large result sets to file with memory efficiency
        
        Args:
            query: Search query
            output_file: Output file path
            batch_size: Batch size for processing
            format: Output format ('jsonl' or 'json')
            
        Returns:
            Export statistics
        """
        print(f"💾 Starting memory-efficient export for query: '{query}'")
        print(f"📁 Output file: {output_file}, Format: {format}")
        
        start_time = time.time()
        exported_count = 0
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format == 'json':
                    f.write('[\n')
                
                first_doc = True
                
                for doc in self.stream_results(query, batch_size, 
                                             select_fields=['hotelId', 'hotelName', 'description', 'rating']):
                    if format == 'jsonl':
                        f.write(json.dumps(doc, ensure_ascii=False) + '\n')
                    else:  # json
                        if not first_doc:
                            f.write(',\n')
                        f.write('  ' + json.dumps(doc, ensure_ascii=False))
                        first_doc = False
                    
                    exported_count += 1
                    
                    # Progress reporting
                    if exported_count % 1000 == 0:
                        elapsed = time.time() - start_time
                        rate = exported_count / elapsed if elapsed > 0 else 0
                        print(f"   📝 Exported {exported_count} documents ({rate:.1f} docs/sec)")
                
                if format == 'json':
                    f.write('\n]')
        
        except Exception as e:
            print(f"❌ Export error: {e}")
            return {'error': str(e), 'exported_count': exported_count}
        
        total_time = time.time() - start_time
        file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
        
        stats = {
            'exported_count': exported_count,
            'total_time_seconds': total_time,
            'throughput_docs_per_sec': exported_count / total_time if total_time > 0 else 0,
            'output_file': output_file,
            'file_size_bytes': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'format': format
        }
        
        print(f"✅ Export completed: {exported_count} documents in {total_time:.1f}s")
        print(f"📁 File size: {stats['file_size_mb']:.2f} MB")
        
        return stats
    
    def get_processing_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        return self.stats
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.stats = ProcessingStats()

# Example processor functions
def analyze_sentiment_batch(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Example batch processor: analyze sentiment of descriptions"""
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for doc in batch:
        description = doc.get('description', '').lower()
        
        # Simple sentiment analysis based on keywords
        positive_words = ['excellent', 'amazing', 'wonderful', 'great', 'fantastic']
        negative_words = ['poor', 'bad', 'terrible', 'awful', 'disappointing']
        
        positive_score = sum(1 for word in positive_words if word in description)
        negative_score = sum(1 for word in negative_words if word in description)
        
        if positive_score > negative_score:
            positive_count += 1
        elif negative_score > positive_score:
            negative_count += 1
        else:
            neutral_count += 1
    
    return {
        'batch_size': len(batch),
        'positive': positive_count,
        'negative': negative_count,
        'neutral': neutral_count,
        'sentiment_ratio': positive_count / len(batch) if batch else 0
    }

def extract_keywords_batch(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Example batch processor: extract common keywords"""
    word_counts = {}
    
    for doc in batch:
        description = doc.get('description', '').lower()
        words = description.split()
        
        for word in words:
            # Simple word cleaning
            word = word.strip('.,!?;:"()[]{}')
            if len(word) > 3:  # Only count words longer than 3 characters
                word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top 10 words
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'batch_size': len(batch),
        'unique_words': len(word_counts),
        'top_words': top_words,
        'total_words': sum(word_counts.values())
    }

async def main_async():
    """Async main function for demonstration"""
    endpoint = os.getenv('SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net')
    api_key = os.getenv('SEARCH_API_KEY', 'your-api-key')
    index_name = os.getenv('INDEX_NAME', 'hotels-sample')
    
    handler = LargeResultSetHandler(endpoint, index_name, api_key)
    
    # Async streaming example
    results = await handler.async_stream_results("hotel", batch_size=50, max_results=200)
    print(f"Async results: {len(results)} documents")
    
    await handler.async_client.close()

def main():
    """Main function demonstrating large result set handling"""
    # Configuration
    endpoint = os.getenv('SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net')
    api_key = os.getenv('SEARCH_API_KEY', 'your-api-key')
    index_name = os.getenv('INDEX_NAME', 'hotels-sample')
    
    print("🌊 Azure AI Search - Large Result Sets Handling")
    print("=" * 50)
    
    # Initialize handler
    handler = LargeResultSetHandler(endpoint, index_name, api_key)
    
    # Example 1: Streaming results
    print("\n1. Streaming Results")
    print("-" * 20)
    
    processed_count = 0
    for doc in handler.stream_results("*", batch_size=25, max_results=100):
        processed_count += 1
        if processed_count <= 3:  # Show first 3 documents
            print(f"   Document {processed_count}: {doc.get('hotelName', 'Unknown')}")
    
    print(f"Total streamed: {processed_count} documents")
    
    # Example 2: Batch processing with sentiment analysis
    print("\n2. Batch Processing - Sentiment Analysis")
    print("-" * 40)
    
    sentiment_results = handler.batch_process_results(
        query="hotel",
        processor_func=analyze_sentiment_batch,
        batch_size=20,
        max_results=100,
        parallel=True,
        max_workers=3
    )
    
    if sentiment_results:
        total_positive = sum(r['positive'] for r in sentiment_results)
        total_negative = sum(r['negative'] for r in sentiment_results)
        total_neutral = sum(r['neutral'] for r in sentiment_results)
        total_docs = sum(r['batch_size'] for r in sentiment_results)
        
        print(f"Sentiment analysis results ({total_docs} documents):")
        print(f"  Positive: {total_positive} ({total_positive/total_docs*100:.1f}%)")
        print(f"  Negative: {total_negative} ({total_negative/total_docs*100:.1f}%)")
        print(f"  Neutral: {total_neutral} ({total_neutral/total_docs*100:.1f}%)")
    
    # Example 3: Parallel range search
    print("\n3. Parallel Range Search")
    print("-" * 26)
    
    ranges = [
        {'name': 'High Rating', 'filter': 'rating ge 4'},
        {'name': 'Medium Rating', 'filter': 'rating ge 3 and rating lt 4'},
        {'name': 'Low Rating', 'filter': 'rating lt 3'}
    ]
    
    range_results = handler.parallel_range_search("hotel", ranges, batch_size=30)
    
    for range_name, docs in range_results.items():
        print(f"  {range_name}: {len(docs)} results")
        if docs:
            avg_rating = sum(doc.get('rating', 0) for doc in docs) / len(docs)
            print(f"    Average rating: {avg_rating:.2f}")
    
    # Example 4: Memory-efficient export
    print("\n4. Memory-Efficient Export")
    print("-" * 27)
    
    output_file = "large_results_export.jsonl"
    export_stats = handler.memory_efficient_export(
        query="luxury",
        output_file=output_file,
        batch_size=50,
        format='jsonl'
    )
    
    if 'error' not in export_stats:
        print(f"Export completed:")
        print(f"  Documents: {export_stats['exported_count']}")
        print(f"  File size: {export_stats['file_size_mb']:.2f} MB")
        print(f"  Throughput: {export_stats['throughput_docs_per_sec']:.1f} docs/sec")
        
        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"  Cleaned up: {output_file}")
    
    # Example 5: Async processing
    print("\n5. Async Processing")
    print("-" * 18)
    
    try:
        asyncio.run(main_async())
    except Exception as e:
        print(f"Async processing error: {e}")
    
    # Show final statistics
    print("\n📊 Processing Statistics")
    print("-" * 24)
    
    stats = handler.get_processing_stats()
    print(f"Total processed: {stats.total_processed}")
    print(f"Total batches: {stats.batch_count}")
    print(f"Errors: {stats.errors}")
    print(f"Throughput: {stats.throughput_docs_per_sec:.1f} docs/sec")
    
    print("\n✅ Large result set handling demonstration completed!")

if __name__ == "__main__":
    main()