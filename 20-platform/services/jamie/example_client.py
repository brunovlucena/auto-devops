#!/usr/bin/env python3
"""
🤖 Jamie AI DevOps Copilot - Example Client

Demonstrates how to interact with Jamie's API and WebSocket
"""

import asyncio
import json
import sys
import httpx
import websockets
from datetime import datetime

class JamieClient:
    """
    Example client for interacting with Jamie AI DevOps Copilot
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.user_id = "example_user"
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    async def check_health(self):
        """Check Jamie's health status"""
        print("🔍 Checking Jamie's health...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✅ Jamie is {health_data['status']}")
                    print(f"   Message: {health_data['message']}")
                    print(f"   AI Status: {health_data['ai_status']}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to Jamie: {str(e)}")
            return False

    async def send_chat_message(self, message: str):
        """Send a message via REST API"""
        print(f"\n💬 Sending message via REST API...")
        print(f"User: {message}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": message,
                        "user_id": self.user_id,
                        "session_id": self.session_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Jamie: {data['response']}")
                    print(f"Confidence: {data.get('confidence', 'N/A')}")
                    print(f"Intent: {data.get('intent', 'N/A')}")
                    print(f"Topics: {data.get('topics', [])}")
                    return data
                else:
                    print(f"❌ Chat failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return None

    async def websocket_chat(self, messages: list):
        """Interactive chat via WebSocket"""
        print(f"\n🌐 Starting WebSocket chat session...")
        
        try:
            async with websockets.connect(f"{self.ws_url}/ws/{self.user_id}") as websocket:
                # Receive initial greeting
                greeting = await websocket.recv()
                greeting_data = json.loads(greeting)
                print(f"Jamie: {greeting_data}")
                
                # Send messages
                for message in messages:
                    print(f"\nUser: {message}")
                    
                    # Send message
                    await websocket.send(json.dumps({
                        "message": message,
                        "session_id": self.session_id
                    }))
                    
                    # Receive response
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "message":
                        print(f"Jamie: {response_data['response']}")
                        print(f"Confidence: {response_data.get('confidence', 'N/A')}")
                        print(f"Intent: {response_data.get('intent', 'N/A')}")
                    
                    # Small delay between messages
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"❌ WebSocket error: {str(e)}")

    async def check_ai_status(self):
        """Check AI system status"""
        print("\n🧠 Checking AI system status...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/ai/status")
                if response.status_code == 200:
                    ai_status = response.json()
                    print(f"AI Brain: {'✅ Active' if ai_status['brain']['available'] else '❌ Inactive'}")
                    print(f"Vector Memory: {'✅ Active' if ai_status['memory']['available'] else '❌ Inactive'}")
                    print(f"Model: {ai_status['brain'].get('model', 'N/A')}")
                    return ai_status
                else:
                    print(f"❌ AI status check failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"❌ Error checking AI status: {str(e)}")
            return None

    async def run_demo(self):
        """Run a complete demo of Jamie's capabilities"""
        print("🤖 Jamie AI DevOps Copilot - Demo Client")
        print("=" * 50)
        
        # Check health
        if not await self.check_health():
            print("❌ Jamie is not available. Make sure it's running on http://localhost:8000")
            return
        
        # Check AI status
        await self.check_ai_status()
        
        # Demo REST API
        print("\n" + "=" * 50)
        print("📡 REST API Demo")
        print("=" * 50)
        
        demo_messages = [
            "Hello Jamie!",
            "How are my pods doing?",
            "My deployment is failing, can you help?",
            "What can you help me with?"
        ]
        
        for message in demo_messages:
            await self.send_chat_message(message)
            await asyncio.sleep(1)
        
        # Demo WebSocket
        print("\n" + "=" * 50)
        print("🌐 WebSocket Demo")
        print("=" * 50)
        
        ws_messages = [
            "Can you check my Kubernetes cluster?",
            "Any alerts I should know about?",
            "Show me recent errors in the logs",
            "Thanks Jamie!"
        ]
        
        await self.websocket_chat(ws_messages)
        
        print("\n✅ Demo completed!")

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        client = JamieClient()
        
        if command == "health":
            await client.check_health()
        elif command == "ai-status":
            await client.check_ai_status()
        elif command == "chat":
            if len(sys.argv) > 2:
                message = " ".join(sys.argv[2:])
                await client.send_chat_message(message)
            else:
                print("Usage: python example_client.py chat <message>")
        elif command == "demo":
            await client.run_demo()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: health, ai-status, chat, demo")
    else:
        # Interactive mode
        client = JamieClient()
        
        print("🤖 Jamie AI DevOps Copilot - Interactive Client")
        print("=" * 50)
        print("Commands:")
        print("  demo        - Run full demo")
        print("  health      - Check health")
        print("  ai-status   - Check AI status")
        print("  chat <msg>  - Send chat message")
        print("  exit        - Exit")
        print()
        
        while True:
            try:
                user_input = input("👤 Command: ").strip()
                
                if user_input == "exit":
                    print("👋 Goodbye!")
                    break
                elif user_input == "demo":
                    await client.run_demo()
                elif user_input == "health":
                    await client.check_health()
                elif user_input == "ai-status":
                    await client.check_ai_status()
                elif user_input.startswith("chat "):
                    message = user_input[5:]  # Remove "chat "
                    await client.send_chat_message(message)
                elif user_input:
                    # Treat as direct chat message
                    await client.send_chat_message(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 