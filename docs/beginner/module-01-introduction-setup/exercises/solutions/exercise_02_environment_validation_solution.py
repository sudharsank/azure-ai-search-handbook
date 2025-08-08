"""
Exercise 2 Solution: Environment Validation and Configuration
Complete implementation with detailed explanations
"""

import os
import sys
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

def check_environment_file() -> Tuple[bool, str]:
    """
    Solution: Check if .env file exists and is properly formatted
    
    This function checks for the existence of the .env file and validates
    that it contains the required variables with proper formatting.
    """
    env_file_path = '.env'
    
    # Check if .env file exists
    if not os.path.exists(env_file_path):
        return False, "❌ .env file not found in project root"
    
    # Check file permissions (should not be world-readable for security)
    try:
        file_stat = os.stat(env_file_path)
        file_mode = file_stat.st_mode & 0o777
        if file_mode & 0o044:  # Check if group or others can read
            print("⚠️  Warning: .env file is readable by group/others (security risk)")
    except OSError:
        pass  # Ignore permission check errors on some systems
    
    # Read and validate .env file content
    required_vars = ['AZURE_SEARCH_SERVICE_ENDPOINT', 'AZURE_SEARCH_API_KEY', 'AZURE_SEARCH_INDEX_NAME']
    found_vars = []
    
    try:
        with open(env_file_path, 'r') as f:
            content = f.read()
            
        for var in required_vars:
            # Look for variable definition (with or without quotes)
            pattern = rf'^{var}\s*=\s*["\']?([^"\'\n]+)["\']?'
            if re.search(pattern, content, re.MULTILINE):
                found_vars.append(var)
        
        missing_vars = set(required_vars) - set(found_vars)
        
        if missing_vars:
            return False, f"❌ Missing variables in .env file: {', '.join(missing_vars)}"
        
        return True, f"✅ .env file exists and contains all required variables"
        
    except Exception as e:
        return False, f"❌ Error reading .env file: {str(e)}"

def validate_endpoint_format(endpoint: str) -> Tuple[bool, List[str]]:
    """
    Solution: Validate Azure AI Search endpoint format
    
    This function validates the endpoint URL according to Azure AI Search
    naming conventions and URL format requirements.
    """
    issues = []
    
    if not endpoint:
        issues.append("Endpoint is empty or None")
        return False, issues
    
    # Check HTTPS requirement
    if not endpoint.startswith('https://'):
        issues.append("Endpoint must start with 'https://' for security")
    
    # Check Azure AI Search domain
    if not endpoint.endswith('.search.windows.net'):
        issues.append("Endpoint must end with '.search.windows.net'")
    
    # Check for extra slashes
    if '//' in endpoint.replace('https://', ''):
        issues.append("Endpoint contains extra slashes")
    
    # Check for spaces
    if ' ' in endpoint:
        issues.append("Endpoint contains spaces")
    
    # Check for trailing slash
    if endpoint.endswith('/'):
        issues.append("Endpoint should not end with a trailing slash")
    
    # Validate service name format
    try:
        # Extract service name from URL
        service_name = endpoint.replace('https://', '').replace('.search.windows.net', '')
        
        # Service name validation rules
        if len(service_name) < 2 or len(service_name) > 60:
            issues.append("Service name must be between 2 and 60 characters")
        
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', service_name):
            issues.append("Service name must contain only lowercase letters, numbers, and hyphens")
        
        if service_name.startswith('-') or service_name.endswith('-'):
            issues.append("Service name cannot start or end with hyphens")
        
        if '--' in service_name:
            issues.append("Service name cannot contain consecutive hyphens")
            
    except Exception:
        issues.append("Could not extract service name from endpoint")
    
    return len(issues) == 0, issues

def validate_api_key_format(api_key: str) -> Tuple[bool, List[str]]:
    """
    Solution: Validate API key format
    
    This function validates the API key according to Azure AI Search
    API key format requirements and security best practices.
    """
    issues = []
    
    if not api_key:
        issues.append("API key is empty or None")
        return False, issues
    
    # Check for spaces
    if ' ' in api_key:
        issues.append("API key contains spaces (invalid format)")
    
    # Check minimum length (Azure AI Search keys are typically 32+ characters)
    if len(api_key) < 20:
        issues.append("API key appears too short (might be invalid)")
    
    # Check for Bearer prefix (common mistake)
    if api_key.startswith('Bearer '):
        issues.append("API key should not include 'Bearer ' prefix")
    
    # Check for common placeholder values
    placeholder_patterns = [
        'your-api-key',
        'api-key-here',
        'replace-with-your-key',
        'insert-key-here',
        'your_api_key_here'
    ]
    
    if any(pattern in api_key.lower() for pattern in placeholder_patterns):
        issues.append("API key appears to be a placeholder value")
    
    # Check for valid characters (Azure keys are typically alphanumeric with some symbols)
    if not re.match(r'^[A-Za-z0-9+/=_-]+$', api_key):
        issues.append("API key contains invalid characters")
    
    # Check for obvious test/dummy values
    if api_key.lower() in ['test', 'dummy', 'fake', 'sample', '123456']:
        issues.append("API key appears to be a test/dummy value")
    
    return len(issues) == 0, issues

def validate_index_name_format(index_name: str) -> Tuple[bool, List[str]]:
    """
    Solution: Validate index name format according to Azure AI Search rules
    
    This function validates the index name according to Azure AI Search
    naming conventions and restrictions.
    """
    issues = []
    
    if not index_name:
        issues.append("Index name is empty or None")
        return False, issues
    
    # Check length (1-128 characters)
    if len(index_name) < 1:
        issues.append("Index name cannot be empty")
    elif len(index_name) > 128:
        issues.append("Index name cannot exceed 128 characters")
    
    # Check if lowercase
    if index_name != index_name.lower():
        issues.append("Index name must be lowercase")
    
    # Check valid characters (letters, numbers, hyphens, underscores only)
    if not re.match(r'^[a-z0-9_-]+$', index_name):
        issues.append("Index name can only contain lowercase letters, numbers, hyphens, and underscores")
    
    # Check that it doesn't start or end with hyphens
    if index_name.startswith('-'):
        issues.append("Index name cannot start with a hyphen")
    
    if index_name.endswith('-'):
        issues.append("Index name cannot end with a hyphen")
    
    # Check for consecutive hyphens
    if '--' in index_name:
        issues.append("Index name cannot contain consecutive hyphens")
    
    # Check for reserved names
    reserved_names = ['system', 'admin', 'root', 'default']
    if index_name.lower() in reserved_names:
        issues.append(f"'{index_name}' is a reserved name and cannot be used")
    
    return len(issues) == 0, issues

def load_and_validate_configuration() -> Dict[str, any]:
    """
    Solution: Load configuration and validate all settings
    
    This function provides comprehensive validation of all configuration
    items and returns detailed results for each component.
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize results structure
    results = {
        'env_file_exists': False,
        'endpoint': {'valid': False, 'value': '', 'issues': []},
        'api_key': {'valid': False, 'value': '', 'issues': []},
        'index_name': {'valid': False, 'value': '', 'issues': []},
        'overall_valid': False
    }
    
    # Check environment file
    env_exists, env_message = check_environment_file()
    results['env_file_exists'] = env_exists
    
    if not env_exists:
        print(f"Environment file check: {env_message}")
        return results
    
    # Validate endpoint
    endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT', '')
    endpoint_valid, endpoint_issues = validate_endpoint_format(endpoint)
    results['endpoint'] = {
        'valid': endpoint_valid,
        'value': endpoint,
        'issues': endpoint_issues
    }
    
    # Validate API key
    api_key = os.getenv('AZURE_SEARCH_API_KEY', '')
    api_key_valid, api_key_issues = validate_api_key_format(api_key)
    results['api_key'] = {
        'valid': api_key_valid,
        'value': f"{api_key[:8]}..." if api_key else '',  # Mask for security
        'issues': api_key_issues
    }
    
    # Validate index name
    index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', '')
    index_name_valid, index_name_issues = validate_index_name_format(index_name)
    results['index_name'] = {
        'valid': index_name_valid,
        'value': index_name,
        'issues': index_name_issues
    }
    
    # Determine overall validity
    results['overall_valid'] = (
        env_exists and 
        endpoint_valid and 
        api_key_valid and 
        index_name_valid
    )
    
    return results

def create_sample_env_file() -> bool:
    """
    Solution: Create a sample .env file with placeholder values
    
    This function creates a comprehensive .env template with examples
    and detailed comments explaining each variable.
    """
    sample_content = '''# Azure AI Search Configuration
# Copy this file to .env and replace the placeholder values with your actual configuration

# Azure AI Search Service Endpoint
# Format: https://your-service-name.search.windows.net
# Example: https://mycompany-search.search.windows.net
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service-name.search.windows.net

# Azure AI Search API Key
# This is your primary or secondary admin key from the Azure portal
# Keep this secure and never commit it to version control
AZURE_SEARCH_API_KEY=your-api-key-here

# Default Index Name
# This should be a lowercase name following Azure AI Search naming rules
# Can contain letters, numbers, hyphens, and underscores
# Cannot start or end with hyphens
AZURE_SEARCH_INDEX_NAME=sample-index

# Optional: Use Managed Identity instead of API key (true/false)
# Set to true if running in Azure with managed identity configured
USE_MANAGED_IDENTITY=false

# Optional: Connection timeout in seconds
CONNECTION_TIMEOUT_SECONDS=30

# Optional: Maximum retry attempts for failed requests
MAX_RETRY_ATTEMPTS=3

# Optional: Enable detailed logging (true/false)
ENABLE_DETAILED_LOGGING=false
'''
    
    try:
        # Check if .env already exists
        if os.path.exists('.env'):
            # Create .env.sample instead
            with open('.env.sample', 'w') as f:
                f.write(sample_content)
            print("✅ Created .env.sample file (original .env file preserved)")
            print("💡 Copy .env.sample to .env and update with your values")
        else:
            # Create .env file
            with open('.env', 'w') as f:
                f.write(sample_content)
            print("✅ Created .env file with template values")
            print("💡 Please update the .env file with your actual Azure AI Search configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample .env file: {str(e)}")
        return False

def main():
    """
    Main function demonstrating comprehensive environment validation
    """
    print("🔍 Environment Validation Exercise - Solution")
    print("=" * 50)
    
    # Step 1: Check environment file
    print("\n📋 Step 1: Environment File Check")
    env_exists, env_message = check_environment_file()
    print(f"Status: {env_message}")
    
    if not env_exists:
        print("\n🔧 Creating sample .env file...")
        if create_sample_env_file():
            print("✅ Sample .env file created. Please update it with your values.")
            print("🔄 Run this exercise again after updating your .env file.")
        else:
            print("❌ Failed to create sample .env file.")
        return
    
    # Step 2: Load and validate configuration
    print("\n🔧 Step 2: Configuration Validation")
    validation_results = load_and_validate_configuration()
    
    if validation_results:
        overall_status = "✅ Valid" if validation_results.get('overall_valid') else "❌ Invalid"
        print(f"Overall Status: {overall_status}")
        
        # Display detailed results
        config_items = ['endpoint', 'api_key', 'index_name']
        for item in config_items:
            result = validation_results.get(item, {})
            status = "✅" if result.get('valid') else "❌"
            value = result.get('value', 'N/A')
            print(f"{status} {item.replace('_', ' ').title()}: {value}")
            
            # Show issues if any
            issues = result.get('issues', [])
            for issue in issues:
                print(f"   • {issue}")
    
    # Provide next steps based on results
    if validation_results.get('overall_valid'):
        print("\n🎉 Excellent! Your configuration is valid and ready to use.")
        print("\n🎯 Next Steps:")
        print("1. Your environment is properly configured")
        print("2. Move on to Exercise 3: Basic Connection Testing")
        print("3. Try connecting to your Azure AI Search service")
    else:
        print("\n🔧 Configuration Issues Detected")
        print("Please fix the issues shown above and run this exercise again.")
        print("\n💡 Common Solutions:")
        print("• Check your Azure portal for the correct endpoint and API key")
        print("• Ensure your .env file has the correct format")
        print("• Verify your index name follows Azure AI Search naming rules")
        print("• Make sure there are no extra spaces or special characters")

if __name__ == "__main__":
    main()