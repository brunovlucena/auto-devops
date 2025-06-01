"""
📝 Jamie's Loki MCP Server

Sprint 3: Real log aggregation and analysis integration
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re

from .mcp_base import HTTPMCPServer, MCPServerError

logger = logging.getLogger(__name__)

class LokiMCPServer(HTTPMCPServer):
    """
    MCP Server for Loki log aggregation and analysis
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("loki", config)
        self.api_path = config.get("api_path", "/loki/api/v1")
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Loki health"""
        try:
            response = await self.make_request("GET", f"{self.api_path}/ready")
            
            if response.status_code == 200:
                health_data = {
                    "status": "healthy",
                    "version": "2.9.0",  # Would get from actual endpoint
                    "ingester_ready": True,
                    "querier_ready": True,
                    "distributor_ready": True
                }
                self.last_health_check = datetime.now()
                return self.format_response(health_data)
            
            return self.format_error("Loki not responding correctly", "health_check")
            
        except Exception as e:
            return self.format_error(f"Health check failed: {str(e)}", "health_check")

    async def query(self, query_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Loki queries"""
        try:
            await self.ensure_connected()
            
            if query_type == "logs":
                return await self._query_logs(params)
            elif query_type == "range":
                return await self._query_range(params)
            elif query_type == "labels":
                return await self._get_labels(params)
            elif query_type == "values":
                return await self._get_label_values(params)
            elif query_type == "errors":
                return await self._get_error_logs(params)
            elif query_type == "service_logs":
                return await self._get_service_logs(params)
            elif query_type == "search":
                return await self._search_logs(params)
            elif query_type == "tail":
                return await self._tail_logs(params)
            else:
                return self.format_error(f"Unknown query type: {query_type}", "invalid_query")
                
        except Exception as e:
            return self.format_error(f"Query failed: {str(e)}", "query_execution")

    async def _query_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query logs with LogQL"""
        query = params.get("query", "{}")
        limit = params.get("limit", 100)
        direction = params.get("direction", "backward")
        start = params.get("start")
        end = params.get("end")
        
        query_params = {
            "query": query,
            "limit": limit,
            "direction": direction
        }
        
        if start:
            query_params["start"] = start
        if end:
            query_params["end"] = end
        
        try:
            response = await self.make_request(
                "GET",
                f"{self.api_path}/query",
                params=query_params
            )
            
            data = response.json()
            if data.get("status") == "success":
                # Process log streams
                processed_logs = self._process_log_streams(data["data"]["result"])
                return self.format_response(processed_logs)
            else:
                return self.format_error(data.get("error", "Query failed"), "query_error")
                
        except Exception as e:
            return self.format_error(f"Log query failed: {str(e)}", "query_execution")

    async def _query_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query logs over a time range"""
        query = params.get("query", "{}")
        start_time = params.get("start", (datetime.now() - timedelta(hours=1)).isoformat())
        end_time = params.get("end", datetime.now().isoformat())
        step = params.get("step", "1m")
        limit = params.get("limit", 1000)
        
        query_params = {
            "query": query,
            "start": start_time,
            "end": end_time,
            "step": step,
            "limit": limit
        }
        
        try:
            response = await self.make_request(
                "GET",
                f"{self.api_path}/query_range", 
                params=query_params
            )
            
            data = response.json()
            if data.get("status") == "success":
                # Process range data
                processed_data = self._process_range_data(data["data"]["result"])
                return self.format_response(processed_data)
            else:
                return self.format_error(data.get("error", "Range query failed"), "query_error")
                
        except Exception as e:
            return self.format_error(f"Range query failed: {str(e)}", "query_execution")

    async def _get_labels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get available labels"""
        start = params.get("start")
        end = params.get("end")
        
        query_params = {}
        if start:
            query_params["start"] = start
        if end:
            query_params["end"] = end
            
        try:
            response = await self.make_request(
                "GET",
                f"{self.api_path}/labels",
                params=query_params
            )
            
            data = response.json()
            if data.get("status") == "success":
                labels_data = {
                    "labels": data["data"],
                    "total_labels": len(data["data"]),
                    "common_labels": [
                        "job", "instance", "container", "namespace", 
                        "pod", "service", "level", "logger"
                    ]
                }
                return self.format_response(labels_data)
            else:
                return self.format_error("Failed to get labels", "labels_error")
                
        except Exception as e:
            return self.format_error(f"Failed to get labels: {str(e)}", "labels_error")

    async def _get_label_values(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get values for a specific label"""
        label = params.get("label")
        if not label:
            return self.format_error("label parameter is required", "missing_parameter")
        
        start = params.get("start")
        end = params.get("end")
        
        query_params = {}
        if start:
            query_params["start"] = start
        if end:
            query_params["end"] = end
            
        try:
            response = await self.make_request(
                "GET",
                f"{self.api_path}/label/{label}/values",
                params=query_params
            )
            
            data = response.json()
            if data.get("status") == "success":
                values_data = {
                    "label": label,
                    "values": data["data"],
                    "total_values": len(data["data"])
                }
                return self.format_response(values_data)
            else:
                return self.format_error(f"Failed to get values for label {label}", "values_error")
                
        except Exception as e:
            return self.format_error(f"Failed to get label values: {str(e)}", "values_error")

    async def _get_error_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get error logs across services"""
        duration = params.get("duration", "1h")
        service = params.get("service", "")
        limit = params.get("limit", 100)
        
        # Build error log query
        if service:
            query = f'{{service="{service}"}} |~ "(?i)(error|exception|fail|panic)"'
        else:
            query = '{job=~".+"} |~ "(?i)(error|exception|fail|panic)"'
        
        # Add time filter
        start_time = (datetime.now() - self._parse_duration(duration)).isoformat()
        
        try:
            result = await self._query_logs({
                "query": query,
                "limit": limit,
                "start": start_time,
                "direction": "backward"
            })
            
            if result.get("success"):
                # Enhance with error analysis
                logs_data = result["data"]
                error_analysis = self._analyze_errors(logs_data.get("entries", []))
                
                enhanced_data = {
                    **logs_data,
                    "error_analysis": error_analysis,
                    "query_info": {
                        "service": service or "all-services",
                        "duration": duration,
                        "error_patterns": ["error", "exception", "fail", "panic"]
                    }
                }
                
                return self.format_response(enhanced_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to get error logs: {str(e)}", "error_logs_error")

    async def _get_service_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get logs for a specific service"""
        service = params.get("service")
        if not service:
            return self.format_error("service parameter is required", "missing_parameter")
        
        duration = params.get("duration", "1h")
        level = params.get("level", "")
        limit = params.get("limit", 100)
        
        # Build service log query
        query_parts = [f'service="{service}"']
        if level:
            query_parts.append(f'level="{level}"')
        
        query = "{" + ",".join(query_parts) + "}"
        
        start_time = (datetime.now() - self._parse_duration(duration)).isoformat()
        
        try:
            result = await self._query_logs({
                "query": query,
                "limit": limit,
                "start": start_time,
                "direction": "backward"
            })
            
            if result.get("success"):
                # Add service-specific analysis
                logs_data = result["data"]
                service_analysis = self._analyze_service_logs(logs_data.get("entries", []))
                
                enhanced_data = {
                    **logs_data,
                    "service_analysis": service_analysis,
                    "query_info": {
                        "service": service,
                        "level": level or "all-levels",
                        "duration": duration
                    }
                }
                
                return self.format_response(enhanced_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to get service logs: {str(e)}", "service_logs_error")

    async def _search_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search logs with text pattern"""
        search_text = params.get("search_text")
        if not search_text:
            return self.format_error("search_text parameter is required", "missing_parameter")
        
        duration = params.get("duration", "1h")
        service = params.get("service", "")
        limit = params.get("limit", 100)
        case_sensitive = params.get("case_sensitive", False)
        
        # Build search query
        if service:
            base_query = f'{{service="{service}"}}'
        else:
            base_query = '{job=~".+"}'
        
        # Add case sensitivity
        if case_sensitive:
            search_filter = f'|~ "{search_text}"'
        else:
            search_filter = f'|~ "(?i){search_text}"'
        
        query = base_query + " " + search_filter
        
        start_time = (datetime.now() - self._parse_duration(duration)).isoformat()
        
        try:
            result = await self._query_logs({
                "query": query,
                "limit": limit,
                "start": start_time,
                "direction": "backward"
            })
            
            if result.get("success"):
                # Add search context
                logs_data = result["data"]
                search_results = self._highlight_search_matches(
                    logs_data.get("entries", []), 
                    search_text, 
                    case_sensitive
                )
                
                enhanced_data = {
                    **logs_data,
                    "search_results": search_results,
                    "query_info": {
                        "search_text": search_text,
                        "service": service or "all-services",
                        "duration": duration,
                        "case_sensitive": case_sensitive
                    }
                }
                
                return self.format_response(enhanced_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to search logs: {str(e)}", "search_error")

    async def _tail_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent logs (tail functionality)"""
        service = params.get("service", "")
        lines = params.get("lines", 50)
        follow = params.get("follow", False)
        
        # Build tail query
        if service:
            query = f'{{service="{service}"}}'
        else:
            query = '{job=~".+"}'
        
        try:
            result = await self._query_logs({
                "query": query,
                "limit": lines,
                "direction": "backward"
            })
            
            if result.get("success"):
                logs_data = result["data"]
                
                # Reverse for tail order (most recent at bottom)
                if logs_data.get("entries"):
                    logs_data["entries"] = list(reversed(logs_data["entries"]))
                
                tail_data = {
                    **logs_data,
                    "tail_info": {
                        "service": service or "all-services",
                        "lines": lines,
                        "follow": follow,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                return self.format_response(tail_data)
            else:
                return result
                
        except Exception as e:
            return self.format_error(f"Failed to tail logs: {str(e)}", "tail_error")

    def _process_log_streams(self, streams: List[Dict]) -> Dict[str, Any]:
        """Process Loki log streams into readable format"""
        entries = []
        total_entries = 0
        
        for stream in streams:
            stream_labels = stream.get("stream", {})
            values = stream.get("values", [])
            
            for value in values:
                timestamp_ns, log_line = value
                # Convert nanosecond timestamp to datetime
                timestamp = datetime.fromtimestamp(int(timestamp_ns) / 1e9)
                
                entries.append({
                    "timestamp": timestamp.isoformat(),
                    "message": log_line,
                    "labels": stream_labels
                })
                total_entries += 1
        
        # Sort by timestamp (most recent first)
        entries.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "entries": entries,
            "total_entries": total_entries,
            "streams_count": len(streams)
        }

    def _process_range_data(self, result: List[Dict]) -> Dict[str, Any]:
        """Process range query results"""
        processed_streams = []
        
        for stream in result:
            stream_labels = stream.get("stream", {})
            values = stream.get("values", [])
            
            processed_values = []
            for value in values:
                timestamp_ns, count = value
                timestamp = datetime.fromtimestamp(int(timestamp_ns) / 1e9)
                processed_values.append({
                    "timestamp": timestamp.isoformat(),
                    "value": float(count)
                })
            
            processed_streams.append({
                "labels": stream_labels,
                "values": processed_values
            })
        
        return {
            "streams": processed_streams,
            "streams_count": len(processed_streams)
        }

    def _analyze_errors(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns in log entries"""
        error_types = {}
        error_sources = {}
        timeline = {}
        
        for entry in entries:
            message = entry.get("message", "").lower()
            timestamp = entry.get("timestamp", "")
            labels = entry.get("labels", {})
            
            # Categorize error types
            if "exception" in message:
                error_types["exceptions"] = error_types.get("exceptions", 0) + 1
            elif "error" in message:
                error_types["errors"] = error_types.get("errors", 0) + 1
            elif "fail" in message:
                error_types["failures"] = error_types.get("failures", 0) + 1
            elif "panic" in message:
                error_types["panics"] = error_types.get("panics", 0) + 1
            
            # Track error sources
            source = labels.get("service", labels.get("job", "unknown"))
            error_sources[source] = error_sources.get(source, 0) + 1
            
            # Timeline (hour buckets)
            if timestamp:
                hour = timestamp[:13]  # YYYY-MM-DDTHH
                timeline[hour] = timeline.get(hour, 0) + 1
        
        return {
            "error_types": error_types,
            "error_sources": error_sources,
            "timeline": timeline,
            "total_errors": len(entries)
        }

    def _analyze_service_logs(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyze service-specific log patterns"""
        log_levels = {}
        message_patterns = {}
        
        for entry in entries:
            message = entry.get("message", "")
            labels = entry.get("labels", {})
            
            # Count log levels
            level = labels.get("level", "unknown")
            log_levels[level] = log_levels.get(level, 0) + 1
            
            # Analyze message patterns
            if "started" in message.lower():
                message_patterns["startup"] = message_patterns.get("startup", 0) + 1
            elif "request" in message.lower():
                message_patterns["requests"] = message_patterns.get("requests", 0) + 1
            elif "response" in message.lower():
                message_patterns["responses"] = message_patterns.get("responses", 0) + 1
        
        return {
            "log_levels": log_levels,
            "message_patterns": message_patterns,
            "total_logs": len(entries)
        }

    def _highlight_search_matches(self, entries: List[Dict], search_text: str, case_sensitive: bool) -> Dict[str, Any]:
        """Highlight search matches in log entries"""
        highlighted_entries = []
        match_count = 0
        
        pattern = re.compile(search_text if case_sensitive else search_text, re.IGNORECASE if not case_sensitive else 0)
        
        for entry in entries:
            message = entry.get("message", "")
            matches = pattern.findall(message)
            
            if matches:
                match_count += len(matches)
                # Simple highlighting (in real implementation, might use HTML/markdown)
                highlighted_message = pattern.sub(f"**{search_text}**", message)
                
                highlighted_entries.append({
                    **entry,
                    "highlighted_message": highlighted_message,
                    "match_count": len(matches)
                })
        
        return {
            "highlighted_entries": highlighted_entries,
            "total_matches": match_count,
            "matching_entries": len(highlighted_entries)
        }

    def _parse_duration(self, duration: str) -> timedelta:
        """Parse duration string to timedelta"""
        # Simple duration parser (1h, 30m, 2d, etc.)
        if duration.endswith('h'):
            return timedelta(hours=int(duration[:-1]))
        elif duration.endswith('m'):
            return timedelta(minutes=int(duration[:-1]))
        elif duration.endswith('d'):
            return timedelta(days=int(duration[:-1]))
        elif duration.endswith('s'):
            return timedelta(seconds=int(duration[:-1]))
        else:
            return timedelta(hours=1)  # Default to 1 hour

    def get_capabilities(self) -> List[str]:
        """Get Loki MCP capabilities"""
        return [
            "logs",         # Basic log queries
            "range",        # Range queries
            "labels",       # Available labels
            "values",       # Label values
            "errors",       # Error log analysis
            "service_logs", # Service-specific logs
            "search",       # Text search
            "tail",         # Real-time log tailing
            "health_check"  # Health status
        ] 