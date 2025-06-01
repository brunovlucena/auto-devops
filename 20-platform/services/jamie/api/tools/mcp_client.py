"""
🔌 Jamie's Enhanced MCP Client

Sprint 3: Real DevOps tool integrations orchestration
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .mcp_base import BaseMCPServer, KubernetesMCPServer
from .prometheus_mcp import PrometheusMCPServer
from .loki_mcp import LokiMCPServer

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Enhanced MCP Client for orchestrating DevOps tool integrations
    
    Sprint 3: Real implementations for Kubernetes, Prometheus, Loki, Tempo, GitHub
    """
    
    def __init__(self):
        self.servers: Dict[str, BaseMCPServer] = {}
        self.connected_servers: List[str] = []
        self.failed_servers: List[str] = []
        
        # Default configurations (can be overridden via environment)
        self.default_configs = {
            "kubernetes": {
                "kubeconfig_path": "~/.kube/config",
                "namespace": "default",
                "enabled": True
            },
            "prometheus": {
                "url": "http://localhost:9090",
                "api_path": "/api/v1",
                "timeout": 30,
                "enabled": True
            },
            "loki": {
                "url": "http://localhost:3100", 
                "api_path": "/loki/api/v1",
                "timeout": 30,
                "enabled": True
            },
            "tempo": {
                "url": "http://localhost:3200",
                "api_path": "/api",
                "timeout": 30,
                "enabled": False  # Coming soon
            },
            "github": {
                "api_url": "https://api.github.com",
                "token": "",  # Set via GITHUB_TOKEN env var
                "enabled": False  # Coming soon
            }
        }
        
        logger.info("Enhanced MCP Client initialized for Sprint 3")

    def configure_server(self, server_name: str, config: Dict[str, Any]):
        """Configure a specific MCP server"""
        if server_name in self.default_configs:
            self.default_configs[server_name].update(config)
            logger.info(f"Updated configuration for {server_name}")
        else:
            logger.warning(f"Unknown server: {server_name}")

    async def connect_to_servers(self):
        """Connect to all enabled MCP servers"""
        logger.info("🔌 Connecting to DevOps MCP servers...")
        
        # Initialize and connect to each enabled server
        for server_name, config in self.default_configs.items():
            if config.get("enabled", False):
                try:
                    await self._initialize_server(server_name, config)
                except Exception as e:
                    logger.error(f"Failed to initialize {server_name}: {str(e)}")
                    self.failed_servers.append(server_name)
        
        logger.info(f"✅ Connected to {len(self.connected_servers)} MCP servers")
        if self.failed_servers:
            logger.warning(f"⚠️ Failed to connect to: {', '.join(self.failed_servers)}")

    async def _initialize_server(self, server_name: str, config: Dict[str, Any]):
        """Initialize a specific MCP server"""
        logger.info(f"Initializing {server_name} MCP server...")
        
        try:
            # Create server instance based on type
            if server_name == "kubernetes":
                server = KubernetesMCPServer(config)
            elif server_name == "prometheus":
                server = PrometheusMCPServer(config)
            elif server_name == "loki":
                server = LokiMCPServer(config)
            elif server_name == "tempo":
                # TODO: Implement Tempo MCP server
                logger.info(f"Tempo MCP server coming in Sprint 3B...")
                return
            elif server_name == "github":
                # TODO: Implement GitHub MCP server
                logger.info(f"GitHub MCP server coming in Sprint 3B...")
                return
            else:
                logger.warning(f"Unknown server type: {server_name}")
                return
            
            # Attempt connection
            connected = await server.connect()
            
            if connected:
                self.servers[server_name] = server
                self.connected_servers.append(server_name)
                logger.info(f"✅ {server_name} MCP server connected")
            else:
                logger.warning(f"⚠️ {server_name} MCP server failed to connect")
                self.failed_servers.append(server_name)
                
        except Exception as e:
            logger.error(f"Error initializing {server_name}: {str(e)}")
            self.failed_servers.append(server_name)

    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        logger.info("Disconnecting from all MCP servers...")
        
        for server_name, server in self.servers.items():
            try:
                await server.disconnect()
                logger.info(f"Disconnected from {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {str(e)}")
        
        self.servers.clear()
        self.connected_servers.clear()

    async def query_server(self, server_name: str, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query a specific MCP server"""
        if server_name not in self.servers:
            return {
                "success": False,
                "error": f"Server {server_name} not available",
                "available_servers": list(self.servers.keys())
            }
        
        try:
            server = self.servers[server_name]
            result = await server.query(query_type, params)
            return result
            
        except Exception as e:
            logger.error(f"Error querying {server_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Query failed: {str(e)}",
                "server": server_name
            }

    async def health_check_all(self) -> Dict[str, Any]:
        """Health check all connected servers"""
        health_results = {}
        
        for server_name, server in self.servers.items():
            try:
                health_result = await server.health_check()
                health_results[server_name] = health_result
            except Exception as e:
                health_results[server_name] = {
                    "success": False,
                    "error": str(e),
                    "server": server_name
                }
        
        return {
            "overall_status": "healthy" if all(r.get("success", False) for r in health_results.values()) else "degraded",
            "connected_servers": len(self.connected_servers),
            "failed_servers": len(self.failed_servers),
            "server_health": health_results,
            "timestamp": datetime.now().isoformat()
        }

    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        server_status = {}
        
        for server_name in self.default_configs.keys():
            if server_name in self.servers:
                server = self.servers[server_name]
                server_status[server_name] = {
                    "connected": True,
                    "capabilities": server.get_capabilities(),
                    "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None
                }
            elif server_name in self.failed_servers:
                server_status[server_name] = {
                    "connected": False,
                    "error": "Connection failed",
                    "enabled": self.default_configs[server_name].get("enabled", False)
                }
            else:
                server_status[server_name] = {
                    "connected": False,
                    "status": "not_initialized",
                    "enabled": self.default_configs[server_name].get("enabled", False)
                }
        
        return server_status

    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all connected servers"""
        capabilities = {}
        
        for server_name, server in self.servers.items():
            capabilities[server_name] = server.get_capabilities()
        
        return capabilities

    # Convenience methods for common DevOps queries

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status from Kubernetes and Prometheus"""
        results = {}
        
        # Get Kubernetes cluster info
        if "kubernetes" in self.servers:
            k8s_health = await self.query_server("kubernetes", "health_check", {})
            results["kubernetes"] = k8s_health
        
        # Get Prometheus metrics overview
        if "prometheus" in self.servers:
            # Get basic cluster metrics
            cpu_result = await self.query_server("prometheus", "cpu_usage", {"duration": "5m"})
            memory_result = await self.query_server("prometheus", "memory_usage", {})
            alerts_result = await self.query_server("prometheus", "alerts", {})
            
            results["prometheus"] = {
                "cpu_usage": cpu_result,
                "memory_usage": memory_result,
                "alerts": alerts_result
            }
        
        return {
            "cluster_overview": results,
            "timestamp": datetime.now().isoformat()
        }

    async def get_recent_errors(self, duration: str = "1h") -> Dict[str, Any]:
        """Get recent errors from logs and alerts"""
        results = {}
        
        # Get error logs from Loki
        if "loki" in self.servers:
            error_logs = await self.query_server("loki", "errors", {
                "duration": duration,
                "limit": 50
            })
            results["error_logs"] = error_logs
        
        # Get alerts from Prometheus
        if "prometheus" in self.servers:
            alerts = await self.query_server("prometheus", "alerts", {})
            results["alerts"] = alerts
        
        return {
            "error_summary": results,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }

    async def get_service_overview(self, service_name: str) -> Dict[str, Any]:
        """Get comprehensive overview of a specific service"""
        results = {}
        
        # Get pods for the service
        if "kubernetes" in self.servers:
            pods = await self.query_server("kubernetes", "pods", {
                "namespace": "default"  # Could be parameterized
            })
            results["pods"] = pods
        
        # Get service metrics
        if "prometheus" in self.servers:
            cpu_usage = await self.query_server("prometheus", "cpu_usage", {
                "instance": service_name,
                "duration": "5m"
            })
            error_rate = await self.query_server("prometheus", "error_rate", {
                "service": service_name,
                "duration": "5m"
            })
            results["metrics"] = {
                "cpu_usage": cpu_usage,
                "error_rate": error_rate
            }
        
        # Get service logs
        if "loki" in self.servers:
            service_logs = await self.query_server("loki", "service_logs", {
                "service": service_name,
                "duration": "1h",
                "limit": 50
            })
            results["logs"] = service_logs
        
        return {
            "service_overview": results,
            "service": service_name,
            "timestamp": datetime.now().isoformat()
        }

    async def search_across_platforms(self, query: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search across multiple platforms"""
        if platforms is None:
            platforms = list(self.servers.keys())
        
        results = {}
        
        for platform in platforms:
            if platform not in self.servers:
                continue
                
            try:
                if platform == "loki":
                    # Search logs
                    search_result = await self.query_server("loki", "search", {
                        "search_text": query,
                        "duration": "24h",
                        "limit": 20
                    })
                    results[platform] = search_result
                
                elif platform == "prometheus":
                    # Search metrics (if query looks like a metric name)
                    if "_" in query or "cpu" in query.lower() or "memory" in query.lower():
                        metrics_result = await self.query_server("prometheus", "metrics", {})
                        results[platform] = metrics_result
                
                # Add more platform-specific search logic as needed
                
            except Exception as e:
                results[platform] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "search_results": results,
            "query": query,
            "platforms_searched": platforms,
            "timestamp": datetime.now().isoformat()
        } 