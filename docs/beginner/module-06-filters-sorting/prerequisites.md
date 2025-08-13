# Prerequisites - Module 6: Filters & Sorting

## Required Knowledge

Before starting this module, you should have:

### Azure AI Search Fundamentals
- ✅ Completed Module 1: Introduction & Setup
- ✅ Completed Module 2: Basic Search
- ✅ Completed Module 4: Simple Queries
- ✅ Understanding of search index field attributes
- ✅ Basic knowledge of query syntax and parameters

### Technical Prerequisites
- ✅ Understanding of comparison operators (equals, greater than, less than)
- ✅ Basic knowledge of logical operators (AND, OR, NOT)
- ✅ Familiarity with data types (strings, numbers, dates, booleans)
- ✅ Understanding of JSON data structures

## Required Azure Resources

### Azure AI Search Service
- ✅ Active Azure AI Search service (Free tier is sufficient for learning)
- ✅ Admin API key or appropriate RBAC permissions
- ✅ Service endpoint URL

### Search Index with Filterable Fields
You'll need a search index with fields configured as filterable and sortable:

#### Required Field Attributes
- ✅ `filterable: true` - For fields used in filter expressions
- ✅ `sortable: true` - For fields used in sorting
- ✅ `facetable: true` - For fields used in faceted navigation (optional)

#### Sample Index Schema
```json
{
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "title", "type": "Edm.String", "searchable": true},
    {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "price", "type": "Edm.Double", "filterable": true, "sortable": true},
    {"name": "rating", "type": "Edm.Double", "filterable": true, "sortable": true},
    {"name": "lastModified", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
    {"name": "location", "type": "Edm.GeographyPoint", "filterable": true, "sortable": true},
    {"name": "tags", "type": "Collection(Edm.String)", "filterable": true, "facetable": true}
  ]
}
```

### Sample Data
Your index should contain sample documents for testing:

```json
[
  {
    "id": "1",
    "title": "Luxury Hotel Downtown",
    "category": "Luxury",
    "price": 299.99,
    "rating": 4.8,
    "lastModified": "2024-01-15T10:30:00Z",
    "location": {"type": "Point", "coordinates": [-122.131577, 47.678581]},
    "tags": ["WiFi", "Pool", "Spa", "Restaurant"]
  },
  {
    "id": "2",
    "title": "Budget Inn Airport",
    "category": "Budget",
    "price": 89.99,
    "rating": 3.2,
    "lastModified": "2024-01-10T14:20:00Z",
    "location": {"type": "Point", "coordinates": [-122.309326, 47.449397]},
    "tags": ["WiFi", "Parking"]
  }
]
```

## Development Environment Setup

### Required Tools
- ✅ Code editor (Visual Studio Code recommended)
- ✅ REST client (Postman, VS Code REST Client, or curl)
- ✅ Web browser for Azure portal access

### SDK Installation (Choose your language)

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

## OData Knowledge Requirements

### Basic OData Concepts
- ✅ Understanding of OData filter syntax
- ✅ Knowledge of comparison operators (`eq`, `ne`, `gt`, `ge`, `lt`, `le`)
- ✅ Familiarity with logical operators (`and`, `or`, `not`)
- ✅ Basic string functions (`startswith`, `endswith`, `contains`)

### Data Type Handling
- ✅ String literals: `'text value'`
- ✅ Numeric values: `123`, `45.67`
- ✅ Boolean values: `true`, `false`
- ✅ Date/time values: `2024-01-15T10:30:00Z`
- ✅ Null values: `null`

## Authentication Setup

### Option 1: API Keys
- ✅ Admin API key for write operations
- ✅ Query API key for read operations

### Option 2: Managed Identity (Recommended for production)
- ✅ System-assigned or user-assigned managed identity
- ✅ Appropriate role assignments:
  - Search Service Contributor (for admin operations)
  - Search Index Data Reader (for query operations)

## Verification Checklist

Before proceeding with the module exercises:

### Service Access
- [ ] Can access Azure AI Search service endpoint
- [ ] Can authenticate using API keys or managed identity
- [ ] Can execute basic search queries

### Index Configuration
- [ ] Index exists with sample data
- [ ] Required fields are marked as filterable
- [ ] Required fields are marked as sortable
- [ ] Sample data includes various data types

### Development Environment
- [ ] Required SDKs or tools are installed
- [ ] Can make REST API calls to Azure AI Search
- [ ] Code editor is configured appropriately

### OData Knowledge
- [ ] Understand basic filter syntax
- [ ] Can construct simple comparison expressions
- [ ] Familiar with logical operators
- [ ] Know how to handle different data types

## Sample Test Queries

Verify your setup with these basic filter and sort queries:

### Basic Equality Filter
```http
GET https://[service-name].search.windows.net/indexes/[index-name]/docs?api-version=2024-07-01&search=*&$filter=category eq 'Luxury'
```

### Range Filter
```http
GET https://[service-name].search.windows.net/indexes/[index-name]/docs?api-version=2024-07-01&search=*&$filter=price gt 100 and price lt 300
```

### Basic Sorting
```http
GET https://[service-name].search.windows.net/indexes/[index-name]/docs?api-version=2024-07-01&search=*&$orderby=rating desc
```

### Combined Filter and Sort
```http
GET https://[service-name].search.windows.net/indexes/[index-name]/docs?api-version=2024-07-01&search=*&$filter=rating ge 4.0&$orderby=price asc
```

## Troubleshooting Common Setup Issues

### Field Not Filterable Error
**Error**: `The field 'fieldname' is not filterable`
**Solution**: Update index schema to mark field as filterable

### Invalid OData Syntax
**Error**: `Invalid expression: ...`
**Solution**: Check OData syntax, ensure proper quoting and operators

### Data Type Mismatch
**Error**: `Cannot convert value to expected type`
**Solution**: Verify data types match between filter values and field types

### Authentication Issues
**Error**: `Access denied` or `Unauthorized`
**Solution**: Verify API keys or managed identity permissions

## Getting Help

If you encounter issues during setup:

1. Check the troubleshooting section in this module
2. Review Azure AI Search documentation
3. Verify all prerequisites are met
4. Test with simple queries before complex ones

## Next Steps

Once all prerequisites are met, proceed to:
- **Best Practices** - Learn filtering and sorting guidelines
- **Practice & Implementation** - Start building filter and sort queries
- **Code Samples** - Explore practical examples