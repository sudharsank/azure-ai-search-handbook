# REST API Examples - Data Sources & Indexers

## Overview

This directory contains REST API examples for working with Azure AI Search data sources and indexers using direct HTTP calls. These examples demonstrate the raw API interactions and can be used with any HTTP client.

## Prerequisites

### Tools
- REST client (Postman, VS Code REST Client, curl, or similar)
- Azure AI Search service
- Data source (SQL Database, Storage Account, or Cosmos DB)
- Admin API key or appropriate permissions

### Environment Variables
Set up the following environment variables or replace them in the examples:
```bash
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-admin-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net

# For SQL Database examples
SQL_CONNECTION_STRING=Server=tcp:your-server.database.windows.net,1433;Database=your-db;User ID=your-user;Password=your-password;

# For Blob Storage examples
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net

# For Cosmos DB examples
COSMOS_CONNECTION_STRING=AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;Database=your-database
```

## Examples

### 01 - Azure SQL Indexer
**File:** `01_azure_sql_indexer.http`

Demonstrates:
- Creating SQL data source with change tracking
- Configuring indexer for relational data
- Field mapping for complex structures
- Monitoring execution status

### 02 - Blob Storage Indexer
**File:** `02_blob_storage_indexer.http`

Demonstrates:
- Creating blob storage data source
- Processing various document formats
- Metadata extraction and content processing
- LastModified change detection

### 03 - Cosmos DB Indexer
**File:** `03_cosmos_db_indexer.http`

Demonstrates:
- Creating Cosmos DB data source
- JSON document processing
- Change feed integration
- Partition key optimization

### 04 - Change Detection
**File:** `04_change_detection.http`

Demonstrates:
- Different change detection policies
- High water mark implementation
- Incremental update strategies
- Custom change detection logic

### 05 - Indexer Scheduling
**File:** `05_indexer_scheduling.http`

Demonstrates:
- Configuring indexer schedules
- Automated execution patterns
- Schedule management APIs
- Monitoring scheduled runs

### 06 - Field Mappings
**File:** `06_field_mappings.http`

Demonstrates:
- Basic and complex field mappings
- Built-in mapping functions
- Output field mappings
- Data transformation techniques

### 07 - Error Handling
**File:** `07_error_handling.http`

Demonstrates:
- Robust error handling patterns
- Error threshold configuration
- Monitoring error scenarios
- Recovery procedures

### 08 - Performance Monitoring & Optimization
**File:** `08_monitoring_optimization.http`

Demonstrates:
- Performance metrics collection and analysis
- Indexer health monitoring
- Optimization strategies implementation
- Batch size and configuration tuning
- Resource usage monitoring

## Using the Examples

### VS Code REST Client
1. Install the REST Client extension
2. Open any `.http` file
3. Click "Send Request" above each request
4. View responses in the output panel

### Postman
1. Import the requests into Postman
2. Set up environment variables
3. Execute requests individually
4. View responses and status codes

### curl
Copy the curl commands from the examples and run them in your terminal.

## Common Headers

All requests require these headers:
```http
Content-Type: application/json
api-key: {{SEARCH_API_KEY}}
```

## API Endpoints

### Data Sources
- **Create/Update**: `PUT /datasources/{name}?api-version=2024-07-01`
- **Get**: `GET /datasources/{name}?api-version=2024-07-01`
- **List**: `GET /datasources?api-version=2024-07-01`
- **Delete**: `DELETE /datasources/{name}?api-version=2024-07-01`

### Indexes
- **Create/Update**: `PUT /indexes/{name}?api-version=2024-07-01`
- **Get**: `GET /indexes/{name}?api-version=2024-07-01`
- **List**: `GET /indexes?api-version=2024-07-01`
- **Delete**: `DELETE /indexes/{name}?api-version=2024-07-01`

### Indexers
- **Create/Update**: `PUT /indexers/{name}?api-version=2024-07-01`
- **Get**: `GET /indexers/{name}?api-version=2024-07-01`
- **List**: `GET /indexers?api-version=2024-07-01`
- **Delete**: `DELETE /indexers/{name}?api-version=2024-07-01`
- **Run**: `POST /indexers/{name}/run?api-version=2024-07-01`
- **Reset**: `POST /indexers/{name}/reset?api-version=2024-07-01`
- **Status**: `GET /indexers/{name}/status?api-version=2024-07-01`

## Response Codes

### Success Codes
- **200 OK**: Request successful, resource returned
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned

### Error Codes
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists or conflict
- **422 Unprocessable Entity**: Request valid but cannot be processed

## Error Handling

### Common Error Response Format
```json
{
  "error": {
    "code": "InvalidRequestParameter",
    "message": "The request parameter 'fieldName' is invalid.",
    "details": [
      {
        "code": "FieldNotFound",
        "message": "Field 'invalidField' does not exist in the index."
      }
    ]
  }
}
```

### Retry Logic
For transient errors (5xx codes), implement exponential backoff:
1. Wait 1 second, retry
2. Wait 2 seconds, retry
3. Wait 4 seconds, retry
4. Give up after 3 attempts

## Testing Workflow

### 1. Setup Phase
```http
# Test service connectivity
GET {{SEARCH_ENDPOINT}}/servicestats?api-version=2024-07-01
api-key: {{SEARCH_API_KEY}}
```

### 2. Create Resources
```http
# Create data source
PUT {{SEARCH_ENDPOINT}}/datasources/test-datasource?api-version=2024-07-01
# Create index
PUT {{SEARCH_ENDPOINT}}/indexes/test-index?api-version=2024-07-01
# Create indexer
PUT {{SEARCH_ENDPOINT}}/indexers/test-indexer?api-version=2024-07-01
```

### 3. Execute and Monitor
```http
# Run indexer
POST {{SEARCH_ENDPOINT}}/indexers/test-indexer/run?api-version=2024-07-01
# Check status
GET {{SEARCH_ENDPOINT}}/indexers/test-indexer/status?api-version=2024-07-01
```

### 4. Cleanup
```http
# Delete resources in reverse order
DELETE {{SEARCH_ENDPOINT}}/indexers/test-indexer?api-version=2024-07-01
DELETE {{SEARCH_ENDPOINT}}/indexes/test-index?api-version=2024-07-01
DELETE {{SEARCH_ENDPOINT}}/datasources/test-datasource?api-version=2024-07-01
```

## Best Practices

### Security
- Never hardcode API keys in files
- Use environment variables or secure vaults
- Rotate API keys regularly
- Use query keys for read-only operations

### Performance
- Use appropriate batch sizes for indexers
- Monitor indexer execution times
- Implement proper error handling
- Use change detection for incremental updates

### Monitoring
- Check indexer status regularly
- Monitor error rates and patterns
- Set up alerts for failed executions
- Track performance metrics

## Troubleshooting

### Authentication Issues
```http
# Test API key validity
GET {{SEARCH_ENDPOINT}}/servicestats?api-version=2024-07-01
api-key: {{SEARCH_API_KEY}}
```

### Connection Issues
```http
# Test data source connection
POST {{SEARCH_ENDPOINT}}/datasources/test-connection?api-version=2024-07-01
Content-Type: application/json
api-key: {{SEARCH_API_KEY}}

{
  "connectionString": "your-connection-string",
  "type": "azuresql"
}
```

### Schema Validation
```http
# Validate index schema
PUT {{SEARCH_ENDPOINT}}/indexes/test-index?api-version=2024-07-01
Content-Type: application/json
api-key: {{SEARCH_API_KEY}}

{
  "name": "test-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true
    }
  ]
}
```

## Additional Resources

- [Azure AI Search REST API Reference](https://docs.microsoft.com/rest/api/searchservice/)
- [HTTP Status Codes](https://docs.microsoft.com/rest/api/searchservice/http-status-codes)
- [API Versioning](https://docs.microsoft.com/azure/search/search-api-versions)
- [Error Handling](https://docs.microsoft.com/azure/search/search-error-handling)

## Next Steps

1. Start with basic examples to understand API structure
2. Modify examples for your specific data sources
3. Implement error handling and monitoring
4. Explore advanced features and configurations