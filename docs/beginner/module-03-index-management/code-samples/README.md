# Module 3: Index Management - Code Samples

This directory contains comprehensive code samples demonstrating index management operations in Azure AI Search across multiple programming languages. These samples are designed to help you understand fundamental index concepts and implement them in your preferred language.

## 📁 Directory Structure

```
code-samples/
├── README.md                    # This file
├── setup_prerequisites.py      # Environment setup and validation
├── notebooks/                  # Interactive Jupyter notebooks
│   └── index_management.ipynb  # Step-by-step interactive examples
├── python/                     # Python examples (6 files)
│   ├── 01_create_basic_index.py
│   ├── 02_schema_design.py
│   ├── 03_data_ingestion.py
│   ├── 04_index_operations.py
│   ├── 05_performance_optimization.py
│   └── 06_error_handling.py
├── csharp/                     # C# .NET examples (6 files)
│   ├── 01_CreateBasicIndex.cs
│   ├── 02_SchemaDesign.cs
│   ├── 03_DataIngestion.cs
│   ├── 04_IndexOperations.cs
│   ├── 05_PerformanceOptimization.cs
│   └── 06_ErrorHandling.cs
├── javascript/                 # JavaScript/Node.js examples (6 files)
│   ├── 01_create_basic_index.js
│   ├── 02_schema_design.js
│   ├── 03_data_ingestion.js
│   ├── 04_index_operations.js
│   ├── 05_performance_optimization.js
│   └── 06_error_handling.js
└── rest/                       # REST API examples (6 files)
    ├── 01_create_basic_index.http
    ├── 02_schema_design.http
    ├── 03_data_ingestion.http
    ├── 04_index_operations.http
    ├── 05_performance_optimization.http
    └── 06_error_handling.http
```

## 🚀 Quick Start

### Prerequisites Setup (Required First Step)

Before running any examples, set up your environment:

```bash
# 1. Set environment variables
export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-service.search.windows.net"
export AZURE_SEARCH_ADMIN_KEY="your-admin-api-key"

# 2. Install dependencies
pip install azure-search-documents python-dotenv

# 3. Run prerequisites setup
python setup_prerequisites.py
```

### Choose Your Learning Path

#### 🐍 Python Path
```bash
cd python/
python 01_create_basic_index.py
```

#### 🔷 C# Path
```bash
cd csharp/
dotnet run 01_CreateBasicIndex.cs
```

#### 🟨 JavaScript Path
```bash
cd javascript/
npm install @azure/search-documents
node 01_create_basic_index.js
```

#### 📓 Interactive Path
```bash
pip install jupyter
jupyter notebook notebooks/index_management.ipynb
```

## 📚 Code Sample Categories

### 1. Basic Index Creation
Learn the fundamentals of creating search indexes.

**What you'll learn:**
- Index schema definition
- Field types and attributes
- Basic index creation
- Index validation

**Files:**
- `01_create_basic_index.py` - Python implementation
- `01_CreateBasicIndex.cs` - C# implementation  
- `01_create_basic_index.js` - JavaScript implementation
- `01_create_basic_index.http` - REST API calls

### 2. Schema Design
Master the art of designing effective index schemas.

**What you'll learn:**
- Field type selection
- Attribute optimization
- Complex field structures
- Schema best practices

**Files:**
- `02_schema_design.py` - Python examples
- `02_SchemaDesign.cs` - C# examples
- `02_schema_design.js` - JavaScript examples
- `02_schema_design.http` - REST API examples

### 3. Data Ingestion
Implement robust data ingestion strategies.

**What you'll learn:**
- Single document upload
- Batch document upload
- Large dataset handling
- Upload optimization

**Files:**
- `03_data_ingestion.py` - Python implementation
- `03_DataIngestion.cs` - C# implementation
- `03_data_ingestion.js` - JavaScript implementation
- `03_data_ingestion.http` - REST API examples

### 4. Index Operations
Manage index lifecycle operations and maintenance.

**What you'll learn:**
- Index lifecycle operations (create, update, delete)
- Schema updates and versioning
- Document operations (update, merge, delete)
- Index health monitoring

**Files:**
- `04_index_operations.py` - Python examples
- `04_IndexOperations.cs` - C# examples
- `04_index_operations.js` - JavaScript examples
- `04_index_operations.http` - REST API examples

### 5. Performance Optimization
Optimize index performance and resource usage.

**What you'll learn:**
- Batch size optimization
- Parallel upload strategies
- Memory management
- Performance monitoring and best practices

**Files:**
- `05_performance_optimization.py` - Python examples
- `05_PerformanceOptimization.cs` - C# examples
- `05_performance_optimization.js` - JavaScript examples
- `05_performance_optimization.http` - REST API examples

### 6. Error Handling
Implement robust error handling and troubleshooting.

**What you'll learn:**
- Common error scenarios
- Retry strategies with exponential backoff
- Input validation and edge cases
- Comprehensive troubleshooting techniques

**Files:**
- `06_error_handling.py` - Python implementation
- `06_ErrorHandling.cs` - C# implementation
- `06_error_handling.js` - JavaScript implementation
- `06_error_handling.http` - REST API examples

## 🎯 Learning Approaches

### 1. Sequential Learning (Recommended for Beginners)
Follow the numbered sequence for a structured learning experience:

```bash
# Python example
python 01_create_basic_index.py
python 02_schema_design.py
python 03_data_ingestion.py
python 04_index_operations.py
python 05_performance_optimization.py
python 06_error_handling.py
```

### 2. Topic-Focused Learning
Jump to specific topics based on your needs:

```bash
# Focus on data ingestion
python 03_data_ingestion.py

# Focus on performance
python 05_performance_optimization.py

# Focus on error handling
python 06_error_handling.py
```

### 3. Cross-Language Learning
Compare implementations across languages:

```bash
# Compare Python and C# approaches
python python/01_create_basic_index.py
dotnet run csharp/01_CreateBasicIndex.cs
```

### 4. Interactive Learning
Use Jupyter notebooks for hands-on experimentation:

```bash
jupyter notebook notebooks/index_management.ipynb
```

## 🔧 Environment Setup

### Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install azure-search-documents python-dotenv pandas jupyter
```

### C# Environment
```bash
# Create new console project
dotnet new console -n IndexManagementSamples
cd IndexManagementSamples

# Add Azure Search package
dotnet add package Azure.Search.Documents
```

### JavaScript Environment
```bash
# Initialize npm project
npm init -y

# Install dependencies
npm install @azure/search-documents dotenv
```

### Environment Variables
Create a `.env` file in your project root:

```bash
# .env
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_ADMIN_KEY=your-admin-api-key
AZURE_SEARCH_INDEX_NAME=handbook-indexes
```

## 📊 Sample Data

The code samples use consistent sample data across all languages:

```json
{
  "id": "1",
  "title": "Getting Started with Azure AI Search",
  "content": "Azure AI Search is a powerful search service...",
  "author": "John Doe",
  "publishedDate": "2024-01-15T10:00:00Z",
  "category": "Tutorial",
  "tags": ["azure", "search", "tutorial"],
  "rating": 4.5,
  "viewCount": 1250,
  "isPublished": true
}
```

## 🚨 Common Issues and Solutions

### Issue 1: "Access Denied" Error
**Problem**: Getting 403 errors when creating indexes.
**Solution**: Ensure you're using an admin API key, not a query key.

```python
# ✅ Correct: Admin key for index operations
index_client = SearchIndexClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(admin_key)  # Admin key required
)
```

### Issue 2: "Index Already Exists" Error
**Problem**: Trying to create an index that already exists.
**Solution**: Use `create_or_update_index()` instead of `create_index()`.

```python
# ✅ Safe: Will create or update
result = index_client.create_or_update_index(index)
```

### Issue 3: Package Import Errors
**Problem**: Cannot import Azure Search modules.
**Solution**: Install the correct package version.

```bash
pip install azure-search-documents==11.4.0
```

### Issue 4: Connection Timeout
**Problem**: Operations timing out.
**Solution**: Increase timeout and implement retry logic.

```python
from azure.core.pipeline.policies import RetryPolicy

# Configure retry policy
retry_policy = RetryPolicy(retry_total=3, retry_backoff_factor=1.0)
```

## 🎓 Best Practices Demonstrated

### Code Quality
- ✅ Comprehensive error handling
- ✅ Input validation and sanitization
- ✅ Proper resource cleanup
- ✅ Consistent logging and monitoring

### Performance
- ✅ Optimal batch sizes for uploads
- ✅ Parallel processing strategies
- ✅ Memory-efficient data handling
- ✅ Connection pooling and reuse

### Security
- ✅ Environment variable usage
- ✅ API key management
- ✅ Input sanitization
- ✅ Secure connection practices

### Maintainability
- ✅ Clear code structure and comments
- ✅ Modular function design
- ✅ Configuration externalization
- ✅ Comprehensive documentation

## 🔗 Related Resources

### Module 3 Resources
- **[Module 3 Documentation](../documentation.md)** - Core concepts and theory
- **[Prerequisites Setup](../prerequisites.md)** - Environment configuration
- **[Best Practices](../best-practices.md)** - Guidelines and recommendations

### Azure AI Search Resources
- **[Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)**
- **[Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-search-documents/)**
- **[REST API Reference](https://docs.microsoft.com/en-us/rest/api/searchservice/)**

## 🚀 Next Steps

After working through the code samples:

1. **✅ Master the Basics**: Complete samples 01-04
2. **🔧 Explore Advanced Features**: Try samples 05-08
3. **📝 Practice with Exercises**: Apply concepts in guided scenarios
4. **🏗️ Build Your Own**: Create indexes for your own data
5. **📚 Continue Learning**: Move to Module 4: Simple Queries and Filters

---

**Ready to start building indexes?** 🏗️✨

Begin with the prerequisites setup and choose your preferred learning path!