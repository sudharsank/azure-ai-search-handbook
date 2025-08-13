# Schema Issues Troubleshooting - Module 3: Index Management

## Schema Design Problems

### Issue: Field attribute conflicts
**Symptoms:**
- Index creation fails with validation errors
- Unexpected behavior with field operations
- Performance issues with certain field combinations

**Common Causes:**
- Incompatible field attribute combinations
- Key fields with inappropriate attributes
- Collection fields with unsupported attributes

**Solutions:**
```json
// Invalid: Key field cannot be facetable
{
  "name": "id",
  "type": "Edm.String",
  "key": true,
  "facetable": true  // ❌ This will fail
}

// Valid: Key field configuration
{
  "name": "id",
  "type": "Edm.String",
  "key": true,
  "retrievable": true
}
```

### Issue: Incorrect data type selection
**Symptoms:**
- Data conversion errors during indexing
- Unexpected query behavior
- Performance issues

**Common Causes:**
- Using string for numeric data
- Wrong date/time format specification
- Inappropriate collection types

**Solutions:**
1. **Numeric Data**: Use appropriate numeric types
```json
// Wrong
{"name": "price", "type": "Edm.String"}

// Correct
{"name": "price", "type": "Edm.Double"}
```

2. **Date/Time Data**: Use DateTimeOffset for dates
```json
// Wrong
{"name": "created", "type": "Edm.String"}

// Correct
{"name": "created", "type": "Edm.DateTimeOffset"}
```

3. **Boolean Data**: Use Boolean type for true/false values
```json
// Wrong
{"name": "isActive", "type": "Edm.String"}

// Correct
{"name": "isActive", "type": "Edm.Boolean"}
```

## Field Naming Issues

### Issue: Invalid field names
**Symptoms:**
- Schema validation errors
- Index creation failures
- API operation failures

**Common Causes:**
- Field names starting with numbers
- Special characters in field names
- Reserved keywords used as field names
- Case sensitivity issues

**Solutions:**
```json
// Invalid field names
{
  "name": "2ndField",     // ❌ Cannot start with number
  "name": "field-name",   // ❌ Hyphens not allowed
  "name": "field name",   // ❌ Spaces not allowed
  "name": "type"          // ❌ Reserved keyword
}

// Valid field names
{
  "name": "secondField",  // ✅ Starts with letter
  "name": "field_name",   // ✅ Underscores allowed
  "name": "fieldName",    // ✅ CamelCase allowed
  "name": "documentType"  // ✅ Descriptive name
}
```

### Field Naming Best Practices
- Start with letter or underscore
- Use only letters, numbers, and underscores
- Avoid reserved keywords
- Use descriptive, meaningful names
- Be consistent with naming conventions

## Analyzer Configuration Issues

### Issue: Incorrect analyzer selection
**Symptoms:**
- Poor search results
- Unexpected tokenization behavior
- Language-specific search problems

**Common Causes:**
- Wrong language analyzer
- Inappropriate analyzer for content type
- Missing custom analyzer configuration

**Solutions:**
1. **Language-Specific Content**:
```json
// For English content
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true,
  "analyzer": "en.lucene"
}

// For multilingual content
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true,
  "analyzer": "standard.lucene"
}
```

2. **Exact Match Fields**:
```json
// For exact matching (like product codes)
{
  "name": "productCode",
  "type": "Edm.String",
  "searchable": true,
  "analyzer": "keyword"
}
```

### Issue: Custom analyzer problems
**Symptoms:**
- Analyzer not found errors
- Unexpected tokenization results
- Performance issues

**Common Causes:**
- Analyzer not defined in index
- Incorrect analyzer configuration
- Circular dependencies in analyzer definition

**Solutions:**
1. Define custom analyzers properly:
```json
{
  "analyzers": [
    {
      "name": "my_custom_analyzer",
      "tokenizer": "standard",
      "tokenFilters": ["lowercase", "asciifolding"]
    }
  ],
  "fields": [
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "analyzer": "my_custom_analyzer"
    }
  ]
}
```

## Complex Field Issues

### Issue: Complex field configuration errors
**Symptoms:**
- Schema validation failures
- Nested object indexing problems
- Query failures on complex fields

**Common Causes:**
- Incorrect complex field structure
- Missing sub-field definitions
- Inappropriate attributes on complex fields

**Solutions:**
```json
// Correct complex field definition
{
  "name": "address",
  "type": "Edm.ComplexType",
  "fields": [
    {
      "name": "street",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "city",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "zipCode",
      "type": "Edm.String",
      "filterable": true
    }
  ]
}
```

### Issue: Collection field problems
**Symptoms:**
- Array data not indexing correctly
- Filter operations failing on collections
- Unexpected query results

**Common Causes:**
- Incorrect collection type specification
- Missing collection syntax
- Inappropriate operations on collections

**Solutions:**
```json
// String collection
{
  "name": "tags",
  "type": "Collection(Edm.String)",
  "searchable": true,
  "filterable": true,
  "facetable": true
}

// Complex type collection
{
  "name": "reviews",
  "type": "Collection(Edm.ComplexType)",
  "fields": [
    {
      "name": "rating",
      "type": "Edm.Int32",
      "filterable": true
    },
    {
      "name": "comment",
      "type": "Edm.String",
      "searchable": true
    }
  ]
}
```

## Schema Evolution Issues

### Issue: Cannot modify existing field
**Symptoms:**
- Schema update operations fail
- Field modification errors
- Index update rejections

**Common Causes:**
- Attempting to change immutable field properties
- Modifying field types
- Changing key field configuration

**Solutions:**
1. **Understand Immutable Properties**:
   - Field name cannot be changed
   - Field type cannot be changed
   - Key field designation cannot be changed

2. **Workaround Strategies**:
   - Add new field with desired configuration
   - Migrate data to new field
   - Remove old field if possible
   - Consider creating new index for major changes

### Issue: Schema version compatibility
**Symptoms:**
- Application errors after schema updates
- Unexpected query behavior
- Data access issues

**Common Causes:**
- Breaking changes in schema
- Application code not updated
- Cached schema information

**Solutions:**
1. **Plan Schema Changes**:
   - Analyze impact of changes
   - Update application code
   - Test in development environment
   - Implement gradual rollout

2. **Backward Compatibility**:
   - Add new fields as optional
   - Maintain old field names when possible
   - Use field aliases if supported
   - Document breaking changes

## Performance-Related Schema Issues

### Issue: Poor query performance due to schema design
**Symptoms:**
- Slow query response times
- High resource utilization
- Timeout errors

**Common Causes:**
- Too many searchable fields
- Inappropriate field attributes
- Large text fields with full indexing
- Excessive facetable fields

**Solutions:**
1. **Optimize Field Attributes**:
```json
// Before: Over-attributed field
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true,
  "filterable": true,    // ❌ Unnecessary if not filtering
  "sortable": true,      // ❌ Unnecessary if not sorting
  "facetable": true      // ❌ Unnecessary if not faceting
}

// After: Optimized field
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true     // ✅ Only necessary attribute
}
```

2. **Reduce Index Size**:
   - Remove unnecessary fields
   - Use appropriate data types
   - Optimize text field storage
   - Consider field-specific analyzers

## Diagnostic Techniques

### Schema Validation
```http
PUT https://[service-name].search.windows.net/indexes/[index-name]?api-version=2024-07-01
{
  "name": "test-index",
  "fields": [
    // Your field definitions
  ]
}
```

### Field Testing
Test individual fields with sample data:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/docs/index?api-version=2024-07-01
{
  "value": [
    {
      "@search.action": "upload",
      "id": "test1",
      "testField": "sample value"
    }
  ]
}
```

### Analyzer Testing
Test analyzer behavior:
```http
POST https://[service-name].search.windows.net/indexes/[index-name]/analyze?api-version=2024-07-01
{
  "text": "sample text to analyze",
  "analyzer": "en.lucene"
}
```

## Common Schema Patterns

### E-commerce Product Schema
```json
{
  "name": "products",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "name", "type": "Edm.String", "searchable": true, "analyzer": "en.lucene"},
    {"name": "description", "type": "Edm.String", "searchable": true},
    {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "price", "type": "Edm.Double", "filterable": true, "sortable": true},
    {"name": "inStock", "type": "Edm.Boolean", "filterable": true},
    {"name": "tags", "type": "Collection(Edm.String)", "searchable": true, "facetable": true}
  ]
}
```

### Document Management Schema
```json
{
  "name": "documents",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "title", "type": "Edm.String", "searchable": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "author", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "created", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
    {"name": "fileType", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "size", "type": "Edm.Int64", "filterable": true, "sortable": true}
  ]
}
```

## Prevention Strategies

### Schema Design Review
- Conduct thorough schema reviews before implementation
- Validate with representative data
- Test performance with expected data volumes
- Document design decisions and rationale

### Testing Procedures
- Test schema with various data scenarios
- Validate field attribute combinations
- Test analyzer behavior with sample content
- Perform load testing with realistic data

### Documentation
- Maintain comprehensive schema documentation
- Document field purposes and usage
- Keep track of schema evolution history
- Document known limitations and workarounds

By following these troubleshooting guidelines and prevention strategies, you can avoid common schema issues and maintain robust, performant search indexes.