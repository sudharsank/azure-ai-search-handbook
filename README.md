# Azure AI Search Handbook

A comprehensive learning resource for Azure AI Search, taking you from beginner to expert through hands-on practice and real-world examples.

## 🎯 Overview

This handbook provides a structured learning path for mastering Azure AI Search through:

- **Progressive Learning**: Beginner → Intermediate → Advanced modules
- **Hands-on Practice**: 120+ exercises with complete solutions
- **Real-world Examples**: Practical code samples and use cases
- **Interactive Content**: Jupyter notebooks and Python scripts
- **Comprehensive Coverage**: All Azure AI Search features and capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Azure subscription (free tier available)
- Basic programming knowledge

### Setup Options

#### Option 1: Clean Setup (Recommended)

If you have packages installed globally, clean them up first:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/azure-ai-search-handbook.git
cd azure-ai-search-handbook

# 2. Clean up global packages (optional)
python cleanup_global_install.py

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 5. Run setup
python setup/environment_setup.py
```

#### Option 2: Automatic Setup

Let the setup script handle virtual environment creation:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/azure-ai-search-handbook.git
cd azure-ai-search-handbook

# 2. Run setup (will offer to create virtual environment)
python setup/environment_setup.py

# 3. IMPORTANT: If virtual environment was created, activate it and run setup again
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows
python setup/environment_setup.py
```

> **⚠️ Important**: If the setup creates a virtual environment, you **must** activate it and run the setup again to install packages in the virtual environment rather than globally.

#### Option 3: Using CLI

```bash
# Full setup with validation
python setup/setup_cli.py setup --validate

# Or use individual commands
python setup/setup_cli.py status     # Check environment status
python setup/setup_cli.py notebooks  # Generate Jupyter notebooks
python setup/setup_cli.py test       # Test Azure connection
```

### Configuration

1. **Set up Azure AI Search service** (if you don't have one):
   ```bash
   # Interactive setup script
   python3 scripts/setup_azure_search.py
   
   # Or follow the detailed guide
   # See: docs/setup/azure-ai-search-setup.md
   ```

2. **Configure your Azure credentials**
   ```bash
   cp .env.template .env
   # Edit .env with your Azure AI Search service details:
   # AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
   # AZURE_SEARCH_API_KEY=your-api-key
   # AZURE_SEARCH_INDEX_NAME=sample-index
   ```

2. **Test your connection**
   ```bash
   python scripts/test_connection.py
   ```

3. **Generate sample data**
   ```bash
   python scripts/generate_sample_data.py
   ```

4. **Generate Jupyter notebooks**
   ```bash
   python scripts/generate_notebooks.py
   ```

### Start Learning!

- **Documentation**: `mkdocs serve` (browse at http://localhost:8000)
- **Python Scripts**: `docs/*/code-samples/*.py`
- **Jupyter Notebooks**: `docs/*/code-samples/*.ipynb`
- **Exercises**: `docs/*/exercises/*.py` and `*.ipynb`
- **Begin with**: [Module 1: Introduction and Setup](docs/beginner/module-01-introduction-setup/)

## 📖 Documentation

- **[Setup Guide](docs/setup/)** - Complete Azure AI Search service setup
- **[Quick Reference](docs/setup/quick-reference.md)** - Essential commands and troubleshooting
- **[Azure Setup Guide](docs/setup/azure-ai-search-setup.md)** - Detailed Azure service configuration

## 📚 Learning Path

### 🟢 Beginner Level
Perfect for developers new to Azure AI Search or search technologies.

- **Module 1: Introduction and Setup** - Azure AI Search fundamentals and environment setup
- **Module 2: Basic Search Operations** - Core search functionality and result handling
- **Module 3: Index Management** - Index creation, schema design, and data ingestion
- **Module 4: Simple Queries and Filters** - Query construction and basic filtering

### 🟡 Intermediate Level
For developers ready to implement sophisticated search solutions.

- **Module 5: Advanced Querying** - Complex queries, boosting, and relevance tuning
- **Module 6: Analyzers and Custom Scoring** - Text analysis and custom relevance scoring
- **Module 7: Facets and Aggregations** - Rich search experiences with faceted navigation
- **Module 8: Security and Access Control** - Authentication, authorization, and security best practices

### 🔴 Advanced Level
Expert-level topics for production-ready implementations.

- **Module 9: AI Enrichment and Cognitive Skills** - AI-powered content enhancement
- **Module 10: Vector Search and Semantic Search** - Modern search capabilities with embeddings
- **Module 11: Performance Optimization** - Scaling, caching, and performance tuning
- **Module 12: Production Deployment and Monitoring** - Enterprise deployment and operations

## 🛠️ Repository Structure

```
azure-ai-search-handbook/
├── docs/                           # Documentation and learning materials
│   ├── beginner/                   # Beginner level modules
│   │   ├── module-01-introduction-setup/
│   │   │   ├── documentation.md    # Module documentation
│   │   │   ├── code-samples/       # Python scripts (.py) and notebooks (.ipynb)
│   │   │   └── exercises/          # Hands-on exercises (.py and .ipynb)
│   │   └── [other modules...]
│   ├── intermediate/               # Intermediate level modules
│   ├── advanced/                   # Advanced level modules
│   └── reference/                  # Quick reference and troubleshooting
├── setup/                          # Environment setup and utilities
│   ├── environment_setup.py       # Main setup script
│   ├── setup_cli.py               # Command-line interface
│   ├── notebook_generator.py      # Jupyter notebook generator
│   └── [other setup files...]
├── scripts/                        # Utility scripts
│   ├── test_connection.py         # Test Azure AI Search connection
│   ├── generate_sample_data.py    # Generate sample data
│   └── generate_notebooks.py      # Generate Jupyter notebooks
├── config/                         # Configuration templates
├── data/                          # Sample data and datasets
├── logs/                          # Application logs
├── venv/                          # Virtual environment (after setup)
├── mkdocs.yml                     # Documentation site configuration
├── requirements.txt               # Python dependencies
├── .env.template                  # Environment variables template
├── cleanup_global_install.py      # Global package cleanup script
└── README.md                      # This file
```

### Module Structure

Each learning module contains:
- **📖 Documentation**: Comprehensive guides and explanations (`documentation.md`)
- **🐍 Python Scripts**: Runnable code samples (`.py` files)
- **📓 Jupyter Notebooks**: Interactive learning experiences (`.ipynb` files)
- **📝 Exercises**: 10+ hands-on exercises with starter code and solutions
- **✅ Solutions**: Complete implementations with detailed explanations

### File Types

- **`.py` files**: Standalone Python scripts that can be run directly
- **`.ipynb` files**: Interactive Jupyter notebooks with explanations and exercises
- **Both formats available**: Every code sample and exercise comes in both formats

## 🔧 CLI Commands

The handbook includes a comprehensive CLI for managing your environment:

```bash
# Environment setup and validation
python setup/setup_cli.py setup                    # Full environment setup
python setup/setup_cli.py setup --validate         # Setup with validation
python setup/setup_cli.py validate                 # Validate environment only
python setup/setup_cli.py status                   # Show environment status

# Content generation
python setup/setup_cli.py notebooks                # Generate Jupyter notebooks
python setup/setup_cli.py data --count 50          # Generate sample data

# Testing and configuration
python setup/setup_cli.py test                     # Test Azure connection
python setup/setup_cli.py test --verbose           # Test with detailed info
python setup/setup_cli.py config complete          # Create complete config set

# Quick setup
python setup/setup_cli.py quick --name my-project  # Quick setup everything
```

## 🌐 Online Documentation

Visit the online documentation at: [https://your-username.github.io/azure-ai-search-handbook](https://your-username.github.io/azure-ai-search-handbook)

### Local Development

Run the documentation locally:
```bash
mkdocs serve
```

### GitHub Pages Deployment

The documentation is automatically deployed to GitHub Pages on every push to the main branch:

1. **Automatic Deployment**: GitHub Actions builds and deploys the site
2. **Live Updates**: Changes are reflected within minutes of pushing
3. **Build Status**: Check the Actions tab for deployment status

To set up GitHub Pages for your fork:
1. Go to repository Settings → Pages
2. Set Source to "GitHub Actions"
3. Update the repository URLs in `mkdocs.yml`
4. Push to main branch to trigger deployment

See [deployment/github-pages-setup.md](deployment/github-pages-setup.md) for detailed setup instructions.

## 🔍 Environment Testing

To test your environment setup:

1. **Check environment status**:
   ```bash
   python setup/setup_cli.py status
   ```
   This should show:
   - ✅ Key files exist
   - ✅ Directories created
   - ❌ Environment variables (until you configure .env)

2. **Test CLI functionality**:
   ```bash
   python setup/setup_cli.py --help
   python setup/setup_cli.py notebooks  # Generate notebooks
   ```

3. **Set up and test Azure AI Search**:
   ```bash
   # Option 1: Interactive setup (recommended)
   python3 scripts/setup_azure_search.py
   
   # Option 2: Manual setup
   cp .env.template .env
   # Edit .env with your Azure AI Search credentials
   # See: docs/setup/azure-ai-search-setup.md for detailed instructions
   
   # Test connection
   python scripts/test_connection.py
   ```

4. **View documentation and test notebooks**:
   ```bash
   # Serve documentation (multiple options)
   mkdocs serve                           # Default (may need flags)
   python3 setup/setup_cli.py docs       # Using CLI
   python3 scripts/serve_docs.py         # Using script
   ./serve-docs.sh                       # Using shell script
   
   # Or start Jupyter for interactive notebooks
   jupyter notebook
   # Browse to any .ipynb file in docs/*/code-samples/ or docs/*/exercises/
   ```

5. **Validate complete setup** (after .env configuration):
   ```bash
   python setup/validate_setup.py
   ```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Virtual Environment Issues**:
```bash
# If virtual environment creation fails
python3 -m pip install --upgrade pip
python3 -m venv venv --clear

# If activation doesn't work
# On macOS/Linux: source venv/bin/activate
# On Windows: venv\Scripts\activate
```

**Package Installation Issues**:
```bash
# Clean up global packages first
python cleanup_global_install.py

# Upgrade pip in virtual environment
pip install --upgrade pip
pip install -r requirements.txt
```

**Azure Connection Issues**:
```bash
# Check your .env file configuration
python setup/setup_cli.py status

# Test connection with verbose output
python setup/setup_cli.py test --verbose

# Set up Azure AI Search service
python3 scripts/setup_azure_search.py

# See detailed setup guide
# docs/setup/azure-ai-search-setup.md
```

**Notebook Generation Issues**:
```bash
# Manually generate notebooks
python setup/setup_cli.py notebooks

# Check if Jupyter is installed
pip install jupyter notebook
```

### Getting Help

If you encounter issues:

1. **Check Status**: Run `python setup/setup_cli.py status`
2. **Validate Setup**: Run `python setup/validate_setup.py`
3. **Check Logs**: Look in the `logs/` directory for error details
4. **Clean Restart**: Use `python cleanup_global_install.py` and start fresh

## 🆘 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/your-username/azure-ai-search-handbook/issues)
- **Discussions**: Join the community in [GitHub Discussions](https://github.com/your-username/azure-ai-search-handbook/discussions)
- **Documentation**: Check the [troubleshooting guide](docs/reference/troubleshooting.md)

## 🏷️ Tags

`azure` `search` `ai` `machine-learning` `python` `tutorial` `handbook` `cognitive-search` `vector-search` `semantic-search`

---

**Happy Learning!** 🎉

Start your Azure AI Search journey today with [Module 1: Introduction and Setup](docs/beginner/module-01-introduction-setup/documentation.md).