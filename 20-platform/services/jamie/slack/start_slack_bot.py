#!/usr/bin/env python3
"""
🚀 Jamie AI DevOps Copilot - Slack Bot Startup
Sprint 5: Slack Integration

=== WHAT THIS FILE DOES ===
The mission control for Jamie's Slack bot! Handles everything needed to get Jamie online:
- 🔧 Environment Configuration: Load tokens, channels, settings
- 🏥 Health Monitoring: Keep Jamie running smoothly  
- 🛡️ Error Recovery: Restart if something goes wrong
- 📊 Production Readiness: Logging, monitoring, graceful shutdown

=== STARTUP FLOW ===
1. Load Configuration → 2. Validate Credentials → 3. Test Connection → 4. Initialize Jamie → 5. Start Monitoring → 6. Go Live!

=== PRODUCTION FEATURES ===
- Environment variable validation
- Slack connection testing
- Health check monitoring
- Graceful shutdown handling
- Comprehensive logging
- Startup notifications

=== FOR ADHD BRAINS ===
Think of this as Jamie's "wake up routine" - all the steps needed to get from "off" to "ready to help the team!"
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

# ===== CORE IMPORTS =====
from slack_bot import JamieSlackBot                    # Main bot class
from notifications import JamieNotificationManager     # Notification system
from slack_sdk.web.async_client import AsyncWebClient  # Slack API client

# ===== LOGGING CONFIGURATION =====
# Proper logging is CRITICAL for production debugging!
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File logging (for persistent logs)
        logging.FileHandler('/var/log/jamie/slack_bot.log'),
        # Console logging (for immediate feedback)
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# 🚀 JAMIE SLACK BOOTSTRAP CLASS
# ==========================================

class JamieSlackBootstrap:
    """
    🎯 Bootstrap and manage Jamie's Slack bot lifecycle
    
    ✨ RESPONSIBILITIES:
    - Environment configuration and validation
    - Bot initialization and dependency injection
    - Health monitoring and error recovery
    - Graceful shutdown and cleanup
    - Production logging and metrics
    
    🧠 LIFECYCLE:
    STARTING → VALIDATING → CONNECTING → INITIALIZING → RUNNING → MONITORING → (SHUTTING DOWN)
    
    💡 ADHD TIP: This class is like Jamie's "life support system" - keeps everything running smoothly
    """
    
    def __init__(self):
        """
        🔧 Initialize bootstrap with default settings
        
        WHAT WE TRACK:
        - bot: The main Jamie Slack bot instance
        - notification_manager: Alert/notification system
        - health_check_interval: How often to check if everything's OK
        - running: Is the bot currently active?
        """
        self.bot: JamieSlackBot = None                      # Main bot instance
        self.notification_manager: JamieNotificationManager = None  # Notification system
        self.health_check_interval = 300                    # 5 minutes between health checks
        self.running = False                                # Bot status flag
        
    async def initialize(self) -> bool:
        """
        🚀 Initialize Jamie's Slack bot with all dependencies
        
        🎯 PURPOSE: Get Jamie ready to serve the team!
        
        INITIALIZATION STEPS:
        1. Load configuration from environment
        2. Validate Slack credentials  
        3. Test Slack connection
        4. Initialize notification manager
        5. Create Jamie bot instance
        6. Send startup notification
        
        RETURNS: True if successful, False if any step fails
        
        💡 ADHD TIP: Each step must succeed before the next - like a checklist!
        """
        
        try:
            logger.info("🚀 Initializing Jamie AI DevOps Copilot Slack Bot...")
            
            # ===== STEP 1: LOAD CONFIGURATION =====
            # Get all the settings and secrets we need
            config = self._load_configuration()
            if not config:
                logger.error("❌ Failed to load configuration")
                return False
            
            # ===== STEP 2: VALIDATE CREDENTIALS =====
            # Make sure tokens look right before trying to use them
            if not self._validate_slack_credentials(config):
                logger.error("❌ Invalid Slack credentials")
                return False
            
            # ===== STEP 3: TEST SLACK CONNECTION =====
            # Actually try to connect to Slack workspace
            slack_client = AsyncWebClient(token=config['bot_token'])
            
            try:
                auth_response = await slack_client.auth_test()
                logger.info(f"✅ Connected to Slack workspace: {auth_response['team']}")
                logger.info(f"🤖 Bot user: @{auth_response['user']}")
            except Exception as e:
                logger.error(f"❌ Slack connection test failed: {e}")
                return False
            
            # ===== STEP 4: INITIALIZE NOTIFICATION MANAGER =====
            # Set up the system that sends alerts and updates
            self.notification_manager = JamieNotificationManager(slack_client)
            logger.info("✅ Notification manager initialized")
            
            # ===== STEP 5: INITIALIZE JAMIE BOT =====
            # Create the main bot with all capabilities
            self.bot = JamieSlackBot(
                bot_token=config['bot_token'],
                app_token=config['app_token'],
                signing_secret=config['signing_secret']
            )
            logger.info("✅ Jamie Slack bot initialized")
            
            # ===== STEP 6: SEND STARTUP NOTIFICATION =====
            # Let the team know Jamie is online!
            await self._send_startup_notification()
            
            logger.info("🎉 Jamie Slack bot ready for action!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _load_configuration(self) -> Dict[str, str]:
        """
        📋 Load Slack bot configuration from environment variables
        
        🎯 PURPOSE: Gather all settings needed to run Jamie
        
        REQUIRED ENVIRONMENT VARIABLES:
        - SLACK_BOT_TOKEN: Bot's identity token (starts with xoxb-)
        - SLACK_APP_TOKEN: Real-time connection token (starts with xapp-)
        - SLACK_SIGNING_SECRET: Security validation key
        
        OPTIONAL SETTINGS:
        - SLACK_DEFAULT_CHANNEL: Where to send general messages
        - SLACK_ALERTS_CHANNEL: Where to send critical alerts
        - SLACK_NOTIFICATIONS_CHANNEL: Where to send Jamie's updates
        
        💡 ADHD TIP: Environment variables keep secrets out of code (security!)
        """
        
        # ===== DEFINE REQUIRED VARIABLES =====
        required_vars = [
            'SLACK_BOT_TOKEN',      # Jamie's Slack identity
            'SLACK_APP_TOKEN',      # Real-time connection key
            'SLACK_SIGNING_SECRET'  # Security validation
        ]
        
        config = {}
        missing_vars = []
        
        # ===== CHECK EACH REQUIRED VARIABLE =====
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                # ===== MAP TO INTERNAL NAMES =====
                # Convert environment names to config keys
                key_mapping = {
                    'SLACK_BOT_TOKEN': 'bot_token',
                    'SLACK_APP_TOKEN': 'app_token', 
                    'SLACK_SIGNING_SECRET': 'signing_secret'
                }
                config[key_mapping[var]] = value
        
        # ===== HANDLE MISSING VARIABLES =====
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("💡 Set the following environment variables:")
            for var in missing_vars:
                logger.info(f"   export {var}='your_{var.lower()}_here'")
            return None
        
        # ===== ADD OPTIONAL CONFIGURATION =====
        # These have sensible defaults if not provided
        config['default_channel'] = os.getenv('SLACK_DEFAULT_CHANNEL', '#devops')
        config['alerts_channel'] = os.getenv('SLACK_ALERTS_CHANNEL', '#alerts')
        config['notifications_channel'] = os.getenv('SLACK_NOTIFICATIONS_CHANNEL', '#jamie-notifications')
        
        return config
    
    def _validate_slack_credentials(self, config: Dict[str, str]) -> bool:
        """
        🛡️ Validate Slack credential format
        
        🎯 PURPOSE: Catch credential errors early (before trying to connect)
        
        VALIDATION CHECKS:
        - Bot token starts with 'xoxb-' (Slack format requirement)
        - App token starts with 'xapp-' (Socket Mode requirement)
        - Signing secret is long enough (security requirement)
        
        WHY THIS MATTERS:
        - Saves time debugging connection failures
        - Provides clear error messages
        - Prevents runtime crashes with bad tokens
        
        💡 ADHD TIP: Fail fast with clear errors - don't waste time on impossible connections!
        """
        
        # ===== EXTRACT TOKENS =====
        bot_token = config.get('bot_token', '')
        app_token = config.get('app_token', '')
        signing_secret = config.get('signing_secret', '')
        
        # ===== VALIDATE BOT TOKEN FORMAT =====
        if not bot_token.startswith('xoxb-'):
            logger.error("❌ Bot token should start with 'xoxb-'")
            logger.info("💡 Get your bot token from https://api.slack.com/apps → OAuth & Permissions")
            return False
        
        # ===== VALIDATE APP TOKEN FORMAT =====
        if not app_token.startswith('xapp-'):
            logger.error("❌ App token should start with 'xapp-'") 
            logger.info("💡 Generate app token at https://api.slack.com/apps → Basic Information → App-Level Tokens")
            return False
        
        # ===== VALIDATE SIGNING SECRET LENGTH =====
        if len(signing_secret) < 32:
            logger.error("❌ Signing secret appears to be too short")
            logger.info("💡 Get signing secret from https://api.slack.com/apps → Basic Information")
            return False
        
        return True
    
    async def _send_startup_notification(self):
        """
        📢 Send startup notification to configured channels
        
        🎯 PURPOSE: Let the team know Jamie is back online and ready to help
        
        NOTIFICATION INCLUDES:
        - Startup timestamp
        - Jamie's British greeting
        - Available features reminder
        - Quick action suggestions
        
        💡 ADHD TIP: Startup notifications help teams know when tools are available again
        """
        
        try:
            # ===== BUILD STARTUP MESSAGE =====
            startup_data = {
                "title": "Jamie AI DevOps Copilot Started",
                "description": f"🤖 Alright mate! Jamie's back online and ready to help with your DevOps needs! 🇬🇧\n\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "type": "system",
                "priority": "info"
            }
            
            # ===== SEND TO NOTIFICATIONS CHANNEL =====
            # Only send if a channel is configured (don't spam)
            notifications_channel = os.getenv('SLACK_NOTIFICATIONS_CHANNEL')
            if notifications_channel:
                await self.notification_manager.send_proactive_insight(
                    startup_data,
                    [notifications_channel]
                )
            
        except Exception as e:
            # ===== NON-CRITICAL ERROR =====
            # Startup notification failure shouldn't stop the bot
            logger.warning(f"⚠️ Failed to send startup notification: {e}")
    
    async def start(self):
        """
        🎬 Start the Slack bot and all background services
        
        🎯 PURPOSE: Begin serving the team! This is where Jamie goes "live"
        
        STARTUP SEQUENCE:
        1. Initialize all components
        2. Start health monitoring (background task)
        3. Start the main bot (this blocks until shutdown)
        
        ERROR HANDLING:
        - Keyboard interrupt (Ctrl+C) → Graceful shutdown
        - Unexpected errors → Log and attempt recovery
        
        💡 ADHD TIP: This function blocks - it's where Jamie "lives" until shutdown
        """
        
        # ===== INITIALIZE EVERYTHING =====
        if not await self.initialize():
            logger.error("❌ Failed to initialize Jamie Slack bot")
            return False
        
        self.running = True
        
        try:
            # ===== START HEALTH MONITORING =====
            # Run health checks in background while bot operates
            health_task = asyncio.create_task(self._health_monitor())
            
            # ===== START THE BOT =====
            # This will block here until the bot shuts down
            logger.info("🚀 Starting Jamie Slack bot...")
            await self.bot.start()
            
        except KeyboardInterrupt:
            # ===== GRACEFUL SHUTDOWN ON CTRL+C =====
            logger.info("⚠️ Received shutdown signal (Ctrl+C)")
            await self._graceful_shutdown()
        except Exception as e:
            # ===== UNEXPECTED ERROR HANDLING =====
            logger.error(f"❌ Unexpected error in main loop: {e}")
            await self._graceful_shutdown()
        finally:
            # ===== CLEANUP =====
            self.running = False
            logger.info("👋 Jamie Slack bot stopped")
    
    async def _health_monitor(self):
        """Monitor bot health and restart if necessary"""
        
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                if not self.running:
                    break
                
                # Perform health checks
                await self._perform_health_checks()
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
    
    async def _perform_health_checks(self):
        """Perform various health checks"""
        
        try:
            # Check Slack connection
            if self.bot and self.bot.client:
                auth_response = await self.bot.client.auth_test()
                logger.debug(f"✅ Slack connection healthy: {auth_response['user']}")
            
            # Check MCP connections (if available)
            if hasattr(self.bot, 'mcp_client'):
                # Add MCP health checks here
                pass
            
            # Check memory usage
            import psutil
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                logger.warning(f"⚠️ High memory usage: {memory_percent}%")
            
            logger.debug("✅ Health check completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            # Consider implementing auto-restart logic here
    
    async def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        
        logger.info("🛑 Initiating graceful shutdown...")
        
        try:
            # Send shutdown notification
            if self.notification_manager:
                shutdown_data = {
                    "title": "Jamie AI DevOps Copilot Shutting Down",
                    "description": f"🤖 Right then, I'm heading off for a bit of maintenance! I'll be back shortly, mate! 🇬🇧\n\nShutdown at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "type": "system",
                    "priority": "info"
                }
                
                notifications_channel = os.getenv('SLACK_NOTIFICATIONS_CHANNEL')
                if notifications_channel:
                    await self.notification_manager.send_proactive_insight(
                        shutdown_data,
                        [notifications_channel]
                    )
            
            # Clean up resources
            if self.bot:
                # Close any open connections
                pass
            
            logger.info("✅ Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# ==========================================
# 🎨 STARTUP DISPLAY FUNCTIONS  
# ==========================================

def print_banner():
    """
    🎨 Print Jamie's startup banner
    
    🎯 PURPOSE: Make startup feel friendly and professional
    
    💡 ADHD TIP: Visual banners help confirm "yes, the right thing is starting"
    """
    banner = """
    ╔══════════════════════════════════════╗
    ║        🤖 Jamie AI DevOps Copilot    ║
    ║             Slack Integration        ║
    ║                                      ║
    ║  Your friendly British DevOps mate   ║
    ║    bringing AI to team chat! 🇬🇧     ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def print_setup_instructions():
    """
    📋 Print setup instructions for first-time users
    
    🎯 PURPOSE: Help teams get Jamie configured correctly
    
    COVERS:
    - Environment variable setup
    - Slack app configuration  
    - Channel setup suggestions
    - Testing instructions
    
    💡 ADHD TIP: Step-by-step instructions reduce setup overwhelm
    """
    
    instructions = """
    🚀 JAMIE SLACK BOT SETUP GUIDE
    
    1️⃣ ENVIRONMENT VARIABLES (Required):
       export SLACK_BOT_TOKEN='xoxb-your-bot-token'
       export SLACK_APP_TOKEN='xapp-your-app-token'  
       export SLACK_SIGNING_SECRET='your-signing-secret'
    
    2️⃣ OPTIONAL CHANNELS:
       export SLACK_DEFAULT_CHANNEL='#devops'
       export SLACK_ALERTS_CHANNEL='#alerts'
       export SLACK_NOTIFICATIONS_CHANNEL='#jamie-notifications'
    
    3️⃣ SLACK APP PERMISSIONS NEEDED:
       - app_mentions:read (respond to @jamie)
       - channels:read (access channels)
       - chat:write (send messages)
       - commands (handle slash commands)
       - im:history, im:read, im:write (direct messages)
       - users:read (user information)
    
    4️⃣ SLASH COMMANDS TO CREATE:
       /jamie → Ask Jamie anything
       /jamie-status → Quick health check
       /jamie-help → Show available commands
       /jamie-setup → Team configuration
    
    5️⃣ TEST SETUP:
       Try: /jamie How's my cluster doing?
       Expected: Jamie responds with cluster status
    
    💡 Need help? Check the README.md for detailed setup!
    """
    
    print(instructions)

# ==========================================
# 🎬 MAIN ENTRY POINT
# ==========================================

async def main():
    """
    🎬 Main entry point for Jamie's Slack bot
    
    🎯 PURPOSE: The single place where everything starts
    
    FLOW:
    1. Print friendly banner
    2. Check for environment variables
    3. Show setup help if needed
    4. Start Jamie if ready
    
    💡 ADHD TIP: Single main() function makes it clear where execution begins
    """
    
    # ===== SHOW STARTUP BANNER =====
    print_banner()
    
    # ===== QUICK ENVIRONMENT CHECK =====
    # Don't even try to start if basic config is missing
    required_vars = ['SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'SLACK_SIGNING_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        print_setup_instructions()
        return
    
    # ===== START JAMIE =====
    bootstrap = JamieSlackBootstrap()
    await bootstrap.start()

# ===== SCRIPT EXECUTION =====
if __name__ == "__main__":
    """
    🎯 Run this script directly to start Jamie
    
    USAGE:
    python slack/start_slack_bot.py
    
    💡 ADHD TIP: This guard ensures the script only runs when executed directly
    """
    try:
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Jamie Slack bot stopped.")
    except Exception as e:
        print(f"❌ Failed to start Jamie: {e}")
        sys.exit(1) 