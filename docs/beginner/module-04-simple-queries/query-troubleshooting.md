# Query Operations Troubleshooting - Module 4: Simple Queries

## Common Query Issues

### Issue: No results returned for valid queries
**Symptoms:**
- Query executes successfully but returns zero results
- Expected documents are not found
- Similar queries work in other contexts

**Common Causes:**
- Field not marked as searchable in index schema
- Incorrect field names in searchFields parameter
- Analyzer mismatch between indexing and querying
- Case sensitivity issues
- Special characters not properly escaped

**Solutions:**
1. **Verify Field Configuration**:
```http
GET https://[service-name].search.windows.net/indexes/[index-name]?api-version=2024-07-01
```
Check that fields are marked as `"searchable": true`

2. **Test with Wildcard Search**:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/search?api-version=2024-07-01
{
  "search": "*",
  "top": 5
}
```

3. **Verify Field Names**:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/search?api-version=2024-07-01
{
  "search": "test",
  "searchFields": "title,description",  // Verify these field names exist
  "select": "id,title,description"
}
```

### Issue: Query syntax errors
**Symptoms:**
- HTTP 400 Bad Request errors
- "Invalid query syntax" error messages
- Queries fail to execute

**Common Causes:**
- Malformed boolean expressions
- Unescaped special characters
- Invalid field references
- Incorrect query type specification

**Solutions:**
1. **Validate Boolean Syntax**:
```javascript
// Invalid
{
  "search": "hotel AND (luxury OR",  // Missing closing parenthesis
  "queryType": "full"
}

// Valid
{
  "search": "hotel AND (luxury OR premium)",
  "queryType": "full"
}
```

2. **Escape Special Characters**:
```javascript
// Characters that need escaping: + - && || ! ( ) { } [ ] ^ " ~ * ? : \ /
function escapeSearchQuery(query) {
  return query.replace(/[+\-&|!(){}[\]^"~*?:\\\/]/g, '\\$&');
}
```

3. **Test with Simple Syntax First**:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/search?api-version=2024-07-01
{
  "search": "hotel",
  "queryType": "simple"  // Start with simple syntax
}
```

### Issue: Poor search relevance
**Symptoms:**
- Irrelevant results appearing first
- Expected results ranked too low
- Inconsistent ranking across similar queries

**Common Causes:**
- Inappropriate search mode selection
- Missing or incorrect field boosting
- Analyzer configuration issues
- Poor query construction

**Solutions:**
1. **Adjust Search Mode**:
```javascript
// For broader matching
{
  "search": "luxury hotel",
  "searchMode": "any"  // Matches documents with "luxury" OR "hotel"
}

// For more precise matching
{
  "search": "luxury hotel",
  "searchMode": "all"  // Matches documents with "luxury" AND "hotel"
}
```

2. **Implement Field Boosting**:
```javascript
{
  "search": "hotel",
  "searchFields": "title^3,description^1,tags^2"  // Boost title 3x, tags 2x
}
```

3. **Use Scoring Profiles**:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/search?api-version=2024-07-01
{
  "search": "hotel",
  "scoringProfile": "titleBoost"
}
```

## Performance Issues

### Issue: Slow query response times
**Symptoms:**
- Queries take longer than expected to execute
- Timeout errors on complex queries
- Poor user experience due to delays

**Common Causes:**
- Complex query expressions
- Large result sets without pagination
- Inefficient field selection
- Resource constraints on search service

**Solutions:**
1. **Optimize Query Complexity**:
```javascript
// Avoid overly complex boolean expressions
// Instead of:
{
  "search": "(title:(luxury OR premium OR deluxe) AND description:(hotel OR resort OR spa)) OR (tags:(5-star OR luxury) AND category:(accommodation OR lodging))",
  "queryType": "full"
}

// Use simpler approach:
{
  "search": "luxury hotel",
  "searchFields": "title,description,tags",
  "searchMode": "any"
}
```

2. **Implement Pagination**:
```javascript
{
  "search": "hotel",
  "top": 20,      // Limit results per page
  "skip": 0,      // Start from beginning
  "count": true   // Include total count
}
```

3. **Optimize Field Selection**:
```javascript
{
  "search": "hotel",
  "select": "id,title,rating,price",  // Only return needed fields
  "searchFields": "title,description"  // Only search relevant fields
}
```

### Issue: High resource utilization
**Symptoms:**
- Search service showing high CPU or memory usage
- Throttling or rate limiting errors
- Degraded performance across all queries

**Common Causes:**
- Too many concurrent queries
- Inefficient query patterns
- Large index size relative to service tier
- Wildcard queries with leading wildcards

**Solutions:**
1. **Optimize Wildcard Usage**:
```javascript
// Avoid leading wildcards (slower)
{
  "search": "*otel",
  "queryType": "full"
}

// Prefer trailing wildcards (faster)
{
  "search": "hot*",
  "queryType": "full"
}
```

2. **Implement Query Caching**:
```javascript
const queryCache = new Map();

async function cachedSearch(query) {
  const cacheKey = JSON.stringify(query);
  
  if (queryCache.has(cacheKey)) {
    return queryCache.get(cacheKey);
  }
  
  const results = await searchClient.search(query);
  queryCache.set(cacheKey, results);
  
  return results;
}
```

3. **Monitor and Scale Service**:
- Monitor search service metrics
- Consider upgrading service tier
- Implement connection pooling
- Use appropriate replica and partition configuration

## Field-Specific Issues

### Issue: Multi-field search not working as expected
**Symptoms:**
- Results missing from specific fields
- Inconsistent behavior across fields
- Field-specific queries failing

**Common Causes:**
- Fields not marked as searchable
- Different analyzers on different fields
- Field name typos in searchFields parameter
- Complex field structures not handled properly

**Solutions:**
1. **Verify Field Configuration**:
```http
GET https://[service-name].search.windows.net/indexes/[index-name]?api-version=2024-07-01
```
Check each field's `searchable` attribute and `analyzer` configuration.

2. **Test Individual Fields**:
```javascript
// Test each field individually
const testFields = ['title', 'description', 'tags'];

for (const field of testFields) {
  const results = await searchClient.search({
    search: "test query",
    searchFields: field,
    select: `id,${field}`
  });
  
  console.log(`Field ${field}: ${results.length} results`);
}
```

3. **Handle Complex Fields**:
```javascript
// For complex fields, specify the full path
{
  "search": "seattle",
  "searchFields": "address/city,address/state",
  "select": "id,title,address"
}
```

### Issue: Analyzer-related search problems
**Symptoms:**
- Expected matches not found
- Language-specific searches failing
- Inconsistent tokenization behavior

**Common Causes:**
- Wrong analyzer for content language
- Mismatch between index-time and query-time analyzers
- Custom analyzer configuration issues
- Case sensitivity problems

**Solutions:**
1. **Test Analyzer Behavior**:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/analyze?api-version=2024-07-01
{
  "text": "Luxury Hotel in Seattle",
  "analyzer": "en.lucene"
}
```

2. **Verify Analyzer Configuration**:
```javascript
// Check field analyzer in index definition
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true,
  "analyzer": "en.lucene"  // Ensure appropriate analyzer
}
```

3. **Test with Different Analyzers**:
```javascript
// Test with standard analyzer for comparison
{
  "search": "test query",
  "searchFields": "description",
  "queryType": "simple"
}
```

## Boolean Logic Issues

### Issue: Boolean queries not working as expected
**Symptoms:**
- AND/OR logic not behaving correctly
- Unexpected results with boolean combinations
- Precedence issues in complex expressions

**Common Causes:**
- Incorrect operator precedence
- Missing parentheses for grouping
- Wrong query type (simple vs full)
- Escaped operators in simple syntax

**Solutions:**
1. **Use Proper Query Type**:
```javascript
// For boolean operators, use full Lucene syntax
{
  "search": "hotel AND (luxury OR premium)",
  "queryType": "full"  // Required for boolean operators
}
```

2. **Add Explicit Grouping**:
```javascript
// Clear precedence with parentheses
{
  "search": "(title:hotel OR title:resort) AND (category:luxury)",
  "queryType": "full"
}
```

3. **Test Boolean Logic Step by Step**:
```javascript
// Test individual parts first
const tests = [
  "hotel",
  "luxury",
  "hotel AND luxury",
  "hotel OR resort",
  "(hotel OR resort) AND luxury"
];

for (const query of tests) {
  const results = await searchClient.search({
    search: query,
    queryType: "full"
  });
  console.log(`Query "${query}": ${results.length} results`);
}
```

## Diagnostic Techniques

### Query Analysis
```javascript
async function analyzeQuery(query) {
  console.log(`Analyzing query: ${JSON.stringify(query)}`);
  
  try {
    const startTime = Date.now();
    const results = await searchClient.search(query);
    const duration = Date.now() - startTime;
    
    console.log(`Results: ${results.length} documents in ${duration}ms`);
    
    // Log first few results for analysis
    const firstResults = results.slice(0, 3);
    firstResults.forEach((result, index) => {
      console.log(`Result ${index + 1}:`, {
        id: result.id,
        score: result['@search.score'],
        highlights: result['@search.highlights']
      });
    });
    
    return results;
  } catch (error) {
    console.error(`Query failed:`, error.message);
    throw error;
  }
}
```

### Performance Profiling
```javascript
class QueryProfiler {
  constructor() {
    this.metrics = [];
  }
  
  async profileQuery(query, description = '') {
    const startTime = performance.now();
    const startMemory = process.memoryUsage().heapUsed;
    
    try {
      const results = await searchClient.search(query);
      const endTime = performance.now();
      const endMemory = process.memoryUsage().heapUsed;
      
      const metrics = {
        description,
        query: JSON.stringify(query),
        duration: endTime - startTime,
        memoryDelta: endMemory - startMemory,
        resultCount: results.length,
        success: true
      };
      
      this.metrics.push(metrics);
      return results;
    } catch (error) {
      const endTime = performance.now();
      
      const metrics = {
        description,
        query: JSON.stringify(query),
        duration: endTime - startTime,
        error: error.message,
        success: false
      };
      
      this.metrics.push(metrics);
      throw error;
    }
  }
  
  getReport() {
    return {
      totalQueries: this.metrics.length,
      successRate: this.metrics.filter(m => m.success).length / this.metrics.length,
      averageDuration: this.metrics.reduce((sum, m) => sum + m.duration, 0) / this.metrics.length,
      slowestQuery: this.metrics.reduce((max, m) => m.duration > max.duration ? m : max),
      metrics: this.metrics
    };
  }
}
```

### Error Pattern Analysis
```javascript
function analyzeSearchErrors(errors) {
  const errorPatterns = {};
  
  errors.forEach(error => {
    const pattern = error.message.replace(/['"]\w+['"]/g, '"FIELD"')
                                .replace(/\d+/g, 'NUMBER');
    
    if (!errorPatterns[pattern]) {
      errorPatterns[pattern] = {
        count: 0,
        examples: []
      };
    }
    
    errorPatterns[pattern].count++;
    if (errorPatterns[pattern].examples.length < 3) {
      errorPatterns[pattern].examples.push(error.message);
    }
  });
  
  return errorPatterns;
}
```

## Prevention Strategies

### Input Validation
```javascript
function validateSearchQuery(query) {
  const errors = [];
  
  // Check for empty query
  if (!query.search || query.search.trim().length === 0) {
    errors.push("Search query cannot be empty");
  }
  
  // Check query length
  if (query.search && query.search.length > 1000) {
    errors.push("Search query too long (max 1000 characters)");
  }
  
  // Validate searchFields
  if (query.searchFields) {
    const validFields = ['title', 'description', 'tags', 'content'];
    const requestedFields = query.searchFields.split(',');
    const invalidFields = requestedFields.filter(f => !validFields.includes(f.trim()));
    
    if (invalidFields.length > 0) {
      errors.push(`Invalid search fields: ${invalidFields.join(', ')}`);
    }
  }
  
  // Validate top parameter
  if (query.top && (query.top < 1 || query.top > 1000)) {
    errors.push("Top parameter must be between 1 and 1000");
  }
  
  return errors;
}
```

### Query Sanitization
```javascript
function sanitizeQuery(query) {
  // Remove potentially harmful characters
  let sanitized = query.replace(/[<>]/g, '');
  
  // Escape special Lucene characters if using full syntax
  if (query.queryType === 'full') {
    sanitized = sanitized.replace(/[+\-&|!(){}[\]^"~*?:\\\/]/g, '\\$&');
  }
  
  return sanitized;
}
```

### Monitoring and Alerting
```javascript
class QueryMonitor {
  constructor() {
    this.errorThreshold = 0.05; // 5% error rate threshold
    this.slowQueryThreshold = 2000; // 2 second threshold
    this.recentQueries = [];
    this.maxHistorySize = 1000;
  }
  
  recordQuery(query, duration, success, error = null) {
    const record = {
      timestamp: Date.now(),
      query: JSON.stringify(query),
      duration,
      success,
      error
    };
    
    this.recentQueries.push(record);
    
    // Keep only recent queries
    if (this.recentQueries.length > this.maxHistorySize) {
      this.recentQueries.shift();
    }
    
    // Check for alerts
    this.checkAlerts();
  }
  
  checkAlerts() {
    const recent = this.recentQueries.slice(-100); // Last 100 queries
    
    // Check error rate
    const errorRate = recent.filter(q => !q.success).length / recent.length;
    if (errorRate > this.errorThreshold) {
      this.alert(`High error rate: ${(errorRate * 100).toFixed(1)}%`);
    }
    
    // Check for slow queries
    const slowQueries = recent.filter(q => q.duration > this.slowQueryThreshold);
    if (slowQueries.length > 0) {
      this.alert(`${slowQueries.length} slow queries detected`);
    }
  }
  
  alert(message) {
    console.warn(`QUERY ALERT: ${message}`);
    // Implement your alerting mechanism here
  }
}
```

By following these troubleshooting guidelines and implementing proper monitoring, you can identify and resolve query issues quickly, ensuring reliable and performant search functionality in your Azure AI Search implementation.