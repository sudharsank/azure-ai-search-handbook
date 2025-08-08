/*
Result Processing - Module 2 C# Examples
Processing and formatting search results from Azure AI Search

This module demonstrates:
- Basic result processing
- Result formatting for display
- Score analysis
- Result filtering and sorting
- Export capabilities
*/

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;

namespace AzureSearchHandbook.Module02.BasicSearch
{
    /// <summary>
    /// Simple structure for processed search results
    /// </summary>
    public class ProcessedResult
    {
        public string Title { get; set; } = string.Empty;
        public double Score { get; set; }
        public string Author { get; set; } = string.Empty;
        public string ContentPreview { get; set; } = string.Empty;
        public string Url { get; set; } = string.Empty;

        public Dictionary<string, object> ToDictionary()
        {
            return new Dictionary<string, object>
            {
                ["title"] = Title,
                ["score"] = Score,
                ["author"] = Author,
                ["contentPreview"] = ContentPreview,
                ["url"] = Url
            };
        }
    }

    /// <summary>
    /// Class for processing search results
    /// </summary>
    public class ResultProcessor
    {
        private readonly int _maxContentLength;

        public ResultProcessor(int maxContentLength = 150)
        {
            _maxContentLength = maxContentLength;
        }

        /// <summary>
        /// Convert raw search results to ProcessedResult objects
        /// </summary>
        /// <param name="rawResults">Raw search results</param>
        /// <returns>List of ProcessedResult objects</returns>
        public List<ProcessedResult> ProcessRawResults(SearchResults<SearchDocument> rawResults)
        {
            var processedResults = new List<ProcessedResult>();

            foreach (var result in rawResults.GetResults())
            {
                try
                {
                    var document = result.Document;

                    // Extract and clean fields
                    var title = document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() ?? "Untitled" : "Untitled";
                    
                    var score = result.Score ?? 0.0;
                    
                    var author = document.TryGetValue("author", out var authorValue) ? 
                        authorValue?.ToString() ?? "Unknown" : "Unknown";
                    
                    var url = document.TryGetValue("url", out var urlValue) ? 
                        urlValue?.ToString() ?? "#" : "#";

                    // Create content preview
                    var content = document.TryGetValue("content", out var contentValue) ? 
                        contentValue?.ToString() ?? "" : "";
                    var contentPreview = CreatePreview(content);

                    var processedResult = new ProcessedResult
                    {
                        Title = title,
                        Score = score,
                        Author = author,
                        ContentPreview = contentPreview,
                        Url = url
                    };

                    processedResults.Add(processedResult);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error processing result: {ex.Message}");
                    continue;
                }
            }

            return processedResults;
        }

        /// <summary>
        /// Create a content preview with appropriate length
        /// </summary>
        /// <param name="content">Full content text</param>
        /// <returns>Preview text</returns>
        private string CreatePreview(string content)
        {
            if (string.IsNullOrEmpty(content))
                return "No content available";

            if (content.Length <= _maxContentLength)
                return content;

            // Find a good breaking point
            var preview = content.Substring(0, _maxContentLength);
            var lastSpace = preview.LastIndexOf(' ');

            if (lastSpace > _maxContentLength * 0.8)
                preview = preview.Substring(0, lastSpace);

            return preview + "...";
        }

        /// <summary>
        /// Format results for console display
        /// </summary>
        /// <param name="results">List of ProcessedResult objects</param>
        /// <returns>Formatted string for display</returns>
        public string FormatForDisplay(List<ProcessedResult> results)
        {
            if (results == null || results.Count == 0)
                return "No results found.";

            var output = new List<string>
            {
                "",
                new string('=', 60),
                $"SEARCH RESULTS ({results.Count} found)",
                new string('=', 60)
            };

            for (int i = 0; i < results.Count; i++)
            {
                var result = results[i];
                output.Add($"\n{i + 1}. {result.Title}");
                output.Add($"   Score: {result.Score:F3}");

                if (result.Author != "Unknown")
                    output.Add($"   Author: {result.Author}");

                if (!string.IsNullOrEmpty(result.ContentPreview))
                    output.Add($"   Preview: {result.ContentPreview}");

                if (result.Url != "#")
                    output.Add($"   URL: {result.Url}");

                output.Add($"   {new string('-', 50)}");
            }

            return string.Join("\n", output);
        }

        /// <summary>
        /// Sort results by score
        /// </summary>
        /// <param name="results">Results to sort</param>
        /// <param name="descending">Sort in descending order</param>
        /// <returns>Sorted results</returns>
        public List<ProcessedResult> SortByScore(List<ProcessedResult> results, bool descending = true)
        {
            return descending ? 
                results.OrderByDescending(r => r.Score).ToList() :
                results.OrderBy(r => r.Score).ToList();
        }

        /// <summary>
        /// Filter results by minimum score
        /// </summary>
        /// <param name="results">Results to filter</param>
        /// <param name="minScore">Minimum score threshold</param>
        /// <returns>Filtered results</returns>
        public List<ProcessedResult> FilterByScore(List<ProcessedResult> results, double minScore)
        {
            return results.Where(r => r.Score >= minScore).ToList();
        }

        /// <summary>
        /// Analyze score distribution
        /// </summary>
        /// <param name="results">Results to analyze</param>
        /// <returns>Score statistics</returns>
        public Dictionary<string, double> AnalyzeScores(List<ProcessedResult> results)
        {
            if (results == null || results.Count == 0)
                return new Dictionary<string, double>();

            var scores = results.Select(r => r.Score).ToList();

            return new Dictionary<string, double>
            {
                ["count"] = scores.Count,
                ["minScore"] = scores.Min(),
                ["maxScore"] = scores.Max(),
                ["avgScore"] = scores.Average(),
                ["scoreRange"] = scores.Max() - scores.Min()
            };
        }

        /// <summary>
        /// Export results to JSON file
        /// </summary>
        /// <param name="results">Results to export</param>
        /// <param name="filename">Output filename</param>
        public async Task ExportToJsonAsync(List<ProcessedResult> results, string filename)
        {
            try
            {
                var resultsDictionary = results.Select(r => r.ToDictionary()).ToList();
                
                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                };

                var json = JsonSerializer.Serialize(resultsDictionary, options);
                await File.WriteAllTextAsync(filename, json);

                Console.WriteLine($"✅ Results exported to {filename}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error exporting to JSON: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class ResultProcessingProgram
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
                    new Azure.AzureKeyCredential(ApiKey)
                );

                await DemonstrateResultProcessingAsync(searchClient);

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Try processing results from different searches");
                Console.WriteLine("   - Experiment with different filtering criteria");
                Console.WriteLine("   - Check out 07_ErrorHandling.cs for robust error handling");
                Console.WriteLine("   - Learn about search patterns in 08_SearchPatterns.cs");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstrateResultProcessingAsync(SearchClient searchClient)
        {
            Console.WriteLine("🔧 Result Processing Demonstration");
            Console.WriteLine(new string('=', 50));

            try
            {
                // Get some sample results
                var searchOptions = new SearchOptions { Size = 5 };
                var rawResults = await searchClient.SearchAsync<SearchDocument>("python programming", searchOptions);

                var resultsList = new List<SearchResult<SearchDocument>>();
                await foreach (var result in rawResults.Value.GetResultsAsync())
                {
                    resultsList.Add(result);
                }

                if (resultsList.Count == 0)
                {
                    Console.WriteLine("❌ No results found for demo. Make sure your index has data.");
                    return;
                }

                // Process results
                var processor = new ResultProcessor();
                var processedResults = processor.ProcessRawResults(rawResults.Value);

                Console.WriteLine($"✅ Processed {processedResults.Count} results");

                // Display formatted results
                var formattedOutput = processor.FormatForDisplay(processedResults.Take(3).ToList());
                Console.WriteLine(formattedOutput);

                // Analyze scores
                var stats = processor.AnalyzeScores(processedResults);
                Console.WriteLine($"\n📊 Score Analysis:");
                Console.WriteLine($"   Total results: {stats["count"]}");
                Console.WriteLine($"   Score range: {stats["minScore"]:F3} - {stats["maxScore"]:F3}");
                Console.WriteLine($"   Average score: {stats["avgScore"]:F3}");

                // Filter high-quality results
                var highQuality = processor.FilterByScore(processedResults, 1.0);
                Console.WriteLine($"\n🎯 High-quality results (score ≥ 1.0): {highQuality.Count}");

                // Export to JSON
                await processor.ExportToJsonAsync(processedResults, "sample_results.json");

                Console.WriteLine("\n✅ Result processing demonstration completed!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
            }
        }
    }
}