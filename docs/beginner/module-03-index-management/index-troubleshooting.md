# Index Operations Troubleshooting - Module 3: Index Management

## Common Index Creation Issues

### Issue: Index creation fails with validation errors
**Symptoms:**
- HTTP 400 Bad Request errors
- Schema validation error messages
- Index not created in service

**Common Causes:**
- Invalid field names or types
- Conflicting field attributes
- Unsupported analyzer configurations
- Malformed JSON in request

**Solutions:**
1. Validate field names follow naming conventions
2. Check field attribute combinations are valid
3. Verify analyzer names are correct
4. Test with minimal schema first

### Issue: Index creation succeeds but fields don't work as expected
**Symptoms:**
- Fields not searchable despite being marked as searchable
- Filters don't work on filterable fields
- Sorting fails on sortable fields

**Common Causes:**
- Field attributes not properly set
- Data type mismatches
- Analyzer configuration issues
- Case sensitivity problems

**Solutions:**
1. Verify field attributes in index definition
2. Check data types match expected values
3. Test with simple queries first
4. Review analyzer behavior

## Document Upload Issues

### Issue: Documents fail to upload
**Symptoms:**
- HTTP 400 or 422 errors during upload
- Documents not appearing in index
- Partial batch failures

**Common Causes:**
- Document key violations
- Field type mismatches
- Document size limits exceeded
- Malformed document structure

**Solutions:**
```json
// Example error response
{
  "error": {
    "code": "InvalidDocumentFormat",
    "message": "The document contains a field 'price' with value 'invalid' that cannot be converted to type 'Edm.Double'."
  }
}
```

**Resolution Steps:**
1. Validate document structure matches index schema
2. Ensure document keys are unique and valid
3. Check field value types match schema
4. Verify document size is within limits

### Issue: Documents upload but content is not searchable
**Symptoms:**
- Documents exist in index
- Search queries return no results
- Field values appear in results but aren't searchable

**Common Causes:**
- Fields not marked as searchable
- Incorrect analyzer configuration
- Empty or null field values
- Language analyzer mismatch

**Solutions:**
1. Verify field is marked as searchable in schema
2. Check analyzer configuration for the field
3. Test with simple exact match queries
4. Validate field content is not empty

## Index Performance Issues

### Issue: Slow index operations
**Symptoms:**
- Long response times for document uploads
- Timeouts during batch operations
- High resource utilization

**Common Causes:**
- Large document sizes
- Complex field configurations
- Insufficient service capacity
- Network latency issues

**Solutions:**
1. Reduce batch sizes for uploads
2. Optimize field configurations
3. Scale up service tier if needed
4. Monitor resource utilization

### Issue: Index size grows unexpectedly
**Symptoms:**
- Storage usage higher than expected
- Costs increasing rapidly
- Performance degradation

**Common Causes:**
- Unnecessary field attributes enabled
- Large text fields being stored
- Duplicate documents
- Inefficient data types

**Solutions:**
1. Review field attribute usage
2. Optimize field types and storage
3. Check for duplicate documents
4. Implement data deduplication

## Query Performance Issues

### Issue: Search queries are slow
**Symptoms:**
- High query response times
- Timeouts on complex queries
- Poor user experience

**Common Causes:**
- Inefficient query patterns
- Large result sets
- Complex filtering or sorting
- Insufficient service resources

**Solutions:**
1. Analyze query patterns and optimize
2. Use appropriate filters to reduce result sets
3. Implement pagination for large results
4. Consider service tier upgrade

### Issue: Relevance scoring is poor
**Symptoms:**
- Irrelevant results appearing first
- Expected results not found
- Poor search experience

**Common Causes:**
- Inappropriate analyzer configuration
- Missing or incorrect field weights
- Poor query construction
- Data quality issues

**Solutions:**
1. Review and optimize analyzer settings
2. Implement scoring profiles if needed
3. Improve query construction
4. Validate source data quality

## Index Maintenance Issues

### Issue: Index becomes corrupted or inconsistent
**Symptoms:**
- Unexpected query results
- Missing documents
- Error messages during operations

**Common Causes:**
- Interrupted operations
- Concurrent modification conflicts
- Service outages during updates
- Hardware or software failures

**Solutions:**
1. Check service health and status
2. Validate index statistics
3. Consider index rebuild if necessary
4. Implement proper error handling

### Issue: Index schema needs to be updated
**Symptoms:**
- Need to add new fields
- Need to change field attributes
- Need to modify analyzers

**Common Causes:**
- Changing business requirements
- New data sources
- Performance optimization needs
- Feature enhancements

**Solutions:**
1. Plan schema changes carefully
2. Test changes in development environment
3. Consider creating new index for major changes
4. Implement gradual migration strategy

## Error Code Reference

### HTTP 400 Errors

#### 400.1: Invalid Field Name
```json
{
  "error": {
    "code": "InvalidFieldName",
    "message": "Field name 'field-name' is invalid. Field names must start with a letter or underscore."
  }
}
```
**Solution:** Use valid field naming conventions

#### 400.2: Invalid Field Attribute Combination
```json
{
  "error": {
    "code": "InvalidFieldDefinition",
    "message": "Field 'myField' cannot be both key and facetable."
  }
}
```
**Solution:** Review field attribute compatibility

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
**Solution:** Check API key permissions or RBAC roles

### HTTP 404 Errors

#### 404.1: Index Not Found
```json
{
  "error": {
    "code": "ResourceNotFound",
    "message": "The index 'myindex' was not found."
  }
}
```
**Solution:** Verify index name and existence

### HTTP 422 Errors

#### 422.1: Document Validation Error
```json
{
  "error": {
    "code": "InvalidDocument",
    "message": "Document key cannot be null or empty."
  }
}
```
**Solution:** Ensure all documents have valid keys

## Diagnostic Techniques

### Index Statistics Analysis
```http
GET https://[service-name].search.windows.net/indexes/[index-name]/stats?api-version=2024-07-01
```

**Key Metrics to Monitor:**
- Document count
- Storage size
- Vector index size (if applicable)

### Query Analysis
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/search?api-version=2024-07-01
{
  "search": "*",
  "queryType": "simple",
  "searchMode": "any",
  "count": true
}
```

### Field Analysis
Test individual fields to isolate issues:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/search?api-version=2024-07-01
{
  "search": "test",
  "searchFields": "specificField",
  "select": "specificField"
}
```

## Monitoring and Alerting

### Key Metrics to Monitor

#### Index Health
- Document count trends
- Storage utilization
- Index availability
- Error rates

#### Performance Metrics
- Query response times
- Indexing throughput
- Resource utilization
- Cache hit rates

### Alert Configuration

#### Critical Alerts
- Index unavailable
- High error rates (>5%)
- Storage quota exceeded
- Performance degradation

#### Warning Alerts
- Unusual document count changes
- Increasing response times
- Resource utilization spikes
- Schema validation errors

## Recovery Procedures

### Index Recovery
1. **Assess Damage**: Determine extent of corruption or data loss
2. **Check Backups**: Verify availability of configuration and data backups
3. **Rebuild Strategy**: Decide between repair or complete rebuild
4. **Execute Recovery**: Implement chosen recovery strategy
5. **Validate Results**: Verify index functionality and data integrity

### Data Recovery
1. **Identify Missing Data**: Determine which documents are affected
2. **Source Data Validation**: Verify source data integrity
3. **Incremental Restore**: Re-index missing or corrupted documents
4. **Consistency Check**: Validate data consistency across the index

## Best Practices for Troubleshooting

### Systematic Approach
1. **Isolate the Problem**: Narrow down the scope of the issue
2. **Gather Information**: Collect relevant logs, metrics, and error messages
3. **Test Hypotheses**: Systematically test potential causes
4. **Document Solutions**: Record successful resolution steps
5. **Prevent Recurrence**: Implement measures to prevent similar issues

### Preventive Measures
- Implement comprehensive monitoring
- Regular health checks
- Automated testing
- Proper error handling
- Documentation maintenance

## Getting Help

### Microsoft Support Resources
- Azure AI Search documentation
- Microsoft Q&A forums
- Azure support tickets
- Community forums

### Information to Provide
When seeking help, include:
- Service name and region
- Index configuration (sanitized)
- Error messages and codes
- Steps to reproduce
- Timeline of when issues started

### Self-Service Resources
- Azure AI Search REST API reference
- SDK documentation
- Troubleshooting guides
- Performance optimization guides

By following these troubleshooting guidelines and implementing proper monitoring, you can maintain healthy and performant search indexes in your Azure AI Search implementation.