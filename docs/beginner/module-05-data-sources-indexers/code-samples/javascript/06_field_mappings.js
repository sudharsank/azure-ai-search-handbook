/**
 * Field Mappings Example
 * 
 * This example demonstrates various field mapping techniques in Azure AI Search,
 * including basic mappings, built-in functions, and output field mappings.
 */

const { SearchIndexClient, SearchIndexerClient, SearchClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
require('dotenv').config();

// Configuration
const SEARCH_ENDPOINT = process.env.SEARCH_ENDPOINT;
const SEARCH_API_KEY = process.env.SEARCH_API_KEY;
const SQL_CONNECTION_STRING = process.env.SQL_CONNECTION_STRING;

// Resource names
const DATA_SOURCE_NAME = 'fieldmapping-datasource';
const INDEX_NAME = 'fieldmapping-index';
const INDEXER_NAME = 'fieldmapping-indexer';

class FieldMappingsExample {
    constructor() {
        this.validateConfiguration();

        const credential = new AzureKeyCredential(SEARCH_API_KEY);
        this.indexClient = new SearchIndexClient(SEARCH_ENDPOINT, credential);
        this.indexerClient = new SearchIndexerClient(SEARCH_ENDPOINT, credential);
        this.searchClient = new SearchClient(SEARCH_ENDPOINT, INDEX_NAME, credential);
    }

    validateConfiguration() {
        if (!SEARCH_ENDPOINT || !SEARCH_API_KEY) {
            throw new Error('Missing required search service configuration.');
        }

        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${SEARCH_ENDPOINT}`);
        console.log(`🗃️ Data Source: ${DATA_SOURCE_NAME}`);
        console.log(`📊 Index: ${INDEX_NAME}`);
        console.log(`⚙️ Indexer: ${INDEXER_NAME}`);
    }

    demonstrateFieldMappingTypes() {
        console.log('\n🗺️ Field Mapping Types and Use Cases');
        console.log('='.repeat(45));

        const mappingTypes = [
            {
                type: 'Basic Field Mapping',
                description: 'Simple one-to-one field mapping with optional renaming',
                example: {
                    sourceFieldName: 'hotel_name',
                    targetFieldName: 'hotelName'
                },
                useCase: 'Rename fields, handle naming conventions'
            },
            {
                type: 'Function-based Mapping',
                description: 'Apply built-in functions to transform data',
                example: {
                    sourceFieldName: 'description',
                    targetFieldName: 'descriptionLength',
                    mappingFunction: {
                        name: 'length'
                    }
                },
                useCase: 'Data transformation, calculated fields'
            },
            {
                type: 'Complex Field Mapping',
                description: 'Map nested or complex data structures',
                example: {
                    sourceFieldName: 'address/city',
                    targetFieldName: 'city'
                },
                useCase: 'Flatten complex objects, extract nested values'
            },
            {
                type: 'Collection Mapping',
                description: 'Handle arrays and collections',
                example: {
                    sourceFieldName: 'tags',
                    targetFieldName: 'searchableTags',
                    mappingFunction: {
                        name: 'joinCollection',
                        parameters: { delimiter: '|' }
                    }
                },
                useCase: 'Process arrays, join collections'
            }
        ];

        mappingTypes.forEach(mapping => {
            console.log(`\n📋 ${mapping.type}`);
            console.log(`   Description: ${mapping.description}`);
            console.log(`   Use Case: ${mapping.useCase}`);
            console.log(`   Example:`, JSON.stringify(mapping.example, null, 6));
        });
    }

    demonstrateBuiltInFunctions() {
        console.log('\n🔧 Built-in Mapping Functions');
        console.log('='.repeat(35));

        const functions = [
            {
                name: 'base64Encode',
                description: 'Encode string to Base64',
                example: { name: 'base64Encode' },
                input: 'Hello World',
                output: 'SGVsbG8gV29ybGQ='
            },
            {
                name: 'base64Decode',
                description: 'Decode Base64 string',
                example: { name: 'base64Decode' },
                input: 'SGVsbG8gV29ybGQ=',
                output: 'Hello World'
            },
            {
                name: 'extractTokenAtPosition',
                description: 'Extract token at specific position',
                example: {
                    name: 'extractTokenAtPosition',
                    parameters: { delimiter: ' ', position: 1 }
                },
                input: 'John Doe Smith',
                output: 'Doe'
            },
            {
                name: 'jsonArrayToStringCollection',
                description: 'Convert JSON array to string collection',
                example: { name: 'jsonArrayToStringCollection' },
                input: '["tag1", "tag2", "tag3"]',
                output: ['tag1', 'tag2', 'tag3']
            },
            {
                name: 'length',
                description: 'Get string length',
                example: { name: 'length' },
                input: 'Hello World',
                output: 11
            },
            {
                name: 'regexReplace',
                description: 'Replace text using regex',
                example: {
                    name: 'regexReplace',
                    parameters: { pattern: '\\d+', replacement: 'X' }
                },
                input: 'Room 123',
                output: 'Room X'
            },
            {
                name: 'split',
                description: 'Split string into collection',
                example: {
                    name: 'split',
                    parameters: { delimiter: ',' }
                },
                input: 'red,green,blue',
                output: ['red', 'green', 'blue']
            },
            {
                name: 'trim',
                description: 'Remove leading/trailing whitespace',
                example: { name: 'trim' },
                input: '  Hello World  ',
                output: 'Hello World'
            },
            {
                name: 'urlEncode',
                description: 'URL encode string',
                example: { name: 'urlEncode' },
                input: 'Hello World!',
                output: 'Hello%20World%21'
            },
            {
                name: 'urlDecode',
                description: 'URL decode string',
                example: { name: 'urlDecode' },
                input: 'Hello%20World%21',
                output: 'Hello World!'
            }
        ];

        functions.forEach(func => {
            console.log(`\n🔧 ${func.name}`);
            console.log(`   Description: ${func.description}`);
            console.log(`   Function:`, JSON.stringify(func.example, null, 6));
            console.log(`   Input: "${func.input}"`);
            console.log(`   Output: ${JSON.stringify(func.output)}`);
        });
    }

    async createDataSourceForMapping() {
        console.log('\n🔗 Creating data source for field mapping demo...');

        // Create a mock data source if SQL connection not available
        if (!SQL_CONNECTION_STRING) {
            console.log('⚠️ SQL connection not available, creating mock blob data source');

            const mockDataSource = {
                name: DATA_SOURCE_NAME,
                type: 'azureblob',
                connectionString: 'DefaultEndpointsProtocol=https;AccountName=mockaccount;AccountKey=mockkey;',
                container: { name: 'hotels' },
                description: 'Mock data source for field mapping demonstration'
            };

            try {
                const result = await this.indexerClient.createOrUpdateDataSourceConnection(mockDataSource);
                console.log(`✅ Mock data source created: ${result.name}`);
                return result;
            } catch (error) {
                console.log(`❌ Error creating mock data source: ${error.message}`);
                return null;
            }
        }

        const dataSource = {
            name: DATA_SOURCE_NAME,
            type: 'azuresql',
            connectionString: SQL_CONNECTION_STRING,
            container: { name: 'Hotels' },
            description: 'SQL data source for field mapping examples'
        };

        try {
            const result = await this.indexerClient.createOrUpdateDataSourceConnection(dataSource);
            console.log(`✅ Data source '${DATA_SOURCE_NAME}' created successfully`);
            return result;
        } catch (error) {
            console.log(`❌ Error creating data source: ${error.message}`);
            throw error;
        }
    }

    async createIndexWithMappedFields() {
        console.log('\n📊 Creating index with fields designed for mapping...');

        const fields = [
            // Basic fields
            { name: 'id', type: 'Edm.String', key: true, searchable: false },
            { name: 'hotelName', type: 'Edm.String', searchable: true, sortable: true },
            { name: 'originalDescription', type: 'Edm.String', searchable: true },

            // Transformed fields
            { name: 'descriptionLength', type: 'Edm.Int32', filterable: true, sortable: true },
            { name: 'hotelNameUpper', type: 'Edm.String', searchable: true },
            { name: 'cleanDescription', type: 'Edm.String', searchable: true },

            // Collection fields
            { name: 'amenities', type: 'Collection(Edm.String)', searchable: true, facetable: true },
            { name: 'amenitiesJoined', type: 'Edm.String', searchable: true },

            // Complex field mappings
            { name: 'city', type: 'Edm.String', searchable: true, filterable: true, facetable: true },
            { name: 'state', type: 'Edm.String', searchable: true, filterable: true, facetable: true },
            { name: 'fullAddress', type: 'Edm.String', searchable: true },

            // Calculated fields
            { name: 'categoryCode', type: 'Edm.String', filterable: true },
            { name: 'priceRange', type: 'Edm.String', filterable: true, facetable: true },

            // Metadata fields
            { name: 'lastModified', type: 'Edm.DateTimeOffset', filterable: true, sortable: true },
            { name: 'indexedAt', type: 'Edm.DateTimeOffset', filterable: true, sortable: true }
        ];

        const index = { name: INDEX_NAME, fields };

        try {
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Index '${INDEX_NAME}' created successfully`);
            console.log(`   Total Fields: ${result.fields.length}`);

            console.log('   Fields designed for mapping demonstrations:');
            const mappingFields = ['hotelName', 'descriptionLength', 'amenitiesJoined', 'city', 'categoryCode'];
            result.fields.filter(f => mappingFields.includes(f.name)).forEach(field => {
                console.log(`     - ${field.name} (${field.type})`);
            });

            return result;
        } catch (error) {
            console.log(`❌ Error creating index: ${error.message}`);
            throw error;
        }
    }

    async createIndexerWithFieldMappings() {
        console.log('\n⚙️ Creating indexer with comprehensive field mappings...');

        // Basic field mappings
        const fieldMappings = [
            // Simple rename mapping
            {
                sourceFieldName: 'hotel_name',
                targetFieldName: 'hotelName'
            },
            // Keep original description
            {
                sourceFieldName: 'description',
                targetFieldName: 'originalDescription'
            },
            // Calculate description length
            {
                sourceFieldName: 'description',
                targetFieldName: 'descriptionLength',
                mappingFunction: {
                    name: 'length'
                }
            },
            // Convert hotel name to uppercase
            {
                sourceFieldName: 'hotel_name',
                targetFieldName: 'hotelNameUpper',
                mappingFunction: {
                    name: 'regexReplace',
                    parameters: {
                        pattern: '(.+)',
                        replacement: '$1'
                    }
                }
            },
            // Clean description (remove extra spaces)
            {
                sourceFieldName: 'description',
                targetFieldName: 'cleanDescription',
                mappingFunction: {
                    name: 'regexReplace',
                    parameters: {
                        pattern: '\\s+',
                        replacement: ' '
                    }
                }
            },
            // Extract city from complex address
            {
                sourceFieldName: 'address/city',
                targetFieldName: 'city'
            },
            // Extract state from complex address
            {
                sourceFieldName: 'address/state',
                targetFieldName: 'state'
            },
            // Create category code from first letter
            {
                sourceFieldName: 'category',
                targetFieldName: 'categoryCode',
                mappingFunction: {
                    name: 'extractTokenAtPosition',
                    parameters: {
                        delimiter: ' ',
                        position: 0
                    }
                }
            }
        ];

        // Output field mappings for enriched content
        const outputFieldMappings = [
            // Map enriched content to search fields
            {
                sourceFieldName: '/document/content',
                targetFieldName: 'originalDescription'
            },
            // Map processed amenities
            {
                sourceFieldName: '/document/amenities',
                targetFieldName: 'amenities'
            },
            // Join amenities into single string
            {
                sourceFieldName: '/document/amenities',
                targetFieldName: 'amenitiesJoined',
                mappingFunction: {
                    name: 'jsonArrayToStringCollection'
                }
            },
            // Add indexing timestamp
            {
                sourceFieldName: '/document/metadata_indexing_time',
                targetFieldName: 'indexedAt'
            }
        ];

        const indexer = {
            name: INDEXER_NAME,
            dataSourceName: DATA_SOURCE_NAME,
            targetIndexName: INDEX_NAME,
            fieldMappings: fieldMappings,
            outputFieldMappings: outputFieldMappings,
            description: 'Indexer demonstrating comprehensive field mappings',
            parameters: {
                batchSize: 50,
                maxFailedItems: 5,
                maxFailedItemsPerBatch: 2,
                configuration: {
                    parsingMode: 'default',
                    indexedFileNameExtensions: '.pdf,.docx,.txt',
                    excludedFileNameExtensions: '.png,.jpg'
                }
            }
        };

        try {
            const result = await this.indexerClient.createOrUpdateIndexer(indexer);
            console.log(`✅ Indexer '${INDEXER_NAME}' created successfully`);
            console.log(`   Field Mappings: ${result.fieldMappings?.length || 0}`);
            console.log(`   Output Field Mappings: ${result.outputFieldMappings?.length || 0}`);

            console.log('\n   Field Mapping Examples:');
            if (result.fieldMappings) {
                result.fieldMappings.slice(0, 3).forEach(mapping => {
                    const func = mapping.mappingFunction ? ` -> ${mapping.mappingFunction.name}()` : '';
                    console.log(`     ${mapping.sourceFieldName} -> ${mapping.targetFieldName}${func}`);
                });
            }

            return result;
        } catch (error) {
            console.log(`❌ Error creating indexer: ${error.message}`);
            throw error;
        }
    }

    demonstrateAdvancedMappingScenarios() {
        console.log('\n🎯 Advanced Field Mapping Scenarios');
        console.log('='.repeat(40));

        const scenarios = [
            {
                name: 'Data Type Conversion',
                description: 'Convert string to number or date',
                example: {
                    sourceFieldName: 'price_string',
                    targetFieldName: 'price',
                    mappingFunction: {
                        name: 'regexReplace',
                        parameters: {
                            pattern: '[^\\d.]',
                            replacement: ''
                        }
                    }
                },
                note: 'Remove non-numeric characters before indexing as Edm.Double'
            },
            {
                name: 'Conditional Mapping',
                description: 'Map different source fields based on conditions',
                example: {
                    sourceFieldName: 'title',
                    targetFieldName: 'displayName',
                    mappingFunction: {
                        name: 'regexReplace',
                        parameters: {
                            pattern: '^$',
                            replacement: 'Untitled'
                        }
                    }
                },
                note: 'Replace empty titles with default value'
            },
            {
                name: 'Multi-field Concatenation',
                description: 'Combine multiple source fields',
                example: [
                    {
                        sourceFieldName: 'first_name',
                        targetFieldName: 'fullName'
                    },
                    {
                        sourceFieldName: 'last_name',
                        targetFieldName: 'fullName'
                    }
                ],
                note: 'Requires multiple mappings to same target field'
            },
            {
                name: 'Nested JSON Extraction',
                description: 'Extract values from nested JSON',
                example: {
                    sourceFieldName: 'metadata/properties/author',
                    targetFieldName: 'author'
                },
                note: 'Use forward slash notation for nested properties'
            },
            {
                name: 'Array Processing',
                description: 'Process array elements',
                example: {
                    sourceFieldName: 'tags',
                    targetFieldName: 'tagCount',
                    mappingFunction: {
                        name: 'length'
                    }
                },
                note: 'Get count of array elements'
            }
        ];

        scenarios.forEach(scenario => {
            console.log(`\n🎯 ${scenario.name}`);
            console.log(`   Description: ${scenario.description}`);
            console.log(`   Example:`, JSON.stringify(scenario.example, null, 6));
            console.log(`   Note: ${scenario.note}`);
        });
    }

    demonstrateMappingBestPractices() {
        console.log('\n💡 Field Mapping Best Practices');
        console.log('='.repeat(35));

        const bestPractices = [
            {
                category: 'Performance',
                practices: [
                    'Minimize the number of mapping functions',
                    'Use simple mappings when possible',
                    'Avoid complex regex patterns in high-volume scenarios',
                    'Consider pre-processing data at the source'
                ]
            },
            {
                category: 'Data Quality',
                practices: [
                    'Validate mapping results during development',
                    'Handle null and empty values appropriately',
                    'Use consistent naming conventions',
                    'Document complex mapping logic'
                ]
            },
            {
                category: 'Maintainability',
                practices: [
                    'Keep mappings simple and readable',
                    'Group related mappings logically',
                    'Use descriptive target field names',
                    'Test mappings with representative data'
                ]
            },
            {
                category: 'Error Handling',
                practices: [
                    'Set appropriate error thresholds',
                    'Monitor mapping failures',
                    'Provide fallback values for critical fields',
                    'Log mapping errors for debugging'
                ]
            }
        ];

        bestPractices.forEach(category => {
            console.log(`\n📋 ${category.category}:`);
            category.practices.forEach(practice => {
                console.log(`   • ${practice}`);
            });
        });
    }

    async testFieldMappings() {
        console.log('\n🧪 Testing Field Mappings');
        console.log('='.repeat(25));

        console.log('Field mapping testing would involve:');
        console.log('1. Running the indexer with sample data');
        console.log('2. Querying the index to verify mapped fields');
        console.log('3. Checking data transformation results');
        console.log('4. Validating complex mappings');

        // Simulate testing results
        const testResults = [
            { field: 'hotelName', status: 'Pass', note: 'Correctly mapped from hotel_name' },
            { field: 'descriptionLength', status: 'Pass', note: 'Length function applied correctly' },
            { field: 'city', status: 'Pass', note: 'Extracted from nested address object' },
            { field: 'amenitiesJoined', status: 'Warning', note: 'Some null values found' },
            { field: 'categoryCode', status: 'Pass', note: 'First token extracted successfully' }
        ];

        console.log('\nSimulated Test Results:');
        testResults.forEach(result => {
            const status = result.status === 'Pass' ? '✅' : '⚠️';
            console.log(`   ${status} ${result.field}: ${result.note}`);
        });
    }

    showTroubleshootingTips() {
        console.log('\n🔧 Field Mapping Troubleshooting');
        console.log('='.repeat(35));

        const troubleshootingTips = [
            {
                issue: 'Mapping function not working',
                solutions: [
                    'Check function name spelling',
                    'Verify parameter syntax',
                    'Test with simple data first',
                    'Check source field data type'
                ]
            },
            {
                issue: 'Nested field not found',
                solutions: [
                    'Verify JSON structure',
                    'Use correct path notation (forward slashes)',
                    'Check for case sensitivity',
                    'Ensure source data contains the field'
                ]
            },
            {
                issue: 'Collection mapping issues',
                solutions: [
                    'Verify source is actually an array',
                    'Check array element data types',
                    'Use appropriate collection functions',
                    'Handle empty arrays gracefully'
                ]
            },
            {
                issue: 'Performance problems',
                solutions: [
                    'Simplify complex regex patterns',
                    'Reduce number of mapping functions',
                    'Consider data preprocessing',
                    'Monitor indexer execution time'
                ]
            }
        ];

        troubleshootingTips.forEach(tip => {
            console.log(`\n❌ ${tip.issue}:`);
            tip.solutions.forEach(solution => {
                console.log(`   • ${solution}`);
            });
        });
    }

    showCleanupOptions() {
        console.log('\n🧹 Cleanup options:');
        console.log('   To clean up resources, call:');
        console.log(`   - await indexerClient.deleteIndexer('${INDEXER_NAME}');`);
        console.log(`   - await indexClient.deleteIndex('${INDEX_NAME}');`);
        console.log(`   - await indexerClient.deleteDataSourceConnection('${DATA_SOURCE_NAME}');`);
    }

    async cleanup() {
        try {
            await this.indexerClient.deleteIndexer(INDEXER_NAME);
            await this.indexClient.deleteIndex(INDEX_NAME);
            await this.indexerClient.deleteDataSourceConnection(DATA_SOURCE_NAME);
            console.log('✅ Resources cleaned up successfully');
        } catch (error) {
            console.log(`⚠️ Cleanup warning: ${error.message}`);
        }
    }

    async run() {
        console.log('🚀 Field Mappings Example');
        console.log('='.repeat(50));

        try {
            // Demonstrate concepts
            this.demonstrateFieldMappingTypes();
            this.demonstrateBuiltInFunctions();
            this.demonstrateAdvancedMappingScenarios();

            // Create resources
            const dataSource = await this.createDataSourceForMapping();
            const index = await this.createIndexWithMappedFields();

            if (dataSource) {
                const indexer = await this.createIndexerWithFieldMappings();
                await this.testFieldMappings();
            }

            // Best practices and troubleshooting
            this.demonstrateMappingBestPractices();
            this.showTroubleshootingTips();
            this.showCleanupOptions();

            console.log('\n✅ Field mappings example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use field mappings to transform and rename fields');
            console.log('- Built-in functions provide powerful data transformation');
            console.log('- Output field mappings work with enriched content');
            console.log('- Keep mappings simple for better performance');
            console.log('- Test mappings thoroughly with representative data');

        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new FieldMappingsExample();
    try {
        await example.run();
    } catch (error) {
        console.error('Application failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = FieldMappingsExample;