# Python Examples - Filters & Sorting

## Overview

This directory contains Python examples for implementing filters and sorting in Azure AI Search using the `azure-search-documents` SDK. The examples demonstrate various filtering techniques, sorting strategies, and performance optimization approaches.

## Prerequisites

### Python Environment
- Python 3.7 or higher
- pip package manager

### Required Packages
```bash
pip install azure-search-documents
pip install python-dotenv
pip install azure-identity
```

### Azure Resources
- Azure AI Search service
- Search index with filterable and sortable fields
- Sample data for testing

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your Azure credentials:
```bash
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-admin-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
INDEX_NAME=your-index-name
```

### 3. Verify Setup
Run the setup verification script:
```bash
python verify_setup.py
```

## Examples

### 01 - Basic Filters
**File:** `01_basic_filters.py`

Demonstrates:
- Equality filters (`eq`, `ne`)
- Comparison filters (`gt`, `ge`, `lt`, `le`)
- Boolean logic combinations (`and`, `or`, `not`)
- Null value handling

### 02 - Range Filters
**File:** `02_range_filters.py`

Demonstrates:
- Numeric range filtering
- Date range filtering
- Price range implementations
- Performance optimization techniques

### 03 - String Filters
**File:** `03_string_filters.py`

Demonstrates:
- Text matching with `startswith`, `endswith`, `contains`
- Case sensitivity handling
- Pattern matching techniques
- Multi-language considerations

### 04 - Date Filters
**File:** `04_date_filters.py`

Demonstrates:
- Date range filtering
- Relative date calculations
- Time zone handling
- Date format considerations

### 05 - Geographic Filters
**File:** `05_geographic_filters.py`

Demonstrates:
- Distance-based filtering with `geo.distance()`
- Geographic bounds and coordinate systems
- Location data analysis and visualization
- Spatial query performance optimization
- Multi-point geographic filtering
- Coordinate validation and error handling

### 06 - Sorting Operations
**File:** `06_sorting_operations.py`

Demonstrates:
- Single field sorting
- Multi-field sorting
- Custom sort orders
- Performance optimization

### 07 - Complex Filters
**File:** `07_complex_filters.py`

Demonstrates:
- Collection filtering with `any()` and `all()` functions
- Nested condition optimization
- Advanced logical combinations
- Filter logic tree building
- Complex filter validation and syntax checking
- Performance analysis for complex expressions
- Real-world complex filtering scenarios

### 08 - Performance Analysis
**File:** `08_performance_analysis.py`

Demonstrates:
- Real-time query performance monitoring
- Filter optimization strategies
- Resource usage pattern analysis
- Optimization recommendations generation
- Scalability planning and bottleneck identification
- Comparative analysis of filtering approaches
- Performance benchmarking and reporting

## Running Examples

### Individual Examples
```bash
python 01_basic_filters.py
python 02_range_filters.py
# ... etc
```

### All Examples
```bash
# Run all examples in sequence
python run_all_examples.py

# Run in demo mode (no API calls)
python run_all_examples.py --demo-mode

# Skip search-dependent examples
python run_all_examples.py --skip-search
```

### Validation
```bash
# Validate all samples for syntax and structure
python validate_samples.py
```

## Common Patterns

### Authentication
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Using API key
credential = AzureKeyCredential(api_key)
search_client = SearchClient(endpoint, index_name, credential)

# Using managed identity
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
search_client = SearchClient(endpoint, index_name, credential)
```

### Basic Filtering
```python
# Simple equality filter
results = search_client.search(
    search_text="*",
    filter="category eq 'Electronics'"
)

# Range filter
results = search_client.search(
    search_text="*",
    filter="price gt 100 and price lt 500"
)

# Combined filters
results = search_client.search(
    search_text="*",
    filter="category eq 'Electronics' and rating ge 4.0"
)
```

### Sorting
```python
# Single field sorting
results = search_client.search(
    search_text="*",
    order_by=["rating desc"]
)

# Multi-field sorting
results = search_client.search(
    search_text="*",
    order_by=["category asc", "rating desc", "price asc"]
)
```

### Error Handling
```python
try:
    results = search_client.search(
        search_text="*",
        filter="category eq 'Electronics'"
    )
    for result in results:
        print(f"Found: {result['name']}")
except Exception as e:
    print(f"Search failed: {e}")
```

## Configuration Management

### Using Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'endpoint': os.getenv('SEARCH_ENDPOINT'),
    'api_key': os.getenv('SEARCH_API_KEY'),
    'index_name': os.getenv('INDEX_NAME')
}
```

### Configuration Class
```python
class SearchConfig:
    def __init__(self):
        self.endpoint = os.getenv('SEARCH_ENDPOINT')
        self.api_key = os.getenv('SEARCH_API_KEY')
        self.index_name = os.getenv('INDEX_NAME')
    
    def validate(self):
        required = [self.endpoint, self.api_key, self.index_name]
        if not all(required):
            raise ValueError('Missing required configuration')
```

## Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Performance Tests
```bash
python -m pytest tests/performance/
```

## Debugging

### Enable Logging
```python
import logging

# Enable Azure SDK logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('azure.search.documents')
logger.setLevel(logging.DEBUG)
```

### Debug Mode
```python
# Set debug flag for detailed output
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

if DEBUG:
    print(f"Filter: {filter_expression}")
    print(f"Order by: {order_by}")
```

## Best Practices

### Filter Construction
```python
def build_filter(category=None, min_price=None, max_price=None, in_stock=None):
    """Build filter expression from parameters"""
    filters = []
    
    if category:
        filters.append(f"category eq '{category}'")
    
    if min_price is not None:
        filters.append(f"price ge {min_price}")
    
    if max_price is not None:
        filters.append(f"price le {max_price}")
    
    if in_stock is not None:
        filters.append(f"inStock eq {str(in_stock).lower()}")
    
    return " and ".join(filters) if filters else None
```

### Result Processing
```python
def process_results(results, max_results=10):
    """Process search results efficiently"""
    processed = []
    count = 0
    
    for result in results:
        if count >= max_results:
            break
        
        processed.append({
            'id': result.get('id'),
            'name': result.get('name'),
            'price': result.get('price'),
            'rating': result.get('rating')
        })
        count += 1
    
    return processed
```

### Performance Monitoring
```python
import time

def timed_search(search_client, **kwargs):
    """Execute search with timing"""
    start_time = time.time()
    
    try:
        results = search_client.search(**kwargs)
        result_list = list(results)  # Materialize results
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'results': result_list,
            'duration': duration,
            'count': len(result_list)
        }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'error': str(e),
            'duration': duration
        }
```

## Troubleshooting

### Common Issues
1. **Field not filterable**: Ensure field has `filterable=True` in index schema
2. **Invalid filter syntax**: Check OData expression syntax
3. **Data type mismatches**: Ensure filter values match field types
4. **Performance issues**: Optimize filter expressions and index design

### Debug Tools
```python
def validate_filter(filter_expression):
    """Validate filter expression syntax"""
    try:
        # Simple validation - check for common issues
        if not filter_expression:
            return True, "Empty filter is valid"
        
        # Check for balanced quotes
        single_quotes = filter_expression.count("'")
        if single_quotes % 2 != 0:
            return False, "Unbalanced single quotes"
        
        # Check for valid operators
        valid_operators = ['eq', 'ne', 'gt', 'ge', 'lt', 'le', 'and', 'or', 'not']
        # Add more validation as needed
        
        return True, "Filter appears valid"
    except Exception as e:
        return False, f"Validation error: {e}"
```

## Validation and Testing

### Sample Validation
The `validate_samples.py` script checks all Python samples for:
- Syntax correctness
- Required function presence (main)
- Azure SDK imports
- Documentation completeness
- Code structure analysis

### Running All Examples
The `run_all_examples.py` script provides:
- Sequential execution of all samples
- Demo mode for testing without API calls
- Comprehensive error reporting
- Execution summary and recommendations

### Example Output
```bash
$ python validate_samples.py
🔍 Azure AI Search Python Samples Validation
==================================================
🔍 Validating 01_basic_filters.py...
  ✅ Syntax: Valid (245 lines)
  ✅ Main function: True
  ✅ Azure imports: True
  ✅ Docstring: True
  📊 Functions: 8
  🏗️  Classes: 2

✅ All 8 samples passed validation!
```

## Additional Resources

- [Azure Search Documents SDK Documentation](https://docs.microsoft.com/python/api/azure-search-documents/)
- [Python SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents/samples)
- [OData Filter Syntax Reference](https://docs.microsoft.com/azure/search/search-query-odata-filter)
- [Interactive Notebooks](../notebooks/) - Jupyter notebooks for hands-on learning

## Next Steps

1. **Validate Setup**: Run `python validate_samples.py` to check all samples
2. **Demo Mode**: Try `python run_all_examples.py --demo-mode` for a quick overview
3. **Individual Examples**: Run specific examples that match your use case
4. **Interactive Learning**: Explore the Jupyter notebooks for hands-on experience
5. **Customize**: Modify examples for your specific data and requirements
6. **Production**: Implement filtering in your applications with proper error handling
7. **Advanced Features**: Explore intermediate and advanced modules