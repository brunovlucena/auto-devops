#!/usr/bin/env python3
"""
🔧 Jamie AI DevOps Copilot - Slack Utilities
Sprint 5: Slack Integration

=== WHAT THIS FILE DOES ===
The Swiss Army knife of Slack integration! Contains all the smart utility functions:
- 🧠 Intent Extraction: "show me errors" → {"intent": "error_investigation"}
- 👤 User Preferences: Remember how each person likes their notifications
- 🇬🇧 British Personality: Generate Jamie's charming British expressions
- 🔄 Cross-Platform Sync: Connect Slack conversations with the web portal

=== KEY MAGIC ===
1. Intent Extraction: Turn natural language into structured data
2. Entity Recognition: Find service names, time ranges, severity levels
3. Context Building: Add who, what, when, where to every request
4. British Flavor: Keep Jamie's personality consistent everywhere

=== EXAMPLES ===
Input: "show me errors from auth-service in the last hour"
Output: {
  "intent": "error_investigation",
  "entities": {"service_names": ["auth-service"], "time_ranges": ["1h"]},
  "priority": "normal"
}
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# ===== IN-MEMORY STORAGE =====
# TODO: Replace with proper database in production
USER_PREFERENCES: Dict[str, Dict] = {}  # User settings and preferences
USER_SESSIONS: Dict[str, Dict] = {}     # Active conversation sessions

# ==========================================
# 👤 USER PREFERENCES MANAGEMENT
# ==========================================

async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    🎯 Get user preferences for Jamie interactions
    
    WHAT IT RETURNS:
    - Notification settings (how often, what channels)
    - Display preferences (blocks vs text, timezone)
    - Quick actions (their favorite shortcuts)
    - Custom filters (which services they care about)
    
    💡 ADHD TIP: Default preferences are sensible - users don't HAVE to configure anything
    """
    
    # ===== SENSIBLE DEFAULTS =====
    # Start with good defaults so Jamie works immediately
    default_prefs = {
        # ===== NOTIFICATION PREFERENCES =====
        "notification_level": "important",  # all, important, critical, none
        "preferred_format": "blocks",       # blocks (rich), text (simple), minimal
        "timezone": "UTC",                  # User's timezone for timestamps
        
        # ===== CHANNEL ROUTING =====
        # Where different types of messages should go
        "channels": {
            "alerts": None,        # Critical alerts channel
            "reports": None,       # Daily/weekly reports
            "personal": None       # Personal notifications (DMs)
        },
        
        # ===== AUTO-SUBSCRIBE SETTINGS =====
        # What should Jamie automatically notify about?
        "auto_subscribe": {
            "critical_alerts": True,      # Always notify for critical issues
            "daily_reports": False,       # Don't spam with daily reports by default
            "weekly_summaries": True      # Weekly summaries are useful
        },
        
        # ===== QUICK ACTIONS =====
        # Shortcuts that appear in Jamie's responses
        "quick_actions": [
            "cluster_status",           # "How's my cluster?"
            "recent_errors",           # "Show recent errors"
            "performance_metrics"      # "Performance overview"
        ],
        
        # ===== CUSTOM FILTERS =====
        # What the user cares about (personalization!)
        "custom_filters": {
            "services": [],                    # Specific services they monitor
            "namespaces": [],                  # Kubernetes namespaces
            "severity_levels": ["critical", "warning"]  # What severity to show
        }
    }
    
    # Return user's preferences or defaults
    return USER_PREFERENCES.get(user_id, default_prefs)

async def save_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """
    💾 Save user preferences
    
    🎯 PURPOSE: Remember user's settings between conversations
    
    TODO: Replace with actual database storage
    """
    try:
        USER_PREFERENCES[user_id] = preferences
        return True
    except Exception:
        return False

# ==========================================
# 🧠 DEVOPS INTENT EXTRACTION
# ==========================================

def extract_devops_intent(text: str) -> Dict[str, Any]:
    """
    🎯 Extract DevOps-related intent and entities from user message
    
    ✨ THIS IS THE MAGIC! Turn natural language into structured data
    
    EXAMPLES:
    "How's my cluster doing?" → {"intent": "cluster_status", "confidence": 0.8}
    "Show me errors from auth-service" → {"intent": "error_investigation", "entities": {"service_names": ["auth-service"]}}
    "Any slow requests?" → {"intent": "performance_monitoring", "entities": {"metrics": ["latency"]}}
    
    FLOW:
    1. Clean and normalize the text
    2. Match against intent patterns
    3. Extract entities (services, times, etc.)
    4. Determine priority and context
    5. Return structured data
    
    💡 ADHD TIP: This turns messy human language into clean computer data
    """
    
    text_lower = text.lower()
    
    # ===== INTENT PATTERN MATCHING =====
    # Define what different types of questions look like
    intent_patterns = {
        # ===== CLUSTER STATUS QUERIES =====
        "cluster_status": [
            r"cluster.*(?:status|health|doing)",      # "cluster status", "how's cluster doing"
            r"how.*(?:cluster|nodes|pods)",           # "how are my pods", "how's the cluster"
            r"(?:status|health).*cluster"             # "status of cluster", "health cluster"
        ],
        
        # ===== ERROR INVESTIGATION =====
        "error_investigation": [
            r"error.*(?:show|find|search)",           # "show me errors", "find errors"
            r"(?:show|find|search).*error",           # "search for errors"
            r"what.*(?:wrong|issue|problem)",         # "what's wrong", "what's the issue"
            r"(?:investigate|debug|troubleshoot)"     # "investigate this", "debug", "troubleshoot"
        ],
        
        # ===== PERFORMANCE MONITORING =====
        "performance_monitoring": [
            r"(?:cpu|memory|disk|performance).*usage", # "cpu usage", "memory usage"
            r"(?:slow|latency|response.*time)",         # "slow requests", "response time"
            r"performance.*(?:metrics|stats)"           # "performance metrics"
        ],
        
        # ===== ALERT MANAGEMENT =====
        "alert_management": [
            r"(?:alert|alerts).*(?:active|firing)",    # "active alerts", "alerts firing"
            r"(?:any|show).*alerts",                   # "any alerts", "show alerts"
            r"notification.*(?:setup|config)"          # "notification setup"
        ],
        
        # ===== LOG ANALYSIS =====
        "log_analysis": [
            r"log.*(?:show|search|find)",              # "show logs", "search logs"
            r"(?:search|find).*log",                   # "find in logs"
            r"tail.*log"                               # "tail logs"
        ],
        
        # ===== SERVICE STATUS =====
        "service_status": [
            r"service.*(?:status|health)",             # "service status", "service health"
            r"(?:status|health).*service",             # "status of service"
            r"(?:up|down|running).*service"            # "is service up", "service running"
        ]
    }
    
    # ===== ENTITY EXTRACTION PATTERNS =====
    # Find specific things mentioned in the text
    entity_patterns = {
        # Common service naming patterns
        "service_names": r"(?:auth|frontend|backend|api|web|db|database|redis|nginx|payment|user)-?(?:service)?",
        
        # Kubernetes namespaces
        "namespaces": r"(?:default|kube-system|monitoring|ingress|production|staging|dev)",
        
        # Time expressions
        "time_ranges": r"(?:last|past)\s+(\d+)\s+(minute|hour|day|week)s?",
        
        # Severity levels
        "severity_levels": r"(?:critical|warning|error|info|debug)",
        
        # Performance metrics
        "metrics": r"(?:cpu|memory|disk|network|bandwidth|latency|response.*time)"
    }
    
    # ===== DETECT INTENT =====
    # Find the best matching intent
    detected_intent = "general"  # Default fallback
    confidence = 0.0
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                detected_intent = intent
                confidence = 0.8  # High confidence for pattern match
                break
        if confidence > 0:
            break
    
    # ===== EXTRACT ENTITIES =====
    # Find specific things mentioned
    entities = {}
    
    for entity_type, pattern in entity_patterns.items():
        matches = re.findall(pattern, text_lower)
        if matches:
            entities[entity_type] = matches
    
    # ===== EXTRACT TIME RANGE =====
    # Convert "last 2 hours" → "2h"
    time_range = "1h"  # Sensible default
    time_match = re.search(entity_patterns["time_ranges"], text_lower)
    if time_match:
        amount, unit = time_match.groups()
        time_range = f"{amount}{unit[0]}"  # "2 hours" → "2h"
    
    # ===== DETERMINE PRIORITY =====
    # How urgent is this request?
    priority = "normal"
    
    # High priority keywords
    if any(word in text_lower for word in ["critical", "urgent", "emergency", "down", "outage"]):
        priority = "high"
    # Low priority keywords  
    elif any(word in text_lower for word in ["please", "when possible", "low priority"]):
        priority = "low"
    
    # ===== DETECT FOLLOW-UP QUESTIONS =====
    # Is this continuing a previous conversation?
    is_followup = any(word in text_lower for word in [
        "what about", "and also", "additionally", "furthermore",
        "also", "too", "as well", "more", "details"
    ])
    
    # ===== RETURN STRUCTURED DATA =====
    return {
        "intent": detected_intent,              # What they want
        "confidence": confidence,               # How sure are we
        "entities": entities,                   # Specific things mentioned
        "time_range": time_range,              # Time scope
        "priority": priority,                   # How urgent
        "is_followup": is_followup,            # Continuing conversation?
        "keywords": extract_keywords(text),    # Important words
        "platform_context": {                  # Where this came from
            "source": "slack",
            "message_type": "command" if text.startswith("/") else "natural"
        }
    }

def extract_keywords(text: str) -> List[str]:
    """
    📝 Extract relevant DevOps keywords from text
    
    🎯 PURPOSE: Find important technical terms to help with context
    
    CATEGORIES:
    - Infrastructure: kubernetes, cluster, pod, service
    - Monitoring: prometheus, alert, metric, cpu, memory
    - Logging: loki, log, error, warning
    - Performance: latency, response time, throughput
    - Operations: deploy, scale, restart, health
    - Troubleshooting: debug, investigate, fix, issue
    
    💡 ADHD TIP: Keywords help Jamie understand technical context
    """
    
    # ===== DEVOPS KEYWORD DICTIONARY =====
    # Comprehensive list of DevOps-related terms
    devops_keywords = {
        # ===== INFRASTRUCTURE =====
        "kubernetes", "k8s", "cluster", "node", "pod", "deployment", "service",
        "namespace", "ingress", "configmap", "secret", "volume",
        
        # ===== MONITORING =====
        "prometheus", "grafana", "alert", "metric", "dashboard", "query",
        "cpu", "memory", "disk", "network", "bandwidth", "latency",
        
        # ===== LOGGING =====
        "loki", "log", "error", "warning", "debug", "trace", "event",
        
        # ===== PERFORMANCE =====
        "performance", "response", "time", "throughput", "load", "stress",
        "benchmark", "optimization", "bottleneck",
        
        # ===== OPERATIONS =====
        "deploy", "deployment", "rollback", "scale", "restart", "update",
        "health", "status", "availability", "uptime", "downtime",
        
        # ===== SECURITY =====
        "security", "vulnerability", "compliance", "audit", "access",
        "permission", "rbac", "ssl", "certificate",
        
        # ===== TROUBLESHOOTING =====
        "debug", "troubleshoot", "investigate", "diagnose", "fix",
        "issue", "problem", "bug", "incident", "outage"
    }
    
    # ===== EXTRACT MATCHING KEYWORDS =====
    words = text.lower().split()
    found_keywords = []
    
    for word in words:
        # Remove punctuation and check if it's a DevOps term
        clean_word = re.sub(r'[^\w-]', '', word)
        if clean_word in devops_keywords:
            found_keywords.append(clean_word)
    
    return found_keywords

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

# ==========================================
# 🇬🇧 BRITISH PERSONALITY FUNCTIONS
# ==========================================

def get_british_greeting() -> str:
    """
    🎩 Get a time-appropriate British greeting
    
    EXAMPLES:
    - Morning: "Good morning, mate!"
    - Afternoon: "Afternoon!"
    - Evening: "Evening! How's tricks?"
    - Late night: "Blimey, still up?"
    
    💡 ADHD TIP: Time-aware greetings make interactions feel more natural
    """
    
    current_hour = datetime.now().hour
    
    # ===== TIME-BASED GREETINGS =====
    if 5 <= current_hour < 12:        # Morning
        greetings = [
            "Good morning, mate!",
            "Morning! What's the crack?",
            "Right then, morning!",
            "Alright mate, morning!"
        ]
    elif 12 <= current_hour < 17:     # Afternoon  
        greetings = [
            "Afternoon!",
            "Good afternoon, mate!",
            "Afternoon! How's it going?",
            "Right, afternoon!"
        ]
    elif 17 <= current_hour < 22:     # Evening
        greetings = [
            "Evening!",
            "Good evening! How's tricks?",
            "Evening, mate!",
            "Alright, evening!"
        ]
    else:                              # Late night
        greetings = [
            "Blimey, still up?",
            "Crikey, working late?",
            "Evening! Burning the midnight oil?",
            "Right then, night owl!"
        ]
    
    import random
    return random.choice(greetings)

def get_british_response_flavor() -> str:
    """
    🎭 Get British expressions for different situations
    
    USAGE: Add personality to Jamie's responses
    
    CATEGORIES:
    - Success: "Brilliant!", "Spot on!", "Bob's your uncle!"
    - Thinking: "Let me have a butcher's...", "Give me a tick..."
    - Problems: "Blimey!", "Bit of a pickle!", "Gone pear-shaped!"
    - Acknowledgment: "Right then!", "Fair enough!", "Too right!"
    
    💡 ADHD TIP: Consistent personality makes Jamie feel more human
    """
    
    import random
    
    # ===== BRITISH EXPRESSIONS BY CATEGORY =====
    expressions = {
        "success": [
            "Brilliant!", "Spot on!", "Bob's your uncle!", "Top notch!",
            "Smashing!", "Cracking!", "Champion!", "Bang on!"
        ],
        "thinking": [
            "Let me have a butcher's...", "Give me a tick...", "One moment...",
            "Right, let me check...", "Hold on a mo...", "Bear with me..."
        ],
        "problems": [
            "Blimey!", "Crikey!", "Bit of a pickle!", "Gone pear-shaped!",
            "That's not ideal...", "Bit of a wobble!", "Oh dear...", "Cor!"
        ],
        "acknowledgment": [
            "Right then!", "Fair enough!", "Too right!", "Absolutely!",
            "Indeed!", "Quite so!", "Certainly!", "Of course!"
        ]
    }
    
    # Return random expression from random category
    category = random.choice(list(expressions.keys()))
    return random.choice(expressions[category])

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