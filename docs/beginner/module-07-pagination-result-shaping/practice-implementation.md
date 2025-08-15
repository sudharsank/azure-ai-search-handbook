# Practice & Implementation - Module 7: Pagination & Result Shaping

## Learning Path

This module provides hands-on exercises to master pagination and result shaping in Azure AI Search. Work through the exercises in order, building complexity as you progress.

## Exercise 1: Basic Skip/Top Pagination

### Objective
Implement basic pagination using skip and top parameters.

### Tasks
1. **Simple Pagination**
   ```http
   # Get first page (items 1-10)
   GET /indexes/hotels/docs?search=*&$top=10&$skip=0
   
   # Get second page (items 11-20)  
   GET /indexes/hotels/docs?search=*&$top=10&$skip=10
   
   # Get third page (items 21-30)
   GET /indexes/hotels/docs?search=*&$top=10&$skip=20
   ```

2. **Add Result Counting**
   ```http
   GET /indexes/hotels/docs?search=*&$top=10&$skip=0&$count=true
   ```

3. **Implement Page Navigation Logic**
   - Calculate total pages from result count
   - Generate page numbers
   - Handle edge cases (first/last page)

### Expected Results
- Consistent page sizes across requests
- Proper total count calculation
- Working next/previous navigation

### Code Implementation
See [Code Samples](code-samples/README.md) for language-specific implementations.

## Exercise 2: Field Selection and Result Shaping

### Objective
Control which fields are returned to optimize response size and performance.

### Tasks
1. **Basic Field Selection**
   ```http
   # Return only essential fields for list view
   GET /indexes/hotels/docs?search=*&$select=hotelId,hotelName,rating&$top=10
   ```

2. **Different Views for Different Contexts**
   ```http
   # List view - minimal fields
   GET /indexes/hotels/docs?search=*&$select=hotelId,hotelName,rating,thumbnailUrl&$top=20
   
   # Detail view - comprehensive fields
   GET /indexes/hotels/docs/hotel123?$select=hotelName,description,amenities,location,images
   ```

3. **Performance Comparison**
   - Measure response times with/without field selection
   - Compare payload sizes
   - Document performance improvements

### Expected Results
- Reduced response payload sizes
- Faster response times
- Appropriate field selection for different use cases

## Exercise 3: Hit Highlighting

### Objective
Implement hit highlighting to emphasize search terms in results.

### Tasks
1. **Basic Highlighting**
   ```http
   GET /indexes/hotels/docs?search=luxury&highlight=description&$top=10
   ```

2. **Multiple Field Highlighting**
   ```http
   GET /indexes/hotels/docs?search=spa resort&highlight=description,amenities&$top=10
   ```

3. **Custom Highlighting Tags**
   ```http
   GET /indexes/hotels/docs?search=luxury&highlight=description&highlightPreTag=<mark>&highlightPostTag=</mark>&$top=10
   ```

4. **Process Highlighting Results**
   - Extract highlighted snippets
   - Display highlighted terms in UI
   - Handle multiple highlights per field

### Expected Results
- Search terms highlighted in results
- Custom highlighting tags applied
- Proper handling of multiple highlights

## Exercise 4: Range-Based Pagination

### Objective
Implement efficient pagination for large datasets using range filters.

### Tasks
1. **Setup Sortable Field**
   ```http
   # Ensure your index has a sortable unique field (e.g., hotelId)
   GET /indexes/hotels/docs?search=*&$orderby=hotelId&$top=10
   ```

2. **Implement Range-Based Navigation**
   ```http
   # First page
   GET /indexes/hotels/docs?search=*&$orderby=hotelId&$top=10
   
   # Next page (using last ID from previous page)
   GET /indexes/hotels/docs?search=*&$filter=hotelId gt 'hotel_010'&$orderby=hotelId&$top=10
   ```

3. **Handle Edge Cases**
   - Empty result sets
   - Last page detection
   - Concurrent data changes

### Expected Results
- Consistent performance regardless of page depth
- Proper handling of data changes during pagination
- Efficient navigation through large result sets

## Exercise 5: Search After Pattern

### Objective
Implement the search after pattern for optimal deep pagination performance.

### Tasks
1. **Compound Sorting Setup**
   ```http
   # Sort by score and unique field
   GET /indexes/hotels/docs?search=luxury&$orderby=search.score() desc,hotelId&$top=10
   ```

2. **Implement Search After**
   ```http
   # First page
   GET /indexes/hotels/docs?search=luxury&$orderby=search.score() desc,hotelId&$top=10
   
   # Next page using search after values
   GET /indexes/hotels/docs?search=luxury&$orderby=search.score() desc,hotelId&searchAfter=0.85,hotel_123&$top=10
   ```

3. **Client-Side Logic**
   - Extract sort values from results
   - Build search after parameters
   - Handle navigation state

### Expected Results
- Optimal performance for deep pagination
- Consistent results during concurrent updates
- Proper search after value extraction

## Exercise 6: Advanced Result Shaping

### Objective
Combine multiple result shaping techniques for optimal user experience.

### Tasks
1. **Comprehensive Search Interface**
   ```http
   GET /indexes/hotels/docs?search=luxury spa&$select=hotelId,hotelName,rating,description&highlight=description&$count=true&$top=15&$skip=0
   ```

2. **Faceted Search with Pagination**
   ```http
   GET /indexes/hotels/docs?search=*&facet=category&facet=rating&$select=hotelId,hotelName,category,rating&$top=20&$skip=0
   ```

3. **Search Suggestions with Highlighting**
   ```http
   GET /indexes/hotels/docs/suggest?search=lux&suggesterName=sg&highlight=hotelName&$top=5
   ```

### Expected Results
- Rich search interface with multiple features
- Proper integration of pagination with faceting
- Enhanced user experience with highlighting

## Exercise 7: Performance Optimization

### Objective
Optimize pagination and result shaping for production scenarios.

### Tasks
1. **Performance Benchmarking**
   - Measure response times for different page sizes
   - Compare skip/top vs range-based pagination
   - Test with large result sets (10,000+ documents)

2. **Caching Implementation**
   - Implement result caching
   - Cache pagination metadata
   - Handle cache invalidation

3. **Memory Management**
   - Set maximum page sizes
   - Implement timeout handling
   - Monitor resource usage

### Expected Results
- Documented performance characteristics
- Effective caching strategy
- Production-ready pagination implementation

## Exercise 8: Error Handling and Edge Cases

### Objective
Build robust pagination with proper error handling.

### Tasks
1. **Parameter Validation**
   ```javascript
   function validatePaginationParams(skip, top) {
       if (skip < 0) throw new Error('Skip cannot be negative');
       if (top < 1 || top > 1000) throw new Error('Top must be between 1 and 1000');
       if (skip + top > 100000) throw new Error('Cannot access results beyond 100,000');
   }
   ```

2. **Error Recovery**
   - Handle rate limiting (429 errors)
   - Retry with exponential backoff
   - Graceful degradation for service issues

3. **Edge Case Handling**
   - Empty result sets
   - Invalid pagination parameters
   - Concurrent data modifications

### Expected Results
- Robust error handling
- Graceful degradation
- Proper user feedback for errors

## Exercise 9: User Interface Integration

### Objective
Build a complete paginated search interface.

### Tasks
1. **Pagination Controls**
   - Previous/Next buttons
   - Page number navigation
   - Jump to page functionality

2. **Loading States**
   - Show loading indicators
   - Disable controls during requests
   - Progressive loading for infinite scroll

3. **Accessibility Features**
   - Keyboard navigation
   - Screen reader support
   - Semantic HTML markup

### Expected Results
- Complete, accessible pagination UI
- Smooth user experience
- Proper loading state management

## Exercise 10: Production Deployment

### Objective
Deploy pagination solution with monitoring and optimization.

### Tasks
1. **Performance Monitoring**
   - Track pagination performance metrics
   - Monitor error rates
   - Set up alerting for issues

2. **A/B Testing**
   - Test different page sizes
   - Compare pagination strategies
   - Measure user engagement

3. **Optimization**
   - Implement based on usage patterns
   - Optimize for common scenarios
   - Scale for production load

### Expected Results
- Production-ready pagination system
- Performance monitoring in place
- Data-driven optimization strategy

## Validation Checklist

After completing the exercises, verify you can:

- [ ] Implement basic skip/top pagination
- [ ] Use field selection to optimize responses
- [ ] Add hit highlighting to search results
- [ ] Implement range-based pagination for large datasets
- [ ] Use search after pattern for deep pagination
- [ ] Combine multiple result shaping techniques
- [ ] Handle errors and edge cases gracefully
- [ ] Build accessible pagination interfaces
- [ ] Monitor and optimize pagination performance
- [ ] Deploy pagination solutions to production

## Next Steps

After completing these exercises:
1. Review [Troubleshooting](troubleshooting.md) for common issues
2. Explore [Code Samples](code-samples/README.md) for implementation details
3. Move to Module 8: Search Explorer & Portal Tools
4. Consider advanced pagination patterns in intermediate modules

## Additional Challenges

For advanced learners:
- Implement cursor-based pagination for real-time data
- Build infinite scroll with virtual scrolling
- Create pagination with URL state management
- Implement server-side pagination caching
- Build pagination analytics and optimization