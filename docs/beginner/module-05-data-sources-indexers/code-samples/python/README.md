# Python Examples - Data Sources & Indexers

## Overview

This directory contains Python examples for working with Azure AI Search data sources and indexers using the `azure-search-documents` SDK.

## Prerequisites

### Python Environment
- Python 3.7 or higher
- pip package manager

### Required Packages
```bash
pip install azure-search-documents
pip install azure-identity
pip install python-dotenv
```

### Azure Resources
- Azure AI Search service
- Data source (SQL Database, Storage Account, or Cosmos DB)
- Appropriate permissions configured

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
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
python verify_setup.py
```

## Examples

### 01 - Azure SQL Indexer
**File:** `01_azure_sql_indexer.py`

Demonstrates:
- Creating SQL data source
- Configuring indexer for SQL data
- Setting up change tracking
- Running and monitoring indexer

### 02 - Blob Storage Indexer
**File:** `02_blob_storage_indexer.py`

Demonstrates:
- Creating blob storage data source
- Document content extraction
- Metadata processing
- Change detection with LastModified

### 03 - Cosmos DB Indexer
**File:** `03_cosmos_db_indexer.py`

Demonstrates:
- Creating Cosmos DB data source
- JSON document processing
- Change feed integration
- Partition key handling

### 04 - Change Detection
**File:** `04_change_detection.py`

Demonstrates:
- Different change detection policies
- High water mark implementation
- Incremental update strategies
- Custom change detection logic

### 05 - Indexer Scheduling
**File:** `05_indexer_scheduling.py`

Demonstrates:
- Configuring indexer schedules
- Automated execution
- Schedule management
- Monitoring scheduled runs

### 06 - Field Mappings
**File:** `06_field_mappings.py`

Demonstrates:
- Basic field mappings
- Complex data transformations
- Built-in mapping functions
- Output field mappings

### 07 - Error Handling
**File:** `07_error_handling.py`

Demonstrates:
- Robust error handling patterns
- Retry logic implementation
- Error threshold configuration
- Logging and monitoring

### 08 - Performance Monitoring & Optimization
**File:** `08_monitoring_optimization.py`

Demonstrates:
- Performance metrics collection and analysis
- Indexer health monitoring
- Optimization strategies implementation
- Performance trend analysis
- Resource usage optimization

## Running Examples

### Individual Examples
```bash
python 01_azure_sql_indexer.py
python 02_blob_storage_indexer.py
# ... etc
```

### All Examples
```bash
python run_all_examples.py
```

### Interactive Mode
```bash
python -i interactive_examples.py
```

## Common Patterns

### Authentication
```python
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential

# Using API key
credential = AzureKeyCredential(api_key)
indexer_client = SearchIndexerClient(endpoint, credential)

# Using managed identity
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
indexer_client = SearchIndexerClient(endpoint, credential)
```

### Error Handling
```python
from azure.core.exceptions import HttpResponseError

try:
    indexer_client.create_indexer(indexer)
except HttpResponseError as e:
    print(f"Error creating indexer: {e.message}")
    # Handle specific error scenarios
```

### Monitoring
```python
def monitor_indexer_execution(indexer_name):
    status = indexer_client.get_indexer_status(indexer_name)
    print(f"Status: {status.status}")
    print(f"Items processed: {status.last_result.item_count}")
    print(f"Errors: {len(status.last_result.errors)}")
```

## Configuration Management

### Using Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()

SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
```

### Configuration Class
```python
class SearchConfig:
    def __init__(self):
        self.endpoint = os.getenv('SEARCH_ENDPOINT')
        self.api_key = os.getenv('SEARCH_API_KEY')
        self.sql_connection = os.getenv('SQL_CONNECTION_STRING')
        
    def validate(self):
        required = [self.endpoint, self.api_key]
        if not all(required):
            raise ValueError("Missing required configuration")
```

## Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Test Coverage
```bash
python -m pytest --cov=. tests/
```

## Debugging

### Enable Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('azure.search.documents')
```

### Debug Mode
```python
# Set debug flag for detailed output
DEBUG = True

if DEBUG:
    print(f"Creating indexer: {indexer_name}")
    print(f"Configuration: {indexer_definition}")
```

## Best Practices

### Resource Management
```python
# Use context managers when possible
with SearchIndexerClient(endpoint, credential) as client:
    # Perform operations
    pass
```

### Async Operations
```python
from azure.search.documents.indexes.aio import SearchIndexerClient

async def create_indexer_async():
    async with SearchIndexerClient(endpoint, credential) as client:
        await client.create_indexer(indexer)
```

### Error Recovery
```python
def create_indexer_with_retry(indexer, max_retries=3):
    for attempt in range(max_retries):
        try:
            return indexer_client.create_indexer(indexer)
        except HttpResponseError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Troubleshooting

### Common Issues
1. **Authentication failures**: Check API keys and permissions
2. **Connection errors**: Verify network connectivity and firewall rules
3. **Schema mismatches**: Ensure field mappings are correct
4. **Performance issues**: Optimize batch sizes and queries

### Debug Tools
```python
def debug_indexer_status(indexer_name):
    status = indexer_client.get_indexer_status(indexer_name)
    
    print(f"Indexer: {indexer_name}")
    print(f"Status: {status.status}")
    print(f"Last run: {status.last_result.start_time}")
    
    if status.last_result.errors:
        print("Errors:")
        for error in status.last_result.errors:
            print(f"  - {error.error_message}")
```

## Additional Resources

- [Azure Search Documents SDK Documentation](https://docs.microsoft.com/python/api/azure-search-documents/)
- [Python SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents/samples)
- [Azure AI Search REST API Reference](https://docs.microsoft.com/rest/api/searchservice/)

## Next Steps

1. Run the basic examples to understand core concepts
2. Modify examples for your specific data sources
3. Implement error handling and monitoring
4. Explore advanced features in intermediate modules