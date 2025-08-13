#!/usr/bin/env python3
"""
Change Detection Strategies Example

This script demonstrates different change detection policies and strategies
for efficient incremental indexing in Azure AI Search.

Prerequisites:
- Azure AI Search service
- Data sources with appropriate change tracking configured
- Admin API key or managed identity
- Required Python packages installed
"""

import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection, SearchIndexerDataSourceType,
    SearchIndexerDataContainer, HighWaterMarkChangeDetectionPolicy,
    SqlIntegratedChangeTrackingPolicy, SearchIndexer
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
SQL_CONNECTION_STRING = os.getenv('SQL_CONNECTION_STRING')
STORAGE_CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')
COSMOS_CONNECTION_STRING = os.getenv('COSMOS_CONNECTION_STRING')

def validate_configuration():
    """Validate that required configuration is present."""
    if not all([SEARCH_ENDPOINT, SEARCH_API_KEY]):
        raise ValueError("Missing required search service configuration.")
    
    print("✅ Configuration validated")
    print(f"📍 Search Endpoint: {SEARCH_ENDPOINT}")

def demonstrate_high_water_mark_policies():
    """Demonstrate High Water Mark change detection policies."""
    print("\n🌊 High Water Mark Change Detection Policies")
    print("=" * 50)
    
    policies = [
        {
            'name': 'SQL Database - LastModified',
            'data_source_type': SearchIndexerDataSourceType.AZURE_SQL,
            'policy': HighWaterMarkChangeDetectionPolicy(
                high_water_mark_column_name="LastModified"
            ),
            'description': 'Uses a datetime column to track changes',
            'requirements': [
                'DateTime column (e.g., LastModified, UpdatedAt)',
                'Column updated on every record change',
                'Column indexed for performance'
            ],
            'pros': [
                'Simple to implement',
                'Works with any datetime column',
                'Good performance with proper indexing'
            ],
            'cons': [
                'Requires application to maintain timestamp',
                'May miss concurrent updates with same timestamp',
                'Requires column to be consistently updated'
            ]
        },
        {
            'name': 'Blob Storage - LastModified',
            'data_source_type': SearchIndexerDataSourceType.AZURE_BLOB,
            'policy': HighWaterMarkChangeDetectionPolicy(
                high_water_mark_column_name="metadata_storage_last_modified"
            ),
            'description': 'Uses blob last modified timestamp',
            'requirements': [
                'Azure Blob Storage',
                'Automatic metadata tracking enabled'
            ],
            'pros': [
                'Automatic timestamp management',
                'No application changes required',
                'Built into blob storage'
            ],
            'cons': [
                'Only detects file-level changes',
                'May not detect metadata-only changes',
                'Dependent on storage service timestamps'
            ]
        },
        {
            'name': 'Cosmos DB - Timestamp',
            'data_source_type': SearchIndexerDataSourceType.COSMOS_DB,
            'policy': HighWaterMarkChangeDetectionPolicy(
                high_water_mark_column_name="_ts"
            ),
            'description': 'Uses Cosmos DB internal timestamp',
            'requirements': [
                'Azure Cosmos DB',
                'Access to _ts system property'
            ],
            'pros': [
                'Automatic timestamp management',
                'Guaranteed uniqueness and ordering',
                'Built into Cosmos DB'
            ],
            'cons': [
                'Limited to Cosmos DB',
                'Timestamp is in epoch format',
                'May require query modifications'
            ]
        }
    ]
    
    for policy_info in policies:
        print(f"\n📋 {policy_info['name']}")
        print(f"   Description: {policy_info['description']}")
        print(f"   Column: {policy_info['policy'].high_water_mark_column_name}")
        
        print("   Requirements:")
        for req in policy_info['requirements']:
            print(f"     • {req}")
        
        print("   Pros:")
        for pro in policy_info['pros']:
            print(f"     ✅ {pro}")
        
        print("   Cons:")
        for con in policy_info['cons']:
            print(f"     ⚠️ {con}")

def demonstrate_sql_integrated_change_tracking():
    """Demonstrate SQL Integrated Change Tracking policy."""
    print("\n🔄 SQL Integrated Change Tracking")
    print("=" * 40)
    
    print("SQL Server Change Tracking provides the most efficient change detection for SQL databases.")
    
    # Example policy
    policy = SqlIntegratedChangeTrackingPolicy()
    
    print(f"\nPolicy Configuration:")
    print(f"   Type: {type(policy).__name__}")
    print(f"   Description: Uses SQL Server's built-in change tracking")
    
    print(f"\nSQL Server Setup Requirements:")
    requirements = [
        "Enable change tracking on database: ALTER DATABASE [YourDB] SET CHANGE_TRACKING = ON",
        "Enable change tracking on table: ALTER TABLE [YourTable] ENABLE CHANGE_TRACKING",
        "Ensure proper permissions for indexer service",
        "Consider retention period for change tracking data"
    ]
    
    for i, req in enumerate(requirements, 1):
        print(f"   {i}. {req}")
    
    print(f"\nBenefits:")
    benefits = [
        "Most efficient - only changed rows are processed",
        "Handles deletes automatically",
        "No application changes required",
        "Built-in conflict resolution",
        "Minimal storage overhead"
    ]
    
    for benefit in benefits:
        print(f"   ✅ {benefit}")
    
    print(f"\nConsiderations:")
    considerations = [
        "Only available for SQL Server/Azure SQL",
        "Requires database-level configuration",
        "May impact database performance slightly",
        "Change tracking data has retention limits"
    ]
    
    for consideration in considerations:
        print(f"   ⚠️ {consideration}")

def create_change_detection_examples(indexer_client):
    """Create example data sources with different change detection policies."""
    print("\n🛠️ Creating Change Detection Examples")
    print("=" * 40)
    
    examples = []
    
    # SQL with High Water Mark
    if SQL_CONNECTION_STRING:
        print("\n📊 Creating SQL data source with High Water Mark...")
        try:
            sql_datasource = SearchIndexerDataSourceConnection(
                name="sql-highwatermark-example",
                type=SearchIndexerDataSourceType.AZURE_SQL,
                connection_string=SQL_CONNECTION_STRING,
                container=SearchIndexerDataContainer(name="Hotels"),
                data_change_detection_policy=HighWaterMarkChangeDetectionPolicy(
                    high_water_mark_column_name="LastModified"
                ),
                description="SQL data source with LastModified change detection"
            )
            
            result = indexer_client.create_or_update_data_source_connection(sql_datasource)
            examples.append(('SQL High Water Mark', result))
            print(f"   ✅ Created: {result.name}")
            
        except HttpResponseError as e:
            print(f"   ❌ Error: {e.message}")
    
    # SQL with Integrated Change Tracking
    if SQL_CONNECTION_STRING:
        print("\n🔄 Creating SQL data source with Integrated Change Tracking...")
        try:
            sql_ct_datasource = SearchIndexerDataSourceConnection(
                name="sql-changetracking-example",
                type=SearchIndexerDataSourceType.AZURE_SQL,
                connection_string=SQL_CONNECTION_STRING,
                container=SearchIndexerDataContainer(name="Hotels"),
                data_change_detection_policy=SqlIntegratedChangeTrackingPolicy(),
                description="SQL data source with integrated change tracking"
            )
            
            result = indexer_client.create_or_update_data_source_connection(sql_ct_datasource)
            examples.append(('SQL Integrated Change Tracking', result))
            print(f"   ✅ Created: {result.name}")
            
        except HttpResponseError as e:
            print(f"   ❌ Error: {e.message}")
    
    # Blob Storage with LastModified
    if STORAGE_CONNECTION_STRING:
        print("\n📁 Creating Blob data source with LastModified...")
        try:
            blob_datasource = SearchIndexerDataSourceConnection(
                name="blob-lastmodified-example",
                type=SearchIndexerDataSourceType.AZURE_BLOB,
                connection_string=STORAGE_CONNECTION_STRING,
                container=SearchIndexerDataContainer(name="documents"),
                data_change_detection_policy=HighWaterMarkChangeDetectionPolicy(
                    high_water_mark_column_name="metadata_storage_last_modified"
                ),
                description="Blob data source with LastModified change detection"
            )
            
            result = indexer_client.create_or_update_data_source_connection(blob_datasource)
            examples.append(('Blob LastModified', result))
            print(f"   ✅ Created: {result.name}")
            
        except HttpResponseError as e:
            print(f"   ❌ Error: {e.message}")
    
    return examples

def demonstrate_change_detection_behavior(indexer_client, examples):
    """Demonstrate how change detection works in practice."""
    print("\n🔍 Change Detection Behavior Analysis")
    print("=" * 40)
    
    for name, datasource in examples:
        print(f"\n📋 Analyzing: {name}")
        print(f"   Data Source: {datasource.name}")
        print(f"   Type: {datasource.type}")
        
        policy = datasource.data_change_detection_policy
        if policy:
            policy_type = type(policy).__name__
            print(f"   Change Detection: {policy_type}")
            
            if hasattr(policy, 'high_water_mark_column_name'):
                print(f"   High Water Mark Column: {policy.high_water_mark_column_name}")
            
            # Explain behavior
            if policy_type == "HighWaterMarkChangeDetectionPolicy":
                print("   Behavior:")
                print("     • First run: Processes all records")
                print("     • Subsequent runs: Only processes records with timestamp > last processed")
                print("     • Efficient for append-mostly data")
                print("     • May miss updates if timestamp doesn't change")
                
            elif policy_type == "SqlIntegratedChangeTrackingPolicy":
                print("   Behavior:")
                print("     • First run: Processes all records")
                print("     • Subsequent runs: Uses SQL change tracking to find changes")
                print("     • Handles inserts, updates, and deletes")
                print("     • Most efficient for SQL data sources")
        else:
            print("   Change Detection: None (full reprocessing each run)")

def demonstrate_performance_comparison():
    """Compare performance characteristics of different change detection strategies."""
    print("\n📊 Performance Comparison")
    print("=" * 30)
    
    comparison_data = [
        {
            'strategy': 'No Change Detection',
            'first_run': 'Full scan',
            'subsequent_runs': 'Full scan',
            'efficiency': 'Low',
            'resource_usage': 'High',
            'best_for': 'Small datasets, infrequent updates'
        },
        {
            'strategy': 'High Water Mark',
            'first_run': 'Full scan',
            'subsequent_runs': 'Incremental',
            'efficiency': 'Medium-High',
            'resource_usage': 'Low-Medium',
            'best_for': 'Append-heavy workloads, timestamped data'
        },
        {
            'strategy': 'SQL Integrated Change Tracking',
            'first_run': 'Full scan',
            'subsequent_runs': 'Changed rows only',
            'efficiency': 'Very High',
            'resource_usage': 'Very Low',
            'best_for': 'SQL databases with frequent updates'
        }
    ]
    
    for data in comparison_data:
        print(f"\n🎯 {data['strategy']}")
        print(f"   First Run: {data['first_run']}")
        print(f"   Subsequent Runs: {data['subsequent_runs']}")
        print(f"   Efficiency: {data['efficiency']}")
        print(f"   Resource Usage: {data['resource_usage']}")
        print(f"   Best For: {data['best_for']}")

def demonstrate_best_practices():
    """Demonstrate best practices for change detection."""
    print("\n💡 Change Detection Best Practices")
    print("=" * 35)
    
    practices = [
        {
            'category': 'Column Selection',
            'practices': [
                'Use indexed columns for high water mark',
                'Ensure timestamp columns are consistently updated',
                'Consider timezone implications for datetime columns',
                'Use monotonically increasing values when possible'
            ]
        },
        {
            'category': 'Performance Optimization',
            'practices': [
                'Index the change detection column',
                'Use appropriate data types (datetime2 vs datetime)',
                'Consider partitioning for large tables',
                'Monitor change tracking overhead'
            ]
        },
        {
            'category': 'Data Consistency',
            'practices': [
                'Ensure atomic updates to data and timestamp',
                'Handle clock skew in distributed systems',
                'Consider using triggers for automatic timestamp updates',
                'Test with concurrent updates'
            ]
        },
        {
            'category': 'Monitoring',
            'practices': [
                'Monitor indexer execution frequency',
                'Track change detection effectiveness',
                'Alert on change detection failures',
                'Monitor high water mark progression'
            ]
        }
    ]
    
    for category in practices:
        print(f"\n🎯 {category['category']}")
        for practice in category['practices']:
            print(f"   • {practice}")

def cleanup_examples(indexer_client, examples):
    """Clean up created example data sources."""
    print("\n🧹 Cleanup Options")
    print("=" * 20)
    
    print("To clean up the example data sources:")
    for name, datasource in examples:
        print(f"   indexer_client.delete_data_source_connection('{datasource.name}')")

def main():
    """Main execution function."""
    print("🚀 Change Detection Strategies Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize client
        credential = AzureKeyCredential(SEARCH_API_KEY)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Demonstrate different policies
        demonstrate_high_water_mark_policies()
        demonstrate_sql_integrated_change_tracking()
        
        # Create examples (if data sources are available)
        examples = create_change_detection_examples(indexer_client)
        
        if examples:
            # Analyze behavior
            demonstrate_change_detection_behavior(indexer_client, examples)
            
            # Show cleanup options
            cleanup_examples(indexer_client, examples)
        
        # Performance comparison
        demonstrate_performance_comparison()
        
        # Best practices
        demonstrate_best_practices()
        
        print("\n✅ Change detection strategies example completed!")
        print("\nKey takeaways:")
        print("- Choose change detection strategy based on data source capabilities")
        print("- SQL Integrated Change Tracking is most efficient for SQL databases")
        print("- High Water Mark works well for timestamped data")
        print("- Proper indexing is crucial for performance")
        print("- Monitor change detection effectiveness regularly")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()