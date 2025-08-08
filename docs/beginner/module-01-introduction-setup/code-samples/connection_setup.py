"""
Azure AI Search Connection Setup - Module 1 Code Sample
==================================================

This script demonstrates the fundamental concepts of connecting to Azure AI Search service.
It covers basic authentication methods and connection testing.

Learning Objectives:
- Understand Azure AI Search service endpoints and authentication
- Learn how to create and configure search clients
- Practice connection testing and error handling
- Explore different authentication methods (API key and managed identity)

Prerequisites:
- Azure AI Search service created in Azure portal
- Service endpoint URL and API key available
- Environment variables configured in .env file

Author: Azure AI Search Handbook
Module: Beginner - Module 1: Introduction and Setup
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Azure AI Search SDK imports
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import AzureError, ClientAuthenticationError

# Environment and utility imports
from dotenv import load_dotenv

# Add setup directory to path for utility imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'setup'))
from connection_utils import AzureSearchConnectionManager, SearchConfig


class BeginnerConnectionDemo:
    """
    Beginner-friendly demonstration of Azure AI Search connections.
    
    This class provides step-by-step examples of connecting to Azure AI Search
    with detailed explanations and error handling suitable for beginners.
    """
    
    def __init__(self):
        """Initialize the connection demo with logging and configuration."""
        # Set up logging for better debugging and learning
        self.logger = self._setup_logging()
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize configuration
        self.config = self._load_configuration()
        
        self.logger.info("🚀 Azure AI Search Connection Demo initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Set up logging configuration for educational purposes.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger("azure_search_beginner")
        
        # Only add handler if it doesn't exist (avoid duplicate logs)
        if not logger.handlers:
            # Create console handler with formatting
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _load_configuration(self) -> Dict[str, Optional[str]]:
        """
        Load configuration from environment variables.
        
        This method demonstrates how to safely load and validate
        configuration values needed for Azure AI Search connection.
        
        Returns:
            Dict[str, Optional[str]]: Configuration dictionary
        """
        config = {
            'endpoint': os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT'),
            'api_key': os.getenv('AZURE_SEARCH_API_KEY'),
            'index_name': os.getenv('AZURE_SEARCH_INDEX_NAME', 'sample-index'),
            'use_managed_identity': os.getenv('USE_MANAGED_IDENTITY', 'false').lower() == 'true'
        }
        
        self.logger.info("📋 Configuration loaded from environment variables")
        
        # Log configuration (without sensitive data)
        safe_config = {k: v if k != 'api_key' else '***' for k, v in config.items() if v}
        self.logger.info(f"Configuration: {safe_config}")
        
        return config
    
    def validate_configuration(self) -> bool:
        """
        Validate that all required configuration is present.
        
        This method checks if the necessary environment variables are set
        and provides helpful error messages for missing configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        self.logger.info("🔍 Validating configuration...")
        
        # Check required fields
        required_fields = ['endpoint']
        missing_fields = []
        
        for field in required_fields:
            if not self.config.get(field):
                missing_fields.append(field)
        
        # Check authentication method
        has_api_key = bool(self.config.get('api_key'))
        has_managed_identity = self.config.get('use_managed_identity', False)
        
        if not has_api_key and not has_managed_identity:
            missing_fields.append('api_key or managed_identity')
        
        if missing_fields:
            self.logger.error(f"❌ Missing required configuration: {', '.join(missing_fields)}")
            self.logger.error("💡 Please check your .env file and ensure all required variables are set")
            return False
        
        self.logger.info("✅ Configuration validation passed")
        return True
    
    def create_search_client_basic(self, index_name: Optional[str] = None) -> Optional[SearchClient]:
        """
        Create a basic SearchClient using API key authentication.
        
        This is the simplest way to connect to Azure AI Search and is recommended
        for beginners and development scenarios.
        
        Args:
            index_name (Optional[str]): Name of the index to connect to
            
        Returns:
            Optional[SearchClient]: Configured search client or None if failed
        """
        self.logger.info("🔑 Creating SearchClient with API key authentication...")
        
        try:
            # Use provided index name or fall back to configuration
            target_index = index_name or self.config['index_name']
            
            # Validate required parameters
            if not self.config['endpoint']:
                raise ValueError("Service endpoint is required")
            
            if not self.config['api_key']:
                raise ValueError("API key is required for basic authentication")
            
            if not target_index:
                raise ValueError("Index name is required")
            
            # Create the credential object
            credential = AzureKeyCredential(self.config['api_key'])
            
            # Create the SearchClient
            search_client = SearchClient(
                endpoint=self.config['endpoint'],
                index_name=target_index,
                credential=credential
            )
            
            self.logger.info(f"✅ SearchClient created successfully for index: {target_index}")
            return search_client
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create SearchClient: {str(e)}")
            return None
    
    def create_index_client_basic(self) -> Optional[SearchIndexClient]:
        """
        Create a basic SearchIndexClient for index management operations.
        
        The SearchIndexClient is used for administrative operations like
        creating, updating, and deleting indexes.
        
        Returns:
            Optional[SearchIndexClient]: Configured index client or None if failed
        """
        self.logger.info("🔧 Creating SearchIndexClient for index management...")
        
        try:
            # Validate required parameters
            if not self.config['endpoint']:
                raise ValueError("Service endpoint is required")
            
            if not self.config['api_key']:
                raise ValueError("API key is required")
            
            # Create the credential object
            credential = AzureKeyCredential(self.config['api_key'])
            
            # Create the SearchIndexClient
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            self.logger.info("✅ SearchIndexClient created successfully")
            return index_client
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create SearchIndexClient: {str(e)}")
            return None
    
    def test_connection_basic(self) -> bool:
        """
        Test the connection to Azure AI Search service.
        
        This method performs a simple connection test by attempting to
        retrieve service statistics, which requires minimal permissions.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        self.logger.info("🧪 Testing connection to Azure AI Search...")
        
        try:
            # Create an index client for testing
            index_client = self.create_index_client_basic()
            
            if not index_client:
                self.logger.error("❌ Could not create index client for testing")
                return False
            
            # Attempt to get service statistics (lightweight operation)
            stats = index_client.get_service_statistics()
            
            # Log success with service information
            self.logger.info("✅ Connection test successful!")
            self.logger.info(f"📊 Service Statistics:")
            self.logger.info(f"   - Document Count: {stats.counters.document_count}")
            self.logger.info(f"   - Index Count: {stats.counters.index_count}")
            self.logger.info(f"   - Storage Size: {stats.counters.storage_size} bytes")
            
            return True
            
        except ClientAuthenticationError as e:
            self.logger.error("❌ Authentication failed - please check your API key")
            self.logger.error(f"   Error details: {str(e)}")
            return False
            
        except AzureError as e:
            self.logger.error(f"❌ Azure service error: {str(e)}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error during connection test: {str(e)}")
            return False
    
    def test_index_access(self, index_name: Optional[str] = None) -> bool:
        """
        Test access to a specific index.
        
        This method tests whether we can successfully connect to and
        query a specific index.
        
        Args:
            index_name (Optional[str]): Name of the index to test
            
        Returns:
            bool: True if index access successful, False otherwise
        """
        target_index = index_name or self.config['index_name']
        self.logger.info(f"🎯 Testing access to index: {target_index}")
        
        try:
            # Create a search client for the specific index
            search_client = self.create_search_client_basic(target_index)
            
            if not search_client:
                self.logger.error("❌ Could not create search client for index testing")
                return False
            
            # Attempt to get document count (simple operation)
            document_count = search_client.get_document_count()
            
            self.logger.info(f"✅ Index access successful!")
            self.logger.info(f"📄 Index '{target_index}' contains {document_count} documents")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to access index '{target_index}': {str(e)}")
            
            # Provide helpful troubleshooting tips
            self.logger.info("💡 Troubleshooting tips:")
            self.logger.info("   - Verify the index name is correct")
            self.logger.info("   - Check if the index exists in your search service")
            self.logger.info("   - Ensure your API key has the necessary permissions")
            
            return False
    
    def demonstrate_managed_identity(self) -> bool:
        """
        Demonstrate connection using managed identity authentication.
        
        This method shows how to connect using Azure managed identity,
        which is the recommended approach for production scenarios.
        
        Returns:
            bool: True if managed identity connection successful, False otherwise
        """
        self.logger.info("🔐 Demonstrating managed identity authentication...")
        
        try:
            # Check if managed identity is configured
            if not self.config.get('use_managed_identity'):
                self.logger.info("ℹ️  Managed identity not configured, skipping demonstration")
                return False
            
            # Create credential using managed identity
            credential = DefaultAzureCredential()
            
            # Create SearchIndexClient with managed identity
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            # Test the connection
            stats = index_client.get_service_statistics()
            
            self.logger.info("✅ Managed identity authentication successful!")
            self.logger.info(f"📊 Connected with managed identity - {stats.counters.index_count} indexes available")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Managed identity authentication failed: {str(e)}")
            self.logger.info("💡 Managed identity troubleshooting:")
            self.logger.info("   - Ensure managed identity is enabled for your resource")
            self.logger.info("   - Verify the identity has 'Search Service Contributor' role")
            self.logger.info("   - Check if you're running in an Azure environment")
            
            return False
    
    def list_available_indexes(self) -> list:
        """
        List all available indexes in the search service.
        
        This method demonstrates how to discover what indexes are available
        in your Azure AI Search service.
        
        Returns:
            list: List of index names
        """
        self.logger.info("📋 Listing available indexes...")
        
        try:
            # Create index client
            index_client = self.create_index_client_basic()
            
            if not index_client:
                self.logger.error("❌ Could not create index client")
                return []
            
            # Get list of indexes
            indexes = list(index_client.list_indexes())
            index_names = [index.name for index in indexes]
            
            if index_names:
                self.logger.info(f"✅ Found {len(index_names)} indexes:")
                for i, name in enumerate(index_names, 1):
                    self.logger.info(f"   {i}. {name}")
            else:
                self.logger.info("ℹ️  No indexes found in the search service")
            
            return index_names
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list indexes: {str(e)}")
            return []
    
    def run_comprehensive_demo(self) -> Dict[str, bool]:
        """
        Run a comprehensive demonstration of all connection methods.
        
        This method executes all the connection examples in sequence,
        providing a complete overview of Azure AI Search connectivity.
        
        Returns:
            Dict[str, bool]: Results of each test
        """
        self.logger.info("🎬 Starting comprehensive Azure AI Search connection demonstration")
        self.logger.info("=" * 70)
        
        results = {}
        
        # Step 1: Validate configuration
        results['configuration_valid'] = self.validate_configuration()
        
        if not results['configuration_valid']:
            self.logger.error("❌ Configuration validation failed - stopping demo")
            return results
        
        # Step 2: Test basic connection
        results['basic_connection'] = self.test_connection_basic()
        
        # Step 3: List available indexes
        available_indexes = self.list_available_indexes()
        results['index_listing'] = len(available_indexes) >= 0  # Success if no error
        
        # Step 4: Test index access (if indexes are available)
        if available_indexes:
            results['index_access'] = self.test_index_access(available_indexes[0])
        else:
            self.logger.info("ℹ️  Skipping index access test - no indexes available")
            results['index_access'] = None
        
        # Step 5: Test managed identity (if configured)
        results['managed_identity'] = self.demonstrate_managed_identity()
        
        # Summary
        self.logger.info("=" * 70)
        self.logger.info("📊 Demo Results Summary:")
        
        for test_name, result in results.items():
            if result is True:
                status = "✅ PASSED"
            elif result is False:
                status = "❌ FAILED"
            else:
                status = "⏭️  SKIPPED"
            
            self.logger.info(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        return results


def create_search_client():
    """
    Legacy function for backward compatibility.
    
    Creates a basic SearchClient using environment variables.
    This function is kept for compatibility with existing code.
    
    Returns:
        SearchClient: Configured search client
    """
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "sample-index")
    
    # Validate configuration
    if not service_endpoint or not api_key:
        raise ValueError("Missing required environment variables: AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_API_KEY")
    
    # Create and return search client
    search_client = SearchClient(
        endpoint=service_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )
    
    return search_client


def test_connection():
    """
    Legacy function for backward compatibility.
    
    Tests the connection to Azure AI Search using basic method.
    This function is kept for compatibility with existing code.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = create_search_client()
        # Simple test - get document count
        result = client.get_document_count()
        print(f"✅ Connection successful! Index contains {result} documents.")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def main():
    """
    Main function demonstrating Azure AI Search connection setup.
    
    This function provides a complete walkthrough of connecting to
    Azure AI Search with detailed explanations and error handling.
    """
    print("🚀 Azure AI Search Connection Setup - Module 1")
    print("=" * 50)
    print()
    print("This script demonstrates how to connect to Azure AI Search service.")
    print("You'll learn about authentication, connection testing, and troubleshooting.")
    print()
    
    # Create demo instance
    demo = BeginnerConnectionDemo()
    
    # Run comprehensive demonstration
    results = demo.run_comprehensive_demo()
    
    # Provide next steps based on results
    print()
    print("🎯 Next Steps:")
    
    if results.get('basic_connection'):
        print("✅ Great! Your connection is working. You can now:")
        print("   1. Explore the Jupyter notebook version of this demo")
        print("   2. Try the exercises in the exercises/ directory")
        print("   3. Move on to Module 2: Basic Search Operations")
    else:
        print("❌ Connection issues detected. Please:")
        print("   1. Check your .env file configuration")
        print("   2. Verify your Azure AI Search service is running")
        print("   3. Confirm your API key has the correct permissions")
        print("   4. Review the troubleshooting guide in the documentation")
    
    print()
    print("📚 Additional Resources:")
    print("   - Documentation: docs/beginner/module-01-introduction-setup/documentation.md")
    print("   - Interactive Notebook: code-samples/connection_setup.ipynb")
    print("   - Exercises: exercises/")
    print("   - Troubleshooting: setup/validate_setup.py")


if __name__ == "__main__":
    main()