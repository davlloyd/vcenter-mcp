#!/usr/bin/env python3
"""
Test script to verify vCenter connectivity and credentials.
"""

import os
import sys

# Add main to path for development
sys.path.insert(0, os.path.dirname(__file__))

from main.config.config_manager import ConfigManager
from main.services.vcenter_service import VCenterService

def test_connection():
    """Test vCenter connection and basic API calls"""
    
    try:
        # Get configuration
        config_manager = ConfigManager()
        config = config_manager.get_vcenter_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  Host: {config.host}")
        print(f"  Username: {config.username}")
        print(f"  SSL Verify: {config.verify_ssl}")
        print(f"  Timeout: {config.timeout}s")
        
        # Create service
        service = VCenterService(config)
        print("✓ VCenter service created successfully")
        
        # Test basic API calls
        print("\nTesting API calls...")
        
        # Test clusters
        clusters = service.get_clusters()
        print(f"✓ Clusters API: Found {len(clusters)} clusters")
        for cluster in clusters[:3]:  # Show first 3
            print(f"  - {cluster.get('name', 'Unknown')}")
        
        # Test resource pools
        resource_pools = service.get_resource_pools()
        print(f"✓ Resource Pools API: Found {len(resource_pools)} resource pools")
        
        # Test VMs
        vms = service.get_virtual_machines()
        print(f"✓ Virtual Machines API: Found {len(vms)} VMs")
        
        # Test connection status
        status = service.test_connection()
        print(f"✓ Connection test: {'PASSED' if status else 'FAILED'}")
        
        print("\n🎉 All tests passed! vCenter connection is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1) 