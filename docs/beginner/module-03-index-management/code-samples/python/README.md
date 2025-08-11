# Python Code Samples - Module 3: Index Management

This directory contains focused Python examples for index management operations in Azure AI Search. Each file demonstrates a specific aspect of index management with clear, production-ready code.

## 📁 File Structure

```
python/
├── README.md                           # This file
├── 01_create_basic_index.py           # Basic index creation
├── 02_schema_design.py                # Advanced schema design patterns
├── 03_data_ingestion.py               # Document upload strategies
├── 04_index_operations.py             # Index management operations
├── 05_performance_optimization.py     # Performance tuning techniques
└── 06_error_handling.py               # Robust error handling patterns
```

## 🚀 Quick Start

### Prerequisites

1. **Environment Setup**:
   ```bash
   # Set environment variables
   export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
   export AZURE_SEARCH_ADMIN_KEY="your-admin-api-key"
   
   # Install dependencies
   pip install azure-search-documents python-dotenv
   ```

2. **Run Prerequisites Setup**:
   ```bash
   cd ../
   python setup_prerequisites.py
   ```

### Running Examples

```bash
# Basic index creation
python 01_create_basic_index.py

# Advanced schema design
python 02_schema_design.py

# Data ingestion strategies
python 03_data_ingestion.py

# Continue with other examples...
```

## 📚 Example Categories

### 1. Basic Index Creation (`01_create_basic_index.py`)
**Focus**: Fundamental index creation concepts

**What you'll learn**:
- Creating SearchIndexClient
- Defining field types and attributes
- Basic index creation and validation
- Testing index functionality

**Key concepts**:
```python
# Basic field definition
SimpleField(name="id", type=SearchFieldDataType.String, key=True)
SearchableField(name="title", type=SearchFieldDataType.String)

# Index creation
index = SearchIndex(name="my-index", fields=fields)
result = index_client.create_index(index)
```

### 2. Schema Design (`02_schema_design.py`)
**Focus**: Advanced schema design patterns and best practices

**What you'll learn**:
- Field type selection strategies
- Attribute optimization for performance
- Complex field structures
- Schema design patterns for different use cases

**Key concepts**:
```python
# Complex field with nested structure
ComplexField(name="author", fields=[
    SimpleField(name="name", type=SearchFieldDataType.String),
    SimpleField(name="email", type=SearchFieldDataType.String)
])

# Collection fields
SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String))
```

### 3. Data Ingestion (`03_data_ingestion.py`)
**Focus**: Efficient document upload and management strategies

**What you'll learn**:
- Single vs batch document uploads
- Large dataset handling techniques
- Upload optimization strategies
- Progress tracking and monitoring

**Key concepts**:
```python
# Batch upload with error handling
result = search_client.upload_documents(documents)
successful = sum(1 for r in result if r.succeeded)

# Large dataset processing
for batch in create_batches(large_dataset, batch_size=100):
    upload_batch(batch)
```

### 4. Index Operations (`04_index_operations.py`)
**Focus**: Index lifecycle management operations

**What you'll learn**:
- Listing and inspecting indexes
- Getting index statistics
- Updating index schemas
- Index deletion and cleanup

**Key concepts**:
```python
# List indexes
indexes = list(index_client.list_indexes())

# Get index details
index = index_client.get_index("my-index")

# Update schema
updated_index = SearchIndex(name="my-index", fields=new_fields)
index_client.create_or_update_index(updated_index)
```

### 5. Performance Optimization (`05_performance_optimization.py`)
**Focus**: Performance tuning and optimization techniques

**What you'll learn**:
- Batch size optimization
- Parallel upload strategies
- Memory management techniques
- Performance monitoring and metrics

**Key concepts**:
```python
# Custom analyzer
custom_analyzer = CustomAnalyzer(
    name="my_analyzer",
    tokenizer_name="standard",
    token_filters=["lowercase", "stop"]
)

# Scoring profile
scoring_profile = ScoringProfile(
    name="boost_recent",
    text_weights=TextWeights(weights={"title": 2.0})
)
```

### 6. Error Handling (`06_error_handling.py`)
**Focus**: Robust error handling and recovery patterns

**What you'll learn**:
- Common error scenarios and solutions
- Retry strategies with exponential backoff
- Partial failure handling
- Graceful degradation techniques

**Key concepts**:
```python
# Optimal batch sizing
def get_optimal_batch_size(document_size):
    if document_size < 1024:  # 1KB
        return 1000
    elif document_size < 10240:  # 10KB
        return 500
    else:
        return 100

# Parallel processing
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(upload_batch, batch) for batch in batches]
```

**Key concepts**:
```python
# Retry with exponential backoff
@retry(max_attempts=3, backoff_factor=2.0)
def upload_with_retry(documents):
    return search_client.upload_documents(documents)

# Comprehensive error handling
try:
    result = upload_documents(docs)
except HttpResponseError as e:
    handle_http_error(e)
except Exception as e:
    handle_general_error(e)
```

## 🎯 Learning Paths

### 1. Beginner Path (Sequential)
Follow the numbered sequence for structured learning:

```bash
python 01_create_basic_index.py      # Start here
python 02_schema_design.py           # Learn schema design
python 03_data_ingestion.py          # Master data upload
python 04_index_operations.py        # Index management
# Continue through all examples...
```

### 2. Topic-Focused Path
Jump to specific areas of interest:

```bash
# Focus on performance
python 05_performance_optimization.py

# Focus on error handling
python 06_error_handling.py

# Focus on index operations
python 04_index_operations.py
```

### 3. Problem-Solving Path
Start with common scenarios:

```bash
# "I need to create an index"
python 01_create_basic_index.py

# "I need to upload lots of data"
python 03_data_ingestion.py

# "My uploads are failing"
python 06_error_handling.py
```

## 🔧 Code Features

### Production-Ready Patterns
- ✅ Comprehensive error handling
- ✅ Input validation and sanitization
- ✅ Proper resource cleanup
- ✅ Logging and monitoring integration

### Performance Optimizations
- ✅ Efficient batch processing
- ✅ Memory-conscious data handling
- ✅ Connection pooling and reuse
- ✅ Parallel processing where appropriate

### Best Practices
- ✅ Environment variable configuration
- ✅ Secure credential management
- ✅ Clear code structure and documentation
- ✅ Modular, reusable functions

## 🚨 Common Issues and Solutions

### Issue 1: Import Errors
```bash
# Problem: Cannot import azure.search.documents
# Solution: Install the correct package
pip install azure-search-documents==11.4.0
```

### Issue 2: Authentication Errors
```python
# Problem: 403 Forbidden errors
# Solution: Use admin key for index operations
credential = AzureKeyCredential(admin_key)  # Not query key!
```

### Issue 3: Index Already Exists
```python
# Problem: Index creation fails because it exists
# Solution: Use create_or_update_index
result = index_client.create_or_update_index(index)  # Safe
```

### Issue 4: Document Upload Failures
```python
# Problem: Some documents fail to upload
# Solution: Check individual results
for result in upload_results:
    if not result.succeeded:
        print(f"Failed: {result.key} - {result.error_message}")
```

## 💡 Tips for Success

### Development Workflow
1. **Start Simple**: Begin with basic examples and add complexity
2. **Test Frequently**: Run examples with small datasets first
3. **Handle Errors**: Always implement proper error handling
4. **Monitor Performance**: Track upload speeds and success rates
5. **Clean Up**: Delete test indexes when done

### Debugging Techniques
1. **Enable Logging**: Use Python logging for detailed output
2. **Check Responses**: Examine HTTP response codes and messages
3. **Validate Data**: Ensure documents match your schema
4. **Test Incrementally**: Upload small batches to isolate issues
5. **Use Try-Catch**: Wrap operations in appropriate exception handling

### Performance Tips
1. **Batch Operations**: Always use batch uploads for multiple documents
2. **Optimize Batch Size**: Adjust based on document size and complexity
3. **Use Parallel Processing**: For large datasets, consider parallel uploads
4. **Monitor Resources**: Watch memory usage during large operations
5. **Connection Reuse**: Reuse clients instead of creating new ones

## 🔗 Related Resources

### Module 3 Resources
- **[Module 3 Documentation](../documentation.md)** - Complete theory and concepts
- **[Interactive Notebooks](../notebooks/README.md)** - Jupyter notebook examples
- **[C# Examples](../csharp/README.md)** - .NET implementations
- **[JavaScript Examples](../javascript/README.md)** - Node.js implementations

### External Resources
- **[Azure AI Search Python SDK](https://docs.microsoft.com/en-us/python/api/azure-search-documents/)** - Official SDK documentation
- **[Azure AI Search REST API](https://docs.microsoft.com/en-us/rest/api/searchservice/)** - REST API reference
- **[Python Best Practices](https://docs.python.org/3/tutorial/)** - Python programming guide

## 🚀 Next Steps

After mastering these Python examples:

1. **✅ Complete All Examples**: Work through each file systematically
2. **🔬 Experiment**: Modify examples to work with your own data
3. **📝 Practice**: Complete the module exercises
4. **🌐 Explore Other Languages**: Try C#, JavaScript, or REST examples
5. **🏗️ Build Applications**: Apply concepts to real-world projects
6. **📚 Continue Learning**: Move to Module 4: Simple Queries and Filters

---

**Ready to master Azure AI Search index management with Python?** 🐍✨

Start with `01_create_basic_index.py` and begin your journey!