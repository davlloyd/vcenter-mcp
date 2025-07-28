"""
vCenter Service Layer.

This module contains the service layer that handles data access
and external API interactions with vCenter.
"""

import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from ..models.vcenter_config import VCenterConfig

logger = logging.getLogger(__name__)


class VCenterService:
    """Service layer for vCenter REST API interactions."""
    
    def __init__(self, config: VCenterConfig):
        """
        Initialize the vCenter service.
        
        Args:
            config: vCenter configuration
        """
        self.config = config
        self.host = config.host.rstrip('/')
        self.session = self._create_session()
        
        # Disable SSL warnings if verify_ssl is False
        if not config.verify_ssl:
            self._disable_ssl_warnings()
    
    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.config.username, self.config.password)
        session.verify = self.config.verify_ssl
        session.timeout = self.config.timeout
        
        # Add default headers
        session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        return session
    
    def _disable_ssl_warnings(self):
        """Disable SSL warnings for self-signed certificates."""
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            logger.warning("urllib3 not available, SSL warnings may appear")
    
    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """
        Make a request to the vCenter REST API.
        
        Args:
            endpoint: API endpoint (without /rest/ prefix)
            method: HTTP method
            **kwargs: Additional request parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: If the request fails
        """
        url = urljoin(f"{self.host}/rest/", endpoint)
        
        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise Exception(f"vCenter API request failed: {e}")
    
    def get_clusters(self) -> List[Dict[str, Any]]:
        """
        Get all clusters from vCenter.
        
        Returns:
            List of cluster objects
        """
        try:
            response = self._make_request("vcenter/cluster")
            clusters = response.get("value", [])
            logger.info(f"Retrieved {len(clusters)} clusters from vCenter")
            return clusters
        except Exception as e:
            logger.error(f"Failed to get clusters: {e}")
            return []
    
    def get_resource_pools(self, cluster_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get resource pools, optionally filtered by cluster.
        
        Args:
            cluster_id: Optional cluster ID to filter by
            
        Returns:
            List of resource pool objects
        """
        try:
            endpoint = "vcenter/resource-pool"
            if cluster_id:
                endpoint += f"?clusters={cluster_id}"
            
            response = self._make_request(endpoint)
            resource_pools = response.get("value", [])
            logger.info(f"Retrieved {len(resource_pools)} resource pools from vCenter")
            return resource_pools
        except Exception as e:
            logger.error(f"Failed to get resource pools: {e}")
            return []
    
    def get_virtual_machines(self, cluster_id: Optional[str] = None, 
                           resource_pool_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get virtual machines, optionally filtered by cluster or resource pool.
        
        Args:
            cluster_id: Optional cluster ID to filter by
            resource_pool_id: Optional resource pool ID to filter by
            
        Returns:
            List of virtual machine objects
        """
        try:
            endpoint = "vcenter/vm"
            params = []
            
            if cluster_id:
                params.append(f"clusters={cluster_id}")
            if resource_pool_id:
                params.append(f"resource_pools={resource_pool_id}")
            
            if params:
                endpoint += "?" + "&".join(params)
            
            response = self._make_request(endpoint)
            vms = response.get("value", [])
            logger.info(f"Retrieved {len(vms)} virtual machines from vCenter")
            return vms
        except Exception as e:
            logger.error(f"Failed to get virtual machines: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test the connection to vCenter.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get clusters as a simple test
            self.get_clusters()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False 