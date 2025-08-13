# Indexer Troubleshooting - Module 5: Data Sources & Indexers

## Common Indexer Issues

### Indexer Execution Failures

#### Issue: Indexer fails to start
**Symptoms:**
- Indexer status shows "Failed" immediately
- No documents processed
- Error in execution history

**Common Causes:**
- Invalid data source configuration
- Network connectivity issues
- Authentication failures
- Insufficient permissions

**Solutions:**
1. Verify data source connection
2. Check firewall and network settings
3. Validate authentication credentials
4. Review service tier limits

#### Issue: Indexer runs but processes no documents
**Symptoms:**
- Indexer status shows "Success"
- Zero documents indexed
- No errors reported

**Common Causes:**
- Empty data source
- Incorrect container/table specification
- Change detection policy issues
- Query filters excluding all data

**Solutions:**
1. Verify data exists in source
2. Check container/table names
3. Review change detection settings
4. Test source queries independently

### Field Mapping Issues

#### Issue: Fields not mapping correctly
**Symptoms:**
- Expected fields are empty in index
- Data appears in wrong fields
- Type conversion errors

**Common Causes:**
- Incorrect field names in mappings
- Data type mismatches
- Missing source fields
- Case sensitivity issues

**Solutions:**
1. Verify source field names
2. Check data type compatibility
3. Use explicit field mappings
4. Test with sample documents

#### Issue: Complex data not indexing
**Symptoms:**
- Nested objects not processed
- Arrays not handled correctly
- JSON structure flattened incorrectly

**Common Causes:**
- Missing output field mappings
- Incorrect complex type definitions
- Unsupported data structures

**Solutions:**
1. Use output field mappings for complex types
2. Define proper complex field structures
3. Flatten data at source if needed
4. Use built-in mapping functions

### Performance Issues

#### Issue: Slow indexer execution
**Symptoms:**
- Long execution times
- Timeouts during processing
- High resource utilization

**Common Causes:**
- Large batch sizes
- Complex field mappings
- Network latency
- Resource constraints

**Solutions:**
1. Optimize batch sizes
2. Simplify field mappings
3. Improve network connectivity
4. Scale up search service

#### Issue: Memory or timeout errors
**Symptoms:**
- Out of memory exceptions
- Request timeout errors
- Indexer stops mid-execution

**Common Causes:**
- Documents too large
- Batch size too high
- Insufficient service capacity
- Complex transformations

**Solutions:**
1. Reduce batch sizes
2. Split large documents
3. Upgrade service tier
4. Optimize transformations

## Error Code Reference

### HTTP 400 Errors

#### 400.1: Invalid Request
```json
{
  "error": {
    "code": "InvalidRequestParameter",
    "message": "The request parameter 'batchSize' is invalid."
  }
}
```
**Solution:** Check parameter values and formats

#### 400.2: Invalid Field Mapping
```json
{
  "error": {
    "code": "InvalidFieldMapping",
    "message": "Field mapping source field 'invalidField' does not exist."
  }
}
```
**Solution:** Verify source field names and structure

### HTTP 403 Errors

#### 403.1: Insufficient Permissions
```json
{
  "error": {
    "code": "Forbidden",
    "message": "The request is forbidden due to insufficient permissions."
  }
}
```
**Solution:** Check API key or managed identity permissions

#### 403.2: Service Limits Exceeded
```json
{
  "error": {
    "code": "QuotaExceeded",
    "message": "The indexer limit for this service tier has been exceeded."
  }
}
```
**Solution:** Upgrade service tier or reduce number of indexers

### HTTP 404 Errors

#### 404.1: Data Source Not Found
```json
{
  "error": {
    "code": "ResourceNotFound",
    "message": "The data source 'myDataSource' was not found."
  }
}
```
**Solution:** Verify data source name and existence

#### 404.2: Index Not Found
```json
{
  "error": {
    "code": "ResourceNotFound",
    "message": "The index 'myIndex' was not found."
  }
}
```
**Solution:** Create index before running indexer

### HTTP 500 Errors

#### 500.1: Internal Server Error
```json
{
  "error": {
    "code": "InternalServerError",
    "message": "An internal server error occurred."
  }
}
```
**Solution:** Retry operation, contact support if persistent

## Diagnostic Techniques

### Execution History Analysis

#### Checking Indexer Status
```http
GET https://[service-name].search.windows.net/indexers/[indexer-name]/status?api-version=2024-07-01
```

#### Key Metrics to Monitor
- **itemsProcessed**: Number of documents processed
- **itemsFailed**: Number of failed documents
- **executionTime**: Total execution duration
- **errors**: Detailed error information
- **warnings**: Non-fatal issues

### Log Analysis

#### Enable Diagnostic Logging
1. Configure Azure Monitor
2. Set up Log Analytics workspace
3. Enable search service diagnostics
4. Query logs for indexer events

#### Sample Log Queries
```kusto
// Indexer execution failures
AzureDiagnostics
| where Category == "OperationLogs"
| where OperationName == "Microsoft.Search/searchServices/indexers/run"
| where ResultType == "Failure"
| project TimeGenerated, ResourceId, OperationName, ResultDescription

// Performance analysis
AzureDiagnostics
| where Category == "OperationLogs"
| where OperationName == "Microsoft.Search/searchServices/indexers/run"
| summarize avg(DurationMs), count() by bin(TimeGenerated, 1h)
```

### Testing Strategies

#### Isolated Testing
1. Test data source connection independently
2. Validate index schema separately
3. Test field mappings with sample data
4. Run indexer with small data subset

#### Progressive Testing
1. Start with minimal configuration
2. Add complexity incrementally
3. Test each change thoroughly
4. Document working configurations

## Recovery Procedures

### Indexer Reset and Rebuild

#### When to Reset
- Persistent execution failures
- Schema changes requiring reprocessing
- Data corruption issues
- Change detection problems

#### Reset Procedure
```http
POST https://[service-name].search.windows.net/indexers/[indexer-name]/reset?api-version=2024-07-01
```

#### Full Rebuild Process
1. Reset indexer state
2. Clear target index (if needed)
3. Verify data source accessibility
4. Run indexer with monitoring
5. Validate results

### Data Consistency Issues

#### Detecting Inconsistencies
- Compare source and index document counts
- Verify key field uniqueness
- Check for missing or duplicate documents
- Validate field content accuracy

#### Resolution Steps
1. Identify scope of inconsistency
2. Determine root cause
3. Fix underlying issue
4. Reset and rerun indexer
5. Verify consistency restored

## Monitoring and Alerting

### Key Metrics to Monitor

#### Execution Metrics
- Success/failure rates
- Execution duration trends
- Document processing rates
- Error frequency and types

#### Resource Metrics
- Search service utilization
- Storage consumption
- Network bandwidth usage
- API call patterns

### Alert Configuration

#### Critical Alerts
- Indexer execution failures
- High error rates (>5%)
- Execution timeouts
- Service quota exceeded

#### Warning Alerts
- Slow execution times
- Increasing error rates
- Resource utilization spikes
- Unusual processing patterns

### Sample Alert Rules

#### Azure Monitor Alert
```json
{
  "name": "IndexerFailureAlert",
  "condition": {
    "allOf": [
      {
        "metricName": "SearchLatency",
        "operator": "GreaterThan",
        "threshold": 300,
        "timeAggregation": "Average"
      }
    ]
  },
  "actions": [
    {
      "actionGroupId": "/subscriptions/.../actionGroups/myActionGroup"
    }
  ]
}
```

## Best Practices for Troubleshooting

### Proactive Monitoring
- Set up comprehensive monitoring
- Establish baseline performance metrics
- Create automated health checks
- Document normal operating parameters

### Systematic Debugging
- Start with simplest possible configuration
- Change one variable at a time
- Document all changes and results
- Keep working configurations as backups

### Documentation and Knowledge Sharing
- Maintain troubleshooting runbooks
- Document common issues and solutions
- Share knowledge across team members
- Keep configuration change logs

## Getting Help

### Microsoft Support Resources
- Azure AI Search documentation
- Microsoft Q&A forums
- Azure support tickets
- Community forums and blogs

### Information to Provide
When seeking help, include:
- Service name and region
- Indexer configuration
- Error messages and codes
- Execution history details
- Data source information (sanitized)
- Steps to reproduce issue

### Self-Service Resources
- Azure AI Search REST API reference
- SDK documentation and samples
- Troubleshooting guides
- Performance optimization guides

## Prevention Strategies

### Configuration Management
- Use infrastructure as code
- Version control configurations
- Implement change approval processes
- Test changes in non-production environments

### Capacity Planning
- Monitor resource utilization trends
- Plan for data growth
- Understand service limits
- Scale proactively

### Regular Maintenance
- Review indexer performance regularly
- Update configurations as needed
- Clean up unused resources
- Keep documentation current

By following these troubleshooting guidelines and implementing proper monitoring, you can maintain reliable and efficient indexer operations in your Azure AI Search implementation.