#!/usr/bin/env python3
"""
Diagnostic script to identify the gunicorn module issue
"""
import os
import sys
import subprocess
import stat
from pathlib import Path

def diagnose_gunicorn_issue():
    print("=== GUNICORN MODULE DIAGNOSIS ===")
    print()
    
    # Check current user
    print(f"Current user: {os.getenv('USER', 'unknown')}")
    print(f"Current UID: {os.getuid()}")
    print(f"Current GID: {os.getgid()}")
    print()
    
    # Check PATH
    path_env = os.getenv('PATH', '')
    print(f"PATH environment variable:")
    for path_dir in path_env.split(':'):
        print(f"  - {path_dir}")
    print()
    
    # Check Python path
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path:")
    for path in sys.path:
        print(f"  - {path}")
    print()
    
    # Check for gunicorn in various locations
    potential_locations = [
        '/home/appuser/.local/bin/gunicorn',
        '/usr/local/bin/gunicorn',
        '/usr/bin/gunicorn',
        '/root/.local/bin/gunicorn'
    ]
    
    print("Checking gunicorn binary locations:")
    for location in potential_locations:
        path = Path(location)
        if path.exists():
            stat_info = path.stat()
            print(f"  ✓ {location} (exists)")
            print(f"    - Size: {stat_info.st_size} bytes")
            print(f"    - Owner UID: {stat_info.st_uid}")
            print(f"    - Owner GID: {stat_info.st_gid}")
            print(f"    - Permissions: {stat.filemode(stat_info.st_mode)}")
            print(f"    - Executable: {os.access(location, os.X_OK)}")
        else:
            print(f"  ✗ {location} (not found)")
    print()
    
    # Check if gunicorn module can be imported
    print("Testing gunicorn module import:")
    try:
        import gunicorn
        print(f"  ✓ gunicorn module found at: {gunicorn.__file__}")
        print(f"  ✓ gunicorn version: {gunicorn.__version__}")
    except ImportError as e:
        print(f"  ✗ Cannot import gunicorn: {e}")
    print()
    
    # Check pip list for gunicorn
    print("Checking installed packages:")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        if 'gunicorn' in result.stdout.lower():
            for line in result.stdout.split('\n'):
                if 'gunicorn' in line.lower():
                    print(f"  ✓ {line.strip()}")
        else:
            print("  ✗ gunicorn not found in pip list")
    except Exception as e:
        print(f"  ✗ Error running pip list: {e}")
    print()
    
    # Check directory permissions
    local_dir = Path('/home/appuser/.local')
    if local_dir.exists():
        print(f"Directory permissions for {local_dir}:")
        for item in [local_dir, local_dir / 'bin', local_dir / 'lib']:
            if item.exists():
                stat_info = item.stat()
                print(f"  {item}: {stat.filemode(stat_info.st_mode)} (UID: {stat_info.st_uid}, GID: {stat_info.st_gid})")
    print()
    
    # Check if we can execute gunicorn directly
    print("Testing gunicorn execution:")
    gunicorn_path = '/home/appuser/.local/bin/gunicorn'
    if Path(gunicorn_path).exists():
        try:
            result = subprocess.run([gunicorn_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            print(f"  ✓ Direct execution result: {result.stdout.strip()}")
        except Exception as e:
            print(f"  ✗ Direct execution failed: {e}")
    
    # Test with python -m gunicorn
    try:
        result = subprocess.run([sys.executable, '-m', 'gunicorn', '--version'], 
                              capture_output=True, text=True, timeout=10)
        print(f"  ✓ Python module execution: {result.stdout.strip()}")
    except Exception as e:
        print(f"  ✗ Python module execution failed: {e}")

if __name__ == "__main__":
    diagnose_gunicorn_issue()