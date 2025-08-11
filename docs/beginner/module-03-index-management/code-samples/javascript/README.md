# JavaScript Code Samples - Module 3: Index Management

This directory contains focused JavaScript examples for index management operations in Azure AI Search using the JavaScript SDK. Each file demonstrates a specific aspect of index management with clear, production-ready code for both Node.js and browser environments.

## 📁 File Structure

```
javascript/
├── README.md                           # This file
├── 01_create_basic_index.js           # Basic index creation
├── 02_schema_design.js                # Advanced schema design patterns
├── 03_data_ingestion.js               # Document upload strategies
├── 04_index_operations.js             # Index management operations
├── 05_performance_optimization.js     # Performance tuning techniques
└── 06_error_handling.js               # Robust error handling patterns
```

## 🚀 Quick Start

### Prerequisites

1. **Node.js Environment**:
   ```bash
   # Node.js 14.x or later required
   node --version
   npm --version
   
   # Initialize project (if needed)
   npm init -y
   ```

2. **Package Installation**:
   ```bash
   # Install Azure Search SDK
   npm install @azure/search-documents
   
   # Install additional utilities
   npm install dotenv axios
   
   # For development
   npm install --save-dev @types/node
   ```

3. **Environment Configuration**:
   ```bash
   # Create .env file
   echo "AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net" > .env
   echo "AZURE_SEARCH_ADMIN_KEY=your-admin-api-key" >> .env
   ```

### Running Examples

```bash
# Basic index creation
node 01_create_basic_index.js

# Advanced schema design
node 02_schema_design.js

# Data ingestion strategies
node 03_data_ingestion.js

# Continue with other examples...
```

## 📚 Example Categories

### 1. Basic Index Creation (`01_create_basic_index.js`)
**Focus**: Fundamental index creation concepts in JavaScript

**What you'll learn**:
- Creating SearchIndexClient with proper authentication
- Defining field types using JavaScript objects
- Index creation with async/await patterns
- Basic error handling with try/catch

**Key concepts**:
```javascript
const { SearchIndexClient, AzureKeyCredential } = require('@azure/search-documents');

// Client creation
const indexClient = new SearchIndexClient(
    endpoint,
    new AzureKeyCredential(adminKey)
);

// Field definition
const fields = [
    {
        name: "id",
        type: "Edm.String",
        key: true
    },
    {
        name: "title",
        type: "Edm.String",
        searchable: true
    }
];

// Index creation
const index = { name: "my-index", fields };
await indexClient.createIndex(index);
```

### 2. Schema Design (`02_schema_design.js`)
**Focus**: Advanced schema design patterns and JavaScript best practices

**What you'll learn**:
- Complex field type definitions
- Attribute optimization for web applications
- Nested object handling with complex fields
- Schema validation and testing patterns

**Key concepts**:
```javascript
// Complex field with nested structure
const authorField = {
    name: "author",
    type: "Edm.ComplexType",
    fields: [
        { name: "name", type: "Edm.String" },
        { name: "email", type: "Edm.String" }
    ]
};

// Collection field
const tagsField = {
    name: "tags",
    type: "Collection(Edm.String)",
    filterable: true,
    facetable: true
};

// Date field with proper formatting
const dateField = {
    name: "publishedDate",
    type: "Edm.DateTimeOffset",
    filterable: true,
    sortable: true
};
```

### 3. Data Ingestion (`03_data_ingestion.js`)
**Focus**: Efficient document upload and management strategies

**What you'll learn**:
- Batch document operations using uploadDocuments
- Promise-based async patterns
- Large dataset processing with streams
- Progress tracking and monitoring

**Key concepts**:
```javascript
// Batch upload
const documents = [
    { id: "1", title: "Document 1", content: "Content..." },
    { id: "2", title: "Document 2", content: "Content..." }
];

const uploadResult = await searchClient.uploadDocuments(documents);

// Check results
uploadResult.results.forEach(result => {
    if (!result.succeeded) {
        console.log(`Failed: ${result.key} - ${result.errorMessage}`);
    }
});

// Large dataset processing
async function uploadLargeDataset(documents, batchSize = 100) {
    for (let i = 0; i < documents.length; i += batchSize) {
        const batch = documents.slice(i, i + batchSize);
        await uploadBatch(batch);
        console.log(`Uploaded batch ${Math.floor(i / batchSize) + 1}`);
    }
}
```

### 4. Index Operations (`04_index_operations.js`)
**Focus**: Index lifecycle management operations

**What you'll learn**:
- Listing and inspecting indexes
- Getting index statistics and metrics
- Schema updates and versioning
- Index deletion with safety checks

**Key concepts**:
```javascript
// List indexes
const indexes = await indexClient.listIndexes();
for await (const index of indexes) {
    console.log(`Index: ${index.name} (${index.fields.length} fields)`);
}

// Get index details
const index = await indexClient.getIndex("my-index");
console.log(`Fields: ${index.fields.length}`);

// Update schema
const updatedIndex = {
    name: index.name,
    fields: [...index.fields, newField]
};
await indexClient.createOrUpdateIndex(updatedIndex);
```

### 5. Performance Optimization (`05_performance_optimization.js`)
**Focus**: Performance tuning and optimization techniques

**What you'll learn**:
- Optimal batch sizing for JavaScript environments
- Parallel processing with Promise.all
- Memory management for large datasets
- Performance monitoring and metrics

**Key concepts**:
```javascript
// Custom analyzer
const customAnalyzer = {
    name: "my_analyzer",
    tokenizer: "standard",
    tokenFilters: ["lowercase", "stop"]
};

// Scoring profile
const scoringProfile = {
    name: "boost_recent",
    textWeights: {
        title: 2.0,
        content: 1.0
    },
    functions: [
        {
            type: "freshness",
            fieldName: "publishedDate",
            boost: 2.0,
            interpolation: "linear",
            freshness: {
                boostingDuration: "P30D"
            }
        }
    ]
};

// Index with advanced configuration
const index = {
    name: "advanced-index",
    fields: fields,
    analyzers: [customAnalyzer],
    scoringProfiles: [scoringProfile]
};
```

### 6. Error Handling (`06_error_handling.js`)
**Focus**: Robust error handling and recovery patterns

**What you'll learn**:
- Exception handling with RestError
- Retry strategies with exponential backoff
- Partial failure recovery strategies
- Logging and monitoring integration

**Key concepts**:
```javascript
// Parallel batch processing
async function parallelUpload(batches, maxConcurrency = 4) {
    const semaphore = new Semaphore(maxConcurrency);
    
    const uploadPromises = batches.map(async (batch) => {
        await semaphore.acquire();
        try {
            return await uploadBatch(batch);
        } finally {
            semaphore.release();
        }
    });
    
    return await Promise.all(uploadPromises);
}

// Optimal batch sizing
function getOptimalBatchSize(documentSizeKB) {
    if (documentSizeKB < 1) return 1000;
    if (documentSizeKB < 10) return 500;
    if (documentSizeKB < 100) return 100;
    return 50;
}

// Memory-efficient streaming
async function* processLargeFile(filePath) {
    const stream = fs.createReadStream(filePath, { encoding: 'utf8' });
    let buffer = '';
    
    for await (const chunk of stream) {
        buffer += chunk;
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line
        
        for (const line of lines) {
            if (line.trim()) {
                yield JSON.parse(line);
            }
        }
    }
}
```

**Key concepts**:
```javascript
// Comprehensive error handling
async function safeUpload(documents, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const result = await searchClient.uploadDocuments(documents);
            return processResults(result);
        } catch (error) {
            lastError = error;
            
            if (error.statusCode === 403) {
                throw new Error('Authentication failed - check admin key');
            }
            
            if (error.statusCode === 503 && attempt < maxRetries) {
                const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
                console.log(`Service unavailable, retrying in ${delay}ms...`);
                await sleep(delay);
                continue;
            }
            
            if (attempt === maxRetries) {
                throw lastError;
            }
        }
    }
}

// Retry utility
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Error classification
function classifyError(error) {
    if (error.statusCode >= 400 && error.statusCode < 500) {
        return 'client_error';
    } else if (error.statusCode >= 500) {
        return 'server_error';
    } else {
        return 'unknown_error';
    }
}
```

## 🎯 Learning Paths

### 1. Beginner Path (Sequential)
Follow the numbered sequence for structured learning:

```bash
node 01_create_basic_index.js      # Start here
node 02_schema_design.js           # Learn schema design
node 03_data_ingestion.js          # Master data upload
node 04_index_operations.js        # Index management
# Continue through all examples...
```

### 2. Web Development Path
Focus on browser and web application patterns:

```bash
node 05_performance_optimization.js # Client-side performance
node 06_error_handling.js          # User-friendly error handling
node 03_data_ingestion.js          # Efficient data loading
```

### 3. Node.js Backend Path
Focus on server-side patterns:

```bash
node 03_data_ingestion.js          # Bulk data processing
node 05_performance_optimization.js # Server performance
node 06_error_handling.js          # Robust error handling
node 04_index_operations.js        # Index management
```

## 🔧 Code Features

### Modern JavaScript Patterns
- ✅ ES6+ syntax with async/await
- ✅ Promise-based error handling
- ✅ Modular code with imports/exports
- ✅ Environment variable configuration
- ✅ Comprehensive JSDoc documentation

### Performance Optimizations
- ✅ Efficient batch processing
- ✅ Parallel operations with Promise.all
- ✅ Memory-conscious streaming for large datasets
- ✅ Connection pooling and reuse

### Browser and Node.js Compatibility
- ✅ Works in both browser and Node.js environments
- ✅ Proper CORS handling for web applications
- ✅ Environment-specific optimizations
- ✅ Polyfills for older browsers when needed

## 🚨 Common Issues and Solutions

### Issue 1: Package Installation Problems
```bash
# Problem: npm install fails
# Solution: Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue 2: CORS Issues in Browser
```javascript
// Problem: CORS errors when calling from browser
// Solution: Configure CORS in index definition
const corsOptions = {
    allowedOrigins: ["https://mywebsite.com"],
    maxAgeInSeconds: 300
};

const index = {
    name: "my-index",
    fields: fields,
    corsOptions: corsOptions
};
```

### Issue 3: Authentication in Browser
```javascript
// Problem: Exposing admin keys in browser
// Solution: Use a backend proxy or query keys for read operations
// Never expose admin keys in client-side code!

// For read-only operations, use query key:
const searchClient = new SearchClient(
    endpoint,
    indexName,
    new AzureKeyCredential(queryKey) // Query key, not admin key
);
```

### Issue 4: Memory Issues with Large Files
```javascript
// Problem: Out of memory with large datasets
// Solution: Use streaming and batching
async function processLargeDataset(filePath) {
    const batchSize = 100;
    let batch = [];
    
    for await (const document of readFileStream(filePath)) {
        batch.push(document);
        
        if (batch.length >= batchSize) {
            await uploadBatch(batch);
            batch = []; // Clear batch to free memory
        }
    }
    
    // Upload remaining documents
    if (batch.length > 0) {
        await uploadBatch(batch);
    }
}
```

## 💡 Tips for Success

### Development Workflow
1. **Use Environment Variables**: Never hardcode credentials
2. **Handle Promises Properly**: Always use async/await or .catch()
3. **Implement Proper Logging**: Use console.log strategically
4. **Test in Both Environments**: Browser and Node.js if applicable
5. **Monitor Performance**: Track upload speeds and success rates

### Debugging Techniques
1. **Use Browser DevTools**: Network tab for HTTP requests
2. **Enable Verbose Logging**: Log request/response details
3. **Check Network Connectivity**: Verify endpoint accessibility
4. **Validate JSON**: Ensure document structure is correct
5. **Test Incrementally**: Start with small batches

### Performance Tips
1. **Batch Operations**: Always batch multiple documents
2. **Optimize Batch Size**: Adjust based on document size
3. **Use Parallel Processing**: Promise.all for concurrent operations
4. **Monitor Memory Usage**: Especially important in browsers
5. **Implement Caching**: Cache clients and reuse connections

## 🔗 Related Resources

### Module 3 Resources
- **[Module 3 Documentation](../documentation.md)** - Complete theory and concepts
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter notebook examples
- **[Python Examples](../python/README.md)** - Python implementations
- **[C# Examples](../csharp/README.md)** - .NET implementations

### JavaScript and Azure Resources
- **[@azure/search-documents Documentation](https://docs.microsoft.com/en-us/javascript/api/@azure/search-documents/)** - Official JavaScript SDK docs
- **[Azure AI Search JavaScript Samples](https://github.com/Azure-Samples/azure-search-javascript-samples)** - Official samples
- **[Modern JavaScript Guide](https://javascript.info/)** - Comprehensive JavaScript reference

## 🚀 Next Steps

After mastering these JavaScript examples:

1. **✅ Complete All Examples**: Work through each file systematically
2. **🌐 Build Web Applications**: Integrate with your web projects
3. **📝 Practice**: Complete the module exercises
4. **🔄 Explore Other Languages**: Try Python, C#, or REST examples
5. **🏗️ Create Full-Stack Solutions**: Combine with frontend frameworks
6. **📚 Continue Learning**: Move to Module 4: Simple Queries and Filters

---

**Ready to master Azure AI Search index management with JavaScript?** 🟨✨

Start with `01_create_basic_index.js` and build powerful search experiences!