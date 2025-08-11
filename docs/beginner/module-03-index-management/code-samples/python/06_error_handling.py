#!/usr/bin/env python3
"""
Module 3: Index Management - Error Handling and Troubleshooting
==============================================================

This example demonstrates comprehensive error handling patterns and troubleshooting
techniques for Azure AI Search index management operations.

Learning Objectives:
- Handle common error scenarios gracefully
- Implement retry strategies with exponential backoff
- Validate inputs and handle edge cases
- Provide meaningful error messages and recovery options
- Debug and troubleshoot index management issues

Prerequisites:
- Completed previous examples (01-05)
- Understanding of index operations and performance
- Azure AI Search service with admin access

Author: Azure AI Search Handbook
Module: Beginner - Module 3: Index Management
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from functools import wraps

try:
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex, SimpleField, SearchableField, SearchFieldDataType
    )
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0, 
                      exceptions: tuple = (HttpResponseError,)):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Don't retry on client errors (4xx)
                    if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                        raise e
                    
                    if attempt < max_retries - 1:
                        delay = backoff_factor ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator

class ErrorHandlingManager:
    """Demonstrates comprehensive error handling patterns"""
    
    def __init__(self):
        """Initialize the error handling manager"""
        self.endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.index_client = None
        
        # Validate configuration
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate environment configuration"""
        errors = []
        
        if not self.endpoint:
            errors.append("AZURE_SEARCH_SERVICE_ENDPOINT not set")
        elif not self.endpoint.startswith("https://"):
            errors.append("AZURE_SEARCH_SERVICE_ENDPOINT must start with https://")
        
        if not self.admin_key:
            errors.append("AZURE_SEARCH_ADMIN_KEY not set")
        elif len(self.admin_key) < 32:
            errors.append("AZURE_SEARCH_ADMIN_KEY appears to be invalid (too short)")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
    
    @retry_with_backoff(max_retries=3)
    def create_clients_with_retry(self) -> bool:
        """Create clients with retry logic"""
        logger.info("Creating Search Clients with retry logic...")
        
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Test connection
            stats = self.index_client.get_service_statistics()
            logger.info("✅ Successfully connected to Azure AI Search service")
            return True
            
        except HttpResponseError as e:
            self._handle_http_error(e, "client creation")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during client creation: {str(e)}")
            raise
    
    def _handle_http_error(self, error: HttpResponseError, operation: str) -> None:
        """Handle HTTP errors with specific guidance"""
        status_code = error.status_code
        
        if status_code == 401:
            logger.error(f"❌ Authentication failed during {operation}")
            logger.error("   Check your API key and ensure it's valid")
        elif status_code == 403:
            logger.error(f"❌ Access denied during {operation}")
            logger.error("   Ensure you're using an admin key (not query key)")
            logger.error("   Verify your service has the required permissions")
        elif status_code == 404:
            logger.error(f"❌ Resource not found during {operation}")
            logger.error("   Check your service endpoint and resource names")
        elif status_code == 429:
            logger.error(f"❌ Rate limit exceeded during {operation}")
            logger.error("   Reduce request frequency or upgrade service tier")
        elif status_code == 503:
            logger.error(f"❌ Service unavailable during {operation}")
            logger.error("   This is usually temporary - retry with backoff")
        else:
            logger.error(f"❌ HTTP {status_code} error during {operation}: {error.message}")
    
    def safe_index_creation(self, index_name: str, fields: List) -> Optional[SearchIndex]:
        """Demonstrate safe index creation with comprehensive error handling"""
        logger.info(f"Creating index '{index_name}' with error handling...")
        
        try:
            # Validate index name
            self._validate_index_name(index_name)
            
            # Validate fields
            self._validate_index_fields(fields)
            
            # Create index
            index = SearchIndex(name=index_name, fields=fields)
            result = self.index_client.create_or_update_index(index)
            
            logger.info(f"✅ Index '{result.name}' created successfully")
            return result
            
        except ValueError as e:
            logger.error(f"❌ Validation error: {str(e)}")
            return None
        except HttpResponseError as e:
            self._handle_http_error(e, "index creation")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during index creation: {str(e)}")
            return None
    
    def _validate_index_name(self, index_name: str) -> None:
        """Validate index name according to Azure AI Search rules"""
        if not index_name:
            raise ValueError("Index name cannot be empty")
        
        if len(index_name) > 128:
            raise ValueError("Index name cannot exceed 128 characters")
        
        if not index_name.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Index name can only contain letters, numbers, hyphens, and underscores")
        
        if index_name.startswith('-') or index_name.endswith('-'):
            raise ValueError("Index name cannot start or end with a hyphen")
        
        if index_name.lower() in ['indexes', 'index']:
            raise ValueError("Index name cannot be a reserved word")
    
    def _validate_index_fields(self, fields: List) -> None:
        """Validate index field definitions"""
        if not fields:
            raise ValueError("Index must have at least one field")
        
        key_fields = [f for f in fields if hasattr(f, 'key') and f.key]
        if len(key_fields) != 1:
            raise ValueError(f"Index must have exactly one key field, found {len(key_fields)}")
        
        field_names = [f.name for f in fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Field names must be unique")
        
        for field in fields:
            if not field.name:
                raise ValueError("Field name cannot be empty")
            
            if len(field.name) > 128:
                raise ValueError(f"Field name '{field.name}' exceeds 128 characters")
    
    def safe_document_upload(self, index_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Demonstrate safe document upload with error handling"""
        logger.info(f"Uploading {len(documents)} documents to '{index_name}' with error handling...")
        
        upload_stats = {
            'total_documents': len(documents),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'retry_attempts': 0
        }
        
        try:
            # Validate documents
            self._validate_documents(documents)
            
            # Create search client
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # Upload with retry logic
            result = self._upload_with_retry(search_client, documents, upload_stats)
            
            # Process results
            for r in result:
                if r.succeeded:
                    upload_stats['successful'] += 1
                else:
                    upload_stats['failed'] += 1
                    upload_stats['errors'].append({
                        'document_id': r.key,
                        'error': r.error_message
                    })
            
            logger.info(f"✅ Upload completed: {upload_stats['successful']}/{upload_stats['total_documents']} successful")
            
            if upload_stats['failed'] > 0:
                logger.warning(f"⚠️  {upload_stats['failed']} documents failed to upload")
                for error in upload_stats['errors'][:5]:  # Show first 5 errors
                    logger.warning(f"   - {error['document_id']}: {error['error']}")
            
            return upload_stats
            
        except Exception as e:
            logger.error(f"❌ Document upload failed: {str(e)}")
            upload_stats['errors'].append({'general_error': str(e)})
            return upload_stats
    
    def _validate_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Validate document structure"""
        if not documents:
            raise ValueError("Document list cannot be empty")
        
        if len(documents) > 1000:
            raise ValueError("Cannot upload more than 1000 documents in a single batch")
        
        # Check for required ID field
        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                raise ValueError(f"Document {i} must be a dictionary")
            
            if 'id' not in doc:
                raise ValueError(f"Document {i} missing required 'id' field")
            
            if not doc['id']:
                raise ValueError(f"Document {i} has empty 'id' field")
    
    @retry_with_backoff(max_retries=3, exceptions=(HttpResponseError,))
    def _upload_with_retry(self, search_client: SearchClient, documents: List[Dict[str, Any]], 
                          stats: Dict[str, Any]):
        """Upload documents with retry logic"""
        stats['retry_attempts'] += 1
        return search_client.upload_documents(documents)
    
    def demonstrate_error_scenarios(self) -> None:
        """Demonstrate various error scenarios and their handling"""
        logger.info("🧪 Demonstrating Error Scenarios...")
        
        # Scenario 1: Invalid index name
        print("\n   Scenario 1: Invalid Index Name")
        invalid_names = ["", "index-name-that-is-way-too-long-" * 10, "-invalid-start", "invalid end-"]
        
        for name in invalid_names:
            try:
                self._validate_index_name(name)
                print(f"   ❌ Validation should have failed for: '{name}'")
            except ValueError as e:
                print(f"   ✅ Correctly caught error for '{name}': {str(e)}")
        
        # Scenario 2: Invalid field configuration
        print("\n   Scenario 2: Invalid Field Configuration")
        try:
            # No key field
            invalid_fields = [
                SimpleField(name="title", type=SearchFieldDataType.String)
            ]
            self._validate_index_fields(invalid_fields)
            print("   ❌ Validation should have failed for missing key field")
        except ValueError as e:
            print(f"   ✅ Correctly caught error: {str(e)}")
        
        # Scenario 3: Invalid documents
        print("\n   Scenario 3: Invalid Document Structure")
        try:
            invalid_docs = [{"title": "Missing ID"}]
            self._validate_documents(invalid_docs)
            print("   ❌ Validation should have failed for missing ID")
        except ValueError as e:
            print(f"   ✅ Correctly caught error: {str(e)}")
        
        # Scenario 4: Network timeout simulation
        print("\n   Scenario 4: Network Error Handling")
        self._simulate_network_errors()
    
    def _simulate_network_errors(self) -> None:
        """Simulate network error scenarios"""
        print("   Simulating network timeout scenarios...")
        
        # This would normally involve actual network calls
        # For demo purposes, we'll show the error handling structure
        
        try:
            # Simulate a timeout
            raise HttpResponseError("Simulated timeout", response=None)
        except HttpResponseError as e:
            print(f"   ✅ Network error handled: {str(e)}")
            print("   ✅ Would retry with exponential backoff")
    
    def troubleshooting_guide(self) -> None:
        """Provide a comprehensive troubleshooting guide"""
        print("\n🔧 Troubleshooting Guide:")
        print("=" * 50)
        
        troubleshooting_steps = [
            {
                'issue': 'Connection Failures',
                'symptoms': ['401/403 errors', 'Authentication failed'],
                'solutions': [
                    'Verify AZURE_SEARCH_SERVICE_ENDPOINT is correct',
                    'Ensure AZURE_SEARCH_ADMIN_KEY is an admin key (not query key)',
                    'Check that the service is running and accessible',
                    'Verify network connectivity and firewall settings'
                ]
            },
            {
                'issue': 'Index Creation Failures',
                'symptoms': ['400 Bad Request', 'Invalid field definition'],
                'solutions': [
                    'Validate index name follows naming conventions',
                    'Ensure exactly one key field is defined',
                    'Check field names are unique and valid',
                    'Verify field types are supported'
                ]
            },
            {
                'issue': 'Document Upload Failures',
                'symptoms': ['Partial upload success', 'Document validation errors'],
                'solutions': [
                    'Ensure all documents have required ID field',
                    'Validate document structure matches index schema',
                    'Check batch size (max 1000 documents)',
                    'Verify field data types match schema'
                ]
            },
            {
                'issue': 'Performance Issues',
                'symptoms': ['Slow uploads', 'Timeouts', 'Rate limiting'],
                'solutions': [
                    'Optimize batch sizes (100-500 documents)',
                    'Implement parallel processing',
                    'Add retry logic with exponential backoff',
                    'Consider upgrading service tier'
                ]
            }
        ]
        
        for step in troubleshooting_steps:
            print(f"\n📋 {step['issue']}:")
            print(f"   Symptoms: {', '.join(step['symptoms'])}")
            print(f"   Solutions:")
            for solution in step['solutions']:
                print(f"     • {solution}")
    
    def create_error_handling_test_index(self) -> Optional[str]:
        """Create a test index for error handling demonstrations"""
        index_name = "error-handling-test"
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, filterable=True, sortable=True)
        ]
        
        return self.safe_index_creation(index_name, fields)

def main():
    """Main function demonstrating error handling and troubleshooting"""
    print("=" * 60)
    print("Module 3: Error Handling and Troubleshooting Example")
    print("=" * 60)
    
    # Initialize the error handling manager
    try:
        manager = ErrorHandlingManager()
        logger.info("✅ Configuration validated successfully")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return
    
    # Create clients with retry logic
    try:
        if not manager.create_clients_with_retry():
            logger.error("❌ Failed to create clients. Exiting.")
            return
    except Exception as e:
        logger.error(f"❌ Client creation failed: {str(e)}")
        return
    
    # Create test index with error handling
    print(f"\n{'='*20} Safe Index Creation {'='*20}")
    test_index = manager.create_error_handling_test_index()
    
    if test_index:
        # Test document upload with error handling
        print(f"\n{'='*20} Safe Document Upload {'='*20}")
        
        # Mix of valid and invalid documents
        test_documents = [
            {
                "id": "valid-1",
                "title": "Valid Document 1",
                "category": "Test",
                "rating": 4.5
            },
            {
                "id": "valid-2",
                "title": "Valid Document 2",
                "category": "Test",
                "rating": 4.0
            },
            {
                # This document has an invalid rating type
                "id": "invalid-1",
                "title": "Invalid Document",
                "category": "Test",
                "rating": "not-a-number"  # This will cause an error
            }
        ]
        
        upload_stats = manager.safe_document_upload(test_index.name, test_documents)
        
        print(f"\n📊 Upload Statistics:")
        print(f"   Total: {upload_stats['total_documents']}")
        print(f"   Successful: {upload_stats['successful']}")
        print(f"   Failed: {upload_stats['failed']}")
        print(f"   Retry Attempts: {upload_stats['retry_attempts']}")
    
    # Demonstrate error scenarios
    print(f"\n{'='*20} Error Scenario Demonstrations {'='*20}")
    manager.demonstrate_error_scenarios()
    
    # Show troubleshooting guide
    print(f"\n{'='*20} Troubleshooting Guide {'='*20}")
    manager.troubleshooting_guide()
    
    # Cleanup
    if test_index:
        cleanup = input(f"\nDelete the test index '{test_index.name}'? (y/N): ").lower().strip()
        if cleanup in ['y', 'yes']:
            try:
                manager.index_client.delete_index(test_index.name)
                logger.info(f"✅ Index '{test_index.name}' deleted successfully")
            except Exception as e:
                logger.error(f"❌ Failed to delete index: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\n📚 What you learned:")
    print("✅ How to handle common error scenarios gracefully")
    print("✅ How to implement retry strategies with exponential backoff")
    print("✅ How to validate inputs and handle edge cases")
    print("✅ How to provide meaningful error messages and recovery options")
    print("✅ How to debug and troubleshoot index management issues")
    
    print("\n🚀 Next steps:")
    print("1. Implement error handling in your production code")
    print("2. Set up monitoring and alerting for errors")
    print("3. Create automated error recovery procedures")
    print("4. Document common issues and solutions for your team")

if __name__ == "__main__":
    main()