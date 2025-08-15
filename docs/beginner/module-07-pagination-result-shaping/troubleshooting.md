# Troubleshooting - Module 7: Pagination & Result Shaping

## Common Pagination Issues

### Issue 1: Poor Performance with Large Skip Values

**Symptoms:**
- Slow response times when accessing later pages
- Timeouts on deep pagination requests
- Increasing latency as page number increases

**Causes:**
- Using skip/top pagination with large skip values
- Azure AI Search must process all skipped results internally

**Solutions:**
```http
# Problem: Deep pagination with skip
GET /indexes/hotels/docs?search=*&$skip=50000&$top=20

# Solution 1: Range-based pagination
GET /indexes/hotels/docs?search=*&$filter=hotelId gt 'last_seen_id'&$orderby=hotelId&$top=20

# Solution 2: Search after pattern
GET /indexes/hotels/docs?search=*&$orderby=rating desc,hotelId&searchAfter=4.5,hotel_123&$top=20
```

**Prevention:**
- Limit maximum skip values (< 10,000)
- Use range-based pagination for large datasets
- Implement search after pattern for deep pagination

### Issue 2: Inconsistent Results During Pagination

**Symptoms:**
- Documents appearing on multiple pages
- Missing documents between pages
- Different total counts on subsequent requests

**Causes:**
- Concurrent index updates during pagination
- Using skip/top without stable sorting

**Solutions:**
```http
# Problem: Unstable pagination
GET /indexes/hotels/docs?search=*&$skip=20&$top=10

# Solution: Add stable sorting
GET /indexes/hotels/docs?search=*&$orderby=hotelId&$skip=20&$top=10

# Better: Use range-based pagination
GET /indexes/hotels/docs?search=*&$filter=hotelId gt 'hotel_020'&$orderby=hotelId&$top=10
```

**Prevention:**
- Always include stable sorting fields
- Use range-based pagination for consistency
- Consider timestamp-based filtering for real-time data

### Issue 3: Pagination Parameters Not Working

**Symptoms:**
- Skip parameter ignored
- Top parameter not limiting results
- Unexpected result counts

**Causes:**
- Incorrect parameter syntax
- Parameter value limits exceeded
- URL encoding issues

**Solutions:**
```http
# Problem: Incorrect syntax
GET /indexes/hotels/docs?search=*&skip=10&top=20

# Solution: Use $ prefix
GET /indexes/hotels/docs?search=*&$skip=10&$top=20

# Problem: Exceeding limits
GET /indexes/hotels/docs?search=*&$top=10000

# Solution: Respect limits
GET /indexes/hotels/docs?search=*&$top=1000
```

**Validation:**
```javascript
function validatePaginationParams(skip, top) {
    if (skip < 0) {
        throw new Error('Skip must be non-negative');
    }
    if (top < 1 || top > 1000) {
        throw new Error('Top must be between 1 and 1000');
    }
    if (skip + top > 100000) {
        throw new Error('Cannot retrieve results beyond position 100,000');
    }
}
```

## Result Shaping Issues

### Issue 4: Field Selection Not Working

**Symptoms:**
- All fields returned despite $select parameter
- Specific fields missing from results
- Unexpected field names in response

**Causes:**
- Incorrect field names in $select
- Case sensitivity issues
- Non-retrievable fields specified

**Solutions:**
```http
# Problem: Incorrect field names
GET /indexes/hotels/docs?search=*&$select=HotelName,Rating

# Solution: Use exact field names (case-sensitive)
GET /indexes/hotels/docs?search=*&$select=hotelName,rating

# Problem: Non-retrievable field
GET /indexes/hotels/docs?search=*&$select=hotelName,searchableField

# Solution: Check field configuration
GET /indexes/hotels
```

**Debugging:**
```javascript
// Check index schema for field names and retrievability
async function validateFieldSelection(fields) {
    const index = await searchClient.getIndex('hotels');
    const retrievableFields = index.fields
        .filter(f => f.retrievable !== false)
        .map(f => f.name);
    
    const invalidFields = fields.filter(f => !retrievableFields.includes(f));
    if (invalidFields.length > 0) {
        throw new Error(`Non-retrievable fields: ${invalidFields.join(', ')}`);
    }
}
```

### Issue 5: Hit Highlighting Not Appearing

**Symptoms:**
- No highlighting in search results
- Highlighting tags not applied
- Partial highlighting only

**Causes:**
- Fields not configured as searchable
- Incorrect highlight parameter syntax
- Search terms not found in highlighted fields

**Solutions:**
```http
# Problem: Non-searchable field
GET /indexes/hotels/docs?search=luxury&highlight=rating

# Solution: Use searchable fields only
GET /indexes/hotels/docs?search=luxury&highlight=description,amenities

# Problem: No search terms
GET /indexes/hotels/docs?search=*&highlight=description

# Solution: Use actual search query
GET /indexes/hotels/docs?search=luxury spa&highlight=description,amenities
```

**Field Validation:**
```javascript
async function validateHighlightFields(fields) {
    const index = await searchClient.getIndex('hotels');
    const searchableFields = index.fields
        .filter(f => f.searchable === true)
        .map(f => f.name);
    
    const invalidFields = fields.filter(f => !searchableFields.includes(f));
    if (invalidFields.length > 0) {
        console.warn(`Non-searchable fields for highlighting: ${invalidFields.join(', ')}`);
    }
}
```

### Issue 6: Result Count Performance Issues

**Symptoms:**
- Slow response times when using $count=true
- Timeouts on large result sets
- Inconsistent count values

**Causes:**
- Expensive count operations on large indexes
- Complex queries requiring full result set evaluation
- Concurrent index updates affecting counts

**Solutions:**
```http
# Problem: Always requesting count
GET /indexes/hotels/docs?search=*&$count=true&$top=20

# Solution: Request count only when needed
GET /indexes/hotels/docs?search=*&$top=20

# For UI that needs approximate counts
GET /indexes/hotels/docs?search=*&$top=20
# Show "20+ results" instead of exact count
```

**Conditional Counting:**
```javascript
async function searchWithOptionalCount(query, options, needsCount = false) {
    const searchOptions = {
        ...options,
        includeTotalCount: needsCount
    };
    
    const results = await searchClient.search(query, searchOptions);
    
    if (!needsCount && results.results.length === options.top) {
        // Estimate: "20+ results"
        results.estimatedCount = `${options.top}+`;
    }
    
    return results;
}
```

## Performance Issues

### Issue 7: Large Response Payloads

**Symptoms:**
- Slow network transfer times
- High bandwidth usage
- Client-side memory issues

**Causes:**
- Returning unnecessary fields
- Large page sizes
- Including binary data in results

**Solutions:**
```http
# Problem: All fields returned
GET /indexes/hotels/docs?search=*&$top=50

# Solution: Select only needed fields
GET /indexes/hotels/docs?search=*&$select=hotelId,hotelName,rating&$top=50

# Problem: Large binary fields
GET /indexes/hotels/docs?search=*&$select=hotelName,imageData

# Solution: Exclude binary data, use URLs
GET /indexes/hotels/docs?search=*&$select=hotelName,imageUrl
```

**Response Size Monitoring:**
```javascript
class ResponseSizeMonitor {
    static monitor(response) {
        const size = JSON.stringify(response).length;
        if (size > 1024 * 1024) { // 1MB
            console.warn(`Large response size: ${(size / 1024 / 1024).toFixed(2)}MB`);
        }
        return response;
    }
}
```

### Issue 8: Memory Issues with Large Result Sets

**Symptoms:**
- Out of memory errors
- Application crashes during pagination
- Slow garbage collection

**Causes:**
- Accumulating results in memory
- Large page sizes
- Not releasing previous page data

**Solutions:**
```javascript
// Problem: Accumulating all results
class BadPaginator {
    constructor() {
        this.allResults = []; // Memory leak!
    }
    
    async loadPage(pageNum) {
        const results = await this.search(pageNum);
        this.allResults.push(...results); // Accumulating
        return results;
    }
}

// Solution: Process pages independently
class GoodPaginator {
    async loadPage(pageNum) {
        const results = await this.search(pageNum);
        return results; // No accumulation
    }
    
    async *streamResults() {
        let pageNum = 0;
        let hasMore = true;
        
        while (hasMore) {
            const results = await this.loadPage(pageNum);
            if (results.length === 0) {
                hasMore = false;
            } else {
                yield results;
                pageNum++;
            }
        }
    }
}
```

## Error Handling Issues

### Issue 9: Rate Limiting Errors (429)

**Symptoms:**
- HTTP 429 "Too Many Requests" errors
- Intermittent pagination failures
- Service unavailable responses

**Causes:**
- Exceeding search service limits
- Too many concurrent requests
- Rapid pagination requests

**Solutions:**
```javascript
class RateLimitHandler {
    constructor(maxRetries = 3) {
        this.maxRetries = maxRetries;
    }
    
    async searchWithRetry(query, options, retryCount = 0) {
        try {
            return await searchClient.search(query, options);
        } catch (error) {
            if (error.status === 429 && retryCount < this.maxRetries) {
                const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
                await this.delay(delay);
                return this.searchWithRetry(query, options, retryCount + 1);
            }
            throw error;
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### Issue 10: Invalid Parameter Errors (400)

**Symptoms:**
- HTTP 400 "Bad Request" errors
- "Invalid parameter" error messages
- Pagination requests failing

**Causes:**
- Invalid skip/top values
- Malformed filter expressions
- Incorrect field names

**Solutions:**
```javascript
class ParameterValidator {
    static validatePagination(skip, top) {
        const errors = [];
        
        if (typeof skip !== 'number' || skip < 0) {
            errors.push('Skip must be a non-negative number');
        }
        
        if (typeof top !== 'number' || top < 1 || top > 1000) {
            errors.push('Top must be a number between 1 and 1000');
        }
        
        if (skip + top > 100000) {
            errors.push('Cannot retrieve results beyond position 100,000');
        }
        
        if (errors.length > 0) {
            throw new Error(`Validation errors: ${errors.join(', ')}`);
        }
    }
    
    static validateSelect(fields, indexSchema) {
        const retrievableFields = indexSchema.fields
            .filter(f => f.retrievable !== false)
            .map(f => f.name);
        
        const invalidFields = fields.filter(f => !retrievableFields.includes(f));
        if (invalidFields.length > 0) {
            throw new Error(`Invalid fields for selection: ${invalidFields.join(', ')}`);
        }
    }
}
```

## Debugging Tools and Techniques

### Debug Logging
```javascript
class PaginationDebugger {
    static logRequest(query, options) {
        console.log('Search Request:', {
            query,
            skip: options.skip,
            top: options.top,
            select: options.select,
            timestamp: new Date().toISOString()
        });
    }
    
    static logResponse(response, duration) {
        console.log('Search Response:', {
            resultCount: response.results.length,
            totalCount: response.count,
            duration: `${duration}ms`,
            timestamp: new Date().toISOString()
        });
    }
}
```

### Performance Monitoring
```javascript
class PerformanceMonitor {
    static async measurePagination(searchFn, pages = 10) {
        const results = [];
        
        for (let i = 0; i < pages; i++) {
            const start = Date.now();
            const response = await searchFn(i);
            const duration = Date.now() - start;
            
            results.push({
                page: i,
                duration,
                resultCount: response.results.length
            });
        }
        
        return {
            averageDuration: results.reduce((sum, r) => sum + r.duration, 0) / results.length,
            maxDuration: Math.max(...results.map(r => r.duration)),
            minDuration: Math.min(...results.map(r => r.duration)),
            results
        };
    }
}
```

### Health Checks
```javascript
class PaginationHealthCheck {
    static async checkPaginationHealth(searchClient) {
        const checks = [];
        
        // Test basic pagination
        try {
            await searchClient.search('*', { top: 10, skip: 0 });
            checks.push({ test: 'basic_pagination', status: 'pass' });
        } catch (error) {
            checks.push({ test: 'basic_pagination', status: 'fail', error: error.message });
        }
        
        // Test field selection
        try {
            await searchClient.search('*', { select: ['hotelId'], top: 1 });
            checks.push({ test: 'field_selection', status: 'pass' });
        } catch (error) {
            checks.push({ test: 'field_selection', status: 'fail', error: error.message });
        }
        
        // Test highlighting
        try {
            await searchClient.search('test', { highlightFields: ['description'], top: 1 });
            checks.push({ test: 'highlighting', status: 'pass' });
        } catch (error) {
            checks.push({ test: 'highlighting', status: 'fail', error: error.message });
        }
        
        return checks;
    }
}
```

## Quick Reference

### Common Error Codes
- **400**: Invalid parameters (check skip, top, select, highlight values)
- **429**: Rate limiting (implement retry with backoff)
- **500**: Service error (check service health, retry)
- **503**: Service unavailable (temporary issue, retry later)

### Parameter Limits
- **$top**: 1-1000 (default: 50)
- **$skip**: 0-100000 (performance degrades with large values)
- **$select**: Field names must be retrievable
- **highlight**: Field names must be searchable

### Performance Guidelines
- Page size: 10-50 for UI, up to 1000 for APIs
- Skip limit: < 10,000 for good performance
- Field selection: Always use for production
- Caching: Implement for frequently accessed pages

## Next Steps

After resolving issues:
1. Review [Best Practices](best-practices.md) for prevention strategies
2. Implement monitoring and alerting
3. Test with production-like data volumes
4. Document common issues for your team
5. Move to Module 8: Search Explorer & Portal Tools