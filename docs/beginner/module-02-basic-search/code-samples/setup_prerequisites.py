"""
Prerequisites Setup for Module 2: Basic Search Operations
=========================================================

⚠️ IMPORTANT: Run this script BEFORE attempting the basic search examples!

This script will set up everything you need to successfully run the basic search operations examples:

1. ✅ Validates your Azure AI Search connection
2. 🏗️ Creates a sample index (if it doesn't exist)
3. 📄 Uploads sample documents with rich content for searching
4. 🧪 Tests all functionality to ensure everything works
5. 📋 Provides a summary of what's ready for the basic search examples

Prerequisites:
- Azure AI Search service created in Azure portal
- Environment variables set (see instructions below)
- Python packages: azure-search-documents, python-dotenv

Time Required: ⏱️ 5-10 minutes (depending on your internet connection)

Usage:
    python setup_prerequisites.py

Author: Azure AI Search Handbook
Module: Beginner - Module 2: Basic Search Operations
"""

import os
import json
import logging
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Azure AI Search SDK imports
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceExistsError

# Environment imports
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PrerequisitesSetup:
    """
    Comprehensive setup class for Module 2 prerequisites.
    
    This class handles all the setup required for the basic search examples,
    including index creation, document upload, and functionality testing.
    """
    
    def __init__(self):
        """Initialize the prerequisites setup."""
        print("🚀 Azure AI Search - Module 2 Prerequisites Setup")
        print("=" * 60)
        print("This script will prepare everything needed for the basic search examples.")
        print()
        
        # Load environment variables
        load_dotenv()
        
        # Configuration
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT", "")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY", "")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "handbook-samples")
        
        # Clients (will be initialized later)
        self.index_client = None
        self.search_client = None
        
        # Status tracking
        self.setup_status = {
            'connection_tested': False,
            'index_created': False,
            'documents_uploaded': False,
            'functionality_tested': False
        }
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is present."""
        print("🔧 Step 1: Validating Configuration")
        print("-" * 40)
        
        print(f"   Endpoint: {self.endpoint}")
        print(f"   Index Name: {self.index_name}")
        print(f"   API Key: {'***' + self.api_key[-4:] if len(self.api_key) > 4 else '***'}")
        
        missing_config = []
        
        if not self.endpoint or self.endpoint == "https://your-service.search.windows.net":
            missing_config.append("AZURE_SEARCH_SERVICE_ENDPOINT")
        
        if not self.api_key or self.api_key == "your-api-key":
            missing_config.append("AZURE_SEARCH_API_KEY")
        
        if missing_config:
            print(f"\\n❌ Missing or invalid configuration: {', '.join(missing_config)}")
            print("\\n📝 To fix this, set the following environment variables:")
            print("   export AZURE_SEARCH_SERVICE_ENDPOINT='https://your-service.search.windows.net'")
            print("   export AZURE_SEARCH_API_KEY='your-api-key'")
            print("   export AZURE_SEARCH_INDEX_NAME='handbook-samples'")
            print("\\nOr create a .env file with these values.")
            return False
        
        print("\\n✅ Configuration validation passed!")
        return True
    
    def test_connection(self) -> bool:
        """Test connection to Azure AI Search service."""
        print("\\n🔌 Step 2: Testing Connection")
        print("-" * 40)
        
        try:
            # Create index client
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.api_key)
            )
            
            # Test connection
            stats = self.index_client.get_service_statistics()
            
            print("✅ Connection successful!")
            print(f"📊 Service Statistics:")
            
            # Handle different response formats
            if hasattr(stats, 'counters'):
                # Newer SDK format
                print(f"   - Total Documents: {stats.counters.document_count:,}")
                print(f"   - Total Indexes: {stats.counters.index_count}")
                print(f"   - Storage Used: {stats.counters.storage_size:,} bytes")
            elif isinstance(stats, dict) and 'counters' in stats:
                # Dictionary format
                counters = stats['counters']
                print(f"   - Total Documents: {counters.get('documentCount', 0):,}")
                print(f"   - Total Indexes: {counters.get('indexCount', 0)}")
                print(f"   - Storage Used: {counters.get('storageSize', 0):,} bytes")
            else:
                # Fallback - just show that connection works
                print("   - Connection verified successfully")
                print("   - Service is responding to requests")
            
            self.setup_status['connection_tested'] = True
            return True
            
        except HttpResponseError as e:
            print(f"❌ HTTP Error: {e.status_code} - {e.message}")
            if e.status_code == 401:
                print("💡 This usually means your API key is incorrect")
            elif e.status_code == 404:
                print("💡 This usually means your service endpoint is incorrect")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def check_existing_index(self) -> bool:
        """Check if the target index already exists."""
        try:
            indexes = list(self.index_client.list_indexes())
            
            if indexes:
                print(f"\\n📋 Found {len(indexes)} existing indexes:")
                for i, index in enumerate(indexes, 1):
                    print(f"   {i}. {index.name} ({len(index.fields)} fields)")
                
                # Check if our target index exists
                target_exists = any(index.name == self.index_name for index in indexes)
                if target_exists:
                    print(f"\\n🎯 Target index '{self.index_name}' already exists!")
                    return True
                else:
                    print(f"\\n📝 Target index '{self.index_name}' does not exist yet.")
                    return False
            else:
                print("\\n📝 No indexes found. We'll create one for you.")
                return False
                
        except Exception as e:
            print(f"❌ Error checking indexes: {str(e)}")
            return False
    
    def create_sample_index(self) -> bool:
        """Create a comprehensive sample index for basic search demonstrations."""
        print("\\n🏗️ Step 3: Creating Sample Index")
        print("-" * 40)
        
        try:
            print(f"Creating index: {self.index_name}")
            
            # Define comprehensive index schema
            fields = [
                # Primary key
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                
                # Main searchable fields
                SearchableField(name="title", type=SearchFieldDataType.String, 
                              searchable=True, filterable=True, sortable=True),
                SearchableField(name="content", type=SearchFieldDataType.String, 
                              searchable=True, analyzer_name="en.microsoft"),
                SearchableField(name="description", type=SearchFieldDataType.String, 
                              searchable=True),
                
                # Metadata fields
                SimpleField(name="author", type=SearchFieldDataType.String, 
                           filterable=True, sortable=True, facetable=True),
                SimpleField(name="category", type=SearchFieldDataType.String, 
                           filterable=True, facetable=True),
                SearchableField(name="tags", type=SearchFieldDataType.String, 
                              searchable=True, filterable=True, facetable=True),
                
                # Date and numeric fields
                SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, 
                           filterable=True, sortable=True, facetable=True),
                SimpleField(name="rating", type=SearchFieldDataType.Double, 
                           filterable=True, sortable=True, facetable=True),
                SimpleField(name="viewCount", type=SearchFieldDataType.Int32, 
                           filterable=True, sortable=True),
                
                # Additional fields
                SimpleField(name="url", type=SearchFieldDataType.String),
                SimpleField(name="language", type=SearchFieldDataType.String, 
                           filterable=True, facetable=True),
                SimpleField(name="difficulty", type=SearchFieldDataType.String, 
                           filterable=True, facetable=True)
            ]
            
            # Create the index
            index = SearchIndex(name=self.index_name, fields=fields)
            result = self.index_client.create_index(index)
            
            print(f"✅ Index '{self.index_name}' created successfully!")
            print(f"📋 Index contains {len(fields)} fields suitable for all basic search operations")
            
            self.setup_status['index_created'] = True
            return True
            
        except ResourceExistsError:
            print(f"ℹ️ Index '{self.index_name}' already exists, skipping creation.")
            self.setup_status['index_created'] = True
            return True
        except Exception as e:
            print(f"❌ Failed to create index: {str(e)}")
            return False
    
    def generate_sample_documents(self) -> List[Dict[str, Any]]:
        """Generate comprehensive sample documents for search demonstrations."""
        print("\\n📄 Step 4: Generating Sample Documents")
        print("-" * 40)
        
        documents = [
            {
                "id": "1",
                "title": "Python Programming Fundamentals",
                "content": "Learn the basics of Python programming language. This comprehensive guide covers variables, data types, control structures, functions, and object-oriented programming concepts. Perfect for beginners who want to start their programming journey with Python.",
                "description": "A beginner-friendly introduction to Python programming",
                "author": "John Smith",
                "category": "Programming",
                "tags": "python, programming, beginner, tutorial",
                "publishedDate": "2024-01-15T10:00:00Z",
                "rating": 4.5,
                "viewCount": 1250,
                "url": "https://example.com/python-fundamentals",
                "language": "English",
                "difficulty": "Beginner"
            },
            {
                "id": "2",
                "title": "Machine Learning with Python",
                "content": "Explore the world of machine learning using Python. This tutorial covers scikit-learn, pandas, numpy, and matplotlib. Learn about supervised and unsupervised learning, data preprocessing, model evaluation, and deployment strategies.",
                "description": "Complete guide to machine learning using Python libraries",
                "author": "Sarah Johnson",
                "category": "Data Science",
                "tags": "machine learning, python, scikit-learn, data science",
                "publishedDate": "2024-02-01T14:30:00Z",
                "rating": 4.8,
                "viewCount": 2100,
                "url": "https://example.com/ml-python",
                "language": "English",
                "difficulty": "Intermediate"
            },
            {
                "id": "3",
                "title": "Web Development with JavaScript",
                "content": "Master modern web development with JavaScript. Learn about ES6+ features, DOM manipulation, asynchronous programming, and popular frameworks like React and Vue.js. Build responsive and interactive web applications.",
                "description": "Modern JavaScript for web development",
                "author": "Mike Chen",
                "category": "Web Development",
                "tags": "javascript, web development, react, frontend",
                "publishedDate": "2024-01-20T09:15:00Z",
                "rating": 4.3,
                "viewCount": 1800,
                "url": "https://example.com/js-web-dev",
                "language": "English",
                "difficulty": "Intermediate"
            },
            {
                "id": "4",
                "title": "Data Science Tutorial for Beginners",
                "content": "Start your data science journey with this comprehensive tutorial. Learn about data analysis, visualization, statistical concepts, and machine learning basics. Uses Python, pandas, and Jupyter notebooks for hands-on learning.",
                "description": "Introduction to data science concepts and tools",
                "author": "Emily Davis",
                "category": "Data Science",
                "tags": "data science, python, pandas, tutorial, beginner",
                "publishedDate": "2024-01-10T16:45:00Z",
                "rating": 4.6,
                "viewCount": 3200,
                "url": "https://example.com/data-science-tutorial",
                "language": "English",
                "difficulty": "Beginner"
            },
            {
                "id": "5",
                "title": "Advanced Python Programming Techniques",
                "content": "Take your Python skills to the next level with advanced programming techniques. Learn about decorators, context managers, metaclasses, async programming, and performance optimization. Includes real-world examples and best practices.",
                "description": "Advanced Python concepts for experienced developers",
                "author": "David Wilson",
                "category": "Programming",
                "tags": "python, advanced, programming, optimization",
                "publishedDate": "2024-02-10T11:20:00Z",
                "rating": 4.7,
                "viewCount": 950,
                "url": "https://example.com/advanced-python",
                "language": "English",
                "difficulty": "Advanced"
            },
            {
                "id": "6",
                "title": "Artificial Intelligence Overview",
                "content": "Comprehensive overview of artificial intelligence technologies. Covers machine learning, deep learning, natural language processing, computer vision, and AI ethics. Suitable for both technical and non-technical audiences.",
                "description": "Complete introduction to AI technologies and applications",
                "author": "Lisa Anderson",
                "category": "Artificial Intelligence",
                "tags": "artificial intelligence, AI, machine learning, overview",
                "publishedDate": "2024-01-25T13:10:00Z",
                "rating": 4.4,
                "viewCount": 2800,
                "url": "https://example.com/ai-overview",
                "language": "English",
                "difficulty": "Beginner"
            },
            {
                "id": "7",
                "title": "Database Design and SQL",
                "content": "Learn database design principles and SQL programming. Covers relational database concepts, normalization, indexing, query optimization, and advanced SQL features. Includes practical exercises with real datasets.",
                "description": "Complete guide to database design and SQL programming",
                "author": "Robert Taylor",
                "category": "Database",
                "tags": "database, SQL, design, programming",
                "publishedDate": "2024-01-30T08:30:00Z",
                "rating": 4.2,
                "viewCount": 1600,
                "url": "https://example.com/database-sql",
                "language": "English",
                "difficulty": "Intermediate"
            },
            {
                "id": "8",
                "title": "Cloud Computing with Azure",
                "content": "Master cloud computing concepts using Microsoft Azure. Learn about virtual machines, storage, networking, databases, and serverless computing. Includes hands-on labs and real-world deployment scenarios.",
                "description": "Comprehensive Azure cloud computing tutorial",
                "author": "Jennifer Lee",
                "category": "Cloud Computing",
                "tags": "cloud computing, azure, microsoft, tutorial",
                "publishedDate": "2024-02-05T15:45:00Z",
                "rating": 4.6,
                "viewCount": 2200,
                "url": "https://example.com/azure-cloud",
                "language": "English",
                "difficulty": "Intermediate"
            },
            {
                "id": "9",
                "title": "Mobile App Development Guide",
                "content": "Complete guide to mobile app development. Covers native development for iOS and Android, cross-platform frameworks like React Native and Flutter, UI/UX design principles, and app store deployment.",
                "description": "Learn mobile app development from scratch",
                "author": "Alex Rodriguez",
                "category": "Mobile Development",
                "tags": "mobile development, iOS, android, react native",
                "publishedDate": "2024-01-18T12:00:00Z",
                "rating": 4.1,
                "viewCount": 1400,
                "url": "https://example.com/mobile-dev",
                "language": "English",
                "difficulty": "Intermediate"
            },
            {
                "id": "10",
                "title": "Cybersecurity Fundamentals",
                "content": "Essential cybersecurity concepts for developers and IT professionals. Learn about threat modeling, secure coding practices, encryption, authentication, network security, and incident response procedures.",
                "description": "Introduction to cybersecurity principles and practices",
                "author": "Maria Garcia",
                "category": "Security",
                "tags": "cybersecurity, security, encryption, fundamentals",
                "publishedDate": "2024-02-08T10:15:00Z",
                "rating": 4.5,
                "viewCount": 1900,
                "url": "https://example.com/cybersecurity",
                "language": "English",
                "difficulty": "Beginner"
            }
        ]
        
        print(f"✅ Generated {len(documents)} sample documents")
        print("📋 Document topics include:")
        
        categories = {}
        for doc in documents:
            category = doc['category']
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in categories.items():
            print(f"   - {category}: {count} documents")
        
        return documents
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload sample documents to the search index."""
        print("\\n📤 Step 5: Uploading Documents")
        print("-" * 40)
        
        try:
            # Create search client
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.api_key)
            )
            
            print(f"Uploading {len(documents)} documents to index '{self.index_name}'...")
            
            # Upload documents
            result = self.search_client.upload_documents(documents)
            
            # Check results
            successful_uploads = sum(1 for r in result if r.succeeded)
            failed_uploads = len(result) - successful_uploads
            
            if successful_uploads == len(documents):
                print(f"✅ Successfully uploaded all {successful_uploads} documents!")
            else:
                print(f"⚠️ Uploaded {successful_uploads} documents, {failed_uploads} failed")
                for r in result:
                    if not r.succeeded:
                        print(f"   Failed: {r.key} - {r.error_message}")
            
            # Wait for indexing
            print("⏳ Waiting for indexing to complete...")
            time.sleep(3)
            
            # Verify document count
            doc_count = self.search_client.get_document_count()
            print(f"📊 Index now contains {doc_count} documents")
            
            self.setup_status['documents_uploaded'] = successful_uploads > 0
            return successful_uploads > 0
            
        except Exception as e:
            print(f"❌ Failed to upload documents: {str(e)}")
            return False
    
    def test_search_functionality(self) -> bool:
        """Test all basic search operations to ensure they work correctly."""
        print("\\n🧪 Step 6: Testing Search Functionality")
        print("-" * 40)
        
        if not self.search_client:
            print("❌ Cannot test - no search client available")
            return False
        
        test_results = {}
        
        # Test 1: Simple text search
        try:
            print("\\n1️⃣ Testing simple text search...")
            results = list(self.search_client.search(search_text="python programming", top=3))
            test_results['simple_search'] = len(results) > 0
            print(f"   ✅ Found {len(results)} results for 'python programming'")
        except Exception as e:
            test_results['simple_search'] = False
            print(f"   ❌ Simple search failed: {str(e)}")
        
        # Test 2: Phrase search
        try:
            print("\\n2️⃣ Testing phrase search...")
            results = list(self.search_client.search(search_text='"machine learning"', top=3))
            test_results['phrase_search'] = True
            print(f"   ✅ Phrase search works - found {len(results)} results")
        except Exception as e:
            test_results['phrase_search'] = False
            print(f"   ❌ Phrase search failed: {str(e)}")
        
        # Test 3: Boolean search
        try:
            print("\\n3️⃣ Testing boolean search...")
            results = list(self.search_client.search(search_text="python AND tutorial", top=3))
            test_results['boolean_search'] = True
            print(f"   ✅ Boolean search works - found {len(results)} results")
        except Exception as e:
            test_results['boolean_search'] = False
            print(f"   ❌ Boolean search failed: {str(e)}")
        
        # Test 4: Wildcard search
        try:
            print("\\n4️⃣ Testing wildcard search...")
            results = list(self.search_client.search(search_text="program*", top=3))
            test_results['wildcard_search'] = True
            print(f"   ✅ Wildcard search works - found {len(results)} results")
        except Exception as e:
            test_results['wildcard_search'] = False
            print(f"   ❌ Wildcard search failed: {str(e)}")
        
        # Test 5: Field-specific search
        try:
            print("\\n5️⃣ Testing field-specific search...")
            results = list(self.search_client.search(
                search_text="python", 
                search_fields=["title"], 
                top=3
            ))
            test_results['field_search'] = True
            print(f"   ✅ Field search works - found {len(results)} results in title field")
        except Exception as e:
            test_results['field_search'] = False
            print(f"   ❌ Field search failed: {str(e)}")
        
        # Summary
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"\\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\\n🎉 All tests passed! Your setup is ready for the basic search examples.")
            self.setup_status['functionality_tested'] = True
            return True
        else:
            print(f"\\n⚠️ {total_tests - passed_tests} tests failed. Some examples might not work correctly.")
            return False
    
    def display_summary(self) -> None:
        """Display a comprehensive summary of the setup process."""
        print("\\n" + "=" * 60)
        print("📋 SETUP SUMMARY")
        print("=" * 60)
        
        # Configuration
        print("\\n🔧 Configuration:")
        print(f"   Service Endpoint: {self.endpoint}")
        print(f"   Index Name: {self.index_name}")
        print(f"   API Key: {'***' + self.api_key[-4:] if len(self.api_key) > 4 else '***'}")
        
        # Status
        print("\\n✅ Setup Status:")
        for step, completed in self.setup_status.items():
            status = "✅ COMPLETED" if completed else "❌ FAILED"
            step_name = step.replace('_', ' ').title()
            print(f"   {step_name}: {status}")
        
        # Next steps
        all_completed = all(self.setup_status.values())
        
        if all_completed:
            print("\\n🎯 You're Now Ready For:")
            print("   📓 basic_search.ipynb - Interactive basic search operations")
            print("   🐍 Python examples (01-08) - Complete Python implementations")
            print("   🔷 C# examples (01-08) - .NET implementations")
            print("   🟨 JavaScript examples (01-08) - Node.js/Browser implementations")
            print("   🌐 REST API examples (01-08) - Direct HTTP calls")
            
            print("\\n🚀 Next Steps:")
            print("   1. Open and run 'basic_search.ipynb' for interactive learning")
            print("   2. Try the language-specific examples in your preferred language")
            print("   3. Experiment with different search queries and parameters")
            print("   4. Move on to Module 3: Index Management when ready")
        else:
            print("\\n⚠️ Setup Issues Detected:")
            print("   Some steps failed. Please review the errors above and:")
            print("   1. Check your Azure AI Search service configuration")
            print("   2. Verify your API key has the correct permissions")
            print("   3. Ensure your service endpoint URL is correct")
            print("   4. Try running this script again")
    
    def run_complete_setup(self) -> bool:
        """Run the complete prerequisites setup process."""
        print("Starting comprehensive setup process...")
        print()
        
        # Step 1: Validate configuration
        if not self.validate_configuration():
            return False
        
        # Step 2: Test connection
        if not self.test_connection():
            return False
        
        # Step 3: Check/create index
        index_exists = self.check_existing_index()
        if not index_exists:
            if not self.create_sample_index():
                return False
        else:
            self.setup_status['index_created'] = True
        
        # Step 4: Generate and upload documents
        documents = self.generate_sample_documents()
        if not self.upload_documents(documents):
            return False
        
        # Step 5: Test functionality
        if not self.test_search_functionality():
            return False
        
        # Step 6: Display summary
        self.display_summary()
        
        return all(self.setup_status.values())


def main():
    """Main function to run the prerequisites setup."""
    try:
        # Create and run setup
        setup = PrerequisitesSetup()
        success = setup.run_complete_setup()
        
        if success:
            print("\\n" + "=" * 60)
            print("🎊 SETUP COMPLETE! 🎊")
            print("Your Azure AI Search environment is fully ready!")
            print("\\n📚 You can now run the basic search examples:")
            print("   • basic_search.ipynb (interactive notebook)")
            print("   • Python, C#, JavaScript, or REST API examples")
            print("\\n🚀 Happy searching!")
            print("=" * 60)
        else:
            print("\\n" + "=" * 60)
            print("⚠️ SETUP INCOMPLETE")
            print("Some issues were detected. Please review the errors above.")
            print("\\n💡 Need help? Check the documentation or contact support.")
            print("=" * 60)
        
        return success
        
    except KeyboardInterrupt:
        print("\\n\\n⚠️ Setup interrupted by user.")
        return False
    except Exception as e:
        print(f"\\n\\n❌ Unexpected error during setup: {str(e)}")
        return False


if __name__ == "__main__":
    main()