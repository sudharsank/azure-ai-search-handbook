#!/usr/bin/env python3
"""
Run All Examples - Azure AI Search Filters & Sorting

This script runs all the Python examples in sequence, providing a comprehensive
demonstration of Azure AI Search filtering and sorting capabilities.

Usage:
    python run_all_examples.py [--demo-mode] [--skip-search]

Options:
    --demo-mode: Run in demonstration mode (no actual API calls)
    --skip-search: Skip examples that require actual search operations
"""

import os
import sys
import argparse
import importlib.util
from typing import List, Dict, Any

def load_module_from_file(file_path: str, module_name: str):
    """Load a Python module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"❌ Failed to load {file_path}: {e}")
        return None

def run_example(file_path: str, example_name: str, demo_mode: bool = False) -> Dict[str, Any]:
    """Run a single example and return results."""
    print(f"\n{'='*60}")
    print(f"🚀 Running: {example_name}")
    print(f"📁 File: {file_path}")
    print(f"{'='*60}")
    
    if demo_mode:
        print("🎭 DEMO MODE: Simulating execution without API calls")
    
    try:
        # Load and execute the module
        module = load_module_from_file(file_path, example_name.replace(' ', '_'))
        
        if module and hasattr(module, 'main'):
            if demo_mode:
                # In demo mode, we'll just validate the module loads
                print("✅ Module loaded successfully")
                print("✅ Main function found")
                return {'status': 'success', 'mode': 'demo'}
            else:
                # Run the actual main function
                module.main()
                return {'status': 'success', 'mode': 'live'}
        else:
            print("❌ Module does not have a main() function")
            return {'status': 'error', 'error': 'No main function'}
            
    except Exception as e:
        print(f"❌ Error running {example_name}: {e}")
        return {'status': 'error', 'error': str(e)}

def check_environment() -> bool:
    """Check if the environment is properly configured."""
    print("🔍 Checking Environment Configuration...")
    
    required_vars = ['SEARCH_ENDPOINT', 'SEARCH_API_KEY', 'INDEX_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Create a .env file with the required variables or set them in your environment")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def main():
    """Main function to run all examples."""
    parser = argparse.ArgumentParser(description='Run all Azure AI Search filter examples')
    parser.add_argument('--demo-mode', action='store_true', 
                       help='Run in demo mode (no API calls)')
    parser.add_argument('--skip-search', action='store_true',
                       help='Skip examples that require search operations')
    
    args = parser.parse_args()
    
    print("🎯 Azure AI Search - Filters & Sorting Examples")
    print("=" * 55)
    
    # Check environment unless in demo mode
    if not args.demo_mode and not check_environment():
        if not args.skip_search:
            print("\n💡 Use --demo-mode to run without API calls")
            print("💡 Use --skip-search to skip search-dependent examples")
            return
    
    # Define examples to run
    examples = [
        {
            'file': '01_basic_filters.py',
            'name': 'Basic Filters',
            'description': 'Equality, comparison, and boolean logic filters',
            'requires_search': True
        },
        {
            'file': '02_range_filters.py',
            'name': 'Range Filters',
            'description': 'Numeric and date range filtering',
            'requires_search': True
        },
        {
            'file': '03_string_filters.py',
            'name': 'String Filters',
            'description': 'Text matching and pattern filtering',
            'requires_search': True
        },
        {
            'file': '04_date_filters.py',
            'name': 'Date Filters',
            'description': 'Date range and temporal filtering',
            'requires_search': True
        },
        {
            'file': '05_geographic_filters.py',
            'name': 'Geographic Filters',
            'description': 'Distance-based and spatial filtering',
            'requires_search': True
        },
        {
            'file': '06_sorting_operations.py',
            'name': 'Sorting Operations',
            'description': 'Single and multi-field sorting',
            'requires_search': True
        },
        {
            'file': '07_complex_filters.py',
            'name': 'Complex Filters',
            'description': 'Collection filtering and nested conditions',
            'requires_search': True
        },
        {
            'file': '08_performance_analysis.py',
            'name': 'Performance Analysis',
            'description': 'Query performance monitoring and optimization',
            'requires_search': True
        }
    ]
    
    # Filter examples based on arguments
    if args.skip_search:
        examples = [ex for ex in examples if not ex['requires_search']]
    
    results = []
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n📊 Running {len(examples)} examples...")
    if args.demo_mode:
        print("🎭 Demo mode enabled - no API calls will be made")
    if args.skip_search:
        print("⏭️  Skipping search-dependent examples")
    
    # Run each example
    for i, example in enumerate(examples, 1):
        file_path = os.path.join(base_path, example['file'])
        
        if not os.path.exists(file_path):
            print(f"\n❌ File not found: {file_path}")
            results.append({
                'name': example['name'],
                'status': 'error',
                'error': 'File not found'
            })
            continue
        
        print(f"\n[{i}/{len(examples)}] {example['name']}")
        print(f"📝 {example['description']}")
        
        result = run_example(file_path, example['name'], args.demo_mode)
        result['name'] = example['name']
        results.append(result)
        
        # Add a small delay between examples
        import time
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 EXECUTION SUMMARY")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📊 Total: {len(results)}")
    
    if successful:
        print(f"\n✅ Successful Examples:")
        for result in successful:
            mode_indicator = "🎭" if result.get('mode') == 'demo' else "🔍"
            print(f"   {mode_indicator} {result['name']}")
    
    if failed:
        print(f"\n❌ Failed Examples:")
        for result in failed:
            print(f"   • {result['name']}: {result.get('error', 'Unknown error')}")
    
    # Final recommendations
    print(f"\n💡 Next Steps:")
    if failed and not args.demo_mode:
        print("   • Check your .env configuration for failed examples")
        print("   • Ensure your Azure AI Search service is accessible")
        print("   • Verify your index schema supports the required fields")
    
    if args.demo_mode:
        print("   • Run without --demo-mode to execute actual searches")
        print("   • Configure your .env file with Azure AI Search credentials")
    
    print("   • Explore individual examples for detailed learning")
    print("   • Modify examples to work with your specific data")
    print("   • Check the notebooks for interactive learning experiences")
    
    print(f"\n🎉 Examples execution completed!")
    
    # Return appropriate exit code
    return 0 if not failed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)