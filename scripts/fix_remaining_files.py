#!/usr/bin/env python3
"""
Script to manually fix files with encoding issues.
This script directly reads and rewrites problematic files by removing null bytes.
"""
import os
import sys

def clean_file(file_path):
    """Clean a file by removing null bytes and ensuring UTF-8 encoding."""
    try:
        print(f"Cleaning {file_path}...")
        # Read the file in binary mode
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Remove null bytes
        cleaned_content = content.replace(b'\x00', b'')
        
        # Try to decode with utf-8
        try:
            text = cleaned_content.decode('utf-8')
            
            # Write back as UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"  Successfully cleaned {file_path}")
            return True
        except UnicodeDecodeError:
            print(f"  ERROR: Could not decode cleaned content for {file_path}")
            return False
    except Exception as e:
        print(f"  ERROR: Failed to clean {file_path}: {str(e)}")
        return False

def main():
    """Main function to clean problematic files."""
    # List of files that failed conversion previously
    problem_files = [
        "src/api/app.py",
        "src/api/security_schemas.py",
        "src/llm/context.py",
        "src/llm/ollama_client.py",
        "src/llm/prompts.py",
        "src/middleware/performance.py",
        "src/middleware/rate_limit.py",
        "src/middleware/web_optimization.py",
        "src/performance_config.py",
        "src/security/audit_log.py",
        "src/security/utils.py",
        "src/security/__init__.py",
        "src/security_config.py",
        "src/telephony/freeswitch/scripts/call_handler.py",
        "src/workflow/flows/appointment_flow.py",
        "src/workflow/flows/flow_manager.py",
        "src/workflow/flows/general_flow.py",
        "src/workflow/flows/message_flow.py",
        "src/workflow/__init__.py"
    ]
    
    if len(sys.argv) > 1:
        # Get problem files from arguments
        problem_files = sys.argv[1:]
    
    print(f"Found {len(problem_files)} problematic files:")
    for file in problem_files:
        print(f" - {file}")
    
    print("\nCleaning files...")
    success_count = 0
    failure_count = 0
    
    for file in problem_files:
        if clean_file(file):
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\nCleaning complete: {success_count} files cleaned, {failure_count} files failed.")

if __name__ == "__main__":
    main()