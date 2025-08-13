#!/usr/bin/env python3
"""
Indexer Scheduling & Automation Example

This script demonstrates how to configure indexer schedules and automation patterns
for Azure AI Search indexers.

Prerequisites:
- Azure AI Search service
- Existing indexers to schedule
- Admin API key or managed identity
- Required Python packages installed
"""

import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    IndexingSchedule, SearchIndexer
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')

def validate_configuration():
    """Validate that required configuration is present."""
    if not all([SEARCH_ENDPOINT, SEARCH_API_KEY]):
        raise ValueError("Missing required search service configuration.")
    
    print("✅ Configuration validated")
    print(f"📍 Search Endpoint: {SEARCH_ENDPOINT}")

def demonstrate_scheduling_patterns():
    """Demonstrate different indexer scheduling patterns."""
    print("\n📅 Common Indexer Scheduling Patterns")
    print("=" * 40)
    
    patterns = [
        {
            'name': 'High-Frequency Updates',
            'interval': timedelta(minutes=15),
            'use_case': 'Real-time data feeds, news, social media',
            'cost': 'High',
            'data_freshness': 'Very High',
            'example_start': datetime.now().replace(second=0, microsecond=0)
        },
        {
            'name': 'Hourly Updates',
            'interval': timedelta(hours=1),
            'use_case': 'E-commerce catalogs, inventory systems',
            'cost': 'Medium-High',
            'data_freshness': 'High',
            'example_start': datetime.now().replace(minute=0, second=0, microsecond=0)
        },
        {
            'name': 'Daily Updates',
            'interval': timedelta(days=1),
            'use_case': 'Document repositories, CRM data',
            'cost': 'Medium',
            'data_freshness': 'Medium',
            'example_start': datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
        },
        {
            'name': 'Weekly Updates',
            'interval': timedelta(days=7),
            'use_case': 'Archive data, reference materials',
            'cost': 'Low',
            'data_freshness': 'Low',
            'example_start': datetime.now().replace(hour=1, minute=0, second=0, microsecond=0)
        }
    ]
    
    for pattern in patterns:
        print(f"\n🔄 {pattern['name']}")
        print(f"   Interval: {pattern['interval']}")
        print(f"   Use Case: {pattern['use_case']}")
        print(f"   Cost Impact: {pattern['cost']}")
        print(f"   Data Freshness: {pattern['data_freshness']}")
        print(f"   Example Start Time: {pattern['example_start']}")
        
        # Calculate next few runs
        next_runs = []
        current_time = pattern['example_start']
        for i in range(3):
            next_runs.append(current_time + (pattern['interval'] * i))
        
        print(f"   Next 3 runs: {', '.join([t.strftime('%H:%M') for t in next_runs])}")
    
    return patterns

def create_scheduled_indexer_examples():
    """Create example indexer schedules for different scenarios."""
    print("\n⚙️ Creating Scheduled Indexer Examples")
    print("=" * 40)
    
    examples = []
    
    # Example 1: E-commerce Product Catalog
    print("\n🛒 E-commerce Product Catalog Indexer:")
    ecommerce_schedule = IndexingSchedule(
        interval=timedelta(hours=2),  # Every 2 hours during business hours
        start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    )
    
    print(f"   Interval: {ecommerce_schedule.interval}")
    print(f"   Start Time: {ecommerce_schedule.start_time} (8 AM)")
    print("   Rationale: Frequent updates for inventory and pricing changes")
    print("   Business Impact: High - affects customer experience and sales")
    
    examples.append(('E-commerce', ecommerce_schedule))
    
    # Example 2: Document Management System
    print("\n📄 Document Management System Indexer:")
    document_schedule = IndexingSchedule(
        interval=timedelta(days=1),
        start_time=datetime.now().replace(hour=2, minute=30, second=0, microsecond=0)
    )
    
    print(f"   Interval: {document_schedule.interval}")
    print(f"   Start Time: {document_schedule.start_time} (2:30 AM)")
    print("   Rationale: Documents change less frequently, off-hours processing")
    print("   Business Impact: Medium - affects search accuracy but not critical")
    
    examples.append(('Documents', document_schedule))
    
    # Example 3: News and Media Content
    print("\n📰 News and Media Content Indexer:")
    news_schedule = IndexingSchedule(
        interval=timedelta(minutes=15),
        start_time=datetime.now().replace(second=0, microsecond=0)
    )
    
    print(f"   Interval: {news_schedule.interval}")
    print(f"   Start Time: {news_schedule.start_time}")
    print("   Rationale: Breaking news requires immediate indexing")
    print("   Business Impact: Critical - affects content relevance and user engagement")
    
    examples.append(('News', news_schedule))
    
    # Example 4: Reference Data (Low Priority)
    print("\n📚 Reference Data Indexer:")
    reference_schedule = IndexingSchedule(
        interval=timedelta(days=7),
        start_time=datetime.now().replace(hour=1, minute=0, second=0, microsecond=0)
    )
    
    print(f"   Interval: {reference_schedule.interval}")
    print(f"   Start Time: {reference_schedule.start_time} (1 AM Sunday)")
    print("   Rationale: Reference data changes infrequently")
    print("   Business Impact: Low - static content with minimal updates")
    
    examples.append(('Reference', reference_schedule))
    
    return examples

def demonstrate_scheduling_best_practices():
    """Demonstrate scheduling best practices and considerations."""
    print("\n💡 Indexer Scheduling Best Practices")
    print("=" * 35)
    
    best_practices = [
        {
            'category': 'Timing Optimization',
            'practices': [
                'Schedule during off-peak hours (2-4 AM)',
                'Avoid overlapping with backup windows',
                'Consider time zones for global applications',
                'Stagger multiple indexers to avoid resource conflicts'
            ]
        },
        {
            'category': 'Performance Considerations',
            'practices': [
                'Use change detection to minimize processing',
                'Adjust batch sizes based on data volume',
                'Monitor execution duration trends',
                'Set appropriate timeout values'
            ]
        },
        {
            'category': 'Cost Management',
            'practices': [
                'Balance frequency with business requirements',
                'Use incremental indexing when possible',
                'Monitor search unit consumption',
                'Consider data source throttling limits'
            ]
        },
        {
            'category': 'Reliability & Monitoring',
            'practices': [
                'Set up alerting for failed executions',
                'Monitor execution history regularly',
                'Implement retry logic for transient failures',
                'Document schedule rationale and dependencies'
            ]
        }
    ]
    
    for category in best_practices:
        print(f"\n🎯 {category['category']}")
        for practice in category['practices']:
            print(f"   • {practice}")
    
    # Create a scheduling decision matrix
    print(f"\n📊 Scheduling Decision Matrix:")
    print("   Data Volatility | Business Criticality | Data Volume | Recommended Frequency")
    print("   Low             | Low                  | Small       | Weekly")
    print("   Medium          | Medium               | Medium      | Daily")
    print("   High            | High                 | Large       | Hourly")
    print("   Very High       | Critical             | Very Large  | 15-30 min")

def apply_schedule_to_indexer(indexer_client, indexer_name, schedule):
    """Apply a schedule to an existing indexer."""
    print(f"\n⚙️ Applying schedule to indexer: {indexer_name}")
    
    try:
        # Get existing indexer
        indexer = indexer_client.get_indexer(indexer_name)
        
        # Update with schedule
        indexer.schedule = schedule
        
        # Update the indexer
        result = indexer_client.create_or_update_indexer(indexer)
        
        print(f"   ✅ Schedule applied successfully")
        print(f"   Interval: {result.schedule.interval}")
        print(f"   Start Time: {result.schedule.start_time}")
        
        return result
        
    except HttpResponseError as e:
        if e.status_code == 404:
            print(f"   ⚠️ Indexer '{indexer_name}' not found")
        else:
            print(f"   ❌ Error applying schedule: {e.message}")
        return None

def monitor_scheduled_indexers(indexer_client):
    """Monitor scheduled indexer performance and execution patterns."""
    print("\n📊 Monitoring Scheduled Indexers")
    print("=" * 30)
    
    try:
        # Get all indexers
        indexers = list(indexer_client.get_indexers())
        
        if not indexers:
            print("⚠️ No indexers found in the search service")
            return []
        
        monitoring_data = []
        
        for indexer in indexers:
            print(f"\n🔍 Analyzing indexer: {indexer.name}")
            
            try:
                status = indexer_client.get_indexer_status(indexer.name)
                
                # Collect basic info
                indexer_info = {
                    'name': indexer.name,
                    'status': status.status,
                    'has_schedule': indexer.schedule is not None,
                    'schedule_interval': str(indexer.schedule.interval) if indexer.schedule else 'Manual',
                    'last_result_status': status.last_result.status if status.last_result else 'None',
                    'execution_count': len(status.execution_history) if status.execution_history else 0
                }
                
                if status.last_result:
                    result = status.last_result
                    indexer_info.update({
                        'items_processed': result.item_count or 0,
                        'items_failed': result.failed_item_count or 0,
                        'last_execution': result.end_time or result.start_time,
                        'execution_duration': (result.end_time - result.start_time).total_seconds() if result.end_time and result.start_time else 0
                    })
                
                monitoring_data.append(indexer_info)
                
                # Display indexer details
                print(f"   Status: {indexer_info['status']}")
                print(f"   Schedule: {indexer_info['schedule_interval']}")
                print(f"   Last Result: {indexer_info['last_result_status']}")
                if 'items_processed' in indexer_info:
                    print(f"   Items Processed: {indexer_info['items_processed']}")
                    print(f"   Execution Duration: {indexer_info['execution_duration']:.1f}s")
                
            except Exception as e:
                print(f"   ❌ Error getting status: {str(e)}")
                continue
        
        return monitoring_data
        
    except Exception as e:
        print(f"❌ Error monitoring indexers: {str(e)}")
        return []

def demonstrate_optimization_strategies():
    """Demonstrate advanced scheduling optimization strategies."""
    print("\n🚀 Advanced Scheduling Optimization Strategies")
    print("=" * 45)
    
    strategies = [
        {
            'name': 'Adaptive Scheduling',
            'description': 'Adjust frequency based on data change patterns',
            'implementation': [
                'Monitor change detection results',
                'Reduce frequency when few changes detected',
                'Increase frequency during high-activity periods',
                'Use Azure Logic Apps for dynamic scheduling'
            ],
            'benefits': 'Optimal balance of freshness and cost'
        },
        {
            'name': 'Tiered Scheduling',
            'description': 'Different schedules for different data priorities',
            'implementation': [
                'Critical data: High frequency (15-30 min)',
                'Important data: Medium frequency (hourly)',
                'Archive data: Low frequency (daily/weekly)',
                'Use separate indexers for each tier'
            ],
            'benefits': 'Resource optimization and cost control'
        },
        {
            'name': 'Event-Driven Indexing',
            'description': 'Trigger indexing based on data source events',
            'implementation': [
                'Use Azure Event Grid for blob storage changes',
                'Implement webhook triggers for database changes',
                'Combine with scheduled baseline runs',
                'Use Azure Functions for event processing'
            ],
            'benefits': 'Near real-time updates with minimal overhead'
        },
        {
            'name': 'Load Balancing',
            'description': 'Distribute indexer execution across time',
            'implementation': [
                'Stagger start times for multiple indexers',
                'Use different intervals to avoid conflicts',
                'Monitor search unit utilization',
                'Implement queue-based execution'
            ],
            'benefits': 'Improved performance and resource utilization'
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎯 {strategy['name']}")
        print(f"   Description: {strategy['description']}")
        print(f"   Benefits: {strategy['benefits']}")
        print("   Implementation:")
        for step in strategy['implementation']:
            print(f"     • {step}")

def troubleshoot_scheduling_issues():
    """Demonstrate troubleshooting techniques for scheduled indexers."""
    print("\n🔧 Common Scheduling Issues and Solutions")
    print("=" * 40)
    
    issues = [
        {
            'issue': 'Indexer Not Running on Schedule',
            'symptoms': [
                'No recent execution history',
                'Status shows as idle',
                'Data not updating as expected'
            ],
            'causes': [
                'Schedule not properly configured',
                'Indexer disabled or in error state',
                'Service quota limits reached',
                'Data source connection issues'
            ],
            'solutions': [
                'Verify schedule configuration',
                'Check indexer status and enable if needed',
                'Review service limits and usage',
                'Test data source connectivity'
            ]
        },
        {
            'issue': 'Execution Timeouts',
            'symptoms': [
                'Indexer stops mid-execution',
                'Partial data processing',
                'Timeout errors in execution history'
            ],
            'causes': [
                'Large batch sizes',
                'Complex data transformations',
                'Slow data source responses',
                'Network connectivity issues'
            ],
            'solutions': [
                'Reduce batch size',
                'Optimize field mappings',
                'Implement data source caching',
                'Increase timeout settings'
            ]
        },
        {
            'issue': 'Resource Conflicts',
            'symptoms': [
                'Multiple indexers failing simultaneously',
                'Performance degradation',
                'Search unit exhaustion'
            ],
            'causes': [
                'Overlapping execution schedules',
                'Insufficient search units',
                'Concurrent indexer limits exceeded'
            ],
            'solutions': [
                'Stagger indexer schedules',
                'Upgrade service tier',
                'Implement execution queuing'
            ]
        }
    ]
    
    for issue in issues:
        print(f"\n❌ {issue['issue']}")
        print("   Symptoms:")
        for symptom in issue['symptoms']:
            print(f"     • {symptom}")
        print("   Common Causes:")
        for cause in issue['causes']:
            print(f"     • {cause}")
        print("   Solutions:")
        for solution in issue['solutions']:
            print(f"     ✅ {solution}")
    
    # Diagnostic checklist
    print(f"\n📋 Scheduling Diagnostic Checklist:")
    checklist = [
        "✓ Verify indexer schedule configuration",
        "✓ Check indexer status and last execution",
        "✓ Review execution history for patterns",
        "✓ Monitor search unit consumption",
        "✓ Test data source connectivity",
        "✓ Validate change detection settings",
        "✓ Check for service limit violations",
        "✓ Review error logs and messages",
        "✓ Verify field mapping configurations",
        "✓ Test manual indexer execution"
    ]
    
    for item in checklist:
        print(f"   {item}")

def main():
    """Main execution function."""
    print("🚀 Indexer Scheduling & Automation Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize client
        credential = AzureKeyCredential(SEARCH_API_KEY)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Demonstrate scheduling patterns
        patterns = demonstrate_scheduling_patterns()
        
        # Create scheduling examples
        schedule_examples = create_scheduled_indexer_examples()
        
        # Show best practices
        demonstrate_scheduling_best_practices()
        
        # Monitor existing indexers
        monitoring_data = monitor_scheduled_indexers(indexer_client)
        
        # Show optimization strategies
        demonstrate_optimization_strategies()
        
        # Troubleshooting guide
        troubleshoot_scheduling_issues()
        
        print("\n✅ Indexer scheduling example completed successfully!")
        print("\nKey takeaways:")
        print("- Balance frequency with cost - more frequent updates cost more resources")
        print("- Use change detection - minimize processing overhead with incremental updates")
        print("- Schedule during off-peak hours - optimize performance and resource usage")
        print("- Monitor execution patterns - track performance trends and adjust accordingly")
        print("- Implement proper error handling - ensure reliable automated operations")
        print("- Consider business requirements - align technical scheduling with business needs")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()