# Module 2: Search Operations Troubleshooting

## Overview

This guide helps you resolve common issues encountered while performing search operations in Azure AI Search. Issues are organized by category with clear solutions and debugging techniques.

## Common Issues and Solutions

### 1. No Results Found

**Problem**: Search returns no results even though you expect matches.

**Possible Causes and Solutions**:

- **Index is empty**: Verify your index contains documents
  ```python
  # Check document count
  stats = search_client.get_document_count()
  print(f"Index contains {stats} documents")
  ```

- **Wrong index name**: Verify you're searching the correct index
  ```python
  # List available indexes
  from azure.search.documents.indexes import SearchIndexClient
  index_client = SearchIndexClient(endpoint, credential)
  indexes = index_client.list_indexes()
  for index in indexes:
      print(f"Available index: {index.name}")
  ```

- **Query too specific**: Try broader search terms
  ```python
  # Instead of exact phrase
  results = search_client.search(search_text='"exact phrase"')
  
  # Try individual terms
  results = search_client.search(search_text='exact phrase', search_mode='any')
  ```

### 2. Unexpected Results

**Problem**: Search returns irrelevant or unexpected results.

**Solutions**:

- **Check search mode**: Use "all" for more precise results
  ```python
  # More precise - all terms must match
  results = search_client.search(search_text="python tutorial", search_mode="all")
  ```

- **Use field-specific search**: Limit search to relevant fields
  ```python
  # Search only in title and description
  results = search_client.search(
      search_text="python",
      search_fields=["title", "description"]
  )
  ```

- **Examine search scores**: Low scores indicate weak matches
  ```python
  for result in results:
      if result['@search.score'] < 1.0:
          print(f"Weak match (score: {result['@search.score']:.3f}): {result.get('title')}")
  ```

### 3. Performance Issues

**Problem**: Searches are slow or timing out.

**Solutions**:

- **Limit result count**: Use `top` parameter
  ```python
  # Limit to 20 results for faster response
  results = search_client.search(search_text="query", top=20)
  ```

- **Select only needed fields**: Reduce data transfer
  ```python
  # Return only essential fields
  results = search_client.search(
      search_text="query",
      select=["id", "title", "summary"]
  )
  ```

- **Use pagination**: Process results in chunks
  ```python
  # Process 10 results at a time
  for skip in range(0, 100, 10):
      batch = search_client.search(search_text="query", top=10, skip=skip)
      process_batch(list(batch))
  ```

### 4. Authentication Errors

**Problem**: Getting 401 or 403 errors.

**Solutions**:

- **Verify API key**: Check your API key is correct and active
  ```python
  # Test connection
  try:
      count = search_client.get_document_count()
      print(f"Connection successful. Document count: {count}")
  except Exception as e:
      print(f"Connection failed: {e}")
  ```

- **Check permissions**: Ensure your key has search permissions
- **Verify endpoint**: Make sure the service URL is correct

### 5. Query Syntax Errors

**Problem**: Getting 400 errors due to invalid query syntax.

**Solutions**:

- **Escape special characters**: Handle quotes and operators properly
  ```python
  # Escape quotes in user input
  def escape_query(query):
      return query.replace('"', '\\"')
  
  safe_query = escape_query(user_input)
  results = search_client.search(search_text=safe_query)
  ```

- **Validate boolean operators**: Ensure proper AND/OR/NOT usage
  ```python
  # Valid boolean query
  results = search_client.search(search_text="python AND (tutorial OR guide)")
  ```

## Debugging Tools

### Enable Logging

```python
import logging

# Enable Azure SDK logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('azure.search.documents')
logger.setLevel(logging.DEBUG)
```

### Search Result Analysis

```python
def analyze_search_results(query, top=10):
    """Analyze search results for debugging"""
    results = search_client.search(
        search_text=query,
        top=top,
        include_total_count=True
    )
    
    result_list = list(results)
    
    print(f"Query: '{query}'")
    print(f"Total results: {results.get_count()}")
    print(f"Returned: {len(result_list)}")
    print(f"Score range: {min(r['@search.score'] for r in result_list):.3f} - {max(r['@search.score'] for r in result_list):.3f}")
    
    # Show top results
    print("\nTop results:")
    for i, result in enumerate(result_list[:5], 1):
        print(f"{i}. Score: {result['@search.score']:.3f} - {result.get('title', 'No title')}")
```

## Advanced Debugging Techniques

### Query Analysis

```python
def debug_query(query):
    """Debug query execution step by step"""
    print(f"Original query: '{query}'")
    
    # Test different variations
    variations = [
        (query, "original"),
        (f'"{query}"', "exact phrase"),
        (query.replace(' ', ' AND '), "AND terms"),
        (query.replace(' ', ' OR '), "OR terms"),
        (f"{query}*", "wildcard")
    ]
    
    for test_query, description in variations:
        try:
            results = list(search_client.search(search_text=test_query, top=3))
            print(f"{description}: {len(results)} results")
            if results:
                print(f"  Top score: {results[0]['@search.score']:.3f}")
        except Exception as e:
            print(f"{description}: Error - {e}")
```

### Index Health Check

```python
def check_index_health():
    """Perform comprehensive index health check"""
    try:
        # Check document count
        doc_count = search_client.get_document_count()
        print(f"✅ Index contains {doc_count} documents")
        
        # Test basic search
        test_results = list(search_client.search("*", top=1))
        if test_results:
            print("✅ Basic search works")
            print(f"   Sample document fields: {list(test_results[0].keys())}")
        else:
            print("❌ No documents found in index")
        
        # Test specific search
        specific_results = list(search_client.search("test", top=1))
        print(f"✅ Specific search returned {len(specific_results)} results")
        
    except Exception as e:
        print(f"❌ Index health check failed: {e}")
```

## Prevention Tips

### Best Practices to Avoid Issues

1. **Always validate input**: Check queries before sending
2. **Use appropriate search modes**: Choose "all" vs "any" based on needs
3. **Implement proper error handling**: Catch and handle all exception types
4. **Monitor search performance**: Track slow queries and optimize
5. **Test with various query types**: Ensure all search patterns work
6. **Keep indexes optimized**: Regular maintenance and updates

### Monitoring and Alerting

```python
def monitor_search_performance(query, threshold_ms=1000):
    """Monitor search performance and alert on slow queries"""
    import time
    
    start_time = time.time()
    try:
        results = list(search_client.search(query, top=10))
        execution_time = (time.time() - start_time) * 1000
        
        if execution_time > threshold_ms:
            print(f"⚠️ Slow query detected: {execution_time:.2f}ms for '{query}'")
        else:
            print(f"✅ Query performed well: {execution_time:.2f}ms")
        
        return results
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return []
```

---

**Need more help?** Check the [Prerequisites Troubleshooting](prerequisites-troubleshooting.md) for setup-related issues, or review the [Best Practices](best-practices.md) for optimal search implementation patterns.