"""
Exercise 6: Configuration Management
Learn to manage configurations for different environments
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv

class Environment(Enum):
    """Enumeration of deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class SearchServiceConfig:
    """Configuration data class for Azure AI Search service"""
    endpoint: str
    api_key: str
    index_name: str
    environment: Environment
    timeout_seconds: int = 30
    max_retries: int = 3
    enable_logging: bool = True

def load_environment_config(env: Environment) -> Optional[SearchServiceConfig]:
    """
    Exercise: Load configuration for a specific environment
    
    Instructions:
    1. Load environment variables with environment-specific prefixes
    2. Create a SearchServiceConfig instance
    3. Validate the configuration
    4. Return the configuration or None if invalid
    
    Args:
        env: Target environment
        
    Returns:
        SearchServiceConfig instance or None if invalid
    """
    # TODO: Implement environment-specific configuration loading
    # Environment variable patterns:
    # DEV_AZURE_SEARCH_SERVICE_ENDPOINT
    # TEST_AZURE_SEARCH_SERVICE_ENDPOINT
    # PROD_AZURE_SEARCH_SERVICE_ENDPOINT
    # etc.
    pass

def create_config_template(env: Environment) -> Dict[str, str]:
    """
    Exercise: Create a configuration template for an environment
    
    Instructions:
    1. Define all required configuration variables
    2. Include environment-specific prefixes
    3. Add helpful comments and examples
    4. Return the template as a dictionary
    
    Args:
        env: Target environment
        
    Returns:
        Dict containing configuration template
    """
    # TODO: Implement configuration template creation
    # Template should include:
    # - Environment-prefixed variables
    # - Example values
    # - Comments explaining each variable
    # - Security considerations
    pass

def validate_configuration(config: SearchServiceConfig) -> Dict[str, Any]:
    """
    Exercise: Validate a configuration object
    
    Instructions:
    1. Check that all required fields are present
    2. Validate endpoint URL format
    3. Check API key format
    4. Validate index name according to Azure rules
    5. Check timeout and retry values are reasonable
    6. Return validation results
    
    Args:
        config: Configuration to validate
        
    Returns:
        Dict containing validation results
    """
    # TODO: Implement configuration validation
    # Return structure:
    # {
    #     'valid': bool,
    #     'errors': [str],
    #     'warnings': [str],
    #     'recommendations': [str]
    # }
    pass

def create_environment_specific_configs() -> Dict[Environment, SearchServiceConfig]:
    """
    Exercise: Create configurations for all environments
    
    Instructions:
    1. Define different configurations for each environment
    2. Use appropriate settings for each environment type
    3. Include environment-specific optimizations
    4. Return a dictionary of all configurations
    
    Returns:
        Dict mapping environments to their configurations
    """
    # TODO: Implement environment-specific configuration creation
    # Consider different settings for:
    # - Development: More logging, shorter timeouts for faster feedback
    # - Testing: Stable settings, moderate logging
    # - Staging: Production-like settings with extra logging
    # - Production: Optimized for performance and reliability
    pass

def implement_config_encryption() -> Dict[str, Any]:
    """
    Exercise: Implement configuration encryption for sensitive data
    
    Instructions:
    1. Create functions to encrypt/decrypt API keys
    2. Use environment variables for encryption keys
    3. Demonstrate secure storage of sensitive configuration
    4. Return encryption implementation results
    
    Returns:
        Dict containing encryption implementation details
    """
    # TODO: Implement configuration encryption
    # This is a simplified example - in production, use proper key management
    # Show how to:
    # - Encrypt sensitive configuration values
    # - Store encryption keys securely
    # - Decrypt values at runtime
    # - Rotate encryption keys
    pass

def create_config_validation_script() -> Callable:
    """
    Exercise: Create a script to validate configurations
    
    Instructions:
    1. Create a function that validates all environment configs
    2. Check for common configuration issues
    3. Verify connectivity with each configuration
    4. Generate a validation report
    5. Return the validation function
    
    Returns:
        Callable that validates all configurations
    """
    # TODO: Implement configuration validation script
    # The script should:
    # - Load all environment configurations
    # - Validate each configuration
    # - Test connectivity where possible
    # - Generate a comprehensive report
    # - Suggest fixes for any issues
    pass

def demonstrate_config_hot_reload() -> Dict[str, Any]:
    """
    Exercise: Demonstrate configuration hot reload capability
    
    Instructions:
    1. Create a configuration manager that can reload configs
    2. Implement file watching for configuration changes
    3. Show how to update running applications
    4. Handle configuration validation during reload
    5. Return hot reload implementation details
    
    Returns:
        Dict containing hot reload implementation details
    """
    # TODO: Implement configuration hot reload
    # This is an advanced topic showing how to:
    # - Watch configuration files for changes
    # - Reload configuration without restarting
    # - Validate new configuration before applying
    # - Handle reload failures gracefully
    pass

def create_config_migration_tool() -> Dict[str, Any]:
    """
    Exercise: Create a tool to migrate configurations between versions
    
    Instructions:
    1. Define configuration schema versions
    2. Create migration functions between versions
    3. Implement backward compatibility
    4. Validate migrated configurations
    5. Return migration tool details
    
    Returns:
        Dict containing configuration migration details
    """
    # TODO: Implement configuration migration tool
    # Show how to:
    # - Version configuration schemas
    # - Migrate between schema versions
    # - Maintain backward compatibility
    # - Validate migrated configurations
    pass

def generate_config_documentation() -> str:
    """
    Exercise: Generate documentation for configuration options
    
    Instructions:
    1. Document all configuration variables
    2. Include descriptions and examples
    3. Explain environment-specific considerations
    4. Add troubleshooting information
    5. Return formatted documentation
    
    Returns:
        String containing configuration documentation
    """
    # TODO: Implement configuration documentation generation
    # Generate markdown documentation that includes:
    # - All configuration variables
    # - Descriptions and examples
    # - Environment-specific notes
    # - Security considerations
    # - Troubleshooting tips
    pass

if __name__ == "__main__":
    print("⚙️  Configuration Management Exercise")
    print("=" * 40)
    
    print("This exercise teaches you how to manage configurations")
    print("across different environments and deployment scenarios.\n")
    
    # Test 1: Environment-specific configuration loading
    print("1️⃣ Environment-Specific Configuration Loading")
    for env in Environment:
        config = load_environment_config(env)
        if config:
            print(f"✅ {env.value.title()} configuration loaded")
        else:
            print(f"⚠️  {env.value.title()} configuration not available")
    
    # Test 2: Configuration templates
    print("\n2️⃣ Configuration Templates")
    for env in [Environment.DEVELOPMENT, Environment.PRODUCTION]:
        template = create_config_template(env)
        if template:
            print(f"✅ {env.value.title()} template created ({len(template)} variables)")
    
    # Test 3: Configuration validation
    print("\n3️⃣ Configuration Validation")
    # Create a sample configuration for testing
    sample_config = SearchServiceConfig(
        endpoint="https://sample.search.windows.net",
        api_key="sample-key-123",
        index_name="test-index",
        environment=Environment.DEVELOPMENT
    )
    
    validation_result = validate_configuration(sample_config)
    if validation_result:
        print(f"Validation completed: {'✅ Valid' if validation_result.get('valid') else '❌ Invalid'}")
        errors = validation_result.get('errors', [])
        if errors:
            print(f"Errors found: {len(errors)}")
    
    # Test 4: Environment-specific configurations
    print("\n4️⃣ Environment-Specific Configurations")
    env_configs = create_environment_specific_configs()
    if env_configs:
        print(f"✅ Created configurations for {len(env_configs)} environments")
        for env, config in env_configs.items():
            print(f"   • {env.value.title()}: timeout={config.timeout_seconds}s, retries={config.max_retries}")
    
    # Test 5: Configuration encryption
    print("\n5️⃣ Configuration Encryption")
    encryption_result = implement_config_encryption()
    if encryption_result:
        print("✅ Configuration encryption implemented")
        if encryption_result.get('encryption_available'):
            print("   • Sensitive data can be encrypted")
            print("   • Decryption keys managed securely")
    
    # Test 6: Configuration validation script
    print("\n6️⃣ Configuration Validation Script")
    validation_script = create_config_validation_script()
    if validation_script:
        print("✅ Configuration validation script created")
        print("   • Can validate all environment configurations")
        print("   • Includes connectivity testing")
    
    # Test 7: Configuration hot reload
    print("\n7️⃣ Configuration Hot Reload")
    hot_reload_result = demonstrate_config_hot_reload()
    if hot_reload_result:
        print("✅ Configuration hot reload demonstrated")
        if hot_reload_result.get('file_watching_available'):
            print("   • File watching implemented")
            print("   • Safe configuration updates")
    
    # Test 8: Configuration migration
    print("\n8️⃣ Configuration Migration")
    migration_result = create_config_migration_tool()
    if migration_result:
        print("✅ Configuration migration tool created")
        versions = migration_result.get('supported_versions', [])
        if versions:
            print(f"   • Supports {len(versions)} schema versions")
    
    # Test 9: Configuration documentation
    print("\n9️⃣ Configuration Documentation")
    documentation = generate_config_documentation()
    if documentation:
        print("✅ Configuration documentation generated")
        print(f"   • Documentation length: {len(documentation)} characters")
    
    print("\n📚 Configuration Best Practices:")
    print("1. Use environment-specific configuration files")
    print("2. Validate configurations at startup")
    print("3. Encrypt sensitive configuration data")
    print("4. Document all configuration options")
    print("5. Implement configuration versioning")
    print("6. Test configurations in CI/CD pipelines")
    
    print("\n🎯 Next Steps:")
    print("1. Set up environment-specific configurations for your project")
    print("2. Implement configuration validation in your applications")
    print("3. Move on to Exercise 7: Service Health Monitoring")