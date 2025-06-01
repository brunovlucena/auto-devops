"""
�� Jamie's AI Brain - Enhanced with MongoDB RAG

Sprint 6: RAG-powered intelligent DevOps responses using MongoDB vector search
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

class JamieBrain:
    """
    Jamie's Enhanced AI Brain with RAG (Retrieval-Augmented Generation)
    
    Features:
    - Ollama LLM integration
    - MongoDB RAG knowledge retrieval
    - DevOps-specific context awareness
    - Learning from conversations
    - Personality-infused responses
    """
    
    def __init__(self):
        # Ollama configuration
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model_name = os.getenv("JAMIE_MODEL", "llama3.1:8b")
        self.model_available = False
        
        # AI configuration
        self.max_tokens = 2048
        self.temperature = 0.7
        self.context_window = 4096
        
        # RAG Memory System
        self.rag_memory = MongoRAGMemory()
        self.rag_available = False
        
        # DevOps knowledge categories
        self.devops_categories = [
            "kubernetes", "monitoring", "logging", "tracing", 
            "git", "infrastructure", "security"
        ]
        
        # Enhanced system prompts for RAG
        self.system_prompts = {
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
        """Initialize the AI brain with RAG capabilities"""
        try:
            # Initialize RAG memory system
            self.rag_available = await self.rag_memory.initialize()
            
            # Check Ollama availability
            await self._check_ollama_availability()
            
            logger.info(f"✅ JamieBrain initialized - Ollama: {self.model_available}, RAG: {self.rag_available}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize JamieBrain: {str(e)}")
            return False

    async def generate_response(
        self,
        user_message: str,
        conversation_history: str = "",
        intent: Optional[Dict[str, Any]] = None,
        relevant_memories: Optional[List[Dict]] = None,
        devops_context: Optional[Dict] = None,
        personality: Optional[JamiePersonality] = None
    ) -> Dict[str, Any]:
        """Generate RAG-enhanced response using knowledge base and LLM"""
        try:
            # Get RAG context for the user message
            rag_context = await self._get_rag_context(user_message, intent)
            
            # Build comprehensive context
            full_context = self._build_rag_context(
                user_message=user_message,
                conversation_history=conversation_history,
                intent=intent or {},
                rag_context=rag_context,
                devops_context=devops_context
            )
            
            # Select appropriate system prompt
            system_prompt = self._select_system_prompt(intent)
            
            # Generate response using Ollama if available
            if self.model_available:
                response = await self._generate_with_ollama(
                    system_prompt=system_prompt,
                    context=full_context,
                    user_message=user_message
                )
            else:
                # Fallback to knowledge-based response
                response = await self._generate_knowledge_response(
                    user_message, rag_context, intent, personality
                )
            
            # Enhance with personality if needed
            if personality:
                response = self._enhance_personality(response, personality, intent or {})
            
            # Calculate confidence score
            confidence = self._calculate_rag_confidence(intent or {}, rag_context)
            
            # Store the conversation in RAG memory for future learning
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

    async def _get_rag_context(self, user_message: str, intent: Optional[Dict] = None) -> Dict[str, Any]:
        """Get relevant context from RAG knowledge base"""
        if not self.rag_available:
            return {
                "context": "",
                "context_length": 0,
                "documents_used": 0,
                "total_documents_found": 0,
                "categories_covered": []
            }
        
        try:
            # Determine what type of context to include
            include_conversations = True
            include_knowledge = True
            
            # Adjust based on intent
            if intent:
                intent_type = intent.get("primary_intent", "general")
                if intent_type == "troubleshoot":
                    # Prioritize troubleshooting docs and similar issues
                    include_conversations = True
                    include_knowledge = True
                elif intent_type == "learn":
                    # Focus on knowledge and tutorials
                    include_conversations = False
                    include_knowledge = True
                elif intent_type == "query":
                    # Include both for comprehensive answers
                    include_conversations = True
                    include_knowledge = True
            
            # Get RAG context
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
        """Build comprehensive context including RAG knowledge"""
        
        context_parts = []
        
        # Add RAG knowledge context (most important)
        if rag_context["context"]:
            context_parts.append(f"KNOWLEDGE BASE CONTEXT:\n{rag_context['context']}")
        
        # Add conversation history
        if conversation_history:
            context_parts.append(f"RECENT CONVERSATION:\n{conversation_history}")
        
        # Add user intent and topics
        intent_info = f"USER INTENT: {intent.get('primary_intent', 'unknown')}"
        if intent.get("topics"):
            intent_info += f"\nTOPICS: {', '.join(intent['topics'])}"
        if intent.get("urgency") != "normal":
            intent_info += f"\nURGENCY: {intent['urgency']}"
        context_parts.append(intent_info)
        
        # Add DevOps context if available
        if devops_context:
            context_parts.append(f"DEVOPS CONTEXT: {json.dumps(devops_context, indent=2)}")
        
        # Add RAG metadata
        if rag_context["documents_used"] > 0:
            rag_info = f"KNOWLEDGE SOURCES: {rag_context['documents_used']} documents from {len(rag_context['categories_covered'])} categories"
            if rag_context["categories_covered"]:
                rag_info += f" ({', '.join(rag_context['categories_covered'])})"
            context_parts.append(rag_info)
        
        return "\n\n".join(context_parts)

    async def _generate_with_ollama(
        self,
        system_prompt: str,
        context: str,
        user_message: str
    ) -> str:
        """Generate response using Ollama with RAG context"""
        try:
            # Build the prompt with RAG context
            full_prompt = f"""{system_prompt}

{context}

USER MESSAGE: {user_message}

Please provide a helpful response as Jamie, incorporating the knowledge base information where relevant. Be specific and actionable while maintaining Jamie's British personality."""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": full_prompt,
                        "stream": False,
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

    async def _generate_knowledge_response(
        self,
        user_message: str,
        rag_context: Dict[str, Any],
        intent: Optional[Dict],
        personality: Optional[JamiePersonality]
    ) -> str:
        """Generate response using knowledge base when Ollama is unavailable"""
        try:
            # If we have RAG context, use it
            if rag_context["context"]:
                # Extract key information from context
                context_text = rag_context["context"]
                
                # Simple knowledge-based response
                greeting = "Right then! Based on what I know..."
                if personality:
                    greeting = personality.get_thinking_phrase()
                
                # Determine response based on intent
                if intent and intent.get("primary_intent") == "troubleshoot":
                    response = f"{greeting} I've found some relevant troubleshooting information in my knowledge base. Here's what typically works for this issue:\n\n"
                elif intent and intent.get("primary_intent") == "learn":
                    response = f"{greeting} Let me share what I know about this topic from my documentation:\n\n"
                else:
                    response = f"{greeting} Here's what I can tell you based on my knowledge:\n\n"
                
                # Add relevant context snippets
                if len(context_text) > 500:
                    # Truncate and add key points
                    response += context_text[:500] + "...\n\nWould you like me to elaborate on any specific part, mate?"
                else:
                    response += context_text
                
                response += "\n\nHope that helps! Let me know if you need more details on any of this."
                
                return response
            
            # Fallback response when no RAG context
            fallback_responses = {
                "kubernetes": "Right then! For Kubernetes issues, I'd typically recommend checking your pod status with `kubectl get pods` and looking at the logs with `kubectl logs`. What specific problem are you seeing?",
                "monitoring": "Brilliant! For monitoring questions, I usually point folks to check Prometheus metrics and Grafana dashboards. What metrics are you trying to track?",
                "logging": "Good question! For log analysis, Loki's your friend. Try using LogQL queries to filter your logs. What kind of errors are you seeing?",
                "tracing": "Spot on! For tracing issues, Tempo can help you identify bottlenecks. Are you seeing slow requests that need investigation?",
                "git": "Right! For Git and deployment questions, I'd check your repository settings and pipeline status. What's the specific issue you're facing?"
            }
            
            # Try to match user message to categories
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
            
            # Generic fallback
            return "Right then! I'd love to help you with that. Could you give me a bit more detail about what you're trying to accomplish? The more specific you can be, the better I can assist!"
            
        except Exception as e:
            logger.error(f"Error generating knowledge response: {str(e)}")
            return "Sorry mate, I'm having a bit of trouble accessing my knowledge right now. Could you try rephrasing your question?"

    def _select_system_prompt(self, intent: Optional[Dict]) -> str:
        """Select appropriate system prompt based on intent"""
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
        """Calculate confidence score based on RAG context quality"""
        base_confidence = 0.7
        
        # Boost confidence based on RAG context quality
        if rag_context["documents_used"] > 0:
            base_confidence += 0.1
            
            # Additional boost for multiple relevant documents
            if rag_context["documents_used"] >= 3:
                base_confidence += 0.1
            
            # Boost for knowledge base coverage
            if len(rag_context["categories_covered"]) > 1:
                base_confidence += 0.05
        
        # Adjust based on intent confidence
        intent_confidence = intent.get("confidence", 0.5)
        base_confidence = (base_confidence + intent_confidence) / 2
        
        # Boost if we have topic-specific knowledge
        topics = intent.get("topics", [])
        known_topics = [topic for topic in topics if topic in self.devops_categories]
        if known_topics:
            base_confidence += 0.05 * len(known_topics)
        
        return min(base_confidence, 0.95)  # Cap at 95%

    async def _check_ollama_availability(self):
        """Check if Ollama is available and working"""
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

    def _enhance_personality(self, response: str, personality: JamiePersonality, intent: Dict) -> str:
        """Enhance response with Jamie's personality if needed"""
        # Check if response already has British personality
        british_indicators = ["mate", "brilliant", "blimey", "right then", "alright", "cheers"]
        has_personality = any(indicator in response.lower() for indicator in british_indicators)
        
        if not has_personality:
            # Add personality prefix based on intent
            if intent.get("urgency") == "high":
                prefix = personality.get_error_response()
            elif intent.get("primary_intent") == "help":
                prefix = personality.get_general_response()
            else:
                prefix = personality.get_thinking_phrase()
            
            response = f"{prefix} {response}"
        
        return response

    def is_available(self) -> bool:
        """Check if AI brain is available (either Ollama or RAG)"""
        return self.model_available or self.rag_available

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
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

    async def add_knowledge(
        self,
        title: str,
        content: str,
        category: str,
        doc_type: str = "knowledge",
        tags: Optional[List[str]] = None,
        source_url: Optional[str] = None
    ) -> str:
        """Add new knowledge to the RAG system"""
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
        """Search the knowledge base"""
        if not self.rag_available:
            return []
        
        return await self.rag_memory.search_similar_documents(
            query=query,
            doc_types=["knowledge", "runbook", "troubleshoot"],
            categories=categories,
            limit=limit
        )

    async def close(self):
        """Clean up resources"""
        if self.rag_memory:
            await self.rag_memory.close()

# Example usage
if __name__ == "__main__":
    async def test_enhanced_brain():
        brain = JamieBrain()
        await brain.initialize()
        
        print("Brain Status:", brain.get_health_status())
        
        # Test knowledge search
        results = await brain.search_knowledge("kubernetes pod troubleshooting")
        print(f"Knowledge search: {len(results)} results")
        
        # Test response generation
        response = await brain.generate_response(
            user_message="My pods are crashing, what should I do?",
            intent={"primary_intent": "troubleshoot", "topics": ["kubernetes"], "urgency": "high"}
        )
        
        print(f"Response: {response['response'][:100]}...")
        print(f"Confidence: {response['confidence']}")
        print(f"RAG docs used: {response['rag_context_used']}")
        
        await brain.close()
    
    asyncio.run(test_enhanced_brain()) 