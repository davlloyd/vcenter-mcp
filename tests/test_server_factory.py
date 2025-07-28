"""
Tests for the server factory.
"""

import pytest
from unittest.mock import Mock, patch
from fastmcp import FastMCP

from main.server_factory import create_mcp_server, create_mcp_server_with_config
from main.models.vcenter_config import VCenterConfig


class TestServerFactory:
    """Test the server factory functionality."""
    
    @patch('main.server_factory.ConfigManager')
    @patch('main.server_factory.VCenterController')
    @patch('main.server_factory.MCPToolsView')
    @patch('main.server_factory.FastMCP')
    def test_create_mcp_server(self, mock_fastmcp, mock_view, mock_controller, mock_config_manager):
        """Test creating MCP server with default configuration."""
        # Setup mocks
        mock_config = Mock(spec=VCenterConfig)
        mock_config.host = "https://test-vcenter.com"
        mock_config_manager.return_value.get_vcenter_config.return_value = mock_config
        
        mock_controller_instance = Mock()
        mock_controller.return_value = mock_controller_instance
        
        mock_view_instance = Mock()
        mock_view.return_value = mock_view_instance
        
        mock_app = Mock(spec=FastMCP)
        mock_fastmcp.return_value = mock_app
        
        # Test
        result = create_mcp_server()
        
        # Verify
        assert result == mock_app
        mock_config_manager.assert_called_once()
        mock_controller.assert_called_once_with(mock_config)
        mock_view.assert_called_once_with(mock_controller_instance)
        mock_view_instance.register_tools.assert_called_once_with(mock_app)
    
    @patch('main.server_factory.VCenterController')
    @patch('main.server_factory.MCPToolsView')
    @patch('main.server_factory.FastMCP')
    def test_create_mcp_server_with_config(self, mock_fastmcp, mock_view, mock_controller):
        """Test creating MCP server with specific configuration."""
        # Setup mocks
        mock_config = Mock(spec=VCenterConfig)
        mock_config.host = "https://test-vcenter.com"
        
        mock_controller_instance = Mock()
        mock_controller.return_value = mock_controller_instance
        
        mock_view_instance = Mock()
        mock_view.return_value = mock_view_instance
        
        mock_app = Mock(spec=FastMCP)
        mock_fastmcp.return_value = mock_app
        
        # Test
        result = create_mcp_server_with_config(mock_config)
        
        # Verify
        assert result == mock_app
        mock_controller.assert_called_once_with(mock_config)
        mock_view.assert_called_once_with(mock_controller_instance)
        mock_view_instance.register_tools.assert_called_once_with(mock_app)
    
    @patch('main.server_factory.ConfigManager')
    def test_create_mcp_server_config_error(self, mock_config_manager):
        """Test error handling when configuration fails."""
        # Setup mock to raise exception
        mock_config_manager.return_value.get_vcenter_config.side_effect = Exception("Config error")
        
        # Test
        with pytest.raises(Exception, match="Config error"):
            create_mcp_server()
    
    @patch('main.server_factory.ConfigManager')
    @patch('main.server_factory.VCenterController')
    def test_create_mcp_server_controller_error(self, mock_controller, mock_config_manager):
        """Test error handling when controller initialization fails."""
        # Setup mocks
        mock_config = Mock(spec=VCenterConfig)
        mock_config.host = "https://test-vcenter.com"
        mock_config_manager.return_value.get_vcenter_config.return_value = mock_config
        
        mock_controller.side_effect = Exception("Controller error")
        
        # Test
        with pytest.raises(Exception, match="Controller error"):
            create_mcp_server()


class TestServerFactoryIntegration:
    """Integration tests for server factory."""
    
    def test_server_factory_import(self):
        """Test that server factory can be imported without circular imports."""
        try:
            from main.server_factory import create_mcp_server, create_mcp_server_with_config
            assert callable(create_mcp_server)
            assert callable(create_mcp_server_with_config)
        except ImportError as e:
            pytest.fail(f"Failed to import server factory: {e}")
    
    def test_mvc_components_import(self):
        """Test that all MVC components can be imported together."""
        try:
            from main.controllers.vcenter_controller import VCenterController
            from main.views.mcp_tools import MCPToolsView
            from main.services.vcenter_service import VCenterService
            from main.config.config_manager import ConfigManager
            assert True  # If we get here, no circular imports
        except ImportError as e:
            pytest.fail(f"Failed to import MVC components: {e}") 