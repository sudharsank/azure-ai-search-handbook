# JavaScript Code Samples - Simple Queries and Filters

This directory contains JavaScript/Node.js implementations for learning simple queries and filters in Azure AI Search using the Azure SDK for JavaScript.

## 📋 Prerequisites

### Required Packages

Install the required npm packages:

```bash
npm install @azure/search-documents dotenv
```

Or using yarn:
```bash
yarn add @azure/search-documents dotenv
```

### Environment Setup

Create a `.env` file in your project root:

```env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=your-index-name
```

### Package.json Setup

Ensure your `package.json` includes:

```json
{
  "name": "azure-search-module4",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@azure/search-documents": "^12.0.0",
    "dotenv": "^16.0.0"
  },
  "scripts": {
    "basic-queries": "node 01_basic_queries.js",
    "filtering": "node 02_filtering.js",
    "sorting-pagination": "node 03_sorting_pagination.js",
    "result-customization": "node 04_result_customization.js",
    "advanced-queries": "node 05_advanced_queries.js",
    "error-handling": "node 06_error_handling.js"
  }
}
```

### Sample Data

These examples assume you have sample indexes created from previous modules with documents containing:

- `id` (string) - Unique identifier
- `title` (string) - Document title
- `content` (string) - Document content
- `category` (string) - Document category
- `tags` (string[]) - Document tags
- `rating` (number) - Document rating (0.0-5.0)
- `publishedDate` (string) - Publication date (ISO format)
- `price` (number) - Document price

## 🚀 Getting Started

### Basic Usage

```javascript
import { SearchClient, AzureKeyCredential } from '@azure/search-documents';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize the search client
const searchClient = new SearchClient(
    process.env.AZURE_SEARCH_SERVICE_ENDPOINT,
    process.env.AZURE_SEARCH_INDEX_NAME,
    new AzureKeyCredential(process.env.AZURE_SEARCH_API_KEY)
);

// Perform a simple search
const results = await searchClient.search('azure');
for await (const result of results.results) {
    console.log(`Title: ${result.document.title}`);
}
```

## 📚 Code Samples

### 1. Basic Queries (`01_basic_queries.js`)
Learn fundamental text search operations:
- Simple text search
- Field-specific search
- Query operators (+, -, "", *, ())
- Search modes and query types

**Key Concepts:**
- SearchClient initialization
- Search options configuration
- Result iteration with async generators
- Error handling with try-catch

### 2. Filtering (`02_filtering.js`)
Master OData filter expressions:
- Equality and comparison filters
- Logical operators (and, or, not)
- Collection filters (any, all)
- Date and numeric range filters

**Key Concepts:**
- OData filter syntax
- Type handling in JavaScript
- Complex filter expressions
- Performance optimization

### 3. Sorting and Pagination (`03_sorting_pagination.js`)
Implement result ordering and pagination:
- Single and multi-field sorting
- Ascending and descending order
- Page-based navigation
- Total count retrieval

**Key Concepts:**
- OrderBy expressions
- Skip and top parameters
- Pagination patterns
- Performance considerations

### 4. Result Customization (`04_result_customization.js`)
Customize search results:
- Field selection
- Search highlighting
- Result formatting
- Custom result processing

**Key Concepts:**
- Select parameter
- Highlight configuration
- Result metadata
- Custom formatting

### 5. Advanced Queries (`05_advanced_queries.js`)
Explore advanced query features:
- Field boosting
- Fuzzy search
- Wildcard patterns
- Regular expressions

**Key Concepts:**
- Query complexity
- Performance optimization
- Advanced syntax
- Use case scenarios

### 6. Error Handling (`06_error_handling.js`)
Implement robust error handling:
- Exception types and handling
- Query validation
- Retry logic
- Debugging techniques

**Key Concepts:**
- Azure SDK exceptions
- Error recovery
- Logging and debugging
- Production best practices

## 🔧 Running the Examples

### Individual Examples

Run each example individually:

```bash
# Basic queries
node 01_basic_queries.js

# Filtering
node 02_filtering.js

# Sorting and pagination
node 03_sorting_pagination.js

# Result customization
node 04_result_customization.js

# Advanced queries
node 05_advanced_queries.js

# Error handling
node 06_error_handling.js
```

### Using npm scripts

```bash
npm run basic-queries
npm run filtering
npm run sorting-pagination
npm run result-customization
npm run advanced-queries
npm run error-handling
```

### All Examples

Run all examples in sequence:

```bash
# Run all examples
for file in 0*.js; do
    echo "Running $file..."
    node "$file"
    echo "---"
done
```

## 🎯 Learning Outcomes

After completing these JavaScript examples, you will be able to:

- ✅ **Initialize Search Client**: Set up Azure AI Search client with proper authentication
- ✅ **Execute Basic Queries**: Perform text searches with various operators
- ✅ **Apply Filters**: Use OData expressions to filter results effectively
- ✅ **Implement Pagination**: Handle large result sets with proper pagination
- ✅ **Customize Results**: Select fields and highlight matching terms
- ✅ **Handle Errors**: Implement robust error handling and validation
- ✅ **Optimize Performance**: Write efficient queries for production use

## 🔍 Common Patterns

### Search Client Initialization

```javascript
import { SearchClient, AzureKeyCredential } from '@azure/search-documents';
import dotenv from 'dotenv';

dotenv.config();

function createSearchClient() {
    const endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
    const apiKey = process.env.AZURE_SEARCH_API_KEY;
    const indexName = process.env.AZURE_SEARCH_INDEX_NAME;

    if (!endpoint || !apiKey || !indexName) {
        throw new Error('Missing required environment variables. Check your .env file.');
    }

    return new SearchClient(endpoint, indexName, new AzureKeyCredential(apiKey));
}
```

### Error Handling Pattern

```javascript
async function safeSearch(searchClient, searchText, options = {}) {
    try {
        const results = await searchClient.search(searchText, options);
        const resultArray = [];
        for await (const result of results.results) {
            resultArray.push(result);
        }
        return resultArray;
    } catch (error) {
        if (error.statusCode) {
            console.error(`Search error ${error.statusCode}: ${error.message}`);
        } else {
            console.error(`Unexpected error: ${error.message}`);
        }
        return [];
    }
}
```

### Result Processing Pattern

```javascript
function displayResults(results, title, maxResults = 5) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(title);
    console.log('='.repeat(60));

    if (!results || results.length === 0) {
        console.log('No results found.');
        return;
    }

    const displayCount = Math.min(results.length, maxResults);
    
    for (let i = 0; i < displayCount; i++) {
        const result = results[i];
        const document = result.document;
        
        console.log(`\n${i + 1}. ${document.title || 'No title'}`);
        console.log(`   Score: ${result.score?.toFixed(2) || 'N/A'}`);
        console.log(`   Category: ${document.category || 'N/A'}`);
        console.log(`   Rating: ${document.rating || 'N/A'}`);
        
        // Show content preview if available
        if (document.content) {
            const preview = document.content.length > 100 
                ? document.content.substring(0, 100) + '...' 
                : document.content;
            console.log(`   Preview: ${preview}`);
        }
    }

    if (results.length > maxResults) {
        console.log(`\n... and ${results.length - maxResults} more results`);
    }
}
```

### Async Iterator Pattern

```javascript
async function processSearchResults(searchClient, query) {
    try {
        const searchResults = await searchClient.search(query);
        
        // Process results as they come
        for await (const result of searchResults.results) {
            console.log(`Processing: ${result.document.title}`);
            // Process each result...
        }
        
        // Access metadata
        console.log(`Total count: ${searchResults.count}`);
        
    } catch (error) {
        console.error('Search failed:', error.message);
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Ensure you're using ES modules
   # Add "type": "module" to package.json
   # Or use .mjs file extension
   ```

2. **Environment Variable Issues**
   - Verify your `.env` file is in the correct location
   - Check for typos in variable names
   - Ensure dotenv.config() is called before using variables

3. **Authentication Errors**
   - Verify your API key is correct
   - Check API key permissions
   - Ensure service endpoint is correct

4. **Index Not Found**
   - Verify index name in environment variables
   - Check if index exists in your search service
   - Run index creation from previous modules

5. **No Results**
   - Check if your index contains data
   - Try broader search terms
   - Verify field names in filters

### Debug Mode

Enable debug logging:

```javascript
// Add debug logging
function debugLog(message, data = null) {
    if (process.env.DEBUG === 'true') {
        console.log(`[DEBUG] ${message}`);
        if (data) {
            console.log(JSON.stringify(data, null, 2));
        }
    }
}

// Usage
debugLog('Executing search', { query: 'azure', options: searchOptions });
```

### Performance Monitoring

```javascript
async function timedSearch(searchClient, query, options = {}) {
    const startTime = Date.now();
    
    try {
        const results = await searchClient.search(query, options);
        const resultArray = [];
        
        for await (const result of results.results) {
            resultArray.push(result);
        }
        
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        console.log(`Search completed in ${duration}ms: ${resultArray.length} results`);
        return resultArray;
        
    } catch (error) {
        const endTime = Date.now();
        const duration = endTime - startTime;
        console.error(`Search failed after ${duration}ms: ${error.message}`);
        return [];
    }
}
```

## 📖 Additional Resources

- [Azure SDK for JavaScript Documentation](https://docs.microsoft.com/en-us/javascript/api/@azure/search-documents/)
- [Azure AI Search JavaScript Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents/samples)
- [Node.js Best Practices](https://nodejs.org/en/docs/guides/)
- [Modern JavaScript Features](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

## 🔗 Next Steps

1. **Practice with Real Data**: Apply these patterns to your own datasets
2. **Explore Advanced Features**: Move to Module 5 for advanced querying
3. **Build Applications**: Integrate search into your JavaScript applications
4. **Performance Tuning**: Learn about search optimization and analytics
5. **Web Integration**: Use these patterns in browser-based applications

## 🌐 Browser Usage

These examples can be adapted for browser use:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Azure Search Example</title>
</head>
<body>
    <script type="module">
        import { SearchClient, AzureKeyCredential } from 'https://cdn.skypack.dev/@azure/search-documents';
        
        // Note: In production, use environment variables or secure configuration
        const searchClient = new SearchClient(
            'https://your-service.search.windows.net',
            'your-index-name',
            new AzureKeyCredential('your-api-key')
        );
        
        async function performSearch() {
            try {
                const results = await searchClient.search('azure');
                for await (const result of results.results) {
                    console.log(result.document.title);
                }
            } catch (error) {
                console.error('Search failed:', error);
            }
        }
        
        performSearch();
    </script>
</body>
</html>
```

Happy coding! 🟨