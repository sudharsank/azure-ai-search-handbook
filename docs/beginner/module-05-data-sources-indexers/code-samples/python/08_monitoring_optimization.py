#!/usr/bin/env python3
"""
Performance Monitoring & Optimization Example

This script demonstrates how to monitor indexer performance and implement
optimization strategies for Azure AI Search indexers.

Prerequisites:
- Azure AI Search service
- Running indexers to monitor
- Admin API key or managed identity
- Required Python packages installed
"""

import os
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexerClient
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

def collect_performance_metrics(indexer_client, indexer_name):
    """Collect comprehensive performance metrics for an indexer."""
    print(f"\n📊 Collecting Performance Metrics: {indexer_name}")
    print("=" * 50)
    
    try:
        status = indexer_client.get_indexer_status(indexer_name)
        
        if not status.execution_history:
            print("   ⚠️ No execution history available")
            return None
        
        metrics = {
            'indexer_name': indexer_name,
            'current_status': status.status,
            'executions': [],
            'summary': {}
        }
        
        # Analyze execution history
        for execution in status.execution_history:
            execution_metrics = {
                'start_time': execution.start_time,
                'end_time': execution.end_time,
                'status': execution.status,
                'items_processed': execution.item_count or 0,
                'items_failed': execution.failed_item_count or 0,
                'error_count': len(execution.errors) if execution.errors else 0,
                'warning_count': len(execution.warnings) if execution.warnings else 0
            }
            
            # Calculate duration
            if execution.start_time and execution.end_time:
                duration = execution.end_time - execution.start_time
                execution_metrics['duration_seconds'] = duration.total_seconds()
                
                # Calculate throughput
                if execution_metrics['duration_seconds'] > 0 and execution_metrics['items_processed'] > 0:
                    execution_metrics['throughput_items_per_second'] = (
                        execution_metrics['items_processed'] / execution_metrics['duration_seconds']
                    )
            
            metrics['executions'].append(execution_metrics)
        
        # Calculate summary statistics
        if metrics['executions']:
            successful_executions = [e for e in metrics['executions'] if e['status'] == 'success']
            
            metrics['summary'] = {
                'total_executions': len(metrics['executions']),
                'successful_executions': len(successful_executions),
                'success_rate': len(successful_executions) / len(metrics['executions']),
                'total_items_processed': sum(e['items_processed'] for e in metrics['executions']),
                'total_items_failed': sum(e['items_failed'] for e in metrics['executions']),
                'total_errors': sum(e['error_count'] for e in metrics['executions']),
                'total_warnings': sum(e['warning_count'] for e in metrics['executions'])
            }
            
            # Calculate average metrics for successful executions
            if successful_executions:
                durations = [e['duration_seconds'] for e in successful_executions if 'duration_seconds' in e]
                throughputs = [e['throughput_items_per_second'] for e in successful_executions if 'throughput_items_per_second' in e]
                
                if durations:
                    metrics['summary']['avg_duration_seconds'] = sum(durations) / len(durations)
                    metrics['summary']['min_duration_seconds'] = min(durations)
                    metrics['summary']['max_duration_seconds'] = max(durations)
                
                if throughputs:
                    metrics['summary']['avg_throughput_items_per_second'] = sum(throughputs) / len(throughputs)
                    metrics['summary']['min_throughput_items_per_second'] = min(throughputs)
                    metrics['summary']['max_throughput_items_per_second'] = max(throughputs)
        
        # Display metrics
        display_performance_metrics(metrics)
        
        return metrics
        
    except HttpResponseError as e:
        print(f"   ❌ Error collecting metrics: {e.message}")
        return None

def display_performance_metrics(metrics):
    """Display performance metrics in a readable format."""
    print(f"\n📈 Performance Summary for {metrics['indexer_name']}:")
    
    summary = metrics['summary']
    
    # Basic statistics
    print(f"   Current Status: {metrics['current_status']}")
    print(f"   Total Executions: {summary.get('total_executions', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1%}")
    print(f"   Items Processed: {summary.get('total_items_processed', 0):,}")
    print(f"   Items Failed: {summary.get('total_items_failed', 0):,}")
    print(f"   Total Errors: {summary.get('total_errors', 0)}")
    print(f"   Total Warnings: {summary.get('total_warnings', 0)}")
    
    # Performance metrics
    if 'avg_duration_seconds' in summary:
        print(f"\n⏱️ Execution Time Metrics:")
        print(f"   Average Duration: {summary['avg_duration_seconds']:.1f} seconds")
        print(f"   Min Duration: {summary['min_duration_seconds']:.1f} seconds")
        print(f"   Max Duration: {summary['max_duration_seconds']:.1f} seconds")
    
    if 'avg_throughput_items_per_second' in summary:
        print(f"\n🚀 Throughput Metrics:")
        print(f"   Average Throughput: {summary['avg_throughput_items_per_second']:.2f} items/sec")
        print(f"   Min Throughput: {summary['min_throughput_items_per_second']:.2f} items/sec")
        print(f"   Max Throughput: {summary['max_throughput_items_per_second']:.2f} items/sec")
    
    # Recent execution trend
    if len(metrics['executions']) >= 3:
        recent_executions = metrics['executions'][:3]  # Last 3 executions
        print(f"\n📊 Recent Execution Trend:")
        for i, execution in enumerate(recent_executions):
            status_icon = "✅" if execution['status'] == 'success' else "❌"
            duration = execution.get('duration_seconds', 0)
            throughput = execution.get('throughput_items_per_second', 0)
            print(f"   {i+1}. {status_icon} {execution['items_processed']} items in {duration:.1f}s ({throughput:.2f} items/sec)")

def analyze_performance_trends(indexer_client, indexer_names):
    """Analyze performance trends across multiple indexers."""
    print(f"\n📈 Performance Trend Analysis")
    print("=" * 30)
    
    all_metrics = []
    
    for indexer_name in indexer_names:
        metrics = collect_performance_metrics(indexer_client, indexer_name)
        if metrics:
            all_metrics.append(metrics)
    
    if not all_metrics:
        print("   ⚠️ No metrics available for analysis")
        return
    
    # Compare indexers
    print(f"\n🔍 Indexer Comparison:")
    print(f"{'Indexer':<25} {'Success Rate':<12} {'Avg Duration':<12} {'Avg Throughput':<15}")
    print("-" * 70)
    
    for metrics in all_metrics:
        name = metrics['indexer_name'][:24]  # Truncate long names
        success_rate = metrics['summary'].get('success_rate', 0)
        avg_duration = metrics['summary'].get('avg_duration_seconds', 0)
        avg_throughput = metrics['summary'].get('avg_throughput_items_per_second', 0)
        
        print(f"{name:<25} {success_rate:<11.1%} {avg_duration:<11.1f}s {avg_throughput:<14.2f}")
    
    # Identify performance issues
    identify_performance_issues(all_metrics)

def identify_performance_issues(all_metrics):
    """Identify potential performance issues across indexers."""
    print(f"\n🚨 Performance Issue Detection:")
    
    issues_found = False
    
    for metrics in all_metrics:
        indexer_name = metrics['indexer_name']
        summary = metrics['summary']
        
        issues = []
        
        # Check success rate
        success_rate = summary.get('success_rate', 1.0)
        if success_rate < 0.95:  # Less than 95% success rate
            issues.append(f"Low success rate: {success_rate:.1%}")
        
        # Check error rate
        total_items = summary.get('total_items_processed', 0) + summary.get('total_items_failed', 0)
        if total_items > 0:
            error_rate = summary.get('total_items_failed', 0) / total_items
            if error_rate > 0.05:  # More than 5% error rate
                issues.append(f"High error rate: {error_rate:.1%}")
        
        # Check throughput consistency
        if 'min_throughput_items_per_second' in summary and 'max_throughput_items_per_second' in summary:
            min_throughput = summary['min_throughput_items_per_second']
            max_throughput = summary['max_throughput_items_per_second']
            if max_throughput > 0 and (max_throughput - min_throughput) / max_throughput > 0.5:
                issues.append("Inconsistent throughput (>50% variation)")
        
        # Check execution duration trends
        if len(metrics['executions']) >= 3:
            recent_durations = [
                e.get('duration_seconds', 0) 
                for e in metrics['executions'][:3] 
                if 'duration_seconds' in e
            ]
            if len(recent_durations) >= 2:
                if recent_durations[0] > recent_durations[-1] * 1.5:  # 50% increase
                    issues.append("Execution time increasing")
        
        if issues:
            issues_found = True
            print(f"\n   ⚠️ {indexer_name}:")
            for issue in issues:
                print(f"      • {issue}")
    
    if not issues_found:
        print("   ✅ No significant performance issues detected")

def demonstrate_optimization_strategies():
    """Demonstrate various optimization strategies for indexers."""
    print(f"\n🚀 Optimization Strategies")
    print("=" * 25)
    
    strategies = [
        {
            'category': 'Batch Size Optimization',
            'description': 'Adjust batch size based on data characteristics',
            'techniques': [
                'Start with default batch size (1000 for SQL, 100 for blobs)',
                'Increase batch size for small documents',
                'Decrease batch size for large documents or complex processing',
                'Monitor memory usage and adjust accordingly',
                'Test different batch sizes and measure throughput'
            ],
            'code_example': '''
# Optimize batch size based on document size
if avg_document_size < 1024:  # Small documents
    batch_size = 2000
elif avg_document_size > 10240:  # Large documents
    batch_size = 50
else:
    batch_size = 1000  # Default
            '''
        },
        {
            'category': 'Field Mapping Optimization',
            'description': 'Optimize field mappings for better performance',
            'techniques': [
                'Use only necessary field mappings',
                'Avoid complex mapping functions when possible',
                'Pre-process data at source when feasible',
                'Use built-in functions instead of custom logic',
                'Minimize the number of target fields'
            ],
            'code_example': '''
# Efficient field mapping
field_mappings = [
    FieldMapping(source_field_name="id", target_field_name="id"),
    FieldMapping(source_field_name="title", target_field_name="title"),
    # Avoid complex transformations in high-volume scenarios
]
            '''
        },
        {
            'category': 'Change Detection Optimization',
            'description': 'Optimize change detection for incremental updates',
            'techniques': [
                'Use SQL Integrated Change Tracking when possible',
                'Ensure change detection columns are indexed',
                'Use appropriate high water mark columns',
                'Monitor change detection effectiveness',
                'Consider partition-based processing for large datasets'
            ],
            'code_example': '''
# Efficient change detection
change_policy = SqlIntegratedChangeTrackingPolicy()
# OR for high water mark
change_policy = HighWaterMarkChangeDetectionPolicy(
    high_water_mark_column_name="LastModified"  # Ensure this is indexed
)
            '''
        },
        {
            'category': 'Resource Management',
            'description': 'Optimize resource usage and allocation',
            'techniques': [
                'Schedule indexers during off-peak hours',
                'Stagger multiple indexer executions',
                'Monitor search unit consumption',
                'Use appropriate service tier for workload',
                'Implement connection pooling for data sources'
            ],
            'code_example': '''
# Stagger indexer schedules
indexer1_schedule = IndexingSchedule(
    interval=timedelta(hours=1),
    start_time=datetime.now().replace(minute=0)
)
indexer2_schedule = IndexingSchedule(
    interval=timedelta(hours=1),
    start_time=datetime.now().replace(minute=15)  # 15 min offset
)
            '''
        },
        {
            'category': 'Error Handling Optimization',
            'description': 'Optimize error handling for better performance',
            'techniques': [
                'Set appropriate error thresholds',
                'Use failOnUnprocessableDocument: false for mixed content',
                'Implement circuit breaker patterns',
                'Monitor error patterns and adjust accordingly',
                'Pre-validate data quality when possible'
            ],
            'code_example': '''
# Optimized error handling
parameters = {
    "maxFailedItems": 100,  # Allow some failures
    "maxFailedItemsPerBatch": 10,
    "configuration": {
        "failOnUnprocessableDocument": False,
        "failOnUnsupportedContentType": False
    }
}
            '''
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎯 {strategy['category']}")
        print(f"   Description: {strategy['description']}")
        print("   Techniques:")
        for technique in strategy['techniques']:
            print(f"     • {technique}")
        
        if 'code_example' in strategy:
            print("   Code Example:")
            for line in strategy['code_example'].strip().split('\n'):
                print(f"     {line}")

def create_performance_dashboard(all_metrics):
    """Create a simple performance dashboard."""
    print(f"\n📊 Performance Dashboard")
    print("=" * 25)
    
    if not all_metrics:
        print("   ⚠️ No metrics available for dashboard")
        return
    
    # Overall statistics
    total_executions = sum(m['summary'].get('total_executions', 0) for m in all_metrics)
    total_items_processed = sum(m['summary'].get('total_items_processed', 0) for m in all_metrics)
    total_errors = sum(m['summary'].get('total_errors', 0) for m in all_metrics)
    
    print(f"📈 Overall Statistics:")
    print(f"   Total Indexers: {len(all_metrics)}")
    print(f"   Total Executions: {total_executions}")
    print(f"   Total Items Processed: {total_items_processed:,}")
    print(f"   Total Errors: {total_errors}")
    
    if total_items_processed > 0:
        overall_error_rate = total_errors / total_items_processed
        print(f"   Overall Error Rate: {overall_error_rate:.2%}")
    
    # Top performers
    print(f"\n🏆 Top Performers:")
    
    # Sort by throughput
    throughput_sorted = sorted(
        [m for m in all_metrics if 'avg_throughput_items_per_second' in m['summary']],
        key=lambda x: x['summary']['avg_throughput_items_per_second'],
        reverse=True
    )
    
    if throughput_sorted:
        print("   Highest Throughput:")
        for i, metrics in enumerate(throughput_sorted[:3]):
            throughput = metrics['summary']['avg_throughput_items_per_second']
            print(f"     {i+1}. {metrics['indexer_name']}: {throughput:.2f} items/sec")
    
    # Sort by success rate
    success_sorted = sorted(
        all_metrics,
        key=lambda x: x['summary'].get('success_rate', 0),
        reverse=True
    )
    
    print("   Highest Success Rate:")
    for i, metrics in enumerate(success_sorted[:3]):
        success_rate = metrics['summary'].get('success_rate', 0)
        print(f"     {i+1}. {metrics['indexer_name']}: {success_rate:.1%}")

def generate_optimization_recommendations(all_metrics):
    """Generate specific optimization recommendations based on metrics."""
    print(f"\n💡 Optimization Recommendations")
    print("=" * 35)
    
    recommendations = []
    
    for metrics in all_metrics:
        indexer_name = metrics['indexer_name']
        summary = metrics['summary']
        
        # Low throughput recommendations
        avg_throughput = summary.get('avg_throughput_items_per_second', 0)
        if avg_throughput > 0 and avg_throughput < 1.0:  # Less than 1 item per second
            recommendations.append({
                'indexer': indexer_name,
                'issue': 'Low throughput',
                'recommendation': 'Consider increasing batch size or optimizing field mappings'
            })
        
        # High error rate recommendations
        total_items = summary.get('total_items_processed', 0) + summary.get('total_items_failed', 0)
        if total_items > 0:
            error_rate = summary.get('total_items_failed', 0) / total_items
            if error_rate > 0.05:
                recommendations.append({
                    'indexer': indexer_name,
                    'issue': 'High error rate',
                    'recommendation': 'Review data quality and adjust error handling parameters'
                })
        
        # Long execution time recommendations
        avg_duration = summary.get('avg_duration_seconds', 0)
        if avg_duration > 3600:  # More than 1 hour
            recommendations.append({
                'indexer': indexer_name,
                'issue': 'Long execution time',
                'recommendation': 'Consider using change detection or reducing batch size'
            })
        
        # Inconsistent performance recommendations
        if 'min_throughput_items_per_second' in summary and 'max_throughput_items_per_second' in summary:
            min_throughput = summary['min_throughput_items_per_second']
            max_throughput = summary['max_throughput_items_per_second']
            if max_throughput > 0 and (max_throughput - min_throughput) / max_throughput > 0.5:
                recommendations.append({
                    'indexer': indexer_name,
                    'issue': 'Inconsistent performance',
                    'recommendation': 'Check for resource contention or data source throttling'
                })
    
    if recommendations:
        for rec in recommendations:
            print(f"\n🎯 {rec['indexer']}:")
            print(f"   Issue: {rec['issue']}")
            print(f"   Recommendation: {rec['recommendation']}")
    else:
        print("   ✅ No specific optimization recommendations at this time")
        print("   Continue monitoring performance trends for future optimization opportunities")

def main():
    """Main execution function."""
    print("🚀 Performance Monitoring & Optimization Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize client
        credential = AzureKeyCredential(SEARCH_API_KEY)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Get list of indexers
        try:
            indexers = list(indexer_client.get_indexers())
            indexer_names = [indexer.name for indexer in indexers]
            
            if not indexer_names:
                print("⚠️ No indexers found. Create some indexers first to see monitoring in action.")
                indexer_names = ["example-indexer"]  # Use example for demonstration
            
        except Exception as e:
            print(f"⚠️ Could not retrieve indexers: {str(e)}")
            indexer_names = ["example-indexer"]  # Use example for demonstration
        
        print(f"📊 Found {len(indexer_names)} indexer(s) to monitor")
        
        # Collect metrics for all indexers
        all_metrics = []
        for indexer_name in indexer_names[:3]:  # Limit to first 3 for demo
            metrics = collect_performance_metrics(indexer_client, indexer_name)
            if metrics:
                all_metrics.append(metrics)
        
        if all_metrics:
            # Analyze trends
            analyze_performance_trends(indexer_client, [m['indexer_name'] for m in all_metrics])
            
            # Create dashboard
            create_performance_dashboard(all_metrics)
            
            # Generate recommendations
            generate_optimization_recommendations(all_metrics)
        
        # Show optimization strategies
        demonstrate_optimization_strategies()
        
        print("\n✅ Performance monitoring example completed successfully!")
        print("\nKey takeaways:")
        print("- Monitor indexer performance regularly to identify trends")
        print("- Use metrics to make data-driven optimization decisions")
        print("- Optimize batch sizes based on document characteristics")
        print("- Implement proper change detection for incremental updates")
        print("- Schedule indexers to avoid resource conflicts")
        print("- Set appropriate error handling thresholds")
        print("- Create dashboards for ongoing performance visibility")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()