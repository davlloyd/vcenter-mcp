"""
vCenter Configuration Model.

This module contains the data models for vCenter configuration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VCenterConfig:
    """Configuration model for vCenter connection."""
    host: str
    username: str
    password: str
    verify_ssl: bool = True
    timeout: int = 30


@dataclass
class VCenterCredentials:
    """Credentials model for vCenter authentication."""
    host: str
    username: str
    password: str


@dataclass
class Cluster:
    """Model representing a vCenter cluster."""
    cluster_id: str
    name: str
    resource_pools: Optional[list] = None


@dataclass
class ResourcePool:
    """Model representing a vCenter resource pool."""
    resource_pool_id: str
    name: str
    cluster_id: Optional[str] = None


@dataclass
class VirtualMachine:
    """Model representing a vCenter virtual machine."""
    vm_id: str
    name: str
    power_state: str
    cluster_id: Optional[str] = None
    resource_pool_id: Optional[str] = None 