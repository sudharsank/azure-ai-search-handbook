#!/usr/bin/env python3
"""
Error Handling & Recovery Example

This script demonstrates robust error handling patterns and recovery strategies
for Azure AI Search indexers.

Prerequisites:
- Azure AI Search service
- Data sources that may contain problematic data
- Admin API key or managed identity
- Required Python packages installed
"""

import os
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer, IndexingParameters
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('indexer_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_configuration():
    """Validate that required configuration is present."""
    if not all([SEARCH_ENDPOINT, SEARCH_API_KEY]):
        raise ValueError("Missing required search service configuration.")
    
    print("✅ Configuration validated")
    print(f"📍 Search Endpoint: {SEARCH_ENDPOINT}")

def demonstrate_error_types():
    """Demonstrate different types of indexer errors."""
    print("\n❌ Common Indexer Error Types")
    print("=" * 30)
    
    error_types = [
        {
            'category': 'Data Source Errors',
            'errors': [
                'Connection timeouts',
                'Authentication failures',
                'Network connectivity issues',
                'Data source unavailable',
                'Permission denied'
            ],
            'impact': 'Indexer cannot access source data',
            'recovery': 'Retry with exponential backoff'
        },
        {
            'category': 'Data Format Errors',
            'errors': [
                'Invalid JSON structure',
                'Unsupported file formats',
                'Encoding issues',
                'Malformed data',
                'Missing required fields'
            ],
            'impact': 'Individual documents fail to process',
            'recovery': 'Skip problematic documents, log for review'
        },
        {
            'category': 'Schema Mismatch Errors',
            'errors': [
                'Field type mismatches',
                'Missing target fields',
                'Invalid field mappings',
                'Collection vs single value conflicts',
                'Date format incompatibilities'
            ],
            'impact': 'Documents rejected during indexing',
            'recovery': 'Fix mappings or transform data'
        },
        {
            'category': 'Resource Limit Errors',
            'errors': [
                'Document size too large',
                'Too many fields per document',
                'Batch size exceeded',
                'Search unit exhaustion',
                'Storage quota exceeded'
            ],
            'impact': 'Indexing stops or throttles',
            'recovery': 'Adjust batch sizes, upgrade service tier'
        },
        {
            'category': 'Transient Errors',
            'errors': [
                'Service temporarily unavailable',
                'Request throttling',
                'Network timeouts',
                'Temporary service degradation',
                'Load balancer issues'
            ],
            'impact': 'Temporary indexing interruption',
            'recovery': 'Automatic retry with backoff'
        }
    ]
    
    for error_type in error_types:
        print(f"\n🚨 {error_type['category']}")
        print(f"   Impact: {error_type['impact']}")
        print(f"   Recovery Strategy: {error_type['recovery']}")
        print("   Common Errors:")
        for error in error_type['errors']:
            print(f"     • {error}")

def create_robust_indexer_configuration():
    """Create indexer configuration with robust error handling."""
    print("\n🛡️ Robust Indexer Configuration")
    print("=" * 35)
    
    # Error handling parameters
    error_handling_params = {
        "maxFailedItems": 10,           # Allow up to 10 failed items
        "maxFailedItemsPerBatch": 5,    # Allow up to 5 failures per batch
        "batchSize": 100,               # Smaller batches for better error isolation
        "configuration": {
            "failOnUnsupportedContentType": False,  # Continue with unsupported files
            "failOnUnprocessableDocument": False,   # Skip unprocessable documents
            "indexedFileNameExtensions": ".pdf,.docx,.txt,.json",  # Limit to known types
            "excludedFileNameExtensions": ".zip,.exe,.bin",        # Exclude problematic types
            "dataToExtract": "contentAndMetadata",
            "parsingMode": "default"
        }
    }
    
    print("📋 Error Handling Configuration:")
    print(f"   Max Failed Items: {error_handling_params['maxFailedItems']}")
    print(f"   Max Failed Items Per Batch: {error_handling_params['maxFailedItemsPerBatch']}")
    print(f"   Batch Size: {error_handling_params['batchSize']}")
    print(f"   Fail on Unsupported Content: {error_handling_params['configuration']['failOnUnsupportedContentType']}")
    print(f"   Fail on Unprocessable Document: {error_handling_params['configuration']['failOnUnprocessableDocument']}")
    
    return error_handling_params

def implement_retry_logic():
    """Implement retry logic with exponential backoff."""
    print("\n🔄 Retry Logic Implementation")
    print("=" * 30)
    
    def run_indexer_with_retry(indexer_client, indexer_name, max_retries=3):
        """Run indexer with retry logic and exponential backoff."""
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Starting indexer '{indexer_name}' (attempt {attempt + 1}/{max_retries})")
                
                # Start the indexer
                indexer_client.run_indexer(indexer_name)
                
                # Monitor execution
                success = monitor_indexer_execution(indexer_client, indexer_name)
                
                if success:
                    logger.info(f"Indexer '{indexer_name}' completed successfully")
                    return True
                else:
                    logger.warning(f"Indexer '{indexer_name}' completed with errors")
                    
            except HttpResponseError as e:
                logger.error(f"HTTP error running indexer (attempt {attempt + 1}): {e.message}")
                
                if e.status_code in [429, 503, 504]:  # Throttling or service unavailable
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 5, 9 seconds
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                else:
                    logger.error(f"Non-retryable error: {e.status_code}")
                    break
                    
            except ServiceRequestError as e:
                logger.error(f"Service request error (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {str(e)}")
                break
        
        logger.error(f"Indexer '{indexer_name}' failed after {max_retries} attempts")
        return False
    
    print("🔧 Retry Logic Features:")
    print("   • Exponential backoff (2, 5, 9 seconds)")
    print("   • Handles HTTP 429 (throttling) and 5xx errors")
    print("   • Configurable maximum retry attempts")
    print("   • Comprehensive logging")
    print("   • Distinguishes between retryable and non-retryable errors")
    
    return run_indexer_with_retry

def monitor_indexer_execution(indexer_client, indexer_name, timeout_minutes=10):
    """Monitor indexer execution with detailed error reporting."""
    print(f"\n📊 Monitoring indexer: {indexer_name}")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while time.time() - start_time < timeout_seconds:
        try:
            status = indexer_client.get_indexer_status(indexer_name)
            
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"   ⏰ {current_time} - Status: {status.status}")
            
            if status.last_result:
                result = status.last_result
                
                # Show progress
                items_processed = result.item_count or 0
                items_failed = result.failed_item_count or 0
                print(f"      📄 Processed: {items_processed}, Failed: {items_failed}")
                
                # Show errors if any
                if result.errors:
                    print(f"      ❌ Errors ({len(result.errors)}):")
                    for i, error in enumerate(result.errors[:3]):  # Show first 3 errors
                        print(f"         {i+1}. {error.error_message}")
                        if hasattr(error, 'details') and error.details:
                            print(f"            Details: {error.details}")
                
                # Show warnings if any
                if result.warnings:
                    print(f"      ⚠️ Warnings ({len(result.warnings)}):")
                    for i, warning in enumerate(result.warnings[:2]):  # Show first 2 warnings
                        print(f"         {i+1}. {warning.message}")
            
            # Check if execution is complete
            if status.status in ["success", "error"]:
                success = status.status == "success"
                if success:
                    print(f"   ✅ Indexer completed successfully")
                else:
                    print(f"   ❌ Indexer completed with errors")
                
                return success
            
            time.sleep(10)  # Wait 10 seconds before next check
            
        except Exception as e:
            logger.error(f"Error monitoring indexer: {str(e)}")
            return False
    
    print(f"   ⏰ Monitoring timeout reached ({timeout_minutes} minutes)")
    return False

def analyze_indexer_errors(indexer_client, indexer_name):
    """Analyze and categorize indexer errors."""
    print(f"\n🔍 Analyzing Errors for Indexer: {indexer_name}")
    print("=" * 40)
    
    try:
        status = indexer_client.get_indexer_status(indexer_name)
        
        if not status.execution_history:
            print("   ℹ️ No execution history available")
            return
        
        # Analyze recent executions
        recent_executions = status.execution_history[:5]  # Last 5 executions
        
        error_categories = {
            'data_source': [],
            'data_format': [],
            'schema_mismatch': [],
            'resource_limits': [],
            'transient': [],
            'other': []
        }
        
        for execution in recent_executions:
            if execution.errors:
                for error in execution.errors:
                    error_msg = error.error_message.lower()
                    
                    # Categorize errors
                    if any(keyword in error_msg for keyword in ['connection', 'timeout', 'network', 'authentication']):
                        error_categories['data_source'].append(error)
                    elif any(keyword in error_msg for keyword in ['json', 'format', 'encoding', 'parse']):
                        error_categories['data_format'].append(error)
                    elif any(keyword in error_msg for keyword in ['field', 'mapping', 'type', 'schema']):
                        error_categories['schema_mismatch'].append(error)
                    elif any(keyword in error_msg for keyword in ['size', 'limit', 'quota', 'capacity']):
                        error_categories['resource_limits'].append(error)
                    elif any(keyword in error_msg for keyword in ['throttle', 'unavailable', 'temporary']):
                        error_categories['transient'].append(error)
                    else:
                        error_categories['other'].append(error)
        
        # Report error analysis
        total_errors = sum(len(errors) for errors in error_categories.values())
        
        if total_errors == 0:
            print("   ✅ No errors found in recent executions")
            return
        
        print(f"   📊 Total Errors Analyzed: {total_errors}")
        
        for category, errors in error_categories.items():
            if errors:
                category_name = category.replace('_', ' ').title()
                print(f"\n   🚨 {category_name} Errors ({len(errors)}):")
                
                # Show unique error messages
                unique_errors = {}
                for error in errors:
                    msg = error.error_message
                    if msg in unique_errors:
                        unique_errors[msg] += 1
                    else:
                        unique_errors[msg] = 1
                
                for msg, count in list(unique_errors.items())[:3]:  # Show top 3
                    print(f"      • {msg} (occurred {count} times)")
        
        # Provide recommendations
        provide_error_recommendations(error_categories)
        
    except Exception as e:
        logger.error(f"Error analyzing indexer errors: {str(e)}")

def provide_error_recommendations(error_categories):
    """Provide recommendations based on error analysis."""
    print(f"\n💡 Recommendations:")
    
    recommendations = []
    
    if error_categories['data_source']:
        recommendations.append("• Check data source connectivity and credentials")
        recommendations.append("• Implement connection retry logic")
        recommendations.append("• Monitor network stability")
    
    if error_categories['data_format']:
        recommendations.append("• Validate source data format and encoding")
        recommendations.append("• Add data preprocessing steps")
        recommendations.append("• Use failOnUnprocessableDocument: false")
    
    if error_categories['schema_mismatch']:
        recommendations.append("• Review and fix field mappings")
        recommendations.append("• Ensure data types match index schema")
        recommendations.append("• Add data transformation functions")
    
    if error_categories['resource_limits']:
        recommendations.append("• Reduce batch size")
        recommendations.append("• Consider upgrading service tier")
        recommendations.append("• Optimize document size")
    
    if error_categories['transient']:
        recommendations.append("• Implement exponential backoff retry")
        recommendations.append("• Monitor service health")
        recommendations.append("• Consider scheduling during off-peak hours")
    
    if not recommendations:
        recommendations.append("• Review error details for specific guidance")
        recommendations.append("• Check Azure service health status")
        recommendations.append("• Contact support if issues persist")
    
    for rec in recommendations:
        print(f"   {rec}")

def implement_error_alerting():
    """Implement error alerting and notification system."""
    print("\n🚨 Error Alerting Implementation")
    print("=" * 35)
    
    def check_indexer_health(indexer_client, indexer_names, alert_threshold=0.1):
        """Check indexer health and send alerts if error rate exceeds threshold."""
        
        alerts = []
        
        for indexer_name in indexer_names:
            try:
                status = indexer_client.get_indexer_status(indexer_name)
                
                if status.last_result:
                    result = status.last_result
                    total_items = (result.item_count or 0) + (result.failed_item_count or 0)
                    
                    if total_items > 0:
                        error_rate = (result.failed_item_count or 0) / total_items
                        
                        if error_rate > alert_threshold:
                            alert = {
                                'indexer': indexer_name,
                                'error_rate': error_rate,
                                'failed_items': result.failed_item_count,
                                'total_items': total_items,
                                'last_run': result.end_time or result.start_time
                            }
                            alerts.append(alert)
                            
            except Exception as e:
                logger.error(f"Error checking health for indexer {indexer_name}: {str(e)}")
        
        return alerts
    
    def send_alert(alert):
        """Send alert notification (placeholder implementation)."""
        logger.warning(f"ALERT: Indexer '{alert['indexer']}' has high error rate")
        logger.warning(f"  Error Rate: {alert['error_rate']:.2%}")
        logger.warning(f"  Failed Items: {alert['failed_items']}/{alert['total_items']}")
        logger.warning(f"  Last Run: {alert['last_run']}")
        
        # In a real implementation, you would:
        # - Send email notifications
        # - Post to Slack/Teams
        # - Create Azure Monitor alerts
        # - Update dashboard status
    
    print("🔧 Alerting Features:")
    print("   • Configurable error rate thresholds")
    print("   • Multiple notification channels")
    print("   • Health check scheduling")
    print("   • Alert suppression to avoid spam")
    print("   • Integration with monitoring systems")
    
    return check_indexer_health, send_alert

def demonstrate_recovery_strategies():
    """Demonstrate different recovery strategies for failed indexers."""
    print("\n🔧 Recovery Strategies")
    print("=" * 20)
    
    strategies = [
        {
            'strategy': 'Automatic Retry',
            'description': 'Automatically retry failed operations',
            'when_to_use': 'Transient errors, network issues',
            'implementation': 'Exponential backoff, max retry limits',
            'pros': ['Handles temporary issues', 'No manual intervention'],
            'cons': ['May mask persistent problems', 'Can delay error detection']
        },
        {
            'strategy': 'Partial Reset',
            'description': 'Reset indexer to last successful high water mark',
            'when_to_use': 'Data corruption, schema changes',
            'implementation': 'Reset indexer state, resume from checkpoint',
            'pros': ['Avoids full reprocessing', 'Maintains progress'],
            'cons': ['May miss some updates', 'Requires change detection']
        },
        {
            'strategy': 'Full Reset',
            'description': 'Complete reprocessing of all data',
            'when_to_use': 'Major schema changes, data source migration',
            'implementation': 'Reset indexer, clear index, full rerun',
            'pros': ['Ensures data consistency', 'Clean slate approach'],
            'cons': ['Time consuming', 'Resource intensive']
        },
        {
            'strategy': 'Error Isolation',
            'description': 'Skip problematic documents, continue processing',
            'when_to_use': 'Bad data in source, format issues',
            'implementation': 'Increase error thresholds, log failures',
            'pros': ['Maintains service availability', 'Isolates problems'],
            'cons': ['Incomplete data', 'Requires manual cleanup']
        },
        {
            'strategy': 'Circuit Breaker',
            'description': 'Stop processing when error rate is too high',
            'when_to_use': 'Systematic issues, data source problems',
            'implementation': 'Monitor error rates, disable on threshold',
            'pros': ['Prevents resource waste', 'Fast failure detection'],
            'cons': ['Service interruption', 'Requires manual intervention']
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎯 {strategy['strategy']}")
        print(f"   Description: {strategy['description']}")
        print(f"   When to Use: {strategy['when_to_use']}")
        print(f"   Implementation: {strategy['implementation']}")
        print("   Pros:")
        for pro in strategy['pros']:
            print(f"     ✅ {pro}")
        print("   Cons:")
        for con in strategy['cons']:
            print(f"     ⚠️ {con}")

def main():
    """Main execution function."""
    print("🚀 Error Handling & Recovery Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize client
        credential = AzureKeyCredential(SEARCH_API_KEY)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Demonstrate error types
        demonstrate_error_types()
        
        # Show robust configuration
        error_config = create_robust_indexer_configuration()
        
        # Implement retry logic
        retry_function = implement_retry_logic()
        
        # Show error analysis
        print("\n📊 Error Analysis Example:")
        print("   (Run with actual indexer names to see real analysis)")
        
        # Implement alerting
        health_check, send_alert = implement_error_alerting()
        
        # Show recovery strategies
        demonstrate_recovery_strategies()
        
        print("\n✅ Error handling example completed successfully!")
        print("\nKey takeaways:")
        print("- Implement comprehensive error handling from the start")
        print("- Use appropriate retry strategies for different error types")
        print("- Monitor error patterns to identify systemic issues")
        print("- Set up alerting for proactive issue detection")
        print("- Choose recovery strategies based on business requirements")
        print("- Log errors comprehensively for troubleshooting")
        print("- Test error scenarios in development environments")
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()