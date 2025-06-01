"""
🔌 Jamie's MCP Base Framework

Sprint 3: Foundation for all MCP server implementations
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class MCPServerError(Exception):
    """Base exception for MCP server errors"""
    pass

class MCPConnectionError(MCPServerError):
    """Connection-related MCP errors"""
    pass

class MCPQueryError(MCPServerError):
    """Query execution errors"""
    pass

class BaseMCPServer(ABC):
    """
    Base class for all MCP server implementations
    
    Provides common functionality for DevOps tool integrations
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.connected = False
        self.last_health_check = None
        self.capabilities = []
        
        logger.info(f"Initializing MCP server: {name}")

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the DevOps tool"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the DevOps tool"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health status of the connection"""
        pass

    @abstractmethod
    async def query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query against the DevOps tool"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of supported operations"""
        pass

    async def ensure_connected(self):
        """Ensure connection is established"""
        if not self.connected:
            await self.connect()
        
        # Check if we need to refresh connection
        if self.last_health_check:
            time_since_check = (datetime.now() - self.last_health_check).total_seconds()
            if time_since_check > 300:  # 5 minutes
                await self.health_check()

    def format_response(self, data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
        """Format standard MCP response"""
        return {
            "success": success,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "server": self.name
        }

    def format_error(self, error: str, error_type: str = "general") -> Dict[str, Any]:
        """Format error response"""
        return {
            "success": False,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "server": self.name
        }

class HTTPMCPServer(BaseMCPServer):
    """
    Base class for HTTP-based MCP servers (Prometheus, Loki, etc.)
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.base_url = config.get("url", "")
        self.timeout = config.get("timeout", 30)
        self.headers = config.get("headers", {})
        
        # Authentication
        if config.get("username") and config.get("password"):
            import base64
            credentials = base64.b64encode(f"{config['username']}:{config['password']}".encode()).decode()
            self.headers["Authorization"] = f"Basic {credentials}"
        
        if config.get("token"):
            self.headers["Authorization"] = f"Bearer {config['token']}"

    async def make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request to the service"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response

    async def connect(self) -> bool:
        """Test connection to HTTP service"""
        try:
            health_result = await self.health_check()
            self.connected = health_result.get("success", False)
            return self.connected
        except Exception as e:
            logger.error(f"Connection failed for {self.name}: {str(e)}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from HTTP service"""
        self.connected = False
        logger.info(f"Disconnected from {self.name}")

class KubernetesMCPServer(BaseMCPServer):
    """
    MCP Server for Kubernetes integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("kubernetes", config)
        self.kubeconfig_path = config.get("kubeconfig_path")
        self.namespace = config.get("namespace", "default")
        self.client = None

    async def connect(self) -> bool:
        """Connect to Kubernetes cluster"""
        try:
            # In a real implementation, we'd use kubernetes-asyncio
            # For now, we'll simulate the connection
            logger.info(f"Connecting to Kubernetes cluster...")
            
            # TODO: Implement actual Kubernetes client connection
            # from kubernetes_asyncio import client, config
            # await config.load_kube_config(config_file=self.kubeconfig_path)
            # self.client = client.ApiClient()
            
            self.connected = True
            logger.info("Connected to Kubernetes cluster")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Kubernetes: {str(e)}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from Kubernetes"""
        if self.client:
            await self.client.close()
        self.connected = False
        logger.info("Disconnected from Kubernetes")

    async def health_check(self) -> Dict[str, Any]:
        """Check Kubernetes cluster health"""
        try:
            await self.ensure_connected()
            
            # TODO: Implement actual health check
            # v1 = client.CoreV1Api(self.client)
            # nodes = await v1.list_node()
            
            # Simulated health check for now
            health_data = {
                "cluster_status": "healthy",
                "nodes_ready": 3,
                "pods_running": 45,
                "services_active": 12
            }
            
            self.last_health_check = datetime.now()
            return self.format_response(health_data)
            
        except Exception as e:
            return self.format_error(f"Health check failed: {str(e)}", "health_check")

    async def query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Kubernetes queries"""
        try:
            await self.ensure_connected()
            
            if query_type == "pods":
                return await self._get_pods(params)
            elif query_type == "deployments":
                return await self._get_deployments(params)
            elif query_type == "services":
                return await self._get_services(params)
            elif query_type == "logs":
                return await self._get_pod_logs(params)
            else:
                return self.format_error(f"Unknown query type: {query_type}", "invalid_query")
                
        except Exception as e:
            return self.format_error(f"Query failed: {str(e)}", "query_execution")

    async def _get_pods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pod information"""
        namespace = params.get("namespace", self.namespace)
        
        # TODO: Implement actual pod querying
        # v1 = client.CoreV1Api(self.client)
        # pods = await v1.list_namespaced_pod(namespace)
        
        # Simulated response for now
        pods_data = [
            {
                "name": "frontend-deployment-abc123",
                "namespace": namespace,
                "status": "Running",
                "ready": "1/1",
                "restarts": 0,
                "age": "2d",
                "node": "worker-node-1"
            },
            {
                "name": "backend-deployment-def456", 
                "namespace": namespace,
                "status": "Running",
                "ready": "1/1", 
                "restarts": 0,
                "age": "1d",
                "node": "worker-node-2"
            }
        ]
        
        return self.format_response(pods_data)

    async def _get_deployments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get deployment information"""
        namespace = params.get("namespace", self.namespace)
        
        # Simulated deployment data
        deployments_data = [
            {
                "name": "frontend-deployment",
                "namespace": namespace,
                "ready_replicas": 3,
                "desired_replicas": 3,
                "available_replicas": 3,
                "age": "5d"
            },
            {
                "name": "backend-deployment",
                "namespace": namespace, 
                "ready_replicas": 2,
                "desired_replicas": 2,
                "available_replicas": 2,
                "age": "3d"
            }
        ]
        
        return self.format_response(deployments_data)

    async def _get_services(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get service information"""
        namespace = params.get("namespace", self.namespace)
        
        # Simulated service data
        services_data = [
            {
                "name": "frontend-service",
                "namespace": namespace,
                "type": "LoadBalancer",
                "cluster_ip": "10.96.100.1",
                "external_ip": "192.168.1.100",
                "ports": "80:30001/TCP"
            },
            {
                "name": "backend-service",
                "namespace": namespace,
                "type": "ClusterIP", 
                "cluster_ip": "10.96.100.2",
                "external_ip": "<none>",
                "ports": "8080:31001/TCP"
            }
        ]
        
        return self.format_response(services_data)

    async def _get_pod_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pod logs"""
        pod_name = params.get("pod_name")
        namespace = params.get("namespace", self.namespace)
        lines = params.get("lines", 100)
        
        if not pod_name:
            return self.format_error("pod_name is required", "missing_parameter")
        
        # Simulated log data
        logs_data = {
            "pod_name": pod_name,
            "namespace": namespace,
            "lines_returned": 50,
            "logs": [
                "2024-01-15T10:30:00Z INFO Starting application...",
                "2024-01-15T10:30:01Z INFO Server listening on port 8080",
                "2024-01-15T10:30:05Z INFO Database connection established",
                "2024-01-15T10:35:00Z INFO Health check passed",
                "2024-01-15T10:40:00Z INFO Processing request from 192.168.1.50"
            ]
        }
        
        return self.format_response(logs_data)

    def get_capabilities(self) -> List[str]:
        """Get Kubernetes MCP capabilities"""
        return [
            "pods",
            "deployments", 
            "services",
            "logs",
            "events",
            "health_check"
        ] 