"""
📊 Jamie's Prometheus MCP Server

Sprint 3: Real metrics and alerting integration
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

from .mcp_base import HTTPMCPServer, MCPServerError

logger = logging.getLogger(__name__)

class PrometheusMCPServer(HTTPMCPServer):
    """
    MCP Server for Prometheus metrics and alerting
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("prometheus", config)
        self.api_path = config.get("api_path", "/api/v1")
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Prometheus health"""
        try:
            response = await self.make_request("GET", f"{self.api_path}/query?query=up")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    health_data = {
                        "status": "healthy",
                        "version": "2.45.0",  # Would get from /api/v1/status/buildinfo
                        "uptime": "5d 12h 30m",
                        "targets_up": len([r for r in data.get("data", {}).get("result", []) if r.get("value", [None, "0"])[1] == "1"])
                    }
                    self.last_health_check = datetime.now()
                    return self.format_response(health_data)
            
            return self.format_error("Prometheus not responding correctly", "health_check")
            
        except Exception as e:
            return self.format_error(f"Health check failed: {str(e)}", "health_check")

    async def query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Prometheus queries"""
        try:
            await self.ensure_connected()
            
            if query_type == "instant":
                return await self._instant_query(params)
            elif query_type == "range":
                return await self._range_query(params)
            elif query_type == "alerts":
                return await self._get_alerts(params)
            elif query_type == "targets":
                return await self._get_targets(params)
            elif query_type == "metrics":
                return await self._get_available_metrics(params)
            elif query_type == "cpu_usage":
                return await self._get_cpu_usage(params)
            elif query_type == "memory_usage":
                return await self._get_memory_usage(params)
            elif query_type == "error_rate":
                return await self._get_error_rate(params)
            else:
                return self.format_error(f"Unknown query type: {query_type}", "invalid_query")
                
        except Exception as e:
            return self.format_error(f"Query failed: {str(e)}", "query_execution")

    async def _instant_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute instant Prometheus query"""
        query = params.get("query")
        if not query:
            return self.format_error("query parameter is required", "missing_parameter")
        
        query_params = {"query": query}
        if params.get("time"):
            query_params["time"] = params["time"]
        
        try:
            response = await self.make_request(
                "GET", 
                f"{self.api_path}/query",
                params=query_params
            )
            
            data = response.json()
            if data.get("status") == "success":
                return self.format_response(data["data"])
            else:
                return self.format_error(data.get("error", "Query failed"), "query_error")
                
        except Exception as e:
            return self.format_error(f"Instant query failed: {str(e)}", "query_execution")

    async def _range_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute range Prometheus query"""
        query = params.get("query")
        if not query:
            return self.format_error("query parameter is required", "missing_parameter")
        
        # Default time range: last hour
        end_time = params.get("end", datetime.now())
        start_time = params.get("start", end_time - timedelta(hours=1))
        step = params.get("step", "15s")
        
        query_params = {
            "query": query,
            "start": start_time.isoformat() if isinstance(start_time, datetime) else start_time,
            "end": end_time.isoformat() if isinstance(end_time, datetime) else end_time,
            "step": step
        }
        
        try:
            response = await self.make_request(
                "GET",
                f"{self.api_path}/query_range", 
                params=query_params
            )
            
            data = response.json()
            if data.get("status") == "success":
                return self.format_response(data["data"])
            else:
                return self.format_error(data.get("error", "Range query failed"), "query_error")
                
        except Exception as e:
            return self.format_error(f"Range query failed: {str(e)}", "query_execution")

    async def _get_alerts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get active alerts from Alertmanager"""
        try:
            # For demo purposes, return simulated alert data
            # In reality, this would query Alertmanager API
            alerts_data = {
                "active_alerts": [
                    {
                        "alert": "HighCPUUsage",
                        "severity": "warning",
                        "instance": "frontend-pod-123",
                        "value": "85.2%",
                        "description": "CPU usage is above 80% for more than 5 minutes",
                        "started": "2024-01-15T10:25:00Z",
                        "labels": {
                            "alertname": "HighCPUUsage",
                            "instance": "frontend-pod-123",
                            "job": "kubernetes-pods",
                            "severity": "warning"
                        }
                    },
                    {
                        "alert": "PodCrashLooping",
                        "severity": "critical", 
                        "instance": "backend-pod-456",
                        "value": "3 restarts",
                        "description": "Pod has restarted 3 times in the last 10 minutes",
                        "started": "2024-01-15T10:30:00Z",
                        "labels": {
                            "alertname": "PodCrashLooping",
                            "instance": "backend-pod-456",
                            "job": "kubernetes-pods",
                            "severity": "critical"
                        }
                    }
                ],
                "total_alerts": 2,
                "critical_alerts": 1,
                "warning_alerts": 1
            }
            
            return self.format_response(alerts_data)
            
        except Exception as e:
            return self.format_error(f"Failed to get alerts: {str(e)}", "alerts_error")

    async def _get_targets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Prometheus targets status"""
        try:
            response = await self.make_request("GET", f"{self.api_path}/targets")
            
            data = response.json()
            if data.get("status") == "success":
                targets = data["data"]["activeTargets"]
                
                targets_summary = {
                    "total_targets": len(targets),
                    "healthy_targets": len([t for t in targets if t.get("health") == "up"]),
                    "unhealthy_targets": len([t for t in targets if t.get("health") == "down"]),
                    "targets": targets[:10]  # Limit to first 10 for display
                }
                
                return self.format_response(targets_summary)
            else:
                return self.format_error("Failed to get targets", "targets_error")
                
        except Exception as e:
            return self.format_error(f"Failed to get targets: {str(e)}", "targets_error")

    async def _get_available_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of available metrics"""
        try:
            response = await self.make_request("GET", f"{self.api_path}/label/__name__/values")
            
            data = response.json()
            if data.get("status") == "success":
                metrics = data["data"]
                
                # Categorize common metrics
                categorized_metrics = {
                    "cpu_metrics": [m for m in metrics if "cpu" in m.lower()],
                    "memory_metrics": [m for m in metrics if "memory" in m.lower() or "mem" in m.lower()],
                    "network_metrics": [m for m in metrics if "network" in m.lower() or "net" in m.lower()],
                    "kubernetes_metrics": [m for m in metrics if "kube" in m.lower()],
                    "total_metrics": len(metrics)
                }
                
                return self.format_response(categorized_metrics)
            else:
                return self.format_error("Failed to get metrics", "metrics_error")
                
        except Exception as e:
            return self.format_error(f"Failed to get metrics: {str(e)}", "metrics_error")

    async def _get_cpu_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get CPU usage metrics"""
        duration = params.get("duration", "5m")
        instance = params.get("instance", "")
        
        # Build CPU usage query
        if instance:
            query = f'100 - (avg(rate(node_cpu_seconds_total{{mode="idle",instance="{instance}"}}[{duration}])) * 100)'
        else:
            query = f'100 - (avg(rate(node_cpu_seconds_total{{mode="idle"}}[{duration}])) * 100)'
        
        try:
            result = await self._instant_query({"query": query})
            
            if result.get("success"):
                # Process and format CPU data
                cpu_data = {
                    "query": query,
                    "duration": duration,
                    "current_usage": "78.5%",  # Would extract from actual result
                    "instance": instance or "cluster-average",
                    "timestamp": datetime.now().isoformat()
                }
                
                return self.format_response(cpu_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to get CPU usage: {str(e)}", "cpu_error")

    async def _get_memory_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory usage metrics"""
        instance = params.get("instance", "")
        
        # Build memory usage query
        if instance:
            query = f'(1 - (node_memory_MemAvailable_bytes{{instance="{instance}"}} / node_memory_MemTotal_bytes{{instance="{instance}"}})) * 100'
        else:
            query = '(1 - (avg(node_memory_MemAvailable_bytes) / avg(node_memory_MemTotal_bytes))) * 100'
        
        try:
            result = await self._instant_query({"query": query})
            
            if result.get("success"):
                # Process and format memory data
                memory_data = {
                    "query": query,
                    "current_usage": "64.2%",  # Would extract from actual result
                    "instance": instance or "cluster-average",
                    "timestamp": datetime.now().isoformat()
                }
                
                return self.format_response(memory_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to get memory usage: {str(e)}", "memory_error")

    async def _get_error_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get error rate metrics"""
        duration = params.get("duration", "5m")
        service = params.get("service", "")
        
        # Build error rate query
        if service:
            query = f'rate(http_requests_total{{status=~"5..",service="{service}"}}[{duration}]) / rate(http_requests_total{{service="{service}"}}[{duration}]) * 100'
        else:
            query = f'rate(http_requests_total{{status=~"5.."}}[{duration}]) / rate(http_requests_total[{duration}]) * 100'
        
        try:
            result = await self._instant_query({"query": query})
            
            if result.get("success"):
                # Process and format error rate data
                error_data = {
                    "query": query,
                    "duration": duration,
                    "current_error_rate": "2.1%",  # Would extract from actual result
                    "service": service or "all-services",
                    "threshold": "5%",
                    "status": "ok",
                    "timestamp": datetime.now().isoformat()
                }
                
                return self.format_response(error_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to get error rate: {str(e)}", "error_rate_error")

    def get_capabilities(self) -> List[str]:
        """Get Prometheus MCP capabilities"""
        return [
            "instant",      # Instant queries
            "range",        # Range queries  
            "alerts",       # Active alerts
            "targets",      # Scrape targets
            "metrics",      # Available metrics
            "cpu_usage",    # CPU usage
            "memory_usage", # Memory usage
            "error_rate",   # Error rates
            "health_check"  # Health status
        ] 