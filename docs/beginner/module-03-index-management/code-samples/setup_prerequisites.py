#!/usr/bin/env python3
"""
Prerequisites Setup for Module 3: Index Management
==================================================

This script sets up your environment for Module 3 by:
1. Validating your Azure AI Search service connection
2. Creating sample indexes for learning and practice
3. Testing index management operations
4. Providing sample data for exercises

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import List, Dict, Any

try:
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SimpleField,
        SearchableField,
        ComplexField,
        SearchFieldDataType
    )
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
except ImportError as e:
    print("❌ Missing required packages. Please install:")
    print("   pip install azure-search-documents python-dotenv")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

class IndexManagementSetup:
    """Setup class for Module 3: Index Management"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_client = None
        self.sample_indexes = [
            "handbook-blog-posts",
            "handbook-products", 
            "handbook-documents"
        ]
        
    def validate_environment(self) -> bool:
        """Validate environment configuration"""
        print("🔍 Validating Environment Configuration...")
        
        if not self.endpoint:
            print("❌ AZURE_SEARCH_SERVICE_ENDPOINT not set")
            return False
            
        if not self.admin_key:
            print("❌ AZURE_SEARCH_ADMIN_KEY not set")
            return False
            
        print("✅ Environment variables configured")
        return True
    
    def create_index_client(self) -> bool:
        """Create and test index client connection"""
        print("🔍 Creating Index Client...")
        
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Test connection
            stats = self.index_client.get_service_statistics()
            print(f"✅ Connected to Azure AI Search service")
            print(f"   Storage used: {stats.storage_size_in_bytes:,} bytes")
            print(f"   Document count: {stats.document_count:,}")
            
            return True
            
        except HttpResponseError as e:
            if e.status_code == 403:
                print("❌ Access denied - check your admin API key")
            else:
                print(f"❌ HTTP error {e.status_code}: {e.message}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to create index client: {str(e)}")
            return False
    
    def create_blog_posts_index(self) -> bool:
        """Create blog posts sample index"""
        print("🔍 Creating Blog Posts Index...")
        
        try:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String, 
                              analyzer_name="en.microsoft"),
                SearchableField(name="content", type=SearchFieldDataType.String,
                              analyzer_name="en.microsoft"),
                SimpleField(name="author", type=SearchFieldDataType.String, 
                           filterable=True, facetable=True),
                SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset,
                           filterable=True, sortable=True),
                SimpleField(name="category", type=SearchFieldDataType.String,
                           filterable=True, facetable=True),
                SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                           filterable=True, facetable=True),
                SimpleField(name="rating", type=SearchFieldDataType.Double,
                           filterable=True, sortable=True),
                SimpleField(name="viewCount", type=SearchFieldDataType.Int32,
                           filterable=True, sortable=True),
                SimpleField(name="isPublished", type=SearchFieldDataType.Boolean,
                           filterable=True)
            ]
            
            index = SearchIndex(name="handbook-blog-posts", fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            print(f"✅ Blog posts index '{result.name}' created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create blog posts index: {str(e)}")
            return False
    
    def create_products_index(self) -> bool:
        """Create products sample index"""
        print("🔍 Creating Products Index...")
        
        try:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="name", type=SearchFieldDataType.String),
                SearchableField(name="description", type=SearchFieldDataType.String),
                SimpleField(name="category", type=SearchFieldDataType.String,
                           filterable=True, facetable=True),
                SimpleField(name="brand", type=SearchFieldDataType.String,
                           filterable=True, facetable=True),
                SimpleField(name="price", type=SearchFieldDataType.Double,
                           filterable=True, sortable=True),
                SimpleField(name="inStock", type=SearchFieldDataType.Boolean,
                           filterable=True),
                SimpleField(name="stockQuantity", type=SearchFieldDataType.Int32,
                           filterable=True, sortable=True),
                SimpleField(name="features", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                           filterable=True, facetable=True),
                SimpleField(name="rating", type=SearchFieldDataType.Double,
                           filterable=True, sortable=True),
                SimpleField(name="reviewCount", type=SearchFieldDataType.Int32,
                           filterable=True, sortable=True)
            ]
            
            index = SearchIndex(name="handbook-products", fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            print(f"✅ Products index '{result.name}' created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create products index: {str(e)}")
            return False
    
    def create_documents_index(self) -> bool:
        """Create documents sample index with complex fields"""
        print("🔍 Creating Documents Index...")
        
        try:
            # Complex field for author information
            author_fields = [
                SimpleField(name="name", type=SearchFieldDataType.String),
                SimpleField(name="email", type=SearchFieldDataType.String),
                SimpleField(name="department", type=SearchFieldDataType.String)
            ]
            
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                ComplexField(name="author", fields=author_fields),
                SimpleField(name="documentType", type=SearchFieldDataType.String,
                           filterable=True, facetable=True),
                SimpleField(name="createdDate", type=SearchFieldDataType.DateTimeOffset,
                           filterable=True, sortable=True),
                SimpleField(name="lastModified", type=SearchFieldDataType.DateTimeOffset,
                           filterable=True, sortable=True),
                SimpleField(name="fileSize", type=SearchFieldDataType.Int64,
                           filterable=True, sortable=True),
                SimpleField(name="language", type=SearchFieldDataType.String,
                           filterable=True, facetable=True),
                SimpleField(name="keywords", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                           filterable=True, facetable=True),
                SimpleField(name="isConfidential", type=SearchFieldDataType.Boolean,
                           filterable=True)
            ]
            
            index = SearchIndex(name="handbook-documents", fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            print(f"✅ Documents index '{result.name}' created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create documents index: {str(e)}")
            return False
    
    def populate_sample_data(self) -> bool:
        """Populate indexes with sample data"""
        print("🔍 Populating Sample Data...")
        
        try:
            # Blog posts sample data
            blog_posts = [
                {
                    "id": "1",
                    "title": "Getting Started with Azure AI Search",
                    "content": "Azure AI Search is a powerful search service that provides rich search capabilities for your applications. Learn the basics of setting up and using Azure AI Search.",
                    "author": "John Doe",
                    "publishedDate": "2024-01-15T10:00:00Z",
                    "category": "Tutorial",
                    "tags": ["azure", "search", "tutorial", "beginner"],
                    "rating": 4.5,
                    "viewCount": 1250,
                    "isPublished": True
                },
                {
                    "id": "2",
                    "title": "Advanced Search Techniques",
                    "content": "Master advanced search techniques including faceting, filtering, and custom scoring profiles to build sophisticated search experiences.",
                    "author": "Jane Smith",
                    "publishedDate": "2024-01-20T14:30:00Z",
                    "category": "Advanced",
                    "tags": ["azure", "search", "advanced", "faceting"],
                    "rating": 4.8,
                    "viewCount": 890,
                    "isPublished": True
                },
                {
                    "id": "3",
                    "title": "Index Management Best Practices",
                    "content": "Learn best practices for managing search indexes including schema design, data ingestion strategies, and performance optimization.",
                    "author": "Mike Johnson",
                    "publishedDate": "2024-01-25T09:15:00Z",
                    "category": "Best Practices",
                    "tags": ["azure", "search", "index", "management"],
                    "rating": 4.7,
                    "viewCount": 675,
                    "isPublished": True
                }
            ]
            
            # Upload blog posts
            blog_client = SearchClient(
                endpoint=self.endpoint,
                index_name="handbook-blog-posts",
                credential=AzureKeyCredential(self.admin_key)
            )
            result = blog_client.upload_documents(blog_posts)
            successful_blogs = sum(1 for r in result if r.succeeded)
            print(f"✅ Uploaded {successful_blogs}/{len(blog_posts)} blog posts")
            
            # Products sample data
            products = [
                {
                    "id": "p1",
                    "name": "Azure Search Pro License",
                    "description": "Professional license for Azure AI Search with advanced features and support.",
                    "category": "Software",
                    "brand": "Microsoft",
                    "price": 299.99,
                    "inStock": True,
                    "stockQuantity": 100,
                    "features": ["advanced-search", "analytics", "support"],
                    "rating": 4.6,
                    "reviewCount": 45
                },
                {
                    "id": "p2",
                    "name": "Search Analytics Dashboard",
                    "description": "Comprehensive analytics dashboard for monitoring search performance and user behavior.",
                    "category": "Analytics",
                    "brand": "SearchCorp",
                    "price": 149.99,
                    "inStock": True,
                    "stockQuantity": 25,
                    "features": ["real-time", "dashboards", "reporting"],
                    "rating": 4.3,
                    "reviewCount": 28
                }
            ]
            
            # Upload products
            products_client = SearchClient(
                endpoint=self.endpoint,
                index_name="handbook-products",
                credential=AzureKeyCredential(self.admin_key)
            )
            result = products_client.upload_documents(products)
            successful_products = sum(1 for r in result if r.succeeded)
            print(f"✅ Uploaded {successful_products}/{len(products)} products")
            
            # Documents sample data
            documents = [
                {
                    "id": "d1",
                    "title": "Azure AI Search Architecture Guide",
                    "content": "Comprehensive guide to Azure AI Search architecture, covering service tiers, scaling, and deployment patterns.",
                    "author": {
                        "name": "Sarah Wilson",
                        "email": "sarah.wilson@company.com",
                        "department": "Engineering"
                    },
                    "documentType": "Technical Guide",
                    "createdDate": "2024-01-10T08:00:00Z",
                    "lastModified": "2024-01-15T16:30:00Z",
                    "fileSize": 2048576,
                    "language": "en",
                    "keywords": ["architecture", "azure", "search", "guide"],
                    "isConfidential": False
                },
                {
                    "id": "d2",
                    "title": "Search Implementation Checklist",
                    "content": "Step-by-step checklist for implementing Azure AI Search in production environments.",
                    "author": {
                        "name": "David Chen",
                        "email": "david.chen@company.com",
                        "department": "DevOps"
                    },
                    "documentType": "Checklist",
                    "createdDate": "2024-01-12T11:20:00Z",
                    "lastModified": "2024-01-18T14:45:00Z",
                    "fileSize": 512000,
                    "language": "en",
                    "keywords": ["implementation", "checklist", "production"],
                    "isConfidential": False
                }
            ]
            
            # Upload documents
            documents_client = SearchClient(
                endpoint=self.endpoint,
                index_name="handbook-documents",
                credential=AzureKeyCredential(self.admin_key)
            )
            result = documents_client.upload_documents(documents)
            successful_docs = sum(1 for r in result if r.succeeded)
            print(f"✅ Uploaded {successful_docs}/{len(documents)} documents")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to populate sample data: {str(e)}")
            return False
    
    def test_index_operations(self) -> bool:
        """Test basic index operations"""
        print("🔍 Testing Index Operations...")
        
        try:
            # List indexes
            indexes = list(self.index_client.list_indexes())
            handbook_indexes = [idx for idx in indexes if idx.name.startswith("handbook-")]
            print(f"✅ Found {len(handbook_indexes)} handbook indexes")
            
            # Test getting index details
            for index_name in self.sample_indexes:
                try:
                    index = self.index_client.get_index(index_name)
                    print(f"✅ Retrieved index '{index.name}' with {len(index.fields)} fields")
                except Exception as e:
                    print(f"⚠️  Could not retrieve index '{index_name}': {str(e)}")
            
            # Test search client creation
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name="handbook-blog-posts",
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Test document count
            doc_count = search_client.get_document_count()
            print(f"✅ Blog posts index contains {doc_count} documents")
            
            return True
            
        except Exception as e:
            print(f"❌ Index operations test failed: {str(e)}")
            return False
    
    def cleanup_old_indexes(self) -> bool:
        """Clean up any old test indexes"""
        print("🔍 Cleaning Up Old Test Indexes...")
        
        try:
            indexes = list(self.index_client.list_indexes())
            test_indexes = [idx for idx in indexes if idx.name.startswith("test-") or idx.name.startswith("temp-")]
            
            for index in test_indexes:
                try:
                    self.index_client.delete_index(index.name)
                    print(f"✅ Deleted old test index '{index.name}'")
                except Exception as e:
                    print(f"⚠️  Could not delete index '{index.name}': {str(e)}")
            
            if not test_indexes:
                print("✅ No old test indexes to clean up")
            
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")
            return False
    
    def run_setup(self) -> bool:
        """Run complete setup process"""
        print("=" * 60)
        print("Module 3: Index Management - Prerequisites Setup")
        print("=" * 60)
        
        steps = [
            ("Environment Validation", self.validate_environment),
            ("Index Client Creation", self.create_index_client),
            ("Cleanup Old Indexes", self.cleanup_old_indexes),
            ("Blog Posts Index", self.create_blog_posts_index),
            ("Products Index", self.create_products_index),
            ("Documents Index", self.create_documents_index),
            ("Sample Data Population", self.populate_sample_data),
            ("Index Operations Test", self.test_index_operations)
        ]
        
        results = []
        for step_name, step_func in steps:
            print(f"\n{step_name}:")
            print("-" * 40)
            success = step_func()
            results.append(success)
            
            if not success and step_name in ["Environment Validation", "Index Client Creation"]:
                print(f"\n❌ Critical step '{step_name}' failed. Stopping setup.")
                break
        
        # Summary
        print("\n" + "=" * 60)
        print("SETUP SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print("🎉 SETUP COMPLETED SUCCESSFULLY!")
            print("\nCreated indexes:")
            for index_name in self.sample_indexes:
                print(f"   ✅ {index_name}")
            
            print("\nNext steps:")
            print("1. 📚 Read Module 3 documentation")
            print("2. 🔬 Try the code samples")
            print("3. 📝 Complete the exercises")
            print("4. 🏗️ Build your own indexes!")
            
            return True
        else:
            print(f"⚠️  Setup partially completed: {passed}/{total} steps successful")
            print("\nPlease resolve any issues and run setup again.")
            return False

def main():
    """Main setup function"""
    setup = IndexManagementSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🚀 You're ready to start Module 3: Index Management!")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()