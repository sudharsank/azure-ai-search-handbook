#!/usr/bin/env python3
"""
Advanced Field Mappings Example

This script demonstrates advanced field mapping techniques for Azure AI Search indexers,
including complex transformations, built-in functions, and output field mappings.

Prerequisites:
- Azure AI Search service
- Data sources with complex data structures
- Admin API key or managed identity
- Required Python packages installed
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, SearchIndexer,
    SearchIndexerDataContainer, SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType, FieldMapping, FieldMappingFunction,
    SimpleField, SearchableField, ComplexField
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv('SEARCH_ENDPOINT')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
SQL_CONNECTION_STRING = os.getenv('SQL_CONNECTION_STRING')

def validate_configuration():
    """Validate that required configuration is present."""
    if not all([SEARCH_ENDPOINT, SEARCH_API_KEY]):
        raise ValueError("Missing required search service configuration.")
    
    print("✅ Configuration validated")
    print(f"📍 Search Endpoint: {SEARCH_ENDPOINT}")

def demonstrate_basic_field_mappings():
    """Demonstrate basic field mapping concepts."""
    print("\n📋 Basic Field Mapping Concepts")
    print("=" * 30)
    
    print("Field mappings connect source data fields to target index fields.")
    print("They are essential when:")
    print("• Source field names differ from target field names")
    print("• Data transformation is needed")
    print("• Complex data structures need flattening")
    print("• Multiple source fields map to one target field")
    
    # Basic mapping examples
    basic_mappings = [
        {
            'source': 'customer_name',
            'target': 'customerName',
            'purpose': 'Field name transformation (snake_case to camelCase)'
        },
        {
            'source': 'created_date',
            'target': 'createdDate',
            'purpose': 'Date field mapping with potential format conversion'
        },
        {
            'source': 'product_description',
            'target': 'description',
            'purpose': 'Field name simplification'
        }
    ]
    
    print(f"\n📝 Basic Mapping Examples:")
    for mapping in basic_mappings:
        print(f"   {mapping['source']} → {mapping['target']}")
        print(f"      Purpose: {mapping['purpose']}")

def create_field_mapping_examples():
    """Create comprehensive field mapping examples."""
    print("\n🛠️ Field Mapping Examples")
    print("=" * 25)
    
    # Example 1: Basic field mappings
    print("\n1️⃣ Basic Field Mappings:")
    basic_mappings = [
        FieldMapping(source_field_name="ProductID", target_field_name="id"),
        FieldMapping(source_field_name="ProductName", target_field_name="name"),
        FieldMapping(source_field_name="ProductDescription", target_field_name="description"),
        FieldMapping(source_field_name="CategoryName", target_field_name="category"),
        FieldMapping(source_field_name="UnitPrice", target_field_name="price")
    ]
    
    for mapping in basic_mappings:
        print(f"   {mapping.source_field_name} → {mapping.target_field_name}")
    
    # Example 2: Mappings with built-in functions
    print("\n2️⃣ Mappings with Built-in Functions:")
    function_mappings = [
        FieldMapping(
            source_field_name="Tags",
            target_field_name="tags",
            mapping_function=FieldMappingFunction(
                name="splitAndTrim",
                parameters={"delimiter": ",", "trimWhitespace": True}
            )
        ),
        FieldMapping(
            source_field_name="FullName",
            target_field_name="searchableText",
            mapping_function=FieldMappingFunction(
                name="extractTokenAtPosition",
                parameters={"delimiter": " ", "position": 0}
            )
        ),
        FieldMapping(
            source_field_name="JsonData",
            target_field_name="extractedValue",
            mapping_function=FieldMappingFunction(
                name="jsonArrayToStringCollection"
            )
        )
    ]
    
    for mapping in function_mappings:
        func_name = mapping.mapping_function.name if mapping.mapping_function else "None"
        print(f"   {mapping.source_field_name} → {mapping.target_field_name} (function: {func_name})")
    
    return basic_mappings, function_mappings

def demonstrate_built_in_functions():
    """Demonstrate available built-in mapping functions."""
    print("\n🔧 Built-in Mapping Functions")
    print("=" * 30)
    
    functions = [
        {
            'name': 'base64Encode',
            'description': 'Encodes the input string using Base64',
            'parameters': None,
            'example': 'Convert binary data to Base64 string'
        },
        {
            'name': 'base64Decode',
            'description': 'Decodes a Base64 encoded string',
            'parameters': None,
            'example': 'Decode Base64 string to original value'
        },
        {
            'name': 'extractTokenAtPosition',
            'description': 'Extracts a token at specified position after splitting',
            'parameters': {'delimiter': 'string', 'position': 'int'},
            'example': 'Extract first name from "John Doe" using space delimiter'
        },
        {
            'name': 'jsonArrayToStringCollection',
            'description': 'Converts JSON array to string collection',
            'parameters': None,
            'example': 'Convert ["tag1", "tag2"] to searchable collection'
        },
        {
            'name': 'splitAndTrim',
            'description': 'Splits string and trims whitespace from each part',
            'parameters': {'delimiter': 'string', 'trimWhitespace': 'bool'},
            'example': 'Convert "tag1, tag2, tag3" to clean array'
        },
        {
            'name': 'urlEncode',
            'description': 'URL encodes the input string',
            'parameters': None,
            'example': 'Encode URLs for safe storage'
        },
        {
            'name': 'urlDecode',
            'description': 'URL decodes the input string',
            'parameters': None,
            'example': 'Decode URL-encoded strings'
        }
    ]
    
    for func in functions:
        print(f"\n🔧 {func['name']}")
        print(f"   Description: {func['description']}")
        if func['parameters']:
            print(f"   Parameters: {func['parameters']}")
        print(f"   Example: {func['example']}")

def create_complex_field_mapping_scenarios():
    """Create complex field mapping scenarios."""
    print("\n🎯 Complex Field Mapping Scenarios")
    print("=" * 35)
    
    scenarios = []
    
    # Scenario 1: E-commerce Product Data
    print("\n📦 Scenario 1: E-commerce Product Data")
    ecommerce_mappings = [
        # Basic mappings
        FieldMapping(source_field_name="ProductID", target_field_name="id"),
        FieldMapping(source_field_name="ProductName", target_field_name="name"),
        
        # Split categories from comma-separated string
        FieldMapping(
            source_field_name="Categories",
            target_field_name="categories",
            mapping_function=FieldMappingFunction(
                name="splitAndTrim",
                parameters={"delimiter": ",", "trimWhitespace": True}
            )
        ),
        
        # Extract brand from product name (first word)
        FieldMapping(
            source_field_name="ProductName",
            target_field_name="brand",
            mapping_function=FieldMappingFunction(
                name="extractTokenAtPosition",
                parameters={"delimiter": " ", "position": 0}
            )
        ),
        
        # Convert JSON specifications to searchable collection
        FieldMapping(
            source_field_name="SpecificationsJson",
            target_field_name="specifications",
            mapping_function=FieldMappingFunction(
                name="jsonArrayToStringCollection"
            )
        )
    ]
    
    scenarios.append(('E-commerce', ecommerce_mappings))
    
    for mapping in ecommerce_mappings:
        func_info = f" (function: {mapping.mapping_function.name})" if mapping.mapping_function else ""
        print(f"   {mapping.source_field_name} → {mapping.target_field_name}{func_info}")
    
    # Scenario 2: Document Management
    print("\n📄 Scenario 2: Document Management")
    document_mappings = [
        # Basic document fields
        FieldMapping(source_field_name="DocumentPath", target_field_name="id"),
        FieldMapping(source_field_name="Title", target_field_name="title"),
        
        # Extract file extension from path
        FieldMapping(
            source_field_name="DocumentPath",
            target_field_name="fileExtension",
            mapping_function=FieldMappingFunction(
                name="extractTokenAtPosition",
                parameters={"delimiter": ".", "position": -1}
            )
        ),
        
        # Split and clean author list
        FieldMapping(
            source_field_name="Authors",
            target_field_name="authorList",
            mapping_function=FieldMappingFunction(
                name="splitAndTrim",
                parameters={"delimiter": ";", "trimWhitespace": True}
            )
        ),
        
        # URL encode document path for safe linking
        FieldMapping(
            source_field_name="DocumentPath",
            target_field_name="encodedPath",
            mapping_function=FieldMappingFunction(
                name="urlEncode"
            )
        )
    ]
    
    scenarios.append(('Document Management', document_mappings))
    
    for mapping in document_mappings:
        func_info = f" (function: {mapping.mapping_function.name})" if mapping.mapping_function else ""
        print(f"   {mapping.source_field_name} → {mapping.target_field_name}{func_info}")
    
    return scenarios

def demonstrate_output_field_mappings():
    """Demonstrate output field mappings for skillsets."""
    print("\n🎨 Output Field Mappings (for Skillsets)")
    print("=" * 40)
    
    print("Output field mappings are used with cognitive skills to map")
    print("skill outputs to index fields. They're essential for:")
    print("• AI enrichment pipelines")
    print("• Custom skill outputs")
    print("• Complex data transformations")
    
    # Example output field mappings
    output_mappings = [
        {
            'source': '/document/content/keyphrases/*',
            'target': 'keyphrases',
            'description': 'Map extracted key phrases to collection field'
        },
        {
            'source': '/document/content/entities/*/name',
            'target': 'entityNames',
            'description': 'Extract entity names from entity recognition'
        },
        {
            'source': '/document/content/sentiment/score',
            'target': 'sentimentScore',
            'description': 'Map sentiment analysis score'
        },
        {
            'source': '/document/content/language',
            'target': 'detectedLanguage',
            'description': 'Map detected language from language detection skill'
        }
    ]
    
    print(f"\n📝 Output Field Mapping Examples:")
    for mapping in output_mappings:
        print(f"   {mapping['source']} → {mapping['target']}")
        print(f"      Purpose: {mapping['description']}")

def create_index_for_field_mapping_demo(index_client):
    """Create an index to demonstrate field mappings."""
    print("\n📊 Creating Demo Index for Field Mappings")
    print("=" * 40)
    
    index_name = "field-mapping-demo-index"
    
    # Define fields that will receive mapped data
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="name", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="price", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        
        # Fields for function mapping results
        SearchableField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), facetable=True),
        SearchableField(name="brand", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="specifications", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
        
        # Document-specific fields
        SearchableField(name="title", type=SearchFieldDataType.String),
        SimpleField(name="fileExtension", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="authorList", type=SearchFieldDataType.Collection(SearchFieldDataType.String), facetable=True),
        SimpleField(name="encodedPath", type=SearchFieldDataType.String),
        
        # AI enrichment fields
        SearchableField(name="keyphrases", type=SearchFieldDataType.Collection(SearchFieldDataType.String), facetable=True),
        SearchableField(name="entityNames", type=SearchFieldDataType.Collection(SearchFieldDataType.String), facetable=True),
        SimpleField(name="sentimentScore", type=SearchFieldDataType.Double, filterable=True, sortable=True),
        SimpleField(name="detectedLanguage", type=SearchFieldDataType.String, filterable=True, facetable=True)
    ]
    
    index = SearchIndex(name=index_name, fields=fields)
    
    try:
        result = index_client.create_or_update_index(index)
        print(f"✅ Demo index '{index_name}' created successfully")
        print(f"   Total Fields: {len(result.fields)}")
        
        # Show field categories
        basic_fields = [f.name for f in result.fields if f.name in ['id', 'name', 'description', 'category', 'price']]
        function_fields = [f.name for f in result.fields if f.name in ['tags', 'brand', 'specifications']]
        document_fields = [f.name for f in result.fields if f.name in ['title', 'fileExtension', 'authorList', 'encodedPath']]
        ai_fields = [f.name for f in result.fields if f.name in ['keyphrases', 'entityNames', 'sentimentScore', 'detectedLanguage']]
        
        print(f"   Basic Fields: {', '.join(basic_fields)}")
        print(f"   Function Mapping Fields: {', '.join(function_fields)}")
        print(f"   Document Fields: {', '.join(document_fields)}")
        print(f"   AI Enrichment Fields: {', '.join(ai_fields)}")
        
        return result
        
    except HttpResponseError as e:
        print(f"❌ Error creating demo index: {e.message}")
        return None

def demonstrate_field_mapping_best_practices():
    """Demonstrate best practices for field mappings."""
    print("\n💡 Field Mapping Best Practices")
    print("=" * 30)
    
    practices = [
        {
            'category': 'Performance',
            'practices': [
                'Use field mappings only when necessary',
                'Avoid complex transformations in high-volume scenarios',
                'Consider pre-processing data at the source when possible',
                'Test mapping functions with sample data first'
            ]
        },
        {
            'category': 'Data Quality',
            'practices': [
                'Validate mapping function parameters',
                'Handle null and empty values appropriately',
                'Test with edge cases and special characters',
                'Monitor for mapping errors in indexer execution'
            ]
        },
        {
            'category': 'Maintainability',
            'practices': [
                'Document complex mapping logic',
                'Use descriptive target field names',
                'Group related mappings logically',
                'Version control mapping configurations'
            ]
        },
        {
            'category': 'Troubleshooting',
            'practices': [
                'Test mappings with small data samples first',
                'Use indexer execution history to debug issues',
                'Validate source data format matches expectations',
                'Check for data type compatibility issues'
            ]
        }
    ]
    
    for category in practices:
        print(f"\n🎯 {category['category']}")
        for practice in category['practices']:
            print(f"   • {practice}")

def demonstrate_common_mapping_patterns():
    """Demonstrate common field mapping patterns and use cases."""
    print("\n🎨 Common Field Mapping Patterns")
    print("=" * 30)
    
    patterns = [
        {
            'pattern': 'Name Transformation',
            'description': 'Convert between naming conventions',
            'example': 'customer_name → customerName',
            'code': 'FieldMapping(source_field_name="customer_name", target_field_name="customerName")'
        },
        {
            'pattern': 'String Splitting',
            'description': 'Split delimited strings into collections',
            'example': '"tag1,tag2,tag3" → ["tag1", "tag2", "tag3"]',
            'code': '''FieldMapping(
    source_field_name="tags_string",
    target_field_name="tags",
    mapping_function=FieldMappingFunction(
        name="splitAndTrim",
        parameters={"delimiter": ",", "trimWhitespace": True}
    )
)'''
        },
        {
            'pattern': 'Token Extraction',
            'description': 'Extract specific parts from structured strings',
            'example': '"John Doe" → "John" (first name)',
            'code': '''FieldMapping(
    source_field_name="full_name",
    target_field_name="first_name",
    mapping_function=FieldMappingFunction(
        name="extractTokenAtPosition",
        parameters={"delimiter": " ", "position": 0}
    )
)'''
        },
        {
            'pattern': 'JSON Array Processing',
            'description': 'Convert JSON arrays to searchable collections',
            'example': '["skill1", "skill2"] → searchable collection',
            'code': '''FieldMapping(
    source_field_name="skills_json",
    target_field_name="skills",
    mapping_function=FieldMappingFunction(
        name="jsonArrayToStringCollection"
    )
)'''
        },
        {
            'pattern': 'URL Encoding',
            'description': 'Encode URLs for safe storage and linking',
            'example': '"path with spaces" → "path%20with%20spaces"',
            'code': '''FieldMapping(
    source_field_name="file_path",
    target_field_name="encoded_path",
    mapping_function=FieldMappingFunction(
        name="urlEncode"
    )
)'''
        }
    ]
    
    for pattern in patterns:
        print(f"\n🎯 {pattern['pattern']}")
        print(f"   Description: {pattern['description']}")
        print(f"   Example: {pattern['example']}")
        print(f"   Code:")
        for line in pattern['code'].split('\n'):
            print(f"     {line}")

def main():
    """Main execution function."""
    print("🚀 Advanced Field Mappings Example")
    print("=" * 50)
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize clients
        credential = AzureKeyCredential(SEARCH_API_KEY)
        index_client = SearchIndexClient(SEARCH_ENDPOINT, credential)
        indexer_client = SearchIndexerClient(SEARCH_ENDPOINT, credential)
        
        # Demonstrate concepts
        demonstrate_basic_field_mappings()
        
        # Create mapping examples
        basic_mappings, function_mappings = create_field_mapping_examples()
        
        # Show built-in functions
        demonstrate_built_in_functions()
        
        # Complex scenarios
        scenarios = create_complex_field_mapping_scenarios()
        
        # Output field mappings
        demonstrate_output_field_mappings()
        
        # Create demo index
        demo_index = create_index_for_field_mapping_demo(index_client)
        
        # Best practices
        demonstrate_field_mapping_best_practices()
        
        # Common patterns
        demonstrate_common_mapping_patterns()
        
        print("\n✅ Advanced field mappings example completed successfully!")
        print("\nKey takeaways:")
        print("- Field mappings bridge the gap between source data and target schema")
        print("- Built-in functions provide powerful data transformation capabilities")
        print("- Complex scenarios often require multiple mapping strategies")
        print("- Output field mappings are essential for AI enrichment pipelines")
        print("- Test mappings thoroughly with representative data samples")
        print("- Consider performance implications of complex transformations")
        
        if demo_index:
            print(f"\n🧹 Cleanup: Delete demo index with:")
            print(f"   index_client.delete_index('{demo_index.name}')")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()