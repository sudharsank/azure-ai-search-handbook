"""
Exercise 1 Solution: Basic Setup and Connection
Complete implementation with detailed explanations
"""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, AzureError

def setup_environment():
    """
    Solution: Set up your environment variables
    
    This function validates that all required environment variables are present
    and provides helpful guidance if they're missing.
    """
    print("🔧 Setting up environment...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for required environment variables
    required_vars = {
        'AZURE_SEARCH_SERVICE_ENDPOINT': 'Your Azure AI Search service endpoint URL',
        'AZURE_SEARCH_API_KEY': 'Your Azure AI Search API key',
        'AZURE_SEARCH_INDEX_NAME': 'Default index name for testing'
    }
    
    missing_vars = []
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(f"{var_name}: {description}")
        else:
            # Mask sensitive information in output
            display_value = value if 'KEY' not in var_name else f"{value[:8]}..."
            print(f"✅ {var_name}: {display_value}")
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Create a .env file in your project root with these variables.")
        return False
    
    print("✅ Environment setup complete!")
    return True

def create_client():
    """
    Solution: Create an Azure AI Search client
    
    This function creates both SearchIndexClient (for admin operations)
    and SearchClient (for document operations) with proper error handling.
    """
    print("🔧 Creating Azure AI Search clients...")
    
    # Load configuration
    endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
    api_key = os.getenv('AZURE_SEARCH_API_KEY')
    index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
    
    if not endpoint or not api_key:
        print("❌ Missing endpoint or API key configuration")
        return None, None
    
    try:
        # Create credential object
        credential = AzureKeyCredential(api_key)
        print("✅ Credential created successfully")
        
        # Create SearchIndexClient for administrative operations
        index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=credential
        )
        print("✅ SearchIndexClient created successfully")
        
        # Create SearchClient for document operations (if index name provided)
        search_client = None
        if index_name:
            search_client = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=credential
            )
            print(f"✅ SearchClient created for index: {index_name}")
        else:
            print("⚠️  No index name provided - SearchClient not created")
        
        return index_client, search_client
        
    except Exception as e:
        print(f"❌ Failed to create clients: {str(e)}")
        return None, None

def validate_connection():
    """
    Solution: Validate your connection works
    
    This function tests the connection by performing actual operations
    and provides detailed feedback about the connection status.
    """
    print("🔧 Validating connection...")
    
    try:
        # Get clients
        index_client, search_client = create_client()
        
        if not index_client:
            print("❌ Cannot validate connection - client creation failed")
            return False
        
        # Test 1: Get service statistics
        print("📊 Testing service statistics...")
        stats = index_client.get_service_statistics()
        
        print("✅ Service statistics retrieved successfully!")
        print(f"   • Document count: {stats.counters.document_count:,}")
        print(f"   • Index count: {stats.counters.index_count}")
        print(f"   • Storage size: {stats.counters.storage_size:,} bytes")
        
        # Test 2: List indexes
        print("\n📋 Testing index listing...")
        indexes = list(index_client.list_indexes())
        print(f"✅ Found {len(indexes)} indexes:")
        
        for idx in indexes[:3]:  # Show first 3 indexes
            print(f"   • {idx.name} ({len(idx.fields)} fields)")
        
        if len(indexes) > 3:
            print(f"   ... and {len(indexes) - 3} more")
        
        # Test 3: Test SearchClient if available
        if search_client:
            print(f"\n🔍 Testing SearchClient access...")
            try:
                doc_count = search_client.get_document_count()
                print(f"✅ Index access successful - {doc_count:,} documents")
            except Exception as e:
                print(f"⚠️  Index access failed: {str(e)}")
                print("💡 This might mean the index doesn't exist yet")
        
        return True
        
    except ClientAuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("💡 Check your API key and ensure it has the correct permissions")
        return False
        
    except Exception as e:
        print(f"❌ Connection validation failed: {str(e)}")
        print("💡 Check your endpoint URL and network connectivity")
        return False

def main():
    """
    Main function that orchestrates the complete setup and validation process
    """
    print("🚀 Azure AI Search Setup Exercise - Solution")
    print("=" * 50)
    
    # Step 1: Environment setup
    print("\n📋 Step 1: Environment Setup")
    env_success = setup_environment()
    
    if not env_success:
        print("\n❌ Environment setup failed. Please fix the issues above.")
        return False
    
    # Step 2: Client creation
    print("\n🔧 Step 2: Client Creation")
    index_client, search_client = create_client()
    
    if not index_client:
        print("\n❌ Client creation failed. Please check your configuration.")
        return False
    
    # Step 3: Connection validation
    print("\n✅ Step 3: Connection Validation")
    connection_success = validate_connection()
    
    if connection_success:
        print("\n🎉 Congratulations! Your Azure AI Search setup is complete and working!")
        print("\n🎯 What you've accomplished:")
        print("   ✅ Environment variables configured correctly")
        print("   ✅ Azure AI Search clients created successfully")
        print("   ✅ Connection to Azure AI Search service verified")
        print("   ✅ Service statistics and indexes accessed")
        
        print("\n📚 Next Steps:")
        print("   1. Try Exercise 2: Environment Validation")
        print("   2. Explore the code samples in the code-samples/ directory")
        print("   3. Read the documentation for deeper understanding")
        
        return True
    else:
        print("\n❌ Connection validation failed. Please review the errors above.")
        print("\n🔧 Troubleshooting Tips:")
        print("   1. Verify your Azure AI Search service is running")
        print("   2. Check that your API key is correct and hasn't expired")
        print("   3. Ensure your endpoint URL is properly formatted")
        print("   4. Run the troubleshooting script: python code-samples/troubleshooting_utilities.py")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)