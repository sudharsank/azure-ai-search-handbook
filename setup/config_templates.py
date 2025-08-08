"""
Configuration Templates
Templates and utilities for creating Azure AI Search configurations
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class IndexSchemaTemplate:
    """Templates for creating Azure AI Search index schemas"""
    
    @staticmethod
    def basic_document_schema(index_name: str) -> Dict[str, Any]:
        """Basic document schema for general content"""
        return {
            "name": index_name,
            "fields": [
                {
                    "name": "id",
                    "type": "Edm.String",
                    "key": True,
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": False,
                    "facetable": False
                },
                {
                    "name": "title",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": False,
                    "analyzer": "standard.lucene",
                    "highlightable": True
                },
                {
                    "name": "content",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True,
                    "sortable": False,
                    "facetable": False,
                    "analyzer": "standard.lucene",
                    "highlightable": True
                },
                {
                    "name": "category",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": True
                },
                {
                    "name": "tags",
                    "type": "Collection(Edm.String)",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": False,
                    "facetable": True
                },
                {
                    "name": "created_date",
                    "type": "Edm.DateTimeOffset",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": True
                },
                {
                    "name": "rating",
                    "type": "Edm.Double",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": True
                }
            ],
            "suggesters": [
                {
                    "name": "sg",
                    "searchMode": "analyzingInfixMatching",
                    "sourceFields": ["title", "content", "category"]
                }
            ],
            "corsOptions": {
                "allowedOrigins": ["*"],
                "maxAgeInSeconds": 300
            }
        }
    
    @staticmethod
    def ecommerce_product_schema(index_name: str) -> Dict[str, Any]:
        """E-commerce product schema template"""
        return {
            "name": index_name,
            "fields": [
                {
                    "name": "product_id",
                    "type": "Edm.String",
                    "key": True,
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True
                },
                {
                    "name": "name",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "analyzer": "standard.lucene",
                    "highlightable": True
                },
                {
                    "name": "description",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True,
                    "analyzer": "standard.lucene",
                    "highlightable": True
                },
                {
                    "name": "brand",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "facetable": True
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
                    "name": "price",
                    "type": "Edm.Double",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": True
                },
                {
                    "name": "in_stock",
                    "type": "Edm.Boolean",
                    "searchable": False,
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
                    "name": "rating",
                    "type": "Edm.Double",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": True
                },
                {
                    "name": "review_count",
                    "type": "Edm.Int32",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True,
                    "facetable": True
                }
            ],
            "suggesters": [
                {
                    "name": "product_suggester",
                    "searchMode": "analyzingInfixMatching",
                    "sourceFields": ["name", "brand", "category"]
                }
            ],
            "scoringProfiles": [
                {
                    "name": "popularity",
                    "text": {
                        "weights": {
                            "name": 2.0,
                            "description": 1.0,
                            "brand": 1.5
                        }
                    },
                    "functions": [
                        {
                            "type": "magnitude",
                            "boost": 2.0,
                            "fieldName": "rating",
                            "interpolation": "linear",
                            "magnitude": {
                                "boostingRangeStart": 3.0,
                                "boostingRangeEnd": 5.0,
                                "constantBoostBeyondRange": False
                            }
                        },
                        {
                            "type": "magnitude",
                            "boost": 1.5,
                            "fieldName": "review_count",
                            "interpolation": "linear",
                            "magnitude": {
                                "boostingRangeStart": 10,
                                "boostingRangeEnd": 100,
                                "constantBoostBeyondRange": False
                            }
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def knowledge_base_schema(index_name: str) -> Dict[str, Any]:
        """Knowledge base/FAQ schema template"""
        return {
            "name": index_name,
            "fields": [
                {
                    "name": "id",
                    "type": "Edm.String",
                    "key": True,
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True
                },
                {
                    "name": "question",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True,
                    "analyzer": "standard.lucene",
                    "highlightable": True
                },
                {
                    "name": "answer",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True,
                    "analyzer": "standard.lucene",
                    "highlightable": True
                },
                {
                    "name": "topic",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "facetable": True
                },
                {
                    "name": "keywords",
                    "type": "Collection(Edm.String)",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True,
                    "facetable": True
                },
                {
                    "name": "difficulty_level",
                    "type": "Edm.String",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "facetable": True
                },
                {
                    "name": "last_updated",
                    "type": "Edm.DateTimeOffset",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True
                },
                {
                    "name": "helpful_votes",
                    "type": "Edm.Int32",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True,
                    "sortable": True
                }
            ],
            "suggesters": [
                {
                    "name": "question_suggester",
                    "searchMode": "analyzingInfixMatching",
                    "sourceFields": ["question", "keywords", "topic"]
                }
            ]
        }


class ScoringProfileTemplate:
    """Templates for creating scoring profiles"""
    
    @staticmethod
    def relevance_boosting_profile() -> Dict[str, Any]:
        """Basic relevance boosting profile"""
        return {
            "name": "relevance_boost",
            "text": {
                "weights": {
                    "title": 3.0,
                    "content": 1.0,
                    "category": 2.0
                }
            },
            "functions": [
                {
                    "type": "freshness",
                    "boost": 2.0,
                    "fieldName": "created_date",
                    "interpolation": "linear",
                    "freshness": {
                        "boostingDuration": "P30D"  # 30 days
                    }
                },
                {
                    "type": "magnitude",
                    "boost": 1.5,
                    "fieldName": "rating",
                    "interpolation": "linear",
                    "magnitude": {
                        "boostingRangeStart": 3.0,
                        "boostingRangeEnd": 5.0,
                        "constantBoostBeyondRange": False
                    }
                }
            ]
        }
    
    @staticmethod
    def popularity_profile() -> Dict[str, Any]:
        """Popularity-based scoring profile"""
        return {
            "name": "popularity",
            "functions": [
                {
                    "type": "magnitude",
                    "boost": 3.0,
                    "fieldName": "rating",
                    "interpolation": "quadratic",
                    "magnitude": {
                        "boostingRangeStart": 1.0,
                        "boostingRangeEnd": 5.0,
                        "constantBoostBeyondRange": True
                    }
                }
            ]
        }


class AnalyzerTemplate:
    """Templates for custom analyzers"""
    
    @staticmethod
    def custom_text_analyzer() -> Dict[str, Any]:
        """Custom text analyzer configuration"""
        return {
            "analyzers": [
                {
                    "name": "custom_standard",
                    "tokenizer": "standard_v2",
                    "tokenFilters": [
                        "lowercase",
                        "asciifolding",
                        "stop_words_filter"
                    ]
                }
            ],
            "tokenFilters": [
                {
                    "name": "stop_words_filter",
                    "type": "stopwords",
                    "stopwords": ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
                }
            ]
        }
    
    @staticmethod
    def multilingual_analyzer() -> Dict[str, Any]:
        """Multilingual analyzer configuration"""
        return {
            "analyzers": [
                {
                    "name": "multilingual",
                    "tokenizer": "standard_v2",
                    "tokenFilters": [
                        "lowercase",
                        "asciifolding"
                    ]
                }
            ]
        }


class ConfigurationManager:
    """Manage configuration templates and generation"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def create_index_config(self, schema_type: str, index_name: str, 
                          file_name: Optional[str] = None) -> str:
        """Create index configuration file"""
        
        schema_templates = {
            "basic": IndexSchemaTemplate.basic_document_schema,
            "ecommerce": IndexSchemaTemplate.ecommerce_product_schema,
            "knowledge_base": IndexSchemaTemplate.knowledge_base_schema
        }
        
        if schema_type not in schema_templates:
            raise ValueError(f"Unknown schema type: {schema_type}")
        
        schema = schema_templates[schema_type](index_name)
        
        if not file_name:
            file_name = f"{index_name}_schema.json"
        
        file_path = self.config_dir / file_name
        
        with open(file_path, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"✅ Created index configuration: {file_path}")
        return str(file_path)
    
    def create_scoring_profile_config(self, profile_type: str, 
                                    file_name: Optional[str] = None) -> str:
        """Create scoring profile configuration file"""
        
        profile_templates = {
            "relevance": ScoringProfileTemplate.relevance_boosting_profile,
            "popularity": ScoringProfileTemplate.popularity_profile
        }
        
        if profile_type not in profile_templates:
            raise ValueError(f"Unknown profile type: {profile_type}")
        
        profile = profile_templates[profile_type]()
        
        if not file_name:
            file_name = f"{profile_type}_scoring_profile.json"
        
        file_path = self.config_dir / file_name
        
        with open(file_path, 'w') as f:
            json.dump(profile, f, indent=2)
        
        print(f"✅ Created scoring profile configuration: {file_path}")
        return str(file_path)
    
    def create_analyzer_config(self, analyzer_type: str, 
                             file_name: Optional[str] = None) -> str:
        """Create analyzer configuration file"""
        
        analyzer_templates = {
            "custom_text": AnalyzerTemplate.custom_text_analyzer,
            "multilingual": AnalyzerTemplate.multilingual_analyzer
        }
        
        if analyzer_type not in analyzer_templates:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")
        
        analyzer = analyzer_templates[analyzer_type]()
        
        if not file_name:
            file_name = f"{analyzer_type}_analyzer.json"
        
        file_path = self.config_dir / file_name
        
        with open(file_path, 'w') as f:
            json.dump(analyzer, f, indent=2)
        
        print(f"✅ Created analyzer configuration: {file_path}")
        return str(file_path)
    
    def create_complete_config_set(self, project_name: str):
        """Create a complete set of configuration files for a project"""
        print(f"🚀 Creating complete configuration set for: {project_name}")
        
        # Create basic index schema
        self.create_index_config("basic", f"{project_name}-index")
        
        # Create scoring profiles
        self.create_scoring_profile_config("relevance")
        self.create_scoring_profile_config("popularity")
        
        # Create analyzer configuration
        self.create_analyzer_config("custom_text")
        
        # Create environment-specific configs
        environments = ["development", "staging", "production"]
        
        for env in environments:
            env_config = {
                "environment": env,
                "azure_search": {
                    "endpoint": f"https://{project_name}-{env}.search.windows.net",
                    "index_name": f"{project_name}-{env}-index",
                    "api_version": "2023-11-01"
                },
                "logging": {
                    "level": "DEBUG" if env == "development" else "INFO",
                    "file": f"logs/{env}.log"
                },
                "performance": {
                    "enable_monitoring": env != "production",
                    "cache_ttl": 300 if env == "production" else 60
                }
            }
            
            env_file = self.config_dir / f"{env}_config.json"
            with open(env_file, 'w') as f:
                json.dump(env_config, f, indent=2)
            
            print(f"✅ Created {env} environment configuration")
        
        print(f"🎉 Complete configuration set created for {project_name}")


def main():
    """Example usage of configuration templates"""
    print("🔧 Azure AI Search Configuration Templates")
    print("=" * 50)
    
    # Create configuration manager
    manager = ConfigurationManager()
    
    # Create sample configurations
    try:
        # Basic document index
        manager.create_index_config("basic", "sample-documents")
        
        # E-commerce product index
        manager.create_index_config("ecommerce", "products")
        
        # Knowledge base index
        manager.create_index_config("knowledge_base", "faq")
        
        # Scoring profiles
        manager.create_scoring_profile_config("relevance")
        manager.create_scoring_profile_config("popularity")
        
        # Analyzers
        manager.create_analyzer_config("custom_text")
        manager.create_analyzer_config("multilingual")
        
        print("\n✅ All configuration templates created successfully!")
        print("📁 Check the config/ directory for generated files")
        
    except Exception as e:
        print(f"❌ Error creating configurations: {str(e)}")


if __name__ == "__main__":
    main()