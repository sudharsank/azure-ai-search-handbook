# Exercise 1: Building a Tech Blog Search System

## 🎯 Scenario

You are building a search system for a technology blog website. The blog contains articles about programming, data science, web development, and emerging technologies. Your task is to implement various search features that will help users find relevant content quickly and efficiently.

## 📚 Learning Objectives

By completing this exercise, you will:
- Implement basic text search functionality
- Create exact phrase search capabilities
- Build boolean search with AND, OR, NOT operators
- Add wildcard pattern matching
- Implement field-specific searches
- Process and format search results
- Handle errors gracefully
- Apply advanced search patterns

## ⚠️ Prerequisites

Before starting this exercise:
1. Complete the Module 2 prerequisites setup
2. Ensure your Azure AI Search service is running
3. Verify the `handbook-samples` index exists with sample data

## 🏗️ Setup Tasks

### Task 0: Environment Setup
**Goal**: Set up your development environment and verify connectivity

**Instructions**:
1. Import required libraries (`azure.search.documents`, `os`, `logging`)
2. Load environment variables for your Azure AI Search service
3. Create a SearchClient instance
4. Test the connection by performing a simple search for "*"

**Expected Output**: Connection successful message and count of documents in index

---

## 📝 Exercise Tasks

### Task 1: Basic Text Search
**Goal**: Implement a simple keyword search function

**Scenario**: A user wants to search for articles about "python programming"

**Instructions**:
1. Create a function `basic_search(query, top=10)` that:
   - Accepts a search query string
   - Returns the specified number of results
   - Includes total count in response
2. Test with queries: "python", "machine learning", "javascript"
3. Display results showing title, author, and search score

**Expected Output**: List of relevant articles with scores

---

### Task 2: Exact Phrase Search
**Goal**: Implement phrase search for exact matches

**Scenario**: A user wants to find articles that contain the exact phrase "machine learning algorithm"

**Instructions**:
1. Create a function `phrase_search(phrase, top=10)` that:
   - Wraps the phrase in quotes for exact matching
   - Compares results with individual word search
2. Test with phrases: "web development", "data science", "artificial intelligence"
3. Show the difference between phrase search and individual word search

**Expected Output**: Comparison showing phrase vs individual word results

---

### Task 3: Boolean Search Operations
**Goal**: Implement complex search logic with boolean operators

**Scenario**: Users need to combine multiple search terms with AND, OR, NOT logic

**Instructions**:
1. Create a function `boolean_search(query, top=10)` that handles:
   - AND operations: "python AND tutorial"
   - OR operations: "javascript OR typescript"
   - NOT operations: "programming NOT beginner"
   - Combined operations: "(python OR javascript) AND tutorial"
2. Test each type of boolean operation
3. Display results with explanations of the logic used

**Expected Output**: Results demonstrating different boolean logic outcomes

---

### Task 4: Wildcard Pattern Matching
**Goal**: Implement pattern-based searching with wildcards

**Scenario**: Users want to find variations of terms or partial matches

**Instructions**:
1. Create a function `wildcard_search(pattern, top=10)` that:
   - Supports prefix matching: "program*"
   - Supports suffix matching: "*script"
   - Handles multiple wildcards: "data*science"
2. Test with patterns: "web*", "*learning", "java*"
3. Show how wildcards expand the search results

**Expected Output**: Results showing pattern matches and variations found

---

### Task 5: Field-Specific Search
**Goal**: Target specific document fields for more precise searches

**Scenario**: Users want to search only in titles, or only by specific authors

**Instructions**:
1. Create a function `field_search(query, fields, top=10)` that:
   - Searches only in specified fields (title, content, author, tags)
   - Supports multi-field searches with different priorities
   - Allows field-specific queries like "title:python"
2. Test searches in different field combinations
3. Compare results when searching all fields vs specific fields

**Expected Output**: Results showing field-targeted search effectiveness

---

### Task 6: Result Processing and Formatting
**Goal**: Process and format search results for different use cases

**Scenario**: Display results in different formats for web, mobile, and API responses

**Instructions**:
1. Create a `ResultProcessor` class with methods:
   - `format_for_web(results)`: HTML-friendly format with highlighting
   - `format_for_mobile(results)`: Compact format for mobile apps
   - `format_for_api(results)`: JSON format for API responses
   - `export_to_csv(results)`: Export results to CSV format
2. Add result filtering by score threshold
3. Implement result sorting by different criteria

**Expected Output**: Same results in multiple formats

---

### Task 7: Error Handling and Validation
**Goal**: Build robust search with comprehensive error handling

**Scenario**: Handle various error conditions gracefully

**Instructions**:
1. Create a `SafeSearchClient` class that:
   - Validates user input (empty queries, special characters)
   - Handles network errors and timeouts
   - Provides fallback search strategies
   - Returns user-friendly error messages
2. Test with invalid inputs: empty strings, special characters, very long queries
3. Simulate network errors and show recovery

**Expected Output**: Graceful error handling with helpful messages

---

### Task 8: Advanced Search Patterns
**Goal**: Implement intelligent search strategies

**Scenario**: Create a smart search system that adapts to user needs

**Instructions**:
1. Create a `SmartSearch` class with methods:
   - `progressive_search(query)`: Start specific, broaden if no results
   - `auto_suggest(partial_query)`: Suggest completions
   - `similar_articles(article_id)`: Find related content
   - `trending_searches()`: Show popular search terms
2. Implement search result caching for performance
3. Add search analytics (track popular queries, success rates)

**Expected Output**: Intelligent search behavior with adaptive results

---

## 🎯 Final Challenge: Complete Search System

### Task 9: Integration Challenge
**Goal**: Combine all features into a complete search system

**Scenario**: Build a complete search interface that uses all the features you've implemented

**Instructions**:
1. Create a `TechBlogSearchSystem` class that:
   - Provides a unified interface for all search types
   - Automatically selects the best search strategy based on query
   - Includes search suggestions and auto-complete
   - Tracks and displays search statistics
2. Create a simple command-line interface for testing
3. Demonstrate all search features working together

**Expected Output**: A fully functional search system demonstrating all Module 2 concepts

---

## 📊 Success Criteria

To successfully complete this exercise, your implementation should:

✅ **Basic Functionality**:
- [ ] Perform basic text searches
- [ ] Handle exact phrase matching
- [ ] Support boolean operations (AND, OR, NOT)
- [ ] Implement wildcard pattern matching
- [ ] Enable field-specific searches

✅ **Advanced Features**:
- [ ] Process and format results in multiple formats
- [ ] Handle errors gracefully with user-friendly messages
- [ ] Implement intelligent search patterns
- [ ] Provide search suggestions and auto-complete

✅ **Code Quality**:
- [ ] Clean, readable, and well-documented code
- [ ] Proper error handling throughout
- [ ] Efficient result processing
- [ ] Good separation of concerns

✅ **User Experience**:
- [ ] Clear result presentation
- [ ] Helpful error messages
- [ ] Responsive search performance
- [ ] Intuitive search interface

## 💡 Tips for Success

1. **Start Simple**: Begin with basic search and gradually add complexity
2. **Test Frequently**: Test each function with various inputs
3. **Handle Edge Cases**: Consider empty results, invalid inputs, network errors
4. **Document Your Code**: Add clear comments explaining your logic
5. **Use the Sample Data**: Leverage the handbook-samples index for testing
6. **Refer to Examples**: Use the Module 2 code samples as reference

## 🚀 Next Steps

After completing this exercise:
1. Review the solution notebook to compare approaches
2. Try implementing the same functionality in C# or JavaScript
3. Experiment with your own search scenarios
4. Move on to Module 3: Index Management

---

**Good luck with your tech blog search system!** 🔍✨