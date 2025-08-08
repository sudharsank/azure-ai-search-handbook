"""
Jupyter Notebook Generator
Converts Python code samples to interactive Jupyter notebooks
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


def create_notebook_cell(cell_type: str, source: List[str], metadata: Dict = None) -> Dict[str, Any]:
    """Create a notebook cell"""
    cell = {
        "cell_type": cell_type,
        "metadata": metadata or {},
        "source": source
    }
    
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    
    return cell


def python_to_notebook(python_file: Path, output_file: Path = None) -> Path:
    """Convert a Python file to a Jupyter notebook"""
    if output_file is None:
        output_file = python_file.with_suffix('.ipynb')
    
    # Read the Python file
    with open(python_file, 'r', encoding='utf-8') as f:
        python_content = f.read()
    
    # Split content into sections
    cells = []
    current_section = []
    in_docstring = False
    docstring_delimiter = None
    
    lines = python_content.split('\n')
    
    # Add title cell
    title = python_file.stem.replace('_', ' ').title()
    cells.append(create_notebook_cell(
        "markdown",
        [f"# {title}\n", "\n", "Interactive code samples for Azure AI Search\n"]
    ))
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for docstrings
        if '"""' in line or "'''" in line:
            if not in_docstring:
                # Starting a docstring
                in_docstring = True
                docstring_delimiter = '"""' if '"""' in line else "'''"
                
                # If we have accumulated code, create a code cell
                if current_section and any(l.strip() for l in current_section):
                    cells.append(create_notebook_cell("code", current_section + [""]))
                    current_section = []
                
                # Start collecting docstring content
                docstring_content = []
                if line.strip() != docstring_delimiter:
                    # Content on the same line as opening delimiter
                    content = line.split(docstring_delimiter, 1)[1]
                    if docstring_delimiter in content:
                        # Closing delimiter on same line
                        docstring_content.append(content.split(docstring_delimiter)[0])
                        in_docstring = False
                    else:
                        docstring_content.append(content)
                
            else:
                # Ending a docstring
                if docstring_delimiter in line:
                    content = line.split(docstring_delimiter)[0]
                    if content:
                        docstring_content.append(content)
                    
                    # Create markdown cell from docstring
                    if docstring_content:
                        # Clean up the docstring content
                        cleaned_content = []
                        for doc_line in docstring_content:
                            cleaned_content.append(doc_line.rstrip() + "\n")
                        cells.append(create_notebook_cell("markdown", cleaned_content))
                    
                    in_docstring = False
                    docstring_content = []
                else:
                    docstring_content.append(line)
        
        elif in_docstring:
            docstring_content.append(line)
        
        else:
            # Regular code line
            current_section.append(line)
        
        i += 1
    
    # Add any remaining code
    if current_section and any(l.strip() for l in current_section):
        cells.append(create_notebook_cell("code", current_section))
    
    # Create the notebook structure
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Write the notebook
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    return output_file


def generate_all_notebooks(docs_dir: Path = None) -> List[Path]:
    """Generate notebooks for all Python code samples"""
    if docs_dir is None:
        docs_dir = Path("docs")
    
    generated_notebooks = []
    
    # Find all Python files in code-samples directories
    for python_file in docs_dir.rglob("code-samples/*.py"):
        try:
            notebook_file = python_to_notebook(python_file)
            generated_notebooks.append(notebook_file)
            print(f"✅ Generated notebook: {notebook_file}")
        except Exception as e:
            print(f"❌ Failed to generate notebook for {python_file}: {e}")
    
    return generated_notebooks


def create_exercise_notebook(exercise_file: Path, output_file: Path = None) -> Path:
    """Create an exercise notebook with instructions and starter code"""
    if output_file is None:
        output_file = exercise_file.with_suffix('.ipynb')
    
    # Read the exercise file
    with open(exercise_file, 'r', encoding='utf-8') as f:
        exercise_content = f.read()
    
    cells = []
    
    # Add title and instructions
    exercise_name = exercise_file.stem.replace('_', ' ').title()
    cells.append(create_notebook_cell(
        "markdown",
        [
            f"# {exercise_name}\n",
            "\n",
            "## Instructions\n",
            "\n",
            "Complete the exercises below. Each cell contains a task with starter code.\n",
            "Run each cell and modify the code as needed to complete the exercises.\n",
            "\n",
            "## Setup\n",
            "\n",
            "First, let's import the required libraries and set up our environment:\n"
        ]
    ))
    
    # Add setup cell
    setup_code = [
        "# Setup and imports\n",
        "import os\n",
        "import sys\n",
        "from pathlib import Path\n",
        "\n",
        "# Add the project root to the path\n",
        "project_root = Path().resolve()\n",
        "while not (project_root / 'setup').exists() and project_root != project_root.parent:\n",
        "    project_root = project_root.parent\n",
        "sys.path.append(str(project_root))\n",
        "\n",
        "print(f\"Project root: {project_root}\")\n"
    ]
    cells.append(create_notebook_cell("code", setup_code))
    
    # Parse the exercise file and create cells
    lines = exercise_content.split('\n')
    current_code = []
    current_exercise = 1
    
    for line in lines:
        if line.strip().startswith('# Exercise') or line.strip().startswith('## Exercise'):
            # New exercise section
            if current_code:
                cells.append(create_notebook_cell("code", current_code + [""]))
                current_code = []
            
            # Add exercise header
            cells.append(create_notebook_cell(
                "markdown",
                [f"## Exercise {current_exercise}\n", "\n", f"{line.strip()[1:].strip()}\n"]
            ))
            current_exercise += 1
        
        elif line.strip().startswith('"""') and 'TODO' in line:
            # Exercise instruction
            cells.append(create_notebook_cell(
                "markdown",
                [line.replace('"""', '').replace('TODO:', '**TODO:**').strip() + "\n"]
            ))
        
        else:
            current_code.append(line)
    
    # Add any remaining code
    if current_code and any(l.strip() for l in current_code):
        cells.append(create_notebook_cell("code", current_code))
    
    # Create the notebook
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Write the notebook
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    return output_file


def generate_all_exercise_notebooks(docs_dir: Path = None) -> List[Path]:
    """Generate exercise notebooks for all Python exercise files"""
    if docs_dir is None:
        docs_dir = Path("docs")
    
    generated_notebooks = []
    
    # Find all Python files in exercises directories
    for exercise_file in docs_dir.rglob("exercises/*.py"):
        try:
            notebook_file = create_exercise_notebook(exercise_file)
            generated_notebooks.append(notebook_file)
            print(f"✅ Generated exercise notebook: {notebook_file}")
        except Exception as e:
            print(f"❌ Failed to generate exercise notebook for {exercise_file}: {e}")
    
    return generated_notebooks


def main():
    """Main function to generate all notebooks"""
    print("📓 Generating Jupyter notebooks from Python files...")
    
    # Generate code sample notebooks
    print("\n🔬 Generating code sample notebooks...")
    code_notebooks = generate_all_notebooks()
    
    # Generate exercise notebooks
    print("\n📝 Generating exercise notebooks...")
    exercise_notebooks = generate_all_exercise_notebooks()
    
    total_notebooks = len(code_notebooks) + len(exercise_notebooks)
    print(f"\n✅ Generated {total_notebooks} notebooks total:")
    print(f"   📊 Code samples: {len(code_notebooks)}")
    print(f"   📝 Exercises: {len(exercise_notebooks)}")
    
    if total_notebooks > 0:
        print("\n📋 To use the notebooks:")
        print("1. Make sure Jupyter is installed: pip install jupyter")
        print("2. Start Jupyter: jupyter notebook")
        print("3. Navigate to the generated .ipynb files")
    
    return total_notebooks > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)