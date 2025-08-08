# Module 2: Prerequisites Setup Troubleshooting

## Overview

This guide helps you resolve issues specifically related to the prerequisites setup process for Module 2. If you're having trouble with the setup script or environment configuration, this is your go-to resource.

## Common Setup Issues and Solutions

### ❌ "Connection failed" errors
**Symptoms**: Setup script fails during connection test
**Solution**: Check your environment variables:
```bash
echo $AZURE_SEARCH_SERVICE_ENDPOINT
echo $AZURE_SEARCH_API_KEY
echo $AZURE_SEARCH_INDEX_NAME
```

**Troubleshooting Steps**:
1. Verify the endpoint format is correct: `https://your-service.search.windows.net`
2. Ensure the API key is an admin key (not query key) for setup
3. Test the connection manually:
   ```bash
   curl -H "api-key: YOUR_KEY" "https://your-service.search.windows.net/servicestats?api-version=2023-11-01"
   ```

### ❌ "'dict' object has no attribute 'counters'" (Fixed!)
**Status**: ✅ **RESOLVED** - The setup script now handles both old and new API response formats

**Background**: This error occurred due to changes in the Azure Search SDK response format. The current setup script includes compatibility handling for both response formats.

### ❌ "Document upload failed" (Fixed!)
**Status**: ✅ **RESOLVED** - Fixed JSON array parsing issue with tags field

**Background**: Earlier versions had issues with array field formatting. The current setup script properly formats all field types including arrays and complex objects.

### ❌ "Index already exists"
**Status**: ✅ **This is normal behavior!**
**Action**: The script will use the existing index and upload documents

**What happens**:
- Script detects existing index
- Validates index schema compatibility
- Uploads sample documents to existing index
- Continues with functionality testing

### ❌ "No module named 'azure.search.documents'"
**Cause**: Missing Python packages
**Solution**: 
```bash
pip install azure-search-documents python-dotenv
```

**For virtual environments**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install azure-search-documents python-dotenv
```

### ❌ "Environment variable not set" errors
**Cause**: Missing or incorrectly set environment variables
**Solutions**:

1. **Set variables in current session**:
   ```bash
   export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
   export AZURE_SEARCH_API_KEY="your-api-key"
   export AZURE_SEARCH_INDEX_NAME="handbook-samples"
   ```

2. **Create .env file** (recommended):
   ```env
   AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
   AZURE_SEARCH_API_KEY=your-api-key
   AZURE_SEARCH_INDEX_NAME=handbook-samples
   ```

3. **Add to shell profile** (permanent):
   ```bash
   echo 'export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"' >> ~/.bashrc
   source ~/.bashrc
   ```

### ❌ Permission errors
**Cause**: API key lacks required permissions
**Solutions**: 
1. **Use admin key for setup**: Query keys can't create indexes or upload documents
2. **Verify key permissions** in Azure portal
3. **Check service access policies**: Ensure your key has the right permissions

## Verification Steps

After running the setup, verify everything works:

### Quick Verification Test
```bash
# Run the verification test
python test_setup.py
```

**Expected output**:
```
✅ Index 'handbook-samples' contains 10 documents
✅ Simple search works - found 3 results for 'python'
✅ Sample result: 'Python Programming Fundamentals' (Score: 4.489)
🎉 Setup verification successful!
```

### Manual Verification
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os

# Test connection
try:
    search_client = SearchClient(
        endpoint=os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT'),
        index_name=os.getenv('AZURE_SEARCH_INDEX_NAME'),
        credential=AzureKeyCredential(os.getenv('AZURE_SEARCH_API_KEY'))
    )
    
    # Check document count
    count = search_client.get_document_count()
    print(f"✅ Index contains {count} documents")
    
    # Test basic search
    results = list(search_client.search("python", top=3))
    print(f"✅ Search works - found {len(results)} results")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
```

## Advanced Troubleshooting

### Debug Mode Setup
Run the setup script with debug information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run setup_prerequisites.py
```

### Step-by-Step Manual Setup
If the automated setup fails, you can set up manually:

1. **Create Index**:
   ```python
   from azure.search.documents.indexes import SearchIndexClient
   from azure.search.documents.indexes.models import SearchIndex, SearchField, SearchFieldDataType
   
   index_client = SearchIndexClient(endpoint, credential)
   
   # Define index schema
   fields = [
       SearchField(name="id", type=SearchFieldDataType.String, key=True),
       SearchField(name="title", type=SearchFieldDataType.String, searchable=True),
       SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
       # ... add other fields
   ]
   
   index = SearchIndex(name="handbook-samples", fields=fields)
   index_client.create_index(index)
   ```

2. **Upload Documents**:
   ```python
   documents = [
       {
           "id": "1",
           "title": "Python Programming Fundamentals",
           "content": "Learn Python programming basics...",
           # ... other fields
       }
       # ... more documents
   ]
   
   search_client.upload_documents(documents)
   ```

### Common Environment Issues

#### Windows-Specific Issues
- **PowerShell execution policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Path separators**: Use forward slashes or double backslashes in paths
- **Environment variables**: Use `$env:VARIABLE_NAME` in PowerShell

#### macOS/Linux-Specific Issues
- **Python version**: Ensure you're using Python 3.8+
- **Virtual environment**: Always use virtual environments for isolation
- **Permissions**: May need `sudo` for system-wide package installation

## Getting Additional Help

### Self-Help Checklist
- [ ] Environment variables are set correctly
- [ ] Using admin API key (not query key)
- [ ] Python packages are installed
- [ ] Azure service is running and accessible
- [ ] Network connectivity is working

### Escalation Path
If issues persist after trying these solutions:

1. **Document the exact error**: Copy the complete error message
2. **Note your environment**: OS, Python version, package versions
3. **List steps taken**: What solutions you've already tried
4. **Check service status**: Azure service health dashboard

### Diagnostic Information Collection
```python
import sys
import os
import azure.search.documents

print("=== Diagnostic Information ===")
print(f"Python version: {sys.version}")
print(f"Azure Search SDK version: {azure.search.documents.__version__}")
print(f"Operating System: {os.name}")
print(f"Environment variables set:")
print(f"  AZURE_SEARCH_SERVICE_ENDPOINT: {'✅' if os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT') else '❌'}")
print(f"  AZURE_SEARCH_API_KEY: {'✅' if os.getenv('AZURE_SEARCH_API_KEY') else '❌'}")
print(f"  AZURE_SEARCH_INDEX_NAME: {'✅' if os.getenv('AZURE_SEARCH_INDEX_NAME') else '❌'}")
```

## Success Metrics

Your setup is complete when:
- [ ] Prerequisites script runs without errors
- [ ] Index contains 10 documents
- [ ] All 5 search operations work (5/5 tests pass)
- [ ] Verification test passes
- [ ] You can run examples in your chosen language

---

**Setup working?** Great! Head back to the main [Prerequisites](prerequisites.md) guide or start with [Code Samples](code-samples.md) to begin learning! 🎉