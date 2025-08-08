#!/usr/bin/env python3
"""
Azure AI Search Handbook Setup CLI
Command-line interface for setting up and managing the learning environment
"""

import argparse
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import setup modules
sys.path.append(str(Path(__file__).parent.parent))

# Import basic setup functions that don't depend on Azure packages
from setup.environment_setup import main as run_environment_setup

# Conditional imports for functions that depend on Azure packages
def _safe_import_setup_functions():
    """Safely import setup functions that depend on Azure packages"""
    try:
        from setup import quick_setup, validate_environment, get_connection_manager
        from setup.validate_setup import main as run_validation
        from setup.config_templates import ConfigurationManager
        from setup.common_utils import setup_sample_environment
        
        return {
            'quick_setup': quick_setup,
            'validate_environment': validate_environment,
            'get_connection_manager': get_connection_manager,
            'run_validation': run_validation,
            'ConfigurationManager': ConfigurationManager,
            'setup_sample_environment': setup_sample_environment
        }
    except ImportError as e:
        return None

# Try to import Azure-dependent functions
_setup_functions = _safe_import_setup_functions()


def setup_command(args):
    """Handle the setup command"""
    print("🚀 Running full environment setup...")
    
    if run_environment_setup():
        print("✅ Environment setup completed successfully!")
        
        if args.validate:
            print("\n🔍 Running validation...")
            # Re-import setup functions after installation
            global _setup_functions
            _setup_functions = _safe_import_setup_functions()
            
            if _setup_functions and _setup_functions.get('run_validation'):
                run_validation = _setup_functions['run_validation']
                if run_validation():
                    print("✅ Validation passed!")
                else:
                    print("❌ Validation failed!")
                    return False
            else:
                print("⚠️  Validation skipped - some modules not available yet")
        
        return True
    else:
        print("❌ Environment setup failed!")
        return False


def validate_command(args):
    """Handle the validate command"""
    print("🔍 Running environment validation...")
    
    if not _setup_functions:
        print("❌ Azure packages not installed yet!")
        print("💡 Run 'python setup/environment_setup.py' first to install dependencies")
        return False
    
    run_validation = _setup_functions.get('run_validation')
    if not run_validation:
        print("❌ Validation function not available")
        return False
    
    if run_validation():
        print("✅ All validation checks passed!")
        return True
    else:
        print("❌ Some validation checks failed!")
        return False


def config_command(args):
    """Handle the config command"""
    print(f"🔧 Creating configuration for: {args.type}")
    
    if not _setup_functions:
        print("❌ Azure packages not installed yet!")
        print("💡 Run 'python setup/environment_setup.py' first to install dependencies")
        return False
    
    ConfigurationManager = _setup_functions.get('ConfigurationManager')
    if not ConfigurationManager:
        print("❌ Configuration manager not available")
        return False
    
    try:
        manager = ConfigurationManager()
        
        if args.type == "index":
            if not args.schema_type:
                print("❌ --schema-type is required for index configuration")
                return False
            
            if not args.name:
                print("❌ --name is required for index configuration")
                return False
            
            manager.create_index_config(args.schema_type, args.name)
            
        elif args.type == "scoring":
            if not args.profile_type:
                print("❌ --profile-type is required for scoring configuration")
                return False
            
            manager.create_scoring_profile_config(args.profile_type)
            
        elif args.type == "analyzer":
            if not args.analyzer_type:
                print("❌ --analyzer-type is required for analyzer configuration")
                return False
            
            manager.create_analyzer_config(args.analyzer_type)
            
        elif args.type == "complete":
            project_name = args.name or "azure-search-handbook"
            manager.create_complete_config_set(project_name)
            
        else:
            print(f"❌ Unknown configuration type: {args.type}")
            return False
        
        print("✅ Configuration created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration creation failed: {str(e)}")
        return False


def data_command(args):
    """Handle the data command"""
    print(f"🎲 Generating {args.count} sample documents...")
    
    if not _setup_functions:
        print("❌ Azure packages not installed yet!")
        print("💡 Run 'python setup/environment_setup.py' first to install dependencies")
        return False
    
    setup_sample_environment = _setup_functions.get('setup_sample_environment')
    if not setup_sample_environment:
        print("❌ Sample environment function not available")
        return False
    
    try:
        documents = setup_sample_environment(
            data_file=args.output,
            document_count=args.count
        )
        
        print(f"✅ Generated {len(documents)} sample documents!")
        print(f"📁 Saved to: {args.output}")
        return True
        
    except Exception as e:
        print(f"❌ Data generation failed: {str(e)}")
        return False


def test_command(args):
    """Handle the test command"""
    print("🔍 Testing Azure AI Search connection...")
    
    if not _setup_functions:
        print("❌ Azure packages not installed yet!")
        print("💡 Run 'python setup/environment_setup.py' first to install dependencies")
        return False
    
    try:
        from setup.connection_utils import test_default_connection
        
        if test_default_connection():
            print("✅ Connection test passed!")
            
            # Get additional service information if requested
            if args.verbose:
                get_connection_manager = _setup_functions.get('get_connection_manager')
                if get_connection_manager:
                    manager = get_connection_manager()
                    stats = manager.get_service_statistics()
                    indexes = manager.list_indexes()
                    
                    if stats:
                        print(f"📊 Service Statistics:")
                        print(f"  Documents: {stats['counters']['document_count']}")
                        print(f"  Indexes: {stats['counters']['index_count']}")
                        print(f"  Storage: {stats['counters']['storage_size']} bytes")
                    
                    if indexes:
                        print(f"📋 Available Indexes: {', '.join(indexes)}")
            
            return True
        else:
            print("❌ Connection test failed!")
            print("💡 Make sure your .env file is configured correctly")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {str(e)}")
        print("💡 This is normal if Azure packages aren't installed yet")
        return False


def quick_command(args):
    """Handle the quick setup command"""
    project_name = args.name or "azure-search-handbook"
    
    print(f"⚡ Running quick setup for: {project_name}")
    
    if not _setup_functions:
        print("❌ Azure packages not installed yet!")
        print("💡 Run 'python setup/environment_setup.py' first to install dependencies")
        return False
    
    quick_setup = _setup_functions.get('quick_setup')
    if not quick_setup:
        print("❌ Quick setup function not available")
        return False
    
    if quick_setup(project_name):
        print("✅ Quick setup completed!")
        return True
    else:
        print("❌ Quick setup failed!")
        return False


def status_command(args):
    """Handle the status command"""
    print("📊 Azure AI Search Handbook Environment Status")
    print("=" * 50)
    
    # Check if key files exist
    key_files = [
        ".env",
        ".env.template",
        "requirements.txt",
        "setup/connection_utils.py",
        "setup/common_utils.py"
    ]
    
    print("📁 Key Files:")
    for file_path in key_files:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
    
    # Check directories
    key_dirs = ["config", "data", "logs", "scripts"]
    print("\n📂 Directories:")
    for dir_path in key_dirs:
        exists = Path(dir_path).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}/")
    
    # Check environment variables
    print("\n🔧 Environment Variables:")
    env_vars = [
        "AZURE_SEARCH_SERVICE_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}={display_value}")
        else:
            print(f"  ❌ {var}=<not set>")
    
    # Test connection if possible
    print("\n🔍 Connection Test:")
    if _setup_functions:
        try:
            from setup.connection_utils import test_default_connection
            if test_default_connection():
                print("  ✅ Azure AI Search connection working")
            else:
                print("  ❌ Azure AI Search connection failed")
        except Exception as e:
            print(f"  ❌ Connection test error: {str(e)}")
    else:
        print("  ⚠️  Azure packages not installed yet")
    
    return True


def notebooks_command(args):
    """Handle the notebooks command"""
    print("📓 Generating Jupyter notebooks from Python files...")
    
    try:
        from setup.notebook_generator import generate_all_notebooks, generate_all_exercise_notebooks
        
        docs_path = Path("docs")
        if not docs_path.exists():
            print("❌ No docs directory found!")
            print("💡 Make sure you're in the project root directory")
            return False
        
        # Generate code sample notebooks
        print("\n🔬 Generating code sample notebooks...")
        code_notebooks = generate_all_notebooks(docs_path)
        
        # Generate exercise notebooks
        print("\n📝 Generating exercise notebooks...")
        exercise_notebooks = generate_all_exercise_notebooks(docs_path)
        
        total = len(code_notebooks) + len(exercise_notebooks)
        
        if total > 0:
            print(f"\n✅ Successfully generated {total} notebooks:")
            print(f"   📊 Code samples: {len(code_notebooks)}")
            print(f"   📝 Exercises: {len(exercise_notebooks)}")
            
            print("\n📋 To use the notebooks:")
            print("1. Start Jupyter: jupyter notebook")
            print("2. Navigate to the generated .ipynb files")
            print("3. Run the cells interactively")
        else:
            print("ℹ️  No Python files found to convert")
            print("💡 Make sure there are .py files in docs/*/code-samples/ or docs/*/exercises/")
        
        return True
        
    except Exception as e:
        print(f"❌ Notebook generation failed: {str(e)}")
        return False


def docs_command(args):
    """Handle the docs command"""
    print("📚 Starting documentation server...")
    
    if not Path("mkdocs.yml").exists():
        print("❌ mkdocs.yml not found!")
        print("💡 Make sure you're in the project root directory")
        return False
    
    try:
        import socket
        
        # Check if port is available
        port = args.port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
        except OSError:
            print(f"⚠️  Port {port} is busy, trying port {port + 1}")
            port = port + 1
        
        # Build command
        cmd = ['mkdocs', 'serve', '--dev-addr', f'localhost:{port}']
        if args.no_reload:
            cmd.append('--no-livereload')
        
        print(f"🌐 Starting server at http://localhost:{port}")
        print("⏹️  Press Ctrl+C to stop")
        
        subprocess.run(cmd, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start documentation server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Documentation server stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting docs server: {str(e)}")
        return False


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Azure AI Search Handbook Setup CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup                          # Run full environment setup
  %(prog)s setup --validate              # Setup and validate
  %(prog)s validate                      # Run validation only
  %(prog)s config index --schema-type basic --name my-index
  %(prog)s config complete --name my-project
  %(prog)s data --count 50 --output data/samples.json
  %(prog)s test --verbose                # Test connection with details
  %(prog)s quick --name my-project       # Quick setup everything
  %(prog)s notebooks                     # Generate Jupyter notebooks
  %(prog)s docs                          # Serve documentation
  %(prog)s docs --port 8001 --no-reload # Serve docs with custom settings
  %(prog)s status                        # Show environment status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Run full environment setup')
    setup_parser.add_argument('--validate', action='store_true', 
                            help='Run validation after setup')
    setup_parser.set_defaults(func=setup_command)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate environment')
    validate_parser.set_defaults(func=validate_command)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Create configuration files')
    config_parser.add_argument('type', choices=['index', 'scoring', 'analyzer', 'complete'],
                              help='Type of configuration to create')
    config_parser.add_argument('--schema-type', choices=['basic', 'ecommerce', 'knowledge_base'],
                              help='Schema type for index configuration')
    config_parser.add_argument('--profile-type', choices=['relevance', 'popularity'],
                              help='Profile type for scoring configuration')
    config_parser.add_argument('--analyzer-type', choices=['custom_text', 'multilingual'],
                              help='Analyzer type for analyzer configuration')
    config_parser.add_argument('--name', help='Name for the configuration')
    config_parser.set_defaults(func=config_command)
    
    # Data command
    data_parser = subparsers.add_parser('data', help='Generate sample data')
    data_parser.add_argument('--count', type=int, default=100,
                           help='Number of sample documents to generate')
    data_parser.add_argument('--output', default='data/sample_documents.json',
                           help='Output file path')
    data_parser.set_defaults(func=data_command)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test Azure AI Search connection')
    test_parser.add_argument('--verbose', action='store_true',
                           help='Show detailed connection information')
    test_parser.set_defaults(func=test_command)
    
    # Quick command
    quick_parser = subparsers.add_parser('quick', help='Quick setup everything')
    quick_parser.add_argument('--name', default='azure-search-handbook',
                            help='Project name for configurations')
    quick_parser.set_defaults(func=quick_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show environment status')
    status_parser.set_defaults(func=status_command)
    
    # Notebooks command
    notebooks_parser = subparsers.add_parser('notebooks', help='Generate Jupyter notebooks')
    notebooks_parser.set_defaults(func=notebooks_command)
    
    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Serve documentation')
    docs_parser.add_argument('--port', type=int, default=8000, help='Port to serve on')
    docs_parser.add_argument('--no-reload', action='store_true', help='Disable live reload')
    docs_parser.set_defaults(func=docs_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run the selected command
    try:
        success = args.func(args)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())