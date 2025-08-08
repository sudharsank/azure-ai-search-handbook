"""
Setup Validation Script
Comprehensive validation of Azure AI Search environment and connectivity
"""

import os
import sys
import json
import importlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv


class ValidationResult:
    """Container for validation results"""
    def __init__(self, name: str, passed: bool, message: str, details: Dict[str, Any] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}


class SetupValidator:
    """Comprehensive setup validation"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        load_dotenv()
    
    def add_result(self, name: str, passed: bool, message: str, details: Dict[str, Any] = None):
        """Add a validation result"""
        result = ValidationResult(name, passed, message, details)
        self.results.append(result)
        
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")
        
        return passed
    
    def check_python_environment(self) -> bool:
        """Check Python environment and version"""
        try:
            version = sys.version_info
            if version < (3, 8):
                return self.add_result(
                    "Python Version",
                    False,
                    f"Python 3.8+ required, found {version.major}.{version.minor}",
                    {"current_version": f"{version.major}.{version.minor}.{version.micro}"}
                )
            
            return self.add_result(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro}",
                {"version": f"{version.major}.{version.minor}.{version.micro}"}
            )
            
        except Exception as e:
            return self.add_result(
                "Python Version",
                False,
                f"Error checking Python version: {str(e)}"
            )
    
    def check_required_packages(self) -> bool:
        """Check if all required packages are installed"""
        required_packages = [
            ("azure-search-documents", "azure.search.documents"),
            ("python-dotenv", "dotenv"),
            ("requests", "requests"),
            ("pandas", "pandas"),
            ("numpy", "numpy"),
            ("jupyter", "jupyter"),
            ("mkdocs", "mkdocs"),
            ("pytest", "pytest")
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package_name, import_name in required_packages:
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'unknown')
                installed_packages.append(f"{package_name} ({version})")
            except ImportError:
                missing_packages.append(package_name)
        
        if missing_packages:
            return self.add_result(
                "Required Packages",
                False,
                f"Missing packages: {', '.join(missing_packages)}",
                {
                    "missing": missing_packages,
                    "installed": installed_packages
                }
            )
        
        return self.add_result(
            "Required Packages",
            True,
            f"All {len(required_packages)} required packages installed",
            {"installed": installed_packages}
        )
    
    def check_environment_variables(self) -> bool:
        """Check if required environment variables are set"""
        required_vars = [
            "AZURE_SEARCH_SERVICE_ENDPOINT",
            "AZURE_SEARCH_API_KEY"
        ]
        
        optional_vars = [
            "AZURE_SEARCH_INDEX_NAME",
            "AZURE_CLIENT_ID",
            "AZURE_CLIENT_SECRET",
            "AZURE_TENANT_ID"
        ]
        
        missing_required = []
        present_vars = {}
        
        # Check required variables
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_required.append(var)
            else:
                # Mask sensitive values for display
                if "KEY" in var or "SECRET" in var:
                    present_vars[var] = f"{value[:8]}..." if len(value) > 8 else "***"
                else:
                    present_vars[var] = value
        
        # Check optional variables
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                if "KEY" in var or "SECRET" in var:
                    present_vars[var] = f"{value[:8]}..." if len(value) > 8 else "***"
                else:
                    present_vars[var] = value
        
        if missing_required:
            return self.add_result(
                "Environment Variables",
                False,
                f"Missing required variables: {', '.join(missing_required)}",
                {
                    "missing_required": missing_required,
                    "present": present_vars
                }
            )
        
        return self.add_result(
            "Environment Variables",
            True,
            f"All required environment variables set",
            {"present": present_vars}
        )
    
    def check_directory_structure(self) -> bool:
        """Check if required directories exist"""
        required_dirs = [
            "config",
            "data", 
            "logs",
            "scripts",
            "setup"
        ]
        
        missing_dirs = []
        present_dirs = []
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                present_dirs.append(dir_name)
            else:
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return self.add_result(
                "Directory Structure",
                False,
                f"Missing directories: {', '.join(missing_dirs)}",
                {
                    "missing": missing_dirs,
                    "present": present_dirs
                }
            )
        
        return self.add_result(
            "Directory Structure",
            True,
            f"All {len(required_dirs)} required directories exist",
            {"present": present_dirs}
        )
    
    def check_configuration_files(self) -> bool:
        """Check if configuration files exist"""
        required_files = [
            ".env.template",
            "requirements.txt",
            "setup/connection_utils.py",
            "setup/common_utils.py"
        ]
        
        optional_files = [
            ".env",
            "config/search_config.json",
            "config/logging.json"
        ]
        
        missing_required = []
        present_files = []
        
        # Check required files
        for file_path in required_files:
            if Path(file_path).exists():
                present_files.append(file_path)
            else:
                missing_required.append(file_path)
        
        # Check optional files
        for file_path in optional_files:
            if Path(file_path).exists():
                present_files.append(f"{file_path} (optional)")
        
        if missing_required:
            return self.add_result(
                "Configuration Files",
                False,
                f"Missing required files: {', '.join(missing_required)}",
                {
                    "missing_required": missing_required,
                    "present": present_files
                }
            )
        
        return self.add_result(
            "Configuration Files",
            True,
            f"All required configuration files exist",
            {"present": present_files}
        )
    
    def test_azure_connection(self) -> bool:
        """Test connection to Azure AI Search service"""
        try:
            # Import connection utilities
            sys.path.append(str(Path(__file__).parent))
            from connection_utils import AzureSearchConnectionManager
            
            # Test connection
            manager = AzureSearchConnectionManager()
            
            if not manager.test_connection():
                return self.add_result(
                    "Azure Connection",
                    False,
                    "Failed to connect to Azure AI Search service"
                )
            
            # Get service statistics if possible
            try:
                stats = manager.get_service_statistics()
                indexes = manager.list_indexes()
                
                return self.add_result(
                    "Azure Connection",
                    True,
                    f"Connected successfully to Azure AI Search",
                    {
                        "service_stats": stats,
                        "available_indexes": indexes
                    }
                )
                
            except Exception as e:
                # Connection works but can't get detailed info
                return self.add_result(
                    "Azure Connection",
                    True,
                    f"Connected successfully (limited info: {str(e)})"
                )
                
        except ImportError as e:
            return self.add_result(
                "Azure Connection",
                False,
                f"Cannot import connection utilities: {str(e)}"
            )
        except Exception as e:
            return self.add_result(
                "Azure Connection",
                False,
                f"Connection test failed: {str(e)}"
            )
    
    def test_utility_functions(self) -> bool:
        """Test that utility functions work correctly"""
        try:
            # Import and test common utilities
            sys.path.append(str(Path(__file__).parent))
            from common_utils import DataGenerator, ExerciseValidator, ConfigurationHelper
            
            # Test data generation
            generator = DataGenerator()
            sample_docs = generator.generate_sample_documents(5)
            
            # Test validator
            validator = ExerciseValidator()
            
            # Test configuration helper
            helper = ConfigurationHelper()
            fields = helper.create_basic_field_definitions()
            
            return self.add_result(
                "Utility Functions",
                True,
                f"All utility functions working correctly",
                {
                    "sample_docs_generated": len(sample_docs),
                    "field_definitions_created": len(fields)
                }
            )
            
        except Exception as e:
            return self.add_result(
                "Utility Functions",
                False,
                f"Utility function test failed: {str(e)}"
            )
    
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        print("🔍 Azure AI Search Handbook - Comprehensive Setup Validation")
        print("=" * 70)
        
        validation_methods = [
            self.check_python_environment,
            self.check_required_packages,
            self.check_environment_variables,
            self.check_directory_structure,
            self.check_configuration_files,
            self.test_utility_functions,
            self.test_azure_connection
        ]
        
        all_passed = True
        
        for method in validation_methods:
            try:
                if not method():
                    all_passed = False
            except Exception as e:
                print(f"❌ Unexpected error in {method.__name__}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a detailed validation report"""
        passed_count = sum(1 for result in self.results if result.passed)
        total_count = len(self.results)
        
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "summary": {
                "total_checks": total_count,
                "passed_checks": passed_count,
                "failed_checks": total_count - passed_count,
                "success_rate": (passed_count / total_count * 100) if total_count > 0 else 0
            },
            "results": [
                {
                    "name": result.name,
                    "passed": result.passed,
                    "message": result.message,
                    "details": result.details
                }
                for result in self.results
            ]
        }
        
        return report
    
    def save_report(self, file_path: str = "logs/validation_report.json"):
        """Save validation report to file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            report = self.generate_report()
            
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Validation report saved to {file_path}")
            
        except Exception as e:
            print(f"⚠️  Could not save report: {str(e)}")


def main():
    """Main validation function"""
    validator = SetupValidator()
    
    # Run all validations
    all_passed = validator.run_all_validations()
    
    # Generate and save report
    validator.save_report()
    
    # Print summary
    print("\n" + "=" * 70)
    
    if all_passed:
        print("🎉 All validation checks passed!")
        print("✅ Your Azure AI Search Handbook environment is ready!")
        print("\n📚 Next steps:")
        print("1. Start with beginner modules in docs/beginner/")
        print("2. Generate sample data: python scripts/generate_sample_data.py")
        print("3. Test connection: python scripts/test_connection.py")
        print("4. Explore Jupyter notebooks in notebooks/")
    else:
        failed_results = [r for r in validator.results if not r.passed]
        print(f"❌ {len(failed_results)} validation check(s) failed:")
        
        for result in failed_results:
            print(f"   • {result.name}: {result.message}")
        
        print("\n🔧 Troubleshooting:")
        print("1. Run setup again: python setup/environment_setup.py")
        print("2. Check your .env file configuration")
        print("3. Verify Azure AI Search service credentials")
        print("4. Review the detailed report in logs/validation_report.json")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)