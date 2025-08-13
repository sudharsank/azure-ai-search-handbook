# Code Samples - Module 8: Search Explorer & Portal Tools

## Overview

This directory contains code samples that complement the Azure AI Search portal tools, demonstrating how to automate portal workflows, integrate with portal-generated configurations, and transition from portal-based development to programmatic implementations.

## Sample Categories

### 1. Portal API Integration
- Automating portal workflows with APIs
- Exporting portal configurations
- Programmatic resource management
- Configuration synchronization

### 2. Query Testing
- Automated query testing frameworks
- Portal query validation
- Performance benchmarking
- Regression testing

### 3. Index Validation
- Schema validation tools
- Data consistency checks
- Index health monitoring
- Configuration drift detection

### 4. Import Data Automation
- Automating Import Data wizard workflows
- Batch data source creation
- Template-based configurations
- CI/CD integration

### 5. Monitoring Tools
- Portal metrics automation
- Custom monitoring dashboards
- Alert configuration
- Performance tracking

### 6. Debug Sessions
- Automated debugging workflows
- Error analysis tools
- Performance profiling
- Troubleshooting automation

### 7. Performance Analysis
- Query performance monitoring
- Resource utilization tracking
- Capacity planning tools
- Optimization recommendations

### 8. Portal Workflows
- End-to-end automation
- Workflow orchestration
- Configuration management
- Deployment automation

## Programming Languages

Each sample category is implemented in multiple programming languages:

- **Python** - Using azure-search-documents and azure-mgmt-search SDKs
- **C#** - Using Azure.Search.Documents and Azure.ResourceManager SDKs
- **JavaScript/Node.js** - Using @azure/search-documents and @azure/arm-search SDKs
- **REST API** - Direct HTTP calls with examples

## Sample Structure

Each programming language directory contains:

```
language/
├── README.md                        # Language-specific setup and overview
├── 01_portal_api_integration.*     # Portal workflow automation
├── 02_query_testing.*              # Automated query testing
├── 03_index_validation.*           # Index validation tools
├── 04_import_data_automation.*     # Import wizard automation
├── 05_monitoring_tools.*           # Monitoring and metrics
├── 06_debug_sessions.*             # Debugging automation
├── 07_performance_analysis.*       # Performance monitoring
└── 08_portal_workflows.*           # Complete workflow automation
```

## Prerequisites

Before running these samples, ensure you have:

### Azure Resources
- Azure AI Search service
- Appropriate permissions for management operations
- Sample data sources for testing

### Development Environment
- Programming language runtime
- Required SDKs and packages installed
- Azure CLI (for some automation scenarios)
- Code editor or IDE

### Permissions
- Search Service Contributor role (for management operations)
- Search Index Data Contributor role (for data operations)
- Reader role (for monitoring and metrics)

## Quick Start

### 1. Choose Your Language
Navigate to the appropriate language directory:
- [Python Examples](./python/README.md)
- [C# Examples](./csharp/README.md)
- [JavaScript Examples](./javascript/README.md)
- [REST API Examples](./rest/README.md)

### 2. Set Up Environment
Follow the language-specific setup instructions in each directory's README.

### 3. Configure Authentication
Set up appropriate authentication for management operations.

### 4. Run Samples
Start with basic integration examples and progress to complex workflows.

## Sample Scenarios

### Scenario 1: Development Workflow Automation
**Files:** `01_portal_api_integration.*`, `04_import_data_automation.*`, `08_portal_workflows.*`

Automate development workflows:
- Export portal configurations to code
- Automate resource creation and updates
- Implement CI/CD pipelines
- Synchronize environments

### Scenario 2: Quality Assurance and Testing
**Files:** `02_query_testing.*`, `03_index_validation.*`, `06_debug_sessions.*`

Implement automated testing:
- Validate search functionality
- Test query performance
- Monitor index health
- Automate debugging workflows

### Scenario 3: Operations and Monitoring
**Files:** `05_monitoring_tools.*`, `07_performance_analysis.*`

Build operational tools:
- Monitor service health
- Track performance metrics
- Generate reports
- Implement alerting

## Portal Integration Patterns

### Configuration Export
```python
# Export index configuration from portal
def export_index_config(index_name):
    index = index_client.get_index(index_name)
    config = {
        "name": index.name,
        "fields": [field.as_dict() for field in index.fields],
        "scoring_profiles": index.scoring_profiles,
        "cors_options": index.cors_options
    }
    return config
```

### Automated Resource Creation
```python
# Create resources based on portal templates
def create_from_template(template_config):
    # Create data source
    data_source = create_data_source(template_config['dataSource'])
    
    # Create index
    index = create_index(template_config['index'])
    
    # Create indexer
    indexer = create_indexer(template_config['indexer'])
    
    return data_source, index, indexer
```

### Query Validation
```python
# Validate queries from Search Explorer
def validate_search_explorer_query(query_params):
    try:
        results = search_client.search(**query_params)
        return {
            "valid": True,
            "result_count": len(list(results)),
            "execution_time": results.get_facets()
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
```

## Configuration Templates

### Environment Variables
```bash
# Azure AI Search
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-admin-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net

# Azure Management
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

### Portal Configuration Template
```json
{
  "portalConfig": {
    "searchExplorer": {
      "defaultQueryType": "simple",
      "defaultSearchMode": "any",
      "enableHighlighting": true,
      "enableFaceting": true
    },
    "importWizard": {
      "defaultBatchSize": 1000,
      "enableSkillsets": true,
      "defaultChangeDetection": "HighWaterMark"
    },
    "monitoring": {
      "enableMetrics": true,
      "enableLogs": true,
      "retentionDays": 30
    }
  }
}
```

## Best Practices Demonstrated

### Automation Strategies
- Infrastructure as Code principles
- Configuration management
- Version control integration
- Environment synchronization

### Testing Approaches
- Automated regression testing
- Performance benchmarking
- Configuration validation
- Error handling verification

### Monitoring and Observability
- Comprehensive metrics collection
- Custom dashboard creation
- Proactive alerting
- Performance analysis

## Testing and Validation

### Unit Tests
Each language directory includes tests for:
- API integration functionality
- Configuration validation
- Error handling scenarios
- Performance benchmarks

### Integration Tests
End-to-end tests covering:
- Complete workflow automation
- Portal-to-code transitions
- Multi-environment scenarios
- Error recovery procedures

### Performance Tests
Benchmarking for:
- API operation performance
- Bulk configuration operations
- Monitoring data collection
- Resource utilization

## Workflow Automation Examples

### CI/CD Pipeline Integration
```yaml
# Azure DevOps pipeline example
steps:
- task: AzureCLI@2
  displayName: 'Deploy Search Configuration'
  inputs:
    azureSubscription: 'Azure-Connection'
    scriptType: 'python'
    scriptPath: 'scripts/deploy_search_config.py'
    arguments: '--environment $(Environment) --config-file config.json'
```

### Configuration Drift Detection
```python
# Detect changes between portal and code configurations
def detect_configuration_drift(expected_config, actual_config):
    differences = []
    
    # Compare index schemas
    if expected_config['index'] != actual_config['index']:
        differences.append('Index schema mismatch')
    
    # Compare indexer configurations
    if expected_config['indexer'] != actual_config['indexer']:
        differences.append('Indexer configuration mismatch')
    
    return differences
```

### Automated Health Checks
```python
# Automated health check for search service
def perform_health_check():
    checks = {
        'service_status': check_service_status(),
        'index_health': check_index_health(),
        'indexer_status': check_indexer_status(),
        'query_performance': check_query_performance()
    }
    return checks
```

## Portal Tool Integration

### Search Explorer Automation
- Automated query testing
- Result validation
- Performance monitoring
- Query optimization suggestions

### Import Wizard Automation
- Batch data source creation
- Template-based configurations
- Automated field mapping
- Error handling and recovery

### Monitoring Dashboard Integration
- Custom metric collection
- Alert rule automation
- Report generation
- Capacity planning

## Troubleshooting

### Common Issues
- Authentication and permission problems
- API rate limiting
- Configuration synchronization issues
- Performance bottlenecks

### Debugging Tools
- API response analysis
- Configuration comparison tools
- Performance profiling
- Error tracking and analysis

### Monitoring and Alerting
- Service health monitoring
- Performance degradation detection
- Configuration change tracking
- Error rate monitoring

## Interactive Notebooks

The [notebooks](./notebooks/README.md) directory contains Jupyter notebooks with:
- Interactive portal tool exploration
- Configuration analysis and comparison
- Performance monitoring dashboards
- Workflow automation examples

## Additional Resources

- [Azure AI Search Management REST API](https://docs.microsoft.com/rest/api/searchmanagement/)
- [Azure Search .NET Management SDK](https://docs.microsoft.com/dotnet/api/overview/azure/search/management)
- [Azure CLI for Search](https://docs.microsoft.com/cli/azure/search)
- [PowerShell for Search](https://docs.microsoft.com/powershell/module/az.search/)

## Next Steps

After exploring these samples:
1. Implement automation for your development workflows
2. Build custom monitoring and alerting solutions
3. Integrate with your CI/CD pipelines
4. Explore advanced management scenarios

## Feedback and Support

For questions, issues, or suggestions:
- Review the troubleshooting guides
- Check the Azure AI Search documentation
- Engage with the community forums
- Submit feedback through appropriate channels