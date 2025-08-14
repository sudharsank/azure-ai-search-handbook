using Azure;
using Azure.Search.Documents;
using Microsoft.Extensions.Configuration;

namespace AzureSearchFiltersExamples
{
    /// <summary>
    /// Factory class for creating Azure AI Search clients with proper configuration.
    /// </summary>
    public static class SearchClientFactory
    {
        /// <summary>
        /// Create a SearchClient instance from configuration.
        /// </summary>
        /// <param name="configuration">Configuration containing search service settings</param>
        /// <returns>Configured SearchClient instance</returns>
        public static SearchClient Create(IConfiguration configuration)
        {
            ValidateConfiguration(configuration);

            var endpoint = new Uri(configuration["SearchService:Endpoint"]!);
            var apiKey = configuration["SearchService:ApiKey"]!;
            var indexName = configuration["SearchService:IndexName"]!;

            var credential = new AzureKeyCredential(apiKey);
            return new SearchClient(endpoint, indexName, credential);
        }

        /// <summary>
        /// Create a SearchClient instance with explicit parameters.
        /// </summary>
        /// <param name="endpoint">Search service endpoint</param>
        /// <param name="indexName">Index name</param>
        /// <param name="apiKey">API key</param>
        /// <returns>Configured SearchClient instance</returns>
        public static SearchClient Create(string endpoint, string indexName, string apiKey)
        {
            if (string.IsNullOrEmpty(endpoint))
                throw new ArgumentException("Endpoint cannot be null or empty", nameof(endpoint));
            if (string.IsNullOrEmpty(indexName))
                throw new ArgumentException("Index name cannot be null or empty", nameof(indexName));
            if (string.IsNullOrEmpty(apiKey))
                throw new ArgumentException("API key cannot be null or empty", nameof(apiKey));

            var endpointUri = new Uri(endpoint);
            var credential = new AzureKeyCredential(apiKey);
            return new SearchClient(endpointUri, indexName, credential);
        }

        /// <summary>
        /// Validate that all required configuration values are present.
        /// </summary>
        /// <param name="configuration">Configuration to validate</param>
        /// <exception cref="InvalidOperationException">Thrown when required configuration is missing</exception>
        private static void ValidateConfiguration(IConfiguration configuration)
        {
            var endpoint = configuration["SearchService:Endpoint"];
            var apiKey = configuration["SearchService:ApiKey"];
            var indexName = configuration["SearchService:IndexName"];

            if (string.IsNullOrEmpty(endpoint))
                throw new InvalidOperationException("SearchService:Endpoint is missing from configuration");
            if (string.IsNullOrEmpty(apiKey))
                throw new InvalidOperationException("SearchService:ApiKey is missing from configuration");
            if (string.IsNullOrEmpty(indexName))
                throw new InvalidOperationException("SearchService:IndexName is missing from configuration");

            // Validate endpoint format
            if (!Uri.TryCreate(endpoint, UriKind.Absolute, out _))
                throw new InvalidOperationException("SearchService:Endpoint is not a valid URI");
        }
    }
}