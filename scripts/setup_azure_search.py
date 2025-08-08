#!/usr/bin/env python3
"""
Azure AI Search Service Setup Script
Interactive script to help set up Azure AI Search service
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_azure_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Azure CLI is installed")
            return True
        else:
            print("❌ Azure CLI is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Azure CLI is not installed")
        print("💡 Install from: https://docs.microsoft.com/cli/azure/install-azure-cli")
        return False


def check_azure_login():
    """Check if user is logged into Azure"""
    try:
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            account_info = json.loads(result.stdout)
            print(f"✅ Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
            print(f"📋 Subscription: {account_info.get('name', 'Unknown')}")
            return True
        else:
            print("❌ Not logged into Azure")
            return False
    except Exception as e:
        print(f"❌ Error checking Azure login: {e}")
        return False


def login_to_azure():
    """Login to Azure"""
    print("🔐 Logging into Azure...")
    try:
        result = subprocess.run(['az', 'login'], check=True)
        print("✅ Successfully logged into Azure")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to login to Azure")
        return False


def list_subscriptions():
    """List available Azure subscriptions"""
    try:
        result = subprocess.run(['az', 'account', 'list'], capture_output=True, text=True, check=True)
        subscriptions = json.loads(result.stdout)
        
        print("\n📋 Available subscriptions:")
        for i, sub in enumerate(subscriptions, 1):
            status = "✅" if sub.get('isDefault') else "  "
            print(f"{status} {i}. {sub['name']} ({sub['id']})")
        
        return subscriptions
    except Exception as e:
        print(f"❌ Error listing subscriptions: {e}")
        return []


def set_subscription(subscription_id):
    """Set the active Azure subscription"""
    try:
        subprocess.run(['az', 'account', 'set', '--subscription', subscription_id], check=True)
        print(f"✅ Set active subscription to: {subscription_id}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to set subscription: {subscription_id}")
        return False


def create_resource_group(name, location):
    """Create a resource group"""
    try:
        result = subprocess.run([
            'az', 'group', 'create',
            '--name', name,
            '--location', location
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ Created resource group: {name}")
        return True
    except subprocess.CalledProcessError as e:
        if "already exists" in e.stderr:
            print(f"ℹ️  Resource group {name} already exists")
            return True
        else:
            print(f"❌ Failed to create resource group: {e.stderr}")
            return False


def create_search_service(service_name, resource_group, sku, location):
    """Create Azure AI Search service"""
    try:
        print(f"🔍 Creating Azure AI Search service: {service_name}")
        print("⏳ This may take a few minutes...")
        
        result = subprocess.run([
            'az', 'search', 'service', 'create',
            '--name', service_name,
            '--resource-group', resource_group,
            '--sku', sku,
            '--location', location
        ], capture_output=True, text=True, check=True)
        
        service_info = json.loads(result.stdout)
        print(f"✅ Created search service: {service_name}")
        return service_info
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create search service: {e.stderr}")
        return None


def get_search_service_details(service_name, resource_group):
    """Get search service endpoint and keys"""
    try:
        # Get service details
        result = subprocess.run([
            'az', 'search', 'service', 'show',
            '--name', service_name,
            '--resource-group', resource_group
        ], capture_output=True, text=True, check=True)
        
        service_info = json.loads(result.stdout)
        endpoint = f"https://{service_info['hostName']}"
        
        # Get admin key
        key_result = subprocess.run([
            'az', 'search', 'admin-key', 'show',
            '--service-name', service_name,
            '--resource-group', resource_group
        ], capture_output=True, text=True, check=True)
        
        key_info = json.loads(key_result.stdout)
        admin_key = key_info['primaryKey']
        
        return {
            'endpoint': endpoint,
            'admin_key': admin_key,
            'service_name': service_name
        }
    except Exception as e:
        print(f"❌ Error getting service details: {e}")
        return None


def update_env_file(endpoint, api_key, index_name):
    """Update the .env file with Azure AI Search details"""
    env_file = Path('.env')
    env_template = Path('.env.template')
    
    # Read template if .env doesn't exist
    if not env_file.exists() and env_template.exists():
        with open(env_template, 'r') as f:
            content = f.read()
    elif env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        print("❌ No .env or .env.template file found")
        return False
    
    # Update the values
    content = content.replace(
        'AZURE_SEARCH_SERVICE_ENDPOINT=https://your-service-name.search.windows.net',
        f'AZURE_SEARCH_SERVICE_ENDPOINT={endpoint}'
    )
    content = content.replace(
        'AZURE_SEARCH_API_KEY=your-api-key-here',
        f'AZURE_SEARCH_API_KEY={api_key}'
    )
    content = content.replace(
        'AZURE_SEARCH_INDEX_NAME=sample-index',
        f'AZURE_SEARCH_INDEX_NAME={index_name}'
    )
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated .env file with Azure AI Search configuration")
    return True


def test_connection():
    """Test the Azure AI Search connection"""
    try:
        result = subprocess.run([sys.executable, 'scripts/test_connection.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Connection test passed!")
            return True
        else:
            print("❌ Connection test failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Azure AI Search Service Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_azure_cli():
        return False
    
    if not check_azure_login():
        if input("\nWould you like to login to Azure? (y/N): ").lower().strip() == 'y':
            if not login_to_azure():
                return False
        else:
            print("❌ Azure login required to continue")
            return False
    
    # List and select subscription
    subscriptions = list_subscriptions()
    if not subscriptions:
        return False
    
    if len(subscriptions) > 1:
        try:
            choice = input(f"\nSelect subscription (1-{len(subscriptions)}, or press Enter for default): ").strip()
            if choice:
                sub_index = int(choice) - 1
                if 0 <= sub_index < len(subscriptions):
                    if not set_subscription(subscriptions[sub_index]['id']):
                        return False
        except ValueError:
            print("Invalid selection, using default subscription")
    
    # Get service configuration
    print("\n🔧 Service Configuration")
    service_name = input("Enter search service name (must be globally unique): ").strip()
    if not service_name:
        print("❌ Service name is required")
        return False
    
    resource_group = input("Enter resource group name [rg-search-handbook]: ").strip() or "rg-search-handbook"
    
    print("\nAvailable SKUs:")
    print("1. free (Free tier - good for learning)")
    print("2. basic (Basic tier - ~$250/month)")
    print("3. standard (Standard tier - ~$250/month)")
    
    sku_choice = input("Select SKU (1-3) [1]: ").strip() or "1"
    sku_map = {"1": "free", "2": "basic", "3": "standard"}
    sku = sku_map.get(sku_choice, "free")
    
    location = input("Enter location [eastus]: ").strip() or "eastus"
    index_name = input("Enter default index name [handbook-samples]: ").strip() or "handbook-samples"
    
    # Create resource group
    print(f"\n📁 Creating resource group: {resource_group}")
    if not create_resource_group(resource_group, location):
        return False
    
    # Create search service
    service_info = create_search_service(service_name, resource_group, sku, location)
    if not service_info:
        return False
    
    # Get service details
    print("\n🔍 Getting service details...")
    details = get_search_service_details(service_name, resource_group)
    if not details:
        return False
    
    print(f"\n✅ Service created successfully!")
    print(f"📋 Service Details:")
    print(f"   Name: {details['service_name']}")
    print(f"   Endpoint: {details['endpoint']}")
    print(f"   Admin Key: {details['admin_key'][:8]}...")
    
    # Update .env file
    if input("\nUpdate .env file with these settings? (Y/n): ").lower().strip() != 'n':
        if update_env_file(details['endpoint'], details['admin_key'], index_name):
            print("\n🧪 Testing connection...")
            if test_connection():
                print("\n🎉 Setup completed successfully!")
                print("\n📋 Next steps:")
                print("1. Start learning: docs/beginner/module-01-introduction-setup/")
                print("2. Generate sample data: python3 scripts/generate_sample_data.py")
                print("3. Run Jupyter notebooks: jupyter notebook")
                return True
    
    print(f"\n📝 Manual configuration required:")
    print(f"Update your .env file with:")
    print(f"AZURE_SEARCH_SERVICE_ENDPOINT={details['endpoint']}")
    print(f"AZURE_SEARCH_API_KEY={details['admin_key']}")
    print(f"AZURE_SEARCH_INDEX_NAME={index_name}")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)