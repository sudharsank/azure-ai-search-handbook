# REST API Examples - Module 3: Index Management

This directory contains comprehensive REST API examples for index management operations in Azure AI Search. These examples use direct HTTP calls and can be used with any programming language or HTTP client, making them perfect for understanding the underlying API and for integration with any technology stack.

## 📁 File Structure

```
rest/
├── README.md                           # This file
├── 01_create_basic_index.http         # Basic index creation
├── 02_schema_design.http              # Advanced schema design patterns
├── 03_data_ingestion.http             # Document upload strategies
├── 04_index_operations.http           # Index management operations
├── 05_performance_optimization.http   # Performance tuning techniques
└── 06_error_handling.http             # Error scenarios and responses
```

## 🚀 Quick Start

### Prerequisites

1. **HTTP Client**: Choose one of these options:
   - **VS Code REST Client Extension** (Recommended)
   - **Postman**
   - **curl** command line
   - **Insomnia**
   - Any HTTP client that supports REST

2. **Environment Variables**: Set these in your HTTP client:
   ```
   AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
   AZURE_SEARCH_ADMIN_KEY=your-admin-api-key
   AZURE_SEARCH_API_VERSION=2023-11-01
   ```

3. **VS Code Setup** (Recommended):
   ```bash
   # Install REST Client extension
   code --install-extension humao.rest-client
   
   # Create settings file
   mkdir .vscode
   echo '{"rest-client.environmentVariables": {"local": {"endpoint": "https://your-service.search.windows.net", "adminKey": "your-admin-key"}}}' > .vscode/settings.json
   ```

### Running Examples

#### With VS Code REST Client:
1. Open any `.http` file
2. Click "Send Request" above each HTTP request
3. View response in the adjacent panel

#### With curl:
```bash
# Basic index creation
curl -X POST "https://your-service.search.windows.net/indexes?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: your-admin-key" \
  -d @01_create_basic_index.json
```

#### With Postman:
1. Import the `.http` files or copy requests manually
2. Set environment variables
3. Execute requests

## 📚 Example Categories

### 1. Basic Index Creation (`01_create_basic_index.http`)
**Focus**: Fundamental index creation using REST API

**What you'll learn**:
- HTTP POST requests for index creation
- JSON schema definition structure
- Field type specifications in REST format
- Basic error response handling

**Key concepts**:
```http
POST {{endpoint}}/indexes?api-version={{apiVersion}}
Content-Type: application/json
api-key: {{adminKey}}

{
  "name": "basic-blog-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "retrievable": true
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "retrievable": true,
      "analyzer": "en.microsoft"
    }
  ]
}
```

### 2. Schema Design (`02_schema_design.http`)
**Focus**: Advanced schema design patterns using REST API

**What you'll learn**:
- Complex field type definitions
- Collection and complex field structures
- Field attribute optimization
- Schema validation through API responses

**Key concepts**:
```http
# Complex field with nested structure
{
  "name": "author",
  "type": "Edm.ComplexType",
  "fields": [
    {
      "name": "name",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "email",
      "type": "Edm.String",
      "searchable": false,
      "filterable": true
    }
  ]
}

# Collection field
{
  "name": "tags",
  "type": "Collection(Edm.String)",
  "searchable": false,
  "filterable": true,
  "facetable": true
}

# Date field with proper attributes
{
  "name": "publishedDate",
  "type": "Edm.DateTimeOffset",
  "filterable": true,
  "sortable": true,
  "facetable": false
}
```

### 3. Data Ingestion (`03_data_ingestion.http`)
**Focus**: Document upload and management using REST API

**What you'll learn**:
- Single document upload with POST
- Batch document operations
- Document merge and delete operations
- Upload result interpretation

**Key concepts**:
```http
# Single document upload
POST {{endpoint}}/indexes/{{indexName}}/docs/index?api-version={{apiVersion}}
Content-Type: application/json
api-key: {{adminKey}}

{
  "value": [
    {
      "@search.action": "upload",
      "id": "1",
      "title": "Getting Started with Azure AI Search",
      "content": "Azure AI Search is a powerful search service...",
      "author": "John Doe",
      "publishedDate": "2024-01-15T10:00:00Z"
    }
  ]
}

# Batch operations with different actions
{
  "value": [
    {
      "@search.action": "upload",
      "id": "1",
      "title": "New Document"
    },
    {
      "@search.action": "merge",
      "id": "2",
      "title": "Updated Title"
    },
    {
      "@search.action": "delete",
      "id": "3"
    }
  ]
}
```

### 4. Index Operations (`04_index_operations.http`)
**Focus**: Index lifecycle management using REST API

**What you'll learn**:
- Listing indexes with GET requests
- Getting index details and statistics
- Updating index schemas with PUT
- Index deletion with proper safety checks

**Key concepts**:
```http
# List all indexes
GET {{endpoint}}/indexes?api-version={{apiVersion}}
api-key: {{adminKey}}

# Get specific index
GET {{endpoint}}/indexes/{{indexName}}?api-version={{apiVersion}}
api-key: {{adminKey}}

# Update index schema
PUT {{endpoint}}/indexes/{{indexName}}?api-version={{apiVersion}}
Content-Type: application/json
api-key: {{adminKey}}

{
  "name": "{{indexName}}",
  "fields": [
    // Updated field definitions
  ]
}

# Delete index
DELETE {{endpoint}}/indexes/{{indexName}}?api-version={{apiVersion}}
api-key: {{adminKey}}
```

### 5. Performance Optimization (`05_performance_optimization.http`)
**Focus**: Performance tuning using REST API

**What you'll learn**:
- Optimal batch sizing for REST calls
- Parallel request strategies
- Request optimization techniques
- Performance monitoring through API responses

**Key concepts**:
```http
# Index with custom analyzer
{
  "name": "advanced-index",
  "fields": [...],
  "analyzers": [
    {
      "name": "custom_analyzer",
      "@odata.type": "#Microsoft.Azure.Search.CustomAnalyzer",
      "tokenizer": "standard_v2",
      "tokenFilters": [
        "lowercase",
        "stop"
      ]
    }
  ],
  "scoringProfiles": [
    {
      "name": "boost_recent",
      "textWeights": {
        "title": 2.0,
        "content": 1.0
      },
      "functions": [
        {
          "type": "freshness",
          "fieldName": "publishedDate",
          "boost": 2.0,
          "interpolation": "linear",
          "freshness": {
            "boostingDuration": "P30D"
          }
        }
      ]
    }
  ],
  "corsOptions": {
    "allowedOrigins": ["https://mywebsite.com"],
    "maxAgeInSeconds": 300
  }
}
```

### 6. Error Handling (`06_error_handling.http`)
**Focus**: Error scenarios and proper response handling

**What you'll learn**:
- Common HTTP error codes and meanings
- Error response structure analysis
- Retry strategies for different error types
- Validation error interpretation

**Key concepts**:
```http
# Optimized batch upload (100 documents)
POST {{endpoint}}/indexes/{{indexName}}/docs/index?api-version={{apiVersion}}
Content-Type: application/json
api-key: {{adminKey}}

{
  "value": [
    // 100 documents with @search.action: "upload"
  ]
}

# Get index statistics for monitoring
GET {{endpoint}}/indexes/{{indexName}}/stats?api-version={{apiVersion}}
api-key: {{adminKey}}

# Service statistics
GET {{endpoint}}/servicestats?api-version={{apiVersion}}
api-key: {{adminKey}}
```

**Key concepts**:
```http
# Example of validation error (missing required field)
POST {{endpoint}}/indexes?api-version={{apiVersion}}
Content-Type: application/json
api-key: {{adminKey}}

{
  "name": "invalid-index",
  "fields": [
    {
      "name": "title",
      "type": "Edm.String"
      // Missing key field - will cause 400 error
    }
  ]
}

# Response will be:
# HTTP/1.1 400 Bad Request
# {
#   "error": {
#     "code": "InvalidRequestParameter",
#     "message": "The request is invalid. Details: index : Found 0 key fields in index 'invalid-index'. Each index must have exactly one key field."
#   }
# }
```

## 🎯 Learning Paths

### 1. API Fundamentals Path
Understand the core REST API concepts:

```
01_create_basic_index.http      # Basic HTTP operations
04_index_operations.http        # CRUD operations
06_error_handling.http          # Error responses
03_data_ingestion.http          # Data operations
```

### 2. Advanced Features Path
Explore sophisticated index capabilities:

```
02_schema_design.http           # Complex schemas
05_performance_optimization.http # Optimization
04_index_operations.http        # Index management
06_error_handling.http          # Error handling
```

### 3. Integration Path
Focus on real-world integration scenarios:

```
06_error_handling.http          # Robust error handling
05_performance_optimization.http # Performance patterns
03_data_ingestion.http          # Bulk operations
04_index_operations.http        # Operational monitoring
```

## 🔧 HTTP Client Features

### VS Code REST Client Benefits
- ✅ Syntax highlighting for HTTP requests
- ✅ Variable substitution and environments
- ✅ Response formatting and history
- ✅ Code generation for multiple languages

### Postman Benefits
- ✅ GUI interface for request building
- ✅ Collection organization and sharing
- ✅ Automated testing capabilities
- ✅ Environment management

### curl Benefits
- ✅ Command-line automation
- ✅ Scriptable and CI/CD friendly
- ✅ Universal availability
- ✅ Precise control over requests

## 🚨 Common Issues and Solutions

### Issue 1: Authentication Errors (403 Forbidden)
```http
# Problem: Using query key for admin operations
# Solution: Use admin key for index management
api-key: {{adminKey}}  # Admin key required for index operations
```

### Issue 2: API Version Mismatch
```http
# Problem: Using outdated API version
# Solution: Use latest stable version
GET {{endpoint}}/indexes?api-version=2023-11-01  # Current version
```

### Issue 3: Content-Type Issues
```http
# Problem: Missing or incorrect Content-Type
# Solution: Always specify for POST/PUT operations
Content-Type: application/json
```

### Issue 4: JSON Formatting Errors
```json
// Problem: Invalid JSON syntax
// Solution: Validate JSON before sending
{
  "name": "valid-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true
    }
  ]
}
```

## 💡 Tips for Success

### Request Building
1. **Use Variables**: Define endpoints and keys as variables
2. **Validate JSON**: Always validate JSON syntax before sending
3. **Check Headers**: Ensure proper Content-Type and api-key headers
4. **Handle Responses**: Always check HTTP status codes
5. **Log Requests**: Keep track of successful request patterns

### Debugging Techniques
1. **Check Status Codes**: 200/201 for success, 4xx for client errors
2. **Read Error Messages**: Azure provides detailed error descriptions
3. **Validate Payloads**: Ensure JSON matches expected schema
4. **Test Incrementally**: Start with simple requests
5. **Use Network Tools**: Browser DevTools or Fiddler for debugging

### Performance Tips
1. **Batch Operations**: Always batch multiple documents
2. **Optimize Payload Size**: Balance batch size with request size
3. **Use Compression**: Enable gzip compression when possible
4. **Monitor Responses**: Track response times and success rates
5. **Implement Retry Logic**: Handle transient failures gracefully

## 🔗 Related Resources

### Module 3 Resources
- **[Module 3 Documentation](../documentation.md)** - Complete theory and concepts
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter notebook examples
- **[Python Examples](../python/README.md)** - Python SDK implementations
- **[C# Examples](../csharp/README.md)** - .NET SDK implementations
- **[JavaScript Examples](../javascript/README.md)** - JavaScript SDK implementations

### REST API Resources
- **[Azure AI Search REST API Reference](https://docs.microsoft.com/en-us/rest/api/searchservice/)** - Complete API documentation
- **[HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)** - HTTP status code reference
- **[JSON Schema Validation](https://json-schema.org/)** - JSON schema validation tools

### HTTP Client Resources
- **[VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)** - VS Code extension
- **[Postman](https://www.postman.com/)** - API development platform
- **[curl Documentation](https://curl.se/docs/)** - curl command reference

## 🚀 Next Steps

After mastering these REST API examples:

1. **✅ Complete All Examples**: Work through each HTTP file systematically
2. **🔧 Integrate with Your Stack**: Use any programming language with HTTP support
3. **📝 Practice**: Complete the module exercises
4. **🌐 Explore SDKs**: Try Python, C#, or JavaScript SDK examples
5. **🏗️ Build Applications**: Apply REST patterns to your projects
6. **📚 Continue Learning**: Move to Module 4: Simple Queries and Filters

---

**Ready to master Azure AI Search index management with REST API?** 🌐✨

Start with `01_create_basic_index.http` and build language-agnostic search solutions!