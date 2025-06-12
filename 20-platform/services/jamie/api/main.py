"""
🤖 Jamie: AI DevOps Copilot - Enhanced with AI Brain

Sprint 2: AI Brain & Memory Integration
Your friendly IT buddy meets AI-powered automation

⭐ WHAT THIS FILE DOES:
    - Main FastAPI web server for Jamie
    - Handles chat messages via HTTP and WebSocket
    - Integrates with MongoDB RAG system for knowledge
    - Provides health checks and AI status monitoring
    - Connects to DevOps tools via MCP (Model Context Protocol)
    - Serves as the central hub for all Jamie interactions
    - Enhanced with comprehensive observability (metrics, tracing, logging)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
import asyncio
from fastapi.responses import JSONResponse

# Import Jamie's components
from .personality import JamiePersonality
from .models.conversation import ConversationManager
from .tools.mcp_client import MCPClient
from .ai.brain import JamieBrain
from .ai.rag_memory import MongoRAGMemory

# Import observability components
from .observability import (
    initialize_observability, 
    setup_fastapi_observability,
    jamie_metrics,
    trace_endpoint,
    measure_time,
    get_correlation_id,
    set_correlation_id
)
from loguru import logger

# Import config for observability setup
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 SETUP AND CONFIGURATION - Basic app initialization
# ═══════════════════════════════════════════════════════════════════════════════

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
# Note: Using loguru logger imported above, not standard logging

# 🚀 Initialize FastAPI app with metadata
app = FastAPI(
    title="Jamie - AI DevOps Copilot",
    description="Your friendly IT buddy meets AI-powered automation - The personable face of DevOps",
    version="2.0.0",  # Sprint 2 with RAG enhancement
)

# 🌐 Configure CORS (Cross-Origin Resource Sharing)
# This allows web browsers to connect to Jamie from different domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 INITIALIZE JAMIE'S COMPONENTS - Set up all the AI systems
# ═══════════════════════════════════════════════════════════════════════════════

# 🎭 PERSONALITY SYSTEM - Jamie's British charm
jamie_personality = JamiePersonality()

# 💬 CONVERSATION MANAGEMENT - Track chat sessions and history
conversation_manager = ConversationManager()

# 🔌 MCP CLIENT - Connect to DevOps tools (Kubernetes, Prometheus, etc.)
mcp_client = MCPClient()

# 🧠 AI BRAIN - Enhanced with RAG (includes MongoDB knowledge base)
ai_brain = JamieBrain()  # This now includes RAG memory

# 🗄️ RAG MEMORY - Direct reference for backward compatibility
rag_memory = None  # Will be set to ai_brain.rag_memory after initialization

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 DATA MODELS - Define request/response structures
# ═══════════════════════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    """📝 Structure for incoming chat messages"""
    message: str                                    # What the user said
    user_id: str = "default"                       # Who sent it
    session_id: str = "default"                    # Which conversation
    context: Optional[Dict[str, Any]] = None       # Extra info (namespace, etc.)

class ChatResponse(BaseModel):
    """📤 Structure for Jamie's responses"""
    response: str                                   # Jamie's reply
    timestamp: str                                  # When it was generated
    session_id: str                                # Which conversation
    confidence: Optional[float] = None             # How confident Jamie is
    topics: Optional[List[str]] = None             # What topics were discussed
    intent: Optional[str] = None                   # What the user wanted

class HealthCheck(BaseModel):
    """🏥 Structure for health check responses"""
    status: str                                     # "healthy" or "degraded"
    message: str                                    # Human-readable status
    timestamp: str                                  # When the check was done
    ai_status: Dict[str, Any]                      # Detailed AI system status

# ═══════════════════════════════════════════════════════════════════════════════
# 💬 WEBSOCKET CONNECTION MANAGER - Handle real-time chat
# ═══════════════════════════════════════════════════════════════════════════════

class ConnectionManager:
    """
    🔗 Manage WebSocket connections for real-time chat
    
    WHAT IT DOES:
    - Keep track of who's connected
    - Send messages to specific users
    - Handle connections and disconnections
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """✅ Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """❌ Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """📤 Send message to specific WebSocket connection"""
        await websocket.send_text(message)

# 🌐 Create global connection manager
manager = ConnectionManager()

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 STARTUP AND SHUTDOWN - Initialize and cleanup systems
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 MIDDLEWARE SETUP - Must be done before startup
# ═══════════════════════════════════════════════════════════════════════════════

# Initialize observability middleware (must be done before startup)
if config.METRICS_ENABLED:
    from prometheus_fastapi_instrumentator import Instrumentator
    instrumentator = Instrumentator()
    instrumentator.instrument(app)

@app.on_event("startup")
async def startup_event():
    """
    🚀 Initialize Jamie's AI components and observability on startup
    
    STARTUP SEQUENCE:
    1. Initialize observability (logging, tracing, metrics)
    2. Setup FastAPI observability features
    3. Initialize AI brain (includes RAG memory system)
    4. Set up backward compatibility references
    5. Log startup status
    """
    global rag_memory
    
    # 📊 STEP 1: Initialize observability first
    initialize_observability()
    setup_fastapi_observability(app)
    
    logger.info(f"🚀 Starting Jamie AI DevOps Copilot... [correlation_id: {get_correlation_id()}]")
    
    # 🧠 STEP 2: Initialize AI brain with RAG capabilities
    brain_initialized = await ai_brain.initialize()
    if brain_initialized:
        logger.info(f"✅ Jamie's enhanced AI brain is ready! [ai_model: {ai_brain.model_name}]")
        # Set the rag_memory reference for backward compatibility
        rag_memory = ai_brain.rag_memory
        
        # 📊 Update system health metrics
        jamie_metrics.system_health.labels(component="ai_brain").set(1.0)
    else:
        logger.warning("⚠️ Jamie's AI brain initialization failed - running in limited mode")
        jamie_metrics.system_health.labels(component="ai_brain").set(0.5)
    
    # 📊 Track startup completion
    jamie_metrics.system_health.labels(component="api_server").set(1.0)
    
    logger.info(f"🤖 Jamie is ready to help with your DevOps challenges! [observability_enabled: True, ai_available: {brain_initialized}]")

@app.on_event("shutdown")
async def shutdown_event():
    """
    👋 Clean shutdown of Jamie's systems
    
    SHUTDOWN SEQUENCE:
    1. Disconnect from MCP servers
    2. Clean up AI systems
    3. Log shutdown completion
    """
    logger.info("👋 Shutting down Jamie AI DevOps Copilot...")
    
    try:
        # 🔌 DISCONNECT FROM MCP SERVERS
        await mcp_client.disconnect_all()
        logger.info("Disconnected from MCP servers")
        
        # 🧠 SHUTDOWN AI SYSTEMS gracefully
        if hasattr(ai_brain, 'close'):
            await ai_brain.close()
        
        logger.info("✅ Jamie shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🏥 HEALTH CHECK ENDPOINTS - Monitor Jamie's status
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_model=HealthCheck)
async def root():
    """
    🏠 Root endpoint - Basic health check with Jamie's personality
    
    WHAT IT SHOWS:
    - Basic system status
    - AI brain availability
    - Jamie's friendly greeting
    """
    # 📊 GET AI STATUS
    ai_status = {
        "brain_active": ai_brain is not None and ai_brain.is_available(),
        "vector_memory_active": rag_memory is not None and rag_memory.available,
        "llm_model": ai_brain.model_name if ai_brain else "Not available",
        "memory_collections": "Available" if rag_memory else "Not available"
    }
    
    # 🎭 GET JAMIE'S GREETING based on time of day
    greeting = jamie_personality.get_time_appropriate_greeting()
    if ai_status["brain_active"]:
        message = f"{greeting} Jamie's AI brain is running smoothly, mate! Ready to help with DevOps."
    else:
        message = f"{greeting} Jamie's API is running (basic mode) - working on getting the AI brain connected!"
    
    return HealthCheck(
        status="healthy",
        message=message,
        timestamp=datetime.now().isoformat(),
        ai_status=ai_status
    )

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    🏥 Detailed health check with AI component status
    
    COMPREHENSIVE STATUS CHECK:
    - AI brain availability
    - RAG memory system status
    - MCP server connections
    - Personality system status
    - Conversation manager status
    """
    # 📊 GATHER DETAILED STATUS
    ai_status = {
        "brain_active": ai_brain is not None and ai_brain.is_available(),
        "vector_memory_active": rag_memory is not None and rag_memory.available,
        "mcp_servers": mcp_client.get_server_status(),
        "personality_loaded": True,
        "conversation_manager_active": True
    }
    
    # 🔍 GET DETAILED AI BRAIN STATUS
    if ai_brain:
        brain_status = await ai_brain.get_health_status()
        ai_status.update(brain_status)
    
    return HealthCheck(
        status="healthy" if ai_status["brain_active"] else "degraded",
        message="All systems operational!" if ai_status["brain_active"] else "Running in basic mode",
        timestamp=datetime.now().isoformat(),
        ai_status=ai_status
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 💬 CHAT ENDPOINTS - Main conversation interfaces
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/chat", response_model=ChatResponse)
@trace_endpoint("chat_endpoint")
@measure_time("http_request_duration", {"method": "POST", "endpoint": "chat"})
async def chat_endpoint(chat_message: ChatMessage):
    """
    💬 Enhanced chat endpoint with AI brain integration
    
    CHAT PROCESS:
    1. Receive user message
    2. Store in conversation history
    3. Generate AI-enhanced response using RAG
    4. Store Jamie's response
    5. Update vector memory for learning
    6. Return formatted response
    """
    try:
        logger.info("Received chat message", 
                   user_id=chat_message.user_id,
                   session_id=chat_message.session_id,
                   message_length=len(chat_message.message),
                   correlation_id=get_correlation_id())
        
        # 📊 Track chat metrics
        jamie_metrics.chat_messages_total.labels(
            user_type="user",
            intent="unknown"  # Will be updated when we analyze intent
        ).inc()
        
        # 📝 STEP 1: Store the user's message
        conversation_manager.add_message(
            session_id=chat_message.session_id,
            user_id=chat_message.user_id,
            message=chat_message.message,
            is_user=True,
            metadata=chat_message.context
        )
        
        # 🧠 STEP 2: Generate Jamie's enhanced response
        response_data = await generate_ai_response(
            message=chat_message.message,
            user_id=chat_message.user_id,
            session_id=chat_message.session_id,
            context=chat_message.context
        )
        
        # 📊 Update metrics with response data
        if response_data.get("intent"):
            jamie_metrics.chat_messages_total.labels(
                user_type="assistant", 
                intent=response_data["intent"]
            ).inc()
            
        if response_data.get("confidence"):
            jamie_metrics.chat_response_quality.labels(
                intent=response_data.get("intent", "unknown")
            ).observe(response_data["confidence"])
        
        # 📝 STEP 3: Store Jamie's response
        conversation_manager.add_message(
            session_id=chat_message.session_id,
            user_id=chat_message.user_id,
            message=response_data["response"],
            is_user=False,
            metadata={
                "confidence": response_data.get("confidence"),
                "topics": response_data.get("topics"),
                "intent": response_data.get("intent")
            }
        )
        
        logger.info("Generated chat response",
                   response_length=len(response_data["response"]),
                   confidence=response_data.get("confidence"),
                   intent=response_data.get("intent"))
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=datetime.now().isoformat(),
            session_id=chat_message.session_id,
            confidence=response_data.get("confidence"),
            topics=response_data.get("topics"),
            intent=response_data.get("intent")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message [error: {str(e)}, user_id: {chat_message.user_id}, correlation_id: {get_correlation_id()}]")
        
        jamie_metrics.errors_total.labels(
            component="chat_endpoint",
            error_type=type(e).__name__,
            severity="error"
        ).inc()
        
        error_response = jamie_personality.get_error_response() + f" Had a bit of trouble there: {str(e)}"
        raise HTTPException(status_code=500, detail=error_response)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    🌐 Enhanced WebSocket endpoint with streaming AI responses
    
    WEBSOCKET FLOW:
    1. Accept connection and send greeting
    2. Listen for messages in a loop
    3. Generate responses using AI brain
    4. Send responses back with metadata
    5. Handle disconnections gracefully
    """
    await manager.connect(websocket)
    
    # 🎭 SEND JAMIE'S GREETING
    greeting = jamie_personality.get_time_appropriate_greeting()
    intro_message = f"{greeting} I'm Jamie, your AI DevOps copilot! "
    if ai_brain and ai_brain.is_available():
        intro_message += "My AI brain is fully loaded and ready to help with your infrastructure!"
    else:
        intro_message += "I'm running in basic mode right now, but I can still help with DevOps questions!"
    
    await manager.send_personal_message(intro_message, websocket)
    
    try:
        # 🔄 MAIN MESSAGE LOOP
        while True:
            # 📥 RECEIVE MESSAGE from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id", "ws_default")
            
            if user_message:
                logger.info(f"WebSocket message from {user_id}: {user_message}")
                
                # 🧠 GENERATE ENHANCED RESPONSE
                response_data = await generate_ai_response(
                    message=user_message,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # 📤 SEND RESPONSE BACK with metadata
                response_payload = {
                    "response": response_data["response"],
                    "timestamp": datetime.now().isoformat(),
                    "type": "message",
                    "confidence": response_data.get("confidence"),
                    "topics": response_data.get("topics"),
                    "intent": response_data.get("intent")
                }
                await manager.send_personal_message(json.dumps(response_payload), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for user {user_id}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 AI RESPONSE GENERATION - Core intelligence functions
# ═══════════════════════════════════════════════════════════════════════════════

@trace_endpoint("ai_response_generation")
@measure_time("ai_response_time", {"model": "gemini-2.0-flash", "operation": "chat"})
async def generate_ai_response(message: str, user_id: str, session_id: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    🎯 Generate Jamie's RAG-enhanced AI response
    
    INTELLIGENCE PIPELINE:
    1. Get conversation context and history
    2. Detect user intent (help, troubleshoot, query, etc.)
    3. Use enhanced AI brain with RAG for response
    4. Fallback to basic responses if AI unavailable
    
    RETURNS: Complete response with confidence and metadata
    """
    try:
        logger.info(f"Generating AI response [message_length: {len(message)}, user_id: {user_id}, session_id: {session_id}, correlation_id: {get_correlation_id()}]")
        
        # 📊 Track AI request metrics
        jamie_metrics.ai_requests_total.labels(
            model="gemini-2.0-flash",
            operation="chat",
            status="started"
        ).inc()
        
        # 📖 STEP 1: Get conversation context and history
        conversation_context = conversation_manager.get_conversation_context(session_id)
        recent_history = conversation_manager.get_recent_context(session_id, 5)
        
        # 🎯 STEP 2: Detect user intent with enhanced AI
        intent_data = conversation_manager.detect_user_intent(message, session_id)
        
        # 🧠 STEP 3: Generate response using enhanced AI brain with RAG
        if ai_brain and ai_brain.is_available():
            response_data = await ai_brain.generate_response(
                user_message=message,
                conversation_history=recent_history,
                intent=intent_data,
                devops_context={**context, "session_id": session_id} if context else {"session_id": session_id},
                personality=jamie_personality
            )
            
            # 📊 Track successful AI operation
            jamie_metrics.ai_requests_total.labels(
                model="gemini-2.0-flash",
                operation="chat", 
                status="success"
            ).inc()
            
        else:
            # 🔄 FALLBACK: Use basic response generation
            response_data = await generate_basic_response(message, intent_data, conversation_context)
            
            # 📊 Track fallback usage
            jamie_metrics.ai_requests_total.labels(
                model="fallback",
                operation="chat",
                status="fallback"
            ).inc()
        
        logger.info(f"AI response generated successfully [response_length: {len(response_data.get('response', ''))}, confidence: {response_data.get('confidence')}, intent: {response_data.get('intent')}]")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error generating AI response [error: {str(e)}, user_id: {user_id}, session_id: {session_id}, correlation_id: {get_correlation_id()}]")
        
        # 📊 Track AI errors
        jamie_metrics.ai_requests_total.labels(
            model="gemini-2.0-flash",
            operation="chat",
            status="error"
        ).inc()
        
        jamie_metrics.errors_total.labels(
            component="ai_brain",
            error_type=type(e).__name__, 
            severity="error"
        ).inc()
        
        return {
            "response": jamie_personality.get_error_response() + " Give me a moment to sort myself out!",
            "confidence": 0.3,
            "intent": "error",
            "topics": [],
            "timestamp": datetime.now().isoformat()
        }

# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 FALLBACK RESPONSE SYSTEM - When AI brain isn't available
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_basic_response(message: str, intent_data: Dict, context: Dict) -> Dict[str, Any]:
    """
    🤖 Fallback basic response generation when AI brain unavailable
    
    BASIC RESPONSE STRATEGY:
    1. Use intent to determine response type
    2. Route to appropriate handler based on topic
    3. Provide helpful responses even without full AI
    4. Maintain Jamie's personality
    """
    # 🎯 DETERMINE RESPONSE based on intent
    if intent_data["primary_intent"] == "help":
        response = jamie_personality.get_help_response()
    elif intent_data["primary_intent"] == "query":
        # 📂 ROUTE TO TOPIC-SPECIFIC HANDLERS
        if "kubernetes" in intent_data["topics"]:
            response = await handle_kubernetes_query(message, context)
        elif "monitoring" in intent_data["topics"]:
            response = await handle_metrics_query(message, context)
        elif "logging" in intent_data["topics"]:
            response = await handle_logs_query(message, context)
        elif "tracing" in intent_data["topics"]:
            response = await handle_traces_query(message, context)
        elif "git" in intent_data["topics"]:
            response = await handle_github_query(message, context)
        else:
            response = jamie_personality.get_general_response() + " What would you like to know about your infrastructure?"
    elif intent_data["primary_intent"] == "troubleshoot":
        response = jamie_personality.get_error_response() + " Right, let's get this sorted! What's the specific issue you're seeing?"
    else:
        # 👋 HANDLE GREETINGS and general responses
        if any(keyword in message.lower() for keyword in ["hello", "hi", "hey", "morning", "afternoon"]):
            response = jamie_personality.get_time_appropriate_greeting() + " What's the plan for today then?"
        else:
            response = jamie_personality.get_general_response() + " Could you be a bit more specific about what you'd like to know?"
    
    return {
        "response": response,
        "confidence": intent_data["confidence"],
        "intent": intent_data["primary_intent"],
        "topics": intent_data["topics"]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 DEVOPS TOPIC HANDLERS - Placeholder implementations for MCP integration
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_kubernetes_query(message: str, context: Dict) -> str:
    """🚢 Handle Kubernetes-related queries"""
    # TODO: Integrate with Kubernetes MCP server
    return jamie_personality.get_thinking_phrase() + " Right, let me have a look at your cluster... Unfortunately, I haven't got my eyes on Kubernetes just yet, but I'm working on it! Soon I'll be able to tell you all about your pods and deployments."

async def handle_metrics_query(message: str, context: Dict) -> str:
    """📊 Handle Prometheus metrics queries"""
    # TODO: Integrate with Prometheus MCP server  
    return jamie_personality.get_thinking_phrase() + " Let me check those metrics for you... Blimey, I need to get connected to Prometheus first! Once that's sorted, I'll be able to give you the full rundown on your system performance."

async def handle_logs_query(message: str, context: Dict) -> str:
    """📝 Handle Loki log queries"""
    # TODO: Integrate with Loki MCP server
    return jamie_personality.get_thinking_phrase() + " I'll have a butcher's at those logs... Actually, I need to get plugged into Loki first! Once I'm connected, I'll be able to spot those pesky errors in no time."

async def handle_traces_query(message: str, context: Dict) -> str:
    """🔍 Handle Tempo trace queries"""
    # TODO: Integrate with Tempo MCP server
    return jamie_personality.get_thinking_phrase() + " Let me trace through that for you... Right, I need to get connected to Tempo first! Once that's done, I'll be able to track down any performance bottlenecks."

async def handle_github_query(message: str, context: Dict) -> str:
    """🐙 Handle GitHub repository queries"""
    # TODO: Integrate with GitHub MCP server
    return jamie_personality.get_thinking_phrase() + " Let me check what's happening in your repos... I need to get my GitHub integration sorted first! Once that's ready, I'll be able to tell you all about your latest commits and deployments."

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 AI STATUS AND MANAGEMENT ENDPOINTS - Monitor and manage AI systems
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/ai/status")
@trace_endpoint("ai_status_check")
async def ai_status():
    """
    📊 Get comprehensive AI system status including RAG
    
    STATUS INCLUDES:
    - AI brain availability and configuration
    - RAG memory system status
    - Available features and capabilities
    - Personality system information
    """
    try:
        logger.info(f"AI status check requested [correlation_id: {get_correlation_id()}]")
        
        # 🧠 GET BRAIN STATUS
        brain_status = ai_brain.get_health_status() if ai_brain else {"available": False}
        
        # 🗄️ GET RAG-SPECIFIC STATUS
        rag_status = {}
        if ai_brain and ai_brain.rag_available:
            rag_status = await ai_brain.rag_memory.get_status()
        
        # 📊 Update system health metrics
        jamie_metrics.system_health.labels(component="ai_status_check").set(1.0)
        
        status_response = {
            "timestamp": datetime.now().isoformat(),
            "ai_brain": brain_status,
            "rag_memory": rag_status,
            "personality": {
                "loaded": True,
                "type": "British DevOps Personality"
            },
            "features": {
                "conversation_memory": True,
                "intent_detection": True,
                "personality_responses": True,
                "rag_enhanced_responses": ai_brain.rag_available if ai_brain else False,
                "devops_context_awareness": True
            }
        }
        
        logger.info(f"AI status check completed [ai_available: {brain_status.get('available', False)}]")
        return status_response
        
    except Exception as e:
        logger.error(f"Error getting AI status [error: {str(e)}]")
        jamie_metrics.errors_total.labels(
            component="ai_status",
            error_type=type(e).__name__,
            severity="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Error getting AI status: {str(e)}")

@app.post("/ai/knowledge")
async def add_knowledge(
    title: str,
    content: str,
    category: str,
    doc_type: str = "knowledge",
    tags: Optional[List[str]] = None,
    source_url: Optional[str] = None
):
    """
    📚 Add new knowledge to Jamie's RAG system
    
    KNOWLEDGE TYPES:
    - knowledge: General information and best practices
    - troubleshoot: Problem-solving guides
    - runbook: Step-by-step procedures
    
    CATEGORIES:
    - kubernetes, monitoring, logging, tracing, git, infrastructure, security
    """
    try:
        if not ai_brain or not ai_brain.rag_available:
            return {"error": "RAG system not available", "success": False}
        
        doc_id = await ai_brain.add_knowledge(
            title=title,
            content=content,
            category=category,
            doc_type=doc_type,
            tags=tags,
            source_url=source_url
        )
        
        if doc_id:
            return {
                "success": True,
                "document_id": doc_id,
                "message": f"Added knowledge: {title}"
            }
        else:
            return {"success": False, "error": "Failed to store knowledge"}
            
    except Exception as e:
        logger.error(f"Error adding knowledge: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/ai/search")
async def search_knowledge(
    query: str,
    categories: Optional[str] = None,
    limit: int = 5
):
    """
    🔍 Search Jamie's knowledge base
    
    SEARCH FEATURES:
    - Semantic search using vector embeddings
    - Category filtering (comma-separated)
    - Configurable result limit
    - Fallback to text search if vector search fails
    """
    try:
        if not ai_brain or not ai_brain.rag_available:
            return {"error": "RAG system not available", "results": []}
        
        # 📂 PARSE CATEGORIES if provided
        category_list = None
        if categories:
            category_list = [cat.strip() for cat in categories.split(",")]
        
        # 🔍 SEARCH KNOWLEDGE BASE
        results = await ai_brain.search_knowledge(
            query=query,
            categories=category_list,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching knowledge: {str(e)}")
        return {"error": str(e), "results": []}

# ═══════════════════════════════════════════════════════════════════════════════
# 🔌 MCP INTEGRATION ENDPOINTS - Connect to DevOps tools
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/mcp/status")
async def get_mcp_status():
    """📊 Get status of all MCP servers"""
    try:
        server_status = mcp_client.get_server_status()
        capabilities = mcp_client.get_capabilities()
        
        return {
            "mcp_status": "active",
            "servers": server_status,
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting MCP status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get MCP status", "details": str(e)}
        )

@app.get("/mcp/health")
async def check_mcp_health():
    """🏥 Health check for all MCP servers"""
    try:
        health_results = await mcp_client.health_check_all()
        return health_results
    except Exception as e:
        logger.error(f"Error checking MCP health: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to check MCP health", "details": str(e)}
        )

@app.post("/mcp/query/{server_name}")
async def query_mcp_server(server_name: str, request: dict):
    """🔍 Query a specific MCP server"""
    try:
        query_type = request.get("query_type")
        params = request.get("params", {})
        
        if not query_type:
            return JSONResponse(
                status_code=400,
                content={"error": "query_type is required"}
            )
        
        result = await mcp_client.query_server(server_name, query_type, params)
        return result
        
    except Exception as e:
        logger.error(f"Error querying MCP server {server_name}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to query {server_name}", "details": str(e)}
        )

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 DEVOPS INTEGRATION ENDPOINTS - High-level DevOps operations
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/devops/cluster/status")
async def get_cluster_status():
    """🚢 Get overall cluster status with Jamie's analysis"""
    try:
        cluster_status = await mcp_client.get_cluster_status()
        
        # 🎭 ENHANCE WITH JAMIE'S PERSONALITY
        status_message = "Right then! Let me check your cluster status, mate..."
        if cluster_status.get("cluster_overview", {}).get("prometheus", {}).get("alerts", {}).get("data", {}).get("total_alerts", 0) > 0:
            status_message = "Blimey! Found some alerts that need your attention!"
        else:
            status_message = "Brilliant! Your cluster's looking healthy as can be!"
        
        return {
            **cluster_status,
            "jamie_says": status_message
        }
        
    except Exception as e:
        logger.error(f"Error getting cluster status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get cluster status", "details": str(e)}
        )

@app.get("/devops/errors/recent")
async def get_recent_errors(duration: str = "1h"):
    """🚨 Get recent errors from logs and alerts with Jamie's analysis"""
    try:
        errors = await mcp_client.get_recent_errors(duration)
        
        # 🔍 ADD JAMIE'S ANALYSIS
        error_count = 0
        if errors.get("error_summary", {}).get("error_logs", {}).get("success"):
            error_count = errors["error_summary"]["error_logs"]["data"]["error_analysis"]["total_errors"]
        
        if error_count > 0:
            jamie_analysis = f"Found {error_count} errors in the last {duration}. Let's sort these out!"
        else:
            jamie_analysis = f"No errors found in the last {duration}. Your services are behaving brilliantly!"
        
        return {
            **errors,
            "jamie_analysis": jamie_analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting recent errors: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get recent errors", "details": str(e)}
        )

@app.get("/devops/service/{service_name}")
async def get_service_overview(service_name: str):
    """🔍 Get comprehensive overview of a specific service with Jamie's insights"""
    try:
        service_overview = await mcp_client.get_service_overview(service_name)
        
        # 🧠 JAMIE'S SERVICE ANALYSIS
        jamie_insights = []
        if service_overview.get("service_overview", {}).get("metrics", {}).get("error_rate", {}).get("success"):
            error_rate = service_overview["service_overview"]["metrics"]["error_rate"]["data"]["current_error_rate"]
            if error_rate and float(error_rate.rstrip('%')) > 5:
                jamie_insights.append(f"Your {service_name} service has a {error_rate} error rate - might want to investigate!")
            else:
                jamie_insights.append(f"Error rate for {service_name} looks spot on!")
        
        return {
            **service_overview,
            "jamie_insights": jamie_insights
        }
        
    except Exception as e:
        logger.error(f"Error getting service overview: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get overview for {service_name}", "details": str(e)}
        )

@app.post("/devops/search")
async def search_devops_platforms(request: dict):
    """🔍 Search across multiple DevOps platforms with Jamie's summary"""
    try:
        query = request.get("query")
        platforms = request.get("platforms")  # Optional filter
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "query is required"}
            )
        
        search_results = await mcp_client.search_across_platforms(query, platforms)
        
        # 📊 JAMIE'S SEARCH SUMMARY
        total_results = 0
        for platform_results in search_results.get("search_results", {}).values():
            if platform_results.get("success"):
                # Count results based on platform type
                if "entries" in platform_results.get("data", {}):
                    total_results += len(platform_results["data"]["entries"])
        
        jamie_summary = f"Found {total_results} results for '{query}' across your DevOps platforms!"
        
        return {
            **search_results,
            "jamie_summary": jamie_summary
        }
        
    except Exception as e:
        logger.error(f"Error searching DevOps platforms: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to search platforms", "details": str(e)}
        )

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 OBSERVABILITY MIDDLEWARE - Correlation ID and request tracking
# ═══════════════════════════════════════════════════════════════════════════════

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """
    📊 Add observability context to all requests
    
    FEATURES:
    - Generate correlation ID for request tracing
    - Track request metrics
    - Add request context to logs
    """
    # Generate correlation ID from header or create new one
    correlation_id = request.headers.get("x-correlation-id") or get_correlation_id()
    set_correlation_id(correlation_id)
    
    # Add response header with correlation ID
    response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id
    
    # Track request metrics
    jamie_metrics.http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    return response

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 OBSERVABILITY ENDPOINTS - Metrics, health, and monitoring
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/observability/status")
@trace_endpoint("observability_status")
async def observability_status():
    """
    📊 Get comprehensive observability system status
    
    STATUS INCLUDES:
    - Metrics collection status
    - Tracing configuration
    - Logging configuration
    - Active correlation IDs
    - System health scores
    """
    try:
        
        # Get current system health metrics
        health_scores = {}
        for component in ["ai_brain", "api_server", "chat_system"]:
            try:
                # Get current health score for component
                health_scores[component] = 1.0  # Default healthy
            except:
                health_scores[component] = 0.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "enabled": config.METRICS_ENABLED,
                "endpoint": config.METRICS_PATH,
                "port": config.METRICS_PORT
            },
            "tracing": {
                "enabled": config.TRACING_ENABLED,
                "service_name": config.TRACING_SERVICE_NAME,
                "endpoint": config.TRACING_ENDPOINT,
                "sample_rate": config.TRACING_SAMPLE_RATE
            },
            "logging": {
                "level": config.LOG_LEVEL,
                "format": config.LOG_FORMAT,
                "structured": config.LOG_STRUCTURED,
                "correlation_enabled": config.LOG_CORRELATION_ID
            },
            "health_scores": health_scores,
            "current_correlation_id": get_correlation_id()
        }
        
    except Exception as e:
        logger.error(f"Error getting observability status [error: {str(e)}]")
        raise HTTPException(status_code=500, detail=f"Error getting observability status: {str(e)}")

@app.get("/observability/metrics/summary")
@trace_endpoint("metrics_summary")
async def metrics_summary():
    """
    📈 Get summary of key metrics for dashboards
    
    INCLUDES:
    - Request counts and latencies
    - AI operation metrics
    - Error rates
    - System health scores
    """
    try:
        # This would typically query the metrics registry
        # For now, return a summary structure
        return {
            "timestamp": datetime.now().isoformat(),
            "api": {
                "total_requests": "See /metrics endpoint",
                "average_latency": "See /metrics endpoint",
                "error_rate": "See /metrics endpoint"
            },
            "ai": {
                "total_ai_requests": "See /metrics endpoint", 
                "average_response_time": "See /metrics endpoint",
                "success_rate": "See /metrics endpoint"
            },
            "chat": {
                "active_sessions": "See /metrics endpoint",
                "total_messages": "See /metrics endpoint",
                "average_quality_score": "See /metrics endpoint"
            },
            "note": "Full metrics available at /metrics endpoint in Prometheus format"
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary [error: {str(e)}]")
        raise HTTPException(status_code=500, detail=f"Error getting metrics summary: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN APPLICATION ENTRY POINT - Run Jamie
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    🏃 Run Jamie directly for development
    
    USAGE: python -m api.main
    
    This starts Jamie on localhost:8000 with auto-reload
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 