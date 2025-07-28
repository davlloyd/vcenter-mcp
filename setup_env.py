#!/usr/bin/env python3
"""
Environment Setup Script

This script helps you create a .env file for the vCenter MCP Server.
It will copy the template and prompt you for the required values.
"""

import os
import shutil
from pathlib import Path


def setup_environment():
    """Set up the environment configuration file."""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Check if template exists
    if not os.path.exists('config.env.example'):
        print("❌ config.env.example template not found!")
        print("Please ensure the template file exists.")
        return
    
    print("🚀 Setting up vCenter MCP Server environment...")
    print()
    
    # Copy template to .env
    shutil.copy('config.env.example', '.env')
    print("✅ Created .env file from template")
    print()
    
    # Prompt for configuration values
    print("Please provide your vCenter server details:")
    print()
    
    # Get vCenter host
    host = input("vCenter Host URL (e.g., https://vcenter.example.com): ").strip()
    if host:
        update_env_value('VCENTER_HOST', host)
    
    # Get username
    username = input("vCenter Username: ").strip()
    if username:
        update_env_value('VCENTER_USERNAME', username)
    
    # Get password
    password = input("vCenter Password: ").strip()
    if password:
        update_env_value('VCENTER_PASSWORD', password)
    
    # Get SSL verification preference
    ssl_verify = input("Verify SSL certificates? (Y/n): ").lower().strip()
    if ssl_verify == 'n':
        update_env_value('VCENTER_VERIFY_SSL', 'false')
    
    # Get timeout
    timeout = input("Request timeout in seconds (default: 30): ").strip()
    if timeout and timeout.isdigit():
        update_env_value('VCENTER_TIMEOUT', timeout)
    
    # Get log level
    log_level = input("Log level (DEBUG/INFO/WARNING/ERROR, default: INFO): ").strip().upper()
    if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        update_env_value('LOG_LEVEL', log_level)
    
    print()
    print("✅ Environment setup complete!")
    print()
    print("Next steps:")
    print("1. Verify your .env file contains the correct values")
    print("2. Test your connection: python test_connection.py")
    print("3. Run the MCP server: python -m main")
    print()
    print("Note: Keep your .env file secure and never commit it to version control.")


def update_env_value(key, value):
    """Update a specific value in the .env file."""
    if not os.path.exists('.env'):
        return
    
    # Read current .env file
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update the specific key
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            updated = True
            break
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.writelines(lines)
    
    if updated:
        print(f"✅ Updated {key}")
    else:
        print(f"⚠️  Could not find {key} in .env file")


def show_current_config():
    """Show the current configuration values."""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Run this script to create one.")
        return
    
    print("📋 Current configuration:")
    print()
    
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if 'PASSWORD' in key:
                    # Mask password for security
                    masked_value = '*' * min(len(value), 8)
                    print(f"{key}={masked_value}")
                else:
                    print(f"{key}={value}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'show':
        show_current_config()
    else:
        setup_environment() 