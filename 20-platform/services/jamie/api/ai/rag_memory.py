"""
🧠 Jamie's MongoDB RAG Memory System

Enhanced vector memory with MongoDB Atlas Search for proper RAG (Retrieval-Augmented Generation)
Stores conversations, DevOps knowledge base, and provides semantic search

⭐ WHAT THIS FILE DOES:
    - Stores conversations and knowledge in MongoDB with vector embeddings
    - Provides semantic search for finding relevant information
    - Uses Ollama for generating text embeddings
    - Seeds the database with DevOps best practices
    - Supports fallback text search when vector search fails
"""

import asyncio
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
import os
from dataclasses import dataclass, asdict

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 DEPENDENCY IMPORTS - Try to import MongoDB, handle gracefully if missing
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from motor.motor_asyncio import AsyncIOMotorClient  # Async MongoDB client
    from pymongo import IndexModel, TEXT                # MongoDB indexing
    MONGODB_AVAILABLE = True
except ImportError:
    # 🚨 MongoDB not installed - we'll handle this gracefully
    MONGODB_AVAILABLE = False
    AsyncIOMotorClient = None

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 DATA STRUCTURES - Classes that define our data models
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RAGDocument:
    """
    🏗️ A single document in Jamie's RAG knowledge base
    
    This represents ANY piece of information we store:
    - Conversations between users and Jamie
    - Knowledge base articles (like troubleshooting guides)
    - Runbooks and procedures
    - Best practices documentation
    """
    
    # 🆔 IDENTIFICATION
    id: str                                    # Unique identifier for this document
    title: str                                 # Human-readable title
    content: str                              # The actual text content
    
    # 📂 CATEGORIZATION 
    doc_type: str                             # 'conversation', 'knowledge', 'runbook', 'troubleshoot'
    category: str                             # 'kubernetes', 'monitoring', 'logging', 'tracing', 'git'
    tags: List[str]                           # Keywords for searching
    
    # 🔢 VECTOR DATA
    embedding: Optional[List[float]] = None    # Vector representation for similarity search
    
    # 📝 METADATA
    metadata: Optional[Dict[str, Any]] = None  # Extra info (session_id, context, etc.)
    created_at: datetime = None               # When this was created
    updated_at: datetime = None               # When this was last modified
    confidence: float = 1.0                   # How confident we are in this info
    source_url: Optional[str] = None          # Where this came from (if external)
    
    def __post_init__(self):
        """🕐 Auto-set timestamps if not provided"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        📤 Convert to dictionary for MongoDB storage
        
        MongoDB stores documents as dictionaries, so we need to convert
        our dataclass to a dict and handle datetime serialization
        """
        data = asdict(self)
        # Convert datetimes to ISO strings for JSON compatibility
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGDocument':
        """
        📥 Create from MongoDB document
        
        When we read from MongoDB, we get dictionaries back.
        This converts them back to our RAGDocument objects
        """
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 OLLAMA EMBEDDINGS - Converts text to vectors for similarity search
# ═══════════════════════════════════════════════════════════════════════════════

class OllamaEmbeddings:
    """
    🎯 Ollama-based embedding generation for RAG
    
    WHAT IT DOES:
    - Takes text and converts it to a vector (list of numbers)
    - These vectors represent the "meaning" of the text
    - Similar texts have similar vectors
    - We can then do math to find similar documents
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """🔧 Set up connection to Ollama"""
        self.base_url = base_url          # Where Ollama is running
        self.model = model                # Which model to use for embeddings
        self.available = False            # Whether we can actually use it
        
    async def initialize(self):
        """
        🚀 Check if Ollama is available and working
        
        STEPS:
        1. Try to connect to Ollama
        2. Check if it responds
        3. Set available flag based on result
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    self.available = True
                    logger.info("✅ Ollama embeddings available")
                else:
                    logger.warning("⚠️ Ollama not available for embeddings")
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Ollama: {str(e)}")
            self.available = False
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        🔢 Generate embeddings for text using Ollama
        
        PROCESS:
        1. Check if Ollama is available
        2. Send text to Ollama's embedding API
        3. Get back a vector (list of numbers)
        4. Return the vector or None if failed
        """
        if not self.available:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("embedding", [])
                else:
                    logger.error(f"Ollama embedding error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        📊 Generate embeddings for multiple texts
        
        This is useful when we need to process many documents at once.
        We'll call embed_text for each one (could be optimized later).
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings

# ═══════════════════════════════════════════════════════════════════════════════
# 🗄️ MAIN RAG MEMORY CLASS - The heart of our knowledge system
# ═══════════════════════════════════════════════════════════════════════════════

class MongoRAGMemory:
    """
    🧠 MongoDB-based RAG Memory System for Jamie
    
    ⭐ MAIN FEATURES:
    - Vector search using MongoDB Atlas Search
    - DevOps knowledge base storage
    - Conversation memory with embeddings
    - Semantic search for RAG
    - Knowledge base management
    
    💡 HOW IT WORKS:
    1. Store documents (conversations, knowledge) in MongoDB
    2. Generate embeddings for each document
    3. When user asks a question, find similar documents
    4. Use those documents as context for AI responses
    """
    
    def __init__(self, mongodb_url: str = None, database_name: str = "jamie_rag"):
        """
        🔧 Initialize the RAG memory system
        
        SETUP:
        - Configure MongoDB connection
        - Set up Ollama embeddings
        - Define collection names
        - Set configuration limits
        """
        # 🔗 DATABASE CONNECTION
        self.mongodb_url = mongodb_url or os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = database_name
        self.client = None                # MongoDB client (set during initialization)
        self.db = None                    # Database reference
        self.available = False            # Whether the system is ready to use
        
        # 📂 COLLECTIONS (think of these as tables in a database)
        self.conversations_collection = None    # User conversations with Jamie
        self.knowledge_collection = None        # Knowledge base articles
        self.embeddings_collection = None       # Vector embeddings (if needed separately)
        
        # 🤖 EMBEDDING SYSTEM
        self.embeddings = OllamaEmbeddings()
        
        # ⚙️ CONFIGURATION LIMITS
        self.max_documents = 50000              # Don't store more than this
        self.similarity_threshold = 0.7         # Minimum similarity for matches
        self.embedding_dimension = 4096         # Llama 3.1 embedding dimension
        
        logger.info("MongoRAGMemory initialized")

    async def initialize(self):
        """
        🚀 Initialize MongoDB connection and collections
        
        BIG PICTURE STEPS:
        1. Check if MongoDB dependencies are available
        2. Initialize Ollama embeddings
        3. Connect to MongoDB
        4. Set up database collections
        5. Create indexes for fast searching
        6. Seed knowledge base if empty
        """
        # ❌ DEPENDENCY CHECK
        if not MONGODB_AVAILABLE:
            logger.error("❌ MongoDB dependencies not available. Install: pip install motor pymongo")
            return False
            
        try:
            # 🤖 STEP 1: Initialize Ollama embeddings
            await self.embeddings.initialize()
            
            # 🔗 STEP 2: Connect to MongoDB
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # 🏥 STEP 3: Test connection (ping the database)
            await self.client.admin.command('ping')
            
            # 📂 STEP 4: Initialize collections
            self.conversations_collection = self.db.conversations
            self.knowledge_collection = self.db.knowledge_base
            self.embeddings_collection = self.db.embeddings
            
            # 🗂️ STEP 5: Create indexes for fast searching
            await self._create_indexes()
            
            # 📚 STEP 6: Load initial knowledge base if empty
            knowledge_count = await self.knowledge_collection.count_documents({})
            if knowledge_count == 0:
                await self._seed_devops_knowledge()
            
            # ✅ SUCCESS! Mark as available
            self.available = True
            logger.info(f"✅ MongoDB RAG Memory initialized with {knowledge_count} knowledge documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MongoDB RAG Memory: {str(e)}")
            self.available = False
            return False

    async def _create_indexes(self):
        """
        🗂️ Create necessary indexes for efficient search
        
        INDEXES ARE LIKE BOOKMARKS:
        - They make searching much faster
        - Without them, MongoDB has to scan every document
        - With them, MongoDB can jump directly to relevant documents
        
        WE CREATE INDEXES FOR:
        - Text search on content and titles
        - Category filtering
        - Tag searching
        - Timestamp sorting
        """
        try:
            # 📝 TEXT SEARCH INDEXES - for keyword searching
            await self.conversations_collection.create_index([("content", TEXT), ("title", TEXT)])
            await self.knowledge_collection.create_index([("content", TEXT), ("title", TEXT)])
            
            # 📂 CATEGORY AND TAG INDEXES - for filtering
            await self.conversations_collection.create_index("category")
            await self.knowledge_collection.create_index("category")
            await self.knowledge_collection.create_index("tags")
            
            # 🕐 TIMESTAMP INDEXES - for sorting by date
            await self.conversations_collection.create_index("created_at")
            await self.knowledge_collection.create_index("updated_at")
            
            # 🔢 VECTOR SEARCH INDEX (for Atlas Search)
            # NOTE: This needs to be created in MongoDB Atlas UI or via API
            # We can't create vector search indexes programmatically with motor
            logger.debug("Database indexes created")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 💾 STORING DATA - Save conversations and knowledge
    # ═══════════════════════════════════════════════════════════════════════════════

    async def store_conversation(
        self,
        user_message: str,
        jamie_response: str,
        context: Dict[str, Any],
        session_id: str,
        topics: Optional[List[str]] = None,
        intent: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> str:
        """
        💬 Store a conversation with embeddings for RAG
        
        WHAT THIS DOES:
        1. Take a user question and Jamie's response
        2. Extract topics and categorize the conversation
        3. Generate an embedding (vector) for the conversation
        4. Store everything in MongoDB for future searching
        
        RETURNS: Document ID if successful, empty string if failed
        """
        if not self.available:
            return ""
            
        try:
            # 🆔 STEP 1: Create unique document ID
            doc_id = self._generate_id(user_message, jamie_response, session_id)
            
            # 🏷️ STEP 2: Extract topics if not provided
            if not topics:
                topics = self._extract_topics(user_message + " " + jamie_response)
            
            # 📂 STEP 3: Determine primary category
            category = self._determine_category(topics)
            
            # 📝 STEP 4: Create conversation content for embedding
            conversation_content = f"User: {user_message}\nJamie: {jamie_response}"
            
            # 🔢 STEP 5: Generate embedding (vector representation)
            embedding = await self.embeddings.embed_text(conversation_content)
            
            # 🏗️ STEP 6: Create RAG document
            doc = RAGDocument(
                id=doc_id,
                title=f"Conversation: {user_message[:50]}...",
                content=conversation_content,
                doc_type="conversation",
                category=category,
                tags=topics or [],
                embedding=embedding,
                metadata={
                    "session_id": session_id,
                    "intent": intent or "unknown",
                    "confidence": confidence or 0.5,
                    "context": context
                }
            )
            
            # 💾 STEP 7: Store in MongoDB
            await self.conversations_collection.insert_one(doc.to_dict())
            
            logger.debug(f"Stored conversation: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
            return ""

    async def store_knowledge(
        self,
        title: str,
        content: str,
        category: str,
        doc_type: str = "knowledge",
        tags: Optional[List[str]] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        📚 Store knowledge base document with embeddings
        
        WHAT THIS DOES:
        1. Take a knowledge article (like a troubleshooting guide)
        2. Generate an embedding for it
        3. Store it in the knowledge base
        4. Make it searchable for future questions
        
        EXAMPLES OF KNOWLEDGE:
        - "How to troubleshoot Kubernetes pods"
        - "Prometheus alerting best practices"
        - "Common Docker issues and solutions"
        """
        if not self.available:
            return ""
            
        try:
            # 🆔 STEP 1: Create unique document ID
            doc_id = self._generate_id(title, content, category)
            
            # 🔢 STEP 2: Generate embedding for title + content
            embedding_text = f"{title}\n{content}"
            embedding = await self.embeddings.embed_text(embedding_text)
            
            # 🏗️ STEP 3: Create RAG document
            doc = RAGDocument(
                id=doc_id,
                title=title,
                content=content,
                doc_type=doc_type,
                category=category,
                tags=tags or [],
                embedding=embedding,
                metadata=metadata or {},
                source_url=source_url
            )
            
            # 💾 STEP 4: Store in MongoDB (upsert = insert or update)
            await self.knowledge_collection.replace_one(
                {"id": doc_id},        # Find document with this ID
                doc.to_dict(),         # Replace with new content
                upsert=True            # Create if doesn't exist
            )
            
            logger.debug(f"Stored knowledge: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing knowledge: {str(e)}")
            return ""

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔍 SEARCHING DATA - Find relevant information
    # ═══════════════════════════════════════════════════════════════════════════════

    async def search_similar_documents(
        self,
        query: str,
        doc_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        limit: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        🔍 Search for similar documents using vector similarity
        
        HOW VECTOR SEARCH WORKS:
        1. Convert the query to a vector (using Ollama)
        2. Compare this vector to all stored document vectors
        3. Find documents with similar vectors (similar meaning)
        4. Return the most similar ones
        
        PARAMETERS:
        - query: What the user is asking about
        - doc_types: Filter by document type (e.g., only "knowledge")
        - categories: Filter by category (e.g., only "kubernetes")
        - limit: Maximum number of results to return
        - min_similarity: Only return results above this similarity score
        """
        if not self.available:
            return []
            
        try:
            # 🔢 STEP 1: Generate query embedding
            query_embedding = await self.embeddings.embed_text(query)
            if not query_embedding:
                # If we can't generate embeddings, fall back to text search
                return await self._fallback_text_search(query, doc_types, categories, limit)
            
            # 🏗️ STEP 2: Build MongoDB aggregation pipeline for vector search
            pipeline = []
            
            # 🔽 FILTERING: Apply filters if specified
            match_filter = {}
            if doc_types:
                match_filter["doc_type"] = {"$in": doc_types}
            if categories:
                match_filter["category"] = {"$in": categories}
            
            if match_filter:
                pipeline.append({"$match": match_filter})
            
            # 🧮 STEP 3: Calculate similarity scores
            # This is complex MongoDB math that computes cosine similarity
            pipeline.extend([
                {
                    "$addFields": {
                        "similarity": {
                            "$reduce": {
                                "input": {"$zip": {"inputs": ["$embedding", query_embedding]}},
                                "initialValue": 0,
                                "in": {"$add": ["$$value", {"$multiply": [{"$arrayElemAt": ["$$this", 0]}, {"$arrayElemAt": ["$$this", 1]}]}]}
                            }
                        }
                    }
                },
                {"$match": {"similarity": {"$gte": min_similarity}}},    # Filter by minimum similarity
                {"$sort": {"similarity": -1}},                          # Sort by similarity (highest first)
                {"$limit": limit}                                       # Limit results
            ])
            
            # 🔍 STEP 4: Search both collections
            results = []
            
            # Search conversations
            async for doc in self.conversations_collection.aggregate(pipeline):
                results.append(self._format_search_result(doc))
            
            # Search knowledge base
            async for doc in self.knowledge_collection.aggregate(pipeline):
                results.append(self._format_search_result(doc))
            
            # 📊 STEP 5: Sort all results by similarity and limit
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.debug(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            # If vector search fails, try text search
            return await self._fallback_text_search(query, doc_types, categories, limit)

    async def get_rag_context(
        self,
        query: str,
        max_context_length: int = 4000,
        include_conversations: bool = True,
        include_knowledge: bool = True
    ) -> Dict[str, Any]:
        """
        🎯 Get RAG context for a query including relevant documents
        
        THIS IS THE MAGIC! 🪄
        When a user asks a question, this function:
        1. Finds relevant documents (conversations + knowledge)
        2. Combines them into context text
        3. Returns formatted context for the AI to use
        
        RESULT: The AI gets relevant background information to answer better
        
        PARAMETERS:
        - query: What the user is asking
        - max_context_length: Don't exceed this many characters
        - include_conversations: Include past conversations?
        - include_knowledge: Include knowledge base articles?
        """
        try:
            # 📋 STEP 1: Determine what types of documents to search
            doc_types = []
            if include_conversations:
                doc_types.append("conversation")
            if include_knowledge:
                doc_types.extend(["knowledge", "runbook", "troubleshoot"])
            
            # 🔍 STEP 2: Search for relevant documents
            relevant_docs = await self.search_similar_documents(
                query=query,
                doc_types=doc_types,
                limit=8,                    # Look at top 8 results
                min_similarity=0.3          # Minimum similarity threshold
            )
            
            # 📝 STEP 3: Build context text
            context_parts = []
            current_length = 0
            
            # 📚 PRIORITIZE KNOWLEDGE: Add most relevant knowledge first
            knowledge_docs = [doc for doc in relevant_docs if doc["doc_type"] != "conversation"]
            for doc in knowledge_docs[:3]:  # Top 3 knowledge docs
                content = f"**{doc['title']}** ({doc['category']})\n{doc['content']}\n"
                if current_length + len(content) < max_context_length:
                    context_parts.append(content)
                    current_length += len(content)
                else:
                    break  # Stop if we'd exceed the limit
            
            # 💬 ADD CONVERSATIONS: Add relevant past conversations
            if include_conversations:
                conversation_docs = [doc for doc in relevant_docs if doc["doc_type"] == "conversation"]
                for doc in conversation_docs[:2]:  # Top 2 conversations
                    content = f"**Similar Conversation:**\n{doc['content']}\n"
                    if current_length + len(content) < max_context_length:
                        context_parts.append(content)
                        current_length += len(content)
                    else:
                        break  # Stop if we'd exceed the limit
            
            # 📊 STEP 4: Return formatted context with metadata
            return {
                "context": "\n---\n".join(context_parts),
                "context_length": current_length,
                "documents_used": len(context_parts),
                "total_documents_found": len(relevant_docs),
                "categories_covered": list(set(doc["category"] for doc in relevant_docs))
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG context: {str(e)}")
            return {
                "context": "",
                "context_length": 0,
                "documents_used": 0,
                "total_documents_found": 0,
                "categories_covered": []
            }

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔄 FALLBACK METHODS - When vector search isn't available
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _fallback_text_search(
        self,
        query: str,
        doc_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        🔍 Fallback to MongoDB text search when vector search fails
        
        WHEN THIS IS USED:
        - Ollama is not available
        - Vector search fails for some reason
        - No embeddings are available
        
        HOW IT WORKS:
        - Uses MongoDB's built-in text search
        - Searches for keywords in document content
        - Less sophisticated than vector search but still useful
        """
        try:
            # 🔍 STEP 1: Build search filter for text search
            search_filter = {"$text": {"$search": query}}
            if doc_types:
                search_filter["doc_type"] = {"$in": doc_types}
            if categories:
                search_filter["category"] = {"$in": categories}
            
            # 📊 STEP 2: Search both collections
            results = []
            
            # Search conversations
            async for doc in self.conversations_collection.find(
                search_filter,
                {"score": {"$meta": "textScore"}}      # Get relevance score
            ).sort([("score", {"$meta": "textScore"})]).limit(limit):
                results.append(self._format_search_result(doc, use_text_score=True))
            
            # Search knowledge base
            async for doc in self.knowledge_collection.find(
                search_filter,
                {"score": {"$meta": "textScore"}}      # Get relevance score
            ).sort([("score", {"$meta": "textScore"})]).limit(limit):
                results.append(self._format_search_result(doc, use_text_score=True))
            
            # 📈 STEP 3: Sort by text relevance score
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in text search fallback: {str(e)}")
            return []

    def _format_search_result(self, doc: Dict[str, Any], use_text_score: bool = False) -> Dict[str, Any]:
        """
        📋 Format a search result for return
        
        STANDARDIZES OUTPUT:
        - Whether from vector search or text search
        - Ensures consistent format for the AI to use
        - Normalizes similarity scores
        """
        similarity = doc.get("similarity", 0)
        if use_text_score:
            # Convert MongoDB text score to 0-1 range
            similarity = doc.get("score", 0) / 10  # Normalize text score
        
        return {
            "id": doc.get("id", ""),
            "title": doc.get("title", ""),
            "content": doc.get("content", ""),
            "doc_type": doc.get("doc_type", ""),
            "category": doc.get("category", ""),
            "tags": doc.get("tags", []),
            "similarity": similarity,
            "metadata": doc.get("metadata", {}),
            "created_at": doc.get("created_at", ""),
            "source_url": doc.get("source_url")
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🌱 KNOWLEDGE SEEDING - Initialize with DevOps best practices
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _seed_devops_knowledge(self):
        """
        📚 Seed the knowledge base with DevOps best practices
        
        WHY WE DO THIS:
        - Give Jamie some initial knowledge to work with
        - Provide helpful DevOps information out of the box
        - Examples of common troubleshooting scenarios
        
        WHAT WE INCLUDE:
        - Kubernetes troubleshooting guides
        - Prometheus alerting best practices
        - Log analysis techniques with Loki
        - Distributed tracing with Tempo
        """
        devops_knowledge = [
            # 🚢 KUBERNETES KNOWLEDGE
            {
                "title": "Kubernetes Pod Troubleshooting",
                "content": """
Common Kubernetes pod issues and solutions:

1. **CrashLoopBackOff**: Pod container crashes repeatedly
   - Check logs: kubectl logs <pod-name> --previous
   - Verify resource limits and requests
   - Check environment variables and config

2. **ImagePullBackOff**: Cannot pull container image
   - Verify image name and tag
   - Check registry access and credentials
   - Use kubectl describe pod to see events

3. **Pending State**: Pod cannot be scheduled
   - Check node resources: kubectl describe nodes
   - Verify node selectors and affinity rules
   - Check for taints and tolerations

4. **Init Container Issues**: 
   - Check init container logs
   - Verify dependencies and timing
   - Ensure proper resource allocation
                """,
                "category": "kubernetes",
                "tags": ["troubleshooting", "pods", "debugging"],
                "doc_type": "troubleshoot"
            },
            
            # 📊 MONITORING KNOWLEDGE
            {
                "title": "Prometheus Alerting Best Practices",
                "content": """
Effective Prometheus alerting strategies:

1. **Alert Fatigue Prevention**:
   - Set appropriate thresholds
   - Use alert suppression for known issues
   - Group related alerts together

2. **Critical vs Warning Alerts**:
   - Critical: Immediate action required
   - Warning: Attention needed within hours
   - Info: For awareness only

3. **Common Alert Rules**:
   - High CPU/Memory usage
   - Service downtime detection
   - Error rate increases
   - Disk space warnings

4. **Alert Resolution**:
   - Include runbook links in alerts
   - Provide context and suggested actions
   - Set up proper escalation paths
                """,
                "category": "monitoring",
                "tags": ["prometheus", "alerting", "best-practices"],
                "doc_type": "knowledge"
            },
            
            # 📝 LOGGING KNOWLEDGE
            {
                "title": "Log Analysis with Loki",
                "content": """
Effective log analysis techniques using Loki:

1. **LogQL Basics**:
   - {service="frontend"} | json | status >= 400
   - rate({job="nginx"}[5m])
   - topk(10, sum by (path) (rate({service="api"}[1h])))

2. **Error Pattern Detection**:
   - Look for HTTP 5xx errors
   - Database connection failures
   - Timeout errors and retries

3. **Performance Analysis**:
   - Response time patterns
   - Slow query identification
   - Resource utilization from logs

4. **Structured Logging**:
   - Use JSON format for better parsing
   - Include correlation IDs
   - Add context like user ID, request ID
                """,
                "category": "logging",
                "tags": ["loki", "logql", "analysis"],
                "doc_type": "knowledge"
            },
            
            # 🔍 TRACING KNOWLEDGE
            {
                "title": "Distributed Tracing with Tempo",
                "content": """
Using Tempo for performance analysis:

1. **Trace Analysis**:
   - Identify bottlenecks in request flow
   - Find slow database queries
   - Detect external service delays

2. **Key Metrics**:
   - End-to-end latency
   - Service dependency mapping
   - Error correlation across services

3. **Optimization Strategies**:
   - Parallel processing where possible
   - Caching frequently accessed data
   - Connection pooling for databases

4. **Troubleshooting**:
   - Follow trace spans to find issues
   - Look for error tags and logs
   - Check resource utilization patterns
                """,
                "category": "tracing",
                "tags": ["tempo", "performance", "optimization"],
                "doc_type": "knowledge"
            }
        ]
        
        # 💾 STORE EACH KNOWLEDGE DOCUMENT
        for knowledge in devops_knowledge:
            await self.store_knowledge(
                title=knowledge["title"],
                content=knowledge["content"],
                category=knowledge["category"],
                doc_type=knowledge["doc_type"],
                tags=knowledge["tags"]
            )
        
        logger.info(f"Seeded {len(devops_knowledge)} DevOps knowledge documents")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔧 UTILITY METHODS - Helper functions for processing data
    # ═══════════════════════════════════════════════════════════════════════════════

    def _extract_topics(self, text: str) -> List[str]:
        """
        🏷️ Extract DevOps topics from text
        
        HOW IT WORKS:
        1. Look for keywords related to each DevOps category
        2. If we find keywords, add that category to the topics list
        3. Return all matching topics
        
        EXAMPLE:
        - Text: "kubectl get pods failing"
        - Topics found: ["kubernetes"]
        """
        topics = []
        text_lower = text.lower()
        
        # 📋 KEYWORD MAPPING - each category and its keywords
        topic_keywords = {
            "kubernetes": ["k8s", "pods", "cluster", "deployment", "service", "ingress", "kubectl"],
            "monitoring": ["prometheus", "grafana", "alerts", "metrics", "cpu", "memory", "monitoring"],
            "logging": ["loki", "logs", "errors", "debugging", "logql"],
            "tracing": ["tempo", "traces", "performance", "latency", "spans"],
            "git": ["github", "git", "commit", "pr", "pipeline", "deployment"],
            "infrastructure": ["docker", "container", "network", "storage", "volume"],
            "security": ["rbac", "secrets", "auth", "ssl", "tls", "certificates"]
        }
        
        # 🔍 SEARCH FOR KEYWORDS
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics or ["general"]  # Return "general" if no specific topics found

    def _determine_category(self, topics: List[str]) -> str:
        """
        📂 Determine primary category from topics
        
        WHY WE NEED THIS:
        - A document might match multiple topics
        - We need to pick the most important one as the primary category
        - We use a priority order to decide
        """
        if not topics:
            return "general"
        
        # 📊 PRIORITY ORDER - more specific categories first
        category_priority = ["kubernetes", "monitoring", "logging", "tracing", "git", "infrastructure", "security"]
        
        for category in category_priority:
            if category in topics:
                return category
        
        return topics[0] if topics else "general"

    def _generate_id(self, *args) -> str:
        """
        🆔 Generate unique document ID
        
        HOW IT WORKS:
        1. Combine all arguments into a string
        2. Add current timestamp for uniqueness
        3. Create MD5 hash for consistent, short ID
        """
        content = "".join(str(arg) for arg in args) + str(datetime.now().timestamp())
        return hashlib.md5(content.encode()).hexdigest()

    # ═══════════════════════════════════════════════════════════════════════════════
    # 📊 STATUS AND MANAGEMENT - Monitor the system and clean up
    # ═══════════════════════════════════════════════════════════════════════════════

    async def get_status(self) -> Dict[str, Any]:
        """
        📊 Get RAG memory system status
        
        RETURNS INFORMATION ABOUT:
        - Whether the system is working
        - How many documents we have stored
        - What categories are available
        - Whether embeddings are working
        """
        if not self.available:
            return {"available": False, "error": "MongoDB not available"}
        
        try:
            # 📊 GET COUNTS
            conversations_count = await self.conversations_collection.count_documents({})
            knowledge_count = await self.knowledge_collection.count_documents({})
            
            # 📂 GET AVAILABLE CATEGORIES
            categories = await self.knowledge_collection.distinct("category")
            
            return {
                "available": True,
                "ollama_embeddings": self.embeddings.available,
                "conversations_count": conversations_count,
                "knowledge_count": knowledge_count,
                "categories": categories,
                "embedding_dimension": self.embedding_dimension,
                "database": self.database_name
            }
            
        except Exception as e:
            return {"available": False, "error": str(e)}

    async def close(self):
        """🔐 Close MongoDB connection cleanly"""
        if self.client:
            self.client.close()

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TESTING AND EXAMPLES - Show how to use this system
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test_rag_memory():
        """
        🧪 Test the RAG memory system
        
        THIS EXAMPLE SHOWS:
        1. How to initialize the system
        2. How to store a conversation
        3. How to get RAG context for a query
        4. How to check system status
        """
        # 🚀 STEP 1: Initialize
        rag = MongoRAGMemory()
        await rag.initialize()
        
        print("RAG Memory Status:", await rag.get_status())
        
        # 💬 STEP 2: Store a test conversation
        conv_id = await rag.store_conversation(
            user_message="How do I check my pods?",
            jamie_response="Right then! Use 'kubectl get pods' to see your pod status, mate!",
            context={"namespace": "default"},
            session_id="test_session",
            topics=["kubernetes"],
            intent="query",
            confidence=0.8
        )
        print(f"Stored conversation: {conv_id}")
        
        # 🔍 STEP 3: Test RAG context retrieval
        context = await rag.get_rag_context("kubernetes pod troubleshooting")
        print(f"RAG Context: {len(context['context'])} chars, {context['documents_used']} docs")
        
        # 🔐 STEP 4: Clean up
        await rag.close()
    
    # 🏃 RUN THE TEST
    asyncio.run(test_rag_memory()) 