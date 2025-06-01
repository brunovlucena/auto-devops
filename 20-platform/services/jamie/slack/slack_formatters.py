#!/usr/bin/env python3
"""
🎨 Jamie AI DevOps Copilot - Slack Formatters
Sprint 5: Slack Integration

=== WHAT THIS FILE DOES ===
Transform boring DevOps data into beautiful Slack messages!
- Cluster status → Pretty health dashboard with bars and emojis
- Error logs → Organized service breakdown with timelines  
- Metrics → Visual usage bars and health scores
- Alerts → Color-coded severity with action buttons

=== KEY CONCEPTS ===
1. Slack Blocks: Like HTML but for Slack (sections, buttons, text)
2. Visual Elements: Usage bars, emojis, color coding
3. Interactive Components: Buttons for "Details", "Refresh", etc.
4. British Personality: Jamie's charm woven into every message

=== VISUAL EXAMPLES ===
Input: {"cpu_percent": 75}
Output: 🔥🔥🔥🔥🔥🔥🔥🔥⬜⬜ 75%

Input: {"status": "healthy"}  
Output: ✅ All systems go, mate! 🇬🇧
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# ==========================================
# 🏗️ CLUSTER STATUS FORMATTING
# ==========================================
def format_cluster_status(k8s_status: Dict[str, Any], prometheus_status: Dict[str, Any]) -> List[Dict]:
    """
    🎯 Format cluster status for Slack display
    
    INPUT: Raw data from Kubernetes and Prometheus
    OUTPUT: Beautiful Slack blocks with health indicators, usage bars, action buttons
    
    🖼️ VISUAL RESULT:
    ┌─────────────────────────────┐
    │ 🏗️ Cluster Status Overview │
    │ ✅ All systems go, mate!   │
    │ 🏗️ Nodes: 3/3 Ready       │
    │ 🚀 Pods: 47 Running        │
    │ 💾 CPU: ████████░░ 80%     │
    │ [🔍 Details] [🔄 Refresh]  │
    └─────────────────────────────┘
    
    💡 ADHD TIP: Each block is like a LEGO piece - header, content, actions
    """
    
    # ===== START WITH HEADER BLOCK =====
    # Every good Slack message starts with a clear title
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🏗️ Cluster Status Overview"
            }
        }
    ]
    
    # ===== HEALTH SUMMARY WITH PERSONALITY =====
    # Show overall health with Jamie's British charm
    health_emoji = "✅" if k8s_status.get("healthy", False) else "❌"
    health_message = "All systems go, mate!" if k8s_status.get("healthy") else "Houston, we have a problem!"
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{health_emoji} *Cluster Health:* {health_message} 🇬🇧"
        }
    })
    
    # ===== KEY METRICS IN GRID LAYOUT =====
    # Show important numbers in a 2x2 grid layout for easy scanning
    blocks.append({
        "type": "section",
        "fields": [  # Fields create a grid layout - perfect for metrics!
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
    
    # ===== VISUAL RESOURCE USAGE BARS =====
    # Turn percentages into visual bars (much easier to understand!)
    if k8s_status.get("resource_usage"):
        resources = k8s_status["resource_usage"]
        
        # CREATE VISUAL BARS: 80% → 🔥🔥🔥🔥🔥🔥🔥🔥⬜⬜
        cpu_bar = create_usage_bar(resources.get("cpu_percent", 0))
        memory_bar = create_usage_bar(resources.get("memory_percent", 0))
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*💾 Resource Usage:*\n• CPU: {cpu_bar} {resources.get('cpu_percent', 0):.1f}%\n• Memory: {memory_bar} {resources.get('memory_percent', 0):.1f}%"
            }
        })
    
    # ===== RECENT EVENTS (IF ANY) =====
    # Show what's been happening lately (max 3 events to avoid clutter)
    if k8s_status.get("recent_events"):
        events_text = "\n".join([
            f"• {event.get('type', 'Info')}: {event.get('message', 'No details')}"
            for event in k8s_status["recent_events"][:3]  # Only show top 3
        ])
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📝 Recent Events:*\n{events_text}"
            }
        })
    
    # ===== ACTION BUTTONS =====
    # Give users quick actions they can take
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Detailed View"},
                "action_id": "cluster_details",     # Slack will send this ID when clicked
                "style": "primary"                   # Blue button (most important action)
            },
            {
                "type": "button", 
                "text": {"type": "plain_text", "text": "🔄 Refresh"},
                "action_id": "refresh_status"       # Update the data
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 Metrics"},
                "action_id": "show_metrics"         # Deep dive into metrics
            }
        ]
    })
    
    return blocks

# ==========================================
# 🚨 ERROR ANALYSIS FORMATTING  
# ==========================================
def format_error_analysis(errors: List[Dict[str, Any]], time_range: str = "1h") -> List[Dict]:
    """
    🎯 Format error analysis for Slack display
    
    INPUT: List of errors from logs/monitoring
    OUTPUT: Organized breakdown by service with severity indicators
    
    🖼️ VISUAL RESULT:
    ┌─────────────────────────────┐
    │ 🚨 Error Analysis - Last 1h│
    │ Found 15 errors across 3   │
    │ services. Let me break it   │
    │ down for you:              │
    │                           │
    │ ❌ auth-service - 8 errors │
    │ ```Connection timeout...``` │
    │ [🔍 Details]              │
    │                           │
    │ 📈 Error Timeline:         │
    │ ████▅▅▃▃▁▁ (last 10 min)  │
    └─────────────────────────────┘
    
    💡 ADHD TIP: Group similar errors to reduce overwhelm
    """
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 Error Analysis - Last {time_range}"
            }
        }
    ]
    
    # ===== HANDLE NO ERRORS (CELEBRATE!) =====
    if not errors:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🎉 *Brilliant!* No errors found in the last hour. Your systems are running like a dream, mate! 🇬🇧"
            }
        })
        return blocks
    
    # ===== ERROR SUMMARY STATS =====
    # Give overview before diving into details
    total_errors = len(errors)
    unique_services = len(set(error.get("service", "unknown") for error in errors))
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Found *{total_errors} errors* across *{unique_services} services*. Let me break it down for you:"
        }
    })
    
    # ===== GROUP ERRORS BY SERVICE =====
    # Organize chaos into manageable chunks
    service_errors = {}
    for error in errors:
        service = error.get("service", "unknown")
        if service not in service_errors:
            service_errors[service] = []
        service_errors[service].append(error)
    
    # ===== SHOW TOP 3 PROBLEMATIC SERVICES =====
    # Don't overwhelm with every service - focus on worst ones
    top_services = sorted(service_errors.items(), key=lambda x: len(x[1]), reverse=True)[:3]
    
    for service, service_error_list in top_services:
        error_count = len(service_error_list)
        latest_error = service_error_list[0]  # Most recent error
        
        # ===== SEVERITY COLOR CODING =====
        # Visual indicators for error severity
        severity_emoji = {
            "critical": "🔥",   # Fire for critical
            "error": "❌",      # X for errors
            "warning": "⚠️",    # Warning triangle
            "info": "ℹ️"        # Info symbol
        }.get(latest_error.get("severity", "error"), "❌")
        
        # ===== SERVICE ERROR BLOCK =====
        # Show service name, count, sample error, and action button
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{severity_emoji} *{service}* - {error_count} error{'s' if error_count > 1 else ''}\n```{latest_error.get('message', 'No error message')[:100]}...```"  # Truncate long messages
            },
            "accessory": {  # Side button for details
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Details"},
                "action_id": f"error_details_{service}"
            }
        })
    
    # ===== ERROR TIMELINE VISUALIZATION =====
    # Show when errors happened (visual pattern recognition)
    if len(errors) > 0:
        timeline_text = create_error_timeline(errors)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📈 Error Timeline:*\n{timeline_text}"
            }
        })
    
    # ===== ACTION BUTTONS =====
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
                "text": {"type": "plain_text", "text": "🚑 Start Investigation"},
                "action_id": "start_investigation",
                "style": "danger"  # Red button for urgent action
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📋 Create Incident"},
                "action_id": "create_incident"
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

# ==========================================
# 📊 VISUAL HELPER FUNCTIONS
# ==========================================
def create_usage_bar(percentage: float, width: int = 10) -> str:
    """
    🎯 Create visual usage bar from percentage
    
    EXAMPLES:
    75% → 🔥🔥🔥🔥🔥🔥🔥🔥⬜⬜
    50% → 🔥🔥🔥🔥🔥⬜⬜⬜⬜⬜
    90% → 🔥🔥🔥🔥🔥🔥🔥🔥🔥⬜
    
    💡 ADHD TIP: Visual bars are easier to understand than raw numbers
    """
    filled = int((percentage / 100) * width)  # How many filled squares
    empty = width - filled                     # How many empty squares
    
    # Choose emoji based on usage level
    if percentage >= 90:
        fill_emoji = "🔥"  # Fire for high usage
    elif percentage >= 70:
        fill_emoji = "🟨"  # Yellow for medium-high
    elif percentage >= 50:
        fill_emoji = "🟩"  # Green for normal
    else:
        fill_emoji = "🟦"  # Blue for low
    
    return fill_emoji * filled + "⬜" * empty

def create_error_timeline(errors: List[Dict[str, Any]]) -> str:
    """
    🎯 Create visual timeline of errors
    
    INPUT: List of errors with timestamps
    OUTPUT: Visual bar chart showing error frequency over time
    
    EXAMPLE:
    ████▅▅▃▃▁▁ (errors in last 10 minutes)
    ───────────────────────────────────────
    10m ago                           now
    
    💡 ADHD TIP: Patterns are easier to spot visually than in raw timestamps
    """
    if not errors:
        return "No errors in timeline"
    
    # ===== GROUP ERRORS BY TIME BUCKETS =====
    # Divide time into 10 buckets and count errors in each
    now = datetime.now()
    buckets = [0] * 10  # 10 time periods
    
    for error in errors:
        # Calculate how long ago this error occurred
        if error.get("timestamp"):
            error_time = datetime.fromisoformat(error["timestamp"])
            minutes_ago = (now - error_time).total_seconds() / 60
            
            # Put error in appropriate time bucket
            if minutes_ago <= 60:  # Only last hour
                bucket_index = min(int(minutes_ago / 6), 9)  # 6-minute buckets
                buckets[9 - bucket_index] += 1  # Reverse order (oldest to newest)
    
    # ===== CREATE VISUAL BARS =====
    # Convert counts to visual height
    max_errors = max(buckets) if max(buckets) > 0 else 1
    bar_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    
    timeline = ""
    for count in buckets:
        if count == 0:
            timeline += "▁"  # Minimum bar
        else:
            # Scale to bar height
            bar_index = min(int((count / max_errors) * 7), 7)
            timeline += bar_chars[bar_index]
    
    return f"{timeline} (last 60 minutes)"

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