# Module 2: Best Practices

## Overview

This guide covers best practices for implementing Azure AI Search basic operations in production applications. These practices ensure optimal performance, security, maintainability, and user experience.

## 🔍 Search Query Best Practices

### Query Design

#### ✅ **Use Appropriate Search Types**
```python
# For exact matches
results = search_client.search('"machine learning"')  # Phrase search

# For flexible matching
results = search_client.search('machine learning', search_mode='any')  # Any terms

# For precise matching
results = search_client.search('machine AND learning')  # Boolean search

# For partial matching
results = search_client.search('mach*')  # Wildcard search
```

#### ✅ **Optimize Query Structure**
```python
# Good: Specific and targeted
query = 'python tutorial beginner'

# Better: Use field-specific search when possible
results = search_client.search(
    'python tutorial',
    search_fields=['title', 'description']
)

# Best: Combine with filters for precision
results = search_client.search(
    'python tutorial',
    search_fields=['title', 'description'],
    filter="difficulty eq 'Beginner' and rating ge 4.0"
)
```

#### ✅ **Handle User Input Safely**
```python
import re

def sanitize_query(user_input):
    """Sanitize user input for safe searching"""
    if not user_input or not user_input.strip():
        return None
    
    # Remove potentially problematic characters
    sanitized = re.sub(r'[<>]', '', user_input.strip())
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized

# Usage
user_query = sanitize_query(request.get('q'))
if user_query:
    results = search_client.search(user_query)
```

### Performance Optimization

#### ✅ **Limit Result Sets**
```python
# Always specify reasonable limits
results = search_client.search(
    query,
    top=20,  # Don't return more than needed
    skip=0   # For pagination
)
```

#### ✅ **Select Only Required Fields**
```python
# Instead of returning all fields
results = search_client.search(query)

# Return only what you need
results = search_client.search(
    query,
    select=['id', 'title', 'author', 'publishedDate']
)
```

#### ✅ **Use Field-Specific Search**
```python
# More efficient than searching all fields
results = search_client.search(
    query,
    search_fields=['title', 'description']  # Target specific fields
)
```

## 🛡️ Error Handling Best Practices

### Comprehensive Error Handling

#### ✅ **Handle Specific Error Types**
```python
from azure.core.exceptions import HttpResponseError
import logging

def safe_search(search_client, query, **kwargs):
    """Perform search with comprehensive error handling"""
    try:
        results = search_client.search(query, **kwargs)
        return list(results), None
        
    except HttpResponseError as e:
        error_msg = handle_http_error(e)
        logging.error(f"Search HTTP error: {error_msg}")
        return [], error_msg
        
    except Exception as e:
        error_msg = f"Unexpected search error: {str(e)}"
        logging.error(error_msg)
        return [], error_msg

def handle_http_error(error):
    """Convert HTTP errors to user-friendly messages"""
    status_code = error.status_code
    
    error_messages = {
        400: "Invalid search query. Please check your search terms.",
        401: "Authentication failed. Please check your credentials.",
        403: "Access denied. Insufficient permissions.",
        404: "Search index not found.",
        429: "Too many requests. Please wait and try again.",
        503: "Search service temporarily unavailable."
    }
    
    return error_messages.get(status_code, f"Search error: {error.message}")
```

#### ✅ **Implement Fallback Strategies**
```python
def search_with_fallback(search_client, query):
    """Search with progressive fallback strategies"""
    strategies = [
        (f'"{query}"', "exact phrase"),
        (query, "all terms"),
        (query.replace(' ', ' OR '), "any terms"),
        (' OR '.join(f"{term}*" for term in query.split()), "wildcard")
    ]
    
    for search_query, strategy_name in strategies:
        try:
            results = list(search_client.search(search_query, top=10))
            if results:
                logging.info(f"Found {len(results)} results using {strategy_name}")
                return results
        except Exception as e:
            logging.warning(f"Strategy '{strategy_name}' failed: {e}")
            continue
    
    return []
```

### Input Validation

#### ✅ **Validate Before Searching**
```python
def validate_search_input(query, max_length=1000):
    """Validate search input before processing"""
    errors = []
    
    if not query:
        errors.append("Search query cannot be empty")
    elif not query.strip():
        errors.append("Search query cannot be just whitespace")
    elif len(query) > max_length:
        errors.append(f"Search query too long (max {max_length} characters)")
    elif len(query.strip()) < 2:
        errors.append("Search query must be at least 2 characters")
    
    return errors

# Usage
def perform_search(user_query):
    validation_errors = validate_search_input(user_query)
    if validation_errors:
        return {"errors": validation_errors, "results": []}
    
    sanitized_query = sanitize_query(user_query)
    results, error = safe_search(search_client, sanitized_query)
    
    return {"results": results, "error": error}
```

## 📊 Result Processing Best Practices

### Efficient Result Handling

#### ✅ **Process Results Efficiently**
```python
def process_search_results(results, max_preview_length=200):
    """Process search results for optimal display"""
    processed_results = []
    
    for result in results:
        # Extract core fields safely
        processed_result = {
            'id': result.get('id', ''),
            'title': result.get('title', 'Untitled'),
            'score': result.get('@search.score', 0.0),
            'author': result.get('author', 'Unknown'),
            'url': result.get('url', '#')
        }
        
        # Create content preview
        content = result.get('content', '')
        if content:
            preview = content[:max_preview_length]
            if len(content) > max_preview_length:
                # Find good breaking point
                last_space = preview.rfind(' ')
                if last_space > max_preview_length * 0.8:
                    preview = preview[:last_space]
                preview += '...'
            processed_result['preview'] = preview
        
        processed_results.append(processed_result)
    
    return processed_results
```

#### ✅ **Implement Smart Pagination**
```python
class SearchPaginator:
    def __init__(self, search_client, page_size=20):
        self.search_client = search_client
        self.page_size = page_size
    
    def get_page(self, query, page_number=1, **search_options):
        """Get a specific page of results"""
        skip = (page_number - 1) * self.page_size
        
        try:
            results = self.search_client.search(
                query,
                top=self.page_size,
                skip=skip,
                include_total_count=True,
                **search_options
            )
            
            result_list = list(results)
            total_count = getattr(results, 'get_count', lambda: 0)()
            total_pages = (total_count + self.page_size - 1) // self.page_size
            
            return {
                'results': result_list,
                'page': page_number,
                'page_size': self.page_size,
                'total_results': total_count,
                'total_pages': total_pages,
                'has_next': page_number < total_pages,
                'has_previous': page_number > 1
            }
            
        except Exception as e:
            logging.error(f"Pagination error: {e}")
            return {
                'results': [],
                'error': str(e),
                'page': page_number,
                'total_results': 0
            }
```

### Score Analysis

#### ✅ **Analyze and Use Search Scores**
```python
def analyze_result_quality(results, min_quality_score=1.0):
    """Analyze search result quality and provide insights"""
    if not results:
        return {"quality": "no_results", "recommendation": "Try broader search terms"}
    
    scores = [r.get('@search.score', 0) for r in results]
    
    analysis = {
        'total_results': len(results),
        'score_range': {'min': min(scores), 'max': max(scores)},
        'average_score': sum(scores) / len(scores),
        'high_quality_count': len([s for s in scores if s >= min_quality_score])
    }
    
    # Provide recommendations
    if analysis['high_quality_count'] == 0:
        analysis['quality'] = 'low'
        analysis['recommendation'] = 'Try different search terms or use broader matching'
    elif analysis['high_quality_count'] >= len(results) * 0.7:
        analysis['quality'] = 'high'
        analysis['recommendation'] = 'Results look highly relevant'
    else:
        analysis['quality'] = 'mixed'
        analysis['recommendation'] = 'Consider filtering by score or refining query'
    
    return analysis
```

## 🔒 Security Best Practices

### API Key Management

#### ✅ **Secure Credential Handling**
```python
import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential

def get_search_client(use_managed_identity=False):
    """Get search client with secure credential handling"""
    endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
    index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
    
    if not endpoint or not index_name:
        raise ValueError("Missing required environment variables")
    
    if use_managed_identity:
        # Preferred for production
        credential = DefaultAzureCredential()
    else:
        # For development/testing
        api_key = os.getenv('AZURE_SEARCH_API_KEY')
        if not api_key:
            raise ValueError("API key not found in environment variables")
        credential = AzureKeyCredential(api_key)
    
    return SearchClient(endpoint, index_name, credential)
```

#### ✅ **Use Appropriate Key Types**
```python
# For different environments
class SearchClientFactory:
    @staticmethod
    def create_for_environment(environment='development'):
        """Create search client appropriate for environment"""
        if environment == 'production':
            # Use managed identity in production
            return get_search_client(use_managed_identity=True)
        elif environment == 'development':
            # Use API key for development
            return get_search_client(use_managed_identity=False)
        else:
            raise ValueError(f"Unknown environment: {environment}")
```

### Input Sanitization

#### ✅ **Prevent Injection Attacks**
```python
import html
import re

def secure_query_processing(user_input):
    """Securely process user search input"""
    if not user_input:
        return None
    
    # HTML escape to prevent XSS
    escaped = html.escape(user_input)
    
    # Remove potentially dangerous patterns
    # Remove script tags, SQL injection patterns, etc.
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'--',  # SQL comment
        r';.*drop\s+table',  # SQL injection
    ]
    
    cleaned = escaped
    for pattern in dangerous_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Normalize and limit length
    cleaned = re.sub(r'\s+', ' ', cleaned.strip())[:1000]
    
    return cleaned
```

## 🚀 Performance Best Practices

### Caching Strategies

#### ✅ **Implement Result Caching**
```python
import hashlib
import json
from datetime import datetime, timedelta

class SearchCache:
    def __init__(self, cache_duration_minutes=30):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def _get_cache_key(self, query, options):
        """Generate cache key from query and options"""
        cache_data = {'query': query, 'options': options}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, query, options):
        """Get cached results if available and not expired"""
        cache_key = self._get_cache_key(query, options)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['results']
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        return None
    
    def set(self, query, options, results):
        """Cache search results"""
        cache_key = self._get_cache_key(query, options)
        self.cache[cache_key] = {
            'results': results,
            'timestamp': datetime.now()
        }
    
    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, data in self.cache.items()
            if now - data['timestamp'] >= self.cache_duration
        ]
        for key in expired_keys:
            del self.cache[key]

# Usage
search_cache = SearchCache(cache_duration_minutes=15)

def cached_search(query, **options):
    """Search with caching"""
    # Try cache first
    cached_results = search_cache.get(query, options)
    if cached_results is not None:
        return cached_results
    
    # Perform search
    results = list(search_client.search(query, **options))
    
    # Cache results
    search_cache.set(query, options, results)
    
    return results
```

### Connection Management

#### ✅ **Reuse Search Client Instances**
```python
# Good: Singleton pattern for search client
class SearchService:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self):
        if self._client is None:
            self._client = get_search_client()
        return self._client

# Usage
search_service = SearchService()
search_client = search_service.get_client()
```

## 📱 User Experience Best Practices

### Search Interface Design

#### ✅ **Provide Search Feedback**
```python
def search_with_feedback(query, search_client):
    """Search with user feedback"""
    start_time = time.time()
    
    try:
        results = list(search_client.search(query, top=20))
        search_time = time.time() - start_time
        
        feedback = {
            'query': query,
            'results_count': len(results),
            'search_time': round(search_time, 3),
            'status': 'success'
        }
        
        if len(results) == 0:
            feedback['suggestion'] = 'Try different keywords or check spelling'
        elif len(results) < 5:
            feedback['suggestion'] = 'Try broader search terms for more results'
        
        return results, feedback
        
    except Exception as e:
        return [], {
            'query': query,
            'status': 'error',
            'error': str(e),
            'suggestion': 'Please try again or contact support'
        }
```

#### ✅ **Implement Search Suggestions**
```python
def get_search_suggestions(partial_query, search_client):
    """Get search suggestions based on partial input"""
    if len(partial_query) < 2:
        return []
    
    try:
        # Use wildcard search for suggestions
        suggestion_query = f"{partial_query}*"
        results = search_client.search(
            suggestion_query,
            search_fields=['title'],
            select=['title'],
            top=5
        )
        
        suggestions = []
        seen_titles = set()
        
        for result in results:
            title = result.get('title', '')
            if title and title not in seen_titles:
                suggestions.append(title)
                seen_titles.add(title)
        
        return suggestions[:5]  # Limit to 5 suggestions
        
    except Exception:
        return []  # Fail silently for suggestions
```

### Result Presentation

#### ✅ **Format Results for Different Contexts**
```python
class ResultFormatter:
    @staticmethod
    def for_web(results):
        """Format results for web display"""
        return [
            {
                'id': r.get('id'),
                'title': r.get('title', 'Untitled'),
                'snippet': ResultFormatter._create_snippet(r.get('content', '')),
                'author': r.get('author', 'Unknown'),
                'score': round(r.get('@search.score', 0), 2),
                'url': r.get('url', '#')
            }
            for r in results
        ]
    
    @staticmethod
    def for_api(results):
        """Format results for API response"""
        return {
            'results': [
                {
                    'id': r.get('id'),
                    'title': r.get('title'),
                    'score': r.get('@search.score'),
                    'fields': {k: v for k, v in r.items() if not k.startswith('@')}
                }
                for r in results
            ],
            'count': len(results)
        }
    
    @staticmethod
    def _create_snippet(content, max_length=150):
        """Create content snippet"""
        if not content or len(content) <= max_length:
            return content
        
        snippet = content[:max_length]
        last_space = snippet.rfind(' ')
        if last_space > max_length * 0.8:
            snippet = snippet[:last_space]
        
        return snippet + '...'
```

## 📊 Monitoring and Analytics

### Search Analytics

#### ✅ **Track Search Metrics**
```python
import logging
from datetime import datetime

class SearchAnalytics:
    def __init__(self):
        self.logger = logging.getLogger('search_analytics')
    
    def log_search(self, query, results_count, search_time, user_id=None):
        """Log search event for analytics"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': results_count,
            'search_time_ms': round(search_time * 1000, 2),
            'user_id': user_id
        }
        
        self.logger.info(f"SEARCH_EVENT: {json.dumps(event)}")
    
    def log_no_results(self, query, user_id=None):
        """Log when searches return no results"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'no_results',
            'query': query,
            'user_id': user_id
        }
        
        self.logger.warning(f"NO_RESULTS: {json.dumps(event)}")

# Usage
analytics = SearchAnalytics()

def monitored_search(query, user_id=None):
    """Search with monitoring"""
    start_time = time.time()
    
    try:
        results = list(search_client.search(query))
        search_time = time.time() - start_time
        
        analytics.log_search(query, len(results), search_time, user_id)
        
        if len(results) == 0:
            analytics.log_no_results(query, user_id)
        
        return results
        
    except Exception as e:
        analytics.logger.error(f"Search error for query '{query}': {e}")
        raise
```

## 🔄 Testing Best Practices

### Unit Testing

#### ✅ **Test Search Functionality**
```python
import unittest
from unittest.mock import Mock, patch

class TestSearchFunctionality(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.search_service = SearchService()
        self.search_service._client = self.mock_client
    
    def test_safe_search_success(self):
        """Test successful search"""
        # Mock successful response
        mock_results = [{'title': 'Test', '@search.score': 1.0}]
        self.mock_client.search.return_value = mock_results
        
        results, error = safe_search(self.mock_client, "test query")
        
        self.assertEqual(len(results), 1)
        self.assertIsNone(error)
        self.mock_client.search.assert_called_once_with("test query")
    
    def test_safe_search_http_error(self):
        """Test HTTP error handling"""
        from azure.core.exceptions import HttpResponseError
        
        # Mock HTTP error
        http_error = HttpResponseError("Bad request")
        http_error.status_code = 400
        self.mock_client.search.side_effect = http_error
        
        results, error = safe_search(self.mock_client, "bad query")
        
        self.assertEqual(len(results), 0)
        self.assertIn("Invalid search query", error)
    
    def test_query_validation(self):
        """Test input validation"""
        # Test empty query
        errors = validate_search_input("")
        self.assertIn("cannot be empty", errors[0])
        
        # Test too long query
        long_query = "x" * 1001
        errors = validate_search_input(long_query)
        self.assertIn("too long", errors[0])
        
        # Test valid query
        errors = validate_search_input("valid query")
        self.assertEqual(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
```

## 📋 Checklist for Production

### Pre-Deployment Checklist

- [ ] **Security**

    - [ ] API keys stored securely (environment variables/key vault)
    - [ ] Input validation implemented
    - [ ] Query sanitization in place
    - [ ] Appropriate authentication method chosen

- [ ] **Performance**

    - [ ] Result limits implemented
    - [ ] Field selection optimized
    - [ ] Caching strategy in place
    - [ ] Connection pooling configured

- [ ] **Error Handling**

    - [ ] All error types handled
    - [ ] User-friendly error messages
    - [ ] Fallback strategies implemented
    - [ ] Logging configured

- [ ] **Monitoring**

    - [ ] Search analytics implemented
    - [ ] Performance monitoring in place
    - [ ] Error tracking configured
    - [ ] Health checks implemented

- [ ] **Testing**

    - [ ] Unit tests written
    - [ ] Integration tests completed
    - [ ] Load testing performed
    - [ ] Error scenarios tested

---

**Ready for production?** These best practices will help you build robust, secure, and performant search applications. Remember to adapt these patterns to your specific use case and requirements! 🚀