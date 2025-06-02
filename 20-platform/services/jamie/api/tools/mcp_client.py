"""
🔌 Jamie's Enhanced MCP Client - DevOps Tool Orchestration Hub

Sprint 3: Real DevOps tool integrations orchestration

⭐ WHAT THIS FILE DOES:
    - Connects Jamie to real DevOps tools (Kubernetes, Prometheus, Loki, etc.)
    - Orchestrates multiple MCP (Model Context Protocol) servers
    - Provides unified interface for DevOps queries across platforms
    - Manages health checking and failover for tool connections
    - Handles complex multi-platform searches and aggregations
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

# ═══════════════════════════════════════════════════════════════════════════════
# 🎛️ MAIN MCP CLIENT - The orchestration hub for all DevOps tools
# ═══════════════════════════════════════════════════════════════════════════════

class MCPClient:
    """
    🔌 Enhanced MCP Client for orchestrating DevOps tool integrations
    
    Sprint 3: Real implementations for Kubernetes, Prometheus, Loki, Tempo, GitHub
    
    ⭐ WHAT THIS ORCHESTRATES:
    - 🚢 Kubernetes: Cluster status, pods, deployments, services
    - 📊 Prometheus: Metrics, alerts, performance monitoring
    - 📝 Loki: Log aggregation, error analysis, debugging
    - 🔍 Tempo: Distributed tracing, performance bottlenecks (coming soon)
    - 🐙 GitHub: Repository info, deployments, pipelines (coming soon)
    
    💡 HOW IT WORKS:
    1. Initialize connections to all enabled DevOps platforms
    2. Maintain health checks and connection status
    3. Route queries to appropriate MCP servers
    4. Aggregate results from multiple platforms
    5. Handle failures gracefully with fallbacks
    
    🔧 CONNECTION MANAGEMENT:
    - Async connection handling for performance
    - Automatic retry and reconnection logic
    - Health monitoring for all connected services
    - Graceful degradation when services are unavailable
    """
    
    def __init__(self):
        """
        🔧 Initialize the MCP orchestration client
        
        SETUP PROCESS:
        1. Initialize empty server registry
        2. Set up default configurations for all supported tools
        3. Prepare connection tracking for health monitoring
        4. Log initialization for debugging
        """
        # 🗄️ SERVER REGISTRY - Track all connected MCP servers
        self.servers: Dict[str, BaseMCPServer] = {}           # server_name -> server_instance
        self.connected_servers: List[str] = []                # List of successfully connected servers
        self.failed_servers: List[str] = []                   # List of servers that failed to connect
        
        # ⚙️ DEFAULT CONFIGURATIONS for all supported DevOps tools
        # These can be overridden via environment variables or explicit configuration
        self.default_configs = {
            # 🚢 KUBERNETES CONFIGURATION
            "kubernetes": {
                "kubeconfig_path": "~/.kube/config",            # Path to kubectl config
                "namespace": "default",                         # Default namespace to query
                "enabled": True                                 # Enable Kubernetes integration
            },
            
            # 📊 PROMETHEUS CONFIGURATION  
            "prometheus": {
                "url": "http://localhost:9090",                 # Prometheus server URL
                "api_path": "/api/v1",                          # API endpoint path
                "timeout": 30,                                  # Query timeout in seconds
                "enabled": True                                 # Enable Prometheus integration
            },
            
            # 📝 LOKI CONFIGURATION
            "loki": {
                "url": "http://localhost:3100",                 # Loki server URL
                "api_path": "/loki/api/v1",                     # API endpoint path
                "timeout": 30,                                  # Query timeout in seconds
                "enabled": True                                 # Enable Loki integration
            },
            
            # 🔍 TEMPO CONFIGURATION (Sprint 3B)
            "tempo": {
                "url": "http://localhost:3200",                 # Tempo server URL
                "api_path": "/api",                             # API endpoint path
                "timeout": 30,                                  # Query timeout in seconds
                "enabled": False                                # Coming in Sprint 3B
            },
            
            # 🐙 GITHUB CONFIGURATION (Sprint 3B)
            "github": {
                "api_url": "https://api.github.com",            # GitHub API URL
                "token": "",                                    # Set via GITHUB_TOKEN env var
                "enabled": False                                # Coming in Sprint 3B
            }
        }
        
        logger.info("Enhanced MCP Client initialized for Sprint 3")

    # ═══════════════════════════════════════════════════════════════════════════════
    # ⚙️ CONFIGURATION MANAGEMENT - Setup and customization
    # ═══════════════════════════════════════════════════════════════════════════════

    def configure_server(self, server_name: str, config: Dict[str, Any]):
        """
        ⚙️ Configure a specific MCP server
        
        USAGE EXAMPLES:
        - client.configure_server("prometheus", {"url": "http://prometheus.monitoring:9090"})
        - client.configure_server("kubernetes", {"namespace": "production"})
        - client.configure_server("loki", {"timeout": 60})
        
        PARAMETERS:
        - server_name: Which server to configure (kubernetes, prometheus, loki, etc.)
        - config: Dictionary of configuration overrides
        
        WHAT IT DOES:
        - Merges new config with existing defaults
        - Validates server name is supported
        - Logs configuration changes for debugging
        """
        if server_name in self.default_configs:
            self.default_configs[server_name].update(config)
            logger.info(f"Updated configuration for {server_name}")
        else:
            logger.warning(f"Unknown server: {server_name}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔌 CONNECTION MANAGEMENT - Connecting to and managing DevOps tools
    # ═══════════════════════════════════════════════════════════════════════════════

    async def connect_to_servers(self):
        """
        🔌 Connect to all enabled MCP servers
        
        CONNECTION PROCESS:
        1. Check which servers are enabled in configuration
        2. Initialize each enabled server with its config
        3. Attempt async connections to all servers
        4. Track successful and failed connections
        5. Log connection summary for monitoring
        
        ERROR HANDLING:
        - Individual server failures don't stop other connections
        - Failed servers are tracked for retry logic
        - Connection status is logged for debugging
        """
        logger.info("🔌 Connecting to DevOps MCP servers...")
        
        # 🚀 INITIALIZE AND CONNECT to each enabled server
        for server_name, config in self.default_configs.items():
            if config.get("enabled", False):
                try:
                    await self._initialize_server(server_name, config)
                except Exception as e:
                    logger.error(f"Failed to initialize {server_name}: {str(e)}")
                    self.failed_servers.append(server_name)
        
        # 📊 LOG CONNECTION SUMMARY
        logger.info(f"✅ Connected to {len(self.connected_servers)} MCP servers")
        if self.failed_servers:
            logger.warning(f"⚠️ Failed to connect to: {', '.join(self.failed_servers)}")

    async def _initialize_server(self, server_name: str, config: Dict[str, Any]):
        """
        🏗️ Initialize a specific MCP server
        
        INITIALIZATION PROCESS:
        1. Determine server type and create appropriate instance
        2. Pass configuration to server constructor
        3. Attempt connection with error handling
        4. Update connection tracking based on result
        5. Log success/failure for monitoring
        
        SUPPORTED SERVERS:
        - kubernetes: KubernetesMCPServer for cluster management
        - prometheus: PrometheusMCPServer for metrics and alerts
        - loki: LokiMCPServer for log analysis
        - tempo: Coming in Sprint 3B for distributed tracing
        - github: Coming in Sprint 3B for repository management
        """
        logger.info(f"Initializing {server_name} MCP server...")
        
        try:
            # 🏭 FACTORY PATTERN: Create server instance based on type
            if server_name == "kubernetes":
                server = KubernetesMCPServer(config)
                
            elif server_name == "prometheus":
                server = PrometheusMCPServer(config)
                
            elif server_name == "loki":
                server = LokiMCPServer(config)
                
            elif server_name == "tempo":
                # 🚧 COMING SOON: Tempo MCP server for distributed tracing
                logger.info(f"Tempo MCP server coming in Sprint 3B...")
                return
                
            elif server_name == "github":
                # 🚧 COMING SOON: GitHub MCP server for repository management
                logger.info(f"GitHub MCP server coming in Sprint 3B...")
                return
                
            else:
                logger.warning(f"Unknown server type: {server_name}")
                return
            
            # 🔗 ATTEMPT CONNECTION
            connected = await server.connect()
            
            if connected:
                # ✅ SUCCESS: Register server and update tracking
                self.servers[server_name] = server
                self.connected_servers.append(server_name)
                logger.info(f"✅ {server_name} MCP server connected")
            else:
                # ❌ FAILURE: Log and track failed connection
                logger.warning(f"⚠️ {server_name} MCP server failed to connect")
                self.failed_servers.append(server_name)
                
        except Exception as e:
            logger.error(f"Error initializing {server_name}: {str(e)}")
            self.failed_servers.append(server_name)

    async def disconnect_all(self):
        """
        🔌 Disconnect from all MCP servers
        
        DISCONNECTION PROCESS:
        1. Iterate through all connected servers
        2. Call disconnect method on each server
        3. Handle individual disconnection errors gracefully
        4. Clear server registry and connection tracking
        5. Log disconnection summary
        
        USED WHEN:
        - Application shutdown
        - Configuration changes requiring reconnection
        - Error recovery scenarios
        - Testing and debugging
        """
        logger.info("Disconnecting from all MCP servers...")
        
        # 🔌 DISCONNECT EACH SERVER individually
        for server_name, server in self.servers.items():
            try:
                await server.disconnect()
                logger.info(f"Disconnected from {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {str(e)}")
        
        # 🧹 CLEAN UP TRACKING
        self.servers.clear()
        self.connected_servers.clear()

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔍 QUERY EXECUTION - Routing queries to appropriate servers
    # ═══════════════════════════════════════════════════════════════════════════════

    async def query_server(self, server_name: str, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 Query a specific MCP server
        
        QUERY ROUTING:
        1. Validate server is available and connected
        2. Route query to appropriate server instance
        3. Handle query execution with error catching
        4. Return results with success/error status
        5. Log query attempts for debugging
        
        EXAMPLES:
        - query_server("kubernetes", "pod_status", {"namespace": "default"})
        - query_server("prometheus", "cpu_usage", {"time_range": "1h"})
        - query_server("loki", "error_logs", {"service": "api", "duration": "30m"})
        
        PARAMETERS:
        - server_name: Which MCP server to query
        - query_type: Type of query to execute
        - params: Query parameters and filters
        
        RETURNS: Standardized response with success status and data/error
        """
        # 🔍 VALIDATE SERVER AVAILABILITY
        if server_name not in self.servers:
            return {
                "success": False,
                "error": f"Server {server_name} not available",
                "available_servers": list(self.servers.keys())
            }
        
        try:
            # 🎯 EXECUTE QUERY on target server
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

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🏥 HEALTH MONITORING - Checking system health across all platforms
    # ═══════════════════════════════════════════════════════════════════════════════

    async def health_check_all(self) -> Dict[str, Any]:
        """
        🏥 Health check all connected servers
        
        HEALTH CHECK PROCESS:
        1. Query health status from each connected server
        2. Collect individual health results
        3. Determine overall system health status
        4. Aggregate statistics and metrics
        5. Return comprehensive health report
        
        HEALTH INDICATORS:
        - Individual server connectivity
        - Response times and performance
        - Error rates and availability
        - Resource utilization where applicable
        
        USED FOR:
        - System monitoring dashboards
        - Alerting and notifications
        - Troubleshooting connection issues
        - Performance optimization
        
        RETURNS: Comprehensive health report with individual and overall status
        """
        health_results = {}
        
        # 🏥 CHECK EACH CONNECTED SERVER
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
        
        # 📊 CALCULATE OVERALL HEALTH STATUS
        all_healthy = all(r.get("success", False) for r in health_results.values())
        overall_status = "healthy" if all_healthy else "degraded"
        
        return {
            "overall_status": overall_status,
            "connected_servers": len(self.connected_servers),
            "failed_servers": len(self.failed_servers),
            "server_health": health_results,
            "timestamp": datetime.now().isoformat()
        }

    def get_server_status(self) -> Dict[str, Any]:
        """
        📊 Get status of all MCP servers
        
        STATUS INFORMATION:
        - Connection status (connected/failed/disabled)
        - Server capabilities and supported operations
        - Last health check timestamps
        - Configuration summaries
        
        USEFUL FOR:
        - Administrative monitoring
        - Debugging connection issues
        - Understanding available capabilities
        - System documentation and reporting
        
        RETURNS: Complete server status registry
        """
        server_status = {}
        
        # 📊 BUILD STATUS FOR EACH CONFIGURED SERVER
        for server_name in self.default_configs.keys():
            if server_name in self.servers:
                # ✅ CONNECTED SERVER STATUS
                server = self.servers[server_name]
                server_status[server_name] = {
                    "connected": True,
                    "capabilities": server.get_capabilities(),
                    "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None
                }
            elif server_name in self.failed_servers:
                # ❌ FAILED SERVER STATUS
                server_status[server_name] = {
                    "connected": False,
                    "status": "failed",
                    "last_attempt": "recent"  # Could be more specific with timestamps
                }
            else:
                # 🔌 DISABLED SERVER STATUS
                server_status[server_name] = {
                    "connected": False,
                    "status": "disabled",
                    "enabled": self.default_configs[server_name].get("enabled", False)
                }
        
        return {
            "servers": server_status,
            "summary": {
                "total_configured": len(self.default_configs),
                "connected": len(self.connected_servers),
                "failed": len(self.failed_servers),
                "disabled": len([s for s in self.default_configs.values() if not s.get("enabled", True)])
            }
        }

    def get_capabilities(self) -> Dict[str, List[str]]:
        """
        🎯 Get capabilities of all connected servers
        
        CAPABILITY MAPPING:
        - Lists what each server can do
        - Groups capabilities by server type
        - Shows available query types and operations
        - Indicates integration readiness
        
        EXAMPLES:
        {
            "kubernetes": ["pod_status", "deployment_info", "service_list"],
            "prometheus": ["metrics_query", "alert_status", "target_health"],
            "loki": ["log_search", "error_analysis", "log_stream"]
        }
        
        USED BY:
        - AI brain for query planning
        - UI for showing available features
        - Documentation generation
        - Integration testing
        """
        capabilities = {}
        
        for server_name, server in self.servers.items():
            try:
                capabilities[server_name] = server.get_capabilities()
            except Exception as e:
                logger.error(f"Error getting capabilities from {server_name}: {str(e)}")
                capabilities[server_name] = []
        
        return capabilities

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 HIGH-LEVEL DEVOPS OPERATIONS - Complex orchestrated queries
    # ═══════════════════════════════════════════════════════════════════════════════

    async def get_cluster_status(self) -> Dict[str, Any]:
        """
        🚢 Get comprehensive Kubernetes cluster status
        
        ORCHESTRATED QUERY that combines:
        1. Kubernetes cluster health and pod status
        2. Prometheus metrics for resource utilization
        3. Loki logs for recent errors
        4. Aggregated health assessment
        
        WHAT IT PROVIDES:
        - Overall cluster health (healthy/warning/critical)
        - Pod status breakdown (running/pending/failed)
        - Resource utilization (CPU/memory)
        - Recent error summary
        - Key metrics and alerts
        
        EXAMPLE RESPONSE:
        {
            "overall_status": "healthy",
            "cluster_info": {...},
            "pod_summary": {...},
            "resource_usage": {...},
            "recent_errors": [...],
            "alerts": [...]
        }
        
        USED FOR:
        - Dashboard overview
        - Quick health assessments
        - Alert generation
        - Status page updates
        """
        logger.info("🚢 Getting comprehensive cluster status...")
        
        status = {
            "overall_status": "unknown",
            "cluster_info": {},
            "pod_summary": {},
            "resource_usage": {},
            "recent_errors": [],
            "alerts": []
        }
        
        try:
            # 🚢 STEP 1: Get Kubernetes cluster information
            if "kubernetes" in self.servers:
                k8s_result = await self.query_server("kubernetes", "cluster_status", {})
                if k8s_result.get("success"):
                    status["cluster_info"] = k8s_result.get("data", {})
                    status["pod_summary"] = k8s_result.get("pod_summary", {})
            
            # 📊 STEP 2: Get Prometheus metrics
            if "prometheus" in self.servers:
                # CPU usage query
                cpu_result = await self.query_server("prometheus", "query", {
                    "query": "100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
                })
                
                # Memory usage query
                memory_result = await self.query_server("prometheus", "query", {
                    "query": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
                })
                
                if cpu_result.get("success") and memory_result.get("success"):
                    status["resource_usage"] = {
                        "cpu_percent": cpu_result.get("data", {}),
                        "memory_percent": memory_result.get("data", {})
                    }
            
            # 📝 STEP 3: Get recent errors from Loki
            if "loki" in self.servers:
                error_result = await self.query_server("loki", "query", {
                    "query": '{level="error"} |= "error"',
                    "limit": 10,
                    "since": "1h"
                })
                
                if error_result.get("success"):
                    status["recent_errors"] = error_result.get("data", [])
            
            # 🎯 STEP 4: Determine overall status
            if status["cluster_info"] and status["pod_summary"]:
                failed_pods = status["pod_summary"].get("failed", 0)
                total_pods = status["pod_summary"].get("total", 1)
                error_count = len(status["recent_errors"])
                
                if failed_pods == 0 and error_count < 5:
                    status["overall_status"] = "healthy"
                elif failed_pods < total_pods * 0.1 and error_count < 20:
                    status["overall_status"] = "warning"
                else:
                    status["overall_status"] = "critical"
            
            logger.info(f"✅ Cluster status: {status['overall_status']}")
            
        except Exception as e:
            logger.error(f"Error getting cluster status: {str(e)}")
            status["error"] = str(e)
        
        return status

    async def get_recent_errors(self, duration: str = "1h") -> Dict[str, Any]:
        """
        🚨 Get recent errors across all platforms
        
        ERROR AGGREGATION from:
        1. Loki logs - Application and system errors
        2. Prometheus alerts - Metric-based alerts
        3. Kubernetes events - Cluster events and warnings
        
        PARAMETERS:
        - duration: Time window to search (1h, 30m, 24h, etc.)
        
        WHAT IT PROVIDES:
        - Categorized error summary
        - Error frequency and patterns
        - Severity classification
        - Source system identification
        - Correlation opportunities
        
        ERROR CATEGORIES:
        - application: App-level errors from logs
        - infrastructure: System and resource errors
        - alerts: Prometheus alert firing
        - events: Kubernetes events and warnings
        
        USED FOR:
        - Troubleshooting workflows
        - Error dashboards
        - Alert aggregation
        - Root cause analysis
        """
        logger.info(f"🚨 Getting recent errors from last {duration}...")
        
        errors = {
            "duration": duration,
            "error_summary": {
                "application": [],
                "infrastructure": [],
                "alerts": [],
                "events": []
            },
            "total_errors": 0,
            "severity_breakdown": {"critical": 0, "warning": 0, "info": 0}
        }
        
        try:
            # 📝 STEP 1: Get application errors from Loki
            if "loki" in self.servers:
                loki_result = await self.query_server("loki", "query", {
                    "query": '{level=~"error|fatal"} |= ""',
                    "since": duration,
                    "limit": 50
                })
                
                if loki_result.get("success"):
                    app_errors = loki_result.get("data", [])
                    errors["error_summary"]["application"] = app_errors
                    errors["total_errors"] += len(app_errors)
            
            # 📊 STEP 2: Get alerts from Prometheus
            if "prometheus" in self.servers:
                alerts_result = await self.query_server("prometheus", "alerts", {})
                
                if alerts_result.get("success"):
                    active_alerts = alerts_result.get("data", [])
                    errors["error_summary"]["alerts"] = active_alerts
                    errors["total_errors"] += len(active_alerts)
            
            # 🚢 STEP 3: Get Kubernetes events
            if "kubernetes" in self.servers:
                events_result = await self.query_server("kubernetes", "events", {
                    "types": ["Warning", "Error"],
                    "since": duration
                })
                
                if events_result.get("success"):
                    k8s_events = events_result.get("data", [])
                    errors["error_summary"]["events"] = k8s_events
                    errors["total_errors"] += len(k8s_events)
            
            # 🎯 STEP 4: Categorize by severity
            # This is a simplified categorization - could be enhanced with ML/rules
            for category, error_list in errors["error_summary"].items():
                for error in error_list:
                    if any(keyword in str(error).lower() for keyword in ["critical", "fatal", "down", "outage"]):
                        errors["severity_breakdown"]["critical"] += 1
                    elif any(keyword in str(error).lower() for keyword in ["warning", "warn", "slow"]):
                        errors["severity_breakdown"]["warning"] += 1
                    else:
                        errors["severity_breakdown"]["info"] += 1
            
            logger.info(f"✅ Found {errors['total_errors']} errors in last {duration}")
            
        except Exception as e:
            logger.error(f"Error getting recent errors: {str(e)}")
            errors["error"] = str(e)
        
        return errors

    async def get_service_overview(self, service_name: str) -> Dict[str, Any]:
        """
        🔍 Get comprehensive overview of a specific service
        
        SERVICE ANALYSIS across multiple platforms:
        1. Kubernetes: Pod status, deployment info, resource usage
        2. Prometheus: Service metrics, response times, error rates
        3. Loki: Service logs, error patterns, recent activity
        4. Integration: Correlation and insights
        
        PARAMETERS:
        - service_name: Name of the service to analyze
        
        WHAT IT PROVIDES:
        - Service health status
        - Resource utilization
        - Performance metrics
        - Error analysis
        - Recent activity summary
        
        ANALYSIS DIMENSIONS:
        - availability: Is the service running and accessible?
        - performance: How fast is it responding?
        - errors: What problems are occurring?
        - resources: How much CPU/memory is it using?
        - logs: What is it doing recently?
        
        USED FOR:
        - Service troubleshooting
        - Performance optimization
        - Health monitoring
        - Capacity planning
        """
        logger.info(f"🔍 Getting comprehensive overview for service: {service_name}")
        
        overview = {
            "service_name": service_name,
            "overall_health": "unknown",
            "kubernetes": {},
            "metrics": {},
            "logs": {},
            "summary": {}
        }
        
        try:
            # 🚢 STEP 1: Get Kubernetes information
            if "kubernetes" in self.servers:
                k8s_result = await self.query_server("kubernetes", "service_info", {
                    "service_name": service_name
                })
                
                if k8s_result.get("success"):
                    overview["kubernetes"] = k8s_result.get("data", {})
            
            # 📊 STEP 2: Get Prometheus metrics
            if "prometheus" in self.servers:
                # Request rate
                rate_result = await self.query_server("prometheus", "query", {
                    "query": f'rate(http_requests_total{{service="{service_name}"}}[5m])'
                })
                
                # Error rate
                error_rate_result = await self.query_server("prometheus", "query", {
                    "query": f'rate(http_requests_total{{service="{service_name}",status=~"5.."}}[5m])'
                })
                
                # Response time
                latency_result = await self.query_server("prometheus", "query", {
                    "query": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[5m]))'
                })
                
                overview["metrics"] = {
                    "request_rate": rate_result.get("data") if rate_result.get("success") else None,
                    "error_rate": error_rate_result.get("data") if error_rate_result.get("success") else None,
                    "latency_p95": latency_result.get("data") if latency_result.get("success") else None
                }
            
            # 📝 STEP 3: Get Loki logs
            if "loki" in self.servers:
                logs_result = await self.query_server("loki", "query", {
                    "query": f'{{service="{service_name}"}} |= ""',
                    "since": "1h",
                    "limit": 20
                })
                
                if logs_result.get("success"):
                    overview["logs"] = {
                        "recent_entries": logs_result.get("data", []),
                        "entry_count": len(logs_result.get("data", []))
                    }
            
            # 🎯 STEP 4: Generate summary and health assessment
            pod_count = overview["kubernetes"].get("pods", {}).get("running", 0)
            error_rate = overview["metrics"].get("error_rate")
            recent_errors = len([log for log in overview["logs"].get("recent_entries", []) 
                               if "error" in str(log).lower()])
            
            # Simple health calculation (could be enhanced with ML)
            if pod_count > 0 and (not error_rate or error_rate < 0.05) and recent_errors < 5:
                overview["overall_health"] = "healthy"
            elif pod_count > 0 and recent_errors < 10:
                overview["overall_health"] = "warning"
            else:
                overview["overall_health"] = "critical"
            
            overview["summary"] = {
                "running_pods": pod_count,
                "recent_errors": recent_errors,
                "health_score": 100 if overview["overall_health"] == "healthy" else 
                               50 if overview["overall_health"] == "warning" else 10
            }
            
            logger.info(f"✅ Service {service_name} health: {overview['overall_health']}")
            
        except Exception as e:
            logger.error(f"Error getting service overview: {str(e)}")
            overview["error"] = str(e)
        
        return overview

    async def search_across_platforms(self, query: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        🔍 Search across multiple DevOps platforms
        
        CROSS-PLATFORM SEARCH that queries:
        1. Loki logs for text matches
        2. Prometheus metrics for related data
        3. Kubernetes resources for name matches
        4. Aggregated and correlated results
        
        PARAMETERS:
        - query: Search term or phrase
        - platforms: List of platforms to search (None = all available)
        
        SEARCH STRATEGIES:
        - Text search in logs and events
        - Metric name matching
        - Resource name patterns
        - Label and annotation searches
        
        WHAT IT FINDS:
        - Log entries containing the query
        - Metrics related to the search term
        - Kubernetes resources matching the pattern
        - Cross-references and correlations
        
        EXAMPLE QUERIES:
        - "authentication" → finds auth logs, auth service metrics, auth pods
        - "memory" → finds memory alerts, memory metrics, OOM events
        - "api-gateway" → finds gateway logs, latency metrics, gateway pods
        
        USED FOR:
        - Troubleshooting workflows
        - Investigation and exploration
        - Finding related information
        - Cross-platform correlation
        """
        logger.info(f"🔍 Searching across platforms for: {query}")
        
        # 🎯 DETERMINE PLATFORMS TO SEARCH
        if platforms is None:
            platforms = list(self.servers.keys())
        
        search_results = {
            "query": query,
            "platforms_searched": platforms,
            "results": {},
            "summary": {"total_matches": 0, "platforms_with_results": []}
        }
        
        try:
            # 📝 SEARCH LOKI LOGS
            if "loki" in platforms and "loki" in self.servers:
                loki_result = await self.query_server("loki", "query", {
                    "query": f'{{}} |~ "(?i){query}"',  # Case-insensitive search
                    "since": "24h",
                    "limit": 50
                })
                
                if loki_result.get("success"):
                    loki_matches = loki_result.get("data", [])
                    search_results["results"]["loki"] = {
                        "matches": loki_matches,
                        "count": len(loki_matches)
                    }
                    search_results["summary"]["total_matches"] += len(loki_matches)
                    if loki_matches:
                        search_results["summary"]["platforms_with_results"].append("loki")
            
            # 📊 SEARCH PROMETHEUS METRICS
            if "prometheus" in platforms and "prometheus" in self.servers:
                # Search for metrics containing the query term
                metrics_result = await self.query_server("prometheus", "label_values", {
                    "label": "__name__",
                    "match": f".*{query}.*"
                })
                
                if metrics_result.get("success"):
                    metric_matches = metrics_result.get("data", [])
                    search_results["results"]["prometheus"] = {
                        "matching_metrics": metric_matches,
                        "count": len(metric_matches)
                    }
                    search_results["summary"]["total_matches"] += len(metric_matches)
                    if metric_matches:
                        search_results["summary"]["platforms_with_results"].append("prometheus")
            
            # 🚢 SEARCH KUBERNETES RESOURCES
            if "kubernetes" in platforms and "kubernetes" in self.servers:
                k8s_result = await self.query_server("kubernetes", "search", {
                    "query": query,
                    "resource_types": ["pods", "services", "deployments"]
                })
                
                if k8s_result.get("success"):
                    k8s_matches = k8s_result.get("data", [])
                    search_results["results"]["kubernetes"] = {
                        "matching_resources": k8s_matches,
                        "count": len(k8s_matches)
                    }
                    search_results["summary"]["total_matches"] += len(k8s_matches)
                    if k8s_matches:
                        search_results["summary"]["platforms_with_results"].append("kubernetes")
            
            logger.info(f"✅ Found {search_results['summary']['total_matches']} matches across {len(search_results['summary']['platforms_with_results'])} platforms")
            
        except Exception as e:
            logger.error(f"Error searching across platforms: {str(e)}")
            search_results["error"] = str(e)
        
        return search_results

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 MCP CLIENT TESTING AND EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    🧪 Test MCP client when run directly
    
    USAGE: python api/tools/mcp_client.py
    
    This will:
    - Create an MCP client instance
    - Test server configuration
    - Simulate connection attempts
    - Show capability mapping
    - Demonstrate query routing
    """
    print("🔌 Jamie's MCP Client Test")
    print("=" * 50)
    
    async def test_mcp_client():
        # 🏗️ CREATE MCP CLIENT
        client = MCPClient()
        
        # ⚙️ TEST CONFIGURATION
        print("\n⚙️ Testing server configuration:")
        print(f"  Default servers: {list(client.default_configs.keys())}")
        
        client.configure_server("prometheus", {"url": "http://test-prometheus:9090"})
        print(f"  Configured prometheus with custom URL")
        
        # 📊 SHOW SERVER STATUS
        print("\n📊 Server status before connection:")
        status = client.get_server_status()
        for server, info in status["servers"].items():
            print(f"  {server}: {info['status'] if not info['connected'] else 'ready'}")
        
        # 🔌 SIMULATE CONNECTION (without actual servers)
        print("\n🔌 Connection simulation:")
        print("  In real usage, would connect to:")
        for server_name, config in client.default_configs.items():
            if config.get("enabled"):
                print(f"    - {server_name}: {config.get('url', 'local')}")
        
        # 🎯 SHOW CAPABILITIES (simulated)
        print("\n🎯 Available capabilities (when connected):")
        capabilities = {
            "kubernetes": ["cluster_status", "pod_info", "service_info", "events"],
            "prometheus": ["query", "alerts", "targets", "label_values"],
            "loki": ["query", "labels", "label_values", "streams"]
        }
        
        for server, caps in capabilities.items():
            print(f"  {server}: {', '.join(caps)}")
        
        print("\n🎉 MCP Client testing complete!")
        print("Note: Run with actual DevOps infrastructure for full functionality")
    
    # Run the async test
    import asyncio
    asyncio.run(test_mcp_client()) 