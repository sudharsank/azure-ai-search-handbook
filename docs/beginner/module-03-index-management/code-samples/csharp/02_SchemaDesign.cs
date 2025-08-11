/*
 * Module 3: Index Management - Advanced Schema Design (C#)
 * =======================================================
 * 
 * This example demonstrates advanced schema design patterns and best practices for
 * Azure AI Search indexes using the .NET SDK. You'll learn about complex fields,
 * collections, and optimization strategies for different use cases.
 * 
 * Learning Objectives:
 * - Design complex field structures using SearchField
 * - Use complex fields for nested objects
 * - Optimize field attributes for performance
 * - Handle different data types effectively
 * - Implement schema design patterns
 * 
 * Prerequisites:
 * - Completed 01_CreateBasicIndex.cs
 * - Understanding of basic field types
 * - Azure AI Search service with admin access
 * 
 * Author: Azure AI Search Handbook
 * Module: Beginner - Module 3: Index Management
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace AzureSearchHandbook.Module03
{
    /// <summary>
    /// Demonstrates advanced schema design patterns using the .NET SDK
    /// </summary>
    public class AdvancedSchemaDesigner
    {
        private readonly string _endpoint;
        private readonly string _adminKey;
        private SearchIndexClient? _indexClient;

        /// <summary>
        /// Initialize the schema designer
        /// </summary>
        public AdvancedSchemaDesigner()
        {
            _endpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_ENDPOINT") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_SERVICE_ENDPOINT environment variable is required");
            
            _adminKey = Environment.GetEnvironmentVariable("AZURE_SEARCH_ADMIN_KEY") 
                ?? throw new InvalidOperationException("AZURE_SEARCH_ADMIN_KEY environment variable is required");
        }

        /// <summary>
        /// Create and validate the SearchIndexClient
        /// </summary>
        public async Task<bool> CreateIndexClientAsync()
        {
            Console.WriteLine("🔍 Creating SearchIndexClient...");

            try
            {
                _indexClient = new SearchIndexClient(
                    new Uri(_endpoint),
                    new AzureKeyCredential(_adminKey)
                );

                // Test connection
                var stats = await _indexClient.GetServiceStatisticsAsync();
                Console.WriteLine("✅ Connected to Azure AI Search service");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create index client: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Design a comprehensive e-commerce product schema
        /// </summary>
        public IList<SearchField> DesignEcommerceSchema()
        {
            Console.WriteLine("🛍️  Designing E-commerce Product Schema...");

            var fields = new List<SearchField>
            {
                // Primary key
                new SearchField("productId", SearchFieldDataType.String)
                {
                    IsKey = true,
                    IsSearchable = false,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Basic product information
                new SearchField("name", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true,
                    AnalyzerName = LexicalAnalyzerName.EnMicrosoft
                },

                new SearchField("description", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true,
                    AnalyzerName = LexicalAnalyzerName.EnMicrosoft
                },

                // Categorization
                new SearchField("category", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                new SearchField("brand", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                // Product attributes
                new SearchField("sku", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Collections for multiple values
                new SearchField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String))
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                new SearchField("features", SearchFieldDataType.Collection(SearchFieldDataType.String))
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                // Inventory and availability
                new SearchField("inStock", SearchFieldDataType.Boolean)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                new SearchField("stockQuantity", SearchFieldDataType.Int32)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Dates
                new SearchField("createdDate", SearchFieldDataType.DateTimeOffset)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                }
            };

            // Add complex fields for nested structures
            fields.AddRange(CreateComplexFields());

            Console.WriteLine($"✅ E-commerce schema designed with {fields.Count} fields");
            DisplaySchemaSummary(fields);

            return fields;
        }

        /// <summary>
        /// Create complex fields for nested data structures
        /// </summary>
        private IEnumerable<SearchField> CreateComplexFields()
        {
            // Complex field for product dimensions
            var dimensionsField = new SearchField("dimensions", SearchFieldDataType.Complex)
            {
                Fields =
                {
                    new SearchField("length", SearchFieldDataType.Double) { IsRetrievable = true },
                    new SearchField("width", SearchFieldDataType.Double) { IsRetrievable = true },
                    new SearchField("height", SearchFieldDataType.Double) { IsRetrievable = true },
                    new SearchField("weight", SearchFieldDataType.Double) { IsRetrievable = true },
                    new SearchField("unit", SearchFieldDataType.String) { IsRetrievable = true }
                }
            };

            // Complex field for pricing information
            var pricingField = new SearchField("pricing", SearchFieldDataType.Complex)
            {
                Fields =
                {
                    new SearchField("basePrice", SearchFieldDataType.Double) 
                    { 
                        IsRetrievable = true, 
                        IsSortable = true 
                    },
                    new SearchField("salePrice", SearchFieldDataType.Double) 
                    { 
                        IsRetrievable = true, 
                        IsSortable = true 
                    },
                    new SearchField("currency", SearchFieldDataType.String) 
                    { 
                        IsRetrievable = true, 
                        IsFilterable = true 
                    },
                    new SearchField("discountPercentage", SearchFieldDataType.Double) 
                    { 
                        IsRetrievable = true 
                    }
                }
            };

            // Complex field for manufacturer information
            var manufacturerField = new SearchField("manufacturer", SearchFieldDataType.Complex)
            {
                Fields =
                {
                    new SearchField("name", SearchFieldDataType.String) 
                    { 
                        IsRetrievable = true, 
                        IsFilterable = true, 
                        IsFacetable = true 
                    },
                    new SearchField("country", SearchFieldDataType.String) 
                    { 
                        IsRetrievable = true, 
                        IsFilterable = true, 
                        IsFacetable = true 
                    },
                    new SearchField("website", SearchFieldDataType.String) 
                    { 
                        IsRetrievable = true 
                    }
                }
            };

            // Complex field for reviews and ratings
            var reviewsField = new SearchField("reviews", SearchFieldDataType.Complex)
            {
                Fields =
                {
                    new SearchField("averageRating", SearchFieldDataType.Double) 
                    { 
                        IsRetrievable = true, 
                        IsFilterable = true, 
                        IsSortable = true 
                    },
                    new SearchField("totalReviews", SearchFieldDataType.Int32) 
                    { 
                        IsRetrievable = true, 
                        IsSortable = true 
                    },
                    new SearchField("fiveStarCount", SearchFieldDataType.Int32) 
                    { 
                        IsRetrievable = true 
                    }
                }
            };

            return new[] { dimensionsField, pricingField, manufacturerField, reviewsField };
        }

        /// <summary>
        /// Design an optimized blog schema with performance considerations
        /// </summary>
        public IList<SearchField> DesignOptimizedBlogSchema()
        {
            Console.WriteLine("📝 Designing Optimized Blog Schema...");

            var fields = new List<SearchField>
            {
                // Primary key
                new SearchField("postId", SearchFieldDataType.String)
                {
                    IsKey = true,
                    IsSearchable = false,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Core content - optimized for search
                new SearchField("title", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true,
                    AnalyzerName = LexicalAnalyzerName.EnMicrosoft
                },

                new SearchField("content", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = false,  // Don't return full content in results
                    AnalyzerName = LexicalAnalyzerName.EnMicrosoft
                },

                new SearchField("excerpt", SearchFieldDataType.String)
                {
                    IsSearchable = true,
                    IsFilterable = false,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Author information - optimized for filtering
                new SearchField("authorName", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                // Categorization - optimized for faceting
                new SearchField("primaryCategory", SearchFieldDataType.String)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                new SearchField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String))
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = true,
                    IsRetrievable = true
                },

                // Dates - optimized for sorting and filtering
                new SearchField("publishedDate", SearchFieldDataType.DateTimeOffset)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Status fields - optimized for filtering
                new SearchField("isPublished", SearchFieldDataType.Boolean)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = false,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Reading information
                new SearchField("readingTimeMinutes", SearchFieldDataType.Int32)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                },

                // Engagement metrics - sortable for popularity
                new SearchField("popularityScore", SearchFieldDataType.Double)
                {
                    IsSearchable = false,
                    IsFilterable = true,
                    IsSortable = true,
                    IsFacetable = false,
                    IsRetrievable = true
                }
            };

            Console.WriteLine($"✅ Optimized blog schema designed with {fields.Count} fields");
            DisplaySchemaSummary(fields);

            return fields;
        }

        /// <summary>
        /// Display a summary of the schema design
        /// </summary>
        private void DisplaySchemaSummary(IList<SearchField> fields)
        {
            var fieldTypes = new Dictionary<string, int>();
            var attributes = new Dictionary<string, int>
            {
                ["key"] = 0,
                ["searchable"] = 0,
                ["filterable"] = 0,
                ["sortable"] = 0,
                ["facetable"] = 0,
                ["retrievable"] = 0
            };

            var complexFields = 0;
            var collectionFields = 0;

            foreach (var field in fields)
            {
                // Count field types
                var fieldType = field.Type.ToString();
                fieldTypes[fieldType] = fieldTypes.GetValueOrDefault(fieldType, 0) + 1;

                // Count attributes
                if (field.IsKey == true) attributes["key"]++;
                if (field.IsSearchable == true) attributes["searchable"]++;
                if (field.IsFilterable == true) attributes["filterable"]++;
                if (field.IsSortable == true) attributes["sortable"]++;
                if (field.IsFacetable == true) attributes["facetable"]++;
                if (field.IsRetrievable == true) attributes["retrievable"]++;

                // Count special field types
                if (field.Type == SearchFieldDataType.Complex) complexFields++;
                if (field.Type.ToString().Contains("Collection")) collectionFields++;
            }

            Console.WriteLine("\n📊 Schema Summary:");
            Console.WriteLine($"   Total fields: {fields.Count}");
            Console.WriteLine($"   Complex fields: {complexFields}");
            Console.WriteLine($"   Collection fields: {collectionFields}");
            Console.WriteLine($"   Searchable fields: {attributes["searchable"]}");
            Console.WriteLine($"   Filterable fields: {attributes["filterable"]}");
            Console.WriteLine($"   Sortable fields: {attributes["sortable"]}");
            Console.WriteLine($"   Facetable fields: {attributes["facetable"]}");

            Console.WriteLine("\n📈 Field Type Distribution:");
            foreach (var (fieldType, count) in fieldTypes.OrderBy(kvp => kvp.Key))
            {
                Console.WriteLine($"   {fieldType}: {count}");
            }
        }

        /// <summary>
        /// Create an index with the given schema and test it
        /// </summary>
        public async Task<bool> CreateAndTestSchemaAsync(string indexName, IList<SearchField> fields, string description)
        {
            Console.WriteLine($"\n🏗️  Creating index '{indexName}' - {description}");

            try
            {
                // Create the index
                var index = new SearchIndex(indexName, fields);
                var result = await _indexClient!.CreateOrUpdateIndexAsync(index);

                Console.WriteLine($"✅ Index '{result.Value.Name}' created successfully");

                // Test with a sample document
                return await TestSchemaWithSampleDataAsync(indexName, fields);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Failed to create index: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Test the schema with appropriate sample data
        /// </summary>
        private async Task<bool> TestSchemaWithSampleDataAsync(string indexName, IList<SearchField> fields)
        {
            Console.WriteLine($"🧪 Testing schema with sample data...");

            try
            {
                var searchClient = new SearchClient(
                    new Uri(_endpoint),
                    indexName,
                    new AzureKeyCredential(_adminKey)
                );

                // Create sample document based on schema
                var sampleDoc = GenerateSampleDocument(fields);

                // Upload sample document
                var result = await searchClient.UploadDocumentsAsync(new[] { sampleDoc });

                if (result.Value.Results[0].Succeeded)
                {
                    Console.WriteLine("✅ Sample document uploaded successfully");

                    // Wait for indexing
                    await Task.Delay(2000);

                    // Verify document count
                    var docCount = await searchClient.GetDocumentCountAsync();
                    Console.WriteLine($"✅ Index contains {docCount.Value} document(s)");

                    return true;
                }
                else
                {
                    Console.WriteLine($"❌ Sample document upload failed: {result.Value.Results[0].ErrorMessage}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Schema test failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Generate a sample document that matches the schema
        /// </summary>
        private Dictionary<string, object> GenerateSampleDocument(IList<SearchField> fields)
        {
            var doc = new Dictionary<string, object>();

            foreach (var field in fields)
            {
                var fieldName = field.Name;
                var fieldType = field.Type;

                // Generate sample data based on field type
                if (field.IsKey == true)
                {
                    doc[fieldName] = "sample-doc-1";
                }
                else if (fieldType == SearchFieldDataType.String)
                {
                    doc[fieldName] = $"Sample {fieldName}";
                }
                else if (fieldType == SearchFieldDataType.Int32)
                {
                    doc[fieldName] = 42;
                }
                else if (fieldType == SearchFieldDataType.Int64)
                {
                    doc[fieldName] = 1024L;
                }
                else if (fieldType == SearchFieldDataType.Double)
                {
                    doc[fieldName] = 4.5;
                }
                else if (fieldType == SearchFieldDataType.Boolean)
                {
                    doc[fieldName] = true;
                }
                else if (fieldType == SearchFieldDataType.DateTimeOffset)
                {
                    doc[fieldName] = DateTimeOffset.Parse("2024-02-10T10:00:00Z");
                }
                else if (fieldType.ToString().Contains("Collection(Edm.String)"))
                {
                    doc[fieldName] = new[] { "sample", "test", "data" };
                }
                else if (fieldType == SearchFieldDataType.Complex)
                {
                    // Generate nested object
                    var nestedDoc = new Dictionary<string, object>();
                    foreach (var nestedField in field.Fields)
                    {
                        var nestedFieldType = nestedField.Type;
                        if (nestedFieldType == SearchFieldDataType.String)
                        {
                            nestedDoc[nestedField.Name] = $"Sample {nestedField.Name}";
                        }
                        else if (nestedFieldType == SearchFieldDataType.Int32)
                        {
                            nestedDoc[nestedField.Name] = 10;
                        }
                        else if (nestedFieldType == SearchFieldDataType.Double)
                        {
                            nestedDoc[nestedField.Name] = 1.5;
                        }
                        else if (nestedFieldType == SearchFieldDataType.Boolean)
                        {
                            nestedDoc[nestedField.Name] = true;
                        }
                    }
                    doc[fieldName] = nestedDoc;
                }
            }

            return doc;
        }

        /// <summary>
        /// Compare different schema designs
        /// </summary>
        public void CompareSchemas(List<(string Name, IList<SearchField> Fields)> schemas)
        {
            Console.WriteLine("\n📊 Schema Comparison:");
            Console.WriteLine("=".PadRight(80, '='));

            var comparisonData = new List<dynamic>();

            foreach (var (name, fields) in schemas)
            {
                var stats = new
                {
                    Name = name,
                    TotalFields = fields.Count,
                    Searchable = fields.Count(f => f.IsSearchable == true),
                    Filterable = fields.Count(f => f.IsFilterable == true),
                    Sortable = fields.Count(f => f.IsSortable == true),
                    Facetable = fields.Count(f => f.IsFacetable == true),
                    Complex = fields.Count(f => f.Type == SearchFieldDataType.Complex),
                    Collections = fields.Count(f => f.Type.ToString().Contains("Collection"))
                };
                comparisonData.Add(stats);
            }

            // Display comparison table
            var headers = new[] { "Schema", "Total", "Search", "Filter", "Sort", "Facet", "Complex", "Collections" };
            var colWidths = new[] { 20, 8, 8, 8, 6, 7, 9, 13 };

            // Print header
            var headerRow = string.Join(" | ", headers.Zip(colWidths, (h, w) => h.PadRight(w)));
            Console.WriteLine(headerRow);
            Console.WriteLine("".PadRight(headerRow.Length, '-'));

            // Print data rows
            foreach (var data in comparisonData)
            {
                var row = new object[] 
                { 
                    data.Name.ToString().PadRight(19).Substring(0, 19),
                    data.TotalFields, 
                    data.Searchable, 
                    data.Filterable, 
                    data.Sortable, 
                    data.Facetable, 
                    data.Complex, 
                    data.Collections 
                };
                var dataRow = string.Join(" | ", row.Zip(colWidths, (val, w) => val.ToString().PadRight(w)));
                Console.WriteLine(dataRow);
            }
        }
    }

    /// <summary>
    /// Main program demonstrating advanced schema design
    /// </summary>
    public class Program
    {
        /// <summary>
        /// Main entry point
        /// </summary>
        public static async Task Main(string[] args)
        {
            Console.WriteLine("=".PadRight(60, '='));
            Console.WriteLine("Module 3: Advanced Schema Design Example (C#)");
            Console.WriteLine("=".PadRight(60, '='));

            // Initialize the schema designer
            AdvancedSchemaDesigner designer;
            try
            {
                designer = new AdvancedSchemaDesigner();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"❌ Configuration error: {ex.Message}");
                return;
            }

            // Create index client
            if (!await designer.CreateIndexClientAsync())
            {
                Console.WriteLine("❌ Failed to create index client. Exiting.");
                return;
            }

            // Design different schemas
            Console.WriteLine("\n🎨 Designing Multiple Schema Patterns...");

            var ecommerceSchema = designer.DesignEcommerceSchema();
            var blogSchema = designer.DesignOptimizedBlogSchema();

            // Compare schemas
            var schemas = new List<(string, IList<SearchField>)>
            {
                ("E-commerce", ecommerceSchema),
                ("Optimized Blog", blogSchema)
            };

            designer.CompareSchemas(schemas);

            // Create and test one schema (user choice)
            Console.WriteLine("\n🏗️  Schema Creation Options:");
            Console.WriteLine("1. E-commerce Product Schema");
            Console.WriteLine("2. Optimized Blog Schema");

            Console.Write("\nWhich schema would you like to create and test? (1-2, or 'skip'): ");
            var choice = Console.ReadLine();

            bool success = true;

            switch (choice)
            {
                case "1":
                    success = await designer.CreateAndTestSchemaAsync(
                        "advanced-ecommerce-schema-cs",
                        ecommerceSchema,
                        "E-commerce Product Schema"
                    );
                    break;
                case "2":
                    success = await designer.CreateAndTestSchemaAsync(
                        "advanced-blog-schema-cs",
                        blogSchema,
                        "Optimized Blog Schema"
                    );
                    break;
                default:
                    Console.WriteLine("Skipping schema creation.");
                    break;
            }

            if (success)
            {
                Console.WriteLine("\n🎉 Advanced schema design completed successfully!");
            }

            Console.WriteLine("\n" + "=".PadRight(60, '='));
            Console.WriteLine("Example completed!");
            Console.WriteLine("=".PadRight(60, '='));

            Console.WriteLine("\n📚 What you learned:");
            Console.WriteLine("✅ How to design complex field structures using SearchField");
            Console.WriteLine("✅ How to use complex fields for nested objects");
            Console.WriteLine("✅ How to optimize field attributes for performance");
            Console.WriteLine("✅ How to handle different data types effectively");
            Console.WriteLine("✅ How to implement schema design patterns");
            Console.WriteLine("✅ How to compare different schema approaches");

            Console.WriteLine("\n🚀 Next steps:");
            Console.WriteLine("1. Try creating your own schema for your use case");
            Console.WriteLine("2. Experiment with different field attribute combinations");
            Console.WriteLine("3. Run the next example: 03_DataIngestion.cs");
            Console.WriteLine("4. Test performance with different schema designs");

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}