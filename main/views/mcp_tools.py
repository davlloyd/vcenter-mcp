"""
MCP Tools View Layer.

This module contains the MCP tools that serve as the view layer,
presenting vCenter data to MCP clients.
"""

import logging
from typing import Optional, TYPE_CHECKING
from fastmcp import FastMCP

from ..models.vcenter_config import Cluster, ResourcePool, VirtualMachine

if TYPE_CHECKING:
    from ..controllers.vcenter_controller import VCenterController

logger = logging.getLogger(__name__)


class MCPToolsView:
    """View layer for MCP tools that presents vCenter data."""
    
    def __init__(self, controller: 'VCenterController'):
        """
        Initialize the MCP tools view.
        
        Args:
            controller: VCenter controller instance
        """
        self.controller = controller
    
    def register_tools(self, app: FastMCP):
        """Register all MCP tools with the FastMCP application."""
        
        @app.tool(
            name="list_clusters",
            description="List all clusters in vCenter. Returns a formatted list of all available clusters with their names and IDs."
        )
        async def list_clusters() -> str:
            """List all clusters in vCenter"""
            try:
                clusters = self.controller.get_clusters()
                if not clusters:
                    return "No clusters found in vCenter"
                
                result = "Clusters in vCenter:\n"
                for cluster in clusters:
                    result += f"- {cluster.name} (ID: {cluster.cluster_id})\n"
                
                return result
            except Exception as e:
                logger.error(f"Error listing clusters: {e}")
                return f"Error listing clusters: {e}"
        
        @app.tool(
            name="list_vms_in_cluster",
            description="List all virtual machines in a specific cluster. Requires the cluster name as input and returns a formatted list of VMs with their names and power states."
        )
        async def list_vms_in_cluster(cluster_name: str) -> str:
            """List all virtual machines in a specific cluster"""
            try:
                vms = self.controller.get_vms_in_cluster(cluster_name)
                if not vms:
                    return f"No virtual machines found in cluster '{cluster_name}'"
                
                result = f"Virtual machines in cluster '{cluster_name}':\n"
                for vm in vms:
                    result += f"- {vm.name} (Power: {vm.power_state})\n"
                
                return result
            except Exception as e:
                logger.error(f"Error listing VMs in cluster: {e}")
                return f"Error listing VMs in cluster: {e}"
        
        @app.tool(
            name="list_resource_pools",
            description="List all resource pools in a specific cluster. Requires the cluster name as input and returns a formatted list of resource pools with their names and IDs."
        )
        async def list_resource_pools(cluster_name: str) -> str:
            """List all resource pools in a specific cluster"""
            try:
                resource_pools = self.controller.get_resource_pools_in_cluster(cluster_name)
                if not resource_pools:
                    return f"No resource pools found in cluster '{cluster_name}'"
                
                result = f"Resource pools in cluster '{cluster_name}':\n"
                for rp in resource_pools:
                    result += f"- {rp.name} (ID: {rp.resource_pool_id})\n"
                
                return result
            except Exception as e:
                logger.error(f"Error listing resource pools: {e}")
                return f"Error listing resource pools: {e}"
        
        @app.tool(
            name="list_vms_in_resource_pool",
            description="List all virtual machines in a specific resource pool. Requires the resource pool name as input and returns a formatted list of VMs with their names and power states."
        )
        async def list_vms_in_resource_pool(resource_pool_name: str) -> str:
            """List all virtual machines in a specific resource pool"""
            try:
                vms = self.controller.get_vms_in_resource_pool(resource_pool_name)
                if not vms:
                    return f"No virtual machines found in resource pool '{resource_pool_name}'"
                
                result = f"Virtual machines in resource pool '{resource_pool_name}':\n"
                for vm in vms:
                    result += f"- {vm.name} (Power: {vm.power_state})\n"
                
                return result
            except Exception as e:
                logger.error(f"Error listing VMs in resource pool: {e}")
                return f"Error listing VMs in resource pool: {e}"
        
        @app.tool(
            name="get_vcenter_status",
            description="Get vCenter connection status and basic information. Returns connection status, host information, and counts of clusters, resource pools, and virtual machines."
        )
        async def get_vcenter_status() -> str:
            """Get vCenter connection status and basic information"""
            try:
                status_data = self.controller.get_vcenter_status()
                return self.format_status(status_data)
            except Exception as e:
                logger.error(f"Error getting vCenter status: {e}")
                return f"Error getting vCenter status: {e}"
    
    def format_cluster_list(self, clusters: list[Cluster]) -> str:
        """Format a list of clusters for display."""
        if not clusters:
            return "No clusters found"
        
        result = "Clusters in vCenter:\n"
        for cluster in clusters:
            result += f"- {cluster.name} (ID: {cluster.cluster_id})\n"
        
        return result
    
    def format_vm_list(self, vms: list[VirtualMachine], context: str) -> str:
        """Format a list of virtual machines for display."""
        if not vms:
            return f"No virtual machines found in {context}"
        
        result = f"Virtual machines in {context}:\n"
        for vm in vms:
            result += f"- {vm.name} (Power: {vm.power_state})\n"
        
        return result
    
    def format_resource_pool_list(self, resource_pools: list[ResourcePool], context: str) -> str:
        """Format a list of resource pools for display."""
        if not resource_pools:
            return f"No resource pools found in {context}"
        
        result = f"Resource pools in {context}:\n"
        for rp in resource_pools:
            result += f"- {rp.name} (ID: {rp.resource_pool_id})\n"
        
        return result
    
    def format_status(self, status_data: dict) -> str:
        """Format vCenter status information for display."""
        if status_data.get('connection_status') == 'Failed':
            return f"Error: {status_data.get('error', 'Unknown error')}"
        
        if status_data.get('connection_status') == 'Error':
            return f"Error getting vCenter status: {status_data.get('error', 'Unknown error')}"
        
        result = "vCenter Status:\n"
        result += f"- Connected to: {status_data.get('host', 'Unknown')}\n"
        result += f"- Clusters: {status_data.get('clusters_count', 0)}\n"
        result += f"- Resource Pools: {status_data.get('resource_pools_count', 0)}\n"
        result += f"- Virtual Machines: {status_data.get('vms_count', 0)}\n"
        result += f"- Connection: {status_data.get('connection_status', 'Unknown')}\n"
        
        return result 