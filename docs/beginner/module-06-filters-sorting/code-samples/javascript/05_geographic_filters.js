/**
 * Geographic Filters Example
 * 
 * This example demonstrates geographic filtering operations in Azure AI Search,
 * including distance-based filtering, bounding box filtering, and polygon intersection.
 */

const { SearchClient, AzureKeyCredential } = require('@azure/search-documents');
require('dotenv').config();

class GeographicFiltersExample {
    constructor() {
        this.validateConfiguration();
        
        // Initialize search client
        const credential = new AzureKeyCredential(process.env.SEARCH_API_KEY);
        this.searchClient = new SearchClient(
            process.env.SEARCH_ENDPOINT,
            process.env.INDEX_NAME,
            credential
        );
        
        // Common reference points
        this.referencePoints = {
            seattle: { lat: 47.608013, lon: -122.335167, name: 'Seattle, WA' },
            sanFrancisco: { lat: 37.774929, lon: -122.419416, name: 'San Francisco, CA' },
            newYork: { lat: 40.712776, lon: -74.005974, name: 'New York, NY' },
            london: { lat: 51.507351, lon: -0.127758, name: 'London, UK' },
            tokyo: { lat: 35.676676, lon: 139.650344, name: 'Tokyo, Japan' }
        };
    }

    validateConfiguration() {
        const requiredVars = ['SEARCH_ENDPOINT', 'SEARCH_API_KEY', 'INDEX_NAME'];
        const missingVars = requiredVars.filter(varName => !process.env[varName]);
        
        if (missingVars.length > 0) {
            throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
        }
        
        console.log('✅ Configuration validated');
        console.log(`📍 Search Endpoint: ${process.env.SEARCH_ENDPOINT}`);
        console.log(`📊 Index Name: ${process.env.INDEX_NAME}`);
    }

    formatPoint(lat, lon) {
        /**
         * Format coordinates as OData geography point
         * @param {number} lat - Latitude
         * @param {number} lon - Longitude
         * @returns {string} Formatted geography point
         */
        return `geography'POINT(${lon} ${lat})'`;
    }

    async demonstrateDistanceFilters() {
        console.log('\n📍 Distance-Based Filters');
        console.log('='.repeat(40));
        
        const seattle = this.referencePoints.seattle;
        const seattlePoint = this.formatPoint(seattle.lat, seattle.lon);
        
        const distanceExamples = [
            {
                name: 'Within 10km of Seattle',
                filter: `geo.distance(location, ${seattlePoint}) le 10`,
                description: 'Find items within 10 kilometers of Seattle'
            },
            {
                name: 'Within 50km of Seattle',
                filter: `geo.distance(location, ${seattlePoint}) le 50`,
                description: 'Find items within 50 kilometers of Seattle'
            },
            {
                name: 'More than 100km from Seattle',
                filter: `geo.distance(location, ${seattlePoint}) gt 100`,
                description: 'Find items more than 100km away from Seattle'
            },
            {
                name: 'Between 20-50km from Seattle',
                filter: `geo.distance(location, ${seattlePoint}) gt 20 and geo.distance(location, ${seattlePoint}) le 50`,
                description: 'Find items in a ring around Seattle'
            }
        ];

        for (const example of distanceExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            console.log(`   Reference: ${seattle.name} (${seattle.lat}, ${seattle.lon})`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'location', 'category'],
                    orderBy: [`geo.distance(location, ${seattlePoint})`]
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const location = result.location ? 
                        `${result.location.coordinates[1]}, ${result.location.coordinates[0]}` : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Location: ${location}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateMultipleLocationFilters() {
        console.log('\n🌍 Multiple Location Filters');
        console.log('='.repeat(40));
        
        const seattle = this.referencePoints.seattle;
        const sanFrancisco = this.referencePoints.sanFrancisco;
        const seattlePoint = this.formatPoint(seattle.lat, seattle.lon);
        const sfPoint = this.formatPoint(sanFrancisco.lat, sanFrancisco.lon);
        
        const multiLocationExamples = [
            {
                name: 'Near Seattle OR San Francisco',
                filter: `geo.distance(location, ${seattlePoint}) le 50 or geo.distance(location, ${sfPoint}) le 50`,
                description: 'Find items within 50km of either Seattle or San Francisco'
            },
            {
                name: 'Close to both Seattle AND San Francisco',
                filter: `geo.distance(location, ${seattlePoint}) le 200 and geo.distance(location, ${sfPoint}) le 200`,
                description: 'Find items within 200km of both cities (unlikely but possible)'
            },
            {
                name: 'Closer to Seattle than San Francisco',
                filter: `geo.distance(location, ${seattlePoint}) lt geo.distance(location, ${sfPoint})`,
                description: 'Find items closer to Seattle than to San Francisco'
            }
        ];

        for (const example of multiLocationExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'location', 'category'],
                    orderBy: [`geo.distance(location, ${seattlePoint})`]
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const location = result.location ? 
                        `${result.location.coordinates[1]}, ${result.location.coordinates[0]}` : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Location: ${location}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstratePolygonFilters() {
        console.log('\n🔷 Polygon Intersection Filters');
        console.log('='.repeat(40));
        
        // Define a polygon around Seattle area (simplified rectangle)
        const seattleAreaPolygon = `geography'POLYGON((-122.5 47.4, -122.5 47.8, -122.1 47.8, -122.1 47.4, -122.5 47.4))'`;
        
        // Define a polygon around San Francisco Bay Area
        const bayAreaPolygon = `geography'POLYGON((-122.6 37.3, -122.6 38.0, -121.8 38.0, -121.8 37.3, -122.6 37.3))'`;
        
        const polygonExamples = [
            {
                name: 'Items in Seattle area polygon',
                filter: `geo.intersects(location, ${seattleAreaPolygon})`,
                description: 'Find items within the Seattle metropolitan area'
            },
            {
                name: 'Items in Bay Area polygon',
                filter: `geo.intersects(location, ${bayAreaPolygon})`,
                description: 'Find items within the San Francisco Bay Area'
            },
            {
                name: 'Items in either metropolitan area',
                filter: `geo.intersects(location, ${seattleAreaPolygon}) or geo.intersects(location, ${bayAreaPolygon})`,
                description: 'Find items in either Seattle or Bay Area'
            }
        ];

        for (const example of polygonExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'location', 'category']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const location = result.location ? 
                        `${result.location.coordinates[1]}, ${result.location.coordinates[0]}` : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Location: ${location}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    async demonstrateGeographicWithOtherFilters() {
        console.log('\n🔗 Geographic Filters Combined with Other Filters');
        console.log('='.repeat(40));
        
        const seattle = this.referencePoints.seattle;
        const seattlePoint = this.formatPoint(seattle.lat, seattle.lon);
        
        const combinedFilterExamples = [
            {
                name: 'Electronics near Seattle',
                filter: `category eq 'Electronics' and geo.distance(location, ${seattlePoint}) le 25`,
                description: 'Find electronics within 25km of Seattle'
            },
            {
                name: 'High-priced items near Seattle',
                filter: `price gt 500 and geo.distance(location, ${seattlePoint}) le 50`,
                description: 'Find expensive items within 50km of Seattle'
            },
            {
                name: 'Apple stores near Seattle',
                filter: `brand eq 'Apple' and category eq 'Store' and geo.distance(location, ${seattlePoint}) le 100`,
                description: 'Find Apple stores within 100km of Seattle'
            },
            {
                name: 'Recent items near Seattle',
                filter: `lastModified ge ${new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()} and geo.distance(location, ${seattlePoint}) le 30`,
                description: 'Find recently updated items within 30km of Seattle'
            }
        ];

        for (const example of combinedFilterExamples) {
            console.log(`\n📋 ${example.name}`);
            console.log(`   Description: ${example.description}`);
            console.log(`   Filter: ${example.filter}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: example.filter,
                    top: 3,
                    select: ['id', 'name', 'category', 'brand', 'price', 'location', 'lastModified'],
                    orderBy: [`geo.distance(location, ${seattlePoint})`]
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.slice(0, 2).forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const brand = result.brand || 'N/A';
                    const price = result.price || 'N/A';
                    const location = result.location ? 
                        `${result.location.coordinates[1]}, ${result.location.coordinates[0]}` : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - ${brand} - $${price}`);
                    console.log(`        Location: ${location}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    buildDistanceFilter(field, centerLat, centerLon, maxDistanceKm, minDistanceKm = null) {
        /**
         * Build a distance-based filter
         * @param {string} field - Location field name
         * @param {number} centerLat - Center latitude
         * @param {number} centerLon - Center longitude
         * @param {number} maxDistanceKm - Maximum distance in kilometers
         * @param {number} minDistanceKm - Minimum distance in kilometers (optional)
         * @returns {string} Filter expression
         */
        const centerPoint = this.formatPoint(centerLat, centerLon);
        const filters = [];
        
        if (minDistanceKm !== null) {
            filters.push(`geo.distance(${field}, ${centerPoint}) gt ${minDistanceKm}`);
        }
        
        filters.push(`geo.distance(${field}, ${centerPoint}) le ${maxDistanceKm}`);
        
        return filters.join(' and ');
    }

    buildBoundingBoxFilter(field, northLat, southLat, eastLon, westLon) {
        /**
         * Build a bounding box filter using polygon
         * @param {string} field - Location field name
         * @param {number} northLat - Northern boundary
         * @param {number} southLat - Southern boundary
         * @param {number} eastLon - Eastern boundary
         * @param {number} westLon - Western boundary
         * @returns {string} Filter expression
         */
        const polygon = `geography'POLYGON((${westLon} ${southLat}, ${westLon} ${northLat}, ${eastLon} ${northLat}, ${eastLon} ${southLat}, ${westLon} ${southLat}))'`;
        return `geo.intersects(${field}, ${polygon})`;
    }

    async demonstrateDynamicGeographicFiltering() {
        console.log('\n🏗️ Dynamic Geographic Filter Building');
        console.log('='.repeat(40));
        
        const geoScenarios = [
            {
                name: 'Distance filter around Seattle',
                type: 'distance',
                centerLat: 47.608013,
                centerLon: -122.335167,
                maxDistance: 25,
                description: 'Items within 25km of Seattle'
            },
            {
                name: 'Ring around San Francisco',
                type: 'distance',
                centerLat: 37.774929,
                centerLon: -122.419416,
                maxDistance: 50,
                minDistance: 10,
                description: 'Items 10-50km from San Francisco'
            },
            {
                name: 'Pacific Northwest bounding box',
                type: 'boundingBox',
                northLat: 49.0,
                southLat: 45.0,
                eastLon: -116.0,
                westLon: -125.0,
                description: 'Items in Pacific Northwest region'
            },
            {
                name: 'California bounding box',
                type: 'boundingBox',
                northLat: 42.0,
                southLat: 32.5,
                eastLon: -114.0,
                westLon: -124.5,
                description: 'Items in California'
            }
        ];

        for (const scenario of geoScenarios) {
            console.log(`\n📋 ${scenario.name}`);
            
            let filter;
            if (scenario.type === 'distance') {
                filter = this.buildDistanceFilter(
                    'location',
                    scenario.centerLat,
                    scenario.centerLon,
                    scenario.maxDistance,
                    scenario.minDistance
                );
            } else if (scenario.type === 'boundingBox') {
                filter = this.buildBoundingBoxFilter(
                    'location',
                    scenario.northLat,
                    scenario.southLat,
                    scenario.eastLon,
                    scenario.westLon
                );
            }
            
            console.log(`   Generated Filter: ${filter}`);
            console.log(`   Description: ${scenario.description}`);
            
            try {
                const searchResults = await this.searchClient.search('*', {
                    filter: filter,
                    top: 2,
                    select: ['id', 'name', 'location', 'category']
                });

                const results = [];
                for await (const result of searchResults.results) {
                    results.push(result.document);
                }

                console.log(`   Results: ${results.length} items found`);
                
                results.forEach((result, index) => {
                    const name = result.name || 'N/A';
                    const category = result.category || 'N/A';
                    const location = result.location ? 
                        `${result.location.coordinates[1]}, ${result.location.coordinates[0]}` : 'N/A';
                    console.log(`     ${index + 1}. ${name} (${category}) - Location: ${location}`);
                });
                
            } catch (error) {
                console.log(`   ❌ Error: ${error.message}`);
            }
        }
    }

    demonstrateGeographicFilterBestPractices() {
        console.log('\n💡 Geographic Filter Best Practices');
        console.log('='.repeat(40));
        
        console.log('\n1. Coordinate Format');
        console.log('   ✅ Use geography\'POINT(longitude latitude)\' format');
        console.log('   ✅ Longitude comes first, then latitude');
        console.log('   ✅ Use decimal degrees (not degrees/minutes/seconds)');
        console.log('   ❌ Don\'t confuse latitude and longitude order');
        
        console.log('\n2. Distance Calculations');
        console.log('   ✅ Distances are calculated in kilometers by default');
        console.log('   ✅ Use appropriate distance ranges for your use case');
        console.log('   ✅ Consider Earth\'s curvature for large distances');
        console.log('   ⚠️ Very large distances may be less accurate');
        
        console.log('\n3. Polygon Definitions');
        console.log('   ✅ Define polygons in counterclockwise order');
        console.log('   ✅ Close polygons (first point = last point)');
        console.log('   ✅ Keep polygons simple for better performance');
        console.log('   ❌ Avoid self-intersecting polygons');
        
        console.log('\n4. Performance Optimization');
        console.log('   ✅ Use distance filters before other complex filters');
        console.log('   ✅ Combine geographic filters with selective filters');
        console.log('   ✅ Use appropriate distance ranges (not too large)');
        console.log('   ❌ Avoid multiple complex geographic calculations');
        
        console.log('\n5. Common Geographic Patterns');
        console.log('   📍 Nearby: geo.distance(location, point) le 10');
        console.log('   📍 Ring: distance gt 5 and distance le 20');
        console.log('   📍 Region: geo.intersects(location, polygon)');
        console.log('   📍 Closest: orderby geo.distance(location, point)');
        console.log('   📍 Multiple: distance1 le 50 or distance2 le 50');
        
        console.log('\n6. Data Quality Considerations');
        console.log('   ✅ Validate coordinate ranges (-90 to 90 lat, -180 to 180 lon)');
        console.log('   ✅ Handle null location values appropriately');
        console.log('   ✅ Consider coordinate precision needs');
        console.log('   ✅ Test with edge cases (poles, date line)');
        
        console.log('\n7. User Experience Tips');
        console.log('   ✅ Provide distance units in UI (km/miles)');
        console.log('   ✅ Show distance in search results');
        console.log('   ✅ Allow users to adjust search radius');
        console.log('   ✅ Provide map visualization when possible');
    }

    async run() {
        console.log('🚀 Geographic Filters Example');
        console.log('='.repeat(50));
        
        try {
            await this.demonstrateDistanceFilters();
            await this.demonstrateMultipleLocationFilters();
            await this.demonstratePolygonFilters();
            await this.demonstrateGeographicWithOtherFilters();
            await this.demonstrateDynamicGeographicFiltering();
            this.demonstrateGeographicFilterBestPractices();
            
            console.log('\n✅ Geographic filters example completed successfully!');
            console.log('\nKey takeaways:');
            console.log('- Use geo.distance() for radius-based filtering');
            console.log('- Use geo.intersects() for polygon-based filtering');
            console.log('- Remember longitude comes before latitude in POINT format');
            console.log('- Combine geographic filters with other criteria for precision');
            console.log('- Consider performance implications of complex geographic queries');
            console.log('- Validate coordinate data and handle edge cases properly');
            
        } catch (error) {
            console.log(`\n❌ Example failed: ${error.message}`);
            throw error;
        }
    }
}

async function main() {
    const example = new GeographicFiltersExample();
    try {
        await example.run();
    } catch (error) {
        console.error(`Application failed: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = GeographicFiltersExample;