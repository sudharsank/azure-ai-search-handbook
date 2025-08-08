"""
Quick test script to verify the prerequisites setup worked correctly.
Run this after running setup_prerequisites.py to confirm everything is ready.
"""

import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

def test_setup():
    """Test that the prerequisites setup completed successfully."""
    print("🧪 Testing Prerequisites Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT", "")
    api_key = os.getenv("AZURE_SEARCH_API_KEY", "")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "handbook-samples")
    
    if not endpoint or not api_key:
        print("❌ Environment variables not set properly")
        return False
    
    try:
        # Create search client
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        
        # Test 1: Check document count
        doc_count = search_client.get_document_count()
        print(f"✅ Index '{index_name}' contains {doc_count} documents")
        
        if doc_count == 0:
            print("⚠️ No documents found. Did you run setup_prerequisites.py?")
            return False
        
        # Test 2: Simple search
        results = list(search_client.search(search_text="python", top=3))
        print(f"✅ Simple search works - found {len(results)} results for 'python'")
        
        # Test 3: Show sample result
        if results:
            first_result = results[0]
            title = first_result.get('title', 'No title')
            score = first_result['@search.score']
            print(f"✅ Sample result: '{title}' (Score: {score:.3f})")
        
        print(f"\n🎉 Setup verification successful!")
        print(f"📚 You can now run:")
        print(f"   • basic_search.ipynb (interactive notebook)")
        print(f"   • Python examples in python/ directory")
        print(f"   • C# examples in csharp/ directory")
        print(f"   • JavaScript examples in javascript/ directory")
        print(f"   • REST API examples in rest/ directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print(f"💡 Make sure you ran 'python setup_prerequisites.py' first")
        return False

if __name__ == "__main__":
    test_setup()