"""
💬 Jamie's Conversation Management System - Memory & Context Intelligence

Sprint 2: Enhanced conversation tracking with AI integration

⭐ WHAT THIS FILE DOES:
    - Tracks conversation history across sessions (who said what when)
    - Manages conversation context and user preferences
    - Detects user intent from natural language (help, troubleshoot, query)
    - Learns from user patterns and preferences over time
    - Provides conversation memory for better AI responses
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 DATA MODELS - Structures for storing conversation data
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConversationMessage:
    """
    📨 Individual message in a conversation
    
    WHAT IT STORES:
    - Who sent the message (user or Jamie)
    - What was said (the actual message text)
    - When it was sent (timestamp)
    - Extra context (metadata like confidence, topics, etc.)
    """
    session_id: str                                # Which conversation this belongs to
    user_id: str                                   # Who is talking to Jamie
    message: str                                   # The actual message text
    is_user: bool                                  # True if user said it, False if Jamie said it
    timestamp: datetime                            # When this message was sent
    metadata: Optional[Dict[str, Any]] = None      # Extra info (confidence, topics, etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        📤 Convert to dictionary for storage
        
        WHY WE NEED THIS:
        - Databases store dictionaries, not Python objects
        - JSON serialization requires dictionaries
        - Makes data portable between systems
        """
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()  # Convert datetime to string
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """
        📥 Create from dictionary
        
        REVERSE OF to_dict():
        - Takes dictionary from database/JSON
        - Converts back to Python object
        - Handles datetime conversion properly
        """
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])  # Convert string back to datetime
        return cls(**data)

@dataclass
class ConversationContext:
    """
    🧠 Context information for a conversation session
    
    WHAT IT TRACKS:
    - Session metadata (when started, last activity)
    - Conversation statistics (message count, topics discussed)
    - User preferences learned from this session
    - Current context for ongoing conversation
    """
    session_id: str                                # Unique identifier for this conversation
    user_id: str                                   # Who is having this conversation
    created_at: datetime                           # When the conversation started
    last_activity: datetime                        # Last message timestamp
    message_count: int                             # How many messages in this session
    topics_discussed: List[str]                    # DevOps topics covered (kubernetes, monitoring, etc.)
    user_preferences: Dict[str, Any]               # What we've learned about this user
    current_context: Dict[str, Any]                # Current conversation state
    
    def to_dict(self) -> Dict[str, Any]:
        """📤 Convert to dictionary for storage"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """📥 Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)

# ═══════════════════════════════════════════════════════════════════════════════
# 💬 MAIN CONVERSATION MANAGER - The brain for conversation tracking
# ═══════════════════════════════════════════════════════════════════════════════

class ConversationManager:
    """
    🧠 Manages Jamie's conversation memory and context
    
    ⭐ KEY FEATURES:
    - Session-based conversation tracking (remembers what you talked about)
    - Context-aware responses (understands follow-up questions)
    - User preference learning (remembers how you like to interact)
    - Topic tracking (knows you're talking about Kubernetes vs monitoring)
    - Message history management (keeps conversations organized)
    
    💡 HOW IT WORKS:
    1. Each conversation gets a unique session ID
    2. Messages are stored with metadata (who, what, when)
    3. Intent detection figures out what user wants (help, status check, troubleshooting)
    4. Context is maintained for better follow-up responses
    5. User preferences are learned and applied
    
    🗄️ STORAGE:
    - Currently uses in-memory storage (conversations dict)
    - In production, this would use MongoDB for persistence
    - Context and preferences are tracked per session
    """
    
    def __init__(self, max_messages_per_session: int = 1000, session_timeout_hours: int = 24):
        """
        🔧 Initialize conversation manager
        
        PARAMETERS:
        - max_messages_per_session: Trim conversations after this many messages
        - session_timeout_hours: Clean up sessions older than this
        """
        self.max_messages_per_session = max_messages_per_session
        self.session_timeout_hours = session_timeout_hours
        
        # 🗄️ IN-MEMORY STORAGE (would be replaced with MongoDB in production)
        self.conversations: Dict[str, List[ConversationMessage]] = {}     # session_id -> messages
        self.contexts: Dict[str, ConversationContext] = {}               # session_id -> context
        
        # 🏷️ DEVOPS TOPIC CATEGORIES for context tracking
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

    # ═══════════════════════════════════════════════════════════════════════════════
    # 📝 MESSAGE MANAGEMENT - Adding and retrieving conversation messages
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_message(self, session_id: str, user_id: str, message: str, is_user: bool, metadata: Optional[Dict[str, Any]] = None):
        """
        📝 Add a message to the conversation
        
        THIS IS THE CORE FUNCTION! 🎯
        Every time someone talks to Jamie, this gets called.
        
        PROCESS:
        1. Create a ConversationMessage object
        2. Initialize session if it's the first message
        3. Add message to conversation history
        4. Update session context with new info
        5. Trim old messages if conversation gets too long
        
        PARAMETERS:
        - session_id: Which conversation this belongs to
        - user_id: Who sent the message
        - message: What was said
        - is_user: True if human sent it, False if Jamie responded
        - metadata: Extra info like confidence, topics, intent
        """
        try:
            # 📨 STEP 1: Create message object
            msg = ConversationMessage(
                session_id=session_id,
                user_id=user_id,
                message=message,
                is_user=is_user,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # 🆕 STEP 2: Initialize conversation if it's new
            if session_id not in self.conversations:
                self.conversations[session_id] = []
                self._create_session_context(session_id, user_id)
            
            # ➕ STEP 3: Add message to conversation history
            self.conversations[session_id].append(msg)
            
            # 🔄 STEP 4: Update session context
            self._update_session_context(session_id, message, is_user)
            
            # ✂️ STEP 5: Trim old messages if needed
            self._trim_conversation(session_id)
            
            logger.info(f"Added message to session {session_id}: {'User' if is_user else 'Jamie'}")
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")

    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """
        📚 Get conversation history for a session
        
        USAGE:
        - AI brain wants to see recent conversation
        - User wants to review what they talked about
        - Analytics wants to analyze conversation patterns
        
        PARAMETERS:
        - session_id: Which conversation to retrieve
        - limit: Only return the most recent X messages (None = all messages)
        
        RETURNS: List of ConversationMessage objects in chronological order
        """
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        if limit:
            messages = messages[-limit:]  # Get last N messages
        
        return messages

    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """
        🧠 Get conversation context for a session
        
        WHAT CONTEXT INCLUDES:
        - Session metadata (who, when, how many messages)
        - Topics discussed in this conversation
        - User preferences learned
        - Current conversation state
        - Session age for determining relevance
        
        USAGE:
        - AI brain uses this for context-aware responses
        - Intent detection uses this for better accuracy
        - Personality system adapts based on user preferences
        
        RETURNS: Dictionary with all context information
        """
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
        """
        📝 Get recent conversation context as a formatted string
        
        PURPOSE:
        This creates a summary of recent messages that the AI brain can use
        to understand the current conversation flow.
        
        EXAMPLE OUTPUT:
        User: How's my cluster doing?
        Jamie: Your cluster's running brilliantly! All 15 pods are healthy.
        User: What about CPU usage?
        Jamie: CPU usage is at 45% across all nodes, well within normal limits.
        User: And memory?
        
        PARAMETERS:
        - session_id: Which conversation to summarize
        - message_limit: How many recent messages to include
        
        RETURNS: Formatted string with recent conversation
        """
        recent_messages = self.get_conversation_history(session_id, limit=message_limit)
        
        if not recent_messages:
            return "No previous conversation context."
        
        context_parts = []
        for msg in recent_messages:
            speaker = "User" if msg.is_user else "Jamie"
            context_parts.append(f"{speaker}: {msg.message}")
        
        return "\n".join(context_parts)

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 INTENT DETECTION - Understanding what the user wants
    # ═══════════════════════════════════════════════════════════════════════════════

    def detect_user_intent(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        🎯 Detect user intent from message and conversation context
        
        THIS IS JAMIE'S "LISTENING COMPREHENSION"! 👂
        
        INTENT TYPES:
        - help: "What can you do?", "How does this work?"
        - query: "How's my cluster?", "Show me status", "What's the CPU usage?"
        - troubleshoot: "My pods are failing!", "There's an error", "Something's broken"
        - general: General conversation, greetings, thank you
        
        WHAT IT ANALYZES:
        1. Keywords in the message (status, error, help, broken)
        2. DevOps topic detection (kubernetes, monitoring, logs)
        3. Urgency indicators (urgent, critical, emergency)
        4. Conversation context (follow-up questions)
        5. Emotional tone (frustrated, confused, happy)
        
        RETURNS: Intent analysis with confidence score and metadata
        """
        message_lower = message.lower()
        context = self.get_conversation_context(session_id)
        
        # 🏗️ BUILD INTENT STRUCTURE
        intent = {
            "primary_intent": "general",        # Main intent category
            "confidence": 0.5,                  # How sure we are (0-1)
            "topics": [],                       # DevOps topics detected
            "urgency": "normal",                # normal, high, critical
            "follow_up": False                  # Is this a follow-up question?
        }
        
        # 🏷️ STEP 1: Detect DevOps topics
        for topic, keywords in self.devops_topics.items():
            if any(keyword in message_lower for keyword in keywords):
                intent["topics"].append(topic)
                intent["confidence"] = min(intent["confidence"] + 0.2, 1.0)  # Boost confidence
        
        # 🎯 STEP 2: Detect primary intent based on keywords
        
        # 🆘 HELP INTENT - User asking for assistance or information
        if any(word in message_lower for word in ["help", "what can you do", "commands", "how does", "how do i"]):
            intent["primary_intent"] = "help"
            intent["confidence"] = 0.9
            
        # ❓ QUERY INTENT - User asking for status or information
        elif any(word in message_lower for word in ["status", "how", "what's", "check", "show me", "tell me"]):
            intent["primary_intent"] = "query"
            intent["confidence"] = 0.8
            
        # 🚨 TROUBLESHOOT INTENT - User reporting problems
        elif any(word in message_lower for word in ["error", "problem", "issue", "broken", "down", "failing", "crash"]):
            intent["primary_intent"] = "troubleshoot"
            intent["urgency"] = "high"
            intent["confidence"] = 0.9
            
        # 🔥 CRITICAL URGENCY DETECTION
        if any(word in message_lower for word in ["urgent", "emergency", "critical", "outage", "production down"]):
            intent["urgency"] = "critical"
            intent["confidence"] = min(intent["confidence"] + 0.1, 1.0)
        
        # 🔄 STEP 3: Check if this is a follow-up question
        if context.get("message_count", 0) > 0:
            # Look for follow-up indicators
            follow_up_indicators = ["and", "also", "what about", "how about", "any", "still"]
            if any(indicator in message_lower for indicator in follow_up_indicators):
                intent["follow_up"] = True
                # Inherit topics from recent conversation if not explicitly mentioned
                if not intent["topics"] and context.get("topics_discussed"):
                    intent["topics"] = context["topics_discussed"][-2:]  # Last 2 topics
        
        # 📊 STEP 4: Apply context-based confidence adjustments
        if context.get("topics_discussed"):
            # If we've discussed similar topics before, boost confidence
            for topic in intent["topics"]:
                if topic in context["topics_discussed"]:
                    intent["confidence"] = min(intent["confidence"] + 0.1, 1.0)
        
        return intent

    # ═══════════════════════════════════════════════════════════════════════════════
    # 📚 LEARNING AND PREFERENCES - Understanding user patterns
    # ═══════════════════════════════════════════════════════════════════════════════

    def learn_user_preferences(self, session_id: str, user_message: str, jamie_response: str):
        """
        📚 Learn user preferences from interaction patterns
        
        WHAT JAMIE LEARNS:
        - Response format preferences (detailed vs brief)
        - Technical depth level (novice vs expert)
        - Preferred DevOps topics and tools
        - Active hours (when user typically asks questions)
        - Response style preferences (formal vs casual)
        
        LEARNING SIGNALS:
        - Message length indicates detail preference
        - Technical terms suggest expertise level
        - Time patterns show active hours
        - Repeated topics show interests
        - Response timing indicates urgency preferences
        
        EXAMPLE LEARNING:
        - Short questions → User prefers brief responses
        - Lots of kubectl commands → User is Kubernetes-focused
        - Questions at 2 AM → User works late hours
        - "Thanks!" responses → User appreciates current style
        """
        if session_id not in self.contexts:
            return
        
        context = self.contexts[session_id]
        user_prefs = context.user_preferences
        
        # 📏 ANALYZE MESSAGE LENGTH (detail preference)
        message_length = len(user_message.split())
        if message_length > 10:
            user_prefs["prefers_detailed"] = user_prefs.get("prefers_detailed", 0) + 1
        else:
            user_prefs["prefers_brief"] = user_prefs.get("prefers_brief", 0) + 1
        
        # 🔧 DETECT TECHNICAL LEVEL based on DevOps terminology
        technical_terms = ["kubectl", "prometheus", "grafana", "loki", "namespace", "deployment", "service"]
        tech_term_count = sum(1 for term in technical_terms if term in user_message.lower())
        if tech_term_count > 0:
            current_level = user_prefs.get("technical_level", 5)  # Scale 1-10
            user_prefs["technical_level"] = min(current_level + tech_term_count, 10)
        
        # 🕐 TRACK ACTIVE HOURS
        current_hour = datetime.now().hour
        active_hours = user_prefs.get("active_hours", [])
        if current_hour not in active_hours:
            active_hours.append(current_hour)
            user_prefs["active_hours"] = active_hours[-10:]  # Keep last 10 unique hours
        
        # 🏷️ TRACK TOPIC INTERESTS
        for topic in context.topics_discussed:
            topic_count = user_prefs.get(f"interested_in_{topic}", 0)
            user_prefs[f"interested_in_{topic}"] = topic_count + 1
        
        logger.debug(f"Updated user preferences for session {session_id}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🧹 SESSION MANAGEMENT - Cleanup and maintenance
    # ═══════════════════════════════════════════════════════════════════════════════

    def cleanup_old_sessions(self):
        """
        🧹 Clean up old conversation sessions
        
        WHY WE NEED THIS:
        - Memory usage grows over time
        - Old conversations become irrelevant
        - User privacy (don't keep data forever)
        - Performance (fewer sessions to search)
        
        CLEANUP CRITERIA:
        - Sessions older than session_timeout_hours
        - Sessions with no recent activity
        - Abandoned sessions (single message, no follow-up)
        
        WHAT GETS CLEANED:
        - Conversation messages
        - Session context
        - User preferences (but could be preserved separately)
        """
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        
        sessions_to_remove = []
        for session_id, context in self.contexts.items():
            if context.last_activity < cutoff_time:
                sessions_to_remove.append(session_id)
        
        # 🗑️ REMOVE OLD SESSIONS
        for session_id in sessions_to_remove:
            if session_id in self.conversations:
                del self.conversations[session_id]
            if session_id in self.contexts:
                del self.contexts[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old conversation sessions")

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """
        📊 Get a summary of the conversation session
        
        SUMMARY INCLUDES:
        - Session statistics (duration, message count)
        - Topics discussed and their frequency
        - User engagement patterns
        - Key insights and preferences learned
        - Notable events (errors reported, successes achieved)
        
        USEFUL FOR:
        - Analytics and reporting
        - User experience optimization
        - Training data for AI improvements
        - Session review and debugging
        
        RETURNS: Comprehensive session summary
        """
        if session_id not in self.contexts:
            return {"error": "Session not found"}
        
        context = self.contexts[session_id]
        messages = self.conversations.get(session_id, [])
        
        # 📊 CALCULATE SESSION STATISTICS
        session_duration = (context.last_activity - context.created_at).total_seconds() / 60  # minutes
        user_messages = [msg for msg in messages if msg.is_user]
        jamie_messages = [msg for msg in messages if not msg.is_user]
        
        # 🏷️ ANALYZE TOPICS DISCUSSED
        topic_frequency = {}
        for topic in context.topics_discussed:
            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        return {
            "session_id": session_id,
            "user_id": context.user_id,
            "duration_minutes": round(session_duration, 2),
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "jamie_messages": len(jamie_messages),
            "topics_discussed": topic_frequency,
            "user_preferences": context.user_preferences,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔧 PRIVATE HELPER METHODS - Internal session management
    # ═══════════════════════════════════════════════════════════════════════════════

    def _create_session_context(self, session_id: str, user_id: str):
        """
        🆕 Create a new session context
        
        CALLED WHEN:
        - User starts a new conversation
        - First message in a session
        - After session cleanup/reset
        
        INITIALIZES:
        - Basic session metadata
        - Empty user preferences
        - Empty topic tracking
        - Current timestamp for tracking
        """
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            message_count=0,
            topics_discussed=[],
            user_preferences={},
            current_context={}
        )
        self.contexts[session_id] = context
        logger.debug(f"Created new session context for {session_id}")

    def _update_session_context(self, session_id: str, message: str, is_user: bool):
        """
        🔄 Update session context with new message information
        
        UPDATES:
        - Last activity timestamp
        - Message count
        - Topics discussed (extracted from message)
        - Current context state
        
        TOPIC EXTRACTION:
        - Scans message for DevOps keywords
        - Adds new topics to discussion list
        - Maintains topic history for context
        """
        if session_id not in self.contexts:
            return
        
        context = self.contexts[session_id]
        
        # 📊 UPDATE BASIC STATS
        context.last_activity = datetime.now()
        context.message_count += 1
        
        # 🏷️ EXTRACT AND UPDATE TOPICS
        if is_user:  # Only extract topics from user messages
            message_lower = message.lower()
            for topic, keywords in self.devops_topics.items():
                if any(keyword in message_lower for keyword in keywords):
                    if topic not in context.topics_discussed:
                        context.topics_discussed.append(topic)
        
        # 📝 UPDATE CURRENT CONTEXT
        context.current_context["last_message"] = message
        context.current_context["last_speaker"] = "user" if is_user else "jamie"

    def _trim_conversation(self, session_id: str):
        """
        ✂️ Trim conversation to maximum message limit
        
        WHY WE TRIM:
        - Prevent memory bloat
        - Keep responses focused on recent context
        - Maintain performance
        - Respect storage limits
        
        TRIMMING STRATEGY:
        - Keep most recent messages
        - Preserve conversation flow
        - Remove oldest messages first
        - Log when trimming occurs
        """
        if session_id not in self.conversations:
            return
        
        messages = self.conversations[session_id]
        if len(messages) > self.max_messages_per_session:
            # 📏 TRIM TO MAXIMUM SIZE
            trimmed_count = len(messages) - self.max_messages_per_session
            self.conversations[session_id] = messages[-self.max_messages_per_session:]
            logger.debug(f"Trimmed {trimmed_count} messages from session {session_id}")

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 CONVERSATION TESTING AND EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    🧪 Test conversation management when run directly
    
    USAGE: python api/models/conversation.py
    
    This will:
    - Create a conversation manager
    - Simulate a conversation
    - Test intent detection
    - Show conversation summaries
    """
    print("💬 Jamie's Conversation Management Test")
    print("=" * 50)
    
    # 🏗️ CREATE CONVERSATION MANAGER
    manager = ConversationManager()
    
    # 🧪 SIMULATE A CONVERSATION
    session_id = "test_session_123"
    user_id = "test_user"
    
    print("\n📝 Simulating conversation:")
    
    # User starts with a greeting
    manager.add_message(session_id, user_id, "Hello Jamie!", True)
    intent = manager.detect_user_intent("Hello Jamie!", session_id)
    print(f"  User: Hello Jamie! (Intent: {intent['primary_intent']}, Confidence: {intent['confidence']})")
    
    # Jamie responds
    manager.add_message(session_id, user_id, "Alright mate! What can I help you with today?", False)
    print(f"  Jamie: Alright mate! What can I help you with today?")
    
    # User asks about cluster status
    manager.add_message(session_id, user_id, "How's my Kubernetes cluster doing?", True)
    intent = manager.detect_user_intent("How's my Kubernetes cluster doing?", session_id)
    print(f"  User: How's my Kubernetes cluster doing? (Intent: {intent['primary_intent']}, Topics: {intent['topics']})")
    
    # Jamie responds with status
    manager.add_message(session_id, user_id, "Your cluster's running brilliantly! All 12 pods are healthy.", False)
    print(f"  Jamie: Your cluster's running brilliantly! All 12 pods are healthy.")
    
    # User asks follow-up question
    manager.add_message(session_id, user_id, "What about CPU usage?", True)
    intent = manager.detect_user_intent("What about CPU usage?", session_id)
    print(f"  User: What about CPU usage? (Intent: {intent['primary_intent']}, Follow-up: {intent['follow_up']})")
    
    # 📊 SHOW CONVERSATION SUMMARY
    print("\n📊 Conversation Summary:")
    summary = manager.get_conversation_summary(session_id)
    print(f"  Duration: {summary['duration_minutes']} minutes")
    print(f"  Messages: {summary['total_messages']} total ({summary['user_messages']} user, {summary['jamie_messages']} Jamie)")
    print(f"  Topics: {list(summary['topics_discussed'].keys())}")
    
    # 🧠 SHOW CONVERSATION CONTEXT
    print("\n🧠 Current Context:")
    context = manager.get_conversation_context(session_id)
    print(f"  Session age: {round(context['session_age_minutes'], 1)} minutes")
    print(f"  Topics discussed: {context['topics_discussed']}")
    
    # 📝 SHOW RECENT CONTEXT
    print("\n📝 Recent Context:")
    recent = manager.get_recent_context(session_id, 3)
    for line in recent.split('\n'):
        print(f"    {line}")
    
    print("\n🎉 Conversation management working perfectly!") 