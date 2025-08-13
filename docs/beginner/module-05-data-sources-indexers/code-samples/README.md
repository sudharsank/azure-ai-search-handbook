# Code Samples - Module 5: Data Sources & Indexers

## Overview

This directory contains comprehensive code samples demonstrating how to work with data sources and indexers in Azure AI Search. The examples cover various data source types, configuration patterns, and implementation approaches across multiple programming languages.

## Sample Categories

### 1. Azure SQL Database Indexers
- Basic SQL data source configuration
- Change tracking implementation
- Field mapping examples
- Performance optimization techniques

### 2. Blob Storage Indexers
- Document processing from blob storage
- Change detection with LastModified policy
- Metadata extraction
- Multi-format document handling

### 3. Cosmos DB Indexers
- NoSQL data indexing
- Change feed integration
- Partition key optimization
- JSON document processing

### 4. Change Detection
- Implementing various change detection policies
- Incremental update strategies
- High water mark patterns
- Custom change detection logic

### 5. Indexer Scheduling
- Automated indexer execution
- Schedule configuration
- Monitoring and alerting
- Error handling and recovery

### 6. Field Mappings
- Basic field mapping configurations
- Complex data transformations
- Built-in mapping functions
- Custom field processing

### 7. Error Handling
- Robust error handling patterns
- Retry logic implementation
- Error threshold configuration
- Logging and monitoring

### 8. Monitoring & Status
- Indexer status monitoring
- Performance metrics collection
- Health check implementations
- Alerting configurations

## Programming Languages

Each sample category is implemented in multiple programming languages:

- **Python** - Using azure-search-documents SDK
- **C#** - Using Azure.Search.Documents SDK
- **JavaScript/Node.js** - Using @azure/search-documents SDK
- **REST API** - Direct HTTP calls with examples

## Sample Structure

Each programming language directory contains:

```
language/
├── README.md                    # Language-specific setup and overview
├── 01_azure_sql_indexer.*      # SQL database indexer examples
├── 02_blob_storage_indexer.*   # Blob storage indexer examples
├── 03_cosmos_db_indexer.*      # Cosmos DB indexer examples
├── 04_change_detection.*       # Change detection implementations
├── 05_indexer_scheduling.*     # Scheduling and automation
├── 06_field_mappings.*         # Field mapping examples
├── 07_error_handling.*         # Error handling patterns
└── 08_monitoring_optimization.* # Monitoring and performance optimization
```

## Prerequisites

Before running these samples, ensure you have:

### Azure Resources
- Azure AI Search service
- At least one data source (SQL Database, Storage Account, or Cosmos DB)
- Appropriate permissions and connection strings

### Development Environment
- Programming language runtime (Python 3.7+, .NET 6+, Node.js 14+)
- Required SDKs and packages installed
- Code editor or IDE
- REST client (for REST API examples)

### Configuration
- Service endpoint and API keys
- Data source connection strings
- Sample data in your data sources

## Quick Start

### 1. Choose Your Language
Navigate to the appropriate language directory:
- [Python Examples](./python/README.md)
- [C# Examples](./csharp/README.md)
- [JavaScript Examples](./javascript/README.md)
- [REST API Examples](./rest/README.md)

### 2. Set Up Environment
Follow the language-specific setup instructions in each directory's README.

### 3. Configure Connections
Update the configuration files with your Azure AI Search service details and data source connections.

### 4. Run Samples
Start with basic examples and progress to more complex scenarios.

## Sample Scenarios

### Scenario 1: E-commerce Product Catalog
**Files:** `01_azure_sql_indexer.*`, `04_change_detection.*`, `05_indexer_scheduling.*`

Index product data from SQL Database with automatic updates:
- Configure SQL data source with change tracking
- Set up indexer with field mappings
- Implement scheduled updates
- Monitor indexer performance

### Scenario 2: Document Management System
**Files:** `02_blob_storage_indexer.*`, `06_field_mappings.*`, `07_error_handling.*`

Process various document types from blob storage:
- Configure blob storage data source
- Extract content and metadata
- Handle different file formats
- Implement error recovery

### Scenario 3: Customer Data Integration
**Files:** `03_cosmos_db_indexer.*`, `04_change_detection.*`, `08_monitoring_optimization.*`

Index customer data from Cosmos DB with real-time updates:
- Set up Cosmos DB data source
- Configure change feed detection
- Implement monitoring and alerting
- Handle data privacy requirements

## Configuration Templates

### Environment Variables
```bash
# Azure AI Search
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-admin-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net

# Azure SQL Database
SQL_CONNECTION_STRING=Server=tcp:your-server.database.windows.net,1433;Database=your-db;User ID=your-user;Password=your-password;

# Azure Storage
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net

# Azure Cosmos DB
COSMOS_CONNECTION_STRING=AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;Database=your-database
```

### Configuration Files
Each language directory includes sample configuration files:
- `config.json` - JSON configuration
- `appsettings.json` - .NET configuration
- `.env` - Environment variables
- `config.py` - Python configuration

## Best Practices Demonstrated

### Security
- Managed identity authentication examples
- Secure credential management
- Network security configurations
- Access control implementations

### Performance
- Batch size optimization
- Parallel processing patterns
- Resource utilization monitoring
- Query optimization techniques

### Reliability
- Error handling and retry logic
- Health check implementations
- Monitoring and alerting
- Recovery procedures

### Maintainability
- Configuration management
- Logging and debugging
- Documentation patterns
- Testing strategies

## Testing and Validation

### Unit Tests
Each language directory includes unit tests for:
- Data source configuration
- Indexer creation and management
- Field mapping validation
- Error handling scenarios

### Integration Tests
End-to-end tests covering:
- Complete indexing workflows
- Multi-source scenarios
- Performance benchmarks
- Error recovery procedures

### Sample Data
Test data sets are provided for:
- SQL database schemas and data
- Sample documents for blob storage
- JSON documents for Cosmos DB
- Various file formats and structures

## Troubleshooting

### Common Issues
- Connection failures and solutions
- Authentication problems
- Performance optimization
- Error handling patterns

### Debugging Tools
- Logging configurations
- Monitoring setups
- Diagnostic utilities
- Performance profiling

### Support Resources
- Error code references
- Troubleshooting guides
- Community forums
- Microsoft documentation

## Contributing

### Adding New Samples
1. Follow the established naming convention
2. Include comprehensive documentation
3. Add appropriate error handling
4. Provide test data and validation

### Improving Existing Samples
1. Enhance error handling
2. Add performance optimizations
3. Improve documentation
4. Add test coverage

## Interactive Notebooks

The [notebooks](./notebooks/README.md) directory contains Jupyter notebooks with:
- Interactive tutorials
- Step-by-step walkthroughs
- Visualization examples
- Experimentation environments

## Additional Resources

- [Azure AI Search Documentation](https://docs.microsoft.com/azure/search/)
- [Indexer Overview](https://docs.microsoft.com/azure/search/search-indexer-overview)
- [Data Source Configuration](https://docs.microsoft.com/azure/search/search-howto-create-indexers)
- [Best Practices Guide](../best-practices.md)
- [Troubleshooting Guide](../indexer-troubleshooting.md)

## Next Steps

After exploring these samples:
1. Implement similar patterns in your projects
2. Customize configurations for your specific needs
3. Explore advanced features in intermediate modules
4. Share your experiences with the community

## Feedback and Support

For questions, issues, or suggestions:
- Review the troubleshooting guides
- Check the Azure AI Search documentation
- Engage with the community forums
- Submit feedback through appropriate channels