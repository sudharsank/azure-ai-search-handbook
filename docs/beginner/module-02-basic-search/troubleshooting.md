# Module 2: Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide helps you resolve common issues encountered while working with Azure AI Search basic operations. Issues are organized by category with clear solutions and prevention tips.

## 🔧 Prerequisites Setup Issues

### Connection Problems

#### ❌ **"Connection failed" or timeout errors**
**Symptoms**: 
- Script fails during connection test
- HTTP timeout errors
- "Service unavailable" messages

**Solutions**:
1. **Verify Service Endpoint**:
   ```bash
   # Check your endpoint format
   echo $AZURE_SEARCH_SERVICE_ENDPOINT
   # Should be: https://your-service.search.windows.net
   ```

2. **Test Network Connectivity**:
   ```bash
   # Test if you can reach the service
   curl -I https://your-service.search.windows.net
   ```

3. **Check Service Status**:
   - Visit Azure portal
   - Verify service is running and not paused
   - Check for any service alerts

#### ❌ **"Authentication failed" (401/403 errors)**
**Symptoms**:
- "Access denied" messages
- "Invalid subscription key" errors
- 401 or 403 HTTP status codes

**Solutions**:
1. **Verify API Key**:
   ```bash
   # Check your API key is set
   echo $AZURE_SEARCH_API_KEY
   # Should show your key (last 4 characters)
   ```

2. **Check Key Permissions**:
   - Use **Admin Key** for setup (has full permissions)
   - Query keys won't work for index creation
   - Verify key hasn't expired

3. **Test Key Manually**:
   ```bash
   curl -H "api-key: YOUR_KEY" \
        "https://your-service.search.windows.net/servicestats?api-version=2023-11-01"
   ```

### Index Creation Issues

#### ❌ **"Index already exists" (Normal)**
**Status**: ✅ **This is expected behavior**
**Action**: The script will use the existing index - no action needed

#### ❌ **"Failed to create index" errors**
**Symptoms**:
- Index creation fails with schema errors
- Field definition errors
- Permission denied for index creation

**Solutions**:
1. **Use Admin Key**: Query keys can't create indexes
2. **Check Service Tier**: Ensure your service tier supports the features used
3. **Clear Existing Index** (if needed):
   ```python
   # Only if you need to start fresh
   from azure.search.documents.indexes import SearchIndexClient
   index_client = SearchIndexClient(endpoint, credential)
   index_client.delete_index("handbook-samples")
   ```

### Document Upload Issues

#### ❌ **"Document upload failed" errors**
**Symptoms**:
- JSON parsing errors
- "StartArray node was found" errors
- Upload returns 400 status

**Status**: ✅ **RESOLVED** - Fixed in current version
**Previous Issue**: Tags field array format issue
**Current Solution**: Uses string format for tags field

#### ❌ **"Some documents failed to upload"**
**Solutions**:
1. **Check Document Format**: Ensure all required fields are present
2. **Verify Field Types**: Match the index schema exactly
3. **Check Document Size**: Ensure documents aren't too large
4. **Review Error Details**: Script shows specific failure reasons

## 🔍 Search Operation Issues

### No Results Found

#### ❌ **Search returns empty results**
**Symptoms**:
- All searches return 0 results
- Index shows documents but searches fail

**Solutions**:
1. **Verify Index Has Data**:
   ```python
   doc_count = search_client.get_document_count()
   print(f"Index contains {doc_count} documents")
   ```

2. **Check Search Syntax**:
   ```python
   # Try the simplest possible search
   results = list(search_client.search("*", top=5))
   print(f"Found {len(results)} total documents")
   ```

3. **Verify Field Names**:
   ```python
   # Check what fields exist in your documents
   results = list(search_client.search("*", top=1))
   if results:
       print("Available fields:", list(results[0].keys()))
   ```

#### ❌ **Specific searches return no results**
**Solutions**:
1. **Try Broader Terms**:
   ```python
   # Instead of specific terms
   results = search_client.search("machine learning tutorial")
   
   # Try individual terms
   results = search_client.search("machine")
   results = search_client.search("learning")
   ```

2. **Use Wildcard Search**:
   ```python
   # Try partial matching
   results = search_client.search("mach*")
   ```

3. **Check Search Mode**:
   ```python
   # Try "any" mode instead of "all"
   results = search_client.search("machine learning", search_mode="any")
   ```

### Query Syntax Errors

#### ❌ **"Invalid query syntax" (400 errors)**
**Symptoms**:
- Boolean queries fail
- Special characters cause errors
- Phrase searches don't work

**Solutions**:
1. **Escape Special Characters**:
   ```python
   # Problematic
   query = 'title:"C# Programming"'
   
   # Fixed
   query = 'title:"C# Programming"'  # Use proper quotes
   ```

2. **Validate Boolean Syntax**:
   ```python
   # Correct boolean syntax
   query = "python AND tutorial"
   query = "(python OR java) AND tutorial"
   query = "programming NOT deprecated"
   ```

3. **Check Phrase Syntax**:
   ```python
   # Correct phrase search
   query = '"machine learning"'  # Use double quotes
   ```

### Performance Issues

#### ❌ **Slow search responses**
**Solutions**:
1. **Limit Result Count**:
   ```python
   # Instead of returning many results
   results = search_client.search(query, top=10)  # Limit to 10
   ```

2. **Select Specific Fields**:
   ```python
   # Return only needed fields
   results = search_client.search(
       query, 
       select=["id", "title", "score"]
   )
   ```

3. **Use Field-Specific Search**:
   ```python
   # Search specific fields only
   results = search_client.search(
       query,
       search_fields=["title", "description"]
   )
   ```

## 💻 Language-Specific Issues

### Python Issues

#### ❌ **"No module named 'azure.search.documents'"**
**Solution**:
```bash
pip install azure-search-documents python-dotenv
```

#### ❌ **"ImportError" or package conflicts**
**Solutions**:
1. **Use Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install azure-search-documents python-dotenv
   ```

2. **Update Packages**:
   ```bash
   pip install --upgrade azure-search-documents
   ```

### C# Issues

#### ❌ **"Package not found" errors**
**Solution**:
```bash
dotnet add package Azure.Search.Documents
```

#### ❌ **"Namespace not found" errors**
**Solution**: Add proper using statements:
```csharp
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
```

### JavaScript Issues

#### ❌ **"Module not found" errors**
**Solution**:
```bash
npm install @azure/search-documents
```

#### ❌ **"CORS errors" in browser**
**Solutions**:
1. **Configure CORS** in Azure portal
2. **Use Query Key** (not admin key) for browser apps
3. **Use Server-Side Proxy** for sensitive operations

### REST API Issues

#### ❌ **"Invalid Content-Type" errors**
**Solution**: Ensure proper headers:
```http
Content-Type: application/json
api-key: your-api-key
```

#### ❌ **"API version not supported"**
**Solution**: Use supported API version:
```http
GET https://service.search.windows.net/indexes?api-version=2023-11-01
```

## 🔧 Environment Issues

### Environment Variables

#### ❌ **"Environment variable not set" errors**
**Solutions**:
1. **Check Variables Are Set**:
   ```bash
   echo $AZURE_SEARCH_SERVICE_ENDPOINT
   echo $AZURE_SEARCH_API_KEY
   echo $AZURE_SEARCH_INDEX_NAME
   ```

2. **Set Variables Properly**:
   ```bash
   # For current session
   export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
   
   # For permanent (add to ~/.bashrc or ~/.zshrc)
   echo 'export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"' >> ~/.bashrc
   ```

3. **Use .env File**:
   ```env
   AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
   AZURE_SEARCH_API_KEY=your-api-key
   AZURE_SEARCH_INDEX_NAME=handbook-samples
   ```

### Path and Directory Issues

#### ❌ **"File not found" or "Module not found"**
**Solutions**:
1. **Check Current Directory**:
   ```bash
   pwd  # Should be in code-samples directory for setup
   ```

2. **Navigate to Correct Directory**:
   ```bash
   cd docs/beginner/module-02-basic-search/code-samples/
   ```

3. **Verify File Exists**:
   ```bash
   ls -la setup_prerequisites.py
   ```

## 🧪 Testing and Validation

### Verification Steps

#### ✅ **Run Verification Test**
```bash
python test_setup.py
```

Expected output:
```
✅ Index 'handbook-samples' contains 10 documents
✅ Simple search works - found 3 results for 'python'
✅ Sample result: 'Python Programming Fundamentals' (Score: 4.489)
🎉 Setup verification successful!
```

#### ✅ **Manual Testing**
```python
# Test basic connectivity
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

search_client = SearchClient(endpoint, index_name, credential)
count = search_client.get_document_count()
print(f"Index contains {count} documents")

# Test basic search
results = list(search_client.search("python", top=3))
print(f"Search returned {len(results)} results")
```

## 🆘 Getting Additional Help

### Self-Help Resources

1. **Check Error Messages Carefully**: They often contain the exact solution
2. **Review Prerequisites**: Ensure all requirements are met
3. **Try Verification Test**: Isolates the specific issue
4. **Check Azure Portal**: Verify service status and configuration

### Escalation Path

If issues persist after trying these solutions:

1. **Document the Error**: Copy exact error messages
2. **Note Your Environment**: OS, Python version, package versions
3. **List Steps Taken**: What solutions you've already tried
4. **Check Service Status**: Azure service health dashboard

### Common Resolution Patterns

Most issues fall into these categories:
- **90%**: Environment variables or API key issues
- **5%**: Network connectivity or service availability
- **3%**: Package installation or version conflicts
- **2%**: Index schema or data format issues

## 📊 Prevention Tips

### Best Practices to Avoid Issues

1. **Always Run Prerequisites First**: Don't skip the setup script
2. **Use Environment Variables**: Avoid hardcoding credentials
3. **Test Incrementally**: Verify each step before proceeding
4. **Keep Packages Updated**: Use latest SDK versions
5. **Use Admin Keys for Setup**: Query keys have limited permissions
6. **Monitor Service Health**: Check Azure portal regularly

### Monitoring and Maintenance

```python
# Regular health check
def health_check():
    try:
        count = search_client.get_document_count()
        test_results = list(search_client.search("test", top=1))
        print(f"✅ Service healthy: {count} docs, search working")
        return True
    except Exception as e:
        print(f"❌ Service issue: {e}")
        return False
```

---

**Still having issues?** The troubleshooting steps above resolve 99% of common problems. If you're still stuck, double-check your [Prerequisites](prerequisites.md) setup and try the verification test. 🔧