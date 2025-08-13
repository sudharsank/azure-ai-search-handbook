# Performance Issues Troubleshooting - Module 4: Simple Queries

## Query Performance Issues

### Issue: Slow query response times
**Symptoms:**
- Queries taking longer than 1-2 seconds consistently
- User interface feels sluggish
- Timeout errors on complex queries
- High latency in search operations

**Common Causes:**
- Inefficient query patterns
- Large result sets without pagination
- Complex boolean expressions
- Wildcard queries with leading wildcards
- Insufficient service tier resources

**Solutions:**

1. **Optimize Query Structure**:
```javascript
// Inefficient: Complex nested boolean query
{
  "search": "((title:(luxury OR premium OR deluxe) AND description:(hotel OR resort)) OR (tags:(5-star OR luxury) AND category:(accommodation))) AND NOT (tags:(budget OR economy))",
  "queryType": "full"
}

// Efficient: Simplified query with targeted fields
{
  "search": "luxury hotel",
  "searchFields": "title,description,tags",
  "searchMode": "any"
}
```

2. **Implement Proper Pagination**:
```javascript
// Inefficient: Loading all results
{
  "search": "hotel",
  "top": 1000  // Too many results at once
}

// Efficient: Reasonable page size
{
  "search": "hotel",
  "top": 20,
  "skip": 0,
  "count": true
}
```

3. **Optimize Field Selection**:
```javascript
// Inefficient: Returning all fields
{
  "search": "hotel"
  // Returns all retrievable fields
}

// Efficient: Select only needed fields
{
  "search": "hotel",
  "select": "id,title,rating,price,location",
  "searchFields": "title,description"
}
```

### Issue: High memory usage during queries
**Symptoms:**
- Memory spikes during search operations
- Out of memory errors
- Service becoming unresponsive
- Degraded performance for concurrent users

**Common Causes:**
- Large result sets being loaded into memory
- Complex aggregations or faceting
- Inefficient result processing
- Memory leaks in application code

**Solutions:**

1. **Implement Streaming for Large Results**:
```javascript
async function* streamSearchResults(query, batchSize = 100) {
  let skip = 0;
  let hasMore = true;
  
  while (hasMore) {
    const batch = await searchClient.search({
      ...query,
      top: batchSize,
      skip: skip
    });
    
    if (batch.length === 0) {
      hasMore = false;
    } else {
      yield batch;
      skip += batchSize;
      hasMore = batch.length === batchSize;
    }
  }
}
```

2. **Optimize Faceting Operations**:
```javascript
// Inefficient: Too many facets
{
  "search": "hotel",
  "facets": ["category", "rating", "amenities", "location", "priceRange", "brand", "type"]
}

// Efficient: Essential facets only
{
  "search": "hotel",
  "facets": ["category", "rating", "priceRange"]
}
```

3. **Implement Result Caching**:
```javascript
class QueryCache {
  constructor(maxSize = 100, ttlMs = 300000) { // 5 minutes TTL
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttlMs = ttlMs;
  }
  
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > this.ttlMs) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  set(key, data) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
}
```

## Resource Utilization Issues

### Issue: High CPU usage on search service
**Symptoms:**
- Search service showing consistently high CPU utilization
- Throttling errors (HTTP 503)
- Degraded performance across all operations
- Increased response times

**Common Causes:**
- Too many concurrent queries
- Complex query patterns
- Insufficient service tier for workload
- Inefficient indexing operations running concurrently

**Solutions:**

1. **Implement Query Rate Limiting**:
```javascript
class RateLimiter {
  constructor(maxRequests = 10, windowMs = 1000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requests = [];
  }
  
  async acquire() {
    const now = Date.now();
    
    // Remove old requests outside the window
    this.requests = this.requests.filter(time => now - time < this.windowMs);
    
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = this.windowMs - (now - oldestRequest);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      return this.acquire();
    }
    
    this.requests.push(now);
  }
}
```

2. **Optimize Concurrent Query Handling**:
```javascript
class QueryQueue {
  constructor(maxConcurrent = 5) {
    this.maxConcurrent = maxConcurrent;
    this.running = 0;
    this.queue = [];
  }
  
  async execute(queryFn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ queryFn, resolve, reject });
      this.processQueue();
    });
  }
  
  async processQueue() {
    if (this.running >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }
    
    this.running++;
    const { queryFn, resolve, reject } = this.queue.shift();
    
    try {
      const result = await queryFn();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      this.running--;
      this.processQueue();
    }
  }
}
```

3. **Monitor and Scale Resources**:
```javascript
class ResourceMonitor {
  constructor(searchClient) {
    this.searchClient = searchClient;
    this.metrics = [];
  }
  
  async collectMetrics() {
    const startTime = Date.now();
    
    try {
      // Simple health check query
      await this.searchClient.search({
        search: "*",
        top: 1
      });
      
      const responseTime = Date.now() - startTime;
      
      this.metrics.push({
        timestamp: Date.now(),
        responseTime,
        success: true
      });
      
      // Alert if response time is consistently high
      const recentMetrics = this.metrics.slice(-10);
      const avgResponseTime = recentMetrics.reduce((sum, m) => sum + m.responseTime, 0) / recentMetrics.length;
      
      if (avgResponseTime > 2000) { // 2 seconds threshold
        console.warn(`High average response time: ${avgResponseTime}ms`);
      }
      
    } catch (error) {
      this.metrics.push({
        timestamp: Date.now(),
        error: error.message,
        success: false
      });
    }
  }
}
```

### Issue: Network latency affecting performance
**Symptoms:**
- Inconsistent query performance
- Higher latency from certain geographic locations
- Network timeout errors
- Variable response times

**Common Causes:**
- Geographic distance from search service
- Network congestion
- Inefficient connection management
- Missing connection pooling

**Solutions:**

1. **Implement Connection Pooling**:
```javascript
const https = require('https');

const agent = new https.Agent({
  keepAlive: true,
  maxSockets: 10,
  maxFreeSockets: 5,
  timeout: 60000,
  freeSocketTimeout: 30000
});

const searchClient = new SearchClient(endpoint, credential, {
  httpClient: {
    agent: agent
  }
});
```

2. **Add Retry Logic with Exponential Backoff**:
```javascript
async function executeWithRetry(queryFn, maxRetries = 3, baseDelay = 1000) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await queryFn();
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

3. **Implement Circuit Breaker Pattern**:
```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.threshold = threshold;
    this.timeout = timeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
  }
  
  async execute(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }
  
  onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.threshold) {
      this.state = 'OPEN';
    }
  }
}
```

## Query Optimization Techniques

### Wildcard Query Optimization
```javascript
// Inefficient: Leading wildcard
{
  "search": "*hotel",
  "queryType": "full"
}

// Efficient: Trailing wildcard
{
  "search": "hotel*",
  "queryType": "full"
}

// Alternative: Use contains function for partial matching
{
  "search": "hotel",
  "searchMode": "any"
}
```

### Boolean Query Optimization
```javascript
// Inefficient: Complex nested boolean
{
  "search": "((A AND B) OR (C AND D)) AND ((E OR F) AND (G OR H))",
  "queryType": "full"
}

// Efficient: Simplified with filters
{
  "search": "A B C D",
  "filter": "category eq 'E' or category eq 'F'",
  "searchMode": "any"
}
```

### Field-Specific Optimization
```javascript
// Inefficient: Searching all fields
{
  "search": "luxury hotel"
}

// Efficient: Target specific fields
{
  "search": "luxury hotel",
  "searchFields": "title,description",
  "select": "id,title,rating,price"
}
```

## Performance Monitoring

### Query Performance Metrics
```javascript
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      totalQueries: 0,
      totalDuration: 0,
      slowQueries: [],
      errorCount: 0,
      cacheHits: 0,
      cacheMisses: 0
    };
  }
  
  recordQuery(query, duration, fromCache = false, error = null) {
    this.metrics.totalQueries++;
    this.metrics.totalDuration += duration;
    
    if (fromCache) {
      this.metrics.cacheHits++;
    } else {
      this.metrics.cacheMisses++;
    }
    
    if (error) {
      this.metrics.errorCount++;
    }
    
    if (duration > 2000) { // Slow query threshold
      this.metrics.slowQueries.push({
        query: JSON.stringify(query),
        duration,
        timestamp: Date.now()
      });
      
      // Keep only recent slow queries
      if (this.metrics.slowQueries.length > 100) {
        this.metrics.slowQueries.shift();
      }
    }
  }
  
  getReport() {
    const avgDuration = this.metrics.totalDuration / this.metrics.totalQueries;
    const cacheHitRate = this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses);
    const errorRate = this.metrics.errorCount / this.metrics.totalQueries;
    
    return {
      totalQueries: this.metrics.totalQueries,
      averageDuration: avgDuration,
      cacheHitRate: cacheHitRate,
      errorRate: errorRate,
      slowQueryCount: this.metrics.slowQueries.length,
      recentSlowQueries: this.metrics.slowQueries.slice(-10)
    };
  }
}
```

### Real-time Performance Dashboard
```javascript
class PerformanceDashboard {
  constructor(monitor) {
    this.monitor = monitor;
    this.alertThresholds = {
      avgResponseTime: 1000,
      errorRate: 0.05,
      cacheHitRate: 0.7
    };
  }
  
  generateReport() {
    const report = this.monitor.getReport();
    const alerts = this.checkAlerts(report);
    
    return {
      ...report,
      alerts,
      timestamp: new Date().toISOString()
    };
  }
  
  checkAlerts(report) {
    const alerts = [];
    
    if (report.averageDuration > this.alertThresholds.avgResponseTime) {
      alerts.push({
        type: 'HIGH_RESPONSE_TIME',
        message: `Average response time ${report.averageDuration}ms exceeds threshold`,
        severity: 'WARNING'
      });
    }
    
    if (report.errorRate > this.alertThresholds.errorRate) {
      alerts.push({
        type: 'HIGH_ERROR_RATE',
        message: `Error rate ${(report.errorRate * 100).toFixed(1)}% exceeds threshold`,
        severity: 'CRITICAL'
      });
    }
    
    if (report.cacheHitRate < this.alertThresholds.cacheHitRate) {
      alerts.push({
        type: 'LOW_CACHE_HIT_RATE',
        message: `Cache hit rate ${(report.cacheHitRate * 100).toFixed(1)}% below threshold`,
        severity: 'INFO'
      });
    }
    
    return alerts;
  }
}
```

## Load Testing and Benchmarking

### Query Load Testing
```javascript
class LoadTester {
  constructor(searchClient) {
    this.searchClient = searchClient;
  }
  
  async runLoadTest(queries, concurrency = 10, duration = 60000) {
    const results = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      responseTimes: [],
      errors: []
    };
    
    const startTime = Date.now();
    const workers = [];
    
    // Create worker promises
    for (let i = 0; i < concurrency; i++) {
      workers.push(this.worker(queries, startTime + duration, results));
    }
    
    // Wait for all workers to complete
    await Promise.all(workers);
    
    return this.analyzeResults(results);
  }
  
  async worker(queries, endTime, results) {
    while (Date.now() < endTime) {
      const query = queries[Math.floor(Math.random() * queries.length)];
      const startTime = Date.now();
      
      try {
        await this.searchClient.search(query);
        const responseTime = Date.now() - startTime;
        
        results.totalRequests++;
        results.successfulRequests++;
        results.responseTimes.push(responseTime);
      } catch (error) {
        results.totalRequests++;
        results.failedRequests++;
        results.errors.push(error.message);
      }
    }
  }
  
  analyzeResults(results) {
    const responseTimes = results.responseTimes.sort((a, b) => a - b);
    
    return {
      totalRequests: results.totalRequests,
      successRate: results.successfulRequests / results.totalRequests,
      averageResponseTime: responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length,
      medianResponseTime: responseTimes[Math.floor(responseTimes.length / 2)],
      p95ResponseTime: responseTimes[Math.floor(responseTimes.length * 0.95)],
      p99ResponseTime: responseTimes[Math.floor(responseTimes.length * 0.99)],
      maxResponseTime: Math.max(...responseTimes),
      minResponseTime: Math.min(...responseTimes),
      errorRate: results.failedRequests / results.totalRequests,
      uniqueErrors: [...new Set(results.errors)]
    };
  }
}
```

## Best Practices for Performance

### Query Design
- Use specific fields instead of searching all fields
- Implement appropriate pagination
- Avoid complex boolean expressions when possible
- Use filters instead of search terms when appropriate

### Caching Strategy
- Cache frequently used queries
- Implement appropriate TTL values
- Use cache invalidation strategies
- Monitor cache hit rates

### Resource Management
- Implement connection pooling
- Use appropriate service tier for workload
- Monitor resource utilization
- Scale proactively based on usage patterns

### Error Handling
- Implement retry logic with exponential backoff
- Use circuit breaker pattern for resilience
- Monitor error rates and patterns
- Provide graceful degradation

By following these performance troubleshooting guidelines and implementing proper monitoring, you can maintain fast and reliable search performance in your Azure AI Search implementation.