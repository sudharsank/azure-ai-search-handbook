# Module 5: Data Sources & Indexers - Overview

## Introduction

This module covers data sources and indexers - the backbone of automated data ingestion in Azure AI Search. You'll learn how to connect to various Azure data sources, configure indexers for automated data processing, and implement robust data ingestion pipelines. By the end of this module, you'll be comfortable building production-ready indexing workflows.

## Learning Objectives

By completing this module, you will be able to:

- ✅ **Create and configure data source connections** to Azure SQL Database, Blob Storage, and Cosmos DB
- ✅ **Set up automated indexers** with optimized configurations for different data types
- ✅ **Implement change detection strategies** for efficient incremental updates
- ✅ **Configure field mappings** for data transformation and schema alignment
- ✅ **Schedule indexer execution** with automated monitoring and alerting
- ✅ **Handle errors gracefully** with retry logic and resilient pipeline design
- ✅ **Monitor and optimize performance** for production workloads
- ✅ **Troubleshoot common indexing issues** with confidence

## Module Structure

This module is organized into focused sections for better learning:

### 📚 **Core Documentation**
- **[📖 Overview](documentation.md)** - This page: module introduction and structure
- **[🔧 Prerequisites](prerequisites.md)** - Setup requirements and environment preparation
- **[💡 Best Practices](best-practices.md)** - Guidelines and recommendations for production
- **[🛠️ Practice & Implementation](practice-implementation.md)** - Hands-on exercises and examples

### 🔧 **Troubleshooting Guides**
- **[⚙️ Indexer Troubleshooting](indexer-troubleshooting.md)** - Common indexer issues and solutions
- **[🔗 Data Source Troubleshooting](datasource-troubleshooting.md)** - Connection and configuration problems

### 🎯 **Hands-On Learning**
- **[📁 Code Samples Directory](code-samples/)** - All language implementations and examples

## What You'll Learn

### 🔗 **Data Source Fundamentals**
- **Connection Configuration**: Setting up secure connections to Azure data sources
- **Authentication Methods**: Using connection strings, managed identity, and service principals
- **Container Specifications**: Defining tables, containers, and query parameters
- **Change Detection Policies**: Implementing efficient incremental update strategies

### ⚙️ **Indexer Management**
- **Automated Data Extraction**: Configuring indexers for different data source types
- **Field Mappings**: Transforming data between source and target schemas
- **Scheduling & Automation**: Setting up regular execution patterns
- **Error Handling**: Building resilient pipelines with retry logic

### 📊 **Advanced Features**
- **Performance Optimization**: Tuning batch sizes and execution parameters
- **Monitoring & Alerting**: Tracking indexer health and performance metrics
- **Complex Transformations**: Using built-in mapping functions and custom logic
- **Multi-source Integration**: Coordinating multiple indexers and data sources

### 🛡️ **Production Readiness**
- **Error Recovery**: Comprehensive error handling and retry strategies
- **Performance Monitoring**: Tracking execution metrics and resource usage
- **Security Best Practices**: Secure connection management and access control
- **Operational Excellence**: Monitoring, logging, and maintenance procedures

## Multi-Language Support

This module provides complete implementations in multiple programming languages:

| Language | Best For | Key Features |
|----------|----------|--------------|
| 🐍 **Python** | Data science, automation scripts | Comprehensive examples, Jupyter notebooks |
| 🔷 **C#** | Enterprise applications, .NET ecosystem | Strongly-typed, production-ready examples |
| 🟨 **JavaScript** | Web development, Node.js applications | Modern async/await patterns, comprehensive error handling |
| 🌐 **REST API** | Any language, direct HTTP integration | Universal compatibility, debugging examples |

## Learning Paths

### 🎯 **Beginner Path** (Recommended)
1. **Start Here**: Read this overview and understand key concepts
2. **Setup**: Complete [Prerequisites](prerequisites.md) setup
3. **Practice**: Follow [Practice & Implementation](practice-implementation.md) guide
4. **Choose Language**: Pick your preferred programming language
5. **Build**: Apply concepts in your own data ingestion scenarios

### ⚡ **Quick Start Path**
1. **Prerequisites**: Run the setup script for your environment
2. **Basic Example**: Try the Azure SQL indexer example
3. **Language Examples**: Jump to your preferred language implementation
4. **Experiment**: Modify examples with your own data sources

### 🔬 **Deep Dive Path**
1. **Theory**: Read all documentation sections thoroughly
2. **Practice**: Work through all 8 code sample categories
3. **Troubleshooting**: Study common issues and solutions
4. **Best Practices**: Implement production-ready patterns
5. **Advanced**: Explore performance optimization and monitoring

## Code Sample Categories

This module includes 8 comprehensive code sample categories:

### 🗄️ **Data Source Examples**
1. **Azure SQL Indexer** - Relational database indexing with change tracking
2. **Blob Storage Indexer** - Document processing and metadata extraction  
3. **Cosmos DB Indexer** - NoSQL data indexing with change feeds

### ⚙️ **Advanced Configuration**
4. **Change Detection** - Efficient incremental update strategies
5. **Indexer Scheduling** - Automated execution and monitoring
6. **Field Mappings** - Data transformation and schema mapping

### 🛡️ **Production Features**
7. **Error Handling** - Resilient pipeline implementation
8. **Monitoring & Optimization** - Performance tracking and tuning

Each category includes complete, runnable examples with comprehensive error handling, logging, and best practices.

## Practical Scenarios

### 🛒 **E-commerce Product Catalog**
**Goal**: Index product data from SQL Database with automatic updates
**Path**: SQL Indexer → Change Detection → Scheduling → Monitoring
**Skills**: Relational data indexing, change tracking, automation

### 📄 **Document Management System**
**Goal**: Process various document types from blob storage
**Path**: Blob Indexer → Field Mappings → Error Handling
**Skills**: Document processing, metadata extraction, error recovery

### 👥 **Customer Data Integration**
**Goal**: Index customer data from Cosmos DB with real-time updates
**Path**: Cosmos Indexer → Change Detection → Monitoring
**Skills**: NoSQL indexing, change feeds, performance monitoring

## Success Metrics

By the end of this module, you should be able to:

- [ ] Successfully create data sources for SQL Database, Blob Storage, and Cosmos DB
- [ ] Configure indexers with appropriate settings for different data types
- [ ] Implement efficient change detection strategies
- [ ] Set up automated indexing schedules with monitoring
- [ ] Handle errors gracefully with retry logic
- [ ] Monitor indexer performance and optimize for production
- [ ] Troubleshoot common indexing issues independently
- [ ] Apply best practices for secure and reliable data ingestion

## Time Investment

- **Prerequisites Setup**: 15-20 minutes
- **Core Concepts**: 45-60 minutes reading
- **Hands-On Practice**: 2-4 hours (depending on language choice and depth)
- **Total Module**: 3-5 hours for comprehensive understanding

## Next Steps

Ready to get started? Here's your roadmap:

1. **📋 [Complete Prerequisites](prerequisites.md)** - Essential setup (20 minutes)
2. **🎯 [Start Practice & Implementation](practice-implementation.md)** - Choose your learning path
3. **💡 [Review Best Practices](best-practices.md)** - Learn professional techniques
4. **🛠️ [Bookmark Troubleshooting Guides](indexer-troubleshooting.md)** - For when you need help

---

**Ready to build automated data ingestion pipelines?** Start with the [Prerequisites](prerequisites.md) to set up your environment! 🚀