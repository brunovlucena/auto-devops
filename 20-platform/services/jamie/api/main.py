"""
🤖 Jamie: AI DevOps Copilot - Enhanced with AI Brain

Sprint 2: AI Brain & Memory Integration
Your friendly IT buddy meets AI-powered automation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
import asyncio
from fastapi.responses import JSONResponse

from .personality import JamiePersonality
from .models.conversation import ConversationManager
from .tools.mcp_client import MCPClient
from .ai.brain import JamieBrain
from .ai.memory import VectorMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jamie - AI DevOps Copilot",
    description="Your friendly IT buddy meets AI-powered automation - The personable face of DevOps",
    version="2.0.0",  # Sprint 2
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Jamie's components
jamie_personality = JamiePersonality()
conversation_manager = ConversationManager()
mcp_client = MCPClient()

# Sprint 2: Initialize AI components
ai_brain = None
vector_memory = None

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"
    session_id: str = "default"
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: str
    confidence: Optional[float] = None
    topics: Optional[List[str]] = None
    intent: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    message: str
    timestamp: str
    ai_status: Dict[str, Any]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize Jamie's systems on startup"""
    logger.info("🚀 Starting Jamie AI DevOps Copilot - Sprint 3!")
    
    try:
        # Initialize MCP client and connect to DevOps tools
        logger.info("🔌 Initializing MCP connections...")
        await mcp_client.connect_to_servers()
        
        # Initialize AI systems
        logger.info("🧠 Initializing AI brain...")
        await ai_brain.initialize()
        
        # Initialize memory systems
        logger.info("🎯 Initializing vector memory...")
        vector_memory.initialize_memory()
        
        logger.info("✅ Jamie is fully operational and ready to help with DevOps!")
        logger.info("   💬 Chat endpoints: /chat, /ws/{user_id}")
        logger.info("   🔍 MCP status: /mcp/status")
        logger.info("   📊 Cluster status: /devops/cluster/status")
        logger.info("   🚨 Recent errors: /devops/errors/recent")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        # Continue startup even if some systems fail
        logger.warning("⚠️ Some systems may not be fully operational")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of Jamie's systems"""
    logger.info("👋 Shutting down Jamie AI DevOps Copilot...")
    
    try:
        # Disconnect from MCP servers
        await mcp_client.disconnect_all()
        logger.info("Disconnected from MCP servers")
        
        # Shutdown AI systems gracefully
        if hasattr(ai_brain, 'cleanup'):
            await ai_brain.cleanup()
        
        logger.info("✅ Jamie shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint with Jamie's personality and AI status"""
    ai_status = {
        "brain_active": ai_brain is not None and ai_brain.is_available(),
        "vector_memory_active": vector_memory is not None and vector_memory.is_available(),
        "llm_model": ai_brain.get_model_info() if ai_brain else "Not available",
        "memory_collections": vector_memory.get_collection_count() if vector_memory else 0
    }
    
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
    """Detailed health check with AI component status"""
    ai_status = {
        "brain_active": ai_brain is not None and ai_brain.is_available(),
        "vector_memory_active": vector_memory is not None and vector_memory.is_available(),
        "mcp_servers": mcp_client.get_server_status(),
        "personality_loaded": True,
        "conversation_manager_active": True
    }
    
    if ai_brain:
        ai_status.update(ai_brain.get_health_status())
    
    return HealthCheck(
        status="healthy" if ai_status["brain_active"] else "degraded",
        message="All systems operational!" if ai_status["brain_active"] else "Running in basic mode",
        timestamp=datetime.now().isoformat(),
        ai_status=ai_status
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Enhanced chat endpoint with AI brain integration
    """
    try:
        logger.info(f"Received message from user {chat_message.user_id}: {chat_message.message}")
        
        # Store the conversation
        conversation_manager.add_message(
            session_id=chat_message.session_id,
            user_id=chat_message.user_id,
            message=chat_message.message,
            is_user=True,
            metadata=chat_message.context
        )
        
        # Generate Jamie's enhanced response
        response_data = await generate_ai_response(
            message=chat_message.message,
            user_id=chat_message.user_id,
            session_id=chat_message.session_id,
            context=chat_message.context
        )
        
        # Store Jamie's response
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
        
        # Store in vector memory for future learning
        if vector_memory:
            await vector_memory.store_interaction(
                user_message=chat_message.message,
                jamie_response=response_data["response"],
                context=chat_message.context or {},
                session_id=chat_message.session_id
            )
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=datetime.now().isoformat(),
            session_id=chat_message.session_id,
            confidence=response_data.get("confidence"),
            topics=response_data.get("topics"),
            intent=response_data.get("intent")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        error_response = jamie_personality.get_error_response() + f" Had a bit of trouble there: {str(e)}"
        raise HTTPException(status_code=500, detail=error_response)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    Enhanced WebSocket endpoint with streaming AI responses
    """
    await manager.connect(websocket)
    
    # Send Jamie's greeting
    greeting = jamie_personality.get_time_appropriate_greeting()
    intro_message = f"{greeting} I'm Jamie, your AI DevOps copilot! "
    if ai_brain and ai_brain.is_available():
        intro_message += "My AI brain is fully loaded and ready to help with your infrastructure!"
    else:
        intro_message += "I'm running in basic mode right now, but I can still help with DevOps questions!"
    
    await manager.send_personal_message(intro_message, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id", "ws_default")
            
            if user_message:
                logger.info(f"WebSocket message from {user_id}: {user_message}")
                
                # Generate enhanced response
                response_data = await generate_ai_response(
                    message=user_message,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Send response back
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

async def generate_ai_response(message: str, user_id: str, session_id: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Generate Jamie's AI-powered response with enhanced understanding
    """
    try:
        # Get conversation context and history
        conversation_context = conversation_manager.get_conversation_context(session_id)
        recent_history = conversation_manager.get_recent_context(session_id, 5)
        
        # Detect user intent with enhanced AI
        intent_data = conversation_manager.detect_user_intent(message, session_id)
        
        # Get relevant memories from vector store
        relevant_memories = []
        if vector_memory:
            relevant_memories = await vector_memory.search_similar_interactions(message, limit=3)
        
        # Generate response using AI brain if available
        if ai_brain and ai_brain.is_available():
            response_data = await ai_brain.generate_response(
                user_message=message,
                conversation_history=recent_history,
                intent=intent_data,
                relevant_memories=relevant_memories,
                devops_context=context,
                personality=jamie_personality
            )
        else:
            # Fallback to basic response generation
            response_data = await generate_basic_response(message, intent_data, conversation_context)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return {
            "response": jamie_personality.get_error_response() + " Give me a moment to sort myself out!",
            "confidence": 0.3,
            "intent": "error",
            "topics": []
        }

async def generate_basic_response(message: str, intent_data: Dict, context: Dict) -> Dict[str, Any]:
    """Fallback basic response generation"""
    # Determine response based on intent
    if intent_data["primary_intent"] == "help":
        response = jamie_personality.get_help_response()
    elif intent_data["primary_intent"] == "query":
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
        # Greetings and general responses
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

async def handle_kubernetes_query(message: str, context: Dict) -> str:
    """Handle Kubernetes-related queries"""
    # TODO: Integrate with Kubernetes MCP server
    return jamie_personality.get_thinking_phrase() + " Right, let me have a look at your cluster... Unfortunately, I haven't got my eyes on Kubernetes just yet, but I'm working on it! Soon I'll be able to tell you all about your pods and deployments."

async def handle_metrics_query(message: str, context: Dict) -> str:
    """Handle Prometheus metrics queries"""
    # TODO: Integrate with Prometheus MCP server  
    return jamie_personality.get_thinking_phrase() + " Let me check those metrics for you... Blimey, I need to get connected to Prometheus first! Once that's sorted, I'll be able to give you the full rundown on your system performance."

async def handle_logs_query(message: str, context: Dict) -> str:
    """Handle Loki log queries"""
    # TODO: Integrate with Loki MCP server
    return jamie_personality.get_thinking_phrase() + " I'll have a butcher's at those logs... Actually, I need to get plugged into Loki first! Once I'm connected, I'll be able to spot those pesky errors in no time."

async def handle_traces_query(message: str, context: Dict) -> str:
    """Handle Tempo trace queries"""
    # TODO: Integrate with Tempo MCP server
    return jamie_personality.get_thinking_phrase() + " Let me trace through that for you... Right, I need to get connected to Tempo first! Once that's done, I'll be able to track down any performance bottlenecks."

async def handle_github_query(message: str, context: Dict) -> str:
    """Handle GitHub repository queries"""
    # TODO: Integrate with GitHub MCP server
    return jamie_personality.get_thinking_phrase() + " Let me check what's happening in your repos... I need to get my GitHub integration sorted first! Once that's ready, I'll be able to tell you all about your latest commits and deployments."

# New AI endpoints for Sprint 2
@app.get("/ai/status")
async def ai_status():
    """Get detailed AI system status"""
    status = {
        "brain": ai_brain.get_health_status() if ai_brain else {"available": False},
        "memory": vector_memory.get_status() if vector_memory else {"available": False},
        "personality": jamie_personality.generate_personality_metadata()
    }
    return status

@app.post("/ai/learn")
async def learn_from_feedback(feedback_data: Dict[str, Any]):
    """Allow Jamie to learn from user feedback"""
    if ai_brain and vector_memory:
        await ai_brain.learn_from_feedback(feedback_data)
        return {"message": jamie_personality.get_success_response() + " Thanks for the feedback, mate! I'll learn from that."}
    else:
        return {"message": jamie_personality.get_error_response() + " My learning systems aren't available right now."}

# MCP Integration Endpoints
@app.get("/mcp/status")
async def get_mcp_status():
    """Get status of all MCP servers"""
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
    """Health check for all MCP servers"""
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
    """Query a specific MCP server"""
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

# DevOps Integration Endpoints
@app.get("/devops/cluster/status")
async def get_cluster_status():
    """Get overall cluster status"""
    try:
        cluster_status = await mcp_client.get_cluster_status()
        
        # Enhance with Jamie's personality
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
    """Get recent errors from logs and alerts"""
    try:
        errors = await mcp_client.get_recent_errors(duration)
        
        # Add Jamie's analysis
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
    """Get comprehensive overview of a specific service"""
    try:
        service_overview = await mcp_client.get_service_overview(service_name)
        
        # Jamie's service analysis
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
    """Search across multiple DevOps platforms"""
    try:
        query = request.get("query")
        platforms = request.get("platforms")  # Optional filter
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "query is required"}
            )
        
        search_results = await mcp_client.search_across_platforms(query, platforms)
        
        # Jamie's search summary
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 