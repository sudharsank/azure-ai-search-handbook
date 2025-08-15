# Python Examples - Module 7: Pagination & Result Shaping

## Overview

This directory contains comprehensive Python examples demonstrating pagination and result shaping techniques in Azure AI Search using the `azure-search-documents` SDK.

## Prerequisites

### Python Environment
```bash
# Python 3.8 or higher
python --version

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install azure-search-documents
pip install python-dotenv
pip install pandas  # For data analysis examples
pip install matplotlib  # For visualization examples
```

### Environment Configuration
Create a `.env` file in this directory:
```env
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_API_KEY=your-api-key
INDEX_NAME=hotels-sample
```

### Azure AI Search Setup
- Active Azure AI Search service
- Sample data index (hotels-sample recommended)
- Valid API keys and endpoint URLs

## Examples Overview

### Core Pagination Examples
1. **01_basic_pagination.py** - Skip/top pagination fundamentals with error handling
2. **02_field_selection.py** - Field selection optimization and context-based strategies
3. **03_hit_highlighting.py** - Hit highlighting implementation with custom tags
4. **04_result_counting.py** - Smart counting strategies with caching
5. **05_range_pagination.py** - Range-based pagination for large datasets

### Advanced Examples
6. **06_search_after_pattern.py** - Search after pattern for deep pagination
7. **07_advanced_shaping.py** - Combining multiple result shaping techniques
8. **08_performance_optimization.py** - Production-ready pagination with monitoring

## Quick Start

### 1. Basic Usage
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# Initialize client
client = SearchClient(
    endpoint=os.getenv('SEARCH_ENDPOINT'),
    index_name=os.getenv('INDEX_NAME'),
    credential=AzureKeyCredential(os.getenv('SEARCH_API_KEY'))
)

# Basic pagination
results = client.search(
    search_text="luxury",
    skip=0,
    top=10,
    include_total_count=True
)

for result in results:
    print(f"Hotel: {result['hotelName']}, Rating: {result.get('rating', 'N/A')}")
```

### 2. Running Examples
```bash
# Run individual examples
python 01_basic_pagination.py
python 02_field_selection.py

# Run all examples
python run_all_examples.py
```

## Example Details

### 01_basic_pagination.py
**Features:**
- Skip/top pagination implementation
- Page navigation (first, next, previous, last)
- Error handling and validation
- Performance monitoring
- Pagination state management

**Key Classes:**
- `BasicPaginator`: Core pagination functionality
- `PaginationState`: State management
- `PaginationMetrics`: Performance tracking

### 02_field_selection.py
**Features:**
- Field selection optimization
- Context-based field selection
- Response size analysis
- Performance comparison
- Dynamic field selection

**Key Classes:**
- `FieldSelector`: Field selection management
- `FieldSelectionPresets`: Common field combinations
- `ResponseAnalyzer`: Size and performance analysis

### 03_hit_highlighting.py
**Features:**
- Hit highlighting implementation
- Custom highlighting tags
- Multi-field highlighting
- Highlight processing utilities
- Performance optimization

**Key Classes:**
- `HitHighlighter`: Highlighting functionality
- `HighlightProcessor`: Result processing
- `HighlightUtils`: Utility functions

### 04_result_counting.py
**Features:**
- Smart counting strategies
- Count caching
- Performance optimization
- Conditional counting
- Count formatting

**Key Classes:**
- `ResultCounter`: Counting functionality
- `CountCache`: Caching implementation
- `CountingStrategy`: Strategy pattern

### 05_range_pagination.py
**Features:**
- Range-based pagination
- Filter-based navigation
- State management
- Performance optimization
- Large dataset handling

**Key Classes:**
- `RangePaginator`: Range pagination
- `RangeNavigator`: Navigation logic
- `RangeStateManager`: State tracking

## Common Patterns

### Pagination with Error Handling
```python
class SafePaginator:
    def __init__(self, client, page_size=20, max_retries=3):
        self.client = client
        self.page_size = page_size
        self.max_retries = max_retries
    
    async def search_page(self, query, page_number, retry_count=0):
        try:
            results = self.client.search(
                search_text=query,
                skip=page_number * self.page_size,
                top=self.page_size
            )
            return list(results)
        except Exception as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.search_page(query, page_number, retry_count + 1)
            raise e
```

### Field Selection Optimization
```python
class OptimizedFieldSelector:
    PRESETS = {
        'list_view': ['hotelId', 'hotelName', 'rating'],
        'detail_view': ['hotelId', 'hotelName', 'description', 'rating', 'location'],
        'map_view': ['hotelId', 'hotelName', 'location', 'rating']
    }
    
    def search_with_context(self, query, context='list_view', **kwargs):
        fields = self.PRESETS.get(context, self.PRESETS['list_view'])
        return self.client.search(
            search_text=query,
            select=fields,
            **kwargs
        )
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            print(f"{func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"{func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    return wrapper

@monitor_performance
def search_with_monitoring(client, query, **kwargs):
    return list(client.search(search_text=query, **kwargs))
```

## Testing and Validation

### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch

class TestPagination(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.paginator = BasicPaginator(self.mock_client)
    
    def test_basic_pagination(self):
        # Mock search results
        self.mock_client.search.return_value = [
            {'hotelId': '1', 'hotelName': 'Hotel 1'},
            {'hotelId': '2', 'hotelName': 'Hotel 2'}
        ]
        
        result = self.paginator.search_page("test", 0)
        self.assertEqual(len(result), 2)
        self.mock_client.search.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests
```python
def test_integration():
    """Test with real Azure AI Search service"""
    client = SearchClient(endpoint, index_name, credential)
    
    # Test basic search
    results = list(client.search("*", top=5))
    assert len(results) <= 5
    
    # Test pagination
    page1 = list(client.search("*", skip=0, top=5))
    page2 = list(client.search("*", skip=5, top=5))
    
    # Ensure different results (assuming enough data)
    if len(page1) == 5 and len(page2) > 0:
        assert page1[0]['hotelId'] != page2[0]['hotelId']
```

## Performance Optimization

### Async Support
```python
import asyncio
from azure.search.documents.aio import SearchClient as AsyncSearchClient

class AsyncPaginator:
    def __init__(self, client, page_size=20):
        self.client = client
        self.page_size = page_size
    
    async def search_page(self, query, page_number):
        async with self.client:
            results = self.client.search(
                search_text=query,
                skip=page_number * self.page_size,
                top=self.page_size
            )
            return [doc async for doc in results]
    
    async def search_multiple_pages(self, query, page_count):
        tasks = [
            self.search_page(query, page) 
            for page in range(page_count)
        ]
        return await asyncio.gather(*tasks)
```

### Caching Implementation
```python
from functools import lru_cache
import hashlib
import json

class CachedPaginator:
    def __init__(self, client, cache_size=128):
        self.client = client
        self.cache_size = cache_size
    
    def _cache_key(self, query, skip, top, **kwargs):
        """Generate cache key from parameters"""
        params = {'query': query, 'skip': skip, 'top': top, **kwargs}
        key_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def _cached_search(self, cache_key, query, skip, top, **kwargs):
        """Cached search implementation"""
        return list(self.client.search(
            search_text=query,
            skip=skip,
            top=top,
            **kwargs
        ))
    
    def search_page(self, query, page_number, **kwargs):
        skip = page_number * self.page_size
        cache_key = self._cache_key(query, skip, self.page_size, **kwargs)
        return self._cached_search(cache_key, query, skip, self.page_size, **kwargs)
```

## Troubleshooting

### Common Issues

#### Connection Problems
```python
def test_connection():
    try:
        client = SearchClient(endpoint, index_name, credential)
        results = list(client.search("*", top=1))
        print("✅ Connection successful")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
```

#### Rate Limiting
```python
import time
import random

def handle_rate_limiting(func, max_retries=3):
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    continue
                raise e
    return wrapper
```

#### Memory Management
```python
def memory_efficient_pagination(client, query, batch_size=100):
    """Generator for memory-efficient pagination"""
    skip = 0
    while True:
        results = list(client.search(
            search_text=query,
            skip=skip,
            top=batch_size
        ))
        
        if not results:
            break
            
        for result in results:
            yield result
        
        if len(results) < batch_size:
            break
            
        skip += batch_size
```

## Best Practices

### Code Organization
- Use classes for complex pagination logic
- Implement proper error handling
- Add logging for debugging
- Use type hints for better code documentation
- Follow PEP 8 style guidelines

### Performance
- Use appropriate page sizes (10-50 for UI, up to 1000 for APIs)
- Implement caching for frequently accessed data
- Use async operations for concurrent requests
- Monitor and log performance metrics
- Set reasonable timeouts

### Error Handling
- Implement retry logic with exponential backoff
- Handle rate limiting gracefully
- Validate input parameters
- Provide meaningful error messages
- Log errors for debugging

## Contributing

To contribute to these examples:
1. Follow the existing code style
2. Add comprehensive docstrings
3. Include error handling
4. Add unit tests
5. Update documentation

## Next Steps

After exploring these examples:
1. Try the interactive Jupyter notebooks
2. Implement pagination in your application
3. Explore advanced patterns in other modules
4. Contribute improvements and new examples