#!/usr/bin/env node
/**
 * Module 3: Index Management - Advanced Schema Design (JavaScript)
 * ===============================================================
 * 
 * This example demonstrates advanced schema design patterns and best practices for
 * Azure AI Search indexes using JavaScript. You'll learn about complex fields,
 * collections, and optimization strategies for different use cases.
 * 
 * Learning Objectives:
 * - Design complex field structures in JavaScript
 * - Use complex fields for nested objects
 * - Optimize field attributes for performance
 * - Handle different data types effectively
 * - Implement schema design patterns
 * 
 * Prerequisites:
 * - Completed 01_create_basic_index.js
 * - Understanding of basic field types
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

const { SearchIndexClient, SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class AdvancedSchemaDesigner {
    /**
     * Initialize the schema designer
     */
    constructor() {
        this.endpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
        this.adminKey = process.env.AZURE_SEARCH_ADMIN_KEY;
        this.indexClient = null;
        
        if (!this.endpoint || !this.adminKey) {
            throw new Error('Missing required environment variables');
        }
    }
    
    /**
     * Create and validate the SearchIndexClient
     */
    async createIndexClient() {
        console.log('🔍 Creating SearchIndexClient...');
        
        try {
            this.indexClient = new SearchIndexClient(
                this.endpoint,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Test connection
            const stats = await this.indexClient.getServiceStatistics();
            console.log('✅ Connected to Azure AI Search service');
            return true;
            
        } catch (error) {
            console.log(`❌ Failed to create index client: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Design a comprehensive e-commerce product schema
     */
    designEcommerceSchema() {
        console.log('🛍️  Designing E-commerce Product Schema...');
        
        const fields = [
            // Primary key
            {
                name: 'productId',
                type: 'Edm.String',
                key: true,
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Basic product information
            {
                name: 'name',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'
            },
            
            {
                name: 'description',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'
            },
            
            {
                name: 'shortDescription',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Categorization
            {
                name: 'category',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'subcategory',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'brand',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Product attributes
            {
                name: 'sku',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'model',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'color',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'size',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Collections for multiple values
            {
                name: 'tags',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'features',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'imageUrls',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Inventory and availability
            {
                name: 'inStock',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'stockQuantity',
                type: 'Edm.Int32',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'availabilityDate',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Dates
            {
                name: 'createdDate',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'lastModified',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Geographic information
            {
                name: 'originCountry',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Status flags
            {
                name: 'isActive',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'isFeatured',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'isOnSale',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Complex field for product dimensions
            {
                name: 'dimensions',
                type: 'Edm.ComplexType',
                fields: [
                    {
                        name: 'length',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'width',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'height',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'weight',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'unit',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    }
                ]
            },
            
            // Complex field for pricing information
            {
                name: 'pricing',
                type: 'Edm.ComplexType',
                fields: [
                    {
                        name: 'basePrice',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'salePrice',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'currency',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'discountPercentage',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'validUntil',
                        type: 'Edm.DateTimeOffset',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    }
                ]
            },
            
            // Complex field for manufacturer information
            {
                name: 'manufacturer',
                type: 'Edm.ComplexType',
                fields: [
                    {
                        name: 'name',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: true,
                        retrievable: true
                    },
                    {
                        name: 'country',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: true,
                        retrievable: true
                    },
                    {
                        name: 'website',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'supportEmail',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    }
                ]
            },
            
            // Complex field for ratings and reviews
            {
                name: 'reviews',
                type: 'Edm.ComplexType',
                fields: [
                    {
                        name: 'averageRating',
                        type: 'Edm.Double',
                        searchable: false,
                        filterable: true,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'totalReviews',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: false,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'fiveStarCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'fourStarCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'threeStarCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'twoStarCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'oneStarCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    }
                ]
            }
        ];
        
        console.log(`✅ E-commerce schema designed with ${fields.length} fields`);
        this.displaySchemaSummary(fields);
        
        return fields;
    }
    
    /**
     * Design a schema for document management system
     */
    designDocumentManagementSchema() {
        console.log('📄 Designing Document Management Schema...');
        
        const fields = [
            // Primary key
            {
                name: 'documentId',
                type: 'Edm.String',
                key: true,
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Basic document information
            {
                name: 'title',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'
            },
            
            {
                name: 'content',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'
            },
            
            {
                name: 'summary',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Document classification
            {
                name: 'documentType',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'category',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'subcategory',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // File information
            {
                name: 'fileName',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'filePath',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'fileUrl',
                type: 'Edm.String',
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Dates
            {
                name: 'createdDate',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'lastModified',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'lastAccessed',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'expirationDate',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Language and localization
            {
                name: 'language',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'locale',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Collections
            {
                name: 'keywords',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'tags',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'relatedDocuments',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Status and workflow
            {
                name: 'status',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'workflowStage',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'isArchived',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'isPublished',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Complex field for author information
            {
                name: 'author',
                type: 'Edm.ComplexType',
                fields: [
                    {
                        name: 'name',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'email',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'department',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: true,
                        retrievable: true
                    },
                    {
                        name: 'employeeId',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    }
                ]
            },
            
            // Complex field for document metadata
            {
                name: 'metadata',
                type: 'Edm.ComplexType',
                fields: [
                    {
                        name: 'fileSize',
                        type: 'Edm.Int64',
                        searchable: false,
                        filterable: true,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'fileType',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: true,
                        retrievable: true
                    },
                    {
                        name: 'mimeType',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: true,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'pageCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: true,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'wordCount',
                        type: 'Edm.Int32',
                        searchable: false,
                        filterable: true,
                        sortable: true,
                        facetable: false,
                        retrievable: true
                    },
                    {
                        name: 'checksum',
                        type: 'Edm.String',
                        searchable: false,
                        filterable: false,
                        sortable: false,
                        facetable: false,
                        retrievable: true
                    }
                ]
            }
        ];
        
        console.log(`✅ Document management schema designed with ${fields.length} fields`);
        this.displaySchemaSummary(fields);
        
        return fields;
    }
    
    /**
     * Design an optimized blog schema with performance considerations
     */
    designOptimizedBlogSchema() {
        console.log('📝 Designing Optimized Blog Schema...');
        
        const fields = [
            // Primary key
            {
                name: 'postId',
                type: 'Edm.String',
                key: true,
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Core content - optimized for search
            {
                name: 'title',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true,
                analyzer: 'en.microsoft'
            },
            
            {
                name: 'content',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: false,  // Don't return full content in results
                analyzer: 'en.microsoft'
            },
            
            {
                name: 'excerpt',
                type: 'Edm.String',
                searchable: true,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Author information - optimized for filtering
            {
                name: 'authorName',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'authorId',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Categorization - optimized for faceting
            {
                name: 'primaryCategory',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            {
                name: 'secondaryCategories',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Tags - limited facetable for performance
            {
                name: 'tags',
                type: 'Collection(Edm.String)',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: true,
                retrievable: true
            },
            
            // Dates - optimized for sorting and filtering
            {
                name: 'publishedDate',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'lastModified',
                type: 'Edm.DateTimeOffset',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Status fields - optimized for filtering
            {
                name: 'status',
                type: 'Edm.String',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'isPublished',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'isFeatured',
                type: 'Edm.Boolean',
                searchable: false,
                filterable: true,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Media
            {
                name: 'featuredImage',
                type: 'Edm.String',
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'imageAltText',
                type: 'Edm.String',
                searchable: false,
                filterable: false,
                sortable: false,
                facetable: false,
                retrievable: true
            },
            
            // Reading information
            {
                name: 'readingTimeMinutes',
                type: 'Edm.Int32',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            {
                name: 'wordCount',
                type: 'Edm.Int32',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            },
            
            // Engagement metrics - sortable for popularity
            {
                name: 'popularityScore',
                type: 'Edm.Double',
                searchable: false,
                filterable: true,
                sortable: true,
                facetable: false,
                retrievable: true
            }
        ];
        
        console.log(`✅ Optimized blog schema designed with ${fields.length} fields`);
        this.displaySchemaSummary(fields);
        
        return fields;
    }
    
    /**
     * Display a summary of the schema design
     */
    displaySchemaSummary(fields) {
        const fieldTypes = {};
        const attributes = { searchable: 0, filterable: 0, sortable: 0, facetable: 0, key: 0 };
        let complexFields = 0;
        let collectionFields = 0;
        
        for (const field of fields) {
            // Count field types
            const fieldType = field.type;
            fieldTypes[fieldType] = (fieldTypes[fieldType] || 0) + 1;
            
            // Count attributes
            if (field.key) attributes.key++;
            if (field.searchable) attributes.searchable++;
            if (field.filterable) attributes.filterable++;
            if (field.sortable) attributes.sortable++;
            if (field.facetable) attributes.facetable++;
            
            // Count special field types
            if (field.type === 'Edm.ComplexType') complexFields++;
            if (field.type.includes('Collection')) collectionFields++;
        }
        
        console.log('\n📊 Schema Summary:');
        console.log(`   Total fields: ${fields.length}`);
        console.log(`   Complex fields: ${complexFields}`);
        console.log(`   Collection fields: ${collectionFields}`);
        console.log(`   Searchable fields: ${attributes.searchable}`);
        console.log(`   Filterable fields: ${attributes.filterable}`);
        console.log(`   Sortable fields: ${attributes.sortable}`);
        console.log(`   Facetable fields: ${attributes.facetable}`);
        
        console.log('\n📈 Field Type Distribution:');
        for (const [fieldType, count] of Object.entries(fieldTypes).sort()) {
            console.log(`   ${fieldType}: ${count}`);
        }
    }
    
    /**
     * Create an index with the given schema and test it
     */
    async createAndTestSchema(indexName, fields, description) {
        console.log(`\n🏗️  Creating index '${indexName}' - ${description}`);
        
        try {
            // Create the index
            const index = {
                name: indexName,
                fields: fields
            };
            
            const result = await this.indexClient.createOrUpdateIndex(index);
            console.log(`✅ Index '${result.name}' created successfully`);
            
            // Test with a sample document
            return await this.testSchemaWithSampleData(indexName, fields);
            
        } catch (error) {
            console.log(`❌ Failed to create index: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Test the schema with appropriate sample data
     */
    async testSchemaWithSampleData(indexName, fields) {
        console.log(`🧪 Testing schema with sample data...`);
        
        try {
            const searchClient = new SearchClient(
                this.endpoint,
                indexName,
                new AzureKeyCredential(this.adminKey)
            );
            
            // Create sample document based on schema
            const sampleDoc = this.generateSampleDocument(fields);
            
            // Upload sample document
            const result = await searchClient.uploadDocuments([sampleDoc]);
            
            if (result.results[0].succeeded) {
                console.log('✅ Sample document uploaded successfully');
                
                // Wait for indexing
                await this.sleep(2000);
                
                // Verify document count
                const docCount = await searchClient.getDocumentCount();
                console.log(`✅ Index contains ${docCount} document(s)`);
                
                return true;
            } else {
                console.log(`❌ Sample document upload failed: ${result.results[0].errorMessage}`);
                return false;
            }
            
        } catch (error) {
            console.log(`❌ Schema test failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Generate a sample document that matches the schema
     */
    generateSampleDocument(fields) {
        const doc = {};
        
        for (const field of fields) {
            const fieldName = field.name;
            const fieldType = field.type;
            
            // Generate sample data based on field type
            if (field.key) {
                doc[fieldName] = 'sample-doc-1';
            } else if (fieldType === 'Edm.String') {
                doc[fieldName] = `Sample ${fieldName}`;
            } else if (fieldType === 'Edm.Int32') {
                doc[fieldName] = 42;
            } else if (fieldType === 'Edm.Int64') {
                doc[fieldName] = 1024;
            } else if (fieldType === 'Edm.Double') {
                doc[fieldName] = 4.5;
            } else if (fieldType === 'Edm.Boolean') {
                doc[fieldName] = true;
            } else if (fieldType === 'Edm.DateTimeOffset') {
                doc[fieldName] = '2024-02-10T10:00:00Z';
            } else if (fieldType.includes('Collection(Edm.String)')) {
                doc[fieldName] = ['sample', 'test', 'data'];
            } else if (fieldType === 'Edm.ComplexType') {
                // Generate nested object
                const nestedDoc = {};
                for (const nestedField of field.fields) {
                    const nestedFieldType = nestedField.type;
                    if (nestedFieldType === 'Edm.String') {
                        nestedDoc[nestedField.name] = `Sample ${nestedField.name}`;
                    } else if (nestedFieldType === 'Edm.Int32') {
                        nestedDoc[nestedField.name] = 10;
                    } else if (nestedFieldType === 'Edm.Int64') {
                        nestedDoc[nestedField.name] = 1024;
                    } else if (nestedFieldType === 'Edm.Double') {
                        nestedDoc[nestedField.name] = 1.5;
                    } else if (nestedFieldType === 'Edm.Boolean') {
                        nestedDoc[nestedField.name] = true;
                    } else if (nestedFieldType === 'Edm.DateTimeOffset') {
                        nestedDoc[nestedField.name] = '2024-02-10T10:00:00Z';
                    } else if (nestedFieldType.includes('Collection(Edm.String)')) {
                        nestedDoc[nestedField.name] = ['nested', 'sample'];
                    }
                }
                doc[fieldName] = nestedDoc;
            }
        }
        
        return doc;
    }
    
    /**
     * Compare different schema designs
     */
    compareSchemas(schemas) {
        console.log('\n📊 Schema Comparison:');
        console.log('='.repeat(80));
        
        const comparisonData = [];
        
        for (const [name, fields] of schemas) {
            const stats = {
                name: name,
                totalFields: fields.length,
                searchable: fields.filter(f => f.searchable).length,
                filterable: fields.filter(f => f.filterable).length,
                sortable: fields.filter(f => f.sortable).length,
                facetable: fields.filter(f => f.facetable).length,
                complex: fields.filter(f => f.type === 'Edm.ComplexType').length,
                collections: fields.filter(f => f.type.includes('Collection')).length
            };
            comparisonData.push(stats);
        }
        
        // Display comparison table
        const headers = ['Schema', 'Total', 'Search', 'Filter', 'Sort', 'Facet', 'Complex', 'Collections'];
        console.log(`${headers[0].padEnd(20)} | ${headers[1].padEnd(5)} | ${headers[2].padEnd(6)} | ${headers[3].padEnd(6)} | ${headers[4].padEnd(4)} | ${headers[5].padEnd(5)} | ${headers[6].padEnd(7)} | ${headers[7].padEnd(11)}`);
        console.log('-'.repeat(80));
        
        for (const stats of comparisonData) {
            console.log(`${stats.name.padEnd(20)} | ${stats.totalFields.toString().padEnd(5)} | ${stats.searchable.toString().padEnd(6)} | ${stats.filterable.toString().padEnd(6)} | ${stats.sortable.toString().padEnd(4)} | ${stats.facetable.toString().padEnd(5)} | ${stats.complex.toString().padEnd(7)} | ${stats.collections.toString().padEnd(11)}`);
        }
    }
    
    /**
     * Utility function to sleep for a specified number of milliseconds
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Main function demonstrating advanced schema design
 */
async function main() {
    console.log('='.repeat(60));
    console.log('Module 3: Advanced Schema Design Example (JavaScript)');
    console.log('='.repeat(60));
    
    // Initialize the schema designer
    let designer;
    try {
        designer = new AdvancedSchemaDesigner();
    } catch (error) {
        console.log(`❌ Configuration error: ${error.message}`);
        return;
    }
    
    // Create index client
    if (!(await designer.createIndexClient())) {
        console.log('❌ Failed to create index client. Exiting.');
        return;
    }
    
    // Design different schemas
    console.log('\n🎨 Designing Multiple Schema Patterns...');
    
    const ecommerceSchema = designer.designEcommerceSchema();
    const documentSchema = designer.designDocumentManagementSchema();
    const blogSchema = designer.designOptimizedBlogSchema();
    
    // Compare schemas
    const schemas = [
        ['E-commerce', ecommerceSchema],
        ['Document Mgmt', documentSchema],
        ['Optimized Blog', blogSchema]
    ];
    
    designer.compareSchemas(schemas);
    
    // Create and test one schema (user choice)
    console.log('\n🏗️  Schema Creation Options:');
    console.log('1. E-commerce Product Schema');
    console.log('2. Document Management Schema');
    console.log('3. Optimized Blog Schema');
    
    const readline = require('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    rl.question('\nWhich schema would you like to create and test? (1-3, or \'skip\'): ', async (choice) => {
        let success = true;
        
        if (choice === '1') {
            success = await designer.createAndTestSchema(
                'advanced-ecommerce-schema-js',
                ecommerceSchema,
                'E-commerce Product Schema'
            );
        } else if (choice === '2') {
            success = await designer.createAndTestSchema(
                'advanced-document-schema-js',
                documentSchema,
                'Document Management Schema'
            );
        } else if (choice === '3') {
            success = await designer.createAndTestSchema(
                'advanced-blog-schema-js',
                blogSchema,
                'Optimized Blog Schema'
            );
        } else {
            console.log('Skipping schema creation.');
        }
        
        if (success) {
            console.log('\n🎉 Advanced schema design completed successfully!');
        }
        
        console.log('\n' + '='.repeat(60));
        console.log('Example completed!');
        console.log('='.repeat(60));
        
        console.log('\n📚 What you learned:');
        console.log('✅ How to design complex field structures in JavaScript');
        console.log('✅ How to use complex fields for nested objects');
        console.log('✅ How to optimize field attributes for performance');
        console.log('✅ How to handle different data types effectively');
        console.log('✅ How to implement schema design patterns');
        console.log('✅ How to compare different schema approaches');
        
        console.log('\n🚀 Next steps:');
        console.log('1. Try creating your own schema for your use case');
        console.log('2. Experiment with different field attribute combinations');
        console.log('3. Run the next example: 03_data_ingestion.js');
        console.log('4. Test performance with different schema designs');
        
        rl.close();
    });
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Run the main function
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Application error:', error.message);
        process.exit(1);
    });
}

module.exports = { AdvancedSchemaDesigner };