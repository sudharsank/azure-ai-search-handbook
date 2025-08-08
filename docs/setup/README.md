# Setup Documentation

This directory contains comprehensive setup guides for the Azure AI Search Handbook.

## 📋 Setup Guides

### 🚀 [Azure AI Search Service Setup](azure-ai-search-setup.md)
Complete guide for setting up your Azure AI Search service with multiple deployment options:
- Azure Portal setup (recommended for beginners)
- Azure CLI setup (for advanced users)
- ARM template deployment (for automation)
- Security best practices and troubleshooting

### ⚡ [Quick Reference](quick-reference.md)
Essential commands, configuration templates, and troubleshooting tips for quick access.

## 🛠️ Setup Scripts

### Interactive Setup
```bash
# Set up Azure AI Search service interactively
python3 scripts/setup_azure_search.py
```

### Environment Setup
```bash
# Set up development environment
python3 setup/environment_setup.py

# Or use CLI
python3 setup/setup_cli.py setup --validate
```

## 📁 Deployment Resources

### ARM Templates
- **[azure-search-template.json](../deployment/azure-search-template.json)**: Azure Resource Manager template for automated deployment
- Supports all pricing tiers and configuration options
- Includes managed identity setup

### Configuration Files
- **[.env.template](../../.env.template)**: Environment variables template
- **[requirements.txt](../../requirements.txt)**: Python dependencies

## 🔍 Verification

After setup, verify everything works:

```bash
# Check environment status
python3 setup/setup_cli.py status

# Test Azure connection
python3 scripts/test_connection.py

# Generate and test notebooks
python3 setup/setup_cli.py notebooks
jupyter notebook
```

## 🆘 Getting Help

1. **Setup Issues**: Check the [troubleshooting section](azure-ai-search-setup.md#troubleshooting)
2. **Connection Problems**: Run `python3 setup/setup_cli.py status`
3. **Azure Service Issues**: Check the [Azure portal](https://portal.azure.com)
4. **Environment Issues**: See the main [README](../../README.md#troubleshooting)

## 📚 Next Steps

Once setup is complete:

1. **Start Learning**: [Module 1 - Introduction and Setup](../beginner/module-01-introduction-setup/)
2. **Generate Sample Data**: `python3 scripts/generate_sample_data.py`
3. **Explore Notebooks**: Open any `.ipynb` file in the `docs/` directory
4. **Join the Community**: Check the main repository for discussion links

---

**Need help?** Check the [Quick Reference](quick-reference.md) or the detailed [Azure AI Search Setup Guide](azure-ai-search-setup.md).