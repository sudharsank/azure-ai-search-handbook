# JavaScript Examples - Module 7: Pagination & Result Shaping

## Overview

This directory contains JavaScript/Node.js examples demonstrating pagination and result shaping techniques in Azure AI Search. These examples use the `@azure/search-documents` SDK and showcase various approaches to handling search results efficiently.

## Prerequisites

### Node.js Environment
- Node.js 14.x or later
- npm or yarn package manager

### Required Packages
```bash
npm install @azure/search-documents
npm install dotenv
```

### Azure AI Search Setup
- Active Azure AI Search service
- Search index with sample data (hotels-sample recommended)
- Valid API keys and service endpoint

## Configuration

Create a `.env` file in this directory:
```env
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_API_KEY=your-api-key
INDEX_NAME=hotels-sample
```

## Examples

### 1. Basic Pagination (`01_basic_pagination.js`)
- Skip/top pagination implementation
- Page navigation controls
- Error handling and edge cases
- Performance monitoring

**Key Features:**
- Traditional offset-based pagination
- Configurable page sizes
- Navigation state management
- User-friendly pagination controls

### 2. Field Selection (`02_field_selection.js`)
- Controlling returned fields with `$select`
- Payload optimization techniques
- Context-based field selection
- Performance comparison

**Key Features:**
- Dynamic field selection
- Payload size optimization
- Context-aware field sets
- Performance impact analysis

### 3. Hit Highlighting (`03_hit_highlighting.js`)
- Search term highlighting implementation
- Custom highlighting tags
- Multi-field highlighting
- Styling and presentation

**Key Features:**
- Configurable highlight tags
- Multiple field highlighting
- Custom styling options
- HTML-safe highlighting

### 4. Result Counting (`04_result_counting.js`)
- Total result count implementation
- Performance optimization strategies
- Conditional counting
- Caching mechanisms

**Key Features:**
- Smart counting strategies
- Performance optimization
- Caching implementation
- Context-aware counting

### 5. Range Pagination (`05_range_pagination.js`)
- Filter-based pagination for large datasets
- Cursor-based navigation
- Consistent performance
- Concurrent data handling

**Key Features:**
- Range-based filtering
- Consistent performance
- Large dataset handling
- Concurrent update handling

### 6. Advanced Range Pagination (`06_advanced_range_pagination.js`)
- Hybrid pagination strategies
- Performance optimization
- State management
- Advanced navigation patterns

**Key Features:**
- Hybrid pagination approaches
- Advanced state management
- Performance optimization
- Complex navigation scenarios

## Usage Patterns

### Basic Setup
```javascript
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

const client = new SearchClient(
    process.env.SEARCH_ENDPOINT,
    process.env.INDEX_NAME,
    new AzureKeyCredential(process.env.SEARCH_API_KEY)
);
```

### Skip/Top Pagination
```javascript
async function paginateResults(query, pageNumber, pageSize) {
    const skip = pageNumber * pageSize;
    
    const results = await client.search(query, {
        skip: skip,
        top: pageSize,
        includeTotalCount: true
    });
    
    return {
        documents: results.results,
        totalCount: results.count,
        hasMore: results.results.length === pageSize
    };
}
```

### Field Selection
```javascript
async function searchWithFields(query, fields) {
    const results = await client.search(query, {
        select: fields,
        top: 20
    });
    
    return results.results;
}
```

### Hit Highlighting
```javascript
async function searchWithHighlighting(query, highlightFields) {
    const results = await client.search(query, {
        highlightFields: highlightFields,
        highlightPreTag: '<mark>',
        highlightPostTag: '</mark>',
        top: 10
    });
    
    return results.results;
}
```

## Error Handling

### Common Error Patterns
```javascript
async function safeSearch(query, options) {
    try {
        const results = await client.search(query, options);
        return { success: true, data: results };
    } catch (error) {
        if (error.statusCode === 400) {
            return { success: false, error: 'Invalid query parameters' };
        } else if (error.statusCode === 429) {
            return { success: false, error: 'Rate limit exceeded' };
        } else {
            return { success: false, error: 'Search service error' };
        }
    }
}
```

### Retry Logic
```javascript
async function searchWithRetry(query, options, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await client.search(query, options);
        } catch (error) {
            if (attempt === maxRetries || error.statusCode !== 429) {
                throw error;
            }
            
            // Exponential backoff
            await new Promise(resolve => 
                setTimeout(resolve, Math.pow(2, attempt) * 1000)
            );
        }
    }
}
```

## Performance Optimization

### Caching Strategy
```javascript
const cache = new Map();

async function cachedSearch(query, options, ttl = 300000) {
    const cacheKey = JSON.stringify({ query, options });
    const cached = cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < ttl) {
        return cached.data;
    }
    
    const results = await client.search(query, options);
    cache.set(cacheKey, {
        data: results,
        timestamp: Date.now()
    });
    
    return results;
}
```

### Batch Processing
```javascript
async function processBatch(queries, batchSize = 5) {
    const results = [];
    
    for (let i = 0; i < queries.length; i += batchSize) {
        const batch = queries.slice(i, i + batchSize);
        const batchPromises = batch.map(query => client.search(query));
        
        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);
    }
    
    return results;
}
```

## Testing

### Unit Testing Example
```javascript
const { describe, it, expect } = require('@jest/globals');

describe('Pagination', () => {
    it('should handle basic pagination', async () => {
        const result = await paginateResults('hotel', 0, 10);
        
        expect(result.documents).toBeDefined();
        expect(result.documents.length).toBeLessThanOrEqual(10);
        expect(result.totalCount).toBeGreaterThan(0);
    });
    
    it('should handle empty results', async () => {
        const result = await paginateResults('nonexistentterm', 0, 10);
        
        expect(result.documents.length).toBe(0);
        expect(result.totalCount).toBe(0);
        expect(result.hasMore).toBe(false);
    });
});
```

## Best Practices

### Performance
- Use appropriate page sizes (10-50 for UI, 100+ for processing)
- Implement field selection to reduce payload size
- Cache expensive queries when appropriate
- Use range-based pagination for large datasets

### Error Handling
- Implement comprehensive error handling
- Use retry logic for transient failures
- Validate input parameters
- Handle rate limiting gracefully

### Security
- Validate and sanitize user input
- Use environment variables for sensitive configuration
- Implement proper authentication
- Follow least privilege principles

### User Experience
- Provide loading indicators
- Handle empty states gracefully
- Implement proper navigation controls
- Show meaningful error messages

## Integration Examples

### Express.js API
```javascript
const express = require('express');
const app = express();

app.get('/api/search', async (req, res) => {
    try {
        const { q, page = 0, size = 20 } = req.query;
        const result = await paginateResults(q, parseInt(page), parseInt(size));
        
        res.json({
            success: true,
            data: result.documents,
            pagination: {
                page: parseInt(page),
                size: parseInt(size),
                total: result.totalCount,
                hasMore: result.hasMore
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});
```

### React Integration
```javascript
import { useState, useEffect } from 'react';

function useSearch(query, page, pageSize) {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        async function search() {
            setLoading(true);
            setError(null);
            
            try {
                const result = await paginateResults(query, page, pageSize);
                setResults(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }
        
        if (query) {
            search();
        }
    }, [query, page, pageSize]);
    
    return { results, loading, error };
}
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify endpoint URL and API key
   - Check network connectivity
   - Validate service availability

2. **Query Errors**
   - Validate query syntax
   - Check field names and types
   - Verify index schema

3. **Performance Issues**
   - Monitor query complexity
   - Optimize field selection
   - Implement appropriate caching

4. **Rate Limiting**
   - Implement retry logic
   - Use connection pooling
   - Monitor request rates

### Debug Mode
```javascript
const client = new SearchClient(
    process.env.SEARCH_ENDPOINT,
    process.env.INDEX_NAME,
    new AzureKeyCredential(process.env.SEARCH_API_KEY),
    {
        // Enable request/response logging
        loggingOptions: {
            enableUnsafeConsoleLogging: true
        }
    }
);
```

## Next Steps

1. Run the examples in order (01 through 06)
2. Experiment with different parameters and configurations
3. Integrate patterns into your applications
4. Explore the interactive notebooks for deeper learning
5. Review the troubleshooting guide for common issues

## Support

For additional help:
- Review the main module documentation
- Check the troubleshooting guides
- Explore the interactive notebooks
- Consult Azure AI Search documentation