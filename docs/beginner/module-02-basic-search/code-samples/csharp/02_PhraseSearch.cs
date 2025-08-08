/*
Phrase Search - Module 2 C# Examples
Exact phrase matching in Azure AI Search using .NET SDK

This module demonstrates:
- Exact phrase search with quotes
- Comparing phrase vs individual terms
- Understanding when to use phrase search
- Phrase search best practices
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
    public class PhraseSearch
    {
        private readonly SearchClient _searchClient;

        public PhraseSearch(SearchClient searchClient)
        {
            _searchClient = searchClient ?? throw new ArgumentNullException(nameof(searchClient));
        }

        /// <summary>
        /// Search for an exact phrase using quotes
        /// </summary>
        /// <param name="phrase">Exact phrase to search for</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> ExactPhraseSearchAsync(string phrase, int top = 10)
        {
            try
            {
                // Wrap phrase in quotes for exact matching
                var quotedPhrase = $"\"{phrase}\"";
                Console.WriteLine($"Performing exact phrase search: {quotedPhrase}");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(quotedPhrase, searchOptions);
                
                Console.WriteLine($"Found exact phrase matches");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in phrase search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for individual terms (without quotes)
        /// </summary>
        /// <param name="phrase">Terms to search for individually</param>
        /// <param name="top">Maximum number of results to return</param>
        /// <returns>Search results</returns>
        public async Task<SearchResults<SearchDocument>> IndividualTermsSearchAsync(string phrase, int top = 10)
        {
            try
            {
                Console.WriteLine($"Performing individual terms search: '{phrase}'");

                var searchOptions = new SearchOptions
                {
                    Size = top,
                    IncludeTotalCount = true
                };

                var results = await _searchClient.SearchAsync<SearchDocument>(phrase, searchOptions);
                
                Console.WriteLine($"Found results for individual terms");
                return results.Value;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in individual terms search: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Compare exact phrase search vs individual terms search
        /// </summary>
        /// <param name="phrase">Phrase to compare</param>
        /// <param name="top">Maximum number of results for each search</param>
        /// <returns>Tuple of (phrase_results, terms_results)</returns>
        public async Task<(SearchResults<SearchDocument> phraseResults, SearchResults<SearchDocument> termsResults)> 
            ComparePhraseVsTermsAsync(string phrase, int top = 5)
        {
            var phraseResults = await ExactPhraseSearchAsync(phrase, top);
            var termsResults = await IndividualTermsSearchAsync(phrase, top);

            return (phraseResults, termsResults);
        }

        /// <summary>
        /// Display comparison between phrase and terms search
        /// </summary>
        /// <param name="phrase">Original phrase searched</param>
        /// <param name="phraseResults">Results from exact phrase search</param>
        /// <param name="termsResults">Results from individual terms search</param>
        public static void DisplayComparison(string phrase, 
            SearchResults<SearchDocument> phraseResults, 
            SearchResults<SearchDocument> termsResults)
        {
            Console.WriteLine($"\n🔤 Phrase vs Terms Comparison: '{phrase}'");
            Console.WriteLine(new string('=', 60));

            // Convert results to lists for easier handling
            var phraseList = phraseResults?.GetResults()?.ToList() ?? new List<SearchResult<SearchDocument>>();
            var termsList = termsResults?.GetResults()?.ToList() ?? new List<SearchResult<SearchDocument>>();

            // Exact phrase results
            Console.WriteLine($"\n1️⃣ EXACT PHRASE SEARCH: \"{phrase}\"");
            Console.WriteLine(new string('-', 40));
            Console.WriteLine($"Results found: {phraseList.Count}");

            if (phraseList.Any())
            {
                Console.WriteLine("Top matches:");
                for (int i = 0; i < Math.Min(3, phraseList.Count); i++)
                {
                    var result = phraseList[i];
                    var title = result.Document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() : "No title";
                    var score = result.Score ?? 0.0;
                    Console.WriteLine($"  {i + 1}. {title} (Score: {score:F3})");
                }
            }
            else
            {
                Console.WriteLine("  No exact phrase matches found");
            }

            // Individual terms results
            Console.WriteLine($"\n2️⃣ INDIVIDUAL TERMS SEARCH: {phrase}");
            Console.WriteLine(new string('-', 40));
            Console.WriteLine($"Results found: {termsList.Count}");

            if (termsList.Any())
            {
                Console.WriteLine("Top matches:");
                for (int i = 0; i < Math.Min(3, termsList.Count); i++)
                {
                    var result = termsList[i];
                    var title = result.Document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() : "No title";
                    var score = result.Score ?? 0.0;
                    Console.WriteLine($"  {i + 1}. {title} (Score: {score:F3})");
                }
            }
            else
            {
                Console.WriteLine("  No results found for individual terms");
            }

            // Analysis
            Console.WriteLine($"\n📊 COMPARISON ANALYSIS:");
            Console.WriteLine($"   Exact phrase: {phraseList.Count} results");
            Console.WriteLine($"   Individual terms: {termsList.Count} results");

            if (phraseList.Any() && termsList.Any())
            {
                var phraseAvg = phraseList.Where(r => r.Score.HasValue).Average(r => r.Score.Value);
                var termsAvg = termsList.Where(r => r.Score.HasValue).Average(r => r.Score.Value);
                Console.WriteLine($"   Average phrase score: {phraseAvg:F3}");
                Console.WriteLine($"   Average terms score: {termsAvg:F3}");
            }

            // Recommendations
            Console.WriteLine($"\n💡 RECOMMENDATIONS:");
            if (phraseList.Count > 0)
            {
                Console.WriteLine("   ✅ Exact phrase found - use phrase search for precision");
            }
            else if (termsList.Count > 0)
            {
                Console.WriteLine("   ⚠️ No exact phrase - individual terms provide broader results");
            }
            else
            {
                Console.WriteLine("   ❌ No results found - try different keywords or broader terms");
            }
        }

        /// <summary>
        /// Search for multiple phrases
        /// </summary>
        /// <param name="phrases">List of phrases to search for</param>
        /// <param name="top">Maximum results per phrase</param>
        /// <returns>Dictionary mapping phrases to their results</returns>
        public async Task<Dictionary<string, SearchResults<SearchDocument>>> MultiPhraseSearchAsync(
            IEnumerable<string> phrases, int top = 3)
        {
            var results = new Dictionary<string, SearchResults<SearchDocument>>();

            foreach (var phrase in phrases)
            {
                Console.WriteLine($"Searching for phrase: '{phrase}'");
                var phraseResults = await ExactPhraseSearchAsync(phrase, top);
                results[phrase] = phraseResults;
            }

            return results;
        }
    }

    /// <summary>
    /// Program class for demonstration
    /// </summary>
    public class PhraseSearchProgram
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

                await DemonstratePhraseSearchAsync(searchClient);
                await PhraseSearchBestPracticesAsync(searchClient);

                Console.WriteLine("\n💡 Next Steps:");
                Console.WriteLine("   - Try your own phrases with the examples above");
                Console.WriteLine("   - Compare results between phrase and terms search");
                Console.WriteLine("   - Check out 03_BooleanSearch.cs for combining terms with AND/OR");
                Console.WriteLine("   - Learn about wildcards in 04_WildcardSearch.cs");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Demo failed: {ex.Message}");
                Console.WriteLine("Make sure your Azure AI Search service is configured correctly.");
            }
        }

        private static async Task DemonstratePhraseSearchAsync(SearchClient searchClient)
        {
            Console.WriteLine("🔤 Phrase Search Demonstration");
            Console.WriteLine(new string('=', 50));

            var searchOps = new PhraseSearch(searchClient);

            // Example 1: Compare phrase vs terms
            Console.WriteLine("\n1️⃣ Phrase vs Terms Comparison");

            var testPhrase = "machine learning";
            var (phraseResults, termsResults) = await searchOps.ComparePhraseVsTermsAsync(testPhrase, 5);
            PhraseSearch.DisplayComparison(testPhrase, phraseResults, termsResults);

            // Example 2: Another comparison
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n2️⃣ Another Comparison Example");

            var testPhrase2 = "web development";
            var (phraseResults2, termsResults2) = await searchOps.ComparePhraseVsTermsAsync(testPhrase2, 5);
            PhraseSearch.DisplayComparison(testPhrase2, phraseResults2, termsResults2);

            // Example 3: Multiple phrase search
            Console.WriteLine($"\n{new string('=', 70)}");
            Console.WriteLine("\n3️⃣ Multiple Phrase Search");
            Console.WriteLine(new string('-', 30));

            var phrasesToSearch = new[]
            {
                "artificial intelligence",
                "data science",
                "software engineering"
            };

            var multiResults = await searchOps.MultiPhraseSearchAsync(phrasesToSearch, 2);

            foreach (var kvp in multiResults)
            {
                var phrase = kvp.Key;
                var results = kvp.Value.GetResults().ToList();

                Console.WriteLine($"\nPhrase: \"{phrase}\"");
                Console.WriteLine($"Results: {results.Count}");
                
                if (results.Any())
                {
                    var topResult = results.First();
                    var title = topResult.Document.TryGetValue("title", out var titleValue) ? 
                        titleValue?.ToString() : "No title";
                    var score = topResult.Score ?? 0.0;
                    Console.WriteLine($"Top match: {title} (Score: {score:F3})");
                }
                else
                {
                    Console.WriteLine("No matches found");
                }
            }

            Console.WriteLine("\n✅ Phrase search demonstration completed!");
        }

        private static async Task PhraseSearchBestPracticesAsync(SearchClient searchClient)
        {
            Console.WriteLine("\n📚 Phrase Search Best Practices");
            Console.WriteLine(new string('=', 50));

            var searchOps = new PhraseSearch(searchClient);

            Console.WriteLine("\n💡 When to Use Phrase Search:");
            Console.WriteLine("   ✅ Looking for specific technical terms");
            Console.WriteLine("   ✅ Searching for proper names or titles");
            Console.WriteLine("   ✅ Finding exact quotes or references");
            Console.WriteLine("   ✅ When word order matters");

            Console.WriteLine("\n⚠️ When NOT to Use Phrase Search:");
            Console.WriteLine("   ❌ General topic searches");
            Console.WriteLine("   ❌ When you want broader results");
            Console.WriteLine("   ❌ Searching for concepts (not exact terms)");
            Console.WriteLine("   ❌ When unsure of exact wording");

            // Demonstrate with examples
            Console.WriteLine("\n🧪 Practice Examples:");

            // Good phrase search examples
            var goodPhrases = new[]
            {
                "React hooks",
                "machine learning algorithm",
                "REST API"
            };

            Console.WriteLine("\n✅ Good Phrase Search Examples:");
            foreach (var phrase in goodPhrases)
            {
                var results = await searchOps.ExactPhraseSearchAsync(phrase, 1);
                var resultCount = results.GetResults().Count();
                var status = resultCount > 0 ? "Found" : "Not found";
                Console.WriteLine($"   \"{phrase}\": {status}");
            }

            // Show fallback strategy
            Console.WriteLine("\n🔄 Fallback Strategy Example:");
            var testPhrase = "deep learning neural networks";

            // Try exact phrase first
            var exactResults = await searchOps.ExactPhraseSearchAsync(testPhrase, 3);
            var exactCount = exactResults.GetResults().Count();
            Console.WriteLine($"   Exact phrase \"{testPhrase}\": {exactCount} results");

            if (exactCount == 0)
            {
                // Fallback to individual terms
                var termsResults = await searchOps.IndividualTermsSearchAsync(testPhrase, 3);
                var termsCount = termsResults.GetResults().Count();
                Console.WriteLine($"   Fallback to terms: {termsCount} results");

                if (termsCount > 0)
                {
                    Console.WriteLine("   💡 Recommendation: Use individual terms for broader results");
                }
            }
        }
    }
}