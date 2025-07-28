"""
Server Factory.

This module creates and configures the MCP server with proper MVC initialization.
"""

import logging
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config.config_manager import ConfigManager
from .controllers.vcenter_controller import VCenterController
from .views.mcp_tools import MCPToolsView

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """
    Create and configure the MCP server with proper MVC initialization.
    
    Returns:
        Configured FastMCP server instance
    """
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        logger.info(f"Configuration loaded for vCenter at {config.host}")
        
        # Initialize controller
        controller = VCenterController(config)
        logger.info("vCenter controller initialized")
        
        # Initialize view with controller
        view = MCPToolsView(controller)
        logger.info("MCP tools view initialized")
        
        # Create and configure FastMCP application
        app = FastMCP("vcenter-mcp")
        
        # Add health check endpoint
        @app.custom_route("/health", methods=["GET"])
        async def health_check(request: Request) -> JSONResponse:
            """Health check endpoint for Cloud Foundry."""
            return JSONResponse({
                "status": "healthy",
                "service": "vcenter-mcp",
                "version": "1.0.0"
            })
        
        # Register MCP tools
        view.register_tools(app)
        logger.info("MCP tools and health check endpoint registered")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        raise


def create_mcp_server_with_config(config) -> FastMCP:
    """
    Create MCP server with a specific configuration.
    
    Args:
        config: VCenterConfig instance
        
    Returns:
        Configured FastMCP server instance
    """
    try:
        # Initialize controller
        controller = VCenterController(config)
        logger.info("vCenter controller initialized")
        
        # Initialize view with controller
        view = MCPToolsView(controller)
        logger.info("MCP tools view initialized")
        
        # Create and configure FastMCP application
        app = FastMCP("vcenter-mcp")
        
        # Add health check endpoint
        @app.custom_route("/health", methods=["GET"])
        async def health_check(request: Request) -> JSONResponse:
            """Health check endpoint for Cloud Foundry."""
            return JSONResponse({
                "status": "healthy",
                "service": "vcenter-mcp",
                "version": "1.0.0"
            })
        
        # Register MCP tools
        view.register_tools(app)
        logger.info("MCP tools and health check endpoint registered")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        raise 