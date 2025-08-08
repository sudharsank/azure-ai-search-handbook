"""
Azure AI Search Connection Utilities
Common utilities for connecting to and working with Azure AI Search
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from dotenv import load_dotenv


@dataclass
class SearchConfig:
    """Configuration class for Azure AI Search connection"""
    endpoint: str
    api_key: Optional[str] = None
    index_name: Optional[str] = None
    use_managed_identity: bool = False
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None


class AzureSearchConnectionManager:
    """Manages connections to Azure AI Search service"""
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """Initialize connection manager with configuration"""
        self.config = config or self._load_config_from_env()
        self.logger = self._setup_logging()
        
    def _load_config_from_env(self) -> SearchConfig:
        """Load configuration from environment variables"""
        load_dotenv()
        
        endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        if not endpoint:
            raise ValueError("AZURE_SEARCH_SERVICE_ENDPOINT environment variable is required")
        
        return SearchConfig(
            endpoint=endpoint,
            api_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
            use_managed_identity=os.getenv("USE_MANAGED_IDENTITY", "false").lower() == "true",
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            tenant_id=os.getenv("AZURE_TENANT_ID")
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the connection manager"""
        logger = logging.getLogger("azure_search_connection")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_credential(self):
        """Get appropriate credential based on configuration"""
        if self.config.use_managed_identity:
            if self.config.client_id and self.config.client_secret and self.config.tenant_id:
                return ClientSecretCredential(
                    tenant_id=self.config.tenant_id,
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret
                )
            else:
                return DefaultAzureCredential()
        elif self.config.api_key:
            return AzureKeyCredential(self.config.api_key)
        else:
            raise ValueError("Either API key or managed identity configuration is required")
    
    def get_search_client(self, index_name: Optional[str] = None) -> SearchClient:
        """Get a SearchClient for document operations"""
        index_name = index_name or self.config.index_name
        if not index_name:
            raise ValueError("Index name is required for SearchClient")
        
        credential = self._get_credential()
        client = SearchClient(
            endpoint=self.config.endpoint,
            index_name=index_name,
            credential=credential
        )
        
        self.logger.info(f"Created SearchClient for index: {index_name}")
        return client
    
    def get_index_client(self) -> SearchIndexClient:
        """Get a SearchIndexClient for index management operations"""
        credential = self._get_credential()
        client = SearchIndexClient(
            endpoint=self.config.endpoint,
            credential=credential
        )
        
        self.logger.info("Created SearchIndexClient for index management")
        return client
    
    def test_connection(self) -> bool:
        """Test connection to Azure AI Search service"""
        try:
            index_client = self.get_index_client()
            # Try to list indexes to test connection
            indexes = list(index_client.list_indexes())
            self.logger.info(f"Connection successful. Found {len(indexes)} indexes.")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get service statistics and information"""
        try:
            index_client = self.get_index_client()
            stats = index_client.get_service_statistics()
            return {
                "counters": {
                    "document_count": stats.counters.document_count,
                    "index_count": stats.counters.index_count,
                    "indexer_count": stats.counters.indexer_count,
                    "data_source_count": stats.counters.data_source_count,
                    "storage_size": stats.counters.storage_size
                },
                "limits": {
                    "max_indexes_allowed": stats.limits.max_indexes_allowed,
                    "max_fields_per_index": stats.limits.max_fields_per_index,
                    "max_complex_collection_fields_per_index": stats.limits.max_complex_collection_fields_per_index,
                    "max_complex_objects_in_collections_per_document": stats.limits.max_complex_objects_in_collections_per_document
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get service statistics: {str(e)}")
            return {}
    
    def list_indexes(self) -> List[str]:
        """List all available indexes"""
        try:
            index_client = self.get_index_client()
            indexes = list(index_client.list_indexes())
            index_names = [index.name for index in indexes]
            self.logger.info(f"Found indexes: {index_names}")
            return index_names
        except Exception as e:
            self.logger.error(f"Failed to list indexes: {str(e)}")
            return []


def create_sample_config_file(file_path: str = "config/search_config.json"):
    """Create a sample configuration file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    sample_config = {
        "endpoint": "https://your-service-name.search.windows.net",
        "api_key": "your-api-key-here",
        "index_name": "sample-index",
        "use_managed_identity": False,
        "client_id": "your-client-id-for-managed-identity",
        "client_secret": "your-client-secret-for-managed-identity",
        "tenant_id": "your-tenant-id-for-managed-identity"
    }
    
    with open(file_path, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"Sample configuration file created at: {file_path}")


def load_config_from_file(file_path: str) -> SearchConfig:
    """Load configuration from JSON file"""
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    
    return SearchConfig(**config_data)


# Convenience functions for common operations
def get_default_search_client(index_name: Optional[str] = None) -> SearchClient:
    """Get a default SearchClient using environment configuration"""
    manager = AzureSearchConnectionManager()
    return manager.get_search_client(index_name)


def get_default_index_client() -> SearchIndexClient:
    """Get a default SearchIndexClient using environment configuration"""
    manager = AzureSearchConnectionManager()
    return manager.get_index_client()


def test_default_connection() -> bool:
    """Test connection using default environment configuration"""
    manager = AzureSearchConnectionManager()
    return manager.test_connection()


if __name__ == "__main__":
    # Example usage and testing
    print("Testing Azure AI Search connection...")
    
    try:
        manager = AzureSearchConnectionManager()
        
        # Test connection
        if manager.test_connection():
            print("✅ Connection successful!")
            
            # Get service statistics
            stats = manager.get_service_statistics()
            if stats:
                print(f"📊 Service Statistics:")
                print(f"  Documents: {stats['counters']['document_count']}")
                print(f"  Indexes: {stats['counters']['index_count']}")
                print(f"  Storage Size: {stats['counters']['storage_size']} bytes")
            
            # List indexes
            indexes = manager.list_indexes()
            if indexes:
                print(f"📋 Available Indexes: {', '.join(indexes)}")
            else:
                print("📋 No indexes found")
        else:
            print("❌ Connection failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure your environment variables are set correctly.")