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

## Next Steps

After completing this module, you'll be ready to:
- Build sophisticated search interfaces with filtering
- Implement faceted navigation
- Move on to Module 7: Pagination & Result Shaping
- Explore advanced query features in intermediate modules

## Additional Resources

- [OData Filter Syntax Reference](https://docs.microsoft.com/azure/search/search-query-odata-filter)
- [OData OrderBy Syntax Reference](https://docs.microsoft.com/azure/search/search-query-odata-orderby)
- [Geographic Search Functions](https://docs.microsoft.com/azure/search/search-query-odata-geo-spatial-functions)