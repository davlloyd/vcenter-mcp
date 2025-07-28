"""
Tests for environment configuration setup.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
import json

from main.config.config_manager import ConfigManager


class TestEnvironmentConfiguration:
    """Test environment configuration functionality."""
    
    @patch.dict('os.environ', {
        'VCENTER_HOST': 'https://test-vcenter.example.com',
        'VCENTER_USERNAME': 'testuser',
        'VCENTER_PASSWORD': 'testpass123',
        'VCENTER_VERIFY_SSL': 'false',
        'VCENTER_TIMEOUT': '60',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_environment_variables_config(self):
        """Test configuration from environment variables."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        assert config.host == "https://test-vcenter.example.com"
        assert config.username == "testuser"
        assert config.password == "testpass123"
        assert config.verify_ssl is False
        assert config.timeout == 60
    
    @patch.dict('os.environ', {
        'VCENTER_HOST': 'https://test-vcenter.example.com',
        'VCENTER_USERNAME': 'testuser',
        'VCENTER_PASSWORD': 'testpass123'
    })
    def test_default_config_values(self):
        """Test default configuration values."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        assert config.verify_ssl is True  # Default value
        assert config.timeout == 30       # Default value
    
    def test_missing_credentials(self):
        """Test error handling for missing credentials."""
        with patch.dict('os.environ', {}, clear=True):
            config_manager = ConfigManager()
            
            with pytest.raises(ValueError, match="vCenter credentials not found"):
                config_manager.get_vcenter_config()
    
    def test_invalid_timeout(self):
        """Test handling of invalid timeout values."""
        with patch.dict(os.environ, {
            'VCENTER_HOST': 'https://vcenter.example.com',
            'VCENTER_USERNAME': 'admin',
            'VCENTER_PASSWORD': 'password123',
            'VCENTER_TIMEOUT': 'invalid'
        }, clear=True):
            config_manager = ConfigManager()
            config = config_manager.get_vcenter_config()
            
            # Should default to 30 for invalid values
            assert config.timeout == 30


class TestConfigTemplate:
    """Test configuration template functionality."""
    
    def test_config_template_structure(self):
        """Test that config template has required variables."""
        template_path = "config.env.example"
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check for required variables
            assert "VCENTER_HOST=" in content
            assert "VCENTER_USERNAME=" in content
            assert "VCENTER_PASSWORD=" in content
            
            # Check for optional variables
            assert "VCENTER_VERIFY_SSL=" in content
            assert "VCENTER_TIMEOUT=" in content
            assert "LOG_LEVEL=" in content
    
    def test_setup_script_import(self):
        """Test that setup script can be imported."""
        try:
            import setup_env
            assert hasattr(setup_env, 'setup_environment')
            assert hasattr(setup_env, 'show_current_config')
        except ImportError:
            pytest.skip("setup_env.py not available")


class TestCloudFoundryServiceBinding:
    """Test Cloud Foundry service binding configuration."""
    
    def test_vcenter_service_detection(self):
        """Test detection of vCenter services in Cloud Foundry."""
        vcap_services = {
            "vcenter": [
                {
                    "name": "my-vcenter",
                    "credentials": {
                        "host": "https://vcenter.example.com",
                        "username": "admin",
                        "password": "password123"
                    }
                }
            ]
        }
        
        with patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(vcap_services)}, clear=True):
            config_manager = ConfigManager()
            credentials = config_manager._get_credentials_from_service_binding()
            
            assert credentials is not None
            assert credentials.host == "https://vcenter.example.com"
            assert credentials.username == "admin"
            assert credentials.password == "password123"
    
    def test_non_vcenter_service_ignored(self):
        """Test that non-vCenter services are ignored."""
        vcap_services = {
            "mysql": [
                {
                    "name": "my-mysql",
                    "credentials": {
                        "host": "mysql.example.com",
                        "username": "user",
                        "password": "pass"
                    }
                }
            ]
        }
        
        with patch.dict('os.environ', {'VCAP_SERVICES': str(vcap_services)}):
            config_manager = ConfigManager()
            credentials = config_manager._get_credentials_from_service_binding()
            
            assert credentials is None 