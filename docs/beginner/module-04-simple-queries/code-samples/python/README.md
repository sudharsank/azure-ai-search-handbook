# Python Code Samples - Simple Queries and Filters

This directory contains Python implementations for learning simple queries and filters in Azure AI Search using the Azure SDK for Python.

## 📋 Prerequisites

### Required Packages

Install the required Python packages:

```bash
pip install azure-search-documents python-dotenv
```

### Environment Setup

Create a `.env` file in your project root with your Azure AI Search credentials:

```env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=your-index-name
```

### Sample Data

These examples assume you have sample indexes created from previous modules. The examples work with indexes containing documents with these fields:

- `id` (string) - Unique identifier
- `title` (string) - Document title
- `content` (string) - Document content
- `category` (string) - Document category
- `tags` (Collection(string)) - Document tags
- `rating` (double) - Document rating (0.0-5.0)
- `publishedDate` (DateTimeOffset) - Publication date
- `price` (double) - Document price (if applicable)
- `location` (GeographyPoint) - Geographic location (if applicable)

## 🚀 Getting Started

### Basic Usage

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the search client
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

# Perform a simple search
results = search_client.search(search_text="azure")
for result in results:
    print(f"Title: {result['title']}")
```

## 📚 Code Samples

### 1. Basic Queries (`01_basic_queries.py`)
Learn fundamental text search operations:
- Simple text search
- Field-specific search
- Query operators (+, -, "", *, ())
- Search modes and query types

**Key Concepts:**
- Search text parameter
- Search fields specification
- Query operators and syntax
- Result iteration and processing

### 2. Filtering (`02_filtering.py`)
Master OData filter expressions:
- Equality and comparison filters
- Logical operators (and, or, not)
- Collection filters (any, all)
- Date and numeric range filters

**Key Concepts:**
- OData filter syntax
- Data type handling
- Complex filter expressions
- Performance optimization

### 3. Sorting and Pagination (`03_sorting_pagination.py`)
Implement result ordering and pagination:
- Single and multi-field sorting
- Ascending and descending order
- Page-based navigation
- Total count retrieval

**Key Concepts:**
- Order by expressions
- Top and skip parameters
- Pagination patterns
- Performance considerations

### 4. Result Customization (`04_result_customization.py`)
Customize search results:
- Field selection
- Search highlighting
- Result formatting
- Custom result processing

**Key Concepts:**
- Select parameter
- Highlight configuration
- Result metadata
- Custom formatting

### 5. Advanced Queries (`05_advanced_queries.py`)
Explore advanced query features:
- Field boosting
- Fuzzy search
- Wildcard patterns
- Regular expressions

**Key Concepts:**
- Query complexity
- Performance optimization
- Advanced syntax
- Use case scenarios

### 6. Error Handling (`06_error_handling.py`)
Implement robust error handling:
- Exception types and handling
- Query validation
- Retry logic
- Debugging techniques

**Key Concepts:**
- Azure SDK exceptions
- Error recovery
- Logging and debugging
- Production best practices

## 🔧 Running the Examples

### Individual Examples

Run each example individually:

```bash
# Basic queries
python 01_basic_queries.py

# Filtering
python 02_filtering.py

# Sorting and pagination
python 03_sorting_pagination.py

# Result customization
python 04_result_customization.py

# Advanced queries
python 05_advanced_queries.py

# Error handling
python 06_error_handling.py
```

### All Examples

Run all examples in sequence:

```bash
# Run all examples
for file in 0*.py; do
    echo "Running $file..."
    python "$file"
    echo "---"
done
```

## 🎯 Learning Outcomes

After completing these Python examples, you will be able to:

- ✅ **Initialize Search Client**: Set up Azure AI Search client with proper authentication
- ✅ **Execute Basic Queries**: Perform text searches with various operators
- ✅ **Apply Filters**: Use OData expressions to filter results effectively
- ✅ **Implement Pagination**: Handle large result sets with proper pagination
- ✅ **Customize Results**: Select fields and highlight matching terms
- ✅ **Handle Errors**: Implement robust error handling and validation
- ✅ **Optimize Performance**: Write efficient queries for production use

## 🔍 Common Patterns

### Search Client Initialization

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os

def create_search_client():
    return SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    )
```

### Error Handling Pattern

```python
from azure.core.exceptions import HttpResponseError

def safe_search(search_client, **kwargs):
    try:
        results = search_client.search(**kwargs)
        return list(results)
    except HttpResponseError as e:
        print(f"Search error: {e.message}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []
```

### Result Processing Pattern

```python
def process_results(results):
    processed = []
    for result in results:
        processed_result = {
            'id': result.get('id'),
            'title': result.get('title'),
            'score': result.get('@search.score'),
            'highlights': result.get('@search.highlights', {})
        }
        processed.append(processed_result)
    return processed
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install azure-search-documents python-dotenv
   ```

2. **Authentication Errors**
   - Verify your `.env` file contains correct credentials
   - Check API key permissions
   - Ensure service endpoint is correct

3. **Index Not Found**
   - Verify index name in environment variables
   - Check if index exists in your search service
   - Run index creation from previous modules

4. **No Results**
   - Check if your index contains data
   - Try broader search terms
   - Verify field names in filters

### Debug Mode

Enable debug logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

## 📖 Additional Resources

- [Azure SDK for Python Documentation](https://docs.microsoft.com/en-us/python/api/azure-search-documents/)
- [Azure AI Search Python Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents/samples)
- [Python Best Practices](https://docs.python.org/3/tutorial/)

## 🔗 Next Steps

1. **Practice with Real Data**: Apply these patterns to your own datasets
2. **Explore Advanced Features**: Move to Module 5 for advanced querying
3. **Build Applications**: Integrate search into your Python applications
4. **Performance Tuning**: Learn about search optimization and analytics

Happy coding! 🐍