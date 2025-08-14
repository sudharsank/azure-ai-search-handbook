# Module 6: Filters & Sorting

## Overview

Filters and sorting are essential features in Azure AI Search that allow you to refine search results and present them in meaningful order. This module covers how to implement various filtering techniques, sorting strategies, and combine them effectively with search queries to create powerful search experiences.

## Learning Objectives

By the end of this module, you will be able to:

- Understand OData filter syntax and expressions
- Implement various filter types (equality, range, string, date, geographic)
- Apply sorting to search results using different criteria
- Combine filters with full-text search queries
- Optimize filter and sort performance
- Handle complex filtering scenarios
- Troubleshoot common filter and sorting issues

## Key Concepts

### Filters
Filters reduce the result set by applying conditions to field values. Key characteristics:
- Use OData expression syntax
- Applied before search scoring
- Support various data types and operators
- Can be combined with logical operators (and, or, not)
- Improve query performance by reducing result set size

### Sorting
Sorting determines the order of search results. Options include:
- Relevance scoring (default for search queries)
- Field-based sorting (ascending or descending)
- Multiple sort criteria
- Geographic distance sorting
- Custom scoring profiles

### Filter Types
- **Equality filters**: Exact matches (`field eq 'value'`)
- **Range filters**: Numeric and date ranges (`field gt 100`)
- **String filters**: Text-based conditions (`startswith(field, 'text')`)
- **Collection filters**: Array and complex type filtering
- **Geographic filters**: Location-based filtering (`geo.distance()`)

## Prerequisites

Before starting this module, ensure you have:
- Completed Module 1 (Introduction & Setup)
- Completed Module 2 (Basic Search)
- Completed Module 4 (Simple Queries)
- Understanding of search index field attributes
- Knowledge of basic query syntax

## Module Structure

This module is organized into the following sections:

1. **Prerequisites** - Required setup and knowledge
2. **Best Practices** - Guidelines for effective filtering and sorting
3. **Practice & Implementation** - Hands-on exercises and examples
4. **Troubleshooting** - Common issues and solutions
5. **Code Samples** - Practical examples in multiple programming languages

## What You'll Build

Throughout this module, you'll create:
- Basic and advanced filter expressions
- Multi-criteria sorting implementations
- Combined search and filter queries
- Geographic distance calculations
- Performance-optimized filter strategies

## Filter Syntax Overview

### Basic Operators
- `eq` (equals): `Category eq 'Luxury'`
- `ne` (not equals): `Rating ne 0`
- `gt` (greater than): `Price gt 100`
- `ge` (greater than or equal): `Rating ge 4.0`
- `lt` (less than): `Price lt 500`
- `le` (less than or equal): `Rating le 3.0`

### Logical Operators
- `and`: `Category eq 'Luxury' and Rating gt 4.0`
- `or`: `Category eq 'Budget' or Category eq 'Economy'`
- `not`: `not (Category eq 'Luxury')`

### String Functions
- `startswith()`: `startswith(HotelName, 'Grand')`
- `endswith()`: `endswith(HotelName, 'Hotel')`
- `contains()`: `contains(Description, 'pool')`

### Collection Functions
- `any()`: `Amenities/any(a: a eq 'WiFi')`
- `all()`: `Amenities/all(a: a ne null)`

### Search Functions
- `search.in()`: `search.in(HotelName, 'Sea View motel,Budget hotel', ',')`
- `search.ismatch()`: `search.ismatch('waterfront')`
- `search.ismatchscoring()`: `search.ismatchscoring('luxury')`

## Sorting Syntax

### Basic Sorting
- Ascending: `$orderby=Rating asc`
- Descending: `$orderby=Rating desc`
- Multiple fields: `$orderby=Rating desc, HotelName asc`

### Geographic Sorting
- Distance: `$orderby=geo.distance(Location, geography'POINT(-122.131577 47.678581)')`

## Performance Considerations

### Filterable Fields
- Mark fields as `filterable` in index schema
- Only filterable fields can be used in filter expressions
- Consider storage and performance implications

### Sortable Fields
- Mark fields as `sortable` in index schema
- Sortable fields consume additional storage
- Numeric and date fields are most efficient for sorting

### Query Optimization
- Use filters to reduce result set size
- Apply most selective filters first
- Consider using facets for common filter values
- Cache frequently used filter combinations

## Module Resources

### 📚 Additional Documentation
- **[Prerequisites](prerequisites.md)** - Required setup and knowledge
- **[Best Practices](best-practices.md)** - Guidelines for effective filtering and sorting
- **[Practice & Implementation](practice-implementation.md)** - Hands-on exercises and examples
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Code Samples](code-samples/README.md)** - Comprehensive examples in multiple languages

### 🔧 When You Need Help
- **Common Issues**: Check the [Troubleshooting Guide](troubleshooting.md)
- **Performance Problems**: Review [Performance Analysis Examples](code-samples/python/08_performance_analysis.py)
- **Syntax Errors**: Validate against [OData Filter Reference](https://learn.microsoft.com/en-us/azure/search/search-query-odata-filter)
- **Complex Scenarios**: Explore [Complex Filter Examples](code-samples/python/07_complex_filters.py)

## Next Steps

After completing this module, you'll be ready to:
- Build sophisticated search interfaces with filtering
- Implement faceted navigation
- Move on to Module 7: Pagination & Result Shaping
- Explore advanced query features in intermediate modules

### Recommended Learning Path
1. **Complete Prerequisites**: Ensure you have the required setup
2. **Study Documentation**: Read through the concepts and examples
3. **Run Code Samples**: Try the examples in your preferred language
4. **Practice Implementation**: Work through the hands-on exercises
5. **Apply Best Practices**: Implement optimized filtering in your projects
6. **Troubleshoot Issues**: Use the troubleshooting guide when needed

## Advanced Examples

### Using search.in() Function
The `search.in()` function is useful for matching against multiple values:

```odata
# Find hotels with specific names
search.in(HotelName, 'Sea View motel,Budget hotel', ',')

# Find hotels with multiple categories
search.in(Category, 'Luxury|Budget|Economy', '|')
```

### Complex Collection Filtering
```odata
# Hotels with WiFi amenity
Rooms/any(room: room/Tags/any(tag: tag eq 'wifi'))

# Hotels where all rooms are non-smoking
Rooms/all(room: not room/SmokingAllowed)

# Hotels with any rooms under $200
Rooms/any(room: room/BaseRate lt 200.0)
```

### Geographic Filtering Examples
```odata
# Hotels within 10km of a point
geo.distance(Location, geography'POINT(-122.131577 47.678581)') le 10

# Hotels within a polygon area
geo.intersects(Location, geography'POLYGON((-122.031577 47.578581, -122.031577 47.678581, -122.131577 47.678581, -122.031577 47.578581))')
```

### Combining Filters with Full-Text Search
```odata
# Search for "luxury" and filter by rating
search.ismatchscoring('luxury') and Rating ge 4

# Search in specific fields with filters
search.ismatchscoring('"ocean view"', 'Description,HotelName') or Rating eq 5
```

## Additional Resources

- [OData Filter Syntax Reference](https://learn.microsoft.com/en-us/azure/search/search-query-odata-filter)
- [OData OrderBy Syntax Reference](https://learn.microsoft.com/en-us/azure/search/search-query-odata-orderby)
- [Geographic Search Functions](https://learn.microsoft.com/en-us/azure/search/search-query-odata-geo-spatial-functions)
- [Collection Operators](https://learn.microsoft.com/en-us/azure/search/search-query-odata-collection-operators)
- [Search Functions](https://learn.microsoft.com/en-us/azure/search/search-query-odata-full-text-search-functions)