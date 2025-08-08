"""
Exercise 2: Environment Validation and Configuration
Validate your environment setup and configuration files
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

def check_environment_file() -> Tuple[bool, str]:
    """
    Exercise: Check if .env file exists and is properly formatted
    
    Instructions:
    1. Check if .env file exists in the project root
    2. Verify it contains the required variables
    3. Return success status and message
    
    Required variables:
    - AZURE_SEARCH_SERVICE_ENDPOINT
    - AZURE_SEARCH_API_KEY
    - AZURE_SEARCH_INDEX_NAME
    """
    # TODO: Implement .env file validation
    # Hint: Use os.path.exists() and check for required variables
    pass

def validate_endpoint_format(endpoint: str) -> Tuple[bool, List[str]]:
    """
    Exercise: Validate Azure AI Search endpoint format
    
    Instructions:
    1. Check if endpoint starts with 'https://'
    2. Check if endpoint ends with '.search.windows.net'
    3. Verify there are no extra slashes or spaces
    4. Return validation status and list of issues
    
    Args:
        endpoint: The endpoint URL to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    # TODO: Implement endpoint format validation
    # Example valid endpoint: https://myservice.search.windows.net
    pass

def validate_api_key_format(api_key: str) -> Tuple[bool, List[str]]:
    """
    Exercise: Validate API key format
    
    Instructions:
    1. Check if API key is not empty
    2. Verify it doesn't contain spaces
    3. Check if it's at least 20 characters long
    4. Ensure it doesn't have 'Bearer ' prefix
    5. Return validation status and list of issues
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    # TODO: Implement API key format validation
    pass

def validate_index_name_format(index_name: str) -> Tuple[bool, List[str]]:
    """
    Exercise: Validate index name format according to Azure AI Search rules
    
    Instructions:
    1. Check if index name is lowercase
    2. Verify it only contains letters, numbers, hyphens, and underscores
    3. Ensure it doesn't start or end with hyphens
    4. Check length is between 1 and 128 characters
    5. Return validation status and list of issues
    
    Args:
        index_name: The index name to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    # TODO: Implement index name format validation
    # Azure AI Search naming rules:
    # - Must be lowercase
    # - Can contain letters, numbers, hyphens, underscores
    # - Cannot start or end with hyphens
    # - Length: 1-128 characters
    pass

def load_and_validate_configuration() -> Dict[str, any]:
    """
    Exercise: Load configuration and validate all settings
    
    Instructions:
    1. Load environment variables using dotenv
    2. Extract required configuration values
    3. Validate each configuration item using the functions above
    4. Return a comprehensive validation report
    
    Returns:
        Dict containing validation results for each configuration item
    """
    # TODO: Implement comprehensive configuration validation
    # Structure the return value as:
    # {
    #     'env_file_exists': bool,
    #     'endpoint': {'valid': bool, 'value': str, 'issues': []},
    #     'api_key': {'valid': bool, 'value': str, 'issues': []},
    #     'index_name': {'valid': bool, 'value': str, 'issues': []},
    #     'overall_valid': bool
    # }
    pass

def create_sample_env_file() -> bool:
    """
    Exercise: Create a sample .env file with placeholder values
    
    Instructions:
    1. Create a .env.sample file with template values
    2. Include comments explaining each variable
    3. Use placeholder values that show the expected format
    4. Return True if file was created successfully
    
    Returns:
        bool: True if sample file created successfully
    """
    # TODO: Implement sample .env file creation
    # Template should include:
    # AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service-name.search.windows.net
    # AZURE_SEARCH_API_KEY=your-api-key-here
    # AZURE_SEARCH_INDEX_NAME=sample-index
    pass

if __name__ == "__main__":
    print("🔍 Environment Validation Exercise")
    print("=" * 40)
    
    # Step 1: Check environment file
    print("\n📋 Step 1: Environment File Check")
    env_exists, env_message = check_environment_file()
    print(f"Status: {env_message}")
    
    if not env_exists:
        print("\n🔧 Creating sample .env file...")
        if create_sample_env_file():
            print("✅ Sample .env file created. Please update it with your values.")
        else:
            print("❌ Failed to create sample .env file.")
    
    # Step 2: Load and validate configuration
    print("\n🔧 Step 2: Configuration Validation")
    validation_results = load_and_validate_configuration()
    
    if validation_results:
        print(f"Overall Status: {'✅ Valid' if validation_results.get('overall_valid') else '❌ Invalid'}")
        
        # Display detailed results
        for key, result in validation_results.items():
            if isinstance(result, dict) and 'valid' in result:
                status = "✅" if result['valid'] else "❌"
                print(f"{status} {key.title()}: {result.get('value', 'N/A')}")
                if result.get('issues'):
                    for issue in result['issues']:
                        print(f"   • {issue}")
    
    print("\n🎯 Next Steps:")
    print("1. Fix any validation issues shown above")
    print("2. Update your .env file with correct values")
    print("3. Run this exercise again to verify your configuration")
    print("4. Move on to Exercise 3: Basic Connection Testing")