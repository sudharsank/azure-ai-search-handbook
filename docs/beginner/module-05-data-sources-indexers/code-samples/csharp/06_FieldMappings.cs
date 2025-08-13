using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

namespace AzureSearchSamples.DataSourcesIndexers
{
    /// <summary>
    /// Advanced Field Mappings Example
    /// 
    /// This example demonstrates advanced field mapping techniques for Azure AI Search indexers,
    /// including complex transformations, built-in functions, and output field mappings.
    /// </summary>
    public class FieldMappingsExample
    {
        private readonly SearchIndexClient _indexClient;
        private readonly SearchIndexerClient _indexerClient;
        private readonly string _searchEndpoint;
        private readonly string _apiKey;

        public FieldMappingsExample(string searchEndpoint, string apiKey)
        {
            _searchEndpoint = searchEndpoint ?? throw new ArgumentNullException(nameof(searchEndpoint));
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));

            var credential = new AzureKeyCredential(_apiKey);
            _indexClient = new SearchIndexClient(new Uri(_searchEndpoint), credential);
            _indexerClient = new SearchIndexerClient(new Uri(_searchEndpoint), credential);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Advanced Field Mappings Example");
            Console.WriteLine("=" + new string('=', 49));

            try
            {
                // Demonstrate concepts
                DemonstrateBasicFieldMappings();

                // Create mapping examples
                var (basicMappings, functionMappings) = CreateFieldMappingExamples();

                // Show built-in functions
                DemonstrateBuiltInFunctions();

                // Complex scenarios
                var scenarios = CreateComplexFieldMappingScenarios();

                // Output field mappings
                DemonstrateOutputFieldMappings();

                // Create demo index
                var demoIndex = await CreateIndexForFieldMappingDemoAsync();

                // Best practices
                DemonstrateFieldMappingBestPractices();

                // Common patterns
                DemonstrateCommonMappingPatterns();

                Console.WriteLine("\n✅ Advanced field mappings example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Field mappings bridge the gap between source data and target schema");
                Console.WriteLine("- Built-in functions provide powerful data transformation capabilities");
                Console.WriteLine("- Complex scenarios often require multiple mapping strategies");
                Console.WriteLine("- Output field mappings are essential for AI enrichment pipelines");
                Console.WriteLine("- Test mappings thoroughly with representative data samples");
                Console.WriteLine("- Consider performance implications of complex transformations");

                if (demoIndex != null)
                {
                    Console.WriteLine($"\n🧹 Cleanup: Delete demo index with:");
                    Console.WriteLine($"   await _indexClient.DeleteIndexAsync(\"{demoIndex.Name}\");");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }

        private void DemonstrateBasicFieldMappings()
        {
            Console.WriteLine("\n📋 Basic Field Mapping Concepts");
            Console.WriteLine("=" + new string('=', 29));

            Console.WriteLine("Field mappings connect source data fields to target index fields.");
            Console.WriteLine("They are essential when:");
            Console.WriteLine("• Source field names differ from target field names");
            Console.WriteLine("• Data transformation is needed");
            Console.WriteLine("• Complex data structures need flattening");
            Console.WriteLine("• Multiple source fields map to one target field");

            // Basic mapping examples
            var basicMappings = new[]
            {
                new { Source = "customer_name", Target = "customerName", Purpose = "Field name transformation (snake_case to camelCase)" },
                new { Source = "created_date", Target = "createdDate", Purpose = "Date field mapping with potential format conversion" },
                new { Source = "product_description", Target = "description", Purpose = "Field name simplification" }
            };

            Console.WriteLine($"\n📝 Basic Mapping Examples:");
            foreach (var mapping in basicMappings)
            {
                Console.WriteLine($"   {mapping.Source} → {mapping.Target}");
                Console.WriteLine($"      Purpose: {mapping.Purpose}");
            }
        }

        private (List<FieldMapping> Basic, List<FieldMapping> Function) CreateFieldMappingExamples()
        {
            Console.WriteLine("\n🛠️ Field Mapping Examples");
            Console.WriteLine("=" + new string('=', 24));

            // Example 1: Basic field mappings
            Console.WriteLine("\n1️⃣ Basic Field Mappings:");
            var basicMappings = new List<FieldMapping>
            {
                new FieldMapping("ProductID") { TargetFieldName = "id" },
                new FieldMapping("ProductName") { TargetFieldName = "name" },
                new FieldMapping("ProductDescription") { TargetFieldName = "description" },
                new FieldMapping("CategoryName") { TargetFieldName = "category" },
                new FieldMapping("UnitPrice") { TargetFieldName = "price" }
            };

            foreach (var mapping in basicMappings)
            {
                Console.WriteLine($"   {mapping.SourceFieldName} → {mapping.TargetFieldName}");
            }

            // Example 2: Mappings with built-in functions
            Console.WriteLine("\n2️⃣ Mappings with Built-in Functions:");
            var functionMappings = new List<FieldMapping>
            {
                new FieldMapping("Tags")
                {
                    TargetFieldName = "tags",
                    MappingFunction = new FieldMappingFunction("splitAndTrim")
                    {
                        Parameters = new Dictionary<string, object>
                        {
                            ["delimiter"] = ",",
                            ["trimWhitespace"] = true
                        }
                    }
                },
                new FieldMapping("FullName")
                {
                    TargetFieldName = "searchableText",
                    MappingFunction = new FieldMappingFunction("extractTokenAtPosition")
                    {
                        Parameters = new Dictionary<string, object>
                        {
                            ["delimiter"] = " ",
                            ["position"] = 0
                        }
                    }
                },
                new FieldMapping("JsonData")
                {
                    TargetFieldName = "extractedValue",
                    MappingFunction = new FieldMappingFunction("jsonArrayToStringCollection")
                }
            };

            foreach (var mapping in functionMappings)
            {
                var funcName = mapping.MappingFunction?.Name ?? "None";
                Console.WriteLine($"   {mapping.SourceFieldName} → {mapping.TargetFieldName} (function: {funcName})");
            }

            return (basicMappings, functionMappings);
        }

        private void DemonstrateBuiltInFunctions()
        {
            Console.WriteLine("\n🔧 Built-in Mapping Functions");
            Console.WriteLine("=" + new string('=', 29));

            var functions = new[]
            {
                new
                {
                    Name = "base64Encode",
                    Description = "Encodes the input string using Base64",
                    Parameters = (Dictionary<string, string>)null,
                    Example = "Convert binary data to Base64 string"
                },
                new
                {
                    Name = "base64Decode",
                    Description = "Decodes a Base64 encoded string",
                    Parameters = (Dictionary<string, string>)null,
                    Example = "Decode Base64 string to original value"
                },
                new
                {
                    Name = "extractTokenAtPosition",
                    Description = "Extracts a token at specified position after splitting",
                    Parameters = new Dictionary<string, string> { ["delimiter"] = "string", ["position"] = "int" },
                    Example = "Extract first name from \"John Doe\" using space delimiter"
                },
                new
                {
                    Name = "jsonArrayToStringCollection",
                    Description = "Converts JSON array to string collection",
                    Parameters = (Dictionary<string, string>)null,
                    Example = "Convert [\"tag1\", \"tag2\"] to searchable collection"
                },
                new
                {
                    Name = "splitAndTrim",
                    Description = "Splits string and trims whitespace from each part",
                    Parameters = new Dictionary<string, string> { ["delimiter"] = "string", ["trimWhitespace"] = "bool" },
                    Example = "Convert \"tag1, tag2, tag3\" to clean array"
                },
                new
                {
                    Name = "urlEncode",
                    Description = "URL encodes the input string",
                    Parameters = (Dictionary<string, string>)null,
                    Example = "Encode URLs for safe storage"
                },
                new
                {
                    Name = "urlDecode",
                    Description = "URL decodes the input string",
                    Parameters = (Dictionary<string, string>)null,
                    Example = "Decode URL-encoded strings"
                }
            };

            foreach (var func in functions)
            {
                Console.WriteLine($"\n🔧 {func.Name}");
                Console.WriteLine($"   Description: {func.Description}");
                if (func.Parameters != null)
                {
                    Console.WriteLine($"   Parameters: {string.Join(", ", func.Parameters.Select(p => $"{p.Key}: {p.Value}"))}");
                }
                Console.WriteLine($"   Example: {func.Example}");
            }
        }

        private List<(string Name, List<FieldMapping> Mappings)> CreateComplexFieldMappingScenarios()
        {
            Console.WriteLine("\n🎯 Complex Field Mapping Scenarios");
            Console.WriteLine("=" + new string('=', 34));

            var scenarios = new List<(string Name, List<FieldMapping> Mappings)>();

            // Scenario 1: E-commerce Product Data
            Console.WriteLine("\n📦 Scenario 1: E-commerce Product Data");
            var ecommerceMappings = new List<FieldMapping>
            {
                new FieldMapping("ProductID") { TargetFieldName = "id" },
                new FieldMapping("ProductName") { TargetFieldName = "name" },
                new FieldMapping("Categories")
                {
                    TargetFieldName = "categories",
                    MappingFunction = new FieldMappingFunction("splitAndTrim")
                    {
                        Parameters = new Dictionary<string, object>
                        {
                            ["delimiter"] = ",",
                            ["trimWhitespace"] = true
                        }
                    }
                },
                new FieldMapping("ProductName")
                {
                    TargetFieldName = "brand",
                    MappingFunction = new FieldMappingFunction("extractTokenAtPosition")
                    {
                        Parameters = new Dictionary<string, object>
                        {
                            ["delimiter"] = " ",
                            ["position"] = 0
                        }
                    }
                },
                new FieldMapping("SpecificationsJson")
                {
                    TargetFieldName = "specifications",
                    MappingFunction = new FieldMappingFunction("jsonArrayToStringCollection")
                }
            };

            scenarios.Add(("E-commerce", ecommerceMappings));

            foreach (var mapping in ecommerceMappings)
            {
                var funcInfo = mapping.MappingFunction != null ? $" (function: {mapping.MappingFunction.Name})" : "";
                Console.WriteLine($"   {mapping.SourceFieldName} → {mapping.TargetFieldName}{funcInfo}");
            }

            // Scenario 2: Document Management
            Console.WriteLine("\n📄 Scenario 2: Document Management");
            var documentMappings = new List<FieldMapping>
            {
                new FieldMapping("DocumentPath") { TargetFieldName = "id" },
                new FieldMapping("Title") { TargetFieldName = "title" },
                new FieldMapping("DocumentPath")
                {
                    TargetFieldName = "fileExtension",
                    MappingFunction = new FieldMappingFunction("extractTokenAtPosition")
                    {
                        Parameters = new Dictionary<string, object>
                        {
                            ["delimiter"] = ".",
                            ["position"] = -1
                        }
                    }
                },
                new FieldMapping("Authors")
                {
                    TargetFieldName = "authorList",
                    MappingFunction = new FieldMappingFunction("splitAndTrim")
                    {
                        Parameters = new Dictionary<string, object>
                        {
                            ["delimiter"] = ";",
                            ["trimWhitespace"] = true
                        }
                    }
                },
                new FieldMapping("DocumentPath")
                {
                    TargetFieldName = "encodedPath",
                    MappingFunction = new FieldMappingFunction("urlEncode")
                }
            };

            scenarios.Add(("Document Management", documentMappings));

            foreach (var mapping in documentMappings)
            {
                var funcInfo = mapping.MappingFunction != null ? $" (function: {mapping.MappingFunction.Name})" : "";
                Console.WriteLine($"   {mapping.SourceFieldName} → {mapping.TargetFieldName}{funcInfo}");
            }

            return scenarios;
        }

        private void DemonstrateOutputFieldMappings()
        {
            Console.WriteLine("\n🎨 Output Field Mappings (for Skillsets)");
            Console.WriteLine("=" + new string('=', 39));

            Console.WriteLine("Output field mappings are used with cognitive skills to map");
            Console.WriteLine("skill outputs to index fields. They're essential for:");
            Console.WriteLine("• AI enrichment pipelines");
            Console.WriteLine("• Custom skill outputs");
            Console.WriteLine("• Complex data transformations");

            // Example output field mappings
            var outputMappings = new[]
            {
                new { Source = "/document/content/keyphrases/*", Target = "keyphrases", Description = "Map extracted key phrases to collection field" },
                new { Source = "/document/content/entities/*/name", Target = "entityNames", Description = "Extract entity names from entity recognition" },
                new { Source = "/document/content/sentiment/score", Target = "sentimentScore", Description = "Map sentiment analysis score" },
                new { Source = "/document/content/language", Target = "detectedLanguage", Description = "Map detected language from language detection skill" }
            };

            Console.WriteLine($"\n📝 Output Field Mapping Examples:");
            foreach (var mapping in outputMappings)
            {
                Console.WriteLine($"   {mapping.Source} → {mapping.Target}");
                Console.WriteLine($"      Purpose: {mapping.Description}");
            }
        }

        private async Task<SearchIndex> CreateIndexForFieldMappingDemoAsync()
        {
            Console.WriteLine("\n📊 Creating Demo Index for Field Mappings");
            Console.WriteLine("=" + new string('=', 39));

            var indexName = "field-mapping-demo-index";

            // Define fields that will receive mapped data
            var fields = new List<SearchField>
            {
                new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
                new SearchableField("name") { IsSortable = true },
                new SearchableField("description") { AnalyzerName = LexicalAnalyzerName.EnLucene },
                new SimpleField("category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SimpleField("price", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true },

                // Fields for function mapping results
                new SearchableField("tags", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFacetable = true },
                new SearchableField("brand", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SearchableField("specifications", SearchFieldDataType.Collection(SearchFieldDataType.String)),

                // Document-specific fields
                new SearchableField("title"),
                new SimpleField("fileExtension", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
                new SearchableField("authorList", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFacetable = true },
                new SimpleField("encodedPath", SearchFieldDataType.String),

                // AI enrichment fields
                new SearchableField("keyphrases", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFacetable = true },
                new SearchableField("entityNames", SearchFieldDataType.Collection(SearchFieldDataType.String)) { IsFacetable = true },
                new SimpleField("sentimentScore", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true },
                new SimpleField("detectedLanguage", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true }
            };

            var index = new SearchIndex(indexName, fields);

            try
            {
                var result = await _indexClient.CreateOrUpdateIndexAsync(index);
                Console.WriteLine($"✅ Demo index '{indexName}' created successfully");
                Console.WriteLine($"   Total Fields: {result.Value.Fields.Count}");

                // Show field categories
                var basicFields = result.Value.Fields.Where(f => new[] { "id", "name", "description", "category", "price" }.Contains(f.Name)).Select(f => f.Name);
                var functionFields = result.Value.Fields.Where(f => new[] { "tags", "brand", "specifications" }.Contains(f.Name)).Select(f => f.Name);
                var documentFields = result.Value.Fields.Where(f => new[] { "title", "fileExtension", "authorList", "encodedPath" }.Contains(f.Name)).Select(f => f.Name);
                var aiFields = result.Value.Fields.Where(f => new[] { "keyphrases", "entityNames", "sentimentScore", "detectedLanguage" }.Contains(f.Name)).Select(f => f.Name);

                Console.WriteLine($"   Basic Fields: {string.Join(", ", basicFields)}");
                Console.WriteLine($"   Function Mapping Fields: {string.Join(", ", functionFields)}");
                Console.WriteLine($"   Document Fields: {string.Join(", ", documentFields)}");
                Console.WriteLine($"   AI Enrichment Fields: {string.Join(", ", aiFields)}");

                return result.Value;
            }
            catch (RequestFailedException ex)
            {
                Console.WriteLine($"❌ Error creating demo index: {ex.Message}");
                return null;
            }
        }

        private void DemonstrateFieldMappingBestPractices()
        {
            Console.WriteLine("\n💡 Field Mapping Best Practices");
            Console.WriteLine("=" + new string('=', 29));

            var practices = new[]
            {
                new
                {
                    Category = "Performance",
                    Practices = new[]
                    {
                        "Use field mappings only when necessary",
                        "Avoid complex transformations in high-volume scenarios",
                        "Consider pre-processing data at the source when possible",
                        "Test mapping functions with sample data first"
                    }
                },
                new
                {
                    Category = "Data Quality",
                    Practices = new[]
                    {
                        "Validate mapping function parameters",
                        "Handle null and empty values appropriately",
                        "Test with edge cases and special characters",
                        "Monitor for mapping errors in indexer execution"
                    }
                },
                new
                {
                    Category = "Maintainability",
                    Practices = new[]
                    {
                        "Document complex mapping logic",
                        "Use descriptive target field names",
                        "Group related mappings logically",
                        "Version control mapping configurations"
                    }
                },
                new
                {
                    Category = "Troubleshooting",
                    Practices = new[]
                    {
                        "Test mappings with small data samples first",
                        "Use indexer execution history to debug issues",
                        "Validate source data format matches expectations",
                        "Check for data type compatibility issues"
                    }
                }
            };

            foreach (var category in practices)
            {
                Console.WriteLine($"\n🎯 {category.Category}");
                foreach (var practice in category.Practices)
                    Console.WriteLine($"   • {practice}");
            }
        }

        private void DemonstrateCommonMappingPatterns()
        {
            Console.WriteLine("\n🎨 Common Field Mapping Patterns");
            Console.WriteLine("=" + new string('=', 29));

            var patterns = new[]
            {
                new
                {
                    Pattern = "Name Transformation",
                    Description = "Convert between naming conventions",
                    Example = "customer_name → customerName",
                    Code = "new FieldMapping(\"customer_name\") { TargetFieldName = \"customerName\" }"
                },
                new
                {
                    Pattern = "String Splitting",
                    Description = "Split delimited strings into collections",
                    Example = "\"tag1,tag2,tag3\" → [\"tag1\", \"tag2\", \"tag3\"]",
                    Code = @"new FieldMapping(""tags_string"") {
    TargetFieldName = ""tags"",
    MappingFunction = new FieldMappingFunction(""splitAndTrim"") {
        Parameters = new Dictionary<string, object> {
            [""delimiter""] = "","",
            [""trimWhitespace""] = true
        }
    }
}"
                },
                new
                {
                    Pattern = "Token Extraction",
                    Description = "Extract specific parts from structured strings",
                    Example = "\"John Doe\" → \"John\" (first name)",
                    Code = @"new FieldMapping(""full_name"") {
    TargetFieldName = ""first_name"",
    MappingFunction = new FieldMappingFunction(""extractTokenAtPosition"") {
        Parameters = new Dictionary<string, object> {
            [""delimiter""] = "" "",
            [""position""] = 0
        }
    }
}"
                }
            };

            foreach (var pattern in patterns)
            {
                Console.WriteLine($"\n🎯 {pattern.Pattern}");
                Console.WriteLine($"   Description: {pattern.Description}");
                Console.WriteLine($"   Example: {pattern.Example}");
                Console.WriteLine($"   Code:");
                foreach (var line in pattern.Code.Split('\n'))
                    Console.WriteLine($"     {line}");
            }
        }
    }

    public class Program
    {
        public static async Task Main(string[] args)
        {
            var searchEndpoint = Environment.GetEnvironmentVariable("SEARCH_ENDPOINT") ?? "https://your-search-service.search.windows.net";
            var apiKey = Environment.GetEnvironmentVariable("SEARCH_API_KEY") ?? "your-admin-api-key";

            var example = new FieldMappingsExample(searchEndpoint, apiKey);

            try
            {
                await example.RunAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Application failed: {ex.Message}");
                Environment.Exit(1);
            }

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}