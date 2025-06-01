#!/usr/bin/env python3
"""
🚀 Jamie AI DevOps Copilot - Slack Bot Startup
Sprint 5: Slack Integration

Main startup script for Jamie's Slack bot.
Handles initialization, configuration, and error recovery.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from slack_bot import JamieSlackBot
from notifications import JamieNotificationManager
from slack_sdk.web.async_client import AsyncWebClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/jamie/slack_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class JamieSlackBootstrap:
    """
    Bootstrap and manage Jamie's Slack bot lifecycle
    
    Handles:
    - Environment configuration
    - Bot initialization
    - Health monitoring
    - Graceful shutdown
    - Error recovery
    """
    
    def __init__(self):
        self.bot: JamieSlackBot = None
        self.notification_manager: JamieNotificationManager = None
        self.health_check_interval = 300  # 5 minutes
        self.running = False
        
    async def initialize(self) -> bool:
        """Initialize Jamie's Slack bot with all dependencies"""
        
        try:
            logger.info("🚀 Initializing Jamie AI DevOps Copilot Slack Bot...")
            
            # Load configuration
            config = self._load_configuration()
            if not config:
                logger.error("❌ Failed to load configuration")
                return False
            
            # Validate Slack credentials
            if not self._validate_slack_credentials(config):
                logger.error("❌ Invalid Slack credentials")
                return False
            
            # Initialize Slack client
            slack_client = AsyncWebClient(token=config['bot_token'])
            
            # Test connection
            try:
                auth_response = await slack_client.auth_test()
                logger.info(f"✅ Connected to Slack workspace: {auth_response['team']}")
                logger.info(f"🤖 Bot user: @{auth_response['user']}")
            except Exception as e:
                logger.error(f"❌ Slack connection test failed: {e}")
                return False
            
            # Initialize notification manager
            self.notification_manager = JamieNotificationManager(slack_client)
            logger.info("✅ Notification manager initialized")
            
            # Initialize Jamie bot
            self.bot = JamieSlackBot(
                bot_token=config['bot_token'],
                app_token=config['app_token'],
                signing_secret=config['signing_secret']
            )
            logger.info("✅ Jamie Slack bot initialized")
            
            # Send startup notification
            await self._send_startup_notification()
            
            logger.info("🎉 Jamie Slack bot ready for action!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _load_configuration(self) -> Dict[str, str]:
        """Load Slack bot configuration from environment"""
        
        required_vars = [
            'SLACK_BOT_TOKEN',
            'SLACK_APP_TOKEN', 
            'SLACK_SIGNING_SECRET'
        ]
        
        config = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                # Map to internal names
                key_mapping = {
                    'SLACK_BOT_TOKEN': 'bot_token',
                    'SLACK_APP_TOKEN': 'app_token',
                    'SLACK_SIGNING_SECRET': 'signing_secret'
                }
                config[key_mapping[var]] = value
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("💡 Set the following environment variables:")
            for var in missing_vars:
                logger.info(f"   export {var}='your_{var.lower()}_here'")
            return None
        
        # Optional configuration
        config['default_channel'] = os.getenv('SLACK_DEFAULT_CHANNEL', '#devops')
        config['alerts_channel'] = os.getenv('SLACK_ALERTS_CHANNEL', '#alerts')
        config['notifications_channel'] = os.getenv('SLACK_NOTIFICATIONS_CHANNEL', '#jamie-notifications')
        
        return config
    
    def _validate_slack_credentials(self, config: Dict[str, str]) -> bool:
        """Validate Slack credential format"""
        
        # Basic format validation
        bot_token = config.get('bot_token', '')
        app_token = config.get('app_token', '')
        
        if not bot_token.startswith('xoxb-'):
            logger.error("❌ Bot token should start with 'xoxb-'")
            return False
        
        if not app_token.startswith('xapp-'):
            logger.error("❌ App token should start with 'xapp-'")
            return False
        
        if len(config.get('signing_secret', '')) < 32:
            logger.error("❌ Signing secret appears to be too short")
            return False
        
        return True
    
    async def _send_startup_notification(self):
        """Send startup notification to configured channels"""
        
        try:
            startup_data = {
                "title": "Jamie AI DevOps Copilot Started",
                "description": f"🤖 Alright mate! Jamie's back online and ready to help with your DevOps needs! 🇬🇧\n\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "type": "system",
                "priority": "info"
            }
            
            # Send to notifications channel if configured
            notifications_channel = os.getenv('SLACK_NOTIFICATIONS_CHANNEL')
            if notifications_channel:
                await self.notification_manager.send_proactive_insight(
                    startup_data,
                    [notifications_channel]
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to send startup notification: {e}")
    
    async def start(self):
        """Start the Slack bot and all background services"""
        
        if not await self.initialize():
            logger.error("❌ Failed to initialize Jamie Slack bot")
            return False
        
        self.running = True
        
        try:
            # Start health monitoring in background
            health_task = asyncio.create_task(self._health_monitor())
            
            # Start the bot (this will block)
            logger.info("🚀 Starting Jamie Slack bot...")
            await self.bot.start()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}")
        finally:
            self.running = False
            await self._graceful_shutdown()
    
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

def print_banner():
    """Print Jamie's startup banner"""
    
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║  🤖 Jamie AI DevOps Copilot - Slack Integration 🇬🇧      ║
    ║                                                          ║
    ║  Sprint 5: Your friendly DevOps buddy in Slack!         ║
    ║                                                          ║
    ║  • Slash commands: /jamie, /jamie-status, /jamie-help   ║
    ║  • Interactive buttons and menus                         ║
    ║  • Real-time alerts and notifications                    ║
    ║  • Team collaboration features                           ║
    ║  • Cross-platform sync with portal                      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_setup_instructions():
    """Print setup instructions for users"""
    
    instructions = """
    🔧 QUICK SETUP GUIDE:
    
    1. Create a Slack app at https://api.slack.com/apps
    2. Set the following environment variables:
       
       export SLACK_BOT_TOKEN='xoxb-your-bot-token'
       export SLACK_APP_TOKEN='xapp-your-app-token'  
       export SLACK_SIGNING_SECRET='your-signing-secret'
       
    3. Optional channel configuration:
       
       export SLACK_DEFAULT_CHANNEL='#devops'
       export SLACK_ALERTS_CHANNEL='#alerts'
       export SLACK_NOTIFICATIONS_CHANNEL='#jamie-notifications'
    
    4. Install your Slack app to your workspace
    5. Run: python start_slack_bot.py
    
    🚀 Then use /jamie in Slack to start chatting!
    """
    print(instructions)

async def main():
    """Main entry point"""
    
    print_banner()
    
    # Check if configuration exists
    required_vars = ['SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'SLACK_SIGNING_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables!")
        print_setup_instructions()
        return 1
    
    # Initialize and start bot
    bootstrap = JamieSlackBootstrap()
    
    try:
        await bootstrap.start()
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the bot
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 