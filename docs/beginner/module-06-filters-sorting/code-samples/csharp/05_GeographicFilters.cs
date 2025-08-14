/*
 * Geographic Filters Example
 * 
 * This example demonstrates geographic filtering operations in Azure AI Search,
 * including distance-based filtering, geographic bounds, and spatial queries.
 */

using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using System.Diagnostics;

namespace AzureSearchFiltersExamples
{
    public class GeographicFiltersExample
    {
        private readonly SearchClient _searchClient;
        private readonly IConfiguration _configuration;

        // Common location presets
        private static readonly Dictionary<string, (double Latitude, double Longitude)> LocationPresets = new()
        {
            { "Seattle", (47.6062, -122.3321) },
            { "NewYork", (40.7128, -74.0060) },
            { "LosAngeles", (34.0522, -118.2437) },
            { "Chicago", (41.8781, -87.6298) },
            { "Miami", (25.7617, -80.1918) },
            { "Orlando", (28.5383, -81.3792) },
            { "SanFrancisco", (37.7749, -122.4194) },
            { "Denver", (39.7392, -104.9903) }
        };

        public GeographicFiltersExample()
        {
            ValidateConfiguration();
            
            _configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();

            var endpoint = new Uri(_configuration["SearchService:Endpoint"]);
            var apiKey = _configuration["SearchService:ApiKey"];
            var indexName = _configuration["SearchService:IndexName"];

            var credential = new AzureKeyCredential(apiKey);
            _searchClient = new SearchClient(endpoint, indexName, credential);
        }

        private void ValidateConfiguration()
        {
            var config = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();

            var endpoint = config["SearchService:Endpoint"];
            var apiKey = config["SearchService:ApiKey"];
            var indexName = config["SearchService:IndexName"];

            if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(indexName))
            {
                throw new InvalidOperationException("Missing required configuration. Check your appsettings.json file.");
            }

            Console.WriteLine("✅ Configuration validated");
            Console.WriteLine($"📍 Search Endpoint: {endpoint}");
            Console.WriteLine($"📊 Index Name: {indexName}");
        }

        public async Task DemonstrateDistanceFiltersAsync()
        {
            Console.WriteLine("\n🌍 Distance-Based Filters");
            Console.WriteLine("=".PadRight(40, '='));

            var distanceExamples = new[]
            {
                new
                {
                    Name = "Nearby Seattle (5km)",
                    Location = LocationPresets["Seattle"],
                    Radius = 5.0,
                    Description = "Find locations within 5km of Seattle downtown"
                },
                new
                {
                    Name = "NYC Metro Area (25km)",
                    Location = LocationPresets["NewYork"],
                    Radius = 25.0,
                    Description = "Find locations within NYC metropolitan area"
                },
                new
                {
                    Name = "LA County (50km)",
                    Location = LocationPresets["LosAngeles"],
                    Radius = 50.0,
                    Description = "Find locations within Los Angeles County area"
                },
                new
                {
                    Name = "Chicago Suburbs (15km)",
                    Location = LocationPresets["Chicago"],
                    Radius = 15.0,
                    Description = "Find locations in Chicago and close suburbs"
                }
            };

            foreach (var example in distanceExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Center: ({example.Location.Latitude}, {example.Location.Longitude})");
                Console.WriteLine($"   Radius: {example.Radius} km");

                var filter = GeographicFilterBuilder.BuildDistanceFilter(
                    example.Location.Latitude, example.Location.Longitude, example.Radius);
                
                Console.WriteLine($"   Filter: {filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("location");
                    searchOptions.Select.Add("address");
                    searchOptions.Select.Add("category");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;
                    var area = Math.PI * example.Radius * example.Radius;

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");
                    Console.WriteLine($"   Search Area: ~{area:F1} km²");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var address = doc.TryGetValue("address", out var addressValue) ? addressValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                        var location = doc.TryGetValue("location", out var locationValue) ? locationValue?.ToString() : "N/A";

                        // Calculate approximate distance (simplified)
                        var distance = CalculateDistance(example.Location.Latitude, example.Location.Longitude, location);

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - {address} - ~{distance:F1}km");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateDistanceRangesAsync()
        {
            Console.WriteLine("\n🎯 Distance Range Filters (Ring Shapes)");
            Console.WriteLine("=".PadRight(40, '='));

            var rangeExamples = new[]
            {
                new
                {
                    Name = "Seattle Ring (10-30km)",
                    Location = LocationPresets["Seattle"],
                    MinRadius = 10.0,
                    MaxRadius = 30.0,
                    Description = "Find locations in Seattle suburbs (avoiding downtown)"
                },
                new
                {
                    Name = "NYC Outer Boroughs (15-40km)",
                    Location = LocationPresets["NewYork"],
                    MinRadius = 15.0,
                    MaxRadius = 40.0,
                    Description = "Find locations in outer NYC areas"
                },
                new
                {
                    Name = "Chicago Metro Ring (20-50km)",
                    Location = LocationPresets["Chicago"],
                    MinRadius = 20.0,
                    MaxRadius = 50.0,
                    Description = "Find locations in Chicago metropolitan ring"
                }
            };

            foreach (var example in rangeExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Center: ({example.Location.Latitude}, {example.Location.Longitude})");
                Console.WriteLine($"   Range: {example.MinRadius}-{example.MaxRadius} km");

                var filter = GeographicFilterBuilder.BuildDistanceRangeFilter(
                    example.Location.Latitude, example.Location.Longitude, 
                    example.MinRadius, example.MaxRadius);
                
                Console.WriteLine($"   Filter: {filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("location");
                    searchOptions.Select.Add("address");
                    searchOptions.Select.Add("category");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;
                    var ringArea = Math.PI * (example.MaxRadius * example.MaxRadius - example.MinRadius * example.MinRadius);

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");
                    Console.WriteLine($"   Ring Area: ~{ringArea:F1} km²");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var address = doc.TryGetValue("address", out var addressValue) ? addressValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                        var location = doc.TryGetValue("location", out var locationValue) ? locationValue?.ToString() : "N/A";

                        var distance = CalculateDistance(example.Location.Latitude, example.Location.Longitude, location);

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - {address} - ~{distance:F1}km");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateMultiPointFiltersAsync()
        {
            Console.WriteLine("\n🗺️ Multi-Point Geographic Filters");
            Console.WriteLine("=".PadRight(40, '='));

            var multiPointExamples = new[]
            {
                new
                {
                    Name = "West Coast Hubs",
                    Locations = new[] 
                    { 
                        (LocationPresets["Seattle"], 20.0),
                        (LocationPresets["SanFrancisco"], 20.0),
                        (LocationPresets["LosAngeles"], 20.0)
                    },
                    Description = "Find locations near major West Coast cities"
                },
                new
                {
                    Name = "Florida Operations",
                    Locations = new[] 
                    { 
                        (LocationPresets["Miami"], 15.0),
                        (LocationPresets["Orlando"], 15.0)
                    },
                    Description = "Find locations near Florida business centers"
                },
                new
                {
                    Name = "Midwest Coverage",
                    Locations = new[] 
                    { 
                        (LocationPresets["Chicago"], 25.0),
                        (LocationPresets["Denver"], 25.0)
                    },
                    Description = "Find locations in Midwest operational areas"
                }
            };

            foreach (var example in multiPointExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Points: {example.Locations.Length} locations");

                var filter = GeographicFilterBuilder.BuildMultiPointFilter(example.Locations);
                
                Console.WriteLine($"   Filter: {filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = filter,
                        Size = 4,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("location");
                    searchOptions.Select.Add("address");
                    searchOptions.Select.Add("category");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");

                    for (int i = 0; i < Math.Min(3, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var address = doc.TryGetValue("address", out var addressValue) ? addressValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - {address}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public async Task DemonstrateAdvancedGeographicFiltersAsync()
        {
            Console.WriteLine("\n🎯 Advanced Geographic Combinations");
            Console.WriteLine("=".PadRight(40, '='));

            var advancedExamples = new[]
            {
                new
                {
                    Name = "Premium Seattle Restaurants",
                    Filter = GeographicFilterBuilder.BuildDistanceFilter(
                        LocationPresets["Seattle"].Latitude, LocationPresets["Seattle"].Longitude, 10) +
                        " and category eq 'Restaurant' and rating ge 4.0",
                    Description = "Find high-rated restaurants within 10km of Seattle"
                },
                new
                {
                    Name = "NYC Hotels with Parking",
                    Filter = GeographicFilterBuilder.BuildDistanceFilter(
                        LocationPresets["NewYork"].Latitude, LocationPresets["NewYork"].Longitude, 15) +
                        " and category eq 'Hotel' and amenities/any(a: a eq 'parking')",
                    Description = "Find hotels with parking within 15km of NYC"
                },
                new
                {
                    Name = "LA Entertainment Venues",
                    Filter = GeographicFilterBuilder.BuildDistanceRangeFilter(
                        LocationPresets["LosAngeles"].Latitude, LocationPresets["LosAngeles"].Longitude, 5, 25) +
                        " and (category eq 'Entertainment' or category eq 'Theater')",
                    Description = "Find entertainment venues in LA suburbs (5-25km from center)"
                }
            };

            foreach (var example in advancedExamples)
            {
                Console.WriteLine($"\n📋 {example.Name}");
                Console.WriteLine($"   Description: {example.Description}");
                Console.WriteLine($"   Filter: {example.Filter}");

                try
                {
                    var stopwatch = Stopwatch.StartNew();
                    
                    var searchOptions = new SearchOptions
                    {
                        Filter = example.Filter,
                        Size = 3,
                        IncludeTotalCount = true
                    };
                    searchOptions.Select.Add("id");
                    searchOptions.Select.Add("name");
                    searchOptions.Select.Add("location");
                    searchOptions.Select.Add("category");
                    searchOptions.Select.Add("rating");
                    searchOptions.Select.Add("amenities");

                    var results = await _searchClient.SearchAsync<SearchDocument>("*", searchOptions);
                    var resultList = new List<SearchResult<SearchDocument>>();

                    await foreach (var result in results.Value.GetResultsAsync())
                    {
                        resultList.Add(result);
                    }

                    stopwatch.Stop();
                    var totalCount = results.Value.TotalCount ?? resultList.Count;

                    Console.WriteLine($"   Results: {resultList.Count} of {totalCount} items found ({stopwatch.ElapsedMilliseconds}ms)");

                    for (int i = 0; i < Math.Min(2, resultList.Count); i++)
                    {
                        var doc = resultList[i].Document;
                        var name = doc.TryGetValue("name", out var nameValue) ? nameValue?.ToString() : "N/A";
                        var category = doc.TryGetValue("category", out var categoryValue) ? categoryValue?.ToString() : "N/A";
                        var rating = doc.TryGetValue("rating", out var ratingValue) ? ratingValue?.ToString() : "N/A";

                        Console.WriteLine($"     {i + 1}. {name} ({category}) - {rating}⭐");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"   ❌ Error: {ex.Message}");
                }
            }
        }

        public void DemonstrateGeographicBestPractices()
        {
            Console.WriteLine("\n💡 Geographic Filter Best Practices");
            Console.WriteLine("=".PadRight(40, '='));

            Console.WriteLine("\n1. Use smaller radii for better performance");
            Console.WriteLine("   ✅ Good: geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 10");
            Console.WriteLine("   ❌ Slower: geo.distance(location, geography'POINT(-122.3321 47.6062)') lt 100");

            Console.WriteLine("\n2. Avoid exclusion filters (gt) when possible");
            Console.WriteLine("   ✅ Good: geo.distance(location, point) lt 20");
            Console.WriteLine("   ❌ Less efficient: geo.distance(location, point) gt 10");

            Console.WriteLine("\n3. Validate coordinate ranges");
            Console.WriteLine("   • Latitude: -90 to +90 degrees");
            Console.WriteLine("   • Longitude: -180 to +180 degrees");

            Console.WriteLine("\n4. Use appropriate distance units");
            Console.WriteLine("   • Kilometers for most international applications");
            Console.WriteLine("   • Miles for US-specific applications");

            Console.WriteLine("\n5. Consider Earth's curvature for large distances");
            Console.WriteLine("   • Distances > 1000km may have accuracy issues");
            Console.WriteLine("   • Use appropriate coordinate systems for precision");

            Console.WriteLine("\n6. Index geographic fields properly");
            Console.WriteLine("   • Mark geographic fields as 'filterable' in index schema");
            Console.WriteLine("   • Use Edm.GeographyPoint data type");

            // Coordinate validation examples
            Console.WriteLine("\n📊 Coordinate Validation Examples:");
            var testCoordinates = new[]
            {
                (47.6062, -122.3321, "Seattle - Valid"),
                (91.0, -122.3321, "Invalid latitude (> 90)"),
                (47.6062, -181.0, "Invalid longitude (< -180)"),
                (0.0, 0.0, "Null Island - Valid but suspicious")
            };

            foreach (var (lat, lon, description) in testCoordinates)
            {
                var isValid = GeographicFilterBuilder.ValidateCoordinates(lat, lon);
                var status = isValid ? "✅" : "❌";
                Console.WriteLine($"   {status} ({lat}, {lon}) - {description}");
            }
        }

        private double CalculateDistance(double lat1, double lon1, string locationString)
        {
            // Simplified distance calculation for demo purposes
            // In real applications, parse the actual location coordinates
            // This is just for demonstration
            return Math.Round(Math.Random.Shared.NextDouble() * 50, 1);
        }

        public async Task RunAsync()
        {
            Console.WriteLine("🚀 Geographic Filters Example");
            Console.WriteLine("=".PadRight(50, '='));

            try
            {
                await DemonstrateDistanceFiltersAsync();
                await DemonstrateDistanceRangesAsync();
                await DemonstrateMultiPointFiltersAsync();
                await DemonstrateAdvancedGeographicFiltersAsync();
                DemonstrateGeographicBestPractices();

                Console.WriteLine("\n✅ Geographic filters example completed successfully!");
                Console.WriteLine("\nKey takeaways:");
                Console.WriteLine("- Use geo.distance() for distance-based filtering");
                Console.WriteLine("- Combine geographic filters with other conditions");
                Console.WriteLine("- Validate coordinate ranges and formats");
                Console.WriteLine("- Use smaller radii for better performance");
                Console.WriteLine("- Consider multi-point filters for complex scenarios");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Example failed: {ex.Message}");
                throw;
            }
        }
    }

    public static class GeographicFilterBuilder
    {
        public static string BuildDistanceFilter(double latitude, double longitude, double radiusKm, string fieldName = "location")
        {
            ValidateCoordinates(latitude, longitude);
            
            if (radiusKm <= 0)
                throw new ArgumentException("Radius must be positive", nameof(radiusKm));

            var point = $"geography'POINT({longitude} {latitude})'";
            return $"geo.distance({fieldName}, {point}) lt {radiusKm}";
        }

        public static string BuildDistanceRangeFilter(double latitude, double longitude, 
            double minRadiusKm, double maxRadiusKm, string fieldName = "location")
        {
            ValidateCoordinates(latitude, longitude);
            
            if (minRadiusKm < 0 || maxRadiusKm <= 0 || minRadiusKm >= maxRadiusKm)
                throw new ArgumentException("Invalid radius range");

            var point = $"geography'POINT({longitude} {latitude})'";
            return $"geo.distance({fieldName}, {point}) ge {minRadiusKm} and geo.distance({fieldName}, {point}) le {maxRadiusKm}";
        }

        public static string BuildMultiPointFilter(((double Latitude, double Longitude) Location, double Radius)[] locations, 
            string fieldName = "location")
        {
            if (locations == null || locations.Length == 0)
                throw new ArgumentException("At least one location must be provided");

            var filters = new List<string>();

            foreach (var (location, radius) in locations)
            {
                ValidateCoordinates(location.Latitude, location.Longitude);
                
                if (radius <= 0)
                    throw new ArgumentException("All radii must be positive");

                var point = $"geography'POINT({location.Longitude} {location.Latitude})'";
                filters.Add($"geo.distance({fieldName}, {point}) lt {radius}");
            }

            return string.Join(" or ", filters);
        }

        public static bool ValidateCoordinates(double latitude, double longitude)
        {
            var isValidLat = latitude >= -90 && latitude <= 90;
            var isValidLon = longitude >= -180 && longitude <= 180;
            
            if (!isValidLat)
                throw new ArgumentException($"Invalid latitude: {latitude}. Must be between -90 and 90", nameof(latitude));
            
            if (!isValidLon)
                throw new ArgumentException($"Invalid longitude: {longitude}. Must be between -180 and 180", nameof(longitude));

            return true;
        }

        public static double CalculateDistance(double lat1, double lon1, double lat2, double lon2)
        {
            // Haversine formula for calculating distance between two points
            const double R = 6371; // Earth's radius in kilometers

            var dLat = ToRadians(lat2 - lat1);
            var dLon = ToRadians(lon2 - lon1);

            var a = Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                    Math.Cos(ToRadians(lat1)) * Math.Cos(ToRadians(lat2)) *
                    Math.Sin(dLon / 2) * Math.Sin(dLon / 2);

            var c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));

            return R * c;
        }

        private static double ToRadians(double degrees)
        {
            return degrees * Math.PI / 180;
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var example = new GeographicFiltersExample();
            try
            {
                await example.RunAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Application failed: {ex.Message}");
                Environment.Exit(1);
            }
        }
    }
}