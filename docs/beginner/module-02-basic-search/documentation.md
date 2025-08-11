# Module 2: Basic Search Operations

## Overview

This module introduces you to the fundamentals of search operations in Azure AI Search. You'll learn how to perform simple queries, handle search results effectively, and understand basic search patterns. By the end of this module, you'll be comfortable executing searches and processing results in your applications.

!!! info "Comprehensive Hands-On Learning Available"
    This module includes **32 complete code samples** across **4 programming languages** with interactive Jupyter notebooks and advanced examples. The code samples are designed to complement this documentation with practical, runnable examples you can use immediately.

    **⚠️ IMPORTANT: Run Prerequisites Setup First!**
    
    Before using any examples, run the [Prerequisites Setup](code-samples/setup_prerequisites.py) to create your index and sample data.
    
    **🎯 Complete Coverage Matrix:**
    
    | Topic | Python | C# | JavaScript | REST | Description |
    |-------|--------|----|-----------|----- |-------------|
    | Simple Text Search | ✅ | ✅ | ✅ | ✅ | Basic keyword searching |
    | Phrase Search | ✅ | ✅ | ✅ | ✅ | Exact phrase matching |
    | Boolean Search | ✅ | ✅ | ✅ | ✅ | AND, OR, NOT operators |
    | Wildcard Search | ✅ | ✅ | ✅ | ✅ | Pattern matching with * |
    | Field Search | ✅ | ✅ | ✅ | ✅ | Field-specific searches |
    | Result Processing | ✅ | ✅ | ✅ | ✅ | Formatting and analysis |
    | Error Handling | ✅ | ✅ | ✅ | ✅ | Robust error management |
    | Search Patterns | ✅ | ✅ | ✅ | ✅ | Advanced strategies |
    
    **Quick Start Options:**
    
    1. 🔧 **Prerequisites Setup**: [Run setup_prerequisites.py](code-samples/setup_prerequisites.py) - **REQUIRED FIRST STEP**
    2. 📓 **Interactive Learning**: [Jupyter Notebook](code-samples/notebooks/basic_search.ipynb) with step-by-step examples
    3. 🐍 **Python Examples**: [8 Complete Scripts](code-samples/python/README.md) with all search operations
    4. 🔷 **C# Examples**: [8 .NET Files](code-samples/csharp/README.md) for enterprise applications
    5. 🟨 **JavaScript Examples**: [8 Node.js/Browser Files](code-samples/javascript/README.md) for web integration
    6. 🌐 **REST API Examples**: [8 HTTP Files](code-samples/rest/README.md) for any language

## Learning Objectives

By completing this module, you will be able to:

- Perform basic search operations using the Azure AI Search Python SDK
- Handle and process search results effectively
- Understand the structure of search responses
- Implement proper error handling for search operations
- Apply basic search patterns and best practices
- Troubleshoot common search-related issues

## Prerequisites

Before starting with basic search operations, you need to complete the setup process. This includes configuring your Azure AI Search service, setting up your development environment, and running the prerequisites setup script.

**📋 [Complete Prerequisites Setup →](prerequisites.md)**

The prerequisites setup includes:
- ✅ **Environment Configuration** - Azure service and API keys
- ✅ **Development Setup** - Required packages and tools  
- ✅ **Sample Data Creation** - Index with 10 test documents
- ✅ **Functionality Testing** - All 5 search operation types verified

**⚠️ CRITICAL**: You must complete the [Prerequisites Setup](prerequisites.md) before attempting any examples in this module!

## Search Fundamentals

### What is a Search Operation?

A search operation in Azure AI Search is a request to find documents in an index that match specified criteria. The search service processes your query and returns a ranked list of matching documents along with metadata about the search results.

### Basic Search Components

Every search operation consists of:

1. **Search Client**: The connection to your Azure AI Search service
2. **Index Name**: The specific index you want to search
3. **Search Query**: The text or criteria you're searching for
4. **Search Parameters**: Additional options that control the search behavior
5. **Search Results**: The response containing matching documents and metadata

### Simple Search Syntax

The most basic search is a simple text query:

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Initialize the search client
search_client = SearchClient(
    endpoint="https://your-service.search.windows.net",
    index_name="your-index",
    credential=AzureKeyCredential("your-api-key")
)

# Perform a simple search
results = search_client.search(search_text="python programming")

# Process results
for result in results:
    print(f"Score: {result['@search.score']}")
    print(f"Document: {result}")
```

!!! success "Complete Code Sample Coverage ✅"
    The prerequisites setup has been tested and works perfectly! After running `setup_prerequisites.py`, you'll have:
    
    - **Index**: `handbook-samples` with 10 rich documents
    - **Test Results**: 8/8 search operations working across all languages
    - **Ready Examples**: All 32 code samples immediately functional
    - **Equal Coverage**: Every language has identical functionality
    
    **🔗 Quick Access:**
    - 🐍 [Python Examples](code-samples/python/README.md) - 8 complete files
    - 🔷 [C# Examples](code-samples/csharp/README.md) - 8 complete files  
    - 🟨 [JavaScript Examples](code-samples/javascript/README.md) - 8 complete files
    - 🌐 [REST API Examples](code-samples/rest/README.md) - 8 complete files
    - 📓 [Interactive Notebook](code-samples/notebooks/basic_search.ipynb) - All concepts in one place

## Simple Query Types

### 1. Simple Text Search

The most straightforward search type where you provide a text string:

```python
# Search for documents containing "machine learning"
results = search_client.search(search_text="machine learning")
```

### 2. Empty Search (Get All Documents)

Retrieve all documents in the index:

```python
# Get all documents (useful for browsing)
results = search_client.search(search_text="*")
```

### 3. Phrase Search

Search for exact phrases using quotes:

```python
# Search for the exact phrase "artificial intelligence"
results = search_client.search(search_text='"artificial intelligence"')
```

### 4. Wildcard Search

Use wildcards for partial matching:

```python
# Search for words starting with "prog"
results = search_client.search(search_text="prog*")

# Search for words ending with "ing"
results = search_client.search(search_text="*ing")
```

### 5. Boolean Operators

Combine terms with AND, OR, NOT:

```python
# Documents containing both "python" AND "tutorial"
results = search_client.search(search_text="python AND tutorial")

# Documents containing either "python" OR "java"
results = search_client.search(search_text="python OR java")

# Documents containing "programming" but NOT "advanced"
results = search_client.search(search_text="programming NOT advanced")
```

## Search Parameters

### Basic Search Parameters

Control your search behavior with these common parameters:

```python
results = search_client.search(
    search_text="python",
    top=10,                    # Return top 10 results
    skip=0,                    # Skip first 0 results (for pagination)
    include_total_count=True,  # Include total count in response
    search_mode="any"          # "any" or "all" for multiple terms
)
```

### Field-Specific Search

Search within specific fields:

```python
# Search only in the title field
results = search_client.search(
    search_text="python",
    search_fields=["title"]
)

# Search in multiple specific fields
results = search_client.search(
    search_text="tutorial",
    search_fields=["title", "description"]
)
```

### Selecting Fields

Choose which fields to return:

```python
# Return only specific fields
results = search_client.search(
    search_text="python",
    select=["id", "title", "author", "publishedDate"]
)
```

## Result Handling and Processing

!!! example "Complete Result Processing"
    For comprehensive result processing utilities including formatting, export capabilities, and statistical analysis, see the result processing examples:
    - [Python: `06_result_processing.py`](code-samples/python/06_result_processing.py)
    - [C#: `06_ResultProcessing.cs`](code-samples/csharp/06_ResultProcessing.cs)
    - [JavaScript: `06_result_processing.js`](code-samples/javascript/06_result_processing.js)
    - [REST API: `06_result_processing.http`](code-samples/rest/06_result_processing.http)

### Understanding Search Results

Search results contain both the matching documents and metadata:

```python
results = search_client.search(search_text="python programming")

# Access result metadata
print(f"Total results: {results.get_count()}")

# Process each result
for result in results:
    # Search score (relevance)
    score = result['@search.score']
    
    # Document fields
    title = result.get('title', 'No title')
    content = result.get('content', 'No content')
    
    print(f"Score: {score:.2f}")
    print(f"Title: {title}")
    print(f"Content: {content[:100]}...")
    print("-" * 50)
```

### Working with Search Scores

Search scores indicate relevance (higher = more relevant):

```python
results = search_client.search(search_text="machine learning")

# Sort results by score (highest first)
sorted_results = sorted(results, key=lambda x: x['@search.score'], reverse=True)

for result in sorted_results[:5]:  # Top 5 results
    print(f"Score: {result['@search.score']:.3f} - {result.get('title', 'No title')}")
```

### Pagination

Handle large result sets with pagination:

```python
def paginated_search(search_text, page_size=10):
    """Perform paginated search"""
    skip = 0
    page = 1
    
    while True:
        results = search_client.search(
            search_text=search_text,
            top=page_size,
            skip=skip,
            include_total_count=True
        )
        
        result_list = list(results)
        if not result_list:
            break
            
        print(f"Page {page} ({len(result_list)} results):")
        for result in result_list:
            print(f"  - {result.get('title', 'No title')}")
        
        skip += page_size
        page += 1
        
        # Ask user if they want to continue
        if input("Continue to next page? (y/n): ").lower() != 'y':
            break
```

### Result Formatting

Format results for display:

```python
def format_search_results(results, max_content_length=200):
    """Format search results for display"""
    formatted_results = []
    
    for result in results:
        formatted_result = {
            'score': round(result['@search.score'], 3),
            'title': result.get('title', 'Untitled'),
            'author': result.get('author', 'Unknown'),
            'content_preview': (result.get('content', '')[:max_content_length] + '...' 
                              if len(result.get('content', '')) > max_content_length 
                              else result.get('content', '')),
            'url': result.get('url', '#')
        }
        formatted_results.append(formatted_result)
    
    return formatted_results

# Usage
results = search_client.search(search_text="python tutorial")
formatted = format_search_results(results)

for result in formatted:
    print(f"Title: {result['title']}")
    print(f"Author: {result['author']}")
    print(f"Score: {result['score']}")
    print(f"Preview: {result['content_preview']}")
    print(f"URL: {result['url']}")
    print("-" * 60)
```

## Basic Search Patterns

!!! info "Advanced Patterns Available"
    For more sophisticated search patterns including progressive search, fallback strategies, and multi-field searches, explore the search patterns examples:
    - [Python: `08_search_patterns.py`](code-samples/python/08_search_patterns.py)
    - [C#: `08_SearchPatterns.cs`](code-samples/csharp/08_SearchPatterns.cs)
    - [JavaScript: `08_search_patterns.js`](code-samples/javascript/08_search_patterns.js)
    - [REST API: `08_search_patterns.http`](code-samples/rest/08_search_patterns.http)

### 1. Search with Fallback

Implement search with fallback to broader queries:

```python
def search_with_fallback(query):
    """Search with progressively broader queries if no results found"""
    
    # Try exact phrase first
    results = list(search_client.search(search_text=f'"{query}"'))
    if results:
        print(f"Found {len(results)} results for exact phrase")
        return results
    
    # Try all terms with AND
    results = list(search_client.search(search_text=query, search_mode="all"))
    if results:
        print(f"Found {len(results)} results for all terms")
        return results
    
    # Try any terms with OR
    results = list(search_client.search(search_text=query, search_mode="any"))
    if results:
        print(f"Found {len(results)} results for any terms")
        return results
    
    # Try wildcard search
    wildcard_query = " OR ".join([f"{term}*" for term in query.split()])
    results = list(search_client.search(search_text=wildcard_query))
    if results:
        print(f"Found {len(results)} results with wildcards")
        return results
    
    print("No results found")
    return []
```

### 2. Search Result Highlighting

Highlight matching terms in results:

```python
def search_with_highlighting(query, fields_to_highlight=None):
    """Search with result highlighting"""
    if fields_to_highlight is None:
        fields_to_highlight = ["title", "content"]
    
    results = search_client.search(
        search_text=query,
        highlight_fields=",".join(fields_to_highlight),
        highlight_pre_tag="<mark>",
        highlight_post_tag="</mark>"
    )
    
    for result in results:
        print(f"Title: {result.get('title', 'No title')}")
        print(f"Score: {result['@search.score']:.3f}")
        
        # Display highlights
        highlights = result.get('@search.highlights', {})
        for field, highlighted_snippets in highlights.items():
            print(f"{field.title()} highlights:")
            for snippet in highlighted_snippets:
                print(f"  - {snippet}")
        print("-" * 50)
```

### 3. Search Suggestions

Implement search suggestions for better user experience:

```python
def get_search_suggestions(partial_query, suggester_name="sg"):
    """Get search suggestions based on partial input"""
    try:
        suggestions = search_client.suggest(
            search_text=partial_query,
            suggester_name=suggester_name,
            top=5
        )
        
        suggestion_list = []
        for suggestion in suggestions:
            suggestion_list.append({
                'text': suggestion['@@search.text'],
                'document': suggestion
            })
        
        return suggestion_list
    except Exception as e:
        print(f"Suggestions not available: {e}")
        return []
```

## Error Handling

!!! tip "Complete Error Handling Examples"
    For production-ready error handling with comprehensive validation, retry logic, and fallback strategies, see the error handling examples:
    - [Python: `07_error_handling.py`](code-samples/python/07_error_handling.py)
    - [C#: `07_ErrorHandling.cs`](code-samples/csharp/07_ErrorHandling.cs)
    - [JavaScript: `07_error_handling.js`](code-samples/javascript/07_error_handling.js)
    - [REST API: `07_error_handling.http`](code-samples/rest/07_error_handling.http)

### Common Search Errors

Handle typical errors that occur during search operations:

```python
from azure.core.exceptions import HttpResponseError
import logging

def safe_search(search_text, **kwargs):
    """Perform search with comprehensive error handling"""
    try:
        results = search_client.search(search_text=search_text, **kwargs)
        return list(results)
        
    except HttpResponseError as e:
        if e.status_code == 400:
            logging.error(f"Bad request - check your query syntax: {search_text}")
            return []
        elif e.status_code == 403:
            logging.error("Access denied - check your API key and permissions")
            return []
        elif e.status_code == 404:
            logging.error("Index not found - verify your index name")
            return []
        elif e.status_code == 503:
            logging.error("Service unavailable - try again later")
            return []
        else:
            logging.error(f"HTTP error {e.status_code}: {e.message}")
            return []
            
    except Exception as e:
        logging.error(f"Unexpected error during search: {str(e)}")
        return []

# Usage with error handling
results = safe_search("python programming", top=10)
if results:
    print(f"Found {len(results)} results")
    for result in results:
        print(f"- {result.get('title', 'No title')}")
else:
    print("No results found or an error occurred")
```

### Validation and Input Sanitization

Validate search inputs before sending requests:

```python
import re

def validate_search_query(query):
    """Validate and sanitize search query"""
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    
    # Remove potentially problematic characters
    sanitized = re.sub(r'[<>]', '', query.strip())
    
    # Check for minimum length
    if len(sanitized) < 2:
        raise ValueError("Search query must be at least 2 characters long")
    
    # Check for maximum length
    if len(sanitized) > 1000:
        raise ValueError("Search query is too long (max 1000 characters)")
    
    return sanitized

def validated_search(query, **kwargs):
    """Perform search with input validation"""
    try:
        validated_query = validate_search_query(query)
        return safe_search(validated_query, **kwargs)
    except ValueError as e:
        print(f"Invalid query: {e}")
        return []
```

## Troubleshooting

Having issues with search operations? We have comprehensive troubleshooting guides to help you resolve common problems quickly.

**🔍 [Search Operations Troubleshooting →](search-troubleshooting.md)**

Common issues covered:

- ✅ **No Results Found** - Index and query validation
- ✅ **Unexpected Results** - Search mode and field targeting
- ✅ **Performance Issues** - Optimization and pagination
- ✅ **Authentication Errors** - API key and permissions
- ✅ **Query Syntax Errors** - Proper escaping and validation

**🔧 [Prerequisites Setup Troubleshooting →](prerequisites-troubleshooting.md)**

Setup-specific issues covered:

- ✅ **Connection Problems** - Environment and network issues
- ✅ **Package Installation** - Python dependencies and virtual environments
- ✅ **Permission Errors** - API key types and access policies
- ✅ **Verification Steps** - Testing your setup

## Best Practices

Ready to implement Azure AI Search in production? Learn professional techniques and optimization strategies.

**💡 [Complete Best Practices Guide →](best-practices.md)**

Key areas covered:

- ✅ **Query Optimization** - Efficient search strategies and patterns
- ✅ **Error Handling** - Robust error management and recovery
- ✅ **Performance** - Caching, pagination, and optimization techniques
- ✅ **Security** - API key management and input sanitization
- ✅ **User Experience** - Search suggestions, highlighting, and feedback
- ✅ **Monitoring** - Analytics, performance tracking, and alerting

## Practice and Implementation

Ready to put your knowledge into practice? Start coding with hands-on exercises and real-world examples.

**🎯 [Complete Practice Guide →](practice-implementation.md)**

What you'll practice:

- ✅ **Interactive Learning** - Jupyter notebooks and step-by-step examples
- ✅ **Complete Examples** - Full implementations in multiple languages
- ✅ **Production Patterns** - Error handling and advanced strategies
- ✅ **Result Processing** - Formatting, pagination, and analysis
- ✅ **Performance Testing** - Monitoring and optimization techniques
- ✅ **Real-World Projects** - Apply concepts to your own applications



## Next Steps

After completing this module, you should be comfortable with:

- Performing basic search operations
- Handling search results and errors
- Understanding search scores and relevance
- Implementing common search patterns

**Recommended Learning Path:**

1. ✅ Complete the theory (this documentation)
2. 🔬 Practice with the [code samples](code-samples/README.md)
3. 📝 Work through the exercises (coming in Module 3)
4. 🚀 Move to **Module 3: Index Management**

In the next module, you'll learn about **Index Management**, where you'll discover how to create, modify, and optimize search indexes for better search performance.

## Code Samples and Hands-On Practice

Ready to put your knowledge into practice? This module includes **32 comprehensive code samples** across **4 programming languages**.

**👨‍💻 [Complete Code Samples Guide →](code-samples/README.md)**

What's included:

- ✅ **Multi-Language Support** - Python, C#, JavaScript, REST API (8 files each)
- ✅ **Focused Examples** - Each file covers one specific search concept  
- ✅ **Interactive Learning** - Jupyter notebooks for hands-on practice
- ✅ **Production-Ready** - Comprehensive error handling patterns
- ✅ **Equal Coverage** - Every language has identical functionality

**📊 Complete Coverage Matrix:**

| Topic | Python | C# | JavaScript | REST | Description |
|-------|--------|----|-----------|----- |-------------|
| Simple Text Search | ✅ | ✅ | ✅ | ✅ | Basic keyword searching |
| Phrase Search | ✅ | ✅ | ✅ | ✅ | Exact phrase matching |
| Boolean Search | ✅ | ✅ | ✅ | ✅ | AND, OR, NOT operators |
| Wildcard Search | ✅ | ✅ | ✅ | ✅ | Pattern matching with * |
| Field Search | ✅ | ✅ | ✅ | ✅ | Field-specific searches |
| Result Processing | ✅ | ✅ | ✅ | ✅ | Formatting and analysis |
| Error Handling | ✅ | ✅ | ✅ | ✅ | Robust error management |
| Search Patterns | ✅ | ✅ | ✅ | ✅ | Advanced strategies |

**Quick Start Options:**

- 🐍 **Python**: `cd code-samples/python/ && python 01_simple_text_search.py`
- 🔷 **C#**: `dotnet run 01_SimpleTextSearch.cs`
- 🟨 **JavaScript**: `node 01_simple_text_search.js`
- 🌐 **REST API**: Open `01_simple_text_search.http` in VS Code with REST Client
- 📓 **Interactive**: `jupyter notebook code-samples/notebooks/basic_search.ipynb`