# Best Practices - Module 4: Simple Queries

## Query Construction Best Practices

### Query Design Principles
- **Start Simple**: Begin with basic queries and add complexity gradually
- **Be Specific**: Use targeted fields rather than searching all fields when possible
- **User Intent**: Design queries to match user search intent and behavior
- **Performance First**: Consider performance implications of query choices

### Query Syntax Guidelines
- **Consistent Syntax**: Use consistent query syntax throughout your application
- **Escape Special Characters**: Properly escape special characters in user input
- **Validate Input**: Always validate and sanitize user input before querying
- **Error Handling**: Implement robust error handling for malformed queries

### Field Selection Strategy
```javascript
// Good: Specific field targeting
{
  search: "luxury hotel",
  searchFields: "title,description",
  select: "id,title,rating,price"
}

// Avoid: Searching all fields unnecessarily
{
  search: "luxury hotel"
  // This searches all searchable fields
}
```

## Performance Optimization

### Query Efficiency
- **Limit Result Sets**: Use appropriate `top` values to limit result sizes
- **Field Selection**: Only retrieve fields you actually need
- **Avoid Wildcards**: Minimize use of leading wildcards (e.g., `*term`)
- **Cache Results**: Implement caching for frequently executed queries

### Search Mode Selection
```javascript
// For broad matching (default)
{
  search: "luxury hotel",
  searchMode: "any"  // Matches documents with "luxury" OR "hotel"
}

// For precise matching
{
  search: "luxury hotel",
  searchMode: "all"  // Matches documents with "luxury" AND "hotel"
}
```

### Resource Management
- **Connection Pooling**: Use connection pooling for better resource utilization
- **Batch Operations**: Group related queries when possible
- **Monitor Usage**: Track query patterns and optimize accordingly
- **Rate Limiting**: Implement appropriate rate limiting for user queries

## User Experience Best Practices

### Search Interface Design
- **Progressive Enhancement**: Start with basic search and add advanced features
- **Clear Feedback**: Provide clear feedback for search operations
- **Loading States**: Show loading indicators for search operations
- **Error Messages**: Display helpful error messages for failed searches

### Result Presentation
```javascript
// Good: Optimized result presentation
{
  search: "hotel",
  highlight: "title,description",
  select: "id,title,description,rating,price,location",
  top: 20,
  count: true
}
```

### Search Suggestions
- **Autocomplete**: Implement autocomplete for better user experience
- **Spell Correction**: Provide spell correction suggestions
- **Query Suggestions**: Offer related query suggestions
- **No Results Handling**: Provide helpful alternatives when no results are found

## Query Types and When to Use Them

### Simple Query Syntax (Default)
**Best for:**
- Basic keyword searches
- User-friendly search boxes
- Most common search scenarios

```javascript
{
  search: "luxury hotel seattle",
  queryType: "simple"  // Default
}
```

### Full Lucene Syntax
**Best for:**
- Advanced search features
- Complex boolean logic
- Proximity searches
- Wildcard and fuzzy searches

```javascript
{
  search: "title:(luxury AND hotel) OR description:resort",
  queryType: "full"
}
```

## Boolean Logic Best Practices

### Operator Usage
```javascript
// Clear boolean logic
{
  search: "hotel AND (luxury OR premium) NOT budget",
  queryType: "full"
}

// Grouped conditions
{
  search: "(title:hotel OR title:resort) AND rating:[4 TO 5]",
  queryType: "full"
}
```

### Precedence and Grouping
- **Use Parentheses**: Always use parentheses to make precedence clear
- **Logical Grouping**: Group related conditions together
- **Avoid Complexity**: Keep boolean expressions as simple as possible
- **Test Thoroughly**: Test complex boolean queries with various data scenarios

## Field-Specific Search Strategies

### Single Field Searches
```javascript
// Searching specific fields
{
  search: "luxury",
  searchFields: "title",  // Only search in title field
  select: "id,title,description"
}
```

### Multi-Field Searches with Weighting
```javascript
// Weighted field searches (using scoring profiles)
{
  search: "hotel",
  searchFields: "title^3,description^1,tags^2",  // Title has 3x weight
  scoringProfile: "titleBoost"
}
```

### Field-Specific Boosting
- **Title Fields**: Typically get higher weight for relevance
- **Content Fields**: Standard weight for main content
- **Metadata Fields**: Lower weight for supplementary information
- **Tag Fields**: Medium weight for categorization

## Fuzzy and Wildcard Search Guidelines

### Fuzzy Search Best Practices
```javascript
// Fuzzy search for typo tolerance
{
  search: "hotel~1",  // Allow 1 character difference
  queryType: "full"
}

// Fuzzy search with distance control
{
  search: "seattle~2",  // Allow up to 2 character differences
  queryType: "full"
}
```

### Wildcard Search Guidelines
- **Avoid Leading Wildcards**: `*term` is slower than `term*`
- **Use Sparingly**: Wildcards can impact performance
- **Combine Wisely**: Combine with other query techniques
- **Test Performance**: Always test wildcard queries under load

```javascript
// Good: Trailing wildcard
{
  search: "hotel*",
  queryType: "full"
}

// Avoid: Leading wildcard (slower)
{
  search: "*otel",
  queryType: "full"
}
```

## Result Optimization

### Hit Highlighting
```javascript
// Effective hit highlighting
{
  search: "luxury hotel",
  highlight: "title,description",
  highlightPreTag: "<mark>",
  highlightPostTag: "</mark>"
}
```

### Field Selection Optimization
```javascript
// Optimized field selection
{
  search: "hotel",
  select: "id,title,rating,price",  // Only necessary fields
  top: 20,  // Reasonable page size
  count: true  // Include total count when needed
}
```

### Pagination Strategy
- **Reasonable Page Sizes**: Use 10-50 results per page typically
- **Skip Limitations**: Be aware of skip limitations for deep pagination
- **Alternative Approaches**: Consider search-after pattern for large datasets
- **User Experience**: Provide clear pagination controls

## Error Handling and Resilience

### Query Validation
```javascript
function validateQuery(query) {
  // Check for empty queries
  if (!query || query.trim().length === 0) {
    throw new Error("Query cannot be empty");
  }
  
  // Check for excessively long queries
  if (query.length > 1000) {
    throw new Error("Query too long");
  }
  
  // Sanitize special characters if needed
  return sanitizeQuery(query);
}
```

### Error Recovery
- **Graceful Degradation**: Provide fallback search options
- **User Feedback**: Give clear error messages to users
- **Retry Logic**: Implement appropriate retry mechanisms
- **Logging**: Log errors for debugging and monitoring

### Timeout Handling
```javascript
// Implement query timeouts
const searchWithTimeout = async (query, timeout = 5000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const results = await searchClient.search(query, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return results;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Search request timed out');
    }
    throw error;
  }
};
```

## Security Best Practices

### Input Sanitization
- **Validate Input**: Always validate user input before processing
- **Escape Characters**: Properly escape special characters
- **Length Limits**: Implement reasonable query length limits
- **Rate Limiting**: Prevent abuse with rate limiting

### Access Control
- **Authentication**: Ensure proper authentication for search operations
- **Authorization**: Implement appropriate authorization checks
- **API Keys**: Secure API keys and rotate them regularly
- **Audit Logging**: Log search operations for security monitoring

## Monitoring and Analytics

### Query Performance Monitoring
```javascript
// Monitor query performance
const monitoredSearch = async (query) => {
  const startTime = Date.now();
  
  try {
    const results = await searchClient.search(query);
    const duration = Date.now() - startTime;
    
    // Log performance metrics
    logMetrics({
      query: query.search,
      duration,
      resultCount: results.length,
      success: true
    });
    
    return results;
  } catch (error) {
    const duration = Date.now() - startTime;
    
    logMetrics({
      query: query.search,
      duration,
      error: error.message,
      success: false
    });
    
    throw error;
  }
};
```

### Usage Analytics
- **Query Patterns**: Track common query patterns
- **Performance Metrics**: Monitor response times and success rates
- **User Behavior**: Analyze user search behavior
- **Result Quality**: Track result click-through rates

## Testing Strategies

### Unit Testing
```javascript
// Test query construction
describe('Query Construction', () => {
  test('should build basic search query', () => {
    const query = buildSearchQuery('hotel', { top: 10 });
    expect(query.search).toBe('hotel');
    expect(query.top).toBe(10);
  });
  
  test('should handle special characters', () => {
    const query = buildSearchQuery('hotel & spa');
    expect(query.search).toBe('hotel \\& spa');
  });
});
```

### Integration Testing
- **End-to-End Tests**: Test complete search workflows
- **Performance Tests**: Test under realistic load conditions
- **Error Scenarios**: Test error handling and recovery
- **Cross-Browser Tests**: Ensure compatibility across browsers

### A/B Testing
- **Query Variations**: Test different query approaches
- **Result Presentation**: Test different result formats
- **User Interface**: Test different search interfaces
- **Performance Impact**: Measure impact of changes

## Common Anti-Patterns to Avoid

### Query Construction Anti-Patterns
- ❌ **Overly Complex Queries**: Avoid unnecessarily complex boolean logic
- ❌ **Unescaped Input**: Never use raw user input without sanitization
- ❌ **Hardcoded Values**: Avoid hardcoding search parameters
- ❌ **Ignoring Performance**: Don't ignore query performance implications

### Result Handling Anti-Patterns
- ❌ **Loading All Results**: Don't load all results at once for large datasets
- ❌ **Ignoring Errors**: Always handle search errors gracefully
- ❌ **Poor Pagination**: Avoid inefficient pagination strategies
- ❌ **No Caching**: Don't ignore caching opportunities

### User Experience Anti-Patterns
- ❌ **No Feedback**: Don't leave users without search feedback
- ❌ **Poor Error Messages**: Avoid cryptic error messages
- ❌ **Slow Responses**: Don't ignore search performance
- ❌ **No Fallbacks**: Always provide fallback options

## Checklist for Production Readiness

### Query Implementation
- [ ] Input validation and sanitization implemented
- [ ] Appropriate query types selected for use cases
- [ ] Error handling and recovery mechanisms in place
- [ ] Performance optimization applied

### User Experience
- [ ] Clear search interface with appropriate feedback
- [ ] Loading states and progress indicators
- [ ] Helpful error messages and fallback options
- [ ] Responsive design for different devices

### Performance
- [ ] Query performance optimized
- [ ] Appropriate caching strategies implemented
- [ ] Resource utilization monitored
- [ ] Scalability considerations addressed

### Security
- [ ] Input validation and sanitization
- [ ] Authentication and authorization
- [ ] Rate limiting and abuse prevention
- [ ] Audit logging and monitoring

### Monitoring
- [ ] Performance metrics collection
- [ ] Error tracking and alerting
- [ ] Usage analytics implementation
- [ ] Regular performance reviews

By following these best practices, you'll create robust, performant, and user-friendly search experiences that scale with your needs and provide excellent search functionality for your users.