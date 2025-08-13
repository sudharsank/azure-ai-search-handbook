# Best Practices - Module 5: Data Sources & Indexers

## Data Source Configuration

### Connection Management
- **Use Managed Identity**: Prefer managed identity over connection strings for enhanced security
- **Secure Connection Strings**: Store connection strings in Azure Key Vault when API keys are necessary
- **Test Connections**: Always validate data source connectivity before creating indexers
- **Monitor Quotas**: Be aware of service tier limits for data sources and indexers

### Data Source Design
- **Single Responsibility**: Create separate data sources for different types of data or environments
- **Descriptive Naming**: Use clear, descriptive names that indicate the data source type and purpose
- **Environment Separation**: Use different data sources for development, staging, and production

## Indexer Configuration

### Scheduling Strategy
- **Appropriate Frequency**: Schedule indexers based on data change frequency, not arbitrarily
- **Off-Peak Hours**: Run large indexing operations during low-traffic periods
- **Incremental Updates**: Use change detection policies to minimize processing time
- **Batch Size Optimization**: Configure batch sizes based on document size and complexity

### Field Mapping Best Practices
- **Explicit Mappings**: Define field mappings explicitly rather than relying on automatic mapping
- **Data Type Consistency**: Ensure source and target field types are compatible
- **Null Handling**: Plan for null values and missing fields in source data
- **Complex Type Mapping**: Use output field mappings for complex data transformations

### Performance Optimization
- **Index Schema Design**: Design your index schema to minimize field mappings
- **Selective Field Extraction**: Only extract and index fields that will be searched or filtered
- **Parallel Processing**: Use multiple indexers for large datasets when possible
- **Resource Scaling**: Consider scaling up your search service for large indexing operations

## Change Detection

### SQL Database
- **Integrated Change Tracking**: Use SQL Integrated Change Tracking for optimal performance
- **High Water Mark**: Use high water mark policy for append-only scenarios
- **Soft Delete**: Implement soft delete patterns rather than hard deletes when possible

### Blob Storage
- **LastModified Policy**: Use LastModified change detection for file-based sources
- **Metadata Tracking**: Leverage blob metadata for custom change detection logic
- **Container Organization**: Organize blobs logically to optimize indexer performance

### Cosmos DB
- **Change Feed**: Utilize Cosmos DB change feed for real-time change detection
- **Partition Strategy**: Align indexer queries with your Cosmos DB partition strategy
- **Query Optimization**: Use efficient queries to minimize RU consumption

## Error Handling and Monitoring

### Robust Error Handling
- **Retry Policies**: Configure appropriate retry policies for transient failures
- **Error Thresholds**: Set reasonable error thresholds to prevent infinite retry loops
- **Graceful Degradation**: Design indexers to continue processing despite individual document failures
- **Logging Strategy**: Implement comprehensive logging for troubleshooting

### Monitoring and Alerting
- **Status Monitoring**: Regularly check indexer status and execution history
- **Performance Metrics**: Monitor indexing duration and throughput
- **Error Alerting**: Set up alerts for indexer failures or high error rates
- **Resource Utilization**: Monitor search service resource usage during indexing

## Security Best Practices

### Authentication and Authorization
- **Principle of Least Privilege**: Grant minimum necessary permissions to indexers
- **Regular Key Rotation**: Rotate API keys regularly if using key-based authentication
- **Network Security**: Use private endpoints and firewall rules to restrict access
- **Audit Logging**: Enable audit logging for indexer operations

### Data Protection
- **Sensitive Data Handling**: Avoid indexing sensitive or personally identifiable information
- **Data Encryption**: Ensure data is encrypted in transit and at rest
- **Access Controls**: Implement proper access controls on both source and target systems
- **Compliance**: Ensure indexer operations comply with relevant data protection regulations

## Development and Testing

### Development Workflow
- **Environment Isolation**: Use separate search services for development and production
- **Version Control**: Store indexer definitions in version control systems
- **Automated Testing**: Implement automated tests for indexer configurations
- **Documentation**: Document indexer configurations and dependencies

### Testing Strategies
- **Unit Testing**: Test individual components like field mappings and transformations
- **Integration Testing**: Test end-to-end indexer workflows with sample data
- **Performance Testing**: Test indexer performance with production-like data volumes
- **Failure Testing**: Test error handling and recovery scenarios

## Maintenance and Operations

### Regular Maintenance
- **Index Rebuilding**: Plan for periodic full index rebuilds when necessary
- **Schema Evolution**: Design for schema changes and field additions
- **Cleanup Procedures**: Implement procedures for cleaning up obsolete indexers and data sources
- **Backup Strategy**: Maintain backups of indexer configurations

### Operational Excellence
- **Documentation**: Maintain up-to-date documentation for all indexers
- **Runbooks**: Create operational runbooks for common maintenance tasks
- **Change Management**: Implement proper change management processes
- **Disaster Recovery**: Plan for disaster recovery scenarios

## Common Anti-Patterns to Avoid

### Configuration Anti-Patterns
- ❌ **Over-Scheduling**: Running indexers too frequently without considering data change patterns
- ❌ **Monolithic Indexers**: Creating single indexers that handle too many different data types
- ❌ **Hardcoded Values**: Embedding environment-specific values in indexer definitions
- ❌ **Ignoring Errors**: Not properly handling or monitoring indexer errors

### Performance Anti-Patterns
- ❌ **Full Rebuilds**: Performing full index rebuilds when incremental updates would suffice
- ❌ **Inefficient Queries**: Using inefficient source queries that scan entire datasets
- ❌ **Resource Contention**: Running multiple resource-intensive indexers simultaneously
- ❌ **Oversized Batches**: Using batch sizes that are too large for available resources

### Security Anti-Patterns
- ❌ **Exposed Credentials**: Storing connection strings or keys in code or configuration files
- ❌ **Excessive Permissions**: Granting broader permissions than necessary
- ❌ **Unencrypted Connections**: Using unencrypted connections to data sources
- ❌ **Missing Monitoring**: Not monitoring for security-related events or anomalies

## Checklist for Production Deployment

### Pre-Deployment
- [ ] All connection strings and credentials are secured
- [ ] Indexer schedules are appropriate for production workloads
- [ ] Error handling and retry policies are configured
- [ ] Monitoring and alerting are set up
- [ ] Performance testing has been completed

### Post-Deployment
- [ ] Indexer execution is monitored and verified
- [ ] Performance metrics are within expected ranges
- [ ] Error rates are acceptable
- [ ] Documentation is updated
- [ ] Team is trained on operational procedures

## Performance Tuning Guidelines

### Indexer Performance
- **Batch Size**: Start with default batch sizes and adjust based on performance
- **Parallel Execution**: Use multiple indexers for large datasets when appropriate
- **Resource Allocation**: Ensure adequate search service capacity during indexing
- **Network Optimization**: Minimize network latency between services

### Query Performance
- **Index Design**: Design indexes to support your query patterns efficiently
- **Field Selection**: Only make fields searchable, filterable, or sortable when necessary
- **Analyzer Selection**: Choose appropriate analyzers for your content and language
- **Caching Strategy**: Implement appropriate caching strategies for frequently accessed data

By following these best practices, you'll create robust, secure, and performant indexing solutions that scale with your needs and provide reliable data ingestion for your Azure AI Search implementation.