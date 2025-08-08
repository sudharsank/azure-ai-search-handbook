# Module 2: Practice and Implementation

## Overview

Now that you understand the concepts of Azure AI Search basic operations, it's time to put your knowledge into practice with real code examples and hands-on exercises.

## 🎯 **Ready to Code?**

Now that you understand the concepts, it's time to practice with real code:

### 1. **📓 Start with Interactive Learning**
   - Open the [Jupyter Notebook](code-samples/basic_search.ipynb) for guided, step-by-step examples
   - Run each cell and experiment with different queries
   - Modify examples to test your understanding

### 2. **🐍 Explore Complete Examples**
   - Run [`basic_search.py`](code-samples/basic_search.py) to see all search operations in action
   - Study [`search_variations.py`](code-samples/search_variations.py) for different query patterns
   - Experiment with different search parameters and observe the results

### 3. **🛡️ Learn Production Patterns**
   - Review [`error_handling.py`](code-samples/error_handling.py) for robust error handling
   - Explore [`advanced_patterns.py`](code-samples/advanced_patterns.py) for sophisticated search strategies
   - Understand how to implement fallback mechanisms and retry logic

### 4. **📊 Master Result Processing**
   - Use [`result_processing.py`](code-samples/result_processing.py) for formatting and analysis
   - Learn to export results in multiple formats
   - Practice with pagination and result filtering

## 📚 **Complete Code Samples Guide**

Visit the [code samples documentation](code-samples.md) for:

- **Detailed explanations** of each file and its purpose
- **Usage examples** and code snippets you can copy and modify
- **Configuration instructions** for different environments
- **Troubleshooting guides** for common issues
- **Performance tips** and optimization techniques

## 🎯 **Learning Paths**

### **Beginner Path** (Recommended)

1. **Theory First**: Complete reading the main documentation
2. **Setup**: Ensure [prerequisites](prerequisites.md) are completed
3. **Interactive**: Start with the Jupyter notebook for guided learning
4. **Practice**: Work through Python examples sequentially
5. **Experiment**: Modify examples with your own queries and data

### **Hands-On Path**

1. **Jump In**: Start directly with code examples
2. **Learn by Doing**: Run examples and observe outputs
3. **Reference**: Use documentation to understand concepts as needed
4. **Customize**: Adapt examples to your specific use cases

### **Production Path**

1. **Best Practices**: Review [best practices guide](best-practices.md)
2. **Error Handling**: Study robust error handling patterns
3. **Performance**: Learn optimization techniques
4. **Integration**: Implement in your own applications

## 🔧 **Practical Exercises**

### Exercise 1: Basic Search Mastery
**Objective**: Master all 5 basic search types

**Tasks**:

1. Perform simple text searches with different keywords
2. Practice phrase searches with exact matches
3. Build complex boolean queries using AND, OR, NOT
4. Use wildcards to find term variations
5. Target specific fields for precise results

**Success Criteria**:

- [ ] Can execute all 5 search types successfully
- [ ] Understands when to use each search type
- [ ] Can combine different search techniques

### Exercise 2: Result Processing
**Objective**: Learn to handle and format search results effectively

**Tasks**:

1. Extract key information from search results
2. Format results for different display contexts
3. Implement pagination for large result sets
4. Sort results by different criteria (score, date, etc.)
5. Create result summaries and statistics

**Success Criteria**:

- [ ] Can process results programmatically
- [ ] Understands search scores and relevance
- [ ] Can implement pagination correctly

### Exercise 3: Error Handling
**Objective**: Build robust search applications

**Tasks**:

1. Handle connection errors gracefully
2. Validate user input before searching
3. Implement fallback strategies for failed searches
4. Log errors appropriately for debugging
5. Provide user-friendly error messages

**Success Criteria**:

- [ ] Application doesn't crash on errors
- [ ] Users receive helpful error messages
- [ ] Errors are logged for troubleshooting

### Exercise 4: Performance Optimization
**Objective**: Create efficient search implementations

**Tasks**:

1. Limit result sets to necessary sizes
2. Select only required fields in results
3. Implement result caching where appropriate
4. Use field-specific searches for better performance
5. Monitor and measure search performance

**Success Criteria**:

- [ ] Searches complete in reasonable time
- [ ] Network traffic is minimized
- [ ] Application scales with usage

## 🚀 **Implementation Patterns**

### Pattern 1: Simple Search Interface
```python
def simple_search_interface():
    """Basic search interface for user queries"""
    while True:
        query = input("Enter search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        try:
            results = search_client.search(query, top=5)
            print(f"\nFound results for '{query}':")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   Score: {result['@search.score']:.3f}")
                print(f"   Author: {result.get('author', 'Unknown')}")
                print()
                
        except Exception as e:
            print(f"Search failed: {e}")
```

### Pattern 2: Advanced Search with Filters
```python
def advanced_search(query, filters=None, sort_by=None):
    """Advanced search with filtering and sorting"""
    search_params = {
        'search_text': query,
        'top': 20,
        'include_total_count': True
    }
    
    if filters:
        search_params['filter'] = filters
    
    if sort_by:
        search_params['order_by'] = sort_by
    
    try:
        results = search_client.search(**search_params)
        return {
            'results': list(results),
            'total_count': results.get_count(),
            'success': True
        }
    except Exception as e:
        return {
            'results': [],
            'total_count': 0,
            'success': False,
            'error': str(e)
        }
```

### Pattern 3: Search with Analytics
```python
import time
from collections import defaultdict

class SearchAnalytics:
    def __init__(self):
        self.search_stats = defaultdict(int)
        self.performance_stats = []
    
    def tracked_search(self, query):
        """Search with performance tracking"""
        start_time = time.time()
        
        try:
            results = list(search_client.search(query, top=10))
            execution_time = time.time() - start_time
            
            # Track statistics
            self.search_stats['total_searches'] += 1
            self.search_stats['successful_searches'] += 1
            self.performance_stats.append(execution_time)
            
            return {
                'results': results,
                'execution_time': execution_time,
                'result_count': len(results)
            }
            
        except Exception as e:
            self.search_stats['failed_searches'] += 1
            return {
                'results': [],
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def get_stats(self):
        """Get search analytics"""
        avg_time = sum(self.performance_stats) / len(self.performance_stats) if self.performance_stats else 0
        return {
            'total_searches': self.search_stats['total_searches'],
            'success_rate': self.search_stats['successful_searches'] / max(1, self.search_stats['total_searches']),
            'average_response_time': avg_time,
            'fastest_search': min(self.performance_stats) if self.performance_stats else 0,
            'slowest_search': max(self.performance_stats) if self.performance_stats else 0
        }
```

## 🔍 **Testing Your Implementation**

### Unit Testing Example
```python
import unittest
from unittest.mock import Mock, patch

class TestSearchFunctionality(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
    
    def test_simple_search(self):
        """Test basic search functionality"""
        # Mock search results
        mock_results = [
            {'title': 'Test Document', '@search.score': 1.5},
            {'title': 'Another Document', '@search.score': 1.2}
        ]
        self.mock_client.search.return_value = mock_results
        
        # Test search
        results = list(self.mock_client.search("test query"))
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Test Document')
        self.mock_client.search.assert_called_once_with("test query")
    
    def test_error_handling(self):
        """Test error handling in search"""
        # Mock search exception
        self.mock_client.search.side_effect = Exception("Connection failed")
        
        # Test error handling
        try:
            results = list(self.mock_client.search("test query"))
            self.fail("Expected exception was not raised")
        except Exception as e:
            self.assertEqual(str(e), "Connection failed")

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing
```python
def integration_test():
    """Test complete search workflow"""
    print("Running integration tests...")
    
    # Test 1: Basic connectivity
    try:
        count = search_client.get_document_count()
        print(f"✅ Connection test passed - {count} documents in index")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    # Test 2: Simple search
    try:
        results = list(search_client.search("test", top=1))
        print(f"✅ Simple search test passed - {len(results)} results")
    except Exception as e:
        print(f"❌ Simple search test failed: {e}")
        return False
    
    # Test 3: Complex search
    try:
        results = list(search_client.search("python AND tutorial", top=5))
        print(f"✅ Complex search test passed - {len(results)} results")
    except Exception as e:
        print(f"❌ Complex search test failed: {e}")
        return False
    
    print("🎉 All integration tests passed!")
    return True
```

## 📈 **Performance Monitoring**

### Search Performance Metrics
```python
class SearchPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'total_searches': 0,
            'total_time': 0,
            'slow_searches': 0,
            'failed_searches': 0
        }
    
    def monitor_search(self, query, threshold_ms=1000):
        """Monitor search performance"""
        start_time = time.time()
        
        try:
            results = list(search_client.search(query))
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update metrics
            self.metrics['total_searches'] += 1
            self.metrics['total_time'] += execution_time
            
            if execution_time > threshold_ms:
                self.metrics['slow_searches'] += 1
                print(f"⚠️ Slow search detected: {execution_time:.2f}ms for '{query}'")
            
            return results
            
        except Exception as e:
            self.metrics['failed_searches'] += 1
            print(f"❌ Search failed: {e}")
            return []
    
    def get_performance_report(self):
        """Generate performance report"""
        if self.metrics['total_searches'] == 0:
            return "No searches performed yet"
        
        avg_time = self.metrics['total_time'] / self.metrics['total_searches']
        success_rate = ((self.metrics['total_searches'] - self.metrics['failed_searches']) / 
                       self.metrics['total_searches']) * 100
        
        return f"""
Performance Report:
- Total searches: {self.metrics['total_searches']}
- Average response time: {avg_time:.2f}ms
- Success rate: {success_rate:.1f}%
- Slow searches: {self.metrics['slow_searches']}
- Failed searches: {self.metrics['failed_searches']}
        """
```

## 🎓 **Next Steps After Practice**

Once you've completed the practice exercises:

1. **📖 [Review Best Practices](best-practices.md)** - Learn professional implementation techniques
2. **🛠️ [Study Troubleshooting](search-troubleshooting.md)** - Prepare for common issues  
3. **🎯 [Move to Module 3](../module-03-index-management/overview.md)** - Learn index management
4. **🔧 [Build Your Own Project](../../../setup/README.md)** - Apply concepts to real applications

## 📋 **Practice Completion Checklist**

You've mastered basic search operations when you can:

- [ ] **Execute all search types** - Simple, phrase, boolean, wildcard, field-specific
- [ ] **Handle results effectively** - Process, format, and paginate results
- [ ] **Implement error handling** - Graceful error recovery and user feedback
- [ ] **Optimize performance** - Efficient queries and result processing
- [ ] **Test your code** - Unit tests and integration tests
- [ ] **Monitor performance** - Track and analyze search metrics
- [ ] **Adapt to your needs** - Customize examples for your use cases

---

**Ready to build something amazing?** You now have the foundation to create powerful search applications with Azure AI Search! 🚀