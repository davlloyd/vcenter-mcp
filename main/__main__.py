"""
Main entry point for the vCenter MCP Server.

This module provides the command-line interface for running the MCP server
using the MVC architecture.
"""

import logging
import os
import sys
import asyncio

from .server_factory import create_mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main_async():
    """Async main entry point for the MCP server."""
    try:
        # Get port from Cloud Foundry environment (required for health checks)
        port = int(os.getenv('PORT', 8080))
        host = os.getenv('HOST', '0.0.0.0')
        
        app = create_mcp_server()
        logger.info(f"MCP server initialized, starting with HTTP transport on {host}:{port}...")
        
        # Configure HTTP transport for Spring AI WebMVC compatibility
        await app.run_http_async(
            transport="http", 
            host=host,
            port=port
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main entry point for the MCP server."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 