# Practice & Implementation - Filters & Sorting

## Overview

This guide provides hands-on exercises and practical implementation scenarios for mastering filters and sorting in Azure AI Search. Work through these exercises to build real-world skills and understanding.

## Prerequisites

Before starting these exercises, ensure you have:
- Completed the [Prerequisites](prerequisites.md) setup
- A working Azure AI Search service
- Sample data loaded in your index
- Basic understanding of OData filter syntax

## Exercise 1: Basic Filter Implementation

### Objective
Implement basic equality and comparison filters for an e-commerce product catalog.

### Scenario
You're building a product search for an online electronics store. Customers need to filter products by category, price range, and availability.

### Tasks

#### Task 1.1: Category Filtering
Create filters for different product categories:

```javascript
// Filter for Electronics category
const electronicsFilter = "category eq 'Electronics'";

// Filter for multiple categories
const multiCategoryFilter = "category eq 'Electronics' or category eq 'Computers'";

// Exclude discontinued products
const activeProductsFilter = "status ne 'Discontinued'";
```

**Implementation:**
```javascript
async function filterByCategory(searchClient, category) {
  const results = await searchClient.search("*", {
    filter: `category eq '${category}'`,
    select: ["id", "name", "category", "price", "rating"],
    top: 10
  });
  
  return results;
}
```

#### Task 1.2: Price Range Filtering
Implement price-based filtering:

```javascript
// Budget products under $50
const budgetFilter = "price lt 50";

// Mid-range products $50-$200
const midRangeFilter = "price ge 50 and price le 200";

// Premium products over $200
const premiumFilter = "price gt 200";
```

**Implementation:**
```javascript
function buildPriceFilter(minPrice, maxPrice) {
  const filters = [];
  
  if (minPrice !== undefined) {
    filters.push(`price ge ${minPrice}`);
  }
  
  if (maxPrice !== undefined) {
    filters.push(`price le ${maxPrice}`);
  }
  
  return filters.length > 0 ? filters.join(' and ') : null;
}
```

#### Task 1.3: Availability Filtering
Filter by stock status:

```javascript
// In-stock items only
const inStockFilter = "inStock eq true";

// Items with quantity > 0
const availableFilter = "quantityInStock gt 0";

// Combine availability with other filters
const availableElectronicsFilter = "category eq 'Electronics' and inStock eq true";
```

### Expected Outcomes
- Understand basic filter operators (eq, ne, gt, ge, lt, le)
- Learn to combine filters with logical operators
- Practice building dynamic filters from user input

## Exercise 2: Advanced Filter Combinations

### Objective
Create complex filter expressions using logical operators and nested conditions.

### Scenario
Customers want sophisticated filtering options: high-rated electronics under $500, or any books with 4+ star ratings.

### Tasks

#### Task 2.1: Complex Logical Combinations
```javascript
// High-rated electronics under $500 OR highly-rated books
const complexFilter = "(category eq 'Electronics' and rating ge 4.0 and price lt 500) or (category eq 'Books' and rating ge 4.0)";

// Products that are either premium OR highly rated
const premiumOrRatedFilter = "price gt 500 or rating ge 4.5";

// Exclude specific conditions
const excludeFilter = "not (category eq 'Discontinued' or price eq 0)";
```

#### Task 2.2: Multi-Criteria Search Builder
Create a flexible filter builder:

```javascript
class FilterBuilder {
  constructor() {
    this.filters = [];
  }
  
  addCategory(category) {
    if (category) {
      this.filters.push(`category eq '${category}'`);
    }
    return this;
  }
  
  addPriceRange(min, max) {
    if (min !== undefined) {
      this.filters.push(`price ge ${min}`);
    }
    if (max !== undefined) {
      this.filters.push(`price le ${max}`);
    }
    return this;
  }
  
  addRatingFilter(minRating) {
    if (minRating !== undefined) {
      this.filters.push(`rating ge ${minRating}`);
    }
    return this;
  }
  
  addAvailability(inStock) {
    if (inStock !== undefined) {
      this.filters.push(`inStock eq ${inStock}`);
    }
    return this;
  }
  
  build() {
    return this.filters.length > 0 ? this.filters.join(' and ') : null;
  }
}

// Usage
const filter = new FilterBuilder()
  .addCategory('Electronics')
  .addPriceRange(100, 500)
  .addRatingFilter(4.0)
  .addAvailability(true)
  .build();
```

### Expected Outcomes
- Master complex logical combinations
- Build reusable filter construction utilities
- Handle nested conditions and parentheses

## Exercise 3: Date and Time Filtering

### Objective
Implement date-based filtering for time-sensitive data.

### Scenario
Filter products by creation date, last modified date, and promotional periods.

### Tasks

#### Task 3.1: Date Range Filtering
```javascript
// Products added in the last 30 days
const last30Days = new Date();
last30Days.setDate(last30Days.getDate() - 30);
const recentFilter = `createdDate ge ${last30Days.toISOString()}`;

// Products modified this year
const thisYear = new Date(new Date().getFullYear(), 0, 1);
const thisYearFilter = `lastModified ge ${thisYear.toISOString()}`;

// Products in a specific date range
const startDate = '2024-01-01T00:00:00Z';
const endDate = '2024-12-31T23:59:59Z';
const dateRangeFilter = `createdDate ge ${startDate} and createdDate le ${endDate}`;
```

#### Task 3.2: Relative Date Calculations
```javascript
function getRelativeDateFilter(field, days) {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return `${field} ge ${date.toISOString()}`;
}

// Usage examples
const lastWeekFilter = getRelativeDateFilter('lastModified', 7);
const lastMonthFilter = getRelativeDateFilter('createdDate', 30);
const lastYearFilter = getRelativeDateFilter('createdDate', 365);
```

### Expected Outcomes
- Handle ISO 8601 date formatting
- Create relative date filters
- Understand timezone considerations

## Exercise 4: String and Text Filtering

### Objective
Implement text-based filtering using string functions.

### Scenario
Enable customers to filter by product names, descriptions, and brands using partial matches.

### Tasks

#### Task 4.1: String Function Filters
```javascript
// Products starting with "iPhone"
const startsWithFilter = "startswith(name, 'iPhone')";

// Products ending with "Pro"
const endsWithFilter = "endswith(name, 'Pro')";

// Products containing "wireless"
const containsFilter = "contains(description, 'wireless')";

// Case-insensitive search
const caseInsensitiveFilter = "contains(tolower(name), 'iphone')";
```

#### Task 4.2: Brand and Model Filtering
```javascript
function buildTextFilter(field, searchTerm, matchType = 'contains') {
  if (!searchTerm) return null;
  
  const escapedTerm = searchTerm.replace(/'/g, "''");
  
  switch (matchType) {
    case 'exact':
      return `${field} eq '${escapedTerm}'`;
    case 'startswith':
      return `startswith(${field}, '${escapedTerm}')`;
    case 'endswith':
      return `endswith(${field}, '${escapedTerm}')`;
    case 'contains':
    default:
      return `contains(${field}, '${escapedTerm}')`;
  }
}

// Usage
const brandFilter = buildTextFilter('brand', 'Apple', 'exact');
const modelFilter = buildTextFilter('model', 'iPhone', 'startswith');
const descriptionFilter = buildTextFilter('description', 'wireless', 'contains');
```

### Expected Outcomes
- Use string functions effectively
- Handle special characters and escaping
- Implement flexible text matching

## Exercise 5: Geographic Filtering

### Objective
Implement location-based filtering for geographic data.

### Scenario
Filter hotels and restaurants by distance from a user's location.

### Tasks

#### Task 5.1: Distance-Based Filtering
```javascript
// Hotels within 10 km of a location
const userLocation = "geography'POINT(-122.131577 47.678581)'";
const distanceFilter = `geo.distance(location, ${userLocation}) lt 10`;

// Restaurants within 5 miles (approximately 8 km)
const restaurantFilter = `geo.distance(location, ${userLocation}) lt 8`;
```

#### Task 5.2: Geographic Bounds Filtering
```javascript
function buildGeographicFilter(userLat, userLon, radiusKm) {
  const point = `geography'POINT(${userLon} ${userLat})'`;
  return `geo.distance(location, ${point}) lt ${radiusKm}`;
}

// Usage
const seattleFilter = buildGeographicFilter(47.6062, -122.3321, 15);
const nearbyFilter = buildGeographicFilter(userLat, userLon, 5);
```

### Expected Outcomes
- Understand geographic point syntax
- Implement distance-based filtering
- Handle coordinate systems correctly

## Exercise 6: Collection Filtering

### Objective
Filter on array and collection fields using any() and all() functions.

### Scenario
Filter hotels by amenities, products by tags, and articles by categories.

### Tasks

#### Task 6.1: Array Filtering with any()
```javascript
// Hotels with WiFi
const wifiFilter = "amenities/any(a: a eq 'WiFi')";

// Hotels with WiFi OR Pool
const amenitiesFilter = "amenities/any(a: a eq 'WiFi' or a eq 'Pool')";

// Products with specific tags
const tagFilter = "tags/any(t: t eq 'featured' or t eq 'bestseller')";
```

#### Task 6.2: Array Filtering with all()
```javascript
// Hotels where all amenities are available
const allAmenitiesFilter = "amenities/all(a: a ne null)";

// Products where all required features are present
const requiredFeaturesFilter = "features/all(f: f eq 'waterproof' or f eq 'wireless')";
```

#### Task 6.3: Complex Collection Filtering
```javascript
function buildAmenityFilter(requiredAmenities, optionalAmenities) {
  const filters = [];
  
  // All required amenities must be present
  if (requiredAmenities && requiredAmenities.length > 0) {
    requiredAmenities.forEach(amenity => {
      filters.push(`amenities/any(a: a eq '${amenity}')`);
    });
  }
  
  // At least one optional amenity should be present
  if (optionalAmenities && optionalAmenities.length > 0) {
    const optionalFilter = optionalAmenities
      .map(amenity => `a eq '${amenity}'`)
      .join(' or ');
    filters.push(`amenities/any(a: ${optionalFilter})`);
  }
  
  return filters.length > 0 ? filters.join(' and ') : null;
}

// Usage
const hotelFilter = buildAmenityFilter(
  ['WiFi', 'Parking'],  // Required
  ['Pool', 'Gym', 'Spa'] // Optional
);
```

### Expected Outcomes
- Master collection filtering syntax
- Understand any() vs all() usage
- Build complex collection filters

## Exercise 7: Sorting Implementation

### Objective
Implement various sorting strategies for different use cases.

### Scenario
Provide customers with multiple sorting options for product listings.

### Tasks

#### Task 7.1: Basic Sorting
```javascript
// Sort by price (ascending)
const priceAscSort = ["price asc"];

// Sort by rating (descending)
const ratingDescSort = ["rating desc"];

// Sort by name (alphabetical)
const nameSort = ["name asc"];
```

#### Task 7.2: Multi-Field Sorting
```javascript
// Sort by category, then rating, then price
const multiSort = ["category asc", "rating desc", "price asc"];

// Sort by availability, then rating
const availabilitySort = ["inStock desc", "rating desc"];
```

#### Task 7.3: Dynamic Sort Builder
```javascript
class SortBuilder {
  constructor() {
    this.sortFields = [];
  }
  
  addField(field, direction = 'asc') {
    this.sortFields.push(`${field} ${direction}`);
    return this;
  }
  
  addPriceSort(direction = 'asc') {
    return this.addField('price', direction);
  }
  
  addRatingSort(direction = 'desc') {
    return this.addField('rating', direction);
  }
  
  addDateSort(field = 'createdDate', direction = 'desc') {
    return this.addField(field, direction);
  }
  
  build() {
    return this.sortFields.length > 0 ? this.sortFields : null;
  }
}

// Usage
const sortOrder = new SortBuilder()
  .addField('category', 'asc')
  .addRatingSort('desc')
  .addPriceSort('asc')
  .build();
```

### Expected Outcomes
- Implement single and multi-field sorting
- Create flexible sorting utilities
- Understand sort order priorities

## Exercise 8: Performance Optimization

### Objective
Optimize filter and sort operations for better performance.

### Scenario
Improve query performance for a high-traffic e-commerce site.

### Tasks

#### Task 8.1: Filter Optimization
```javascript
// Measure query performance
async function measureQueryPerformance(searchClient, searchOptions) {
  const startTime = Date.now();
  
  try {
    const results = await searchClient.search("*", searchOptions);
    const resultList = [];
    
    for await (const result of results.results) {
      resultList.push(result);
    }
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    return {
      results: resultList,
      duration: duration,
      count: resultList.length
    };
  } catch (error) {
    const endTime = Date.now();
    return {
      error: error.message,
      duration: endTime - startTime
    };
  }
}
```

#### Task 8.2: Query Optimization Strategies
```javascript
// Compare different filter approaches
async function compareFilterPerformance(searchClient) {
  const testCases = [
    {
      name: "Specific category first",
      filter: "category eq 'Electronics' and price gt 100"
    },
    {
      name: "Price filter first",
      filter: "price gt 100 and category eq 'Electronics'"
    },
    {
      name: "Combined with availability",
      filter: "category eq 'Electronics' and price gt 100 and inStock eq true"
    }
  ];
  
  const results = [];
  
  for (const testCase of testCases) {
    const performance = await measureQueryPerformance(searchClient, {
      filter: testCase.filter,
      top: 50
    });
    
    results.push({
      name: testCase.name,
      duration: performance.duration,
      count: performance.count
    });
  }
  
  return results;
}
```

### Expected Outcomes
- Measure and compare query performance
- Understand optimization strategies
- Identify performance bottlenecks

## Exercise 9: Real-World Integration

### Objective
Build a complete filter and sort interface for a web application.

### Scenario
Create a product search page with multiple filter options and sorting capabilities.

### Tasks

#### Task 9.1: Filter State Management
```javascript
class FilterState {
  constructor() {
    this.filters = {
      category: null,
      priceRange: { min: null, max: null },
      rating: null,
      inStock: null,
      brand: null,
      features: []
    };
    this.sortBy = null;
  }
  
  setCategory(category) {
    this.filters.category = category;
    return this;
  }
  
  setPriceRange(min, max) {
    this.filters.priceRange = { min, max };
    return this;
  }
  
  setRating(rating) {
    this.filters.rating = rating;
    return this;
  }
  
  toggleFeature(feature) {
    const index = this.filters.features.indexOf(feature);
    if (index > -1) {
      this.filters.features.splice(index, 1);
    } else {
      this.filters.features.push(feature);
    }
    return this;
  }
  
  setSortBy(sortBy) {
    this.sortBy = sortBy;
    return this;
  }
  
  buildFilter() {
    const filterParts = [];
    
    if (this.filters.category) {
      filterParts.push(`category eq '${this.filters.category}'`);
    }
    
    if (this.filters.priceRange.min !== null) {
      filterParts.push(`price ge ${this.filters.priceRange.min}`);
    }
    
    if (this.filters.priceRange.max !== null) {
      filterParts.push(`price le ${this.filters.priceRange.max}`);
    }
    
    if (this.filters.rating !== null) {
      filterParts.push(`rating ge ${this.filters.rating}`);
    }
    
    if (this.filters.inStock !== null) {
      filterParts.push(`inStock eq ${this.filters.inStock}`);
    }
    
    if (this.filters.brand) {
      filterParts.push(`brand eq '${this.filters.brand}'`);
    }
    
    if (this.filters.features.length > 0) {
      const featureFilters = this.filters.features
        .map(feature => `features/any(f: f eq '${feature}')`)
        .join(' and ');
      filterParts.push(featureFilters);
    }
    
    return filterParts.length > 0 ? filterParts.join(' and ') : null;
  }
  
  buildSort() {
    const sortOptions = {
      'price-asc': ['price asc'],
      'price-desc': ['price desc'],
      'rating-desc': ['rating desc'],
      'name-asc': ['name asc'],
      'newest': ['createdDate desc']
    };
    
    return sortOptions[this.sortBy] || null;
  }
}
```

#### Task 9.2: Search Interface Implementation
```javascript
class ProductSearchInterface {
  constructor(searchClient) {
    this.searchClient = searchClient;
    this.filterState = new FilterState();
  }
  
  async search(searchText = "*", page = 0, pageSize = 20) {
    const filter = this.filterState.buildFilter();
    const orderBy = this.filterState.buildSort();
    
    const searchOptions = {
      filter: filter,
      orderBy: orderBy,
      top: pageSize,
      skip: page * pageSize,
      select: [
        'id', 'name', 'category', 'brand', 'price', 
        'rating', 'inStock', 'imageUrl', 'description'
      ],
      facets: [
        'category',
        'brand', 
        'rating,interval:1',
        'inStock'
      ]
    };
    
    try {
      const results = await this.searchClient.search(searchText, searchOptions);
      
      return {
        results: results,
        facets: results.facets,
        filter: filter,
        sort: orderBy
      };
    } catch (error) {
      console.error('Search failed:', error);
      throw error;
    }
  }
  
  setFilters(filters) {
    Object.assign(this.filterState.filters, filters);
    return this;
  }
  
  setSort(sortBy) {
    this.filterState.setSortBy(sortBy);
    return this;
  }
  
  clearFilters() {
    this.filterState = new FilterState();
    return this;
  }
}
```

### Expected Outcomes
- Build complete search interfaces
- Manage complex filter state
- Integrate with web applications

## Exercise 10: Testing and Validation

### Objective
Create comprehensive tests for filter and sort functionality.

### Scenario
Ensure your filter and sort implementations work correctly across different scenarios.

### Tasks

#### Task 10.1: Unit Tests
```javascript
// Test filter building
describe('Filter Building', () => {
  test('should build category filter', () => {
    const filterState = new FilterState();
    filterState.setCategory('Electronics');
    
    const filter = filterState.buildFilter();
    expect(filter).toBe("category eq 'Electronics'");
  });
  
  test('should build price range filter', () => {
    const filterState = new FilterState();
    filterState.setPriceRange(100, 500);
    
    const filter = filterState.buildFilter();
    expect(filter).toBe("price ge 100 and price le 500");
  });
  
  test('should build complex filter', () => {
    const filterState = new FilterState();
    filterState.setCategory('Electronics')
             .setPriceRange(100, 500)
             .setRating(4.0);
    
    const filter = filterState.buildFilter();
    expect(filter).toBe("category eq 'Electronics' and price ge 100 and price le 500 and rating ge 4.0");
  });
});
```

#### Task 10.2: Integration Tests
```javascript
// Test actual search functionality
describe('Search Integration', () => {
  test('should filter by category', async () => {
    const interface = new ProductSearchInterface(searchClient);
    interface.setFilters({ category: 'Electronics' });
    
    const results = await interface.search();
    
    expect(results.results).toBeDefined();
    // Verify all results are in Electronics category
  });
  
  test('should sort by price', async () => {
    const interface = new ProductSearchInterface(searchClient);
    interface.setSort('price-asc');
    
    const results = await interface.search();
    
    // Verify results are sorted by price ascending
    const prices = [];
    for await (const result of results.results.results) {
      prices.push(result.document.price);
    }
    
    expect(prices).toEqual([...prices].sort((a, b) => a - b));
  });
});
```

### Expected Outcomes
- Create comprehensive test suites
- Validate filter and sort logic
- Ensure integration reliability

## Completion Checklist

After completing these exercises, you should be able to:

- [ ] Build basic equality and comparison filters
- [ ] Create complex logical filter combinations
- [ ] Implement date and time-based filtering
- [ ] Use string functions for text filtering
- [ ] Apply geographic distance filtering
- [ ] Filter on collection/array fields
- [ ] Implement single and multi-field sorting
- [ ] Optimize query performance
- [ ] Build complete search interfaces
- [ ] Test filter and sort functionality

## Next Steps

1. **Apply to Your Project**: Implement these patterns in your own application
2. **Explore Advanced Features**: Move on to faceted navigation and aggregations
3. **Performance Tuning**: Monitor and optimize your implementations
4. **User Experience**: Focus on creating intuitive filter and sort interfaces

## Additional Resources

### Module Documentation
- **[Prerequisites](prerequisites.md)** - Required setup and knowledge
- **[Main Documentation](documentation.md)** - Complete module overview
- **[Best Practices](best-practices.md)** - Guidelines for effective implementation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Code Samples](code-samples/README.md)** - Working examples in multiple languages

### External Resources
- **[OData Filter Syntax Reference](https://docs.microsoft.com/azure/search/search-query-odata-filter)**
- **[Azure AI Search Documentation](https://docs.microsoft.com/azure/search/)**
- **[Performance Optimization Guide](https://docs.microsoft.com/azure/search/search-performance-optimization)**

### When You Need Help
- **Syntax Issues**: Check the [Troubleshooting Guide](troubleshooting.md)
- **Performance Problems**: Review [Performance Analysis Examples](code-samples/python/08_performance_analysis.py)
- **Complex Scenarios**: Explore [Complex Filter Examples](code-samples/python/07_complex_filters.py)

Remember: Practice makes perfect! Work through these exercises multiple times with different data sets to build confidence and expertise.