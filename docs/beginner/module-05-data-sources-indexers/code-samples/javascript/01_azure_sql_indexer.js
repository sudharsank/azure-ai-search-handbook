#!/usr/bin/env node

/**
 * Azure AI Search - SQL Database Indexer Example (JavaScript)
 * 
 * This example demonstrates how to:
 * 1. Create a data source connection to Azure SQL Database
 * 2. Create an index for SQL data
 * 3. Create and configure an indexer
 * 4. Monitor indexer execution
 * 5. Implement change tracking for incremental updates
 * 
 * Prerequisites:
 * - Azure AI Search service
 * - Azure SQL Database with sample data
 * - Required Node.js packages: @azure/search-documents, @azure/identity
 */

const { SearchIndexClient, SearchIndexerClient } = require('@azure/search-documents');
const { AzureKeyCredential } = require('@azure/core-auth');
const { RestError } = require('@azure/core-rest-pipeline');
require('dotenv').config();

class SQLIndexerExample {
    constructor() {
        // Load configuration from environment variables
        this.endpoint = process.env.SEARCH_ENDPOINT;
        this.apiKey = process.env.SEARCH_API_KEY;
        this.sqlConnectionString = process.env.SQL_CONNECTION_STRING;
        
        if (!this.endpoint || !this.apiKey || !this.sqlConnectionString) {
            throw new Error('Missing required environment variables');
        }
        
        // Initialize clients
        const credential = new AzureKeyCredential(this.apiKey);
        this.indexClient = new SearchIndexClient(this.endpoint, credential);
        this.indexerClient = new SearchIndexerClient(this.endpoint, credential);
        
        // Configuration
        this.dataSourceName = 'sql-hotels-datasource';
        this.indexName = 'hotels-sql-index';
        this.indexerName = 'hotels-sql-indexer';
        this.tableName = 'Hotels';
    }
    
    /**
     * Create a data source connection to Azure SQL Database
     */
    async createDataSource() {
        console.log(`Creating data source: ${this.dataSourceName}`);
        
        const dataSource = {
            name: this.dataSourceName,
            type: 'azuresql',
            connectionString: this.sqlConnectionString,
            container: { name: this.tableName },
            dataChangeDetectionPolicy: {
                '@odata.type': '#Microsoft.Azure.Search.SqlIntegratedChangeTrackingPolicy'
            },
            description: 'Hotels data from Azure SQL Database'
        };
        
        try {
            const result = await this.indexerClient.createOrUpdateDataSourceConnection(dataSource);
            console.log(`✅ Data source '${this.dataSourceName}' created successfully`);
            return result;
        } catch (error) {
            console.error(`❌ Error creating data source: ${error.message}`);
            throw error;
        }
    }
    
    /**
     * Create a search index for hotel data
     */
    async createIndex() {
        console.log(`Creating index: ${this.indexName}`);
        
        const index = {
            name: this.indexName,
            fields: [
                {
                    name: 'HotelId',
                    type: 'Edm.String',
                    key: true,
                    retrievable: true
                },
                {
                    name: 'HotelName',
                    type: 'Edm.String',
                    searchable: true,
                    retrievable: true,
                    analyzer: 'en.lucene'
                },
                {
                    name: 'Description',
                    type: 'Edm.String',
                    searchable: true,
                    retrievable: true,
                    analyzer: 'en.lucene'
                },
                {
                    name: 'Category',
                    type: 'Edm.String',
                    filterable: true,
                    facetable: true,
                    retrievable: true
                },
                {
                    name: 'Rating',
                    type: 'Edm.Double',
                    filterable: true,
                    sortable: true,
                    facetable: true,
                    retrievable: true
                },
                {
                    name: 'Address',
                    type: 'Edm.ComplexType',
                    fields: [
                        {
                            name: 'StreetAddress',
                            type: 'Edm.String',
                            retrievable: true
                        },
                        {
                            name: 'City',
                            type: 'Edm.String',
                            filterable: true,
                            sortable: true,
                            facetable: true,
                            retrievable: true
                        },
                        {
                            name: 'StateProvince',
                            type: 'Edm.String',
                            filterable: true,
                            facetable: true,
                            retrievable: true
                        },
                        {
                            name: 'PostalCode',
                            type: 'Edm.String',
                            filterable: true,
                            retrievable: true
                        },
                        {
                            name: 'Country',
                            type: 'Edm.String',
                            filterable: true,
                            facetable: true,
                            retrievable: true
                        }
                    ]
                },
                {
                    name: 'LastRenovationDate',
                    type: 'Edm.DateTimeOffset',
                    filterable: true,
                    sortable: true,
                    retrievable: true
                }
            ]
        };
        
        try {
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Index '${this.indexName}' created successfully`);
            return result;
        } catch (error) {
            console.error(`❌ Error creating index: ${error.message}`);
            throw error;
        }
    }
    
    /**
     * Create an indexer to populate the index from SQL data
     */
    async createIndexer() {
        console.log(`Creating indexer: ${this.indexerName}`);
        
        const indexer = {
            name: this.indexerName,
            dataSourceName: this.dataSourceName,
            targetIndexName: this.indexName,
            fieldMappings: [
                { sourceFieldName: 'HotelId', targetFieldName: 'HotelId' },
                { sourceFieldName: 'HotelName', targetFieldName: 'HotelName' },
                { sourceFieldName: 'Description', targetFieldName: 'Description' },
                { sourceFieldName: 'Category', targetFieldName: 'Category' },
                { sourceFieldName: 'Rating', targetFieldName: 'Rating' },
                { sourceFieldName: 'Address', targetFieldName: 'Address/StreetAddress' },
                { sourceFieldName: 'City', targetFieldName: 'Address/City' },
                { sourceFieldName: 'StateProvince', targetFieldName: 'Address/StateProvince' },
                { sourceFieldName: 'PostalCode', targetFieldName: 'Address/PostalCode' },
                { sourceFieldName: 'Country', targetFieldName: 'Address/Country' },
                { sourceFieldName: 'LastRenovationDate', targetFieldName: 'LastRenovationDate' }
            ],
            description: 'Indexer for hotels data from SQL Database',
            parameters: {
                batchSize: 100,
                maxFailedItems: 10,
                maxFailedItemsPerBatch: 5
            }
        };
        
        try {
            const result = await this.indexerClient.createOrUpdateIndexer(indexer);
            console.log(`✅ Indexer '${this.indexerName}' created successfully`);
            return result;
        } catch (error) {
            console.error(`❌ Error creating indexer: ${error.message}`);
            throw error;
        }
    }
    
    /**
     * Run the indexer and monitor its execution
     */
    async runIndexer() {
        console.log(`Running indexer: ${this.indexerName}`);
        
        try {
            // Start the indexer
            await this.indexerClient.runIndexer(this.indexerName);
            console.log('✅ Indexer started successfully');
            
            // Monitor execution
            await this.monitorIndexerExecution();
            
        } catch (error) {
            console.error(`❌ Error running indexer: ${error.message}`);
            throw error;
        }
    }
    
    /**
     * Monitor indexer execution until completion or timeout
     */
    async monitorIndexerExecution(timeoutSeconds = 300) {
        console.log('Monitoring indexer execution...');
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeoutSeconds * 1000) {
            try {
                const status = await this.indexerClient.getIndexerStatus(this.indexerName);
                
                console.log(`Status: ${status.status}`);
                
                if (status.lastResult) {
                    console.log(`Items processed: ${status.lastResult.itemCount || 0}`);
                    console.log(`Items failed: ${status.lastResult.failedItemCount || 0}`);
                    console.log(`Start time: ${status.lastResult.startTime}`);
                    console.log(`End time: ${status.lastResult.endTime}`);
                    
                    // Check for errors
                    if (status.lastResult.errors && status.lastResult.errors.length > 0) {
                        console.log('Errors encountered:');
                        status.lastResult.errors.forEach(error => {
                            console.log(`  - ${error.errorMessage}`);
                        });
                    }
                    
                    // Check for warnings
                    if (status.lastResult.warnings && status.lastResult.warnings.length > 0) {
                        console.log('Warnings:');
                        status.lastResult.warnings.forEach(warning => {
                            console.log(`  - ${warning.message}`);
                        });
                    }
                }
                
                // Check if execution is complete
                if (status.status === 'success' || status.status === 'error') {
                    console.log(`✅ Indexer execution completed with status: ${status.status}`);
                    break;
                }
                
                // Wait before checking again
                await new Promise(resolve => setTimeout(resolve, 10000));
                
            } catch (error) {
                console.error(`Error checking indexer status: ${error.message}`);
                break;
            }
        }
    }
    
    /**
     * Get and display current indexer status
     */
    async getIndexerStatus() {
        try {
            const status = await this.indexerClient.getIndexerStatus(this.indexerName);
            
            console.log(`\n=== Indexer Status: ${this.indexerName} ===`);
            console.log(`Status: ${status.status}`);
            console.log(`Last run status: ${status.lastResult ? status.lastResult.status : 'Never run'}`);
            
            if (status.lastResult) {
                console.log(`Items processed: ${status.lastResult.itemCount || 0}`);
                console.log(`Items failed: ${status.lastResult.failedItemCount || 0}`);
                console.log(`Execution time: ${status.lastResult.startTime} - ${status.lastResult.endTime}`);
                
                if (status.executionHistory) {
                    console.log(`Total executions: ${status.executionHistory.length}`);
                }
            }
            
        } catch (error) {
            console.error(`Error getting indexer status: ${error.message}`);
        }
    }
    
    /**
     * Reset the indexer to clear its execution state
     */
    async resetIndexer() {
        try {
            await this.indexerClient.resetIndexer(this.indexerName);
            console.log(`✅ Indexer '${this.indexerName}' reset successfully`);
        } catch (error) {
            console.error(`❌ Error resetting indexer: ${error.message}`);
        }
    }
    
    /**
     * Clean up created resources
     */
    async deleteResources() {
        console.log('Cleaning up resources...');
        
        try {
            await this.indexerClient.deleteIndexer(this.indexerName);
            console.log(`✅ Deleted indexer: ${this.indexerName}`);
        } catch (error) {
            // Ignore errors during cleanup
        }
        
        try {
            await this.indexClient.deleteIndex(this.indexName);
            console.log(`✅ Deleted index: ${this.indexName}`);
        } catch (error) {
            // Ignore errors during cleanup
        }
        
        try {
            await this.indexerClient.deleteDataSourceConnection(this.dataSourceName);
            console.log(`✅ Deleted data source: ${this.dataSourceName}`);
        } catch (error) {
            // Ignore errors during cleanup
        }
    }
    
    /**
     * Run the complete SQL indexer example
     */
    async runCompleteExample() {
        console.log('=== Azure AI Search SQL Indexer Example ===\n');
        
        try {
            // Step 1: Create data source
            await this.createDataSource();
            
            // Step 2: Create index
            await this.createIndex();
            
            // Step 3: Create indexer
            await this.createIndexer();
            
            // Step 4: Run indexer
            await this.runIndexer();
            
            // Step 5: Check final status
            await this.getIndexerStatus();
            
            console.log('\n✅ SQL indexer example completed successfully!');
            
        } catch (error) {
            console.error(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

// Main execution
async function main() {
    try {
        const example = new SQLIndexerExample();
        await example.runCompleteExample();
        
        // Optionally clean up resources
        const readline = require('readline').createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        readline.question('\nDo you want to clean up the created resources? (y/n): ', async (answer) => {
            if (answer.toLowerCase() === 'y') {
                await example.deleteResources();
            }
            readline.close();
            process.exit(0);
        });
        
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

// Run the example if this file is executed directly
if (require.main === module) {
    main();
}

module.exports = SQLIndexerExample;