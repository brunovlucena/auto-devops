#!/usr/bin/env python3
"""
🤖 Test script for Jamie AI DevOps Copilot

Quick test to verify Jamie is working correctly
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the api directory to the Python path
sys.path.append(str(Path(__file__).parent / "api"))

from personality import JamiePersonality
from models.conversation import ConversationManager
from tools.mcp_client import MCPClient

async def test_jamie_components():
    """Test all Jamie components"""
    print("🤖 Testing Jamie AI DevOps Copilot")
    print("=" * 50)
    
    # Test 1: Personality System
    print("\n1. Testing Jamie's Personality...")
    jamie = JamiePersonality()
    
    print(f"   Greeting: {jamie.get_greeting()}")
    print(f"   Success: {jamie.get_success_response()}")
    print(f"   Error: {jamie.get_error_response()}")
    print(f"   Thinking: {jamie.get_thinking_phrase()}")
    print(f"   Time greeting: {jamie.get_time_appropriate_greeting()}")
    print(f"   Contextual: {jamie.get_contextual_response('kubernetes', 'healthy')}")
    
    # Test user emotion response
    print(f"   Emotion response (broken): {jamie.respond_to_user_emotion('My cluster is broken!')}")
    print(f"   Emotion response (happy): {jamie.respond_to_user_emotion('Everything looks great!')}")
    
    print("   ✅ Personality system working!")
    
    # Test 2: Conversation Manager
    print("\n2. Testing Conversation Management...")
    conv_manager = ConversationManager()
    
    # Add test messages
    conv_manager.add_message("test_session", "user123", "How's my cluster?", True)
    conv_manager.add_message("test_session", "user123", "Your cluster's running like a dream, mate!", False)
    conv_manager.add_message("test_session", "user123", "Any alerts firing?", True)
    
    # Get context
    context = conv_manager.get_conversation_context("test_session")
    print(f"   Session context: {json.dumps(context, indent=2)}")
    
    # Get recent context
    recent = conv_manager.get_recent_context("test_session", 2)
    print(f"   Recent context: {recent}")
    
    # Test intent detection
    intent = conv_manager.detect_user_intent("Show me errors from the auth service", "test_session")
    print(f"   Intent detection: {json.dumps(intent, indent=2)}")
    
    print("   ✅ Conversation management working!")
    
    # Test 3: MCP Client
    print("\n3. Testing MCP Client...")
    mcp_client = MCPClient()
    
    # Test server status
    status = mcp_client.get_server_status()
    print(f"   Server status: {json.dumps(status, indent=2)}")
    
    # Test connection
    await mcp_client.connect_to_servers()
    print("   ✅ MCP client initialized!")
    
    # Test 4: Integration Test
    print("\n4. Testing Component Integration...")
    
    # Simulate a conversation flow
    user_message = "How's my cluster doing?"
    session_id = "integration_test"
    user_id = "test_user"
    
    # Add user message
    conv_manager.add_message(session_id, user_id, user_message, True)
    
    # Detect intent
    intent = conv_manager.detect_user_intent(user_message, session_id)
    print(f"   User intent: {intent['primary_intent']}, topics: {intent['topics']}")
    
    # Generate Jamie's response
    if intent['primary_intent'] == 'query' and 'kubernetes' in intent['topics']:
        jamie_response = (
            jamie.get_thinking_phrase() + 
            " Right, let me check your cluster status... " +
            jamie.get_contextual_response('kubernetes', 'healthy')
        )
    else:
        jamie_response = jamie.get_general_response() + " What would you like to know?"
    
    # Add Jamie's response
    conv_manager.add_message(session_id, user_id, jamie_response, False)
    
    print(f"   Jamie's response: {jamie_response}")
    
    # Get conversation summary
    summary = conv_manager.get_conversation_summary(session_id)
    print(f"   Conversation summary: Total messages: {summary['total_messages']}")
    
    print("   ✅ Integration test successful!")
    
    print("\n🎉 All tests passed! Jamie is ready to help with DevOps!")
    print("\n📝 Next steps:")
    print("   - Run: uvicorn api.main:app --reload --port 8000")
    print("   - Test API: curl http://localhost:8000/")
    print("   - Chat with Jamie: POST http://localhost:8000/chat")
    
    return True

def test_personality_expressions():
    """Test Jamie's personality expressions"""
    print("\n🎭 Jamie's Personality Showcase")
    print("=" * 40)
    
    jamie = JamiePersonality()
    
    print("Greetings:")
    for i in range(3):
        print(f"  - {jamie.get_greeting()}")
    
    print("\nSuccess expressions:")
    for i in range(3):
        print(f"  - {jamie.get_success_response()}")
    
    print("\nError expressions:")
    for i in range(3):
        print(f"  - {jamie.get_error_response()}")
    
    print("\nThinking phrases:")
    for i in range(3):
        print(f"  - {jamie.get_thinking_phrase()}")
    
    print("\nContextual responses:")
    contexts = [
        ("kubernetes", "healthy"), ("kubernetes", "issues"),
        ("monitoring", "alerts"), ("logs", "errors"),
        ("deployment", "success")
    ]
    for context, situation in contexts:
        response = jamie.get_contextual_response(context, situation)
        print(f"  - {context}/{situation}: {response}")

if __name__ == "__main__":
    try:
        # Run personality showcase
        test_personality_expressions()
        
        # Run async component tests
        asyncio.run(test_jamie_components())
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 