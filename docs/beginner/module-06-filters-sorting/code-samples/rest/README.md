# REST API Examples - Filters & Sorting

## Overview

This directory contains REST API examples for implementing filters and sorting in Azure AI Search using direct HTTP calls. These examples demonstrate various filtering techniques, sorting strategies, and can be used with any programming language or HTTP client.

## Prerequisites

### HTTP Client
- Any REST client (Postman, Insomnia, curl, etc.)
- Or any programming language with HTTP support

### Azure Resources
- Azure AI Search service
- Search index with filterable and sortable fields
- Admin API key for write operations

## Setup

### 1. Configure Variables
Set these variables in your HTTP client or environment:

```bash
# Azure AI Search Configuration
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_API_KEY=your-admin-api-key
INDEX_NAME=your-index-name
API_VERSION=2023-11-01
```

### 2. Test Connection
Test your connection with a simple search:

```http
GET {{SEARCH_ENDPOINT}}/indexes/{{INDEX_NAME}}/docs?api-version={{API_VERSION}}
Content-Type: application/json
api-key: {{SEARCH_API_KEY}}
```

## Examples

### 01 - Basic Filters
**File:** `01_basic_filters.http`

Demonstrates:
- Equality filters (`eq`, `ne`)
- Comparison filters (`gt`, `ge`, `lt`, `le`)
- Boolean logic combinations (`and`, `or`, `not`)
- Null value handling

### 02 - Range Filters
**File:** `02_range_filters.http`

Demonstrates:
- Numeric range filtering
- Date range filtering
- Price range implementations
- Performance optimization techniques

### 03 - String Filters
**File:** `03_string_filters.http`

Demonstrates:
- Text matching with `startswith`, `endswith`, `contains`
- Case sensitivity handling
- Pattern matching techniques
- Multi-language considerations

### 04 - Date Filters
**File:** `04_date_filters.http`

Demonstrates:
- Date range filtering
- Relative date calculations
- Time zone handling
- Date format considerations

### 05 - Geographic Filters
**File:** `05_geographic_filters.http`

Demonstrates:
- Distance-based filtering
- Bounding box filtering
- Location proximity searches
- Geographic sorting by distance

### 06 - Sorting Operations
**File:** `06_sorting_operations.http`

Demonstrates:
- Single field sorting
- Multi-field sorting
- Custom sort orders
- Performance optimization

### 07 - Complex Filters
**File:** `07_complex_filters.http`

Demonstrates:
- Collection filtering with `any()` and `all()`
- Nested field filtering
- Combined filter and search queries
- Advanced logical expressions

### 08 - Performance Tips
**File:** `08_performance_tips.http`

Demonstrates:
- Filter optimization strategies
- Index design considerations
- Query performance monitoring
- Caching strategies

## HTTP Client Setup

### Visual Studio Code with REST Client Extension

1. Install the "REST Client" extension
2. Create `.http` files with your requests
3. Use variables for configuration:

```http
### Variables
@searchEndpoint = https://your-search-service.search.windows.net
@apiKey = your-admin-api-key
@indexName = your-index-name
@apiVersion = 2023-11-01

### Basic Search
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version={{apiVersion}}
Content-Type: application/json
api-key: {{apiKey}}
```

### Postman Setup

1. Create a new collection
2. Set collection variables:
   - `searchEndpoint`: Your search service URL
   - `apiKey`: Your admin API key
   - `indexName`: Your index name
   - `apiVersion`: 2023-11-01

3. Add requests using these variables

### curl Examples

```bash
# Basic search with filter
curl -X GET \
  "https://your-search-service.search.windows.net/indexes/your-index/docs?api-version=2023-11-01&search=*&\$filter=category eq 'Electronics'" \
  -H "Content-Type: application/json" \
  -H "api-key: your-admin-api-key"

# Search with sorting
curl -X GET \
  "https://your-search-service.search.windows.net/indexes/your-index/docs?api-version=2023-11-01&search=*&\$orderby=price asc" \
  -H "Content-Type: application/json" \
  -H "api-key: your-admin-api-key"
```

## Common Query Parameters

### Basic Parameters
- `search`: Search text (`*` for all documents)
- `$filter`: OData filter expression
- `$orderby`: Sort order specification
- `$top`: Number of results to return
- `$skip`: Number of results to skip (pagination)
- `$select`: Fields to include in results
- `$count`: Include total count in response

### Filter Examples
```http
# Equality filter
$filter=category eq 'Electronics'

# Range filter
$filter=price ge 100 and price le 500

# String function
$filter=startswith(name, 'iPhone')

# Complex combination
$filter=(category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.0)
```

### Sorting Examples
```http
# Single field ascending
$orderby=price asc

# Single field descending
$orderby=rating desc

# Multiple fields
$orderby=category asc, rating desc, price asc

# Geographic distance
$orderby=geo.distance(location, geography'POINT(-122.131577 47.678581)')
```

## Response Format

### Successful Response
```json
{
  "@odata.context": "https://your-search-service.search.windows.net/indexes('your-index')/$metadata#docs(*)",
  "@odata.count": 150,
  "value": [
    {
      "@search.score": 1.0,
      "id": "1",
      "name": "Product Name",
      "category": "Electronics",
      "price": 299.99,
      "rating": 4.5
    }
  ]
}
```

### Error Response
```json
{
  "error": {
    "code": "InvalidRequestParameter",
    "message": "The request parameter '$filter' is invalid.",
    "details": [
      {
        "code": "InvalidODataExpression",
        "message": "Syntax error in OData expression 'category eq Electronics'. Expected a string literal."
      }
    ]
  }
}
```

## Best Practices

### URL Encoding
Always URL encode special characters in query parameters:
- Space: `%20`
- Single quote: `%27`
- Ampersand: `%26`

### Error Handling
```http
### Test invalid filter
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version={{apiVersion}}&search=*&$filter=invalid filter
Content-Type: application/json
api-key: {{apiKey}}

# Expected: 400 Bad Request with error details
```

### Performance Testing
```http
### Performance test with timing
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?api-version={{apiVersion}}&search=*&$filter=category eq 'Electronics'&$top=100
Content-Type: application/json
api-key: {{apiKey}}

# Check response time in client
```

## Authentication

### API Key Authentication
```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs
Content-Type: application/json
api-key: {{apiKey}}
```

### Azure AD Authentication
```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs
Content-Type: application/json
Authorization: Bearer {{accessToken}}
```

## Debugging Tips

### 1. Validate Filter Syntax
Test filters incrementally:
```http
# Start simple
$filter=category eq 'Electronics'

# Add complexity gradually
$filter=category eq 'Electronics' and price gt 100
```

### 2. Check Field Names
Verify field names match your index schema:
```http
GET {{searchEndpoint}}/indexes/{{indexName}}?api-version={{apiVersion}}
api-key: {{apiKey}}
```

### 3. Test with Small Result Sets
Use `$top=5` for faster testing:
```http
GET {{searchEndpoint}}/indexes/{{indexName}}/docs?$top=5
```

### 4. Use $select for Faster Responses
Only request needed fields:
```http
$select=id,name,price,rating
```

## Sample Data Requirements

For best results with these examples, your index should include:

### Required Fields
- `id` (Edm.String, key)
- `name` (Edm.String, searchable, filterable)
- `category` (Edm.String, filterable, facetable)
- `price` (Edm.Double, filterable, sortable)
- `rating` (Edm.Double, filterable, sortable)
- `inStock` (Edm.Boolean, filterable)

### Optional Fields
- `brand` (Edm.String, filterable, facetable)
- `description` (Edm.String, searchable)
- `createdDate` (Edm.DateTimeOffset, filterable, sortable)
- `location` (Edm.GeographyPoint, filterable, sortable)
- `tags` (Collection(Edm.String), filterable)

## Testing Workflow

1. **Start Simple**: Test basic connectivity
2. **Add Filters**: Test individual filter types
3. **Combine Filters**: Test logical combinations
4. **Add Sorting**: Test sort operations
5. **Optimize**: Test performance with larger datasets
6. **Error Cases**: Test invalid filters and edge cases

## Additional Resources

- [Azure AI Search REST API Reference](https://docs.microsoft.com/rest/api/searchservice/)
- [OData Filter Syntax](https://docs.microsoft.com/azure/search/search-query-odata-filter)
- [OData OrderBy Syntax](https://docs.microsoft.com/azure/search/search-query-odata-orderby)
- [Query Parameters Reference](https://docs.microsoft.com/azure/search/search-query-overview)

## Next Steps

1. Set up your HTTP client with the provided examples
2. Test basic connectivity and authentication
3. Work through the examples in order
4. Adapt the examples for your specific data and use cases
5. Implement error handling and performance monitoring