"""
🤖 Jamie's Conversation Management System

Handles conversation memory, context, and session management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Individual message in a conversation"""
    session_id: str
    user_id: str
    message: str
    is_user: bool
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class ConversationContext:
    """Context information for a conversation session"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    topics_discussed: List[str]
    user_preferences: Dict[str, Any]
    current_context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)

class ConversationManager:
    """
    Manages Jamie's conversation memory and context
    
    Features:
    - Session-based conversation tracking
    - Context-aware responses
    - User preference learning
    - Topic tracking
    - Message history management
    """
    
    def __init__(self, max_messages_per_session: int = 1000, session_timeout_hours: int = 24):
        self.max_messages_per_session = max_messages_per_session
        self.session_timeout_hours = session_timeout_hours
        
        # In-memory storage (would be replaced with MongoDB in production)
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.contexts: Dict[str, ConversationContext] = {}
        
        # DevOps topic categories for context tracking
        self.devops_topics = {
            "kubernetes": ["k8s", "pods", "cluster", "deployment", "service", "ingress"],
            "monitoring": ["prometheus", "grafana", "alerts", "metrics", "cpu", "memory"],
            "logging": ["loki", "logs", "errors", "debugging", "trace"],
            "tracing": ["tempo", "traces", "performance", "latency", "slow"],
            "git": ["github", "git", "commit", "pr", "deployment", "pipeline"],
            "infrastructure": ["docker", "container", "network", "storage", "volume"],
            "security": ["rbac", "secrets", "auth", "ssl", "tls", "certificates"]
        }
        
        logger.info("ConversationManager initialized")

    def add_message(self, session_id: str, user_id: str, message: str, is_user: bool, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation"""
        try:
            # Create message
            msg = ConversationMessage(
                session_id=session_id,
                user_id=user_id,
                message=message,
                is_user=is_user,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Initialize conversation if needed
            if session_id not in self.conversations:
                self.conversations[session_id] = []
                self._create_session_context(session_id, user_id)
            
            # Add message to conversation
            self.conversations[session_id].append(msg)
            
            # Update context
            self._update_session_context(session_id, message, is_user)
            
            # Trim old messages if needed
            self._trim_conversation(session_id)
            
            logger.info(f"Added message to session {session_id}: {'User' if is_user else 'Jamie'}")
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")

    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get conversation history for a session"""
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        if limit:
            messages = messages[-limit:]
        
        return messages

    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for a session"""
        if session_id not in self.contexts:
            return {}
        
        context = self.contexts[session_id]
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "message_count": context.message_count,
            "topics_discussed": context.topics_discussed,
            "current_context": context.current_context,
            "user_preferences": context.user_preferences,
            "session_age_minutes": (datetime.now() - context.created_at).total_seconds() / 60
        }

    def get_recent_context(self, session_id: str, message_limit: int = 5) -> str:
        """Get recent conversation context as a formatted string"""
        recent_messages = self.get_conversation_history(session_id, limit=message_limit)
        
        if not recent_messages:
            return "No previous conversation context."
        
        context_parts = []
        for msg in recent_messages:
            speaker = "User" if msg.is_user else "Jamie"
            context_parts.append(f"{speaker}: {msg.message}")
        
        return "\n".join(context_parts)

    def detect_user_intent(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Detect user intent from message and conversation context
        """
        message_lower = message.lower()
        context = self.get_conversation_context(session_id)
        
        intent = {
            "primary_intent": "general",
            "confidence": 0.5,
            "topics": [],
            "urgency": "normal",
            "follow_up": False
        }
        
        # Detect DevOps topics
        for topic, keywords in self.devops_topics.items():
            if any(keyword in message_lower for keyword in keywords):
                intent["topics"].append(topic)
                intent["confidence"] = min(intent["confidence"] + 0.2, 1.0)
        
        # Detect primary intent
        if any(word in message_lower for word in ["help", "what can you do", "commands"]):
            intent["primary_intent"] = "help"
            intent["confidence"] = 0.9
        elif any(word in message_lower for word in ["status", "how", "what's", "check"]):
            intent["primary_intent"] = "query"
            intent["confidence"] = 0.8
        elif any(word in message_lower for word in ["error", "problem", "issue", "broken", "down"]):
            intent["primary_intent"] = "troubleshoot"
            intent["urgency"] = "high"
            intent["confidence"] = 0.9
        elif any(word in message_lower for word in ["deploy", "update", "release", "push"]):
            intent["primary_intent"] = "deployment"
            intent["confidence"] = 0.8
        
        # Check if this is a follow-up question
        if context.get("message_count", 0) > 1:
            if any(word in message_lower for word in ["also", "and", "what about", "how about"]):
                intent["follow_up"] = True
        
        return intent

    def learn_user_preferences(self, session_id: str, user_message: str, jamie_response: str):
        """
        Learn user preferences from interactions
        """
        if session_id not in self.contexts:
            return
        
        context = self.contexts[session_id]
        
        # Learn from user message patterns
        message_lower = user_message.lower()
        
        # Verbosity preference
        if len(user_message.split()) < 5:
            context.user_preferences["prefers_brief"] = context.user_preferences.get("prefers_brief", 0) + 1
        else:
            context.user_preferences["prefers_detailed"] = context.user_preferences.get("prefers_detailed", 0) + 1
        
        # Technical level
        technical_terms = ["kubernetes", "prometheus", "loki", "tempo", "api", "json", "yaml"]
        if any(term in message_lower for term in technical_terms):
            context.user_preferences["technical_level"] = context.user_preferences.get("technical_level", 0) + 1
        
        # Time of day preferences
        current_hour = datetime.now().hour
        context.user_preferences["active_hours"] = context.user_preferences.get("active_hours", [])
        if current_hour not in context.user_preferences["active_hours"]:
            context.user_preferences["active_hours"].append(current_hour)

    def cleanup_old_sessions(self):
        """Clean up old conversation sessions"""
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        
        sessions_to_remove = []
        for session_id, context in self.contexts.items():
            if context.last_activity < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id in self.conversations:
                del self.conversations[session_id]
            if session_id in self.contexts:
                del self.contexts[session_id]
            logger.info(f"Cleaned up old session: {session_id}")

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation session"""
        if session_id not in self.contexts:
            return {}
        
        context = self.contexts[session_id]
        messages = self.conversations.get(session_id, [])
        
        user_messages = [msg for msg in messages if msg.is_user]
        jamie_messages = [msg for msg in messages if not msg.is_user]
        
        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat(),
            "duration_minutes": (context.last_activity - context.created_at).total_seconds() / 60,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "jamie_messages": len(jamie_messages),
            "topics_discussed": context.topics_discussed,
            "user_preferences": context.user_preferences
        }

    def _create_session_context(self, session_id: str, user_id: str):
        """Create a new session context"""
        self.contexts[session_id] = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            message_count=0,
            topics_discussed=[],
            user_preferences={},
            current_context={}
        )

    def _update_session_context(self, session_id: str, message: str, is_user: bool):
        """Update session context with new message"""
        if session_id not in self.contexts:
            return
        
        context = self.contexts[session_id]
        context.last_activity = datetime.now()
        context.message_count += 1
        
        # Extract topics from message
        if is_user:
            message_lower = message.lower()
            for topic, keywords in self.devops_topics.items():
                if any(keyword in message_lower for keyword in keywords):
                    if topic not in context.topics_discussed:
                        context.topics_discussed.append(topic)

    def _trim_conversation(self, session_id: str):
        """Trim conversation to max message limit"""
        if session_id in self.conversations:
            messages = self.conversations[session_id]
            if len(messages) > self.max_messages_per_session:
                # Keep most recent messages
                self.conversations[session_id] = messages[-self.max_messages_per_session:]
                logger.info(f"Trimmed conversation {session_id} to {self.max_messages_per_session} messages") 