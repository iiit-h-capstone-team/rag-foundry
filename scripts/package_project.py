#!/usr/bin/env python3
"""
Script to package the RAG Foundry project for distribution.
Excludes venv, cache, and other unnecessary directories.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def should_exclude(path, exclude_patterns):
    """Check if a path should be excluded based on patterns."""
    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    return False

def create_project_zip(project_root=None, output_dir=None):
    """
    Create a zip file of the project excluding venv and cache directories.
    
    Args:
        project_root: Path to the project root directory (defaults to parent of scripts folder)
        output_dir: Directory to save the zip file (defaults to project root)
    """
    if project_root is None:
        # Auto-detect project root as parent of scripts directory
        project_root = Path(__file__).parent.parent.resolve()
    else:
        project_root = Path(project_root).resolve()
    
    if output_dir is None:
        output_dir = project_root
    else:
        output_dir = Path(output_dir).resolve()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Patterns to exclude
    exclude_patterns = [
        '/venv/',
        '/.venv/',
        '/env/',
        '/.env/',
        '/__pycache__/',
        '/.pytest_cache/',
        '/.git/',
        '/.github/',
        '/.DS_Store',
        '/.idea/',
        '/.vscode/',
        '*.pyc',
        '*.pyo',
        '*.egg-info/',
        '/dist/',
        '/build/',
        '/node_modules/',
        '.egg-info',
        '/cache/',
        '/.cache/',
        '/vectorstore/',
        '/temp/',
        '/temp-deprecated/',
        '/reports/',
        '/.ipynb_checkpoints/',
        '.zip',
        '.rar',
        '.tar',
        '.gz',
    ]
    
    # Create zip filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"rag-foundry_{timestamp}.zip"
    zip_path = output_dir / zip_filename
    
    print(f"Creating zip file: {zip_path}")
    print(f"Project root: {project_root}")
    print(f"Excluding patterns: {exclude_patterns}")
    print()
    
    file_count = 0
    excluded_count = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip excluded files
                if should_exclude(str(file_path), exclude_patterns):
                    excluded_count += 1
                    continue
                
                # Calculate relative path for archive
                try:
                    rel_path = file_path.relative_to(project_root)
                    arcname = f"rag-foundry/{rel_path}"
                    zipf.write(file_path, arcname)
                    file_count += 1
                    print(f"Added: {rel_path}")
                except Exception as e:
                    print(f"Error adding {file_path}: {e}")
                    excluded_count += 1
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print()
    print("=" * 60)
    print(f"✓ Zip file created successfully!")
    print(f"  Location: {zip_path}")
    print(f"  Size: {zip_size_mb:.2f} MB")
    print(f"  Files included: {file_count}")
    print(f"  Files excluded: {excluded_count}")
    print("=" * 60)
    print()
    print("To use on another computer:")
    print("  1. Unzip the file")
    print("  2. cd rag-foundry")
    print("  3. python -m venv venv")
    print("  4. source venv/bin/activate  (or venv\\Scripts\\activate on Windows)")
    print("  5. pip install -r requirements.txt")
    
    return zip_path

if __name__ == "__main__":
    import sys
    
    # Auto-detect project root (parent of scripts directory)
    project_root = None
    
    # Optional: specify custom output directory
    output_dir = None
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    
    create_project_zip(project_root, output_dir)
