"""
🧠 Jamie's AI Brain - Enhanced with MongoDB RAG

Sprint 6: RAG-powered intelligent DevOps responses using MongoDB vector search

⭐ WHAT THIS FILE DOES:
    - Combines Ollama LLM with MongoDB RAG knowledge base
    - Generates intelligent, context-aware responses
    - Learns from conversations and stores knowledge
    - Handles fallbacks when AI systems are unavailable
    - Provides DevOps-specific intelligence with British personality
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import os

from ..personality import JamiePersonality
from .rag_memory import MongoRAGMemory

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 MAIN AI BRAIN CLASS - The intelligence center of Jamie
# ═══════════════════════════════════════════════════════════════════════════════

class JamieBrain:
    """
    🤖 Jamie's Enhanced AI Brain with RAG (Retrieval-Augmented Generation)
    
    ⭐ MAIN FEATURES:
    - Ollama LLM integration for generating responses
    - MongoDB RAG knowledge retrieval for context
    - DevOps-specific expertise and knowledge
    - Learning from every conversation
    - Personality-infused responses with British charm
    
    💡 HOW IT WORKS:
    1. User asks a question
    2. Search knowledge base for relevant information
    3. Use Ollama LLM to generate response with context
    4. Add Jamie's personality to the response
    5. Store the conversation for future learning
    """
    
    def __init__(self):
        """🔧 Initialize Jamie's AI brain components"""
        
        # 🤖 OLLAMA LLM CONFIGURATION
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model_name = os.getenv("JAMIE_MODEL", "llama3.1:8b")
        self.model_available = False        # Whether Ollama is working
        
        # ⚙️ AI GENERATION SETTINGS
        self.max_tokens = 2048             # Maximum response length
        self.temperature = 0.7             # Creativity level (0=robotic, 1=creative)
        self.context_window = 4096         # How much context we can include
        
        # 🗄️ RAG MEMORY SYSTEM
        self.rag_memory = MongoRAGMemory()
        self.rag_available = False         # Whether RAG system is working
        
        # 🏷️ DEVOPS CATEGORIES we understand
        self.devops_categories = [
            "kubernetes", "monitoring", "logging", "tracing", 
            "git", "infrastructure", "security"
        ]
        
        # 📝 ENHANCED SYSTEM PROMPTS - Tell the AI how to behave
        self.system_prompts = {
            # 🔄 BASE PROMPT - Default behavior
            "base": """You are Jamie, a friendly British AI DevOps copilot with access to a comprehensive knowledge base.

PERSONALITY:
- Use British expressions: "mate", "brilliant", "blimey", "right then"
- Be friendly, helpful, and professional
- Show enthusiasm for solving problems
- Reference your knowledge when helpful: "I recall from our docs that..."

RAG CONTEXT USAGE:
- Use the provided knowledge base context to give accurate answers
- Combine general knowledge with specific documentation
- Reference similar past conversations when relevant
- Always acknowledge when information comes from your knowledge base

DEVOPS EXPERTISE:
- Kubernetes cluster management and troubleshooting
- Prometheus monitoring and alerting best practices
- Loki log analysis and debugging
- Tempo distributed tracing optimization
- GitHub repository and pipeline management

RESPONSE STYLE:
- Start with a British greeting or expression
- Integrate knowledge base context naturally
- Provide clear, actionable advice with commands
- Reference documentation when available
- End with encouragement or next steps""",

            # 🚨 TROUBLESHOOTING PROMPT - For fixing problems
            "troubleshooting": """You are Jamie helping with a DevOps issue using your knowledge base and past experience.

APPROACH:
1. Show empathy: "Blimey, that's not ideal!"
2. Use knowledge base to identify similar issues
3. Reference documented solutions and runbooks
4. Provide step-by-step troubleshooting from experience
5. Suggest monitoring and prevention strategies
6. Be encouraging: "We'll get this sorted based on what I know!"

RAG-ENHANCED TROUBLESHOOTING:
- Search knowledge base for similar issues
- Reference troubleshooting guides and runbooks
- Use past successful resolutions
- Combine multiple knowledge sources
- Provide links to documentation when available

FOCUS ON:
- Root cause analysis using documented patterns
- Immediate fixes from knowledge base
- Long-term prevention strategies
- Monitoring improvements based on best practices""",

            # 📚 LEARNING PROMPT - For teaching concepts
            "learning": """You are Jamie teaching DevOps concepts using your comprehensive knowledge base.

TEACHING STYLE:
- Start with basics: "Right then, let me check what I know about this..."
- Use documented examples and best practices
- Reference knowledge base guides and tutorials
- Provide hands-on commands from documentation
- Encourage experimentation: "Give it a go based on this guide!"

RAG-ENHANCED LEARNING:
- Pull relevant documentation and tutorials
- Show examples from knowledge base
- Reference related concepts and dependencies
- Provide progression paths for deeper learning
- Link to external resources when available

STRUCTURE:
1. Explain concept using knowledge base
2. Show practical examples from documentation
3. Provide commands and configurations
4. Suggest next steps and related topics"""
        }
        
        logger.info("Enhanced JamieBrain with RAG initialized")

    async def initialize(self):
        """
        🚀 Initialize the AI brain with RAG capabilities
        
        INITIALIZATION STEPS:
        1. Set up RAG memory system (MongoDB + embeddings)
        2. Check if Ollama LLM is available
        3. Test connections and mark as ready
        """
        try:
            # 🗄️ STEP 1: Initialize RAG memory system
            self.rag_available = await self.rag_memory.initialize()
            
            # 🤖 STEP 2: Check Ollama availability
            await self._check_ollama_availability()
            
            logger.info(f"✅ JamieBrain initialized - Ollama: {self.model_available}, RAG: {self.rag_available}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize JamieBrain: {str(e)}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # 💬 MAIN RESPONSE GENERATION - The core AI functionality
    # ═══════════════════════════════════════════════════════════════════════════════

    async def generate_response(
        self,
        user_message: str,
        conversation_history: str = "",
        intent: Optional[Dict[str, Any]] = None,
        relevant_memories: Optional[List[Dict]] = None,
        devops_context: Optional[Dict] = None,
        personality: Optional[JamiePersonality] = None
    ) -> Dict[str, Any]:
        """
        🎯 Generate RAG-enhanced response using knowledge base and LLM
        
        THIS IS THE MAIN MAGIC! ✨
        
        PROCESS OVERVIEW:
        1. Get relevant context from RAG knowledge base
        2. Build comprehensive context (conversation + knowledge + intent)
        3. Choose appropriate system prompt based on what user wants
        4. Generate response using Ollama LLM (or fallback if unavailable)
        5. Add Jamie's personality if needed
        6. Store conversation for future learning
        
        PARAMETERS:
        - user_message: What the user is asking
        - conversation_history: Recent chat context
        - intent: What type of request this is (help, troubleshoot, query)
        - relevant_memories: Previous similar conversations
        - devops_context: Technical context (namespace, cluster, etc.)
        - personality: Jamie's personality system
        
        RETURNS: Complete response with metadata
        """
        try:
            # 🔍 STEP 1: Get RAG context for the user message
            rag_context = await self._get_rag_context(user_message, intent)
            
            # 🏗️ STEP 2: Build comprehensive context for the AI
            full_context = self._build_rag_context(
                user_message=user_message,
                conversation_history=conversation_history,
                intent=intent or {},
                rag_context=rag_context,
                devops_context=devops_context
            )
            
            # 📝 STEP 3: Select appropriate system prompt based on intent
            system_prompt = self._select_system_prompt(intent)
            
            # 🤖 STEP 4: Generate response using Ollama if available
            if self.model_available:
                response = await self._generate_with_ollama(
                    system_prompt=system_prompt,
                    context=full_context,
                    user_message=user_message
                )
            else:
                # 🔄 FALLBACK: Generate response using knowledge base only
                response = await self._generate_knowledge_response(
                    user_message, rag_context, intent, personality
                )
            
            # 🎭 STEP 5: Enhance with personality if needed
            if personality:
                response = self._enhance_personality(response, personality, intent or {})
            
            # 📊 STEP 6: Calculate confidence score
            confidence = self._calculate_rag_confidence(intent or {}, rag_context)
            
            # 💾 STEP 7: Store conversation for future learning
            if self.rag_available:
                await self.rag_memory.store_conversation(
                    user_message=user_message,
                    jamie_response=response,
                    context=devops_context or {},
                    session_id=devops_context.get("session_id", "unknown") if devops_context else "unknown",
                    topics=intent.get("topics", []) if intent else [],
                    intent=intent.get("primary_intent", "unknown") if intent else "unknown",
                    confidence=confidence
                )
            
            # 📋 STEP 8: Return complete response with metadata
            return {
                "response": response,
                "confidence": confidence,
                "topics": intent.get("topics", []) if intent else [],
                "intent": intent.get("primary_intent", "general") if intent else "general",
                "rag_context_used": rag_context["documents_used"],
                "knowledge_categories": rag_context["categories_covered"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return {
                "response": "Blimey! I'm having a bit of trouble accessing my knowledge right now. Give me a tick to sort this out!",
                "confidence": 0.3,
                "topics": [],
                "intent": "error",
                "timestamp": datetime.now().isoformat()
            }

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔍 RAG CONTEXT RETRIEVAL - Getting relevant knowledge
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _get_rag_context(self, user_message: str, intent: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🎯 Get relevant context from RAG knowledge base
        
        CONTEXT STRATEGY:
        - For troubleshooting: Include both knowledge and past conversations
        - For learning: Focus on knowledge base and tutorials  
        - For queries: Include both for comprehensive answers
        
        RETURNS: Dictionary with context text and metadata
        """
        if not self.rag_available:
            return {
                "context": "",
                "context_length": 0,
                "documents_used": 0,
                "total_documents_found": 0,
                "categories_covered": []
            }
        
        try:
            # 📋 DETERMINE WHAT TYPE OF CONTEXT TO INCLUDE
            include_conversations = True
            include_knowledge = True
            
            # 🎯 ADJUST BASED ON INTENT
            if intent:
                intent_type = intent.get("primary_intent", "general")
                if intent_type == "troubleshoot":
                    # 🚨 Prioritize troubleshooting docs and similar issues
                    include_conversations = True
                    include_knowledge = True
                elif intent_type == "learn":
                    # 📚 Focus on knowledge and tutorials
                    include_conversations = False
                    include_knowledge = True
                elif intent_type == "query":
                    # ❓ Include both for comprehensive answers
                    include_conversations = True
                    include_knowledge = True
            
            # 🔍 GET RAG CONTEXT from knowledge base
            rag_context = await self.rag_memory.get_rag_context(
                query=user_message,
                max_context_length=3000,  # Leave room for conversation history
                include_conversations=include_conversations,
                include_knowledge=include_knowledge
            )
            
            logger.debug(f"RAG context: {rag_context['documents_used']} docs, {rag_context['context_length']} chars")
            return rag_context
            
        except Exception as e:
            logger.error(f"Error getting RAG context: {str(e)}")
            return {
                "context": "",
                "context_length": 0,
                "documents_used": 0,
                "total_documents_found": 0,
                "categories_covered": []
            }

    def _build_rag_context(
        self,
        user_message: str,
        conversation_history: str,
        intent: Dict[str, Any],
        rag_context: Dict[str, Any],
        devops_context: Optional[Dict]
    ) -> str:
        """
        🏗️ Build comprehensive context including RAG knowledge
        
        CONTEXT ASSEMBLY:
        1. RAG knowledge context (most important)
        2. Recent conversation history  
        3. User intent and topics
        4. DevOps technical context
        5. RAG metadata (what sources we're using)
        
        RESULT: Complete context string for the AI to use
        """
        
        context_parts = []
        
        # 📚 ADD RAG KNOWLEDGE CONTEXT (most important)
        if rag_context["context"]:
            context_parts.append(f"KNOWLEDGE BASE CONTEXT:\n{rag_context['context']}")
        
        # 💬 ADD CONVERSATION HISTORY
        if conversation_history:
            context_parts.append(f"RECENT CONVERSATION:\n{conversation_history}")
        
        # 🎯 ADD USER INTENT AND TOPICS
        intent_info = f"USER INTENT: {intent.get('primary_intent', 'unknown')}"
        if intent.get("topics"):
            intent_info += f"\nTOPICS: {', '.join(intent['topics'])}"
        if intent.get("urgency") != "normal":
            intent_info += f"\nURGENCY: {intent['urgency']}"
        context_parts.append(intent_info)
        
        # 🔧 ADD DEVOPS CONTEXT if available
        if devops_context:
            context_parts.append(f"DEVOPS CONTEXT: {json.dumps(devops_context, indent=2)}")
        
        # 📊 ADD RAG METADATA (what sources we're using)
        if rag_context["documents_used"] > 0:
            rag_info = f"KNOWLEDGE SOURCES: {rag_context['documents_used']} documents from {len(rag_context['categories_covered'])} categories"
            if rag_context["categories_covered"]:
                rag_info += f" ({', '.join(rag_context['categories_covered'])})"
            context_parts.append(rag_info)
        
        return "\n\n".join(context_parts)

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🤖 OLLAMA LLM INTEGRATION - Generate responses using AI
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _generate_with_ollama(
        self,
        system_prompt: str,
        context: str,
        user_message: str
    ) -> str:
        """
        🤖 Generate response using Ollama with RAG context
        
        PROCESS:
        1. Build complete prompt with system instructions + context + user message
        2. Send to Ollama API for generation
        3. Get response back with Jamie's personality and knowledge
        
        PARAMETERS:
        - system_prompt: Instructions on how Jamie should behave
        - context: All the relevant information (RAG + conversation + intent)
        - user_message: What the user actually asked
        """
        try:
            # 🏗️ BUILD THE COMPLETE PROMPT
            full_prompt = f"""{system_prompt}

{context}

USER MESSAGE: {user_message}

Please provide a helpful response as Jamie, incorporating the knowledge base information where relevant. Be specific and actionable while maintaining Jamie's British personality."""

            # 🌐 SEND REQUEST TO OLLAMA
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": full_prompt,
                        "stream": False,              # Get complete response at once
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "Sorry mate, couldn't generate a response!")
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return "Having a spot of bother with my AI brain, mate!"
                    
        except Exception as e:
            logger.error(f"Error with Ollama generation: {str(e)}")
            return "Blimey! My AI's gone a bit wonky. Let me try a different approach..."

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔄 FALLBACK RESPONSES - When AI systems aren't available
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _generate_knowledge_response(
        self,
        user_message: str,
        rag_context: Dict[str, Any],
        intent: Optional[Dict],
        personality: Optional[JamiePersonality]
    ) -> str:
        """
        📚 Generate response using knowledge base when Ollama is unavailable
        
        FALLBACK STRATEGY:
        1. If we have RAG context, use it to create a helpful response
        2. Format the response based on user intent (troubleshoot vs learn)
        3. Add Jamie's personality
        4. Provide category-specific fallbacks if no RAG context
        
        THIS ENSURES JAMIE IS ALWAYS HELPFUL even when LLM is down!
        """
        try:
            # 📚 IF WE HAVE RAG CONTEXT, USE IT
            if rag_context["context"]:
                # Extract key information from context
                context_text = rag_context["context"]
                
                # 🎭 GET JAMIE'S GREETING
                greeting = "Right then! Based on what I know..."
                if personality:
                    greeting = personality.get_thinking_phrase()
                
                # 🎯 DETERMINE RESPONSE STYLE based on intent
                if intent and intent.get("primary_intent") == "troubleshoot":
                    response = f"{greeting} I've found some relevant troubleshooting information in my knowledge base. Here's what typically works for this issue:\n\n"
                elif intent and intent.get("primary_intent") == "learn":
                    response = f"{greeting} Let me share what I know about this topic from my documentation:\n\n"
                else:
                    response = f"{greeting} Here's what I can tell you based on my knowledge:\n\n"
                
                # 📝 ADD RELEVANT CONTEXT snippets
                if len(context_text) > 500:
                    # Truncate long context and offer more details
                    response += context_text[:500] + "...\n\nWould you like me to elaborate on any specific part, mate?"
                else:
                    response += context_text
                
                response += "\n\nHope that helps! Let me know if you need more details on any of this."
                
                return response
            
            # 🔄 FALLBACK RESPONSES when no RAG context available
            fallback_responses = {
                "kubernetes": "Right then! For Kubernetes issues, I'd typically recommend checking your pod status with `kubectl get pods` and looking at the logs with `kubectl logs`. What specific problem are you seeing?",
                "monitoring": "Brilliant! For monitoring questions, I usually point folks to check Prometheus metrics and Grafana dashboards. What metrics are you trying to track?",
                "logging": "Good question! For log analysis, Loki's your friend. Try using LogQL queries to filter your logs. What kind of errors are you seeing?",
                "tracing": "Spot on! For tracing issues, Tempo can help you identify bottlenecks. Are you seeing slow requests that need investigation?",
                "git": "Right! For Git and deployment questions, I'd check your repository settings and pipeline status. What's the specific issue you're facing?"
            }
            
            # 🔍 TRY TO MATCH user message to categories
            user_lower = user_message.lower()
            for category, response in fallback_responses.items():
                category_keywords = {
                    "kubernetes": ["k8s", "pod", "cluster", "kubectl"],
                    "monitoring": ["prometheus", "grafana", "metrics", "alerts"],
                    "logging": ["loki", "logs", "errors"],
                    "tracing": ["tempo", "traces", "performance"],
                    "git": ["github", "git", "deploy", "pipeline"]
                }
                
                if any(keyword in user_lower for keyword in category_keywords.get(category, [])):
                    return response
            
            # 🤷 GENERIC FALLBACK when we can't determine category
            return "Right then! I'd love to help you with that. Could you give me a bit more detail about what you're trying to accomplish? The more specific you can be, the better I can assist!"
            
        except Exception as e:
            logger.error(f"Error generating knowledge response: {str(e)}")
            return "Sorry mate, I'm having a bit of trouble accessing my knowledge right now. Could you try rephrasing your question?"

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎭 PERSONALITY AND PROMPT MANAGEMENT - Making Jamie sound British
    # ═══════════════════════════════════════════════════════════════════════════════

    def _select_system_prompt(self, intent: Optional[Dict]) -> str:
        """
        📝 Select appropriate system prompt based on intent
        
        PROMPT SELECTION:
        - troubleshoot → Use troubleshooting-focused prompt
        - learn/help → Use teaching-focused prompt  
        - everything else → Use base prompt
        """
        if not intent:
            return self.system_prompts["base"]
        
        intent_type = intent.get("primary_intent", "general")
        
        if intent_type == "troubleshoot":
            return self.system_prompts["troubleshooting"]
        elif intent_type in ["learn", "help"]:
            return self.system_prompts["learning"]
        else:
            return self.system_prompts["base"]

    def _calculate_rag_confidence(self, intent: Dict, rag_context: Dict) -> float:
        """
        📊 Calculate confidence score based on RAG context quality
        
        CONFIDENCE FACTORS:
        - Base confidence: 0.7
        - +0.1 if we have relevant documents
        - +0.1 if we have multiple relevant documents  
        - +0.05 if we cover multiple knowledge categories
        - Blend with intent confidence
        - +0.05 for each known DevOps topic
        
        RESULT: Confidence score between 0.0 and 0.95
        """
        base_confidence = 0.7
        
        # 📈 BOOST CONFIDENCE based on RAG context quality
        if rag_context["documents_used"] > 0:
            base_confidence += 0.1
            
            # Additional boost for multiple relevant documents
            if rag_context["documents_used"] >= 3:
                base_confidence += 0.1
            
            # Boost for knowledge base coverage across categories
            if len(rag_context["categories_covered"]) > 1:
                base_confidence += 0.05
        
        # 🎯 ADJUST BASED ON INTENT confidence
        intent_confidence = intent.get("confidence", 0.5)
        base_confidence = (base_confidence + intent_confidence) / 2
        
        # 🏷️ BOOST IF WE HAVE topic-specific knowledge
        topics = intent.get("topics", [])
        known_topics = [topic for topic in topics if topic in self.devops_categories]
        if known_topics:
            base_confidence += 0.05 * len(known_topics)
        
        return min(base_confidence, 0.95)  # Cap at 95%

    def _enhance_personality(self, response: str, personality: JamiePersonality, intent: Dict) -> str:
        """
        🎭 Enhance response with Jamie's personality if needed
        
        PERSONALITY CHECK:
        1. Look for British indicators in the response
        2. If not found, add personality prefix based on intent
        3. Return enhanced response
        
        BRITISH INDICATORS: mate, brilliant, blimey, right then, alright, cheers
        """
        # 🔍 CHECK IF RESPONSE already has British personality
        british_indicators = ["mate", "brilliant", "blimey", "right then", "alright", "cheers"]
        has_personality = any(indicator in response.lower() for indicator in british_indicators)
        
        if not has_personality:
            # 🎯 ADD PERSONALITY PREFIX based on intent
            if intent.get("urgency") == "high":
                prefix = personality.get_error_response()
            elif intent.get("primary_intent") == "help":
                prefix = personality.get_general_response()
            else:
                prefix = personality.get_thinking_phrase()
            
            response = f"{prefix} {response}"
        
        return response

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔌 OLLAMA CONNECTION MANAGEMENT - Check if AI is available
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _check_ollama_availability(self):
        """
        🔍 Check if Ollama is available and working
        
        CONNECTION TEST:
        1. Try to connect to Ollama API
        2. Get list of available models
        3. Check if our preferred model is available
        4. Set availability flag
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_host}/api/tags")
                if response.status_code == 200:
                    tags = response.json()
                    models = [model["name"] for model in tags.get("models", [])]
                    
                    if self.model_name in models:
                        self.model_available = True
                        logger.info(f"✅ Ollama model {self.model_name} available")
                    else:
                        logger.warning(f"⚠️ Model {self.model_name} not found in Ollama")
                        self.model_available = False
                else:
                    logger.warning(f"⚠️ Ollama API returned {response.status_code}")
                    self.model_available = False
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Ollama: {str(e)}")
            self.model_available = False

    # ═══════════════════════════════════════════════════════════════════════════════
    # 📊 STATUS AND MANAGEMENT - Monitor brain health and manage knowledge
    # ═══════════════════════════════════════════════════════════════════════════════

    def is_available(self) -> bool:
        """
        ✅ Check if AI brain is available (either Ollama or RAG)
        
        AVAILABILITY LOGIC:
        - Brain is available if EITHER Ollama OR RAG is working
        - This ensures Jamie can always help in some capacity
        """
        return self.model_available or self.rag_available

    def get_health_status(self) -> Dict[str, Any]:
        """
        🏥 Get comprehensive health status of all brain components
        
        HEALTH CHECK INCLUDES:
        - Overall brain availability
        - Ollama LLM status (host, model, availability)
        - RAG system status (MongoDB, embeddings, documents)
        - Available features
        """
        return {
            "brain_available": self.is_available(),
            "ollama": {
                "available": self.model_available,
                "host": self.ollama_host,
                "model": self.model_name
            },
            "rag": {
                "available": self.rag_available,
                "status": self.rag_memory.get_status() if self.rag_available else {}
            },
            "features": {
                "knowledge_base": self.rag_available,
                "conversation_memory": self.rag_available,
                "vector_search": self.rag_available,
                "llm_generation": self.model_available
            }
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # 📚 KNOWLEDGE MANAGEMENT - Add and search knowledge
    # ═══════════════════════════════════════════════════════════════════════════════

    async def add_knowledge(
        self,
        title: str,
        content: str,
        category: str,
        doc_type: str = "knowledge",
        tags: Optional[List[str]] = None,
        source_url: Optional[str] = None
    ) -> str:
        """
        📝 Add new knowledge to the RAG system
        
        USE CASES:
        - Add new troubleshooting guides
        - Include best practices documentation
        - Store runbooks and procedures
        - Add external documentation links
        
        RETURNS: Document ID if successful, empty string if failed
        """
        if not self.rag_available:
            return ""
        
        return await self.rag_memory.store_knowledge(
            title=title,
            content=content,
            category=category,
            doc_type=doc_type,
            tags=tags,
            source_url=source_url
        )

    async def search_knowledge(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        🔍 Search the knowledge base
        
        SEARCH CAPABILITIES:
        - Semantic search using vector embeddings
        - Filter by categories (kubernetes, monitoring, etc.)
        - Limit number of results
        - Fallback to text search if vector search fails
        
        RETURNS: List of relevant documents with similarity scores
        """
        if not self.rag_available:
            return []
        
        return await self.rag_memory.search_similar_documents(
            query=query,
            doc_types=["knowledge", "runbook", "troubleshoot"],
            categories=categories,
            limit=limit
        )

    async def close(self):
        """🔐 Clean up resources"""
        if self.rag_memory:
            await self.rag_memory.close()

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TESTING AND EXAMPLES - Show how to use the enhanced brain
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test_enhanced_brain():
        """
        🧪 Test the enhanced AI brain with RAG
        
        THIS EXAMPLE SHOWS:
        1. How to initialize the brain
        2. How to search the knowledge base
        3. How to generate responses with context
        4. How to check system health
        """
        # 🚀 STEP 1: Initialize the brain
        brain = JamieBrain()
        await brain.initialize()
        
        print("Brain Status:", brain.get_health_status())
        
        # 🔍 STEP 2: Test knowledge search
        results = await brain.search_knowledge("kubernetes pod troubleshooting")
        print(f"Knowledge search: {len(results)} results")
        
        # 💬 STEP 3: Test response generation
        response = await brain.generate_response(
            user_message="My pods are crashing, what should I do?",
            intent={"primary_intent": "troubleshoot", "topics": ["kubernetes"], "urgency": "high"}
        )
        
        print(f"Response: {response['response'][:100]}...")
        print(f"Confidence: {response['confidence']}")
        print(f"RAG docs used: {response['rag_context_used']}")
        
        # 🔐 STEP 4: Clean up
        await brain.close()
    
    # 🏃 RUN THE TEST
    asyncio.run(test_enhanced_brain()) 