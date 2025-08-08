"""
Exercise Validation Script
Automated validation for Module 1 exercises
"""

import os
import sys
import importlib.util
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

class ExerciseValidator:
    """Validates completion of Module 1 exercises"""
    
    def __init__(self):
        self.exercises_dir = Path(__file__).parent
        self.results = {}
    
    def validate_exercise_01(self) -> Dict[str, Any]:
        """Validate Exercise 1: Basic Setup and Connection"""
        print("🧪 Validating Exercise 1: Basic Setup and Connection")
        
        result = {
            'exercise': 'Exercise 1: Basic Setup and Connection',
            'completed': False,
            'score': 0,
            'max_score': 100,
            'checks': []
        }
        
        # Check 1: File exists and has required functions
        exercise_file = self.exercises_dir / 'exercise_01_setup.py'
        if not exercise_file.exists():
            result['checks'].append({
                'name': 'File exists',
                'passed': False,
                'message': 'exercise_01_setup.py not found'
            })
            return result
        
        try:
            # Import the exercise module
            spec = importlib.util.spec_from_file_location("exercise_01", exercise_file)
            exercise_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(exercise_module)
            
            # Check for required functions
            required_functions = ['setup_environment', 'create_client', 'validate_connection']
            for func_name in required_functions:
                if hasattr(exercise_module, func_name):
                    func = getattr(exercise_module, func_name)
                    # Check if function is implemented (not just 'pass')
                    import inspect
                    source = inspect.getsource(func)
                    if 'pass' in source and len(source.strip().split('\n')) < 10:
                        result['checks'].append({
                            'name': f'Function {func_name} implemented',
                            'passed': False,
                            'message': f'{func_name} contains only placeholder code'
                        })
                    else:
                        result['checks'].append({
                            'name': f'Function {func_name} implemented',
                            'passed': True,
                            'message': f'{func_name} appears to be implemented'
                        })
                        result['score'] += 25
                else:
                    result['checks'].append({
                        'name': f'Function {func_name} exists',
                        'passed': False,
                        'message': f'{func_name} function not found'
                    })
            
            # Check for proper imports
            source_code = exercise_file.read_text()
            if 'from azure.search.documents import SearchClient' in source_code:
                result['checks'].append({
                    'name': 'Azure imports added',
                    'passed': True,
                    'message': 'Required Azure imports found'
                })
                result['score'] += 25
            else:
                result['checks'].append({
                    'name': 'Azure imports added',
                    'passed': False,
                    'message': 'Azure SDK imports not found or commented out'
                })
            
        except Exception as e:
            result['checks'].append({
                'name': 'Code syntax valid',
                'passed': False,
                'message': f'Error importing module: {str(e)}'
            })
        
        result['completed'] = result['score'] >= 75
        return result
    
    def validate_exercise_02(self) -> Dict[str, Any]:
        """Validate Exercise 2: Environment Validation"""
        print("🧪 Validating Exercise 2: Environment Validation")
        
        result = {
            'exercise': 'Exercise 2: Environment Validation',
            'completed': False,
            'score': 0,
            'max_score': 100,
            'checks': []
        }
        
        exercise_file = self.exercises_dir / 'exercise_02_environment_validation.py'
        if not exercise_file.exists():
            result['checks'].append({
                'name': 'File exists',
                'passed': False,
                'message': 'exercise_02_environment_validation.py not found'
            })
            return result
        
        try:
            spec = importlib.util.spec_from_file_location("exercise_02", exercise_file)
            exercise_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(exercise_module)
            
            # Check for required functions
            required_functions = [
                'check_environment_file',
                'validate_endpoint_format',
                'validate_api_key_format',
                'validate_index_name_format',
                'load_and_validate_configuration'
            ]
            
            implemented_functions = 0
            for func_name in required_functions:
                if hasattr(exercise_module, func_name):
                    func = getattr(exercise_module, func_name)
                    import inspect
                    source = inspect.getsource(func)
                    if 'pass' not in source or len(source.strip().split('\n')) > 10:
                        implemented_functions += 1
                        result['checks'].append({
                            'name': f'Function {func_name} implemented',
                            'passed': True,
                            'message': f'{func_name} appears to be implemented'
                        })
                    else:
                        result['checks'].append({
                            'name': f'Function {func_name} implemented',
                            'passed': False,
                            'message': f'{func_name} contains only placeholder code'
                        })
                else:
                    result['checks'].append({
                        'name': f'Function {func_name} exists',
                        'passed': False,
                        'message': f'{func_name} function not found'
                    })
            
            result['score'] = (implemented_functions / len(required_functions)) * 100
            
        except Exception as e:
            result['checks'].append({
                'name': 'Code syntax valid',
                'passed': False,
                'message': f'Error importing module: {str(e)}'
            })
        
        result['completed'] = result['score'] >= 60
        return result
    
    def validate_all_exercises(self) -> Dict[str, Any]:
        """Validate all exercises in Module 1"""
        print("🔍 Validating All Module 1 Exercises")
        print("=" * 50)
        
        # List of all exercises to validate
        exercise_validators = [
            self.validate_exercise_01,
            self.validate_exercise_02,
            # Add more exercise validators as needed
        ]
        
        all_results = []
        total_score = 0
        max_total_score = 0
        completed_exercises = 0
        
        for validator in exercise_validators:
            try:
                result = validator()
                all_results.append(result)
                total_score += result['score']
                max_total_score += result['max_score']
                if result['completed']:
                    completed_exercises += 1
                
                # Display individual results
                status = "✅ COMPLETED" if result['completed'] else "❌ INCOMPLETE"
                print(f"\n{status} {result['exercise']}")
                print(f"Score: {result['score']}/{result['max_score']}")
                
                for check in result['checks']:
                    check_status = "✅" if check['passed'] else "❌"
                    print(f"  {check_status} {check['name']}: {check['message']}")
                
            except Exception as e:
                print(f"❌ Error validating exercise: {str(e)}")
        
        # Overall summary
        overall_percentage = (total_score / max_total_score * 100) if max_total_score > 0 else 0
        
        summary = {
            'total_exercises': len(exercise_validators),
            'completed_exercises': completed_exercises,
            'total_score': total_score,
            'max_total_score': max_total_score,
            'percentage': overall_percentage,
            'results': all_results
        }
        
        print("\n" + "=" * 50)
        print("📊 OVERALL SUMMARY")
        print("=" * 50)
        print(f"Exercises Completed: {completed_exercises}/{len(exercise_validators)}")
        print(f"Overall Score: {total_score}/{max_total_score} ({overall_percentage:.1f}%)")
        
        if overall_percentage >= 80:
            print("🎉 Excellent work! You've mastered Module 1 concepts.")
        elif overall_percentage >= 60:
            print("👍 Good progress! Complete the remaining exercises to master the module.")
        else:
            print("📚 Keep working! Review the solutions and try implementing the exercises.")
        
        return summary
    
    def check_environment_setup(self) -> Dict[str, Any]:
        """Check if the development environment is properly set up"""
        print("🔧 Checking Development Environment Setup")
        
        checks = []
        
        # Check for .env file
        env_file_exists = os.path.exists('.env')
        checks.append({
            'name': '.env file exists',
            'passed': env_file_exists,
            'message': '.env file found' if env_file_exists else '.env file not found'
        })
        
        # Check for required Python packages
        required_packages = [
            'azure-search-documents',
            'azure-identity',
            'python-dotenv'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                checks.append({
                    'name': f'Package {package} installed',
                    'passed': True,
                    'message': f'{package} is available'
                })
            except ImportError:
                checks.append({
                    'name': f'Package {package} installed',
                    'passed': False,
                    'message': f'{package} not installed - run: pip install {package}'
                })
        
        # Check Python version
        python_version = sys.version_info
        version_ok = python_version >= (3, 7)
        checks.append({
            'name': 'Python version compatible',
            'passed': version_ok,
            'message': f'Python {python_version.major}.{python_version.minor} - {"✅ Compatible" if version_ok else "❌ Requires Python 3.7+"}'
        })
        
        return {
            'checks': checks,
            'environment_ready': all(check['passed'] for check in checks)
        }

def main():
    """Main function to run exercise validation"""
    print("🎓 Azure AI Search Handbook - Module 1 Exercise Validator")
    print("=" * 60)
    
    validator = ExerciseValidator()
    
    # Check environment setup first
    env_check = validator.check_environment_setup()
    print("\n🔧 Environment Setup Check:")
    for check in env_check['checks']:
        status = "✅" if check['passed'] else "❌"
        print(f"  {status} {check['name']}: {check['message']}")
    
    if not env_check['environment_ready']:
        print("\n⚠️  Please fix environment issues before running exercise validation.")
        return
    
    print("\n" + "=" * 60)
    
    # Validate all exercises
    summary = validator.validate_all_exercises()
    
    # Provide recommendations
    print("\n🎯 Recommendations:")
    if summary['percentage'] < 60:
        print("1. Review the exercise instructions carefully")
        print("2. Check the solution files for guidance")
        print("3. Make sure to implement all required functions")
        print("4. Test your code before considering it complete")
    elif summary['percentage'] < 80:
        print("1. Complete the remaining exercises")
        print("2. Review any failed checks above")
        print("3. Ensure all functions are fully implemented")
    else:
        print("1. Excellent work on Module 1!")
        print("2. You're ready to move on to Module 2: Basic Search Operations")
        print("3. Consider helping others who might be struggling with these exercises")
    
    print("\n📚 Additional Resources:")
    print("• Solution files are available in the solutions/ directory")
    print("• Code samples are in the code-samples/ directory")
    print("• Documentation is in the documentation.md file")
    print("• Troubleshooting help: python code-samples/troubleshooting_utilities.py")

if __name__ == "__main__":
    main()