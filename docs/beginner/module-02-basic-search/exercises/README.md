# Module 2 Exercises: Basic Search Operations

This directory contains hands-on exercises designed to reinforce your understanding of basic search operations in Azure AI Search. Each exercise is a practical scenario that guides you through implementing real-world search functionality.

## 📁 Exercise Files

### Exercise 1: Tech Blog Search System
**Scenario**: Build a complete search system for a technology blog website

**Files**:
- **`exercise_01_tech_blog_search_tasks.md`** - Detailed task descriptions and requirements
- **`exercise_01_tech_blog_search.ipynb`** - Interactive Jupyter notebook with TODO tasks (no solutions)
- **`exercise_01_tech_blog_search.py`** - Python template with TODO tasks (alternative to notebook)
- **`exercise_01_tech_blog_search_solution.py`** - Complete solution with full implementations

## 🎯 Exercise 1 Overview: Tech Blog Search System

### Scenario
You are building a search system for a technology blog website that contains articles about programming, data science, web development, and emerging technologies. Your task is to implement various search features that help users find relevant content quickly and efficiently.

### Learning Objectives
By completing Exercise 1, you will master:

✅ **Core Search Operations**:
- Basic text search functionality
- Exact phrase search capabilities
- Boolean search with AND, OR, NOT operators
- Wildcard pattern matching
- Field-specific searches

✅ **Advanced Features**:
- Result processing and formatting
- Error handling and validation
- Advanced search patterns
- Smart search with auto-suggestions

✅ **Integration Skills**:
- Combining multiple search types
- Building a complete search system
- Performance optimization
- User experience considerations

### Exercise Structure

The exercise is broken down into **9 progressive tasks**:

1. **Task 0: Environment Setup** - Set up and test your search client
2. **Task 1: Basic Text Search** - Implement simple keyword searching
3. **Task 2: Exact Phrase Search** - Add exact phrase matching capabilities
4. **Task 3: Boolean Search Operations** - Build complex search logic
5. **Task 4: Wildcard Pattern Matching** - Implement pattern-based searching
6. **Task 5: Field-Specific Search** - Target specific document fields
7. **Task 6: Result Processing** - Format results for different use cases
8. **Task 7: Error Handling** - Build robust error handling
9. **Task 8: Advanced Search Patterns** - Implement intelligent search features
10. **Task 9: Integration Challenge** - Combine everything into a complete system

## 🚀 Getting Started

### Prerequisites
Before starting the exercises:

1. **Complete Module 2 Prerequisites**:
   ```bash
   cd ../code-samples/
   python setup_prerequisites.py
   ```

2. **Verify Environment**:
   - Azure AI Search service is running
   - Environment variables are set
   - `handbook-samples` index exists with sample data

3. **Install Dependencies**:
   ```bash
   pip install azure-search-documents python-dotenv
   ```

4. **For Jupyter Notebook Users** (Recommended):
   ```bash
   pip install jupyter
   jupyter notebook exercise_01_tech_blog_search.ipynb
   ```

   **Note**: The notebook contains the first 3 tasks (Environment Setup, Basic Search, Phrase Search) to get you started. For the complete exercise with all 9 tasks, use the Python file `exercise_01_tech_blog_search.py`.

### How to Use the Exercises

#### Option 1: Interactive Notebook Learning (Recommended)
1. **Read the Task Description**: Start with `exercise_01_tech_blog_search_tasks.md`
2. **Work Through Notebook**: Open `exercise_01_tech_blog_search.ipynb` in Jupyter
3. **Implement Each Task**: Fill in the TODO sections in each notebook cell
4. **Test Your Implementation**: Run cells and verify your code works
5. **Compare with Solution**: Check `exercise_01_tech_blog_search_solution.py`

#### Option 2: Python File Learning
1. **Read the Task Description**: Start with `exercise_01_tech_blog_search_tasks.md`
2. **Implement Each Task**: Work through `exercise_01_tech_blog_search.py`
3. **Test Your Implementation**: Run your code and verify it works
4. **Compare with Solution**: Check `exercise_01_tech_blog_search_solution.py`

#### Option 3: Challenge Mode
1. **Read the Scenario**: Understand the overall goal
2. **Implement Your Solution**: Build the entire system from scratch
3. **Compare Approaches**: See how your solution differs from the provided one

#### Option 4: Study Mode
1. **Review the Solution**: Examine the complete implementation in `exercise_01_tech_blog_search_solution.py`
2. **Understand the Patterns**: Learn from the code structure and techniques
3. **Modify and Experiment**: Try different approaches and improvements

## 📚 Exercise 1 Task Breakdown

### Task 0: Environment Setup
**Goal**: Set up your development environment and verify connectivity
- Import required libraries
- Create SearchClient instance
- Test connection with simple search
- Verify sample data is available

### Task 1: Basic Text Search
**Goal**: Implement simple keyword search functionality
- Create `basic_search()` function
- Handle search parameters (query, top, include_total_count)
- Display results with title, author, and score
- Test with various queries

### Task 2: Exact Phrase Search
**Goal**: Implement exact phrase matching and compare with word search
- Create `phrase_search()` function
- Use quotes for exact matching
- Compare phrase vs individual word results
- Understand when to use each approach

### Task 3: Boolean Search Operations
**Goal**: Build complex search logic with boolean operators
- Support AND, OR, NOT operations
- Handle query grouping with parentheses
- Analyze boolean operators used
- Test complex boolean queries

### Task 4: Wildcard Pattern Matching
**Goal**: Implement pattern-based searching with wildcards
- Support prefix matching (`program*`)
- Support suffix matching (`*script`)
- Support contains matching (`*data*`)
- Identify and explain pattern types

### Task 5: Field-Specific Search
**Goal**: Target specific document fields for precise searches
- Search in specific fields (title, content, author, tags)
- Support multi-field searches
- Compare field-specific vs general search
- Demonstrate field targeting benefits

### Task 6: Result Processing and Formatting
**Goal**: Process and format results for different use cases
- Format for web display (HTML)
- Format for mobile apps (compact)
- Format for API responses (JSON)
- Export to CSV format
- Filter by score threshold
- Sort by different criteria

### Task 7: Error Handling and Validation
**Goal**: Build robust search with comprehensive error handling
- Validate user input
- Handle HTTP errors gracefully
- Implement fallback search strategies
- Provide user-friendly error messages

### Task 8: Advanced Search Patterns
**Goal**: Implement intelligent search strategies
- Progressive search (specific to broad)
- Auto-suggest functionality
- Similar articles feature
- Trending searches tracking

### Task 9: Integration Challenge
**Goal**: Combine all features into a complete search system
- Unified search interface
- Automatic strategy selection
- Search analytics and caching
- Command-line interface for testing

## 🎯 Success Criteria

To successfully complete Exercise 1, your implementation should demonstrate:

### ✅ Functional Requirements
- [ ] All 8 search types work correctly
- [ ] Results are properly formatted and displayed
- [ ] Error handling prevents crashes
- [ ] Search strategies adapt to different query types

### ✅ Code Quality
- [ ] Clean, readable, and well-documented code
- [ ] Proper separation of concerns
- [ ] Consistent error handling throughout
- [ ] Efficient result processing

### ✅ User Experience
- [ ] Clear result presentation
- [ ] Helpful error messages
- [ ] Responsive search performance
- [ ] Intuitive search interface

### ✅ Technical Skills
- [ ] Proper use of Azure Search SDK
- [ ] Understanding of search concepts
- [ ] Effective debugging and testing
- [ ] Integration of multiple components

## 💡 Tips for Success

### 🎯 Implementation Strategy
1. **Start Simple**: Begin with basic search and gradually add complexity
2. **Test Frequently**: Test each function with various inputs as you build
3. **Handle Edge Cases**: Consider empty results, invalid inputs, network errors
4. **Use Sample Data**: Leverage the handbook-samples index for realistic testing

### 🔍 Debugging Tips
1. **Check Connections**: Verify your Azure Search service is accessible
2. **Validate Queries**: Use simple queries first, then add complexity
3. **Log Everything**: Use logging to understand what's happening
4. **Compare Results**: Use the solution file to compare approaches

### 📖 Learning Tips
1. **Read the Documentation**: Refer to Module 2 documentation for concepts
2. **Study the Examples**: Use the code samples as reference
3. **Experiment**: Try different queries and parameters
4. **Ask Questions**: Think about why certain approaches work better

## 🔗 Related Resources

### Module 2 Resources
- **[Module 2 Documentation](../documentation.md)** - Core concepts and theory
- **[Code Samples](../code-samples/)** - Reference implementations
- **[Best Practices](../best-practices.md)** - Guidelines and recommendations

### Azure AI Search Resources
- **[Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)**
- **[Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-search-documents/)**
- **[Query Syntax Guide](https://docs.microsoft.com/en-us/azure/search/query-simple-syntax)**

## 🚀 Next Steps

After completing Exercise 1:

1. **✅ Review Your Solution**: Compare with the provided solution
2. **🔧 Experiment Further**: Try implementing additional features
3. **📚 Explore Other Languages**: Try the same exercise in C# or JavaScript
4. **📖 Continue Learning**: Move on to Module 3: Index Management
5. **🎯 Build Projects**: Apply your skills to real-world scenarios

## 🤝 Getting Help

If you encounter issues:

1. **Check Prerequisites**: Ensure your environment is set up correctly
2. **Review Error Messages**: Look for specific error details
3. **Compare with Examples**: Use the code samples as reference
4. **Test Incrementally**: Build and test one feature at a time

---

**Ready to build your tech blog search system?** 🔍✨

Start with the task descriptions in `exercise_01_tech_blog_search_tasks.md` and begin implementing your solution in `exercise_01_tech_blog_search.py`!