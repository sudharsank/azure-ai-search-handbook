# Module 4: Simple Queries and Filters - Prerequisites

Before starting with simple queries and filters, you need to ensure your environment is properly configured and you have the necessary foundation from previous modules.

## 📋 Required Prerequisites

### 1. Previous Module Completion

You must have successfully completed:

- ✅ **Module 1: Introduction and Setup** - Azure AI Search service configured
- ✅ **Module 2: Basic Search Operations** - Understanding of search fundamentals  
- ✅ **Module 3: Index Management** - Sample indexes created and populated

### 2. Azure AI Search Service

Ensure you have:

- ✅ **Active Azure AI Search service** with appropriate pricing tier
- ✅ **API keys** with query permissions (query key or admin key)
- ✅ **Service endpoint** URL accessible
- ✅ **Sample indexes** with data from previous modules

### 3. Development Environment

#### Python Environment
```bash
# Required Python packages
pip install azure-search-documents python-dotenv jupyter

# Optional but recommended
pip install pandas matplotlib  # For data analysis examples
```

#### Environment Variables
Create a `.env` file in your project root:

```env
# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-query-or-admin-key
AZURE_SEARCH_INDEX_NAME=your-sample-index-name

# Optional: For advanced examples
AZURE_SEARCH_ADMIN_KEY=your-admin-key
```

### 4. Sample Data Requirements

Your search index should contain documents with these fields for optimal learning:

#### Required Fields
- `id` (Edm.String) - Unique document identifier
- `title` (Edm.String) - Document title (searchable)
- `content` (Edm.String) - Document content (searchable)

#### Recommended Fields
- `category` (Edm.String) - Document category (filterable, facetable)
- `tags` (Collection(Edm.String)) - Document tags (filterable, facetable)
- `rating` (Edm.Double) - Document rating 0.0-5.0 (filterable, sortable)
- `publishedDate` (Edm.DateTimeOffset) - Publication date (filterable, sortable)
- `price` (Edm.Double) - Document price (filterable, sortable)

#### Optional Fields
- `location` (Edm.GeographyPoint) - Geographic location (for geo-distance examples)
- `author` (Edm.String) - Document author (filterable)
- `views` (Edm.Int32) - View count (filterable, sortable)

## 🔧 Environment Verification

### Quick Verification Script

Run this script to verify your environment is ready:

```python
#!/usr/bin/env python3
"""
Module 4 Prerequisites Verification
"""

import os
import sys
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv

def verify_environment():
    """Verify that the environment is ready for Module 4."""
    print("Module 4: Simple Queries and Filters - Prerequisites Check")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    required_vars = [
        "AZURE_SEARCH_SERVICE_ENDPOINT",
        "AZURE_SEARCH_API_KEY", 
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Environment variables configured")
    
    # Test search client connection
    try:
        search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
        )
        
        # Test basic search
        results = list(search_client.search(search_text="*", top=1))
        print("✅ Search client connection successful")
        
        if not results:
            print("⚠️  Index exists but contains no data")
            print("   Run index creation from Module 3 to populate sample data")
            return False
        
        print(f"✅ Index contains data ({len(results)} sample documents found)")
        
        # Check for recommended fields
        sample_doc = results[0]
        recommended_fields = ['title', 'content', 'category', 'rating', 'publishedDate']
        missing_fields = []
        
        for field in recommended_fields:
            if field not in sample_doc:
                missing_fields.append(field)
        
        if missing_fields:
            print("⚠️  Some recommended fields are missing:")
            for field in missing_fields:
                print(f"   - {field}")
            print("   Some examples may not work as expected")
        else:
            print("✅ All recommended fields present")
        
        return True
        
    except HttpResponseError as e:
        print(f"❌ Search client error: {e.message}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_environment():
        print("\n🎉 Environment is ready for Module 4!")
        print("\nNext steps:")
        print("• Start with the interactive notebook: notebooks/simple_queries.ipynb")
        print("• Or run Python examples: python/01_basic_queries.py")
    else:
        print("\n🔧 Please fix the issues above before proceeding")
        sys.exit(1)
```

Save this as `verify_prerequisites.py` and run it:

```bash
python verify_prerequisites.py
```

## 🚀 Getting Started

Once your prerequisites are verified:

### Option 1: Interactive Learning (Recommended)
```bash
# Start Jupyter notebook for hands-on learning
jupyter notebook code-samples/notebooks/simple_queries.ipynb
```

### Option 2: Python Scripts
```bash
# Run individual Python examples
cd code-samples/python/
python 01_basic_queries.py
python 02_filtering.py
# ... continue with other examples
```

### Option 3: Quick Overview
```bash
# Run the comprehensive example
python code-samples/query_examples.py
```

## 📚 Learning Path

Follow this recommended sequence:

1. **Basic Queries** (`01_basic_queries.py`)
   - Simple text search
   - Query operators
   - Field-specific search

2. **Filtering** (`02_filtering.py`)
   - OData filter syntax
   - Comparison operators
   - Logical combinations

3. **Sorting & Pagination** (`03_sorting_pagination.py`)
   - Result ordering
   - Pagination patterns
   - Performance optimization

4. **Result Customization** (`04_result_customization.py`)
   - Field selection
   - Search highlighting
   - Custom formatting

5. **Advanced Queries** (`05_advanced_queries.py`)
   - Field boosting
   - Fuzzy search
   - Complex patterns

6. **Error Handling** (`06_error_handling.py`)
   - Exception handling
   - Query validation
   - Debugging techniques

## 🔍 Sample Data Creation

If you need to create sample data for testing, here's a quick script:

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from datetime import datetime, timedelta
import random

def create_sample_documents():
    """Create sample documents for testing queries and filters."""
    
    categories = ["Technology", "Science", "Business", "Education", "Health"]
    tags_pool = ["python", "javascript", "tutorial", "guide", "beginner", "advanced", "api", "web", "mobile", "cloud"]
    
    documents = []
    
    for i in range(20):
        doc = {
            "id": f"doc_{i+1:03d}",
            "title": f"Sample Document {i+1}: {random.choice(['Azure', 'Python', 'Machine Learning', 'Web Development', 'Data Science'])} Tutorial",
            "content": f"This is sample content for document {i+1}. It contains information about various topics including technology, programming, and tutorials. The content is designed to test search functionality.",
            "category": random.choice(categories),
            "tags": random.sample(tags_pool, random.randint(2, 5)),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "publishedDate": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat() + "Z",
            "price": round(random.uniform(0, 100), 2),
            "author": f"Author {random.randint(1, 10)}",
            "views": random.randint(100, 10000)
        }
        documents.append(doc)
    
    return documents

# Use this function if you need to populate your index with sample data
```

## ❓ Troubleshooting

### Common Issues

1. **"Index not found" error**
   - Verify your index name in the environment variables
   - Ensure the index was created in previous modules

2. **"Authentication failed" error**
   - Check your API key is correct
   - Ensure the key has query permissions

3. **"No results found" warnings**
   - Your index may be empty
   - Run the sample data creation script above

4. **Import errors**
   - Install required packages: `pip install azure-search-documents python-dotenv`

5. **Environment variable issues**
   - Ensure your `.env` file is in the correct location
   - Check for typos in variable names

### Getting Help

If you encounter issues:

1. Review the error messages carefully
2. Check the troubleshooting section in each code example
3. Verify your Azure AI Search service is running
4. Ensure your API keys haven't expired
5. Try the verification script above to diagnose issues

## 🎯 Success Criteria

You're ready to proceed when:

- ✅ Environment verification script passes
- ✅ You can run basic search queries
- ✅ Your index contains sample data
- ✅ All required packages are installed
- ✅ Environment variables are configured correctly

## 🔗 Next Steps

Once prerequisites are met:

1. Start with the interactive notebook for hands-on learning
2. Work through the Python examples in order
3. Experiment with your own queries and filters
4. Apply the concepts to your specific use case

Good luck with Module 4! 🚀