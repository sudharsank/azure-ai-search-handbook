# JavaScript Examples - Data Sources & Indexers

## Overview

This directory contains JavaScript/Node.js examples for working with Azure AI Search data sources and indexers using the `@azure/search-documents` SDK.

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
- Data source (SQL Database, Storage Account, or Cosmos DB)
- Appropriate permissions configured

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

# For SQL Database examples
SQL_CONNECTION_STRING=Server=tcp:your-server.database.windows.net,1433;Database=your-db;User ID=your-user;Password=your-password;

# For Blob Storage examples
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net

# For Cosmos DB examples
COSMOS_CONNECTION_STRING=AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;Database=your-database
```

### 3. Verify Setup
Run the setup verification script:
```bash
node verify_setup.js
```

## Examples

### 01 - Azure SQL Indexer
**File:** `01_azure_sql_indexer.js`

Demonstrates:
- Creating SQL data source with change tracking
- Configuring indexer for relational data
- Field mapping for complex structures
- Monitoring execution status

### 02 - Blob Storage Indexer
**File:** `02_blob_storage_indexer.js`

Demonstrates:
- Creating blob storage data source
- Processing various document formats
- Metadata extraction and content processing
- LastModified change detection

### 03 - Cosmos DB Indexer
**File:** `03_cosmos_db_indexer.js`

Demonstrates:
- Creating Cosmos DB data source
- JSON document processing
- Change feed integration
- Partition key optimization

### 04 - Change Detection
**File:** `04_change_detection.js`

Demonstrates:
- Different change detection policies
- High water mark implementation
- Incremental update strategies
- Custom change detection logic

### 05 - Indexer Scheduling
**File:** `05_indexer_scheduling.js`

Demonstrates:
- Configuring indexer schedules
- Automated execution patterns
- Schedule management APIs
- Monitoring scheduled runs

### 06 - Field Mappings
**File:** `06_field_mappings.js`

Demonstrates:
- Basic and complex field mappings
- Built-in mapping functions
- Output field mappings
- Data transformation techniques

### 07 - Error Handling
**File:** `07_error_handling.js`

Demonstrates:
- Robust error handling patterns
- Retry logic implementation
- Error threshold configuration
- Logging and monitoring

### 08 - Monitoring & Optimization
**File:** `08_monitoring_optimization.js`

Demonstrates:
- Performance metrics collection and analysis
- Indexer health monitoring
- Optimization strategies implementation
- Batch size and configuration tuning
- Resource usage monitoring

## Running Examples

### Individual Examples
```bash
node 01_azure_sql_indexer.js
node 02_blob_storage_indexer.js
# ... etc
```

### All Examples
```bash
node run_all_examples.js
```

## Common Patterns

### Authentication
```javascript
const { SearchIndexClient, SearchIndexerClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');

// Using API key
const credential = new AzureKeyCredential(apiKey);
const indexerClient = new SearchIndexerClient(endpoint, credential);

// Using managed identity
const { DefaultAzureCredential } = require('@azure/identity');
const credential = new DefaultAzureCredential();
const indexerClient = new SearchIndexerClient(endpoint, credential);
```

### Error Handling
```javascript
try {
    await indexerClient.createIndexer(indexer);
    console.log('Indexer created successfully');
} catch (error) {
    console.error('Error creating indexer:', error.message);
    // Handle specific error scenarios
}
```

### Monitoring
```javascript
async function monitorIndexerExecution(indexerName) {
    const status = await indexerClient.getIndexerStatus(indexerName);
    console.log(`Status: ${status.status}`);
    console.log(`Items processed: ${status.lastResult?.itemCount || 0}`);
    console.log(`Errors: ${status.lastResult?.errors?.length || 0}`);
}
```

## Configuration Management

### Using Environment Variables
```javascript
require('dotenv').config();

const config = {
    endpoint: process.env.SEARCH_ENDPOINT,
    apiKey: process.env.SEARCH_API_KEY,
    sqlConnectionString: process.env.SQL_CONNECTION_STRING
};
```

### Configuration Class
```javascript
class SearchConfig {
    constructor() {
        this.endpoint = process.env.SEARCH_ENDPOINT;
        this.apiKey = process.env.SEARCH_API_KEY;
        this.sqlConnection = process.env.SQL_CONNECTION_STRING;
    }
    
    validate() {
        const required = [this.endpoint, this.apiKey];
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

### Test Coverage
```bash
npm run test:coverage
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
    console.log(`Creating indexer: ${indexerName}`);
    console.log(`Configuration:`, indexerDefinition);
}
```

## Best Practices

### Async/Await Usage
```javascript
// Use async/await for better error handling
async function createIndexer() {
    try {
        const result = await indexerClient.createIndexer(indexer);
        return result;
    } catch (error) {
        console.error('Failed to create indexer:', error);
        throw error;
    }
}
```

### Error Recovery
```javascript
async function createIndexerWithRetry(indexer, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await indexerClient.createIndexer(indexer);
        } catch (error) {
            if (attempt === maxRetries) throw error;
            
            const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}
```

## Troubleshooting

### Common Issues
1. **Authentication failures**: Check API keys and permissions
2. **Connection errors**: Verify network connectivity and firewall rules
3. **Schema mismatches**: Ensure field mappings are correct
4. **Performance issues**: Optimize batch sizes and queries

### Debug Tools
```javascript
function debugIndexerStatus(indexerName) {
    return indexerClient.getIndexerStatus(indexerName)
        .then(status => {
            console.log(`Indexer: ${indexerName}`);
            console.log(`Status: ${status.status}`);
            console.log(`Last run: ${status.lastResult?.startTime}`);
            
            if (status.lastResult?.errors?.length > 0) {
                console.log('Errors:');
                status.lastResult.errors.forEach(error => {
                    console.log(`  - ${error.errorMessage}`);
                });
            }
        });
}
```

## Additional Resources

- [Azure Search Documents SDK Documentation](https://docs.microsoft.com/javascript/api/@azure/search-documents/)
- [JavaScript SDK Samples](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/search/search-documents/samples)
- [Azure AI Search REST API Reference](https://docs.microsoft.com/rest/api/searchservice/)

## Next Steps

1. Run the basic examples to understand core concepts
2. Modify examples for your specific data sources
3. Implement error handling and monitoring
4. Explore advanced features in intermediate modules