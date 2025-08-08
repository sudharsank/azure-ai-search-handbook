# Comprehensive Troubleshooting Guide

[Go to top](#comprehensive-troubleshooting-guide)

## Connection and Network Issues

### Service Not Found Errors
**Symptoms**:

    - HTTP 404 errors when accessing service endpoint
    - "Service not found" or "Resource not found" messages
    - DNS resolution failures

**Diagnostic Steps**:

1. **Verify service name and URL**:
   ```bash
   # Test DNS resolution
   nslookup your-service-name.search.windows.net
   
   # Test HTTP connectivity
   curl -I https://your-service-name.search.windows.net
   ```

2. **Check service status in Azure portal**:

    - Navigate to your search service
    - Verify "Status" shows as "Running"
    - Check "Activity log" for any deployment issues

3. **Validate service configuration**:
   ```python
   # Test service accessibility
   import requests
   
   endpoint = "https://your-service-name.search.windows.net"
   response = requests.get(f"{endpoint}?api-version=2023-11-01")
   print(f"Status: {response.status_code}")
   print(f"Response: {response.text}")
   ```

**Common Solutions**:

    - Ensure service name is spelled correctly and matches Azure portal
    - Verify service has completed deployment (can take 2-15 minutes)
    - Check if service was accidentally deleted or moved to different resource group
    - Confirm you're using the correct Azure subscription

[Go to top](#comprehensive-troubleshooting-guide)

### Network Connectivity Problems
**Symptoms**:

    - Connection timeouts
    - "Connection refused" errors
    - Intermittent connectivity issues

**Diagnostic Steps**:

1. **Test network connectivity**:
   ```bash
   # Test basic connectivity
   telnet your-service-name.search.windows.net 443
   
   # Test with curl (verbose output)
   curl -v https://your-service-name.search.windows.net
   
   # Check for proxy issues
   curl --proxy-insecure https://your-service-name.search.windows.net
   ```

2. **Check firewall and proxy settings**:

    - Verify corporate firewall allows HTTPS traffic to *.search.windows.net
    - Check proxy configuration if behind corporate network
    - Test from different network (mobile hotspot) to isolate network issues

3. **Validate IP restrictions**:
   ```python
   # Check current IP address
   import requests
   current_ip = requests.get('https://api.ipify.org').text
   print(f"Current IP: {current_ip}")
   ```

**Common Solutions**:

    - Add your IP address to service firewall rules
    - Configure proxy settings in your application
    - Use private endpoints for internal network access
    - Check with network administrator about firewall rules

[Go to top](#comprehensive-troubleshooting-guide)

## Authentication and Authorization Issues

### API Key Authentication Errors
**Symptoms**:

    - HTTP 401 "Unauthorized" errors
    - HTTP 403 "Forbidden" errors
    - "Access denied" messages

**Diagnostic Steps**:
1. **Verify API key format and validity**:
   ```python
   # Test API key format (should be 32 characters)
   api_key = "your-api-key"
   print(f"Key length: {len(api_key)}")
   print(f"Key format valid: {len(api_key) == 32 and api_key.isalnum()}")
   ```

2. **Test different key types**:
   ```python
   from azure.search.documents.indexes import SearchIndexClient
   from azure.core.credentials import AzureKeyCredential
   
   # Test admin key
   try:
       admin_client = SearchIndexClient(
           endpoint="https://your-service.search.windows.net",
           credential=AzureKeyCredential("your-admin-key")
       )
       stats = admin_client.get_service_statistics()
       print("✅ Admin key works")
   except Exception as e:
       print(f"❌ Admin key failed: {e}")
   
   # Test query key
   try:
       query_client = SearchClient(
           endpoint="https://your-service.search.windows.net",
           index_name="existing-index-name",
           credential=AzureKeyCredential("your-query-key")
       )
       # Query keys can't access service stats, so try a search
       results = query_client.search("*")
       print("✅ Query key works")
   except Exception as e:
       print(f"❌ Query key failed: {e}")
   ```

3. **Check key permissions and scope**:

    - Admin keys: Full service access
    - Query keys: Read-only access to search operations
    - Verify you're using the correct key type for your operation

**Common Solutions**:

    - Regenerate API keys if they appear corrupted
    - Ensure you're copying the complete key without extra spaces
    - Use admin keys for index management operations
    - Use query keys only for search operations
    - Check if keys were recently rotated

[Go to top](#comprehensive-troubleshooting-guide)

### Azure AD Authentication Issues
**Symptoms**:

    - Token acquisition failures
    - "Invalid audience" errors
    - Permission denied with valid Azure AD credentials

**Diagnostic Steps**:

1. **Verify Azure AD configuration**:
   ```python
   from azure.identity import DefaultAzureCredential
   from azure.search.documents.indexes import SearchIndexClient
   
   try:
       credential = DefaultAzureCredential()
       # Test token acquisition
       token = credential.get_token("https://search.azure.com/.default")
       print(f"✅ Token acquired: {token.token[:20]}...")
   except Exception as e:
       print(f"❌ Token acquisition failed: {e}")
   ```

2. **Check role assignments**:
   ```bash
   # List role assignments for the search service
   az role assignment list \
     --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Search/searchServices/{service-name}" \
     --output table
   ```

3. **Validate service principal configuration**:
   ```python
   from azure.identity import ClientSecretCredential
   
   credential = ClientSecretCredential(
       tenant_id="your-tenant-id",
       client_id="your-client-id",
       client_secret="your-client-secret"
   )
   
   try:
       token = credential.get_token("https://search.azure.com/.default")
       print("✅ Service principal authentication successful")
   except Exception as e:
       print(f"❌ Service principal authentication failed: {e}")
   ```

**Common Solutions**:

    - Assign appropriate roles (Search Index Data Reader/Contributor)
    - Verify tenant ID, client ID, and client secret are correct
    - Check if multi-factor authentication is required
    - Ensure service principal has not expired
    - Validate redirect URIs for interactive authentication

[Go to top](#comprehensive-troubleshooting-guide)

## Service Quota and Limit Issues

### Storage Quota Exceeded
**Symptoms**:

    - "Storage quota exceeded" errors during indexing
    - Unable to add new documents
    - Indexing operations fail with quota messages

**Diagnostic Steps**:
1. **Check current storage usage**:
   ```python
   from azure.search.documents.indexes import SearchIndexClient
   
   index_client = SearchIndexClient(endpoint, credential)
   stats = index_client.get_service_statistics()
   
   print(f"Storage used: {stats['storage_size']} bytes")
   print(f"Document count: {stats['document_count']}")
   print(f"Index count: {stats['index_count']}")
   ```

2. **Analyze storage by index**:
   ```python
   indexes = index_client.list_indexes()
   for index in indexes:
       index_stats = index_client.get_index_statistics(index.name)
       print(f"Index '{index.name}': {index_stats['storage_size']} bytes, {index_stats['document_count']} docs")
   ```

**Common Solutions**:

    - Delete unused indexes or documents
    - Upgrade to higher service tier
    - Optimize document size by removing unnecessary fields
    - Use more efficient field types (e.g., Collection(Edm.String) instead of multiple string fields)
    - Implement data retention policies

[Go to top](#comprehensive-troubleshooting-guide)

### Request Rate Limiting
**Symptoms**:

    - HTTP 429 "Too Many Requests" errors
    - Throttling messages in responses
    - Slow response times during peak usage

**Diagnostic Steps**:
1. **Monitor request patterns**:
   ```python
   import time
   import requests
   
   # Test request rate limits
   for i in range(100):
       start_time = time.time()
       response = requests.get(f"{endpoint}/indexes?api-version=2023-11-01", 
                             headers={"api-key": api_key})
       end_time = time.time()
       
       print(f"Request {i}: Status {response.status_code}, Time: {end_time - start_time:.2f}s")
       
       if response.status_code == 429:
           print(f"Rate limited at request {i}")
           break
   ```

2. **Check service tier limits**:

    - Free: 3 requests per second
    - Basic: 15 requests per second
    - Standard: Higher limits based on service units

**Common Solutions**:

    - Implement exponential backoff retry logic
    - Batch multiple operations into single requests
    - Upgrade to higher service tier for increased limits
    - Distribute load across multiple time periods
    - Use indexers for bulk data operations instead of individual document uploads

[Go to top](#comprehensive-troubleshooting-guide)

## Performance and Latency Issues

### Slow Query Performance
**Symptoms**:

    - Search queries taking longer than expected
    - Timeouts on complex queries
    - Poor user experience due to slow responses

**Diagnostic Steps**:
1. **Analyze query complexity**:
   ```python
   # Test different query types
   simple_query = search_client.search("test")
   complex_query = search_client.search(
       search_text="test",
       facets=["category", "brand", "price_range"],
       filter="price gt 100 and category eq 'electronics'",
       order_by=["rating desc", "price asc"]
   )
   
   # Measure response times
   import time
   start = time.time()
   results = list(simple_query)
   simple_time = time.time() - start
   
   start = time.time()
   results = list(complex_query)
   complex_time = time.time() - start
   
   print(f"Simple query: {simple_time:.2f}s")
   print(f"Complex query: {complex_time:.2f}s")
   ```

2. **Check index design**:
   ```python
   # Review index schema for optimization opportunities
   index = index_client.get_index("your-index-name")
   
   for field in index.fields:
       print(f"Field: {field.name}")
       print(f"  Type: {field.type}")
       print(f"  Searchable: {field.searchable}")
       print(f"  Filterable: {field.filterable}")
       print(f"  Sortable: {field.sortable}")
       print(f"  Facetable: {field.facetable}")
   ```

**Common Solutions**:

    - Add more replicas to handle query load
    - Optimize index schema (remove unnecessary attributes)
    - Use appropriate field types for your data
    - Implement result caching in your application
    - Use filters to reduce result set size
    - Consider using search profiles for custom scoring

[Go to top](#comprehensive-troubleshooting-guide)

### Indexing Performance Issues
**Symptoms**:

    - Slow document upload speeds
    - Indexing operations timing out
    - High latency during bulk operations

**Diagnostic Steps**:
1. **Test batch sizes**:
   ```python
   import time
   
   # Test different batch sizes
   batch_sizes = [10, 50, 100, 500, 1000]
   
   for batch_size in batch_sizes:
       documents = [{"id": str(i), "content": f"Document {i}"} 
                   for i in range(batch_size)]
       
       start_time = time.time()
       result = search_client.upload_documents(documents)
       end_time = time.time()
       
       print(f"Batch size {batch_size}: {end_time - start_time:.2f}s")
   ```

2. **Monitor indexing progress**:
   ```python
   # Check indexer status
   indexer_client = SearchIndexerClient(endpoint, credential)
   indexer_status = indexer_client.get_indexer_status("your-indexer-name")
   
   print(f"Status: {indexer_status.status}")
   print(f"Last result: {indexer_status.last_result}")
   print(f"Execution history: {len(indexer_status.execution_history)} runs")
   ```

**Common Solutions**:

    - Increase partition count for more indexing capacity
    - Optimize batch sizes (typically 100-1000 documents)
    - Use merge operations instead of upload for updates
    - Implement parallel indexing with multiple threads
    - Schedule indexing during off-peak hours
    - Use indexers for large-scale data ingestion

[Go to top](#comprehensive-troubleshooting-guide)

## SDK and Development Issues

### Python SDK Issues
**Symptoms**:

    - Import errors or module not found
    - Version compatibility issues
    - Unexpected behavior with SDK methods

**Diagnostic Steps**:
1. **Verify SDK installation and version**:
   ```bash
   pip show azure-search-documents
   pip list | grep azure
   ```

2. **Test SDK functionality**:
   ```python
   # Test basic SDK imports
   try:
       from azure.search.documents import SearchClient
       from azure.search.documents.indexes import SearchIndexClient
       from azure.core.credentials import AzureKeyCredential
       print("✅ All imports successful")
   except ImportError as e:
       print(f"❌ Import error: {e}")
   
   # Test SDK version compatibility
   import azure.search.documents
   print(f"SDK version: {azure.search.documents.__version__}")
   ```

**Common Solutions**:

    - Update to latest SDK version: `pip install --upgrade azure-search-documents`
    - Check Python version compatibility (3.7+ required)
    - Resolve dependency conflicts with `pip check`
    - Use virtual environments to isolate dependencies
    - Refer to SDK documentation for breaking changes

[Go to top](#comprehensive-troubleshooting-guide)

## Monitoring and Diagnostics

### Enable Comprehensive Logging
```python
import logging
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.search.documents import SearchClient

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('azure.search')

# Configure client with logging
search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=credential,
    logging_enable=True
)
```

### Set Up Azure Monitor Integration
```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Azure Monitor
configure_azure_monitor(
    connection_string="your-application-insights-connection-string"
)

# Create tracer
tracer = trace.get_tracer(__name__)

# Trace search operations
with tracer.start_as_current_span("search_operation"):
    results = search_client.search("query")
```

[Go to top](#comprehensive-troubleshooting-guide)

## Emergency Recovery Procedures

### Service Outage Response
1. **Check Azure Service Health**: Monitor Azure status page for known issues
2. **Implement fallback mechanisms**: Use cached results or alternative search providers
3. **Contact Azure Support**: For critical production issues
4. **Document incidents**: Track issues for post-mortem analysis

### Data Recovery
1. **Backup strategies**: Regularly export index data
2. **Disaster recovery**: Plan for service recreation in different regions
3. **Version control**: Maintain index schemas and configuration in source control
4. **Testing procedures**: Regularly test backup and recovery processes

[Go to top](#comprehensive-troubleshooting-guide)