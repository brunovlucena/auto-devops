"""
🎯 Jamie's Vector Memory System

Sprint 2: Stores and retrieves conversation interactions for learning
"""

import asyncio
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass, asdict
import pickle
import os

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """A single memory entry in Jamie's vector memory"""
    id: str
    user_message: str
    jamie_response: str
    context: Dict[str, Any]
    session_id: str
    timestamp: datetime
    topics: List[str]
    intent: str
    confidence: float
    user_feedback: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class SimpleEmbedding:
    """
    Simple text embedding using basic TF-IDF approach
    (In production, this would be replaced with proper embeddings from Ollama or similar)
    """
    
    def __init__(self):
        self.vocabulary = {}
        self.idf_scores = {}
        self.documents = []
        
    def fit(self, documents: List[str]):
        """Build vocabulary and IDF scores from documents"""
        self.documents = documents
        
        # Build vocabulary
        word_counts = {}
        doc_word_counts = {}
        
        for doc_idx, doc in enumerate(documents):
            words = self._tokenize(doc)
            doc_words = set(words)
            
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
                
            for word in doc_words:
                doc_word_counts[word] = doc_word_counts.get(word, 0) + 1
        
        # Create vocabulary mapping
        self.vocabulary = {word: idx for idx, word in enumerate(word_counts.keys())}
        
        # Calculate IDF scores
        n_docs = len(documents)
        for word, doc_count in doc_word_counts.items():
            self.idf_scores[word] = np.log(n_docs / (1 + doc_count))
    
    def transform(self, text: str) -> List[float]:
        """Transform text to embedding vector"""
        if not self.vocabulary:
            return [0.0] * 100  # Default embedding size
        
        words = self._tokenize(text)
        word_counts = {}
        
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Create TF-IDF vector
        vector = [0.0] * len(self.vocabulary)
        total_words = len(words)
        
        for word, count in word_counts.items():
            if word in self.vocabulary:
                tf = count / total_words
                idf = self.idf_scores.get(word, 0)
                vector[self.vocabulary[word]] = tf * idf
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        import re
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        return words

class VectorMemory:
    """
    Jamie's Vector Memory System
    
    Features:
    - Store conversation interactions
    - Semantic search for similar interactions
    - Learning from user feedback
    - Memory consolidation and cleanup
    """
    
    def __init__(self, memory_dir: str = "./jamie_memory"):
        self.memory_dir = memory_dir
        self.memories: Dict[str, MemoryEntry] = {}
        self.embedding_model = SimpleEmbedding()
        self.available = False
        
        # Memory configuration
        self.max_memories = 10000
        self.similarity_threshold = 0.7
        self.memory_consolidation_days = 30
        
        # Create memory directory
        os.makedirs(memory_dir, exist_ok=True)
        
        logger.info("VectorMemory initialized")

    async def initialize(self):
        """Initialize the vector memory system"""
        try:
            # Load existing memories
            await self._load_memories()
            
            # Build/update embedding model if we have memories
            if self.memories:
                await self._update_embedding_model()
            
            self.available = True
            logger.info(f"✅ Vector memory initialized with {len(self.memories)} memories")
            
        except Exception as e:
            logger.warning(f"⚠️ Vector memory initialization failed: {str(e)}")
            self.available = False

    def is_available(self) -> bool:
        """Check if vector memory is available"""
        return self.available

    def get_collection_count(self) -> int:
        """Get number of stored memories"""
        return len(self.memories)

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of vector memory"""
        return {
            "available": self.available,
            "memory_count": len(self.memories),
            "memory_dir": self.memory_dir,
            "max_memories": self.max_memories,
            "embedding_vocab_size": len(self.embedding_model.vocabulary)
        }

    async def store_interaction(
        self,
        user_message: str,
        jamie_response: str,
        context: Dict[str, Any],
        session_id: str,
        topics: Optional[List[str]] = None,
        intent: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> str:
        """Store a conversation interaction in memory"""
        try:
            # Create memory ID
            memory_id = self._generate_memory_id(user_message, jamie_response, session_id)
            
            # Extract topics and intent if not provided
            if not topics:
                topics = self._extract_topics(user_message)
            if not intent:
                intent = self._extract_intent(user_message)
            if confidence is None:
                confidence = 0.5
            
            # Create memory entry
            memory = MemoryEntry(
                id=memory_id,
                user_message=user_message,
                jamie_response=jamie_response,
                context=context,
                session_id=session_id,
                timestamp=datetime.now(),
                topics=topics,
                intent=intent,
                confidence=confidence
            )
            
            # Generate embedding for the interaction
            combined_text = f"{user_message} {jamie_response}"
            if self.embedding_model.vocabulary:
                memory.embedding = self.embedding_model.transform(combined_text)
            
            # Store memory
            self.memories[memory_id] = memory
            
            # Save to disk periodically
            if len(self.memories) % 10 == 0:
                await self._save_memories()
            
            # Update embedding model if needed
            if len(self.memories) % 100 == 0:
                await self._update_embedding_model()
            
            # Cleanup old memories if needed
            if len(self.memories) > self.max_memories:
                await self._cleanup_old_memories()
            
            logger.debug(f"Stored memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return ""

    async def search_similar_interactions(
        self,
        query: str,
        limit: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for similar interactions in memory"""
        try:
            if not self.memories or not self.embedding_model.vocabulary:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.transform(query)
            
            # Calculate similarities
            similarities = []
            for memory_id, memory in self.memories.items():
                if memory.embedding:
                    similarity = self._calculate_similarity(query_embedding, memory.embedding)
                    if similarity >= min_similarity:
                        similarities.append((similarity, memory))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for similarity, memory in similarities[:limit]:
                result = {
                    "memory_id": memory.id,
                    "similarity": similarity,
                    "user_message": memory.user_message,
                    "jamie_response": memory.jamie_response,
                    "topics": memory.topics,
                    "intent": memory.intent,
                    "confidence": memory.confidence,
                    "timestamp": memory.timestamp.isoformat(),
                    "summary": f"User asked about {', '.join(memory.topics)} - Jamie {memory.intent}"
                }
                results.append(result)
            
            logger.debug(f"Found {len(results)} similar interactions for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return []

    async def add_feedback(self, memory_id: str, feedback: Dict[str, Any]) -> bool:
        """Add user feedback to a memory entry"""
        try:
            if memory_id in self.memories:
                self.memories[memory_id].user_feedback = feedback
                
                # Adjust confidence based on feedback
                if feedback.get("helpful", False):
                    self.memories[memory_id].confidence = min(
                        self.memories[memory_id].confidence + 0.1, 1.0
                    )
                elif feedback.get("helpful", False) is False:
                    self.memories[memory_id].confidence = max(
                        self.memories[memory_id].confidence - 0.1, 0.0
                    )
                
                await self._save_memories()
                logger.debug(f"Added feedback to memory: {memory_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            return False

    async def get_conversation_patterns(self, session_id: str) -> Dict[str, Any]:
        """Analyze patterns in a conversation session"""
        try:
            session_memories = [
                memory for memory in self.memories.values()
                if memory.session_id == session_id
            ]
            
            if not session_memories:
                return {}
            
            # Analyze patterns
            topics = []
            intents = []
            confidence_scores = []
            
            for memory in session_memories:
                topics.extend(memory.topics)
                intents.append(memory.intent)
                confidence_scores.append(memory.confidence)
            
            # Calculate statistics
            unique_topics = list(set(topics))
            unique_intents = list(set(intents))
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            return {
                "session_id": session_id,
                "total_interactions": len(session_memories),
                "topics_discussed": unique_topics,
                "intent_types": unique_intents,
                "average_confidence": avg_confidence,
                "session_duration": (
                    session_memories[-1].timestamp - session_memories[0].timestamp
                ).total_seconds() / 60 if len(session_memories) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {str(e)}")
            return {}

    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about Jamie's learning from memories"""
        try:
            if not self.memories:
                return {"total_memories": 0}
            
            # Analyze all memories
            topics = []
            intents = []
            confidence_scores = []
            feedback_scores = []
            
            for memory in self.memories.values():
                topics.extend(memory.topics)
                intents.append(memory.intent)
                confidence_scores.append(memory.confidence)
                
                if memory.user_feedback:
                    if memory.user_feedback.get("helpful", False):
                        feedback_scores.append(1)
                    elif memory.user_feedback.get("helpful", False) is False:
                        feedback_scores.append(0)
            
            # Calculate insights
            topic_counts = {}
            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            intent_counts = {}
            for intent in intents:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            return {
                "total_memories": len(self.memories),
                "average_confidence": sum(confidence_scores) / len(confidence_scores),
                "most_common_topics": sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "most_common_intents": sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "positive_feedback_rate": (
                    sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0
                ),
                "memories_with_feedback": len(feedback_scores),
                "memory_age_days": (datetime.now() - min(
                    memory.timestamp for memory in self.memories.values()
                )).days if self.memories else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating learning insights: {str(e)}")
            return {"error": str(e)}

    def _generate_memory_id(self, user_message: str, jamie_response: str, session_id: str) -> str:
        """Generate unique memory ID"""
        content = f"{user_message}{jamie_response}{session_id}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()

    def _extract_topics(self, message: str) -> List[str]:
        """Extract topics from message"""
        topics = []
        message_lower = message.lower()
        
        topic_keywords = {
            "kubernetes": ["k8s", "pods", "cluster", "deployment", "service"],
            "monitoring": ["prometheus", "grafana", "alerts", "metrics", "cpu", "memory"],
            "logging": ["loki", "logs", "errors", "debugging"],
            "tracing": ["tempo", "traces", "performance", "latency"],
            "git": ["github", "git", "commit", "pr", "pipeline"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics or ["general"]

    def _extract_intent(self, message: str) -> str:
        """Extract intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["help", "what can you do"]):
            return "help"
        elif any(word in message_lower for word in ["error", "problem", "broken", "down"]):
            return "troubleshoot"
        elif any(word in message_lower for word in ["how", "what", "status", "check"]):
            return "query"
        else:
            return "general"

    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0

    async def _update_embedding_model(self):
        """Update the embedding model with current memories"""
        try:
            if not self.memories:
                return
            
            # Collect all texts for training
            texts = []
            for memory in self.memories.values():
                combined_text = f"{memory.user_message} {memory.jamie_response}"
                texts.append(combined_text)
            
            # Retrain embedding model
            self.embedding_model.fit(texts)
            
            # Update embeddings for all memories
            for memory in self.memories.values():
                combined_text = f"{memory.user_message} {memory.jamie_response}"
                memory.embedding = self.embedding_model.transform(combined_text)
            
            logger.debug("Updated embedding model")
            
        except Exception as e:
            logger.error(f"Error updating embedding model: {str(e)}")

    async def _save_memories(self):
        """Save memories to disk"""
        try:
            memories_file = os.path.join(self.memory_dir, "memories.json")
            embedding_file = os.path.join(self.memory_dir, "embeddings.pkl")
            
            # Save memories as JSON
            memories_data = {
                memory_id: memory.to_dict()
                for memory_id, memory in self.memories.items()
            }
            
            with open(memories_file, 'w') as f:
                json.dump(memories_data, f, indent=2)
            
            # Save embedding model
            with open(embedding_file, 'wb') as f:
                pickle.dump(self.embedding_model, f)
            
            logger.debug(f"Saved {len(self.memories)} memories to disk")
            
        except Exception as e:
            logger.error(f"Error saving memories: {str(e)}")

    async def _load_memories(self):
        """Load memories from disk"""
        try:
            memories_file = os.path.join(self.memory_dir, "memories.json")
            embedding_file = os.path.join(self.memory_dir, "embeddings.pkl")
            
            # Load memories
            if os.path.exists(memories_file):
                with open(memories_file, 'r') as f:
                    memories_data = json.load(f)
                
                self.memories = {
                    memory_id: MemoryEntry.from_dict(data)
                    for memory_id, data in memories_data.items()
                }
                
                logger.debug(f"Loaded {len(self.memories)} memories from disk")
            
            # Load embedding model
            if os.path.exists(embedding_file):
                with open(embedding_file, 'rb') as f:
                    self.embedding_model = pickle.load(f)
                
                logger.debug("Loaded embedding model from disk")
            
        except Exception as e:
            logger.error(f"Error loading memories: {str(e)}")

    async def _cleanup_old_memories(self):
        """Clean up old memories to maintain size limit"""
        try:
            if len(self.memories) <= self.max_memories:
                return
            
            # Sort memories by timestamp (oldest first)
            sorted_memories = sorted(
                self.memories.items(),
                key=lambda x: x[1].timestamp
            )
            
            # Remove oldest memories, keeping only max_memories
            memories_to_remove = len(self.memories) - self.max_memories
            
            for i in range(memories_to_remove):
                memory_id = sorted_memories[i][0]
                del self.memories[memory_id]
            
            logger.info(f"Cleaned up {memories_to_remove} old memories")
            
        except Exception as e:
            logger.error(f"Error cleaning up memories: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    async def test_vector_memory():
        memory = VectorMemory()
        await memory.initialize()
        
        print("Vector Memory Status:", memory.get_status())
        
        # Test storing interactions
        memory_id = await memory.store_interaction(
            user_message="How do I check my pods?",
            jamie_response="Right then! Use 'kubectl get pods' to see your pod status, mate!",
            context={"namespace": "default"},
            session_id="test_session",
            topics=["kubernetes"],
            intent="query",
            confidence=0.8
        )
        
        print(f"Stored memory: {memory_id}")
        
        # Test searching
        results = await memory.search_similar_interactions("pod status check")
        print(f"Search results: {len(results)}")
        for result in results:
            print(f"- {result['summary']} (similarity: {result['similarity']:.2f})")
        
        # Test insights
        insights = await memory.get_learning_insights()
        print("Learning insights:", insights)
    
    # Run test
    asyncio.run(test_vector_memory()) 