# Azure AI Search Quick Reference

## Essential Commands

### Environment Setup
```bash
# Full environment setup
python3 setup/environment_setup.py

# CLI setup with validation
python3 setup/setup_cli.py setup --validate

# Check environment status
python3 setup/setup_cli.py status
```

### Azure AI Search Setup
```bash
# Interactive Azure setup
python3 scripts/setup_azure_search.py

# Test connection
python3 scripts/test_connection.py

# Test with verbose output
python3 setup/setup_cli.py test --verbose
```

### Content Generation
```bash
# Generate Jupyter notebooks
python3 setup/setup_cli.py notebooks

# Generate sample data
python3 scripts/generate_sample_data.py

# Start Jupyter
jupyter notebook
```

## Configuration Files

### .env File Template
```bash
# Required Azure AI Search settings
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key-here
AZURE_SEARCH_INDEX_NAME=sample-index

# Optional settings
LOG_LEVEL=INFO
ENVIRONMENT=development
SAMPLE_DATA_COUNT=100
```

### Directory Structure
```
azure-ai-search-handbook/
├── docs/
│   ├── setup/                    # Setup documentation
│   ├── beginner/                 # Beginner modules
│   ├── intermediate/             # Intermediate modules
│   └── advanced/                 # Advanced modules
├── scripts/                      # Utility scripts
├── setup/                        # Setup utilities
├── deployment/                   # ARM templates
├── config/                       # Configuration files
├── data/                         # Sample data
└── logs/                         # Application logs
```

## Azure AI Search Pricing

| Tier | Price | Storage | Indexes | Best For |
|------|-------|---------|---------|----------|
| Free | $0 | 50 MB | 3 | Learning |
| Basic | ~$250/month | 2 GB | 15 | Development |
| Standard S1 | ~$250/month | 25 GB | 50 | Production |

## Common Issues & Solutions

### "Service name already exists"
- Service names must be globally unique
- Try: `my-search-service-{your-initials}-{random-number}`

### "Connection failed"
- Check endpoint URL format: `https://service-name.search.windows.net`
- Verify API key is admin key (not query key)
- Test with: `python3 scripts/test_connection.py`

### "Module not found: azure"
- Ensure you're in virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "Quota exceeded"
- Free tier allows only 1 service per subscription
- Delete existing service or upgrade to paid tier

## Learning Path

1. **Setup** → `docs/setup/azure-ai-search-setup.md`
2. **Module 1** → `docs/beginner/module-01-introduction-setup/`
3. **Exercises** → `docs/*/exercises/*.ipynb`
4. **Advanced** → `docs/advanced/`

## Useful Links

- **Azure Portal**: [portal.azure.com](https://portal.azure.com)
- **Azure AI Search Docs**: [docs.microsoft.com/azure/search](https://docs.microsoft.com/azure/search)
- **Azure CLI**: [docs.microsoft.com/cli/azure](https://docs.microsoft.com/cli/azure)
- **Pricing Calculator**: [azure.microsoft.com/pricing/calculator](https://azure.microsoft.com/pricing/calculator)

## Support

- **Setup Issues**: Check `docs/setup/azure-ai-search-setup.md`
- **Connection Problems**: Run `python3 setup/setup_cli.py status`
- **Azure Issues**: Use Azure portal support or community forums