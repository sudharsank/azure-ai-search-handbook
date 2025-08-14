# Best Practices - Filters & Sorting

## Overview

This guide provides best practices for implementing effective filters and sorting in Azure AI Search. Following these guidelines will help you create performant, maintainable, and user-friendly search experiences.

## Filter Best Practices

### 1. Index Schema Design

#### Mark Fields as Filterable
```json
{
  "name": "category",
  "type": "Edm.String",
  "filterable": true,
  "facetable": true
}
```

**Guidelines:**
- Only mark fields as `filterable` if you plan to filter on them
- Filterable fields consume additional storage space
- Consider the trade-off between functionality and storage costs

#### Choose Appropriate Data Types
```json
{
  "name": "price",
  "type": "Edm.Double",  // ✅ Good for numeric filtering
  "filterable": true,
  "sortable": true
}
```

**Guidelines:**
- Use `Edm.Double` for decimal numbers (prices, ratings)
- Use `Edm.Int32` or `Edm.Int64` for whole numbers
- Use `Edm.DateTimeOffset` for dates and times
- Use `Edm.Boolean` for true/false values

### 2. Filter Construction

#### Use Most Selective Filters First
```odata
✅ Good: category eq 'Electronics' and price gt 1000
❌ Avoid: price gt 0 and category eq 'Electronics'
```

**Rationale:**
- More selective filters reduce the result set faster
- Improves query performance
- Reduces resource consumption

#### Handle Null Values Explicitly
```odata
✅ Good: rating ne null and rating ge 4.0
❌ Risky: rating ge 4.0
```

**Guidelines:**
- Always check for null values when filtering
- Use `ne null` to exclude null values
- Use `eq null` to find missing values

#### Use Appropriate Operators
```odata
✅ Inclusive range: price ge 100 and price le 200
✅ Exclusive range: price gt 100 and price lt 200
✅ Open-ended: price ge 100
```

### 3. Logical Combinations

#### Use Parentheses for Complex Logic
```odata
✅ Clear: (category eq 'Electronics' and price gt 100) or (category eq 'Books' and rating ge 4.5)
❌ Ambiguous: category eq 'Electronics' and price gt 100 or category eq 'Books' and rating ge 4.5
```

#### Optimize Boolean Logic
```odata
✅ Efficient: category eq 'Electronics' and (price gt 100 or rating ge 4.0)
❌ Inefficient: (category eq 'Electronics' and price gt 100) or (category eq 'Electronics' and rating ge 4.0)
```

### 4. String Filtering

#### Use Appropriate String Functions
```odata
✅ Prefix search: startswith(name, 'iPhone')
✅ Suffix search: endswith(name, 'Pro')
✅ Contains search: contains(description, 'wireless')
```

#### Consider Case Sensitivity
```odata
✅ Case-insensitive: tolower(name) eq 'iphone'
✅ Exact match: name eq 'iPhone'
```

### 5. Collection Filtering

#### Use any() for OR Logic
```odata
✅ Has WiFi: amenities/any(a: a eq 'WiFi')
✅ Has WiFi or Pool: amenities/any(a: a eq 'WiFi' or a eq 'Pool')
```

#### Use all() for AND Logic
```odata
✅ All amenities available: amenities/all(a: a ne null)
✅ Multiple requirements: amenities/all(a: a eq 'WiFi') and amenities/all(a: a eq 'Pool')
```

## Sorting Best Practices

### 1. Index Schema for Sorting

#### Mark Fields as Sortable
```json
{
  "name": "rating",
  "type": "Edm.Double",
  "sortable": true,
  "filterable": true
}
```

**Guidelines:**
- Only mark fields as `sortable` if needed for sorting
- Sortable fields consume additional storage
- Numeric and date fields are most efficient for sorting

### 2. Sort Order Design

#### Use Meaningful Default Sorting
```javascript
// ✅ Good default: relevance for search, rating for browse
const orderBy = searchText === "*" ? ["rating desc"] : null;
```

#### Provide Multiple Sort Options
```javascript
const sortOptions = [
  { label: "Relevance", value: null },
  { label: "Price: Low to High", value: ["price asc"] },
  { label: "Price: High to Low", value: ["price desc"] },
  { label: "Rating", value: ["rating desc"] },
  { label: "Newest", value: ["createdDate desc"] }
];
```

### 3. Multi-field Sorting

#### Order Fields by Importance
```odata
✅ Good: category asc, rating desc, price asc
❌ Poor: price asc, category asc, rating desc
```

#### Limit Sort Fields
```javascript
// ✅ Good: 2-3 sort fields maximum
orderBy: ["category asc", "rating desc", "name asc"]

// ❌ Avoid: Too many sort fields
orderBy: ["category asc", "rating desc", "price asc", "createdDate desc", "name asc"]
```

### 4. Geographic Sorting

#### Use Efficient Distance Calculations
```odata
✅ Good: geo.distance(location, geography'POINT(-122.131577 47.678581)')
```

#### Combine with Other Sorting
```odata
✅ Good: geo.distance(location, geography'POINT(-122.131577 47.678581)'), rating desc
```

## Performance Optimization

### 1. Query Optimization

#### Use Selective Filters
```javascript
// ✅ Good: Specific category filter
filter: "category eq 'Electronics' and inStock eq true"

// ❌ Avoid: Non-selective filters
filter: "price gt 0"
```

#### Combine Filters Efficiently
```javascript
// ✅ Good: Single filter expression
filter: "category eq 'Electronics' and price ge 100 and price le 500"

// ❌ Avoid: Multiple separate queries
```

### 2. Result Set Management

#### Use Appropriate Page Sizes
```javascript
// ✅ Good: Reasonable page size
const results = await searchClient.search("*", {
  filter: filter,
  top: 20,  // Good for most UIs
  skip: page * 20
});
```

#### Limit Selected Fields
```javascript
// ✅ Good: Only select needed fields
select: ["id", "name", "price", "rating", "imageUrl"]

// ❌ Avoid: Selecting all fields unnecessarily
```

### 3. Caching Strategies

#### Cache Common Filter Results
```javascript
// ✅ Good: Cache popular categories
const cacheKey = `category_${category}_page_${page}`;
let results = cache.get(cacheKey);

if (!results) {
  results = await searchClient.search("*", { filter, top, skip });
  cache.set(cacheKey, results, 300); // 5 minutes
}
```

#### Cache Facet Values
```javascript
// ✅ Good: Cache facet data
const facetCacheKey = "product_facets";
let facets = cache.get(facetCacheKey);

if (!facets) {
  const facetResults = await searchClient.search("*", {
    facets: ["category", "brand", "priceRange"]
  });
  facets = facetResults.facets;
  cache.set(facetCacheKey, facets, 3600); // 1 hour
}
```

## User Experience Best Practices

### 1. Filter UI Design

#### Provide Clear Filter Options
```javascript
// ✅ Good: Clear filter labels and values
const filterOptions = {
  category: {
    label: "Category",
    options: [
      { label: "Electronics", value: "Electronics", count: 150 },
      { label: "Books", value: "Books", count: 89 },
      { label: "Clothing", value: "Clothing", count: 234 }
    ]
  }
};
```

#### Show Filter State
```javascript
// ✅ Good: Show active filters
const activeFilters = [
  { type: "category", value: "Electronics", label: "Category: Electronics" },
  { type: "price", value: "100-500", label: "Price: $100 - $500" }
];
```

### 2. Progressive Filtering

#### Start with Broad Categories
```javascript
// ✅ Good: Progressive refinement
const filterHierarchy = [
  "category",      // Broad categorization
  "brand",         // Brand within category
  "priceRange",    // Price refinement
  "features"       // Specific features
];
```

#### Update Facets Dynamically
```javascript
// ✅ Good: Update available options based on current filters
async function updateFacets(currentFilters) {
  const results = await searchClient.search("*", {
    filter: buildFilterExpression(currentFilters),
    facets: ["brand", "priceRange", "rating"],
    top: 0  // Only get facets, not results
  });
  
  return results.facets;
}
```

### 3. Sort UI Design

#### Provide Intuitive Sort Options
```javascript
// ✅ Good: User-friendly sort labels
const sortOptions = [
  { label: "Best Match", value: null },
  { label: "Price: Low to High", value: ["price asc"] },
  { label: "Price: High to Low", value: ["price desc"] },
  { label: "Customer Rating", value: ["rating desc"] },
  { label: "Newest First", value: ["createdDate desc"] }
];
```

#### Remember User Preferences
```javascript
// ✅ Good: Persist sort preferences
localStorage.setItem('preferredSort', JSON.stringify(selectedSort));
```

## Error Handling

### 1. Filter Validation

#### Validate Filter Syntax
```javascript
function validateFilter(filterExpression) {
  try {
    // Check for balanced quotes
    const singleQuotes = (filterExpression.match(/'/g) || []).length;
    if (singleQuotes % 2 !== 0) {
      return { valid: false, error: "Unbalanced quotes" };
    }
    
    // Check for balanced parentheses
    const openParens = (filterExpression.match(/\(/g) || []).length;
    const closeParens = (filterExpression.match(/\)/g) || []).length;
    if (openParens !== closeParens) {
      return { valid: false, error: "Unbalanced parentheses" };
    }
    
    return { valid: true };
  } catch (error) {
    return { valid: false, error: error.message };
  }
}
```

#### Handle Invalid Filters Gracefully
```javascript
// ✅ Good: Graceful error handling
try {
  const results = await searchClient.search("*", { filter });
  return results;
} catch (error) {
  if (error.message.includes("Invalid filter")) {
    // Log error and return results without filter
    console.warn("Invalid filter, falling back to unfiltered results", error);
    return await searchClient.search("*");
  }
  throw error;
}
```

### 2. Performance Monitoring

#### Monitor Query Performance
```javascript
// ✅ Good: Track query performance
async function monitoredSearch(searchOptions) {
  const startTime = Date.now();
  
  try {
    const results = await searchClient.search("*", searchOptions);
    const duration = Date.now() - startTime;
    
    // Log slow queries
    if (duration > 1000) {
      console.warn(`Slow query detected: ${duration}ms`, searchOptions);
    }
    
    return results;
  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`Query failed after ${duration}ms`, error);
    throw error;
  }
}
```

## Security Considerations

### 1. Input Sanitization

#### Sanitize User Input
```javascript
// ✅ Good: Sanitize filter values
function sanitizeFilterValue(value) {
  if (typeof value === 'string') {
    // Escape single quotes
    return value.replace(/'/g, "''");
  }
  return value;
}
```

#### Validate Filter Fields
```javascript
// ✅ Good: Whitelist allowed filter fields
const allowedFilterFields = ['category', 'price', 'rating', 'inStock'];

function validateFilterField(fieldName) {
  return allowedFilterFields.includes(fieldName);
}
```

### 2. Access Control

#### Implement Row-Level Security
```javascript
// ✅ Good: Add user-specific filters
function addSecurityFilter(baseFilter, userId, userRole) {
  const securityFilters = [];
  
  if (userRole !== 'admin') {
    securityFilters.push("isPublic eq true");
  }
  
  if (userId) {
    securityFilters.push(`ownerId eq '${userId}' or isPublic eq true`);
  }
  
  const securityFilter = securityFilters.join(' and ');
  
  return baseFilter 
    ? `(${baseFilter}) and (${securityFilter})`
    : securityFilter;
}
```

## Testing Strategies

### 1. Unit Testing

#### Test Filter Building Logic
```javascript
// ✅ Good: Test filter construction
describe('Filter Building', () => {
  test('should build category filter', () => {
    const filter = buildFilter({ category: 'Electronics' });
    expect(filter).toBe("category eq 'Electronics'");
  });
  
  test('should handle multiple filters', () => {
    const filter = buildFilter({ 
      category: 'Electronics', 
      minPrice: 100 
    });
    expect(filter).toBe("category eq 'Electronics' and price ge 100");
  });
});
```

### 2. Integration Testing

#### Test End-to-End Scenarios
```javascript
// ✅ Good: Test complete filter workflows
describe('Filter Integration', () => {
  test('should filter and sort products', async () => {
    const results = await searchClient.search("*", {
      filter: "category eq 'Electronics' and price gt 100",
      orderBy: ["rating desc"],
      top: 10
    });
    
    expect(results).toBeDefined();
    // Verify results match filter criteria
  });
});
```

## Monitoring and Analytics

### 1. Query Analytics

#### Track Filter Usage
```javascript
// ✅ Good: Track popular filters
function trackFilterUsage(filterExpression) {
  analytics.track('filter_applied', {
    filter: filterExpression,
    timestamp: new Date().toISOString()
  });
}
```

#### Monitor Performance Metrics
```javascript
// ✅ Good: Track query performance
function trackQueryPerformance(duration, resultCount, filters) {
  analytics.track('query_performance', {
    duration,
    resultCount,
    filterCount: filters ? filters.split(' and ').length : 0
  });
}
```

### 2. User Behavior Analysis

#### Track Sort Preferences
```javascript
// ✅ Good: Understand user preferences
function trackSortUsage(sortOption) {
  analytics.track('sort_applied', {
    sortOption,
    timestamp: new Date().toISOString()
  });
}
```

By following these best practices, you'll create efficient, user-friendly, and maintainable filter and sorting implementations in Azure AI Search.