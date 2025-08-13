# Practice & Implementation - Module 4: Simple Queries

## Hands-On Exercises

This section provides practical exercises to help you master simple queries in Azure AI Search. Each exercise builds upon the previous one, covering different query types and techniques that form the foundation of search applications.

## Exercise 1: Basic Text Search

### Objective
Learn to construct and execute basic text search queries using different query modes and syntax options.

### Prerequisites
- Azure AI Search service with sample data
- Understanding of basic search concepts
- Index with searchable text fields

### Steps

1. **Simple Text Search**
   - Execute basic keyword searches
   - Understand default search behavior
   - Test with single and multiple terms

2. **Search Modes**
   - Compare "any" vs "all" search modes
   - Understand impact on result relevance
   - Test with different query combinations

3. **Query Types**
   - Use simple query syntax (default)
   - Experiment with full Lucene syntax
   - Understand when to use each type

### Expected Outcome
- Understanding of basic search mechanics
- Knowledge of query modes and their impact
- Ability to construct effective text searches

## Exercise 2: Field-Specific Searches

### Objective
Learn to target specific fields in your search queries and understand field weighting.

### Prerequisites
- Completed Exercise 1
- Index with multiple searchable fields
- Understanding of field attributes

### Steps

1. **Single Field Search**
   - Search within specific fields
   - Use searchFields parameter
   - Compare results across different fields

2. **Multi-Field Search**
   - Search across multiple specific fields
   - Understand field weighting
   - Test relevance with different field combinations

3. **Field Boosting**
   - Apply field-specific boosting
   - Understand impact on relevance scoring
   - Test with different boost values

### Expected Outcome
- Ability to target specific fields in searches
- Understanding of field weighting and boosting
- Knowledge of relevance impact

## Exercise 3: Boolean and Phrase Searches

### Objective
Master boolean operators and phrase searching for more precise query control.

### Prerequisites
- Completed Exercise 2
- Understanding of boolean logic
- Sample data with varied content

### Steps

1. **Boolean Operators**
   - Use AND, OR, NOT operators
   - Combine multiple boolean conditions
   - Understand operator precedence

2. **Phrase Searches**
   - Search for exact phrases
   - Use proximity searches
   - Understand phrase matching behavior

3. **Complex Boolean Queries**
   - Combine boolean operators with phrases
   - Use parentheses for grouping
   - Test complex query scenarios

### Expected Outcome
- Mastery of boolean search operators
- Understanding of phrase search mechanics
- Ability to construct complex boolean queries

## Exercise 4: Wildcard and Fuzzy Searches

### Objective
Learn to handle partial matches and typos using wildcard and fuzzy search techniques.

### Prerequisites
- Completed Exercise 3
- Understanding of pattern matching
- Data with varied spelling and formats

### Steps

1. **Wildcard Searches**
   - Use * and ? wildcards
   - Understand wildcard limitations
   - Test with different wildcard patterns

2. **Fuzzy Searches**
   - Implement fuzzy matching for typos
   - Adjust fuzzy distance parameters
   - Test with common misspellings

3. **Prefix Searches**
   - Implement autocomplete-style searches
   - Use prefix matching effectively
   - Understand performance implications

### Expected Outcome
- Ability to handle partial matches
- Understanding of fuzzy search capabilities
- Knowledge of wildcard search patterns

## Exercise 5: Result Customization

### Objective
Learn to customize search results by selecting fields, highlighting matches, and controlling result format.

### Prerequisites
- Completed Exercise 4
- Understanding of result structure
- Index with various field types

### Steps

1. **Field Selection**
   - Use select parameter to control returned fields
   - Optimize payload size
   - Handle complex field selection

2. **Hit Highlighting**
   - Enable search term highlighting
   - Customize highlighting tags
   - Test with different content types

3. **Result Counting**
   - Include total result counts
   - Understand performance impact
   - Use counting strategically

### Expected Outcome
- Ability to customize result presentation
- Understanding of hit highlighting
- Knowledge of result optimization techniques

## Real-World Scenarios

### Scenario 1: E-commerce Product Search

**Challenge**: Implement product search with various query types and result customization.

**Implementation Steps**:
1. Basic product name and description search
2. Category and brand-specific searches
3. Boolean combinations for complex filters
4. Fuzzy search for handling typos
5. Result highlighting for better UX

**Key Learning Points**:
- Multi-field search strategies
- Handling user input variations
- Optimizing for user experience
- Performance considerations

### Scenario 2: Document Search System

**Challenge**: Build a document search system with advanced query capabilities.

**Implementation Steps**:
1. Full-text search across document content
2. Author and title-specific searches
3. Date range and metadata searches
4. Boolean combinations for complex queries
5. Phrase searches for exact content matching

**Key Learning Points**:
- Content-focused search strategies
- Metadata utilization
- Complex query construction
- Relevance optimization

### Scenario 3: Knowledge Base Search

**Challenge**: Create a knowledge base search with intelligent query handling.

**Implementation Steps**:
1. Question and answer content search
2. Topic and category-based searches
3. Fuzzy matching for question variations
4. Boolean logic for complex topics
5. Result customization for answer display

**Key Learning Points**:
- Natural language query handling
- Topic-based search organization
- User intent interpretation
- Answer-focused result presentation

## Advanced Query Patterns

### Pattern 1: Progressive Search Enhancement

Start with simple queries and progressively add complexity:

1. **Basic Search**: Simple keyword matching
2. **Field-Specific**: Target relevant fields
3. **Boolean Logic**: Add precision with operators
4. **Fuzzy Matching**: Handle variations and typos
5. **Result Optimization**: Customize for user experience

### Pattern 2: Multi-Strategy Search

Implement multiple search strategies for different scenarios:

1. **Exact Match**: For precise queries
2. **Fuzzy Match**: For handling typos
3. **Partial Match**: For autocomplete scenarios
4. **Boolean Search**: For complex requirements
5. **Fallback Search**: For no-results scenarios

### Pattern 3: Context-Aware Searching

Adapt search behavior based on context:

1. **User Profile**: Personalize based on user preferences
2. **Search History**: Learn from previous queries
3. **Content Type**: Adapt to different content types
4. **Device Context**: Optimize for mobile vs desktop
5. **Time Context**: Consider temporal relevance

## Query Optimization Techniques

### Performance Optimization
- Use specific fields instead of searching all fields
- Implement appropriate query types for use cases
- Optimize result set sizes
- Use caching for frequent queries

### Relevance Optimization
- Apply field boosting strategically
- Use appropriate search modes
- Implement custom scoring profiles
- Test with real user queries

### User Experience Optimization
- Provide search suggestions and autocomplete
- Implement spell checking and correction
- Offer search refinement options
- Display helpful no-results messages

## Testing and Validation

### Query Testing Framework
```python
def test_search_query(query, expected_results=None, min_results=0):
    """Test search query and validate results"""
    results = search_client.search(query)
    
    # Validate result count
    assert len(list(results)) >= min_results
    
    # Validate expected results if provided
    if expected_results:
        result_ids = [r['id'] for r in results]
        for expected_id in expected_results:
            assert expected_id in result_ids
    
    return results
```

### Relevance Testing
- Test with known good queries and expected results
- Validate ranking order for important queries
- Test edge cases and boundary conditions
- Gather user feedback on result quality

### Performance Testing
- Measure query response times
- Test with various query complexities
- Monitor resource utilization
- Test under load conditions

## Common Query Patterns

### Search Box Implementation
```javascript
// Basic search box with multiple query types
function executeSearch(query, searchType = 'simple') {
    const searchParams = {
        search: query,
        queryType: searchType,
        searchMode: 'any',
        highlight: 'title,content',
        select: 'id,title,content,category',
        top: 20
    };
    
    return searchClient.search(searchParams);
}
```

### Autocomplete Implementation
```javascript
// Autocomplete with prefix matching
function getAutocompleteSuggestions(prefix) {
    return searchClient.search({
        search: prefix + '*',
        queryType: 'simple',
        searchFields: 'title,tags',
        select: 'title',
        top: 10
    });
}
```

### Advanced Search Form
```javascript
// Advanced search with multiple criteria
function advancedSearch(criteria) {
    let query = '';
    
    // Build boolean query from criteria
    if (criteria.title) {
        query += `title:(${criteria.title})`;
    }
    
    if (criteria.category) {
        query += query ? ` AND category:(${criteria.category})` : `category:(${criteria.category})`;
    }
    
    if (criteria.dateRange) {
        query += query ? ` AND created:[${criteria.dateRange.start} TO ${criteria.dateRange.end}]` : `created:[${criteria.dateRange.start} TO ${criteria.dateRange.end}]`;
    }
    
    return searchClient.search({
        search: query,
        queryType: 'full'
    });
}
```

## Troubleshooting Common Issues

### No Results Returned
1. Check query syntax and spelling
2. Verify field names and searchable attributes
3. Test with simpler queries
4. Check data exists in index
5. Validate search permissions

### Poor Result Relevance
1. Review field boosting and weights
2. Check analyzer configuration
3. Test different search modes
4. Validate query construction
5. Consider custom scoring profiles

### Slow Query Performance
1. Optimize query complexity
2. Use specific fields instead of all fields
3. Implement result pagination
4. Consider query caching
5. Monitor service resources

## Best Practices Implementation

### Query Construction
- Start with simple queries and add complexity gradually
- Use appropriate query types for different scenarios
- Implement proper error handling
- Validate user input before querying

### Result Handling
- Implement pagination for large result sets
- Provide meaningful feedback for no results
- Cache frequently used queries
- Optimize result payload size

### User Experience
- Provide search suggestions and autocomplete
- Implement spell checking and correction
- Offer search refinement options
- Display search progress and feedback

## Next Steps

After completing these exercises:

1. **Advanced Querying**: Move to intermediate modules for complex queries
2. **Integration**: Implement queries in real applications
3. **Optimization**: Focus on performance and relevance tuning
4. **User Experience**: Enhance search interfaces and interactions

## Additional Resources

- [Query Troubleshooting Guide](./query-troubleshooting.md)
- [Performance Troubleshooting](./performance-troubleshooting.md)
- [Code Samples](./code-samples/README.md)
- [Azure AI Search Query Documentation](https://docs.microsoft.com/azure/search/search-query-overview)