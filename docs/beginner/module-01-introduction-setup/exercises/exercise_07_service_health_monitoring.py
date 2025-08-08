"""
Exercise 7: Service Health Monitoring
Learn to monitor Azure AI Search service health and performance
"""

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from dotenv import load_dotenv

# TODO: Import Azure AI Search libraries
# from azure.search.documents.indexes import SearchIndexClient
# from azure.core.credentials import AzureKeyCredential
# from azure.core.exceptions import AzureError

@dataclass
class HealthCheckResult:
    """Data class for health check results"""
    timestamp: datetime
    service_name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    response_time_ms: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

def perform_basic_health_check(endpoint: str, api_key: str) -> HealthCheckResult:
    """
    Exercise: Perform a basic health check of the Azure AI Search service
    
    Instructions:
    1. Create a SearchIndexClient
    2. Measure response time for getting service statistics
    3. Check if the service is responding correctly
    4. Return a HealthCheckResult with the status
    
    Args:
        endpoint: Azure AI Search service endpoint
        api_key: API key for authentication
        
    Returns:
        HealthCheckResult containing health status
    """
    # TODO: Implement basic health check
    # Measure response time and check service availability
    # Return HealthCheckResult with:
    # - timestamp: current time
    # - service_name: extracted from endpoint
    # - status: 'healthy', 'degraded', or 'unhealthy'
    # - response_time_ms: time taken for the request
    # - details: service statistics and other info
    pass

def monitor_service_performance(endpoint: str, api_key: str, duration_minutes: int = 5) -> List[HealthCheckResult]:
    """
    Exercise: Monitor service performance over time
    
    Instructions:
    1. Perform health checks at regular intervals
    2. Track response times and availability
    3. Detect performance degradation
    4. Return a list of health check results
    
    Args:
        endpoint: Azure AI Search service endpoint
        api_key: API key for authentication
        duration_minutes: How long to monitor (default 5 minutes)
        
    Returns:
        List of HealthCheckResult objects
    """
    # TODO: Implement continuous service monitoring
    # Perform health checks every 30 seconds for the specified duration
    # Track trends in response time and availability
    pass

def analyze_service_metrics(health_results: List[HealthCheckResult]) -> Dict[str, Any]:
    """
    Exercise: Analyze service health metrics
    
    Instructions:
    1. Calculate average, min, max response times
    2. Determine availability percentage
    3. Identify performance trends
    4. Detect anomalies or issues
    5. Return comprehensive analysis
    
    Args:
        health_results: List of health check results
        
    Returns:
        Dict containing service metrics analysis
    """
    # TODO: Implement service metrics analysis
    # Calculate:
    # - Average response time
    # - 95th percentile response time
    # - Availability percentage
    # - Error rate
    # - Performance trends
    # Return structure:
    # {
    #     'summary': {
    #         'total_checks': int,
    #         'successful_checks': int,
    #         'availability_percentage': float,
    #         'average_response_time_ms': float,
    #         'p95_response_time_ms': float
    #     },
    #     'trends': {
    #         'response_time_trend': str,  # 'improving', 'stable', 'degrading'
    #         'availability_trend': str
    #     },
    #     'issues': [str],  # List of detected issues
    #     'recommendations': [str]
    # }
    pass

def create_alerting_system() -> Dict[str, Any]:
    """
    Exercise: Create a simple alerting system for service health
    
    Instructions:
    1. Define alert thresholds for response time and availability
    2. Create functions to check if thresholds are exceeded
    3. Implement alert notification logic
    4. Return alerting system configuration
    
    Returns:
        Dict containing alerting system details
    """
    # TODO: Implement alerting system
    # Define thresholds:
    # - Response time > 5000ms = warning
    # - Response time > 10000ms = critical
    # - Availability < 99% = warning
    # - Availability < 95% = critical
    # Return alerting configuration and functions
    pass

def implement_health_dashboard() -> Dict[str, Any]:
    """
    Exercise: Create a simple health dashboard
    
    Instructions:
    1. Design a text-based dashboard layout
    2. Display current service status
    3. Show key metrics and trends
    4. Include recent alerts and issues
    5. Return dashboard implementation
    
    Returns:
        Dict containing dashboard implementation details
    """
    # TODO: Implement health dashboard
    # Create a text-based dashboard that shows:
    # - Current service status (green/yellow/red)
    # - Key metrics (response time, availability)
    # - Recent trends
    # - Active alerts
    # - Historical data summary
    pass

def test_service_resilience() -> Dict[str, Any]:
    """
    Exercise: Test service resilience under different conditions
    
    Instructions:
    1. Test service behavior with invalid requests
    2. Test response to rate limiting
    3. Simulate network issues
    4. Test recovery from failures
    5. Return resilience test results
    
    Returns:
        Dict containing resilience test results
    """
    # TODO: Implement service resilience testing
    # Test scenarios:
    # - Invalid authentication
    # - Malformed requests
    # - Rate limiting behavior
    # - Network timeout handling
    # - Service recovery patterns
    pass

def create_monitoring_automation() -> Dict[str, Any]:
    """
    Exercise: Create automated monitoring scripts
    
    Instructions:
    1. Create a script that runs health checks automatically
    2. Implement data persistence for historical tracking
    3. Add automated report generation
    4. Include integration with external monitoring systems
    5. Return automation implementation details
    
    Returns:
        Dict containing monitoring automation details
    """
    # TODO: Implement monitoring automation
    # Create automation that:
    # - Runs health checks on schedule
    # - Stores results in files/database
    # - Generates daily/weekly reports
    # - Integrates with monitoring tools
    # - Sends notifications for issues
    pass

def generate_health_report(health_results: List[HealthCheckResult]) -> str:
    """
    Exercise: Generate a comprehensive health report
    
    Instructions:
    1. Create a formatted report with service health summary
    2. Include performance metrics and trends
    3. Add recommendations for improvements
    4. Format the report for easy reading
    5. Return the formatted report
    
    Args:
        health_results: List of health check results
        
    Returns:
        String containing formatted health report
    """
    # TODO: Implement health report generation
    # Generate a report that includes:
    # - Executive summary
    # - Detailed metrics
    # - Performance trends
    # - Issues and recommendations
    # - Historical comparisons
    pass

def implement_predictive_monitoring() -> Dict[str, Any]:
    """
    Exercise: Implement predictive monitoring capabilities
    
    Instructions:
    1. Analyze historical performance data
    2. Identify patterns and trends
    3. Predict potential issues before they occur
    4. Create early warning systems
    5. Return predictive monitoring implementation
    
    Returns:
        Dict containing predictive monitoring details
    """
    # TODO: Implement predictive monitoring
    # This is an advanced topic showing how to:
    # - Analyze performance trends
    # - Predict capacity issues
    # - Identify degradation patterns
    # - Create proactive alerts
    # - Recommend preventive actions
    pass

if __name__ == "__main__":
    print("📊 Service Health Monitoring Exercise")
    print("=" * 40)
    
    print("This exercise teaches you how to monitor Azure AI Search")
    print("service health and implement effective monitoring strategies.\n")
    
    # Load configuration
    load_dotenv()
    endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
    api_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not endpoint or not api_key:
        print("❌ Missing configuration. Please set AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_API_KEY")
        sys.exit(1)
    
    print("🔍 Running Health Monitoring Tests...")
    
    # Test 1: Basic health check
    print("\n1️⃣ Basic Health Check")
    health_result = perform_basic_health_check(endpoint, api_key)
    if health_result:
        status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(health_result.status, "❓")
        print(f"{status_emoji} Service Status: {health_result.status.title()}")
        print(f"Response Time: {health_result.response_time_ms:.2f}ms")
    
    # Test 2: Performance monitoring
    print("\n2️⃣ Performance Monitoring (2 minutes)")
    print("Monitoring service performance... (this will take 2 minutes)")
    performance_results = monitor_service_performance(endpoint, api_key, duration_minutes=2)
    if performance_results:
        print(f"✅ Collected {len(performance_results)} performance samples")
        avg_response = sum(r.response_time_ms for r in performance_results) / len(performance_results)
        print(f"Average Response Time: {avg_response:.2f}ms")
    
    # Test 3: Metrics analysis
    print("\n3️⃣ Service Metrics Analysis")
    if performance_results:
        metrics_analysis = analyze_service_metrics(performance_results)
        if metrics_analysis:
            summary = metrics_analysis.get('summary', {})
            print(f"✅ Analysis completed")
            print(f"Availability: {summary.get('availability_percentage', 0):.1f}%")
            print(f"P95 Response Time: {summary.get('p95_response_time_ms', 0):.2f}ms")
            
            issues = metrics_analysis.get('issues', [])
            if issues:
                print(f"Issues detected: {len(issues)}")
    
    # Test 4: Alerting system
    print("\n4️⃣ Alerting System")
    alerting_system = create_alerting_system()
    if alerting_system:
        print("✅ Alerting system created")
        thresholds = alerting_system.get('thresholds', {})
        print(f"Response time warning: {thresholds.get('response_time_warning_ms', 0)}ms")
        print(f"Availability warning: {thresholds.get('availability_warning_percent', 0)}%")
    
    # Test 5: Health dashboard
    print("\n5️⃣ Health Dashboard")
    dashboard = implement_health_dashboard()
    if dashboard:
        print("✅ Health dashboard implemented")
        if dashboard.get('dashboard_available'):
            print("Dashboard includes:")
            features = dashboard.get('features', [])
            for feature in features[:3]:
                print(f"   • {feature}")
    
    # Test 6: Service resilience testing
    print("\n6️⃣ Service Resilience Testing")
    resilience_results = test_service_resilience()
    if resilience_results:
        print("✅ Resilience testing completed")
        tests_passed = resilience_results.get('tests_passed', 0)
        total_tests = resilience_results.get('total_tests', 0)
        print(f"Tests passed: {tests_passed}/{total_tests}")
    
    # Test 7: Monitoring automation
    print("\n7️⃣ Monitoring Automation")
    automation = create_monitoring_automation()
    if automation:
        print("✅ Monitoring automation implemented")
        if automation.get('scheduled_monitoring'):
            print("   • Scheduled health checks enabled")
            print("   • Automated reporting configured")
    
    # Test 8: Health report generation
    print("\n8️⃣ Health Report Generation")
    if performance_results:
        health_report = generate_health_report(performance_results)
        if health_report:
            print("✅ Health report generated")
            print(f"Report length: {len(health_report)} characters")
    
    # Test 9: Predictive monitoring
    print("\n9️⃣ Predictive Monitoring")
    predictive_monitoring = implement_predictive_monitoring()
    if predictive_monitoring:
        print("✅ Predictive monitoring implemented")
        if predictive_monitoring.get('trend_analysis_available'):
            print("   • Trend analysis enabled")
            print("   • Early warning system configured")
    
    print("\n📚 Monitoring Best Practices:")
    print("1. Monitor key metrics continuously")
    print("2. Set appropriate alert thresholds")
    print("3. Track trends over time")
    print("4. Implement automated health checks")
    print("5. Create comprehensive dashboards")
    print("6. Plan for incident response")
    
    print("\n🎯 Next Steps:")
    print("1. Set up continuous monitoring for your service")
    print("2. Configure alerting for critical issues")
    print("3. Move on to Exercise 8: Performance Optimization")