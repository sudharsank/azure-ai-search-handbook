/*
Simple Text Search - Module 2 C# Examples
Basic text search operations in Azure AI Search using .NET SDK

This module demonstrates:
- Simple text queries
- Basic result handling
- Search client initialization
- Understanding search scores
*/

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module02.BasicSearch
{
    public class SimpleTextSearch
    {
        private readonly SearchClient _searchClient;

        public SimpleTextSearch(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Perform a basic text search
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> BasicSearchAsync(string query, int top = 10)
        {
            try
            {
                Console.WriteLine($"Performing basic search: '{query}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(query, searchOptions);
                
                Console.WriteLine($"Found {results.Value.TotalCount} total results");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in basic search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search with a specific result limit
        /// </summary>
        /// <param name="query">Search query string</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> SearchWithLimitAsync(string query, int top = 5)
        {
            return await BasicSearchAsync(query, top);
        }

        /// <summary>
        /// Get all documents in the index (useful for browsing)
        /// </summary>
        /// <param name="top">Maximum number of documents to return</param>
        /// <returns>All documents</returns>
        public async Task<SearchResults<SearchDocument>> GetAllDocumentsAsync(int top = 20)
        {
            try
            {
                Console.WriteLine("Retrieving all documents");

                var searchOptions = new SearchOptions
                {
                    Size = top
                };

                // Use "*" to match all documents
                var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                
                Console.WriteLine($"Retrieved documents from index");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error retrieving all documents: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Display search results in a readable format
        /// </summary>
        /// <param name="results">Search results to display</param>
        /// <param name="showScores">Whether to display search scores</param>
        public static void DisplayResults(SearchResults<SearchDocument> results, bool showScores = true)
        {
            if (results == null)
            {
                Console.WriteLine("No results found.");
                return;
            }

            var resultList = new List<SearchResult<SearchDocument>>();
            foreach (var result in results.GetResults())
            {
                resultList.Add(result);
            }

            if (resultList.Count == 0)
            {
                Console.WriteLine("No results found.");
                return;
            }

            Console.WriteLine(new string('=', 60));
            Console.WriteLine($"SEARCH RESULTS ({resultList.Count} found)");
            Console.WriteLine(new string('=', 60));

            for (int i = 0; i < resultList.Count; i++)
            {
                var result = resultList[i];
                var document = result.Document;

                var title = document.TryGetValue("title", out var titleValue) ? titleValue?.ToString() : "Untitled";
                Console.WriteLine($"\n{i + 1}. {title}");

                if (showScores)
                {
                    Console.WriteLine($"   Score: {result.Score:F3}");
                }

                if (document.TryGetValue("author", out var authorValue) && authorValue?.ToString() != "Unknown")
                {
                    Console.WriteLine($"   Author: {authorValue}");
                }

                if (document.TryGetValue("content", out var contentValue))
                {
                    var content = contentValue?.ToString() ?? "";
                    var preview = content.Length > 150 ? content.Substring(0, 150) + "..." : content;
                    if (!string.IsNullOrEmpty(preview))
                    {
                        Console.WriteLine($"   Preview: {preview}");
                    }
                }

                if (document.TryGetValue("url", out var urlValue) && !string.IsNullOrEmpty(urlValue?.ToString()))
                {
                    Console.WriteLine($"   URL: {urlValue}");
                }

                Console.WriteLine($"   {new string('-', 50)}");
            }
        }

        /// <summary>
        /// Analyze search scores to understand result quality
        /// </summary>
        /// <param name="results">Search results to analyze</param>
        /// <returns>Score statistics</returns>
        public static Dictionary<string, double> AnalyzeScores(SearchResults<SearchDocument> results)
        {
            var scores = new List<double>();
            
            foreach (var result in results.GetResults())
            {
                if (result.Score.HasValue)
                {
                    scores.Add(result.Score.Value);
                }
            }

            if (scores.Count == 0)
            {
                return new Dictionary<string, double>();
            }

            return new Dictionary<string, double>
            {
                ["TotalResults"] = scores.Count,
                ["MinScore"] = scores.Min(),
                ["MaxScore"] = scores.Max(),
                ["AvgScore"] = scores.Average(),
                ["ScoreRange"] = scores.Max() - scores.Min()
            };
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class Program
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

                await DemonstrateSimpleSearchAsync(searchClient);
                await InteractiveSearchExampleAsync(searchClient);

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Try modifying the queries above");
                Console.WriteLine("   - Experiment with different search terms");
                Console.WriteLine("   - Check out 02_PhraseSearch.cs for exact phrase matching");
                Console.WriteLine("   - Learn about boolean searches in 03_BooleanSearch.cs");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateSimpleSearchAsync(SearchClient searchClient)
        {
            Console.WriteLine("🔍 Simple Text Search Demonstration");
            Console.WriteLine(new string('=', 50));

            var searchOps = new SimpleTextSearch(searchClient);

            // Example 1: Basic search
            Console.WriteLine("\n1️⃣ Basic Text Search");
            Console.WriteLine(new string('-', 30));

            var query = "python programming";
            var results = await searchOps.BasicSearchAsync(query, 5);
            SimpleTextSearch.DisplayResults(results);

            // Analyze the results
            var stats = SimpleTextSearch.AnalyzeScores(results);
            if (stats.Count > 0)
            {
                Console.WriteLine($"\n📊 Score Analysis:");
                Console.WriteLine($"   Total results: {stats["TotalResults"]}");
                Console.WriteLine($"   Score range: {stats["MinScore"]:F3} - {stats["MaxScore"]:F3}");
                Console.WriteLine($"   Average score: {stats["AvgScore"]:F3}");
            }

            // Example 2: Different query
            Console.WriteLine($"\n{new string('=', 60)}");
            Console.WriteLine("\n2️⃣ Another Search Example");
            Console.WriteLine(new string('-', 30));

            var query2 = "machine learning";
            var results2 = await searchOps.BasicSearchAsync(query2, 3);
            SimpleTextSearch.DisplayResults(results2);

            // Example 3: Browse all documents
            Console.WriteLine($"\n{new string('=', 60)}");
            Console.WriteLine("\n3️⃣ Browse All Documents");
            Console.WriteLine(new string('-', 30));

            var allDocs = await searchOps.GetAllDocumentsAsync(5);
            Console.WriteLine($"Total documents available in index");

            var docList = new List<SearchResult<SearchDocument>>();
            foreach (var doc in allDocs.GetResults())
            {
                docList.Add(doc);
                if (docList.Count >= 3) break; // Show first 3
            }

            if (docList.Count > 0)
            {
                Console.WriteLine("\nFirst few documents:");
                for (int i = 0; i < docList.Count; i++)
                {
                    var doc = docList[i].Document;
                    var title = doc.TryGetValue("title", out var titleValue) ? titleValue?.ToString() : "Untitled";
                    var author = doc.TryGetValue("author", out var authorValue) ? authorValue?.ToString() : "Unknown";
                    Console.WriteLine($"  {i + 1}. {title} by {author}");
                }
            }

            Console.WriteLine("\n✅ Simple text search demonstration completed!");
        }

        private static async Task InteractiveSearchExampleAsync(SearchClient searchClient)
        {
            Console.WriteLine("\n🎮 Interactive Search Example");
            Console.WriteLine(new string('=', 50));

            var searchOps = new SimpleTextSearch(searchClient);

            // Sample queries for demonstration
            var sampleQueries = new[]
            {
                "web development",
                "tutorial",
                "javascript",
                "data science",
                "artificial intelligence"
            };

            Console.WriteLine("Here are some sample queries you can try:");
            for (int i = 0; i < sampleQueries.Length; i++)
            {
                Console.WriteLine($"  {i + 1}. {sampleQueries[i]}");
            }

            // For demonstration, let's try the first query
            var demoQuery = sampleQueries[0];
            Console.WriteLine($"\n🔍 Trying query: '{demoQuery}'");
            Console.WriteLine(new string('-', 40));

            var results = await searchOps.BasicSearchAsync(demoQuery, 3);
            SimpleTextSearch.DisplayResults(results, showScores: true);

            var stats = SimpleTextSearch.AnalyzeScores(results);
            if (stats.Count > 0)
            {
                Console.WriteLine($"\n💡 Tips for interpreting results:");
                Console.WriteLine($"   - Higher scores (closer to {stats["MaxScore"]:F1}) indicate better matches");
                Console.WriteLine($"   - Scores below 1.0 might indicate weaker relevance");
                Console.WriteLine($"   - Try different keywords if results aren't relevant");
            }
        }
    }
}