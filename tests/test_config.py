"""
Unit tests for the configuration module.
"""

import os
import json
import pytest
from unittest.mock import patch

from main.config.config_manager import ConfigManager
from main.models.vcenter_config import VCenterConfig


class TestVCenterConfig:
    """Test VCenterConfig dataclass."""
    
    def test_vcenter_config_creation(self):
        """Test creating a VCenterConfig instance."""
        config = VCenterConfig(
            host="https://vcenter.example.com",
            username="admin",
            password="password123",
            verify_ssl=True,
            timeout=30
        )
        
        assert config.host == "https://vcenter.example.com"
        assert config.username == "admin"
        assert config.password == "password123"
        assert config.verify_ssl is True
        assert config.timeout == 30


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_config_manager_creation(self):
        """Test creating a ConfigManager instance."""
        config_manager = ConfigManager()
        assert config_manager is not None
    
    @patch.dict(os.environ, {
        'VCENTER_HOST': 'https://vcenter.example.com',
        'VCENTER_USERNAME': 'admin',
        'VCENTER_PASSWORD': 'password123'
    }, clear=True)
    def test_get_vcenter_config_from_env(self):
        """Test getting vCenter config from environment variables."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        assert config.host == "https://vcenter.example.com"
        assert config.username == "admin"
        assert config.password == "password123"
        assert config.verify_ssl is True  # default
        assert config.timeout == 30  # default
    
    @patch.dict(os.environ, {
        'VCENTER_HOST': 'https://vcenter.example.com',
        'VCENTER_USERNAME': 'admin',
        'VCENTER_PASSWORD': 'password123',
        'VCENTER_VERIFY_SSL': 'false',
        'VCENTER_TIMEOUT': '60'
    }, clear=True)
    def test_get_vcenter_config_with_options(self):
        """Test getting vCenter config with custom options."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        assert config.host == "https://vcenter.example.com"
        assert config.username == "admin"
        assert config.password == "password123"
        assert config.verify_ssl is False
        assert config.timeout == 60
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_vcenter_config_missing_credentials(self):
        """Test getting vCenter config when credentials are missing."""
        config_manager = ConfigManager()
        
        with pytest.raises(ValueError, match="vCenter credentials not found"):
            config_manager.get_vcenter_config()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_vcenter_config_from_service_binding(self):
        """Test getting vCenter config from Cloud Foundry service binding."""
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
        
        with patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(vcap_services)}):
            config_manager = ConfigManager()
            config = config_manager.get_vcenter_config()
            
            assert config.host == "https://vcenter.example.com"
            assert config.username == "admin"
            assert config.password == "password123"
    
    def test_get_vcenter_config_service_binding_priority(self):
        """Test that environment variables take priority over service binding."""
        vcap_services = {
            "vcenter": [
                {
                    "name": "my-vcenter",
                    "credentials": {
                        "host": "https://service-vcenter.example.com",
                        "username": "service-admin",
                        "password": "service-password"
                    }
                }
            ]
        }
        
        with patch.dict(os.environ, {
            'VCAP_SERVICES': json.dumps(vcap_services),
            'VCENTER_HOST': 'https://env-vcenter.example.com',
            'VCENTER_USERNAME': 'env-admin',
            'VCENTER_PASSWORD': 'env-password'
        }, clear=True):
            config_manager = ConfigManager()
            config = config_manager.get_vcenter_config()
            
            # Environment variables should take priority
            assert config.host == "https://env-vcenter.example.com"
            assert config.username == "env-admin"
            assert config.password == "env-password"
    
    @patch.dict(os.environ, {
        'VCENTER_HOST': 'https://vcenter.example.com',
        'VCENTER_USERNAME': 'admin',
        'VCENTER_PASSWORD': 'password123',
        'VCENTER_VERIFY_SSL': 'invalid'
    }, clear=True)
    def test_invalid_ssl_verification_setting(self):
        """Test handling of invalid SSL verification setting."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        # Should default to True for invalid values
        assert config.verify_ssl is True
    
    @patch.dict(os.environ, {
        'VCENTER_HOST': 'https://vcenter.example.com',
        'VCENTER_USERNAME': 'admin',
        'VCENTER_PASSWORD': 'password123',
        'VCENTER_TIMEOUT': 'invalid'
    }, clear=True)
    def test_invalid_timeout_setting(self):
        """Test handling of invalid timeout setting."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        # Should default to 30 for invalid values
        assert config.timeout == 30 