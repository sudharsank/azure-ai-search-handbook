# Code Samples - Module 6: Filters & Sorting

## Overview

This directory contains comprehensive code samples demonstrating how to implement filters and sorting in Azure AI Search. The examples cover various filter types, sorting strategies, and optimization techniques across multiple programming languages.

## Sample Categories

### 1. Basic Filters
- Equality filters (`eq`, `ne`)
- Comparison filters (`gt`, `ge`, `lt`, `le`)
- Boolean logic combinations
- Null value handling

### 2. Range Filters
- Numeric range filtering
- Date range filtering
- Price range implementations
- Performance optimization techniques

### 3. String Filters
- Text matching with `startswith`, `endswith`, `contains`
- Case sensitivity handling
- Pattern matching techniques
- Multi-language considerations

### 4. Date Filters
- Date range filtering
- Relative date calculations
- Time zone handling
- Date format considerations

### 5. Geographic Filters
- Distance-based filtering
- Bounding box filtering
- Location proximity searches
- Geographic sorting by distance

### 6. Sorting Operations
- Single field sorting
- Multi-field sorting
- Custom sort orders
- Performance optimization

### 7. Complex Filters
- Collection filtering with `any()` and `all()`
- Nested field filtering
- Combined filter and search queries
- Advanced logical expressions

### 8. Performance Tips
- Filter optimization strategies
- Index design considerations
- Query performance monitoring
- Caching strategies

## Programming Languages

Each sample category is implemented in multiple programming languages:

- **Python** - Using azure-search-documents SDK
- **C#** - Using Azure.Search.Documents SDK
- **JavaScript/Node.js** - Using @azure/search-documents SDK
- **REST API** - Direct HTTP calls with examples

## Sample Structure

Each programming language directory contains:

```
language/
├── README.md                    # Language-specific setup and overview
├── 01_basic_filters.*          # Basic filter implementations
├── 02_range_filters.*          # Range filtering examples
├── 03_string_filters.*         # String filtering techniques
├── 04_date_filters.*           # Date and time filtering
├── 05_geographic_filters.*     # Location-based filtering
├── 06_sorting_operations.*     # Sorting implementations
├── 07_complex_filters.*        # Advanced filtering scenarios
└── 08_performance_tips.*       # Optimization techniques
```

## Prerequisites

Before running these samples, ensure you have:

### Azure Resources
- Azure AI Search service
- Search index with filterable and sortable fields
- Sample data for testing

### Development Environment
- Programming language runtime
- Required SDKs and packages installed
- Code editor or IDE
- REST client (for REST API examples)

### Index Configuration
Your search index should have fields configured with appropriate attributes:
- `filterable: true` for fields used in filters
- `sortable: true` for fields used in sorting
- `facetable: true` for fields used in faceted navigation

## Quick Start

### 1. Choose Your Language
Navigate to the appropriate language directory:
- [Python Examples](./python/README.md)
- [C# Examples](./csharp/README.md)
- [JavaScript Examples](./javascript/README.md)
- [REST API Examples](./rest/README.md)

### 2. Set Up Environment
Follow the language-specific setup instructions in each directory's README.

### 3. Configure Connections
Update configuration files with your Azure AI Search service details.

### 4. Run Samples
Start with basic examples and progress to more complex scenarios.

## Sample Scenarios

### Scenario 1: E-commerce Product Filtering
**Files:** `01_basic_filters.*`, `02_range_filters.*`, `06_sorting_operations.*`

Implement product catalog filtering:
- Filter by category, brand, price range
- Sort by price, rating, popularity
- Handle multiple filter combinations
- Optimize for performance

### Scenario 2: Hotel Search with Location
**Files:** `05_geographic_filters.*`, `04_date_filters.*`, `07_complex_filters.*`

Build location-based hotel search:
- Filter by distance from location
- Date range availability filtering
- Amenity filtering with collections
- Sort by distance and rating

### Scenario 3: Document Search with Metadata
**Files:** `03_string_filters.*`, `04_date_filters.*`, `08_performance_tips.*`

Search documents with metadata filtering:
- Filter by document type, author, tags
- Date range filtering for creation/modification
- Text content filtering
- Performance optimization

## Filter Syntax Examples

### Basic Equality Filters
```odata
category eq 'Electronics'
status ne 'Discontinued'
inStock eq true
```

### Range Filters
```odata
price gt 100 and price lt 500
rating ge 4.0
lastModified gt 2024-01-01T00:00:00Z
```

### String Filters
```odata
startswith(name, 'iPhone')
contains(description, 'wireless')
endswith(model, 'Pro')
```

### Geographic Filters
```odata
geo.distance(location, geography'POINT(-122.131577 47.678581)') lt 10
```

### Collection Filters
```odata
tags/any(t: t eq 'featured')
amenities/all(a: a ne null)
```

### Complex Combinations
```odata
(category eq 'Hotels' and rating gt 4.0) or (category eq 'Resorts' and price lt 300)
```

## Sorting Examples

### Basic Sorting
```odata
$orderby=rating desc
$orderby=price asc
$orderby=name
```

### Multi-field Sorting
```odata
$orderby=category asc, rating desc, price asc
```

### Geographic Sorting
```odata
$orderby=geo.distance(location, geography'POINT(-122.131577 47.678581)')
```

## Configuration Templates

### Environment Variables
```bash
# Azure AI Search
SEARCH_SERVICE_NAME=your-search-service
SEARCH_API_KEY=your-api-key
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
INDEX_NAME=your-index-name
```

### Sample Index Schema
```json
{
  "name": "products",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "name", "type": "Edm.String", "searchable": true, "filterable": true, "sortable": true},
    {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "price", "type": "Edm.Double", "filterable": true, "sortable": true, "facetable": true},
    {"name": "rating", "type": "Edm.Double", "filterable": true, "sortable": true},
    {"name": "inStock", "type": "Edm.Boolean", "filterable": true},
    {"name": "lastModified", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
    {"name": "location", "type": "Edm.GeographyPoint", "filterable": true, "sortable": true},
    {"name": "tags", "type": "Collection(Edm.String)", "filterable": true, "facetable": true}
  ]
}
```

## Best Practices Demonstrated

### Performance Optimization
- Efficient filter construction
- Proper field attribute usage
- Query optimization techniques
- Result set size management

### User Experience
- Progressive filtering
- Faceted navigation
- Sort option presentation
- Filter state management

### Error Handling
- Invalid filter syntax handling
- Data type validation
- Graceful degradation
- User feedback mechanisms

## Testing and Validation

### Unit Tests
Each language directory includes tests for:
- Filter syntax validation
- Sort parameter handling
- Error condition testing
- Performance benchmarking

### Integration Tests
End-to-end tests covering:
- Complete filtering workflows
- Multi-criteria scenarios
- Performance validation
- User experience flows

### Sample Data Sets
Test data includes:
- Various data types and ranges
- Edge cases and null values
- Geographic coordinates
- Collection fields

## Performance Considerations

### Filter Optimization
- Use most selective filters first
- Combine filters efficiently
- Avoid complex nested expressions
- Monitor query performance

### Sorting Optimization
- Use appropriate field types
- Consider storage implications
- Implement caching strategies
- Monitor resource usage

### Index Design
- Mark only necessary fields as filterable/sortable
- Consider field storage requirements
- Optimize for common query patterns
- Balance functionality vs. performance

## Troubleshooting

### Common Issues
- Field not filterable/sortable errors
- Invalid OData syntax
- Data type mismatches
- Performance problems

### Debugging Tools
- Query syntax validation
- Performance profiling
- Error message interpretation
- Index analysis tools

## Interactive Notebooks

The [notebooks](./notebooks/README.md) directory contains Jupyter notebooks with:
- Interactive filter building
- Visual query results
- Performance analysis
- Experimentation environments

## Additional Resources

### Module Documentation
- **[Main Documentation](../documentation.md)** - Complete module overview
- **[Prerequisites](../prerequisites.md)** - Required setup and knowledge
- **[Best Practices](../best-practices.md)** - Guidelines for effective implementation
- **[Practice & Implementation](../practice-implementation.md)** - Hands-on exercises
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

### External Resources
- **[OData Filter Syntax Reference](https://learn.microsoft.com/en-us/azure/search/search-query-odata-filter)**
- **[OData OrderBy Syntax Reference](https://learn.microsoft.com/en-us/azure/search/search-query-odata-orderby)**
- **[Geographic Functions](https://learn.microsoft.com/en-us/azure/search/search-query-odata-geo-spatial-functions)**
- **[Collection Operators](https://learn.microsoft.com/en-us/azure/search/search-query-odata-collection-operators)**
- **[Search Functions](https://learn.microsoft.com/en-us/azure/search/search-query-odata-full-text-search-functions)**

### When You Need Help
- **Syntax Issues**: Check the [Troubleshooting Guide](../troubleshooting.md)
- **Performance Problems**: Review [Performance Analysis Examples](python/08_performance_analysis.py)
- **Complex Scenarios**: Explore [Complex Filter Examples](python/07_complex_filters.py)

## Next Steps

After exploring these samples:
1. Implement similar patterns in your projects
2. Customize for your specific data and requirements
3. Explore advanced features in intermediate modules
4. Share your experiences with the community

## Feedback and Support

For questions, issues, or suggestions:
- Review the troubleshooting guides
- Check the Azure AI Search documentation
- Engage with the community forums
- Submit feedback through appropriate channels