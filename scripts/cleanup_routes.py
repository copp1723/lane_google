#!/usr/bin/env python3
"""
Route Cleanup Script for Lane Google
Helps identify and optionally remove duplicate/obsolete files
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Files to be deleted or backed up
FILES_TO_DELETE = [
    # Duplicate blueprints
    'backend/src/api/health.py',  # Conflicts with src/routes/health.py
    'backend/src/api/ai_agent_api.py',  # Conflicts with src/routes/ai_agent.py
    
    # Files with blueprints that should only contain models/services
    # Note: These need manual review to extract blueprint code
    # 'backend/src/models/analytics.py',
    # 'backend/src/models/campaigns.py',
    # 'backend/src/services/google_ads.py',
    
    # Already backed up files
    'src/main_production.py.backup',
    'src/main_unified.py.backup',
]

FILES_TO_REVIEW = [
    # These files contain blueprints mixed with models/services
    'backend/src/models/analytics.py',
    'backend/src/models/campaigns.py', 
    'backend/src/services/google_ads.py',
]

CACHE_PATTERNS = [
    '**/__pycache__',
    '**/*.pyc',
    '**/*.pyo',
    '**/*.pyd',
    '**/node_modules',
    '**/.pytest_cache',
    '**/.coverage',
]


def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


def create_backup_dir():
    """Create a backup directory with timestamp"""
    root = get_project_root()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = root / f'backups/route_cleanup_{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def backup_file(file_path: Path, backup_dir: Path):
    """Backup a file before deletion"""
    if file_path.exists():
        relative_path = file_path.relative_to(get_project_root())
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        print(f"  Backed up: {relative_path}")
        return True
    return False


def clean_cache_files(dry_run=True):
    """Clean cache files and directories"""
    root = get_project_root()
    cleaned = []
    
    for pattern in CACHE_PATTERNS:
        for path in root.glob(pattern):
            if dry_run:
                print(f"  Would delete: {path.relative_to(root)}")
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                cleaned.append(str(path.relative_to(root)))
    
    return cleaned


def analyze_blueprints():
    """Analyze blueprint usage across the project"""
    root = get_project_root()
    blueprint_files = {}
    
    # Find all Python files with Blueprint definitions
    for py_file in root.glob('**/*.py'):
        if 'node_modules' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                if 'Blueprint(' in content and 'from flask import' in content:
                    # Extract blueprint names
                    import re
                    blueprints = re.findall(r'(\w+)\s*=\s*Blueprint\s*\(', content)
                    if blueprints:
                        blueprint_files[str(py_file.relative_to(root))] = blueprints
        except Exception as e:
            pass
    
    return blueprint_files


def main():
    """Main cleanup function"""
    print("Lane Google Route Cleanup Script")
    print("=" * 50)
    
    root = get_project_root()
    
    # Analyze blueprints
    print("\n1. Analyzing Blueprint Definitions...")
    blueprints = analyze_blueprints()
    for file_path, bp_names in sorted(blueprints.items()):
        print(f"  {file_path}: {', '.join(bp_names)}")
    
    # Check files to delete
    print("\n2. Files Marked for Deletion:")
    files_exist = []
    for file_path in FILES_TO_DELETE:
        full_path = root / file_path
        if full_path.exists():
            files_exist.append(full_path)
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (not found)")
    
    # Check files to review
    print("\n3. Files Requiring Manual Review:")
    for file_path in FILES_TO_REVIEW:
        full_path = root / file_path
        if full_path.exists():
            print(f"  ⚠ {file_path}")
            if file_path in blueprints:
                print(f"    Contains blueprints: {', '.join(blueprints[file_path])}")
    
    # Check cache files
    print("\n4. Cache Files to Clean:")
    clean_cache_files(dry_run=True)
    
    # Prompt for action
    if files_exist:
        print("\n" + "=" * 50)
        response = input("Do you want to proceed with cleanup? (yes/no/dry-run): ").lower()
        
        if response == 'yes':
            # Create backup
            backup_dir = create_backup_dir()
            print(f"\nCreating backups in: {backup_dir}")
            
            # Backup and delete files
            for file_path in files_exist:
                if backup_file(file_path, backup_dir):
                    file_path.unlink()
                    print(f"  Deleted: {file_path.relative_to(root)}")
            
            # Clean cache
            print("\nCleaning cache files...")
            cleaned = clean_cache_files(dry_run=False)
            print(f"  Cleaned {len(cleaned)} cache files/directories")
            
            print(f"\nCleanup complete! Backups saved to: {backup_dir}")
            
        elif response == 'dry-run':
            print("\nDry run - no changes made")
            print("Files that would be deleted:")
            for file_path in files_exist:
                print(f"  - {file_path.relative_to(root)}")
    else:
        print("\nNo files to delete. Project is clean!")
    
    # Final recommendations
    print("\n" + "=" * 50)
    print("Recommendations:")
    print("1. Manually review files in FILES_TO_REVIEW list")
    print("2. Extract blueprint code from model/service files")
    print("3. Update imports to use new route registry")
    print("4. Run tests to ensure everything works")
    print("5. Delete backup directory after confirming everything works")


if __name__ == '__main__':
    main()