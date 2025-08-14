# JavaScript Examples - Filters & Sorting

## Overview

This directory contains JavaScript/Node.js examples for implementing filters and sorting in Azure AI Search using the `@azure/search-documents` SDK. The examples demonstrate various filtering techniques, sorting strategies, and performance optimization approaches.

## Prerequisites

### Node.js Environment
- Node.js 14 or higher
- npm package manager

### Required Packages
```bash
npm install @azure/search-documents
npm install @azure/identity
npm install dotenv
```

### Azure Resources
- Azure AI Search service
- Search index with filterable and sortable fields
- Sample data for testing

## Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create a `.env` file with your Azure credentials:
```bash
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-admin-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
INDEX_NAME=your-index-name
```

### 3. Verify Setup
Run the setup verification script:
```bash
node verify_setup.js
```

## Examples

### 01 - Basic Filters
**File:** `01_basic_filters.js`

Demonstrates:
- Equality filters (`eq`, `ne`)
- Comparison filters (`gt`, `ge`, `lt`, `le`)
- Boolean logic combinations (`and`, `or`, `not`)
- Null value handling

### 02 - Range Filters
**File:** `02_range_filters.js`

Demonstrates:
- Numeric range filtering
- Date range filtering
- Price range implementations
- Performance optimization techniques

### 03 - String Filters
**File:** `03_string_filters.js`

Demonstrates:
- Text matching with `startswith`, `endswith`, `contains`
- Case sensitivity handling
- Pattern matching techniques
- Multi-language considerations

### 04 - Date Filters
**File:** `04_date_filters.js`

Demonstrates:
- Date range filtering
- Relative date calculations
- Time zone handling
- Date format considerations

### 05 - Geographic Filters
**File:** `05_geographic_filters.js`

Demonstrates:
- Distance-based filtering
- Bounding box filtering
- Location proximity searches
- Geographic sorting by distance

### 06 - Sorting Operations
**File:** `06_sorting_operations.js`

Demonstrates:
- Single field sorting
- Multi-field sorting
- Custom sort orders
- Performance optimization

### 07 - Complex Filters
**File:** `07_complex_filters.js`

Demonstrates:
- Collection filtering with `any()` and `all()`
- Nested field filtering
- Combined filter and search queries
- Advanced logical expressions

### 08 - Performance Tips
**File:** `08_performance_tips.js`

Demonstrates:
- Filter optimization strategies
- Index design considerations
- Query performance monitoring
- Caching strategies

## Running Examples

### Individual Examples
```bash
node 01_basic_filters.js
node 02_range_filters.js
# ... etc
```

### All Examples
```bash
node run_all_examples.js
```

## Common Patterns

### Authentication
```javascript
const { SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');

// Using API key
const credential = new AzureKeyCredential(apiKey);
const searchClient = new SearchClient(endpoint, indexName, credential);

// Using managed identity
const { DefaultAzureCredential } = require('@azure/identity');
const credential = new DefaultAzureCredential();
const searchClient = new SearchClient(endpoint, indexName, credential);
```

### Basic Filtering
```javascript
// Simple equality filter
const results = await searchClient.search("*", {
    filter: "category eq 'Electronics'"
});

// Range filter
const results = await searchClient.search("*", {
    filter: "price gt 100 and price lt 500"
});

// Combined filters
const results = await searchClient.search("*", {
    filter: "category eq 'Electronics' and rating ge 4.0"
});
```

### Sorting
```javascript
// Single field sorting
const results = await searchClient.search("*", {
    orderBy: ["rating desc"]
});

// Multi-field sorting
const results = await searchClient.search("*", {
    orderBy: ["category asc", "rating desc", "price asc"]
});
```

### Error Handling
```javascript
try {
    const results = await searchClient.search("*", {
        filter: "category eq 'Electronics'"
    });
    
    for await (const result of results.results) {
        console.log(`Found: ${result.document.name}`);
    }
} catch (error) {
    console.error(`Search failed: ${error.message}`);
}
```

## Configuration Management

### Using Environment Variables
```javascript
require('dotenv').config();

const config = {
    endpoint: process.env.SEARCH_ENDPOINT,
    apiKey: process.env.SEARCH_API_KEY,
    indexName: process.env.INDEX_NAME
};
```

### Configuration Class
```javascript
class SearchConfig {
    constructor() {
        this.endpoint = process.env.SEARCH_ENDPOINT;
        this.apiKey = process.env.SEARCH_API_KEY;
        this.indexName = process.env.INDEX_NAME;
    }
    
    validate() {
        const required = [this.endpoint, this.apiKey, this.indexName];
        if (!required.every(Boolean)) {
            throw new Error('Missing required configuration');
        }
    }
}
```

## Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### Performance Tests
```bash
npm run test:performance
```

## Debugging

### Enable Logging
```javascript
const { setLogLevel } = require('@azure/logger');
setLogLevel('info');
```

### Debug Mode
```javascript
// Set debug flag for detailed output
const DEBUG = process.env.NODE_ENV === 'development';

if (DEBUG) {
    console.log(`Filter: ${filterExpression}`);
    console.log(`Order by: ${orderBy}`);
}
```

## Best Practices

### Filter Construction
```javascript
function buildFilter(category, minPrice, maxPrice, inStock) {
    const filters = [];
    
    if (category) {
        filters.push(`category eq '${category}'`);
    }
    
    if (minPrice !== undefined) {
        filters.push(`price ge ${minPrice}`);
    }
    
    if (maxPrice !== undefined) {
        filters.push(`price le ${maxPrice}`);
    }
    
    if (inStock !== undefined) {
        filters.push(`inStock eq ${inStock}`);
    }
    
    return filters.length > 0 ? filters.join(' and ') : null;
}
```

### Result Processing
```javascript
async function processResults(results, maxResults = 10) {
    const processed = [];
    let count = 0;
    
    for await (const result of results.results) {
        if (count >= maxResults) break;
        
        processed.push({
            id: result.document.id,
            name: result.document.name,
            price: result.document.price,
            rating: result.document.rating
        });
        count++;
    }
    
    return processed;
}
```

### Performance Monitoring
```javascript
async function timedSearch(searchClient, searchOptions) {
    const startTime = Date.now();
    
    try {
        const results = await searchClient.search("*", searchOptions);
        const resultList = [];
        
        for await (const result of results.results) {
            resultList.push(result);
        }
        
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        return {
            results: resultList,
            duration: duration,
            count: resultList.length
        };
    } catch (error) {
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        return {
            error: error.message,
            duration: duration
        };
    }
}
```

## Troubleshooting

### Common Issues
1. **Field not filterable**: Ensure field has `filterable: true` in index schema
2. **Invalid filter syntax**: Check OData expression syntax
3. **Data type mismatches**: Ensure filter values match field types
4. **Performance issues**: Optimize filter expressions and index design

### Debug Tools
```javascript
function validateFilter(filterExpression) {
    try {
        if (!filterExpression) {
            return { valid: true, message: "Empty filter is valid" };
        }
        
        // Check for balanced quotes
        const singleQuotes = (filterExpression.match(/'/g) || []).length;
        if (singleQuotes % 2 !== 0) {
            return { valid: false, message: "Unbalanced single quotes" };
        }
        
        // Check for balanced parentheses
        const openParens = (filterExpression.match(/\(/g) || []).length;
        const closeParens = (filterExpression.match(/\)/g) || []).length;
        if (openParens !== closeParens) {
            return { valid: false, message: "Unbalanced parentheses" };
        }
        
        return { valid: true, message: "Filter appears valid" };
    } catch (error) {
        return { valid: false, message: `Validation error: ${error.message}` };
    }
}
```

## Additional Resources

- [Azure Search Documents SDK Documentation](https://docs.microsoft.com/javascript/api/@azure/search-documents/)
- [JavaScript SDK Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents/samples)
- [OData Filter Syntax Reference](https://docs.microsoft.com/azure/search/search-query-odata-filter)

## Next Steps

1. Run the basic examples to understand core concepts
2. Modify examples for your specific data and requirements
3. Implement filtering in your applications
4. Explore advanced features in intermediate modules