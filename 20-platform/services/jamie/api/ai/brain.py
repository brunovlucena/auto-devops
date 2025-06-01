"""
🧠 Jamie's AI Brain - Core Intelligence System

Sprint 2: Integrates with Ollama/LLM for intelligent DevOps responses
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import os

from ..personality import JamiePersonality

logger = logging.getLogger(__name__)

class JamieBrain:
    """
    Jamie's AI Brain - Core intelligence system
    
    Features:
    - Ollama LLM integration
    - DevOps-specific knowledge
    - Context-aware response generation
    - Learning from interactions
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
        
        # DevOps knowledge base
        self.devops_knowledge = {
            "kubernetes": {
                "concepts": ["pods", "deployments", "services", "ingress", "configmaps", "secrets"],
                "troubleshooting": ["CrashLoopBackOff", "ImagePullBackOff", "Pending", "Failed"],
                "commands": ["kubectl get", "kubectl describe", "kubectl logs", "kubectl exec"]
            },
            "monitoring": {
                "metrics": ["CPU", "memory", "disk", "network", "latency", "error_rate"],
                "tools": ["Prometheus", "Grafana", "AlertManager"],
                "queries": ["rate()", "histogram_quantile()", "increase()"]
            },
            "logging": {
                "levels": ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"],
                "tools": ["Loki", "Elasticsearch", "Fluentd"],
                "patterns": ["error patterns", "performance issues", "security events"]
            },
            "tracing": {
                "concepts": ["spans", "traces", "sampling", "baggage"],
                "tools": ["Tempo", "Jaeger", "Zipkin"],
                "analysis": ["latency", "errors", "dependencies"]
            }
        }
        
        # System prompts for different contexts
        self.system_prompts = {
            "base": """You are Jamie, a friendly British AI DevOps copilot. You help developers and ops teams with infrastructure questions.

PERSONALITY:
- Use British expressions: "mate", "brilliant", "blimey", "right then"
- Be friendly, helpful, and professional
- Show enthusiasm for solving problems
- Be humble when you don't know something

DEVOPS EXPERTISE:
- Kubernetes cluster management
- Prometheus monitoring and alerting
- Loki log analysis
- Tempo distributed tracing
- GitHub repository management

RESPONSE STYLE:
- Start with a British greeting or expression
- Provide clear, actionable advice
- Include relevant commands or queries when helpful
- End with encouragement or next steps""",

            "troubleshooting": """You are Jamie helping with a DevOps issue. The user is experiencing problems.

APPROACH:
1. Show empathy: "Blimey, that's not ideal!"
2. Ask clarifying questions if needed
3. Provide step-by-step troubleshooting
4. Suggest monitoring and prevention
5. Be encouraging: "We'll get this sorted!"

FOCUS ON:
- Root cause analysis
- Immediate fixes
- Long-term prevention
- Monitoring improvements""",

            "learning": """You are Jamie helping someone learn DevOps concepts.

TEACHING STYLE:
- Start with basics: "Right then, let's break this down"
- Use analogies and examples
- Provide hands-on commands
- Encourage experimentation: "Give it a go!"
- Build confidence: "You're getting the hang of it!"

STRUCTURE:
1. Explain the concept simply
2. Show practical examples
3. Provide commands to try
4. Suggest next steps"""
        }
        
        logger.info("JamieBrain initialized")

    async def initialize(self):
        """Initialize the AI brain and check Ollama availability"""
        try:
            # Check if Ollama is running
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_host}/api/tags")
                if response.status_code == 200:
                    models = response.json()
                    available_models = [model["name"] for model in models.get("models", [])]
                    
                    if self.model_name in available_models:
                        self.model_available = True
                        logger.info(f"✅ Ollama model '{self.model_name}' is available")
                    else:
                        logger.warning(f"⚠️ Model '{self.model_name}' not found. Available: {available_models}")
                        # Try to pull the model
                        await self._pull_model()
                else:
                    logger.warning(f"⚠️ Ollama not responding at {self.ollama_host}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Ollama: {str(e)}")
            self.model_available = False

    async def _pull_model(self):
        """Pull the required model from Ollama"""
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                logger.info(f"📥 Pulling model '{self.model_name}' from Ollama...")
                response = await client.post(
                    f"{self.ollama_host}/api/pull",
                    json={"name": self.model_name}
                )
                if response.status_code == 200:
                    self.model_available = True
                    logger.info(f"✅ Successfully pulled model '{self.model_name}'")
                else:
                    logger.error(f"❌ Failed to pull model: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error pulling model: {str(e)}")

    def is_available(self) -> bool:
        """Check if the AI brain is available"""
        return self.model_available

    def get_model_info(self) -> str:
        """Get information about the current model"""
        if self.model_available:
            return f"{self.model_name} (Ollama)"
        return "Not available"

    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status of the AI brain"""
        return {
            "available": self.model_available,
            "model": self.model_name,
            "ollama_host": self.ollama_host,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "knowledge_areas": list(self.devops_knowledge.keys())
        }

    async def generate_response(
        self,
        user_message: str,
        conversation_history: str,
        intent: Dict[str, Any],
        relevant_memories: List[Dict],
        devops_context: Optional[Dict] = None,
        personality: Optional[JamiePersonality] = None
    ) -> Dict[str, Any]:
        """
        Generate an intelligent response using the AI brain
        """
        if not self.model_available:
            return {
                "response": "Sorry mate, my AI brain isn't available right now. Running in basic mode!",
                "confidence": 0.3,
                "intent": intent.get("primary_intent", "unknown"),
                "topics": intent.get("topics", [])
            }

        try:
            # Select appropriate system prompt
            system_prompt = self._select_system_prompt(intent)
            
            # Build context for the AI
            context = self._build_context(
                user_message=user_message,
                conversation_history=conversation_history,
                intent=intent,
                relevant_memories=relevant_memories,
                devops_context=devops_context
            )
            
            # Generate response using Ollama
            response_text = await self._call_ollama(
                system_prompt=system_prompt,
                user_context=context,
                user_message=user_message
            )
            
            # Post-process response to ensure Jamie's personality
            if personality:
                response_text = self._enhance_personality(response_text, personality, intent)
            
            return {
                "response": response_text,
                "confidence": self._calculate_confidence(intent, relevant_memories),
                "intent": intent.get("primary_intent", "general"),
                "topics": intent.get("topics", [])
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            fallback_response = "Blimey! My brain's having a bit of a wobble. Let me try a different approach..."
            if personality:
                fallback_response = personality.get_error_response() + " Give me a tick to sort myself out!"
            
            return {
                "response": fallback_response,
                "confidence": 0.2,
                "intent": "error",
                "topics": []
            }

    def _select_system_prompt(self, intent: Dict[str, Any]) -> str:
        """Select the appropriate system prompt based on user intent"""
        if intent.get("primary_intent") == "troubleshoot" or intent.get("urgency") == "high":
            return self.system_prompts["troubleshooting"]
        elif intent.get("primary_intent") == "help" or "learning" in intent.get("topics", []):
            return self.system_prompts["learning"]
        else:
            return self.system_prompts["base"]

    def _build_context(
        self,
        user_message: str,
        conversation_history: str,
        intent: Dict[str, Any],
        relevant_memories: List[Dict],
        devops_context: Optional[Dict]
    ) -> str:
        """Build comprehensive context for the AI"""
        
        context_parts = []
        
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
        
        # Add relevant memories
        if relevant_memories:
            memory_context = "RELEVANT PAST INTERACTIONS:\n"
            for memory in relevant_memories[:2]:  # Limit to 2 most relevant
                memory_context += f"- {memory.get('summary', 'Previous interaction')}\n"
            context_parts.append(memory_context)
        
        # Add DevOps context if available
        if devops_context:
            context_parts.append(f"DEVOPS CONTEXT: {json.dumps(devops_context, indent=2)}")
        
        # Add relevant DevOps knowledge
        topics = intent.get("topics", [])
        for topic in topics:
            if topic in self.devops_knowledge:
                knowledge = self.devops_knowledge[topic]
                knowledge_text = f"\n{topic.upper()} KNOWLEDGE:\n"
                for key, values in knowledge.items():
                    if isinstance(values, list):
                        knowledge_text += f"- {key}: {', '.join(values[:5])}\n"  # Limit items
                    else:
                        knowledge_text += f"- {key}: {values}\n"
                context_parts.append(knowledge_text)
        
        return "\n\n".join(context_parts)

    async def _call_ollama(self, system_prompt: str, user_context: str, user_message: str) -> str:
        """Make API call to Ollama"""
        try:
            prompt = f"{system_prompt}\n\nCONTEXT:\n{user_context}\n\nUSER: {user_message}\n\nJAMIE:"
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens,
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return "Sorry mate, having trouble with my AI brain right now!"
                    
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            raise

    def _enhance_personality(self, response: str, personality: JamiePersonality, intent: Dict) -> str:
        """Enhance the response with Jamie's personality if needed"""
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

    def _calculate_confidence(self, intent: Dict, relevant_memories: List) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.7
        
        # Adjust based on intent confidence
        intent_confidence = intent.get("confidence", 0.5)
        base_confidence = (base_confidence + intent_confidence) / 2
        
        # Boost if we have relevant memories
        if relevant_memories:
            base_confidence += 0.1
        
        # Boost if we have topic-specific knowledge
        topics = intent.get("topics", [])
        known_topics = [topic for topic in topics if topic in self.devops_knowledge]
        if known_topics:
            base_confidence += 0.1 * len(known_topics)
        
        return min(base_confidence, 0.95)  # Cap at 95%

    async def learn_from_feedback(self, feedback_data: Dict[str, Any]):
        """Learn from user feedback to improve responses"""
        try:
            # Log feedback for future training
            logger.info(f"Received feedback: {feedback_data}")
            
            # TODO: Implement feedback learning mechanism
            # This could involve:
            # - Storing feedback in vector memory
            # - Adjusting confidence scores
            # - Fine-tuning response patterns
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """Get information about Jamie's AI capabilities"""
        return {
            "model": self.model_name,
            "available": self.model_available,
            "knowledge_areas": list(self.devops_knowledge.keys()),
            "capabilities": [
                "Natural language understanding",
                "DevOps troubleshooting",
                "Code and command suggestions",
                "Context-aware responses",
                "Personality-infused interactions",
                "Learning from feedback"
            ],
            "system_prompts": list(self.system_prompts.keys())
        }

# Example usage and testing
if __name__ == "__main__":
    async def test_jamie_brain():
        brain = JamieBrain()
        await brain.initialize()
        
        print("Jamie Brain Status:", brain.get_health_status())
        print("Capabilities:", brain.get_capabilities())
        
        if brain.is_available():
            # Test response generation
            intent = {"primary_intent": "query", "topics": ["kubernetes"], "confidence": 0.8}
            response = await brain.generate_response(
                user_message="How do I check if my pods are running?",
                conversation_history="",
                intent=intent,
                relevant_memories=[],
                devops_context=None
            )
            print("Test Response:", response)
    
    # Run test
    asyncio.run(test_jamie_brain()) 