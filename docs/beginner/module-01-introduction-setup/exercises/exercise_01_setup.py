"""
Exercise 1: Basic Setup and Connection
Complete the setup and verify your Azure AI Search connection
"""

# TODO: Import required libraries
# from azure.search.documents import SearchClient
# from azure.core.credentials import AzureKeyCredential

def setup_environment():
    """
    Exercise: Set up your environment variables
    
    Instructions:
    1. Create a .env file in your project root
    2. Add your Azure AI Search service endpoint
    3. Add your API key
    4. Add a default index name
    
    Required variables:
    - AZURE_SEARCH_SERVICE_ENDPOINT
    - AZURE_SEARCH_API_KEY  
    - AZURE_SEARCH_INDEX_NAME
    """
    # TODO: Implement environment setup validation
    pass

def create_client():
    """
    Exercise: Create an Azure AI Search client
    
    Instructions:
    1. Load environment variables
    2. Create SearchClient instance
    3. Return the client
    """
    # TODO: Implement client creation
    pass

def validate_connection():
    """
    Exercise: Validate your connection works
    
    Instructions:
    1. Use your client to perform a simple operation
    2. Handle any connection errors gracefully
    3. Return True if successful, False otherwise
    """
    # TODO: Implement connection validation
    pass

if __name__ == "__main__":
    print("🚀 Starting Azure AI Search Setup Exercise")
    
    # Step 1: Environment setup
    print("\n📋 Step 1: Environment Setup")
    setup_environment()
    
    # Step 2: Client creation
    print("\n🔧 Step 2: Client Creation")
    client = create_client()
    
    # Step 3: Connection validation
    print("\n✅ Step 3: Connection Validation")
    success = validate_connection()
    
    if success:
        print("\n🎉 Congratulations! Your setup is complete.")
    else:
        print("\n❌ Setup incomplete. Please review the instructions.")