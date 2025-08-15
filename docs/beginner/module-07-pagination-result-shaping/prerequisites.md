# Prerequisites - Module 7: Pagination & Result Shaping

## Required Knowledge

Before starting this module, you should have:

### Completed Modules
- **Module 1**: Introduction & Setup
- **Module 2**: Basic Search Operations  
- **Module 4**: Simple Queries
- **Module 6**: Filters & Sorting (recommended)

### Technical Prerequisites
- Understanding of REST API concepts
- Basic knowledge of HTTP parameters
- Familiarity with JSON response structures
- Understanding of search result pagination concepts

### Azure AI Search Concepts
- Search index structure
- Document fields and data types
- Basic query syntax
- Search result structure and scoring

## Required Setup

### Azure Resources
- Active Azure AI Search service
- Sample data index (hotels-sample recommended)
- Valid API keys and endpoint URLs

### Development Environment
Choose one or more:
- **REST Client**: Postman, VS Code REST Client, or curl
- **JavaScript**: Node.js 16+ with Azure SDK
- **Python**: Python 3.8+ with azure-search-documents
- **C#**: .NET 6+ with Azure.Search.Documents
- **Jupyter Notebooks**: For interactive exploration

### Sample Data
This module uses the hotels-sample index. Ensure you have:
- Hotels index with at least 50 documents
- Fields: hotelId, hotelName, description, category, rating, location
- Proper field configurations for sorting and filtering

## Verification Checklist

Before proceeding, verify you can:
- [ ] Execute basic search queries
- [ ] Apply simple filters to search results
- [ ] Sort search results by different fields
- [ ] Access your Azure AI Search service programmatically
- [ ] View search results in JSON format

## Optional Enhancements

For better learning experience:
- Large dataset (1000+ documents) for pagination testing
- Multiple content types for result shaping examples
- Performance monitoring tools for optimization exercises

## Next Steps

Once prerequisites are met:
1. Review the [Best Practices](best-practices.md) guide
2. Start with [Practice & Implementation](practice-implementation.md)
3. Explore [Code Samples](code-samples/README.md) in your preferred language
4. Reference [Troubleshooting](troubleshooting.md) as needed

## Additional Resources

- [Azure AI Search REST API](https://docs.microsoft.com/rest/api/searchservice/)
- [Search Documents API](https://docs.microsoft.com/rest/api/searchservice/search-documents)
- [Pagination Best Practices](https://docs.microsoft.com/azure/search/search-pagination-page-layout)