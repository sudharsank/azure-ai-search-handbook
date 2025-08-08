"""
Environment Setup Script
Automated setup for Azure AI Search development environment
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


def check_python_version():
    """Check if Python version meets requirements"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_pip_version():
    """Check if pip is available and up to date"""
    try:
        import pip
        print(f"✅ pip {pip.__version__} available")
        return True
    except ImportError:
        print("❌ pip is not available")
        return False


def check_virtual_environment():
    """Check if we're running in a virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        print("⚠️  Warning: Not running in a virtual environment!")
        print("📋 It's strongly recommended to use a virtual environment.")
        print("\n🔧 Would you like to create and use a virtual environment?")
        
        response = input("Create virtual environment? (Y/n): ").lower().strip()
        if response in ['', 'y', 'yes']:
            return create_virtual_environment()
        else:
            print("⚠️  Continuing without virtual environment...")
            response = input("Are you sure you want to install globally? (y/N): ").lower().strip()
            if response != 'y':
                print("Setup cancelled. Please create a virtual environment first.")
                return False
    else:
        venv_path = sys.prefix
        print(f"✅ Running in virtual environment: {venv_path}")
    
    return True


def create_virtual_environment():
    """Create and activate a virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment directory already exists")
        response = input("Use existing virtual environment? (Y/n): ").lower().strip()
        if response in ['', 'y', 'yes']:
            print("✅ Using existing virtual environment")
            return True
        else:
            print("❌ Please remove the existing 'venv' directory and run setup again")
            return False
    
    try:
        print("🔧 Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created successfully")
        
        # Provide activation instructions
        if os.name == 'nt':  # Windows
            activate_cmd = "venv\\Scripts\\activate"
        else:  # Unix/Linux/macOS
            activate_cmd = "source venv/bin/activate"
        
        print(f"\n📋 To activate the virtual environment, run:")
        print(f"   {activate_cmd}")
        print(f"\n📋 Then run this setup script again:")
        print(f"   python setup/environment_setup.py")
        print(f"\n📋 Or use the CLI:")
        print(f"   python setup/setup_cli.py setup")
        
        return False  # Return False to stop current execution
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required Python packages"""
    try:
        print("📦 Installing Python dependencies...")
        
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directory_structure():
    """Create necessary directory structure"""
    directories = [
        "config",
        "data",
        "logs",
        "notebooks",
        "scripts",
        "tests"
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ Created {directory}/")
    
    return True


def create_env_template():
    """Create comprehensive .env template file"""
    env_template = """# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service-name.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key-here
AZURE_SEARCH_INDEX_NAME=sample-index

# Optional: Azure Active Directory Authentication
# USE_MANAGED_IDENTITY=false
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-client-secret
# AZURE_TENANT_ID=your-tenant-id

# Development Settings
LOG_LEVEL=INFO
ENVIRONMENT=development

# Sample Data Configuration
SAMPLE_DATA_COUNT=100
SAMPLE_DATA_FILE=data/sample_documents.json

# Performance Testing
PERFORMANCE_LOG_FILE=logs/performance.json
ENABLE_PERFORMANCE_MONITORING=true

# Jupyter Notebook Configuration
JUPYTER_PORT=8888
JUPYTER_HOST=localhost
"""
    
    env_file = Path(".env.template")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_template)
        print("✅ Created .env.template file")
    else:
        print("ℹ️  .env.template already exists")


def create_config_templates():
    """Create configuration template files"""
    
    # Search service configuration template
    search_config = {
        "endpoint": "https://your-service-name.search.windows.net",
        "api_key": "your-api-key-here",
        "index_name": "sample-index",
        "use_managed_identity": False,
        "client_id": "your-client-id-for-managed-identity",
        "client_secret": "your-client-secret-for-managed-identity",
        "tenant_id": "your-tenant-id-for-managed-identity"
    }
    
    config_file = Path("config/search_config.json.template")
    if not config_file.exists():
        with open(config_file, 'w') as f:
            json.dump(search_config, f, indent=2)
        print("✅ Created config/search_config.json.template")
    
    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler"
            },
            "file": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": "logs/application.log"
            }
        },
        "loggers": {
            "": {
                "handlers": ["default", "file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    logging_file = Path("config/logging.json")
    if not logging_file.exists():
        with open(logging_file, 'w') as f:
            json.dump(logging_config, f, indent=2)
        print("✅ Created config/logging.json")


def create_sample_scripts():
    """Create sample utility scripts"""
    
    # Quick test script
    test_script = '''#!/usr/bin/env python3
"""
Quick test script to verify Azure AI Search connection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setup.connection_utils import test_default_connection

if __name__ == "__main__":
    print("🔍 Testing Azure AI Search connection...")
    if test_default_connection():
        print("✅ Connection test passed!")
        sys.exit(0)
    else:
        print("❌ Connection test failed!")
        sys.exit(1)
'''
    
    script_file = Path("scripts/test_connection.py")
    if not script_file.exists():
        with open(script_file, 'w') as f:
            f.write(test_script)
        script_file.chmod(0o755)  # Make executable
        print("✅ Created scripts/test_connection.py")
    
    # Data generation script
    data_script = '''#!/usr/bin/env python3
"""
Generate sample data for exercises and testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setup.common_utils import setup_sample_environment

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"🎲 Generating {count} sample documents...")
    
    documents = setup_sample_environment(document_count=count)
    print(f"✅ Generated {len(documents)} sample documents")
'''
    
    data_script_file = Path("scripts/generate_sample_data.py")
    if not data_script_file.exists():
        with open(data_script_file, 'w') as f:
            f.write(data_script)
        data_script_file.chmod(0o755)  # Make executable
        print("✅ Created scripts/generate_sample_data.py")
    
    # Notebook generation script
    notebook_script = '''#!/usr/bin/env python3
"""
Generate Jupyter notebooks from Python code samples and exercises
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from setup.notebook_generator import main as generate_notebooks

if __name__ == "__main__":
    print("📓 Generating Jupyter notebooks...")
    if generate_notebooks():
        print("✅ Notebook generation completed!")
        sys.exit(0)
    else:
        print("❌ Notebook generation failed!")
        sys.exit(1)
'''
    
    notebook_script_file = Path("scripts/generate_notebooks.py")
    if not notebook_script_file.exists():
        with open(notebook_script_file, 'w') as f:
            f.write(notebook_script)
        notebook_script_file.chmod(0o755)  # Make executable
        print("✅ Created scripts/generate_notebooks.py")


def create_gitignore():
    """Create .gitignore file for the project"""
    gitignore_content = """# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# Logs
logs/
*.log

# Data files
data/
!data/.gitkeep

# Configuration files with secrets
config/search_config.json
config/*.json
!config/*.json.template

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Documentation build
site/
docs/_build/

# Temporary files
*.tmp
*.temp
"""
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")


def create_readme_sections():
    """Create additional README sections for setup"""
    readme_content = """
## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd azure-ai-search-handbook
   ```

2. **Run the setup script**
   ```bash
   python setup/environment_setup.py
   ```

3. **Configure your environment**
   ```bash
   cp .env.template .env
   # Edit .env with your Azure AI Search credentials
   ```

4. **Validate your setup**
   ```bash
   python setup/validate_setup.py
   ```

5. **Test connection**
   ```bash
   python scripts/test_connection.py
   ```

## Development Environment

### Prerequisites
- Python 3.8 or higher
- Azure AI Search service
- Git

### Directory Structure
```
azure-ai-search-handbook/
├── config/          # Configuration files and templates
├── data/           # Sample data and datasets
├── docs/           # Documentation and learning modules
├── logs/           # Application logs
├── notebooks/      # Jupyter notebooks
├── scripts/        # Utility scripts
├── setup/          # Setup and configuration utilities
└── tests/          # Test files
```

### Environment Variables
Copy `.env.template` to `.env` and configure:

- `AZURE_SEARCH_SERVICE_ENDPOINT`: Your Azure AI Search service endpoint
- `AZURE_SEARCH_API_KEY`: Your Azure AI Search API key
- `AZURE_SEARCH_INDEX_NAME`: Default index name for exercises

### Troubleshooting
If you encounter issues during setup:

1. Ensure Python 3.8+ is installed
2. Check that pip is up to date
3. Verify your Azure AI Search credentials
4. Run the validation script for detailed diagnostics

For more help, see the troubleshooting guide in `docs/reference/troubleshooting.md`.
"""
    
    print("📝 README sections created (content available for manual addition)")
    return readme_content


def generate_jupyter_notebooks():
    """Generate Jupyter notebooks from existing Python files"""
    try:
        from setup.notebook_generator import generate_all_notebooks, generate_all_exercise_notebooks
        
        print("📓 Generating Jupyter notebooks from Python files...")
        
        # Check if there are any Python files to convert
        docs_path = Path("docs")
        if not docs_path.exists():
            print("ℹ️  No docs directory found, skipping notebook generation")
            return True
        
        # Generate code sample notebooks
        code_notebooks = generate_all_notebooks(docs_path)
        
        # Generate exercise notebooks  
        exercise_notebooks = generate_all_exercise_notebooks(docs_path)
        
        total = len(code_notebooks) + len(exercise_notebooks)
        if total > 0:
            print(f"✅ Generated {total} Jupyter notebooks")
        else:
            print("ℹ️  No Python files found to convert to notebooks")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Notebook generation failed: {e}")
        print("ℹ️  You can generate notebooks later using: python scripts/generate_notebooks.py")
        return True  # Don't fail the entire setup for this


def verify_installation():
    """Verify that the installation was successful"""
    print("\n🔍 Verifying installation...")
    
    # Check if key files exist
    required_files = [
        ".env.template",
        "config/search_config.json.template",
        "config/logging.json",
        "scripts/test_connection.py",
        "scripts/generate_sample_data.py",
        "scripts/generate_notebooks.py",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # Check if directories exist
    required_dirs = ["config", "data", "logs", "notebooks", "scripts", "tests"]
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    print("✅ Installation verification passed")
    return True


def main():
    """Main setup function"""
    print("🚀 Azure AI Search Handbook - Environment Setup")
    print("=" * 60)
    
    setup_steps = [
        ("Checking Python version", check_python_version),
        ("Checking pip availability", check_pip_version),
        ("Checking virtual environment", check_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating directory structure", create_directory_structure),
        ("Creating environment template", create_env_template),
        ("Creating configuration templates", create_config_templates),
        ("Creating sample scripts", create_sample_scripts),
        ("Generating Jupyter notebooks", generate_jupyter_notebooks),
        ("Creating .gitignore", create_gitignore),
        ("Verifying installation", verify_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_function in setup_steps:
        print(f"\n📋 {step_name}...")
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {str(e)}")
            failed_steps.append(step_name)
    
    print("\n" + "=" * 60)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Copy .env.template to .env")
        print("2. Update .env with your Azure AI Search credentials")
        print("3. Run: python setup/validate_setup.py")
        print("4. Test connection: python scripts/test_connection.py")
        print("5. Generate sample data: python scripts/generate_sample_data.py")
        print("6. Generate notebooks: python scripts/generate_notebooks.py")
        print("\n📚 Learning options:")
        print("   📖 Documentation: docs/beginner/")
        print("   🐍 Python files: docs/*/code-samples/*.py")
        print("   📓 Jupyter notebooks: docs/*/code-samples/*.ipynb (after generation)")
        print("   📝 Exercises: docs/*/exercises/*.py and *.ipynb")
        
        # Show README content for manual addition
        readme_content = create_readme_sections()
        print(f"\n📝 Consider adding this content to your README.md:\n{readme_content}")
        
        return True
    else:
        print(f"❌ Setup failed. Issues with: {', '.join(failed_steps)}")
        print("Please review the errors above and try again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)