# Module 4: Simple Queries and Filters

## Overview

This module teaches you how to construct effective search queries and apply filters in Azure AI Search. You'll learn the fundamentals of query syntax, filtering options, sorting, pagination, and result customization. By the end of this module, you'll be able to build sophisticated search experiences that deliver relevant results to your users.

!!! info "Hands-On Learning Available"
    This module includes comprehensive **[Code Samples](code-samples/README.md)** with interactive Jupyter notebooks, complete Python scripts, and advanced examples. The code samples are designed to complement this documentation with practical, runnable examples you can use immediately.

    **⚠️ IMPORTANT: Prerequisites Required!**
    
    Before using any examples, ensure you have completed the setup from previous modules and have working search indexes.
    
    **Quick Start Options:**
    
    1. 📓 **Interactive Learning**: [Jupyter Notebook](code-samples/notebooks/simple_queries.ipynb) with step-by-step examples
    2. 🐍 **Python Examples**: [Complete Python Scripts](code-samples/python/) with all query operations
    3. 🔷 **C# Examples**: [.NET Implementation](code-samples/csharp/) for enterprise applications
    4. 🟨 **JavaScript Examples**: [Node.js/Browser Code](code-samples/javascript/) for web integration
    5. 🌐 **REST API Examples**: [Direct HTTP Calls](code-samples/rest/) for any language

## Learning Objectives

By completing this module, you will be able to:

- Construct basic and advanced search queries using Azure AI Search query syntax
- Apply filters to narrow search results based on specific criteria
- Implement sorting and ranking to control result order
- Use pagination to handle large result sets efficiently
- Customize search results with field selection and highlighting
- Handle special characters and query escaping
- Optimize query performance for better user experience
- Troubleshoot common query issues and errors

## Prerequisites

Before starting with simple queries, you should have:

- Completed Module 1 (Introduction and Setup)
- Completed Module 2 (Basic Search Operations) 
- Completed Module 3 (Index Management)
- A working Azure AI Search service with sample indexes
- Basic understanding of search concepts and terminology

## Query Fundamentals

### Understanding Search Queries

Azure AI Search supports several types of queries, each designed for different search scenarios:

1. **Simple Query Syntax** - Easy-to-use syntax for basic searches
2. **Full Lucene Query Syntax** - Advanced syntax with more operators and features
3. **Filter Expressions** - Precise filtering using OData syntax
4. **Faceted Search** - Structured navigation and filtering

### Basic Query Structure

Every search query in Azure AI Search follows this basic structure:

```
GET https://[service-name].search.windows.net/indexes/[index-name]/docs?
    api-version=2023-11-01
    &search=[query-text]
    &$filter=[filter-expression]
    &$orderby=[sort-expression]
    &$top=[page-size]
    &$skip=[offset]
```

## Simple Query Syntax

The simple query syntax is the default and most commonly used approach for basic search operations.

### Basic Text Search

```python
# Simple text search
results = search_client.search(search_text="azure search")

# Search in specific fields
results = search_client.search(
    search_text="machine learning",
    search_fields=["title", "content"]
)
```

### Query Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Required term | `+azure search` |
| `-` | Excluded term | `azure -cognitive` |
| `""` | Exact phrase | `"machine learning"` |
| `*` | Wildcard | `search*` |
| `()` | Grouping | `(azure OR microsoft) search` |

### Examples

```python
# Required and excluded terms
results = search_client.search(search_text="+azure -cognitive")

# Phrase search
results = search_client.search(search_text='"artificial intelligence"')

# Wildcard search
results = search_client.search(search_text="develop*")
```

## Filtering with OData

Filters allow you to narrow search results based on specific field values using OData syntax.

### Basic Filter Syntax

```python
# Filter by exact value
results = search_client.search(
    search_text="*",
    filter="category eq 'Technology'"
)

# Filter by range
results = search_client.search(
    search_text="*",
    filter="price ge 100 and price le 500"
)

# Filter by date
results = search_client.search(
    search_text="*",
    filter="publishedDate ge 2023-01-01T00:00:00Z"
)
```

### Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equal | `category eq 'Tech'` |
| `ne` | Not equal | `status ne 'Draft'` |
| `gt` | Greater than | `price gt 100` |
| `ge` | Greater than or equal | `rating ge 4.0` |
| `lt` | Less than | `views lt 1000` |
| `le` | Less than or equal | `age le 30` |
| `and` | Logical AND | `price gt 50 and price lt 200` |
| `or` | Logical OR | `category eq 'Tech' or category eq 'Science'` |
| `not` | Logical NOT | `not (status eq 'Draft')` |

### Collection Filters

```python
# Any element in collection matches
results = search_client.search(
    search_text="*",
    filter="tags/any(t: t eq 'python')"
)

# All elements in collection match
results = search_client.search(
    search_text="*",
    filter="tags/all(t: t ne 'deprecated')"
)
```

## Sorting and Ordering

Control the order of search results using the `order_by` parameter.

### Basic Sorting

```python
# Sort by single field
results = search_client.search(
    search_text="azure",
    order_by=["publishedDate desc"]
)

# Sort by multiple fields
results = search_client.search(
    search_text="azure",
    order_by=["category asc", "publishedDate desc"]
)
```

### Sorting Options

- **asc** - Ascending order (default)
- **desc** - Descending order
- **geo.distance()** - Sort by geographic distance

```python
# Geographic sorting
results = search_client.search(
    search_text="restaurants",
    order_by=["geo.distance(location, geography'POINT(-122.131577 47.678581)') asc"]
)
```

## Pagination

Handle large result sets efficiently using pagination parameters.

### Basic Pagination

```python
# First page (top 10 results)
results = search_client.search(
    search_text="azure",
    top=10,
    skip=0
)

# Second page (next 10 results)
results = search_client.search(
    search_text="azure",
    top=10,
    skip=10
)
```

### Pagination Best Practices

```python
def paginated_search(query, page_size=10, page_number=1):
    """
    Perform paginated search with proper error handling
    """
    skip = (page_number - 1) * page_size
    
    results = search_client.search(
        search_text=query,
        top=page_size,
        skip=skip,
        include_total_count=True
    )
    
    return {
        'results': list(results),
        'total_count': results.get_count(),
        'page': page_number,
        'page_size': page_size,
        'has_more': skip + page_size < results.get_count()
    }
```

## Result Customization

### Field Selection

Choose which fields to return in search results:

```python
# Select specific fields
results = search_client.search(
    search_text="azure",
    select=["id", "title", "summary", "publishedDate"]
)

# Exclude large fields for performance
results = search_client.search(
    search_text="azure",
    select=["id", "title", "summary"]  # Exclude 'content' field
)
```

### Search Highlighting

Highlight matching terms in search results:

```python
# Basic highlighting
results = search_client.search(
    search_text="machine learning",
    highlight_fields=["title", "content"],
    highlight_pre_tag="<mark>",
    highlight_post_tag="</mark>"
)

# Process highlighted results
for result in results:
    if '@search.highlights' in result:
        highlights = result['@search.highlights']
        if 'title' in highlights:
            print(f"Highlighted title: {highlights['title'][0]}")
```

## Advanced Query Techniques

### Boosting Fields

Give more weight to matches in specific fields:

```python
# Boost title matches
results = search_client.search(
    search_text="azure",
    search_fields=["title^3", "content"]  # Title matches weighted 3x
)
```

### Fuzzy Search

Handle typos and variations:

```python
# Enable fuzzy matching
results = search_client.search(
    search_text="machne~",  # Will match "machine"
    query_type="full"
)
```

### Regular Expressions

Use regex patterns for complex matching:

```python
# Regex search (requires full Lucene syntax)
results = search_client.search(
    search_text="/[0-9]{4}-[0-9]{2}-[0-9]{2}/",
    query_type="full"
)
```

## Performance Optimization

### Query Performance Tips

1. **Use Filters Before Search**: Filters are faster than text search
2. **Limit Field Selection**: Only return needed fields
3. **Optimize Page Size**: Balance between performance and user experience
4. **Cache Common Queries**: Store frequently used results
5. **Use Search Fields**: Limit search to relevant fields only

```python
# Optimized query example
results = search_client.search(
    search_text="azure",
    search_fields=["title", "summary"],  # Limit search scope
    select=["id", "title", "summary"],   # Limit returned fields
    filter="category eq 'Technology'",   # Pre-filter results
    top=20                               # Reasonable page size
)
```

## Error Handling

### Common Query Errors

```python
from azure.core.exceptions import HttpResponseError

def safe_search(query_text, **kwargs):
    """
    Perform search with comprehensive error handling
    """
    try:
        results = search_client.search(search_text=query_text, **kwargs)
        return list(results)
    
    except HttpResponseError as e:
        if e.status_code == 400:
            print(f"Bad request - check query syntax: {e.message}")
        elif e.status_code == 404:
            print(f"Index not found: {e.message}")
        else:
            print(f"Search error: {e.message}")
        return []
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []
```

### Query Validation

```python
def validate_query(query_text):
    """
    Validate query before execution
    """
    if not query_text or query_text.strip() == "":
        return False, "Query cannot be empty"
    
    if len(query_text) > 1000:
        return False, "Query too long (max 1000 characters)"
    
    # Check for balanced quotes
    if query_text.count('"') % 2 != 0:
        return False, "Unbalanced quotes in query"
    
    return True, "Query is valid"
```

## Best Practices

### Query Design

1. **Start Simple**: Begin with basic queries and add complexity gradually
2. **Use Appropriate Syntax**: Choose simple vs. full Lucene based on needs
3. **Combine Search and Filters**: Use both for optimal results
4. **Test Query Performance**: Monitor response times and optimize
5. **Handle Edge Cases**: Plan for empty results, errors, and timeouts

### User Experience

1. **Provide Search Suggestions**: Help users construct better queries
2. **Show Result Counts**: Let users know how many results were found
3. **Implement Faceted Navigation**: Allow users to refine results
4. **Handle No Results**: Provide helpful suggestions when searches fail
5. **Progressive Enhancement**: Start with basic search, add advanced features

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No results returned | Query too restrictive | Broaden search terms or filters |
| Too many results | Query too broad | Add filters or more specific terms |
| Slow queries | Complex filters or large result sets | Optimize filters, reduce page size |
| Syntax errors | Invalid OData or Lucene syntax | Validate query syntax |
| Timeout errors | Query too complex | Simplify query or increase timeout |

### Debugging Queries

```python
def debug_search(query_text, **kwargs):
    """
    Debug search queries with detailed logging
    """
    print(f"Executing search: '{query_text}'")
    print(f"Parameters: {kwargs}")
    
    start_time = time.time()
    
    try:
        results = search_client.search(search_text=query_text, **kwargs)
        result_list = list(results)
        
        execution_time = time.time() - start_time
        print(f"Query executed in {execution_time:.2f} seconds")
        print(f"Found {len(result_list)} results")
        
        return result_list
    
    except Exception as e:
        print(f"Query failed: {str(e)}")
        return []
```

## Next Steps

After mastering simple queries and filters, you're ready to explore more advanced search capabilities:

- **Module 5: Advanced Querying** - Complex queries, faceting, and suggestions
- **Module 6: Search Analytics** - Monitoring and optimizing search performance
- **Module 7: Custom Scoring** - Implementing custom relevance algorithms

## Summary

In this module, you learned how to:

- ✅ Construct effective search queries using simple and Lucene syntax
- ✅ Apply filters to narrow results using OData expressions
- ✅ Implement sorting and pagination for better user experience
- ✅ Customize search results with field selection and highlighting
- ✅ Handle errors and optimize query performance
- ✅ Apply best practices for production search applications

You now have the foundation to build sophisticated search experiences that deliver relevant, well-organized results to your users.