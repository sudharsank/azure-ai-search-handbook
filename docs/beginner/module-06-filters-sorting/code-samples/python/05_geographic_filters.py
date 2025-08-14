#!/usr/bin/env python3
"""
Azure AI Search - Geographic Filters

This script demonstrates geographic filtering operations using Azure AI Search,
including distance-based filtering, geographic bounds, and spatial queries.

Key Features:
- Distance-based filtering with geo.distance()
- Geographic bounds and regions
- Location data analysis
- Spatial query optimization
- Coordinate system handling

Prerequisites:
- Azure AI Search service configured
- Sample data with geographic fields (Edm.GeographyPoint)
- Environment variables set in .env file
"""

import os
import math
import time
from typing import List, Dict, Tuple, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeographicFilterManager:
    """Manages geographic filtering operations for Azure AI Search."""
    
    def __init__(self):
        """Initialize the geographic filter manager."""
        self.search_client = self._initialize_client()
        self.location_presets = {
            'seattle': (47.6062, -122.3321),
            'new_york': (40.7128, -74.0060),
            'los_angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'miami': (25.7617, -80.1918),
            'orlando': (28.5383, -81.3792)
        }
    
    def _initialize_client(self) -> SearchClient:
        """Initialize Azure AI Search client."""
        try:
            endpoint = os.getenv('SEARCH_ENDPOINT')
            api_key = os.getenv('SEARCH_API_KEY')
            index_name = os.getenv('INDEX_NAME')
            
            if not all([endpoint, api_key, index_name]):
                raise ValueError("Missing required environment variables")
            
            credential = AzureKeyCredential(api_key)
            client = SearchClient(endpoint, index_name, credential)
            
            print(f"✅ Connected to Azure AI Search")
            print(f"📍 Endpoint: {endpoint}")
            print(f"📊 Index: {index_name}")
            
            return client
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            raise
    
    def build_distance_filter(self, latitude: float, longitude: float, 
                            radius: float, field_name: str = 'location') -> str:
        """
        Build a distance-based geographic filter.
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius: Search radius in kilometers
            field_name: Name of the geographic field
            
        Returns:
            OData filter expression
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180")
        if radius <= 0:
            raise ValueError(f"Invalid radius: {radius}. Must be positive")
        
        point = f"geography'POINT({longitude} {latitude})'"
        return f"geo.distance({field_name}, {point}) lt {radius}"
    
    def build_distance_range_filter(self, latitude: float, longitude: float,
                                  min_radius: float, max_radius: float,
                                  field_name: str = 'location') -> str:
        """
        Build a distance range filter (ring shape).
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            min_radius: Minimum distance in kilometers
            max_radius: Maximum distance in kilometers
            field_name: Name of the geographic field
            
        Returns:
            OData filter expression
        """
        if min_radius >= max_radius:
            raise ValueError("min_radius must be less than max_radius")
        
        point = f"geography'POINT({longitude} {latitude})'"
        return (f"geo.distance({field_name}, {point}) ge {min_radius} and "
                f"geo.distance({field_name}, {point}) le {max_radius}")
    
    def build_multi_point_filter(self, locations: List[Tuple[float, float, float]],
                               field_name: str = 'location') -> str:
        """
        Build a filter for multiple location points (OR condition).
        
        Args:
            locations: List of (latitude, longitude, radius) tuples
            field_name: Name of the geographic field
            
        Returns:
            OData filter expression
        """
        if not locations:
            raise ValueError("At least one location must be provided")
        
        filters = []
        for lat, lon, radius in locations:
            point = f"geography'POINT({lon} {lat})'"
            filters.append(f"geo.distance({field_name}, {point}) lt {radius}")
        
        return " or ".join(filters)
    
    def calculate_area(self, radius: float) -> float:
        """Calculate approximate area of a circular search region."""
        return math.pi * radius ** 2
    
    def calculate_distance(self, lat1: float, lon1: float, 
                         lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        return c * r
    
    def search_by_location(self, latitude: float, longitude: float, 
                          radius: float, search_text: str = "*",
                          top: int = 10) -> Dict:
        """
        Execute a geographic search query.
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius: Search radius in kilometers
            search_text: Search query text
            top: Number of results to return
            
        Returns:
            Search results dictionary
        """
        try:
            filter_expr = self.build_distance_filter(latitude, longitude, radius)
            
            print(f"🔍 Executing geographic search...")
            print(f"   Filter: {filter_expr}")
            print(f"   Center: ({latitude}, {longitude})")
            print(f"   Radius: {radius} km")
            print(f"   Area: ~{self.calculate_area(radius):.1f} km²")
            
            start_time = time.time()
            
            results = self.search_client.search(
                search_text=search_text,
                filter=filter_expr,
                top=top,
                include_total_count=True
            )
            
            execution_time = time.time() - start_time
            
            # Process results
            documents = list(results)
            total_count = results.get_count()
            
            return {
                'documents': documents,
                'total_count': total_count,
                'execution_time': execution_time,
                'filter': filter_expr,
                'search_params': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius': radius,
                    'area_km2': self.calculate_area(radius)
                }
            }
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {'error': str(e)}
    
    def analyze_location_distribution(self, results: List[Dict]) -> Dict:
        """Analyze the geographic distribution of search results."""
        if not results:
            return {'error': 'No results to analyze'}
        
        locations = []
        for doc in results:
            if 'location' in doc and doc['location']:
                # Parse location (assuming it's in a standard format)
                locations.append(doc['location'])
        
        return {
            'total_locations': len(locations),
            'unique_locations': len(set(str(loc) for loc in locations)),
            'coverage_analysis': 'Geographic distribution analysis complete'
        }
    
    def demonstrate_geographic_filters(self):
        """Demonstrate various geographic filtering scenarios."""
        print("🌍 Geographic Filters Demonstration")
        print("=" * 50)
        
        examples = [
            {
                'name': 'Nearby Locations (5km)',
                'params': {'latitude': 47.6062, 'longitude': -122.3321, 'radius': 5},
                'description': 'Find locations within 5km of Seattle downtown'
            },
            {
                'name': 'City-wide Search (25km)',
                'params': {'latitude': 40.7128, 'longitude': -74.0060, 'radius': 25},
                'description': 'Find locations within 25km of NYC center'
            },
            {
                'name': 'Distance Range (Ring)',
                'params': {'latitude': 41.8781, 'longitude': -87.6298, 'min_radius': 10, 'max_radius': 30},
                'description': 'Find locations 10-30km from Chicago (ring shape)',
                'type': 'range'
            }
        ]
        
        for example in examples:
            print(f"\n📍 {example['name']}")
            print(f"   Description: {example['description']}")
            
            if example.get('type') == 'range':
                filter_expr = self.build_distance_range_filter(
                    example['params']['latitude'],
                    example['params']['longitude'],
                    example['params']['min_radius'],
                    example['params']['max_radius']
                )
            else:
                filter_expr = self.build_distance_filter(
                    example['params']['latitude'],
                    example['params']['longitude'],
                    example['params']['radius']
                )
            
            print(f"   Filter: {filter_expr}")
    
    def show_best_practices(self):
        """Display geographic filtering best practices."""
        print("\n🚀 Geographic Filter Best Practices:")
        print("=" * 40)
        
        practices = [
            "Use smaller radii for better performance and precision",
            "Avoid exclusion filters (gt) when possible - use inclusion (lt, le)",
            "Index geographic fields as 'filterable' with Edm.GeographyPoint type",
            "Consider coordinate accuracy for your use case",
            "Validate coordinate ranges: lat (-90 to +90), lon (-180 to +180)",
            "Use appropriate distance units (km for international, miles for US)",
            "Consider Earth's curvature for large distances",
            "Cache frequently used location queries"
        ]
        
        for i, practice in enumerate(practices, 1):
            print(f"{i}. {practice}")
    
    def performance_analysis(self, test_radii: List[float] = None):
        """Analyze performance of different search radii."""
        if test_radii is None:
            test_radii = [1, 5, 10, 25, 50, 100]
        
        print("\n⚡ Performance Analysis")
        print("=" * 30)
        
        # Use Seattle as test location
        test_lat, test_lon = self.location_presets['seattle']
        
        print(f"Test Location: Seattle ({test_lat}, {test_lon})")
        print(f"{'Radius (km)':<12} {'Area (km²)':<12} {'Performance':<15}")
        print("-" * 40)
        
        for radius in test_radii:
            area = self.calculate_area(radius)
            
            # Performance estimation based on area
            if area < 100:
                performance = "Excellent"
            elif area < 500:
                performance = "Good"
            elif area < 2000:
                performance = "Fair"
            else:
                performance = "Consider optimization"
            
            print(f"{radius:<12} {area:<12.1f} {performance:<15}")

def main():
    """Main demonstration function."""
    try:
        # Initialize the geographic filter manager
        geo_manager = GeographicFilterManager()
        
        # Demonstrate geographic filters
        geo_manager.demonstrate_geographic_filters()
        
        # Show best practices
        geo_manager.show_best_practices()
        
        # Performance analysis
        geo_manager.performance_analysis()
        
        # Example search (commented out to avoid actual API calls in demo)
        # results = geo_manager.search_by_location(47.6062, -122.3321, 10)
        # print(f"\n📊 Search Results: {results.get('total_count', 0)} documents found")
        
        print("\n✅ Geographic filters demonstration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()