#!/usr/bin/env python3
"""
🔧 Jamie AI DevOps Copilot - Slack Utilities
Sprint 5: Slack Integration

Helper functions for Slack integration including user preferences,
DevOps intent extraction, and cross-platform synchronization.
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# In-memory storage for demo (replace with proper database)
USER_PREFERENCES: Dict[str, Dict] = {}
USER_SESSIONS: Dict[str, Dict] = {}

async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Get user preferences for Jamie interactions"""
    
    default_prefs = {
        "notification_level": "important",  # all, important, critical, none
        "preferred_format": "blocks",       # blocks, text, minimal
        "timezone": "UTC",
        "channels": {
            "alerts": None,
            "reports": None,
            "personal": None
        },
        "auto_subscribe": {
            "critical_alerts": True,
            "daily_reports": False,
            "weekly_summaries": True
        },
        "quick_actions": [
            "cluster_status",
            "recent_errors", 
            "performance_metrics"
        ],
        "custom_filters": {
            "services": [],
            "namespaces": [],
            "severity_levels": ["critical", "warning"]
        }
    }
    
    return USER_PREFERENCES.get(user_id, default_prefs)

async def save_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """Save user preferences"""
    try:
        USER_PREFERENCES[user_id] = preferences
        return True
    except Exception:
        return False

def extract_devops_intent(text: str) -> Dict[str, Any]:
    """
    Extract DevOps-related intent and entities from user message
    
    Returns:
        Dict containing intent, entities, priority, and context
    """
    
    text_lower = text.lower()
    
    # Intent patterns
    intent_patterns = {
        "cluster_status": [
            r"cluster.*(?:status|health|doing)",
            r"how.*(?:cluster|nodes|pods)",
            r"(?:status|health).*cluster"
        ],
        "error_investigation": [
            r"error.*(?:show|find|search)",
            r"(?:show|find|search).*error",
            r"what.*(?:wrong|issue|problem)",
            r"(?:investigate|debug|troubleshoot)"
        ],
        "performance_monitoring": [
            r"(?:cpu|memory|disk|performance).*usage",
            r"(?:slow|latency|response.*time)",
            r"performance.*(?:metrics|stats)"
        ],
        "alert_management": [
            r"(?:alert|alerts).*(?:active|firing)",
            r"(?:any|show).*alerts",
            r"notification.*(?:setup|config)"
        ],
        "log_analysis": [
            r"log.*(?:show|search|find)",
            r"(?:search|find).*log",
            r"tail.*log"
        ],
        "service_status": [
            r"service.*(?:status|health)",
            r"(?:status|health).*service",
            r"(?:up|down|running).*service"
        ]
    }
    
    # Entity extraction patterns
    entity_patterns = {
        "service_names": r"(?:auth|frontend|backend|api|web|db|database|redis|nginx|payment|user)-?(?:service)?",
        "namespaces": r"(?:default|kube-system|monitoring|ingress|production|staging|dev)",
        "time_ranges": r"(?:last|past)\s+(\d+)\s+(minute|hour|day|week)s?",
        "severity_levels": r"(?:critical|warning|error|info|debug)",
        "metrics": r"(?:cpu|memory|disk|network|bandwidth|latency|response.*time)"
    }
    
    # Detect intent
    detected_intent = "general"
    confidence = 0.0
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                detected_intent = intent
                confidence = 0.8
                break
        if confidence > 0:
            break
    
    # Extract entities
    entities = {}
    
    for entity_type, pattern in entity_patterns.items():
        matches = re.findall(pattern, text_lower)
        if matches:
            entities[entity_type] = matches
    
    # Extract time range
    time_range = "1h"  # default
    time_match = re.search(entity_patterns["time_ranges"], text_lower)
    if time_match:
        amount, unit = time_match.groups()
        time_range = f"{amount}{unit[0]}"  # e.g., "2h", "30m"
    
    # Determine priority based on keywords
    priority = "normal"
    if any(word in text_lower for word in ["critical", "urgent", "emergency", "down", "outage"]):
        priority = "high"
    elif any(word in text_lower for word in ["please", "when possible", "low priority"]):
        priority = "low"
    
    # Detect if this is a follow-up question
    is_followup = any(word in text_lower for word in [
        "what about", "and also", "additionally", "furthermore",
        "also", "too", "as well", "more", "details"
    ])
    
    return {
        "intent": detected_intent,
        "confidence": confidence,
        "entities": entities,
        "time_range": time_range,
        "priority": priority,
        "is_followup": is_followup,
        "keywords": extract_keywords(text),
        "platform_context": {
            "source": "slack",
            "message_type": "command" if text.startswith("/") else "natural"
        }
    }

def extract_keywords(text: str) -> List[str]:
    """Extract relevant DevOps keywords from text"""
    
    devops_keywords = {
        # Infrastructure
        "kubernetes", "k8s", "cluster", "node", "pod", "deployment", "service",
        "namespace", "ingress", "configmap", "secret", "volume",
        
        # Monitoring
        "prometheus", "grafana", "alert", "metric", "dashboard", "query",
        "cpu", "memory", "disk", "network", "bandwidth", "latency",
        
        # Logging
        "loki", "log", "error", "warning", "debug", "trace", "event",
        
        # Performance
        "performance", "response", "time", "throughput", "load", "stress",
        "benchmark", "optimization", "bottleneck",
        
        # Operations
        "deploy", "deployment", "rollback", "scale", "restart", "update",
        "health", "status", "availability", "uptime", "downtime",
        
        # Security
        "security", "vulnerability", "compliance", "audit", "access",
        "permission", "rbac", "ssl", "certificate",
        
        # Troubleshooting
        "debug", "troubleshoot", "investigate", "diagnose", "fix",
        "issue", "problem", "bug", "incident", "outage"
    }
    
    words = text.lower().split()
    found_keywords = []
    
    for word in words:
        # Remove punctuation
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word in devops_keywords:
            found_keywords.append(clean_word)
    
    return list(set(found_keywords))

def create_session_id(user_id: str, channel_id: str, platform: str = "slack") -> str:
    """Create a unique session ID for cross-platform tracking"""
    
    session_data = f"{platform}_{user_id}_{channel_id}_{datetime.now().date()}"
    return hashlib.md5(session_data.encode()).hexdigest()[:16]

async def sync_with_portal(user_id: str, message: str, response: str, context: Dict) -> bool:
    """
    Sync Slack conversation with the portal for cross-platform continuity
    
    This allows users to continue conversations started in Slack within the portal
    """
    try:
        session_id = context.get("session_id", create_session_id(user_id, context.get("channel_id", "unknown")))
        
        # Store conversation data (in real implementation, sync with portal database)
        conversation_data = {
            "user_id": user_id,
            "session_id": session_id,
            "platform": "slack",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "context": context,
            "sync_status": "pending"
        }
        
        # In real implementation, send to portal via API or message queue
        USER_SESSIONS[session_id] = conversation_data
        
        return True
        
    except Exception as e:
        print(f"Failed to sync with portal: {e}")
        return False

def format_user_mention(user_id: str) -> str:
    """Format user mention for Slack"""
    return f"<@{user_id}>"

def format_channel_mention(channel_id: str) -> str:
    """Format channel mention for Slack"""
    return f"<#{channel_id}>"

def extract_slack_ids(text: str) -> Dict[str, List[str]]:
    """Extract user and channel IDs from Slack message"""
    
    user_ids = re.findall(r'<@([A-Z0-9]+)>', text)
    channel_ids = re.findall(r'<#([A-Z0-9]+)>', text)
    
    return {
        "users": user_ids,
        "channels": channel_ids
    }

def sanitize_for_slack(text: str) -> str:
    """Sanitize text for safe display in Slack"""
    
    # Escape special Slack characters
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def create_deep_link(action: str, params: Dict[str, str] = None) -> str:
    """Create a deep link to the Jamie portal"""
    
    base_url = "https://jamie.company.com"  # Replace with actual portal URL
    
    if params:
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?action={action}&{param_string}"
    else:
        return f"{base_url}?action={action}"

def should_notify_channel(message_type: str, severity: str, user_prefs: Dict) -> bool:
    """Determine if a message should trigger channel notifications"""
    
    notification_level = user_prefs.get("notification_level", "important")
    
    # Notification level hierarchy
    levels = {
        "none": [],
        "critical": ["critical"],
        "important": ["critical", "warning"],
        "all": ["critical", "warning", "info", "debug"]
    }
    
    return severity in levels.get(notification_level, ["critical"])

def build_notification_context(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Build context for notifications"""
    
    return {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "severity": data.get("severity", "info"),
        "source": data.get("source", "jamie"),
        "summary": data.get("summary", ""),
        "details": data.get("details", {}),
        "suggested_actions": data.get("actions", []),
        "related_links": {
            "portal": create_deep_link("event_details", {"id": data.get("id", "")}),
            "runbook": data.get("runbook_url", ""),
            "dashboard": data.get("dashboard_url", "")
        }
    }

def get_british_greeting() -> str:
    """Get a time-appropriate British greeting"""
    
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        greetings = [
            "Good morning",
            "Morning",
            "Rise and shine",
            "Top of the morning"
        ]
    elif 12 <= hour < 17:
        greetings = [
            "Good afternoon", 
            "Afternoon",
            "Hope you're having a lovely afternoon"
        ]
    elif 17 <= hour < 22:
        greetings = [
            "Good evening",
            "Evening",
            "Hope you're having a pleasant evening"
        ]
    else:
        greetings = [
            "Working late, are we?",
            "Burning the midnight oil?",
            "Good evening (though quite late!)"
        ]
    
    import random
    return random.choice(greetings)

def get_british_response_flavor() -> str:
    """Get a random British expression for responses"""
    
    expressions = [
        "Right then!",
        "Brilliant!",
        "Smashing!",
        "Lovely!",
        "Top notch!",
        "Spot on!",
        "Bob's your uncle!",
        "Sorted!",
        "Ace!",
        "Blimey!",
        "Crikey!",
        "Good show!",
        "Quite right!",
        "Indeed!",
        "Absolutely!",
        "Certainly!",
        "Rather!",
        "Precisely!",
        "Exactly so!",
        "Couldn't agree more!"
    ]
    
    import random
    return random.choice(expressions)

def format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as 'time ago' string with British flair"""
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.seconds < 60:
        return "just now"
    elif diff.seconds < 3600:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff.days == 0:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "yesterday"
    elif diff.days < 7:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"

def validate_slack_webhook_url(url: str) -> bool:
    """Validate Slack webhook URL format"""
    
    pattern = r'^https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+$'
    return bool(re.match(pattern, url))

def parse_slack_timestamp(ts: str) -> datetime:
    """Parse Slack timestamp to datetime object"""
    
    try:
        # Slack timestamps are in format "1234567890.123456"
        timestamp_float = float(ts)
        return datetime.fromtimestamp(timestamp_float)
    except (ValueError, TypeError):
        return datetime.now()

# Quick action configurations
QUICK_ACTIONS = {
    "health_check": {
        "label": "🏥 Health Check",
        "description": "Quick overview of system health",
        "command": "/jamie cluster status",
        "style": "primary"
    },
    "recent_errors": {
        "label": "🚨 Recent Errors", 
        "description": "Show errors from the last hour",
        "command": "/jamie show me recent errors",
        "style": "danger"
    },
    "performance": {
        "label": "📊 Performance",
        "description": "CPU, memory, and response time metrics",
        "command": "/jamie performance metrics",
        "style": "default"
    },
    "alerts": {
        "label": "🔔 Active Alerts",
        "description": "Show all firing alerts",
        "command": "/jamie active alerts",
        "style": "danger"
    },
    "deployments": {
        "label": "🚀 Deployments",
        "description": "Recent deployment status",
        "command": "/jamie deployment status",
        "style": "default"
    }
}

def get_quick_action_buttons() -> List[Dict[str, Any]]:
    """Get standard quick action buttons for Slack messages"""
    
    buttons = []
    for action_id, config in QUICK_ACTIONS.items():
        buttons.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": config["label"]
            },
            "action_id": f"quick_action_{action_id}",
            "style": config.get("style", "default")
        })
    
    return buttons 