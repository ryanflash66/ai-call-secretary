#!/usr/bin/env python3
"""
Script to convert UTF-16 files to UTF-8.
This script identifies files with null bytes (common in UTF-16) and converts them to UTF-8.
"""
import os
import sys
import subprocess
from pathlib import Path

def detect_files_with_null_bytes(root_dir='.'):
    """Find files with null bytes, which likely indicates UTF-16 encoding."""
    command = f"find {root_dir} -type f -name '*.py' -exec grep -l \"$(printf '\\0')\" {{}} \\; 2>/dev/null"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    files = result.stdout.splitlines()
    return files

def convert_file_to_utf8(file_path):
    """Convert a file from UTF-16 to UTF-8."""
    try:
        print(f"Converting {file_path} to UTF-8...")
        temp_path = f"{file_path}.utf8"
        
        # Detect the current encoding
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Try different encodings
        for encoding in ['utf-16le', 'utf-16be', 'utf-16']:
            try:
                decoded = content.decode(encoding)
                # If we get here, the encoding works
                print(f"  Detected {encoding} encoding")
                
                # Write as UTF-8
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(decoded)
                
                # Replace the original file
                os.replace(temp_path, file_path)
                print(f"  Successfully converted {file_path}")
                return True
            except UnicodeDecodeError:
                continue
        
        # If we get here, none of the encodings worked
        print(f"  ERROR: Could not determine encoding for {file_path}")
        return False
    
    except Exception as e:
        print(f"  ERROR: Failed to convert {file_path}: {str(e)}")
        return False

def main():
    """Main function to find and convert files."""
    root_dir = '.'
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    
    files = detect_files_with_null_bytes(root_dir)
    
    if not files:
        print("No files with null bytes found. All files appear to be properly encoded.")
        return
    
    print(f"Found {len(files)} files with potential encoding issues:")
    for file in files:
        print(f" - {file}")
    
    print("\nConverting files to UTF-8...")
    success_count = 0
    failure_count = 0
    
    for file in files:
        if convert_file_to_utf8(file):
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\nConversion complete: {success_count} files converted, {failure_count} files failed.")

if __name__ == "__main__":
    main()