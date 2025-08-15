# Best Practices - Module 7: Pagination & Result Shaping

## Pagination Best Practices

### Choose the Right Pagination Strategy

#### Skip/Top Pagination
**Best for**: Small to medium result sets (< 10,000 results)
```http
GET /indexes/hotels/docs?search=*&$skip=20&$top=10
```
- ✅ Simple to implement
- ✅ Works with any sorting
- ❌ Performance degrades with large skip values
- ❌ Inconsistent results during concurrent updates

#### Range-Based Pagination
**Best for**: Large datasets with stable sort fields
```http
GET /indexes/hotels/docs?search=*&$filter=hotelId gt 'hotel_100'&$orderby=hotelId&$top=10
```
- ✅ Consistent performance regardless of page depth
- ✅ Handles concurrent data changes well
- ❌ Requires unique, sortable field
- ❌ More complex to implement

#### Search After Pattern
**Best for**: Deep pagination scenarios
```http
GET /indexes/hotels/docs?search=*&$orderby=rating desc,hotelId&searchAfter=4.5,hotel_123&$top=10
```
- ✅ Optimal performance for deep pagination
- ✅ Consistent results during updates
- ❌ Requires compound sorting
- ❌ More complex client-side logic

### Page Size Guidelines

#### Recommended Page Sizes
- **Web interfaces**: 10-20 items
- **Mobile interfaces**: 5-15 items
- **API responses**: 20-50 items
- **Bulk operations**: 100-1000 items

#### Performance Considerations
```javascript
// Good: Reasonable page size
const results = await searchClient.search('*', {
    top: 20,
    skip: 0
});

// Avoid: Excessive page size
const results = await searchClient.search('*', {
    top: 10000  // Too large, impacts performance
});
```

### Deep Pagination Strategies

#### Avoid Deep Skip Values
```http
# Problematic: Deep pagination with skip
GET /indexes/hotels/docs?search=*&$skip=50000&$top=20

# Better: Use range-based pagination
GET /indexes/hotels/docs?search=*&$filter=id gt 'last_seen_id'&$top=20
```

#### Implement Progressive Loading
```javascript
// Infinite scroll pattern
class SearchPaginator {
    constructor(searchClient) {
        this.searchClient = searchClient;
        this.lastId = null;
        this.hasMore = true;
    }
    
    async loadNext(pageSize = 20) {
        if (!this.hasMore) return [];
        
        const filter = this.lastId ? `id gt '${this.lastId}'` : null;
        const results = await this.searchClient.search('*', {
            filter,
            orderBy: ['id'],
            top: pageSize
        });
        
        if (results.results.length < pageSize) {
            this.hasMore = false;
        }
        
        if (results.results.length > 0) {
            this.lastId = results.results[results.results.length - 1].document.id;
        }
        
        return results.results;
    }
}
```

## Result Shaping Best Practices

### Field Selection Optimization

#### Select Only Necessary Fields
```http
# Good: Select specific fields
GET /indexes/hotels/docs?search=*&$select=hotelName,rating,location

# Avoid: Returning all fields unnecessarily
GET /indexes/hotels/docs?search=*
```

#### Field Selection Strategies
```javascript
// List view: Minimal fields
const listResults = await searchClient.search('luxury', {
    select: ['hotelId', 'hotelName', 'rating', 'thumbnailUrl'],
    top: 20
});

// Detail view: Comprehensive fields
const detailResult = await searchClient.getDocument('hotel123', {
    select: ['hotelName', 'description', 'amenities', 'location', 'images']
});
```

### Result Counting Guidelines

#### Use Count Judiciously
```http
# Good: Count for small result sets
GET /indexes/hotels/docs?search=luxury&$count=true&$top=20

# Consider: Skip count for large result sets to improve performance
GET /indexes/hotels/docs?search=*&$top=20
```

#### Approximate Counting for Large Sets
```javascript
// For large datasets, consider approximate counting
const searchOptions = {
    top: 20,
    includeTotalCount: false,  // Skip exact count for performance
    queryType: 'simple'
};

// Show "1000+ results" instead of exact count
```

### Hit Highlighting Best Practices

#### Selective Highlighting
```http
# Good: Highlight specific searchable fields
GET /indexes/hotels/docs?search=luxury&highlight=description,amenities

# Avoid: Highlighting all fields
GET /indexes/hotels/docs?search=luxury&highlight=*
```

#### Highlighting Configuration
```javascript
const searchOptions = {
    searchText: 'luxury spa',
    highlightFields: ['description', 'amenities'],
    highlightPreTag: '<mark>',
    highlightPostTag: '</mark>',
    top: 10
};
```

## Performance Optimization

### Caching Strategies

#### Result Caching
```javascript
class CachedSearchClient {
    constructor(searchClient, cacheTimeout = 300000) { // 5 minutes
        this.searchClient = searchClient;
        this.cache = new Map();
        this.cacheTimeout = cacheTimeout;
    }
    
    async search(query, options) {
        const cacheKey = this.generateCacheKey(query, options);
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.results;
        }
        
        const results = await this.searchClient.search(query, options);
        this.cache.set(cacheKey, {
            results,
            timestamp: Date.now()
        });
        
        return results;
    }
}
```

#### Page Prefetching
```javascript
// Prefetch next page for better UX
async function loadPageWithPrefetch(pageNumber, pageSize) {
    const currentPagePromise = loadPage(pageNumber, pageSize);
    const nextPagePromise = loadPage(pageNumber + 1, pageSize);
    
    const currentPage = await currentPagePromise;
    
    // Prefetch next page in background
    nextPagePromise.catch(() => {}); // Ignore prefetch errors
    
    return currentPage;
}
```

### Memory Management

#### Limit Result Set Size
```javascript
const MAX_PAGE_SIZE = 100;
const MAX_TOTAL_RESULTS = 10000;

function validatePaginationParams(skip, top) {
    if (top > MAX_PAGE_SIZE) {
        throw new Error(`Page size cannot exceed ${MAX_PAGE_SIZE}`);
    }
    
    if (skip + top > MAX_TOTAL_RESULTS) {
        throw new Error(`Cannot retrieve results beyond ${MAX_TOTAL_RESULTS}`);
    }
}
```

#### Streaming for Large Responses
```javascript
// For large result sets, consider streaming
async function* streamSearchResults(query, batchSize = 100) {
    let skip = 0;
    let hasMore = true;
    
    while (hasMore) {
        const results = await searchClient.search(query, {
            skip,
            top: batchSize
        });
        
        if (results.results.length === 0) {
            hasMore = false;
        } else {
            yield results.results;
            skip += batchSize;
            
            if (results.results.length < batchSize) {
                hasMore = false;
            }
        }
    }
}
```

## User Experience Guidelines

### Loading States
```javascript
// Implement proper loading states
class SearchInterface {
    async loadPage(pageNumber) {
        this.showLoading();
        
        try {
            const results = await this.searchClient.search('*', {
                skip: pageNumber * this.pageSize,
                top: this.pageSize
            });
            
            this.displayResults(results);
        } catch (error) {
            this.showError(error);
        } finally {
            this.hideLoading();
        }
    }
}
```

### Error Handling
```javascript
// Graceful error handling for pagination
async function handlePaginationError(error, retryCount = 0) {
    const MAX_RETRIES = 3;
    
    if (error.status === 429 && retryCount < MAX_RETRIES) {
        // Rate limiting - exponential backoff
        const delay = Math.pow(2, retryCount) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        return retrySearch(retryCount + 1);
    }
    
    if (error.status === 400) {
        // Bad request - likely invalid pagination parameters
        return handleInvalidPagination();
    }
    
    throw error;
}
```

### Accessibility Considerations
```html
<!-- Semantic pagination markup -->
<nav aria-label="Search results pagination">
    <ul class="pagination">
        <li><a href="#" aria-label="Previous page">Previous</a></li>
        <li><a href="#" aria-current="page">1</a></li>
        <li><a href="#" aria-label="Page 2">2</a></li>
        <li><a href="#" aria-label="Next page">Next</a></li>
    </ul>
</nav>

<!-- Skip to results link -->
<a href="#search-results" class="skip-link">Skip to search results</a>
```

## Common Anti-Patterns to Avoid

### Performance Anti-Patterns
- Using large skip values for deep pagination
- Requesting all fields when only few are needed
- Not implementing result caching for repeated queries
- Using count=true for every query regardless of need

### User Experience Anti-Patterns
- Not providing loading indicators during pagination
- Inconsistent page sizes across the application
- Not handling empty result sets gracefully
- Missing error handling for pagination failures

### Implementation Anti-Patterns
- Hardcoding pagination parameters
- Not validating pagination inputs
- Ignoring concurrent data changes
- Not implementing proper timeout handling

## Next Steps

After implementing these best practices:
1. Test with [Practice & Implementation](practice-implementation.md) exercises
2. Explore [Code Samples](code-samples/README.md) for implementation examples
3. Use [Troubleshooting](troubleshooting.md) guide for common issues
4. Monitor performance and adjust strategies as needed