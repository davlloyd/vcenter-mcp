"""
vCenter Controller.

This module contains the controller layer that handles business logic
and coordinates between the models and views.
"""

import logging
from typing import List, Optional
from fastmcp import FastMCP

from ..models.vcenter_config import VCenterConfig, Cluster, ResourcePool, VirtualMachine
from ..services.vcenter_service import VCenterService

logger = logging.getLogger(__name__)


class VCenterController:
    """Controller for vCenter operations."""
    
    def __init__(self, config: VCenterConfig):
        """
        Initialize the vCenter controller.
        
        Args:
            config: vCenter configuration
        """
        self.config = config
        self.service = VCenterService(config)
    
    def get_clusters(self) -> List[Cluster]:
        """
        Get all clusters from vCenter.
        
        Returns:
            List of Cluster objects
        """
        try:
            raw_clusters = self.service.get_clusters()
            clusters = []
            
            for raw_cluster in raw_clusters:
                cluster = Cluster(
                    cluster_id=raw_cluster.get('cluster', 'Unknown'),
                    name=raw_cluster.get('name', 'Unknown')
                )
                clusters.append(cluster)
            
            logger.info(f"Retrieved {len(clusters)} clusters")
            return clusters
        except Exception as e:
            logger.error(f"Failed to get clusters: {e}")
            return []
    
    def get_cluster_by_name(self, cluster_name: str) -> Optional[Cluster]:
        """
        Get a specific cluster by name.
        
        Args:
            cluster_name: Name of the cluster to find
            
        Returns:
            Cluster object if found, None otherwise
        """
        clusters = self.get_clusters()
        for cluster in clusters:
            if cluster.name == cluster_name:
                return cluster
        return None
    
    def get_resource_pools_in_cluster(self, cluster_name: str) -> List[ResourcePool]:
        """
        Get all resource pools in a specific cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of ResourcePool objects
        """
        try:
            cluster = self.get_cluster_by_name(cluster_name)
            if not cluster:
                logger.warning(f"Cluster '{cluster_name}' not found")
                return []
            
            raw_resource_pools = self.service.get_resource_pools(cluster_id=cluster.cluster_id)
            resource_pools = []
            
            for raw_rp in raw_resource_pools:
                resource_pool = ResourcePool(
                    resource_pool_id=raw_rp.get('resource_pool', 'Unknown'),
                    name=raw_rp.get('name', 'Unknown'),
                    cluster_id=cluster.cluster_id
                )
                resource_pools.append(resource_pool)
            
            logger.info(f"Retrieved {len(resource_pools)} resource pools from cluster '{cluster_name}'")
            return resource_pools
        except Exception as e:
            logger.error(f"Failed to get resource pools for cluster '{cluster_name}': {e}")
            return []
    
    def get_resource_pool_by_name(self, resource_pool_name: str) -> Optional[ResourcePool]:
        """
        Get a specific resource pool by name.
        
        Args:
            resource_pool_name: Name of the resource pool to find
            
        Returns:
            ResourcePool object if found, None otherwise
        """
        raw_resource_pools = self.service.get_resource_pools()
        for raw_rp in raw_resource_pools:
            if raw_rp.get('name') == resource_pool_name:
                return ResourcePool(
                    resource_pool_id=raw_rp.get('resource_pool', 'Unknown'),
                    name=raw_rp.get('name', 'Unknown')
                )
        return None
    
    def get_vms_in_cluster(self, cluster_name: str) -> List[VirtualMachine]:
        """
        Get all virtual machines in a specific cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of VirtualMachine objects
        """
        try:
            cluster = self.get_cluster_by_name(cluster_name)
            if not cluster:
                logger.warning(f"Cluster '{cluster_name}' not found")
                return []
            
            raw_vms = self.service.get_virtual_machines(cluster_id=cluster.cluster_id)
            vms = []
            
            for raw_vm in raw_vms:
                vm = VirtualMachine(
                    vm_id=raw_vm.get('vm', 'Unknown'),
                    name=raw_vm.get('name', 'Unknown'),
                    power_state=raw_vm.get('power_state', 'Unknown'),
                    cluster_id=cluster.cluster_id
                )
                vms.append(vm)
            
            logger.info(f"Retrieved {len(vms)} VMs from cluster '{cluster_name}'")
            return vms
        except Exception as e:
            logger.error(f"Failed to get VMs for cluster '{cluster_name}': {e}")
            return []
    
    def get_vms_in_resource_pool(self, resource_pool_name: str) -> List[VirtualMachine]:
        """
        Get all virtual machines in a specific resource pool.
        
        Args:
            resource_pool_name: Name of the resource pool
            
        Returns:
            List of VirtualMachine objects
        """
        try:
            resource_pool = self.get_resource_pool_by_name(resource_pool_name)
            if not resource_pool:
                logger.warning(f"Resource pool '{resource_pool_name}' not found")
                return []
            
            raw_vms = self.service.get_virtual_machines(resource_pool_id=resource_pool.resource_pool_id)
            vms = []
            
            for raw_vm in raw_vms:
                vm = VirtualMachine(
                    vm_id=raw_vm.get('vm', 'Unknown'),
                    name=raw_vm.get('name', 'Unknown'),
                    power_state=raw_vm.get('power_state', 'Unknown'),
                    resource_pool_id=resource_pool.resource_pool_id
                )
                vms.append(vm)
            
            logger.info(f"Retrieved {len(vms)} VMs from resource pool '{resource_pool_name}'")
            return vms
        except Exception as e:
            logger.error(f"Failed to get VMs for resource pool '{resource_pool_name}': {e}")
            return []
    
    def get_vcenter_status(self) -> dict:
        """
        Get vCenter connection status and basic information.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Test connection
            if not self.service.test_connection():
                return {
                    'connection_status': 'Failed',
                    'host': self.config.host,
                    'error': 'Cannot connect to vCenter'
                }
            
            # Get basic stats
            clusters = self.get_clusters()
            raw_resource_pools = self.service.get_resource_pools()
            raw_vms = self.service.get_virtual_machines()
            
            return {
                'host': self.config.host,
                'clusters_count': len(clusters),
                'resource_pools_count': len(raw_resource_pools),
                'vms_count': len(raw_vms),
                'connection_status': 'Connected'
            }
        except Exception as e:
            logger.error(f"Error getting vCenter status: {e}")
            return {
                'connection_status': 'Error',
                'host': self.config.host,
                'error': str(e)
            } 