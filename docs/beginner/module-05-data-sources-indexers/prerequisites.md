# Prerequisites - Module 5: Data Sources & Indexers

## Required Knowledge

Before starting this module, you should have:

### Azure AI Search Fundamentals
- ✅ Completed Module 1: Introduction & Setup
- ✅ Completed Module 3: Index Management
- ✅ Understanding of search indexes and their structure
- ✅ Basic knowledge of Azure AI Search REST APIs or SDKs

### Azure Services Knowledge
- ✅ Basic understanding of Azure resource management
- ✅ Familiarity with at least one of the following:
  - Azure SQL Database
  - Azure Blob Storage
  - Azure Cosmos DB
  - Azure Table Storage

### Technical Prerequisites
- ✅ Programming experience in at least one language (Python, C#, JavaScript, or REST APIs)
- ✅ Understanding of JSON data format
- ✅ Basic knowledge of database concepts and SQL (for SQL-based sources)

## Required Azure Resources

### Azure AI Search Service
- ✅ Active Azure AI Search service (Free tier is sufficient for learning)
- ✅ Admin API key or appropriate RBAC permissions
- ✅ Service endpoint URL

### Data Source Requirements

You'll need access to at least one of the following data sources:

#### Option 1: Azure SQL Database
- ✅ Azure SQL Database with sample data
- ✅ Database connection string
- ✅ SQL authentication or managed identity configured
- ✅ Tables with primary keys (required for indexers)

#### Option 2: Azure Blob Storage
- ✅ Azure Storage Account
- ✅ Blob container with sample documents
- ✅ Storage account connection string or managed identity
- ✅ Supported file formats (PDF, Word, Excel, JSON, etc.)

#### Option 3: Azure Cosmos DB
- ✅ Azure Cosmos DB account
- ✅ Database and container with sample data
- ✅ Connection string or managed identity configured
- ✅ Documents in JSON format

### Sample Data

If you don't have existing data, you can use these sample datasets:

#### For Azure SQL Database
```sql
-- Sample hotels table
CREATE TABLE Hotels (
    HotelId NVARCHAR(50) PRIMARY KEY,
    HotelName NVARCHAR(100),
    Description NVARCHAR(MAX),
    Category NVARCHAR(50),
    Rating FLOAT,
    Address NVARCHAR(200),
    City NVARCHAR(50),
    StateProvince NVARCHAR(50),
    PostalCode NVARCHAR(20),
    Country NVARCHAR(50)
);
```

#### For Azure Blob Storage
- Sample PDF documents
- JSON files with structured data
- Office documents (Word, Excel, PowerPoint)

#### For Azure Cosmos DB
```json
{
  "id": "1",
  "hotelName": "Sample Hotel",
  "description": "A beautiful hotel in the city center",
  "category": "Luxury",
  "rating": 4.5,
  "address": {
    "streetAddress": "123 Main St",
    "city": "Seattle",
    "stateProvince": "WA",
    "postalCode": "98101",
    "country": "USA"
  }
}
```

## Development Environment Setup

### Required Tools
- ✅ Code editor (Visual Studio Code recommended)
- ✅ REST client (Postman, VS Code REST Client, or curl)
- ✅ Azure CLI (optional but recommended)

### SDK Installation

Choose your preferred programming language:

#### Python
```bash
pip install azure-search-documents
pip install azure-identity
```

#### C# (.NET)
```bash
dotnet add package Azure.Search.Documents
dotnet add package Azure.Identity
```

#### JavaScript/Node.js
```bash
npm install @azure/search-documents
npm install @azure/identity
```

## Authentication Setup

### Option 1: API Keys (Simpler for learning)
- ✅ Admin API key from Azure portal
- ✅ Query API key (for read operations)

### Option 2: Managed Identity (Recommended for production)
- ✅ System-assigned or user-assigned managed identity
- ✅ Appropriate role assignments:
  - Search Service Contributor (for admin operations)
  - Search Index Data Contributor (for data operations)

## Network Configuration

### Firewall Settings
- ✅ Azure AI Search service accessible from your development environment
- ✅ Data source services accessible from Azure AI Search
- ✅ Appropriate firewall rules configured

### Private Endpoints (Optional)
- ✅ Private endpoint configuration if using private networking
- ✅ DNS resolution properly configured

## Verification Checklist

Before proceeding with the module exercises:

### Azure AI Search Service
- [ ] Can access Azure AI Search service endpoint
- [ ] Can authenticate using API keys or managed identity
- [ ] Can create and manage indexes

### Data Source Access
- [ ] Can connect to your chosen data source
- [ ] Sample data is available and accessible
- [ ] Appropriate permissions are configured

### Development Environment
- [ ] Required SDKs or tools are installed
- [ ] Can make REST API calls to Azure AI Search
- [ ] Code editor is configured with appropriate extensions

## Troubleshooting Common Setup Issues

### Connection Issues
- Verify firewall settings allow access between services
- Check that connection strings are correct and up-to-date
- Ensure managed identity has appropriate permissions

### Authentication Problems
- Verify API keys are valid and have correct permissions
- For managed identity, check role assignments
- Ensure service principal has necessary access rights

### Data Access Issues
- Confirm data source contains accessible data
- Verify table/container names are correct
- Check that primary keys exist for SQL-based sources

## Getting Help

If you encounter issues during setup:

1. Check the troubleshooting section in this module
2. Review Azure AI Search documentation
3. Verify all prerequisites are met
4. Test connections independently before creating indexers

## Next Steps

Once all prerequisites are met, proceed to:
- **Best Practices** - Learn indexer implementation guidelines
- **Practice & Implementation** - Start building your first indexer
- **Code Samples** - Explore practical examples