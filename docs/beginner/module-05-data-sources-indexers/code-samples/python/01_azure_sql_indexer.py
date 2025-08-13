#!/usr/bin/env python3
"""
Azure AI Search - SQL Database Indexer Example

This example demonstrates how to:
1. Create a data source connection to Azure SQL Database
2. Create an index for SQL data
3. Create and configure an indexer
4. Monitor indexer execution
5. Implement change tracking for incremental updates

Prerequisites:
- Azure AI Search service
- Azure SQL Database with sample data
- Required Python packages: azure-search-documents, azure-identity
"""

import os
import time
from typing import Optional
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
    SqlIntegratedChangeTrackingPolicy,
    FieldMapping,
    SimpleField,
    SearchableField,
    ComplexField
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

class SQLIndexerExample:
    """Example class for Azure SQL Database indexer operations."""
    
    def __init__(self):
        """Initialize the SQL indexer example with Azure credentials."""
        self.endpoint = os.getenv('SEARCH_ENDPOINT')
        self.api_key = os.getenv('SEARCH_API_KEY')
        self.sql_connection_string = os.getenv('SQL_CONNECTION_STRING')
        
        if not all([self.endpoint, self.api_key, self.sql_connection_string]):
            raise ValueError("Missing required environment variables")
        
        # Initialize clients
        credential = AzureKeyCredential(self.api_key)
        self.index_client = SearchIndexClient(self.endpoint, credential)
        self.indexer_client = SearchIndexerClient(self.endpoint, credential)
        
        # Configuration
        self.data_source_name = "sql-hotels-datasource"
        self.index_name = "hotels-sql-index"
        self.indexer_name = "hotels-sql-indexer"
        self.table_name = "Hotels"  # Adjust based on your table name
    
    def create_data_source(self) -> SearchIndexerDataSourceConnection:
        """
        Create a data source connection to Azure SQL Database.
        
        Returns:
            SearchIndexerDataSourceConnection: The created data source
        """
        print(f"Creating data source: {self.data_source_name}")
        
        # Configure data source with change tracking
        data_source = SearchIndexerDataSourceConnection(
            name=self.data_source_name,
            type=SearchIndexerDataSourceType.AZURE_SQL,
            connection_string=self.sql_connection_string,
            container=SearchIndexerDataContainer(name=self.table_name),
            data_change_detection_policy=SqlIntegratedChangeTrackingPolicy(),
            description="Hotels data from Azure SQL Database"
        )
        
        try:
            # Create or update the data source
            result = self.indexer_client.create_or_update_data_source_connection(data_source)
            print(f"✓ Data source '{self.data_source_name}' created successfully")
            return result
        except HttpResponseError as e:
            print(f"✗ Error creating data source: {e.message}")
            raise
    
    def create_index(self) -> SearchIndex:
        """
        Create a search index for hotel data.
        
        Returns:
            SearchIndex: The created search index
        """
        print(f"Creating index: {self.index_name}")
        
        # Define index fields based on SQL table schema
        fields = [
            SimpleField(name="HotelId", type=SearchFieldDataType.String, key=True),
            SearchableField(name="HotelName", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="Description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SimpleField(name="Category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="Rating", type=SearchFieldDataType.Double, filterable=True, sortable=True, facetable=True),
            ComplexField(name="Address", fields=[
                SimpleField(name="StreetAddress", type=SearchFieldDataType.String),
                SimpleField(name="City", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
                SimpleField(name="StateProvince", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SimpleField(name="PostalCode", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="Country", type=SearchFieldDataType.String, filterable=True, facetable=True)
            ]),
            SimpleField(name="LastRenovationDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True)
        ]
        
        # Create the index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            scoring_profiles=[],
            cors_options=None
        )
        
        try:
            result = self.index_client.create_or_update_index(index)
            print(f"✓ Index '{self.index_name}' created successfully")
            return result
        except HttpResponseError as e:
            print(f"✗ Error creating index: {e.message}")
            raise
    
    def create_indexer(self) -> SearchIndexer:
        """
        Create an indexer to populate the index from SQL data.
        
        Returns:
            SearchIndexer: The created indexer
        """
        print(f"Creating indexer: {self.indexer_name}")
        
        # Define field mappings if source and target field names differ
        field_mappings = [
            FieldMapping(source_field_name="HotelId", target_field_name="HotelId"),
            FieldMapping(source_field_name="HotelName", target_field_name="HotelName"),
            FieldMapping(source_field_name="Description", target_field_name="Description"),
            FieldMapping(source_field_name="Category", target_field_name="Category"),
            FieldMapping(source_field_name="Rating", target_field_name="Rating"),
            # Complex field mapping for address
            FieldMapping(source_field_name="Address", target_field_name="Address/StreetAddress"),
            FieldMapping(source_field_name="City", target_field_name="Address/City"),
            FieldMapping(source_field_name="StateProvince", target_field_name="Address/StateProvince"),
            FieldMapping(source_field_name="PostalCode", target_field_name="Address/PostalCode"),
            FieldMapping(source_field_name="Country", target_field_name="Address/Country"),
            FieldMapping(source_field_name="LastRenovationDate", target_field_name="LastRenovationDate")
        ]
        
        # Create indexer configuration
        indexer = SearchIndexer(
            name=self.indexer_name,
            data_source_name=self.data_source_name,
            target_index_name=self.index_name,
            field_mappings=field_mappings,
            description="Indexer for hotels data from SQL Database",
            parameters={
                "batchSize": 100,  # Process 100 documents at a time
                "maxFailedItems": 10,  # Allow up to 10 failed items
                "maxFailedItemsPerBatch": 5  # Allow up to 5 failures per batch
            }
        )
        
        try:
            result = self.indexer_client.create_or_update_indexer(indexer)
            print(f"✓ Indexer '{self.indexer_name}' created successfully")
            return result
        except HttpResponseError as e:
            print(f"✗ Error creating indexer: {e.message}")
            raise
    
    def run_indexer(self) -> None:
        """Run the indexer and monitor its execution."""
        print(f"Running indexer: {self.indexer_name}")
        
        try:
            # Start the indexer
            self.indexer_client.run_indexer(self.indexer_name)
            print("✓ Indexer started successfully")
            
            # Monitor execution
            self.monitor_indexer_execution()
            
        except HttpResponseError as e:
            print(f"✗ Error running indexer: {e.message}")
            raise
    
    def monitor_indexer_execution(self, timeout_seconds: int = 300) -> None:
        """
        Monitor indexer execution until completion or timeout.
        
        Args:
            timeout_seconds: Maximum time to wait for completion
        """
        print("Monitoring indexer execution...")
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                status = self.indexer_client.get_indexer_status(self.indexer_name)
                
                print(f"Status: {status.status}")
                
                if status.last_result:
                    print(f"Items processed: {status.last_result.item_count}")
                    print(f"Items failed: {status.last_result.failed_item_count}")
                    print(f"Start time: {status.last_result.start_time}")
                    print(f"End time: {status.last_result.end_time}")
                    
                    # Check for errors
                    if status.last_result.errors:
                        print("Errors encountered:")
                        for error in status.last_result.errors:
                            print(f"  - {error.error_message}")
                    
                    # Check for warnings
                    if status.last_result.warnings:
                        print("Warnings:")
                        for warning in status.last_result.warnings:
                            print(f"  - {warning.message}")
                
                # Check if execution is complete
                if status.status in ["success", "error"]:
                    print(f"✓ Indexer execution completed with status: {status.status}")
                    break
                
                # Wait before checking again
                time.sleep(10)
                
            except HttpResponseError as e:
                print(f"Error checking indexer status: {e.message}")
                break
        else:
            print("⚠ Indexer monitoring timed out")
    
    def get_indexer_status(self) -> None:
        """Get and display current indexer status."""
        try:
            status = self.indexer_client.get_indexer_status(self.indexer_name)
            
            print(f"\n=== Indexer Status: {self.indexer_name} ===")
            print(f"Status: {status.status}")
            print(f"Last run status: {status.last_result.status if status.last_result else 'Never run'}")
            
            if status.last_result:
                print(f"Items processed: {status.last_result.item_count}")
                print(f"Items failed: {status.last_result.failed_item_count}")
                print(f"Execution time: {status.last_result.start_time} - {status.last_result.end_time}")
                
                if status.execution_history:
                    print(f"Total executions: {len(status.execution_history)}")
                    
        except HttpResponseError as e:
            print(f"Error getting indexer status: {e.message}")
    
    def reset_indexer(self) -> None:
        """Reset the indexer to clear its execution state."""
        try:
            self.indexer_client.reset_indexer(self.indexer_name)
            print(f"✓ Indexer '{self.indexer_name}' reset successfully")
        except HttpResponseError as e:
            print(f"✗ Error resetting indexer: {e.message}")
    
    def delete_resources(self) -> None:
        """Clean up created resources."""
        print("Cleaning up resources...")
        
        try:
            # Delete indexer
            self.indexer_client.delete_indexer(self.indexer_name)
            print(f"✓ Deleted indexer: {self.indexer_name}")
        except HttpResponseError:
            pass
        
        try:
            # Delete index
            self.index_client.delete_index(self.index_name)
            print(f"✓ Deleted index: {self.index_name}")
        except HttpResponseError:
            pass
        
        try:
            # Delete data source
            self.indexer_client.delete_data_source_connection(self.data_source_name)
            print(f"✓ Deleted data source: {self.data_source_name}")
        except HttpResponseError:
            pass
    
    def run_complete_example(self) -> None:
        """Run the complete SQL indexer example."""
        print("=== Azure AI Search SQL Indexer Example ===\n")
        
        try:
            # Step 1: Create data source
            self.create_data_source()
            
            # Step 2: Create index
            self.create_index()
            
            # Step 3: Create indexer
            self.create_indexer()
            
            # Step 4: Run indexer
            self.run_indexer()
            
            # Step 5: Check final status
            self.get_indexer_status()
            
            print("\n✓ SQL indexer example completed successfully!")
            
        except Exception as e:
            print(f"\n✗ Example failed: {str(e)}")
            raise


def main():
    """Main function to run the SQL indexer example."""
    try:
        example = SQLIndexerExample()
        example.run_complete_example()
        
        # Optionally clean up resources
        cleanup = input("\nDo you want to clean up the created resources? (y/n): ")
        if cleanup.lower() == 'y':
            example.delete_resources()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())