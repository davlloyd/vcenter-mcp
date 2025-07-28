"""
Configuration Manager.

This module handles credential management, environment variable loading,
and Cloud Foundry service binding integration.
"""

import os
import json
import logging
from typing import Tuple, Optional
from dotenv import load_dotenv

from ..models.vcenter_config import VCenterConfig, VCenterCredentials

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration and credentials for the vCenter MCP Server."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        load_dotenv()
    
    def get_vcenter_credentials(self) -> VCenterCredentials:
        """
        Get vCenter credentials from environment variables or Cloud Foundry service binding.
        Environment variables take priority over service binding.
        
        Returns:
            VCenterCredentials object
            
        Raises:
            ValueError: If credentials are not found
        """
        # Check environment variables first (priority)
        credentials = self._get_credentials_from_env()
        if credentials:
            return credentials
        
        # Fall back to Cloud Foundry service binding
        credentials = self._get_credentials_from_service_binding()
        if credentials:
            return credentials
        
        raise ValueError(
            "vCenter credentials not found in environment variables or service binding. "
            "Please set VCENTER_HOST, VCENTER_USERNAME, and VCENTER_PASSWORD environment "
            "variables or bind to a vCenter service in Cloud Foundry."
        )
    
    def get_vcenter_config(self) -> VCenterConfig:
        """
        Get complete vCenter configuration.
        
        Returns:
            VCenterConfig object with all connection parameters
        """
        credentials = self.get_vcenter_credentials()
        
        # Get optional configuration with proper error handling
        verify_ssl_str = os.getenv('VCENTER_VERIFY_SSL', 'true').lower()
        verify_ssl = verify_ssl_str != 'false'  # Default to True unless explicitly 'false'
        
        timeout_str = os.getenv('VCENTER_TIMEOUT', '30')
        try:
            timeout = int(timeout_str)
        except ValueError:
            logger.warning(f"Invalid VCENTER_TIMEOUT value '{timeout_str}', using default 30")
            timeout = 30
        
        return VCenterConfig(
            host=credentials.host,
            username=credentials.username,
            password=credentials.password,
            verify_ssl=verify_ssl,
            timeout=timeout
        )
    
    def _get_credentials_from_service_binding(self) -> Optional[VCenterCredentials]:
        """Extract credentials from Cloud Foundry service binding."""
        vcap_services = os.getenv('VCAP_SERVICES')
        if not vcap_services:
            return None
        
        try:
            services = json.loads(vcap_services)
            
            # Look for vCenter service in the binding
            for service_type, service_list in services.items():
                for service in service_list:
                    if self._is_vcenter_service(service):
                        credentials = service.get('credentials', {})
                        host = credentials.get('host')
                        username = credentials.get('username')
                        password = credentials.get('password')
                        
                        if all([host, username, password]):
                            logger.info(f"Using vCenter credentials from service binding: {service.get('name')}")
                            return VCenterCredentials(host=host, username=username, password=password)
                            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse VCAP_SERVICES: {e}")
        except Exception as e:
            logger.warning(f"Error processing service binding: {e}")
        
        return None
    
    def _get_credentials_from_env(self) -> Optional[VCenterCredentials]:
        """Extract credentials from environment variables."""
        host = os.getenv('VCENTER_HOST')
        username = os.getenv('VCENTER_USERNAME')
        password = os.getenv('VCENTER_PASSWORD')
        
        if all([host, username, password]):
            logger.info("Using vCenter credentials from environment variables")
            return VCenterCredentials(host=host, username=username, password=password)
        
        return None
    
    def _is_vcenter_service(self, service: dict) -> bool:
        """Check if a service is a vCenter service."""
        service_name = service.get('name', '').lower()
        service_label = service.get('label', '').lower()
        
        vcenter_keywords = ['vcenter', 'vmware', 'esxi']
        return any(keyword in service_name or keyword in service_label 
                  for keyword in vcenter_keywords) 