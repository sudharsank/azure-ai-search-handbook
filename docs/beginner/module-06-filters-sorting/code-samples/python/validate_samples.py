#!/usr/bin/env python3
"""
Validate Python Samples

This script validates all Python samples for syntax errors and basic structure.
It's useful for ensuring code quality before deployment or distribution.

Usage:
    python validate_samples.py
"""

import os
import ast
import sys
from typing import List, Dict, Any

def validate_python_syntax(file_path: str) -> Dict[str, Any]:
    """Validate Python file syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        
        return {
            'valid': True,
            'error': None,
            'lines': len(content.splitlines()),
            'size': len(content)
        }
        
    except SyntaxError as e:
        return {
            'valid': False,
            'error': f"Syntax error at line {e.lineno}: {e.msg}",
            'lines': 0,
            'size': 0
        }
    except Exception as e:
        return {
            'valid': False,
            'error': f"Error reading file: {e}",
            'lines': 0,
            'size': 0
        }

def check_required_functions(file_path: str) -> Dict[str, Any]:
    """Check if file has required functions and structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        has_main = 'main' in functions
        has_azure_imports = any('azure' in imp for imp in imports)
        has_docstring = ast.get_docstring(tree) is not None
        
        return {
            'has_main': has_main,
            'has_azure_imports': has_azure_imports,
            'has_docstring': has_docstring,
            'functions': functions,
            'classes': classes,
            'imports': imports
        }
        
    except Exception as e:
        return {
            'error': f"Error analyzing structure: {e}",
            'has_main': False,
            'has_azure_imports': False,
            'has_docstring': False,
            'functions': [],
            'classes': [],
            'imports': []
        }

def validate_all_samples() -> List[Dict[str, Any]]:
    """Validate all Python samples in the directory."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Find all Python files (excluding this validation script)
    python_files = []
    for file in os.listdir(base_path):
        if (file.endswith('.py') and 
            file != 'validate_samples.py' and 
            not file.startswith('__')):
            python_files.append(file)
    
    results = []
    
    for file in sorted(python_files):
        file_path = os.path.join(base_path, file)
        
        print(f"🔍 Validating {file}...")
        
        # Check syntax
        syntax_result = validate_python_syntax(file_path)
        
        # Check structure
        structure_result = check_required_functions(file_path)
        
        result = {
            'file': file,
            'path': file_path,
            'syntax': syntax_result,
            'structure': structure_result
        }
        
        results.append(result)
        
        # Print immediate feedback
        if syntax_result['valid']:
            print(f"  ✅ Syntax: Valid ({syntax_result['lines']} lines)")
        else:
            print(f"  ❌ Syntax: {syntax_result['error']}")
        
        if 'error' not in structure_result:
            main_status = "✅" if structure_result['has_main'] else "⚠️"
            azure_status = "✅" if structure_result['has_azure_imports'] else "⚠️"
            doc_status = "✅" if structure_result['has_docstring'] else "⚠️"
            
            print(f"  {main_status} Main function: {structure_result['has_main']}")
            print(f"  {azure_status} Azure imports: {structure_result['has_azure_imports']}")
            print(f"  {doc_status} Docstring: {structure_result['has_docstring']}")
            print(f"  📊 Functions: {len(structure_result['functions'])}")
            print(f"  🏗️  Classes: {len(structure_result['classes'])}")
        else:
            print(f"  ❌ Structure: {structure_result['error']}")
    
    return results

def generate_validation_report(results: List[Dict[str, Any]]) -> str:
    """Generate a comprehensive validation report."""
    report = []
    report.append("📊 Python Samples Validation Report")
    report.append("=" * 45)
    report.append(f"Generated: {os.popen('date').read().strip()}")
    report.append("")
    
    # Summary statistics
    total_files = len(results)
    valid_syntax = sum(1 for r in results if r['syntax']['valid'])
    has_main = sum(1 for r in results if r['structure'].get('has_main', False))
    has_azure = sum(1 for r in results if r['structure'].get('has_azure_imports', False))
    has_docs = sum(1 for r in results if r['structure'].get('has_docstring', False))
    
    report.append("📈 Summary Statistics")
    report.append("-" * 20)
    report.append(f"Total Files: {total_files}")
    report.append(f"Valid Syntax: {valid_syntax}/{total_files} ({valid_syntax/total_files*100:.1f}%)")
    report.append(f"Has Main Function: {has_main}/{total_files} ({has_main/total_files*100:.1f}%)")
    report.append(f"Has Azure Imports: {has_azure}/{total_files} ({has_azure/total_files*100:.1f}%)")
    report.append(f"Has Docstring: {has_docs}/{total_files} ({has_docs/total_files*100:.1f}%)")
    report.append("")
    
    # Detailed results
    report.append("📋 Detailed Results")
    report.append("-" * 18)
    
    for result in results:
        file = result['file']
        syntax = result['syntax']
        structure = result['structure']
        
        report.append(f"\n📄 {file}")
        
        if syntax['valid']:
            report.append(f"  ✅ Syntax: Valid ({syntax['lines']} lines, {syntax['size']} bytes)")
        else:
            report.append(f"  ❌ Syntax: {syntax['error']}")
        
        if 'error' not in structure:
            report.append(f"  📊 Functions: {len(structure['functions'])}")
            report.append(f"  🏗️  Classes: {len(structure['classes'])}")
            report.append(f"  📦 Imports: {len(structure['imports'])}")
            
            # Key indicators
            indicators = []
            if structure['has_main']:
                indicators.append("✅ Main")
            else:
                indicators.append("⚠️ No Main")
            
            if structure['has_azure_imports']:
                indicators.append("✅ Azure")
            else:
                indicators.append("⚠️ No Azure")
            
            if structure['has_docstring']:
                indicators.append("✅ Docs")
            else:
                indicators.append("⚠️ No Docs")
            
            report.append(f"  🎯 Status: {' | '.join(indicators)}")
        else:
            report.append(f"  ❌ Structure: {structure['error']}")
    
    # Issues and recommendations
    issues = []
    for result in results:
        if not result['syntax']['valid']:
            issues.append(f"Syntax error in {result['file']}")
        if not result['structure'].get('has_main', False):
            issues.append(f"Missing main() function in {result['file']}")
        if not result['structure'].get('has_azure_imports', False):
            issues.append(f"Missing Azure imports in {result['file']}")
    
    if issues:
        report.append("\n⚠️  Issues Found")
        report.append("-" * 15)
        for issue in issues:
            report.append(f"• {issue}")
    else:
        report.append("\n✅ No Issues Found")
        report.append("-" * 18)
        report.append("All samples passed validation!")
    
    # Recommendations
    report.append("\n💡 Recommendations")
    report.append("-" * 18)
    report.append("• Ensure all samples have comprehensive docstrings")
    report.append("• Add error handling for production use")
    report.append("• Include unit tests for critical functions")
    report.append("• Consider adding type hints for better code clarity")
    report.append("• Validate environment configuration in each sample")
    
    return "\n".join(report)

def main():
    """Main validation function."""
    print("🔍 Azure AI Search Python Samples Validation")
    print("=" * 50)
    
    # Validate all samples
    results = validate_all_samples()
    
    # Generate and display report
    print("\n" + "="*60)
    report = generate_validation_report(results)
    print(report)
    
    # Determine exit code
    syntax_errors = sum(1 for r in results if not r['syntax']['valid'])
    structure_errors = sum(1 for r in results if 'error' in r['structure'])
    
    if syntax_errors > 0 or structure_errors > 0:
        print(f"\n❌ Validation completed with {syntax_errors + structure_errors} issues")
        return 1
    else:
        print(f"\n✅ All {len(results)} samples passed validation!")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)