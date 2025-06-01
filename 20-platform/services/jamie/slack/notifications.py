#!/usr/bin/env python3
"""
🔔 Jamie AI DevOps Copilot - Slack Notifications
Sprint 5: Slack Integration

=== WHAT THIS FILE DOES ===
Jamie's smart notification system - the nervous system of your DevOps team!
- 🚨 Alert Notifications: Critical system issues sent to right channels
- 🏥 Incident Management: Coordinate war rooms and status updates
- 🚀 Deployment Notifications: Success/failure updates with details
- 📊 Scheduled Reports: Daily/weekly summaries of system health
- 🔮 Proactive Insights: "Your CPU is trending up, heads up!"

=== KEY CONCEPTS ===
1. Severity Routing: Critical → #alerts, Info → #general
2. Rate Limiting: Don't spam channels with duplicate notifications
3. Threading: Keep incident updates in threads (organization!)
4. User Preferences: Respect each person's notification settings
5. British Personality: Even alerts are charming! 🇬🇧

=== NOTIFICATION FLOW ===
Event Occurs → Check Severity → Check Rate Limits → Route to Channels → Format Message → Send!

=== EXAMPLES ===
- Alert: "🚨 CPU > 90% on node-1" → Formats → Sends to #alerts + #devops
- Incident: "🏥 Database down" → Creates war room → Threads updates
- Deploy: "✅ frontend-v2.1.0 deployed" → Celebrates success!
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from .slack_formatters import (
    format_cluster_status, format_error_analysis, 
    format_metrics_summary, format_alert_summary
)
from .slack_utils import (
    get_user_preferences, should_notify_channel,
    build_notification_context, get_british_response_flavor,
    format_time_ago
)

logger = logging.getLogger(__name__)

# ==========================================
# 📊 NOTIFICATION ENUMS & TYPES
# ==========================================

class NotificationSeverity(Enum):
    """
    🎯 Notification severity levels - determines routing and urgency
    
    CRITICAL: System down, data loss, security breach
    WARNING: Performance degraded, approaching limits  
    INFO: Deployments, maintenance, general updates
    DEBUG: Development info, detailed troubleshooting
    
    💡 ADHD TIP: Clear severity helps brain filter what needs attention NOW
    """
    CRITICAL = "critical"
    WARNING = "warning"  
    INFO = "info"
    DEBUG = "debug"

class NotificationType(Enum):
    """
    🎭 Types of notifications Jamie can send
    
    Each type has different formatting, routing, and behavior:
    - ALERT: Real-time system issues
    - INCIDENT: Coordinated response to outages
    - DEPLOYMENT: Code release updates
    - HEALTH_CHECK: Scheduled system health reports
    - PERFORMANCE: Metrics and optimization insights
    - SECURITY: Vulnerability and compliance alerts
    - MAINTENANCE: Planned work announcements
    - SUMMARY: Daily/weekly rollup reports
    """
    ALERT = "alert"
    INCIDENT = "incident"
    DEPLOYMENT = "deployment"
    HEALTH_CHECK = "health_check"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    SUMMARY = "summary"

# ==========================================
# 🤖 MAIN NOTIFICATION MANAGER
# ==========================================

class JamieNotificationManager:
    """
    🎯 Manages all Slack notifications for Jamie AI DevOps Copilot
    
    ✨ SMART FEATURES:
    - Real-time alerts and incident notifications
    - Scheduled reports and summaries  
    - User preference-based filtering
    - Channel-specific routing
    - Rate limiting and de-duplication
    - Threading for related messages
    - British personality in all notifications
    
    🧠 HOW IT WORKS:
    1. Receives notification request (alert, incident, etc.)
    2. Checks severity and user preferences
    3. Applies rate limiting (don't spam!)
    4. Routes to appropriate channels
    5. Formats message with Jamie's personality
    6. Sends and tracks for threading/updates
    
    💡 ADHD TIP: Think of this as Jamie's mouth - it knows when to speak and how loud!
    """
    
    def __init__(self, slack_client: AsyncWebClient):
        """
        🚀 Initialize notification manager
        
        WHAT WE TRACK:
        - notification_queue: Messages waiting to be sent
        - sent_notifications: Recent messages (for de-duplication)
        - rate_limits: Per-channel send limits (prevent spam)
        """
        self.client = slack_client
        self.notification_queue: List[Dict] = []                    # Pending notifications
        self.sent_notifications: Dict[str, datetime] = {}           # De-duplication tracking
        self.rate_limits: Dict[str, List[datetime]] = {}            # Per-channel rate limiting
        
    async def send_alert_notification(
        self, 
        alert_data: Dict[str, Any], 
        channels: List[str],
        severity: NotificationSeverity = NotificationSeverity.WARNING
    ) -> bool:
        """
        🚨 Send alert notification to specified channels
        
        🎯 PURPOSE: Notify team of system issues in real-time
        
        FLOW:
        1. Build context (who, what, when, where)
        2. Create beautiful alert blocks  
        3. Check rate limits for each channel
        4. Send to appropriate channels
        5. Track sent messages
        
        EXAMPLES:
        - CPU alert → Formats with usage bars → Sends to #alerts
        - Disk full → Shows usage + actions → Routes by severity
        - Service down → Creates incident-style alert
        
        💡 ADHD TIP: Alerts are urgent - they interrupt current focus appropriately
        """
        
        try:
            # ===== BUILD NOTIFICATION CONTEXT =====
            # Add metadata about this alert
            context = build_notification_context("alert", alert_data)
            
            # ===== CREATE BEAUTIFUL ALERT BLOCKS =====
            # Turn raw alert data into visual Slack message
            blocks = await self._build_alert_blocks(alert_data, context)
            
            # ===== SEND TO EACH CHANNEL =====
            # Route alert to appropriate team channels
            success_count = 0
            for channel in channels:
                if await self._can_send_to_channel(channel, severity):
                    try:
                        await self.client.chat_postMessage(
                            channel=channel,
                            text=f"🚨 Alert: {alert_data.get('name', 'Unknown Alert')}",  # Fallback text
                            blocks=blocks,                     # Rich formatting
                            username="Jamie AI",              # Bot display name
                            icon_emoji=":robot_face:"         # Jamie's avatar
                        )
                        success_count += 1
                        
                        # ===== UPDATE RATE LIMITING =====
                        # Track this send to prevent spam
                        await self._update_rate_limit(channel)
                        
                    except SlackApiError as e:
                        logger.error(f"Failed to send alert to {channel}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
            return False
    
    async def send_incident_notification(
        self,
        incident_data: Dict[str, Any],
        channels: List[str],
        update_type: str = "new"  # new, update, resolved
    ) -> bool:
        """
        🏥 Send incident notification with proper escalation
        
        🎯 PURPOSE: Coordinate team response to major outages/issues
        
        INCIDENT LIFECYCLE:
        1. NEW: "🚨 Database is down! War room: #incident-db-001"
        2. UPDATE: "🔄 Still working on database. ETA: 15 minutes"  
        3. RESOLVED: "✅ Database restored! Post-mortem tomorrow."
        
        SPECIAL FEATURES:
        - Creates war room channels for coordination
        - Uses message threading for updates
        - Escalates to critical severity
        - Links to runbooks and documentation
        
        💡 ADHD TIP: Incidents need clear status - is this new, ongoing, or fixed?
        """
        
        try:
            severity = NotificationSeverity.CRITICAL  # Incidents are always critical
            
            # ===== CREATE INCIDENT BLOCKS =====
            # Format incident with status, actions, links
            blocks = await self._build_incident_blocks(incident_data, update_type)
            
            # ===== ADD WAR ROOM LINK =====
            # Show where team is coordinating response
            if incident_data.get("war_room_channel"):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🏥 *War Room:* <#{incident_data['war_room_channel']}>"
                    }
                })
            
            # ===== SEND NOTIFICATIONS =====
            success_count = 0
            for channel in channels:
                if await self._can_send_to_channel(channel, severity):
                    try:
                        # ===== THREAD UPDATES TO ORIGINAL MESSAGE =====
                        # Keep incident updates organized in threads
                        thread_ts = None
                        if update_type != "new" and incident_data.get("original_message_ts"):
                            thread_ts = incident_data["original_message_ts"]
                        
                        response = await self.client.chat_postMessage(
                            channel=channel,
                            text=f"🚨 Incident {update_type.title()}: {incident_data.get('title', 'Unknown Incident')}",
                            blocks=blocks,
                            thread_ts=thread_ts,              # Thread follow-ups
                            username="Jamie AI",
                            icon_emoji=":rotating_light:"     # Emergency light for incidents
                        )
                        
                        # ===== STORE MESSAGE FOR THREADING =====
                        # Remember this message for future updates
                        if update_type == "new":
                            incident_data["original_message_ts"] = response["ts"]
                        
                        success_count += 1
                        
                    except SlackApiError as e:
                        logger.error(f"Failed to send incident notification to {channel}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending incident notification: {e}")
            return False
    
    async def send_deployment_notification(
        self,
        deployment_data: Dict[str, Any],
        channels: List[str]
    ) -> bool:
        """
        🚀 Send deployment status notification
        
        🎯 PURPOSE: Keep team informed about code releases
        
        DEPLOYMENT STATUS TYPES:
        - SUCCESS: "✅ frontend-v2.1.0 deployed successfully!"
        - FAILED: "❌ backend-v1.2.3 deployment failed (rollback initiated)"
        - IN_PROGRESS: "🔄 Deploying user-service-v3.0.0..."
        - ROLLED_BACK: "⏪ Rolled back to api-v2.1.1 (previous stable)"
        
        INCLUDES:
        - Service name and version
        - Git commit hash and author
        - Deployment duration
        - Health check results
        - Quick action buttons
        
        💡 ADHD TIP: Deployment notifications help track "what changed when"
        """
        
        try:
            # ===== CREATE DEPLOYMENT BLOCKS =====
            # Format deployment info with status, timing, actions
            blocks = await self._build_deployment_blocks(deployment_data)
            
            # ===== STATUS EMOJI MAPPING =====
            # Visual indicators for different outcomes
            status = deployment_data.get("status", "unknown")
            emoji = {
                "success": "✅",        # Green check for success
                "failed": "❌",         # Red X for failures
                "in_progress": "🔄",    # Spinning arrow for ongoing
                "rolled_back": "⏪"     # Rewind for rollbacks
            }.get(status, "📦")        # Package for unknown
            
            # ===== SEND TO CHANNELS =====
            success_count = 0
            for channel in channels:
                try:
                    await self.client.chat_postMessage(
                        channel=channel,
                        text=f"{emoji} Deployment {status}: {deployment_data.get('service', 'Unknown Service')}",
                        blocks=blocks,
                        username="Jamie AI",
                        icon_emoji=":rocket:"          # Rocket for deployments
                    )
                    success_count += 1
                    
                except SlackApiError as e:
                    logger.error(f"Failed to send deployment notification to {channel}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending deployment notification: {e}")
            return False
    
    async def send_scheduled_summary(
        self,
        summary_type: str,  # daily, weekly, monthly
        channels: List[str],
        data: Dict[str, Any]
    ) -> bool:
        """Send scheduled summary reports"""
        
        try:
            blocks = await self._build_summary_blocks(summary_type, data)
            
            emoji = {
                "daily": "📅",
                "weekly": "📊", 
                "monthly": "📈"
            }.get(summary_type, "📋")
            
            success_count = 0
            for channel in channels:
                try:
                    await self.client.chat_postMessage(
                        channel=channel,
                        text=f"{emoji} {summary_type.title()} DevOps Summary",
                        blocks=blocks,
                        username="Jamie AI",
                        icon_emoji=":bar_chart:"
                    )
                    success_count += 1
                    
                except SlackApiError as e:
                    logger.error(f"Failed to send summary to {channel}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending scheduled summary: {e}")
            return False
    
    async def send_proactive_insight(
        self,
        insight_data: Dict[str, Any],
        channels: List[str]
    ) -> bool:
        """Send proactive insights and recommendations"""
        
        try:
            blocks = await self._build_insight_blocks(insight_data)
            
            success_count = 0
            for channel in channels:
                try:
                    await self.client.chat_postMessage(
                        channel=channel,
                        text=f"💡 Jamie's Insight: {insight_data.get('title', 'Performance Recommendation')}",
                        blocks=blocks,
                        username="Jamie AI",
                        icon_emoji=":bulb:"
                    )
                    success_count += 1
                    
                except SlackApiError as e:
                    logger.error(f"Failed to send insight to {channel}: {e}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending proactive insight: {e}")
            return False
    
    async def _build_alert_blocks(self, alert_data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict]:
        """
        🎨 Build beautiful Slack blocks for alerts
        
        🎯 PURPOSE: Turn raw alert data into visual, actionable Slack message
        
        VISUAL STRUCTURE:
        ┌─────────────────────────────────┐
        │ 🚨 High CPU Usage Alert         │
        │ Node: production-worker-02      │
        │ Current: 🔥🔥🔥🔥🔥🔥🔥🔥🔥⬜ 92% │
        │ Threshold: 80%                  │
        │ Duration: 15 minutes            │
        │ [🔍 Investigate] [📊 Metrics]   │
        └─────────────────────────────────┘
        
        💡 ADHD TIP: Visual blocks make alerts scannable - key info jumps out
        """
        
        # ===== ALERT HEADER =====
        alert_name = alert_data.get("name", "System Alert")
        severity = alert_data.get("severity", "warning")
        
        # Severity emoji mapping
        severity_emojis = {
            "critical": "🔥",
            "warning": "⚠️", 
            "info": "ℹ️"
        }
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emojis.get(severity, '⚠️')} {alert_name}"
                }
            }
        ]
        
        # ===== ALERT DETAILS =====
        # Show key information in a scannable format
        details_text = f"*🎯 Target:* {alert_data.get('target', 'Unknown')}\n"
        
        if alert_data.get("current_value"):
            details_text += f"*📊 Current:* {alert_data['current_value']}\n"
        
        if alert_data.get("threshold"):
            details_text += f"*🚧 Threshold:* {alert_data['threshold']}\n"
        
        if alert_data.get("duration"):
            details_text += f"*⏱️ Duration:* {alert_data['duration']}\n"
        
        # Add Jamie's British commentary
        if severity == "critical":
            details_text += f"\n🇬🇧 *Blimey!* This needs immediate attention, mate!"
        elif severity == "warning":
            details_text += f"\n🇬🇧 *Right then,* best have a look at this."
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": details_text
            }
        })
        
        # ===== VISUAL USAGE BAR (if applicable) =====
        # Show percentage alerts with visual bars
        if alert_data.get("percentage"):
            from .slack_formatters import create_usage_bar
            usage_bar = create_usage_bar(alert_data["percentage"])
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📈 Usage:* {usage_bar} {alert_data['percentage']:.1f}%"
                }
            })
        
        # ===== ACTION BUTTONS =====
        # Give team quick actions to take
        action_elements = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Investigate"},
                "action_id": f"investigate_alert_{alert_data.get('id', 'unknown')}",
                "style": "primary"
            },
            {
                "type": "button", 
                "text": {"type": "plain_text", "text": "📊 View Metrics"},
                "action_id": f"view_metrics_{alert_data.get('target', 'unknown')}"
            }
        ]
        
        # Add acknowledge button for critical alerts
        if severity == "critical":
            action_elements.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "✅ Acknowledge"},
                "action_id": f"ack_alert_{alert_data.get('id', 'unknown')}",
                "style": "danger"
            })
        
        blocks.append({
            "type": "actions",
            "elements": action_elements
        })
        
        # ===== FOOTER WITH TIMESTAMP =====
        # When did this happen?
        timestamp = alert_data.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
            
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕐 Alert triggered at {timestamp.strftime('%H:%M:%S')} | Powered by Jamie AI 🤖"
                }
            ]
        })
        
        return blocks
    
    async def _build_incident_blocks(self, incident_data: Dict[str, Any], update_type: str) -> List[Dict]:
        """Build Slack blocks for incident notifications"""
        
        severity = incident_data.get("severity", "high")
        status = incident_data.get("status", "investigating")
        
        status_emoji = {
            "investigating": "🔍",
            "identified": "🎯",
            "monitoring": "👀",
            "resolved": "✅"
        }.get(status, "🚨")
        
        severity_emoji = {
            "critical": "🔥",
            "high": "🚨",
            "medium": "⚠️",
            "low": "ℹ️"
        }.get(severity, "🚨")
        
        blocks = [
            {
                "type": "header", 
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji} Incident {update_type.title()}: {incident_data.get('title', 'Unknown Incident')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} *Status:* {status.title()} | *Severity:* {severity.title()}\n*Started:* {format_time_ago(incident_data.get('started_at', datetime.now()))}"
                }
            }
        ]
        
        # Add description/update
        if incident_data.get("description"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{incident_data['description']}"
                }
            })
        
        # Add impact information
        if incident_data.get("impact"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Impact:* {incident_data['impact']}"
                }
            })
        
        # Add affected components
        if incident_data.get("affected_components"):
            components_text = ", ".join(incident_data["affected_components"])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Affected Components:* {components_text}"
                }
            })
        
        # Add action buttons
        buttons = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🏥 Join War Room"},
                "action_id": f"join_war_room_{incident_data.get('id', 'unknown')}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 View Dashboard"},
                "action_id": f"view_dashboard_{incident_data.get('id', 'unknown')}"
            }
        ]
        
        if incident_data.get("status_page_url"):
            buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📢 Status Page"},
                "url": incident_data["status_page_url"]
            })
        
        blocks.append({
            "type": "actions",
            "elements": buttons
        })
        
        return blocks
    
    async def _build_deployment_blocks(self, deployment_data: Dict[str, Any]) -> List[Dict]:
        """Build Slack blocks for deployment notifications"""
        
        status = deployment_data.get("status", "unknown")
        service = deployment_data.get("service", "Unknown Service")
        version = deployment_data.get("version", "unknown")
        environment = deployment_data.get("environment", "unknown")
        
        status_emoji = {
            "success": "✅",
            "failed": "❌",
            "in_progress": "🔄",
            "rolled_back": "⏪"
        }.get(status, "📦")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} Deployment {status.title()}: {service}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Service:*\n{service}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Version:*\n{version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{environment}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status.title()}"
                    }
                ]
            }
        ]
        
        # Add deployment details
        if deployment_data.get("commit_hash"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Commit:* `{deployment_data['commit_hash'][:8]}`\n*Author:* {deployment_data.get('author', 'Unknown')}"
                }
            })
        
        # Add performance metrics if available
        if deployment_data.get("metrics"):
            metrics = deployment_data["metrics"]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Performance:*\n• Response Time: {metrics.get('response_time', 'N/A')}\n• Error Rate: {metrics.get('error_rate', 'N/A')}%\n• Throughput: {metrics.get('throughput', 'N/A')} req/s"
                }
            })
        
        # Add action buttons
        buttons = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 View Metrics"},
                "action_id": f"view_deployment_metrics_{deployment_data.get('id', 'unknown')}",
                "style": "primary"
            }
        ]
        
        if status == "failed":
            buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "🔙 Rollback"},
                "action_id": f"rollback_deployment_{deployment_data.get('id', 'unknown')}",
                "style": "danger"
            })
        
        if deployment_data.get("release_notes_url"):
            buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📝 Release Notes"},
                "url": deployment_data["release_notes_url"]
            })
        
        blocks.append({
            "type": "actions",
            "elements": buttons
        })
        
        return blocks
    
    async def _build_summary_blocks(self, summary_type: str, data: Dict[str, Any]) -> List[Dict]:
        """Build Slack blocks for summary reports"""
        
        period_emoji = {
            "daily": "📅",
            "weekly": "📊",
            "monthly": "📈"
        }.get(summary_type, "📋")
        
        british_greeting = get_british_response_flavor()
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{period_emoji} {summary_type.title()} DevOps Summary"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{british_greeting} Here's your {summary_type} DevOps roundup! 🇬🇧"
                }
            }
        ]
        
        # Add key metrics
        if data.get("metrics"):
            metrics = data["metrics"]
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*🚀 Deployments:*\n{metrics.get('deployments', 0)} total"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🚨 Incidents:*\n{metrics.get('incidents', 0)} resolved"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*⏱️ Avg Response Time:*\n{metrics.get('avg_response_time', 'N/A')}ms"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*📈 Uptime:*\n{metrics.get('uptime', 'N/A')}%"
                    }
                ]
            })
        
        # Add trends
        if data.get("trends"):
            trends = data["trends"]
            trend_text = []
            for metric, change in trends.items():
                direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                trend_text.append(f"• {metric.title()}: {direction} {abs(change):.1f}%")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 Trends vs Previous {summary_type}:*\n{chr(10).join(trend_text)}"
                }
            })
        
        # Add top issues/achievements
        if data.get("highlights"):
            highlights = data["highlights"]
            highlight_text = []
            for highlight in highlights[:3]:
                highlight_text.append(f"• {highlight}")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*✨ Key Highlights:*\n{chr(10).join(highlight_text)}"
                }
            })
        
        # Add action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 Full Report"},
                    "action_id": f"view_full_report_{summary_type}",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📈 Trends Dashboard"},
                    "action_id": f"view_trends_{summary_type}"
                }
            ]
        })
        
        return blocks
    
    async def _build_insight_blocks(self, insight_data: Dict[str, Any]) -> List[Dict]:
        """Build Slack blocks for proactive insights"""
        
        insight_type = insight_data.get("type", "performance")
        priority = insight_data.get("priority", "medium")
        
        type_emoji = {
            "performance": "⚡",
            "security": "🔒",
            "cost": "💰",
            "reliability": "🛡️",
            "capacity": "📊"
        }.get(insight_type, "💡")
        
        priority_color = {
            "high": "danger",
            "medium": "warning", 
            "low": "good"
        }.get(priority, "good")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{type_emoji} Jamie's Insight: {insight_data.get('title', 'Performance Recommendation')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{get_british_response_flavor()}* I've spotted something that might interest you! 🇬🇧\n\n{insight_data.get('description', 'No description available')}"
                }
            }
        ]
        
        # Add impact and recommendation
        if insight_data.get("impact") or insight_data.get("recommendation"):
            fields = []
            if insight_data.get("impact"):
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*📊 Impact:*\n{insight_data['impact']}"
                })
            if insight_data.get("recommendation"):
                fields.append({
                    "type": "mrkdwn", 
                    "text": f"*💡 Recommendation:*\n{insight_data['recommendation']}"
                })
            
            blocks.append({
                "type": "section",
                "fields": fields
            })
        
        # Add metrics if available
        if insight_data.get("metrics"):
            metrics_text = []
            for metric, value in insight_data["metrics"].items():
                metrics_text.append(f"• {metric}: {value}")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📈 Key Metrics:*\n{chr(10).join(metrics_text)}"
                }
            })
        
        # Add action buttons
        buttons = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "✅ Implement"},
                "action_id": f"implement_insight_{insight_data.get('id', 'unknown')}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📊 Learn More"},
                "action_id": f"learn_more_{insight_data.get('id', 'unknown')}"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "⏰ Remind Later"},
                "action_id": f"remind_later_{insight_data.get('id', 'unknown')}"
            }
        ]
        
        blocks.append({
            "type": "actions",
            "elements": buttons
        })
        
        return blocks
    
    async def _can_send_to_channel(self, channel: str, severity: NotificationSeverity) -> bool:
        """Check if notification can be sent to channel based on rate limits and preferences"""
        
        # Check rate limits (max 10 notifications per hour per channel)
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        if channel not in self.rate_limits:
            self.rate_limits[channel] = []
        
        # Clean old timestamps
        self.rate_limits[channel] = [
            ts for ts in self.rate_limits[channel] if ts > hour_ago
        ]
        
        # Check if under rate limit
        if len(self.rate_limits[channel]) >= 10:
            logger.warning(f"Rate limit exceeded for channel {channel}")
            return False
        
        # Always allow critical notifications
        if severity == NotificationSeverity.CRITICAL:
            return True
        
        return True
    
    async def _update_rate_limit(self, channel: str):
        """Update rate limit tracking for channel"""
        now = datetime.now()
        if channel not in self.rate_limits:
            self.rate_limits[channel] = []
        self.rate_limits[channel].append(now) 