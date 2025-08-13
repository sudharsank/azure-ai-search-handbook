# Practice & Implementation - Module 5: Data Sources & Indexers

## Hands-On Exercises

This section provides practical exercises to help you master data sources and indexers in Azure AI Search. Each exercise builds upon the previous one, gradually increasing in complexity.

## Exercise 1: Create Your First Data Source

### Objective
Create a data source connection to Azure Blob Storage and understand the basic configuration.

### Prerequisites
- Azure Storage Account with a container
- Sample documents uploaded to the container
- Azure AI Search service

### Steps

1. **Prepare Sample Data**
   - Create a container named `sample-documents`
   - Upload 3-5 PDF or text files
   - Note the container URL and access keys

2. **Create Data Source via Portal**
   - Navigate to your Azure AI Search service
   - Go to "Data sources" section
   - Click "Add data source"
   - Configure the connection to your blob storage

3. **Verify Connection**
   - Test the connection
   - Review the data source configuration
   - Note the generated data source name

### Expected Outcome
- Successfully created data source
- Connection test passes
- Understanding of data source components

## Exercise 2: Build a Basic Indexer

### Objective
Create a simple indexer that processes documents from your data source.

### Prerequisites
- Completed Exercise 1
- Basic understanding of index schemas

### Steps

1. **Design Index Schema**
   - Create an index with fields for:
     - Document ID (key field)
     - Content (searchable text)
     - Metadata (filename, last modified)

2. **Create Indexer**
   - Use the Import Data wizard
   - Select your data source from Exercise 1
   - Configure field mappings
   - Set indexer name and schedule

3. **Run and Monitor**
   - Execute the indexer
   - Monitor execution status
   - Review indexed documents

### Expected Outcome
- Functional indexer processing documents
- Documents successfully indexed
- Understanding of indexer execution flow

## Exercise 3: Implement Change Detection

### Objective
Configure change detection to enable incremental updates.

### Prerequisites
- Completed Exercise 2
- Understanding of change detection policies

### Steps

1. **Configure Change Detection**
   - Modify your data source
   - Add LastModified change detection policy
   - Update the data source configuration

2. **Test Incremental Updates**
   - Add new documents to your container
   - Modify existing documents
   - Run the indexer again

3. **Verify Results**
   - Check that only new/modified documents are processed
   - Review indexer execution history
   - Validate document counts

### Expected Outcome
- Change detection working correctly
- Only modified documents are reprocessed
- Improved indexer efficiency

## Exercise 4: Advanced Field Mappings

### Objective
Implement complex field mappings and transformations.

### Prerequisites
- Completed Exercise 3
- Understanding of field mapping concepts

### Steps

1. **Create Complex Index Schema**
   - Add fields for different data types
   - Include collection fields
   - Add fields for metadata extraction

2. **Configure Field Mappings**
   - Map source fields to target fields
   - Use built-in functions for transformations
   - Handle missing or null values

3. **Test Transformations**
   - Run indexer with new mappings
   - Verify data transformations
   - Check field population

### Expected Outcome
- Complex field mappings working correctly
- Data transformations applied successfully
- Understanding of mapping functions

## Exercise 5: Error Handling and Monitoring

### Objective
Implement robust error handling and monitoring for your indexers.

### Prerequisites
- Completed Exercise 4
- Access to Azure Monitor or logging tools

### Steps

1. **Configure Error Handling**
   - Set error thresholds
   - Configure retry policies
   - Set up failure notifications

2. **Introduce Test Errors**
   - Upload corrupted documents
   - Create schema mismatches
   - Test error scenarios

3. **Monitor and Respond**
   - Review error logs
   - Understand error types
   - Implement corrective actions

### Expected Outcome
- Robust error handling in place
- Understanding of common error scenarios
- Effective monitoring and alerting

## Real-World Scenarios

### Scenario 1: E-commerce Product Catalog

**Challenge**: Index product data from Azure SQL Database with regular updates.

**Implementation Steps**:
1. Create SQL data source with change tracking
2. Design index for product search
3. Configure field mappings for product attributes
4. Set up scheduled indexing
5. Implement error handling for data quality issues

**Key Learning Points**:
- SQL change tracking configuration
- Handling relational data in search indexes
- Performance optimization for large catalogs

### Scenario 2: Document Management System

**Challenge**: Index various document types from Blob Storage with metadata extraction.

**Implementation Steps**:
1. Configure blob storage data source
2. Set up index for document content and metadata
3. Implement file type-specific processing
4. Configure change detection for file updates
5. Handle different document formats

**Key Learning Points**:
- Multi-format document processing
- Metadata extraction techniques
- Content type handling

### Scenario 3: Customer Data Integration

**Challenge**: Index customer data from Cosmos DB with real-time updates.

**Implementation Steps**:
1. Set up Cosmos DB data source
2. Configure change feed-based detection
3. Design index for customer search scenarios
4. Implement data privacy considerations
5. Set up monitoring and alerting

**Key Learning Points**:
- Cosmos DB change feed integration
- Real-time data processing
- Privacy and compliance considerations

## Troubleshooting Exercises

### Exercise A: Connection Failures

**Scenario**: Your indexer fails to connect to the data source.

**Troubleshooting Steps**:
1. Verify connection strings
2. Check firewall settings
3. Validate authentication credentials
4. Test network connectivity
5. Review service logs

### Exercise B: Performance Issues

**Scenario**: Indexer runs slowly with large datasets.

**Troubleshooting Steps**:
1. Analyze indexer execution metrics
2. Optimize batch sizes
3. Review index schema design
4. Check resource utilization
5. Implement performance improvements

### Exercise C: Data Quality Problems

**Scenario**: Indexed data doesn't match source data.

**Troubleshooting Steps**:
1. Review field mappings
2. Check data type compatibility
3. Validate transformation functions
4. Test with sample data
5. Implement data validation

## Best Practices Implementation

### Checklist for Production Readiness

#### Security
- [ ] Managed identity configured
- [ ] Connection strings secured
- [ ] Network access restricted
- [ ] Audit logging enabled

#### Performance
- [ ] Appropriate batch sizes configured
- [ ] Change detection optimized
- [ ] Resource scaling planned
- [ ] Monitoring in place

#### Reliability
- [ ] Error handling configured
- [ ] Retry policies set
- [ ] Backup procedures defined
- [ ] Recovery plans documented

#### Maintainability
- [ ] Configuration documented
- [ ] Version control implemented
- [ ] Testing procedures defined
- [ ] Operational runbooks created

## Advanced Implementation Patterns

### Pattern 1: Multi-Source Indexing

Combine data from multiple sources into a single index:

1. Create separate data sources for each system
2. Design unified index schema
3. Use multiple indexers with field mappings
4. Coordinate indexer schedules
5. Handle data conflicts and duplicates

### Pattern 2: Hierarchical Data Processing

Process hierarchical data structures:

1. Flatten hierarchical data in source queries
2. Use complex field mappings
3. Implement parent-child relationships
4. Handle nested collections
5. Optimize for search scenarios

### Pattern 3: Real-Time + Batch Processing

Combine real-time and batch processing:

1. Set up real-time indexer for immediate updates
2. Configure batch indexer for bulk processing
3. Coordinate between different update patterns
4. Handle data consistency
5. Monitor both processing paths

## Performance Benchmarking

### Metrics to Track

1. **Indexing Throughput**
   - Documents per second
   - Total processing time
   - Resource utilization

2. **Error Rates**
   - Failed documents percentage
   - Error types and frequency
   - Recovery success rate

3. **Resource Consumption**
   - Search service utilization
   - Data source load impact
   - Network bandwidth usage

### Optimization Techniques

1. **Batch Size Tuning**
   - Test different batch sizes
   - Monitor memory usage
   - Balance throughput vs. resource usage

2. **Parallel Processing**
   - Use multiple indexers when appropriate
   - Coordinate execution schedules
   - Monitor resource contention

3. **Schema Optimization**
   - Minimize unnecessary fields
   - Optimize field types
   - Reduce index size

## Next Steps

After completing these exercises:

1. **Review Code Samples**: Explore the provided code examples
2. **Advanced Topics**: Move to intermediate modules for skillsets
3. **Production Deployment**: Apply learnings to real projects
4. **Community Engagement**: Share experiences and learn from others

## Additional Resources

- [Indexer Troubleshooting Guide](./indexer-troubleshooting.md)
- [Data Source Troubleshooting](./datasource-troubleshooting.md)
- [Code Samples](./code-samples/README.md)
- [Azure AI Search Documentation](https://docs.microsoft.com/azure/search/)