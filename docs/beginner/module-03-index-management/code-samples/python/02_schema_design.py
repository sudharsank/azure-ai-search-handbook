#!/usr/bin/env python3
"""
Module 3: Index Management - Advanced Schema Design
==================================================

This example demonstrates advanced schema design patterns and best practices for
Azure AI Search indexes. You'll learn about complex fields, collections, and
optimization strategies for different use cases.

Learning Objectives:
- Design complex field structures
- Use ComplexField for nested objects
- Optimize field attributes for performance
- Handle different data types effectively
- Implement schema design patterns

Prerequisites:
- Completed 01_create_basic_index.py
- Understanding of basic field types
- Azure AI Search service with admin access

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SimpleField,
        SearchableField,
        ComplexField,
        SearchFieldDataType,
        LexicalAnalyzer
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

class AdvancedSchemaDesigner:
    """Demonstrates advanced schema design patterns"""
    
    def __init__(self):
        """Initialize the schema designer"""
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_client = None
        
        if not self.endpoint or not self.admin_key:
            raise ValueError("Missing required environment variables")
    
    def create_index_client(self) -> bool:
        """Create and validate the SearchIndexClient"""
        print("🔍 Creating SearchIndexClient...")
        
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Test connection
            stats = self.index_client.get_service_statistics()
            print(f"✅ Connected to Azure AI Search service")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create index client: {str(e)}")
            return False
    
    def design_ecommerce_schema(self) -> List:
        """Design a comprehensive e-commerce product schema"""
        print("🛍️  Designing E-commerce Product Schema...")
        
        # Complex field for product dimensions
        dimensions_fields = [
            SimpleField(name="length", type=SearchFieldDataType.Double),
            SimpleField(name="width", type=SearchFieldDataType.Double),
            SimpleField(name="height", type=SearchFieldDataType.Double),
            SimpleField(name="weight", type=SearchFieldDataType.Double),
            SimpleField(name="unit", type=SearchFieldDataType.String)
        ]
        
        # Complex field for pricing information
        pricing_fields = [
            SimpleField(name="basePrice", type=SearchFieldDataType.Double, sortable=True),
            SimpleField(name="salePrice", type=SearchFieldDataType.Double, sortable=True),
            SimpleField(name="currency", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="discountPercentage", type=SearchFieldDataType.Double),
            SimpleField(name="validUntil", type=SearchFieldDataType.DateTimeOffset, filterable=True)
        ]
        
        # Complex field for manufacturer information
        manufacturer_fields = [
            SimpleField(name="name", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="country", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="website", type=SearchFieldDataType.String),
            SimpleField(name="supportEmail", type=SearchFieldDataType.String)
        ]
        
        # Complex field for ratings and reviews
        reviews_fields = [
            SimpleField(name="averageRating", type=SearchFieldDataType.Double, sortable=True, filterable=True),
            SimpleField(name="totalReviews", type=SearchFieldDataType.Int32, sortable=True),
            SimpleField(name="fiveStarCount", type=SearchFieldDataType.Int32),
            SimpleField(name="fourStarCount", type=SearchFieldDataType.Int32),
            SimpleField(name="threeStarCount", type=SearchFieldDataType.Int32),
            SimpleField(name="twoStarCount", type=SearchFieldDataType.Int32),
            SimpleField(name="oneStarCount", type=SearchFieldDataType.Int32)
        ]
        
        fields = [
            # Primary key
            SimpleField(name="productId", type=SearchFieldDataType.String, key=True),
            
            # Basic product information
            SearchableField(name="name", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="shortDescription", type=SearchFieldDataType.String),
            
            # Categorization
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="subcategory", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="brand", type=SearchFieldDataType.String, filterable=True, facetable=True),
            
            # Product attributes
            SimpleField(name="sku", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="model", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="color", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="size", type=SearchFieldDataType.String, filterable=True, facetable=True),
            
            # Collections for multiple values
            SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                       filterable=True, facetable=True),
            SimpleField(name="features", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            SimpleField(name="imageUrls", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            
            # Inventory and availability
            SimpleField(name="inStock", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="stockQuantity", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="availabilityDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            
            # Dates
            SimpleField(name="createdDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="lastModified", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            
            # Geographic information
            SimpleField(name="originCountry", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            
            # Status flags
            SimpleField(name="isActive", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="isFeatured", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="isOnSale", type=SearchFieldDataType.Boolean, filterable=True),
            
            # Complex fields
            ComplexField(name="dimensions", fields=dimensions_fields),
            ComplexField(name="pricing", fields=pricing_fields),
            ComplexField(name="manufacturer", fields=manufacturer_fields),
            ComplexField(name="reviews", fields=reviews_fields)
        ]
        
        print(f"✅ E-commerce schema designed with {len(fields)} fields")
        self._display_schema_summary(fields)
        
        return fields
    
    def design_document_management_schema(self) -> List:
        """Design a schema for document management system"""
        print("📄 Designing Document Management Schema...")
        
        # Complex field for author information
        author_fields = [
            SimpleField(name="name", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="email", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="department", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="employeeId", type=SearchFieldDataType.String, filterable=True)
        ]
        
        # Complex field for document metadata
        metadata_fields = [
            SimpleField(name="fileSize", type=SearchFieldDataType.Int64, filterable=True, sortable=True),
            SimpleField(name="fileType", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="mimeType", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="pageCount", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="wordCount", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="checksum", type=SearchFieldDataType.String)
        ]
        
        # Complex field for security and permissions
        security_fields = [
            SimpleField(name="classificationLevel", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="isConfidential", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="accessLevel", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="ownerGroup", type=SearchFieldDataType.String, filterable=True, facetable=True)
        ]
        
        # Complex field for version control
        version_fields = [
            SimpleField(name="versionNumber", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SimpleField(name="isLatestVersion", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="previousVersionId", type=SearchFieldDataType.String),
            SimpleField(name="changeDescription", type=SearchFieldDataType.String)
        ]
        
        fields = [
            # Primary key
            SimpleField(name="documentId", type=SearchFieldDataType.String, key=True),
            
            # Basic document information
            SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SearchableField(name="summary", type=SearchFieldDataType.String),
            
            # Document classification
            SimpleField(name="documentType", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="category", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="subcategory", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            
            # File information
            SimpleField(name="fileName", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="filePath", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="fileUrl", type=SearchFieldDataType.String),
            
            # Dates
            SimpleField(name="createdDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="lastModified", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="lastAccessed", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="expirationDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            
            # Language and localization
            SimpleField(name="language", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="locale", type=SearchFieldDataType.String, filterable=True),
            
            # Collections
            SimpleField(name="keywords", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            SimpleField(name="relatedDocuments", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            
            # Status and workflow
            SimpleField(name="status", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="workflowStage", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="isArchived", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="isPublished", type=SearchFieldDataType.Boolean, filterable=True),
            
            # Complex fields
            ComplexField(name="author", fields=author_fields),
            ComplexField(name="metadata", fields=metadata_fields),
            ComplexField(name="security", fields=security_fields),
            ComplexField(name="version", fields=version_fields)
        ]
        
        print(f"✅ Document management schema designed with {len(fields)} fields")
        self._display_schema_summary(fields)
        
        return fields
    
    def design_optimized_blog_schema(self) -> List:
        """Design an optimized blog schema with performance considerations"""
        print("📝 Designing Optimized Blog Schema...")
        
        # Complex field for SEO information
        seo_fields = [
            SimpleField(name="metaTitle", type=SearchFieldDataType.String),
            SimpleField(name="metaDescription", type=SearchFieldDataType.String),
            SimpleField(name="keywords", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            SimpleField(name="canonicalUrl", type=SearchFieldDataType.String),
            SimpleField(name="ogTitle", type=SearchFieldDataType.String),
            SimpleField(name="ogDescription", type=SearchFieldDataType.String),
            SimpleField(name="ogImage", type=SearchFieldDataType.String)
        ]
        
        # Complex field for analytics
        analytics_fields = [
            SimpleField(name="viewCount", type=SearchFieldDataType.Int32, sortable=True),
            SimpleField(name="uniqueViews", type=SearchFieldDataType.Int32, sortable=True),
            SimpleField(name="shareCount", type=SearchFieldDataType.Int32, sortable=True),
            SimpleField(name="commentCount", type=SearchFieldDataType.Int32, sortable=True),
            SimpleField(name="likeCount", type=SearchFieldDataType.Int32, sortable=True),
            SimpleField(name="averageTimeOnPage", type=SearchFieldDataType.Double),
            SimpleField(name="bounceRate", type=SearchFieldDataType.Double)
        ]
        
        fields = [
            # Primary key
            SimpleField(name="postId", type=SearchFieldDataType.String, key=True),
            
            # Core content - optimized for search
            SearchableField(name="title", type=SearchFieldDataType.String, 
                          analyzer_name="en.microsoft"),
            SearchableField(name="content", type=SearchFieldDataType.String, 
                          analyzer_name="en.microsoft", 
                          retrievable=False),  # Don't return full content in results
            SearchableField(name="excerpt", type=SearchFieldDataType.String),
            
            # Author information - optimized for filtering
            SimpleField(name="authorName", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="authorId", type=SearchFieldDataType.String, filterable=True),
            
            # Categorization - optimized for faceting
            SimpleField(name="primaryCategory", type=SearchFieldDataType.String, 
                       filterable=True, facetable=True),
            SimpleField(name="secondaryCategories", 
                       type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            
            # Tags - limited facetable for performance
            SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                       filterable=True, facetable=True),
            
            # Dates - optimized for sorting and filtering
            SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            SimpleField(name="lastModified", type=SearchFieldDataType.DateTimeOffset, 
                       filterable=True, sortable=True),
            
            # Status fields - optimized for filtering
            SimpleField(name="status", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="isPublished", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="isFeatured", type=SearchFieldDataType.Boolean, filterable=True),
            
            # Media
            SimpleField(name="featuredImage", type=SearchFieldDataType.String),
            SimpleField(name="imageAltText", type=SearchFieldDataType.String),
            
            # Reading information
            SimpleField(name="readingTimeMinutes", type=SearchFieldDataType.Int32, 
                       filterable=True, sortable=True),
            SimpleField(name="wordCount", type=SearchFieldDataType.Int32, 
                       filterable=True, sortable=True),
            
            # Engagement metrics - sortable for popularity
            SimpleField(name="popularityScore", type=SearchFieldDataType.Double, 
                       sortable=True, filterable=True),
            
            # Complex fields
            ComplexField(name="seo", fields=seo_fields),
            ComplexField(name="analytics", fields=analytics_fields)
        ]
        
        print(f"✅ Optimized blog schema designed with {len(fields)} fields")
        self._display_schema_summary(fields)
        
        return fields
    
    def _display_schema_summary(self, fields: List) -> None:
        """Display a summary of the schema design"""
        field_types = {}
        attributes = {"searchable": 0, "filterable": 0, "sortable": 0, "facetable": 0, "key": 0}
        complex_fields = 0
        collection_fields = 0
        
        for field in fields:
            # Count field types
            field_type = str(field.type)
            field_types[field_type] = field_types.get(field_type, 0) + 1
            
            # Count attributes
            if hasattr(field, 'key') and field.key:
                attributes["key"] += 1
            if hasattr(field, 'searchable') and field.searchable:
                attributes["searchable"] += 1
            if hasattr(field, 'filterable') and field.filterable:
                attributes["filterable"] += 1
            if hasattr(field, 'sortable') and field.sortable:
                attributes["sortable"] += 1
            if hasattr(field, 'facetable') and field.facetable:
                attributes["facetable"] += 1
            
            # Count special field types
            if isinstance(field, ComplexField):
                complex_fields += 1
            if "Collection" in str(field.type):
                collection_fields += 1
        
        print("\n📊 Schema Summary:")
        print(f"   Total fields: {len(fields)}")
        print(f"   Complex fields: {complex_fields}")
        print(f"   Collection fields: {collection_fields}")
        print(f"   Searchable fields: {attributes['searchable']}")
        print(f"   Filterable fields: {attributes['filterable']}")
        print(f"   Sortable fields: {attributes['sortable']}")
        print(f"   Facetable fields: {attributes['facetable']}")
        
        print("\n📈 Field Type Distribution:")
        for field_type, count in sorted(field_types.items()):
            print(f"   {field_type}: {count}")
    
    def create_and_test_schema(self, index_name: str, fields: List, description: str) -> bool:
        """Create an index with the given schema and test it"""
        print(f"\n🏗️  Creating index '{index_name}' - {description}")
        
        try:
            # Create the index
            index = SearchIndex(name=index_name, fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            print(f"✅ Index '{result.name}' created successfully")
            
            # Test with a sample document
            return self._test_schema_with_sample_data(index_name, fields)
            
        except Exception as e:
            print(f"❌ Failed to create index: {str(e)}")
            return False
    
    def _test_schema_with_sample_data(self, index_name: str, fields: List) -> bool:
        """Test the schema with appropriate sample data"""
        print(f"🧪 Testing schema with sample data...")
        
        try:
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Create sample document based on schema
            sample_doc = self._generate_sample_document(fields)
            
            # Upload sample document
            result = search_client.upload_documents([sample_doc])
            
            if result[0].succeeded:
                print("✅ Sample document uploaded successfully")
                
                # Wait for indexing
                import time
                time.sleep(2)
                
                # Verify document count
                doc_count = search_client.get_document_count()
                print(f"✅ Index contains {doc_count} document(s)")
                
                return True
            else:
                print(f"❌ Sample document upload failed: {result[0].error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Schema test failed: {str(e)}")
            return False
    
    def _generate_sample_document(self, fields: List) -> Dict[str, Any]:
        """Generate a sample document that matches the schema"""
        doc = {}
        
        for field in fields:
            field_name = field.name
            field_type = str(field.type)
            
            # Generate sample data based on field type
            if hasattr(field, 'key') and field.key:
                doc[field_name] = "sample-doc-1"
            elif field_type == "Edm.String":
                doc[field_name] = f"Sample {field_name}"
            elif field_type == "Edm.Int32":
                doc[field_name] = 42
            elif field_type == "Edm.Int64":
                doc[field_name] = 1024
            elif field_type == "Edm.Double":
                doc[field_name] = 4.5
            elif field_type == "Edm.Boolean":
                doc[field_name] = True
            elif field_type == "Edm.DateTimeOffset":
                doc[field_name] = "2024-02-10T10:00:00Z"
            elif "Collection(Edm.String)" in field_type:
                doc[field_name] = ["sample", "test", "data"]
            elif isinstance(field, ComplexField):
                # Generate nested object
                nested_doc = {}
                for nested_field in field.fields:
                    nested_field_type = str(nested_field.type)
                    if nested_field_type == "Edm.String":
                        nested_doc[nested_field.name] = f"Sample {nested_field.name}"
                    elif nested_field_type == "Edm.Int32":
                        nested_doc[nested_field.name] = 10
                    elif nested_field_type == "Edm.Double":
                        nested_doc[nested_field.name] = 1.5
                    elif nested_field_type == "Edm.Boolean":
                        nested_doc[nested_field.name] = True
                    elif nested_field_type == "Edm.DateTimeOffset":
                        nested_doc[nested_field.name] = "2024-02-10T10:00:00Z"
                    elif "Collection(Edm.String)" in nested_field_type:
                        nested_doc[nested_field.name] = ["nested", "sample"]
                
                doc[field_name] = nested_doc
        
        return doc
    
    def compare_schemas(self, schemas: List[tuple]) -> None:
        """Compare different schema designs"""
        print("\n📊 Schema Comparison:")
        print("=" * 80)
        
        comparison_data = []
        
        for name, fields in schemas:
            stats = {
                "name": name,
                "total_fields": len(fields),
                "searchable": sum(1 for f in fields if hasattr(f, 'searchable') and f.searchable),
                "filterable": sum(1 for f in fields if hasattr(f, 'filterable') and f.filterable),
                "sortable": sum(1 for f in fields if hasattr(f, 'sortable') and f.sortable),
                "facetable": sum(1 for f in fields if hasattr(f, 'facetable') and f.facetable),
                "complex": sum(1 for f in fields if isinstance(f, ComplexField)),
                "collections": sum(1 for f in fields if "Collection" in str(f.type))
            }
            comparison_data.append(stats)
        
        # Display comparison table
        headers = ["Schema", "Total", "Search", "Filter", "Sort", "Facet", "Complex", "Collections"]
        print(f"{headers[0]:<20} | {headers[1]:<5} | {headers[2]:<6} | {headers[3]:<6} | {headers[4]:<4} | {headers[5]:<5} | {headers[6]:<7} | {headers[7]:<11}")
        print("-" * 80)
        
        for stats in comparison_data:
            print(f"{stats['name']:<20} | {stats['total_fields']:<5} | {stats['searchable']:<6} | {stats['filterable']:<6} | {stats['sortable']:<4} | {stats['facetable']:<5} | {stats['complex']:<7} | {stats['collections']:<11}")

def main():
    """Main function demonstrating advanced schema design"""
    print("=" * 60)
    print("Module 3: Advanced Schema Design Example")
    print("=" * 60)
    
    # Initialize the schema designer
    try:
        designer = AdvancedSchemaDesigner()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Create index client
    if not designer.create_index_client():
        print("❌ Failed to create index client. Exiting.")
        return
    
    # Design different schemas
    print("\n🎨 Designing Multiple Schema Patterns...")
    
    ecommerce_schema = designer.design_ecommerce_schema()
    document_schema = designer.design_document_management_schema()
    blog_schema = designer.design_optimized_blog_schema()
    
    # Compare schemas
    schemas = [
        ("E-commerce", ecommerce_schema),
        ("Document Mgmt", document_schema),
        ("Optimized Blog", blog_schema)
    ]
    
    designer.compare_schemas(schemas)
    
    # Create and test one schema (user choice)
    print("\n🏗️  Schema Creation Options:")
    print("1. E-commerce Product Schema")
    print("2. Document Management Schema")
    print("3. Optimized Blog Schema")
    
    choice = input("\nWhich schema would you like to create and test? (1-3, or 'skip'): ").strip()
    
    if choice == "1":
        success = designer.create_and_test_schema(
            "advanced-ecommerce-schema", 
            ecommerce_schema, 
            "E-commerce Product Schema"
        )
    elif choice == "2":
        success = designer.create_and_test_schema(
            "advanced-document-schema", 
            document_schema, 
            "Document Management Schema"
        )
    elif choice == "3":
        success = designer.create_and_test_schema(
            "advanced-blog-schema", 
            blog_schema, 
            "Optimized Blog Schema"
        )
    else:
        print("Skipping schema creation.")
        success = True
    
    if success:
        print("\n🎉 Advanced schema design completed successfully!")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\n📚 What you learned:")
    print("✅ How to design complex field structures")
    print("✅ How to use ComplexField for nested objects")
    print("✅ How to optimize field attributes for performance")
    print("✅ How to handle different data types effectively")
    print("✅ How to implement schema design patterns")
    print("✅ How to compare different schema approaches")
    
    print("\n🚀 Next steps:")
    print("1. Try creating your own schema for your use case")
    print("2. Experiment with different field attribute combinations")
    print("3. Run the next example: 03_data_ingestion.py")
    print("4. Test performance with different schema designs")

if __name__ == "__main__":
    main()