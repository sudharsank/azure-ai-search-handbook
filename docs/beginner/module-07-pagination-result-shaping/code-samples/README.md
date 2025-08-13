# Code Samples - Module 7: Pagination & Result Shaping

## Overview

This directory contains comprehensive code samples demonstrating how to implement pagination and result shaping in Azure AI Search. The examples cover various pagination strategies, result customization techniques, and performance optimization approaches across multiple programming languages.

## Sample Categories

### 1. Basic Pagination
- Skip/top pagination implementation
- Page size optimization
- Navigation controls
- User experience patterns

### 2. Skip & Top
- Traditional offset-based pagination
- Performance considerations
- Deep pagination challenges
- Best practices and limitations

### 3. Range Pagination
- Filter-based pagination for large datasets
- Cursor-based navigation
- Performance optimization
- Consistency handling

### 4. Field Selection
- Controlling returned fields with `$select`
- Payload optimization
- Security considerations
- Dynamic field selection

### 5. Result Counting
- Total result count implementation
- Performance impact analysis
- Conditional counting strategies
- User interface integration

### 6. Hit Highlighting
- Search term highlighting
- Custom highlighting tags
- Multi-field highlighting
- Performance optimization

### 7. Search Scores
- Relevance score inclusion
- Score interpretation
- Custom scoring scenarios
- Debugging relevance

### 8. Large Result Sets
- Efficient handling of large datasets
- Memory management
- Streaming approaches
- Performance monitoring

## Programming Languages

Each sample category is implemented in multiple programming languages:

- **Python** - Using azure-search-documents SDK
- **C#** - Using Azure.Search.Documents SDK
- **JavaScript/Node.js** - Using @azure/search-documents SDK
- **REST API** - Direct HTTP calls with examples

## Sample Structure

Each programming language directory contains:

```
language/
├── README.md                    # Language-specific setup and overview
├── 01_basic_pagination.*       # Basic pagination implementations
├── 02_skip_top.*              # Skip/top pagination examples
├── 03_range_pagination.*       # Range-based pagination
├── 04_field_selection.*        # Field selection techniques
├── 05_result_counting.*        # Result counting strategies
├── 06_hit_highlighting.*       # Hit highlighting implementations
├── 07_search_scores.*          # Search score handling
└── 08_large_result_sets.*      # Large dataset optimization
```

## Prerequisites

Before running these samples, ensure you have:

### Azure Resources
- Azure AI Search service
- Search index with sample data
- Appropriate permissions configured

### Development Environment
- Programming language runtime
- Required SDKs and packages installed
- Code editor or IDE
- REST client (for REST API examples)

### Sample Data
Your index should contain sufficient data to demonstrate pagination:
- At least 100+ documents for meaningful pagination
- Varied content for highlighting examples
- Different field types for selection examples

## Quick Start

### 1. Choose Your Language
Navigate to the appropriate language directory:
- [Python Examples](./python/README.md)
- [C# Examples](./csharp/README.md)
- [JavaScript Examples](./javascript/README.md)
- [REST API Examples](./rest/README.md)

### 2. Set Up Environment
Follow the language-specific setup instructions in each directory's README.

### 3. Configure Connections
Update configuration files with your Azure AI Search service details.

### 4. Run Samples
Start with basic pagination and progress to advanced techniques.

## Sample Scenarios

### Scenario 1: E-commerce Product Listing
**Files:** `01_basic_pagination.*`, `04_field_selection.*`, `05_result_counting.*`

Implement product catalog pagination:
- Display products with pagination controls
- Show total product count
- Optimize payload with field selection
- Handle category filtering with pagination

### Scenario 2: Search Results Interface
**Files:** `06_hit_highlighting.*`, `07_search_scores.*`, `02_skip_top.*`

Build search results page:
- Highlight search terms in results
- Display relevance scores
- Implement page navigation
- Handle empty result sets

### Scenario 3: Large Dataset Navigation
**Files:** `03_range_pagination.*`, `08_large_result_sets.*`

Handle large datasets efficiently:
- Use range-based pagination
- Optimize for performance
- Handle concurrent data changes
- Implement infinite scroll

## Pagination Techniques

### Skip/Top Pagination
```http
GET /indexes/products/docs?search=*&$skip=20&$top=10
```
- Simple to implement
- Good for small to medium datasets
- Performance degrades with large skip values

### Range-Based Pagination
```http
GET /indexes/products/docs?search=*&$filter=id gt 'product_100'&$orderby=id&$top=10
```
- Better performance for large datasets
- Consistent performance regardless of page depth
- Requires sortable unique field

### Search After Pattern
```http
GET /indexes/products/docs?search=query&$orderby=score desc,id&searchAfter=0.85,product_123&$top=10
```
- Optimal for deep pagination
- Handles concurrent changes well
- Requires compound sorting

## Result Shaping Parameters

### Field Selection
```http
GET /indexes/products/docs?search=*&$select=id,name,price,rating
```
- Reduces response payload
- Improves performance
- Controls data exposure

### Result Counting
```http
GET /indexes/products/docs?search=*&$count=true&$top=10
```
- Returns total result count
- Useful for pagination UI
- May impact performance

### Hit Highlighting
```http
GET /indexes/products/docs?search=wireless&highlight=name,description
```
- Emphasizes search terms
- Improves user experience
- Configurable highlighting tags

## Configuration Templates

### Environment Variables
```bash
# Azure AI Search
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
INDEX_NAME=your-index-name

# Pagination Settings
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Pagination Configuration
```json
{
  "pagination": {
    "defaultPageSize": 20,
    "maxPageSize": 100,
    "enableCounting": true,
    "enableHighlighting": true,
    "highlightPreTag": "<mark>",
    "highlightPostTag": "</mark>"
  }
}
```

## Best Practices Demonstrated

### Performance Optimization
- Appropriate page sizes
- Efficient pagination strategies
- Field selection optimization
- Result caching techniques

### User Experience
- Intuitive navigation controls
- Loading states and feedback
- Empty state handling
- Responsive design considerations

### Accessibility
- Keyboard navigation support
- Screen reader compatibility
- Semantic HTML usage
- Skip links for large result sets

## Testing and Validation

### Unit Tests
Each language directory includes tests for:
- Pagination logic validation
- Parameter handling
- Error condition testing
- Performance benchmarking

### Integration Tests
End-to-end tests covering:
- Complete pagination workflows
- User interaction scenarios
- Performance validation
- Cross-browser compatibility

### Performance Tests
Benchmarking for:
- Different page sizes
- Various pagination strategies
- Large dataset handling
- Memory usage patterns

## Performance Considerations

### Pagination Strategy Selection
- Use skip/top for small datasets (< 10,000 results)
- Use range-based pagination for large datasets
- Consider search-after for deep pagination
- Implement caching for frequently accessed pages

### Result Set Optimization
- Select only necessary fields
- Use appropriate page sizes (10-50 typically)
- Implement result caching
- Monitor query performance

### Memory Management
- Limit maximum page sizes
- Implement timeout handling
- Use streaming for large responses
- Monitor resource utilization

## Common Patterns

### Infinite Scroll Implementation
```javascript
async function loadMoreResults(lastId) {
    const results = await searchClient.search('*', {
        filter: `id gt '${lastId}'`,
        orderBy: ['id'],
        top: 20,
        select: ['id', 'title', 'summary']
    });
    return results;
}
```

### Pagination with Facets
```http
GET /indexes/products/docs?search=*&facet=category&facet=brand&$skip=0&$top=20&$count=true
```

### Search Result Preview
```http
GET /indexes/documents/docs?search=query&$select=title,summary&highlight=content&$top=10
```

## Troubleshooting

### Common Issues
- Deep pagination performance problems
- Memory issues with large result sets
- Inconsistent results during concurrent updates
- Highlighting performance impact

### Debugging Tools
- Query performance analysis
- Memory usage monitoring
- Result consistency validation
- User experience testing

### Performance Monitoring
- Query execution time tracking
- Memory usage analysis
- User interaction metrics
- Error rate monitoring

## Interactive Notebooks

The [notebooks](./notebooks/README.md) directory contains Jupyter notebooks with:
- Interactive pagination examples
- Performance comparison studies
- Visual result analysis
- Experimentation environments

## Additional Resources

- [Search Documents API Reference](https://docs.microsoft.com/rest/api/searchservice/search-documents)
- [Pagination Best Practices](https://docs.microsoft.com/azure/search/search-pagination-page-layout)
- [Hit Highlighting Guide](https://docs.microsoft.com/azure/search/search-pagination-page-layout#hit-highlighting)
- [Performance Optimization](https://docs.microsoft.com/azure/search/search-performance-optimization)

## Next Steps

After exploring these samples:
1. Implement pagination in your applications
2. Optimize for your specific use cases
3. Explore advanced features in intermediate modules
4. Share your experiences with the community

## Feedback and Support

For questions, issues, or suggestions:
- Review the troubleshooting guides
- Check the Azure AI Search documentation
- Engage with the community forums
- Submit feedback through appropriate channels