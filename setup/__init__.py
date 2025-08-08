"""
Azure AI Search Handbook Setup Package
Comprehensive setup and configuration utilities for the Azure AI Search learning environment
"""

# Conditional imports to handle missing dependencies during initial setup
def _safe_import():
    """Safely import modules that depend on Azure packages"""
    try:
        from .connection_utils import (
            AzureSearchConnectionManager,
            SearchConfig,
            get_default_search_client,
            get_default_index_client,
            test_default_connection,
            create_sample_config_file,
            load_config_from_file
        )
        
        from .common_utils import (
            DataGenerator,
            SampleDocument,
            ExerciseValidator,
            PerformanceMonitor,
            ConfigurationHelper,
            setup_sample_environment,
            validate_exercise_solution
        )
        
        from .config_templates import (
            IndexSchemaTemplate,
            ScoringProfileTemplate,
            AnalyzerTemplate,
            ConfigurationManager
        )
        
        return {
            'AzureSearchConnectionManager': AzureSearchConnectionManager,
            'SearchConfig': SearchConfig,
            'get_default_search_client': get_default_search_client,
            'get_default_index_client': get_default_index_client,
            'test_default_connection': test_default_connection,
            'create_sample_config_file': create_sample_config_file,
            'load_config_from_file': load_config_from_file,
            'DataGenerator': DataGenerator,
            'SampleDocument': SampleDocument,
            'ExerciseValidator': ExerciseValidator,
            'PerformanceMonitor': PerformanceMonitor,
            'ConfigurationHelper': ConfigurationHelper,
            'setup_sample_environment': setup_sample_environment,
            'validate_exercise_solution': validate_exercise_solution,
            'IndexSchemaTemplate': IndexSchemaTemplate,
            'ScoringProfileTemplate': ScoringProfileTemplate,
            'AnalyzerTemplate': AnalyzerTemplate,
            'ConfigurationManager': ConfigurationManager
        }
    except ImportError as e:
        print(f"⚠️  Some setup modules not available yet: {e}")
        print("💡 This is normal during initial setup. Run 'python setup/environment_setup.py' first.")
        return {}

# Try to import modules, but don't fail if dependencies aren't installed
_imported_modules = _safe_import()

__version__ = "1.0.0"
__author__ = "Azure AI Search Handbook Team"

# Package-level convenience functions
def quick_setup(project_name: str = "azure-search-handbook"):
    """
    Quick setup function to initialize the entire environment
    
    Args:
        project_name: Name of the project for configuration files
    """
    print(f"🚀 Quick Setup for {project_name}")
    print("=" * 50)
    
    try:
        # Create configuration manager
        from .config_templates import ConfigurationManager
        config_manager = ConfigurationManager()
        
        # Create complete configuration set
        config_manager.create_complete_config_set(project_name)
        
        # Generate sample data
        from .common_utils import setup_sample_environment
        setup_sample_environment()
        
        # Test connection if possible
        try:
            from .connection_utils import test_default_connection
            if test_default_connection():
                print("✅ Azure AI Search connection verified")
            else:
                print("⚠️  Azure AI Search connection not configured yet")
        except:
            print("⚠️  Azure AI Search connection not configured yet")
        
        print(f"\n🎉 Quick setup completed for {project_name}!")
        print("📋 Next steps:")
        print("1. Configure your .env file with Azure credentials")
        print("2. Run: python setup/validate_setup.py")
        print("3. Start learning with the beginner modules")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick setup failed: {str(e)}")
        return False


def get_connection_manager(config_file: str = None):
    """
    Get a configured connection manager
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Configured AzureSearchConnectionManager instance
    """
    try:
        from .connection_utils import AzureSearchConnectionManager, load_config_from_file
        
        if config_file:
            config = load_config_from_file(config_file)
            return AzureSearchConnectionManager(config)
        else:
            return AzureSearchConnectionManager()
    except ImportError:
        print("❌ Azure packages not installed yet")
        return None


def validate_environment() -> bool:
    """
    Validate the current environment setup
    
    Returns:
        True if environment is valid, False otherwise
    """
    try:
        from .validate_setup import SetupValidator
        validator = SetupValidator()
        return validator.run_all_validations()
    except Exception as e:
        print(f"❌ Environment validation failed: {str(e)}")
        return False


# Export available functions
__all__ = ['quick_setup', 'get_connection_manager', 'validate_environment']

# Add imported modules to __all__ if they're available
if _imported_modules:
    __all__.extend(_imported_modules.keys())

# Make imported modules available at package level
globals().update(_imported_modules)