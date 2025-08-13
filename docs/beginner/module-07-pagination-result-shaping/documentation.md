# Module 7: Pagination & Result Shaping

## Overview

Pagination and result shaping are crucial for creating user-friendly search experiences. This module covers how to implement efficient pagination strategies, control result composition, and optimize the presentation of search results in Azure AI Search applications.

## Learning Objectives

By the end of this module, you will be able to:

- Implement various pagination techniques (skip/top, range-based)
- Control which fields are returned in search results
- Add result counting and metadata
- Implement hit highlighting for better user experience
- Handle large result sets efficiently
- Optimize pagination performance
- Troubleshoot common pagination issues

## Key Concepts

### Pagination
Pagination divides large result sets into manageable pages:
- **Skip/Top Pattern**: Traditional offset-based pagination
- **Range-Based Pagination**: Using filters for large datasets
- **Cursor-Based Pagination**: For real-time data scenarios
- **Search After Pattern**: For deep pagination scenarios

### Result Shaping
Control what information is returned:
- **Field Selection**: Choose specific fields to return
- **Result Counting**: Get total result counts
- **Hit Highlighting**: Emphasize search terms in results
- **Search Scores**: Include relevance scores
- **Metadata**: Add execution and diagnostic information

### Performance Considerations
- **Deep Pagination**: Challenges with large offsets
- **Result Set Size**: Impact on performance and costs
- **Field Selection**: Reducing payload size
- **Caching Strategies**: Improving response times

## Prerequisites

Before starting this module, ensure you have:
- Completed Module 1 (Introduction & Setup)
- Completed Module 2 (Basic Search)
- Completed Module 4 (Simple Queries)
- Understanding of search result structure
- Basic knowledge of REST API parameters

## Module Structure

This module is organized into the following sections:

1. **Prerequisites** - Required setup and knowledge
2. **Best Practices** - Guidelines for effective pagination and result shaping
3. **Practice & Implementation** - Hands-on exercises and examples
4. **Troubleshooting** - Common issues and solutions
5. **Code Samples** - Practical examples in multiple programming languages

## What You'll Build

Throughout this module, you'll create:
- Basic pagination implementations
- Advanced pagination strategies for large datasets
- Result shaping configurations
- Hit highlighting implementations
- Performance-optimized pagination solutions

## Pagination Techniques

### Skip/Top Pagination
```http
GET /indexes/hotels/docs?search=*&$skip=20&$top=10
```
- Simple to implement
- Works well for small to medium result sets
- Performance degrades with large skip values

### Range-Based Pagination
```http
GET /indexes/hotels/docs?search=*&$filter=id gt '50'&$orderby=id&$top=10
```
- Better performance for large datasets
- Requires sortable unique field
- Handles concurrent data changes better

### Search After Pattern
```http
GET /indexes/hotels/docs?search=*&$orderby=score desc,id&searchAfter=0.85,hotel123&$top=10
```
- Optimal for deep pagination
- Consistent performance regardless of page depth
- Requires compound sorting

## Result Shaping Parameters

### Field Selection
```http
GET /indexes/hotels/docs?search=*&$select=hotelName,rating,location
```
- Reduces response payload
- Improves performance
- Controls data exposure

### Result Counting
```http
GET /indexes/hotels/docs?search=*&$count=true
```
- Returns total result count
- Useful for pagination UI
- May impact performance for large result sets

### Hit Highlighting
```http
GET /indexes/hotels/docs?search=luxury&highlight=description,amenities
```
- Emphasizes search terms in results
- Improves user experience
- Configurable highlighting tags

## Performance Optimization

### Efficient Pagination
- Use appropriate page sizes (10-50 items typically)
- Avoid deep pagination with skip/top
- Consider range-based pagination for large datasets
- Implement caching for frequently accessed pages

### Result Set Optimization
- Select only necessary fields
- Use appropriate data types
- Consider result caching strategies
- Monitor query performance metrics

### Memory Management
- Limit maximum page sizes
- Implement timeout handling
- Use streaming for large responses
- Monitor resource utilization

## Common Patterns

### Infinite Scroll
```javascript
// Load more results as user scrolls
function loadMoreResults(lastId) {
    return searchClient.search('*', {
        filter: `id gt '${lastId}'`,
        orderBy: ['id'],
        top: 20,
        select: ['id', 'title', 'summary']
    });
}
```

### Faceted Navigation with Pagination
```http
GET /indexes/products/docs?search=*&facet=category&facet=brand&$skip=0&$top=20
```

### Search Result Preview
```http
GET /indexes/documents/docs?search=query&$select=title,summary&highlight=content&$top=10
```

## Best Practices

### User Experience
- Provide clear pagination controls
- Show total result counts when appropriate
- Implement loading states
- Handle empty result sets gracefully

### Performance
- Use appropriate page sizes
- Implement result caching
- Monitor pagination performance
- Optimize for common use cases

### Accessibility
- Ensure keyboard navigation
- Provide screen reader support
- Use semantic HTML elements
- Include skip links for large result sets

## Next Steps

After completing this module, you'll be ready to:
- Build sophisticated search interfaces with pagination
- Implement efficient result presentation
- Move on to Module 8: Search Explorer & Portal Tools
- Explore advanced search features in intermediate modules

## Additional Resources

- [Search Documents API Reference](https://docs.microsoft.com/rest/api/searchservice/search-documents)
- [Pagination Best Practices](https://docs.microsoft.com/azure/search/search-pagination-page-layout)
- [Hit Highlighting](https://docs.microsoft.com/azure/search/search-pagination-page-layout#hit-highlighting)