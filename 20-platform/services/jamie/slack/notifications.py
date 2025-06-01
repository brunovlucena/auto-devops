#!/usr/bin/env python3
"""
🔔 Jamie AI DevOps Copilot - Slack Notifications
Sprint 5: Slack Integration

Automated notification system for team alerts, incident management,
and proactive DevOps insights delivered to Slack channels.
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

class NotificationSeverity(Enum):
    """Notification severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class NotificationType(Enum):
    """Types of notifications Jamie can send"""
    ALERT = "alert"
    INCIDENT = "incident"
    DEPLOYMENT = "deployment"
    HEALTH_CHECK = "health_check"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    SUMMARY = "summary"

class JamieNotificationManager:
    """
    Manages all Slack notifications for Jamie AI DevOps Copilot
    
    Features:
    - Real-time alerts and incident notifications
    - Scheduled reports and summaries
    - User preference-based filtering
    - Channel-specific routing
    - Rate limiting and de-duplication
    """
    
    def __init__(self, slack_client: AsyncWebClient):
        self.client = slack_client
        self.notification_queue: List[Dict] = []
        self.sent_notifications: Dict[str, datetime] = {}  # For de-duplication
        self.rate_limits: Dict[str, List[datetime]] = {}   # Rate limiting per channel
        
    async def send_alert_notification(
        self, 
        alert_data: Dict[str, Any], 
        channels: List[str],
        severity: NotificationSeverity = NotificationSeverity.WARNING
    ) -> bool:
        """Send alert notification to specified channels"""
        
        try:
            # Build notification context
            context = build_notification_context("alert", alert_data)
            
            # Create alert blocks
            blocks = await self._build_alert_blocks(alert_data, context)
            
            # Send to each channel
            success_count = 0
            for channel in channels:
                if await self._can_send_to_channel(channel, severity):
                    try:
                        await self.client.chat_postMessage(
                            channel=channel,
                            text=f"🚨 Alert: {alert_data.get('name', 'Unknown Alert')}",
                            blocks=blocks,
                            username="Jamie AI",
                            icon_emoji=":robot_face:"
                        )
                        success_count += 1
                        
                        # Update rate limiting
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
        """Send incident notification with proper escalation"""
        
        try:
            severity = NotificationSeverity.CRITICAL
            
            # Create incident-specific blocks
            blocks = await self._build_incident_blocks(incident_data, update_type)
            
            # Add incident war room link if available
            if incident_data.get("war_room_channel"):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🏥 *War Room:* <#{incident_data['war_room_channel']}>"
                    }
                })
            
            # Send notifications
            success_count = 0
            for channel in channels:
                if await self._can_send_to_channel(channel, severity):
                    try:
                        # Use thread for updates to existing incidents
                        thread_ts = None
                        if update_type != "new" and incident_data.get("original_message_ts"):
                            thread_ts = incident_data["original_message_ts"]
                        
                        response = await self.client.chat_postMessage(
                            channel=channel,
                            text=f"🚨 Incident {update_type.title()}: {incident_data.get('title', 'Unknown Incident')}",
                            blocks=blocks,
                            thread_ts=thread_ts,
                            username="Jamie AI",
                            icon_emoji=":rotating_light:"
                        )
                        
                        # Store message timestamp for threading
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
        """Send deployment status notification"""
        
        try:
            blocks = await self._build_deployment_blocks(deployment_data)
            
            status = deployment_data.get("status", "unknown")
            emoji = {
                "success": "✅",
                "failed": "❌", 
                "in_progress": "🔄",
                "rolled_back": "⏪"
            }.get(status, "📦")
            
            success_count = 0
            for channel in channels:
                try:
                    await self.client.chat_postMessage(
                        channel=channel,
                        text=f"{emoji} Deployment {status}: {deployment_data.get('service', 'Unknown Service')}",
                        blocks=blocks,
                        username="Jamie AI",
                        icon_emoji=":rocket:"
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
        """Build Slack blocks for alert notifications"""
        
        severity = alert_data.get("severity", "warning")
        severity_emoji = {
            "critical": "🔥",
            "warning": "⚠️", 
            "info": "ℹ️"
        }.get(severity, "⚠️")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji} Alert: {alert_data.get('name', 'Unknown Alert')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Status:* {alert_data.get('status', 'Firing')} | *Severity:* {severity.title()}\n*Description:* {alert_data.get('description', 'No description available')}"
                }
            }
        ]
        
        # Add affected services/components
        if alert_data.get("affected_services"):
            services_text = ", ".join(alert_data["affected_services"])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Affected Services:* {services_text}"
                }
            })
        
        # Add metric values if available
        if alert_data.get("current_value"):
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Current Value:*\n{alert_data['current_value']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Threshold:*\n{alert_data.get('threshold', 'N/A')}"
                    }
                ]
            })
        
        # Add action buttons
        buttons = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔍 Investigate"},
                "action_id": f"investigate_alert_{alert_data.get('id', 'unknown')}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🔇 Acknowledge"},
                "action_id": f"ack_alert_{alert_data.get('id', 'unknown')}"
            }
        ]
        
        if alert_data.get("runbook_url"):
            buttons.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📖 Runbook"},
                "url": alert_data["runbook_url"]
            })
        
        blocks.append({
            "type": "actions",
            "elements": buttons
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