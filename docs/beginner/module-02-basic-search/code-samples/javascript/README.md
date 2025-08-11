# JavaScript Code Samples - Module 2: Basic Search Operations

This directory contains focused JavaScript examples for basic search operations in Azure AI Search using the JavaScript SDK. Each file demonstrates a specific aspect of search functionality with clear, production-ready code for both Node.js and browser environments.

## 📁 Files Overview

### Core Search Operations (Files 01-05)
1. **`01_simple_text_search.js`** - Basic text search and result handling
2. **`02_phrase_search.js`** - Exact phrase matching with quotes
3. **`03_boolean_search.js`** - Boolean operators (AND, OR, NOT)
4. **`04_wildcard_search.js`** - Pattern matching with wildcards
5. **`05_field_search.js`** - Field-specific and multi-field searches

### Advanced Features (Files 06-08)
6. **`06_result_processing.js`** - Processing and formatting search results
7. **`07_error_handling.js`** - Comprehensive error handling strategies
8. **`08_search_patterns.js`** - Advanced search patterns and best practices

## 🎯 Complete Coverage Matrix

| Topic | Python | C# | JavaScript | REST | Description |
|-------|--------|----|-----------|----- |-------------|
| Simple Text Search | ✅ | ✅ | ✅ | ✅ | Basic keyword searching |
| Phrase Search | ✅ | ✅ | ✅ | ✅ | Exact phrase matching |
| Boolean Search | ✅ | ✅ | ✅ | ✅ | AND, OR, NOT operators |
| Wildcard Search | ✅ | ✅ | ✅ | ✅ | Pattern matching with * |
| Field Search | ✅ | ✅ | ✅ | ✅ | Field-specific searches |
| Result Processing | ✅ | ✅ | ✅ | ✅ | Formatting and analysis |
| Error Handling | ✅ | ✅ | ✅ | ✅ | Robust error management |
| Search Patterns | ✅ | ✅ | ✅ | ✅ | Advanced strategies |

## 🚀 Getting Started

### ⚠️ CRITICAL FIRST STEP: Prerequisites Setup

**Before running ANY JavaScript examples, you MUST run the prerequisites setup:**

```bash
# Navigate to the parent directory
cd ../

# Run the prerequisites setup script
python setup_prerequisites.py
```

**What this does:**
- 🔌 Tests your Azure AI Search connection
- 🏗️ Creates the `handbook-samples` index with comprehensive schema
- 📄 Uploads 10 sample documents with rich content
- 🧪 Tests all search operations to ensure everything works
- 📋 Provides a summary of what's ready

**Time Required**: 5-10 minutes

### Prerequisites

#### For Node.js
```bash
# Initialize new project
npm init -y

# Install Azure Search SDK
npm install @azure/search-documents

# Optional: Install dotenv for environment variables
npm install dotenv
```

#### For Browser
```html
<!-- Include via CDN -->
<script src="https://cdn.jsdelivr.net/npm/@azure/search-documents@latest/dist/index.browser.js"></script>

<!-- Or use ES modules -->
<script type="module">
  import { SearchClient, AzureKeyCredential } from 'https://cdn.skypack.dev/@azure/search-documents';
</script>
```

### Configuration Setup

#### Option 1: Environment Variables (Node.js)
Create `.env` file:
```env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=your-index-name
```

Then in your code:
```javascript
require('dotenv').config();
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

const searchClient = new SearchClient(
    process.env.AZURE_SEARCH_SERVICE_ENDPOINT,
    process.env.AZURE_SEARCH_INDEX_NAME,
    new AzureKeyCredential(process.env.AZURE_SEARCH_API_KEY)
);
```

#### Option 2: Direct Configuration
```javascript
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

const searchClient = new SearchClient(
    'https://your-service.search.windows.net',
    'your-index-name',
    new AzureKeyCredential('your-api-key')
);
```

#### Option 3: Browser Configuration
```javascript
const searchClient = new AzureSearch.SearchClient(
    'https://your-service.search.windows.net',
    'your-index-name',
    new AzureSearch.AzureKeyCredential('your-api-key')
);
```

### Quick Start
```bash
# 1. FIRST: Run prerequisites setup (from parent directory)
cd ../
python setup_prerequisites.py

# 2. THEN: Run JavaScript examples
cd javascript/
node 01_simple_text_search.js

# Or with npm script
npm run search
```

## 📚 Learning Path

### Beginner Path (Recommended Order)
1. **Start Here**: `01_simple_text_search.js` - Learn basic search concepts
2. **Precision**: `02_phrase_search.js` - Understand exact matching
3. **Logic**: `03_boolean_search.js` - Combine terms with operators
4. **Flexibility**: `04_wildcard_search.js` - Pattern matching techniques
5. **Targeting**: `05_field_search.js` - Search specific fields

### Advanced Path (After Basics)
6. **Processing**: `06_result_processing.js` - Handle and format results effectively
7. **Reliability**: `07_error_handling.js` - Build robust search applications
8. **Patterns**: `08_search_patterns.js` - Implement advanced search strategies

### Quick Reference
- **Need basic search?** → `01_simple_text_search.js`
- **Want exact phrases?** → `02_phrase_search.js`
- **Combining terms?** → `03_boolean_search.js`
- **Partial matching?** → `04_wildcard_search.js`
- **Specific fields?** → `05_field_search.js`
- **Processing results?** → `06_result_processing.js`
- **Handling errors?** → `07_error_handling.js`
- **Advanced patterns?** → `08_search_patterns.js`

## 💡 Key JavaScript Concepts Covered

### Advanced Search Features
- **Result Processing**: Format, filter, and analyze search results
- **Error Handling**: Comprehensive error management and recovery strategies
- **Search Patterns**: Progressive search, fallback strategies, and multi-field searches
- **Performance Optimization**: Efficient result processing and caching strategies

### Modern JavaScript Features
- **Async/Await**: All search operations use modern async patterns
- **ES6 Classes**: Object-oriented approach to search operations
- **Destructuring**: Clean parameter handling
- **Template Literals**: String formatting and logging
- **For-await-of**: Async iteration over search results

### Azure SDK Integration
```javascript
// Import the SDK
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Create client
const searchClient = new SearchClient(endpoint, indexName, credential);

// Perform search
const results = await searchClient.search(query, options);

// Process results
for await (const result of results.results) {
    console.log(result.document.title);
}
```

### Error Handling
```javascript
try {
    const results = await searchClient.search(query);
    // Process results
} catch (error) {
    if (error.statusCode === 400) {
        console.error('Bad request - check query syntax');
    } else if (error.statusCode === 404) {
        console.error('Index not found');
    } else {
        console.error('Search error:', error.message);
    }
}
```

### Result Processing
```javascript
// Convert async iterator to array
const resultArray = [];
for await (const result of results.results) {
    resultArray.push(result);
}

// Or use helper function
const resultArray = [];
for await (const result of results.results) {
    resultArray.push({
        score: result.score,
        title: result.document.title,
        content: result.document.content
    });
}
```

## 🔧 Code Structure

Each JavaScript file follows this structure:
```javascript
/**
 * Module description and concepts covered
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

class ConceptDemo {
    /**
     * Initialize with a search client
     */
    constructor(searchClient) {
        if (!searchClient) {
            throw new Error('SearchClient is required');
        }
        this.searchClient = searchClient;
    }

    /**
     * Core functionality method
     */
    async mainMethod(query, top = 10) {
        // Implementation
    }

    /**
     * Static helper methods
     */
    static displayResults(searchResults) {
        // Display logic
    }
}

// Demonstration functions
async function demonstrateConcept() {
    // Demo execution
}

// Main execution
async function main() {
    try {
        await demonstrateConcept();
    } catch (error) {
        console.error('Demo failed:', error.message);
    }
}

// Export for use in other modules
module.exports = {
    ConceptDemo,
    demonstrateConcept
};

// Run if executed directly
if (require.main === module) {
    main();
}
```

## 🎯 Usage Examples

### Basic Search (Node.js)
```javascript
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

// Initialize client
const searchClient = new SearchClient(
    'https://your-service.search.windows.net',
    'your-index-name',
    new AzureKeyCredential('your-api-key')
);

// Perform search
async function basicSearch() {
    try {
        const results = await searchClient.search('python programming');
        
        for await (const result of results.results) {
            console.log(`Title: ${result.document.title}`);
            console.log(`Score: ${result.score}`);
        }
    } catch (error) {
        console.error('Search failed:', error.message);
    }
}

basicSearch();
```

### Basic Search (Browser)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Azure Search Demo</title>
    <script src="https://cdn.jsdelivr.net/npm/@azure/search-documents@latest/dist/index.browser.js"></script>
</head>
<body>
    <div id="results"></div>
    
    <script>
        async function performSearch() {
            const searchClient = new AzureSearch.SearchClient(
                'https://your-service.search.windows.net',
                'your-index-name',
                new AzureSearch.AzureKeyCredential('your-api-key')
            );

            try {
                const results = await searchClient.search('javascript tutorial');
                const resultsDiv = document.getElementById('results');
                
                for await (const result of results.results) {
                    const div = document.createElement('div');
                    div.innerHTML = `<h3>${result.document.title}</h3><p>Score: ${result.score}</p>`;
                    resultsDiv.appendChild(div);
                }
            } catch (error) {
                console.error('Search failed:', error.message);
            }
        }

        performSearch();
    </script>
</body>
</html>
```

### Using the Example Classes
```javascript
// Import from any example file
const { SimpleTextSearch } = require('./01_simple_text_search');
const { ResultProcessor } = require('./06_result_processing');
const { SafeSearchClient } = require('./07_error_handling');
const { SearchPatterns } = require('./08_search_patterns');

// Initialize and use basic search
const searchOps = new SimpleTextSearch(searchClient);
const results = await searchOps.basicSearch('machine learning', 5);
SimpleTextSearch.displayResults(results);

// Process results with advanced formatting
const processor = new ResultProcessor();
const processedResults = processor.processRawResults(results.results);
console.log(processor.formatForDisplay(processedResults));

// Use safe search with error handling
const safeClient = new SafeSearchClient(searchClient);
const { results: safeResults, errorMessage } = await safeClient.safeSearch('python programming');

// Implement advanced search patterns
const patterns = new SearchPatterns(searchClient);
const fallbackResults = await patterns.searchWithFallback('artificial intelligence tutorial');
```

## 🛡️ Error Handling

All examples include comprehensive error handling:
```javascript
async function safeSearch(query) {
    try {
        const results = await searchClient.search(query);
        return results;
    } catch (error) {
        // Handle specific error types
        switch (error.statusCode) {
            case 400:
                console.error('Invalid query syntax');
                break;
            case 401:
                console.error('Authentication failed');
                break;
            case 404:
                console.error('Index not found');
                break;
            default:
                console.error('Search error:', error.message);
        }
        return null;
    }
}
```

## 📊 Performance Tips

1. **Reuse Client**: Create SearchClient once and reuse
2. **Limit Results**: Use `top` parameter to limit result count
3. **Select Fields**: Use `select` to return only needed fields
4. **Async Processing**: Use async/await for non-blocking operations
5. **Error Handling**: Always handle errors gracefully

## 🌐 Browser Considerations

### CORS Configuration
Ensure your Azure Search service allows CORS for browser requests:
```javascript
// This needs to be configured in Azure portal, not in code
// Allow origins: https://yourdomain.com
// Allow headers: content-type, api-key
// Allow methods: GET, POST
```

### Security Notes
- Never expose admin API keys in browser code
- Use query-only keys for client-side applications
- Consider using a backend proxy for sensitive operations

## 🔗 Integration Examples

### With Express.js
```javascript
const express = require('express');
const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');

const app = express();
const searchClient = new SearchClient(/* config */);

app.get('/api/search', async (req, res) => {
    try {
        const { q } = req.query;
        const results = await searchClient.search(q);
        
        const resultArray = [];
        for await (const result of results.results) {
            resultArray.push(result);
        }
        
        res.json(resultArray);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000);
```

### With React
```jsx
import React, { useState, useEffect } from 'react';
import { SearchClient, AzureKeyCredential } from '@azure/search-documents';

function SearchComponent() {
    const [results, setResults] = useState([]);
    const [query, setQuery] = useState('');

    const searchClient = new SearchClient(/* config */);

    const performSearch = async () => {
        try {
            const searchResults = await searchClient.search(query);
            const resultArray = [];
            
            for await (const result of searchResults.results) {
                resultArray.push(result);
            }
            
            setResults(resultArray);
        } catch (error) {
            console.error('Search failed:', error);
        }
    };

    return (
        <div>
            <input 
                value={query} 
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && performSearch()}
            />
            <button onClick={performSearch}>Search</button>
            
            {results.map((result, index) => (
                <div key={index}>
                    <h3>{result.document.title}</h3>
                    <p>Score: {result.score}</p>
                </div>
            ))}
        </div>
    );
}
```

## 🚀 Next Steps

After working through these examples:
1. ✅ Try modifying the queries and parameters
2. 🔧 Implement your own search functionality
3. 📚 Explore other language examples
4. 🌐 Build a web interface using the browser examples
5. 📖 Move on to Module 3: Index Management

## 🔗 Cross-Language Learning

These JavaScript examples complement the other language implementations:
- **[Python Examples](../python/README.md)** - Python implementations for data science workflows
- **[C# Examples](../csharp/README.md)** - .NET implementations with enterprise patterns
- **[REST API Examples](../rest/README.md)** - Direct HTTP API calls for any language
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter examples for experimentation

**🎯 Learning Approach:**
- **Web Development Path**: Focus on browser and Node.js patterns
- **Sequential Learning**: Follow 01-08 in order for structured learning
- **Framework Integration**: Learn React, Express.js, and modern web patterns
- **Cross-Platform**: Compare JavaScript patterns with other language implementations

## 📖 Additional Resources

- [@azure/search-documents Documentation](https://docs.microsoft.com/en-us/javascript/api/@azure/search-documents/)
- [Azure AI Search JavaScript Samples](https://github.com/Azure-Samples/azure-search-javascript-samples)
- [JavaScript SDK Quickstart](https://docs.microsoft.com/en-us/azure/search/search-get-started-javascript)
- [Modern JavaScript Guide](https://javascript.info/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)

---

**Happy Coding!** 🟨✨