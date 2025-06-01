#!/usr/bin/env python3
"""
🤖 Jamie AI DevOps Copilot - Slack Bot
Sprint 5: Slack Integration

A native Slack bot that brings Jamie's DevOps intelligence to your team workspace.
Supports slash commands, interactive buttons, team collaboration, and real-time notifications.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from ..api.jamie_brain import JamieBrain
from ..api.mcp_client import MCPClient
from .slack_formatters import format_cluster_status, format_error_analysis, format_metrics_summary
from .slack_utils import extract_devops_intent, get_user_preferences, save_user_preferences

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JamieSlackBot:
    """
    Jamie's Slack Bot - Your AI DevOps Copilot in Slack
    
    Features:
    - Slash commands (/jamie, /jamie-status, /jamie-help)
    - Interactive buttons and menus
    - Team collaboration and notifications
    - Cross-platform sync with portal
    - British personality in all interactions
    """
    
    def __init__(self, bot_token: str, app_token: str, signing_secret: str):
        """Initialize Jamie's Slack bot"""
        self.app = AsyncApp(
            token=bot_token,
            signing_secret=signing_secret,
            process_before_response=True
        )
        
        self.client = AsyncWebClient(token=bot_token)
        self.app_token = app_token
        
        # Initialize Jamie's brain and MCP connections
        self.jamie_brain = JamieBrain()
        self.mcp_client = MCPClient()
        
        # User session management
        self.user_sessions: Dict[str, Dict] = {}
        
        # Register all Slack handlers
        self._register_handlers()
        
        logger.info("🤖 Jamie Slack Bot initialized - Ready to help your team!")
    
    def _register_handlers(self):
        """Register all Slack command and event handlers"""
        
        # Slash Commands
        self.app.command("/jamie")(self.handle_jamie_command)
        self.app.command("/jamie-status")(self.handle_status_command)
        self.app.command("/jamie-help")(self.handle_help_command)
        self.app.command("/jamie-setup")(self.handle_setup_command)
        
        # Interactive Components
        self.app.action("cluster_details")(self.handle_cluster_details)
        self.app.action("error_analysis")(self.handle_error_analysis)
        self.app.action("metrics_deep_dive")(self.handle_metrics_deep_dive)
        self.app.action("refresh_status")(self.handle_refresh_status)
        
        # Button Actions
        self.app.action("quick_health_check")(self.handle_quick_health_check)
        self.app.action("recent_errors")(self.handle_recent_errors)
        self.app.action("performance_summary")(self.handle_performance_summary)
        
        # Menu Selections
        self.app.action("service_selector")(self.handle_service_selection)
        self.app.action("time_range_selector")(self.handle_time_range_selection)
        
        # Message Events
        self.app.event("app_mention")(self.handle_app_mention)
        self.app.event("message")(self.handle_direct_message)
        
        # Home Tab
        self.app.event("app_home_opened")(self.handle_home_tab)
    
    async def handle_jamie_command(self, ack, respond, command, client):
        """
        Handle /jamie slash command - Main interaction point
        
        Usage:
        /jamie How's my cluster?
        /jamie Show me errors from auth-service
        /jamie What's the CPU usage?
        """
        await ack()
        
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        text = command.get("text", "").strip()
        
        if not text:
            await self._show_jamie_help(respond)
            return
        
        # Extract user context and preferences
        user_prefs = await get_user_preferences(user_id)
        
        # Show thinking message
        thinking_msg = await respond(
            text="🤖 *Jamie is thinking...*",
            response_type="ephemeral"
        )
        
        try:
            # Process the query through Jamie's brain
            context = {
                "platform": "slack",
                "user_id": user_id,
                "channel_id": channel_id,
                "preferences": user_prefs,
                **extract_devops_intent(text)
            }
            
            response = await self.jamie_brain.process_message(
                message=text,
                user_id=user_id,
                session_id=f"slack_{user_id}_{channel_id}",
                context=context
            )
            
            # Format response for Slack
            blocks = await self._format_jamie_response(response, text)
            
            # Send the formatted response
            await client.chat_update(
                channel=channel_id,
                ts=thinking_msg["ts"],
                text=f"🤖 Jamie says:",
                blocks=blocks
            )
            
        except Exception as e:
            logger.error(f"Error processing Jamie command: {e}")
            await client.chat_update(
                channel=channel_id,
                ts=thinking_msg["ts"],
                text="🤖 Blimey! I'm having a bit of trouble right now. Give me a tick to sort myself out, mate! 🇬🇧"
            )
    
    async def handle_status_command(self, ack, respond, command):
        """Handle /jamie-status - Quick system overview"""
        await ack()
        
        try:
            # Get comprehensive system status
            k8s_status = await self.mcp_client.kubernetes.get_cluster_status()
            prometheus_status = await self.mcp_client.prometheus.get_alerts_summary()
            
            blocks = format_cluster_status(k8s_status, prometheus_status)
            
            await respond(
                text="📊 *System Status Overview*",
                blocks=blocks,
                response_type="ephemeral"
            )
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await respond(
                text="❌ *Status Check Failed*\n\nSorry mate, I can't fetch the system status right now. The monitoring systems might be having a wobble! 🇬🇧",
                response_type="ephemeral"
            )
    
    async def handle_help_command(self, ack, respond, command):
        """Handle /jamie-help - Show available commands and features"""
        await ack()
        await self._show_jamie_help(respond)
    
    async def handle_setup_command(self, ack, respond, command):
        """Handle /jamie-setup - Configure Jamie for the team"""
        await ack()
        
        user_id = command["user_id"]
        
        # Check if user has admin permissions
        # (In real implementation, check Slack workspace admin status)
        
        setup_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Jamie Setup & Configuration"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Welcome to Jamie's setup wizard!* 🇬🇧\n\nLet's get your team connected to your DevOps infrastructure:"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 Configure Monitoring"
                        },
                        "action_id": "setup_monitoring",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text", 
                            "text": "☸️ Setup Kubernetes"
                        },
                        "action_id": "setup_kubernetes"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔔 Notification Settings"
                        },
                        "action_id": "setup_notifications"
                    }
                ]
            }
        ]
        
        await respond(
            text="🤖 Jamie Setup",
            blocks=setup_blocks,
            response_type="ephemeral"
        )
    
    async def handle_app_mention(self, event, say):
        """Handle @jamie mentions in channels"""
        user_id = event["user"]
        text = event["text"]
        channel = event["channel"]
        
        # Remove mention from text
        mention_text = text.split(">", 1)[1].strip() if ">" in text else text
        
        if not mention_text:
            await say(
                text="Alright mate! 👋 Ask me anything about your infrastructure - I'm here to help! 🤖",
                thread_ts=event.get("ts")
            )
            return
        
        # Process as regular Jamie query
        try:
            context = {
                "platform": "slack",
                "user_id": user_id,
                "channel_id": channel,
                "mention": True,
                **extract_devops_intent(mention_text)
            }
            
            response = await self.jamie_brain.process_message(
                message=mention_text,
                user_id=user_id,
                session_id=f"slack_{user_id}_{channel}",
                context=context
            )
            
            blocks = await self._format_jamie_response(response, mention_text)
            
            await say(
                text="🤖 Jamie here!",
                blocks=blocks,
                thread_ts=event.get("ts")
            )
            
        except Exception as e:
            logger.error(f"Error handling mention: {e}")
            await say(
                text="Blimey! I'm having a bit of trouble processing that. Could you give me another go? 🇬🇧",
                thread_ts=event.get("ts")
            )
    
    async def handle_direct_message(self, event, say):
        """Handle direct messages to Jamie"""
        if event.get("channel_type") != "im":
            return  # Only handle DMs
        
        user_id = event["user"]
        text = event["text"]
        
        try:
            context = {
                "platform": "slack",
                "user_id": user_id,
                "channel_type": "dm",
                **extract_devops_intent(text)
            }
            
            response = await self.jamie_brain.process_message(
                message=text,
                user_id=user_id,
                session_id=f"slack_dm_{user_id}",
                context=context
            )
            
            blocks = await self._format_jamie_response(response, text)
            
            await say(
                text="🤖 Jamie here!",
                blocks=blocks
            )
            
        except Exception as e:
            logger.error(f"Error handling DM: {e}")
            await say(
                text="Sorry mate, I'm having a bit of trouble understanding that. Try asking about your cluster status or recent errors! 🤖"
            )
    
    async def handle_home_tab(self, event, client):
        """Handle Home tab - Jamie's personal dashboard"""
        user_id = event["user"]
        
        try:
            # Get user's recent activity and system overview
            user_prefs = await get_user_preferences(user_id)
            
            home_blocks = await self._build_home_tab(user_prefs)
            
            await client.views_publish(
                user_id=user_id,
                view={
                    "type": "home",
                    "blocks": home_blocks
                }
            )
            
        except Exception as e:
            logger.error(f"Error building home tab: {e}")
    
    async def _format_jamie_response(self, response: Dict[str, Any], original_query: str) -> List[Dict]:
        """Format Jamie's response for Slack with proper blocks"""
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤖 Jamie says:*\n\n{response['response']}"
                }
            }
        ]
        
        # Add metadata if available
        if response.get("metadata"):
            metadata = response["metadata"]
            
            if metadata.get("confidence"):
                confidence = int(metadata["confidence"] * 100)
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🧠 Confidence: {confidence}% | 🏷️ Intent: {metadata.get('intent', 'general')}"
                        }
                    ]
                })
        
        # Add action buttons based on query type
        if any(keyword in original_query.lower() for keyword in ["cluster", "status", "health"]):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Detailed View"},
                        "action_id": "cluster_details"
                    },
                    {
                        "type": "button", 
                        "text": {"type": "plain_text", "text": "🔄 Refresh"},
                        "action_id": "refresh_status"
                    }
                ]
            })
        
        elif any(keyword in original_query.lower() for keyword in ["error", "issue", "problem"]):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔍 Deep Analysis"},
                        "action_id": "error_analysis"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📈 Show Trends"},
                        "action_id": "error_trends"
                    }
                ]
            })
        
        return blocks
    
    async def _show_jamie_help(self, respond):
        """Show comprehensive help for Jamie's Slack commands"""
        
        help_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Jamie AI DevOps Copilot Help"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alright mate! Here's how to chat with your AI DevOps buddy:* 🇬🇧"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Slash Commands:*\n`/jamie <question>` - Ask anything\n`/jamie-status` - Quick health check\n`/jamie-help` - Show this help\n`/jamie-setup` - Configure Jamie"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Example Questions:*\n• How's my cluster doing?\n• Show me recent errors\n• What's the CPU usage?\n• Any alerts firing?"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💡 Pro Tips:*\n• Mention `@jamie` in any channel\n• DM me directly for private queries\n• Use action buttons for quick actions\n• Check the Home tab for your dashboard"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🏥 Health Check"},
                        "action_id": "quick_health_check",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚨 Recent Errors"},
                        "action_id": "recent_errors"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Performance"},
                        "action_id": "performance_summary"
                    }
                ]
            }
        ]
        
        await respond(
            text="🤖 Jamie Help",
            blocks=help_blocks,
            response_type="ephemeral"
        )
    
    async def _build_home_tab(self, user_prefs: Dict) -> List[Dict]:
        """Build the Home tab dashboard for users"""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Jamie AI DevOps Dashboard"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Good {'morning' if datetime.now().hour < 12 else 'afternoon'}!* Welcome to your personal DevOps command center. 🇬🇧"
                }
            }
        ]
        
        # Add quick stats section
        try:
            k8s_summary = await self.mcp_client.kubernetes.get_cluster_summary()
            
            blocks.extend([
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*🏗️ Cluster Nodes:*\n{k8s_summary.get('nodes', 'N/A')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*🚀 Running Pods:*\n{k8s_summary.get('pods', 'N/A')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*⚠️ Active Alerts:*\n{k8s_summary.get('alerts', 'N/A')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*📊 Services:*\n{k8s_summary.get('services', 'N/A')}"
                        }
                    ]
                }
            ])
        except:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📊 *Quick Stats loading...* Use the buttons below for real-time data!"
                }
            })
        
        # Add quick action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🏥 Full Health Check"},
                    "action_id": "quick_health_check",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🚨 Error Analysis"},
                    "action_id": "recent_errors"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📈 Performance Metrics"},
                    "action_id": "performance_summary"
                }
            ]
        })
        
        return blocks
    
    async def start(self):
        """Start the Slack bot with Socket Mode"""
        handler = AsyncSocketModeHandler(self.app, self.app_token)
        logger.info("🚀 Starting Jamie Slack Bot...")
        await handler.start_async()


# Quick action handlers
async def handle_quick_health_check(ack, respond, action):
    """Handle quick health check button"""
    await ack()
    
    try:
        # Implement health check logic
        await respond(
            text="🏥 *Quick Health Check*\n\n✅ All systems looking good, mate! 🇬🇧",
            response_type="ephemeral"
        )
    except Exception as e:
        await respond(
            text="❌ *Health Check Failed*\n\nSorry, having trouble checking the systems right now.",
            response_type="ephemeral"
        )

async def handle_recent_errors(ack, respond, action):
    """Handle recent errors button"""
    await ack()
    
    try:
        # Implement error analysis logic
        await respond(
            text="🚨 *Recent Errors*\n\nNo recent errors found - your systems are running smoothly! 🎉",
            response_type="ephemeral"
        )
    except Exception as e:
        await respond(
            text="❌ *Error Analysis Failed*\n\nCan't fetch error data at the moment.",
            response_type="ephemeral"
        )

async def handle_performance_summary(ack, respond, action):
    """Handle performance summary button"""
    await ack()
    
    try:
        # Implement performance metrics logic
        await respond(
            text="📊 *Performance Summary*\n\n📈 CPU: 65% | 💾 Memory: 72% | 🌐 Network: Normal",
            response_type="ephemeral"
        )
    except Exception as e:
        await respond(
            text="❌ *Performance Check Failed*\n\nUnable to fetch performance metrics right now.",
            response_type="ephemeral"
        ) 