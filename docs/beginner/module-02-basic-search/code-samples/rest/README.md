# REST API Examples - Module 2: Basic Search Operations

This directory contains comprehensive REST API examples for basic search operations in Azure AI Search. These examples use direct HTTP calls and can be used with any programming language or HTTP client.

## 📁 Files Overview

### Core Search Operations
1. **`01_simple_text_search.http`** - Basic text search operations
2. **`02_phrase_search.http`** - Exact phrase matching with quotes
3. **`03_boolean_search.http`** - Boolean operators (AND, OR, NOT)
4. **`04_wildcard_search.http`** - Pattern matching with wildcards
5. **`05_field_search.http`** - Field-specific searches

### Advanced Search Operations
6. **`06_result_processing.http`** - Processing and formatting search results
7. **`07_error_handling.http`** - Comprehensive error handling strategies
8. **`08_search_patterns.http`** - Common search patterns and best practices

## 🚀 Getting Started

### Prerequisites

#### Option 1: VS Code REST Client Extension (Recommended)
1. Install [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
2. Open any `.http` file in VS Code
3. Click "Send Request" above each HTTP request

#### Option 2: curl Command Line
```bash
# Basic search example
curl -X POST "https://your-service.search.windows.net/indexes/your-index/docs/search?api-version=2023-11-01" \
     -H "Content-Type: application/json" \
     -H "api-key: your-api-key" \
     -d '{"search": "python programming", "top": 5}'
```

#### Option 3: Postman
1. Import the HTTP requests into Postman
2. Set up environment variables for endpoint, api-key, and index-name
3. Execute requests

#### Option 4: Any HTTP Client
Use the examples with any HTTP client in any programming language.

### Configuration Setup

Before using the examples, update these variables in each `.http` file:

```http
### Variables (replace with your actual values)
@endpoint = https://your-service.search.windows.net
@api-key = your-api-key-here
@index-name = your-index-name
@api-version = 2023-11-01
```

### Quick Start
```bash
# 1. FIRST: Run prerequisites setup (from parent directory)
cd ../
python setup_prerequisites.py

# 2. THEN: Use REST API examples
```

1. Open any `.http` file in VS Code with REST Client extension
2. Update the variables at the top (endpoint, api-key, index-name should be `handbook-samples`)
3. Click "Send Request" above any HTTP request
4. View the response in the adjacent panel

## 📚 Learning Path

### Beginner Path (Recommended Order)
1. **Start Here**: `01_simple_text_search.http` - Learn basic search concepts
2. **Precision**: `02_phrase_search.http` - Understand exact matching
3. **Logic**: `03_boolean_search.http` - Combine terms with operators
4. **Flexibility**: `04_wildcard_search.http` - Pattern matching techniques
5. **Targeting**: `05_field_search.http` - Search specific fields

### Advanced Path (After Basics)
6. **Processing**: `06_result_processing.http` - Handle and format results effectively
7. **Reliability**: `07_error_handling.http` - Build robust search applications
8. **Patterns**: `08_search_patterns.http` - Implement advanced search strategies

### Quick Reference
- **Need basic search?** → `01_simple_text_search.http`
- **Want exact phrases?** → `02_phrase_search.http`
- **Combining terms?** → `03_boolean_search.http`
- **Partial matching?** → `04_wildcard_search.http`
- **Specific fields?** → `05_field_search.http`
- **Processing results?** → `06_result_processing.http`
- **Handling errors?** → `07_error_handling.http`
- **Advanced patterns?** → `08_search_patterns.http`

## 💡 Key REST API Concepts Covered

### Advanced Search Features
- **Result Processing**: Field selection, highlighting, pagination, and export-ready queries
- **Error Handling**: Comprehensive HTTP status code handling and fallback strategies
- **Search Patterns**: Progressive search, multi-field priority, and performance-optimized patterns
- **API Best Practices**: Proper request structure, parameter validation, and response handling

### HTTP Request Structure
```http
POST {{endpoint}}/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{api-key}}

{
    "search": "your search query",
    "top": 10,
    "includeTotalCount": true
}
```

### Common Request Parameters
- **`search`**: The search query text
- **`top`**: Maximum number of results to return
- **`skip`**: Number of results to skip (for pagination)
- **`select`**: Fields to include in results
- **`searchFields`**: Fields to search in
- **`highlight`**: Fields to highlight
- **`includeTotalCount`**: Include total count in response

### Response Structure
```json
{
  "@odata.context": "...",
  "@odata.count": 42,
  "value": [
    {
      "@search.score": 1.234,
      "@search.highlights": {
        "title": ["<mark>python</mark> tutorial"]
      },
      "id": "doc1",
      "title": "Python Programming Tutorial",
      "author": "John Doe",
      "content": "Learn Python programming...",
      "url": "https://example.com/python-tutorial"
    }
  ]
}
```

### HTTP Status Codes
- **200 OK**: Successful search
- **400 Bad Request**: Invalid query syntax or parameters
- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: API key doesn't have required permissions
- **404 Not Found**: Index doesn't exist
- **429 Too Many Requests**: Rate limit exceeded
- **503 Service Unavailable**: Service temporarily unavailable

## 🔧 Request Examples

### Basic Search
```http
POST {{endpoint}}/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{api-key}}

{
    "search": "python programming",
    "top": 10,
    "includeTotalCount": true
}
```

### Search with Field Selection
```http
POST {{endpoint}}/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{api-key}}

{
    "search": "web development",
    "select": "id,title,author,url",
    "top": 5
}
```

### Search with Highlighting
```http
POST {{endpoint}}/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{api-key}}

{
    "search": "javascript",
    "highlight": "title,content",
    "highlightPreTag": "<mark>",
    "highlightPostTag": "</mark>",
    "top": 5
}
```

### Paginated Search
```http
POST {{endpoint}}/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{api-key}}

{
    "search": "tutorial",
    "top": 10,
    "skip": 20,
    "includeTotalCount": true
}
```

## 🛡️ Error Handling

### Common Errors and Solutions

#### 400 Bad Request
```json
{
  "error": {
    "code": "InvalidRequestParameter",
    "message": "The request is invalid. Details: parameter 'search' cannot be empty."
  }
}
```
**Solution**: Check query syntax and required parameters

#### 401 Unauthorized
```json
{
  "error": {
    "code": "Unauthorized",
    "message": "Access denied due to invalid subscription key."
  }
}
```
**Solution**: Verify API key is correct and active

#### 404 Not Found
```json
{
  "error": {
    "code": "ResourceNotFound",
    "message": "The index 'your-index' was not found."
  }
}
```
**Solution**: Check index name and ensure index exists

## 🌐 Language Integration Examples

### Python with requests
```python
import requests
import json

url = "https://your-service.search.windows.net/indexes/your-index/docs/search"
headers = {
    "Content-Type": "application/json",
    "api-key": "your-api-key"
}
params = {"api-version": "2023-11-01"}
data = {
    "search": "python programming",
    "top": 5
}

response = requests.post(url, headers=headers, params=params, json=data)
results = response.json()
```

### JavaScript with fetch
```javascript
const endpoint = "https://your-service.search.windows.net";
const indexName = "your-index";
const apiKey = "your-api-key";

const response = await fetch(`${endpoint}/indexes/${indexName}/docs/search?api-version=2023-11-01`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'api-key': apiKey
    },
    body: JSON.stringify({
        search: "javascript tutorial",
        top: 5
    })
});

const results = await response.json();
```

### C# with HttpClient
```csharp
using System.Text;
using System.Text.Json;

var client = new HttpClient();
client.DefaultRequestHeaders.Add("api-key", "your-api-key");

var searchRequest = new
{
    search = "machine learning",
    top = 5
};

var json = JsonSerializer.Serialize(searchRequest);
var content = new StringContent(json, Encoding.UTF8, "application/json");

var response = await client.PostAsync(
    "https://your-service.search.windows.net/indexes/your-index/docs/search?api-version=2023-11-01",
    content
);

var results = await response.Content.ReadAsStringAsync();
```

### PowerShell
```powershell
$endpoint = "https://your-service.search.windows.net"
$indexName = "your-index"
$apiKey = "your-api-key"

$headers = @{
    "Content-Type" = "application/json"
    "api-key" = $apiKey
}

$body = @{
    search = "web development"
    top = 5
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$endpoint/indexes/$indexName/docs/search?api-version=2023-11-01" -Method Post -Headers $headers -Body $body
```

## 📊 Performance Tips

1. **Use POST**: POST requests are more flexible than GET for complex queries
2. **Limit Results**: Use `top` parameter to avoid large responses
3. **Select Fields**: Use `select` to return only needed fields
4. **Batch Requests**: Consider batching multiple searches when possible
5. **Cache Results**: Cache frequently used search results
6. **Monitor Usage**: Track API usage to avoid rate limits

## 🔍 Advanced Query Examples

### Complex Boolean Query
```json
{
    "search": "(python OR javascript) AND tutorial NOT deprecated",
    "top": 10
}
```

### Field-Specific Search
```json
{
    "search": "machine learning",
    "searchFields": "title,description",
    "top": 5
}
```

### Search with Facets
```json
{
    "search": "programming",
    "facets": ["category", "author", "publishedYear"],
    "top": 10
}
```

### Search with Filters
```json
{
    "search": "tutorial",
    "filter": "category eq 'programming' and publishedYear ge 2020",
    "top": 10
}
```

## 🔧 Advanced Features

### Result Processing Patterns
The `06_result_processing.http` file demonstrates:
- Field selection for efficient data transfer
- Content highlighting for preview generation
- Pagination strategies for large datasets
- Export-ready query configurations

### Error Handling Strategies
The `07_error_handling.http` file covers:
- Common error scenarios and their HTTP status codes
- Input validation through API parameters
- Fallback search strategies for reliability
- Service health checks and diagnostics

### Search Pattern Implementation
The `08_search_patterns.http` file shows:
- Progressive search from specific to broad
- Multi-field priority search strategies
- Quality-based result filtering
- Performance-optimized query patterns

## 🚀 Next Steps

After working through these examples:
1. ✅ Try different query combinations
2. 🔧 Integrate with your preferred programming language
3. 📚 Explore other language-specific examples
4. 🎯 Build a complete search application
5. 📖 Move on to Module 3: Index Management

## 📖 Additional Resources

- [Azure AI Search REST API Reference](https://docs.microsoft.com/en-us/rest/api/searchservice/)
- [Search API Documentation](https://docs.microsoft.com/en-us/azure/search/search-query-rest-api)
- [Query Syntax Reference](https://docs.microsoft.com/en-us/azure/search/query-simple-syntax)
- [HTTP Status Codes](https://docs.microsoft.com/en-us/azure/search/search-query-rest-api#http-status-codes)

---

**Happy Searching!** 🌐✨