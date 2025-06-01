"""
🔧 Jamie AI DevOps Copilot - Configuration

Sprint 2: Environment configuration and settings management
"""

import os
from typing import Optional
from pathlib import Path

class JamieConfig:
    """
    Configuration management for Jamie AI DevOps Copilot
    """
    
    # API Configuration
    HOST: str = os.getenv("JAMIE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("JAMIE_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("JAMIE_LOG_LEVEL", "INFO")
    
    # AI Brain Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    JAMIE_MODEL: str = os.getenv("JAMIE_MODEL", "llama3.1:8b")
    AI_TEMPERATURE: float = float(os.getenv("JAMIE_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("JAMIE_MAX_TOKENS", "2048"))
    
    # Memory Configuration
    MEMORY_DIR: str = os.getenv("JAMIE_MEMORY_DIR", "./jamie_memory")
    MAX_MEMORIES: int = int(os.getenv("JAMIE_MAX_MEMORIES", "10000"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("JAMIE_SIMILARITY_THRESHOLD", "0.3"))
    
    # Conversation Configuration
    MAX_MESSAGES_PER_SESSION: int = int(os.getenv("JAMIE_MAX_MESSAGES", "1000"))
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("JAMIE_SESSION_TIMEOUT", "24"))
    
    # Database Configuration (for future use)
    MONGODB_URL: Optional[str] = os.getenv("JAMIE_MONGODB_URL")
    REDIS_URL: Optional[str] = os.getenv("JAMIE_REDIS_URL")
    
    # RAG Memory Configuration
    RAG_DATABASE_NAME: str = os.getenv("JAMIE_RAG_DATABASE", "jamie_rag")
    RAG_MAX_DOCUMENTS: int = int(os.getenv("JAMIE_RAG_MAX_DOCUMENTS", "50000"))
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("JAMIE_RAG_SIMILARITY_THRESHOLD", "0.3"))
    RAG_CONTEXT_LENGTH: int = int(os.getenv("JAMIE_RAG_CONTEXT_LENGTH", "4000"))
    
    # Development Configuration
    DEBUG: bool = os.getenv("JAMIE_DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("JAMIE_RELOAD", "false").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        Path(cls.MEMORY_DIR).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_summary(cls) -> dict:
        """Get configuration summary"""
        return {
            "api": {
                "host": cls.HOST,
                "port": cls.PORT,
                "log_level": cls.LOG_LEVEL,
                "debug": cls.DEBUG
            },
            "ai": {
                "ollama_host": cls.OLLAMA_HOST,
                "model": cls.JAMIE_MODEL,
                "temperature": cls.AI_TEMPERATURE,
                "max_tokens": cls.AI_MAX_TOKENS
            },
            "memory": {
                "directory": cls.MEMORY_DIR,
                "max_memories": cls.MAX_MEMORIES,
                "similarity_threshold": cls.SIMILARITY_THRESHOLD
            },
            "conversation": {
                "max_messages": cls.MAX_MESSAGES_PER_SESSION,
                "session_timeout": cls.SESSION_TIMEOUT_HOURS
            }
        }

# Create global config instance
config = JamieConfig() 