# Module 3: Index Management

## Overview

This module teaches you the fundamentals of index management in Azure AI Search. You'll learn how to create, configure, and maintain search indexes, design effective schemas, and implement robust data ingestion strategies. By the end of this module, you'll be able to build and manage production-ready search indexes that scale with your application needs.

!!! info "Hands-On Learning Available"
    This module includes comprehensive **[Code Samples](code-samples/README.md)** with interactive Jupyter notebooks, complete Python scripts, and advanced examples. The code samples are designed to complement this documentation with practical, runnable examples you can use immediately.

    **⚠️ IMPORTANT: Run Prerequisites Setup First!**
    
    Before using any examples, run the [Prerequisites Setup](code-samples/setup_prerequisites.py) to configure your environment and create sample indexes.
    
    **Quick Start Options:**
    
    1. 🔧 **Prerequisites Setup**: [Run setup_prerequisites.py](code-samples/setup_prerequisites.py) - **REQUIRED FIRST STEP**
    2. 📓 **Interactive Learning**: [Jupyter Notebook](code-samples/notebooks/index_management.ipynb) with step-by-step examples
    3. 🐍 **Python Examples**: [Complete Python Scripts](code-samples/python/) with all index operations
    4. 🔷 **C# Examples**: [.NET Implementation](code-samples/csharp/) for enterprise applications
    5. 🟨 **JavaScript Examples**: [Node.js/Browser Code](code-samples/javascript/) for web integration
    6. 🌐 **REST API Examples**: [Direct HTTP Calls](code-samples/rest/) for any language

## Learning Objectives

By completing this module, you will be able to:

- Create and configure search indexes using the Azure AI Search Python SDK
- Design effective index schemas with appropriate field types and attributes
- Implement data ingestion strategies for different data sources
- Manage index lifecycle operations (create, update, delete, rebuild)
- Handle index versioning and schema evolution
- Optimize index performance and storage
- Troubleshoot common index management issues
- Apply best practices for production index management

## Prerequisites

Before starting with index management, you need to complete the setup process and have a solid understanding of basic search operations.

**📋 [Complete Prerequisites Setup →](prerequisites.md)**

The prerequisites setup includes:
- ✅ **Environment Configuration** - Azure service and API keys
- ✅ **Development Setup** - Required packages and tools  
- ✅ **Sample Index Creation** - Practice indexes for learning
- ✅ **Functionality Testing** - All index operations verified

**⚠️ CRITICAL**: You must complete the [Prerequisites Setup](prerequisites.md) before attempting any examples in this module!

## Index Fundamentals

### What is a Search Index?

A search index in Azure AI Search is a persistent collection of documents that enables fast, full-text search operations. Think of it as a specialized database optimized for search rather than transactional operations.

### Key Index Components

Every search index consists of:

1. **Schema Definition**: The structure defining fields, data types, and attributes
2. **Documents**: The actual data stored in the index
3. **Analyzers**: Text processing rules for searchable fields
4. **Scoring Profiles**: Custom relevance scoring configurations
5. **CORS Options**: Cross-origin resource sharing settings
6. **Encryption Keys**: Customer-managed encryption (optional)

### Index vs Database Table

| Aspect | Search Index | Database Table |
|--------|-------------|----------------|
| **Purpose** | Optimized for search and retrieval | Optimized for transactions |
| **Schema** | Flexible, search-focused fields | Rigid, normalized structure |
| **Queries** | Full-text search, faceting, filtering | SQL queries, joins |
| **Performance** | Fast search, slower writes | Fast writes, variable read speed |
| **Scaling** | Horizontal scaling with partitions | Vertical/horizontal scaling |

## Creating Your First Index

### Basic Index Creation

Let's start with a simple index for a blog application:

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    ComplexField,
    SearchFieldDataType
)
from azure.core.credentials import AzureKeyCredential

# Initialize the index client
index_client = SearchIndexClient(
    endpoint="https://your-service.search.windows.net",
    credential=AzureKeyCredential("your-admin-api-key")
)

# Define the index schema
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="author", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, 
                filterable=True, sortable=True),
    SimpleField(name="category", type=SearchFieldDataType.String, 
                filterable=True, facetable=True),
    SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                filterable=True, facetable=True)
]

# Create the index
index = SearchIndex(name="blog-posts", fields=fields)
result = index_client.create_index(index)
print(f"Index '{result.name}' created successfully!")
```

!!! success "Complete Index Creation Examples"
    For comprehensive index creation examples with error handling, validation, and advanced configurations, see the code samples:
    - [Python: `01_create_basic_index.py`](code-samples/python/01_create_basic_index.py)
    - [C#: `01_CreateBasicIndex.cs`](code-samples/csharp/01_CreateBasicIndex.cs)
    - [JavaScript: `01_create_basic_index.js`](code-samples/javascript/01_create_basic_index.js)
    - [REST API: `01_create_basic_index.http`](code-samples/rest/01_create_basic_index.http)

!!! tip "Advanced Topics Available"
    Beyond basic creation, explore advanced index management:
    - **Schema Design**: [02_schema_design.*](code-samples/) - Complex fields and optimization
    - **Index Operations**: [04_index_operations.*](code-samples/) - Lifecycle management
    - **Performance**: [05_performance_optimization.*](code-samples/) - Batch sizing and parallel processing
    - **Error Handling**: [06_error_handling.*](code-samples/) - Comprehensive troubleshooting

### Understanding Field Types

Azure AI Search supports various field types for different use cases:

#### String Fields
```python
# Simple string field
SimpleField(name="id", type=SearchFieldDataType.String, key=True)

# Searchable string field (full-text search enabled)
SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft")

# String collection (array of strings)
SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String))
```

#### Numeric Fields
```python
# Integer field
SimpleField(name="viewCount", type=SearchFieldDataType.Int32, filterable=True, sortable=True)

# Double field for ratings
SimpleField(name="rating", type=SearchFieldDataType.Double, filterable=True, sortable=True)

# Long field for large numbers
SimpleField(name="fileSize", type=SearchFieldDataType.Int64, filterable=True)
```

#### Date and Boolean Fields
```python
# Date field
SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset, 
            filterable=True, sortable=True)

# Boolean field
SimpleField(name="isPublished", type=SearchFieldDataType.Boolean, filterable=True)
```

#### Geographic Fields
```python
# Geographic point for location-based search
SimpleField(name="location", type=SearchFieldDataType.GeographyPoint, filterable=True)
```

### Field Attributes

Control field behavior with these attributes:

```python
SearchableField(
    name="content",
    type=SearchFieldDataType.String,
    searchable=True,      # Enable full-text search
    filterable=True,      # Enable filtering
    sortable=True,        # Enable sorting
    facetable=True,       # Enable faceting
    retrievable=True,     # Include in search results
    analyzer_name="en.microsoft"  # Text analyzer
)
```

#### Attribute Combinations

| Use Case | Searchable | Filterable | Sortable | Facetable | Retrievable |
|----------|------------|------------|----------|-----------|-------------|
| **Full-text search** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Exact match filter** | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Sort results** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Faceted navigation** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Hidden metadata** | ❌ | ✅ | ✅ | ❌ | ❌ |

## Schema Design Best Practices

### Designing for Performance

#### 1. Choose Appropriate Field Types
```python
# Good: Use specific types
SimpleField(name="price", type=SearchFieldDataType.Double)
SimpleField(name="quantity", type=SearchFieldDataType.Int32)

# Avoid: Using strings for numeric data
# SimpleField(name="price", type=SearchFieldDataType.String)  # Don't do this
```

#### 2. Minimize Searchable Fields
```python
# Only make fields searchable if they need full-text search
SearchableField(name="title", type=SearchFieldDataType.String)      # Good
SearchableField(name="content", type=SearchFieldDataType.String)    # Good
SimpleField(name="category", type=SearchFieldDataType.String)       # Good - exact match only
```

#### 3. Use Collections Wisely
```python
# Good: For multiple related values
SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String))

# Consider: Complex fields for structured data
ComplexField(name="author", fields=[
    SimpleField(name="name", type=SearchFieldDataType.String),
    SimpleField(name="email", type=SearchFieldDataType.String)
])
```

### Schema Evolution Strategies

#### 1. Additive Changes (Safe)
```python
# Adding new fields is safe and doesn't require rebuild
new_fields = existing_fields + [
    SimpleField(name="newField", type=SearchFieldDataType.String, filterable=True)
]

# Update the index
updated_index = SearchIndex(name="existing-index", fields=new_fields)
index_client.create_or_update_index(updated_index)
```

#### 2. Breaking Changes (Requires Rebuild)
```python
# These changes require index rebuild:
# - Changing field type
# - Changing field attributes (searchable, filterable, etc.)
# - Removing fields
# - Changing analyzers

# Strategy: Create new index, migrate data, swap aliases
```

## Data Ingestion Strategies

### Single Document Upload

```python
from azure.search.documents import SearchClient

# Initialize search client
search_client = SearchClient(
    endpoint="https://your-service.search.windows.net",
    index_name="blog-posts",
    credential=AzureKeyCredential("your-api-key")
)

# Upload a single document
document = {
    "id": "1",
    "title": "Getting Started with Azure AI Search",
    "content": "Azure AI Search is a powerful search service...",
    "author": "John Doe",
    "publishedDate": "2024-01-15T10:00:00Z",
    "category": "Tutorial",
    "tags": ["azure", "search", "tutorial"]
}

result = search_client.upload_documents([document])
print(f"Document uploaded: {result[0].succeeded}")
```

### Batch Document Upload

```python
# Upload multiple documents efficiently
documents = [
    {
        "id": "1",
        "title": "Azure AI Search Basics",
        "content": "Learn the fundamentals...",
        "author": "John Doe",
        "publishedDate": "2024-01-15T10:00:00Z",
        "category": "Tutorial",
        "tags": ["azure", "search"]
    },
    {
        "id": "2", 
        "title": "Advanced Search Techniques",
        "content": "Master complex queries...",
        "author": "Jane Smith",
        "publishedDate": "2024-01-20T14:30:00Z",
        "category": "Advanced",
        "tags": ["search", "advanced", "queries"]
    }
    # ... more documents
]

# Upload in batches (recommended: 100-1000 documents per batch)
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    result = search_client.upload_documents(batch)
    successful = sum(1 for r in result if r.succeeded)
    print(f"Batch {i//batch_size + 1}: {successful}/{len(batch)} documents uploaded")
```

### Handling Large Datasets

```python
import json
from typing import Iterator

def load_documents_from_file(file_path: str, batch_size: int = 100) -> Iterator[list]:
    """Load documents from JSON file in batches"""
    with open(file_path, 'r') as file:
        documents = json.load(file)
    
    for i in range(0, len(documents), batch_size):
        yield documents[i:i + batch_size]

def upload_large_dataset(file_path: str):
    """Upload large dataset with progress tracking and error handling"""
    total_uploaded = 0
    total_failed = 0
    
    for batch_num, batch in enumerate(load_documents_from_file(file_path), 1):
        try:
            result = search_client.upload_documents(batch)
            
            successful = sum(1 for r in result if r.succeeded)
            failed = len(batch) - successful
            
            total_uploaded += successful
            total_failed += failed
            
            print(f"Batch {batch_num}: {successful}/{len(batch)} uploaded")
            
            # Log failed documents
            for i, r in enumerate(result):
                if not r.succeeded:
                    print(f"Failed to upload document {batch[i]['id']}: {r.error_message}")
                    
        except Exception as e:
            print(f"Batch {batch_num} failed completely: {e}")
            total_failed += len(batch)
    
    print(f"Upload complete: {total_uploaded} successful, {total_failed} failed")
```

!!! tip "Complete Data Ingestion Examples"
    For production-ready data ingestion with comprehensive error handling, retry logic, and performance optimization, see the data ingestion examples:
    - [Python: `03_data_ingestion.py`](code-samples/python/03_data_ingestion.py)
    - [C#: `03_DataIngestion.cs`](code-samples/csharp/03_DataIngestion.cs)
    - [JavaScript: `03_data_ingestion.js`](code-samples/javascript/03_data_ingestion.js)
    - [REST API: `03_data_ingestion.http`](code-samples/rest/03_data_ingestion.http)

!!! info "Complete Code Sample Coverage"
    This module includes **6 comprehensive examples** for each programming language:
    
    **📋 All Languages Include:**
    1. **Basic Index Creation** - Fundamentals and field types
    2. **Schema Design** - Advanced patterns and best practices
    3. **Data Ingestion** - Efficient upload strategies
    4. **Index Operations** - Lifecycle management and maintenance
    5. **Performance Optimization** - Batch sizing and parallel operations
    6. **Error Handling** - Comprehensive troubleshooting and recovery
    
    **🔗 Quick Access:**
    - 🐍 [Python Examples](code-samples/python/README.md) - 6 complete files
    - 🔷 [C# Examples](code-samples/csharp/README.md) - 6 complete files  
    - 🟨 [JavaScript Examples](code-samples/javascript/README.md) - 6 complete files
    - 🌐 [REST API Examples](code-samples/rest/README.md) - 6 complete files
    - 📓 [Interactive Notebook](code-samples/notebooks/index_management.ipynb) - All concepts in one place

## Index Operations and Maintenance

### Listing Indexes

```python
# List all indexes in your service
indexes = index_client.list_indexes()
for index in indexes:
    print(f"Index: {index.name}")
    print(f"  Fields: {len(index.fields)}")
    print(f"  Storage: {index.storage_size_in_bytes} bytes")
    print(f"  Documents: {index.document_count}")
```

### Getting Index Information

```python
# Get detailed information about a specific index
index = index_client.get_index("blog-posts")
print(f"Index Name: {index.name}")
print(f"Fields: {len(index.fields)}")
print(f"Analyzers: {len(index.analyzers) if index.analyzers else 0}")
print(f"Scoring Profiles: {len(index.scoring_profiles) if index.scoring_profiles else 0}")

# Display field information
for field in index.fields:
    attributes = []
    if field.searchable: attributes.append("searchable")
    if field.filterable: attributes.append("filterable")
    if field.sortable: attributes.append("sortable")
    if field.facetable: attributes.append("facetable")
    
    print(f"  {field.name} ({field.type}) - {', '.join(attributes)}")
```

### Updating Index Schema

```python
# Get existing index
existing_index = index_client.get_index("blog-posts")

# Add new fields
new_fields = list(existing_index.fields) + [
    SimpleField(name="viewCount", type=SearchFieldDataType.Int32, 
                filterable=True, sortable=True),
    SimpleField(name="lastModified", type=SearchFieldDataType.DateTimeOffset,
                filterable=True, sortable=True)
]

# Update the index
updated_index = SearchIndex(
    name=existing_index.name,
    fields=new_fields,
    analyzers=existing_index.analyzers,
    scoring_profiles=existing_index.scoring_profiles
)

result = index_client.create_or_update_index(updated_index)
print(f"Index '{result.name}' updated successfully!")
```

### Index Statistics and Monitoring

```python
# Get index statistics
stats = index_client.get_service_statistics()
print(f"Storage used: {stats.storage_size_in_bytes} bytes")
print(f"Document count: {stats.document_count}")

# Get index-specific statistics
index_stats = search_client.get_document_count()
print(f"Documents in index: {index_stats}")
```

### Deleting Indexes

```python
# Delete an index (be careful!)
try:
    index_client.delete_index("old-index")
    print("Index deleted successfully")
except Exception as e:
    print(f"Failed to delete index: {e}")
```

## Advanced Index Configuration

### Custom Analyzers

```python
from azure.search.documents.indexes.models import (
    LexicalAnalyzer,
    PatternAnalyzer,
    CustomAnalyzer,
    PatternTokenizer,
    LowerCaseTokenFilter
)

# Define custom analyzer
custom_analyzer = CustomAnalyzer(
    name="custom_analyzer",
    tokenizer_name="pattern",
    token_filters=["lowercase", "asciifolding"],
    char_filters=[]
)

# Create index with custom analyzer
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="title", type=SearchFieldDataType.String, 
                   analyzer_name="custom_analyzer")
]

index = SearchIndex(
    name="custom-analyzer-index",
    fields=fields,
    analyzers=[custom_analyzer]
)

result = index_client.create_index(index)
```

### Scoring Profiles

```python
from azure.search.documents.indexes.models import (
    ScoringProfile,
    TextWeights,
    ScoringFunction,
    ScoringFunctionType,
    ScoringFunctionInterpolation
)

# Define scoring profile
scoring_profile = ScoringProfile(
    name="boost_recent",
    text_weights=TextWeights(weights={"title": 2.0, "content": 1.0}),
    functions=[
        ScoringFunction(
            type=ScoringFunctionType.FRESHNESS,
            field_name="publishedDate",
            boost=2.0,
            interpolation=ScoringFunctionInterpolation.LINEAR,
            freshness={"boosting_duration": "P30D"}  # Boost documents from last 30 days
        )
    ]
)

# Create index with scoring profile
index = SearchIndex(
    name="scored-index",
    fields=fields,
    scoring_profiles=[scoring_profile]
)
```

### CORS Configuration

```python
from azure.search.documents.indexes.models import CorsOptions

# Configure CORS for web applications
cors_options = CorsOptions(
    allowed_origins=["https://mywebsite.com", "https://localhost:3000"],
    max_age_in_seconds=300
)

index = SearchIndex(
    name="web-index",
    fields=fields,
    cors_options=cors_options
)
```

## Error Handling and Troubleshooting

### Common Index Creation Errors

```python
from azure.core.exceptions import HttpResponseError
import logging

def create_index_safely(index_definition):
    """Create index with comprehensive error handling"""
    try:
        result = index_client.create_index(index_definition)
        print(f"Index '{result.name}' created successfully!")
        return result
        
    except HttpResponseError as e:
        if e.status_code == 400:
            logging.error(f"Bad request - check index definition: {e.message}")
        elif e.status_code == 409:
            logging.error(f"Index already exists: {index_definition.name}")
        elif e.status_code == 403:
            logging.error("Access denied - check your admin API key")
        else:
            logging.error(f"HTTP error {e.status_code}: {e.message}")
        return None
        
    except Exception as e:
        logging.error(f"Unexpected error creating index: {str(e)}")
        return None
```

### Data Upload Error Handling

```python
def upload_documents_safely(documents):
    """Upload documents with error handling and retry logic"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = search_client.upload_documents(documents)
            
            # Check for partial failures
            successful = [r for r in result if r.succeeded]
            failed = [r for r in result if not r.succeeded]
            
            if failed:
                print(f"Partial failure: {len(successful)}/{len(documents)} uploaded")
                for failure in failed:
                    print(f"Failed: {failure.key} - {failure.error_message}")
            else:
                print(f"All {len(documents)} documents uploaded successfully")
            
            return result
            
        except HttpResponseError as e:
            if e.status_code == 503 and attempt < max_retries - 1:
                print(f"Service unavailable, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Upload failed: {e.message}")
                return None
                
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
    
    return None
```

## Performance Optimization

### Index Design for Performance

#### 1. Field Optimization
```python
# Optimize field attributes for your use case
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    
    # Only searchable if full-text search is needed
    SearchableField(name="title", type=SearchFieldDataType.String),
    
    # Use SimpleField for exact-match scenarios
    SimpleField(name="category", type=SearchFieldDataType.String, 
                filterable=True, facetable=True),
    
    # Minimize sortable fields (they use more storage)
    SimpleField(name="publishedDate", type=SearchFieldDataType.DateTimeOffset,
                filterable=True, sortable=True),
    
    # Don't make large text fields sortable
    SearchableField(name="content", type=SearchFieldDataType.String,
                   retrievable=False)  # Don't return in results if not needed
]
```

#### 2. Batch Size Optimization
```python
# Optimal batch sizes for different scenarios
def get_optimal_batch_size(document_size_kb):
    """Determine optimal batch size based on document size"""
    if document_size_kb < 1:
        return 1000  # Small documents
    elif document_size_kb < 10:
        return 500   # Medium documents
    elif document_size_kb < 100:
        return 100   # Large documents
    else:
        return 50    # Very large documents
```

#### 3. Parallel Upload Strategy
```python
import concurrent.futures
import threading

def parallel_upload(documents, max_workers=4):
    """Upload documents in parallel for better performance"""
    batch_size = get_optimal_batch_size(estimate_document_size(documents[0]))
    batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_batch = {
            executor.submit(search_client.upload_documents, batch): batch 
            for batch in batches
        }
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                result = future.result()
                results.extend(result)
                print(f"Batch of {len(batch)} documents uploaded")
            except Exception as e:
                print(f"Batch upload failed: {e}")
    
    return results
```

## Best Practices Summary

### Schema Design
- ✅ Use specific field types (Int32, Double) instead of strings for numeric data
- ✅ Only make fields searchable if they need full-text search
- ✅ Minimize sortable fields to reduce storage overhead
- ✅ Use collections for multi-value fields
- ✅ Plan for schema evolution with additive changes

### Data Ingestion
- ✅ Use batch uploads (100-1000 documents per batch)
- ✅ Implement retry logic with exponential backoff
- ✅ Handle partial failures gracefully
- ✅ Monitor upload progress and performance
- ✅ Use parallel uploads for large datasets

### Performance
- ✅ Choose appropriate batch sizes based on document size
- ✅ Use parallel uploads with thread pools
- ✅ Monitor index statistics and storage usage
- ✅ Optimize field attributes for your use case
- ✅ Consider index partitioning for very large datasets

### Maintenance
- ✅ Regular monitoring of index health and performance
- ✅ Plan for index rebuilds when making breaking changes
- ✅ Implement proper error handling and logging
- ✅ Use staging indexes for testing schema changes
- ✅ Document your index schema and design decisions

## Next Steps

After completing this module, you should be comfortable with:

- Creating and configuring search indexes
- Designing effective schemas for your use case
- Implementing robust data ingestion strategies
- Managing index lifecycle operations
- Optimizing performance and handling errors

**Recommended Learning Path:**

1. ✅ Complete the theory (this documentation)
2. 🔬 Practice with the [code samples](code-samples/README.md)
3. 📝 Work through the exercises (coming soon)
4. 🚀 Move to **Module 4: Simple Queries and Filters**

In the next module, you'll learn about **Simple Queries and Filters**, where you'll discover how to construct effective search queries and apply filters to refine your search results.

## Code Samples and Hands-On Practice

Ready to put your knowledge into practice? This module includes comprehensive code samples across multiple programming languages.

**👨‍💻 [Complete Code Samples Guide →](code-samples/README.md)**

What's included:

- ✅ **Multi-Language Support** - Python, C#, JavaScript, REST API (6 files each)
- ✅ **Focused Examples** - Each file covers one specific concept  
- ✅ **Interactive Learning** - Jupyter notebooks for hands-on practice
- ✅ **Production-Ready** - Comprehensive error handling patterns
- ✅ **Learning Paths** - Beginner, quick reference, and cross-language options

**Quick Start Options:**

- 🐍 **Python**: `cd code-samples/python/ && python 01_create_basic_index.py`
- 🔷 **C#**: `dotnet run 01_CreateBasicIndex.cs`
- 🟨 **JavaScript**: `node 01_create_basic_index.js`
- 🌐 **REST API**: Open `01_create_basic_index.http` in VS Code with REST Client
- 📓 **Interactive**: `jupyter notebook code-samples/notebooks/index_management.ipynb`

**📊 Complete Coverage Matrix:**

| Topic | Python | C# | JavaScript | REST |
|-------|--------|----|-----------|----- |
| Basic Index Creation | ✅ | ✅ | ✅ | ✅ |
| Schema Design | ✅ | ✅ | ✅ | ✅ |
| Data Ingestion | ✅ | ✅ | ✅ | ✅ |
| Index Operations | ✅ | ✅ | ✅ | ✅ |
| Performance Optimization | ✅ | ✅ | ✅ | ✅ |
| Error Handling | ✅ | ✅ | ✅ | ✅ |