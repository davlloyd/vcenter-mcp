#!/usr/bin/env python3
"""
VMware vCenter MCP Server - Main Entry Point

This is the main entry point for the vCenter MCP server using MVC architecture.
For development and deployment, use this file directly.
"""

import sys
import os

# Add main to path for development
sys.path.insert(0, os.path.dirname(__file__))

from main.__main__ import main

if __name__ == "__main__":
    main() 