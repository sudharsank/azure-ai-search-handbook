# Python Code Samples - Module 2: Basic Search Operations

This directory contains focused Python examples for basic search operations in Azure AI Search. Each file demonstrates a specific aspect of search functionality with clear, beginner-friendly code.

## 📁 Files Overview

### Core Search Operations (Files 01-05)
1. **`01_simple_text_search.py`** - Basic text search and result handling
2. **`02_phrase_search.py`** - Exact phrase matching with quotes
3. **`03_boolean_search.py`** - Boolean operators (AND, OR, NOT)
4. **`04_wildcard_search.py`** - Pattern matching with wildcards
5. **`05_field_search.py`** - Field-specific and multi-field searches

### Advanced Features (Files 06-08)
6. **`06_result_processing.py`** - Processing and formatting search results
7. **`07_error_handling.py`** - Comprehensive error handling and validation
8. **`08_search_patterns.py`** - Advanced search patterns and strategies

## 🎯 Complete Coverage Matrix

| Topic | Python | C# | JavaScript | REST | Description |
|-------|--------|----|-----------|----- |-------------|
| Simple Text Search | ✅ | ✅ | ✅ | ✅ | Basic keyword searching |
| Phrase Search | ✅ | ✅ | ✅ | ✅ | Exact phrase matching |
| Boolean Search | ✅ | ✅ | ✅ | ✅ | AND, OR, NOT operators |
| Wildcard Search | ✅ | ✅ | ✅ | ✅ | Pattern matching with * |
| Field Search | ✅ | ✅ | ✅ | ✅ | Field-specific searches |
| Result Processing | ✅ | ✅ | ✅ | ✅ | Formatting and analysis |
| Error Handling | ✅ | ✅ | ✅ | ✅ | Robust error management |
| Search Patterns | ✅ | ✅ | ✅ | ✅ | Advanced strategies |

## 🚀 Getting Started

### ⚠️ CRITICAL FIRST STEP: Prerequisites Setup

**Before running ANY Python examples, you MUST run the prerequisites setup:**

```bash
# Navigate to the parent directory
cd ../

# Run the prerequisites setup script
python setup_prerequisites.py
```

**What this does:**
- 🔌 Tests your Azure AI Search connection
- 🏗️ Creates the `handbook-samples` index with comprehensive schema
- 📄 Uploads 10 sample documents with rich content
- 🧪 Tests all search operations to ensure everything works
- 📋 Provides a summary of what's ready

**Time Required**: 5-10 minutes

### Prerequisites
```bash
# Install required packages
pip install azure-search-documents python-dotenv

# Set environment variables
export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
export AZURE_SEARCH_API_KEY="your-api-key"
export AZURE_SEARCH_INDEX_NAME="handbook-samples"
```

### Quick Start
```bash
# 1. FIRST: Run prerequisites setup (from parent directory)
cd ../
python setup_prerequisites.py

# 2. THEN: Run Python examples
cd python/
python 01_simple_text_search.py
python 02_phrase_search.py
python 03_boolean_search.py
# ... and so on
```

## 📚 Learning Path

### Beginner Path (Recommended Order)
1. **Start Here**: `01_simple_text_search.py` - Learn basic search concepts
2. **Precision**: `02_phrase_search.py` - Understand exact matching
3. **Logic**: `03_boolean_search.py` - Combine terms with operators
4. **Flexibility**: `04_wildcard_search.py` - Pattern matching techniques
5. **Targeting**: `05_field_search.py` - Search specific fields
6. **Processing**: `06_result_processing.py` - Handle and format results
7. **Safety**: `07_error_handling.py` - Robust error handling
8. **Strategies**: `08_search_patterns.py` - Advanced search patterns

### Quick Reference
- **Need basic search?** → `01_simple_text_search.py`
- **Want exact phrases?** → `02_phrase_search.py`
- **Combining terms?** → `03_boolean_search.py`
- **Partial matching?** → `04_wildcard_search.py`
- **Specific fields?** → `05_field_search.py`
- **Format results?** → `06_result_processing.py`
- **Handle errors?** → `07_error_handling.py`
- **Advanced patterns?** → `08_search_patterns.py`

## 💡 Key Concepts Covered

### Search Types
- **Simple Text Search**: Basic keyword searching
- **Phrase Search**: Exact phrase matching with quotes
- **Boolean Search**: AND, OR, NOT operators
- **Wildcard Search**: Pattern matching with *
- **Field Search**: Targeting specific document fields

### Result Handling
- **Score Analysis**: Understanding relevance scores
- **Result Formatting**: Display and export options
- **Filtering**: Score-based and custom filtering
- **Sorting**: By score, field, or custom criteria

### Error Handling
- **Input Validation**: Query sanitization and validation
- **HTTP Errors**: Handling Azure Search API errors
- **Fallback Strategies**: Alternative queries when searches fail
- **User-Friendly Messages**: Converting technical errors

### Search Patterns
- **Progressive Search**: From specific to broad strategies
- **Fallback Search**: Automatic strategy switching
- **Multi-Field Search**: Prioritized field searching
- **Pattern Selection**: Choosing the right approach

## 🔧 Code Structure

Each file follows a consistent structure:
```python
"""
Module docstring explaining the concepts
"""

# Imports and setup
import os, sys, logging
from azure.search.documents import SearchClient

# Main class demonstrating the concept
class ConceptDemo:
    def __init__(self, search_client=None):
        # Initialize with search client
    
    def main_method(self, params):
        # Core functionality demonstration
    
    def helper_methods(self):
        # Supporting functionality

# Demonstration function
def demonstrate_concept():
    # Show the concept in action

# Best practices function  
def concept_best_practices():
    # Guidelines and tips

# Main execution
if __name__ == "__main__":
    demonstrate_concept()
    concept_best_practices()
```

## 🎯 Usage Examples

### Basic Search
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Initialize client
search_client = SearchClient(
    endpoint="https://your-service.search.windows.net",
    index_name="your-index",
    credential=AzureKeyCredential("your-api-key")
)

# Simple search
results = search_client.search(search_text="python programming")
for result in results:
    print(f"Title: {result.get('title')}")
    print(f"Score: {result['@search.score']}")
```

### Using the Example Classes
```python
# Import from any example file
from simple_text_search import SimpleTextSearch

# Initialize and use
search_ops = SimpleTextSearch()
results = search_ops.basic_search("machine learning", top=5)
search_ops.display_results(results)
```

## 🛡️ Error Handling

All examples include basic error handling:
```python
try:
    results = search_client.search(search_text=query)
    # Process results
except HttpResponseError as e:
    print(f"Search error: {e.status_code}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## 📊 Performance Tips

1. **Limit Results**: Use `top` parameter to limit result count
2. **Select Fields**: Use `select` to return only needed fields
3. **Field Targeting**: Use `search_fields` for specific field searches
4. **Caching**: Cache frequently used search results
5. **Error Handling**: Implement proper error handling and retries

## 🔗 Cross-Language Learning

These Python examples complement the other language implementations:

- **[C# Examples](../csharp/README.md)** - .NET implementations with async/await patterns
- **[JavaScript Examples](../javascript/README.md)** - Node.js and browser examples
- **[REST API Examples](../rest/README.md)** - Direct HTTP API calls for any language
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter examples for experimentation

**🎯 Learning Approach:**

- **Sequential**: Follow 01-08 in order for structured learning
- **Cross-Language**: Compare implementations across platforms
- **Topic-Focused**: Jump to specific search types as needed
- **Interactive**: Use notebooks for hands-on experimentation

## 🚀 Next Steps

After working through these examples:

1. ✅ Try modifying the queries and parameters
2. 🔧 Implement your own search functionality
3. 📚 Explore other language examples
4. 🎯 Check out the interactive notebooks
5. 📖 Move on to Module 3: Index Management

---

**Happy Coding!** 🐍✨