# Module 2: Code Samples and Hands-On Practice

## Overview

This module includes comprehensive code samples across multiple programming languages to help you practice what you've learned with Azure AI Search basic operations.

## 📁 **Multi-Language Code Samples**

Choose your preferred programming language and dive into focused, beginner-friendly examples:

### 🐍 **Python Examples** - **[📖 Python README](code-samples/python/README.md)**
Perfect for data scientists and Python developers:
- `01_simple_text_search.py` - Basic search operations
- `02_phrase_search.py` - Exact phrase matching  
- `03_boolean_search.py` - Boolean operators (AND, OR, NOT)
- `04_wildcard_search.py` - Pattern matching with wildcards
- `05_field_search.py` - Field-specific searches
- `06_result_processing.py` - Processing and formatting results
- `07_error_handling.py` - Error handling and validation
- `08_search_patterns.py` - Advanced search patterns

### 🔷 **C# Examples** - **[📖 C# README](code-samples/csharp/README.md)**
Ideal for .NET developers and enterprise applications:
- `01_SimpleTextSearch.cs` - Basic search operations in C#
- `02_PhraseSearch.cs` - Exact phrase matching
- `03_BooleanSearch.cs` - Boolean search operations
- `04_WildcardSearch.cs` - Wildcard pattern matching
- `05_FieldSearch.cs` - Field-specific searches
- `06_ResultProcessing.cs` - Processing and formatting results
- `07_ErrorHandling.cs` - Error handling and validation
- `08_SearchPatterns.cs` - Advanced search patterns

### 🟨 **JavaScript Examples** - **[📖 JavaScript README](code-samples/javascript/README.md)**
Great for web developers and Node.js applications:
- `01_simple_text_search.js` - Basic search with JavaScript SDK
- `02_phrase_search.js` - Phrase search operations
- `03_boolean_search.js` - Boolean search logic
- `04_wildcard_search.js` - Wildcard searches
- `05_field_search.js` - Field-specific operations
- `06_result_processing.js` - Processing and formatting results
- `07_error_handling.js` - Error handling and validation
- `08_search_patterns.js` - Advanced search patterns

### 🌐 **REST API Examples** - **[📖 REST API README](code-samples/rest/README.md)**
Universal approach for any programming language:
- `01_simple_text_search.http` - Basic REST API calls
- `02_phrase_search.http` - Phrase search via REST
- `03_boolean_search.http` - Boolean operations
- `04_wildcard_search.http` - Wildcard patterns
- `05_field_search.http` - Field-specific searches
- `06_result_processing.http` - Processing and formatting results
- `07_error_handling.http` - Error handling and validation
- `08_search_patterns.http` - Advanced search patterns

### 📓 **Interactive Notebooks**
Perfect for learning and experimentation:
- `basic_search.ipynb` - Interactive step-by-step learning

## 🚀 **Quick Start with Code Samples**

=== "Python"
    ```bash
    # Install dependencies
    pip install azure-search-documents python-dotenv
    
    # Run focused examples
    cd code-samples/python/
    python 01_simple_text_search.py
    python 02_phrase_search.py
    ```

=== "C#"
    ```bash
    # Add package and run
    dotnet add package Azure.Search.Documents
    dotnet run 01_SimpleTextSearch.cs
    ```

=== "JavaScript"
    ```bash
    # Install and run
    npm install @azure/search-documents
    node code-samples/javascript/01_simple_text_search.js
    ```

=== "REST API"
    ```bash
    # Use with VS Code REST Client or curl
    # Open code-samples/rest/01_simple_text_search.http
    ```

=== "Jupyter Notebook"
    ```bash
    # Interactive learning
    jupyter notebook code-samples/notebooks/basic_search.ipynb
    ```

## 💡 **What's Included**

- **🎯 Focused Examples**: Each file covers one specific concept
- **🌐 Multi-Language Support**: Python, C#, JavaScript, REST API
- **📚 Beginner-Friendly**: Clear explanations and step-by-step code
- **🛡️ Production-Ready**: Comprehensive error handling patterns
- **📓 Interactive Learning**: Jupyter notebooks for hands-on practice
- **🔧 Real-World Patterns**: Common search strategies and best practices

## 🎯 **Learning Paths**

### **Beginner Path** (Recommended)
1. **Theory First**: Read this documentation for concepts
2. **Choose Language**: Pick your preferred language folder
3. **Sequential Learning**: Work through files 01-08 in order
4. **Interactive Practice**: Try the Jupyter notebook
5. **Experimentation**: Modify examples with your own data

### **Quick Reference Path**
- **Need basic search?** → Any `01_simple_text_search.*`
- **Want exact phrases?** → Any `02_phrase_search.*`
- **Combining terms?** → Any `03_boolean_search.*`
- **Partial matching?** → Any `04_wildcard_search.*`
- **Specific fields?** → Any `05_field_search.*`

### **Cross-Language Learning**
- Compare implementations across languages
- Understand REST API fundamentals
- See how concepts translate between platforms

!!! tip "Pro Tip"
    Each language folder includes its own README with specific setup instructions and learning guidance. The examples are designed to be both educational and production-ready.

## 📋 Prerequisites Checklist

Before starting with code examples, ensure you have completed the setup:

- [ ] **Azure AI Search service** created and running
- [ ] **Environment variables** configured with your service details
- [ ] **Prerequisites script** executed successfully (`python setup_prerequisites.py`)
- [ ] **Sample index** created with 10 test documents
- [ ] **Verification test** passed (`python test_setup.py`)

**Haven't completed setup?** → [Complete Prerequisites Setup](prerequisites.md)

## Additional Resources

- **[📚 Code Samples Documentation](code-samples/README.md)** - Detailed guide to all code samples
- [Azure AI Search REST API Reference](https://docs.microsoft.com/en-us/rest/api/searchservice/)
- [Azure AI Search Python SDK Documentation](https://docs.microsoft.com/en-us/python/api/azure-search-documents/)
- [Query Syntax Reference](https://docs.microsoft.com/en-us/azure/search/query-simple-syntax)
- [Search Best Practices](https://docs.microsoft.com/en-us/azure/search/search-performance-optimization)

**Features:**
- ✅ **Interactive execution** - Run code cells individually
- ✅ **Immediate results** - See search results instantly
- ✅ **Experimentation** - Modify queries and see changes
- ✅ **Documentation** - Detailed explanations alongside code
- ✅ **Visualization** - Search results displayed in formatted tables

## 💻 Choose Your Programming Language

### 🐍 Python (Recommended for Data Science & Rapid Prototyping)

**Best for:** Data scientists, Python developers, rapid prototyping, Jupyter notebooks

**Key Features:**
- Comprehensive Azure SDK
- Excellent for data analysis and visualization
- Rich ecosystem of data science libraries
- Interactive development with Jupyter

**Quick Start:**
```bash
cd code-samples/python/
python basic_search_examples.py
```

**Examples Included:**
- ✅ **Connection setup** with error handling
- ✅ **All 5 search types** (simple, phrase, boolean, wildcard, field-specific)
- ✅ **Result processing** and formatting
- ✅ **Advanced patterns** (pagination, filtering, sorting)
- ✅ **Error handling** and troubleshooting
- ✅ **Performance optimization** techniques

**Sample Code Preview:**
```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Initialize client
search_client = SearchClient(endpoint, index_name, credential)

# Simple search
results = search_client.search("python programming")
for result in results:
    print(f"Title: {result['title']}")
    print(f"Score: {result['@search.score']}")
```

### 🔷 C# (Best for Enterprise & .NET Applications)

**Best for:** Enterprise applications, .NET developers, strongly-typed development, production systems

**Key Features:**
- Strongly-typed SDK with IntelliSense support
- Comprehensive examples for scalable applications
- Excellent integration with .NET ecosystem
- Enterprise-grade error handling

**Quick Start:**
```bash
cd code-samples/csharp/
dotnet run
```

**Examples Included:**
- ✅ **Strongly-typed models** for search results
- ✅ **Comprehensive patterns** for scalable code
- ✅ **LINQ-style querying** for familiar syntax
- ✅ **Comprehensive error handling** with try-catch patterns
- ✅ **Configuration management** with appsettings.json
- ✅ **Dependency injection** patterns

**Sample Code Preview:**
```csharp
var searchClient = new SearchClient(endpoint, indexName, credential);

var searchResults = searchClient.Search<SearchDocument>("python programming");
foreach (var result in searchResults.Value.GetResults())
{
    Console.WriteLine($"Title: {result.Document["title"]}");
    Console.WriteLine($"Score: {result.Score}");
}
```

### 🟨 JavaScript/Node.js (Perfect for Web Development)

**Best for:** Web developers, Node.js applications, browser-based search, modern web frameworks

**Key Features:**
- Works in both browser and Node.js environments
- Promise-based operations
- Excellent for real-time search interfaces
- Easy integration with web frameworks

**Quick Start:**
```bash
cd code-samples/javascript/
npm install
node basic_search_examples.js
```

**Examples Included:**
- ✅ **Browser and Node.js** compatible code
- ✅ **Promise-based** operations
- ✅ **Real-time search** implementation
- ✅ **Web framework integration** examples
- ✅ **CORS handling** for browser applications
- ✅ **Modern ES6+ syntax** with comprehensive examples

**Sample Code Preview:**
```javascript
const { SearchClient, AzureKeyCredential } = require("@azure/search-documents");

const searchClient = new SearchClient(endpoint, indexName, new AzureKeyCredential(apiKey));

function searchDocuments(query) {
    const searchResults = searchClient.search(query);
    for (const result of searchResults.results) {
        console.log(`Title: ${result.document.title}`);
        console.log(`Score: ${result.score}`);
    }
}
```

### 🌐 REST API (Universal Compatibility)

**Best for:** Any programming language, direct HTTP integration, debugging, testing, custom implementations

**Key Features:**
- Works with any programming language
- Direct HTTP requests for maximum control
- Excellent for debugging and testing
- No SDK dependencies required

**Quick Start:**
```bash
cd code-samples/rest-api/
# View examples in rest_api_examples.http
# Or run with curl/PowerShell scripts
```

**Examples Included:**
- ✅ **HTTP request examples** for all operations
- ✅ **cURL commands** for command-line testing
- ✅ **PowerShell scripts** for Windows users
- ✅ **Postman collection** for GUI testing
- ✅ **Raw HTTP examples** for any language
- ✅ **Authentication patterns** (API key, OAuth)

**Sample Code Preview:**
```http
### Simple Search
GET {{endpoint}}/indexes/{{indexName}}/docs/search?api-version=2023-11-01
Content-Type: application/json
api-key: {{apiKey}}

{
    "search": "python programming",
    "top": 10
}
```

## 🔍 Search Operation Examples

All languages demonstrate these 5 core search operations:

### 1. **Simple Text Search**
Basic keyword searching across all searchable fields.

**Use Cases:**
- General content discovery
- User-friendly search boxes
- Broad topic exploration

**Example Queries:**
- `"python programming"`
- `"machine learning"`
- `"web development"`

### 2. **Phrase Search**
Exact phrase matching using quotation marks.

**Use Cases:**
- Finding exact titles or names
- Searching for specific terminology
- Precise content matching

**Example Queries:**
- `'"artificial intelligence"'`
- `'"data science fundamentals"'`
- `'"cloud computing"'`

### 3. **Boolean Search**
Combining terms with AND, OR, NOT operators.

**Use Cases:**
- Complex search requirements
- Including/excluding specific terms
- Logical query combinations

**Example Queries:**
- `"python AND tutorial"`
- `"(javascript OR typescript) AND framework"`
- `"programming NOT deprecated"`

### 4. **Wildcard Search**
Pattern matching with asterisk (*) for partial terms.

**Use Cases:**
- Handling variations in terminology
- Searching with incomplete information
- Finding related terms

**Example Queries:**
- `"program*"` (finds programming, programmer, etc.)
- `"data*"` (finds database, dataset, etc.)
- `"*script"` (finds JavaScript, TypeScript, etc.)

### 5. **Field-Specific Search**
Targeting specific document fields for precise results.

**Use Cases:**
- Searching specific metadata
- Author or category filtering
- Structured data queries

**Example Queries:**
- `title:"Python Programming"`
- `author:"John Smith"`
- `category:"Tutorial"`

## 📊 Working with Search Results

### Result Structure
Every search result contains:

```json
{
    "@search.score": 4.489,
    "id": "doc1",
    "title": "Python Programming Fundamentals",
    "content": "Learn Python programming...",
    "author": "Jane Smith",
    "category": "Programming",
    "rating": 4.8,
    "publishedDate": "2023-01-15T00:00:00Z"
}
```

### Key Result Fields
- **`@search.score`**: Relevance score (higher = more relevant)
- **Document fields**: All indexed fields from your documents
- **Metadata**: Additional information about the search operation

### Processing Results
All examples demonstrate:
- ✅ **Iterating through results** efficiently
- ✅ **Extracting key information** (title, score, content)
- ✅ **Formatting for display** in user interfaces
- ✅ **Handling empty results** gracefully
- ✅ **Pagination** for large result sets

## 🎯 Practical Exercises

### Exercise 1: Basic Search Exploration
1. Run the simple text search examples
2. Try different search terms from the sample data
3. Observe how scores change with different queries
4. Experiment with single vs. multiple keywords

### Exercise 2: Advanced Query Techniques
1. Practice phrase searches with exact matches
2. Build complex boolean queries
3. Use wildcards to find term variations
4. Target specific fields for precise results

### Exercise 3: Result Analysis
1. Compare scores across different search types
2. Analyze which queries return the most relevant results
3. Understand how different fields affect relevance
4. Practice result formatting and display

### Exercise 4: Error Handling
1. Test with invalid queries to see error handling
2. Try searches that return no results
3. Experiment with malformed requests
4. Practice graceful error recovery

## 🔧 Customization and Extension

### Adapting Examples to Your Data

Once you understand the basics, adapt the examples:

1. **Change the Index**: Point to your own search index
2. **Modify Fields**: Update field names to match your schema
3. **Adjust Queries**: Create searches relevant to your content
4. **Customize Results**: Format output for your application needs

### Integration Patterns

The examples demonstrate patterns for:
- ✅ **Web applications**: Search APIs and user interfaces
- ✅ **Data analysis**: Programmatic content discovery
- ✅ **Content management**: Document search and retrieval
- ✅ **E-commerce**: Product search and filtering

## 🚀 Next Steps

After completing the code samples:

1. **📖 [Review Best Practices](best-practices.md)** - Learn professional implementation techniques
2. **🛠️ [Study Troubleshooting](troubleshooting.md)** - Prepare for common issues
3. **🎯 [Move to Module 3](../module-03-index-management/overview.md)** - Learn index management
4. **🔧 [Build Your Own](../../../setup/README.md)** - Apply concepts to your own projects

## 📋 Success Checklist

You've mastered basic search operations when you can:

- [ ] **Execute all 5 search types** successfully in your chosen language
- [ ] **Process and format results** appropriately for display
- [ ] **Handle errors gracefully** with proper error messages
- [ ] **Understand relevance scores** and result ranking
- [ ] **Adapt examples** to work with different data
- [ ] **Integrate search functionality** into your own applications

---

**Ready to start coding?** Choose your preferred language above and dive into the hands-on examples! 🚀