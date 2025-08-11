# Module 3 Prerequisites: Index Management

## Overview

Before diving into index management operations, you need to ensure your development environment is properly configured and you have the necessary permissions to create and manage indexes in Azure AI Search.

## Required Setup

### 1. Azure AI Search Service Configuration

You need an Azure AI Search service with **admin-level access** for index management operations:

```bash
# Required environment variables
export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
export AZURE_SEARCH_ADMIN_KEY="your-admin-api-key"  # Admin key required for index operations
export AZURE_SEARCH_INDEX_NAME="handbook-indexes"   # Default index for examples
```

!!! warning "Admin Key Required"
    Index management operations require an **admin API key**, not a query key. Query keys only allow read operations and cannot create, modify, or delete indexes.

### 2. Python Environment Setup

Install the required packages:

```bash
# Core Azure AI Search SDK
pip install azure-search-documents

# Additional utilities
pip install python-dotenv requests pandas

# For Jupyter notebooks (optional)
pip install jupyter ipykernel
```

### 3. Development Tools (Optional)

For enhanced development experience:

```bash
# Azure CLI (for service management)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# REST client for testing (VS Code extension)
# Install "REST Client" extension in VS Code
```

## Prerequisites Validation

Run this validation script to ensure your environment is ready:

```python
"""
Prerequisites Validation for Module 3: Index Management
"""
import os
import sys
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

def validate_environment():
    """Validate environment variables and configuration"""
    print("🔍 Validating Environment Configuration...")
    
    required_vars = [
        "AZURE_SEARCH_SERVICE_ENDPOINT",
        "AZURE_SEARCH_ADMIN_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def validate_service_connection():
    """Validate connection to Azure AI Search service"""
    print("🔍 Validating Service Connection...")
    
    try:
        endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        
        # Create index client with admin key
        index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(admin_key)
        )
        
        # Test connection by listing indexes
        indexes = list(index_client.list_indexes())
        print(f"✅ Successfully connected to Azure AI Search service")
        print(f"   Service has {len(indexes)} existing indexes")
        
        return True, index_client
        
    except HttpResponseError as e:
        if e.status_code == 403:
            print("❌ Access denied - check your admin API key")
            print("   Make sure you're using an admin key, not a query key")
        else:
            print(f"❌ HTTP error {e.status_code}: {e.message}")
        return False, None
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False, None

def validate_permissions():
    """Validate admin permissions for index operations"""
    print("🔍 Validating Admin Permissions...")
    
    try:
        endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        
        index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(admin_key)
        )
        
        # Try to get service statistics (admin operation)
        stats = index_client.get_service_statistics()
        print("✅ Admin permissions confirmed")
        print(f"   Service storage: {stats.storage_size_in_bytes:,} bytes")
        print(f"   Document count: {stats.document_count:,}")
        
        return True
        
    except HttpResponseError as e:
        if e.status_code == 403:
            print("❌ Insufficient permissions - admin key required")
        else:
            print(f"❌ Permission check failed: {e.message}")
        return False
        
    except Exception as e:
        print(f"❌ Permission validation failed: {str(e)}")
        return False

def create_test_index():
    """Create a test index to verify index management capabilities"""
    print("🔍 Testing Index Management Capabilities...")
    
    try:
        from azure.search.documents.indexes.models import (
            SearchIndex,
            SimpleField,
            SearchableField,
            SearchFieldDataType
        )
        
        endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        
        index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(admin_key)
        )
        
        # Define test index
        test_index_name = "prerequisites-test-index"
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True)
        ]
        
        test_index = SearchIndex(name=test_index_name, fields=fields)
        
        # Create test index
        result = index_client.create_or_update_index(test_index)
        print(f"✅ Test index '{result.name}' created successfully")
        
        # Clean up - delete test index
        index_client.delete_index(test_index_name)
        print("✅ Test index cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Index management test failed: {str(e)}")
        return False

def main():
    """Run all prerequisite validations"""
    print("=" * 60)
    print("Module 3: Index Management - Prerequisites Validation")
    print("=" * 60)
    
    # Run all validations
    validations = [
        ("Environment Configuration", validate_environment),
        ("Service Connection", validate_service_connection),
        ("Admin Permissions", validate_permissions),
        ("Index Management", create_test_index)
    ]
    
    results = []
    for name, validation_func in validations:
        print(f"\n{name}:")
        print("-" * 40)
        
        if name == "Service Connection":
            success, client = validation_func()
            results.append(success)
        else:
            success = validation_func()
            results.append(success)
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nYou're ready to start Module 3: Index Management")
        print("\nNext steps:")
        print("1. 📚 Read the module documentation")
        print("2. 🔬 Try the code samples")
        print("3. 📝 Complete the exercises")
        print("4. 🚀 Build your own indexes!")
        
    else:
        print(f"⚠️  {passed}/{total} validations passed")
        print("\nPlease fix the failed validations before proceeding:")
        
        validation_names = [name for name, _ in validations]
        for i, (name, success) in enumerate(zip(validation_names, results)):
            status = "✅" if success else "❌"
            print(f"   {status} {name}")
        
        print("\nRefer to the setup documentation for help resolving issues.")

if __name__ == "__main__":
    main()
```

## Common Setup Issues

### Issue 1: "Access Denied" Error

**Problem**: Getting 403 Forbidden errors when trying to create indexes.

**Solution**: 
- Verify you're using an **admin API key**, not a query key
- Check that your API key hasn't expired
- Ensure your Azure AI Search service is running

```bash
# Test your admin key with Azure CLI
az search admin-key show --service-name your-service-name --resource-group your-resource-group
```

### Issue 2: "Service Not Found" Error

**Problem**: Cannot connect to the Azure AI Search service.

**Solution**:
- Verify your service endpoint URL is correct
- Check that your Azure AI Search service is running
- Ensure there are no network restrictions blocking access

```python
# Test endpoint connectivity
import requests
endpoint = "https://your-service.search.windows.net"
response = requests.get(f"{endpoint}?api-version=2023-11-01")
print(f"Status: {response.status_code}")
```

### Issue 3: Package Installation Issues

**Problem**: Cannot install azure-search-documents package.

**Solution**:
```bash
# Update pip first
pip install --upgrade pip

# Install with specific version if needed
pip install azure-search-documents==11.4.0

# Use virtual environment to avoid conflicts
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install azure-search-documents
```

### Issue 4: Environment Variables Not Loading

**Problem**: Environment variables are not being read correctly.

**Solution**:
```python
# Create .env file in your project root
# .env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_ADMIN_KEY=your-admin-api-key

# Load in Python
from dotenv import load_dotenv
load_dotenv()

import os
endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
```

## Performance Considerations

### 1. Service Tier Requirements

Different operations have different performance characteristics:

| Operation | Basic Tier | Standard Tier | Recommendation |
|-----------|------------|---------------|----------------|
| **Index Creation** | Slower | Faster | Use Standard for development |
| **Bulk Upload** | Limited | Better | Standard+ for large datasets |
| **Concurrent Operations** | 1-2 | 3+ | Standard+ for production |

### 2. Resource Planning

```python
# Estimate index size for planning
def estimate_index_size(num_documents, avg_document_size_kb):
    """Estimate index storage requirements"""
    # Azure AI Search typically uses 1.5-2x the source data size
    base_size_mb = (num_documents * avg_document_size_kb) / 1024
    estimated_size_mb = base_size_mb * 1.75  # Include search structures
    
    print(f"Estimated index size: {estimated_size_mb:.1f} MB")
    return estimated_size_mb
```

## Next Steps

Once you've completed the prerequisites validation:

1. **✅ Environment Ready**: All validations passed
2. **📚 Study the Documentation**: Read the full Module 3 documentation
3. **🔬 Try Code Samples**: Start with basic index creation examples
4. **📝 Complete Exercises**: Practice with hands-on scenarios
5. **🚀 Build Real Indexes**: Apply concepts to your own data

## Getting Help

If you encounter issues during setup:

1. **Check Error Messages**: Look for specific error codes and messages
2. **Review Prerequisites**: Ensure all requirements are met
3. **Test Incrementally**: Validate each component separately
4. **Use Logging**: Enable detailed logging for troubleshooting

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

**Ready to start managing indexes?** 🏗️✨

Run the prerequisites validation script and begin your journey into Azure AI Search index management!