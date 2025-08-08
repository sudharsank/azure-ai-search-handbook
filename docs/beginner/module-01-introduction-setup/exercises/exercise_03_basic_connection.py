"""
Exercise 3: Basic Connection Testing
Test your connection to Azure AI Search service
"""

import os
import sys
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# TODO: Import Azure AI Search libraries
# from azure.search.documents import SearchClient
# from azure.search.documents.indexes import SearchIndexClient
# from azure.core.credentials import AzureKeyCredential
# from azure.core.exceptions import ClientAuthenticationError, AzureError

def load_configuration() -> Dict[str, Optional[str]]:
    """
    Exercise: Load configuration from environment variables
    
    Instructions:
    1. Load environment variables using dotenv
    2. Extract the required configuration values
    3. Return them in a dictionary
    
    Returns:
        Dict containing endpoint, api_key, and index_name
    """
    # TODO: Implement configuration loading
    # Load .env file and extract:
    # - AZURE_SEARCH_SERVICE_ENDPOINT
    # - AZURE_SEARCH_API_KEY
    # - AZURE_SEARCH_INDEX_NAME
    pass

def create_search_index_client(endpoint: str, api_key: str) -> Optional[Any]:
    """
    Exercise: Create a SearchIndexClient for administrative operations
    
    Instructions:
    1. Create an AzureKeyCredential with the API key
    2. Create a SearchIndexClient with the endpoint and credential
    3. Handle any exceptions that might occur
    4. Return the client or None if creation failed
    
    Args:
        endpoint: Azure AI Search service endpoint
        api_key: API key for authentication
        
    Returns:
        SearchIndexClient instance or None if failed
    """
    # TODO: Implement SearchIndexClient creation
    # Use AzureKeyCredential and SearchIndexClient
    pass

def create_search_client(endpoint: str, api_key: str, index_name: str) -> Optional[Any]:
    """
    Exercise: Create a SearchClient for document operations
    
    Instructions:
    1. Create an AzureKeyCredential with the API key
    2. Create a SearchClient with endpoint, index name, and credential
    3. Handle any exceptions that might occur
    4. Return the client or None if creation failed
    
    Args:
        endpoint: Azure AI Search service endpoint
        api_key: API key for authentication
        index_name: Name of the search index
        
    Returns:
        SearchClient instance or None if failed
    """
    # TODO: Implement SearchClient creation
    pass

def test_service_connection(index_client) -> Dict[str, Any]:
    """
    Exercise: Test connection by getting service statistics
    
    Instructions:
    1. Use the index client to get service statistics
    2. Extract useful information from the statistics
    3. Handle authentication and connection errors
    4. Return a dictionary with test results
    
    Args:
        index_client: SearchIndexClient instance
        
    Returns:
        Dict containing connection test results
    """
    # TODO: Implement service connection test
    # Use index_client.get_service_statistics()
    # Return structure:
    # {
    #     'success': bool,
    #     'message': str,
    #     'statistics': {
    #         'document_count': int,
    #         'index_count': int,
    #         'storage_size': int
    #     } or None,
    #     'error': str or None
    # }
    pass

def test_index_access(search_client, index_name: str) -> Dict[str, Any]:
    """
    Exercise: Test access to a specific index
    
    Instructions:
    1. Use the search client to get document count
    2. Handle cases where the index doesn't exist
    3. Handle authentication errors
    4. Return test results
    
    Args:
        search_client: SearchClient instance
        index_name: Name of the index to test
        
    Returns:
        Dict containing index access test results
    """
    # TODO: Implement index access test
    # Use search_client.get_document_count()
    # Handle ResourceNotFoundError for non-existent indexes
    # Return structure:
    # {
    #     'success': bool,
    #     'message': str,
    #     'index_exists': bool,
    #     'document_count': int or None,
    #     'error': str or None
    # }
    pass

def list_available_indexes(index_client) -> Dict[str, Any]:
    """
    Exercise: List all available indexes in the service
    
    Instructions:
    1. Use the index client to list all indexes
    2. Extract index names and basic information
    3. Handle any errors that occur
    4. Return the list of indexes
    
    Args:
        index_client: SearchIndexClient instance
        
    Returns:
        Dict containing list of indexes and metadata
    """
    # TODO: Implement index listing
    # Use index_client.list_indexes()
    # Return structure:
    # {
    #     'success': bool,
    #     'message': str,
    #     'indexes': [
    #         {
    #             'name': str,
    #             'field_count': int,
    #             'storage_size': int
    #         }
    #     ] or [],
    #     'total_count': int,
    #     'error': str or None
    # }
    pass

def run_comprehensive_connection_test() -> Dict[str, Any]:
    """
    Exercise: Run a comprehensive connection test
    
    Instructions:
    1. Load configuration
    2. Create both types of clients
    3. Test service connection
    4. List available indexes
    5. Test index access if an index is available
    6. Compile comprehensive results
    
    Returns:
        Dict containing all test results
    """
    # TODO: Implement comprehensive connection test
    # This should orchestrate all the above functions
    # and provide a complete picture of the connection status
    pass

if __name__ == "__main__":
    print("🔗 Basic Connection Testing Exercise")
    print("=" * 40)
    
    print("This exercise will test your connection to Azure AI Search")
    print("and verify that your credentials and configuration are working.\n")
    
    # Run comprehensive connection test
    print("🧪 Running Connection Tests...")
    results = run_comprehensive_connection_test()
    
    if results:
        print(f"\n📊 Connection Test Results:")
        print(f"Overall Status: {'✅ Success' if results.get('overall_success') else '❌ Failed'}")
        
        # Display detailed results
        if 'service_connection' in results:
            service_result = results['service_connection']
            print(f"Service Connection: {'✅' if service_result.get('success') else '❌'} {service_result.get('message', '')}")
            
            if service_result.get('statistics'):
                stats = service_result['statistics']
                print(f"  • Documents: {stats.get('document_count', 0):,}")
                print(f"  • Indexes: {stats.get('index_count', 0)}")
                print(f"  • Storage: {stats.get('storage_size', 0):,} bytes")
        
        if 'available_indexes' in results:
            index_result = results['available_indexes']
            if index_result.get('success'):
                print(f"Available Indexes: {index_result.get('total_count', 0)}")
                for idx in index_result.get('indexes', [])[:3]:  # Show first 3
                    print(f"  • {idx.get('name', 'Unknown')}")
        
        if 'index_access' in results:
            access_result = results['index_access']
            print(f"Index Access: {'✅' if access_result.get('success') else '❌'} {access_result.get('message', '')}")
    
    print("\n🎯 Next Steps:")
    if results and results.get('overall_success'):
        print("✅ Great! Your connection is working properly.")
        print("1. Try Exercise 4: Authentication Methods")
        print("2. Explore different ways to authenticate")
        print("3. Learn about security best practices")
    else:
        print("❌ Connection issues detected. Please:")
        print("1. Check your .env file configuration")
        print("2. Verify your Azure AI Search service is running")
        print("3. Confirm your API key has the correct permissions")
        print("4. Run the troubleshooting script if needed")