"""
Azure AI Search Troubleshooting Utilities - Module 1 Code Sample
============================================================

This script provides comprehensive troubleshooting tools for common Azure AI Search
connection and configuration issues. It helps beginners diagnose and fix problems.

Learning Objectives:
- Learn systematic troubleshooting approaches
- Understand common Azure AI Search connection issues
- Practice diagnostic techniques and error analysis
- Explore network connectivity and authentication debugging

Prerequisites:
- Basic Azure AI Search configuration attempted
- Python environment with required packages
- Access to Azure AI Search service (for connectivity tests)

Author: Azure AI Search Handbook
Module: Beginner - Module 1: Introduction and Setup
"""

import os
import sys
import json
import time
import socket
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

# Azure AI Search SDK imports
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import (
    AzureError, ClientAuthenticationError, ResourceNotFoundError,
    ServiceRequestError, HttpResponseError
)

# Standard library imports
import requests
from dotenv import load_dotenv

# Add setup directory to path for utility imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'setup'))


@dataclass
class DiagnosticResult:
    """Container for diagnostic test results."""
    test_name: str
    passed: bool
    message: str
    details: Dict[str, Any]
    error_type: Optional[str]
    fix_suggestions: List[str]
    execution_time: float


class AzureSearchTroubleshooter:
    """
    Comprehensive troubleshooting toolkit for Azure AI Search issues.
    
    This class provides systematic diagnostic tools to identify and
    resolve common connection, authentication, and configuration problems.
    """
    
    def __init__(self):
        """Initialize the troubleshooter with configuration."""
        self.results: List[DiagnosticResult] = []
        self.config = self._load_configuration()
        
        print("🔧 Azure AI Search Troubleshooting Toolkit")
        print("=" * 50)
        print("This tool will help diagnose and fix common issues.")
        print()
    
    def _load_configuration(self) -> Dict[str, Optional[str]]:
        """Load configuration from environment variables."""
        load_dotenv()
        
        return {
            'endpoint': os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT'),
            'api_key': os.getenv('AZURE_SEARCH_API_KEY'),
            'index_name': os.getenv('AZURE_SEARCH_INDEX_NAME', 'sample-index'),
            'use_managed_identity': os.getenv('USE_MANAGED_IDENTITY', 'false').lower() == 'true'
        }
    
    def _run_diagnostic(self, test_name: str, test_func, *args, **kwargs) -> DiagnosticResult:
        """
        Run a diagnostic test and capture results.
        
        Args:
            test_name: Name of the diagnostic test
            test_func: Function to execute for the test
            *args, **kwargs: Arguments to pass to the test function
            
        Returns:
            DiagnosticResult: Results of the diagnostic test
        """
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if isinstance(result, tuple):
                passed, message, details, suggestions = result
            else:
                passed, message, details, suggestions = result, "Test completed", {}, []
            
            diagnostic = DiagnosticResult(
                test_name=test_name,
                passed=passed,
                message=message,
                details=details,
                error_type=None,
                fix_suggestions=suggestions,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            
            diagnostic = DiagnosticResult(
                test_name=test_name,
                passed=False,
                message=f"Test failed: {str(e)}",
                details={"exception": str(e), "exception_type": error_type},
                error_type=error_type,
                fix_suggestions=self._get_error_suggestions(e),
                execution_time=execution_time
            )
        
        self.results.append(diagnostic)
        self._display_result(diagnostic)
        return diagnostic    
  
    def _display_result(self, result: DiagnosticResult):
        """Display a diagnostic result with appropriate formatting."""
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.test_name}: {result.message} ({result.execution_time:.2f}s)")
        
        if not result.passed and result.fix_suggestions:
            print("   💡 Suggestions:")
            for suggestion in result.fix_suggestions[:3]:  # Show top 3 suggestions
                print(f"      • {suggestion}")
    
    def _get_error_suggestions(self, error: Exception) -> List[str]:
        """Get fix suggestions based on error type."""
        error_type = type(error).__name__
        
        suggestions_map = {
            'ClientAuthenticationError': [
                "Check your API key in the .env file",
                "Verify the API key hasn't expired",
                "Ensure the key has the correct permissions"
            ],
            'ResourceNotFoundError': [
                "Verify the service endpoint URL is correct",
                "Check if the Azure AI Search service exists",
                "Confirm the index name is correct"
            ],
            'ServiceRequestError': [
                "Check your internet connection",
                "Verify the service endpoint is accessible",
                "Try again in a few minutes (temporary service issue)"
            ],
            'ConnectionError': [
                "Check your internet connection",
                "Verify firewall settings",
                "Try connecting from a different network"
            ],
            'ValueError': [
                "Check your configuration values",
                "Ensure all required environment variables are set",
                "Verify the format of your configuration"
            ]
        }
        
        return suggestions_map.get(error_type, [
            "Check the error message for specific details",
            "Verify your configuration is correct",
            "Try running the configuration validation script"
        ])
    
    def test_network_connectivity(self) -> Tuple[bool, str, Dict[str, Any], List[str]]:
        """
        Test basic network connectivity to Azure AI Search service.
        
        Returns:
            Tuple of (success, message, details, suggestions)
        """
        if not self.config['endpoint']:
            return False, "No endpoint configured", {}, [
                "Set AZURE_SEARCH_SERVICE_ENDPOINT in your .env file"
            ]
        
        try:
            # Parse the endpoint URL
            parsed_url = urllib.parse.urlparse(self.config['endpoint'])
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            
            # Test DNS resolution
            try:
                ip_address = socket.gethostbyname(hostname)
            except socket.gaierror:
                return False, f"DNS resolution failed for {hostname}", {
                    "hostname": hostname
                }, [
                    "Check your internet connection",
                    "Verify the service endpoint URL is correct",
                    "Try using a different DNS server"
                ]
            
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            try:
                result = sock.connect_ex((ip_address, port))
                if result != 0:
                    return False, f"Cannot connect to {hostname}:{port}", {
                        "hostname": hostname,
                        "port": port,
                        "ip_address": ip_address
                    }, [
                        "Check your firewall settings",
                        "Verify the service is running",
                        "Try connecting from a different network"
                    ]
            finally:
                sock.close()
            
            return True, f"Network connectivity successful to {hostname}", {
                "hostname": hostname,
                "port": port,
                "ip_address": ip_address
            }, []
            
        except Exception as e:
            return False, f"Network test failed: {str(e)}", {}, [
                "Check your internet connection",
                "Verify the endpoint URL format"
            ]
    
    def test_service_availability(self) -> Tuple[bool, str, Dict[str, Any], List[str]]:
        """
        Test if the Azure AI Search service is available and responding.
        
        Returns:
            Tuple of (success, message, details, suggestions)
        """
        if not self.config['endpoint']:
            return False, "No endpoint configured", {}, []
        
        try:
            # Make a simple HTTP request to the service
            url = f"{self.config['endpoint']}/servicestats?api-version=2023-11-01"
            headers = {}
            
            if self.config['api_key']:
                headers['api-key'] = self.config['api_key']
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return True, "Service is available and responding", {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }, []
            elif response.status_code == 401:
                return False, "Authentication failed", {
                    "status_code": response.status_code
                }, [
                    "Check your API key",
                    "Verify the key has correct permissions",
                    "Try regenerating the API key"
                ]
            elif response.status_code == 403:
                return False, "Access forbidden", {
                    "status_code": response.status_code
                }, [
                    "Check your API key permissions",
                    "Verify your Azure subscription is active",
                    "Contact Azure support if the issue persists"
                ]
            else:
                return False, f"Service returned status {response.status_code}", {
                    "status_code": response.status_code,
                    "response_text": response.text[:200]
                }, [
                    "Check Azure service status",
                    "Try again in a few minutes",
                    "Contact Azure support if the issue persists"
                ]
                
        except requests.exceptions.Timeout:
            return False, "Service request timed out", {}, [
                "Check your internet connection",
                "Try again with a longer timeout",
                "Verify the service endpoint is correct"
            ]
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to service", {}, [
                "Check your internet connection",
                "Verify the service endpoint URL",
                "Check firewall settings"
            ]
        except Exception as e:
            return False, f"Service test failed: {str(e)}", {}, []
    
    def test_authentication_methods(self) -> Tuple[bool, str, Dict[str, Any], List[str]]:
        """
        Test different authentication methods.
        
        Returns:
            Tuple of (success, message, details, suggestions)
        """
        auth_results = {}
        
        # Test API key authentication
        if self.config['api_key']:
            try:
                credential = AzureKeyCredential(self.config['api_key'])
                client = SearchIndexClient(
                    endpoint=self.config['endpoint'],
                    credential=credential
                )
                stats = client.get_service_statistics()
                auth_results['api_key'] = {
                    'success': True,
                    'message': 'API key authentication successful',
                    'document_count': stats.counters.document_count
                }
            except ClientAuthenticationError:
                auth_results['api_key'] = {
                    'success': False,
                    'message': 'API key authentication failed - invalid key'
                }
            except Exception as e:
                auth_results['api_key'] = {
                    'success': False,
                    'message': f'API key test failed: {str(e)}'
                }
        
        # Test managed identity authentication
        if self.config['use_managed_identity']:
            try:
                credential = DefaultAzureCredential()
                client = SearchIndexClient(
                    endpoint=self.config['endpoint'],
                    credential=credential
                )
                stats = client.get_service_statistics()
                auth_results['managed_identity'] = {
                    'success': True,
                    'message': 'Managed identity authentication successful',
                    'document_count': stats.counters.document_count
                }
            except Exception as e:
                auth_results['managed_identity'] = {
                    'success': False,
                    'message': f'Managed identity failed: {str(e)}'
                }
        
        # Determine overall result
        successful_methods = [k for k, v in auth_results.items() if v['success']]
        
        if successful_methods:
            return True, f"Authentication successful with: {', '.join(successful_methods)}", {
                'results': auth_results,
                'successful_methods': successful_methods
            }, []
        else:
            suggestions = [
                "Verify your API key is correct",
                "Check if managed identity is properly configured",
                "Ensure your credentials have the necessary permissions"
            ]
            return False, "All authentication methods failed", {
                'results': auth_results
            }, suggestions    

    def test_index_operations(self) -> Tuple[bool, str, Dict[str, Any], List[str]]:
        """
        Test basic index operations to verify permissions.
        
        Returns:
            Tuple of (success, message, details, suggestions)
        """
        if not self.config['api_key']:
            return False, "No API key configured for testing", {}, []
        
        try:
            # Create index client
            credential = AzureKeyCredential(self.config['api_key'])
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            # Test listing indexes
            indexes = list(index_client.list_indexes())
            index_names = [idx.name for idx in indexes]
            
            # Test getting service statistics
            stats = index_client.get_service_statistics()
            
            # Test search client if we have an index
            search_results = {}
            if index_names:
                try:
                    search_client = SearchClient(
                        endpoint=self.config['endpoint'],
                        index_name=index_names[0],
                        credential=credential
                    )
                    doc_count = search_client.get_document_count()
                    search_results[index_names[0]] = {
                        'accessible': True,
                        'document_count': doc_count
                    }
                except Exception as e:
                    search_results[index_names[0]] = {
                        'accessible': False,
                        'error': str(e)
                    }
            
            return True, f"Index operations successful - found {len(index_names)} indexes", {
                'index_count': len(index_names),
                'index_names': index_names,
                'service_stats': {
                    'document_count': stats.counters.document_count,
                    'storage_size': stats.counters.storage_size
                },
                'search_results': search_results
            }, []
            
        except ClientAuthenticationError:
            return False, "Authentication failed for index operations", {}, [
                "Check your API key permissions",
                "Ensure the key has 'Search Service Contributor' role",
                "Try regenerating the API key"
            ]
        except Exception as e:
            return False, f"Index operations failed: {str(e)}", {}, [
                "Check your service configuration",
                "Verify your permissions",
                "Try the basic connection test first"
            ]
    
    def test_common_configurations(self) -> Tuple[bool, str, Dict[str, Any], List[str]]:
        """
        Test common configuration issues and misconfigurations.
        
        Returns:
            Tuple of (success, message, details, suggestions)
        """
        issues = []
        warnings = []
        
        # Check endpoint format
        endpoint = self.config['endpoint']
        if endpoint:
            if not endpoint.startswith('https://'):
                issues.append("Endpoint should start with 'https://'")
            if not endpoint.endswith('.search.windows.net'):
                issues.append("Endpoint should end with '.search.windows.net'")
            if '//' in endpoint.replace('https://', ''):
                issues.append("Endpoint contains extra slashes")
        
        # Check API key format
        api_key = self.config['api_key']
        if api_key:
            if len(api_key) < 20:
                warnings.append("API key seems too short (might be incorrect)")
            if ' ' in api_key:
                issues.append("API key contains spaces")
            if api_key.startswith('Bearer '):
                issues.append("API key should not include 'Bearer ' prefix")
        
        # Check index name format
        index_name = self.config['index_name']
        if index_name:
            if index_name != index_name.lower():
                issues.append("Index name should be lowercase")
            if not index_name.replace('-', '').replace('_', '').isalnum():
                issues.append("Index name contains invalid characters")
            if index_name.startswith('-') or index_name.endswith('-'):
                issues.append("Index name cannot start or end with hyphens")
        
        # Determine result
        if issues:
            return False, f"Found {len(issues)} configuration issues", {
                'issues': issues,
                'warnings': warnings
            }, [
                "Fix the configuration issues listed above",
                "Check the Azure AI Search documentation for naming rules",
                "Verify your configuration against the .env.template file"
            ]
        elif warnings:
            return True, f"Configuration looks good with {len(warnings)} warnings", {
                'warnings': warnings
            }, [
                "Consider addressing the warnings for better reliability"
            ]
        else:
            return True, "Configuration format looks correct", {}, []
    
    def run_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """
        Run all diagnostic tests in sequence.
        
        Returns:
            Dict containing comprehensive diagnostic results
        """
        print("🔍 Running Comprehensive Diagnostics...")
        print("=" * 40)
        
        # Define diagnostic tests
        diagnostic_tests = [
            ("Network Connectivity", self.test_network_connectivity),
            ("Service Availability", self.test_service_availability),
            ("Configuration Format", self.test_common_configurations),
            ("Authentication Methods", self.test_authentication_methods),
            ("Index Operations", self.test_index_operations)
        ]
        
        # Run all tests
        for test_name, test_func in diagnostic_tests:
            print(f"\n🧪 {test_name}...")
            self._run_diagnostic(test_name, test_func)
        
        # Generate summary
        return self._generate_diagnostic_summary()
    
    def _generate_diagnostic_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive diagnostic summary."""
        print("\n" + "=" * 50)
        print("📊 Diagnostic Summary")
        print("=" * 50)
        
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        total_time = sum(r.execution_time for r in self.results)
        
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        
        # Categorize issues
        critical_issues = []
        warnings = []
        
        for result in self.results:
            if not result.passed:
                if result.error_type in ['ClientAuthenticationError', 'ConnectionError']:
                    critical_issues.append(result)
                else:
                    warnings.append(result)
        
        # Overall status
        if failed_count == 0:
            print("\n🎉 Status: ALL DIAGNOSTICS PASSED!")
            print("Your Azure AI Search connection should work perfectly.")
        elif critical_issues:
            print(f"\n❌ Status: CRITICAL ISSUES DETECTED ({len(critical_issues)})")
            print("These issues will prevent Azure AI Search from working:")
            for issue in critical_issues:
                print(f"   • {issue.test_name}: {issue.message}")
        else:
            print(f"\n⚠️  Status: MINOR ISSUES DETECTED ({len(warnings)})")
            print("Your connection should work, but consider fixing these:")
            for warning in warnings:
                print(f"   • {warning.test_name}: {warning.message}")
        
        # Create detailed report
        summary = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed": passed_count,
                "failed": failed_count,
                "total_execution_time": total_time
            },
            "configuration": self.config,
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "error_type": r.error_type,
                    "fix_suggestions": r.fix_suggestions,
                    "execution_time": r.execution_time
                }
                for r in self.results
            ],
            "critical_issues": len(critical_issues),
            "warnings": len(warnings)
        }
        
        return summary
    
    def save_diagnostic_report(self, file_path: str = "logs/troubleshooting_report.json"):
        """Save the diagnostic report to a file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            summary = self._generate_diagnostic_summary()
            
            with open(file_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"\n📄 Diagnostic report saved to: {file_path}")
            
        except Exception as e:
            print(f"\n⚠️  Could not save report: {str(e)}")


def main():
    """
    Main function to run Azure AI Search troubleshooting.
    
    This function provides comprehensive diagnostics to help identify
    and resolve common Azure AI Search connection issues.
    """
    print("🚀 Azure AI Search Troubleshooting Toolkit")
    print("This tool will help diagnose and fix connection issues.")
    print()
    
    # Create troubleshooter and run diagnostics
    troubleshooter = AzureSearchTroubleshooter()
    results = troubleshooter.run_comprehensive_diagnostics()
    
    # Save diagnostic report
    troubleshooter.save_diagnostic_report()
    
    # Provide next steps
    print("\n🎯 Next Steps:")
    
    if results["summary"]["failed"] == 0:
        print("✅ All diagnostics passed! Your setup should work correctly.")
        print("   1. Try connecting: python code-samples/connection_setup.py")
        print("   2. Complete the exercises in exercises/")
        print("   3. Move on to Module 2: Basic Search Operations")
    else:
        print("❌ Issues detected. Please address the failed diagnostics:")
        failed_results = [r for r in troubleshooter.results if not r.passed]
        for result in failed_results[:3]:  # Show top 3 issues
            print(f"   • {result.test_name}: {result.message}")
            if result.fix_suggestions:
                print(f"     Fix: {result.fix_suggestions[0]}")
    
    print("\n📚 Additional Resources:")
    print("   🔧 Configuration Validation: python code-samples/configuration_validation.py")
    print("   📖 Documentation: docs/beginner/module-01-introduction-setup/documentation.md")
    print("   🆘 Setup Validation: python setup/validate_setup.py")
    
    return results["summary"]["failed"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)