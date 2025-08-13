# Data Source Troubleshooting - Module 5: Data Sources & Indexers

## Common Data Source Issues

### Connection Problems

#### Issue: Unable to connect to data source
**Symptoms:**
- Connection test fails in Azure portal
- Indexer fails immediately with connection error
- Authentication errors in logs

**Common Causes:**
- Incorrect connection strings
- Network connectivity issues
- Firewall blocking access
- Invalid credentials

**Solutions:**
1. Verify connection string format
2. Test network connectivity
3. Check firewall rules
4. Validate authentication credentials

#### Issue: Intermittent connection failures
**Symptoms:**
- Indexer sometimes succeeds, sometimes fails
- Timeout errors during execution
- Connection drops mid-process

**Common Causes:**
- Network instability
- Resource contention
- Service throttling
- Connection pool exhaustion

**Solutions:**
1. Implement retry logic
2. Optimize connection pooling
3. Monitor network stability
4. Check service throttling limits

### Authentication Issues

#### Issue: Authentication failures with managed identity
**Symptoms:**
- "Access denied" errors
- Authentication token errors
- Permission-related failures

**Common Causes:**
- Missing role assignments
- Incorrect managed identity configuration
- Insufficient permissions
- Token expiration issues

**Solutions:**
1. Verify role assignments
2. Check managed identity status
3. Review required permissions
4. Test authentication independently

#### Issue: API key authentication problems
**Symptoms:**
- Invalid key errors
- Unauthorized access messages
- Key-related authentication failures

**Common Causes:**
- Expired or invalid API keys
- Wrong key type (admin vs query)
- Key rotation issues
- Incorrect key format

**Solutions:**
1. Regenerate API keys
2. Use correct key type
3. Update key references
4. Implement key rotation process

## Data Source-Specific Issues

### Azure SQL Database

#### Issue: SQL connection failures
**Symptoms:**
- Cannot connect to SQL server
- Database not accessible
- Login failures

**Common Causes:**
- Firewall rules blocking Azure services
- Incorrect server/database names
- SQL authentication disabled
- Network security group restrictions

**Solutions:**
```sql
-- Enable Azure services access
-- In Azure portal: SQL Server > Firewalls and virtual networks
-- Enable "Allow Azure services and resources to access this server"

-- Verify connection string format
Server=tcp:myserver.database.windows.net,1433;Database=mydatabase;User ID=myuser;Password=mypassword;
```

#### Issue: Change tracking not working
**Symptoms:**
- Indexer processes all documents every run
- No incremental updates
- Performance degradation

**Common Causes:**
- Change tracking not enabled
- Incorrect change tracking configuration
- Primary key issues
- Table structure problems

**Solutions:**
```sql
-- Enable change tracking on database
ALTER DATABASE [MyDatabase] SET CHANGE_TRACKING = ON (CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON);

-- Enable change tracking on table
ALTER TABLE [MyTable] ENABLE CHANGE_TRACKING WITH (TRACK_COLUMNS_UPDATED = ON);

-- Verify change tracking status
SELECT name, is_change_tracking_on FROM sys.databases WHERE name = 'MyDatabase';
SELECT name, is_change_tracking_on FROM sys.tables WHERE name = 'MyTable';
```

#### Issue: Query performance problems
**Symptoms:**
- Slow indexer execution
- SQL timeouts
- High database resource usage

**Common Causes:**
- Missing indexes on source tables
- Inefficient queries
- Large result sets
- Resource contention

**Solutions:**
```sql
-- Add indexes for common query patterns
CREATE INDEX IX_LastModified ON MyTable (LastModified);
CREATE INDEX IX_IsDeleted ON MyTable (IsDeleted) WHERE IsDeleted = 0;

-- Optimize queries with proper WHERE clauses
SELECT * FROM MyTable WHERE LastModified > @HighWaterMark;
```

### Azure Blob Storage

#### Issue: Blob access failures
**Symptoms:**
- Cannot access blob container
- File not found errors
- Permission denied messages

**Common Causes:**
- Incorrect container names
- Missing storage permissions
- Network access restrictions
- SAS token issues

**Solutions:**
1. Verify container exists and is accessible
2. Check storage account permissions
3. Review network access rules
4. Validate SAS token if used

```bash
# Test blob access with Azure CLI
az storage blob list --container-name mycontainer --account-name mystorageaccount
```

#### Issue: Change detection not working for blobs
**Symptoms:**
- All blobs processed every run
- Modified files not detected
- Deleted files not handled

**Common Causes:**
- LastModified policy not configured
- Clock synchronization issues
- Metadata not updated
- Soft delete interfering

**Solutions:**
1. Configure LastModified change detection policy
2. Ensure system clocks are synchronized
3. Update blob metadata when content changes
4. Handle soft delete scenarios appropriately

#### Issue: Large file processing problems
**Symptoms:**
- Timeouts with large files
- Memory errors during processing
- Incomplete file processing

**Common Causes:**
- Files exceed size limits
- Insufficient processing resources
- Network bandwidth limitations
- Content extraction issues

**Solutions:**
1. Split large files into smaller chunks
2. Increase indexer timeout settings
3. Optimize network connectivity
4. Use appropriate content extraction settings

### Azure Cosmos DB

#### Issue: Cosmos DB connection problems
**Symptoms:**
- Cannot connect to Cosmos account
- Authentication failures
- Endpoint not accessible

**Common Causes:**
- Incorrect endpoint URLs
- Invalid connection strings
- Firewall restrictions
- Key rotation issues

**Solutions:**
```javascript
// Verify connection string format
AccountEndpoint=https://myaccount.documents.azure.com:443/;AccountKey=mykey;Database=mydatabase
```

#### Issue: Query performance issues
**Symptoms:**
- High RU consumption
- Query timeouts
- Slow indexer execution

**Common Causes:**
- Inefficient queries
- Missing indexes
- Cross-partition queries
- Large result sets

**Solutions:**
```sql
-- Optimize queries with proper WHERE clauses
SELECT * FROM c WHERE c._ts > @HighWaterMark

-- Use partition key in queries when possible
SELECT * FROM c WHERE c.partitionKey = 'value' AND c._ts > @HighWaterMark
```

#### Issue: Change feed configuration problems
**Symptoms:**
- Changes not detected
- Duplicate processing
- Missing updates

**Common Causes:**
- Change feed not enabled
- Incorrect lease configuration
- Partition key issues
- Checkpoint problems

**Solutions:**
1. Enable change feed on container
2. Configure proper lease container
3. Verify partition key strategy
4. Monitor checkpoint progress

## Network and Security Issues

### Firewall Configuration

#### Issue: Firewall blocking connections
**Symptoms:**
- Connection timeouts
- Network unreachable errors
- Intermittent connectivity

**Common Causes:**
- Azure services not allowed
- IP restrictions too restrictive
- Network security groups blocking traffic
- Private endpoint misconfiguration

**Solutions:**
1. Allow Azure services in firewall rules
2. Add search service IP ranges
3. Configure network security groups
4. Set up private endpoints correctly

### Private Endpoint Issues

#### Issue: Private endpoint connectivity problems
**Symptoms:**
- Cannot resolve private endpoint
- Connection failures through private network
- DNS resolution issues

**Common Causes:**
- DNS configuration problems
- Private DNS zone issues
- Network routing problems
- Endpoint provisioning failures

**Solutions:**
1. Configure private DNS zones
2. Verify DNS resolution
3. Check network routing
4. Validate endpoint status

## Diagnostic Tools and Techniques

### Connection Testing

#### Azure Portal Tests
1. Use "Test connection" in data source configuration
2. Review connection test results
3. Check error messages and codes
4. Verify configuration parameters

#### PowerShell Testing
```powershell
# Test SQL connection
Test-NetConnection -ComputerName myserver.database.windows.net -Port 1433

# Test storage account connectivity
$ctx = New-AzStorageContext -StorageAccountName mystorageaccount -StorageAccountKey mykey
Get-AzStorageContainer -Context $ctx
```

#### Azure CLI Testing
```bash
# Test Cosmos DB connectivity
az cosmosdb database show --account-name myaccount --name mydatabase

# Test blob storage access
az storage blob list --container-name mycontainer --account-name mystorageaccount
```

### Monitoring and Logging

#### Enable Diagnostic Logging
1. Configure Azure Monitor for data sources
2. Set up Log Analytics workspace
3. Enable diagnostic settings
4. Query logs for connection issues

#### Sample Log Queries
```kusto
// Connection failures
AzureDiagnostics
| where Category == "DataSourceOperations"
| where Level == "Error"
| where Message contains "connection"
| project TimeGenerated, Resource, Message

// Authentication issues
AzureDiagnostics
| where Category == "DataSourceOperations"
| where Message contains "authentication" or Message contains "authorization"
| project TimeGenerated, Resource, Message, Level
```

## Performance Optimization

### Connection Optimization

#### Connection Pooling
- Configure appropriate connection pool sizes
- Monitor connection usage patterns
- Implement connection retry logic
- Use connection multiplexing when available

#### Query Optimization
- Use efficient queries with proper filtering
- Implement pagination for large result sets
- Add appropriate indexes to source systems
- Monitor query execution plans

### Resource Management

#### Capacity Planning
- Monitor data source resource utilization
- Plan for peak usage periods
- Scale resources appropriately
- Implement throttling if needed

#### Cost Optimization
- Use appropriate service tiers
- Implement efficient change detection
- Optimize query patterns
- Monitor resource consumption

## Best Practices for Data Source Management

### Configuration Management
- Use infrastructure as code for data sources
- Version control connection configurations
- Implement secure credential management
- Document data source dependencies

### Security Best Practices
- Use managed identity when possible
- Implement least privilege access
- Regularly rotate credentials
- Monitor access patterns

### Monitoring and Maintenance
- Set up proactive monitoring
- Implement health checks
- Plan for disaster recovery
- Keep documentation updated

## Recovery Procedures

### Connection Recovery
1. Identify root cause of connection failure
2. Fix underlying network or configuration issue
3. Test connection independently
4. Restart indexer operations
5. Monitor for continued stability

### Data Consistency Recovery
1. Assess scope of data inconsistency
2. Identify missing or corrupted data
3. Reset change detection if needed
4. Perform full reindex if necessary
5. Validate data consistency

## Getting Help

### Microsoft Support
- Azure AI Search documentation
- Azure support tickets
- Community forums
- Microsoft Q&A

### Information to Provide
- Data source type and configuration
- Error messages and codes
- Network topology information
- Authentication method used
- Steps to reproduce issue

By following these troubleshooting guidelines, you can resolve most data source connectivity and configuration issues, ensuring reliable data ingestion for your Azure AI Search implementation.