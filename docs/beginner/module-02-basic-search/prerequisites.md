# Module 2: Prerequisites & Setup

## Overview

Before diving into basic search operations, you need to set up your Azure AI Search environment and prepare sample data. This page guides you through all the requirements and setup steps.

## 📋 Requirements Checklist

### ✅ **Azure Resources**
- [ ] **Azure AI Search Service** - Created and running
- [ ] **API Key** - Admin or query key with appropriate permissions
- [ ] **Service Endpoint** - URL to your search service

### ✅ **Development Environment**
- [ ] **Python 3.8+** - For running the setup script
- [ ] **Programming Language SDK** - For your chosen language (Python, C#, JavaScript)
- [ ] **Environment Variables** - Configured with your service details

### ✅ **Required Packages**
```bash
# Core packages (required for setup)
pip install azure-search-documents python-dotenv

# Optional: For interactive notebooks
pip install jupyter

# Language-specific packages covered in respective sections
```

## 🔧 Environment Configuration

### Option 1: Environment Variables (Recommended)
```bash
# Set these environment variables
export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
export AZURE_SEARCH_API_KEY="your-api-key"
export AZURE_SEARCH_INDEX_NAME="handbook-samples"
```

### Option 2: .env File
Create a `.env` file in the code-samples directory:
```env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=handbook-samples
```

### Option 3: Direct Configuration
Update the configuration directly in the code examples (not recommended for production).

## 🚀 Prerequisites Setup Script

### ⚠️ **CRITICAL FIRST STEP**

**You MUST run the prerequisites setup script before attempting any examples!**

```bash
# Navigate to the code samples directory
cd docs/beginner/module-02-basic-search/code-samples/

# Run the prerequisites setup
python setup_prerequisites.py
```

### What the Setup Script Does

The `setup_prerequisites.py` script creates a complete learning environment:

#### 🔌 **Connection Testing**

- Validates your Azure AI Search service connection
- Tests API key permissions
- Verifies service availability

#### 🏗️ **Index Creation**
Creates the `handbook-samples` index with **13 comprehensive fields**:

| Field | Type | Purpose | Capabilities |
|-------|------|---------|--------------|
| `id` | String | Primary key | Key field |
| `title` | String | Document title | Searchable, filterable, sortable |
| `content` | String | Main content | Searchable with English analyzer |
| `description` | String | Brief description | Searchable |
| `author` | String | Content author | Filterable, sortable, facetable |
| `category` | String | Content category | Filterable, facetable |
| `tags` | String | Comma-separated tags | Searchable, filterable, facetable |
| `publishedDate` | DateTimeOffset | Publication date | Filterable, sortable, facetable |
| `rating` | Double | Content rating | Filterable, sortable, facetable |
| `viewCount` | Int32 | View count | Filterable, sortable |
| `url` | String | Content URL | Retrievable |
| `language` | String | Content language | Filterable, facetable |
| `difficulty` | String | Difficulty level | Filterable, facetable |

#### 📄 **Sample Data Upload**
Uploads **10 comprehensive documents** covering:

- **Programming** (2 docs): Python fundamentals and advanced techniques
- **Data Science** (2 docs): Machine learning and data analysis
- **Web Development** (1 doc): JavaScript and modern web frameworks
- **Artificial Intelligence** (1 doc): AI overview and applications
- **Database** (1 doc): SQL and database design
- **Cloud Computing** (1 doc): Azure cloud services
- **Mobile Development** (1 doc): iOS and Android development
- **Security** (1 doc): Cybersecurity fundamentals

#### 🧪 **Functionality Testing**
Tests all **5 basic search operation types**:

- ✅ Simple text search
- ✅ Phrase search with quotes
- ✅ Boolean search (AND, OR, NOT)
- ✅ Wildcard search with patterns
- ✅ Field-specific search

### Expected Output

When the setup completes successfully, you'll see:

```
🎊 SETUP COMPLETE! 🎊
Your Azure AI Search environment is fully ready!

📚 You can now run the basic search examples:
   • basic_search.ipynb (interactive notebook)
   • Python, C#, JavaScript, or REST API examples

🚀 Happy searching!
```

## ✅ Verification

### Quick Verification Test
Run the verification script to confirm everything works:

```bash
# Run the verification test
python test_setup.py
```

Expected output:
```
✅ Index 'handbook-samples' contains 10 documents
✅ Simple search works - found 3 results for 'python'
✅ Sample result: 'Python Programming Fundamentals' (Score: 4.489)
🎉 Setup verification successful!
```

### Manual Verification
You can also verify manually:

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Initialize client
search_client = SearchClient(
    endpoint="your-endpoint",
    index_name="handbook-samples",
    credential=AzureKeyCredential("your-api-key")
)

# Test search
results = list(search_client.search("python", top=3))
print(f"Found {len(results)} results")
```

## 🛠️ Troubleshooting Setup Issues

### Common Issues and Solutions

#### ❌ **"Connection failed" errors**
**Cause**: Incorrect endpoint or API key
**Solution**: 
1. Verify your service endpoint URL
2. Check your API key in the Azure portal
3. Ensure the service is running

#### ❌ **"Index already exists" message**
**Status**: ✅ **This is normal!**
**Action**: The script will use the existing index and upload documents

#### ❌ **"No module named 'azure.search.documents'"**
**Cause**: Missing Python packages
**Solution**: 
```bash
pip install azure-search-documents python-dotenv
```

#### ❌ **"Environment variable not set" errors**
**Cause**: Missing environment variables
**Solution**: Set the required environment variables or create a `.env` file

#### ❌ **Permission errors**
**Cause**: API key lacks required permissions
**Solution**: 

1. Use an admin key for setup
2. Ensure the key has index creation permissions
3. Check service access policies

### Getting Help

If you encounter issues not covered here:

1. **Check the [Troubleshooting Guide](troubleshooting.md)** for comprehensive solutions
2. **Review the error message** carefully - it often contains the solution
3. **Verify your Azure portal settings** for the search service
4. **Try the verification test** to isolate the issue

## 🎯 Next Steps

Once your prerequisites are set up successfully:

1. **📚 [Start with Code Samples](code-samples.md)** - Choose your learning path
2. **🔍 [Try the Interactive Notebook](code-samples/notebooks/basic_search.ipynb)** - Immediate hands-on learning
3. **💻 [Pick Your Language](code-samples.md#choose-your-language)** - Python, C#, JavaScript, or REST API
4. **💡 [Review Best Practices](best-practices.md)** - Learn professional techniques

## 📊 Setup Success Metrics

Your setup is complete when:

- [ ] Prerequisites script runs without errors
- [ ] Index contains 10 documents
- [ ] All 5 search operations work (5/5 tests pass)
- [ ] Verification test passes
- [ ] You can run examples in your chosen language

---

**Setup complete?** Great! Head to [Code Samples](code-samples.md) to start learning! 🎉