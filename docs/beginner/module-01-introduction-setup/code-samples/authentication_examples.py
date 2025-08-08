"""
Azure AI Search Authentication Examples - Module 1 Code Sample
==========================================================

This script demonstrates different authentication methods for Azure AI Search.
It provides practical examples of API key and managed identity authentication.

Learning Objectives:
- Understand different Azure AI Search authentication methods
- Learn when to use API keys vs managed identity
- Practice implementing secure authentication patterns
- Explore authentication troubleshooting techniques

Prerequisites:
- Azure AI Search service created
- Environment variables configured
- Understanding of Azure authentication concepts

Author: Azure AI Search Handbook
Module: Beginner - Module 1: Introduction and Setup
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime

# Azure AI Search SDK imports
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import (
    DefaultAzureCredential, 
    ClientSecretCredential,
    ManagedIdentityCredential,
    AzureCliCredential
)
from azure.core.exceptions import ClientAuthenticationError, AzureError

# Environment and utility imports
from dotenv import load_dotenv


class AuthenticationDemo:
    """
    Comprehensive demonstration of Azure AI Search authentication methods.
    
    This class provides practical examples of different authentication
    approaches with detailed explanations and best practices.
    """
    
    def __init__(self):
        """Initialize the authentication demo."""
        self.logger = self._setup_logging()
        load_dotenv()
        
        # Load configuration
        self.config = {
            'endpoint': os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT'),
            'api_key': os.getenv('AZURE_SEARCH_API_KEY'),
            'index_name': os.getenv('AZURE_SEARCH_INDEX_NAME', 'sample-index'),
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            'tenant_id': os.getenv('AZURE_TENANT_ID')
        }
        
        self.logger.info("🔐 Azure AI Search Authentication Demo initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the authentication demo."""
        logger = logging.getLogger("azure_search_auth")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def demonstrate_api_key_authentication(self) -> bool:
        """
        Demonstrate API key authentication - the simplest method.
        
        API Key Authentication:
        - Easiest to set up and use
        - Good for development and testing
        - Requires secure storage of the key
        - Key can be regenerated if compromised
        
        Returns:
            bool: True if authentication successful
        """
        self.logger.info("🔑 Demonstrating API Key Authentication")
        self.logger.info("=" * 40)
        
        # Check if API key is configured
        if not self.config['api_key']:
            self.logger.error("❌ No API key configured")
            self.logger.info("💡 Set AZURE_SEARCH_API_KEY in your .env file")
            return False
        
        if not self.config['endpoint']:
            self.logger.error("❌ No endpoint configured")
            return False
        
        try:
            self.logger.info("🔧 Creating credential with API key...")
            
            # Create the API key credential
            # This is the most straightforward authentication method
            credential = AzureKeyCredential(self.config['api_key'])
            
            self.logger.info("✅ API key credential created successfully")
            
            # Create a SearchIndexClient for administrative operations
            self.logger.info("🔧 Creating SearchIndexClient...")
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            # Test the authentication by getting service statistics
            self.logger.info("🧪 Testing authentication...")
            stats = index_client.get_service_statistics()
            
            # Display success information
            self.logger.info("✅ API Key Authentication Successful!")
            self.logger.info(f"📊 Service Statistics:")
            self.logger.info(f"   Documents: {stats.counters.document_count:,}")
            self.logger.info(f"   Indexes: {stats.counters.index_count}")
            self.logger.info(f"   Storage: {stats.counters.storage_size:,} bytes")
            
            # Demonstrate creating a SearchClient for document operations
            if self.config['index_name']:
                self.logger.info(f"🔧 Creating SearchClient for index: {self.config['index_name']}")
                
                search_client = SearchClient(
                    endpoint=self.config['endpoint'],
                    index_name=self.config['index_name'],
                    credential=credential
                )
                
                try:
                    doc_count = search_client.get_document_count()
                    self.logger.info(f"✅ SearchClient created - Index has {doc_count:,} documents")
                except Exception as e:
                    self.logger.warning(f"⚠️  SearchClient created but index access failed: {str(e)}")
                    self.logger.info("💡 This might mean the index doesn't exist yet")
            
            # Security best practices reminder
            self.logger.info("\n🔒 API Key Security Best Practices:")
            self.logger.info("   • Store keys in environment variables, never in code")
            self.logger.info("   • Use different keys for development and production")
            self.logger.info("   • Rotate keys regularly")
            self.logger.info("   • Monitor key usage in Azure portal")
            self.logger.info("   • Consider using managed identity for production")
            
            return True
            
        except ClientAuthenticationError as e:
            self.logger.error(f"❌ Authentication failed: {str(e)}")
            self.logger.info("💡 Troubleshooting steps:")
            self.logger.info("   1. Verify your API key is correct")
            self.logger.info("   2. Check if the key has expired")
            self.logger.info("   3. Ensure the key has the necessary permissions")
            self.logger.info("   4. Try regenerating the key in Azure portal")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {str(e)}")
            return False
    
    def demonstrate_managed_identity_authentication(self) -> bool:
        """
        Demonstrate managed identity authentication - the recommended production method.
        
        Managed Identity Authentication:
        - Most secure method (no stored secrets)
        - Automatic credential rotation
        - Integrates with Azure RBAC
        - Recommended for production workloads
        - Works in Azure environments (VMs, App Service, etc.)
        
        Returns:
            bool: True if authentication successful
        """
        self.logger.info("🔐 Demonstrating Managed Identity Authentication")
        self.logger.info("=" * 50)
        
        if not self.config['endpoint']:
            self.logger.error("❌ No endpoint configured")
            return False
        
        try:
            self.logger.info("🔧 Creating DefaultAzureCredential...")
            self.logger.info("ℹ️  DefaultAzureCredential tries multiple authentication methods:")
            self.logger.info("   1. Environment variables (service principal)")
            self.logger.info("   2. Managed identity")
            self.logger.info("   3. Azure CLI credentials")
            self.logger.info("   4. Visual Studio credentials")
            self.logger.info("   5. And more...")
            
            # Create the managed identity credential
            # DefaultAzureCredential automatically tries different auth methods
            credential = DefaultAzureCredential()
            
            self.logger.info("✅ DefaultAzureCredential created")
            
            # Create SearchIndexClient
            self.logger.info("🔧 Creating SearchIndexClient with managed identity...")
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            # Test the authentication
            self.logger.info("🧪 Testing managed identity authentication...")
            stats = index_client.get_service_statistics()
            
            # Display success information
            self.logger.info("✅ Managed Identity Authentication Successful!")
            self.logger.info(f"📊 Service Statistics:")
            self.logger.info(f"   Documents: {stats.counters.document_count:,}")
            self.logger.info(f"   Indexes: {stats.counters.index_count}")
            self.logger.info(f"   Storage: {stats.counters.storage_size:,} bytes")
            
            # Production benefits
            self.logger.info("\n🏆 Managed Identity Benefits:")
            self.logger.info("   • No secrets to manage or rotate")
            self.logger.info("   • Automatic credential lifecycle management")
            self.logger.info("   • Integration with Azure RBAC")
            self.logger.info("   • Audit trail of authentication events")
            self.logger.info("   • Works across Azure services")
            
            return True
            
        except ClientAuthenticationError as e:
            self.logger.error(f"❌ Managed identity authentication failed: {str(e)}")
            self.logger.info("💡 Managed Identity Troubleshooting:")
            self.logger.info("   1. Ensure you're running in an Azure environment")
            self.logger.info("   2. Enable managed identity for your resource")
            self.logger.info("   3. Assign 'Search Service Contributor' role to the identity")
            self.logger.info("   4. For local development, use 'az login' with Azure CLI")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {str(e)}")
            return False  
  
    def demonstrate_service_principal_authentication(self) -> bool:
        """
        Demonstrate service principal authentication for automated scenarios.
        
        Service Principal Authentication:
        - Good for automated/CI-CD scenarios
        - Uses client ID, client secret, and tenant ID
        - More secure than API keys for automation
        - Requires Azure AD app registration
        
        Returns:
            bool: True if authentication successful
        """
        self.logger.info("🤖 Demonstrating Service Principal Authentication")
        self.logger.info("=" * 50)
        
        # Check if service principal credentials are configured
        required_vars = ['client_id', 'client_secret', 'tenant_id']
        missing_vars = [var for var in required_vars if not self.config[var]]
        
        if missing_vars:
            self.logger.warning(f"⚠️  Missing service principal configuration: {', '.join(missing_vars)}")
            self.logger.info("💡 To use service principal authentication:")
            self.logger.info("   1. Create an Azure AD app registration")
            self.logger.info("   2. Create a client secret for the app")
            self.logger.info("   3. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
            self.logger.info("   4. Assign appropriate roles to the service principal")
            return False
        
        if not self.config['endpoint']:
            self.logger.error("❌ No endpoint configured")
            return False
        
        try:
            self.logger.info("🔧 Creating ClientSecretCredential...")
            
            # Create service principal credential
            credential = ClientSecretCredential(
                tenant_id=self.config['tenant_id'],
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret']
            )
            
            self.logger.info("✅ Service principal credential created")
            
            # Create SearchIndexClient
            self.logger.info("🔧 Creating SearchIndexClient with service principal...")
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            # Test the authentication
            self.logger.info("🧪 Testing service principal authentication...")
            stats = index_client.get_service_statistics()
            
            # Display success information
            self.logger.info("✅ Service Principal Authentication Successful!")
            self.logger.info(f"📊 Service Statistics:")
            self.logger.info(f"   Documents: {stats.counters.document_count:,}")
            self.logger.info(f"   Indexes: {stats.counters.index_count}")
            
            # Use cases
            self.logger.info("\n🎯 Service Principal Use Cases:")
            self.logger.info("   • CI/CD pipelines")
            self.logger.info("   • Automated data ingestion")
            self.logger.info("   • Background services")
            self.logger.info("   • Cross-tenant scenarios")
            
            return True
            
        except ClientAuthenticationError as e:
            self.logger.error(f"❌ Service principal authentication failed: {str(e)}")
            self.logger.info("💡 Service Principal Troubleshooting:")
            self.logger.info("   1. Verify client ID, secret, and tenant ID are correct")
            self.logger.info("   2. Check if the client secret has expired")
            self.logger.info("   3. Ensure the service principal has the right roles")
            self.logger.info("   4. Verify the app registration is in the correct tenant")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {str(e)}")
            return False
    
    def demonstrate_azure_cli_authentication(self) -> bool:
        """
        Demonstrate Azure CLI authentication for local development.
        
        Azure CLI Authentication:
        - Great for local development
        - Uses your Azure CLI login
        - No need to store credentials
        - Requires 'az login' to be run first
        
        Returns:
            bool: True if authentication successful
        """
        self.logger.info("🖥️  Demonstrating Azure CLI Authentication")
        self.logger.info("=" * 45)
        
        if not self.config['endpoint']:
            self.logger.error("❌ No endpoint configured")
            return False
        
        try:
            self.logger.info("🔧 Creating AzureCliCredential...")
            self.logger.info("ℹ️  This uses your Azure CLI login credentials")
            
            # Create Azure CLI credential
            credential = AzureCliCredential()
            
            self.logger.info("✅ Azure CLI credential created")
            
            # Create SearchIndexClient
            self.logger.info("🔧 Creating SearchIndexClient with Azure CLI credentials...")
            index_client = SearchIndexClient(
                endpoint=self.config['endpoint'],
                credential=credential
            )
            
            # Test the authentication
            self.logger.info("🧪 Testing Azure CLI authentication...")
            stats = index_client.get_service_statistics()
            
            # Display success information
            self.logger.info("✅ Azure CLI Authentication Successful!")
            self.logger.info(f"📊 Service Statistics:")
            self.logger.info(f"   Documents: {stats.counters.document_count:,}")
            self.logger.info(f"   Indexes: {stats.counters.index_count}")
            
            # Development benefits
            self.logger.info("\n💻 Azure CLI Authentication Benefits:")
            self.logger.info("   • Perfect for local development")
            self.logger.info("   • Uses your existing Azure login")
            self.logger.info("   • No credentials to manage")
            self.logger.info("   • Easy to switch between subscriptions")
            
            return True
            
        except ClientAuthenticationError as e:
            self.logger.error(f"❌ Azure CLI authentication failed: {str(e)}")
            self.logger.info("💡 Azure CLI Troubleshooting:")
            self.logger.info("   1. Run 'az login' to authenticate")
            self.logger.info("   2. Check 'az account show' to verify your login")
            self.logger.info("   3. Ensure you have access to the search service")
            self.logger.info("   4. Try 'az account set --subscription <subscription-id>'")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {str(e)}")
            return False
    
    def compare_authentication_methods(self) -> Dict[str, Any]:
        """
        Compare different authentication methods and their use cases.
        
        Returns:
            Dict containing comparison results
        """
        self.logger.info("📊 Authentication Methods Comparison")
        self.logger.info("=" * 40)
        
        methods = {
            'API Key': {
                'security': 'Medium',
                'ease_of_use': 'High',
                'production_ready': 'Limited',
                'use_cases': ['Development', 'Testing', 'Simple applications'],
                'pros': ['Easy to set up', 'Works everywhere', 'Simple to understand'],
                'cons': ['Manual key management', 'Key rotation needed', 'Less secure']
            },
            'Managed Identity': {
                'security': 'High',
                'ease_of_use': 'Medium',
                'production_ready': 'Excellent',
                'use_cases': ['Production workloads', 'Azure-hosted apps', 'Enterprise scenarios'],
                'pros': ['No secrets to manage', 'Automatic rotation', 'Azure RBAC integration'],
                'cons': ['Azure environment only', 'More complex setup', 'Learning curve']
            },
            'Service Principal': {
                'security': 'High',
                'ease_of_use': 'Medium',
                'production_ready': 'Good',
                'use_cases': ['CI/CD pipelines', 'Automation', 'Cross-tenant access'],
                'pros': ['Good for automation', 'Cross-tenant support', 'Audit trail'],
                'cons': ['Secret management needed', 'More complex', 'Expiration handling']
            },
            'Azure CLI': {
                'security': 'Medium',
                'ease_of_use': 'High',
                'production_ready': 'No',
                'use_cases': ['Local development', 'Testing', 'Interactive scenarios'],
                'pros': ['Great for development', 'No credential storage', 'Easy switching'],
                'cons': ['Development only', 'Requires CLI', 'Interactive login needed']
            }
        }
        
        # Display comparison table
        for method, details in methods.items():
            self.logger.info(f"\n🔐 {method}:")
            self.logger.info(f"   Security: {details['security']}")
            self.logger.info(f"   Ease of Use: {details['ease_of_use']}")
            self.logger.info(f"   Production Ready: {details['production_ready']}")
            self.logger.info(f"   Use Cases: {', '.join(details['use_cases'])}")
        
        # Recommendations
        self.logger.info("\n💡 Recommendations:")
        self.logger.info("   🏠 Local Development: Azure CLI or API Key")
        self.logger.info("   🧪 Testing: API Key")
        self.logger.info("   🏭 Production: Managed Identity (preferred) or Service Principal")
        self.logger.info("   🤖 Automation/CI-CD: Service Principal")
        
        return methods
    
    def run_authentication_demo(self) -> Dict[str, bool]:
        """
        Run a comprehensive demonstration of all authentication methods.
        
        Returns:
            Dict containing results of each authentication method
        """
        self.logger.info("🚀 Comprehensive Authentication Demonstration")
        self.logger.info("=" * 55)
        
        results = {}
        
        # Test each authentication method
        auth_methods = [
            ("API Key", self.demonstrate_api_key_authentication),
            ("Managed Identity", self.demonstrate_managed_identity_authentication),
            ("Service Principal", self.demonstrate_service_principal_authentication),
            ("Azure CLI", self.demonstrate_azure_cli_authentication)
        ]
        
        for method_name, method_func in auth_methods:
            self.logger.info(f"\n{'='*20} {method_name} {'='*20}")
            try:
                results[method_name] = method_func()
            except Exception as e:
                self.logger.error(f"❌ {method_name} demo failed: {str(e)}")
                results[method_name] = False
        
        # Display summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 Authentication Demo Summary")
        self.logger.info("=" * 60)
        
        successful_methods = [method for method, success in results.items() if success]
        failed_methods = [method for method, success in results.items() if not success]
        
        if successful_methods:
            self.logger.info(f"✅ Successful Methods ({len(successful_methods)}):")
            for method in successful_methods:
                self.logger.info(f"   • {method}")
        
        if failed_methods:
            self.logger.info(f"\n❌ Failed Methods ({len(failed_methods)}):")
            for method in failed_methods:
                self.logger.info(f"   • {method}")
        
        # Compare methods
        self.logger.info("\n" + "=" * 40)
        self.compare_authentication_methods()
        
        return results


def main():
    """
    Main function demonstrating Azure AI Search authentication methods.
    
    This function provides a comprehensive walkthrough of different
    authentication approaches with practical examples and best practices.
    """
    print("🔐 Azure AI Search Authentication Examples")
    print("=" * 50)
    print("This script demonstrates different authentication methods for Azure AI Search.")
    print("You'll learn when and how to use each method effectively.")
    print()
    
    # Create demo instance
    demo = AuthenticationDemo()
    
    # Run comprehensive demonstration
    results = demo.run_authentication_demo()
    
    # Provide guidance based on results
    print("\n🎯 Next Steps Based on Your Results:")
    
    successful_count = sum(results.values())
    
    if successful_count > 0:
        print(f"✅ Great! You have {successful_count} working authentication method(s).")
        print("   1. Choose the most appropriate method for your use case")
        print("   2. Implement proper error handling in your applications")
        print("   3. Follow security best practices for credential management")
        print("   4. Move on to Module 2: Basic Search Operations")
    else:
        print("❌ No authentication methods worked. Please:")
        print("   1. Check your Azure AI Search service configuration")
        print("   2. Verify your credentials and permissions")
        print("   3. Run the troubleshooting script for detailed diagnostics")
        print("   4. Review the authentication setup documentation")
    
    print("\n📚 Additional Resources:")
    print("   🔧 Troubleshooting: python code-samples/troubleshooting_utilities.py")
    print("   📋 Configuration: python code-samples/configuration_validation.py")
    print("   📖 Documentation: docs/beginner/module-01-introduction-setup/documentation.md")
    print("   🌐 Azure Portal: https://portal.azure.com")


if __name__ == "__main__":
    main()