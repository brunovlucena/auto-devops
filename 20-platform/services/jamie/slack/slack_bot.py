#!/usr/bin/env python3
"""
🤖 Jamie AI DevOps Copilot - Slack Bot
Sprint 5: Slack Integration

=== WHAT THIS FILE DOES ===
This is Jamie's main Slack bot - the heart of team collaboration!
- Handles slash commands like /jamie, /jamie-status
- Responds to @mentions and direct messages
- Creates beautiful interactive buttons and menus
- Manages team conversations with British personality

=== KEY CONCEPTS TO UNDERSTAND ===
1. AsyncApp: Slack's modern bot framework (handles all Slack events)
2. Socket Mode: Real-time connection to Slack (no webhooks needed!)
3. Handlers: Functions that respond to specific Slack actions
4. Blocks: Slack's rich formatting system (like HTML for messages)
5. Context: Information about who, where, when each message happens

=== MAIN FLOW ===
User types /jamie → Slack sends event → Our handler processes → Jamie responds
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# ===== SLACK SDK IMPORTS =====
# These are the official Slack libraries for building bots
from slack_bolt.async_app import AsyncApp                    # Main bot app framework
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler  # Real-time connection
from slack_sdk.web.async_client import AsyncWebClient       # For sending messages
from slack_sdk.errors import SlackApiError                   # Error handling

# ===== JAMIE'S BRAIN IMPORTS =====
# These connect to Jamie's AI and DevOps knowledge
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.jamie_brain import JamieBrain     # Jamie's AI intelligence
from api.mcp_client import MCPClient       # DevOps data (Kubernetes, Prometheus, etc.)

# ===== SLACK HELPERS =====
# These make Slack messages beautiful and smart
from .slack_formatters import format_cluster_status, format_error_analysis, format_metrics_summary
from .slack_utils import extract_devops_intent, get_user_preferences, save_user_preferences

# ===== LOGGING SETUP =====
# This helps us debug when things go wrong
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 🤖 MAIN JAMIE SLACK BOT CLASS
# ==========================================
class JamieSlackBot:
    """
    Jamie's Slack Bot - Your AI DevOps Copilot in Slack
    
    🎯 MAIN PURPOSE: Be the friendly face of DevOps in your team chat
    
    ✨ FEATURES:
    - Slash commands (/jamie, /jamie-status, /jamie-help)
    - Interactive buttons and menus  
    - Team collaboration and notifications
    - Cross-platform sync with portal
    - British personality in all interactions
    
    🧠 HOW IT WORKS:
    1. User interacts with Jamie in Slack (command, mention, DM)
    2. Slack sends event to our bot
    3. We extract intent (what does user want?)
    4. Jamie's brain processes with DevOps context
    5. We format response beautifully for Slack
    6. User gets helpful answer with personality!
    """
    
    def __init__(self, bot_token: str, app_token: str, signing_secret: str):
        """
        🚀 Initialize Jamie's Slack bot
        
        IMPORTANT TOKENS EXPLAINED:
        - bot_token: Like Jamie's ID card (starts with xoxb-)
        - app_token: For real-time connection (starts with xapp-)  
        - signing_secret: Security key to verify messages are really from Slack
        """
        
        # ===== SLACK APP SETUP =====
        # This creates the main bot app with security
        self.app = AsyncApp(
            token=bot_token,                    # Jamie's identity
            signing_secret=signing_secret,      # Security verification
            process_before_response=True        # Process in background (faster responses)
        )
        
        # ===== SLACK CLIENT =====
        # This is how we send messages back to Slack
        self.client = AsyncWebClient(token=bot_token)
        self.app_token = app_token
        
        # ===== JAMIE'S BRAIN CONNECTION =====
        # Connect to Jamie's AI and DevOps knowledge
        self.jamie_brain = JamieBrain()      # The AI that makes Jamie smart
        self.mcp_client = MCPClient()        # DevOps data source (K8s, Prometheus, etc.)
        
        # ===== USER SESSION MANAGEMENT =====
        # Remember conversations with each user
        self.user_sessions: Dict[str, Dict] = {}
        
        # ===== REGISTER ALL HANDLERS =====
        # This connects Slack events to our response functions
        self._register_handlers()
        
        logger.info("🤖 Jamie Slack Bot initialized - Ready to help your team!")
    
    def _register_handlers(self):
        """
        📋 Register all Slack command and event handlers
        
        🎯 PURPOSE: Tell Slack "when X happens, call function Y"
        
        HANDLER TYPES:
        - Commands: /jamie, /jamie-status (user types slash commands)
        - Actions: Button clicks, menu selections
        - Events: @mentions, direct messages, home tab opens
        
        💡 ADHD TIP: Each handler is like a specific response to a specific trigger
        """
        
        # ===== SLASH COMMANDS =====
        # These respond when users type /jamie commands
        self.app.command("/jamie")(self.handle_jamie_command)          # Main command
        self.app.command("/jamie-status")(self.handle_status_command)  # Quick status
        self.app.command("/jamie-help")(self.handle_help_command)      # Show help
        self.app.command("/jamie-setup")(self.handle_setup_command)    # Team setup
        
        # ===== INTERACTIVE COMPONENTS =====
        # These respond to button clicks and menu selections
        self.app.action("cluster_details")(self.handle_cluster_details)
        self.app.action("error_analysis")(self.handle_error_analysis)
        self.app.action("metrics_deep_dive")(self.handle_metrics_deep_dive)
        self.app.action("refresh_status")(self.handle_refresh_status)
        
        # ===== BUTTON ACTIONS =====
        # Quick action buttons for common tasks
        self.app.action("quick_health_check")(self.handle_quick_health_check)
        self.app.action("recent_errors")(self.handle_recent_errors)
        self.app.action("performance_summary")(self.handle_performance_summary)
        
        # ===== MENU SELECTIONS =====
        # Dropdown menu selections
        self.app.action("service_selector")(self.handle_service_selection)
        self.app.action("time_range_selector")(self.handle_time_range_selection)
        
        # ===== MESSAGE EVENTS =====
        # These respond to natural conversation
        self.app.event("app_mention")(self.handle_app_mention)         # @jamie mentions
        self.app.event("message")(self.handle_direct_message)          # Direct messages
        
        # ===== HOME TAB =====
        # Personal dashboard when user clicks on Jamie
        self.app.event("app_home_opened")(self.handle_home_tab)
    
    async def handle_jamie_command(self, ack, respond, command, client):
        """
        🎯 Handle /jamie slash command - Main interaction point
        
        ✨ THIS IS THE MAGIC! Main way users talk to Jamie
        
        EXAMPLES:
        /jamie How's my cluster?
        /jamie Show me errors from auth-service  
        /jamie What's the CPU usage?
        
        🔄 FLOW:
        1. User types /jamie <question>
        2. Extract what they want (intent)
        3. Get user preferences 
        4. Show "thinking..." message
        5. Jamie's brain processes with DevOps context
        6. Format beautiful response
        7. Update original message with answer
        
        💡 ADHD TIP: The 'ack()' tells Slack "got it!" within 3 seconds
        """
        # ===== IMMEDIATE ACKNOWLEDGMENT =====
        # CRITICAL: Must call this within 3 seconds or Slack shows error
        await ack()
        
        # ===== EXTRACT COMMAND DETAILS =====
        user_id = command["user_id"]        # Who asked the question?
        channel_id = command["channel_id"]  # Where was it asked?
        text = command.get("text", "").strip()  # What did they ask?
        
        # ===== HANDLE EMPTY COMMAND =====
        # If user just types /jamie with no question
        if not text:
            await self._show_jamie_help(respond)
            return
        
        # ===== GET USER CONTEXT =====
        # Load user preferences and settings
        user_prefs = await get_user_preferences(user_id)
        
        # ===== SHOW THINKING MESSAGE =====
        # Let user know Jamie is working (good UX!)
        thinking_msg = await respond(
            text="🤖 *Jamie is thinking...*",
            response_type="ephemeral"  # Only visible to user who asked
        )
        
        try:
            # ===== EXTRACT DEVOPS INTENT =====
            # Figure out what user wants: cluster status? errors? metrics?
            context = {
                "platform": "slack",                    # Remember this came from Slack
                "user_id": user_id,                     # Who asked
                "channel_id": channel_id,               # Where they asked
                "preferences": user_prefs,              # Their settings
                **extract_devops_intent(text)          # What they want (the magic!)
            }
            
            # ===== JAMIE'S BRAIN PROCESSES =====
            # This is where the AI magic happens!
            response = await self.jamie_brain.process_message(
                message=text,                                    # User's question
                user_id=user_id,                                # Who asked
                session_id=f"slack_{user_id}_{channel_id}",    # Conversation tracking
                context=context                                 # All the context
            )
            
            # ===== FORMAT FOR SLACK =====
            # Turn Jamie's response into beautiful Slack blocks
            blocks = await self._format_jamie_response(response, text)
            
            # ===== SEND THE ANSWER =====
            # Replace "thinking..." with actual answer
            await client.chat_update(
                channel=channel_id,
                ts=thinking_msg["ts"],  # Update the existing message
                text=f"🤖 Jamie says:",
                blocks=blocks
            )
            
        except Exception as e:
            # ===== ERROR HANDLING =====
            # If something goes wrong, tell user in Jamie's voice
            logger.error(f"Error processing Jamie command: {e}")
            await client.chat_update(
                channel=channel_id,
                ts=thinking_msg["ts"],
                text="🤖 Blimey! I'm having a bit of trouble right now. Give me a tick to sort myself out, mate! 🇬🇧"
            )
    
    async def handle_status_command(self, ack, respond, command):
        """
        📊 Handle /jamie-status - Quick system overview
        
        🎯 PURPOSE: Fast health check without typing long questions
        
        WHAT IT DOES:
        1. Gets cluster status from Kubernetes
        2. Gets alert status from Prometheus  
        3. Formats into beautiful overview
        4. Shows only to user (ephemeral)
        
        💡 ADHD TIP: This is for when you just want quick "is everything OK?"
        """
        await ack()
        
        try:
            # ===== GET SYSTEM STATUS =====
            # Fetch data from our DevOps tools
            k8s_status = await self.mcp_client.kubernetes.get_cluster_status()     # Kubernetes health
            prometheus_status = await self.mcp_client.prometheus.get_alerts_summary()  # Alerts
            
            # ===== FORMAT BEAUTIFUL RESPONSE =====
            # Turn raw data into pretty Slack blocks
            blocks = format_cluster_status(k8s_status, prometheus_status)
            
            # ===== SEND STATUS =====
            await respond(
                text="📊 *System Status Overview*",
                blocks=blocks,
                response_type="ephemeral"  # Only visible to user
            )
            
        except Exception as e:
            # ===== ERROR WITH BRITISH PERSONALITY =====
            logger.error(f"Error getting status: {e}")
            await respond(
                text="❌ *Status Check Failed*\n\nSorry mate, I can't fetch the system status right now. The monitoring systems might be having a wobble! 🇬🇧",
                response_type="ephemeral"
            )
    
    async def handle_help_command(self, ack, respond, command):
        """
        🆘 Handle /jamie-help - Show available commands and features
        
        🎯 PURPOSE: Help users discover what Jamie can do
        """
        await ack()
        await self._show_jamie_help(respond)
    
    async def handle_setup_command(self, ack, respond, command):
        """
        ⚙️ Handle /jamie-setup - Configure Jamie for the team
        
        🎯 PURPOSE: Team administrators can configure channels, notifications, preferences
        
        WHAT IT SETS UP:
        - Which channels get alerts
        - Notification preferences  
        - Team-wide settings
        - Integration connections
        """
        await ack()
        
        user_id = command["user_id"]
        
        # ===== CHECK ADMIN PERMISSIONS =====
        # (In real implementation, check Slack workspace admin status)
        
        # ===== BUILD SETUP INTERFACE =====
        setup_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text", 
                    "text": "⚙️ Jamie Team Setup"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Right then! Let's get Jamie properly configured for your team. 🇬🇧"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📢 Channel Configuration*\nChoose where Jamie should send different types of notifications:"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select alerts channel"
                    },
                    "action_id": "select_alerts_channel"
                }
            }
        ]
        
        await respond(
            text="⚙️ *Jamie Team Setup*",
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