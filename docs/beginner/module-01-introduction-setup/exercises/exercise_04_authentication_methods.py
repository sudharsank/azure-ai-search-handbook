"""
Exercise 4: Authentication Methods
Explore different ways to authenticate with Azure AI Search
"""

import os
import sys
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# TODO: Import Azure AI Search and authentication libraries
# from azure.search.documents.indexes import SearchIndexClient
# from azure.core.credentials import AzureKeyCredential
# from azure.identity import DefaultAzureCredential, AzureCliCredential
# from azure.core.exceptions import ClientAuthenticationError

def test_api_key_authentication(endpoint: str, api_key: str) -> Dict[str, Any]:
    """
    Exercise: Test API key authentication
    
    Instructions:
    1. Create an AzureKeyCredential with the provided API key
    2. Create a SearchIndexClient using the credential
    3. Test the connection by getting service statistics
    4. Return detailed results about the authentication test
    
    Args:
        endpoint: Azure AI Search service endpoint
        api_key: API key for authentication
        
    Returns:
        Dict containing authentication test results
    """
    # TODO: Implement API key authentication test
    # Return structure:
    # {
    #     'method': 'API Key',
    #     'success': bool,
    #     'message': str,
    #     'details': {
    #         'credential_type': str,
    #         'service_accessible': bool,
    #         'document_count': int or None,
    #         'execution_time': float
    #     },
    #     'error': str or None
    # }
    pass

def test_managed_identity_authentication(endpoint: str) -> Dict[str, Any]:
    """
    Exercise: Test managed identity authentication
    
    Instructions:
    1. Create a DefaultAzureCredential (tries multiple auth methods)
    2. Create a SearchIndexClient using the credential
    3. Test the connection by getting service statistics
    4. Handle authentication failures gracefully
    5. Return detailed results
    
    Args:
        endpoint: Azure AI Search service endpoint
        
    Returns:
        Dict containing authentication test results
    """
    # TODO: Implement managed identity authentication test
    # Note: This might fail in local development environments
    # DefaultAzureCredential tries multiple methods in order:
    # 1. Environment variables (service principal)
    # 2. Managed identity
    # 3. Azure CLI
    # 4. Visual Studio
    # 5. And more...
    pass

def test_azure_cli_authentication(endpoint: str) -> Dict[str, Any]:
    """
    Exercise: Test Azure CLI authentication
    
    Instructions:
    1. Create an AzureCliCredential
    2. Create a SearchIndexClient using the credential
    3. Test the connection by getting service statistics
    4. Handle cases where Azure CLI is not logged in
    5. Return detailed results
    
    Args:
        endpoint: Azure AI Search service endpoint
        
    Returns:
        Dict containing authentication test results
    """
    # TODO: Implement Azure CLI authentication test
    # This requires 'az login' to be run first
    # Handle CredentialUnavailableError if CLI not available
    pass

def compare_authentication_methods() -> Dict[str, Dict[str, Any]]:
    """
    Exercise: Compare different authentication methods
    
    Instructions:
    1. Define characteristics of each authentication method
    2. Include security level, ease of use, and use cases
    3. Provide recommendations for different scenarios
    4. Return a comprehensive comparison
    
    Returns:
        Dict containing comparison of authentication methods
    """
    # TODO: Implement authentication method comparison
    # Structure should include:
    # {
    #     'API Key': {
    #         'security_level': str,
    #         'ease_of_use': str,
    #         'production_ready': bool,
    #         'use_cases': [str],
    #         'pros': [str],
    #         'cons': [str],
    #         'setup_complexity': str
    #     },
    #     'Managed Identity': { ... },
    #     'Azure CLI': { ... }
    # }
    pass

def get_authentication_recommendations(environment: str) -> Dict[str, str]:
    """
    Exercise: Get authentication recommendations based on environment
    
    Instructions:
    1. Define different deployment environments
    2. Recommend the best authentication method for each
    3. Provide reasoning for each recommendation
    4. Include security considerations
    
    Args:
        environment: Target environment ('development', 'testing', 'production', 'ci_cd')
        
    Returns:
        Dict containing recommendations for the specified environment
    """
    # TODO: Implement environment-specific authentication recommendations
    # Consider factors like:
    # - Security requirements
    # - Ease of setup
    # - Maintenance overhead
    # - Automation needs
    pass

def test_credential_rotation_scenario() -> Dict[str, Any]:
    """
    Exercise: Simulate credential rotation scenario
    
    Instructions:
    1. Demonstrate what happens when credentials expire
    2. Show how different auth methods handle rotation
    3. Provide best practices for credential management
    4. Return insights about credential lifecycle
    
    Returns:
        Dict containing credential rotation insights
    """
    # TODO: Implement credential rotation scenario
    # This is more of an educational exercise showing:
    # - How to detect expired credentials
    # - Best practices for rotation
    # - Automated vs manual rotation
    # - Monitoring credential health
    pass

def run_authentication_comparison() -> Dict[str, Any]:
    """
    Exercise: Run comprehensive authentication method comparison
    
    Instructions:
    1. Load configuration from environment
    2. Test each available authentication method
    3. Compare results and performance
    4. Provide recommendations based on results
    5. Return comprehensive analysis
    
    Returns:
        Dict containing complete authentication analysis
    """
    # TODO: Implement comprehensive authentication comparison
    # This should orchestrate all the authentication tests
    # and provide a complete analysis of available options
    pass

if __name__ == "__main__":
    print("🔐 Authentication Methods Exercise")
    print("=" * 40)
    
    print("This exercise explores different ways to authenticate with Azure AI Search.")
    print("You'll learn about security, ease of use, and best practices for each method.\n")
    
    # Load configuration
    load_dotenv()
    endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
    api_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not endpoint:
        print("❌ No endpoint configured. Please set AZURE_SEARCH_SERVICE_ENDPOINT in your .env file.")
        sys.exit(1)
    
    print("🧪 Testing Authentication Methods...")
    
    # Test API Key Authentication
    print("\n1️⃣ API Key Authentication")
    if api_key:
        api_result = test_api_key_authentication(endpoint, api_key)
        if api_result:
            status = "✅" if api_result.get('success') else "❌"
            print(f"{status} {api_result.get('message', 'Test completed')}")
    else:
        print("⚠️  No API key configured - skipping test")
    
    # Test Managed Identity Authentication
    print("\n2️⃣ Managed Identity Authentication")
    managed_result = test_managed_identity_authentication(endpoint)
    if managed_result:
        status = "✅" if managed_result.get('success') else "❌"
        print(f"{status} {managed_result.get('message', 'Test completed')}")
    
    # Test Azure CLI Authentication
    print("\n3️⃣ Azure CLI Authentication")
    cli_result = test_azure_cli_authentication(endpoint)
    if cli_result:
        status = "✅" if cli_result.get('success') else "❌"
        print(f"{status} {cli_result.get('message', 'Test completed')}")
    
    # Compare methods
    print("\n📊 Authentication Method Comparison")
    comparison = compare_authentication_methods()
    if comparison:
        for method, details in comparison.items():
            print(f"\n🔐 {method}:")
            print(f"   Security: {details.get('security_level', 'Unknown')}")
            print(f"   Ease of Use: {details.get('ease_of_use', 'Unknown')}")
            print(f"   Production Ready: {'Yes' if details.get('production_ready') else 'No'}")
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    environments = ['development', 'testing', 'production', 'ci_cd']
    for env in environments:
        rec = get_authentication_recommendations(env)
        if rec:
            print(f"   {env.title()}: {rec.get('method', 'Not specified')} - {rec.get('reason', '')}")
    
    print("\n🎯 Next Steps:")
    print("1. Choose the authentication method that best fits your use case")
    print("2. Implement proper error handling for authentication failures")
    print("3. Set up credential rotation procedures if using API keys")
    print("4. Move on to Exercise 5: Error Handling and Troubleshooting")