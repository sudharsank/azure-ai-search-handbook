# REST API Examples - Simple Queries and Filters

This directory contains REST API examples for learning simple queries and filters in Azure AI Search using direct HTTP calls. These examples can be used with any HTTP client or programming language.

## 📋 Prerequisites

### HTTP Client Options

Choose one of these HTTP clients to run the examples:

1. **VS Code REST Client Extension** (Recommended)
   - Install the "REST Client" extension in VS Code
   - Open `.http` files directly in VS Code
   - Click "Send Request" above each request

2. **curl** (Command line)
   - Available on most systems
   - Copy commands from examples

3. **Postman**
   - Import the requests
   - Set up environment variables

4. **HTTPie**
   - Modern command-line HTTP client
   - `pip install httpie`

### Environment Setup

Create a `.env` file or set these environment variables:

```env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=your-index-name
```

### VS Code REST Client Variables

If using VS Code REST Client, create a `rest-client.env.json` file:

```json
{
  "dev": {
    "searchEndpoint": "https://your-service.search.windows.net",
    "apiKey": "your-api-key",
    "indexName": "your-index-name"
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

### Basic REST API Structure

All Azure AI Search queries follow this pattern:

```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version=2023-11-01
Content-Type: application/json
api-key: {{apiKey}}
```

### Query Parameters

Common query parameters:

- `search` - Search text
- `$filter` - OData filter expression
- `$orderby` - Sort expression
- `$top` - Number of results to return
- `$skip` - Number of results to skip
- `$select` - Fields to return
- `searchFields` - Fields to search in
- `highlight` - Fields to highlight
- `searchMode` - any or all
- `queryType` - simple or full

## 📚 Code Samples

### 1. Basic Queries (`01_basic_queries.http`)
Learn fundamental text search operations:
- Simple text search
- Field-specific search
- Query operators (+, -, "", *, ())
- Search modes and query types

**Key Concepts:**
- HTTP GET requests
- Query parameter encoding
- Response structure
- Error handling

### 2. Filtering (`02_filtering.http`)
Master OData filter expressions:
- Equality and comparison filters
- Logical operators (and, or, not)
- Collection filters (any, all)
- Date and numeric range filters

**Key Concepts:**
- OData filter syntax
- URL encoding for filters
- Complex filter expressions
- Performance optimization

### 3. Sorting and Pagination (`03_sorting_pagination.http`)
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

### 4. Result Customization (`04_result_customization.http`)
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

### 5. Advanced Queries (`05_advanced_queries.http`)
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

### 6. Error Handling (`06_error_handling.http`)
Implement robust error handling:
- Common error scenarios
- HTTP status codes
- Error response format
- Debugging techniques

**Key Concepts:**
- HTTP error codes
- Error response structure
- Debugging strategies
- Best practices

## 🔧 Running the Examples

### Using VS Code REST Client

1. Install the REST Client extension
2. Open any `.http` file
3. Click "Send Request" above each request
4. View results in the response panel

### Using curl

Copy the curl commands from the examples:

```bash
# Basic search example
curl -X GET \
  "https://your-service.search.windows.net/indexes/your-index/docs?api-version=2023-11-01&search=azure" \
  -H "Content-Type: application/json" \
  -H "api-key: your-api-key"
```

### Using PowerShell

```powershell
# Basic search example
$headers = @{
    'Content-Type' = 'application/json'
    'api-key' = 'your-api-key'
}

$response = Invoke-RestMethod -Uri "https://your-service.search.windows.net/indexes/your-index/docs?api-version=2023-11-01&search=azure" -Headers $headers -Method GET

$response | ConvertTo-Json -Depth 10
```

### Using Python requests

```python
import requests
import json

headers = {
    'Content-Type': 'application/json',
    'api-key': 'your-api-key'
}

url = 'https://your-service.search.windows.net/indexes/your-index/docs'
params = {
    'api-version': '2023-11-01',
    'search': 'azure'
}

response = requests.get(url, headers=headers, params=params)
print(json.dumps(response.json(), indent=2))
```

## 🎯 Learning Outcomes

After completing these REST API examples, you will be able to:

- ✅ **Construct HTTP Requests**: Build proper Azure AI Search API calls
- ✅ **Execute Basic Queries**: Perform text searches with various operators
- ✅ **Apply Filters**: Use OData expressions to filter results effectively
- ✅ **Implement Pagination**: Handle large result sets with proper pagination
- ✅ **Customize Results**: Select fields and highlight matching terms
- ✅ **Handle Errors**: Understand and debug HTTP errors
- ✅ **Optimize Performance**: Write efficient queries for production use

## 🔍 Common Patterns

### Basic Search Request

```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version=2023-11-01&search=azure
Content-Type: application/json
api-key: {{apiKey}}
```

### Filtered Search Request

```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version=2023-11-01&search=*&$filter=category eq 'Technology'
Content-Type: application/json
api-key: {{apiKey}}
```

### Paginated Search Request

```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version=2023-11-01&search=azure&$top=10&$skip=20
Content-Type: application/json
api-key: {{apiKey}}
```

### Search with Highlighting

```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version=2023-11-01&search=machine learning&highlight=title,content&highlightPreTag=<mark>&highlightPostTag=</mark>
Content-Type: application/json
api-key: {{apiKey}}
```

## 🔗 URL Encoding

Important characters that need URL encoding:

| Character | Encoded |
|-----------|---------|
| Space | `%20` |
| `"` | `%22` |
| `'` | `%27` |
| `&` | `%26` |
| `+` | `%2B` |
| `=` | `%3D` |

### Example

```
Original: category eq 'Technology' and rating ge 4.0
Encoded:  category%20eq%20%27Technology%27%20and%20rating%20ge%204.0
```

## 🐛 Troubleshooting

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid query syntax, malformed OData |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | API key lacks permissions |
| 404 | Not Found | Index doesn't exist |
| 429 | Too Many Requests | Rate limiting |
| 500 | Internal Server Error | Service issue |

### Error Response Format

```json
{
  "error": {
    "code": "InvalidRequestParameter",
    "message": "The request parameter 'search' is invalid.",
    "details": [
      {
        "code": "InvalidSyntax",
        "message": "Syntax error in search expression."
      }
    ]
  }
}
```

### Debugging Tips

1. **Check URL Encoding**: Ensure special characters are properly encoded
2. **Validate API Key**: Test with a simple request first
3. **Check Index Name**: Verify the index exists and is spelled correctly
4. **Test Incrementally**: Start with simple queries and add complexity
5. **Use Browser Dev Tools**: Inspect network requests and responses

### Common Issues

1. **"Index not found" (404)**
   - Verify index name in URL
   - Check if index exists in your search service

2. **"Unauthorized" (401)**
   - Check API key is correct
   - Ensure API key has query permissions

3. **"Bad Request" (400)**
   - Check query syntax
   - Verify OData filter expressions
   - Ensure proper URL encoding

4. **No results returned**
   - Check if index contains data
   - Try broader search terms
   - Verify field names in filters

## 📖 Additional Resources

- [Azure AI Search REST API Reference](https://docs.microsoft.com/en-us/rest/api/searchservice/)
- [OData Filter Expression Syntax](https://docs.microsoft.com/en-us/azure/search/search-query-odata-filter)
- [Simple Query Syntax](https://docs.microsoft.com/en-us/azure/search/query-simple-syntax)
- [Full Lucene Query Syntax](https://docs.microsoft.com/en-us/azure/search/query-lucene-syntax)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

## 🔗 Next Steps

1. **Practice with Real Data**: Apply these patterns to your own datasets
2. **Explore Advanced Features**: Move to Module 5 for advanced querying
3. **Build Applications**: Integrate these REST calls into your applications
4. **Performance Tuning**: Learn about search optimization and analytics
5. **Security**: Implement proper authentication and authorization

## 🌐 Cross-Platform Usage

These REST API examples work with any programming language or tool that can make HTTP requests:

- **JavaScript/Node.js**: fetch, axios, request
- **Python**: requests, urllib, httpx
- **C#**: HttpClient, RestSharp
- **Java**: OkHttp, Apache HttpClient
- **PHP**: cURL, Guzzle
- **Ruby**: Net::HTTP, HTTParty
- **Go**: net/http
- **Rust**: reqwest

Happy querying! 🌐