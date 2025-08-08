/*
Boolean Search - Module 2 C# Examples
Boolean operators (AND, OR, NOT) in Azure AI Search using .NET SDK

This module demonstrates:
- AND operator for required terms
- OR operator for alternative terms
- NOT operator for exclusions
- Combining boolean operators
- Boolean search best practices
*/

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module02.BasicSearch
{
    public class BooleanSearch
    {
        private readonly SearchClient _searchClient;

        public BooleanSearch(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Search for documents containing both terms (AND operator)
        /// </summary>
        /// <param name="term1">First required term</param>
        /// <param name="term2">Second required term</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> AndSearchAsync(string term1, string term2, int top = 10)
        {
            try
            {
                var query = $"{term1} AND {term2}";
                Console.WriteLine($"Performing AND search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results with both terms");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in AND search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for documents containing either term (OR operator)
        /// </summary>
        /// <param name="term1">First alternative term</param>
        /// <param name="term2">Second alternative term</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> OrSearchAsync(string term1, string term2, int top = 10)
        {
            try
            {
                var query = $"{term1} OR {term2}";
                Console.WriteLine($"Performing OR search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results with either term");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in OR search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for documents containing one term but not another (NOT operator)
        /// </summary>
        /// <param name="includeTerm">Term that must be present</param>
        /// <param name="excludeTerm">Term that must not be present</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> NotSearchAsync(string includeTerm, string excludeTerm, int top = 10)
        {
            try
            {
                var query = $"{includeTerm} NOT {excludeTerm}";
                Console.WriteLine($"Performing NOT search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results excluding '{excludeTerm}'");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in NOT search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Perform complex boolean search with multiple operators
        /// </summary>
        /// <param name="query">Complex boolean query string</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> ComplexBooleanSearchAsync(string query, int top = 10)
        {
            try
            {
                Console.WriteLine($"Performing complex boolean search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found results for complex query");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in complex boolean search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Compare results from different boolean operators
        /// </summary>
        /// <param name="term1">First term</param>
        /// <param name="term2">Second term</param>
        /// <param name="top">Maximum results per operator</param>
        /// <returns>Dictionary mapping operators to their results</returns>
        public async Task<Dictionary<string, SearchResults<SearchDocument>>> CompareBooleanOperatorsAsync(
            string term1, string term2, int top = 5)
        {
            var results = new Dictionary<string, SearchResults<SearchDocument>>();

            // AND search
            results["AND"] = await AndSearchAsync(term1, term2, top);

            // OR search
            results["OR"] = await OrSearchAsync(term1, term2, top);

            // NOT search (term1 but not term2)
            results["NOT"] = await NotSearchAsync(term1, term2, top);

            return results;
        }

        /// <summary>
        /// Display comparison of boolean operators
        /// </summary>
        /// <param name="term1">First term</param>
        /// <param name="term2">Second term</param>
        /// <param name="results">Results from different boolean operators</param>
        public static void DisplayBooleanComparison(string term1, string term2, 
            Dictionary<string, SearchResults<SearchDocument>> results)
        {
            Console.WriteLine($"\n🔗 Boolean Operators Comparison: '{term1}' and '{term2}'");
            Console.WriteLine(new string('=', 70));

            foreach (var kvp in results)
            {
                var operatorName = kvp.Key;
                var operatorResults = kvp.Value.GetResults().ToList();

                Console.WriteLine($"\n{operatorName} Operation:");

                switch (operatorName)
                {
                    case "AND":
                        Console.WriteLine($"   Query: {term1} AND {term2}");
                        Console.WriteLine($"   Meaning: Documents must contain BOTH terms");
                        break;
                    case "OR":
                        Console.WriteLine($"   Query: {term1} OR {term2}");
                        Console.WriteLine($"   Meaning: Documents can contain EITHER term");
                        break;
                    case "NOT":
                        Console.WriteLine($"   Query: {term1} NOT {term2}");
                        Console.WriteLine($"   Meaning: Documents must contain '{term1}' but NOT '{term2}'");
                        break;
                }

                Console.WriteLine($"   Results found: {operatorResults.Count}");

                if (operatorResults.Any())
                {
                    Console.WriteLine("   Top matches:");
                    for (int i = 0; i < Math.Min(3, operatorResults.Count); i++)
                    {
                        var result = operatorResults[i];
                        var title = result.Document.TryGetValue("title", out var titleValue) ? 
                            titleValue?.ToString() : "No title";
                        var score = result.Score ?? 0.0;
                        Console.WriteLine($"     {i + 1}. {title} (Score: {score:F3})");
                    }
                }
                else
                {
                    Console.WriteLine("   No matches found");
                }

                Console.WriteLine(new string('-', 50));
            }

            // Analysis
            Console.WriteLine($"\n📊 ANALYSIS:");
            var andCount = results.ContainsKey("AND") ? results["AND"].GetResults().Count() : 0;
            var orCount = results.ContainsKey("OR") ? results["OR"].GetResults().Count() : 0;
            var notCount = results.ContainsKey("NOT") ? results["NOT"].GetResults().Count() : 0;

            Console.WriteLine($"   AND results: {andCount} (most specific)");
            Console.WriteLine($"   OR results: {orCount} (broadest)");
            Console.WriteLine($"   NOT results: {notCount} (filtered)");

            if (orCount >= andCount && andCount >= notCount)
            {
                Console.WriteLine("   ✅ Expected pattern: OR ≥ AND ≥ NOT");
            }
            else
            {
                Console.WriteLine("   ⚠️ Unexpected pattern - check your data or terms");
            }
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class BooleanSearchProgram
    {
        // Replace with your actual service details
        private const string ServiceEndpoint = "https://your-service.search.windows.net";
        private const string ApiKey = "your-api-key";
        private const string IndexName = "your-index-name";

        public static async Task Main(string[] args)
        {
            try
            {
                // Initialize search client
                var searchClient = new SearchClient(
                    new Uri(ServiceEndpoint),
                    IndexName,
                    new AzureKeyCredential(ApiKey)
                );

                await DemonstrateBooleanSearchAsync(searchClient);
                await BooleanSearchBestPracticesAsync(searchClient);

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Practice building your own boolean queries");
                Console.WriteLine("   - Try combining different operators");
                Console.WriteLine("   - Check out 04_WildcardSearch.cs for pattern matching");
                Console.WriteLine("   - Learn about field-specific searches in 05_FieldSearch.cs");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateBooleanSearchAsync(SearchClient searchClient)
        {
            Console.WriteLine("🔗 Boolean Search Demonstration");
            Console.WriteLine(new string('=', 50));

            var searchOps = new BooleanSearch(searchClient);

            // Example 1: Compare boolean operators
            Console.WriteLine("\n1️⃣ Boolean Operators Comparison");

            var term1 = "python";
            var term2 = "tutorial";
            var booleanResults = await searchOps.CompareBooleanOperatorsAsync(term1, term2, 5);
            BooleanSearch.DisplayBooleanComparison(term1, term2, booleanResults);

            // Example 2: Complex boolean queries
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n2️⃣ Complex Boolean Queries");
            Console.WriteLine(new string('-', 30));

            var complexQueries = new[]
            {
                "python AND (tutorial OR guide)",
                "(web OR mobile) AND development",
                "programming NOT (beginner OR basic)",
                "machine AND learning AND (python OR r)"
            };

            foreach (var query in complexQueries)
            {
                Console.WriteLine($"\nQuery: {query}");
                var results = await searchOps.ComplexBooleanSearchAsync(query, 3);
                var resultList = results.GetResults().ToList();
                Console.WriteLine($"Results: {resultList.Count}");

                if (resultList.Any())
                {
                    var topResult = resultList.First();
                    var title = topResult.Document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() : "No title";
                    var score = topResult.Score ?? 0.0;
                    Console.WriteLine($"Top match: {title} (Score: {score:F3})");
                }
            }

            // Example 3: Practical use cases
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n3️⃣ Practical Use Cases");
            Console.WriteLine(new string('-', 30));

            var useCases = new[]
            {
                new { Scenario = "Find beginner Python tutorials", Query = "python AND tutorial AND beginner", Explanation = "All three terms must be present" },
                new { Scenario = "Find content about web or mobile development", Query = "development AND (web OR mobile)", Explanation = "Must have 'development' plus either 'web' or 'mobile'" },
                new { Scenario = "Find programming content but exclude advanced topics", Query = "programming NOT (advanced OR expert)", Explanation = "Must have 'programming' but exclude advanced content" }
            };

            foreach (var useCase in useCases)
            {
                Console.WriteLine($"\n📋 Scenario: {useCase.Scenario}");
                Console.WriteLine($"   Query: {useCase.Query}");
                Console.WriteLine($"   Logic: {useCase.Explanation}");

                var results = await searchOps.ComplexBooleanSearchAsync(useCase.Query, 2);
                var resultCount = results.GetResults().Count();
                Console.WriteLine($"   Results: {resultCount} found");
            }

            Console.WriteLine("\n✅ Boolean search demonstration completed!");
        }

        private static async Task BooleanSearchBestPracticesAsync(SearchClient searchClient)
        {
            Console.WriteLine("\n📚 Boolean Search Best Practices");
            Console.WriteLine(new string('=', 50));

            Console.WriteLine("\n💡 When to Use Each Operator:");
            Console.WriteLine("\n✅ AND Operator:");
            Console.WriteLine("   - When you need ALL terms to be present");
            Console.WriteLine("   - For specific, focused searches");
            Console.WriteLine("   - To narrow down broad topics");
            Console.WriteLine("   - Example: 'machine AND learning AND python'");

            Console.WriteLine("\n✅ OR Operator:");
            Console.WriteLine("   - When you want ANY of the terms");
            Console.WriteLine("   - For broader, more inclusive searches");
            Console.WriteLine("   - When searching for synonyms or alternatives");
            Console.WriteLine("   - Example: 'javascript OR typescript OR js'");

            Console.WriteLine("\n✅ NOT Operator:");
            Console.WriteLine("   - To exclude unwanted content");
            Console.WriteLine("   - To filter out irrelevant results");
            Console.WriteLine("   - When you know what you don't want");
            Console.WriteLine("   - Example: 'programming NOT (game OR gaming)'");

            Console.WriteLine("\n⚠️ Common Mistakes to Avoid:");
            Console.WriteLine("   ❌ Using AND when you mean OR");
            Console.WriteLine("   ❌ Overusing NOT (can exclude relevant content)");
            Console.WriteLine("   ❌ Forgetting parentheses in complex queries");
            Console.WriteLine("   ❌ Making queries too restrictive with multiple ANDs");

            Console.WriteLine("\n🔧 Query Building Tips:");
            Console.WriteLine("   ✅ Start simple, then add complexity");
            Console.WriteLine("   ✅ Use parentheses to group terms: (term1 OR term2) AND term3");
            Console.WriteLine("   ✅ Test each part of complex queries separately");
            Console.WriteLine("   ✅ Consider search mode ('any' vs 'all') as alternative to boolean");

            // Demonstrate query building
            Console.WriteLine("\n🏗️ Query Building Example:");
            var searchOps = new BooleanSearch(searchClient);

            var baseTerm = "tutorial";
            Console.WriteLine($"\n1. Start with base term: '{baseTerm}'");
            var baseResults = await searchOps.ComplexBooleanSearchAsync(baseTerm, 1);
            var baseCount = baseResults.GetResults().Count();
            Console.WriteLine($"   Results: {baseCount}");

            var refinedQuery = "tutorial AND python";
            Console.WriteLine($"\n2. Add specificity: '{refinedQuery}'");
            var refinedResults = await searchOps.ComplexBooleanSearchAsync(refinedQuery, 1);
            var refinedCount = refinedResults.GetResults().Count();
            Console.WriteLine($"   Results: {refinedCount} (more specific)");

            var finalQuery = "tutorial AND python AND (beginner OR introduction)";
            Console.WriteLine($"\n3. Add alternatives: '{finalQuery}'");
            var finalResults = await searchOps.ComplexBooleanSearchAsync(finalQuery, 1);
            var finalCount = finalResults.GetResults().Count();
            Console.WriteLine($"   Results: {finalCount} (balanced specificity)");
        }
    }
}