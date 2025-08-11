# Module 2: Basic Search Operations - Code Samples

This directory contains comprehensive code samples demonstrating basic search operations in Azure AI Search across multiple programming languages. These samples are designed to help you understand fundamental search concepts and implement them in your preferred language.

!!! info "📚 Theory and Concepts"
    These code samples complement the [**Module 2 Documentation**](../documentation.md). If you haven't read the theory yet, we recommend starting there to understand the concepts before diving into the code.

    **Learning Path:**
    1. 📖 Read the [Module 2 Documentation](../documentation.md) for concepts
    2. 🔬 Practice with these code samples in your preferred language
    3. 🎯 Apply what you've learned in your own projects

## 🧭 Navigation

- **[← Back to Module 2 Overview](../documentation.md)** - Theory and concepts
- **[→ Module 3: Index Management](../../module-03-index-management/documentation.md)** - Next module

## 🗂️ Language-Specific Code Samples

### 📁 Directory Structure

```
code-samples/
├── python/          # Python examples (8 focused files)
├── csharp/          # C# .NET examples  
├── javascript/      # JavaScript/Node.js examples
├── rest/            # REST API examples
├── notebooks/       # Interactive Jupyter notebooks
└── README.md        # This file
```

### 🐍 **[Python Examples](python/README.md)** (8 files)
**Best for:** Data scientists, Python developers, rapid prototyping

- `01_simple_text_search.py` - Basic text search operations
- `02_phrase_search.py` - Exact phrase matching
- `03_boolean_search.py` - Boolean operators (AND, OR, NOT)
- `04_wildcard_search.py` - Pattern matching with wildcards
- `05_field_search.py` - Field-specific searches
- `06_result_processing.py` - Processing and formatting results
- `07_error_handling.py` - Error handling and validation
- `08_search_patterns.py` - Advanced search patterns

### 🔷 **[C# Examples](csharp/README.md)** (8 files)
**Best for:** .NET developers, enterprise applications, Windows environments

- `01_SimpleTextSearch.cs` - Basic search operations in C#
- `02_PhraseSearch.cs` - Exact phrase matching
- `03_BooleanSearch.cs` - Boolean search operations
- `04_WildcardSearch.cs` - Wildcard pattern matching
- `05_FieldSearch.cs` - Field-specific search operations
- `06_ResultProcessing.cs` - Processing and formatting results
- `07_ErrorHandling.cs` - Error handling and validation
- `08_SearchPatterns.cs` - Advanced search patterns

### 🟨 **[JavaScript Examples](javascript/README.md)** (8 files)
**Best for:** Web developers, Node.js applications, frontend integration

- `01_simple_text_search.js` - Basic search with JavaScript SDK
- `02_phrase_search.js` - Phrase search operations
- `03_boolean_search.js` - Boolean search logic
- `04_wildcard_search.js` - Wildcard searches
- `05_field_search.js` - Field-specific operations
- `06_result_processing.js` - Processing and formatting results
- `07_error_handling.js` - Error handling and validation
- `08_search_patterns.js` - Advanced search patterns

### 🌐 **[REST API Examples](rest/README.md)** (8 files)
**Best for:** Any language, direct HTTP integration, testing, debugging

- `01_simple_text_search.http` - Basic REST API calls
- `02_phrase_search.http` - Phrase search via REST
- `03_boolean_search.http` - Boolean operations
- `04_wildcard_search.http` - Wildcard patterns
- `05_field_search.http` - Field-specific searches
- `06_result_processing.http` - Processing and formatting results
- `07_error_handling.http` - Error handling and validation
- `08_search_patterns.http` - Advanced search patterns

### 📓 **[Interactive Notebooks](notebooks/README.md)** (1 file)
**Best for:** Learning, experimentation, documentation

- `basic_search.ipynb` - Interactive learning notebook with step-by-step examples

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

**📊 Total Coverage:** 32 code samples (8 per language × 4 languages)

## 📁 Files Overview

### Prerequisites Setup (REQUIRED FIRST)
- **`setup_prerequisites.py`** - **RUN THIS FIRST!** Sets up index and sample data

### Core Search Operations (Files 01-05)
Each language includes these fundamental search operations:

- **`01_simple_text_search.*`** - Basic text search operations
- **`02_phrase_search.*`** - Exact phrase matching with quotes
- **`03_boolean_search.*`** - Boolean operators (AND, OR, NOT)
- **`04_wildcard_search.*`** - Pattern matching with wildcards
- **`05_field_search.*`** - Field-specific and multi-field searches

### Advanced Features (Files 06-08)
Each language includes these advanced capabilities:

- **`06_result_processing.*`** - Processing, formatting, and exporting results
- **`07_error_handling.*`** - Comprehensive error handling and validation
- **`08_search_patterns.*`** - Advanced search patterns and strategies

### Interactive Learning
- **`notebooks/basic_search.ipynb`** - Interactive Jupyter notebook with step-by-step examples

## 🏗️ What the Prerequisites Setup Creates

The `setup_prerequisites.py` script creates a comprehensive learning environment:

### Sample Index Schema (`handbook-samples`)
- **13 fields** designed for all search operation types:

    - `id` (key), `title`, `content`, `description` (searchable text)
    - `author`, `category`, `tags` (filterable metadata)
    - `publishedDate`, `rating`, `viewCount` (sortable data)
    - `url`, `language`, `difficulty` (additional metadata)

### Sample Documents (10 documents)
Rich, realistic content covering:

- **Programming**: Python fundamentals, advanced techniques
- **Data Science**: Machine learning, data analysis tutorials
- **Web Development**: JavaScript, mobile app development
- **Technology**: AI overview, cloud computing, cybersecurity
- **Database**: SQL and database design

### Search Capabilities Enabled
- ✅ **Simple text search** across all content
- ✅ **Phrase search** with exact matching
- ✅ **Boolean search** (AND, OR, NOT operators)
- ✅ **Wildcard search** with pattern matching
- ✅ **Field-specific search** targeting individual fields
- ✅ **Result highlighting** with custom tags
- ✅ **Filtering and sorting** by various criteria
- ✅ **Faceted search** for categorization

## 🚀 Getting Started

### ⚠️ CRITICAL FIRST STEP: Prerequisites Setup

**Before running ANY examples, you MUST run the prerequisites setup:**

```bash
# Navigate to this directory
cd docs/beginner/module-02-basic-search/code-samples/

# Run the prerequisites setup script
python setup_prerequisites.py
```

**What this script does:**

- 🔌 Tests your Azure AI Search connection
- 🏗️ Creates a comprehensive sample index (`handbook-samples`)
- 📄 Uploads 10 sample documents with rich content for all search examples
- 🧪 Tests all search operations to ensure everything works
- 📋 Provides a summary of what's ready

**Time Required**: 5-10 minutes

### Prerequisites
1. **Azure AI Search service** configured and running
2. **API credentials** (endpoint URL and API key)
3. **Environment variables** set (see below)
4. **Python packages**: `azure-search-documents`, `python-dotenv`

### Environment Configuration
Set up your connection details:

```bash
# Environment variables (recommended)
export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
export AZURE_SEARCH_API_KEY="your-api-key"
export AZURE_SEARCH_INDEX_NAME="handbook-samples"
```

Or create a `.env` file:
```env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=handbook-samples
```

### Quick Start by Language

**⚠️ Remember: Run `python setup_prerequisites.py` first!**

=== "Python"
    ```bash
    # 1. FIRST: Run prerequisites setup
    python setup_prerequisites.py
    
    # 2. Install dependencies
    pip install azure-search-documents python-dotenv
    
    # 3. Run focused examples
    cd python/
    python 01_simple_text_search.py
    python 06_result_processing.py
    ```

=== "C#"
    ```bash
    # 1. FIRST: Run prerequisites setup
    python setup_prerequisites.py
    
    # 2. Add package and run
    dotnet add package Azure.Search.Documents
    dotnet run 01_SimpleTextSearch.cs
    ```

=== "JavaScript"
    ```bash
    # 1. FIRST: Run prerequisites setup
    python setup_prerequisites.py
    
    # 2. Install and run
    npm install @azure/search-documents
    node javascript/01_simple_text_search.js
    ```

=== "REST API"
    ```bash
    # 1. FIRST: Run prerequisites setup
    python setup_prerequisites.py
    
    # 2. Use with VS Code REST Client extension
    # Open rest/01_simple_text_search.http and click "Send Request"
    ```

=== "Jupyter Notebook"
    ```bash
    # 1. FIRST: Run prerequisites setup
    python setup_prerequisites.py
    
    # 2. Interactive learning
    pip install jupyter azure-search-documents
    jupyter notebook notebooks/basic_search.ipynb
    ```

## 📚 What You'll Learn

### Core Search Operations (Files 01-05)

#### 1. Simple Text Search (`01_simple_text_search.*`)
- **Basic keyword searching** across all document fields
- **Result handling** and score interpretation
- **Search client initialization** and configuration
- **Understanding search responses** and metadata

#### 2. Phrase Search (`02_phrase_search.*`)
- **Exact phrase matching** using quotes
- **Phrase vs individual terms** comparison
- **When to use phrase search** for precision

#### 3. Boolean Search (`03_boolean_search.*`)
- **AND, OR, NOT operators** for complex queries
- **Combining multiple terms** with logic
- **Query precedence** and grouping

#### 4. Wildcard Search (`04_wildcard_search.*`)
- **Pattern matching** with asterisks (*)
- **Prefix and suffix matching** techniques
- **Performance considerations** for wildcards

#### 5. Field Search (`05_field_search.*`)
- **Field-specific searches** targeting document fields
- **Multi-field searches** with different priorities
- **Field selection** for returned results

### Advanced Features (Files 06-08)

#### 6. Result Processing (`06_result_processing.*`)
- **Result formatting** for different output formats
- **Data export** capabilities (JSON, CSV, etc.)
- **Statistical analysis** of search scores
- **Result filtering** and sorting techniques
- **Performance metrics** and quality assessment

#### 7. Error Handling (`07_error_handling.*`)
- **Input validation** and query sanitization
- **HTTP error handling** with user-friendly messages
- **Retry logic** for transient failures
- **Fallback strategies** when searches fail
- **Safe search wrappers** for production use

#### 8. Search Patterns (`08_search_patterns.*`)
- **Progressive search** from specific to broad
- **Fallback search** with automatic strategy switching
- **Multi-field priority** search strategies
- **Pattern selection** guidelines and best practices

### Interactive Learning (`notebooks/basic_search.ipynb`)
The Jupyter notebook provides:

- **Step-by-step explanations** with executable code
- **Interactive experimentation** with different queries
- **Visual result formatting** and analysis
- **Hands-on exercises** and challenges
- **Performance analysis** and optimization tips

## 🎯 Usage Examples

### Basic Search Example (Python)
```python
# Import from the focused examples
from python.simple_text_search import SimpleTextSearch
from python.result_processing import ResultProcessor
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Initialize search client
search_client = SearchClient(
    endpoint="https://your-service.search.windows.net",
    index_name="your-index",
    credential=AzureKeyCredential("your-api-key")
)

# Perform different types of searches
search_ops = SimpleTextSearch(search_client)
results = search_ops.basic_search("python tutorial", top=5)

# Process and display results
processor = ResultProcessor()
processed_results = processor.process_raw_results(results.results)
formatted_output = processor.format_for_display(processed_results)
print(formatted_output)
```

### Error Handling Example (Python)
```python
from python.error_handling import SafeSearchClient

# Create safe search client with error handling
safe_client = SafeSearchClient(search_client)

# Perform safe search with comprehensive error handling
results, error = safe_client.safe_search("user input query")

if error:
    print(f"Search failed: {error}")
else:
    print(f"Found {len(results)} results")
    for result in results[:3]:
        title = result.document.get('title', 'No title')
        score = result.score or 0.0
        print(f"- {title} (Score: {score:.3f})")
```

### Advanced Pattern Example (Python)
```python
from python.search_patterns import SearchPatterns

# Initialize pattern engine
patterns = SearchPatterns(search_client)

# Progressive search from specific to broad
progressive_results = patterns.progressive_search("machine learning", top=10)

# Search with automatic fallback
fallback_results = patterns.search_with_fallback("artificial intelligence tutorial", top=5)

# Multi-field priority search
field_priority = ["title", "description", "content", "tags"]
multi_results = patterns.multi_field_search("python", field_priority, top=5)
```

### Cross-Language Examples

=== "C#"
    ```csharp
    using AzureSearchHandbook.Module02.BasicSearch;
    
    // Initialize search operations
    var searchOps = new SimpleTextSearch(searchClient);
    var results = await searchOps.BasicSearchAsync("python tutorial", 5);
    
    // Process results
    var processor = new ResultProcessor();
    var processedResults = processor.ProcessRawResults(results);
    var formattedOutput = processor.FormatForDisplay(processedResults);
    Console.WriteLine(formattedOutput);
    ```

=== "JavaScript"
    ```javascript
    const { SimpleTextSearch } = require('./javascript/01_simple_text_search');
    const { ResultProcessor } = require('./javascript/06_result_processing');
    
    // Initialize and perform search
    const searchOps = new SimpleTextSearch(searchClient);
    const results = await searchOps.basicSearch('python tutorial', 5);
    
    // Process results
    const processor = new ResultProcessor();
    const processedResults = processor.processRawResults(results.results);
    const formattedOutput = processor.formatForDisplay(processedResults);
    console.log(formattedOutput);
    ```

=== "REST API"
    ```http
    ### Basic Search
    POST {{endpoint}}/indexes/{{index-name}}/docs/search?api-version={{api-version}}
    Content-Type: application/json
    api-key: {{api-key}}
    
    {
        "search": "python tutorial",
        "top": 5,
        "includeTotalCount": true
    }
    ```

## 🔧 Configuration

### Environment Variables
```bash
# Required
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-admin-or-query-key
AZURE_SEARCH_INDEX_NAME=your-index-name

# Optional
USE_MANAGED_IDENTITY=false
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### Logging Configuration
All samples include configurable logging:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
```

## 🚨 Common Issues and Solutions

### Connection Issues
- **Problem**: "Connection failed" errors
- **Solution**: Check endpoint URL and API key, verify network connectivity

### Authentication Issues
- **Problem**: 403 Forbidden errors
- **Solution**: Verify API key permissions and index access rights

### Query Syntax Issues
- **Problem**: 400 Bad Request errors
- **Solution**: Use query validation utilities, check for special characters

### No Results Found
- **Problem**: Searches return empty results
- **Solution**: Try broader terms, check index content, use fallback strategies

## 📈 Performance Tips

1. **Use Appropriate Search Types**:

    - Simple text search for general queries
    - Phrase search for exact matches
    - Boolean search for complex logic

2. **Optimize Result Size**:

    - Use `top` parameter to limit results
    - Implement pagination for large datasets

3. **Field Selection**:

    - Use `select` parameter to return only needed fields
    - Use `search_fields` to target specific fields

4. **Error Handling**:

    - Always validate user input
    - Implement retry logic for transient errors
    - Provide fallback search strategies

## 🔗 Related Resources

- [Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Query Syntax Reference](https://docs.microsoft.com/en-us/azure/search/query-lucene-syntax)
- [Python SDK Documentation](https://docs.microsoft.com/en-us/python/api/azure-search-documents/)
- [Module 1: Introduction and Setup](../../module-01-introduction-setup/documentation.md)
- [Module 3: Index Management](../../module-03-index-management/documentation.md)

## 🤝 Contributing

If you find issues or have suggestions for improvements:

1. Check existing code samples for similar functionality
2. Test your changes with different query types
3. Update documentation and comments
4. Ensure error handling is comprehensive

## 📝 Next Steps

After completing these code samples:

1. ✅ Complete the exercises in the `exercises/` folder
2. 📚 Move on to Module 3: Index Management
3. 🔧 Try implementing your own search functionality
4. 📖 Explore intermediate and advanced modules

---

**Happy Searching!** 🔍✨