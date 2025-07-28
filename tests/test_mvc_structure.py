"""
Tests for the MVC structure components.
"""

import pytest
from unittest.mock import Mock, patch

from main.models.vcenter_config import VCenterConfig, Cluster, ResourcePool, VirtualMachine
from main.config.config_manager import ConfigManager
from main.services.vcenter_service import VCenterService
from main.controllers.vcenter_controller import VCenterController


class TestModels:
    """Test the data models."""
    
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
    
    def test_cluster_creation(self):
        """Test creating a Cluster instance."""
        cluster = Cluster(
            cluster_id="cluster-123",
            name="Test Cluster"
        )
        
        assert cluster.cluster_id == "cluster-123"
        assert cluster.name == "Test Cluster"
        assert cluster.resource_pools is None
    
    def test_resource_pool_creation(self):
        """Test creating a ResourcePool instance."""
        resource_pool = ResourcePool(
            resource_pool_id="rp-123",
            name="Test Resource Pool",
            cluster_id="cluster-123"
        )
        
        assert resource_pool.resource_pool_id == "rp-123"
        assert resource_pool.name == "Test Resource Pool"
        assert resource_pool.cluster_id == "cluster-123"
    
    def test_virtual_machine_creation(self):
        """Test creating a VirtualMachine instance."""
        vm = VirtualMachine(
            vm_id="vm-123",
            name="Test VM",
            power_state="POWERED_ON",
            cluster_id="cluster-123"
        )
        
        assert vm.vm_id == "vm-123"
        assert vm.name == "Test VM"
        assert vm.power_state == "POWERED_ON"
        assert vm.cluster_id == "cluster-123"


class TestConfigManager:
    """Test the configuration manager."""
    
    @patch.dict('os.environ', {
        'VCENTER_HOST': 'https://vcenter.example.com',
        'VCENTER_USERNAME': 'admin',
        'VCENTER_PASSWORD': 'password123'
    })
    def test_get_vcenter_config_from_env(self):
        """Test getting configuration from environment variables."""
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        
        assert config.host == "https://vcenter.example.com"
        assert config.username == "admin"
        assert config.password == "password123"
        assert config.verify_ssl is True
        assert config.timeout == 30


class TestVCenterService:
    """Test the vCenter service layer."""
    
    def test_service_initialization(self):
        """Test VCenterService initialization."""
        config = VCenterConfig(
            host="https://vcenter.example.com",
            username="admin",
            password="password123"
        )
        
        service = VCenterService(config)
        assert service.config == config
        assert service.host == "https://vcenter.example.com"


class TestVCenterController:
    """Test the vCenter controller."""
    
    def test_controller_initialization(self):
        """Test VCenterController initialization."""
        config = VCenterConfig(
            host="https://vcenter.example.com",
            username="admin",
            password="password123"
        )
        
        controller = VCenterController(config)
        
        assert controller.config == config
        assert controller.service is not None
        # Note: view is no longer created in controller to avoid circular imports
    
    @patch('main.controllers.vcenter_controller.VCenterService')
    def test_get_clusters(self, mock_service_class):
        """Test getting clusters through the controller."""
        # Setup mock
        mock_service = Mock()
        mock_service.get_clusters.return_value = [
            {'cluster': 'cluster-123', 'name': 'Test Cluster'}
        ]
        mock_service_class.return_value = mock_service
        
        # Create controller
        config = VCenterConfig(
            host="https://vcenter.example.com",
            username="admin",
            password="password123"
        )
        controller = VCenterController(config)
        
        # Test
        clusters = controller.get_clusters()
        
        assert len(clusters) == 1
        assert clusters[0].cluster_id == "cluster-123"
        assert clusters[0].name == "Test Cluster"
        mock_service.get_clusters.assert_called_once()


class TestMVCIntegration:
    """Test MVC integration."""
    
    @patch('main.config.config_manager.ConfigManager.get_vcenter_config')
    def test_mvc_flow(self, mock_get_config):
        """Test the complete MVC flow."""
        # Setup mock configuration
        config = VCenterConfig(
            host="https://vcenter.example.com",
            username="admin",
            password="password123"
        )
        mock_get_config.return_value = config
        
        # Test configuration manager
        config_manager = ConfigManager()
        retrieved_config = config_manager.get_vcenter_config()
        assert retrieved_config == config
        
        # Test service layer
        service = VCenterService(config)
        assert service.config == config
        
        # Test controller layer
        controller = VCenterController(config)
        assert controller.config == config
        assert controller.service is not None 