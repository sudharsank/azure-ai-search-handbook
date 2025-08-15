/*
 * Module 7: Hit Highlighting for Enhanced Search Results
 * 
 * This example demonstrates how to implement hit highlighting to emphasize
 * search terms in results, improving user experience and search relevance visibility.
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace AzureSearchHitHighlighting
{
    /// <summary>
    /// Represents the result of a hit highlighting operation
    /// </summary>
    /// <typeparam name="T">The type of documents in the result</typeparam>
    public class HighlightResult<T>
    {
        public List<SearchResult<T>> Documents { get; set; } = new List<SearchResult<T>>();
        public List<Dictionary<string, IList<string>>> Highlights { get; set; } = new List<Dictionary<string, IList<string>>>();
        public List<string> SearchTerms { get; set; } = new List<string>();
        public List<string> HighlightedFields { get; set; } = new List<string>();
        public double DurationMs { get; set; }
        public string Query { get; set; } = string.Empty;
        public int HighlightCount { get; set; }
    }

    /// <summary>
    /// Hit highlighter for emphasizing search terms in results
    /// </summary>
    /// <typeparam name="T">The type of documents to work with</typeparam>
    public class HitHighlighter<T> where T : class
    {
        private readonly SearchClient _searchClient;
        private readonly List<string> _defaultHighlightFields;
        private readonly string _defaultPreTag;
        private readonly string _defaultPostTag;

        public HitHighlighter(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
            _defaultHighlightFields = new List<string> { "hotelName", "description", "category" };
            _defaultPreTag = "<em>";
            _defaultPostTag = "</em>";
        }

        /// <summary>
        /// Search with hit highlighting enabled
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="highlightFields">Fields to highlight (null for default)</param>
        /// <param name="preTag">Opening highlight tag</param>
        /// <param name="postTag">Closing highlight tag</param>
        /// <param name="maxHighlights">Maximum highlights per field</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>HighlightResult with highlighted content</returns>
        public async Task<HighlightResult<T>> SearchWithHighlightingAsync(
            string searchText,
            IList<string>? highlightFields = null,
            string preTag = "<em>",
            string postTag = "</em>",
            int maxHighlights = 5,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            try
            {
                highlightFields ??= _defaultHighlightFields;

                Console.WriteLine($"Searching with highlighting: '{searchText}'");
                Console.WriteLine($"Highlight fields: {string.Join(", ", highlightFields)}");

                var stopwatch = Stopwatch.StartNew();

                // Configure search options
                var searchOptions = options ?? new SearchOptions();
                searchOptions.Size = searchOptions.Size ?? 10;
                searchOptions.Skip = searchOptions.Skip ?? 0;

                // Configure highlighting
                searchOptions.HighlightFields.Clear();
                foreach (var field in highlightFields)
                {
                    searchOptions.HighlightFields.Add($"{field}-{maxHighlights}");
                }
                searchOptions.HighlightPreTag = preTag;
                searchOptions.HighlightPostTag = postTag;

                // Perform search
                var response = await _searchClient.SearchAsync<T>(searchText, searchOptions, cancellationToken);
                var searchResults = response.Value;

                // Process results
                var documents = new List<SearchResult<T>>();
                var highlights = new List<Dictionary<string, IList<string>>>();
                var highlightCount = 0;

                await foreach (var result in searchResults.GetResultsAsync())
                {
                    documents.Add(result);

                    // Extract highlights
                    var resultHighlights = new Dictionary<string, IList<string>>();
                    if (result.Highlights != null)
                    {
                        foreach (var highlight in result.Highlights)
                        {
                            resultHighlights[highlight.Key] = highlight.Value;
                            highlightCount += highlight.Value.Count;
                        }
                    }
                    highlights.Add(resultHighlights);
                }

                stopwatch.Stop();
                var duration = stopwatch.Elapsed.TotalMilliseconds;

                // Extract search terms for analysis
                var searchTerms = ExtractSearchTerms(searchText);

                Console.WriteLine($"Search completed in {duration:F1}ms");
                Console.WriteLine($"Found {documents.Count} results with {highlightCount} highlights");

                return new HighlightResult<T>
                {
                    Documents = documents,
                    Highlights = highlights,
                    SearchTerms = searchTerms,
                    HighlightedFields = highlightFields.ToList(),
                    DurationMs = duration,
                    Query = searchText,
                    HighlightCount = highlightCount
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Hit highlighting search error: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search with predefined highlight tag styles
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="tagStyle">Style name ('bold', 'italic', 'mark', 'custom')</param>
        /// <param name="highlightFields">Fields to highlight</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>HighlightResult with styled highlights</returns>
        public async Task<HighlightResult<T>> SearchWithCustomTagsAsync(
            string searchText,
            string tagStyle = "bold",
            IList<string>? highlightFields = null,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            var tagStyles = new Dictionary<string, (string PreTag, string PostTag)>
            {
                ["bold"] = ("<b>", "</b>"),
                ["italic"] = ("<i>", "</i>"),
                ["mark"] = ("<mark>", "</mark>"),
                ["underline"] = ("<u>", "</u>"),
                ["strong"] = ("<strong>", "</strong>"),
                ["span"] = ("<span class=\"highlight\">", "</span>"),
                ["custom"] = ("**", "**") // Markdown-style
            };

            if (!tagStyles.ContainsKey(tagStyle))
            {
                throw new ArgumentException($"Unknown tag style: {tagStyle}");
            }

            var (preTag, postTag) = tagStyles[tagStyle];

            Console.WriteLine($"Using {tagStyle} highlighting style: {preTag}...{postTag}");

            return await SearchWithHighlightingAsync(
                searchText, highlightFields, preTag, postTag, 
                cancellationToken: cancellationToken, options: options);
        }

        /// <summary>
        /// Search with phrase highlighting (quoted search)
        /// </summary>
        /// <param name="phrase">Phrase to search for</param>
        /// <param name="highlightFields">Fields to highlight</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <param name="options">Additional search options</param>
        /// <returns>HighlightResult with phrase highlights</returns>
        public async Task<HighlightResult<T>> SearchPhraseHighlightingAsync(
            string phrase,
            IList<string>? highlightFields = null,
            CancellationToken cancellationToken = default,
            SearchOptions? options = null)
        {
            // Ensure phrase is quoted for exact matching
            var quotedPhrase = phrase.StartsWith("\"") ? phrase : $"\"{phrase}\"";

            Console.WriteLine($"Searching for phrase: {quotedPhrase}");

            return await SearchWithHighlightingAsync(
                quotedPhrase, highlightFields, 
                cancellationToken: cancellationToken, options: options);
        }

        /// <summary>
        /// Compare different highlighting strategies
        /// </summary>
        /// <param name="searchText">Search query</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>Comparison results</returns>
        public async Task<Dictionary<string, object>> CompareHighlightingStrategiesAsync(
            string searchText,
            CancellationToken cancellationToken = default)
        {
            var strategies = new List<(string Name, IList<string>? Fields, int MaxHighlights)>
            {
                ("Default Fields", null, 5),
                ("Title Only", new List<string> { "hotelName" }, 3),
                ("Description Only", new List<string> { "description" }, 10),
                ("All Text Fields", new List<string> { "hotelName", "description", "category", "tags" }, 5)
            };

            var comparisons = new List<Dictionary<string, object>>();

            foreach (var (name, fields, maxHighlights) in strategies)
            {
                try
                {
                    var result = await SearchWithHighlightingAsync(
                        searchText, fields, maxHighlights: maxHighlights, 
                        cancellationToken: cancellationToken,
                        options: new SearchOptions { Size = 5 });

                    comparisons.Add(new Dictionary<string, object>
                    {
                        ["name"] = name,
                        ["fields"] = fields ?? _defaultHighlightFields,
                        ["durationMs"] = result.DurationMs,
                        ["highlightCount"] = result.HighlightCount,
                        ["resultsCount"] = result.Documents.Count,
                        ["avgHighlightsPerResult"] = result.Documents.Count > 0 ? 
                            (double)result.HighlightCount / result.Documents.Count : 0
                    });

                    Console.WriteLine($"{name}: {result.HighlightCount} highlights in {result.DurationMs:F1}ms");
                }
                catch (Exception ex)
                {
                    comparisons.Add(new Dictionary<string, object>
                    {
                        ["name"] = name,
                        ["error"] = ex.Message
                    });
                }
            }

            var bestStrategy = comparisons
                .Where(c => !c.ContainsKey("error"))
                .OrderByDescending(c => (int)c["highlightCount"])
                .FirstOrDefault();

            return new Dictionary<string, object>
            {
                ["query"] = searchText,
                ["strategies"] = comparisons,
                ["bestStrategy"] = bestStrategy
            };
        }

        /// <summary>
        /// Analyze highlight coverage and effectiveness
        /// </summary>
        /// <param name="result">HighlightResult to analyze</param>
        /// <returns>Coverage analysis</returns>
        public Dictionary<string, object> AnalyzeHighlightCoverage(HighlightResult<T> result)
        {
            var analysis = new Dictionary<string, object>
            {
                ["totalDocuments"] = result.Documents.Count,
                ["totalHighlights"] = result.HighlightCount,
                ["highlightedDocuments"] = 0,
                ["fieldCoverage"] = new Dictionary<string, Dictionary<string, object>>(),
                ["highlightDistribution"] = new List<Dictionary<string, object>>(),
                ["searchTermsFound"] = new List<string>()
            };

            var fieldCoverage = (Dictionary<string, Dictionary<string, object>>)analysis["fieldCoverage"];
            var highlightDistribution = (List<Dictionary<string, object>>)analysis["highlightDistribution"];
            var searchTermsFound = (List<string>)analysis["searchTermsFound"];

            // Initialize field coverage
            foreach (var field in result.HighlightedFields)
            {
                fieldCoverage[field] = new Dictionary<string, object>
                {
                    ["documentsWithHighlights"] = 0,
                    ["totalHighlights"] = 0,
                    ["avgHighlightsPerDoc"] = 0.0
                };
            }

            // Process each document's highlights
            for (int i = 0; i < result.Highlights.Count; i++)
            {
                var highlights = result.Highlights[i];
                var docHighlightCount = 0;

                if (highlights.Any())
                {
                    analysis["highlightedDocuments"] = (int)analysis["highlightedDocuments"] + 1;

                    foreach (var (field, fieldHighlights) in highlights)
                    {
                        if (fieldCoverage.ContainsKey(field))
                        {
                            var fieldData = fieldCoverage[field];
                            fieldData["documentsWithHighlights"] = (int)fieldData["documentsWithHighlights"] + 1;
                            fieldData["totalHighlights"] = (int)fieldData["totalHighlights"] + fieldHighlights.Count;
                            docHighlightCount += fieldHighlights.Count;
                        }
                    }
                }

                highlightDistribution.Add(new Dictionary<string, object>
                {
                    ["documentIndex"] = i,
                    ["highlightCount"] = docHighlightCount
                });
            }

            // Calculate averages
            foreach (var (field, fieldData) in fieldCoverage)
            {
                var docsWithHighlights = (int)fieldData["documentsWithHighlights"];
                if (docsWithHighlights > 0)
                {
                    var totalHighlights = (int)fieldData["totalHighlights"];
                    fieldData["avgHighlightsPerDoc"] = (double)totalHighlights / docsWithHighlights;
                }
            }

            // Analyze search term coverage
            foreach (var term in result.SearchTerms)
            {
                var termFound = result.Highlights.Any(docHighlights =>
                    docHighlights.Values.Any(highlightList =>
                        highlightList.Any(highlight => 
                            highlight.Contains(term, StringComparison.OrdinalIgnoreCase))));

                if (termFound)
                {
                    searchTermsFound.Add(term);
                }
            }

            var totalDocs = (int)analysis["totalDocuments"];
            var highlightedDocs = (int)analysis["highlightedDocuments"];
            analysis["coveragePercentage"] = totalDocs > 0 ? (double)highlightedDocs / totalDocs * 100 : 0;

            return analysis;
        }

        /// <summary>
        /// Extract highlighted snippets for display
        /// </summary>
        /// <param name="result">HighlightResult to process</param>
        /// <param name="maxSnippetLength">Maximum snippet length</param>
        /// <returns>List of snippet data</returns>
        public List<Dictionary<string, object>> ExtractHighlightedSnippets(
            HighlightResult<T> result, 
            int maxSnippetLength = 200)
        {
            var snippets = new List<Dictionary<string, object>>();

            for (int i = 0; i < result.Documents.Count; i++)
            {
                var doc = result.Documents[i].Document;
                var highlights = result.Highlights[i];

                var docSnippets = new Dictionary<string, object>
                {
                    ["documentIndex"] = i,
                    ["documentId"] = GetDocumentId(doc),
                    ["title"] = GetDocumentTitle(doc),
                    ["snippets"] = new List<Dictionary<string, object>>()
                };

                var snippetList = (List<Dictionary<string, object>>)docSnippets["snippets"];

                foreach (var (field, fieldHighlights) in highlights)
                {
                    foreach (var highlight in fieldHighlights)
                    {
                        var truncatedHighlight = highlight;
                        
                        // Truncate if too long
                        if (highlight.Length > maxSnippetLength)
                        {
                            // Try to keep highlight tags intact
                            var truncated = highlight.Substring(0, maxSnippetLength);
                            var lastOpenTag = truncated.LastIndexOf('<');
                            var lastCloseTag = truncated.LastIndexOf('>');
                            
                            if (lastOpenTag > lastCloseTag)
                            {
                                // Incomplete tag, truncate before it
                                truncated = highlight.Substring(0, lastOpenTag);
                            }
                            truncatedHighlight = truncated + "...";
                        }

                        snippetList.Add(new Dictionary<string, object>
                        {
                            ["field"] = field,
                            ["text"] = truncatedHighlight,
                            ["length"] = truncatedHighlight.Length
                        });
                    }
                }

                if (snippetList.Any())
                {
                    snippets.Add(docSnippets);
                }
            }

            return snippets;
        }

        private List<string> ExtractSearchTerms(string searchText)
        {
            // Simple term extraction (could be enhanced for complex queries)
            var cleaned = Regex.Replace(searchText, @"[^\w\s]", " ");
            var terms = cleaned.Split(' ', StringSplitOptions.RemoveEmptyEntries)
                              .Where(term => !string.IsNullOrWhiteSpace(term))
                              .ToList();
            return terms;
        }

        private string GetDocumentId(T document)
        {
            // Try to get document ID using reflection
            var idProperty = document.GetType().GetProperty("HotelId") ?? 
                           document.GetType().GetProperty("Id") ?? 
                           document.GetType().GetProperty("id");
            
            return idProperty?.GetValue(document)?.ToString() ?? $"doc_{document.GetHashCode()}";
        }

        private string GetDocumentTitle(T document)
        {
            // Try to get document title using reflection
            var titleProperty = document.GetType().GetProperty("HotelName") ?? 
                              document.GetType().GetProperty("Title") ?? 
                              document.GetType().GetProperty("Name");
            
            return titleProperty?.GetValue(document)?.ToString() ?? "Unknown";
        }
    }

    /// <summary>
    /// Hotel model for demonstration
    /// </summary>
    public class Hotel
    {
        public string HotelId { get; set; } = string.Empty;
        public string HotelName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public double? Rating { get; set; }
        public GeographyPoint? Location { get; set; }
        public string[] Tags { get; set; } = Array.Empty<string>();
    }

    /// <summary>
    /// Demonstration class for hit highlighting
    /// </summary>
    public class HitHighlightingDemo
    {
        private readonly SearchClient _searchClient;

        public HitHighlightingDemo(SearchClient searchClient)
        {
            _searchClient = searchClient;
        }

        /// <summary>
        /// Demonstrates basic hit highlighting functionality
        /// </summary>
        public async Task DemonstrateBasicHighlightingAsync()
        {
            Console.WriteLine("=== Basic Hit Highlighting Demo ===\n");

            var highlighter = new HitHighlighter<Hotel>(_searchClient);

            try
            {
                // Basic highlighting
                Console.WriteLine("1. Basic highlighting with default settings:");
                var result = await highlighter.SearchWithHighlightingAsync("luxury hotel", options: new SearchOptions { Size = 3 });

                Console.WriteLine($"Query: '{result.Query}'");
                Console.WriteLine($"Highlighted fields: {string.Join(", ", result.HighlightedFields)}");
                Console.WriteLine($"Total highlights: {result.HighlightCount}");

                // Display highlighted results
                for (int i = 0; i < result.Documents.Count; i++)
                {
                    var doc = result.Documents[i].Document;
                    var highlights = result.Highlights[i];

                    Console.WriteLine($"\n  Result {i + 1}: {doc.HotelName}");

                    foreach (var (field, fieldHighlights) in highlights)
                    {
                        Console.WriteLine($"    {field}:");
                        foreach (var highlight in fieldHighlights)
                        {
                            Console.WriteLine($"      • {highlight}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Basic highlighting demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates custom highlighting tags and styles
        /// </summary>
        public async Task DemonstrateCustomHighlightingAsync()
        {
            Console.WriteLine("\n=== Custom Highlighting Demo ===\n");

            var highlighter = new HitHighlighter<Hotel>(_searchClient);

            try
            {
                var searchQuery = "beach resort";
                var styles = new[] { "bold", "mark", "custom" };

                foreach (var style in styles)
                {
                    Console.WriteLine($"{style.ToUpper()} highlighting:");
                    var result = await highlighter.SearchWithCustomTagsAsync(
                        searchQuery, style, options: new SearchOptions { Size = 2 });

                    // Show first result's highlights
                    if (result.Highlights.Any())
                    {
                        var firstHighlights = result.Highlights[0];
                        foreach (var (field, highlights) in firstHighlights)
                        {
                            if (highlights.Any())
                            {
                                Console.WriteLine($"  {field}: {highlights[0]}");
                            }
                        }
                    }
                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Custom highlighting demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates phrase highlighting
        /// </summary>
        public async Task DemonstratePhraseHighlightingAsync()
        {
            Console.WriteLine("=== Phrase Highlighting Demo ===\n");

            var highlighter = new HitHighlighter<Hotel>(_searchClient);

            try
            {
                // Compare individual terms vs phrase
                var phrase = "luxury hotel";

                Console.WriteLine("1. Individual terms highlighting:");
                var individualResult = await highlighter.SearchWithHighlightingAsync(phrase, options: new SearchOptions { Size = 2 });

                Console.WriteLine("2. Phrase highlighting:");
                var phraseResult = await highlighter.SearchPhraseHighlightingAsync(phrase, options: new SearchOptions { Size = 2 });

                Console.WriteLine($"\nIndividual terms: {individualResult.HighlightCount} highlights");
                Console.WriteLine($"Phrase search: {phraseResult.HighlightCount} highlights");

                // Show comparison
                if (phraseResult.Highlights.Any())
                {
                    Console.WriteLine("\nPhrase highlighting example:");
                    var firstHighlights = phraseResult.Highlights[0];
                    foreach (var (field, highlights) in firstHighlights)
                    {
                        foreach (var highlight in highlights)
                        {
                            Console.WriteLine($"  {field}: {highlight}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Phrase highlighting demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates highlighting analysis and optimization
        /// </summary>
        public async Task DemonstrateHighlightingAnalysisAsync()
        {
            Console.WriteLine("\n=== Highlighting Analysis Demo ===\n");

            var highlighter = new HitHighlighter<Hotel>(_searchClient);

            try
            {
                var searchQuery = "spa wellness";

                // Compare strategies
                Console.WriteLine("1. Comparing highlighting strategies:");
                var comparison = await highlighter.CompareHighlightingStrategiesAsync(searchQuery);

                Console.WriteLine($"Query: '{comparison["query"]}'");
                var strategies = (List<Dictionary<string, object>>)comparison["strategies"];
                foreach (var strategy in strategies)
                {
                    if (strategy.ContainsKey("error"))
                    {
                        Console.WriteLine($"  {strategy["name"]}: ERROR - {strategy["error"]}");
                    }
                    else
                    {
                        Console.WriteLine($"  {strategy["name"]}: {strategy["highlightCount"]} highlights, " +
                                        $"{strategy["avgHighlightsPerResult"]:F1} avg per result");
                    }
                }

                if (comparison["bestStrategy"] != null)
                {
                    var bestStrategy = (Dictionary<string, object>)comparison["bestStrategy"];
                    Console.WriteLine($"\nBest strategy: {bestStrategy["name"]}");
                }

                // Detailed analysis
                Console.WriteLine("\n2. Detailed highlight analysis:");
                var result = await highlighter.SearchWithHighlightingAsync(searchQuery, options: new SearchOptions { Size = 5 });
                var analysis = highlighter.AnalyzeHighlightCoverage(result);

                Console.WriteLine($"Coverage: {analysis["coveragePercentage"]:F1}% of documents highlighted");
                Console.WriteLine($"Total highlights: {analysis["totalHighlights"]}");
                var searchTermsFound = (List<string>)analysis["searchTermsFound"];
                Console.WriteLine($"Search terms found: {string.Join(", ", searchTermsFound)}");

                Console.WriteLine("\nField coverage:");
                var fieldCoverage = (Dictionary<string, Dictionary<string, object>>)analysis["fieldCoverage"];
                foreach (var (field, coverage) in fieldCoverage)
                {
                    Console.WriteLine($"  {field}: {coverage["documentsWithHighlights"]} docs, " +
                                    $"{coverage["totalHighlights"]} highlights");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Highlighting analysis demo error: {ex.Message}");
            }
        }

        /// <summary>
        /// Demonstrates highlighted snippet extraction
        /// </summary>
        public async Task DemonstrateSnippetExtractionAsync()
        {
            Console.WriteLine("\n=== Snippet Extraction Demo ===\n");

            var highlighter = new HitHighlighter<Hotel>(_searchClient);

            try
            {
                var result = await highlighter.SearchWithHighlightingAsync(
                    "ocean view restaurant",
                    new List<string> { "description", "hotelName" },
                    options: new SearchOptions { Size = 3 });

                var snippets = highlighter.ExtractHighlightedSnippets(result, maxSnippetLength: 150);

                Console.WriteLine("Extracted highlighted snippets:");
                foreach (var snippetData in snippets)
                {
                    Console.WriteLine($"\n{snippetData["title"]} (ID: {snippetData["documentId"]}):");

                    var snippetList = (List<Dictionary<string, object>>)snippetData["snippets"];
                    foreach (var snippet in snippetList)
                    {
                        Console.WriteLine($"  [{snippet["field"]}] {snippet["text"]}");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Snippet extraction demo error: {ex.Message}");
            }
        }
    }

    /// <summary>
    /// Utility class for common highlighting patterns
    /// </summary>
    public static class HighlightingHelper
    {
        public static Dictionary<string, object> ForSearchResults() => new Dictionary<string, object>
        {
            ["highlightFields"] = new List<string> { "hotelName", "description" },
            ["preTag"] = "<mark>",
            ["postTag"] = "</mark>",
            ["maxHighlights"] = 3
        };

        public static Dictionary<string, object> ForAutocomplete() => new Dictionary<string, object>
        {
            ["highlightFields"] = new List<string> { "hotelName" },
            ["preTag"] = "<strong>",
            ["postTag"] = "</strong>",
            ["maxHighlights"] = 1
        };

        public static Dictionary<string, object> ForDetailedView() => new Dictionary<string, object>
        {
            ["highlightFields"] = new List<string> { "hotelName", "description", "category", "tags" },
            ["preTag"] = "<span class=\"highlight\">",
            ["postTag"] = "</span>",
            ["maxHighlights"] = 10
        };

        public static string CleanHighlights(string text, bool preserveTags = false)
        {
            if (preserveTags) return text;

            // Remove common highlight tags
            var patterns = new[]
            {
                @"<em>(.*?)</em>",
                @"<mark>(.*?)</mark>",
                @"<b>(.*?)</b>",
                @"<strong>(.*?)</strong>",
                @"<span[^>]*>(.*?)</span>"
            };

            var cleaned = text;
            foreach (var pattern in patterns)
            {
                cleaned = Regex.Replace(cleaned, pattern, "$1");
            }

            return cleaned;
        }
    }

    /// <summary>
    /// Program entry point for demonstration
    /// </summary>
    public class Program
    {
        public static async Task Main(string[] args)
        {
            try
            {
                // Configuration
                var configuration = new ConfigurationBuilder()
                    .AddJsonFile("appsettings.json", optional: true)
                    .AddEnvironmentVariables()
                    .Build();

                var serviceName = configuration["AzureSearch:ServiceName"] ?? 
                                Environment.GetEnvironmentVariable("AZURE_SEARCH_SERVICE_NAME");
                var indexName = configuration["AzureSearch:IndexName"] ?? 
                              Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX_NAME") ?? 
                              "hotels-sample";
                var apiKey = configuration["AzureSearch:ApiKey"] ?? 
                           Environment.GetEnvironmentVariable("AZURE_SEARCH_API_KEY");

                if (string.IsNullOrEmpty(serviceName) || string.IsNullOrEmpty(apiKey))
                {
                    Console.WriteLine("Please configure Azure Search service name and API key");
                    return;
                }

                // Initialize search client
                var endpoint = new Uri($"https://{serviceName}.search.windows.net");
                var credential = new AzureKeyCredential(apiKey);
                var searchClient = new SearchClient(endpoint, indexName, credential);

                // Run demonstrations
                var demo = new HitHighlightingDemo(searchClient);
                await demo.DemonstrateBasicHighlightingAsync();
                await demo.DemonstrateCustomHighlightingAsync();
                await demo.DemonstratePhraseHighlightingAsync();
                await demo.DemonstrateHighlightingAnalysisAsync();
                await demo.DemonstrateSnippetExtractionAsync();

                // Show helper usage
                Console.WriteLine("\n=== Highlighting Helper Demo ===\n");
                Console.WriteLine("Helper configurations:");
                var searchResults = HighlightingHelper.ForSearchResults();
                var autocomplete = HighlightingHelper.ForAutocomplete();
                var detailedView = HighlightingHelper.ForDetailedView();

                Console.WriteLine($"Search results: {JsonSerializer.Serialize(searchResults)}");
                Console.WriteLine($"Autocomplete: {JsonSerializer.Serialize(autocomplete)}");
                Console.WriteLine($"Detailed view: {JsonSerializer.Serialize(detailedView)}");

                // Test cleaning
                var sampleText = "This is a <mark>highlighted</mark> <em>sample</em> text.";
                Console.WriteLine($"\nOriginal: {sampleText}");
                Console.WriteLine($"Cleaned: {HighlightingHelper.CleanHighlights(sampleText)}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Demo failed: {ex.Message}");
            }
        }
    }
}