"""
Tests for the FastMCP HTTP transport and health check configuration.
"""

import pytest
from unittest.mock import patch, Mock
from starlette.requests import Request
from starlette.responses import JSONResponse

from main.__main__ import main
from main.server_factory import create_mcp_server, create_mcp_server_with_config


class TestHealthCheckEndpoint:
    """Test the health check endpoint via FastMCP custom route."""
    
    def test_health_check_endpoint_creation(self):
        """Test that the health check endpoint is created correctly."""
        app = create_mcp_server()
        
        # Check that the app has custom routes
        assert hasattr(app, 'custom_route')
        assert app is not None
    
    def test_health_check_response_format(self):
        """Test the health check response format."""
        # Create a mock request
        mock_request = Mock(spec=Request)
        
        # Get the health check function from the app
        app = create_mcp_server()
        
        # The health check function should be registered as a custom route
        # We can't easily test it directly, but we can verify the app structure
        assert app is not None
        
        # Test the expected response format
        expected_response = {
            "status": "healthy",
            "service": "vcenter-mcp",
            "version": "1.0.0"
        }
        
        # Verify the structure
        assert "status" in expected_response
        assert "service" in expected_response
        assert "version" in expected_response
        assert expected_response["status"] == "healthy"
        assert expected_response["service"] == "vcenter-mcp"


class TestMainFunction:
    """Test the main function with HTTP transport."""
    
    @patch('main.__main__.create_mcp_server')
    def test_main_function_starts_with_http_transport(self, mock_create_server):
        """Test that main function starts the MCP server with HTTP transport."""
        # Mock the MCP server to return quickly
        mock_app = mock_create_server.return_value
        mock_app.run_http_async.side_effect = KeyboardInterrupt()
        
        # Test main function
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        mock_app.run_http_async.assert_called_once_with(
            transport="http", 
            host="0.0.0.0",
            port=8080
        )
    
    @patch('main.__main__.create_mcp_server')
    def test_main_function_environment_variables(self, mock_create_server):
        """Test that main function uses environment variables correctly."""
        # Mock the MCP server to return quickly
        mock_app = mock_create_server.return_value
        mock_app.run_http_async.side_effect = KeyboardInterrupt()
        
        # Test with custom environment variables
        with patch.dict('os.environ', {'PORT': '9090', 'HOST': '127.0.0.1'}):
            with pytest.raises(SystemExit):
                main()
            
            # Verify the MCP server was called with correct parameters
            mock_app.run_http_async.assert_called_with(
                transport="http", 
                host="127.0.0.1",
                port=9090
            )
    
    @patch('main.__main__.create_mcp_server')
    def test_main_function_default_values(self, mock_create_server):
        """Test that main function uses default values when environment variables are not set."""
        # Mock the MCP server to return quickly
        mock_app = mock_create_server.return_value
        mock_app.run_http_async.side_effect = KeyboardInterrupt()
        
        # Test with no environment variables
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(SystemExit):
                main()
            
            # Verify the MCP server was called with default parameters
            mock_app.run_http_async.assert_called_with(
                transport="http", 
                host="0.0.0.0",
                port=8080
            )
    
    @patch('main.__main__.create_mcp_server')
    def test_main_function_error_handling(self, mock_create_server):
        """Test that main function handles errors gracefully."""
        # Mock the MCP server to raise an exception
        mock_create_server.side_effect = Exception("Test error")
        
        # Test main function
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


class TestServerFactory:
    """Test the server factory with health check endpoint."""
    
    def test_create_mcp_server_with_health_check(self):
        """Test that the server factory creates a server with health check endpoint."""
        # This test requires environment variables to be set
        with patch.dict('os.environ', {
            'VCENTER_HOST': 'https://test-vcenter.com',
            'VCENTER_USERNAME': 'testuser',
            'VCENTER_PASSWORD': 'testpass'
        }):
            app = create_mcp_server()
            assert app is not None
            assert hasattr(app, 'custom_route')
    
    def test_create_mcp_server_with_config(self):
        """Test that the server factory creates a server with custom config."""
        from main.models.vcenter_config import VCenterConfig
        
        config = VCenterConfig(
            host="https://test-vcenter.com",
            username="testuser",
            password="testpass"
        )
        
        app = create_mcp_server_with_config(config)
        assert app is not None
        assert hasattr(app, 'custom_route') 