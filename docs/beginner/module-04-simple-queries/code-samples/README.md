# Module 4: Simple Queries and Filters - Code Samples

This directory contains comprehensive code samples for learning simple queries and filters in Azure AI Search. The examples are organized by programming language and complexity level.

## 📁 Directory Structure

```
code-samples/
├── README.md                    # This file
├── notebooks/                   # Interactive Jupyter notebooks
│   └── simple_queries.ipynb    # Step-by-step query examples
├── python/                      # Python implementations
│   ├── README.md               # Python-specific documentation
│   ├── 01_basic_queries.py     # Simple text search examples
│   ├── 02_filtering.py         # OData filter examples
│   ├── 03_sorting_pagination.py # Sorting and pagination
│   ├── 04_result_customization.py # Field selection and highlighting
│   ├── 05_advanced_queries.py  # Complex query patterns
│   └── 06_error_handling.py    # Error handling and validation
├── csharp/                      # C# implementations
│   ├── README.md               # C#-specific documentation
│   ├── 01_BasicQueries.cs      # Simple text search examples
│   ├── 02_Filtering.cs         # OData filter examples
│   ├── 03_SortingPagination.cs # Sorting and pagination
│   ├── 04_ResultCustomization.cs # Field selection and highlighting
│   ├── 05_AdvancedQueries.cs   # Complex query patterns
│   └── 06_ErrorHandling.cs     # Error handling and validation
├── javascript/                  # JavaScript/Node.js implementations
│   ├── README.md               # JavaScript-specific documentation
│   ├── 01_basic_queries.js     # Simple text search examples
│   ├── 02_filtering.js         # OData filter examples
│   ├── 03_sorting_pagination.js # Sorting and pagination
│   ├── 04_result_customization.js # Field selection and highlighting
│   ├── 05_advanced_queries.js  # Complex query patterns
│   └── 06_error_handling.js    # Error handling and validation
└── rest/                        # REST API examples
    ├── README.md               # REST API documentation
    ├── 01_basic_queries.http    # Simple text search examples
    ├── 02_filtering.http        # OData filter examples
    ├── 03_sorting_pagination.http # Sorting and pagination
    ├── 04_result_customization.http # Field selection and highlighting
    ├── 05_advanced_queries.http # Complex query patterns
    └── 06_error_handling.http   # Error handling examples
```

## 🚀 Quick Start

### Prerequisites

Before running any examples, ensure you have:

1. **Completed previous modules** - Modules 1-3 should be finished
2. **Azure AI Search service** - With sample indexes created
3. **Environment configured** - API keys and endpoints set up
4. **Required packages** - Install dependencies for your chosen language

### Choose Your Learning Path

#### 📓 Interactive Learning (Recommended for Beginners)
Start with the Jupyter notebook for hands-on, step-by-step learning:
```bash
jupyter notebook notebooks/simple_queries.ipynb
```

#### 🐍 Python Development
For Python developers, start with the basic queries:
```bash
python python/01_basic_queries.py
```

#### 🔷 .NET Development
For C# developers, compile and run the examples:
```bash
dotnet run csharp/01_BasicQueries.cs
```

#### 🟨 JavaScript Development
For Node.js developers:
```bash
node javascript/01_basic_queries.js
```

#### 🌐 REST API Testing
Use your favorite HTTP client (VS Code REST Client, Postman, curl):
```http
# Open rest/01_basic_queries.http in VS Code with REST Client extension
```

## 📚 Learning Progression

Follow this recommended order for optimal learning:

### 1. Basic Text Search
- **Focus**: Simple query syntax, basic text search
- **Files**: `01_basic_queries.*`
- **Concepts**: Search text, search fields, query operators

### 2. Filtering
- **Focus**: OData filter expressions
- **Files**: `02_filtering.*`
- **Concepts**: Filter operators, logical combinations, data types

### 3. Sorting and Pagination
- **Focus**: Result ordering and pagination
- **Files**: `03_sorting_pagination.*`
- **Concepts**: Order by, top/skip, pagination patterns

### 4. Result Customization
- **Focus**: Field selection and highlighting
- **Files**: `04_result_customization.*`
- **Concepts**: Select fields, search highlighting, result formatting

### 5. Advanced Queries
- **Focus**: Complex query patterns
- **Files**: `05_advanced_queries.*`
- **Concepts**: Boosting, fuzzy search, regex, faceting

### 6. Error Handling
- **Focus**: Robust query implementation
- **Files**: `06_error_handling.*`
- **Concepts**: Exception handling, validation, debugging

## 🔧 Configuration

### Environment Variables

Ensure these environment variables are set:

```bash
# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
AZURE_SEARCH_API_KEY="your-api-key"
AZURE_SEARCH_INDEX_NAME="your-index-name"

# Optional: For advanced examples
AZURE_SEARCH_ADMIN_KEY="your-admin-key"
```

### Sample Data

The examples assume you have sample indexes created from previous modules. If you need to recreate them:

```python
# Run this from the module-03 directory
python code-samples/setup_prerequisites.py
```

## 🎯 Key Learning Outcomes

After completing these code samples, you will be able to:

- ✅ **Construct Basic Queries**: Write effective search queries using simple syntax
- ✅ **Apply Filters**: Use OData expressions to filter search results
- ✅ **Implement Sorting**: Order results by relevance, date, or custom criteria
- ✅ **Handle Pagination**: Efficiently navigate through large result sets
- ✅ **Customize Results**: Select specific fields and highlight matching terms
- ✅ **Handle Errors**: Implement robust error handling and validation
- ✅ **Optimize Performance**: Write efficient queries for production use

## 🔍 Example Queries

Here are some sample queries you'll learn to build:

### Basic Text Search
```python
# Simple search
results = search_client.search(search_text="azure machine learning")

# Field-specific search
results = search_client.search(
    search_text="python",
    search_fields=["title", "tags"]
)
```

### Filtering
```python
# Category filter
results = search_client.search(
    search_text="*",
    filter="category eq 'Technology' and rating ge 4.0"
)

# Date range filter
results = search_client.search(
    search_text="azure",
    filter="publishedDate ge 2023-01-01T00:00:00Z"
)
```

### Sorting and Pagination
```python
# Sorted results with pagination
results = search_client.search(
    search_text="azure",
    order_by=["publishedDate desc"],
    top=10,
    skip=20
)
```

### Result Customization
```python
# Custom fields with highlighting
results = search_client.search(
    search_text="machine learning",
    select=["id", "title", "summary"],
    highlight_fields=["title", "content"]
)
```

## 🐛 Troubleshooting

### Common Issues

1. **No Results Returned**
   - Check if your search index contains data
   - Verify your query syntax
   - Try broader search terms

2. **Authentication Errors**
   - Verify your API key is correct
   - Check the service endpoint URL
   - Ensure the key has appropriate permissions

3. **Syntax Errors**
   - Validate OData filter syntax
   - Check for balanced quotes and parentheses
   - Review field names and data types

4. **Performance Issues**
   - Reduce page size for large result sets
   - Optimize filter expressions
   - Limit selected fields

### Getting Help

- Review the main documentation: `../documentation.md`
- Check language-specific README files in each subdirectory
- Run the error handling examples for debugging techniques
- Refer to Azure AI Search documentation for advanced scenarios

## 🔗 Related Resources

- [Azure AI Search REST API Reference](https://docs.microsoft.com/en-us/rest/api/searchservice/)
- [OData Filter Expression Syntax](https://docs.microsoft.com/en-us/azure/search/search-query-odata-filter)
- [Simple Query Syntax](https://docs.microsoft.com/en-us/azure/search/query-simple-syntax)
- [Full Lucene Query Syntax](https://docs.microsoft.com/en-us/azure/search/query-lucene-syntax)

## 📝 Next Steps

After mastering these examples:

1. **Practice with Your Own Data**: Apply these patterns to your specific use case
2. **Explore Advanced Features**: Move on to Module 5 for advanced querying
3. **Build a Search UI**: Create a user interface for your search functionality
4. **Monitor Performance**: Learn about search analytics and optimization

Happy searching! 🔍