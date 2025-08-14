# Troubleshooting Guide - Module 6: Filters & Sorting

This guide helps you diagnose and resolve common issues when working with filters and sorting in Azure AI Search.

## Common Filter Issues

### 1. Field Not Filterable Error

**Error Message:**
```
The field 'fieldName' is not filterable. Only filterable fields can be referenced in $filter expressions.
```

**Cause:** The field is not marked as `filterable: true` in the index schema.

**Solution:**
1. Update your index schema to mark the field as filterable:
```json
{
  "name": "fieldName",
  "type": "Edm.String",
  "filterable": true,
  "searchable": true
}
```

2. Rebuild or update your index with the new schema.

**Prevention:**
- Plan filterable fields during index design
- Review field attributes before creating the index
- Use the index analyzer to verify field configurations

### 2. Invalid OData Filter Syntax

**Error Message:**
```
Invalid expression: Syntax error at position X in 'filter expression'
```

**Common Syntax Issues:**

#### Missing Quotes Around String Values
```bash
# ❌ Wrong
category eq Electronics

# ✅ Correct
category eq 'Electronics'
```

#### Incorrect Operator Usage
```bash
# ❌ Wrong
price = 100

# ✅ Correct
price eq 100
```

#### Unbalanced Parentheses
```bash
# ❌ Wrong
(category eq 'Electronics' and price gt 100

# ✅ Correct
(category eq 'Electronics' and price gt 100)
```

#### Incorrect Date Format
```bash
# ❌ Wrong
lastModified gt '2024-12-25'

# ✅ Correct
lastModified gt 2024-12-25T00:00:00Z
```

**Debugging Tips:**
1. Test filter components individually
2. Use parentheses to group complex expressions
3. Validate date formats (ISO 8601)
4. Check for proper quote escaping

### 3. Collection Filter Issues

**Error Message:**
```
Invalid expression: The any/all operator requires a lambda expression
```

**Common Collection Issues:**

#### Missing Lambda Expression
```bash
# ❌ Wrong
tags/any(eq 'featured')

# ✅ Correct
tags/any(t: t eq 'featured')
```

#### Incorrect Collection Syntax
```bash
# ❌ Wrong
tags any 'featured'

# ✅ Correct
tags/any(t: t eq 'featured')
```

#### Nested Collection Operators
```bash
# ❌ Wrong (not supported)
tags/any(t: t/any(s: s eq 'value'))

# ✅ Alternative approach
tags/any(t: contains(t, 'value'))
```

### 4. Geographic Filter Problems

**Error Message:**
```
Invalid geography literal
```

**Common Geographic Issues:**

#### Incorrect Coordinate Order
```bash
# ❌ Wrong (latitude first)
geography'POINT(47.608013 -122.335167)'

# ✅ Correct (longitude first)
geography'POINT(-122.335167 47.608013)'
```

#### Invalid Coordinate Ranges
```bash
# ❌ Wrong (invalid latitude)
geography'POINT(-122.335167 95.0)'

# ✅ Correct (valid ranges: lat -90 to 90, lon -180 to 180)
geography'POINT(-122.335167 47.608013)'
```

#### Malformed Polygon
```bash
# ❌ Wrong (not closed)
geography'POLYGON((-122.5 47.4, -122.1 47.4, -122.1 47.8))'

# ✅ Correct (closed polygon)
geography'POLYGON((-122.5 47.4, -122.1 47.4, -122.1 47.8, -122.5 47.4))'
```

### 5. Data Type Mismatch Errors

**Error Message:**
```
Cannot convert value to expected type
```

**Common Type Issues:**

#### String vs Numeric Comparison
```bash
# ❌ Wrong
price eq '100'

# ✅ Correct
price eq 100
```

#### Date Format Issues
```bash
# ❌ Wrong
lastModified eq '12/25/2024'

# ✅ Correct
lastModified eq 2024-12-25T00:00:00Z
```

#### Boolean Value Format
```bash
# ❌ Wrong
inStock eq 'true'

# ✅ Correct
inStock eq true
```

## Common Sorting Issues

### 1. Field Not Sortable Error

**Error Message:**
```
The field 'fieldName' is not sortable. Only sortable fields can be referenced in $orderby expressions.
```

**Solution:**
1. Update index schema to mark field as sortable:
```json
{
  "name": "fieldName",
  "type": "Edm.Double",
  "sortable": true,
  "filterable": true
}
```

2. Rebuild the index with updated schema.

### 2. Invalid OrderBy Syntax

**Common Sorting Syntax Issues:**

#### Missing Sort Direction
```bash
# ❌ Ambiguous (defaults to asc)
$orderby=price

# ✅ Explicit
$orderby=price desc
```

#### Incorrect Field Reference
```bash
# ❌ Wrong
$orderby=Price desc

# ✅ Correct (case-sensitive)
$orderby=price desc
```

#### Invalid Multi-field Syntax
```bash
# ❌ Wrong
$orderby=category desc price asc

# ✅ Correct
$orderby=category desc, price asc
```

### 3. Geographic Sorting Issues

**Error Message:**
```
Invalid geo.distance expression in orderby
```

**Common Geographic Sorting Issues:**

#### Missing Geography Literal
```bash
# ❌ Wrong
$orderby=geo.distance(location, -122.335167 47.608013)

# ✅ Correct
$orderby=geo.distance(location, geography'POINT(-122.335167 47.608013)')
```

#### Null Location Values
```bash
# ❌ Problem: Null locations cause sorting issues

# ✅ Solution: Filter out nulls
filter=location ne null&$orderby=geo.distance(location, geography'POINT(-122.335167 47.608013)')
```

## Performance Issues

### 1. Slow Filter Performance

**Symptoms:**
- Queries taking longer than expected
- Timeouts on complex filters
- High resource usage

**Diagnostic Steps:**

#### Check Filter Selectivity
```bash
# Test individual filter components
category eq 'Electronics'  # How many results?
price gt 100              # How many results?
rating ge 4.0             # How many results?
```

#### Analyze Filter Order
```bash
# ❌ Less efficient (complex filter first)
contains(description, 'wireless') and category eq 'Electronics'

# ✅ More efficient (selective filter first)
category eq 'Electronics' and contains(description, 'wireless')
```

#### Use Performance Monitoring
```javascript
// JavaScript example
const startTime = Date.now();
const results = await searchClient.search('*', {
    filter: "category eq 'Electronics' and price gt 100"
});
const duration = Date.now() - startTime;
console.log(`Query took ${duration}ms`);
```

### 2. Complex Filter Optimization

**Issue:** Complex filters with multiple OR conditions perform poorly.

**Solution:** Use `search.in()` function:
```bash
# ❌ Slower
category eq 'Electronics' or category eq 'Computers' or category eq 'Phones'

# ✅ Faster
search.in(category, 'Electronics,Computers,Phones', ',')
```

### 3. Large Result Set Performance

**Issue:** Retrieving large result sets is slow.

**Solutions:**

#### Limit Result Size
```bash
# Use appropriate top value
top=50  # Instead of top=1000
```

#### Use Field Selection
```bash
# Only return needed fields
select=id,name,price  # Instead of returning all fields
```

#### Implement Pagination
```bash
# Page through results
skip=0&top=50   # First page
skip=50&top=50  # Second page
```

## Debugging Strategies

### 1. Systematic Filter Testing

**Step-by-Step Approach:**

1. **Test Basic Components**
```bash
# Test each filter component individually
category eq 'Electronics'
price gt 100
rating ge 4.0
```

2. **Combine Gradually**
```bash
# Add complexity step by step
category eq 'Electronics' and price gt 100
(category eq 'Electronics' and price gt 100) and rating ge 4.0
```

3. **Validate Data Types**
```bash
# Ensure correct data types
price eq 100      # Numeric
inStock eq true   # Boolean
lastModified ge 2024-12-25T00:00:00Z  # DateTime
```

### 2. Query Validation Tools

#### REST API Testing
```bash
# Use tools like Postman or curl to test queries
curl -X POST "https://[service].search.windows.net/indexes/[index]/docs/search?api-version=2024-07-01" \
  -H "Content-Type: application/json" \
  -H "api-key: [key]" \
  -d '{"search": "*", "filter": "category eq '\''Electronics'\''"}'
```

#### SDK Debugging
```python
# Python example with error handling
try:
    results = search_client.search(
        search_text="*",
        filter="category eq 'Electronics'",
        top=10
    )
    for result in results:
        print(result)
except Exception as e:
    print(f"Error: {e}")
    print(f"Filter: category eq 'Electronics'")
```

### 3. Index Analysis

#### Check Field Attributes
```bash
# GET index definition to verify field attributes
GET https://[service].search.windows.net/indexes/[index]?api-version=2024-07-01
```

#### Verify Data Types
```json
{
  "fields": [
    {
      "name": "price",
      "type": "Edm.Double",
      "filterable": true,
      "sortable": true
    }
  ]
}
```

## Error Code Reference

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid filter syntax, malformed query |
| 404 | Not Found | Index doesn't exist, invalid endpoint |
| 403 | Forbidden | Invalid API key, insufficient permissions |
| 500 | Internal Server Error | Service issues, complex query timeout |

### Specific Error Messages

#### Filter-Related Errors
- `"The field 'X' is not filterable"` → Update index schema
- `"Invalid expression: Syntax error"` → Check OData syntax
- `"Cannot convert value to expected type"` → Verify data types
- `"Invalid geography literal"` → Check coordinate format

#### Sorting-Related Errors
- `"The field 'X' is not sortable"` → Update index schema
- `"Invalid orderby expression"` → Check sorting syntax
- `"Too many orderby clauses"` → Limit to 32 sort criteria

## Best Practices for Troubleshooting

### 1. Preventive Measures

- **Plan Index Schema Carefully**
  - Mark appropriate fields as filterable/sortable
  - Choose correct data types
  - Consider performance implications

- **Validate Input Data**
  - Check data formats before indexing
  - Handle null values appropriately
  - Validate coordinate ranges for geographic data

- **Test Incrementally**
  - Start with simple filters
  - Add complexity gradually
  - Test with realistic data volumes

### 2. Monitoring and Logging

- **Log Query Performance**
  - Track response times
  - Monitor resource usage
  - Identify slow queries

- **Set Up Alerts**
  - Query timeout alerts
  - Performance degradation alerts
  - Error rate monitoring

### 3. Documentation and Standards

- **Document Filter Patterns**
  - Common filter combinations
  - Performance benchmarks
  - Known limitations

- **Establish Coding Standards**
  - Consistent filter syntax
  - Error handling patterns
  - Testing procedures

## Getting Additional Help

### Microsoft Resources
- [Azure AI Search Documentation](https://docs.microsoft.com/azure/search/)
- [OData Filter Reference](https://docs.microsoft.com/azure/search/search-query-odata-filter)
- [Troubleshooting Guide](https://docs.microsoft.com/azure/search/search-howto-troubleshoot-common-issues)

### Community Support
- [Microsoft Q&A](https://docs.microsoft.com/answers/topics/azure-search.html)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/azure-search)
- [Azure AI Search GitHub](https://github.com/Azure/azure-search-vector-samples)

### Professional Support
- Azure Support Plans
- Microsoft Professional Services
- Azure AI Search Consulting Partners

## Quick Reference Checklist

When troubleshooting filters and sorting:

- [ ] Verify field is marked as filterable/sortable
- [ ] Check OData syntax (quotes, operators, parentheses)
- [ ] Validate data types and formats
- [ ] Test filter components individually
- [ ] Check for null values
- [ ] Verify coordinate formats for geographic queries
- [ ] Monitor query performance
- [ ] Review error messages carefully
- [ ] Test with minimal data set first
- [ ] Document working solutions for future reference

This troubleshooting guide should help you quickly identify and resolve common issues with Azure AI Search filters and sorting operations.