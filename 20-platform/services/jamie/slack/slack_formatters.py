#!/usr/bin/env python3
"""
🎨 Jamie AI DevOps Copilot - Slack Formatters
Sprint 5: Slack Integration

Format DevOps data into beautiful Slack blocks with Jamie's British personality.
Handles cluster status, error analysis, metrics, and more.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

def format_cluster_status(k8s_status: Dict[str, Any], prometheus_status: Dict[str, Any]) -> List[Dict]:
    """Format cluster status for Slack display"""
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🏗️ Cluster Status Overview"
            }
        }
    ]
    
    # Cluster health summary
    health_emoji = "✅" if k8s_status.get("healthy", False) else "❌"
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{health_emoji} *Cluster Health:* {'All systems go, mate!' if k8s_status.get('healthy') else 'Houston, we have a problem!'} 🇬🇧"
        }
    })
    
    # Key metrics in fields
    blocks.append({
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*🏗️ Nodes:*\n{k8s_status.get('nodes_ready', '?')}/{k8s_status.get('nodes_total', '?')} Ready"
            },
            {
                "type": "mrkdwn",
                "text": f"*🚀 Pods:*\n{k8s_status.get('pods_running', '?')} Running"
            },
            {
                "type": "mrkdwn",
                "text": f"*📊 Services:*\n{k8s_status.get('services_count', '?')} Active"
            },
            {
                "type": "mrkdwn",
                "text": f"*⚠️ Alerts:*\n{prometheus_status.get('firing_alerts', 0)} Firing"
            }
        ]
    })
    
    # Resource usage bar charts
    if k8s_status.get("resource_usage"):
        resources = k8s_status["resource_usage"]
        cpu_bar = create_usage_bar(resources.get("cpu_percent", 0))
        memory_bar = create_usage_bar(resources.get("memory_percent", 0))
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*💾 Resource Usage:*\n• CPU: {cpu_bar} {resources.get('cpu_percent', 0):.1f}%\n• Memory: {memory_bar} {resources.get('memory_percent', 0):.1f}%"
            }
        })
    
    # Recent events or issues
    if k8s_status.get("recent_events"):
        events_text = "\n".join([
            f"• {event.get('type', 'Info')}: {event.get('message', 'No details')}"
            for event in k8s_status["recent_events"][:3]
        ])
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📝 Recent Events:*\n{events_text}"
            }
        })
    
    # Action buttons
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Detailed View"},
                "action_id": "cluster_details",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔄 Refresh"},
                "action_id": "refresh_status"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 Metrics"},
                "action_id": "show_metrics"
            }
        ]
    })
    
    return blocks

def format_error_analysis(errors: List[Dict[str, Any]], time_range: str = "1h") -> List[Dict]:
    """Format error analysis for Slack display"""
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 Error Analysis - Last {time_range}"
            }
        }
    ]
    
    if not errors:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🎉 *Brilliant!* No errors found in the last hour. Your systems are running like a dream, mate! 🇬🇧"
            }
        })
        return blocks
    
    # Error summary
    total_errors = len(errors)
    unique_services = len(set(error.get("service", "unknown") for error in errors))
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Found *{total_errors} errors* across *{unique_services} services*. Let me break it down for you:"
        }
    })
    
    # Group errors by service
    service_errors = {}
    for error in errors:
        service = error.get("service", "unknown")
        if service not in service_errors:
            service_errors[service] = []
        service_errors[service].append(error)
    
    # Show top 3 services with errors
    top_services = sorted(service_errors.items(), key=lambda x: len(x[1]), reverse=True)[:3]
    
    for service, service_error_list in top_services:
        error_count = len(service_error_list)
        latest_error = service_error_list[0]
        
        severity_emoji = {
            "critical": "🔥",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }.get(latest_error.get("severity", "error"), "❌")
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{severity_emoji} *{service}* - {error_count} error{'s' if error_count > 1 else ''}\n```{latest_error.get('message', 'No error message')[:100]}...```"
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Details"},
                "action_id": f"error_details_{service}"
            }
        })
    
    # Error timeline
    if len(errors) > 0:
        timeline_text = create_error_timeline(errors)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📈 Error Timeline:*\n{timeline_text}"
            }
        })
    
    # Action buttons
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 Full Report"},
                "action_id": "full_error_report",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔧 Troubleshoot"},
                "action_id": "start_troubleshooting"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔔 Set Alert"},
                "action_id": "create_alert"
            }
        ]
    })
    
    return blocks

def format_metrics_summary(metrics: Dict[str, Any]) -> List[Dict]:
    """Format performance metrics for Slack display"""
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Performance Metrics"
            }
        }
    ]
    
    # Overall health score
    health_score = calculate_health_score(metrics)
    health_emoji = "🟢" if health_score > 80 else "🟡" if health_score > 60 else "🔴"
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{health_emoji} *Overall Health Score:* {health_score}%\n{'Looking brilliant, mate!' if health_score > 80 else 'Bit of attention needed!' if health_score > 60 else 'Houston, we have a problem!'} 🇬🇧"
        }
    })
    
    # Key metrics
    cpu_usage = metrics.get("cpu", {}).get("current", 0)
    memory_usage = metrics.get("memory", {}).get("current", 0)
    disk_usage = metrics.get("disk", {}).get("current", 0)
    
    blocks.append({
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*💻 CPU Usage:*\n{create_usage_bar(cpu_usage)} {cpu_usage:.1f}%"
            },
            {
                "type": "mrkdwn",
                "text": f"*💾 Memory Usage:*\n{create_usage_bar(memory_usage)} {memory_usage:.1f}%"
            },
            {
                "type": "mrkdwn",
                "text": f"*💽 Disk Usage:*\n{create_usage_bar(disk_usage)} {disk_usage:.1f}%"
            },
            {
                "type": "mrkdwn",
                "text": f"*🌐 Network I/O:*\n↗️ {format_bytes(metrics.get('network', {}).get('in', 0))}/s\n↘️ {format_bytes(metrics.get('network', {}).get('out', 0))}/s"
            }
        ]
    })
    
    # Response times if available
    if metrics.get("response_times"):
        rt = metrics["response_times"]
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*⚡ Response Times:*\n• Avg: {rt.get('avg', 0):.2f}ms\n• P95: {rt.get('p95', 0):.2f}ms\n• P99: {rt.get('p99', 0):.2f}ms"
            }
        })
    
    # Top resource consumers
    if metrics.get("top_consumers"):
        consumers_text = "\n".join([
            f"• {consumer['name']}: {consumer['usage']:.1f}%"
            for consumer in metrics["top_consumers"][:3]
        ])
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔥 Top Resource Consumers:*\n{consumers_text}"
            }
        })
    
    # Action buttons
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📈 Historical View"},
                "action_id": "metrics_history",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Deep Dive"},
                "action_id": "metrics_deep_dive"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 Custom Dashboard"},
                "action_id": "create_dashboard"
            }
        ]
    })
    
    return blocks

def format_alert_summary(alerts: List[Dict[str, Any]]) -> List[Dict]:
    """Format active alerts for Slack display"""
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔔 Active Alerts"
            }
        }
    ]
    
    if not alerts:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🎉 *All quiet on the western front!* No active alerts. Your systems are behaving themselves nicely. 🇬🇧"
            }
        })
        return blocks
    
    # Group alerts by severity
    critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
    warning_alerts = [a for a in alerts if a.get("severity") == "warning"]
    
    # Summary
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*{len(alerts)} active alerts:* {len(critical_alerts)} critical, {len(warning_alerts)} warnings"
        }
    })
    
    # Show critical alerts first
    for alert in critical_alerts[:3]:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🔥 *CRITICAL: {alert.get('name', 'Unknown Alert')}*\n{alert.get('description', 'No description')}"
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "🚨 Handle"},
                "action_id": f"handle_alert_{alert.get('id', 'unknown')}"
            }
        })
    
    return blocks

def create_usage_bar(percentage: float, width: int = 10) -> str:
    """Create a visual usage bar using emojis"""
    filled = int((percentage / 100) * width)
    empty = width - filled
    
    if percentage > 90:
        bar_char = "🔴"
    elif percentage > 75:
        bar_char = "🟡"
    else:
        bar_char = "🟢"
    
    return bar_char * filled + "⚪" * empty

def create_error_timeline(errors: List[Dict[str, Any]]) -> str:
    """Create a simple timeline of errors"""
    if not errors:
        return "No errors to display"
    
    # Group by hour
    hourly_counts = {}
    for error in errors:
        timestamp = error.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        hour = timestamp.replace(minute=0, second=0, microsecond=0)
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    # Create simple text timeline
    timeline_parts = []
    for hour, count in sorted(hourly_counts.items())[-6:]:  # Last 6 hours
        hour_str = hour.strftime("%H:%M")
        bar = "█" * min(count, 10)  # Max 10 chars
        timeline_parts.append(f"{hour_str}: {bar} ({count})")
    
    return "\n".join(timeline_parts)

def calculate_health_score(metrics: Dict[str, Any]) -> int:
    """Calculate overall health score from metrics"""
    scores = []
    
    # CPU score (lower is better)
    cpu = metrics.get("cpu", {}).get("current", 0)
    cpu_score = max(0, 100 - cpu) if cpu < 90 else 0
    scores.append(cpu_score)
    
    # Memory score
    memory = metrics.get("memory", {}).get("current", 0)
    memory_score = max(0, 100 - memory) if memory < 90 else 0
    scores.append(memory_score)
    
    # Error rate score
    error_rate = metrics.get("error_rate", 0)
    error_score = max(0, 100 - (error_rate * 10)) if error_rate < 10 else 0
    scores.append(error_score)
    
    # Response time score
    response_time = metrics.get("response_times", {}).get("avg", 0)
    response_score = max(0, 100 - (response_time / 10)) if response_time < 1000 else 0
    scores.append(response_score)
    
    return int(sum(scores) / len(scores)) if scores else 50

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"

def format_service_status(services: List[Dict[str, Any]]) -> List[Dict]:
    """Format service status overview for Slack"""
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚀 Service Status"
            }
        }
    ]
    
    if not services:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No services to display"
            }
        })
        return blocks
    
    # Group by status
    healthy = [s for s in services if s.get("status") == "healthy"]
    unhealthy = [s for s in services if s.get("status") != "healthy"]
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*{len(healthy)}/{len(services)} services healthy* 🇬🇧"
        }
    })
    
    # Show unhealthy services first
    for service in unhealthy[:5]:
        status_emoji = "❌" if service.get("status") == "down" else "⚠️"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{status_emoji} *{service.get('name', 'Unknown')}*\nStatus: {service.get('status', 'Unknown')}\nLast seen: {service.get('last_seen', 'Unknown')}"
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔧 Fix"},
                "action_id": f"troubleshoot_service_{service.get('name', 'unknown')}"
            }
        })
    
    return blocks 