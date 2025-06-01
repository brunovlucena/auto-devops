"""
🤖 Jamie: AI DevOps Copilot - Main API Application

Your friendly IT buddy meets AI-powered automation
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

from .personality import JamiePersonality
from .models.conversation import ConversationManager
from .tools.mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jamie - AI DevOps Copilot",
    description="Your friendly IT buddy meets AI-powered automation - The personable face of DevOps",
    version="1.0.0",
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

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: str

class HealthCheck(BaseModel):
    status: str
    message: str
    timestamp: str

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

@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint with Jamie's personality"""
    return HealthCheck(
        status="healthy",
        message=jamie_personality.get_greeting() + " Jamie's API is running like a dream, mate!",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Detailed health check"""
    return HealthCheck(
        status="healthy", 
        message="All systems go! Jamie's ready to help with your DevOps questions.",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Main chat endpoint for Jamie
    Process user messages and return Jamie's responses with personality
    """
    try:
        logger.info(f"Received message from user {chat_message.user_id}: {chat_message.message}")
        
        # Store the conversation
        conversation_manager.add_message(
            session_id=chat_message.session_id,
            user_id=chat_message.user_id,
            message=chat_message.message,
            is_user=True
        )
        
        # Generate Jamie's response
        response = await generate_jamie_response(
            message=chat_message.message,
            user_id=chat_message.user_id,
            session_id=chat_message.session_id
        )
        
        # Store Jamie's response
        conversation_manager.add_message(
            session_id=chat_message.session_id,
            user_id=chat_message.user_id,
            message=response,
            is_user=False
        )
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            session_id=chat_message.session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        error_response = jamie_personality.get_error_response() + f" Had a bit of trouble there: {str(e)}"
        raise HTTPException(status_code=500, detail=error_response)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time chat with Jamie
    """
    await manager.connect(websocket)
    
    # Send Jamie's greeting
    greeting = jamie_personality.get_greeting() + f" I'm Jamie, your DevOps copilot! What can I help you with today?"
    await manager.send_personal_message(greeting, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id", "ws_default")
            
            if user_message:
                logger.info(f"WebSocket message from {user_id}: {user_message}")
                
                # Generate Jamie's response
                response = await generate_jamie_response(
                    message=user_message,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Send response back
                response_data = {
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "type": "message"
                }
                await manager.send_personal_message(json.dumps(response_data), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for user {user_id}")

async def generate_jamie_response(message: str, user_id: str, session_id: str) -> str:
    """
    Generate Jamie's response with personality and context awareness
    """
    try:
        # Get conversation context
        context = conversation_manager.get_conversation_context(session_id)
        
        # Determine intent and response type
        if any(keyword in message.lower() for keyword in ["hello", "hi", "hey", "morning", "afternoon"]):
            return jamie_personality.get_greeting() + " What's the plan for today then?"
            
        elif any(keyword in message.lower() for keyword in ["help", "what can you do", "commands"]):
            return jamie_personality.get_help_response()
            
        elif any(keyword in message.lower() for keyword in ["cluster", "pods", "kubernetes", "k8s"]):
            return await handle_kubernetes_query(message, context)
            
        elif any(keyword in message.lower() for keyword in ["metrics", "prometheus", "alerts", "cpu", "memory"]):
            return await handle_metrics_query(message, context)
            
        elif any(keyword in message.lower() for keyword in ["logs", "errors", "loki"]):
            return await handle_logs_query(message, context)
            
        elif any(keyword in message.lower() for keyword in ["traces", "tempo", "slow", "performance"]):
            return await handle_traces_query(message, context)
            
        elif any(keyword in message.lower() for keyword in ["deployment", "github", "commits", "pr"]):
            return await handle_github_query(message, context)
            
        else:
            # General DevOps advice with personality
            return jamie_personality.get_general_response() + " Could you be a bit more specific about what you'd like to know?"
            
    except Exception as e:
        logger.error(f"Error generating Jamie response: {str(e)}")
        return jamie_personality.get_error_response() + " Give me a moment to sort myself out!"

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 