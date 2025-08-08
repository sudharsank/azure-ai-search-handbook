# Azure AI Search Handbook Documentation

Welcome to the comprehensive Azure AI Search learning resource!

## 🚀 Getting Started

### 1. Setup Your Environment
- **[Setup Guide](setup/)** - Complete setup instructions
- **[Azure AI Search Setup](setup/azure-ai-search-setup.md)** - Azure service configuration
- **[Quick Reference](setup/quick-reference.md)** - Essential commands

### 2. Choose Your Learning Path

#### 🟢 **Beginner Level** (New to Azure AI Search)
- [Module 1: Introduction and Setup](beginner/module-01-introduction-setup/)
- [Module 2: Basic Search Operations](beginner/module-02-basic-search/)
- [Module 3: Index Management](beginner/module-03-index-management/)
- [Module 4: Simple Queries and Filters](beginner/module-04-simple-queries/)

#### 🟡 **Intermediate Level** (Ready for advanced features)
- [Module 5: Advanced Querying](intermediate/module-05-advanced-querying/)
- [Module 6: Analyzers and Custom Scoring](intermediate/module-06-analyzers-scoring/)
- [Module 7: Facets and Aggregations](intermediate/module-07-facets-aggregations/)
- [Module 8: Security and Access Control](intermediate/module-08-security-access/)

#### 🔴 **Advanced Level** (Production-ready implementations)
- [Module 9: AI Enrichment and Cognitive Skills](advanced/module-09-ai-enrichment/)
- [Module 10: Vector Search and Semantic Search](advanced/module-10-vector-semantic-search/)
- [Module 11: Performance Optimization](advanced/module-11-performance-optimization/)
- [Module 12: Production Deployment and Monitoring](advanced/module-12-production-deployment/)

## 📁 Content Structure

Each module contains:
- **📖 Documentation** (`documentation.md`) - Comprehensive guides and explanations
- **🐍 Python Scripts** (`code-samples/*.py`) - Runnable code examples
- **📓 Jupyter Notebooks** (`code-samples/*.ipynb`) - Interactive learning experiences
- **📝 Exercises** (`exercises/*.py` and `*.ipynb`) - Hands-on practice with solutions

## 🛠️ How to Use This Handbook

### For Interactive Learning
```bash
# Start Jupyter notebooks
jupyter notebook

# Navigate to any module and open .ipynb files
# Example: docs/beginner/module-01-introduction-setup/code-samples/connection_setup.ipynb
```

### For Script-Based Learning
```bash
# Run Python scripts directly
python3 docs/beginner/module-01-introduction-setup/code-samples/connection_setup.py

# Or copy and modify for your own projects
```

### For Hands-On Practice
```bash
# Work through exercises
jupyter notebook docs/beginner/module-01-introduction-setup/exercises/exercise_01_setup.ipynb

# Check solutions and explanations included in each exercise
```

## 🎯 Learning Objectives

By completing this handbook, you will:

- **Understand** Azure AI Search architecture and capabilities
- **Implement** search solutions from basic to advanced
- **Master** indexing, querying, and data management
- **Apply** AI enrichment and cognitive skills
- **Deploy** production-ready search applications
- **Optimize** performance and manage at scale

## 📊 Progress Tracking

Track your progress through the modules:
- ✅ Complete each module's documentation
- ✅ Run all code samples successfully
- ✅ Complete all exercises
- ✅ Build your own search application

## 🆘 Getting Help

- **Setup Issues**: [Setup Documentation](setup/)
- **Module Questions**: Check each module's documentation
- **Code Problems**: Review code samples and exercises
- **Azure Issues**: [Azure AI Search Documentation](https://docs.microsoft.com/azure/search)

## 🚀 Quick Start Commands

```bash
# Check your setup
python3 setup/setup_cli.py status

# Test Azure connection
python3 scripts/test_connection.py

# Generate sample data
python3 scripts/generate_sample_data.py

# Start learning with Module 1
jupyter notebook docs/beginner/module-01-introduction-setup/
```

---

**Ready to start?** Begin with the [Setup Guide](setup/) or jump directly to [Module 1](beginner/module-01-introduction-setup/) if you already have Azure AI Search configured!