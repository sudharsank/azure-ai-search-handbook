"""
Common Utility Functions
Shared utilities for code samples and exercises across all modules
"""

import os
import json
import time
import random
import string
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging


@dataclass
class SampleDocument:
    """Sample document structure for exercises"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_date: str
    rating: float
    metadata: Dict[str, Any]


class DataGenerator:
    """Generate sample data for exercises and demonstrations"""
    
    CATEGORIES = [
        "Technology", "Science", "Business", "Health", "Education",
        "Entertainment", "Sports", "Travel", "Food", "Art"
    ]
    
    TAGS = [
        "tutorial", "guide", "reference", "example", "advanced",
        "beginner", "intermediate", "best-practices", "tips", "troubleshooting"
    ]
    
    SAMPLE_TITLES = [
        "Getting Started with Azure AI Search",
        "Advanced Query Techniques",
        "Index Design Best Practices",
        "Performance Optimization Guide",
        "Security Configuration Tutorial",
        "Vector Search Implementation",
        "Faceted Navigation Setup",
        "Custom Scoring Profiles",
        "AI Enrichment Pipeline",
        "Production Deployment Guide"
    ]
    
    SAMPLE_CONTENT_TEMPLATES = [
        "This comprehensive guide covers {topic} in detail. Learn how to implement {feature} effectively in your Azure AI Search solution. Includes practical examples and best practices.",
        "Explore advanced {topic} techniques that will enhance your search experience. This tutorial provides step-by-step instructions for {feature} implementation.",
        "Master the art of {topic} with this detailed walkthrough. Discover how {feature} can improve your search relevance and user experience.",
        "A complete reference for {topic} implementation. This guide covers everything from basic setup to advanced {feature} configuration.",
        "Learn professional {topic} strategies used in production environments. Includes real-world examples of {feature} optimization."
    ]
    
    @classmethod
    def generate_sample_documents(cls, count: int = 100) -> List[SampleDocument]:
        """Generate a list of sample documents"""
        documents = []
        
        for i in range(count):
            doc_id = f"doc_{i+1:03d}"
            title = random.choice(cls.SAMPLE_TITLES)
            category = random.choice(cls.CATEGORIES)
            tags = random.sample(cls.TAGS, random.randint(2, 5))
            
            # Generate content
            topic = category.lower()
            feature = random.choice(["indexing", "querying", "filtering", "scoring", "analysis"])
            content_template = random.choice(cls.SAMPLE_CONTENT_TEMPLATES)
            content = content_template.format(topic=topic, feature=feature)
            
            # Generate metadata
            created_date = cls._random_date().isoformat()
            rating = round(random.uniform(1.0, 5.0), 1)
            
            metadata = {
                "author": f"Author {random.randint(1, 20)}",
                "word_count": random.randint(100, 2000),
                "language": "en",
                "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                "estimated_read_time": random.randint(2, 15)
            }
            
            document = SampleDocument(
                id=doc_id,
                title=f"{title} - Part {i+1}",
                content=content,
                category=category,
                tags=tags,
                created_date=created_date,
                rating=rating,
                metadata=metadata
            )
            
            documents.append(document)
        
        return documents
    
    @staticmethod
    def _random_date() -> datetime:
        """Generate a random date within the last year"""
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        return start_date + timedelta(days=random_days)
    
    @classmethod
    def save_sample_data(cls, documents: List[SampleDocument], file_path: str):
        """Save sample documents to JSON file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        data = [asdict(doc) for doc in documents]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(documents)} sample documents to {file_path}")
    
    @classmethod
    def load_sample_data(cls, file_path: str) -> List[SampleDocument]:
        """Load sample documents from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        documents = [SampleDocument(**doc_data) for doc_data in data]
        print(f"Loaded {len(documents)} sample documents from {file_path}")
        return documents


class ExerciseValidator:
    """Validate exercise solutions and provide feedback"""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for exercise validation"""
        logger = logging.getLogger("exercise_validator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def validate_search_results(self, results: List[Dict], expected_count: Optional[int] = None,
                              required_fields: Optional[List[str]] = None) -> bool:
        """Validate search results structure and content"""
        try:
            # Check if results is a list
            if not isinstance(results, list):
                self.logger.error("Results should be a list")
                return False
            
            # Check expected count
            if expected_count is not None and len(results) != expected_count:
                self.logger.error(f"Expected {expected_count} results, got {len(results)}")
                return False
            
            # Check required fields
            if required_fields and results:
                for result in results:
                    for field in required_fields:
                        if field not in result:
                            self.logger.error(f"Required field '{field}' missing from result")
                            return False
            
            self.logger.info(f"✅ Search results validation passed ({len(results)} results)")
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    def validate_index_schema(self, schema: Dict, required_fields: List[str]) -> bool:
        """Validate index schema structure"""
        try:
            if "fields" not in schema:
                self.logger.error("Schema must contain 'fields' property")
                return False
            
            field_names = [field.get("name") for field in schema["fields"]]
            
            for required_field in required_fields:
                if required_field not in field_names:
                    self.logger.error(f"Required field '{required_field}' missing from schema")
                    return False
            
            self.logger.info("✅ Index schema validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema validation error: {str(e)}")
            return False
    
    def validate_query_syntax(self, query: str, query_type: str = "simple") -> bool:
        """Validate query syntax (basic validation)"""
        try:
            if not query or not isinstance(query, str):
                self.logger.error("Query must be a non-empty string")
                return False
            
            # Basic syntax checks based on query type
            if query_type == "simple":
                # Simple query validation
                forbidden_chars = ["<", ">", "=", "(", ")", "{", "}"]
                if any(char in query for char in forbidden_chars):
                    self.logger.error("Simple query contains forbidden characters")
                    return False
            
            elif query_type == "full":
                # Full Lucene query validation (basic)
                if query.count("(") != query.count(")"):
                    self.logger.error("Unmatched parentheses in full query")
                    return False
            
            self.logger.info(f"✅ Query syntax validation passed ({query_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Query validation error: {str(e)}")
            return False


class PerformanceMonitor:
    """Monitor and measure performance of search operations"""
    
    def __init__(self):
        self.measurements = []
    
    def measure_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Measure the execution time of an operation"""
        start_time = time.time()
        
        try:
            result = operation_func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            measurement = {
                "operation": operation_name,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            self.measurements.append(measurement)
            print(f"⏱️  {operation_name}: {duration:.3f}s")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            measurement = {
                "operation": operation_name,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            
            self.measurements.append(measurement)
            print(f"❌ {operation_name}: Failed after {duration:.3f}s - {str(e)}")
            
            raise
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance measurements"""
        if not self.measurements:
            return {"message": "No measurements recorded"}
        
        successful_measurements = [m for m in self.measurements if m["success"]]
        failed_measurements = [m for m in self.measurements if not m["success"]]
        
        if successful_measurements:
            durations = [m["duration_seconds"] for m in successful_measurements]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
        else:
            avg_duration = min_duration = max_duration = 0
        
        return {
            "total_operations": len(self.measurements),
            "successful_operations": len(successful_measurements),
            "failed_operations": len(failed_measurements),
            "average_duration": avg_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "measurements": self.measurements
        }
    
    def save_measurements(self, file_path: str):
        """Save performance measurements to file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        summary = self.get_performance_summary()
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Performance measurements saved to {file_path}")


class ConfigurationHelper:
    """Helper functions for configuration management"""
    
    @staticmethod
    def create_index_schema_template(index_name: str, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a basic index schema template"""
        return {
            "name": index_name,
            "fields": fields,
            "suggesters": [
                {
                    "name": "sg",
                    "searchMode": "analyzingInfixMatching",
                    "sourceFields": ["title", "content"]
                }
            ],
            "corsOptions": {
                "allowedOrigins": ["*"],
                "maxAgeInSeconds": 300
            }
        }
    
    @staticmethod
    def create_basic_field_definitions() -> List[Dict[str, Any]]:
        """Create basic field definitions for common use cases"""
        return [
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "searchable": False,
                "filterable": True,
                "retrievable": True
            },
            {
                "name": "title",
                "type": "Edm.String",
                "searchable": True,
                "filterable": True,
                "retrievable": True,
                "sortable": True,
                "analyzer": "standard.lucene"
            },
            {
                "name": "content",
                "type": "Edm.String",
                "searchable": True,
                "filterable": False,
                "retrievable": True,
                "analyzer": "standard.lucene"
            },
            {
                "name": "category",
                "type": "Edm.String",
                "searchable": True,
                "filterable": True,
                "retrievable": True,
                "facetable": True
            },
            {
                "name": "tags",
                "type": "Collection(Edm.String)",
                "searchable": True,
                "filterable": True,
                "retrievable": True,
                "facetable": True
            },
            {
                "name": "created_date",
                "type": "Edm.DateTimeOffset",
                "filterable": True,
                "retrievable": True,
                "sortable": True,
                "facetable": True
            },
            {
                "name": "rating",
                "type": "Edm.Double",
                "filterable": True,
                "retrievable": True,
                "sortable": True,
                "facetable": True
            }
        ]
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """Generate a random string for unique identifiers"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


# Convenience functions for common operations
def setup_sample_environment(data_file: str = "data/sample_documents.json", 
                           document_count: int = 100):
    """Set up sample environment with test data"""
    print("🚀 Setting up sample environment...")
    
    # Generate sample documents
    generator = DataGenerator()
    documents = generator.generate_sample_documents(document_count)
    
    # Save to file
    generator.save_sample_data(documents, data_file)
    
    print(f"✅ Sample environment ready with {document_count} documents")
    return documents


def validate_exercise_solution(solution_data: Any, validation_rules: Dict[str, Any]) -> bool:
    """Validate an exercise solution against rules"""
    validator = ExerciseValidator()
    
    # Apply validation rules
    for rule_name, rule_config in validation_rules.items():
        if rule_name == "search_results":
            if not validator.validate_search_results(
                solution_data, 
                rule_config.get("expected_count"),
                rule_config.get("required_fields")
            ):
                return False
        
        elif rule_name == "index_schema":
            if not validator.validate_index_schema(
                solution_data,
                rule_config.get("required_fields", [])
            ):
                return False
        
        elif rule_name == "query_syntax":
            if not validator.validate_query_syntax(
                solution_data,
                rule_config.get("query_type", "simple")
            ):
                return False
    
    return True


if __name__ == "__main__":
    # Example usage and testing
    print("Testing common utilities...")
    
    # Test data generation
    documents = setup_sample_environment("test_data.json", 10)
    print(f"Generated {len(documents)} sample documents")
    
    # Test performance monitoring
    monitor = PerformanceMonitor()
    
    def sample_operation():
        time.sleep(0.1)  # Simulate work
        return "Operation completed"
    
    result = monitor.measure_operation("Sample Operation", sample_operation)
    summary = monitor.get_performance_summary()
    print(f"Performance summary: {summary}")
    
    # Test configuration helper
    helper = ConfigurationHelper()
    fields = helper.create_basic_field_definitions()
    schema = helper.create_index_schema_template("test-index", fields)
    print(f"Created schema with {len(schema['fields'])} fields")
    
    print("✅ All utility tests completed successfully!")