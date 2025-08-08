"""
Azure AI Search Configuration Validation - Module 1 Code Sample
===========================================================

This script provides comprehensive validation of your Azure AI Search configuration.
It helps beginners identify and fix common setup issues before attempting to connect.

Learning Objectives:
- Understand what configuration is required for Azure AI Search
- Learn to validate environment variables and settings
- Practice systematic troubleshooting approaches
- Explore configuration best practices and security

Prerequisites:
- Python environment set up with required packages
- .env file created (can be empty for this validation)
- Basic understanding of environment variables

Author: Azure AI Search Handbook
Module: Beginner - Module 1: Introduction and Setup
"""

import os
import sys
import json
import re
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Environment and utility imports
from dotenv import load_dotenv

# Add setup directory to path for utility imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'setup'))


@dataclass
class ValidationResult:
    """Container for individual validation results."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any]
    severity: str  # 'error', 'warning', 'info'
    fix_suggestions: List[str]


class ConfigurationValidator:
    """
    Comprehensive configuration validator for Azure AI Search setup.
    
    This class provides step-by-step validation of all configuration
    requirements with detailed explanations and fix suggestions.
    """
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.results: List[ValidationResult] = []
        self.config: Dict[str, Optional[str]] = {}
        
        print("🔍 Azure AI Search Configuration Validator")
        print("=" * 50)
        print("This tool will help you validate your setup and identify any issues.")
        print()
    
    def add_result(self, name: str, passed: bool, message: str, 
                   details: Dict[str, Any] = None, severity: str = 'error',
                   fix_suggestions: List[str] = None) -> bool:
        """
        Add a validation result and display it immediately.
        
        Args:
            name: Name of the validation check
            passed: Whether the validation passed
            message: Description of the result
            details: Additional details about the validation
            severity: Severity level ('error', 'warning', 'info')
            fix_suggestions: List of suggested fixes
            
        Returns:
            bool: The passed status for convenience
        """
        result = ValidationResult(
            name=name,
            passed=passed,
            message=message,
            details=details or {},
            severity=severity,
            fix_suggestions=fix_suggestions or []
        )
        
        self.results.append(result)
        
        # Display result immediately
        if passed:
            status = "✅"
        elif severity == 'warning':
            status = "⚠️ "
        else:
            status = "❌"
        
        print(f"{status} {name}: {message}")
        
        # Show fix suggestions for failed validations
        if not passed and fix_suggestions:
            print("   💡 Suggestions:")
            for suggestion in fix_suggestions:
                print(f"      • {suggestion}")
        
        return passed
    
    def validate_python_environment(self) -> bool:
        """
        Validate Python environment and version requirements.
        
        Returns:
            bool: True if Python environment is valid
        """
        print("🐍 Validating Python Environment...")
        
        try:
            # Check Python version
            version = sys.version_info
            version_string = f"{version.major}.{version.minor}.{version.micro}"
            
            if version < (3, 8):
                return self.add_result(
                    "Python Version",
                    False,
                    f"Python 3.8+ required, found {version.major}.{version.minor}",
                    {"current_version": version_string, "required_version": "3.8+"},
                    fix_suggestions=[
                        "Install Python 3.8 or higher from python.org",
                        "Use pyenv to manage multiple Python versions",
                        "Update your system Python installation"
                    ]
                )
            
            return self.add_result(
                "Python Version",
                True,
                f"Python {version_string} (compatible)",
                {"version": version_string},
                severity='info'
            )
            
        except Exception as e:
            return self.add_result(
                "Python Version",
                False,
                f"Error checking Python version: {str(e)}",
                fix_suggestions=["Ensure Python is properly installed and accessible"]
            )
    
    def validate_required_packages(self) -> bool:
        """
        Validate that all required Python packages are installed.
        
        Returns:
            bool: True if all required packages are available
        """
        print("\n📦 Validating Required Packages...")
        
        # Define required packages with their import names
        required_packages = [
            ("azure-search-documents", "azure.search.documents", "Azure AI Search SDK"),
            ("python-dotenv", "dotenv", "Environment variable loading"),
            ("requests", "requests", "HTTP requests (used by Azure SDK)"),
        ]
        
        optional_packages = [
            ("pandas", "pandas", "Data manipulation (useful for exercises)"),
            ("jupyter", "jupyter", "Interactive notebooks"),
            ("pytest", "pytest", "Testing framework")
        ]
        
        missing_required = []
        missing_optional = []
        installed_packages = []
        
        # Check required packages
        for package_name, import_name, description in required_packages:
            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
                installed_packages.append(f"{package_name} ({version})")
            except ImportError:
                missing_required.append((package_name, description))
        
        # Check optional packages
        for package_name, import_name, description in optional_packages:
            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
                installed_packages.append(f"{package_name} ({version}) [optional]")
            except ImportError:
                missing_optional.append((package_name, description))
        
        # Report required packages
        if missing_required:
            missing_list = [f"{pkg} ({desc})" for pkg, desc in missing_required]
            return self.add_result(
                "Required Packages",
                False,
                f"Missing {len(missing_required)} required packages",
                {
                    "missing_required": missing_list,
                    "installed": installed_packages
                },
                fix_suggestions=[
                    "Run: pip install -r requirements.txt",
                    f"Install individually: pip install {' '.join([pkg for pkg, _ in missing_required])}",
                    "Create a virtual environment first: python -m venv venv",
                    "Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
                ]
            )
        
        # Report optional packages
        if missing_optional:
            missing_list = [f"{pkg} ({desc})" for pkg, desc in missing_optional]
            self.add_result(
                "Optional Packages",
                True,
                f"Missing {len(missing_optional)} optional packages (not critical)",
                {"missing_optional": missing_list},
                severity='warning',
                fix_suggestions=[
                    f"Install optional packages: pip install {' '.join([pkg for pkg, _ in missing_optional])}",
                    "These packages enhance the learning experience but aren't required"
                ]
            )
        
        return self.add_result(
            "Required Packages",
            True,
            f"All {len(required_packages)} required packages installed",
            {"installed": installed_packages},
            severity='info'
        )
    
    def validate_environment_file(self) -> bool:
        """
        Validate the .env file exists and has proper structure.
        
        Returns:
            bool: True if .env file is properly configured
        """
        print("\n📄 Validating Environment File...")
        
        env_file_path = Path(".env")
        env_template_path = Path(".env.template")
        
        # Check if .env file exists
        if not env_file_path.exists():
            fix_suggestions = ["Create a .env file in the project root directory"]
            
            if env_template_path.exists():
                fix_suggestions.extend([
                    "Copy .env.template to .env: cp .env.template .env",
                    "Edit .env file with your actual Azure AI Search credentials"
                ])
            else:
                fix_suggestions.append("Create .env file with required variables (see documentation)")
            
            return self.add_result(
                "Environment File",
                False,
                ".env file not found",
                {"env_file_path": str(env_file_path.absolute())},
                fix_suggestions=fix_suggestions
            )
        
        # Check if .env file is readable
        try:
            with open(env_file_path, 'r') as f:
                env_content = f.read()
        except Exception as e:
            return self.add_result(
                "Environment File",
                False,
                f"Cannot read .env file: {str(e)}",
                fix_suggestions=[
                    "Check file permissions on .env file",
                    "Ensure .env file is not corrupted"
                ]
            )
        
        # Check if .env file has content
        if not env_content.strip():
            return self.add_result(
                "Environment File",
                False,
                ".env file is empty",
                fix_suggestions=[
                    "Add your Azure AI Search configuration to .env file",
                    "Use .env.template as a reference if available",
                    "See documentation for required environment variables"
                ]
            )
        
        # Check for common formatting issues
        lines = env_content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' not in line:
                issues.append(f"Line {i}: Missing '=' separator")
            elif line.startswith('='):
                issues.append(f"Line {i}: Variable name missing")
            elif line.endswith('='):
                issues.append(f"Line {i}: Variable value missing")
        
        if issues:
            return self.add_result(
                "Environment File Format",
                False,
                f"Found {len(issues)} formatting issues",
                {"issues": issues},
                fix_suggestions=[
                    "Fix formatting issues in .env file",
                    "Use format: VARIABLE_NAME=value",
                    "No spaces around the '=' sign",
                    "Use quotes for values with spaces"
                ]
            )
        
        return self.add_result(
            "Environment File",
            True,
            f".env file found and readable ({len(lines)} lines)",
            {"file_path": str(env_file_path.absolute()), "line_count": len(lines)},
            severity='info'
        )
    
    def validate_environment_variables(self) -> bool:
        """
        Validate that required environment variables are set correctly.
        
        Returns:
            bool: True if all required environment variables are valid
        """
        print("\n🔧 Validating Environment Variables...")
        
        # Load environment variables
        load_dotenv()
        
        # Store configuration for later use
        self.config = {
            'endpoint': os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT'),
            'api_key': os.getenv('AZURE_SEARCH_API_KEY'),
            'index_name': os.getenv('AZURE_SEARCH_INDEX_NAME'),
            'use_managed_identity': os.getenv('USE_MANAGED_IDENTITY', 'false').lower() == 'true'
        }
        
        # Define validation rules
        validations = []
        
        # Validate endpoint
        endpoint = self.config['endpoint']
        if not endpoint:
            validations.append(("Service Endpoint", False, "AZURE_SEARCH_SERVICE_ENDPOINT not set", [
                "Set AZURE_SEARCH_SERVICE_ENDPOINT in your .env file",
                "Format: https://your-service-name.search.windows.net",
                "Get this from Azure Portal > Your Search Service > Overview"
            ]))
        elif not self._validate_endpoint_format(endpoint):
            validations.append(("Service Endpoint Format", False, "Invalid endpoint format", [
                "Endpoint should start with https://",
                "Endpoint should end with .search.windows.net",
                "Example: https://my-search-service.search.windows.net"
            ]))
        else:
            validations.append(("Service Endpoint", True, f"Valid endpoint configured", None))
        
        # Validate authentication
        api_key = self.config['api_key']
        use_managed_identity = self.config['use_managed_identity']
        
        if not api_key and not use_managed_identity:
            validations.append(("Authentication", False, "No authentication method configured", [
                "Set AZURE_SEARCH_API_KEY in your .env file, OR",
                "Set USE_MANAGED_IDENTITY=true for managed identity",
                "Get API key from Azure Portal > Your Search Service > Keys"
            ]))
        elif api_key and not self._validate_api_key_format(api_key):
            validations.append(("API Key Format", False, "API key format appears invalid", [
                "API keys are typically 32+ characters long",
                "Check for extra spaces or characters",
                "Regenerate key in Azure Portal if needed"
            ]))
        elif api_key:
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
            validations.append(("Authentication", True, f"API key configured ({masked_key})", None))
        else:
            validations.append(("Authentication", True, "Managed identity configured", None))
        
        # Validate optional settings
        index_name = self.config['index_name']
        if index_name:
            if self._validate_index_name_format(index_name):
                validations.append(("Index Name", True, f"Valid index name: {index_name}", None))
            else:
                validations.append(("Index Name Format", False, "Invalid index name format", [
                    "Index names must be lowercase",
                    "Use only letters, numbers, and hyphens",
                    "Cannot start or end with hyphens",
                    "Maximum 128 characters"
                ]))
        else:
            validations.append(("Index Name", True, "Not specified (will use default)", None))
        
        # Process all validations
        all_passed = True
        for name, passed, message, suggestions in validations:
            if not self.add_result(name, passed, message, fix_suggestions=suggestions or []):
                all_passed = False
        
        return all_passed
    
    def validate_directory_structure(self) -> bool:
        """
        Validate that the project directory structure is correct.
        
        Returns:
            bool: True if directory structure is valid
        """
        print("\n📁 Validating Directory Structure...")
        
        # Define expected directories
        expected_dirs = [
            ("config", "Configuration files", True),
            ("data", "Sample data storage", True),
            ("logs", "Log files", True),
            ("setup", "Setup utilities", True),
            ("docs", "Documentation", False),
            ("scripts", "Utility scripts", False)
        ]
        
        missing_required = []
        missing_optional = []
        present_dirs = []
        
        for dir_name, description, required in expected_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                present_dirs.append(f"{dir_name} ({description})")
            elif required:
                missing_required.append((dir_name, description))
            else:
                missing_optional.append((dir_name, description))
        
        # Report results
        if missing_required:
            missing_list = [f"{dir_name} ({desc})" for dir_name, desc in missing_required]
            return self.add_result(
                "Directory Structure",
                False,
                f"Missing {len(missing_required)} required directories",
                {
                    "missing_required": missing_list,
                    "present": present_dirs
                },
                fix_suggestions=[
                    f"Create missing directories: mkdir -p {' '.join([d for d, _ in missing_required])}",
                    "Run setup script if available: python setup/environment_setup.py",
                    "Check if you're in the correct project directory"
                ]
            )
        
        # Report optional directories
        if missing_optional:
            missing_list = [f"{dir_name} ({desc})" for dir_name, desc in missing_optional]
            self.add_result(
                "Optional Directories",
                True,
                f"Missing {len(missing_optional)} optional directories",
                {"missing_optional": missing_list},
                severity='info',
                fix_suggestions=[
                    "These directories will be created automatically when needed"
                ]
            )
        
        return self.add_result(
            "Directory Structure",
            True,
            f"All required directories present ({len(present_dirs)} total)",
            {"present": present_dirs},
            severity='info'
        )
    
    def validate_configuration_files(self) -> bool:
        """
        Validate that configuration template files exist.
        
        Returns:
            bool: True if configuration files are valid
        """
        print("\n⚙️  Validating Configuration Files...")
        
        # Define expected files
        expected_files = [
            (".env.template", "Environment template", False),
            ("requirements.txt", "Python dependencies", True),
            ("config/search_config.json.template", "Search config template", False),
            ("config/logging.json", "Logging configuration", False)
        ]
        
        missing_required = []
        missing_optional = []
        present_files = []
        
        for file_path, description, required in expected_files:
            path = Path(file_path)
            if path.exists() and path.is_file():
                present_files.append(f"{file_path} ({description})")
            elif required:
                missing_required.append((file_path, description))
            else:
                missing_optional.append((file_path, description))
        
        # Check requirements.txt content if it exists
        req_file = Path("requirements.txt")
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    req_content = f.read()
                
                # Check for essential packages
                essential_packages = ['azure-search-documents', 'python-dotenv']
                missing_packages = []
                
                for package in essential_packages:
                    if package not in req_content:
                        missing_packages.append(package)
                
                if missing_packages:
                    self.add_result(
                        "Requirements Content",
                        False,
                        f"Missing essential packages in requirements.txt",
                        {"missing_packages": missing_packages},
                        severity='warning',
                        fix_suggestions=[
                            f"Add missing packages to requirements.txt: {', '.join(missing_packages)}",
                            "Run: pip freeze > requirements.txt to update"
                        ]
                    )
                else:
                    self.add_result(
                        "Requirements Content",
                        True,
                        "Essential packages found in requirements.txt",
                        severity='info'
                    )
                    
            except Exception as e:
                self.add_result(
                    "Requirements Content",
                    False,
                    f"Cannot read requirements.txt: {str(e)}",
                    severity='warning'
                )
        
        # Report results
        if missing_required:
            missing_list = [f"{file_path} ({desc})" for file_path, desc in missing_required]
            return self.add_result(
                "Configuration Files",
                False,
                f"Missing {len(missing_required)} required files",
                {
                    "missing_required": missing_list,
                    "present": present_files
                },
                fix_suggestions=[
                    "Create missing configuration files",
                    "Check if you're in the correct project directory",
                    "Run setup script if available"
                ]
            )
        
        return self.add_result(
            "Configuration Files",
            True,
            f"All required configuration files present",
            {"present": present_files},
            severity='info'
        )
    
    def _validate_endpoint_format(self, endpoint: str) -> bool:
        """Validate Azure AI Search endpoint format."""
        if not endpoint:
            return False
        
        # Should start with https://
        if not endpoint.startswith('https://'):
            return False
        
        # Should end with .search.windows.net
        if not endpoint.endswith('.search.windows.net'):
            return False
        
        # Should have a service name
        service_name = endpoint.replace('https://', '').replace('.search.windows.net', '')
        if not service_name or len(service_name) < 2:
            return False
        
        return True
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format (basic checks)."""
        if not api_key:
            return False
        
        # API keys are typically 32+ characters
        if len(api_key) < 20:
            return False
        
        # Should not contain spaces
        if ' ' in api_key:
            return False
        
        return True
    
    def _validate_index_name_format(self, index_name: str) -> bool:
        """Validate index name format according to Azure AI Search rules."""
        if not index_name:
            return False
        
        # Must be lowercase
        if index_name != index_name.lower():
            return False
        
        # Must be 1-128 characters
        if len(index_name) < 1 or len(index_name) > 128:
            return False
        
        # Can only contain letters, numbers, and hyphens
        if not re.match(r'^[a-z0-9-]+$', index_name):
            return False
        
        # Cannot start or end with hyphens
        if index_name.startswith('-') or index_name.endswith('-'):
            return False
        
        return True
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report of all validations.
        
        Returns:
            Dict containing the validation summary
        """
        print("\n" + "=" * 50)
        print("📊 Configuration Validation Summary")
        print("=" * 50)
        
        # Count results by status
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = sum(1 for r in self.results if not r.passed and r.severity == 'error')
        warning_count = sum(1 for r in self.results if not r.passed and r.severity == 'warning')
        total_count = len(self.results)
        
        # Display summary
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"⚠️  Warnings: {warning_count}")
        print(f"📊 Total Checks: {total_count}")
        
        # Overall status
        if failed_count == 0:
            if warning_count == 0:
                print("\n🎉 Status: PERFECT CONFIGURATION!")
                print("Your Azure AI Search setup is ready to go!")
            else:
                print("\n✅ Status: READY WITH MINOR ISSUES")
                print("Your setup will work, but consider addressing the warnings.")
        else:
            print("\n❌ Status: CONFIGURATION ISSUES DETECTED")
            print("Please fix the failed validations before proceeding.")
        
        # Create detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": total_count,
                "passed": passed_count,
                "failed": failed_count,
                "warnings": warning_count,
                "success_rate": (passed_count / total_count * 100) if total_count > 0 else 0
            },
            "configuration": self.config,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "severity": r.severity,
                    "details": r.details,
                    "fix_suggestions": r.fix_suggestions
                }
                for r in self.results
            ]
        }
        
        return report
    
    def save_report(self, file_path: str = "logs/configuration_validation.json"):
        """Save the validation report to a file."""
        try:
            # Ensure logs directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Generate and save report
            report = self.generate_summary_report()
            
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n📄 Detailed report saved to: {file_path}")
            
        except Exception as e:
            print(f"\n⚠️  Could not save report: {str(e)}")
    
    def run_all_validations(self) -> bool:
        """
        Run all configuration validations in sequence.
        
        Returns:
            bool: True if all critical validations passed
        """
        validation_methods = [
            self.validate_python_environment,
            self.validate_required_packages,
            self.validate_environment_file,
            self.validate_environment_variables,
            self.validate_directory_structure,
            self.validate_configuration_files
        ]
        
        critical_failures = 0
        
        for method in validation_methods:
            try:
                method()
            except Exception as e:
                print(f"❌ Unexpected error in {method.__name__}: {str(e)}")
                critical_failures += 1
        
        # Generate summary
        report = self.generate_summary_report()
        
        # Save report
        self.save_report()
        
        # Provide next steps
        print("\n🎯 Next Steps:")
        
        failed_count = report["summary"]["failed"]
        if failed_count == 0:
            print("✅ Configuration validation passed!")
            print("   1. Test your connection: python code-samples/connection_setup.py")
            print("   2. Try the interactive notebook: code-samples/connection_setup.ipynb")
            print("   3. Complete the exercises in exercises/")
            print("   4. Move on to Module 2: Basic Search Operations")
        else:
            print("❌ Please fix the configuration issues:")
            failed_results = [r for r in self.results if not r.passed and r.severity == 'error']
            for result in failed_results:
                print(f"   • {result.name}: {result.message}")
                if result.fix_suggestions:
                    for suggestion in result.fix_suggestions[:2]:  # Show top 2 suggestions
                        print(f"     - {suggestion}")
        
        return failed_count == 0


def main():
    """
    Main function to run configuration validation.
    
    This function provides a complete validation of your Azure AI Search
    configuration with detailed feedback and suggestions.
    """
    print("🚀 Azure AI Search Configuration Validation")
    print("This script will validate your setup and help identify any issues.")
    print()
    
    # Create validator and run all checks
    validator = ConfigurationValidator()
    success = validator.run_all_validations()
    
    # Exit with appropriate code
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)