#!/usr/bin/env python3
"""Fix incorrect imports in API files"""

import os
import re

def fix_response_imports():
    """Fix incorrect response imports in API files"""
    
    api_dir = 'src/api'
    fixed_files = []
    
    for filename in os.listdir(api_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(api_dir, filename)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Fix response imports
            content = re.sub(
                r'from src\.utils\.responses import APIResponse',
                'from src.utils.flask_responses import APIResponse',
                content
            )
            
            # Fix other response utility imports
            content = re.sub(
                r'from src\.utils\.responses import (\w+)',
                r'from src.utils.flask_responses import \1',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                fixed_files.append(filename)
                print(f"✓ Fixed imports in {filename}")
    
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for f in fixed_files:
            print(f"  - {f}")
    else:
        print("No files needed fixing")

if __name__ == "__main__":
    fix_response_imports()
    print("\nImport fixes complete!")