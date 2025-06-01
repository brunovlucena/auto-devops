#!/usr/bin/env python3
"""
🚀 Jamie AI DevOps Copilot - Startup Script

Handles dependency checks and service startup for Sprint 2
"""

import asyncio
import subprocess
import sys
import os
import time
import httpx
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JamieStarter:
    """
    Jamie startup manager for Sprint 2
    """
    
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.jamie_model = os.getenv("JAMIE_MODEL", "llama3.1:8b")
        self.jamie_port = int(os.getenv("JAMIE_PORT", "8000"))
        
        logger.info("🤖 Jamie AI DevOps Copilot - Sprint 2 Startup")
        logger.info("=" * 50)

    async def check_dependencies(self):
        """Check if all required dependencies are available"""
        logger.info("🔍 Checking dependencies...")
        
        # Check Python packages
        try:
            import fastapi
            import uvicorn
            import httpx
            import numpy
            logger.info("  ✅ Python packages installed")
        except ImportError as e:
            logger.error(f"  ❌ Missing Python package: {e}")
            logger.info("  💡 Run: pip install -r requirements.txt")
            return False
        
        # Check Ollama availability
        ollama_available = await self.check_ollama()
        if not ollama_available:
            logger.warning("  ⚠️ Ollama not available - Jamie will run in basic mode")
        
        return True

    async def check_ollama(self):
        """Check if Ollama is running and has the required model"""
        try:
            async with httpx.AsyncClient() as client:
                # Check if Ollama is running
                response = await client.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json()
                    available_models = [model["name"] for model in models.get("models", [])]
                    
                    if self.jamie_model in available_models:
                        logger.info(f"  ✅ Ollama running with model '{self.jamie_model}'")
                        return True
                    else:
                        logger.warning(f"  ⚠️ Model '{self.jamie_model}' not found")
                        logger.info(f"  💡 Available models: {available_models}")
                        return await self.pull_model()
                else:
                    logger.warning(f"  ⚠️ Ollama not responding at {self.ollama_host}")
                    return False
        except Exception as e:
            logger.warning(f"  ⚠️ Cannot connect to Ollama: {str(e)}")
            logger.info("  💡 Start Ollama with: ollama serve")
            return False

    async def pull_model(self):
        """Pull the required model from Ollama"""
        try:
            logger.info(f"📥 Pulling model '{self.jamie_model}' from Ollama...")
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/pull",
                    json={"name": self.jamie_model}
                )
                if response.status_code == 200:
                    logger.info(f"  ✅ Successfully pulled model '{self.jamie_model}'")
                    return True
                else:
                    logger.error(f"  ❌ Failed to pull model: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"  ❌ Error pulling model: {str(e)}")
            return False

    def create_memory_directory(self):
        """Create Jamie's memory directory"""
        memory_dir = Path("./jamie_memory")
        memory_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Memory directory ready: {memory_dir.absolute()}")

    async def start_jamie(self):
        """Start Jamie's API server"""
        logger.info(f"🚀 Starting Jamie on port {self.jamie_port}...")
        
        # Create memory directory
        self.create_memory_directory()
        
        # Start the server
        try:
            import uvicorn
            from api.main import app
            
            logger.info("🎉 Jamie is ready to help with DevOps!")
            logger.info(f"   💬 Chat API: http://localhost:{self.jamie_port}/")
            logger.info(f"   📊 Health Check: http://localhost:{self.jamie_port}/health")
            logger.info(f"   📚 API Docs: http://localhost:{self.jamie_port}/docs")
            logger.info(f"   🔌 WebSocket: ws://localhost:{self.jamie_port}/ws/your_user_id")
            
            # Run the server
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=self.jamie_port,
                log_level="info"
            )
            
        except KeyboardInterrupt:
            logger.info("👋 Jamie shutting down...")
        except Exception as e:
            logger.error(f"❌ Error starting Jamie: {str(e)}")

    def print_help(self):
        """Print help information"""
        print("""
🤖 Jamie AI DevOps Copilot - Sprint 2

Usage:
  python start_jamie.py [options]

Options:
  --help, -h        Show this help message
  --check-deps      Only check dependencies, don't start
  --docker          Start with Docker Compose

Environment Variables:
  OLLAMA_HOST       Ollama server URL (default: http://localhost:11434)
  JAMIE_MODEL       LLM model to use (default: llama3.1:8b)
  JAMIE_PORT        Port to run Jamie on (default: 8000)

Examples:
  python start_jamie.py                 # Start Jamie normally
  python start_jamie.py --check-deps    # Check dependencies only
  python start_jamie.py --docker        # Start with Docker

Prerequisites:
  1. Install dependencies: pip install -r requirements.txt
  2. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh
  3. Start Ollama: ollama serve
  4. Pull model: ollama pull llama3.1:8b

For Docker:
  docker-compose up --build
        """)

async def main():
    """Main startup function"""
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        JamieStarter().print_help()
        return
    
    starter = JamieStarter()
    
    if "--docker" in args:
        logger.info("🐳 Starting Jamie with Docker Compose...")
        try:
            subprocess.run(["docker-compose", "up", "--build"], check=True)
        except subprocess.CalledProcessError:
            logger.error("❌ Docker Compose failed. Make sure Docker is installed and running.")
        return
    
    # Check dependencies
    deps_ok = await starter.check_dependencies()
    
    if "--check-deps" in args:
        if deps_ok:
            logger.info("✅ All dependencies check passed!")
        else:
            logger.error("❌ Dependency check failed!")
        return
    
    if deps_ok:
        await starter.start_jamie()
    else:
        logger.error("❌ Cannot start Jamie due to missing dependencies")
        logger.info("💡 Run with --help for setup instructions")

if __name__ == "__main__":
    asyncio.run(main()) 